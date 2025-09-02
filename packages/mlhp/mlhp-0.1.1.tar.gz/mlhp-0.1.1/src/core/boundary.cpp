// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/boundary.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/dense.hpp"
#include "mlhp/core/sparse.hpp"
#include "mlhp/core/quadrature.hpp"
#include "mlhp/core/arrayfunctions.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/algorithm.hpp"
#include "mlhp/core/spatial.hpp"

namespace mlhp::boundary
{

std::vector<size_t> allFaces( size_t D )
{
    std::vector<size_t> face( 2 * D );

    std::iota( face.begin( ), face.end( ), size_t { 0 } );

    return face;
}

size_t face( size_t axis, size_t side )
{
    return 2 * axis + side;
}

template<size_t D>
std::vector<bool> boundaryDofMask( const AbsBasis<D>& basis,
                                   const MeshCellFaces& faces, 
                                   size_t ifield )
{
    auto nfaces = faces.size( );

    std::vector<size_t> count( basis.ndof( ), 0 );

    #pragma omp parallel
    {
        auto locationMap = std::vector<DofIndex> { };
        auto faceDofs = std::vector<size_t> { };

        #pragma omp for schedule(static)
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( nfaces ); ++ii )
        {
            auto iface = static_cast<size_t>( ii );
            auto icell = faces[iface].first;

            locationMap.resize( 0 );
            faceDofs.resize( 0 );

            basis.locationMap( icell, locationMap );
            basis.faceDofs( icell, faces[iface].second, ifield, faceDofs );

            for( auto index : faceDofs )
            {
                auto& entry = count[locationMap[index]];

                #pragma omp atomic
                entry += 1;

            } // for index
        } // for iface
    } // omp parallel
    
    std::vector<bool> mask( basis.ndof( ) );

    std::transform( count.begin( ), count.end( ), mask.begin( ), 
                    []( size_t entry ) { return entry != 0; } );

    return mask;
}

//! Indices of dofs active on one of the given faces
template<size_t D>
std::vector<DofIndex> boundaryDofIndices( const AbsBasis<D>& basis,
                                          const MeshCellFaces& faces,
                                          size_t ifield )
{
    return algorithm::forwardIndexMap<DofIndex>(
        boundaryDofMask( basis, faces, ifield ) );
}

namespace detail
{

void mapAndfilter( LocationMap& map, const LocationMap& filterMap )
{
    auto predicate = [&]( auto dof ){ return filterMap[dof]; };

    std::transform( map.begin( ), map.end( ), map.begin( ), predicate );

    map.erase( std::remove( map.begin( ), map.end( ), NoDof ), map.end( ) );
}

} // namespace detail

