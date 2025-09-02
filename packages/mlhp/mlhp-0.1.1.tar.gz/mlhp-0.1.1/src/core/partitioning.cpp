// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/partitioning.hpp"
#include "mlhp/core/quadrature.hpp"
#include "mlhp/core/refinement.hpp"
#include "mlhp/core/polynomials.hpp"
#include "mlhp/core/arrayfunctions.hpp"
#include "mlhp/core/mesh.hpp"
#include "mlhp/core/spatial.hpp"

#include <array>

namespace mlhp
{

template<size_t D>
QuadratureOrderDeterminor<D> relativeQuadratureOrder( int offset, double factor )
{
    return [=]( CellIndex, std::array<size_t, D> degrees ) noexcept
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            auto newDegree = static_cast<int>( std::ceil( factor * degrees[axis] ) ) + offset;

            degrees[axis] = static_cast<size_t>( std::max( newDegree, 0 ) );
        }

        return degrees;
    };
}

template<size_t D>
QuadratureOrderDeterminor<D> absoluteQuadratureOrder( std::array<size_t, D> orders )
{
    return [=]( CellIndex, std::array<size_t, D> ) noexcept
    {
        return orders;
    };
}

template<size_t D>
void mapQuadraturePointGrid( const AbsMapping<D>& mapping,
                             const CoordinateGrid<D>& rstGrid,
                             CoordinateList<D>& xyzList,
                             std::vector<double>& weights )
{
    auto orders = array::elementSizes( rstGrid );
    auto size = weights.size( );

    MLHP_CHECK( size == array::product( orders ), "Inconsistent sizes." );

    xyzList.resize( size );

    nd::executeWithIndex( orders, [&]( std::array<size_t, D> ijk, size_t i )
    {
        auto [xyz, detJ] = map::withDetJ( mapping, array::extract( rstGrid, ijk ) );

        MLHP_CHECK( detJ > 0, "Jacobian is not positive." );

        xyzList[i] = xyz;
        weights[i] *= detJ;
    } );
}

template<size_t D>
void mapQuadraturePointLists( const AbsMapping<D>& mapping,
                              const CoordinateGrid<D>& rstLists,
                              CoordinateList<D>& xyzList,
                              std::vector<double>& weights )
{
    auto size = weights.size( );

    for( size_t axis = 0; axis < D; ++axis )
    {
        MLHP_CHECK( rstLists[axis].size( ) == size, "Inconsistent sizes" );
    }

    xyzList.resize( size );

    for( size_t i = 0; i < size; ++i )
    {
        auto rst = array::extract( rstLists, array::make<D>( i ) );
        auto [xyz, detJ] = map::withDetJ( mapping, rst );

        MLHP_CHECK( detJ > 0, "Jacobian is not positive." );

        xyzList[i] = xyz;
        weights[i] *= detJ;
    }
}

template<size_t D>
EvaluateQuadratureResult<D> evaluateQuadrature( const AbsQuadrature<D>& quadrature,
                                                const AbsMesh<D>& mesh,
                                                CellIndex icell,
                                                std::array<size_t, D> orders )
{
    auto cache = quadrature.initialize( );
    auto mapping = mesh::mapping( mesh, icell );

    auto npartitions = quadrature.partition( mapping, cache );

    auto result = EvaluateQuadratureResult<D>( npartitions );
    auto rst = std::array<std::vector<double>, D> { };

    for( size_t ipartition = 0; ipartition < npartitions; ++ipartition )
    {
        utilities::resize0( rst );

        result[ipartition].icell = icell;
        result[ipartition].mesh = &mesh;

        result[ipartition].isgrid = quadrature.distribute( ipartition, orders, 
            rst, result[ipartition].xyz, result[ipartition].weights, cache );

        auto sizes = array::elementSizes( rst );

        if( result[ipartition].isgrid )
        {
            result[ipartition].rst.resize( array::product( sizes ) );

            nd::executeWithIndex( sizes, [&]( std::array<size_t, D> ijk, size_t index ) 
            { 
                result[ipartition].rst[index] = array::extract( rst, ijk );
            } );
        }
        else
        {
            MLHP_CHECK( sizes == array::make<D>( rst[0].size( ) ), "Inconsistent sizes." );

            result[ipartition].rst.resize( rst[0].size( ) );

            for( size_t index = 0; index < rst[0].size( ); ++index )
            {
                result[ipartition].rst[index] = array::extract( rst, array::make<D>( index ) );
            }
        }
    }

    return result;
}

template<size_t D>
EvaluateQuadrature2Result<D> evaluateQuadrature( const AbsQuadratureOnMesh<D>& quadrature,
                                                 const AbsMesh<D>& mesh,
                                                 CellIndex icell,
                                                 std::array<size_t, D> orders )
{
    auto cache = quadrature.initialize( );
    auto mapping = mesh::mapping( mesh, icell );
    auto result = EvaluateQuadraturePartition2<D> { };

    result.isgrid = false;
    result.icell = icell;
    result.mesh = &mesh;

    quadrature.distribute( mapping, orders, result.rst, result.normals, result.weights, cache );

    result.xyz.resize( result.rst.size( ) );

    for( size_t ipoint = 0; ipoint < result.rst.size( ); ++ipoint )
    {
        result.xyz[ipoint] = mapping( result.rst[ipoint] );
    }

    return std::vector { result };
}

namespace
{

template<size_t D>
void internalSpaceTreeLeaves( const ImplicitFunction<D>& function, 
                              const AbsMapping<D>& mapping,
                              size_t depth, size_t nseedpoints,
                              auto&& append )
{
    auto generateRecursive = [&]( auto&& self, auto&& cell, size_t level ) -> void
    {
        auto result = int { 0 };
        auto fullMapping = [&]( ){ return ConcatenatedMapping<D>{ &mapping, &cell }; };

        if( level < depth && 0 == ( result = intersectionTest( function, fullMapping( ), nseedpoints ) ) )
        { 
            auto times = array::make<D>( size_t { 2 } );
            auto generator = makeCartesianMappingSplitter( cell, times );

            nd::execute( times, [&]( std::array<size_t, D> ijk )
            { 
                self( self, generator( ijk ), level + 1 );
            } );
        }
        else
        {
            append( cell, result, level );
        }
    };

    generateRecursive( generateRecursive, CartesianMapping<D> { }, 0 );
}

} // namespace

