// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/derivativeHelper.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/mesh.hpp"
#include "mlhp/core/multilevelhpcore.hpp"
#include "mlhp/core/polynomials.hpp"
#include "mlhp/core/arrayfunctions.hpp"
#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/algorithm.hpp"

#include <algorithm>
#include <cmath>
#include <numeric>

namespace mlhp
{
namespace detail
{

template<size_t D>
auto extractDegreesForFieldComponent( const AnsatzTemplateVector& ansatzTemplates, size_t fieldComponent )
{
    auto result = std::vector<std::array<size_t, D>>( ansatzTemplates.shape( )[0] );
    auto nint = static_cast<std::int64_t>( result.size( ) );

    #pragma omp parallel for schedule(static)
    for( std::int64_t ii = 0; ii < nint; ++ii )
    {
        auto i = static_cast<size_t>( ii );

        for( size_t axis = 0; axis < D; ++axis )
        {
            result[i][axis] = ansatzTemplates( i, fieldComponent, axis );
        }
    }

    return result;
}

} // detail

template<size_t D>
MultilevelHpBasis<D>::MultilevelHpBasis( const HierarchicalGridSharedPtr<D>& grid,
                                         const AnsatzTemplateVector& polynomialDegrees,
                                         const InitialMaskProvider<D>& ansatzSpace ) :
    nfields_( polynomialDegrees.shape( )[1] ),
    ndof_( 0 ),
    grid_( grid ),
    indices_( nfields_ * grid->nfull( ) + 1 )
{
    MLHP_EXPECTS( polynomialDegrees.shape( )[0] == grid_->nleaves( ) );
    MLHP_EXPECTS( polynomialDegrees.shape( )[1] >= 1 );
    MLHP_EXPECTS( polynomialDegrees.shape( )[2] == D );

    std::fill( bases1D_.begin( ), bases1D_.end( ), polynomial::makeIntegratedLegendreBasis( ) );

    auto leafMask = mesh::leafMask( *grid );
    auto levels = mesh::refinementLevels( *grid, true );
    auto neighbours = mesh::hierarchicalNeighbours( *grid );

    std::vector<LinearizedTensorProductIndices<D>> tensorProductIndices;

    indices_[0] = 0;

    for( size_t iField = 0; iField < nfields_; ++iField )
    {
        auto degrees = detail::extractDegreesForFieldComponent<D>( polynomialDegrees, iField );

        tensorProductIndices.push_back( constructTensorProductIndices( 
            neighbours, leafMask, levels, degrees, ansatzSpace ) );

        const auto& indices = tensorProductIndices.back( ).second;
        auto nint = static_cast<std::int64_t>( indices.size( ) ) - 1;

        MLHP_CHECK( indices.size( ) > 1, "No active dofs for field component." );

        #pragma omp parallel for schedule(static)
        for( std::int64_t ii = 0; ii < nint; ++ii )
        {
            auto i = static_cast<size_t>( ii );

            indices_[nfields_ * i + iField + 1] = indices[i + 1] - indices[i];
        }
    }

    std::partial_sum( indices_.begin( ), indices_.end( ), indices_.begin( ) );

    locationMaps_.resize( indices_.back( ) );
    tensorProductIndices_.resize( indices_.back( ) );
       
    [[maybe_unused]] 
    auto chunksize = parallel::clampChunksize( grid_->nfull( ), 79 );

    for( size_t iField = 0; iField < nfields_; ++iField )
    {
        auto globalIndices = generateLocationMaps( tensorProductIndices[iField].first, 
            tensorProductIndices[iField].second, neighbours, levels );

        auto ndoffield = DofIndex { 0 };
        auto nint = static_cast<std::int64_t>( grid_->nfull( ) );

        #pragma omp parallel
        {
            auto localndof = DofIndex { 0 };

            #pragma omp for schedule(dynamic, chunksize)
            for( std::int64_t iInt = 0; iInt < nint; ++iInt )
            {
                auto iCell = static_cast<size_t>( iInt );

                auto indexBegin = indices_[iCell * nfields_ + iField];
                auto indexEnd = indices_[iCell * nfields_ + iField + 1];

                auto index2Begin = tensorProductIndices[iField].second[iCell];

                for( DofIndex iDof = 0; iDof < indexEnd - indexBegin; ++iDof )
                {
                    locationMaps_[indexBegin + iDof] = globalIndices[index2Begin + iDof] + ndof_;
                    tensorProductIndices_[indexBegin + iDof] = tensorProductIndices[iField].first[index2Begin + iDof];
                    localndof = std::max( localndof, globalIndices[index2Begin + iDof] );
                }
            }

            #pragma omp critical
            {
                ndoffield = std::max( ndoffield, localndof + 1 );
            }
        }

        ndof_ += ndoffield;
    }
}

namespace detail
{
namespace
{

auto indexRange( const auto& container,
                 const auto& indices,
                 size_t index,
                 size_t increment )
{
    return std::make_pair( container.begin( ) + static_cast<std::ptrdiff_t>( indices[index] ),
                           container.begin( ) + static_cast<std::ptrdiff_t>( indices[index + increment] ) );
}

template<size_t D, typename OffsetsAndSizes>
auto extractMaximumDegrees( const std::vector<OffsetsAndSizes>& fieldLevelData )
{
    std::array<size_t, D> maxdegrees { };

    for( size_t i = 0; i < fieldLevelData.size( ); ++i )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            auto degree = static_cast<size_t>( fieldLevelData[i].degrees[axis] );

            maxdegrees[axis] = std::max( maxdegrees[axis], degree );
        }
    }

    return maxdegrees;
}

template<size_t D> 
auto compute1DBasisIncrements( const auto& fieldLevelData, size_t maxdifforder )
{
    auto increments = array::makeSizes<D>( 2 );

    for( const auto& data : fieldLevelData )
    {
        if( auto p = data.degrees; p[0] > 0 )
        {
            for( size_t axis = 0; axis < D; ++axis )
            {
                increments[axis] += ( static_cast<size_t>( p[axis] ) + 1 ) * ( maxdifforder + 1 );
            }
        }
    }

    return increments;
}

//! Map derivatives of 1D polynomials to the leaf element
void mapDerivatives( double diffFactor, 
                     size_t maxdifforder, 
                     size_t nshapes,
                     double* MLHP_RESTRICT ptr )
{
    if( maxdifforder >= 1 )
    {
        std::transform( ptr + nshapes, ptr + 2 * nshapes, ptr + nshapes,
                        [=]( double value ) { return diffFactor * value; } );
    }

    if( maxdifforder >= 2 )
    {
        diffFactor = diffFactor * diffFactor;

        std::transform( ptr + 2 * nshapes, ptr + 3 * nshapes, ptr + 2 * nshapes,
                        [=]( double value ) { return diffFactor * value; } );
    }
}

template<size_t D> 
auto gatherAxisData( std::array<size_t, D> gridSizes,
                     std::array<size_t, D> increment,
                     std::array<size_t, D> ijk,
                     const double* MLHP_RESTRICT basis1DBegin )
{
    std::array<const double*, D> pointers;
    std::array<double, D> leafRst, rootRst;

    for( size_t axis = 0; axis < D; ++axis )
    {
        pointers[axis] = basis1DBegin + ijk[axis] * increment[axis];

        leafRst[axis] = pointers[axis][0];
        rootRst[axis] = pointers[axis][1];

        pointers[axis] += 2;

        basis1DBegin += gridSizes[axis] * increment[axis];
    }

    return std::make_tuple( pointers, leafRst, rootRst );
}

template<size_t D> MLHP_PURE
auto incrementDiffOrder( std::array<const double*, D> pointers,
                         const std::array<size_t, D>& diffindices,
                         const std::array<PolynomialDegree, D>& degrees )
{
    for( size_t axis = 0; axis < D; ++axis )
    {
        if( diffindices[axis] )
        {
            auto p = static_cast<size_t>( degrees[axis] );

            pointers[axis] += diffindices[axis] * ( p + 1 );
        }
    }

    return pointers;
}

template<size_t MaxDiff, size_t D>
auto incrementDiffOrders( std::array<const double*, D>& pointers,
                          std::array<PolynomialDegree, D> degrees )
{
    for( size_t axis = 0; axis < D; ++axis )
    {
        pointers[axis] += ( degrees[axis] + 1 ) * ( MaxDiff + 1 );
    }
}

} // namespace
} // namespace detail

template<size_t D>
struct MultilevelHpBasis<D>::EvaluationImpl
{
    const MultilevelHpBasis<D>* basis;

    MeshMapping<D> mapping;

    struct LevelData
    {
        CellIndex fullIndex;
        PositionInParent<D> position;
    };

    struct OffsetsAndSizes
    {
        size_t compressedOffset, ndof;
        PolynomialDegrees<D> degrees;
    };

    // Generic cached data
    size_t maxdifforder, nlevels, nfields;

    CellIndex rootIndex;

    std::vector<LevelData> levelData;            // One per level
    std::vector<OffsetsAndSizes> fieldLevelData; // one per field and level
    std::vector<PolynomialDegree> basisData; // All compressed tensor products

    // Grid evaluation cached data
    std::array<size_t, D> gridSizes;             // sizes for rst values in vector below
    std::array<size_t, D> basisBegin;            // Begin index for 1D basis evaluation
    std::array<size_t, D> basisIncrements;       // Increment to go to next evaluation coordinate
    std::vector<double> gridData;                // rst value data and 1D bases evaluations

    // Temporary rst storage for single point evaluation
    CoordinateGrid<D> singleRst;

    std::array<size_t, D> prepareEvaluation( CellIndex ielement,
                                             BasisFunctionEvaluation<D>& shapes,
                                             size_t maxDiffOrder );

    void prepareGridEvaluation( const CoordinateGrid<D>& rst );

    template<size_t MaxDiff>
    void evaluateGridPoint( std::array<size_t, D> ijk,
                            BasisFunctionEvaluation<D>& shapes ) const;
};