template<size_t D>
DofIndicesValuesPair boundaryDofs( const spatial::ScalarFunction<D>& function,
                                   const MeshCellFaces& faces,
                                   const AbsBasis<D>& basis,
                                   const QuadratureOrderDeterminor<D>& determinor,
                                   size_t ifield )
{
    auto indices = boundaryDofIndices( basis, faces, ifield );
    auto dofMap = algorithm::backwardIndexMap( indices, basis.ndof( ) );

    if( indices.empty( ) )
    {
        return { { }, { } };
    }

    std::function globalMaps = [&]( CellIndex iface, LocationMap& map )
    {
        std::vector<size_t> localDof;
        std::vector<DofIndex> locationMap;

        basis.faceDofs( faces[iface].first, faces[iface].second, ifield, localDof );
        basis.locationMap( faces[iface].first, locationMap );

        map.resize( localDof.size( ) );
        for( size_t i = 0; i < localDof.size( ); ++i )
        {
            map[i] = locationMap[localDof[i]];
        }

        detail::mapAndfilter( map, dofMap );
    };

    auto globalndof = static_cast<DofIndex>( indices.size( ) );
    auto generator = LocationMapRange( static_cast<CellIndex>( faces.size( ) ), globalMaps );

    auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( generator, globalndof );
    auto vector = std::vector<double>( matrix.size1( ), 0.0 );

    auto globalSystem = AssemblyTargetVector { matrix, vector };
    auto types = { AssemblyType::UnsymmetricMatrix, AssemblyType::Vector };
    auto assemble = makeAssemblyKernel( globalSystem, types, { { }, { } }, matrix.size1( ) );

    #pragma omp parallel
    {
        auto localMap = std::vector<size_t> { };
        auto globalMap = LocationMap { };
        auto sortedIndices = std::vector<size_t> { };
        auto basisCache = basis.createEvaluationCache( );
        auto shapes = BasisFunctionEvaluation<D> { };
        auto localSystem = AlignedDoubleVectors( 2 );
        auto quadrature = QuadraturePointCache { };
        auto rs = CoordinateList<D - 1> { };
        auto rst = CoordinateList<D> { };
        auto weights = std::vector<double> { };

        #pragma omp for schedule( dynamic )
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( faces.size( ) ); ++ii )
        {
            auto [ielement, localFaceIndex] = faces[static_cast<size_t>( ii )];

            utilities::resize0( localMap, globalMap, weights, sortedIndices, rst, rs );

            globalMaps( static_cast<CellIndex>( ii ), globalMap );

            basis::faceDofsWithoutOffset<D>( basis, ielement, localFaceIndex, ifield, localMap );

            auto maxdegrees = basis.prepareEvaluation( ielement, 0, shapes, basisCache );
            
            const auto& mapping = basis.mapping( basisCache );
                
            // Distribute points (currently this cannot reuse boundary integral stuff since 
            // we treat each face separately here to exclude internal dofs).
            auto orders = determinor( ielement, maxdegrees );

            if( mapping.type == CellType::NCube )
            {
                auto [normal, side] = normalAxisAndSide( localFaceIndex );

                tensorProductQuadrature( array::slice( orders, normal ), rs, weights, quadrature );
            }
            else
            {
                MLHP_CHECK( mapping.type == CellType::Simplex, "Invalid cell type." );

                simplexQuadrature( array::make<D - 1> ( array::maxElement( orders ) ), rs, weights, quadrature );
            }

            // Map points
            auto face = mesh::faceMapping( basis.mesh( ), ielement, localFaceIndex );

            for( size_t i = 0; i < rs.size( ); ++i )
            {
                auto [coords, Jf, detJ1] = map::withJDetJ( face, rs[i] );
                auto [xyz, Jg, detJ2] = map::withJDetJ( mapping, coords );

                auto J = spatial::concatenateJacobians<D, D, D - 1>( Jf, Jg );

                rst.push_back( coords );
                weights[i] *= spatial::computeDeterminant<D, D - 1>( J );
            }

            initializeLocalAssemblyTargets( localSystem, types, localMap.size( ) );

            auto ndof = localMap.size( );
            auto ndofpadded = memory::paddedLength<double>( ndof );

            for( size_t ipoint = 0; ipoint < rst.size( ); ++ipoint )
            {
                // TODO: Enable grid evaluation
                basis.evaluateSinglePoint( rst[ipoint], shapes, basisCache );

                auto xyz = mapping( rst[ipoint] );

                // TODO?: Filter shape functions and use standard integrand?
                auto factor = weights[ipoint];
                auto N = shapes.noalias( ifield, 0 );

                auto Me = memory::assumeAlignedNoalias( localSystem[0].data( ) );
                auto Fe = memory::assumeAlignedNoalias( localSystem[1].data( ) );

                for( size_t i = 0; i < ndof; ++i )
                {
                    for( size_t j = 0; j < ndof; ++j )
                    {
                        Me[i * ndofpadded + j] += N[localMap[i]] * N[localMap[j]] * factor;
                    }
                }

                factor *= function( xyz );

                for( size_t i = 0; i < ndof; ++i )
                {
                    Fe[i] += N[localMap[i]] * factor;
                }
            }

            assemble( localSystem, globalMap, sortedIndices );

        } // for iface
    } // omp parallel

    auto maxiter = std::max( size_t { 2000 }, static_cast<size_t>( 2 * matrix.size1( ) ) );
    auto solver = linalg::makeCGSolver( 1e-12, 0.0, maxiter );

    return { std::move( indices ), solver( matrix, vector ) };
}

template<size_t D> MLHP_EXPORT
DofIndicesValuesPair boundaryDofs( const spatial::ScalarFunction<D>& function,
                                   const AbsBasis<D>& basis,
                                   const std::vector<size_t>& boundaries,
                                   const QuadratureOrderDeterminor<D>& determinor,
                                   size_t ifield )
{
    auto faces = utilities::linearizeVectors( 
        mesh::boundariesByBoundingBox( basis.mesh( ), boundaries ) );

    return boundaryDofs( function, faces, basis, determinor, ifield );
}