template<size_t D>
void generateSpaceTreeLeaves( const ImplicitFunction<D>& function,
                              const AbsMapping<D>& mapping,
                              size_t depth, size_t nseedpoints,
                              std::vector<CartesianMapping<D>>& cells )
{
    auto append = [&]( auto&& cell, auto&&, auto&& )
    {
        cells.push_back( cell );
    };

    internalSpaceTreeLeaves( function, mapping, depth, nseedpoints, append );
}

template<size_t D>
void generateSpaceTreeLeaves( const ImplicitFunction<D>& function,
                              const AbsMapping<D>& mapping,
                              size_t depth, size_t nseedpoints,
                              std::vector<CartesianMapping<D>>& cells,
                              std::vector<int>& cutState,
                              bool computeCutStateOfFinestCells )
{
    auto append = [&]( auto&& cell, auto&& cut, auto&& level )
    {
        if( computeCutStateOfFinestCells && level == depth )
        {
            auto fullMapping = ConcatenatedMapping<D>( &mapping, &cell );

            cut = intersectionTest( function, fullMapping, nseedpoints );
        }
    
        cells.push_back( cell );
        cutState.push_back( cut );
    };

    internalSpaceTreeLeaves( function, mapping, depth, nseedpoints, append );
}

template<size_t D>
struct SpaceTreeQuadrature<D>::Cache
{
    std::vector<CartesianMapping<D>> mappings;
    std::vector<int> cutState;
    const AbsMapping<D>* mapping;
    QuadraturePointCache quadrature;
};

template<size_t D>
SpaceTreeQuadrature<D>::SpaceTreeQuadrature( const ImplicitFunction<D>& function, double alpha, size_t depth, size_t nseedpoints ) :
    function_( function ), depth_( depth ), alphaFCM_( alpha ), numberOfSeedPoints_( nseedpoints )
{ }

template<size_t D>
QuadratureCache<D> SpaceTreeQuadrature<D>::initialize( ) const
{
    return Cache { };
}

template<size_t D>
size_t SpaceTreeQuadrature<D>::partition( const MeshMapping<D>& mapping,
                                          QuadratureCache<D>& anyCache ) const
{
    MLHP_CHECK( mapping.type == CellType::NCube, "Space tree only works on n-cubes." );

    auto& data = utilities::cast<Cache>( anyCache );

    data.mapping = &mapping;
    data.mappings.resize( 0 );
    data.cutState.resize( 0 );

    generateSpaceTreeLeaves( function_, mapping, depth_, numberOfSeedPoints_, data.mappings, data.cutState );

    return data.mappings.size( );
}

template<size_t D>
bool SpaceTreeQuadrature<D>::distribute( size_t ipartition,
                                         std::array<size_t, D> orders,
                                         CoordinateGrid<D>& rst,
                                         CoordinateList<D>& xyzList,
                                         std::vector<double>& weights,
                                         QuadratureCache<D>& anyCache ) const
{
    auto& data = utilities::cast<Cache>( anyCache );

    if( alphaFCM_ == 0.0 && data.cutState[ipartition] == -1 )
    {
        utilities::resize0( rst, xyzList, weights );

        return true;
    }

    tensorProductQuadrature( orders, rst, weights, data.quadrature );

    auto detJ = data.mappings[ipartition].mapGrid( rst );
    auto cut = data.cutState[ipartition];

    mapQuadraturePointGrid( *data.mapping, rst, xyzList, weights );

    for( size_t ipoint = 0; ipoint < xyzList.size( ); ++ipoint )
    {
        weights[ipoint] *= detJ;

        if( alphaFCM_ != 1.0 && ( cut == -1 || ( cut == 0 && !function_( xyzList[ipoint] ) ) ) )
        {
            weights[ipoint] *= alphaFCM_;
        }
    }

    return true;
}

template<size_t D>
bool SpaceTreeQuadrature<D>::distributeForMomentFitting( size_t ipartition,
                                                         std::array<size_t, D> orders,
                                                         CoordinateGrid<D>& rst,
                                                         CoordinateGrid<D>& weightsGrid,
                                                         std::vector<double>& weights,
                                                         QuadratureCache<D>& anyCache ) const
{
    auto& data = utilities::cast<Cache>( anyCache );

    auto intersection = data.cutState[ipartition];

    tensorProductQuadrature( orders, rst, weightsGrid, data.quadrature );

    weights.resize( array::product( orders ) );

    double detJ = data.mappings[ipartition].mapGrid( rst );

    // Do intersection test on gauss points if cell was not checked
    if( intersection == 0 )
    {
        size_t count = 0;

        nd::executeWithIndex( orders, [&]( std::array<size_t, D> ijk, size_t i )
        {
            bool isInside = function_( data.mapping->map( array::extract( rst, ijk ) ) );

            count = count + static_cast<size_t>( isInside );

            weights[i] = isInside ? 1.0 : alphaFCM_;
        } );

        intersection = count == 0 ? -1 : ( count == array::product( orders ) ? 1 : 0 );
    }
    
    // Either distribute tensor product of weights or the weights in each axis
    if( intersection == 0 )
    {
        nd::executeWithIndex( orders, [&]( std::array<size_t, D> ijk, size_t i )
        {
            weights[i] *= array::product( array::extract( weightsGrid, ijk ) ) * detJ;
        } );
    }
    else
    {
        utilities::scaleVector( weightsGrid[0], detJ * ( intersection == 1 ? 1.0 : alphaFCM_ ) );
    }

    return intersection == 0;
}

template<size_t D>
void SpaceTreeQuadrature<D>::setNumberOfSeedPoints( size_t numberOfSeedPoints )
{
    numberOfSeedPoints_ = numberOfSeedPoints;
}