template<size_t D>
std::array<size_t, D> MultilevelHpBasis<D>::EvaluationImpl::prepareEvaluation( CellIndex ielement,
                                                                               BasisFunctionEvaluation<D>& shapes,
                                                                               size_t maxDiffOrder )
{
    levelData.resize( 0 );
    basisData.resize( 0 );
    fieldLevelData.resize( 0 );

    // Prepare cell indices and mapping to root rst
    auto fullIndex = basis->grid_->fullIndex( ielement );

    for( auto iCell = fullIndex; iCell != NoCell; iCell = basis->grid_->parent( iCell ) )
    {
        levelData.push_back( { iCell, basis->grid_->localPosition( iCell ) } );
    }

    maxdifforder = maxDiffOrder;
    nlevels = levelData.size( );
    nfields = basis->nfields_;
    rootIndex = levelData.back( ).fullIndex;

    // Prepare basis information
    shapes.initialize( ielement, nfields, maxDiffOrder );

    for( size_t ifield = 0; ifield < nfields; ++ifield )
    {
        for( size_t ilevel = 0; ilevel < nlevels; ++ilevel )
        {
            auto begin = basis->indices_[levelData[ilevel].fullIndex * nfields + ifield];
            auto end = basis->indices_[levelData[ilevel].fullIndex * nfields + ifield + 1];

            auto ndof = static_cast<size_t>( end - begin );
            auto compressedOffset = basisData.size( );

            PolynomialDegrees<D> degrees { };

            if( ndof > 0 )
            {
                shapes.addDofs( ifield, ndof );

                auto indicesPtr = basis->tensorProductIndices_.data( );

                degrees = compressIndices( indicesPtr + begin, indicesPtr + end, basisData );
            }
          
            fieldLevelData.push_back( { compressedOffset, ndof, degrees } );

        } // for ilevel
    } // for ifield

    shapes.allocate( );

    basis->grid_->prepareMapping( ielement, mapping );

    return detail::extractMaximumDegrees<D>( fieldLevelData );
}

template<size_t D>
void MultilevelHpBasis<D>::EvaluationImpl::prepareGridEvaluation( const CoordinateGrid<D>& rst )
{
    gridData.resize( 0 );
    gridSizes = array::elementSizes( rst );

    // Prepare data to help indexing 1D basis evaluation later
    basisIncrements = detail::compute1DBasisIncrements<D>( fieldLevelData, maxdifforder );

    for( size_t axis = 0; axis < D; ++axis )
    {
        basisBegin[axis] = gridData.size( );

        for( size_t index = 0; index < gridSizes[axis]; ++index )
        {
            gridData.push_back( rst[axis][index] );
            gridData.push_back( rst[axis][index] );

            size_t rootRstIndex = gridData.size( ) - 1;

            double r = 0.0;

            for( size_t ifield = 0; ifield < nfields; ++ifield )
            {
                r = rst[axis][index];

                double diffFactor = 1.0;

                for( size_t ilevel = 0; ilevel < nlevels; ++ilevel )
                {
                    auto p = fieldLevelData[ifield * nlevels + ilevel].degrees[axis];

                    // Resize and evaluate 1D basis functions
                    if( p > 0 )
                    {
                        size_t current = gridData.size( );

                        gridData.resize( current + ( maxdifforder + 1 ) * ( p + 1 ) );

                        // Evaluate 1D polynomials for current axis, polynomial degree and coordinate
                        basis->bases1D_[axis]( p, maxdifforder, r, gridData.data( ) + current );
                        
                        // Map derivatives 1D polynomial evaluation to leaf element
                        detail::mapDerivatives( diffFactor, maxdifforder, p + 1, gridData.data( ) + current );
                    }

                    // Map coordinate to parent level
                    if( ilevel + 1 < nlevels )
                    {
                        auto position = levelData[ilevel].position[axis];

                        r = 0.5 * ( r + ( position ? 1.0 : -1.0 ) );

                        diffFactor *= 0.5;
                    }

                } // for ilevel

                gridData[rootRstIndex] = r;

            } // for ifield
        } // for index
    } // for axis

}

template<size_t D>
template<size_t MaxDiff>
void MultilevelHpBasis<D>::EvaluationImpl::evaluateGridPoint( std::array<size_t, D> ijk,
                                                              BasisFunctionEvaluation<D>& shapes ) const
{
    constexpr auto diffindices = diff::allIndices<D, MaxDiff>( );
    
    auto [basisPtrs, leafRst, rootRst] = detail::gatherAxisData( 
        gridSizes, basisIncrements, ijk, gridData.data( ) );

    for( size_t ifield = 0; ifield < nfields; ++ifield )
    {
        auto target = shapes.get( ifield, 0 );
        auto fieldndof = shapes.ndofpadded( ifield );

        for( size_t ilevel = 0; ilevel < nlevels; ++ilevel )
        {
            const auto& data = fieldLevelData[ifield * nlevels + ilevel];

            if( auto degrees = data.degrees; degrees[0] > 0 )
            {
                auto tensorProduct = basisData.data( ) + data.compressedOffset;

                // Loop over all diff index tuples
                for( size_t icomponent = 0; icomponent < diffindices.size( ); ++icomponent )
                {
                    auto basisPtr = target + icomponent * fieldndof;
                    auto pointers1D = detail::incrementDiffOrder( basisPtrs, diffindices[icomponent], degrees );

                    compressedTensorProduct( tensorProduct, pointers1D, 1.0, basisPtr );
                }

                // Increment 1D basis pointers to next level / field 
                detail::incrementDiffOrders<MaxDiff>( basisPtrs, degrees );

                // Increment target shape function to next level / field
                target += data.ndof;
            }

        } // for ilevel
    } // for ifield

    shapes.setRst( leafRst );

    mapBasisEvaluation( shapes, mapping );
}

template<size_t D>
BasisEvaluationCache<D> MultilevelHpBasis<D>::createEvaluationCache( ) const
{
    EvaluationImpl impl { };

    impl.basis = this;
    impl.mapping = grid_->createMapping( );

    return BasisEvaluationCache<D> ( std::move( impl ) );
}

template<size_t D>
std::array<size_t, D> MultilevelHpBasis<D>::prepareEvaluation( CellIndex ielement,
                                                               size_t maxDiffOrder,
                                                               BasisFunctionEvaluation<D>& shapes,
                                                               BasisEvaluationCache<D>& cache ) const
{
    auto& impl = utilities::cast<EvaluationImpl>( cache );

    return impl.prepareEvaluation( ielement, shapes, maxDiffOrder );
}

template<size_t D>
void MultilevelHpBasis<D>::prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                                  BasisEvaluationCache<D>& cache ) const
{
    auto& impl = utilities::cast<EvaluationImpl>( cache );

    return impl.prepareGridEvaluation( rst );
}

template<size_t D>
void MultilevelHpBasis<D>::evaluateGridPoint( std::array<size_t, D> ijk,
                                              BasisFunctionEvaluation<D>& shapes,
                                              BasisEvaluationCache<D>& cache ) const

{
    auto& impl = utilities::cast<EvaluationImpl>( cache );

    if( impl.maxdifforder == 0 ) impl.template evaluateGridPoint<0>( ijk, shapes );
    else if( impl.maxdifforder == 1 ) impl.template evaluateGridPoint<1>( ijk, shapes );
    else if( impl.maxdifforder == 2 ) impl.template evaluateGridPoint<2>( ijk, shapes );
    else MLHP_THROW( "Invalid diff order." );
}

template<size_t D>
void MultilevelHpBasis<D>::evaluateSinglePoint( std::array<double, D> rst,
                                                BasisFunctionEvaluation<D>& shapes,
                                                BasisEvaluationCache<D>& cache ) const
{
    auto& impl = utilities::cast<EvaluationImpl>( cache );

    for( size_t axis = 0; axis < D; ++axis )
    {
        impl.singleRst[axis] = { rst[axis] };
    }

    impl.prepareGridEvaluation( impl.singleRst );
    
    evaluateGridPoint( { }, shapes, cache );
}

template<size_t D>
const MeshMapping<D>& MultilevelHpBasis<D>::mapping( BasisEvaluationCache<D>& cache ) const
{
    return utilities::cast<EvaluationImpl>( cache ).mapping;
}

template<size_t D>
std::array<size_t, D> MultilevelHpBasis<D>::maxdegrees( CellIndex ielement ) const
{
    PolynomialDegrees<D> degrees { };

    std::ptrdiff_t nshapes = 0;

    for( auto cell = grid_->fullIndex( ielement ); cell != NoCell; cell = grid_->parent( cell ) )
    {
        auto [begin, end] = detail::indexRange( tensorProductIndices_, indices_, cell * nfields_, nfields_ );

        auto compare = []( const auto& a1, const auto& a2 ){
            return array::maxArray( a1, a2 ); };

        degrees = std::reduce( begin, end, degrees, compare );
        nshapes += std::distance( begin, end );
    }

    if( nshapes )
    {
        degrees = array::maxArray( degrees, array::make<D>( PolynomialDegree { 1 } ) );
    }

    return array::convert<size_t>( degrees );
}

template<size_t D>
void MultilevelHpBasis<D>::locationMap( CellIndex ielement, LocationMap& target ) const
{
    for( size_t ifield = 0; ifield < nfields_; ++ifield )
    {
        for( auto cell = grid_->fullIndex( ielement ); cell != NoCell; cell = grid_->parent( cell ) )
        {
            auto [begin, end] = detail::indexRange( locationMaps_, indices_, cell * nfields_ + ifield, 1 );

            target.insert( target.end( ), begin, end );
        }
    }
}

template<size_t D>
DofIndex MultilevelHpBasis<D>::faceDofs( CellIndex ielement, 
                                         size_t iface, 
                                         size_t ifield,
                                         std::vector<size_t>& localDofs ) const
{
    auto [normal, side] = normalAxisAndSide( iface );

    auto fieldOffset = basis::fieldComponentOffset( *this,  ielement, ifield );
    auto dofIndex = fieldOffset;

    bool isInternal = false;

    for( auto icell = grid_->fullIndex( ielement ); icell != NoCell; icell = grid_->parent( icell ) )
    {
        auto offset = icell * nfields_ + ifield;

        for( size_t index = indices_[offset]; index < indices_[offset + 1]; ++index )
        {
            if( isInternal || tensorProductIndices_[index][normal] == side )
            {
                localDofs.push_back( dofIndex );
            }

            ++dofIndex;
        }

        isInternal = isInternal || ( grid_->localPosition( icell )[normal] != side );
    }

    return fieldOffset;
}

template<size_t D>
void MultilevelHpBasis<D>::tensorProductIndices( CellIndex fullIndex, 
                                                 size_t fieldIndex, 
                                                 TensorProductIndicesVector<D>& target ) const
{
    auto [begin, end] = detail::indexRange( tensorProductIndices_, indices_, fullIndex * nfields_ + fieldIndex, 1 );

    target.resize( 0 );
    target.insert( target.end( ), begin, end );
}