template<size_t D>
DofIndicesValuesPair boundaryDofs( const spatial::ScalarFunction<D>& function,
                                   const AbsBasis<D>& basis,
                                   const std::vector<size_t>& faces,
                                   size_t ifield )
{
    return boundaryDofs( function, basis, faces, relativeQuadratureOrder<D>( ), ifield );
}

template<size_t D> MLHP_EXPORT
DofIndicesValuesPair boundaryDofs( const spatial::VectorFunction<D>& function,
                                   const AbsBasis<D>& basis,
                                   const std::vector<size_t>& faces,
                                   const QuadratureOrderDeterminor<D>& determinor )
{
    MLHP_CHECK( function.odim == basis.nfields( ), "Inconsistent number of field components." );

    std::vector<DofIndicesValuesPair> results;

    for( size_t ifield = 0; ifield < function.odim; ++ifield )
    {
        auto sliced = spatial::extractComponent( function, ifield );

        results.push_back( boundaryDofs<D>( sliced, basis, faces, determinor, ifield ) );
    }

    return combine( results );
}

DofIndicesValuesPair makeUnique( const DofIndicesValuesPair& dofs )
{
    if( dofs.first.empty( ) ) return dofs;

    auto ndof = *std::max_element( dofs.first.begin( ), dofs.first.end( ) ) + 1;

    std::vector<size_t> count( static_cast<size_t>( ndof ), 0 );
    std::vector<double> values( static_cast<size_t>( ndof ), 0.0 );

    for( size_t i = 0; i < dofs.first.size( ); ++i )
    {
        count[dofs.first[i]]++;
        values[dofs.first[i]] += dofs.second[i];
    }

    DofIndicesValuesPair result;

    for( DofIndex i = 0; i < ndof; ++i )
    {
        if( count[i] != 0 )
        {
            result.first.push_back( i );
            result.second.push_back( values[i] / count[i] );
        }
    }

    return result;
}


DofIndicesValuesPair combine( const std::vector<DofIndicesValuesPair>& boundaryDofs )
{
    DofIndicesValuesPair result;

    for( const auto& [indices, values] : boundaryDofs )
    {
        result.first.insert( result.first.end( ), indices.begin( ), indices.end( ) );
        result.second.insert( result.second.end( ), values.begin( ), values.end( ) );
    }

    return makeUnique( result );
}

std::vector<double> inflate( std::span<const double> interiorDofs,
                             const DofIndicesValuesPair& boundaryDofs,
                             std::vector<double>& target )
{
    size_t ndof = boundaryDofs.first.size( ) + interiorDofs.size( );

    auto mask = algorithm::indexMask( boundaryDofs.first, ndof );

    MLHP_CHECK_DBG( std::accumulate( mask.begin( ), mask.end( ), size_t { 0 } ) ==
                    boundaryDofs.first.size( ), "Duplicated boundary dofs." );

    target.resize( ndof );

    size_t index1 = 0, index2 = 0;

    for( size_t iDof = 0; iDof < ndof; ++iDof )
    {
        if( mask[iDof] )
        {
            target[iDof] = boundaryDofs.second[index1++];
        }
        else
        {
            target[iDof] = interiorDofs[index2++];
        }
    }

    return target;
}

std::vector<double> inflate( std::span<const double> interiorDofs,
                             const DofIndicesValuesPair& boundaryDofs )
{
    std::vector<double> target;

    inflate( interiorDofs, boundaryDofs, target );

    return target;
}