template<size_t D>
struct MomentFittingQuadrature<D>::Cache
{
    const MeshMapping<D>* mapping;

    size_t numberOfPartitions;

    CoordinateGrid<D> lagrangeEvaluation;
    CoordinateGrid<D> coordinateGrid;
    CoordinateGrid<D> weightsGrid;
    CoordinateList<D> coordinateList;
    std::vector<double> rhsWeights;
    QuadraturePointCache quadrature;

    QuadratureCache<D> spaceTreeCache;
};

template<size_t D>
MomentFittingQuadrature<D>::MomentFittingQuadrature( const ImplicitFunction<D>& function, 
                                                     double alpha, 
                                                     size_t depth,
                                                     size_t nseedpoints,
                                                     QuadratureOrderDeterminor<D> cutOrders ) :
    function_( function ), rhsPartitioner_( function, alpha, depth, nseedpoints ), cutOrders_( std::move( cutOrders ) )
{ }

template<size_t D>
QuadratureCache<D> MomentFittingQuadrature<D>::initialize( ) const
{
    Cache cache;

    cache.spaceTreeCache = rhsPartitioner_.initialize( );

    return cache;
}

template<size_t D>
size_t MomentFittingQuadrature<D>::partition( const MeshMapping<D>& mapping,
                                              QuadratureCache<D>& anyCache ) const
{
    MLHP_CHECK( mapping.type == CellType::NCube, "Moment fitting only works on n-cubes." );

    auto& data = utilities::cast<Cache>( anyCache );

    data.mapping = &mapping;
    data.numberOfPartitions = rhsPartitioner_.partition( mapping, data.spaceTreeCache );

    return 1;
}

template<size_t D>
bool MomentFittingQuadrature<D>::distribute( size_t,
                                             std::array<size_t, D> orders,
                                             CoordinateGrid<D>& rstGrid,
                                             CoordinateList<D>& xyzList,
                                             std::vector<double>& weights,
                                             QuadratureCache<D>& anyCache ) const
{
    auto& data = utilities::cast<Cache>( anyCache );

    if( data.numberOfPartitions == 1 )
    {
        rhsPartitioner_.distribute( 0, orders, rstGrid, xyzList, weights, data.spaceTreeCache );
    }
    else
    {
        // Number of points for which we are computing weights (the result of this function)
        auto morders = cutOrders_( data.mapping->icell, orders );

        // Number of points we are using to compute the weights (only in this function)
        auto qorders = orders;

        weights.resize( array::product( morders ) );
        xyzList.resize( array::product( morders ) );

        tensorProductQuadrature( morders, rstGrid, data.quadrature );

        std::fill( weights.begin( ), weights.end( ), 0.0 );

        for( size_t iPartition = 0; iPartition < data.numberOfPartitions; ++iPartition )
        {
            auto& subRst = data.coordinateGrid;
            auto& lagrange = data.lagrangeEvaluation;

            // Distribute tensor product of weights if cut, otherwise only distribute weights in each axis
            bool cut = rhsPartitioner_.distributeForMomentFitting( iPartition, qorders, subRst, data.weightsGrid,
                                                                   data.rhsWeights, data.spaceTreeCache );

            // Pre-evaluate all lagrange polynomials in each coordinate axis for each integration point
            for( size_t axis = 0; axis < D; ++axis )
            {
                lagrange[axis].resize( morders[axis] * qorders[axis] );

                if( qorders[axis] )
                {
                    polynomial::lagrange( morders[axis] - 1, qorders[axis], rstGrid[axis].data( ), subRst[axis].data( ), lagrange[axis].data( ) );
                }
            }

            // Loop over moment fitting points (on root cell) and add integral of associated Lagrange function
            nd::executeWithIndex( morders, [&]( std::array<size_t, D> ijk1, size_t index1 )
            {
                auto offsets = array::multiply( ijk1, qorders );

                // Integrate current Lagrage function by summing tensor product of leaf quadrature points
                if( cut )
                {
                    // Remove the innermost loop (that we add manually for performance)
                    auto slicedOrders = array::sliceIfNotOne( qorders, D - 1 );

                    nd::executeWithIndex( slicedOrders, [&]( decltype( slicedOrders ) ijk2, size_t index2 )
                    {
                        double shapes = 1.0;

                        // Pre compute N1 * N2 * ... Nd - 1
                        for( size_t axis = 0; axis < ijk2.size( ); ++axis )
                        {   
                            shapes *= lagrange[axis][offsets[axis] + ijk2[axis]];
                        }
                     
                        // Multiply with evaluations of Nd and the integration point weight
                        for( size_t iPoint = 0; iPoint < qorders[D - 1]; ++iPoint )
                        {
                            double value = shapes * lagrange[D - 1][offsets[D - 1] + iPoint];

                            weights[index1] += value * data.rhsWeights[index2 * qorders[D - 1] + iPoint];
                        }
                    } );
                }
                // If cell is not cut we can simplify this N-D integral to a product of 1-D integrals
                else
                {
                    double integralND = 1.0;

                    for( size_t axis = 0; axis < D; ++axis )
                    {
                        double integral1D = 0.0;

                        for( size_t iPoint = 0; iPoint < qorders[axis]; ++iPoint )
                        {
                            integral1D += lagrange[axis][offsets[axis] + iPoint] * data.weightsGrid[axis][iPoint];
                        }

                        integralND *= integral1D;
                    }

                    weights[index1] += integralND;
                }
            } );

        } // for iPartition

        nd::executeWithIndex( morders, [&]( std::array<size_t, D> ijk, size_t i )
        {
            auto [xyz, detJ] = map::withDetJ( *data.mapping, array::extract( rstGrid, ijk ) );

            xyzList[i] = xyz;
            weights[i] *= detJ;
        } );
    }

    return true;
}

template<size_t D>
void MomentFittingQuadrature<D>::setNumberOfSeedPoints( size_t numberOfSeedPoints )
{
    rhsPartitioner_.setNumberOfSeedPoints( numberOfSeedPoints );
}


