// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/multilevelhpcore.hpp"
#include "mlhp/core/arrayfunctions.hpp"
#include "mlhp/core/utilities.hpp"
#include "mlhp/core/algorithm.hpp"
#include "mlhp/core/memory.hpp"

namespace mlhp
{
namespace
{

template<size_t D>
using MaskIndexType = TensorProductIndices<D>;

template<size_t D>
using IndexShapeStrides = std::tuple<size_t, MaskIndexType<D>, std::array<size_t, D>>;

template<size_t D>
using LinearizedTensorProductMasks = std::pair<std::vector<std::uint8_t>,
                                               std::vector<IndexShapeStrides<D>>>;

template<size_t D>
void analyzeDegrees( const PolynomialDegreesVector<D>& degrees )
{
    for( auto degree : degrees )
    {
        MLHP_CHECK( array::maxElement( degree ) < NoValue<PolynomialDegree>,
            "Polynomial degree too high for data type used." );

        MLHP_CHECK( array::minElement( degree ) > 0,
                    "Zero polynomial degree currently not supported." );
    }
}

template<size_t D>
auto gatherTensorProductMaskShapes( const NCubeNeighboursVector<D>& neighbours,
                                    const std::vector<bool>& leafMask,
                                    const RefinementLevelVector& levels,
                                    const PolynomialDegreesVector<D>& degrees )
{
    analyzeDegrees( degrees );

    auto indexMap = algorithm::backwardIndexMap<CellIndex>( leafMask );

    std::vector<MaskIndexType<D>> shapes( levels.size( ), MaskIndexType<D> { } );

    using VisitedArray = typename nd::EquallySizedStaticArray<bool, D, 3>::type;

    // Recursive lambda to increase mask shape in neighbour
    auto gatherShape = [&]( auto&& self, 
                            VisitedArray& visited,
                            CellIndex cell,
                            MaskIndexType<D>& shape,
                            std::array<size_t, D> indices ) -> void
    {
        if( auto leafIndex = indexMap[cell]; leafIndex != NoCell )
        {
            for( size_t axis = 0; axis < D; ++axis )
            {
                auto p = indices[axis] == 1 ? degrees[leafIndex][axis] : 1;

                shape[axis] = std::max( shape[axis], static_cast<PolynomialDegree>( p + 1 ) );
            }
        }

        visited[indices] = true;

        for( size_t axis = 0; axis < D; ++axis )
        {
            for( size_t side = 0; indices[axis] == 1 && side < 2; ++side )
            {
                auto newIndices = array::setEntry<size_t>( indices, axis, 2 * side );

                if( !visited[newIndices] )
                {
                    auto neighbour = neighbours[cell]( axis, side );

                    if( neighbour != NoCell && levels[neighbour] == levels[cell] )
                    {
                        self( self, visited, neighbour, shape, newIndices );
                    }
                }
            }
        }
    };

    auto nint = static_cast<std::int64_t>( leafMask.size( ) );

    [[maybe_unused]] 
    auto chunksize = parallel::clampChunksize( leafMask.size( ), 128 );

    // Transfer sizes of leaves to their (potentially non-leaf) neighbours
    #pragma omp parallel for schedule(dynamic, chunksize)
    for( std::int64_t iCellInt = 0; iCellInt < nint; ++iCellInt )
    {
        auto iCell = static_cast<CellIndex>( iCellInt );

        VisitedArray visited( false );
        
        gatherShape( gatherShape, visited, iCell, shapes[iCell], array::makeSizes<D>( 1 ) );
    }

    return shapes;
}

/* Allocate linearized tensor product masks. For this we first need *
 * to computed the maximum sizes needed after also activating shape *
 * functions in neighbouring elements.                              */
template<size_t D>
auto allocateTensorProductMasks( const NCubeNeighboursVector<D>& neighbours,
                                 const std::vector<bool>& leafMask,
                                 const RefinementLevelVector& levels,
                                 const PolynomialDegreesVector<D>& degrees )
{
    auto shapes = gatherTensorProductMaskShapes( neighbours, leafMask, levels, degrees );

    // Now allocate these and initialize data
    LinearizedTensorProductMasks<D> masks;
    
    masks.second.resize( levels.size( ) );

    auto sizeint = static_cast<std::int64_t>( levels.size( ) );

    #pragma omp parallel for schedule(static)
    for( std::int64_t ii = 0; ii < sizeint; ++ii )
    {
        auto iCell = static_cast<size_t>( ii );
        auto strides = nd::stridesWithType<size_t>( shapes[iCell] );
        auto size = array::product( array::convert<size_t>( shapes[iCell] ) );

        masks.second[iCell] = { size, shapes[iCell], strides };
    }

    auto offset = size_t { 0 };

    for( size_t iCell = 0; iCell < levels.size( ); ++iCell )
    {
        std::get<0>( masks.second[iCell] ) += offset;

        std::swap( std::get<0>( masks.second[iCell] ), offset );
    }

    masks.first.resize( offset, 0 );

    return masks;
}

// Compare index tuple with size tuple
template<size_t D> 
bool inShape( MaskIndexType<D> ijk, MaskIndexType<D> shape )
{
    for( size_t axis = 0; axis < D; ++axis )
    {
        if( ijk[axis] >= shape[axis] )
        {
            return false;
        }
    }

    return true;
}

// Access element in linearized tensor product masks
template<size_t D>
auto& access( LinearizedTensorProductMasks<D>& masks,
              size_t index, MaskIndexType<D> ijk )
{
    auto [begin, shape, strides] = masks.second[index];

    return masks.first[begin + nd::linearIndex( strides, ijk ) ];
}

// Call initial mask provider for each cell and write result into linearized masks
template<size_t D>
void activateLeafMasks( const std::vector<bool>& leafMask,
                        const PolynomialDegreesVector<D>& degrees,
                        const InitialMaskProvider<D>& initialMaskProvider,
                        LinearizedTensorProductMasks<D>& masks )
{
    auto indexMap = algorithm::backwardIndexMap<CellIndex>( leafMask );
    auto sizeint = static_cast<std::int64_t>( leafMask.size( ) );

    #pragma omp parallel 
    {
        BooleanMask<D> mask;

        #pragma omp for schedule(static)
        for( std::int64_t iCellInt = 0; iCellInt < sizeint; ++iCellInt )
        {
            auto iCell = static_cast<size_t>( iCellInt );

            if( auto leafIndex = indexMap[iCell]; leafIndex != NoCell )
            {
                initialMaskProvider( mask, degrees[leafIndex] );

                auto degree = array::convert<PolynomialDegree>( degrees[leafIndex] );
                auto shape = array::add<PolynomialDegree>( degree, 1 );

                nd::executeWithIndex( shape, [&]( MaskIndexType<D> ijk, size_t index )
                { 
                    access( masks, iCell, ijk ) = mask[index];
                } );
            }
        }
    }
}

template<size_t D, typename Operation>
void booleanOperationOnInterfaces( LinearizedTensorProductMasks<D>& masks,
                                   const NCubeNeighboursVector<D>& neighbours,
                                   const RefinementLevelVector& levels,
                                   Operation operation )
{
    [[maybe_unused]]
    auto chunksize = parallel::clampChunksize( levels.size( ), 128 );

    for( size_t axis = 0; axis < D; ++axis )
    {
        #pragma omp parallel for schedule(dynamic, chunksize)
        for( std::int64_t cellInt = 0; cellInt < static_cast<std::int64_t>( levels.size( ) ); ++cellInt )
        {
            auto cell = static_cast<size_t>( cellInt );

            CellIndex neighbour = neighbours[cell]( axis, 0 );

            // If cell interface (and not boundary)
            if( neighbour != NoCell && levels[cell] == levels[neighbour] )
            {
                size_t begin1, begin2;
                MaskIndexType<D> shape1, shape2;
                std::array<size_t, D> strides1, strides2;

                std::tie( begin1, shape1, strides1 ) = masks.second[cell];
                std::tie( begin2, shape2, strides2 ) = masks.second[neighbour];

                auto maxShape = array::maxArray( shape1, shape2 );
                auto interfaceShape = array::setEntry<PolynomialDegree>( maxShape, axis, 1 );

                nd::execute( interfaceShape, [&]( MaskIndexType<D> ijk1 )
                { 
                    auto ijk2 = ijk1;

                    ijk2[axis] = 1;

                    bool inShape1 = inShape( ijk1, shape1 );
                    bool inShape2 = inShape( ijk2, shape2 );

                    size_t offset1 = begin1, offset2 = begin2;
                    bool value1 = false, value2 = false;

                    if( inShape1 )
                    {
                        offset1 += nd::linearIndex( strides1, ijk1 );

                        value1 = masks.first[offset1];
                    }

                    if( inShape2 )
                    {
                        offset2 += nd::linearIndex( strides2, ijk2 );

                        value2 = masks.first[offset2];
                    }

                    bool result = operation( value1, value2 );
                    
                    if( value1 != result && inShape1 )
                    {
                        masks.first[offset1] = result;
                    }

                    if( value2 != result && inShape2 )
                    {
                        masks.first[offset2] = result;
                    }
                } );

            } // if internal boundary
        } // for cell
    } // for axis
}

template<size_t D>
void deactivateOnInternalBoundaries( LinearizedTensorProductMasks<D>& masks,
                                     const RefinementLevelVector& levels,
                                     const NCubeNeighboursVector<D>& neighbours )
{
    auto nint = static_cast<std::int64_t>( levels.size( ) );

    #pragma omp parallel for schedule(static)
    for( std::int64_t ii = 0; ii < nint; ++ii )
    {
        auto cell = static_cast<CellIndex>( ii );

        for( size_t axis = 0; axis < D; ++axis )
        {
            for( size_t side = 0; side < 2; ++side )
            {
                // No need to do anything if mask is too small
                if( auto shape = std::get<1>( masks.second[cell] ); shape[axis] > side )
                {
                    CellIndex neighbour = neighbours[cell]( axis, side );

                    // If internal boundary
                    if( neighbour != NoCell && levels[cell] != levels[neighbour] )
                    {
                        shape[axis] = 1;

                        nd::execute( shape, [&]( MaskIndexType<D> ijk )
                        {
                            ijk[axis] = static_cast<PolynomialDegree>( side );

                            access( masks, cell, ijk ) = false;
                        } );
                    }
                } 

            } // for side
        } // for axis
    } // for cellIndex
}

template<size_t D>
LinearizedTensorProductIndices<D> convertToTensorProductIndices( const LinearizedTensorProductMasks<D>& masks )
{
    LinearizedTensorProductIndices<D> indices;

    auto ncells = masks.second.size( );

    indices.second.resize( ncells + 1 );
    indices.second[0] = 0;

    std::uint64_t sum = 0;

    #pragma omp parallel for schedule(static) reduction(+: sum)
    for( std::int64_t iCellInt = 0; iCellInt < static_cast<std::int64_t>( ncells ); ++iCellInt )
    {
        auto iCell = static_cast<size_t>( iCellInt );

        auto [begin, shape, strides] = masks.second[iCell];

        auto size = array::product( array::convert<size_t>( shape ) );
        
        DofIndex active = 0;

        for( auto iEntry = begin; iEntry < begin + size; ++iEntry )
        {
            active += static_cast<size_t>( masks.first[iEntry] );
        }

        indices.second[iCell + 1] = active;
        sum += active;
    }

    MLHP_CHECK( sum < NoDof, "More (local) dofs than representable by DofIndexType." );

    std::partial_sum( indices.second.begin( ), indices.second.end( ), indices.second.begin( ) );

    indices.first.resize( indices.second.back( ) );

    #pragma omp parallel for schedule(static)
    for( std::int64_t iCellInt = 0; iCellInt < static_cast<std::int64_t>( ncells ); ++iCellInt )
    {
        auto iCell = static_cast<CellIndex>( iCellInt );

        auto begin = std::get<0>( masks.second[iCell] );
        auto shape = std::get<1>( masks.second[iCell] );

        size_t activeIndex = indices.second[iCell];

        nd::executeWithIndex( shape, [&]( MaskIndexType<D> ijk, size_t linearIndex )
        { 
            if( masks.first[begin + linearIndex] )
            {
                indices.first[activeIndex++] = array::convert<PolynomialDegree>( ijk );
            }
        } );
    }

    return indices;
}

} // namespace 

template<size_t D>
LinearizedTensorProductIndices<D> constructTensorProductIndices( const NCubeNeighboursVector<D>& neighbours,
                                                                 const std::vector<bool>& leafMask,
                                                                 const RefinementLevelVector& levels,
                                                                 const PolynomialDegreesVector<D>& polynomialDegrees,
                                                                 const InitialMaskProvider<D>& initialMaskProvider )
{
    auto masks = allocateTensorProductMasks( neighbours, leafMask, levels, polynomialDegrees );
    
    // 1. Activate shape functions of all leaf elements according to initial mask provider
    activateLeafMasks( leafMask, polynomialDegrees, initialMaskProvider, masks );

    // 2. Recover compatible basis by or operation on interfaces and communicate D times
    for( size_t iteration = 0; iteration < D; ++iteration )
    {
        booleanOperationOnInterfaces( masks, neighbours, levels, std::logical_or<bool>{ } );
    }

    // 3. Enforce zero-dirichlet on internal interfaces
    deactivateOnInternalBoundaries( masks, levels, neighbours );

    // 4. Recover compatible basis by or operation on interfaces and communicate D times
    for( size_t iteration = 0; iteration + 1 < D; ++iteration )
    {
        booleanOperationOnInterfaces( masks, neighbours, levels, std::logical_and<bool>{ } );
    }

    return convertToTensorProductIndices( masks );
}

template<size_t D>
DofIndexVector generateLocationMaps( const TensorProductIndicesVector<D>& entries,
                                     const DofIndexVector& indices,
                                     const NCubeNeighboursVector<D>& neighbours,
                                     const RefinementLevelVector& levels )
{
    MLHP_CHECK( static_cast<std::uint64_t>( entries.size( ) ) < static_cast<std::uint64_t>( NoDof ), 
                "Too many entries in tensor product to be represented by DofIndex data type." );

    DofIndexVector global( entries.size( ) );

    std::iota( global.begin( ), global.end( ), DofIndex { 0 } );

    [[maybe_unused]]
    auto chunksize = parallel::clampChunksize( levels.size( ), 128 );

    constexpr size_t side = 0;

    for( size_t iteration = 0; iteration < D; ++iteration )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            auto predicate1 = [=]( TensorProductIndices<D> ijk ){ return ijk[axis] == side; };
            auto predicate2 = [=]( TensorProductIndices<D> ijk ){ return ijk[axis] == 1 - side; };

            #pragma omp parallel for schedule( dynamic, chunksize )
            for( std::int64_t iCellInt = 0; iCellInt < static_cast<std::int64_t>( levels.size( ) ); ++iCellInt )
            {
                auto iCell = static_cast<size_t>( iCellInt );

                auto neighbour = neighbours[iCell]( axis, side );

                if( neighbour != NoCell && levels[neighbour] == levels[iCell] )
                {
                    auto begin1 = entries.begin( ) + utilities::ptrdiff( indices[iCell] );
                    auto begin2 = entries.begin( ) + utilities::ptrdiff( indices[neighbour] );

                    auto end1 = entries.begin( ) + utilities::ptrdiff( indices[iCell + 1] );
                    auto end2 = entries.begin( ) + utilities::ptrdiff( indices[neighbour + 1] );

                    auto result1 = std::find_if( begin1, end1, predicate1 );
                    auto result2 = std::find_if( begin2, end2, predicate2 );

                    while( result1 != end1 )
                    {
                        MLHP_CHECK_DBG( result2 != end2, "Incompatible shape functions." );

                        auto index1 = static_cast<size_t>( std::distance( entries.begin( ), result1 ) );
                        auto index2 = static_cast<size_t>( std::distance( entries.begin( ), result2 ) );
                        auto index = std::min( global[index1], global[index2] );

                        global[index1] = index;
                        global[index2] = index;

                        result1 = std::find_if( result1 + 1, end1, predicate1 );
                        result2 = std::find_if( result2 + 1, end2, predicate2 );
                    } 

                    MLHP_CHECK_DBG( result2 == end2, "Incompatible shape functions." );
                }
            } // for iCell
        } // for axis
    } // for iteration

    algorithm::removeMissingDofs( global );

    return global;
}