std::vector<CellAssociatedTriangles> triangulateFaces( const AbsMesh<3>& mesh,
                                                       const std::vector<size_t>& faces )
{
    std::vector<CellAssociatedTriangles> triangulations( faces.size( ) );

    auto segments = mesh::boundaries( mesh );
    auto map = algorithm::backwardIndexMap( faces, size_t { 6 } );
    auto mapping = mesh.createMapping( );

    std::array<double, 2> rst2[4] = { { -1.0, -1.0 }, { -1.0, 1.0 }, { 1.0, -1.0 }, { 1.0, 1.0 } };

    for( auto [cell, face] : segments )
    {
        if( map[face] != NoValue<size_t> )
        {
            mesh.prepareMapping( cell, mapping );

            std::array<double, 3> rst[4];
            std::array<double, 3> xyz[4];

            auto normal = face / 2;
            auto t = ( face - 2 * normal ) > 0 ? 1.0 : -1.0;
                        
            for( size_t i = 0; i < 4; ++i )
            {
                rst[i] = array::insert<double, 2>( rst2[i], normal, t );
                xyz[i] = mapping.map( rst[i] );
            }

            for( auto index : { 0, 1, 2, 1, 2, 3 } )
            {
                for( size_t axis = 0; axis < 3; ++axis )
                {
                    std::get<0>( triangulations[map[face]] ).push_back( xyz[index][axis] );
                    std::get<1>( triangulations[map[face]] ).push_back( rst[index][axis] );
                }
            }

            std::get<2>( triangulations[map[face]] ).push_back( cell );
            std::get<2>( triangulations[map[face]] ).push_back( cell );
        }
    }

    return triangulations;
}

namespace detail
{

// Compute two vectors [indices, faces] that represent a linearized vector of vectors
// containing the boundary faces for each element in [0, ncells)
auto associateToCells( const std::vector<MeshCellFace>& segments )
{
    auto ncells = CellIndex { };

    for( auto segment : segments )
    {
        ncells = segment.first + 1 > ncells ? segment.first + 1 : ncells;
    }

    std::vector<size_t> nsegments( ncells, 0 );

    for( auto segment : segments )
    {
        nsegments[segment.first]++;
    }

    std::vector<size_t> indices( ncells + 1 );

    indices[0] = 0;

    std::partial_sum( nsegments.begin( ), nsegments.end( ), indices.begin( ) + 1 );
    std::fill( nsegments.begin( ), nsegments.end( ), 0 );

    std::vector<size_t> faces( segments.size( ) );

    for( auto segment : segments )
    {
        auto index = indices[segment.first];
        auto offset = nsegments[segment.first]++;

        faces[index + offset] = segment.second;
    }

    return std::make_tuple( indices, faces );
}

} // namespace detail

template<size_t D>
auto sliceJacobianMatrix( const JacobianMatrix<D, D>& J, size_t axis )
{
    JacobianMatrix<D, D - 1> slicedJ { };

    for( size_t j0 = 0; j0 + 1 < D; ++j0 )
    {
        size_t j1 = j0 + static_cast<size_t>( j0 >= axis );

        for( size_t i = 0; i < D; ++i )
        {
            slicedJ[i * ( D - 1 ) + j0] = J[i * D + j1];
        }
    }

    return slicedJ;
}

template<size_t D>
QuadratureOnMeshFaces<D>::QuadratureOnMeshFaces( const AbsMesh<D>& mesh,
                                                 const std::vector<size_t>& meshFaces,
                                                 const QuadratureOrderDeterminor<D>& order ) :
    QuadratureOnMeshFaces( utilities::linearizeVectors(
        mesh::boundariesByBoundingBox( mesh, meshFaces ) ), order )
{  }

template<size_t D>
QuadratureOnMeshFaces<D>::QuadratureOnMeshFaces( const std::vector<MeshCellFace>& cellFaces,
                                                 const QuadratureOrderDeterminor<D>& order ) :
    order_ { order }
{
    std::tie( indices_, faces_ ) = detail::associateToCells( cellFaces );
}

template<size_t D>
struct QuadratureOnMeshFaces<D>::Cache
{
    QuadraturePointCache quadrature;
    CoordinateList<D - 1> rs = { };
};

template<size_t D>
typename AbsQuadratureOnMesh<D>::AnyCache QuadratureOnMeshFaces<D>::initialize( ) const
{
    return Cache { };
}

