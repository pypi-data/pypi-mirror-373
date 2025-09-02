// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/algorithm.hpp"

#include <limits>
#include <numeric>

namespace mlhp
{
namespace algorithm
{

LocationMapsWithNewNDof removeDofs( const LinearizedLocationMaps& maps,
                                    const DofIndexVector& dofsToRemove,
                                    DofIndex ndof )
{
    const auto& indices = std::get<0>( maps );
    const auto& dofs = std::get<1>( maps );

    if( ndof == NoDof )
    {
        ndof = algorithm::computeNumberOfDofs( dofs );
    }

    auto mask = algorithm::indexMask( dofsToRemove, ndof );
    auto map = algorithm::backwardIndexMap<DofIndex>( mask, true );

    LinearizedLocationMaps reducedMaps;

    auto& reducedIndices = std::get<0>( reducedMaps );
    auto& reducedDofs = std::get<1>( reducedMaps );

    reducedIndices.resize( indices.size( ) );
    reducedIndices[0] = 0;
    
    #pragma omp parallel for schedule( dynamic, 38 )
    for( std::int64_t iInt = 0; iInt < static_cast<std::int64_t>( indices.size( ) ) - 1; ++iInt )
    {
        auto iElement = static_cast<size_t>( iInt );

        for( size_t iDof = indices[iElement]; iDof < indices[iElement + 1]; ++iDof )
        {
            reducedIndices[iElement + 1] += static_cast<DofIndex>( !mask[dofs[iDof]] );
        } 
    }

    std::partial_sum( reducedIndices.begin( ), reducedIndices.end( ), reducedIndices.begin( ) );

    reducedDofs.resize( reducedIndices.back( ) );

    #pragma omp parallel for schedule( dynamic, 38 )
    for( std::int64_t iInt = 0; iInt < static_cast<std::int64_t>( indices.size( ) ) - 1; ++iInt )
    {
        auto iElement = static_cast<size_t>( iInt );

        size_t offset = reducedIndices[iElement];

        for( size_t iDof = indices[iElement]; iDof < indices[iElement + 1]; ++iDof )
        {
            if( auto dof = dofs[iDof]; !mask[dof] )
            {
                reducedDofs[offset++] = map[dof];
            }
        } 
    }

    auto newNDof = ndof - std::accumulate( mask.begin( ), mask.end( ), DofIndex { 0 } );

    return { std::move( reducedMaps), newNDof };
}

MLHP_EXPORT MLHP_PURE
DofIndex computeNumberOfDofs( const DofIndexVector& locationMapData, DofIndex ndof )
{
    if( locationMapData.empty( ) )
    {
        return 0;
    }
    else if( ndof == NoDof )
    {
        ndof = *std::max_element( locationMapData.begin( ), locationMapData.end( ) );

        MLHP_CHECK( ndof++ != NoDof, "Invalid dof index" );
    }

    return ndof;
}

DofIndexVector removeMissingDofs( DofIndexVector& locationMapData )
{
    if( !locationMapData.empty( ) )
    {
        auto ndof = computeNumberOfDofs( locationMapData );
        auto nint0 = static_cast<std::int64_t>( locationMapData.size( ) );
        auto isactive = std::vector<bool>( ndof, false );
        auto map = std::vector<DofIndex>( ndof ); 
        auto index = DofIndex { 0 };

        for( auto entry : locationMapData )
        {
            isactive[entry] = true;
        }

        for( size_t i = 0; i < ndof; ++i )
        {
            map[i] = isactive[i] != 0 ? index++ : NoDof;
        }

        #pragma omp parallel for schedule(static)
        for( std::int64_t ii = 0; ii < nint0; ++ii )
        {
            auto idof = static_cast<size_t>( ii );

            locationMapData[idof] = map[locationMapData[idof]];
        }

        return map;
    }
    else
    {
        return { };
    }
}

template<InstantiatedInteger Index, InstantiatedBoolean Boolean>
std::vector<Index> forwardIndexMap( const std::vector<Boolean>& mask, bool invert )
{
    auto predicate = [=]( auto v ) noexcept { return static_cast<bool>( v ) != invert; };
    auto size = std::ranges::count_if( mask,  predicate );
    auto map = std::vector<Index>( static_cast<size_t>( size ) );
    auto mapIndex = size_t { 0 };

    for( Index i = 0; i < mask.size( ); ++i )
    {
        if( static_cast<bool>( mask[i] ) != invert )
        {
            map[mapIndex++] = i;
        }
    }

    return map;
}

template<InstantiatedInteger Index, InstantiatedBoolean Boolean>
std::vector<Boolean> indexMask( const std::vector<Index>& indices, size_t size, bool invert )
{
    std::vector<Boolean> mask( size, !invert ? 0 : 1 );

    for( size_t i = 0; i < indices.size( ); ++i )
    {
        mask[indices[i]] = !invert;
    }

    return mask;
}

template<InstantiatedInteger Index, InstantiatedBoolean Boolean>
std::vector<Index> backwardIndexMap( const std::vector<Boolean>& mask, bool invert )
{
    std::vector<Index> map( mask.size( ) );

    Index index = 0;

    for( Index i = 0; i < mask.size( ); ++i )
    {
        map[i] = static_cast<bool>( mask[i] ) != invert ? index++ : NoValue<Index>;
    }

    return map;
}

template<InstantiatedInteger Index>
std::vector<Index> backwardIndexMap( const std::vector<Index>& indices, Index size, bool invert )
{ 
    MLHP_CHECK_DBG( indices.empty( ) || ( size > *std::max_element( indices.begin( ), 
        indices.end( ) ) ), "Invalid target size in algorithm::backwardIndexMap" );

    std::vector<Index> result( size, NoValue<Index> );

    for( Index i = 0; i < indices.size( ); ++i )
    {
        result[indices[i]] = i;
    }

    if( invert )
    {
        Index count = 0;

        for( Index i = 0; i < size; ++i )
        {
            result[i] = result[i] == NoValue<Index> ? count++ : NoValue<Index>;
        }
    }

    return result;
}

template<InstantiatedInteger Index, InstantiatedBoolean Boolean> MLHP_EXPORT
std::vector<Index> splitBackwardIndexMap( const std::vector<Boolean>& mask )
{
    std::vector<Index> map( mask.size( ) );

    Index index1 = 0, index2 = 0;

    for( Index i = 0; i < mask.size( ); ++i )
    {
        map[i] = mask[i] ? index1++ : index2++;
    }

    return map;
}

template<InstantiatedInteger Index>
std::vector<Index> invertIndices( const std::vector<Index>& indices, Index size )
{
    auto it = std::max_element( indices.begin( ), indices.end( ) );

    if( size == NoValue<Index> )
    {
        size = indices.empty( ) ? 0 : *it + 1;
    }
    else
    {
        MLHP_CHECK( indices.empty( ) || *it < size, "Invalid size." );
    }

    auto inverted = std::vector<Index>( size, NoValue<Index> );

    for( size_t i = 0; i < indices.size( ); ++i )
    {
        inverted[static_cast<size_t>( indices[i] )] = static_cast<Index>( i );
    }

    return inverted;
}

template<InstantiatedInteger Index>
LinearizedVectors<Index> invertRepeatedIndices( std::span<const Index> indices, Index size )
{
    auto it = std::max_element( indices.begin( ), indices.end( ) );

    if( size == NoValue<Index> )
    {
        size = indices.empty( ) ? 0 : *it + 1;
    }
    else
    {
        MLHP_CHECK( indices.empty( ) || *it < size, "Invalid size." );
    }

    auto offsets = std::vector<size_t>( size + 1 );

    for( size_t i = 0; i < indices.size( ); ++i )
    {
        offsets[static_cast<size_t>( indices[i] ) + 1] += 1;
    }

    offsets[0] = 0;

    std::partial_sum( offsets.begin( ), offsets.end( ), offsets.begin( ) );

    auto inverted = std::vector<Index>( offsets.back( ) );
    auto count = std::vector<size_t>( size, 0 );
        
    for( size_t i = 0; i < indices.size( ); ++i )
    {
        auto offset = static_cast<size_t>( offsets[indices[i]] );

        inverted[offset + count[indices[i]]++] = static_cast<Index>( i );
    }

    return { std::move( offsets ), std::move( inverted ) };
}

template<InstantiatedInteger Index> MLHP_EXPORT
LinearizedVectors<Index> invertRelation( std::span<const size_t> offsets,
                                         std::span<const Index> entities,
                                         Index nentities )
{
    if( nentities == NoValue<Index> )
    {
        nentities = entities.empty( ) ? Index { 0 } : *std::max_element( 
            entities.begin( ), entities.end( ) ) + 1;
    }

    auto indices = utilities::allocateLinearizationIndices<size_t>( nentities );

    for( Index icell = 0; icell + 1 < static_cast<Index>( offsets.size( ) ); ++icell)
    {
        for( auto ientity = offsets[icell]; ientity < offsets[icell + 1]; ++ientity )
        {
            ++indices[entities[ientity] + 1];
        }
    }

    auto data = utilities::sumAndAllocateData<Index>( indices );
    auto currentIndex = indices;

    for( Index icell = 0; icell + 1 < static_cast<Index>( offsets.size( ) ); ++icell )
    {
        for( auto ientity = offsets[icell]; ientity < offsets[icell + 1]; ++ientity )
        {
            data[currentIndex[entities[ientity]]++] = icell;
        }
    }

    return std::make_pair( std::move( indices ), std::move( data ) );
}

#define MLHP_INSTANTIATE_INDEXMAP_ARGUMENT_TYPE( RETURN_TYPE, ARGUMENT_TYPE )                                    \
    template MLHP_EXPORT std::vector<RETURN_TYPE> forwardIndexMap ( const std::vector<ARGUMENT_TYPE>& mask,      \
                                                                    bool invert );                               \
    template MLHP_EXPORT std::vector<RETURN_TYPE> backwardIndexMap( const std::vector<ARGUMENT_TYPE>& mask,      \
                                                                    bool invert );                               \
    template MLHP_EXPORT std::vector<RETURN_TYPE> splitBackwardIndexMap( const std::vector<ARGUMENT_TYPE>& mask )

// X-macro list
#define MLHP_INSTANTIATE_ALGORITHM_INTEGER_TYPES                                                        \
    MLHP_INSTANTIATE_ALGORITHM_INTEGER_TYPE( unsigned long long int )                                   \
    MLHP_INSTANTIATE_ALGORITHM_INTEGER_TYPE( unsigned long int )                                        \
    MLHP_INSTANTIATE_ALGORITHM_INTEGER_TYPE( unsigned int )                                             \
    MLHP_INSTANTIATE_ALGORITHM_INTEGER_TYPE( unsigned short int )                                       \
                                                                                                        
// X-macro body                                                                                         
#define MLHP_INSTANTIATE_ALGORITHM_INTEGER_TYPE( INTEGER_TYPE )                                         \
    MLHP_INSTANTIATE_INDEXMAP_ARGUMENT_TYPE( INTEGER_TYPE, bool         );                              \
    MLHP_INSTANTIATE_INDEXMAP_ARGUMENT_TYPE( INTEGER_TYPE, std::uint8_t );                              \
                                                                                                        \
    template MLHP_EXPORT                                                                                \
    std::vector<INTEGER_TYPE> backwardIndexMap( const std::vector<INTEGER_TYPE>& indices,               \
                                             INTEGER_TYPE size, bool invert );                          \
                                                                                                        \
    template MLHP_EXPORT                                                                                \
    std::vector<bool> indexMask( const std::vector<INTEGER_TYPE>& indices,                              \
                                 size_t size, bool invert );                                            \
                                                                                                        \
    template MLHP_EXPORT                                                                                \
    std::vector<INTEGER_TYPE> invertIndices( const std::vector<INTEGER_TYPE>& indices,                  \
                                             INTEGER_TYPE size );                                       \
                                                                                                        \
    template MLHP_EXPORT                                                                                \
    LinearizedVectors<INTEGER_TYPE> invertRepeatedIndices( std::span<const INTEGER_TYPE> indices,       \
                                                           INTEGER_TYPE size = NoValue<INTEGER_TYPE> ); \
                                                                                                        \
    template MLHP_EXPORT                                                                                \
    LinearizedVectors<INTEGER_TYPE> invertRelation( std::span<const size_t> offsets,                    \
                                                    std::span<const INTEGER_TYPE> entities,             \
                                                    INTEGER_TYPE nentities );

MLHP_INSTANTIATE_ALGORITHM_INTEGER_TYPES
#undef MLHP_INSTANTIATE_INDEXMAP

} // algorithm
} // mlhp