template<size_t D>
CellmeshQuadrature<D>::CellmeshQuadrature( CellMeshCreator<D> meshCreator,
                                           spatial::ScalarFunction<D> scaling ) :
    meshCreator_ { std::move( meshCreator ) }, scaling_ { std::move( scaling ) }
{ }

template<size_t D>
struct CellmeshQuadrature<D>::Cache
{
    std::any meshCreatorCache;
    std::array<std::vector<double>, D> rst;
    std::vector<std::int64_t> connectivity;
    std::vector<std::int64_t> offsets;
    std::vector<std::int8_t> vtkTypes;
    bool isgrid;
    QuadraturePointCache quadratureCache;
    const AbsMapping<D>* mapping;
};

template<size_t D>
QuadratureCache<D> CellmeshQuadrature<D>::initialize( ) const
{
    return Cache { };
}

template<size_t D>
size_t CellmeshQuadrature<D>::partition( const MeshMapping<D>& mapping,
                                         QuadratureCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );

    MLHP_CHECK( mapping.type == CellType::NCube, "CellmeshQuadrature only implemented for NCube cells." );

    utilities::resize0( cache.rst, cache.connectivity, cache.offsets, cache.vtkTypes );

    cache.isgrid = meshCreator_( mapping, cache.rst, cache.connectivity, 
        cache.offsets, cache.vtkTypes, cache.meshCreatorCache );
    cache.mapping = &mapping;
        
    return cache.offsets.size( );
}
    
template<size_t D>
bool CellmeshQuadrature<D>::distribute( size_t ipartition,
                                        std::array<size_t, D> orders,
                                        CoordinateGrid<D>& rst,
                                        CoordinateList<D>& xyzList,
                                        std::vector<double>& weights,
                                        QuadratureCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );

    auto ivertexBegin = ipartition == 0 ? size_t { 0 } : static_cast<size_t>( cache.offsets[ipartition - 1] );

    auto mapAndAppendPoints = [&]( std::array<size_t, D + 1> indices, bool isgrid )
    {
        // Create mapping (use the fact that simplex mapping can also function as Cartesian mapping
        auto vertices = std::array<std::array<double, D>, D + 1> { };

        for( size_t i = 0; i < D + 1; ++i )
        {
            auto vertexIjk = array::makeSizes<D>( static_cast<size_t>( cache.connectivity[ivertexBegin + indices[i]] ) );

            vertexIjk = cache.isgrid ? nd::unravel( vertexIjk[0], array::elementSizes( cache.rst ) ) : vertexIjk;

            vertices[i] = array::extract( cache.rst, vertexIjk );
        }

        auto mapping = SimplexMapping<D, D> { vertices };

        // Map newly added points
        if( isgrid )
        {
            auto [rst0, J, detJ] = map::withJDetJ( mapping, array::make<D>( 0.0 ) );
            auto rst1 = mapping( array::make<D>( 1.0 ) );

            MLHP_CHECK( detJ >= -1e-12, "Negative determinant in CellMeshQuadrature (n-cube)." );

            detJ *= utilities::integerPow( 0.5, D );

            for( size_t axis1 = 0; axis1 < D; ++axis1 )
            {
                auto count = size_t { 0 };

                for( size_t axis2 = 0; axis2 < D; ++axis2 )
                {
                    count += std::abs( J[axis1 * D + axis2] ) > 1e-6;
                }

                MLHP_CHECK( count == 1, "Jacobian singular or not axis-aligned." );
            }

            for( size_t axis = 0; axis < D; ++axis )
            {
                for( auto& value : rst[axis] )
                {
                    value = 0.5 * ( value + 1.0 ) * ( rst1[axis] - rst0[axis] ) + rst0[axis];
                }
            }

            for( auto& weight : weights )
            {
                weight *= detJ;
            }

            mapQuadraturePointGrid( *cache.mapping, rst, xyzList, weights );
        }
        else
        {
            for( size_t ipoint = 0; ipoint < rst[0].size( ); ++ipoint )
            {
                auto [rst0, detJ] = map::withDetJ( mapping, array::extract( rst, array::make<D>( ipoint ) ) );

                MLHP_CHECK( detJ >= -1e-12, "Negative determinant in CellMeshQuadrature (simplex)." );

                for( size_t axis = 0; axis < D; ++axis )
                {
                    rst[axis][ipoint] = rst0[axis];
                }

                weights[ipoint] *= detJ;
            }

            mapQuadraturePointLists( *cache.mapping, rst, xyzList, weights );
        }

        for( size_t ipoint = 0; ipoint < xyzList.size( ); ++ipoint )
        {
            weights[ipoint] *= scaling_( xyzList[ipoint] );
        }

        return isgrid;
    };

    auto cellType = cache.vtkTypes[ipartition];
    auto indices = std::array<size_t, D + 1> { };

    for( size_t axis = 0; axis <= D; ++axis )
    {
        indices[axis] = axis;
    }

    if( ( D == 3 && cellType == 12 ) ||      // VTK_HEXAHEDRON
        ( D == 3 && cellType == 11 ) ||      // VTK_VOXEL
        ( D == 2 && cellType == 9  ) ||      // VTK_PIXEL
        ( D == 2 && cellType == 8  ) ||      // VTK_VOXEL
        ( D == 1 && cellType == 3  ) )       // VTK_LINE 
    {
        tensorProductQuadrature( orders, rst, weights, cache.quadratureCache );
        
        if constexpr( D == 3 ) if( cellType == 12 ) { indices[3] = 4; indices[2] = 3; }
        if constexpr( D == 3 ) if( cellType == 11 ) { indices[3] = 4; }
        if constexpr( D == 2 ) if( cellType == 9  ) { indices[2] = 3; }

        return mapAndAppendPoints( indices, true );
    }
    else if( ( D == 3 && cellType == 10 ) || // VTK_TETRA
             ( D == 2 && cellType == 5  ) )  // VTK_TRIANGLE
    {
        simplexQuadrature( orders, utilities::resize0( rst ), weights, cache.quadratureCache );

        return mapAndAppendPoints( indices, false );
    }
    else
    {
        MLHP_THROW( "VTK cell type " + std::to_string( cellType ) + " is not "
            "implemented in CellmeshQuadrature<" + std::to_string( D ) + ">." );
    }
}

