// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/quadrature.hpp"
#include "mlhp/core/refinement.hpp"
#include "mlhp/core/integrands.hpp"
#include "mlhp/core/algorithm.hpp"
#include "mlhp/core/dense.hpp"
#include "mlhp/core/sparse.hpp"

#include <array>

namespace mlhp
{
namespace
{

class LinearSystemScatterKernel
{
public:
    explicit LinearSystemScatterKernel( DofIndex ndof );

    LinearSystemScatterKernel( const DofIndicesValuesPair& boundaryDofs,
                               DofIndex ndof );

    // Sorted is a thread-safe temporary storage for sorting the location map
    template<typename ElementMatrixTag, typename SystemMatrixType>
    void scatter( SystemMatrixType& globalMatrix,
                  std::vector<double>& globalVector,
                  const AlignedDoubleVector& elementMatrix,
                  const AlignedDoubleVector& elementVector,
                  const LocationMap& locationMap,
                  std::vector<size_t>& sorted ) const;

    // Sorted is a thread-safe temporary storage for sorting the location map
    template<typename ElementMatrixTag, typename SystemMatrixType>
    void scatterLhs( SystemMatrixType& globalMatrix,
                     const AlignedDoubleVector& elementMatrix,
                     const LocationMap& locationMap,
                     std::vector<size_t>& sorted ) const;