template<size_t D>
void MultilevelHpBasis<D>::setPolynomialBases( const std::array<PolynomialBasis, D>& bases )
{
    bases1D_ = bases;
}

template<size_t D>
DofIndex MultilevelHpBasis<D>::ndofelement( CellIndex ielement ) const
{
    DofIndex numberOfDofs = 0;

    for( auto cell = grid_->fullIndex( ielement ); cell != NoCell; cell = grid_->parent( cell ) )
    {
        numberOfDofs += indices_[(cell + 1) * nfields_] - indices_[cell * nfields_];
    }

    return numberOfDofs;
}

template<size_t D>
DofIndex MultilevelHpBasis<D>::ndofelement( CellIndex ielement,
                                            size_t fieldIndex ) const
{
    DofIndex numberOfDofs = 0;

    for( auto cell = grid_->fullIndex( ielement ); cell != NoCell; cell = grid_->parent( cell ) )
    {
        numberOfDofs += indices_[cell * nfields_ + fieldIndex + 1] - 
                        indices_[cell * nfields_ + fieldIndex];
    }

    return numberOfDofs;
}

template<size_t D>
size_t MultilevelHpBasis<D>::memoryUsage( ) const
{
    return utilities::vectorInternalMemory( indices_, locationMaps_, tensorProductIndices_ );
}

template<size_t D>
void print( const MultilevelHpBasis<D>& basis, std::ostream& os )
{
    auto average = basis::averageNumberOfElementDofs( basis );
    auto depth = static_cast<size_t>( mesh::maxRefinementLevel( basis.hierarchicalGrid( ) ) );

    os << "MultilevelHpBasis<" << D << "> (address: " << &basis << ")\n";
    os << "    number of elements         : " << basis.nelements( ) << "\n";
    os << "    highest polynomial degree  : " << basis::maxdegree( basis ) << "\n";
    os << "    number of unknowns         : " << basis.ndof( ) << "\n";
    os << "    number of field components : " << basis.nfields( ) << "\n";
    os << "    average dofs per element   : " << utilities::roundNumberString( average ) << "\n";
    os << "    maximum refinement depth   : " << depth << "\n";
    os << "    heap memory usage          : " << utilities::memoryUsageString( basis.memoryUsage( ) );
    os << std::endl;
}

template<size_t D>
BSplineBasis<D>::BSplineBasis( std::shared_ptr<const CartesianGrid<D>> grid,
                               std::vector<std::array<size_t, D>> degrees,
                               std::vector<std::array<size_t, D>> continuities ) :
    grid_ { std::move( grid ) }, degrees_ { std::move( degrees ) }, continuities_ { std::move( continuities ) }
{
    MLHP_CHECK( degrees_.size( ) == continuities_.size( ), "Inconsistent input sizes: degrees (n = " + 
        std::to_string( degrees_.size( ) ) + ") and continuities (n = " + std::to_string( 
        continuities_.size( ) ) + ") must have one item per solution field component." );

    auto nfields = degrees_.size( );
    auto coordinates = grid_->coordinates( );

    knotVectors_.resize( nfields * D );

    for( size_t ifield = 0; ifield < nfields; ++ifield )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            polynomial::openKnotVector( coordinates[axis], degrees_[ifield][axis], 
                continuities_[ifield][axis], knotVectors_[ifield * D + axis] );
        }
    }
}

template<size_t D>
DofIndex BSplineBasis<D>::ndof( ) const
{
    auto count = DofIndex { 0 };

    for( size_t ifield = 0; ifield < nfields( ); ++ifield )
    {
        auto axisCount = DofIndex { 1 };

        for( size_t axis = 0; axis < D; ++axis )
        {
            auto p = degrees_[ifield][axis];
            auto m = knotVectors_[ifield * D + axis].size( );

            axisCount *= m - p - 1;
        }

        count += axisCount;
    }

    return count;
}

template<size_t D>
DofIndex BSplineBasis<D>::ndofelement( CellIndex ielement ) const
{
    auto count = DofIndex { 0 };
    
    for( size_t ifield = 0; ifield < nfields( ); ++ifield )
    {
        count += ndofelement( ielement, ifield );
    }

    return count;
}

template<size_t D>
DofIndex BSplineBasis<D>::ndofelement( CellIndex /* ielement */, size_t fieldIndex ) const
{
    return static_cast<DofIndex>( array::product( array::add( degrees_[fieldIndex], size_t { 1 } ) ) );
}

template<size_t D>
size_t BSplineBasis<D>::memoryUsage( ) const
{
    return utilities::vectorInternalMemory( degrees_, continuities_, knotVectors_ );
}

namespace
{

template<size_t D>
auto bsplineAxisNDof( const std::vector<std::vector<double>>& knotVectors, 
                      const std::vector<std::array<size_t, D>>& degrees,
                      size_t ifield )
{
    auto ndof = std::array<size_t, D> { };

    for( size_t axis = 0; axis < D; ++axis )
    {
        ndof[axis] = knotVectors[ifield * D + axis].size( ) - degrees[ifield][axis] - 1;
    }

    return ndof;
}

template<size_t D>
auto bsplineAxisFirstDof( const std::vector<std::array<size_t, D>>& degrees,
                          const std::vector<std::array<size_t, D>>& continuities,
                          std::array<CellIndex, D> ijkCell, size_t ifield )
{
    auto ijk0 = std::array<size_t, D>{ };

    for( size_t axis = 0; axis < D; ++axis )
    {
        auto p = degrees[ifield][axis];
        auto c = continuities[ifield][axis];

        ijk0[axis] = ijkCell[axis] * ( p - c );
    }

    return ijk0;
}

}

template<size_t D>
struct BSplineBasis<D>::EvaluationCache
{
    std::array<CellIndex, D> ijkCell = { };
    MeshMapping<D> mapping;
    CoordinateGrid<D> rstGrid;
    CoordinateGrid<D> xyzGrid;
    std::vector<double> tmp;
    std::vector<double> data;
    std::vector<size_t> offsets;
    bool sameFields = true;
    int maxdiff = 0;
};

template<size_t D>
BasisEvaluationCache<D> BSplineBasis<D>::createEvaluationCache( ) const
{
    auto cache = EvaluationCache { };

    cache.mapping = grid_->createMapping( );

    MLHP_CHECK( dynamic_cast<const CartesianMapping<D>*>( cache.mapping.mapping.get( ) ) != nullptr,
        "Failed to cast mapping returned by Cartesian grid to a CartesianMapping<D>." );

    return BasisEvaluationCache<D> { std::move( cache ) };
}

template<size_t D>
std::array<size_t, D> BSplineBasis<D>::prepareEvaluation( CellIndex ielement,
                                                          size_t maxDiffOrder,
                                                          BasisFunctionEvaluation<D>& shapes,
                                                          BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<EvaluationCache>( anyCache );

    shapes.initialize( ielement, nfields( ), maxDiffOrder );

    grid_->prepareMapping( ielement, cache.mapping );

    cache.ijkCell = grid_->gridIndices( ielement );
    cache.sameFields = true;
    cache.maxdiff = static_cast<int>( maxDiffOrder );

    if( auto n = nfields( ); n > 0 && cache.maxdiff >= 0 )
    {
        shapes.addDofs( 0, ndofelement( ielement, 0 ) );

        for( size_t ifield = 1; ifield < n; ++ifield )
        {
            shapes.addDofs( ifield, ndofelement( ielement, ifield ) );

            cache.sameFields = cache.sameFields && degrees_[ifield] == degrees_[0];
            cache.sameFields = cache.sameFields && continuities_[ifield] == continuities_[0];
        }
    }

    shapes.allocate( );

    return maxdegrees( ielement );
}

template<size_t D>
void BSplineBasis<D>::evaluateSinglePoint( std::array<double, D> rst,
                                           BasisFunctionEvaluation<D>& shapes,
                                           BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<EvaluationCache>( anyCache );

    for( size_t axis = 0; axis < D; ++axis )
    {
        cache.rstGrid[axis].resize( 1 );
        cache.rstGrid[axis][0] = rst[axis];
    }

    prepareGridEvaluation( cache.rstGrid, anyCache );
    evaluateGridPoint( { }, shapes, anyCache );
}

template<size_t D>
void BSplineBasis<D>::prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                             BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<EvaluationCache>( anyCache );
    
    if( cache.maxdiff < 0 || nfields( ) == 0 )
    {
        return;
    }

    auto mapping = static_cast<const CartesianMapping<D>*>( cache.mapping.mapping.get( ) );

    cache.rstGrid = rst;
    cache.xyzGrid = rst;

    mapping->mapGrid( cache.xyzGrid );

    auto evaluateBSplines = [&]( auto& knotVector, auto& x, size_t icell, size_t p, size_t c )
    {
        cache.tmp.resize( ( p + 1 ) * ( p + 5 ) );

        auto diff = static_cast<size_t>( cache.maxdiff );
        auto nshapes = ( diff + 1 ) * ( p + 1 );
        auto ispan = icell * ( p - c ) + p;

        cache.offsets.push_back( cache.data.size( ) );
        cache.data.resize( cache.offsets.back( ) + nshapes * x.size( ) );

        auto dataSpan = std::span( cache.data ).subspan( 
            cache.offsets.back( ), nshapes * x.size( ) );

        for( size_t i = 0; i < x.size( ); ++i )
        {
                           /* std::fill( cache.tmp.begin( ), cache.tmp.end( ), 0.0 );
                            std::fill( dataSpan.subspan( i * nshapes, nshapes ).begin( ), dataSpan.subspan( i * nshapes, nshapes ).end( ), 0.0 );*/

            polynomial::bspline( knotVector, p, diff, ispan, x[i], 
                dataSpan.subspan( i * nshapes, nshapes ), cache.tmp );
        }
    };

    auto evaluateField = [&, this]( size_t ifield )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            evaluateBSplines( knotVectors_[ifield * D + axis], cache.xyzGrid[axis],
                cache.ijkCell[axis], degrees_[ifield][axis], continuities_[ifield][axis] );
        }
    };

    cache.offsets.resize( 0 );
    cache.data.resize( 0 );

    evaluateField( 0 );

    if( !cache.sameFields )
    {
        for( size_t ifield = 1; ifield < nfields( ); ++ifield )
        {
            evaluateField( ifield );
        }
    }

    cache.offsets.push_back( cache.data.size( ) );
}