template<size_t D>
struct StandardQuadrature<D>::Cache
{
    QuadraturePointCache quadrature;
    const AbsMapping<D>* mapping;
};

template<size_t D>
QuadratureCache<D> StandardQuadrature<D>::initialize( ) const
{
    return Cache { };
}

template<size_t D>
size_t StandardQuadrature<D>::partition( const MeshMapping<D>& mapping,
                                         QuadratureCache<D>& anyCache ) const
{
    utilities::cast<Cache>( anyCache ).mapping = &mapping;

    return 1;
}

template<size_t D>
bool StandardQuadrature<D>::distribute( size_t,
                                        std::array<size_t, D> orders,
                                        CoordinateGrid<D>& rst,
                                        CoordinateList<D>& xyz,
                                        std::vector<double>& weights,
                                        QuadratureCache<D>& anyCache ) const
{

    auto& data = utilities::cast<Cache>( anyCache );

    if( data.mapping->type == CellType::NCube )
    {
        tensorProductQuadrature( orders, rst, weights, data.quadrature );
        mapQuadraturePointGrid( *data.mapping, rst, xyz, weights );

        return true;
    }
    else
    {
        MLHP_CHECK( data.mapping->type == CellType::Simplex, "Unknown cell type" );
        
        simplexQuadrature<D>( orders, rst, weights, data.quadrature );
        mapQuadraturePointLists<D>( *data.mapping, rst, xyz, weights );

        return false;
    }
}

template<size_t D>
GridQuadrature<D>::GridQuadrature( std::array<size_t, D> nvoxels,
                                   const spatial::ScalarFunction<D>& scaling ) :
    nvoxels_ { [=]( CellIndex ) noexcept { return nvoxels; } }, scaling_ { scaling }
{ }

template<size_t D>
GridQuadrature<D>::GridQuadrature( memory::vptr<const AbsHierarchicalGrid<D>> grid,
                                   std::array<size_t, D> rootsubcells,
                                   const spatial::ScalarFunction<D>& scaling ) :
    GridQuadrature<D>( grid, rootsubcells, array::make<D>( NoValue<size_t> ), scaling )
{ }

template<size_t D>
GridQuadrature<D>::GridQuadrature( memory::vptr<const AbsHierarchicalGrid<D>> grid,
                                   std::array<size_t, D> rootsubcells,
                                   std::array<size_t, D> maxsubcells,
                                   const spatial::ScalarFunction<D>& scaling ) :
    scaling_ { scaling }
{
    nvoxels_ = [=]( CellIndex icell )
    {
        auto factor = utilities::binaryPow<size_t>( grid->refinementLevel( grid->fullIndex( icell ) ) );
        auto nvoxels = array::maxArray( array::divide( rootsubcells, factor ), array::makeSizes<D>( 1 ) );
        
        return array::minArray( nvoxels, maxsubcells );
    };
}

template<size_t D>
struct GridQuadrature<D>::Cache
{
    QuadraturePointCache quadrature;
    std::array<size_t, D> nvoxels;
    double detJ;
    const AbsMapping<D>* mapping;
};

template<size_t D>
QuadratureCache<D> GridQuadrature<D>::initialize( ) const
{
    return Cache { };
}

template<size_t D>
size_t GridQuadrature<D>::partition( const MeshMapping<D>& mapping,
                                     QuadratureCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );

    cache.mapping = &mapping;
    cache.nvoxels = nvoxels_( mapping.icell );
    cache.detJ = array::product( array::divide( 1.0, array::convert<double>( cache.nvoxels ) ) );

    return array::product( cache.nvoxels );
}

template<size_t D>
bool GridQuadrature<D>::distribute( size_t ipartition,
                                    std::array<size_t, D> orders,
                                    CoordinateGrid<D>& rst,
                                    CoordinateList<D>& xyz,
                                    std::vector<double>& weights,
                                    QuadratureCache<D>& anyCache ) const
{
    auto& data = utilities::cast<Cache>( anyCache );

    MLHP_CHECK( data.mapping->type == CellType::NCube, "Invalid cell type." );

    tensorProductQuadrature<D>( orders, rst, weights, data.quadrature );

    auto ijk = nd::unravel( ipartition, data.nvoxels );
    auto cellMapping = makeCartesianMappingSplitter( CartesianMapping<D>( ), data.nvoxels );
    auto subvoxelMapping = cellMapping( ijk );

    subvoxelMapping.mapGrid( rst );

    mapQuadraturePointGrid<D>( *data.mapping, rst, xyz, weights );

    for( size_t ipoint = 0; ipoint < weights.size( ); ++ipoint )
    {
        weights[ipoint] *= data.detJ * scaling_( xyz[ipoint] );
    }

    return true;
}

template<size_t D>
struct CachedQuadrature<D>::CellCache
{ 
    size_t npartitions = 0;

    std::vector<double> data = { };
    std::vector<size_t> offsets = { 0 };

    void addPartition( const CoordinateGrid<D>& rstGrid,
                       const CoordinateList<D>& xyzList,
                       const std::vector<double>& weights );

    void getPartition( size_t ipartition,
                       CoordinateGrid<D>& rstGrid,
                       CoordinateList<D>& xyzList,
                       std::vector<double>& weights );
};