template<size_t D>
void initializeTensorSpaceMasks( BooleanMask<D>& mask, std::array<size_t, D> polynomialDegrees )
{
    MLHP_EXPECTS( array::minElement( polynomialDegrees ) > 0 );

    mask.resize( array::add<size_t>( polynomialDegrees, 1 ) );

    std::fill( mask.begin( ), mask.end( ), true );
}

template<size_t D>
void initializeTrunkSpaceMasks( BooleanMask<D>& mask, std::array<size_t, D> polynomialDegrees )
{
    MLHP_EXPECTS( array::minElement( polynomialDegrees ) > 0 );

    auto shape = array::add<size_t>( polynomialDegrees, 1 );
    auto maxShape = array::maxElement( shape );

    mask.resize( shape );

    // Activate when i + j + ... < max( p_0, p_1, ... )
    nd::executeWithIndex( shape, [&]( std::array<size_t, D> ijk, size_t index )
    { 
        mask[index] = array::sum( ijk ) < maxShape;
    } );

    // For each direction copy 0-slice in axis to 1-slice
    for( size_t axis = 0; axis < D; ++axis )
    {
        nd::execute( array::setEntry<size_t>( shape, axis, 1 ), [&]( std::array<size_t, D> ijk )
        { 
            mask[array::setEntry<size_t>( ijk, axis, 1 )] = mask[ijk];
        } );
    }
}