template<size_t D>
void BSplineBasis<D>::evaluateGridPoint( std::array<size_t, D> ijkPoint,
                                         BasisFunctionEvaluation<D>& shapes,
                                         BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<EvaluationCache>( anyCache );

    if( cache.maxdiff < 0 || nfields( ) == 0 )
    {
        return;
    }

    auto evaluateComponent = [&]( size_t ifield, 
                                  std::array<size_t, D> diffIndices,
                                  std::span<double> target )
    { 
        auto p = degrees_[ifield];
        auto ndiff = static_cast<size_t>( cache.maxdiff + 1 );
        auto univariate = std::array<std::span<double>, D> { };

        for( size_t axis = 0; axis < D; ++axis )
        {
            auto offset = cache.offsets[ifield * D + axis] + ( p[axis] + 1 ) *
                ( ijkPoint[axis] * ndiff + diffIndices[axis] );

            univariate[axis] = std::span { cache.data }.subspan( offset, p[axis] + 1 );
        }

        auto limits = array::add( p, size_t { 1 } );

        nd::executeWithIndex( limits, [&]( std::array<size_t, D> ijkShape, size_t index )
        {
            target[index] = 1.0;

            for( size_t axis = 0; axis < D; ++axis )
            {
                target[index] *= univariate[axis][ijkShape[axis]];
            }
        } );
    };

    auto evaluateComponents = [&]<size_t maxdiff>( size_t ifield, std::span<double> target )
    {
        auto diffIndices = diff::allIndices<D, maxdiff>( );
        auto nshapes = memory::paddedLength<double>( array::product( 
            array::add( degrees_[ifield], size_t { 1 } ) ) );

        for( size_t icomponent = 0; icomponent < diffIndices.size( ); ++icomponent )
        {
            auto subtarget = target.subspan( icomponent * nshapes, nshapes );

            evaluateComponent( ifield, diffIndices[icomponent], subtarget );
        }

    };

    auto evaluateField = [&]( size_t ifield )
    { 
        auto target = std::span { shapes.get( ifield, 0 ), shapes.get( ifield + 1, 0 ) };
        
        if( cache.maxdiff == 0 ) return evaluateComponents.template operator()<0>( ifield, target );
        if( cache.maxdiff == 1 ) return evaluateComponents.template operator()<1>( ifield, target );
        if( cache.maxdiff == 2 ) return evaluateComponents.template operator()<2>( ifield, target );

        MLHP_THROW( "Diff orders > 2 not implemented." );
    };

    evaluateField( 0 );

    for( size_t ifield = 1; ifield < nfields( ); ++ifield )
    {
        if( !cache.sameFields )
        {
            evaluateField( ifield );
        }
        else
        {
            std::copy( shapes.get( 0, 0 ), shapes.get( 1, 0 ), shapes.get( ifield, 0 ) );
        }
    }

    shapes.setRst( array::extract( cache.rstGrid, ijkPoint ) );
    shapes.setXyz( array::extract( cache.xyzGrid, ijkPoint ) );
}

template<size_t D>
const MeshMapping<D>& BSplineBasis<D>::mapping( BasisEvaluationCache<D>& anyCache ) const
{
    return utilities::cast<EvaluationCache>( anyCache ).mapping;
}

template<size_t D>
void BSplineBasis<D>::locationMap( CellIndex ielement,
                                   LocationMap& target ) const
{
    auto ijkCell = grid_->gridIndices( ielement );
    auto offset = size_t { 0 };

    for( size_t ifield = 0; ifield < nfields( ); ++ifield )
    {
        auto axisDofs = bsplineAxisNDof( knotVectors_, degrees_, ifield );
        auto ijkDof0 = bsplineAxisFirstDof( degrees_, continuities_, ijkCell, ifield );
        auto strides = nd::stridesFor( axisDofs );
        auto limits = array::add( degrees_[ifield], size_t { 1 } );
        auto size0 = utilities::increaseSizes( array::product( limits ), target )[0];

        nd::executeWithIndex( limits, [&]( std::array<size_t, D> ijk, size_t index )
        { 
            target[size0 + index] = nd::linearIndex( strides, array::add( ijkDof0, ijk ) ) + offset;
        } );

        offset += axisDofs[0] * strides[0];
    }
}

template<size_t D>
DofIndex BSplineBasis<D>::faceDofs( CellIndex /* ielement */,
                                    size_t iface, 
                                    size_t ifield,
                                    std::vector<size_t>& localDofs ) const
{
    auto offset = size_t { 0 };

    for( size_t jfield = 0; jfield < ifield; ++jfield )
    {
        offset += array::product( array::add( degrees_[jfield], size_t { 1 } ) );
    }

    auto limits = array::add( degrees_[ifield], size_t{ 1 } );
    auto strides = nd::stridesFor( limits );
    auto normalIndex = ( iface % 2 ) * ( degrees_[ifield][iface / 2] );

    limits[iface / 2] = 1;

    auto size0 = utilities::increaseSizes( array::product( limits ), localDofs )[0];

    nd::executeWithIndex( limits, [&]( std::array<size_t, D> ijkDof, size_t index )
    {
        ijkDof[iface / 2] = normalIndex;

        localDofs[size0 + index] = nd::linearIndex( strides, ijkDof ) + offset;
    } );

    return offset;
}

template<size_t D>
std::array<size_t, D> BSplineBasis<D>::maxdegrees( CellIndex /* ielement */ ) const
{
    auto degrees = array::makeSizes<D>( 0 );

    for( size_t ifield = 0; ifield < nfields( ); ++ifield )
    {
        degrees = array::maxArray( degrees, degrees_[ifield] );
    }

    return degrees;
}

template<size_t D>
void print( const BSplineBasis<D>& basis, std::ostream& os )
{
    auto average = basis::averageNumberOfElementDofs( basis );

    os << "BSplineBasis<" << D << "> (address: " << &basis << ")\n";
    os << "    number of elements         : " << basis.nelements( ) << "\n";
    os << "    highest polynomial degree  : " << basis::maxdegree( basis ) << "\n";
    os << "    number of unknowns         : " << basis.ndof( ) << "\n";
    os << "    number of field components : " << basis.nfields( ) << "\n";
    os << "    average dofs per element   : " << utilities::roundNumberString( average ) << "\n";
    os << "    heap memory usage          : " << utilities::memoryUsageString( basis.memoryUsage( ) );
    os << std::endl;
}

template<size_t D>
ElementFilterBasis<D>::ElementFilterBasis( const BasisConstSharedPtr<D>& basis,
                                           const FilteredMeshSharedPtr<D>& mesh ) :
    basis_( basis ), mesh_( mesh )
{
    MLHP_CHECK( &basis->mesh( ) == &mesh->unfilteredMesh( ),
                "In ElementFilterBasis: Filtered mesh and original "
                "basis must be defined on the same mesh" );

    std::vector<bool> dofMask( basis->ndof( ), false );
    std::vector<DofIndex> locationMap;

    for( CellIndex icell = 0; icell < mesh->ncells( ); ++icell )
    {
        locationMap.resize( 0 );

        basis->locationMap( mesh->unfilteredIndex( icell ), locationMap );

        for( auto dof : locationMap )
        {
            dofMask[dof] = true;
        }
    }

    ndof_ = std::accumulate( dofMask.begin( ), dofMask.end( ), DofIndex { 0 } );
    reductionMap_ = algorithm::backwardIndexMap<DofIndex>( dofMask );
}

template<size_t D>
size_t ElementFilterBasis<D>::memoryUsage( ) const
{
    return utilities::vectorInternalMemory( reductionMap_ );
}

template<size_t D>
std::vector<DofIndex> ElementFilterBasis<D>::reductionMap( ) const
{ 
    return reductionMap_; 
}

template<size_t D>
std::vector<DofIndex> ElementFilterBasis<D>::expansionMap( ) const
{
    auto condition = []( auto value ) { return value != NoDof; };
    auto size = std::count_if( reductionMap_.begin( ), reductionMap_.end( ), condition );

    auto map = std::vector<DofIndex>( static_cast<size_t>( size ) );
    auto count = size_t { 0 };

    for( DofIndex idof = 0; idof < reductionMap_.size( ); ++idof )
    {
        if( reductionMap_[idof] != NoDof )
        {
            map[count++] = idof;
        }
    }

    return map;
}

template<size_t D>
FieldFilterBasis<D>::FieldFilterBasis( memory::vptr<const AbsBasis<D>> basis, size_t ifield ) :
    basis_ { basis }, ifield_ { ifield }
{
    auto nelements = static_cast<std::int64_t>( basis->nelements( ) );
    auto mask = std::vector<std::uint8_t>( basis->ndof( ), 0 );

    #pragma omp parallel
    {
        auto locationMap = LocationMap { };

        #pragma omp for schedule(static)
        for( std::int64_t ii = 0; ii < nelements; ++ii )
        {
            auto ielement = static_cast<CellIndex>( ii );
            auto offset = basis::fieldComponentOffset( *basis_, ielement, ifield_ );
            auto nfielddof = basis_->ndofelement( ielement, ifield_ );

            basis_->locationMap( ielement, utilities::resize0( locationMap ) );

            for( size_t idof = 0; idof < nfielddof; ++idof )
            {
                mask[locationMap[offset + idof]] = 1;
            }
        }
    }

    ndof_ = std::accumulate( mask.begin( ), mask.end( ), DofIndex { 0 } );
    dofMap_ = algorithm::backwardIndexMap<DofIndex>( mask );
    dofMask_ = utilities::convertVector<bool>( mask );
}

template<size_t D>
std::vector<DofIndex> FieldFilterBasis<D>::dofIndexMap( bool invert ) const
{
    if( invert )
    {
        return algorithm::forwardIndexMap<DofIndex>( dofMask_ );
    }

    return dofMap_;
}

template<size_t D>
const AbsMesh<D>& FieldFilterBasis<D>::mesh( ) const
{
    return basis_->mesh( );
}
    
template<size_t D>
MeshConstSharedPtr<D> FieldFilterBasis<D>::meshPtr( ) const
{
    return basis_->meshPtr( );
}

template<size_t D>
std::array<size_t, D> FieldFilterBasis<D>::maxdegrees( CellIndex ielement ) const
{
    return basis_->maxdegrees( ielement );
}