template<size_t D>
void CachedQuadrature<D>::CellCache::addPartition( const CoordinateGrid<D>& rstGrid,
                                                   const CoordinateList<D>& xyzList,
                                                   const std::vector<double>& weights )
{
    offsets.resize( offsets.size( ) + D + 2 );

    auto rstOffsets = offsets.data( ) + offsets.size( ) - D - 3;
    auto& xyzOffset = offsets[offsets.size( ) - 3];
    auto& weightsOffset = offsets[offsets.size( ) - 2];

    for( size_t axis = 0; axis + 1 < D; ++axis )
    {
        rstOffsets[axis + 1] = rstOffsets[axis] + rstGrid[axis].size( );
    }
    
    xyzOffset = rstOffsets[D - 1] + rstGrid.back( ).size( );
    weightsOffset = xyzOffset + xyzList.size( ) * D;
    offsets.back( ) = weightsOffset + weights.size( );

    data.resize( offsets.back( ) );
    
    for( size_t axis = 0; axis < D; ++axis )
    {
        std::copy( rstGrid[axis].begin( ), rstGrid[axis].end( ), data.begin( ) + 
            static_cast<std::ptrdiff_t>( rstOffsets[axis] ) );
    }
    
    for( size_t ipoint = 0; ipoint < xyzList.size( ); ++ipoint )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            data[xyzOffset + D * ipoint + axis] = xyzList[ipoint][axis];
        }
    }
    
    std::copy( weights.begin( ), weights.end( ), data.begin( ) + 
        static_cast<std::ptrdiff_t>( weightsOffset ) );
}

template<size_t D>
void CachedQuadrature<D>::CellCache::getPartition( size_t ipartition,
                                                   CoordinateGrid<D>& rstGrid,
                                                   CoordinateList<D>& xyzList,
                                                   std::vector<double>& weights )
{
    auto begin = ipartition * ( D + 2 );
    auto rstOffsets = offsets.data( ) + begin;
    auto xyzOffset = offsets[begin + D];
    auto weightsOffset = offsets[begin + D + 1];
        
    for( size_t axis = 0; axis < D; ++axis )
    {
        rstGrid[axis].resize( rstOffsets[axis + 1] - rstOffsets[axis] );

        std::copy( data.begin( ) + static_cast<std::ptrdiff_t>( rstOffsets[axis] ),
                   data.begin( ) + static_cast<std::ptrdiff_t>( rstOffsets[axis + 1] ),
                   rstGrid[axis].begin( ) );
    }

    xyzList.resize( ( weightsOffset - xyzOffset ) / D );
    weights.resize( xyzList.size( ) );

    for( size_t ipoint = 0; ipoint < xyzList.size( ); ++ipoint )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            xyzList[ipoint][axis] = data[xyzOffset + D * ipoint + axis];
        }
    }

    std::copy( data.begin( ) + static_cast<std::ptrdiff_t>( weightsOffset ), 
               data.begin( ) + static_cast<std::ptrdiff_t>( weightsOffset + xyzList.size( ) ),
               weights.begin( ) );
}

template<size_t D>
CachedQuadrature<D>::CachedQuadrature( const AbsMesh<D>& mesh, 
                                       const std::vector<std::array<size_t, D>>& degrees,
                                       const AbsQuadrature<D>& partitioner ) :
    points_ { std::make_shared<std::vector<CellCache>>( mesh.ncells( ) ) },
    data_( 0 ), offsets_( 0 ), partitions_( mesh.ncells( ) + 1, 0 )
{
    auto ncells = mesh.ncells( );
    
    [[maybe_unused]]
    auto chunksize = parallel::clampChunksize( ncells, 64 );

    MLHP_CHECK( degrees.size( ) == ncells, "Inconsistent sizes." );
    
    #pragma omp parallel
    {
        auto partitionerCache = partitioner.initialize( );
        auto mapping = mesh.createMapping( );
        auto rstGrid = CoordinateGrid<D> { };
        auto xyzList = CoordinateList<D> { };
        auto weights = std::vector<double>{ };
        auto data = std::vector<double> { };
        auto sizes = std::vector<size_t> { };
        auto cells = std::vector<CellIndex>{ };

        #pragma omp for schedule(dynamic, chunksize)
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( ncells ); ++ii )
        {
            auto icell = static_cast<CellIndex>( ii );
        
            cells.push_back( icell );

            mesh.prepareMapping( icell, mapping );

            partitions_[icell + 1] = partitioner.partition( mapping, partitionerCache );

            for( size_t ipartition = 0; ipartition < partitions_[icell + 1]; ++ipartition )
            {
                auto isGrid = partitioner.distribute( ipartition, degrees[icell], 
                    rstGrid, xyzList, weights, partitionerCache );

                MLHP_CHECK( isGrid, "Does cached integration partitioner work for non-grids?" );

                size_t id = sizes.size( );

                sizes.resize( id + D + 2 );

                for( size_t axis = 0; axis < D; ++axis )
                {
                    sizes[id + axis] = rstGrid[axis].size( );
                }

                sizes[id + D + 0] = xyzList.size( ) * D;
                sizes[id + D + 1] = weights.size( );

                auto offsets = std::array<size_t, D + 3> { 0 };

                std::partial_sum( sizes.data( ) + id, sizes.data( ) + id + D + 2, offsets.data( ) + 1 );

                offsets = array::add( offsets, data.size( ) );

                data.resize( offsets.back( ) );
                    
                for( size_t axis = 0; axis < D; ++axis )
                {
                    std::copy( rstGrid[axis].begin( ), rstGrid[axis].end( ), data.data( ) + offsets[axis] );
                }
                    
                for( size_t ipoint = 0; ipoint < xyzList.size( ); ++ipoint )
                {
                    for( size_t axis = 0; axis < D; ++axis )
                    {
                        data[offsets[D] + D * ipoint + axis] = xyzList[ipoint][axis];
                    }
                }
                
                std::copy( weights.begin( ), weights.end( ), data.data( ) + offsets[D + 1] );
            }

        } // for ii
        
        #pragma omp barrier
        { }

        #pragma omp single
        {
            std::partial_sum( partitions_.begin( ), partitions_.end( ), partitions_.begin( ) );

            offsets_.resize( partitions_.back( ) * ( D + 2 ) + 1 );
        }

        size_t offset = 0;

        for( auto icell : cells )
        {
            for( auto ipartition = partitions_[icell]; ipartition < partitions_[icell + 1]; ++ipartition )
            {
                for( size_t i = 0; i < D + 2; ++i )
                {
                    offsets_[ipartition * ( D + 2 ) + i + 1] = sizes[offset++];
                }
            }
        }
        
        #pragma omp barrier
        { }

        #pragma omp single
        {
            std::partial_sum( offsets_.begin( ), offsets_.end( ), offsets_.begin( ) );

            data_.resize( offsets_.back( ) );
        }

        offset = 0;

        for( auto icell : cells )
        {
            for( auto ipartition = partitions_[icell]; ipartition < partitions_[icell + 1]; ++ipartition )
            {
                auto offset0 = offsets_[( D + 2 ) * ipartition];
                auto offset1 = offsets_[( D + 2 ) * ( ipartition + 1 )];
                auto size = offset1 - offset0;

                std::copy( data.data( ) + offset, data.data( ) + offset + size, data_.data( ) + offset0 );
               
                offset += size;
            }
        }
    } // omp parallel 
}