template<size_t D>
void QuadratureOnMeshFaces<D>::distribute( const MeshMapping<D>& mapping,
                                           std::array<size_t, D> orders,
                                           CoordinateList<D>& rst,
                                           CoordinateList<D>& normals,
                                           std::vector<double>& weights,
                                           typename AbsQuadratureOnMesh<D>::AnyCache& anyCache ) const
{
    if constexpr( D > 1 )
    {
        if( mapping.icell + size_t { 1 } >= indices_.size( ) )
        { 
            return;
        }
        
        auto& cache = utilities::cast<Cache>( anyCache );
        auto order = array::maxElement( order_( mapping.icell, orders ) );

        for( size_t index = indices_[mapping.icell]; index < indices_[mapping.icell + 1]; ++index )
        {
            utilities::resize0( cache.rs );
            
            auto rsize = rst.size( );
            auto wsize = weights.size( );
            auto nsize = normals.size( );
            
            if( mapping.type == CellType::NCube )
            {
                tensorProductQuadrature( array::make<D - 1>( order ), 
                    cache.rs, weights, cache.quadrature );
            }
            else
            {
                MLHP_CHECK( mapping.type == CellType::Simplex, "Cell type not implemented." );

                simplexQuadrature( array::make<D - 1>( order ), cache.rs, weights, cache.quadrature );
            }
            
            auto face = FaceMapping<D>( mapping.type, faces_[index] );
            auto npoints = cache.rs.size( );
            
            rst.resize( rsize + npoints );
            normals.resize( nsize + npoints );

            for( size_t ipoint = 0; ipoint < npoints; ++ipoint )
            {
                auto [coords, J0] = map::withJ( face, cache.rs[ipoint] );
                auto [xyz, J1] = map::withJ( mapping, coords );

                auto J = spatial::concatenateJacobians<D, D, D - 1>( J0, J1 );
                auto detJ = spatial::computeDeterminant<D, D - 1>( J );
                
                rst[rsize + ipoint] = coords;
                weights[wsize + ipoint] *= detJ;
                normals[nsize + ipoint] = spatial::mapPlaneNormal<D>( J1, face.normal( ) );

                auto length = spatial::norm( normals[nsize + ipoint] );

                constexpr auto eps = std::numeric_limits<double>::epsilon( );

                MLHP_CHECK( length > 100.0 * eps, "Zero length normal vector." );

                normals[nsize + ipoint] = normals[nsize + ipoint] / length;
            }
        }
    }
    else
    {
        MLHP_THROW( "Check for D = 1 because jacobian has dimension zero then?" );
    }
}

#define MLHP_INSTANTIATE_DIM( D )                                                        \
                                                                                         \
    template MLHP_EXPORT                                                                 \
    std::vector<bool> boundaryDofMask( const AbsBasis<D>& basis,                         \
                                       const MeshCellFaces& faces,                       \
                                       size_t ifield );                                  \
                                                                                         \
    template MLHP_EXPORT                                                                 \
    std::vector<DofIndex> boundaryDofIndices( const AbsBasis<D>& basis,                  \
                                              const MeshCellFaces& faces,                \
                                              size_t ifield );                           \
                                                                                         \
    template MLHP_EXPORT                                                                 \
    DofIndicesValuesPair boundaryDofs( const spatial::ScalarFunction<D>& function,       \
                                       const MeshCellFaces& baseCells,                   \
                                       const AbsBasis<D>& basis,                         \
                                       const QuadratureOrderDeterminor<D>& determinor,   \
                                       size_t ifield );                                  \
                                                                                         \
    template MLHP_EXPORT                                                                 \
    DofIndicesValuesPair boundaryDofs( const spatial::ScalarFunction<D>& function,       \
                                       const AbsBasis<D>& basis,                         \
                                       const std::vector<size_t>& faces,                 \
                                       const QuadratureOrderDeterminor<D>& determinor,   \
                                       size_t ifield );                                  \
                                                                                         \
    template MLHP_EXPORT                                                                 \
    DofIndicesValuesPair boundaryDofs( const spatial::ScalarFunction<D>& function,       \
                                       const AbsBasis<D>& basis,                         \
                                       const std::vector<size_t>& faces,                 \
                                       size_t ifield );                                  \
                                                                                         \
    template MLHP_EXPORT                                                                 \
    DofIndicesValuesPair boundaryDofs( const spatial::VectorFunction<D>& function,       \
                                       const AbsBasis<D>& basis,                         \
                                       const std::vector<size_t>& faces,                 \
                                       const QuadratureOrderDeterminor<D>& determinor ); \
                                                                                         \
    template class QuadratureOnMeshFaces<D>;

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // namespace mlhp::boundary