template<size_t D>
CellIndex FieldFilterBasis<D>::nelements( ) const
{
    return basis_->nelements( );
}

template<size_t D>
DofIndex FieldFilterBasis<D>::ndof( ) const
{
    return ndof_;
}

template<size_t D>
DofIndex FieldFilterBasis<D>::ndofelement( CellIndex ielement ) const
{
    return basis_->ndofelement( ielement, ifield_ );
}

template<size_t D>
DofIndex FieldFilterBasis<D>::ndofelement( CellIndex ielement, 
                                           size_t fieldIndex ) const
{
    MLHP_CHECK( fieldIndex == 0, "Field index out of bounds." );

    return ndofelement( ielement );
}

template<size_t D>
size_t FieldFilterBasis<D>::nfields( ) const
{
    return 1;
}

template<size_t D>
void FieldFilterBasis<D>::locationMap( CellIndex ielement, 
                                       LocationMap& target ) const
{
    auto begin = target.size( );
    auto offset = basis::fieldComponentOffset( *basis_, ielement, ifield_ );
    auto nfielddof = basis_->ndofelement( ielement, ifield_ );

    basis_->locationMap( ielement, target );

    for( size_t idof = 0; idof < nfielddof; ++idof )
    {
        target[idof + begin] = dofMap_[target[idof + offset + begin]];
    }

    target.resize( begin + nfielddof );
}

template<size_t D>
DofIndex FieldFilterBasis<D>::faceDofs( CellIndex ielement,
                                        size_t iface, 
                                        size_t ifield,
                                        std::vector<size_t>& localDofs ) const
{
    MLHP_CHECK( ifield == 0, "Nonzero field index." );

    auto offset = basis::fieldComponentOffset( *basis_, ielement, ifield_ );
    auto begin = localDofs.size( );

    basis_->faceDofs( ielement, iface, ifield_, localDofs );

    for( auto index = begin; index < localDofs.size( ); ++index )
    {
        localDofs[index] -= offset;
    }

    return 0;
}

template<size_t D>
struct FieldFilterBasis<D>::Cache
{
    BasisEvaluationCache<D> unfilteredCache;
    BasisFunctionEvaluation<D> unfilteredShapes;
};

namespace
{

template<size_t D>
void extractFieldShapes( const BasisFunctionEvaluation<D>& unfiltered,
                         BasisFunctionEvaluation<D>& filtered,
                         size_t ifield )
{
    filtered.setRst( unfiltered.rst( ) );
    filtered.setXyz( unfiltered.xyz( ) );

    std::copy( unfiltered.get( ifield, 0 ), 
               unfiltered.get( ifield + 1, 0 ), 
               filtered.get( 0, 0 ) );
}

} // namespace

template<size_t D>
BasisEvaluationCache<D> FieldFilterBasis<D>::createEvaluationCache( ) const
{
    return Cache { basis_->createEvaluationCache( ), BasisFunctionEvaluation<D> { } };
}

template<size_t D>
std::array<size_t, D> FieldFilterBasis<D>::prepareEvaluation( CellIndex ielement,
                                                              size_t maxDiffOrder,
                                                              BasisFunctionEvaluation<D>& shapes,
                                                              BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );

    auto degrees = basis_->prepareEvaluation( ielement, maxDiffOrder, 
        cache.unfilteredShapes, cache.unfilteredCache );

    shapes.initialize( ielement, 1, maxDiffOrder );
    shapes.addDofs( 0, cache.unfilteredShapes.ndof( ifield_ ) );
    shapes.allocate( );
 
    return degrees;
}

template<size_t D>
void FieldFilterBasis<D>::prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                                 BasisEvaluationCache<D>& anyCache ) const
{
    basis_->prepareGridEvaluation( rst, utilities::cast<Cache>( anyCache ).unfilteredCache );
}

template<size_t D>
void FieldFilterBasis<D>::evaluateGridPoint( std::array<size_t, D> ijk,
                                             BasisFunctionEvaluation<D>& shapes,
                                             BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );

    basis_->evaluateGridPoint( ijk, cache.unfilteredShapes, cache.unfilteredCache );

    extractFieldShapes( cache.unfilteredShapes, shapes, ifield_ );
}

template<size_t D>
void FieldFilterBasis<D>::evaluateSinglePoint( std::array<double, D> rst,
                                               BasisFunctionEvaluation<D>& shapes,
                                               BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );

    basis_->evaluateSinglePoint( rst, cache.unfilteredShapes, cache.unfilteredCache );

    extractFieldShapes( cache.unfilteredShapes, shapes, ifield_ );
}

template<size_t D>
const MeshMapping<D>& FieldFilterBasis<D>::mapping( BasisEvaluationCache<D>& cache ) const
{
    return basis_->mapping( utilities::cast<Cache>( cache ).unfilteredCache );
}

template<size_t D>
size_t FieldFilterBasis<D>::memoryUsage( ) const
{
    return utilities::vectorInternalMemory( dofMap_ );
}

template<size_t D>
size_t DofOffsetBasis<D>::memoryUsage( ) const
{
    return 0;
}

template<size_t D>
UnstructuredBasis<D>::UnstructuredBasis( const UnstructuredMeshSharedPtr& mesh,
                                         size_t nfields ) :
    mesh_ { mesh }, nfields_ { nfields }
{ }

template<size_t D>
const AbsMesh<D>& UnstructuredBasis<D>::mesh( ) const
{
    return *mesh_;
}

template<size_t D>
MeshConstSharedPtr<D> UnstructuredBasis<D>::meshPtr( ) const
{
    return mesh_;
}

template<size_t D>
CellIndex UnstructuredBasis<D>::nelements( ) const
{
    return mesh_->ncells( );
}

template<size_t D>
DofIndex UnstructuredBasis<D>::ndof( ) const
{
    return static_cast<DofIndex>( nfields_ * mesh_->nvertices( ) );
}

template<size_t D>
DofIndex UnstructuredBasis<D>::ndofelement( CellIndex ielement ) const
{
    return static_cast<DofIndex>( nfields_ * mesh_->nvertices( ielement ) );
}

template<size_t D>
DofIndex UnstructuredBasis<D>::ndofelement( CellIndex ielement, size_t ) const
{
    return static_cast<DofIndex>( mesh_->nvertices( ielement ) );
}

template<size_t D>
size_t UnstructuredBasis<D>::nfields( ) const
{
    return nfields_;
}

template<size_t D>
std::array<size_t, D> UnstructuredBasis<D>::maxdegrees( CellIndex ) const
{
    return array::make<D>( size_t { 1 } );
}

template<size_t D>
void UnstructuredBasis<D>::locationMap( CellIndex ielement,
                                        LocationMap& locationMap ) const
{
    auto size = locationMap.size( );
    auto nvertices = mesh_->nvertices( ielement );

    locationMap.resize( size + nvertices * nfields_ );

    for( size_t ivertex = 0; ivertex < nvertices; ++ivertex )
    {
        auto globalIndex = nfields_ * mesh_->vertexIndex( ielement, ivertex );

        for( size_t ifield = 0; ifield < nfields_; ++ifield )
        {
            locationMap[size + ifield * nvertices + ivertex] = 
                static_cast<DofIndex>( globalIndex + ifield );
        }
    }
}

template<size_t D>
DofIndex UnstructuredBasis<D>::faceDofs( CellIndex ielement,
                                         size_t iface, 
                                         size_t ifield,
                                         std::vector<size_t>& localDofs ) const
{

    auto size = localDofs.size( );
    auto type = mesh_->cellType( ielement );
    auto nvertices = topology::nvertices<D>( type );
    
    topology::faceVertices<D>( type, iface, localDofs );

    for( auto i = size; i < localDofs.size( ); ++i )
    {
        localDofs[i] += ifield * nvertices;
    };

    return static_cast<DofIndex>( ifield * nvertices );
}

namespace
{

template<size_t D>
struct UnstructuredBasisCache
{
    //std::array<std::vector<double>, D> evaluation;

    CellIndex ielement = NoCell;
    CellType type      = CellType::NCube;
    size_t maxdiff     = 0;

    MeshMapping<D> mapping;
    const CoordinateVectors<D>* rst = nullptr;
};

} // namespace

template<size_t D>
BasisEvaluationCache<D> UnstructuredBasis<D>::createEvaluationCache( ) const
{
    return UnstructuredBasisCache<D> { .mapping = mesh_->createMapping( ) };
}

template<size_t D>
std::array<size_t, D> UnstructuredBasis<D>::prepareEvaluation( CellIndex ielement,
                                                               size_t maxDiffOrder,
                                                               BasisFunctionEvaluation<D>& shapes,
                                                               BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<UnstructuredBasisCache<D>>( anyCache );

    cache.ielement = ielement;
    cache.type = mesh_->cellType( ielement );
    cache.maxdiff = maxDiffOrder;
    
    auto nvertices = topology::nvertices<D>( cache.type );

    mesh_->prepareMapping( cache.ielement, cache.mapping );

    shapes.initialize( ielement, nfields_, maxDiffOrder );
    
    for( size_t ifield = 0; ifield < nfields_; ++ifield )
    {
        shapes.addDofs( ifield, nvertices );
    }

    shapes.allocate( );

    return maxdegrees( ielement );
}

template<size_t D>
void UnstructuredBasis<D>::evaluateSinglePoint( std::array<double, D> rst,
                                                BasisFunctionEvaluation<D>& shapes,
                                                BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<UnstructuredBasisCache<D>>( anyCache );

    auto evaluateDiff = [&]<size_t maxdiff>( )
    {
        auto evaluate = [&]( auto&& evaluateShapes )
        {
            constexpr auto allindices = diff::allIndices<D, maxdiff>( );
            auto ndofpadded = shapes.ndofpadded( 0 );

            for( size_t idiff = 0; idiff < allindices.size( ); ++idiff )
            {
                auto N = evaluateShapes( rst, allindices[idiff] );

                for( size_t ifield = 0; ifield < nfields_; ++ifield )
                {
                    std::copy( N.begin( ), N.end( ), shapes.get( ifield, 0 ) + idiff * ndofpadded );
                }
            }
        };

        if( cache.mapping.type == CellType::NCube ) evaluate( spatial::multilinearShapeFunctions<D> );
        if( cache.mapping.type == CellType::Simplex ) evaluate( spatial::simplexShapeFunctions<D> );
    };
    
    if( cache.maxdiff == 0 ) evaluateDiff.template operator()<0>( );
    if( cache.maxdiff == 1 ) evaluateDiff.template operator()<1>( );
    if( cache.maxdiff == 2 ) evaluateDiff.template operator()<2>( );
    
    shapes.setRst( rst );

    mapBasisEvaluation( shapes, cache.mapping );
}