template<size_t D>
QuadratureCache<D> CachedQuadrature<D>::initialize( ) const
{
    return CellIndex { 0 };
}

template<size_t D>
size_t CachedQuadrature<D>::partition( const MeshMapping<D>& mapping,
                                       QuadratureCache<D>& anyCache ) const 
{
    MLHP_CHECK( mapping.type == CellType::NCube, "Does cached integration partitioner work for non-grids?" );

    auto& icell = utilities::cast<CellIndex>( anyCache );

    icell = mapping.icell;

    return partitions_[icell + 1] - partitions_[icell];
}

template<size_t D>
bool CachedQuadrature<D>::distribute( size_t ipartition,
                                      std::array<size_t, D>,
                                      CoordinateGrid<D>& rstGrid,
                                      CoordinateList<D>& xyzList,
                                      std::vector<double>& weights,
                                      QuadratureCache<D>& anyCache ) const 
{
    auto cellOffset = partitions_[utilities::cast<CellIndex>( anyCache )] + ipartition;
    auto offsets = offsets_.data( ) + ( cellOffset + ipartition ) * ( D + 2 );

    for( size_t axis = 0; axis < D; ++axis )
    {
        rstGrid[axis].resize( offsets[axis + 1] - offsets[axis] );

        std::copy( data_.data( ) + offsets[axis], data_.data( ) + 
            offsets[axis + 1], rstGrid[axis].begin( ) );
    }

    xyzList.resize( ( offsets[D + 1] - offsets[D] ) / D );
    weights.resize( xyzList.size( ) );
    
    for( size_t ipoint = 0; ipoint < xyzList.size( ); ++ipoint )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            xyzList[ipoint][axis] = data_[offsets[D] + D * ipoint + axis];
        }
    }
    
    std::copy( data_.data( ) + offsets[D + 1], data_.data( ) + 
        offsets[D + 2], weights.begin( ) );

    return true;
}

template<size_t D>
MeshProjectionQuadrature<D>::MeshProjectionQuadrature( memory::vptr<const AbsHierarchicalGrid<D>> otherMesh,
                                                       memory::vptr<const AbsQuadrature<D>> partitioner,
                                                       size_t maxdepth ) :
    otherMesh_ { std::move( otherMesh ) }, partitioner_{ std::move( partitioner ) }, maxdepth_{ maxdepth }
{ }

template<size_t D>
QuadratureCache<D> MeshProjectionQuadrature<D>::initialize( ) const
{
    return Cache { };
}

template<size_t D>
size_t cacheQuadratureCells( const AbsQuadrature<D>& quadrature,
                             const MeshMapping<D>& globalMapping,
                             std::span<const AbsMapping<D>*> submappings, 
                             std::vector<SubcellCache<D>>& subcellData,
                             std::vector<size_t>& mapToSubcell )
{
    // Resize and initialize cache
    auto nsubcells = submappings.size( );
    auto previousSize = subcellData.size( );

    mapToSubcell.resize( 0 );
    subcellData.resize( std::max( nsubcells, previousSize ) );

    for( size_t isubcell = previousSize; isubcell < nsubcells; ++isubcell )
    {
        subcellData[isubcell].quadratureCache = quadrature.initialize( );
        subcellData[isubcell].globalMapping.mapping = std::make_shared<ConcatenatedMapping<D>>( );
    }

    auto offset = size_t { 0 };

     // For each subcell: prepare mapping, partition subcell, append to backward index map
     for( size_t isubcell = 0; isubcell < nsubcells; ++isubcell )
     {
         auto& [meshMapping, quadratureCache, npartitions] = subcellData[isubcell];
         auto& concatenatedMapping = static_cast<ConcatenatedMapping<D>&>( *meshMapping.mapping.get( ) );

         concatenatedMapping.globalMapping = &globalMapping;
         concatenatedMapping.localMapping = submappings[isubcell];

         meshMapping.mesh = globalMapping.mesh;
         meshMapping.icell = globalMapping.icell;

         npartitions = quadrature.partition( meshMapping, quadratureCache );

         mapToSubcell.resize( mapToSubcell.size( ) + npartitions, isubcell );

         std::swap( npartitions, offset );
         offset += npartitions;
     }

     return offset;
}

template<size_t D>
struct MeshProjectionQuadrature<D>::Cache
{
    std::vector<mesh::SharedSupport<D>> cells;
    std::vector<const AbsMapping<D>*> submappings;

    std::vector<SubcellCache<D>> data;
    std::vector<size_t> mapToSubcell;
};