namespace 
{

template<size_t D> 
size_t findFlipAxis( TensorProductIndices<D> current,
                     TensorProductIndices<D> last )
{
    for( size_t axis = 0; axis + 1 < D; ++axis ) 
    {
        if( current[axis] > last[axis] )
        {
            return axis;
        }

        MLHP_CHECK_DBG( current[axis] == last[axis], "Tensor "
            "product indices not C-Style ordered." );
    }

    MLHP_CHECK_DBG( current[D - 1] > last[D - 1], "Duplicated entry "
        "or reverse order in tensor product indices." );

    return D - 1;
}

} // namespace  

template<size_t D>
TensorProductIndices<D> compressIndices( const TensorProductIndices<D>* begin,
                                         const TensorProductIndices<D>* end,
                                         std::vector<PolynomialDegree>& target )
{
    if( end <= begin )
    {
        return { };
    }

    auto shape = array::make<D>( PolynomialDegree { 1 } );

    target.reserve( target.size( ) + 2 * D );

    std::array<size_t, D> sizeIndices;
    std::array<PolynomialDegree, D> currentSizes;
    
    for( size_t axis = 0; axis < D; ++axis )
    {
        sizeIndices[axis] = target.size( );
        currentSizes[axis] = 1;

        target.emplace_back( );
        target.push_back( ( *begin )[axis] );
    }

    for( auto ijk = begin + 1; ijk < end; ++ijk )
    {
        auto flipAxis = findFlipAxis( *ijk, *( ijk - 1 ) );

        currentSizes[flipAxis] += 1;
        target.push_back( ijk->at( flipAxis ) );

        // Reset dimensions after flip axis
        for( size_t axis = flipAxis + 1; axis < D; ++axis )
        {
            target[sizeIndices[axis]] = currentSizes[axis];

            sizeIndices[axis] = target.size( );
            currentSizes[axis] = 1;

            target.emplace_back( );              
            target.push_back( ijk->at( axis ) ); 
        }

        shape = array::maxArray( shape, *ijk );
    }

    for( size_t axis = 0; axis < D; ++axis )
    {
        target[sizeIndices[axis]] = currentSizes[axis];
    }

    return shape;
}