template<size_t D>
void UnstructuredBasis<D>::prepareGridEvaluation( const CoordinateGrid<D>& rst,
                                                  BasisEvaluationCache<D>& anyCache ) const
{
    utilities::cast<UnstructuredBasisCache<D>>( anyCache ).rst = &rst;
}

template<size_t D>
void UnstructuredBasis<D>::evaluateGridPoint( std::array<size_t, D> ijk,
                                              BasisFunctionEvaluation<D>& shapes,
                                              BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<UnstructuredBasisCache<D>>( anyCache );

    evaluateSinglePoint( array::extract( *cache.rst, ijk ), shapes, anyCache );
}

template<size_t D>
const MeshMapping<D>& UnstructuredBasis<D>::mapping( BasisEvaluationCache<D>& anyCache ) const
{
    return utilities::cast<UnstructuredBasisCache<D>>( anyCache ).mapping;
}

template<size_t D>
size_t UnstructuredBasis<D>::memoryUsage( ) const
{
    return 0;
}

template<size_t D>
DummyBasis<D>::DummyBasis( const AbsMesh<D>& mesh, size_t nfields ) :
    nfields_ { nfields }, mesh_ { &mesh }
{ }

template<size_t D>
DummyBasis<D>::DummyBasis( std::shared_ptr<const AbsMesh<D>> mesh, size_t nfields ) :
    nfields_ { nfields }, mesh_ { std::move( mesh ) }
{ }

template<size_t D>
struct DummyBasis<D>::Cache
{
    MeshMapping<D> mapping;
    CoordinateGrid<D> rstGrid;
};

template<size_t D>
BasisEvaluationCache<D> DummyBasis<D>::createEvaluationCache( ) const
{
    return Cache { mesh_->createMapping( ), { } };
}

template<size_t D>
std::array<size_t, D> DummyBasis<D>::prepareEvaluation( CellIndex ielement,
                                                        size_t maxDiffOrder,
                                                        BasisFunctionEvaluation<D>& shapes,
                                                        BasisEvaluationCache<D>& anyCache ) const
{
    auto& cache = utilities::cast<Cache>( anyCache );

    mesh_->prepareMapping( ielement, cache.mapping );

    shapes.initialize( ielement, nfields_, maxDiffOrder );
    shapes.allocate( );

    return array::makeSizes<D>( 0 );
}

template<size_t D>
void DummyBasis<D>::evaluateSinglePoint( std::array<double, D> rst,
                                         BasisFunctionEvaluation<D>& shapes,
                                         BasisEvaluationCache<D>& anyCache ) const
{
    shapes.setRst( rst );
    shapes.setXyz( utilities::cast<Cache>( anyCache ).mapping( rst ) );
}

template<size_t D>
void DummyBasis<D>::prepareGridEvaluation( const CoordinateGrid<D>& rstGrid,
                                           BasisEvaluationCache<D>& anyCache ) const
{
    utilities::cast<Cache>( anyCache ).rstGrid = rstGrid;
}

template<size_t D>
void DummyBasis<D>::evaluateGridPoint( std::array<size_t, D> ijk,
                                       BasisFunctionEvaluation<D>& shapes,
                                       BasisEvaluationCache<D>& anyCache ) const
{
    auto rst = array::extract( utilities::cast<Cache>( anyCache ).rstGrid, ijk );

    evaluateSinglePoint( rst, shapes, anyCache );
}

template<size_t D>
const MeshMapping<D>& DummyBasis<D>::mapping( BasisEvaluationCache<D>& anyCache ) const
{
    return utilities::cast<Cache>( anyCache ).mapping;
}

template<size_t D>
void print( const UnstructuredBasis<D>& basis, std::ostream& os )
{
    auto average = basis::averageNumberOfElementDofs( basis );

    os << "UnstructuredBasis<" << D << "> (address: " << &basis << ")\n";
    os << "    number of elements         : " << mesh::analyzeCellTypes( basis.mesh( ) ) << "\n";
    os << "    number of unknowns         : " << basis.ndof( ) << "\n";
    os << "    number of field components : " << basis.nfields( ) << "\n";
    os << "    average dofs per element   : " << utilities::roundNumberString( average ) << "\n";
    os << "    heap memory usage          : " << utilities::memoryUsageString( basis.memoryUsage( ) );
    os << std::endl;
}

namespace detail
{

template<size_t D>
auto makeUniformAnsatzTemplates( std::array<size_t, D> degrees, size_t nleaves, size_t numberOfFieldComponents )
{
    AnsatzTemplateVector ansatzTemplates( { nleaves, numberOfFieldComponents, D }, 0 );

    auto data = memory::assumeNoalias( &ansatzTemplates[0] );
    auto nint = static_cast<std::int64_t>( nleaves );

    #pragma omp parallel for schedule(static)
    for( std::int64_t ii = 0; ii < nint; ++ii )
    {
        auto ielement = static_cast<size_t>( ii );

        for( size_t ifield = 0; ifield < numberOfFieldComponents; ++ifield )
        {
            auto fieldPtr = data + ( ielement * numberOfFieldComponents + ifield ) * D;

            for( size_t axis = 0; axis < D; ++axis )
            {
                fieldPtr[axis] = degrees[axis];
            }
        }
    }

    return ansatzTemplates;
}

template<size_t D>
auto makeGradedAnsatzTemplates( const AbsHierarchicalGrid<D>& grid,
                                size_t numberOfFieldComponents,
                                std::array<size_t, D> pBase,
                                std::array<size_t, D> pLeaf )
{
    auto levels = mesh::refinementLevels( grid );

    AnsatzTemplateVector ansatzTemplates( { levels.size( ), numberOfFieldComponents, D } );

    if( levels.empty( ) )
    {
        return ansatzTemplates;
    }

    auto maxLevel = *std::max_element( levels.begin( ), levels.end( ) );

    for( CellIndex ileaf = 0; ileaf < grid.nleaves( ); ++ileaf )
    {
        for( size_t field = 0; field < numberOfFieldComponents; ++field )
        {
            double t = maxLevel == 0 ? 0.0 : levels[ileaf] / static_cast<double>( maxLevel );

            for( size_t axis = 0; axis < D; ++axis )
            {
                size_t degree = static_cast<size_t>( std::lround( t * pLeaf[axis] + ( 1.0 - t ) * pBase[axis] ) );

                ansatzTemplates( ileaf, field, axis ) = degree;
            }
        }
    }

    return ansatzTemplates;
}

} // namespace detail

namespace basis
{

template<size_t D> MLHP_EXPORT
LocationMapVector locationMapVector( const AbsBasis<D>& basis )
{
    LocationMapVector maps( basis.nelements( ) );

    for( CellIndex iElement = 0; iElement < maps.size( ); ++iElement )
    {
        basis.locationMap( iElement, maps[iElement] );
    }

    return maps;
}

template<size_t D>
LocationMapRange locationMapRange( const AbsBasis<D>& basis )
{
    std::function access = [&]( CellIndex ielement, LocationMap& target )
    { 
        basis.locationMap( ielement, target );
    };

    return utilities::makeIndexRangeFunction( basis.nelements( ), access );
}

template<size_t D>
LocationMap locationMap( const AbsBasis<D>& basis, 
                         CellIndex ielement )
{
    auto locationMap = LocationMap { };

    basis.locationMap( ielement, locationMap );

    return locationMap;
}

template<size_t D>
DofIndex fieldComponentOffset( const AbsBasis<D>& basis,
                                   CellIndex ielement, 
                                   size_t fieldIndex )
{
    DofIndex offset = 0;

    for( size_t ifield = 0; ifield < fieldIndex; ++ifield )
    {
        offset += basis.ndofelement(ielement, ifield);
    }

    return offset;
}

template<size_t D>
double averageNumberOfElementDofs( const AbsBasis<D>& basis )
{
    std::uint64_t ndof = 0;

    for( CellIndex iCell = 0; iCell < basis.nelements( ); ++iCell )
    {
        ndof += basis.ndofelement( iCell );
    }

    return static_cast<double>( ndof ) / basis.nelements( );
}

template<size_t D>
AnsatzTemplateVector createAnsatzTemplates( const std::vector<std::array<size_t, D>>& degrees,
                                            size_t nfields )
{
    AnsatzTemplateVector templates( { degrees.size( ), nfields, D } );

    for( size_t ielement = 0; ielement < degrees.size( ); ++ielement )
    {
        for( size_t ifield = 0; ifield < nfields; ++ifield )
        {
            for( size_t axis = 0; axis < D; ++axis )
            {
                templates( ielement, ifield, axis ) = degrees[ielement][axis];
            }
        }
    }

    return templates;
}

template<size_t D> 
DofIndex faceDofsWithoutOffset( const AbsBasis<D>& basis,
                                CellIndex ielement,
                                size_t iface,
                                size_t ifield,
                                std::vector<size_t>& target )
{
    auto offset = basis.faceDofs( ielement, iface, ifield, target );
    auto predicate = [=]( auto value ) { return value - static_cast<size_t>( offset ); };

    std::transform( target.begin( ), target.end( ), target.begin( ), predicate );

    return offset;
}

template<size_t D>
std::vector<std::array<size_t, D>> maxdegrees( const AbsBasis<D>& basis )
{
    auto nelements = basis.nelements( );
    auto degrees = std::vector<std::array<size_t, D>>( nelements );

    #pragma omp parallel for schedule( dynamic, 7 )
    for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( nelements ); ++ii )
    {
        auto ielement = static_cast<CellIndex>( ii );
        degrees[ielement] = basis.maxdegrees( ielement );
    }

    return degrees;
}

template<size_t D>
size_t maxdegree( const AbsBasis<D>& basis )
{
    auto nelements = basis.nelements( );
    auto degree = size_t { 0 };

    #pragma omp parallel
    {
        auto local = size_t { 0 };

        #pragma omp for schedule( dynamic, 7 )
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( nelements ); ++ii )
        {
            auto ielement = static_cast<CellIndex>( ii );

            local = std::max( local, array::maxElement( basis.maxdegrees( ielement ) ) );
        }

        #pragma omp critical
        {
            degree = std::max( degree, local );
        }
    }

    return degree;
}