template<size_t D>
size_t MeshProjectionQuadrature<D>::partition( const MeshMapping<D>& mapping,
                                               QuadratureCache<D>& anyCache ) const
{
    auto mesh = dynamic_cast<const AbsHierarchicalGrid<D>*>( mapping.mesh );

    MLHP_CHECK( mapping.type == CellType::NCube, "Mesh intersection only works on grids." );
    MLHP_CHECK( mesh != nullptr && mesh->baseGrid( ).ncells( ) == otherMesh_->baseGrid( ).ncells( ),
                "Mesh intersection requires identical base meshes." );

    auto& cache = utilities::cast<Cache>( anyCache );

    cache.cells.resize( 0 );
    cache.mapToSubcell.resize( 0 );

    // Generate partitions 
    mesh::findInOtherGrid( *mesh, *otherMesh_, cache.cells, mesh->fullIndex( mapping.icell ), maxdepth_ );

    // Store pointers to the mappings into this cell
    cache.submappings.resize( cache.cells.size( ) );

    auto predicate = []( auto& shared ) { return &shared.thisCell; };

    std::transform( cache.cells.begin( ), cache.cells.end( ), cache.submappings.begin( ), predicate );

    // Partition each subcell
    return cacheQuadratureCells<D>( *partitioner_, mapping, cache.submappings, cache.data, cache.mapToSubcell );
}

template<size_t D>
CellIndex MeshProjectionQuadrature<D>::distribute( size_t ipartition,
                                                   std::array<size_t, D> orders,
                                                   CoordinateGrid<D>& thisRstGrid,
                                                   CoordinateGrid<D>& otherRstGrid,
                                                   CoordinateList<D>& xyzList,
                                                   std::vector<double>& weights,
                                                   QuadratureCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );
    auto& isubcell = cache.mapToSubcell[ipartition];
    auto& [meshMapping, quadratureCache, offset] = cache.data[isubcell];

    auto isgrid = partitioner_->distribute( ipartition - offset, orders, 
        thisRstGrid, xyzList, weights, quadratureCache );

    MLHP_CHECK( isgrid, "MeshProjectionQuadrature only implemented for grid partitioners." );

    std::copy( thisRstGrid.begin( ), thisRstGrid.end( ), otherRstGrid.begin( ) );

    cache.cells[isubcell].thisCell.mapGrid( thisRstGrid );
    cache.cells[isubcell].otherCell.mapGrid( otherRstGrid );

    return cache.cells[isubcell].otherIndex;
}

template<size_t D>
bool MeshProjectionQuadrature<D>::distribute( size_t ipartition,
                                              std::array<size_t, D> orders,
                                              CoordinateGrid<D>& rstGrid,
                                              CoordinateList<D>& xyzList,
                                              std::vector<double>& weights,
                                              QuadratureCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );
    auto& isubcell = cache.mapToSubcell[ipartition];
    auto& [meshMapping, quadratureCache, offset] = cache.data[isubcell];

    auto isgrid = partitioner_->distribute( ipartition - offset, 
        orders, rstGrid, xyzList, weights, quadratureCache );

    MLHP_CHECK( isgrid, "Quadrature points must be a grid." );

    cache.cells[isubcell].thisCell.mapGrid( rstGrid );

    return true;
}

#define MLHP_INSTANTIATE_DIM( D )                                             \
                                                                              \
    template class SpaceTreeQuadrature<D>;                                    \
    template class MomentFittingQuadrature<D>;                                \
    template class CellmeshQuadrature<D>;                                     \
    template class StandardQuadrature<D>;                                     \
    template class GridQuadrature<D>;                                         \
    template class CachedQuadrature<D>;                                       \
    template class MeshProjectionQuadrature<D>;                               \
                                                                              \
    template MLHP_EXPORT                                                      \
    QuadratureOrderDeterminor<D> relativeQuadratureOrder( int offset,         \
                                                          double factor );    \
                                                                              \
    template MLHP_EXPORT                                                      \
    QuadratureOrderDeterminor<D> absoluteQuadratureOrder(                     \
                                              std::array<size_t, D> orders ); \
                                                                              \
    template MLHP_EXPORT                                                      \
    void mapQuadraturePointGrid( const AbsMapping<D>& mapping,                \
                                 const CoordinateGrid<D>& rstGrid,            \
                                 CoordinateList<D>& xyzList,                  \
                                 std::vector<double>& weights );              \
                                                                              \
    template MLHP_EXPORT                                                      \
    void mapQuadraturePointLists( const AbsMapping<D>& mapping,               \
                                  const CoordinateGrid<D>& rst,               \
                                  CoordinateList<D>& xyzList,                 \
                                  std::vector<double>& weights );             \
                                                                              \
    template MLHP_EXPORT                                                      \
    EvaluateQuadratureResult<D> evaluateQuadrature( const AbsQuadrature<D>&,  \
                                                    const AbsMesh<D>& mesh,   \
                                                    CellIndex icell,          \
                                                    std::array<size_t, D> );  \
                                                                              \
    template MLHP_EXPORT                                                      \
    EvaluateQuadrature2Result<D> evaluateQuadrature(                          \
                                    const AbsQuadratureOnMesh<D>& quadrature, \
                                    const AbsMesh<D>& mesh,                   \
                                    CellIndex icell,                          \
                                    std::array<size_t, D> orders );           \
                                                                              \
    template MLHP_EXPORT                                                      \
    void generateSpaceTreeLeaves( const ImplicitFunction<D>& function,        \
                                  const AbsMapping<D>& mapping,               \
                                  size_t depth,                               \
                                  size_t nseedpoints,                         \
                                  std::vector<CartesianMapping<D>>& cells,    \
                                  std::vector<int>& cutState,                 \
                                  bool computeCutStateOfFinestCells );        \
                                                                              \
    template MLHP_EXPORT                                                      \
    void generateSpaceTreeLeaves( const ImplicitFunction<D>& function,        \
                                  const AbsMapping<D>& mapping,               \
                                  size_t depth,                               \
                                  size_t nseedpoints,                         \
                                  std::vector<CartesianMapping<D>>& cells );  \
                                                                              \
    template MLHP_EXPORT                                                      \
    size_t cacheQuadratureCells( const AbsQuadrature<D>& quadrature,          \
                                 const MeshMapping<D>& globalMapping,         \
                                 std::span<const AbsMapping<D>*> submappings, \
                                 std::vector<SubcellCache<D>>& subcellData,   \
                                 std::vector<size_t>& mapToSubcell );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // mlhp