namespace
{

template<size_t I, size_t D> 
void compressedTensorProductRecursive( const PolynomialDegree*& MLHP_RESTRICT active,
                                       const std::array<const double*, D>& bases1D,
                                       double*& MLHP_RESTRICT target, double N )
{
    auto basis1D = memory::assumeNoalias( bases1D[I] );
    auto nsegments = *( active++ );

    if constexpr( I + 1 == D )
    {
        for( size_t i = 0; i < nsegments; ++i )
        {
            target[i] = N * basis1D[active[i]];
        }

        active += nsegments;
        target += nsegments;
    }
    else
    {
        for( size_t i = 0; i < nsegments; ++i )
        {
            auto index = *( active++ );

            compressedTensorProductRecursive<I + 1>( active,
                bases1D, target, N * basis1D[index] );
        }
    }
}

} // namespace

template<size_t D>
void compressedTensorProduct( const PolynomialDegree* compressedIndices,
                              std::array<const double*, D> bases1D,
                              double scaling,
                              double* target )
{
    compressedTensorProductRecursive<0>( compressedIndices, bases1D, target, scaling );
}

#define MLHP_INSTANTIATE_DIM( D )                                                                                         \
    template MLHP_EXPORT                                                                                                  \
    DofIndexVector generateLocationMaps( const TensorProductIndicesVector<D>& entries,                                    \
                                         const DofIndexVector& indices,                                                   \
                                         const NCubeNeighboursVector<D>& neighbours,                                      \
                                         const RefinementLevelVector& levels );                                           \
                                                                                                                          \
    template MLHP_EXPORT                                                                                                  \
    LinearizedTensorProductIndices<D> constructTensorProductIndices( const NCubeNeighboursVector<D>& neighbours,          \
                                                                     const std::vector<bool>& leafMask,                   \
                                                                     const RefinementLevelVector& levels,                 \
                                                                     const PolynomialDegreesVector<D>& polynomialDegrees, \
                                                                     const InitialMaskProvider<D>& initialMaskProvider ); \
                                                                                                                          \
    template MLHP_EXPORT                                                                                                  \
    void initializeTensorSpaceMasks( BooleanMask<D>& mask,                                                                \
                                     std::array<size_t, D> polynomialDegrees );                                           \
                                                                                                                          \
    template MLHP_EXPORT                                                                                                  \
    void initializeTrunkSpaceMasks( BooleanMask<D>& mask,                                                                 \
                                    std::array<size_t, D> polynomialDegrees );                                            \
                                                                                                                          \
    template MLHP_EXPORT                                                                                                  \
    void compressedTensorProduct( const PolynomialDegree* compressedIndices,                                              \
                                  std::array<const double*, D> bases1D,                                                   \
                                  double scaling,                                                                         \
                                  double* target );                                                                       \
                                                                                                                          \
    template MLHP_EXPORT                                                                                                  \
    TensorProductIndices<D> compressIndices( const TensorProductIndices<D>* begin,                                        \
                                             const TensorProductIndices<D>* end,                                          \
                                             std::vector<PolynomialDegree>& target );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // mlhp