template<size_t D>
LinearizedVectors<CellIndex> findSupportElements( const AbsBasis<D>& basis,
                                                  const std::vector<DofIndex>& dofs )
{
    auto offsets = std::vector<size_t>( dofs.size( ) + 1 );
    auto elements = std::vector<CellIndex> { };

    offsets[0] = 0;

    if( !dofs.empty( ) )
    {
        auto nelements = static_cast<std::int64_t>( basis.nelements( ) );
        auto ndof = static_cast<std::int64_t>( dofs.size( ) );

        auto count = std::vector<size_t>( dofs.size( ), 0 );
        auto map = algorithm::invertRepeatedIndices( dofs );

        #pragma omp parallel
        {
            auto locationMap = std::vector<DofIndex> { };
            auto supports = std::vector<std::pair<DofIndex, CellIndex>>{ };

            #pragma omp for schedule( dynamic )
            for( std::int64_t ii = 0; ii < nelements; ++ii )
            {
                auto ielement = static_cast<CellIndex>( ii );

                utilities::resize0( locationMap );

                basis.locationMap( ielement, locationMap );

                for( auto dof : locationMap )
                {
                    if( dof + DofIndex { 1 } < map.first.size( ) )
                    {
                        for( auto index : utilities::linearizedSpan( map, dof ) )
                        {
                            #pragma omp atomic
                            offsets[index + 1] += 1;

                            supports.emplace_back( index, ielement );
                        }
                    }
                }
            } // for ielement

            #pragma omp barrier
            { }

            #pragma omp single
            {
                std::partial_sum( offsets.begin( ), offsets.end( ), offsets.begin( ) );

                elements.resize( offsets.back( ) );
            }

            #pragma omp critical
            {
                for( auto [index, ielement] : supports )
                {
                    auto offset = offsets[index] + count[index];

                    elements[offset] = ielement;

                    count[index] += 1;
                }
            }

        } // omp parallel

        #pragma omp parallel for
        for( std::int64_t ii = 0; ii < ndof; ++ii )
        {
            auto i0 = utilities::ptrdiff( offsets[static_cast<size_t>( ii )] );
            auto i1 = utilities::ptrdiff( offsets[static_cast<size_t>( ii ) + 1] );

            std::sort( elements.begin( ) + i0, elements.begin( ) + i1 );
        }

    } // if any dof

    return { offsets, elements };
}

template<size_t D>
DofIndexVector findSupportedDofs( const AbsBasis<D>& basis,
                                  const std::vector<CellIndex>& cells,
                                  const std::vector<DofIndex>& dirichletIndices,
                                  bool exclusive,
                                  bool invert )
{
    auto nelements = basis.nelements( );
    auto ndof = basis.ndof( );

    auto complimentary = CellIndexVector { };
    auto cellsPtr = &cells;

    MLHP_CHECK( cells.empty( ) || *std::ranges::max_element( cells ) < 
        nelements, "Invalid element index in support computation." );

    if( exclusive )
    {
        complimentary = algorithm::complementaryIndices( cells, nelements );

        cellsPtr = &complimentary;

        invert = !invert;
    }
    
    auto size = static_cast<std::int64_t>( cellsPtr->size( ) );
    auto count = std::vector<DofIndex>( ndof, 0 );
    auto dirichletMask = algorithm::indexMask( dirichletIndices, ndof );

    #pragma omp parallel
    {
        auto locationMap = LocationMap { };
        
        #pragma omp for schedule(dynamic, 7)
        for( std::int64_t ii = 0; ii < size; ++ii )
        {
            auto icell = ( *cellsPtr )[static_cast<size_t>( ii )];

            basis.locationMap( icell, utilities::resize0( locationMap ) );

            for( auto idof : locationMap )
            {
                #pragma omp atomic
                count[idof] += 1;
            }
        }
    }

    auto nsupport = size_t { 0 };

    for( size_t i = 0; i < count.size( ); ++i )
    {
        nsupport += !dirichletMask[i] && static_cast<bool>( count[i] ) != invert;
    }

    auto indices = std::vector<DofIndex>( nsupport );

    auto mapIndex = size_t { 0 };
    auto dofIndex = DofIndex { 0 };

    for( size_t i = 0; i < count.size( ); ++i )
    {
        if( !dirichletMask[i] )
        {
            if( static_cast<bool>( count[i] ) != invert )
            {
                indices[mapIndex++] = dofIndex;
            }

            dofIndex += 1;
        }
    }

    return indices;
}


namespace
{

template<size_t D, size_t F = std::dynamic_extent>
auto makeEvaluatorHelper( memory::vptr<const AbsBasis<D>> basis, size_t maxdiff = 0 )
{
    using OptionalEvaluatorHelper = std::optional<std::pair<const BasisFunctionEvaluation<D>*, 
                                                            const LocationMap*>>;
    
    // Data needed on each thread for solution evaluation 
    struct Cache
    {
        std::vector<DofIndex> locationMap;
        std::unique_ptr<AbsBackwardMapping<D>> backwardMapping;
        BasisFunctionEvaluation<D> shapes;
        BasisEvaluationCache<D> basisCache;
    };
    
    // Initialize cache for each thread
    auto createBackwardMapping = basis->mesh( ).createBackwardMappingFactory( );
    auto threadLocal = std::make_shared<utilities::ThreadLocalContainer<Cache>>( );
    auto nthreads = parallel::getMaxNumberOfThreads( );

    for( size_t ithread = 0; ithread < nthreads; ++ithread )
    {
        threadLocal->data[ithread].backwardMapping = createBackwardMapping( );
        threadLocal->data[ithread].basisCache = basis->createEvaluationCache( );
    }

    return [=]( std::array<double, D> xyz ) ->OptionalEvaluatorHelper
    {
        auto& cache = threadLocal->get( );

        // Find element index and local coordinates
        if( auto result = cache.backwardMapping->map( xyz ); result )
        {
            auto [ielement, rst] = *result;

            // Obtain location map and evaluate basis functions
            basis->locationMap( ielement, utilities::resize0( cache.locationMap ) );
            basis->prepareEvaluation( ielement, maxdiff, cache.shapes, cache.basisCache );
            basis->evaluateSinglePoint( rst, cache.shapes, cache.basisCache );

            return std::pair { &cache.shapes, &cache.locationMap };
        }

        return std::nullopt;
    };
}

} // namespace

template<size_t D>
spatial::ScalarFunction<D> scalarEvaluator( memory::vptr<const AbsBasis<D>> basis,
                                            memory::vptr<const std::vector<double>> dofs,
                                            size_t ifield, 
                                            size_t difforder, 
                                            size_t icomponent,
                                            double outside )
{
    MLHP_CHECK( basis.get( ) != nullptr, "Basis is a null pointer." );
    MLHP_CHECK( dofs.get( ) != nullptr, "Solution dofs is a null pointer." );
    MLHP_CHECK( ifield < basis->nfields( ), "Field component index " + std::to_string( ifield ) + " exceeds number of fields." );
    MLHP_CHECK( dofs->size( ) == basis->ndof( ), "Inconsistent size between dof vector (n = " + 
        std::to_string( dofs->size( ) ) + ") and basis (n = " + std::to_string( basis->ndof( ) ) + ")." );

    auto evaluator = makeEvaluatorHelper( basis, difforder );

    return [=, evaluator = std::move( evaluator )]( std::array<double, D> xyz )
    { 
        if( auto helper = evaluator( xyz ) )
        {
            auto result = 0.0;

            evaluateSolution( *helper->first, *helper->second, *dofs, std::span
                { &result, 1 }, difforder, icomponent, ifield );

            return result;
        }
        
        return outside;
    };
}

template<size_t D>
spatial::VectorFunction<D> vectorEvaluator( memory::vptr<const AbsBasis<D>> basis,
                                            memory::vptr<const std::vector<double>> dofs,
                                            size_t difforder )
{
    MLHP_CHECK( difforder <= 2, "Diff order must be >= 2." );

    auto components = std::vector<EvaluatorComponent<D>> { };
    auto allIndices = diff::allIndices<D, 2>( );
    auto ncomponents = diff::ncomponents<D>( );

    auto diffIndicesOffset = std::accumulate( ncomponents.begin( ), 
        utilities::begin( ncomponents, difforder ) ,size_t { 0 } );

    for( size_t ifield = 0; ifield < basis->nfields( ); ++ifield )
    {
        for( size_t icomponent = 0; icomponent < ncomponents[difforder]; ++icomponent )
        {
            components.push_back( EvaluatorComponent<D> 
            { 
                .ifield = ifield, 
                .defaultValue = 0.0,
                .diffIndices = allIndices[diffIndicesOffset + icomponent] 
            } );
        }
    }

    return vectorEvaluator( std::move( basis ), std::move( dofs ), std::move( components ) );
}

namespace
{

template<size_t D>
auto prepareVectorEvaluator( std::vector<EvaluatorComponent<D>> components, size_t nfields )
{
    // Find the offset for each given diff index (e.g. [0, 0] -> 0, [1, 0] -> 1, [0, 1] -> 2, [2, 0] -> 3, ...).
    auto data = std::vector<std::pair<size_t, size_t>>( components.size( ) );
    auto defaultValues = std::vector<double> ( components.size( ) );
    auto allIndices = diff::allIndices<D, 2>( );
    auto maxdiff = -1;

    for( size_t i = 0; i < components.size( ); ++i )
    {
        auto [ifield, defaultValue, diffIndices] = components[i];
        auto diffOrder = static_cast<int>( array::maxElement( diffIndices ) );
        
        MLHP_CHECK( diffOrder <= 2, "Order of differentiation of (at index " + 
            std::to_string( i ) + ") must be <= 2 (is " + std::to_string( diffOrder ) + ")." );

        MLHP_CHECK( ifield < nfields, "Invalid field component (value = " + 
            std::to_string( ifield ) + " at index " + std::to_string( i ) + ")." );

        maxdiff = std::max( maxdiff, diffOrder );

        auto it = std::find( allIndices.begin( ), allIndices.end( ), diffIndices );

        if( it == allIndices.end( ) )
        {
            auto str = std::stringstream { };

            str << "Unable to find diff indices (" << diffIndices[0];

            for( size_t axis = 1; axis < D; ++axis )
            {
                str << ", " << diffIndices[axis];
            }

            str << ").";

            MLHP_THROW( str.str( ) );
        }

        data[i] = { ifield, static_cast<size_t>( std::distance( allIndices.begin( ), it ) ) };

        defaultValues[i] = defaultValue;
    }

    return std::tuple { std::move( data ), defaultValues, maxdiff };
}

} // namespace