    void scatterRhs( std::vector<double>& globalVector,
                     const AlignedDoubleVector& elementVector,
                     const LocationMap& locationMap ) const;

private:
    std::vector<bool> boundaryDofsMask;
    DofIndexVector boundaryDofMap;
    std::vector<double> dofValues;
};

template<typename T>
auto& getGlobalMatrix( const AssemblyTarget& target )
{
    return std::get<std::reference_wrapper<T>>( target ).get( );
}

auto& getGlobalVector( const AssemblyTarget& target )
{
    return std::get<std::reference_wrapper<std::vector<double>>>( target ).get( );
}

auto& getGlobalScalar( const AssemblyTarget& target )
{
    return std::get<std::reference_wrapper<double>>( target ).get( );
}

auto targetSize( const AssemblyTarget& target )
{
    if( target.index( ) == 0 ) return size_t { 1 };
    else if( target.index( ) == 1 ) return getGlobalVector( target ).size( );
    else if( target.index( ) == 2 ) 
        return static_cast<size_t>( getGlobalMatrix<linalg::UnsymmetricSparseMatrix>( target ).size1( ) );
    else 
        return static_cast<size_t>( getGlobalMatrix<linalg::SymmetricSparseMatrix>( target ).size1( ) );
}

} // namespace

auto checkConsistency( const AssemblyTypeVector& integrandTypes,
                       const AssemblyTargetVector& globalTargets )
{
    if( integrandTypes.size( ) != globalTargets.size( ) )
    {
        MLHP_THROW( "The number of targets specified by integrand (n = " + 
            std::to_string( integrandTypes.size( ) ) + ") differs from the number "
            "of global targets given to the assembly (n = " + 
            std::to_string( globalTargets.size( ) ) + ")." );
    }

    for( size_t iTarget = 0; iTarget < globalTargets.size( ); ++iTarget )
    {
        auto type1 = globalTargets[iTarget].index( );
        auto type2 = static_cast<size_t>( integrandTypes[iTarget] );

        if( type1 != type2 && ( type1 != 2 || type2 != 3 ) )
        {
            MLHP_THROW( "Global assembly target at index " + std::to_string( iTarget ) + 
                " (type " + std::to_string( type1 ) + ") is inconsistent with integrand target" + 
                " (type " + std::to_string( type2 ) + ")." );
        }
    }
}

void initializeLocalAssemblyTargets( AlignedDoubleVectors& targets, 
                                     const AssemblyTypeVector& types, 
                                     size_t ndofElement )
{
    for( size_t i = 0; i < types.size( ); ++i )
    {
        auto type = static_cast<size_t>( types[i] );

        if( type == 0 ) targets[i].resize( 1 );
        if( type == 1 ) targets[i].resize( memory::paddedLength<double>( ndofElement ) );
        if( type == 2 ) targets[i].resize( linalg::denseMatrixStorageSize<linalg::UnsymmetricDenseMatrix>( ndofElement ) );
        if( type == 3 ) targets[i].resize( linalg::denseMatrixStorageSize<linalg::SymmetricDenseMatrix>( ndofElement ) );

        std::fill( targets[i].begin( ), targets[i].end( ), 0.0 );
    }
}

AssemblyKernel makeAssemblyKernel( const AssemblyTargetVector& globalTargets,
                                   const AssemblyTypeVector& localTypes,
                                   const DofIndicesValuesPair& boundaryDofs,
                                   DofIndex ndofAll )
{
    MLHP_CHECK( globalTargets.size( ) == localTypes.size( ), "Number of integrand target types (n = " + 
        std::to_string( localTypes.size( ) ) + ") differs from the number of assembly targets (n = " + 
        std::to_string( globalTargets.size( ) ) + ")." );

    std::vector<std::array<size_t, 2>> linearSystems;

    if( globalTargets.size( ) == 2 && globalTargets[0].index( ) >= 2 && globalTargets[1].index( ) == 1 )
    {
        linearSystems = { { 0, 1 } };
    }

    auto nsystems = linearSystems.size( );
    auto ntargets = globalTargets.size( );

    checkConsistency( localTypes, globalTargets );

    MLHP_CHECK( nsystems * 2 <= ntargets, "More linear system pairs than global targets given." );

    std::vector<size_t> order( ntargets );

    std::iota( order.begin( ), order.end( ), size_t { 0 } );

    for( auto [matrixIndex, vectorIndex] : linearSystems )
    {
        if( !( matrixIndex < ntargets && globalTargets[matrixIndex].index( ) >= 2 &&
               vectorIndex < ntargets && globalTargets[vectorIndex].index( ) == 1 ) )
        {
            MLHP_THROW( "Invalid linear system indices in assembly." );
        }

        auto matrixEntry = std::find( order.begin( ), order.end( ), matrixIndex );
        auto vectorEntry = std::find( order.begin( ), order.end( ), vectorIndex );

        std::move( matrixEntry, matrixEntry + 1, order.begin( ) );
        std::move( vectorEntry, vectorEntry + 1, order.begin( ) + 1 );
    }

    LinearSystemScatterKernel scatter { 0 };

    for( size_t i = 0; i < globalTargets.size( ); ++i )
    {
        if( globalTargets[i].index( ) != 0 )
        {
            auto tsize = targetSize( globalTargets[i] );
            auto bsize = boundaryDofs.first.size( );

            if( tsize + bsize != ndofAll )
            {
                MLHP_THROW( "The size of the assembly target at index " + std::to_string( i ) + " (n = " + 
                    std::to_string( tsize ) + ") plus the number of constrained dofs (n = " + 
                    std::to_string( bsize ) + ") must be equal to the total number of dofs (n = " + 
                    std::to_string( ndofAll ) + ")." );
            }

            scatter = LinearSystemScatterKernel { boundaryDofs, ndofAll };

            break;
        }
    }

    return [=, scatter = std::move(scatter)]
           ( const AlignedDoubleVectors& localTargets,
             const LocationMap& locationMap,
             std::vector<size_t>& sortedIndices )
    { 
        using UE = linalg::UnsymmetricDenseMatrix; using SE = linalg::SymmetricDenseMatrix;
        using UG = linalg::UnsymmetricSparseMatrix; using SG = linalg::SymmetricSparseMatrix;

        for( size_t isystem = 0; isystem < nsystems; ++isystem )
        {
            auto matrixIndex = order[isystem * 2 + 0];
            auto vectorIndex = order[isystem * 2 + 1];

            auto globalType = globalTargets[matrixIndex].index( );
            auto localType = static_cast<size_t>( localTypes[matrixIndex] );

            auto scatterSystem = [&]<typename ET1, typename GT1>( ) 
            { 
                scatter.scatter<ET1, GT1>( getGlobalMatrix<GT1>( globalTargets[matrixIndex] ), 
                    getGlobalVector( globalTargets[vectorIndex] ), localTargets[matrixIndex], 
                    localTargets[vectorIndex], locationMap, sortedIndices ); 
            };

            if( localType == 2 && globalType == 2 ) scatterSystem.template operator()<UE, UG>( );
            if( localType == 2 && globalType == 3 ) MLHP_THROW( "Incompatible matrix types." );
            if( localType == 3 && globalType == 2 ) scatterSystem.template operator()<SE, UG>( );
            if( localType == 3 && globalType == 3 ) scatterSystem.template operator()<SE, SG>( );
        }

        for( size_t itarget = 2 * nsystems; itarget < ntargets; ++itarget )
        {
            auto targetIndex = order[itarget];

            if( auto globalType = globalTargets[targetIndex].index( ); globalType == 0 )
            {
                auto& globalTarget = getGlobalScalar( globalTargets[targetIndex] );
                auto& localTarget = localTargets[targetIndex][0];

                #pragma omp atomic
                globalTarget += localTarget;
            }
            else if( globalType == 1 )
            {
                scatter.scatterRhs( getGlobalVector( globalTargets[targetIndex] ), 
                                    localTargets[targetIndex], locationMap );
            }
            else
            {
                auto localType = static_cast<size_t>( localTypes[targetIndex] );

                auto scatterLhs = [&]<typename ET2, typename GT2>( ) 
                { 
                    scatter.scatterLhs<ET2, GT2>( getGlobalMatrix<GT2>( globalTargets[targetIndex] ), 
                                                  localTargets[targetIndex], locationMap, sortedIndices ); 
                };

                if( localType == 2 && globalType == 2 ) scatterLhs.template operator()<UE, UG>( );
                if( localType == 2 && globalType == 3 ) MLHP_THROW( "Incompatible matrix types." );
                if( localType == 3 && globalType == 2 ) scatterLhs.template operator()<SE, UG>( );
                if( localType == 3 && globalType == 3 ) scatterLhs.template operator()<SE, SG>( );
            }
        }
    };
}

template<size_t D>
void integrateOnDomain( const AbsBasis<D>& basis,
                        const DomainIntegrand<D>& integrand,
                        const AssemblyTargetVector& globalTargets,
                        const AbsQuadrature<D>& quadrature,
                        const QuadratureOrderDeterminor<D>& orderDeterminor,
                        const DofIndicesValuesPair& boundaryDofs,
                        [[maybe_unused]] size_t chunksize )
{
    auto assemble = makeAssemblyKernel( globalTargets, integrand.types, boundaryDofs, basis.ndof( ) );
    auto diffOrder = std::max( static_cast<size_t>( integrand.maxdiff ) + 1, size_t { 1 } ) - 1;
    auto nelements = static_cast<std::int64_t>( basis.nelements( ) );

    #pragma omp parallel
    {
        auto rst = CoordinateGrid<D> { };
        auto xyz = CoordinateList<D> { };
        auto weights = std::vector<double> { };
        auto locationMap = LocationMap { };
        auto sortedIndices = std::vector<size_t> { };
        auto shapes = BasisFunctionEvaluation<D> { };
        auto localTargets = AlignedDoubleVectors { globalTargets.size( ) };
        auto quadratureCache = quadrature.initialize( );
        auto basisCache = basis.createEvaluationCache( );
        auto integrandCache = integrand.createCache( basis );

        #pragma omp for schedule( dynamic, chunksize )
        for( std::int64_t ii = 0; ii < nelements; ++ii )
        {
            auto iElement = static_cast<CellIndex>( ii );

            utilities::resize0( locationMap, sortedIndices );

            auto maxdegrees = basis.prepareEvaluation( iElement, diffOrder, shapes, basisCache );
            auto& mapping = basis.mapping( basisCache );
            auto npartitions = quadrature.partition( mapping, quadratureCache );
            auto accuracy = orderDeterminor( iElement, maxdegrees );

            basis.locationMap( iElement, locationMap );
            integrand.prepare( integrandCache, mapping, locationMap );

            initializeLocalAssemblyTargets( localTargets, integrand.types, locationMap.size( ) );

            for( size_t ipartition = 0; ipartition < npartitions; ++ipartition )
            {
                utilities::resize0( rst, xyz, weights );

                auto isGrid = quadrature.distribute( ipartition, 
                    accuracy, rst, xyz, weights, quadratureCache );

                if( isGrid )
                {
                    basis.prepareGridEvaluation( rst, basisCache );

                    nd::executeWithIndex( array::elementSizes( rst ), [&]( auto ijk, auto index )
                    {
                        basis.evaluateGridPoint( ijk, shapes, basisCache );
                        integrand.evaluate( integrandCache, shapes, localTargets, weights[index] );
                    } );
                }
                else
                {
                    for( size_t index = 0; index < rst[0].size( ); ++index )
                    {
                        auto ijk = array::makeSizes<D>( index );

                        basis.evaluateSinglePoint( array::extract( rst, ijk ), shapes, basisCache );
                        integrand.evaluate( integrandCache, shapes, localTargets, weights[index] );
                    }
                }
            }

            assemble( localTargets, locationMap, sortedIndices );
        }
    }
}

template<size_t D>
void integrateOnDomain( const MultilevelHpBasis<D>& basis0,
                        const MultilevelHpBasis<D>& basis1,
                        const BasisProjectionIntegrand<D>& integrand,
                        const AssemblyTargetVector& globalTargets,
                        const AbsQuadrature<D>& quadrature,
                        const QuadratureOrderDeterminor<D>& orderDeterminor,
                        const DofIndicesValuesPair& boundaryDofs,
                        [[maybe_unused]] size_t chunksize )
{
    auto assemble = makeAssemblyKernel( globalTargets, integrand.types( ), boundaryDofs, basis1.ndof( ) );
    auto diffOrder = std::max( static_cast<size_t>( integrand.diffOrder( ) ) + 1, size_t { 1 } ) - 1;
    auto nelements = static_cast<std::int64_t>( basis1.nelements( ) );
    auto integrandTypes = integrand.types( );

    auto intersectionPartitioner = MeshProjectionQuadrature<D>( basis0.hierarchicalGrid( ), quadrature );

    #pragma omp parallel
    {
        auto rst0 = CoordinateGrid<D> { };
        auto rst1 = CoordinateGrid<D> { };
        auto xyz = CoordinateList<D> { };
        auto weights = std::vector<double> { };
        auto locationMap0 = LocationMap { };
        auto locationMap1 = LocationMap { };
        auto sortedIndices = std::vector<size_t> { };
        auto shapes0 = BasisFunctionEvaluation<D> { };
        auto shapes1 = BasisFunctionEvaluation<D> { };
        auto localTargets = AlignedDoubleVectors { globalTargets.size( ) };
        auto quadratureCache = intersectionPartitioner.initialize( );
        auto basisCache0 = basis0.createEvaluationCache( );
        auto basisCache1 = basis1.createEvaluationCache( );

        #pragma omp for schedule( dynamic, chunksize )
        for( std::int64_t iiElement = 0; iiElement < nelements; ++iiElement )
        {
            auto iElement1 = static_cast<CellIndex>( iiElement );
            
            utilities::resize0( locationMap1, sortedIndices );

            basis1.locationMap( iElement1, locationMap1 );

            auto maxdegrees = basis1.prepareEvaluation( iElement1, diffOrder, shapes1, basisCache1 );
            auto npartitions = intersectionPartitioner.partition( basis1.mapping( basisCache1 ), quadratureCache );
            auto accuracy = orderDeterminor( iElement1, maxdegrees );

            initializeLocalAssemblyTargets( localTargets, integrandTypes, locationMap1.size( ) );

            for( size_t ipartition = 0; ipartition < npartitions; ++ipartition )
            {
                utilities::resize0( locationMap0, rst0, rst1, xyz, weights );

                auto iFullIndex0 = intersectionPartitioner.distribute( ipartition, 
                    accuracy, rst1, rst0, xyz, weights, quadratureCache );

                auto iElement0 = basis0.hierarchicalGrid( ).leafIndex( iFullIndex0 );

                basis0.locationMap( iElement0, locationMap0 );
                basis0.prepareEvaluation( iElement0, diffOrder, shapes0, basisCache0 );
                basis0.prepareGridEvaluation( rst0, basisCache0 );
                basis1.prepareGridEvaluation( rst1, basisCache1 );

                nd::executeWithIndex( array::elementSizes( rst1 ), [&]( std::array<size_t, D> ijk, size_t index )
                {
                    basis0.evaluateGridPoint( ijk, shapes0, basisCache0 );
                    basis1.evaluateGridPoint( ijk, shapes1, basisCache1 );

                    integrand.evaluate( locationMap0, locationMap1, shapes0, shapes1, localTargets, weights[index] );
                } );
            }

            assemble( localTargets, locationMap1, sortedIndices );
        }
    }
}


template<size_t D>
void integrateOnSurface( const AbsBasis<D>& basis,
                         const SurfaceIntegrand<D>& integrand,
                         const AbsQuadratureOnMesh<D>& generator,
                         const AssemblyTargetVector& globalTargets,
                         const DofIndicesValuesPair& boundaryDofs,
                         [[maybe_unused]] size_t chunksize )
{
    auto& mesh = basis.mesh( );
    auto assemble = makeAssemblyKernel( globalTargets, integrand.types, boundaryDofs, basis.ndof( ) );
    auto diffOrder = std::max( static_cast<size_t>( integrand.maxdiff ) + 1, size_t { 1 } ) - 1;
    auto nelements = static_cast<std::int64_t>( basis.nelements( ) );

    #pragma omp parallel
    {
        auto rst = CoordinateList<D>{ };
        auto normals = CoordinateList<D>{ };
        auto weights = std::vector<double> { };
        auto locationMap = LocationMap { };
        auto sortedIndices = std::vector<size_t> { };
        auto shapes = BasisFunctionEvaluation<D> { };
        auto localTargets = AlignedDoubleVectors { globalTargets.size( ) };
        auto basisCache = basis.createEvaluationCache( );
        auto integrandCache = integrand.createCache( basis );
        auto quadratureCache = generator.initialize( );
        auto mapping = mesh.createMapping( );

        #pragma omp for schedule( dynamic, chunksize )
        for( std::int64_t ii = 0; ii < nelements; ++ii )
        {
            auto ielement = static_cast<CellIndex>( ii );

            utilities::resize0( rst, normals, weights );

            mesh.prepareMapping( ielement, mapping );

            generator.distribute( mapping, basis.maxdegrees( ielement ), 
                rst, normals, weights, quadratureCache );

            if( !rst.empty( ) )
            {
                basis.prepareEvaluation( ielement, diffOrder, shapes, basisCache );
                basis.locationMap( ielement, utilities::resize0( locationMap ) );

                initializeLocalAssemblyTargets( localTargets, integrand.types, locationMap.size( ) );

                integrand.prepare( integrandCache, mapping, locationMap );

                for( size_t iPoint = 0; iPoint < rst.size( ); ++iPoint )
                {
                    basis.evaluateSinglePoint( rst[iPoint], shapes, basisCache );

                    integrand.evaluate( integrandCache, shapes, locationMap, 
                        normals[iPoint], localTargets, weights[iPoint] );
                }

                assemble( localTargets, locationMap, utilities::resize0( sortedIndices ) );
            }
        }
    }
}

namespace detail
{

void checkConsistency( [[maybe_unused]] const LinearizedLocationMaps& maps,
                       [[maybe_unused]] DofIndex ndof )
{
    #ifdef MLHP_DEBUG_CHECKS
    {
        const auto& [indices, dofs] = maps;

        MLHP_CHECK( !indices.empty( ), "Empty location maps." );
        MLHP_CHECK( !dofs.empty( ), "Zero dofs." );

        std::vector<bool> mask1( ndof, false );
        std::vector<bool> mask2( ndof, false );

        for( size_t iElement = 0; iElement + 1 < indices.size( ); ++iElement )
        {
            MLHP_CHECK( indices[iElement + 1] < dofs.size( ) + 1, "Inconsistant location maps." );

            for( size_t iDof = indices[iElement]; iDof < indices[iElement + 1]; ++iDof )
            {
                MLHP_CHECK( dofs[iDof] < ndof, "Dof id larger than number of dofs." );
                MLHP_CHECK( mask1[dofs[iDof]] == false, "Dof repeated in location map." );

                mask1[dofs[iDof]] = true;
                mask2[dofs[iDof]] = true;
            }

            for( size_t iDof = indices[iElement]; iDof < indices[iElement + 1]; ++iDof )
            {
                mask1[dofs[iDof]] = false;
            }
        }

        MLHP_CHECK( std::accumulate( mask2.begin( ), mask2.end( ), size_t { 0 } ) == ndof,
                    "Some dof indices are not referenced in any location map." );
    }
    #endif
}

template<typename IndexType>
auto createRowIndices( const std::vector<std::vector<linalg::SparseIndex>>& dofDofCoupling,
                       linalg::SparsePtr nnz )
{

    auto chunkIndices = utilities::allocateLinearizationIndices<linalg::SparsePtr>( dofDofCoupling.size( ) );

    for( size_t i = 0; i < dofDofCoupling.size( ); ++i )
    {
        chunkIndices[i + 1] = chunkIndices[i] + dofDofCoupling[i].size( );
    }

    auto* MLHP_RESTRICT sparseIndices = new linalg::SparseIndex[nnz];

    // Concatenate dof indices
    #pragma omp parallel for
    for( int index = 0; index < static_cast<int>( dofDofCoupling.size( ) ); ++index )
    {
        auto i = static_cast<size_t>( index );
        auto* MLHP_RESTRICT begin = sparseIndices + chunkIndices[i];

        std::copy( dofDofCoupling[i].begin( ), dofDofCoupling[i].end( ), begin );
    }

    return sparseIndices;
}

template<typename MatrixType>
auto allocateSparsityPattern( const LinearizedLocationMaps& maps,
                              DofIndex ndof )
{
    auto& indices = std::get<0>( maps );
    auto& dofs = std::get<1>( maps );
    auto inverted = algorithm::invertRelation<DofIndex>( indices, dofs, ndof );
    auto& dofElementIndices = std::get<0>( inverted );
    auto& dofElementData = std::get<1>( inverted );
 
    // TODO: Could use omp reduction to determine nnz and allocate this after deleting something else?
    auto* MLHP_RESTRICT sparseIndptr = new linalg::SparsePtr[ndof + 1];

    sparseIndptr[0] = 0;

    auto chunkData = utilities::divideIntoChunks<DofIndex>( ndof, 2000 );

    auto dofToDofCoupling = std::vector<std::vector<DofIndex>>( chunkData[0] );
    auto tmp = std::vector<DofIndex> { };

    #pragma omp parallel for private( tmp ) schedule( dynamic )
    for( int chunk = 0; chunk < static_cast<int>( chunkData[0] ); ++chunk )
    {
        auto iChunk = static_cast<DofIndex>( chunk );

        auto [chunkBegin, chunkEnd] = utilities::chunkRange( iChunk, chunkData );

        // Append row to tmp
        for( size_t iDof = chunkBegin; iDof < chunkEnd; ++iDof )
        {
            size_t previous = tmp.size( );

            // TODO: Could improve this by sorting location maps first and then merging here?
            for( size_t index = dofElementIndices[iDof]; index < dofElementIndices[iDof + 1]; ++index )
            {
                tmp.insert( tmp.end( ), dofs.begin( ) + utilities::ptrdiff( indices[dofElementData[index]] ), 
                                        dofs.begin( ) + utilities::ptrdiff( indices[dofElementData[index] + 1] ) );
                                                        
            } // for iElement

            auto current = tmp.begin( ) + static_cast<int>( previous );
            auto end1 = tmp.end( );
            
            if constexpr( linalg::isSymmetricSparse<MatrixType> )
            {
                end1 = std::partition( current, tmp.end( ), [=]( DofIndex item ){ return item >= iDof; } );
            }

            std::sort( current, end1 );

            auto end2 = std::unique( current, end1 );
            auto size = std::distance( current, end2 );

            sparseIndptr[iDof + 1] = static_cast<size_t>( size );

            tmp.resize( static_cast<size_t>( std::distance( tmp.begin( ), end2 ) ) );

        } // for iDof

        dofToDofCoupling[iChunk] = tmp;

        tmp.resize( 0 );

    } // for iChunk

    std::partial_sum( sparseIndptr, sparseIndptr + ndof + 1, sparseIndptr );

    auto sparseIndices = createRowIndices<linalg::SparseIndex>( dofToDofCoupling, sparseIndptr[ndof] );

    return std::make_pair( sparseIndices, sparseIndptr );
}

template<typename MatrixType>
auto allocateDataAndCreateSparseMatrix( linalg::SparseIndex* indices,
                                        linalg::SparsePtr* indptr,
                                        DofIndex ndof )
{
    // Resize data
    double* MLHP_RESTRICT data = new double[indptr[ndof]];

    #pragma omp parallel for schedule(static)
    for( std::int64_t i = 0; i < static_cast<std::int64_t>( indptr[ndof] ); ++i )
    {
        data[i] = 0.0;
    }

    MatrixType matrix;

    matrix.claim( { indices, indptr, data }, ndof, ndof );

    return matrix;
}

template<typename MatrixType, typename LocationMapsType>
auto allocateSparseMatrixInternal( LocationMapsType&& maps,
                                   DofIndex ndof )
{
    auto [indices, indptr] = allocateSparsityPattern<MatrixType>( maps, ndof );

    if constexpr( std::is_rvalue_reference<LocationMapsType>( ) )
    {
        utilities::clearMemory( maps.first );
        utilities::clearMemory( maps.second );
    }

    return allocateDataAndCreateSparseMatrix<MatrixType>( indices, indptr, ndof );
}

template<typename MatrixType, typename LocationMapsType>
auto allocateSparseMatrix( LocationMapsType&& maps,
                           const DofIndexVector& boundaryDofs,
                           DofIndex ndof )
{
    ndof = algorithm::computeNumberOfDofs( maps.second, ndof );

    detail::checkConsistency( maps, ndof );

    if( ndof == 0 )
    {
        return MatrixType { };
    }

    if( boundaryDofs.empty( ) )
    {
        return allocateSparseMatrixInternal<MatrixType>( std::forward<LocationMapsType>( maps ), ndof );
    }

    auto [reducedMaps, newNdof] = algorithm::removeDofs( maps, boundaryDofs, ndof );

    if constexpr( std::is_rvalue_reference<LocationMapsType>( ) )
    {
        utilities::clearMemory( maps.first );
        utilities::clearMemory( maps.second );
    }

    detail::checkConsistency( reducedMaps, newNdof );

    return allocateSparseMatrixInternal<MatrixType>( std::move( reducedMaps ), newNdof );
}

} // namespace detail


template<typename MatrixType> 
MatrixType allocateMatrix( const LinearizedLocationMaps& maps,
                           const DofIndexVector& boundaryDofs,
                           DofIndex ndof )
{
    return detail::allocateSparseMatrix<MatrixType>( maps, boundaryDofs, ndof );
}

template<typename MatrixType>
MatrixType allocateMatrix( const LocationMapVector& locationMaps,
                           const DofIndexVector& boundaryDofs, 
                           DofIndex ndof )
{
    std::function copyMap = [&]( CellIndex i, LocationMap& map ) ->void
    {
        map.resize( locationMaps[i].size( ) );

        std::copy( locationMaps[i].begin( ), locationMaps[i].end( ), map.begin( ) );
    };

    auto ncells = static_cast<CellIndex>( locationMaps.size( ) );
    
    return allocateMatrix<MatrixType>( utilities::makeIndexRangeFunction( ncells, copyMap ), boundaryDofs, ndof );
}

template<typename MatrixType>
MatrixType allocateMatrix( const LocationMapRange& locationMaps,
                           const DofIndexVector& boundaryDofs,
                           DofIndex ndof )
{
    LinearizedLocationMaps maps;

    auto& indices = std::get<0>( maps );
    auto& values = std::get<1>( maps );

    auto nmaps = locationMaps.size( );
    auto nint = static_cast<std::int64_t>( nmaps );

    [[maybe_unused]] auto chunksize = parallel::clampChunksize( nmaps, 13, 1 );

    indices = utilities::allocateLinearizationIndices<size_t>( nmaps );

    #pragma omp parallel
    {
        auto map = LocationMap { };

        #pragma omp for schedule(dynamic, chunksize)
        for( std::int64_t ii = 0; ii < nint; ++ii )
        {
            locationMaps( static_cast<CellIndex>( ii ), utilities::resize0( map ) );

            indices[static_cast<CellIndex>( ii ) + 1] = map.size( );
        }

        #pragma omp single
        { 
            std::partial_sum( indices.begin( ), indices.end( ), indices.begin( ) );

            values.resize( indices.back( ) );
        }

        #pragma omp for schedule(dynamic, chunksize)
        for( std::int64_t ii = 0; ii < nint; ++ii )
        {
            auto i = static_cast<CellIndex>( ii );

            locationMaps( i, utilities::resize0( map ) );

            std::copy( map.begin( ), map.end( ), utilities::begin( values, indices[i] ) );
        }
    }

    return detail::allocateSparseMatrix<MatrixType>( std::move( maps ), boundaryDofs, ndof );
}

template<typename MatrixType>
MatrixType allocateMatrix( size_t size1, 
                           size_t size2, 
                           linalg::SparsePtr nentries )
{
    constexpr auto issymmetric = std::is_same_v<MatrixType, linalg::SymmetricSparseMatrix>;
    constexpr auto unsymmetric = std::is_same_v<MatrixType, linalg::UnsymmetricSparseMatrix>;

    static_assert( issymmetric || unsymmetric, "Unknown matrix type instantiated." );

    if constexpr ( issymmetric )
    {
        MLHP_CHECK( size1 == size2, "Symmetric matrix requires shape[0] == shape[1]." );
        MLHP_CHECK( nentries <= ( size1 * ( size2 + 1 ) ) / 2, 
                    "Too many data entries for symmetric sparse matrix of given shape." );
    }

    if constexpr( unsymmetric )
    {
        MLHP_CHECK( nentries <= size1 * size2, "Too many data entries for sparse matrix of given shape." );
    }

    auto data = linalg::SparseDataStructure 
    { 
        new linalg::SparseIndex[nentries], 
        new linalg::SparsePtr[size1 + 1], 
        new double[nentries] 
    };

    std::fill( std::get<0>( data ), std::get<0>( data ) + nentries, 0 );
    std::fill( std::get<1>( data ), std::get<1>( data ) + size1 + 1, 0 );
    std::fill( std::get<2>( data ), std::get<2>( data ) + nentries, 0.0 );

    std::get<1>( data )[size1] = nentries;

    auto matrix = MatrixType( );
    
    matrix.claim( data, size1, size2 );

    return matrix;
}

template<size_t D>
std::vector<double> projectOnto( const AbsBasis<D>& basis,
                                 const spatial::VectorFunction<D>& function,
                                 const linalg::SparseSolver& solver )
{
    MLHP_CHECK( basis.nfields( ) == function.odim, "Inconsistent number of field components." );

    auto integrand = makeL2DomainIntegrand<D>( function );

    auto matrix = allocateMatrix<linalg::SymmetricSparseMatrix>( basis );
    auto rhs = std::vector<double>( matrix.size1( ), 0.0 );

    integrateOnDomain( basis, integrand, { matrix, rhs } );
    
    return solver( matrix, rhs );
}

template<size_t D>
std::vector<double> projectOnto( const AbsBasis<D>& basis,
                                 const spatial::VectorFunction<D>& function )
{
    return projectOnto( basis, function, linalg::makeCGSolver( 1e-12 ) );
}

template<size_t D>
std::vector<double> projectOnto( const AbsBasis<D>& basis,
                                 const spatial::ScalarFunction<D>& function )
{
    return projectOnto( basis, spatial::VectorFunction<D>{ function } );
}

template<size_t D>
std::vector<double> projectOnto( const AbsBasis<D>& basis,
                                 const spatial::ScalarFunction<D>& function,
                                 const linalg::SparseSolver& solver )
{
    return projectOnto( basis, spatial::VectorFunction<D>{ function }, solver );
}

namespace 
{
   
template<size_t D, typename MatrixType>
auto internalProjectOnto( const MultilevelHpBasis<D>& basis0,
                          const MultilevelHpBasis<D>& basis1,
                          const std::vector<double>& dofs0,
                          MatrixType& matrix,
                          const linalg::SparseSolver& solver = linalg::makeCGSolver( 1e-10 ) )
{
    auto integrand = makeL2BasisProjectionIntegrand<D>( dofs0 );
    auto vector = std::vector<double>( matrix.size1( ), 0.0 );

    auto quadrature = StandardQuadrature<D>( );
    auto orderDeterminor = relativeQuadratureOrder<D>( 1 );

    integrateOnDomain( basis0, basis1, integrand, { matrix, vector },
        quadrature, orderDeterminor, { { }, { } } );

    return solver( matrix, vector );
}

} // namespace 

template<size_t D>
std::vector<double> projectOnto( const MultilevelHpBasis<D>& basis0,
                                 const MultilevelHpBasis<D>& basis1,
                                 const std::vector<double>& dofs0 )
{
    auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( basis1 );

    return internalProjectOnto( basis0, basis1, dofs0, matrix );
}

template<size_t D>
std::vector<double> projectOnto( const MultilevelHpBasis<D>& basis0,
                                 const MultilevelHpBasis<D>& basis1,
                                 const std::vector<double>& dofs0,
                                 const linalg::SparseSolver& solver )
{
    auto matrix = allocateMatrix<linalg::SymmetricSparseMatrix>( basis1 );

    return internalProjectOnto( basis0, basis1, dofs0, matrix, solver );
}

template<size_t D, typename MatrixType>
std::vector<double> projectOnto( const MultilevelHpBasis<D>& basis0,
                                 const MultilevelHpBasis<D>& basis1,
                                 const std::vector<double>& dofs0,
                                 MatrixType& matrix )
{
    return internalProjectOnto( basis0, basis1, dofs0, matrix );
}

template<size_t D, typename MatrixType>
std::vector<double> projectOnto( const MultilevelHpBasis<D>& basis0,
                                 const MultilevelHpBasis<D>& basis1,
                                 const std::vector<double>& dofs0,
                                 MatrixType& matrix,
                                 const linalg::SparseSolver& solver )
{
    return internalProjectOnto( basis0, basis1, dofs0, matrix, solver );
}

template<size_t D>
std::vector<std::vector<double>> projectDerivatives( const AbsBasis<D>& basis,
                                                     std::span<const double> dofs,
                                                     std::span<const std::array<size_t, D>> diffIndices,
                                                     const AbsQuadrature<D>& quadrature,
                                                     const linalg::SparseSolver& solver,
                                                     const spatial::ScalarFunction<D>& weight )
{
    auto nfields = basis.nfields( );
    auto ndof = basis.ndof( );
    auto ncomponents = diffIndices.size( );

    auto result = std::vector<std::vector<double>>( ncomponents, std::vector<double>( ndof, 0.0 ) );

    auto indices = std::vector<size_t> { };
    auto maxdiff = int { 0 };
    auto allindices = diff::allIndices<D, 2>( );

    for( size_t icomp = 0; icomp < ncomponents; ++icomp )
    {
        maxdiff = std::max( maxdiff, static_cast<int>( array::sum( diffIndices[icomp] ) ) );

        MLHP_CHECK( maxdiff <= 2, "Diff order not implemented." );

        auto it = std::find( allindices.begin( ), allindices.end( ), diffIndices[icomp] );
        
        MLHP_CHECK( it != allindices.end( ), "Derivative index not found." );

        indices.push_back( static_cast<size_t>( std::distance( allindices.begin( ), it ) ) );
    }

    for( size_t ifield = 0; ifield < nfields; ++ifield )
    {
        auto filtered = FieldFilterBasis<D> { &basis, ifield };
        auto dofMap = filtered.dofIndexMap( true );

        auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( filtered );
        auto vectors = std::vector<std::vector<double>>( ncomponents );

        auto assemblyTypes = AssemblyTypeVector { };
        auto assemblyTargets = AssemblyTargetVector { };

        for( size_t icomp = 0; icomp < ncomponents; ++icomp )
        {
            vectors[icomp] = std::vector<double>( filtered.ndof( ), 0.0 );

            assemblyTypes.push_back( AssemblyType::Vector );
            assemblyTargets.push_back( vectors[icomp] );
        }

        assemblyTypes.push_back( AssemblyType::SymmetricMatrix );
        assemblyTargets.push_back( matrix );

        auto evaluate = [&]( const BasisFunctionEvaluation<D>& shapes, const LocationMap& locationMap,
                             AlignedDoubleVectors& targets, AlignedDoubleVector&, double weightDetJ )
        {
            auto ndofelement = shapes.ndof( );
            auto nblocks = shapes.nblocks( );
            auto N = shapes.noalias( 0, 0 );

            weightDetJ *= weight( shapes.xyz( ) );

            for( size_t icomp = 0; icomp < ncomponents; ++icomp )
            {
                auto offset = indices[icomp] * shapes.ndofpadded( );
                auto value = 0.0;

                for( size_t idof = 0; idof < ndofelement; ++idof )
                {
                    value += N[offset + idof] * dofs[dofMap[locationMap[idof]]];
                }

                linalg::elementRhs( targets[icomp].data( ), ndofelement, nblocks, [&]( size_t i )
                { 
                    return N[i] * value * weightDetJ;
                } );
            }

            linalg::symmetricElementLhs( targets.back( ).data( ), ndofelement, nblocks, [=]( size_t i, size_t j )
            { 
                return N[i] * N[j] * weightDetJ;
            } );
        };

        auto integrand = DomainIntegrand<D>( assemblyTypes, static_cast<DiffOrders>( maxdiff ), evaluate );

        integrateOnDomain( filtered, integrand, assemblyTargets, quadrature );

        for( size_t icomp = 0; icomp < ncomponents; ++icomp )
        {
            auto projected = solver( matrix, vectors[icomp] );

            for( size_t idof = 0; idof < projected.size( ); ++idof )
            {
                result[icomp][dofMap[idof]] = projected[idof];
            }
        }
    }

    return result;
}

template<size_t D>
std::array<std::vector<double>, D> projectGradient( const AbsBasis<D>& basis,
                                                    const std::vector<double>& dofs,
                                                    const AbsQuadrature<D>& quadrature,
                                                    const linalg::SparseSolver& solver,
                                                    const spatial::ScalarFunction<D>& weight )
{
    auto resultArray = std::array<std::vector<double>, D> { };
    auto result = projectDerivatives<D>( basis, dofs, diff::indices<D, 1>( ), quadrature, solver, weight );

    for( size_t axis = 0; axis < D; ++axis )
    {
        resultArray[axis] = std::move( result[axis] );
    }

    return resultArray;
}

LinearSystemScatterKernel::LinearSystemScatterKernel( DofIndex ndof ) :
    LinearSystemScatterKernel( { { }, { } }, ndof )
{ }

LinearSystemScatterKernel::LinearSystemScatterKernel( const DofIndicesValuesPair& boundaryDofs, 
                                                      DofIndex ndof ) :
    boundaryDofsMask( algorithm::indexMask( boundaryDofs.first, ndof ) ),
    boundaryDofMap( algorithm::splitBackwardIndexMap<DofIndex>( boundaryDofsMask ) ),
    dofValues( boundaryDofs.second )
{ }

namespace
{

void sortedLocationMapIndices( const LocationMap& locationMap, 
                               std::vector<size_t>& sorted, size_t size )
{
    sorted.resize( size );

    auto predicate = [&]( size_t a, size_t b )
    {
        return locationMap[a] < locationMap[b];
    };

    std::iota( sorted.begin( ), sorted.end( ), size_t { 0 } );
    std::sort( sorted.begin( ), sorted.end( ), predicate );
}

template<typename SystemMatrixType>
auto matrixPointers( SystemMatrixType& globalMatrix,
                     const AlignedDoubleVector& elementMatrix )
{
    return std::make_tuple( memory::assumeNoalias( globalMatrix.indices( ) ),
                            memory::assumeNoalias( globalMatrix.indptr( ) ),
                            memory::assumeNoalias( globalMatrix.data( ) ),
                            memory::assumeAlignedNoalias( elementMatrix.data( ) ) );
}

} // namespace

template<typename ElementMatrixTag, typename SystemMatrixType>
void LinearSystemScatterKernel::scatter( SystemMatrixType& globalMatrix,
                                         std::vector<double>& globalVector,
                                         const AlignedDoubleVector& elementMatrix,
                                         const AlignedDoubleVector& elementVector,
                                         const LocationMap& locationMap,
                                         std::vector<size_t>& sorted ) const
{
    size_t size = locationMap.size( );
    size_t paddedSize = memory::paddedLength<double>( size );

    sortedLocationMapIndices( locationMap, sorted, size );

    auto [indices, indptr, data, Ke] = matrixPointers( globalMatrix, elementMatrix );

    for( size_t iRow = 0; iRow < size; ++iRow )
    {
        if( auto rowFullIndex = locationMap[iRow]; !boundaryDofsMask[rowFullIndex] )
        {
            auto rowReducedIndex = boundaryDofMap[rowFullIndex];
            auto current = indices + indptr[rowReducedIndex];

            double rhsValue = elementVector[iRow];

            for( auto iColumn : sorted )
            {
                double lhsValue = linalg::indexDenseMatrix<ElementMatrixTag>( Ke, iRow, iColumn, paddedSize );

                auto columnFullIndex = locationMap[iColumn];
                auto columnReducedIndex = boundaryDofMap[columnFullIndex];

                if( !boundaryDofsMask[columnFullIndex] )
                {
                    if constexpr( linalg::isSymmetricSparse<SystemMatrixType> )
                    {
                        if( columnReducedIndex < rowReducedIndex ) continue;
                    }

                    current = std::find( current, indices + indptr[rowReducedIndex + 1], columnReducedIndex );

                    MLHP_CHECK_DBG( *current == columnReducedIndex, "Entry was not found in sparsity pattern!" );

                    double* MLHP_RESTRICT target = data + std::distance( indices, current );

                    current++;

                    #pragma omp atomic
                    *target += lhsValue;
                }
                else
                {
                    rhsValue -= lhsValue * dofValues[columnReducedIndex];
                }
            } // iColumn

            #pragma omp atomic
            globalVector[rowReducedIndex] += rhsValue;
        }
    } // iRow
}

template<typename ElementMatrixTag, typename SystemMatrixType>
void LinearSystemScatterKernel::scatterLhs( SystemMatrixType& globalMatrix,
                                            const AlignedDoubleVector& elementMatrix,
                                            const LocationMap& locationMap,
                                            std::vector<size_t>& sorted ) const
{
    size_t size = locationMap.size( );
    size_t paddedSize = memory::paddedLength<double>( size );

    sortedLocationMapIndices( locationMap, sorted, size );

    auto [indices, indptr, data, Ke] = matrixPointers( globalMatrix, elementMatrix );

    for( size_t iRow = 0; iRow < size; ++iRow )
    {
        if( auto rowFullIndex = locationMap[iRow]; !boundaryDofsMask[rowFullIndex] )
        {
            auto rowReducedIndex = boundaryDofMap[rowFullIndex];
            auto current = indices + indptr[rowReducedIndex];

            for( auto iColumn : sorted )
            {
                if( auto columnFullIndex = locationMap[iColumn]; !boundaryDofsMask[columnFullIndex] )
                {
                    auto columnReducedIndex = boundaryDofMap[columnFullIndex];

                    if constexpr( linalg::isSymmetricSparse<SystemMatrixType> )
                    {
                        if( columnReducedIndex < rowReducedIndex ) continue;
                    }

                    current = std::find( current, indices + indptr[rowReducedIndex + 1], columnReducedIndex );

                    MLHP_CHECK_DBG( *current == columnReducedIndex, "Entry was not found in sparsity pattern!" );

                    double lhsValue = linalg::indexDenseMatrix<ElementMatrixTag>( Ke, iRow, iColumn, paddedSize );

                    double* MLHP_RESTRICT target = data + std::distance( indices, current );

                    current++;

                    #pragma omp atomic
                    *target += lhsValue;
                }
            } // iColumn
        }
    } // iRow
}

void LinearSystemScatterKernel::scatterRhs( std::vector<double>& globalVector,
                                            const AlignedDoubleVector& elementVector,
                                            const LocationMap& locationMap ) const
{
    auto* Fe = memory::assumeAligned( elementVector.data( ) );

    for( size_t iRow = 0; iRow < locationMap.size( ); ++iRow )
    {
        if( auto fullIndex = locationMap[iRow]; !boundaryDofsMask[fullIndex] )
        {
            auto reducedIndex = boundaryDofMap[fullIndex];

            #pragma omp atomic
            globalVector[reducedIndex] += Fe[iRow];
        }
    } // iRow
}

#define MLHP_INSTANTIATE_ASSEMBLY_MATRIX_TYPE( MATRIX_TYPE )                                                       \
                                                                                                                   \
    template MLHP_EXPORT                                                                                           \
    MATRIX_TYPE allocateMatrix<MATRIX_TYPE>( const LocationMapRange& locationMaps,                                 \
                                             const DofIndexVector& boundaryDofs,                                   \
                                             DofIndex ndof );                                                      \
                                                                                                                   \
    template MLHP_EXPORT                                                                                           \
    MATRIX_TYPE allocateMatrix<MATRIX_TYPE>( const LinearizedLocationMaps& dofs,                                   \
                                             const DofIndexVector& boundaryDofs,                                   \
                                             DofIndex ndof );                                                      \
                                                                                                                   \
    template MLHP_EXPORT                                                                                           \
    MATRIX_TYPE allocateMatrix<MATRIX_TYPE>( const LocationMapVector& locationMaps,                                \
                                             const DofIndexVector& boundaryDofs,                                   \
                                             DofIndex ndof );                                                      \
                                                                                                                   \
    template MLHP_EXPORT                                                                                           \
    MATRIX_TYPE allocateMatrix<MATRIX_TYPE>( size_t size1, size_t size2, linalg::SparsePtr nentries );

MLHP_INSTANTIATE_ASSEMBLY_MATRIX_TYPE( linalg::SymmetricSparseMatrix )
MLHP_INSTANTIATE_ASSEMBLY_MATRIX_TYPE( linalg::UnsymmetricSparseMatrix )

#define MLHP_INSTANTIATE_DIM( D )                                                                  \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    void integrateOnDomain( const AbsBasis<D>& basis,                                              \
                            const DomainIntegrand<D>& integrand,                                   \
                            const AssemblyTargetVector& globalTargets,                             \
                            const AbsQuadrature<D>& quadrature,                                    \
                            const QuadratureOrderDeterminor<D>& orderDeterminor,                   \
                            const DofIndicesValuesPair& boundaryDofs,                              \
                            size_t chunksize );                                                    \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    void integrateOnDomain( const MultilevelHpBasis<D>& basis0,                                    \
                            const MultilevelHpBasis<D>& basis1,                                    \
                            const BasisProjectionIntegrand<D>& integrand,                          \
                            const AssemblyTargetVector& globalTargets,                             \
                            const AbsQuadrature<D>& quadrature,                                    \
                            const QuadratureOrderDeterminor<D>& orderDeterminor,                   \
                            const DofIndicesValuesPair& boundaryDofs,                              \
                            size_t chunksize );                                                    \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    void integrateOnSurface( const AbsBasis<D>& basis,                                             \
                             const SurfaceIntegrand<D>& integrand,                                 \
                             const AbsQuadratureOnMesh<D>& generator,                              \
                             const AssemblyTargetVector& globalTargets,                            \
                             const DofIndicesValuesPair& boundaryDofs,                             \
                             size_t chunksize );                                                   \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<double> projectOnto( const AbsBasis<D>& basis,                                     \
                                     const spatial::ScalarFunction<D>& function );                 \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<double> projectOnto( const AbsBasis<D>& basis,                                     \
                                     const spatial::ScalarFunction<D>& function,                   \
                                     const linalg::SparseSolver& solver );                         \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<double> projectOnto( const AbsBasis<D>& basis,                                     \
                                     const spatial::VectorFunction<D>& function );                 \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<double> projectOnto( const AbsBasis<D>& basis,                                     \
                                     const spatial::VectorFunction<D>& function,                   \
                                     const linalg::SparseSolver& solver );                         \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<double> projectOnto( const MultilevelHpBasis<D>& newBasis,                         \
                                     const MultilevelHpBasis<D>& oldBasis,                         \
                                     const std::vector<double>& oldDofs );                         \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<double> projectOnto( const MultilevelHpBasis<D>& newBasis,                         \
                                     const MultilevelHpBasis<D>& oldBasis,                         \
                                     const std::vector<double>& oldDofs,                           \
                                     linalg::SymmetricSparseMatrix& matrix );                      \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<double> projectOnto( const MultilevelHpBasis<D>& newBasis,                         \
                                     const MultilevelHpBasis<D>& oldBasis,                         \
                                     const std::vector<double>& oldDofs,                           \
                                     linalg::UnsymmetricSparseMatrix& matrix );                    \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<double> projectOnto( const MultilevelHpBasis<D>& newBasis,                         \
                                     const MultilevelHpBasis<D>& oldBasis,                         \
                                     const std::vector<double>& oldDofs,                           \
                                     const linalg::SparseSolver& solver );                         \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<double> projectOnto( const MultilevelHpBasis<D>& newBasis,                         \
                                     const MultilevelHpBasis<D>& oldBasis,                         \
                                     const std::vector<double>& oldDofs,                           \
                                     linalg::SymmetricSparseMatrix& matrix,                        \
                                     const linalg::SparseSolver& solver );                         \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<double> projectOnto( const MultilevelHpBasis<D>& newBasis,                         \
                                     const MultilevelHpBasis<D>& oldBasis,                         \
                                     const std::vector<double>& oldDofs,                           \
                                     linalg::UnsymmetricSparseMatrix& matrix,                      \
                                     const linalg::SparseSolver& solver  );                        \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::vector<std::vector<double>> projectDerivatives( const AbsBasis<D>& basis,                 \
                                                         std::span<const double> dofs,             \
                                                         std::span<const std::array<size_t, D>>,   \
                                                         const AbsQuadrature<D>& quadrature,       \
                                                         const linalg::SparseSolver& solver,       \
                                                         const spatial::ScalarFunction<D>& weight ); \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    std::array<std::vector<double>, D> projectGradient( const AbsBasis<D>& basis,                  \
                                                        const std::vector<double>& dofs,           \
                                                        const AbsQuadrature<D>& quadrature,        \
                                                        const linalg::SparseSolver& solver,        \
                                                        const spatial::ScalarFunction<D>& weight );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // mlhp