template<size_t D>
spatial::VectorFunction<D> vectorEvaluator( memory::vptr<const AbsBasis<D>> basis,
                                            memory::vptr<const std::vector<double>> dofs,
                                            std::vector<EvaluatorComponent<D>> components )
{   
    MLHP_CHECK( basis.get( ) != nullptr, "Basis is a null pointer." );
    MLHP_CHECK( dofs.get( ) != nullptr, "Solution dofs is a null pointer." );
    MLHP_CHECK( dofs->size( ) == basis->ndof( ), "Inconsistent size between dof vector (n = " + 
        std::to_string( dofs->size( ) ) + ") and basis (n = " + std::to_string( basis->ndof( ) ) + ")." );

    auto data = prepareVectorEvaluator( components, basis->nfields( ) );
    auto evaluator = makeEvaluatorHelper( basis, static_cast<size_t>( std::max( 0, std::get<2>( data ) ) ) );

    auto evaluate = [=,
        evaluator = std::move( evaluator ), 
        components = std::move( std::get<0>( data ) ),
        defaultValues = std::move( std::get<1>( data ) )]
        ( std::array<double, D> xyz, std::span<double> out )
    { 
        if( auto helper = evaluator( xyz ) )
        {
            auto& [shapes, locationMap] = *helper;

            for( size_t i = 0; i < components.size( ); ++i )
            {
                auto& [ifield, diffComponent] = components[i];
                auto dofOffset = fieldOffset<D>( *shapes, ifield );
                auto ndof = shapes->ndof( ifield );
                auto ndofpadded = shapes->ndofpadded( ifield );
                auto N = shapes->noalias( ifield, 0 ) + diffComponent * ndofpadded;

                out[i] = 0.0;

                for( size_t idof = 0; idof < ndof; ++idof )
                {
                    out[i] += N[idof] * ( *dofs )[( *locationMap )[dofOffset + idof]];
                }
            }
        }
        else
        {
            std::copy( defaultValues.begin( ), defaultValues.end( ), out.begin( ) );
        }
    };

    return spatial::VectorFunction<D>{ components.size( ), evaluate };
}

} // namespace basis

template<size_t D>
InitialMaskProvider<D> TensorSpace::initialMaskProvider( )
{
    return &initializeTensorSpaceMasks<D>;
}

template<size_t D>
InitialMaskProvider<D> TrunkSpace::initialMaskProvider( )
{
    return &initializeTrunkSpaceMasks<D>;
}

PolynomialDegreeTuple::PolynomialDegreeTuple( size_t degree ) :
    degrees_( 1, degree ), dimensionality_( 0 )
{ }

PolynomialDegreeTuple::PolynomialDegreeTuple( const std::vector<size_t>& degrees ) :
    degrees_( degrees ), dimensionality_( degrees.size( ) )
{
    MLHP_EXPECTS( dimensionality_ > 0 );
}

template<size_t D>
PolynomialDegreeTuple::PolynomialDegreeTuple( std::array<size_t, D> degrees ) :
    degrees_( degrees.begin( ), degrees.end( ) ), dimensionality_( D )
{ }

template<size_t D>
std::array<size_t, D> PolynomialDegreeTuple::get( )
{
    if( dimensionality_ == 0 )
    {
        return array::makeSizes<D>( degrees_[0] );
    }
    else
    {
        MLHP_CHECK( dimensionality_ == D, "Wrong polynomial degree tuple size." );

        auto degrees = std::array<size_t, D> { };

        std::copy_n( degrees_.begin( ), D, degrees.begin( ) );

        return degrees;
    }
}

template<size_t D>
AnsatzTemplateVector UniformGrading::operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields )
{
    return detail::makeUniformAnsatzTemplates( degrees.get<D>( ), grid.nleaves( ), nfields );
}

template<size_t D>
AnsatzTemplateVector LinearGrading::operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields )
{
    auto fineDegrees_ = fineDegrees.get<D>( );
    auto coarseDegrees = array::add<size_t>( fineDegrees_, mesh::maxRefinementLevel( grid ) );

    return detail::makeGradedAnsatzTemplates( grid, nfields, coarseDegrees, fineDegrees_ );
}

template<size_t D>
AnsatzTemplateVector InterpolatedGrading::operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields )
{
    return detail::makeGradedAnsatzTemplates( grid, nfields, 
        coarseDegrees.get<D>( ), fineDegrees.get<D>( ) );
}

PerLevelGrading::PerLevelGrading( const GradingFunction& gradingFunction ) :
    gradingFunction_( gradingFunction )
{ }

PerLevelGrading::PerLevelGrading( const std::vector<PolynomialDegreeTuple>& degrees )
{ 
    gradingFunction_ = [=]( RefinementLevel level, RefinementLevel maxLevel )
    {
        MLHP_CHECK( maxLevel < degrees.size( ), "To few degrees "
                    "given for refinement depth of mesh" );

        return degrees[level];
    };
}

PerLevelGrading::PerLevelGrading( const PolynomialDegreeVector& degrees ) :
    PerLevelGrading( std::vector<PolynomialDegreeTuple>( degrees.begin( ), degrees.end( ) ) )
{ }

template<size_t D>
AnsatzTemplateVector PerLevelGrading::operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields )
{
    auto maxLevel = mesh::maxRefinementLevel( grid );

    AnsatzTemplateVector ansatzTemplates( { static_cast<size_t>( grid.nleaves( ) ), nfields, D } );

    for( CellIndex iLeaf = 0; iLeaf < grid.nleaves( ); ++iLeaf )
    {
        auto level = grid.refinementLevel( grid.fullIndex( iLeaf ) );
        auto degrees = gradingFunction_( level, maxLevel ).template get<D>( );

        for( size_t iField = 0; iField < nfields; ++iField )
        {
            for( size_t axis = 0; axis < D; ++axis )
            {
                ansatzTemplates( iLeaf, iField, axis ) = degrees[axis];
            }
        }
    }

    return ansatzTemplates;
}

#define MLHP_INSTANTIATE_DIM( D )                                                                                \
                                                                                                                 \
    template class MultilevelHpBasis<D>;                                                                         \
    template class BSplineBasis<D>;                                                                              \
    template class ElementFilterBasis<D>;                                                                        \
    template class UnstructuredBasis<D>;                                                                         \
    template class FieldFilterBasis<D>;                                                                          \
    template class DofOffsetBasis<D>;                                                                            \
    template class DummyBasis<D>;                                                                                \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    void print( const MultilevelHpBasis<D>& basis, std::ostream& os );                                           \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    void print( const BSplineBasis<D>& basis, std::ostream& os );                                                \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    void print( const UnstructuredBasis<D>& basis, std::ostream& os );                                           \
                                                                                                                 \
    namespace basis                                                                                              \
    {                                                                                                            \
        template MLHP_EXPORT                                                                                     \
        LocationMapVector locationMapVector( const AbsBasis<D>& basis );                                         \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        LocationMapRange locationMapRange( const AbsBasis<D>& basis );                                           \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        LocationMap locationMap( const AbsBasis<D>& basis,                                                       \
                                 CellIndex ielement );                                                           \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        DofIndex fieldComponentOffset( const AbsBasis<D>& basis,                                                 \
                                       CellIndex ielement,                                                       \
                                       size_t fieldIndex );                                                      \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        double averageNumberOfElementDofs( const AbsBasis<D>& basis );                                           \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        AnsatzTemplateVector createAnsatzTemplates( const std::vector<std::array<size_t, D>>& degrees,           \
                                                    size_t nfields );                                            \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        DofIndex faceDofsWithoutOffset( const AbsBasis<D>& basis,                                                \
                                        CellIndex ielement,                                                      \
                                        size_t iface,                                                            \
                                        size_t ifield,                                                           \
                                        std::vector<size_t>& target );                                           \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        std::vector<std::array<size_t, D>> maxdegrees( const AbsBasis<D>& basis );                               \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        size_t maxdegree( const AbsBasis<D>& basis );                                                            \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        LinearizedVectors<CellIndex> findSupportElements( const AbsBasis<D>& basis,                              \
                                                          const std::vector<DofIndex>& dofs );                   \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        DofIndexVector findSupportedDofs( const AbsBasis<D>& basis,                                              \
                                          const std::vector<CellIndex>& cells,                                   \
                                          const std::vector<DofIndex>& dirichletIndices,                         \
                                          bool exclusive, bool invert );                                         \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        spatial::ScalarFunction<D> scalarEvaluator( memory::vptr<const AbsBasis<D>> basis,                       \
                                                    memory::vptr<const std::vector<double>> dofs,                \
                                                    size_t ifield,                                               \
                                                    size_t diffOrder,                                            \
                                                    size_t diffComponent,                                        \
                                                    double outside );                                            \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        spatial::VectorFunction<D> vectorEvaluator( memory::vptr<const AbsBasis<D>> basis,                       \
                                                    memory::vptr<const std::vector<double>> dofs,                \
                                                    size_t difforder );                                          \
                                                                                                                 \
        template MLHP_EXPORT                                                                                     \
        spatial::VectorFunction<D> vectorEvaluator( memory::vptr<const AbsBasis<D>> basis,                       \
                                                    memory::vptr<const std::vector<double>> dofs,                \
                                                    std::vector<EvaluatorComponent<D>> components );             \
    }                                                                                                            \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    InitialMaskProvider<D> TensorSpace::initialMaskProvider<D>( );                                               \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    InitialMaskProvider<D> TrunkSpace::initialMaskProvider<D>( );                                                \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    PolynomialDegreeTuple::PolynomialDegreeTuple( std::array<size_t, D> degrees );                               \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    std::array<size_t, D> PolynomialDegreeTuple::get<D>( );                                                      \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    AnsatzTemplateVector UniformGrading::operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields );       \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    AnsatzTemplateVector LinearGrading::operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields );        \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    AnsatzTemplateVector InterpolatedGrading::operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields );  \
                                                                                                                 \
    template MLHP_EXPORT                                                                                         \
    AnsatzTemplateVector PerLevelGrading::operator()( const AbsHierarchicalGrid<D>& grid, size_t nfields );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // mlhp
