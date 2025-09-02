// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_ALGORITHM_HPP
#define MLHP_CORE_ALGORITHM_HPP

#include "mlhp/core/alias.hpp"
#include "mlhp/core/compilermacros.hpp"
#include "mlhp/core/coreexport.hpp"

#include <span>

namespace mlhp::algorithm
{

/* 
 * Index manipulation: Consider the indices 0 - 10 where [1, 4, 6, 7, 9] receive special
 * treatment (could be for example boundary dofs). Then we introduce:
 *
 * - forward index map (normal)   : [ 1,  4,  6,  7,  9 ]
 * - forward index map (inverse)  : [ 0,  2,  3,  5,  8,  10 ]
 
 * - index mask (normal)          : [ 0,  1,  0,  0,  1,  0,  1,  1,  0,  1,  0 ]
 * - index mask (inverse)         : [ 1,  0,  1,  1,  0,  1,  0,  0,  1,  0,  1 ]
 *
 * - backward index map (normal)  : [-1,  0, -1, -1,  1, -1,  2,  3, -1,  4, -1 ]
 * - backward index map (inverse) : [ 0, -1,  1,  2, -1,  3, -1, -1,  4, -1,  5 ]
 *
 * - split backward index map     : [ 0,  0,  1,  2,  1,  3,  2,  3,  4,  4,  5 ]
 *
 * Indices used here are not required to be sorted but will always be returned sorted.
 * So forwardIndexMap( indexMask( indices ) ) will sort in O(n), given that the range
 * of indices is small enough for the index mask to fit into memory.
 */

// Concepts for instantiated types to convert linker errors into nice compiler errors.
template <typename T>
concept InstantiatedInteger = std::is_same_v<T, unsigned long long int> ||
                              std::is_same_v<T, unsigned long int>      ||
                              std::is_same_v<T, unsigned int>           ||
                              std::is_same_v<T, unsigned short int>;

template <typename T>
concept InstantiatedBoolean = std::is_same_v<T, bool> ||
                              std::is_same_v<T, std::uint8_t>;


/*! Compute indices of true entries in mask (or false if invert).
 *
 *  Example (from top): mask = [0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
 *      invert = false   -->   [1, 4, 6, 7, 9]
 *      invert = true    -->   [0, 2, 3, 5, 8, 10]
 */
template<InstantiatedInteger Index, InstantiatedBoolean Boolean> MLHP_EXPORT
std::vector<Index> forwardIndexMap( const std::vector<Boolean>& mask, 
                                    bool invert = false );


/*! Compute mask with true entries given by indices. 
 *
 *  Example (from top): indices = [1, 4, 6, 7, 9],  size = 11,
 *      invert = false      -->   [0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0]
 *      invert = true       -->   [1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1]
 */
template<InstantiatedInteger Index, InstantiatedBoolean Boolean = bool> MLHP_EXPORT
std::vector<Boolean> indexMask( const std::vector<Index>& indices,
                                size_t size, bool invert = false );


/*! Map to full index range with either true index in mask or NoValue (-1) if not present.
 *
 *  Example (from top): mask = [ 0,  1,  0,  0,  1,  0,  1,  1,  0,  1,  0 ],
 *      invert = false   -->   [-1,  0, -1, -1,  1, -1,  2,  3, -1,  4, -1 ]
 *      invert = true    -->   [ 0, -1,  1,  2, -1,  3, -1, -1,  4, -1,  5 ]
 */
template<InstantiatedInteger Index, InstantiatedBoolean Boolean> MLHP_EXPORT
std::vector<Index> backwardIndexMap( const std::vector<Boolean>& mask,
                                     bool invert = false );

/*! Map to full index range with either index in indices or NoValue (-1) if not present.
 *
 *  Example (from top): indices = [ 1,  4,  6,  7,  9 ],  size = 11,
 *      invert = false      -->   [ 0,  0,  1,  2,  1,  3,  2,  3,  4,  4,  5 ]
 *      invert = true       -->   [ 0, -1,  1,  2, -1,  3, -1, -1,  4, -1,  5 ]
 */
template<InstantiatedInteger Index> MLHP_EXPORT
std::vector<Index> backwardIndexMap( const std::vector<Index>& indices,
                                     Index size, bool invert = false );


/*! Map to full index range with either index in indices or counting up values not in 
 *  indices. Basically a combination of normal and inverted backwardIndexMap, which is 
 *  useful together with the boolean mask to distinuish between both index sets.
 *
 *  Example (from top): indices = [1, 4, 6, 7, 9],  size = 11,
 *                          -->   [0, 0, 1, 2, 1, 3, 2, 3, 4, 4, 5]
 */
template<InstantiatedInteger Index, InstantiatedBoolean Boolean> MLHP_EXPORT
std::vector<Index> splitBackwardIndexMap( const std::vector<Boolean>& mask );

/*! Return map for fast index search, assuming they are unique.
 *  For example [4, 3, 6] --> [-1, -1, -1, 1, 0, -1, 2]
 */
template<InstantiatedInteger Index> MLHP_EXPORT
std::vector<Index> invertIndices( const std::vector<Index>& indices, 
                                  Index size = NoValue<Index> );

//! Like invertIndices, but return linearized vector of vectors allowing for multiple occurances
template<InstantiatedInteger Index> MLHP_EXPORT
LinearizedVectors<Index> invertRepeatedIndices( std::span<const Index> indices,
                                                Index size = NoValue<Index> );

//! Vector version of above
template<InstantiatedInteger Index>
LinearizedVectors<Index> invertRepeatedIndices( const std::vector<Index>& indices,
                                                Index size = NoValue<Index> )
{
    return invertRepeatedIndices<Index>( std::span { indices }, size );
}

//! Find indices in [0, indice.size()) that are not in the given index list
template<InstantiatedInteger Index> inline
std::vector<Index> complementaryIndices( const std::vector<Index>& indices,
                                         size_t size )
{
    return forwardIndexMap<Index>( indexMask( indices, size, true ) );
}

/*
 * Other algorithm type functions.
 */

MLHP_EXPORT MLHP_PURE
DofIndex computeNumberOfDofs( const DofIndexVector& locationMapData,
                              DofIndex ndof = NoDof );

MLHP_EXPORT
DofIndexVector removeMissingDofs( DofIndexVector& locationMapData );

using LocationMapsWithNewNDof = std::pair<LinearizedLocationMaps, DofIndex>;

MLHP_EXPORT
LocationMapsWithNewNDof removeDofs( const LinearizedLocationMaps& maps,
                                    const DofIndexVector& dofsToRemove,
                                    DofIndex ndof = NoDof );

//! Given, for examples, the dofs (entities) for each element (offsets), 
//! returns elements for each dof. Or given the vertices (entities) for
//! each cell, returns the cells connected to each vertex
template<InstantiatedInteger Index> MLHP_EXPORT
LinearizedVectors<Index> invertRelation( std::span<const size_t> offsets,
                                         std::span<const Index> entities,
                                         Index nentities = NoValue<Index> );

template<typename ValueType, std::integral IndexType> inline
void extract( const std::vector<ValueType>& values, 
              const std::vector<IndexType>& indices,
              std::vector<ValueType>& target )
{
    target.resize( std::max( target.size( ), indices.size( ) ) );

    for( size_t index = 0; index < indices.size( ); ++index )
    {
        MLHP_CHECK_DBG( indices[index] < values.size( ), "Index out of bounds." );

        target[index] = values[indices[index]];
    }
}

template<typename ValueType, std::integral IndexType> inline
auto extract( const std::vector<ValueType>& values,
              const std::vector<IndexType>& indices )
{
    std::vector<ValueType> target;

    extract( values, indices, target );

    return target;
}

template<typename ValueType, std::integral IndexType> inline
auto remove( const std::vector<ValueType>& values, 
             const std::vector<IndexType>& indices )
{
    return extract( values, complementaryIndices( indices, values.size( ) ) );
}

template<typename ValueType, std::integral IndexType> inline
void scatter( const std::vector<ValueType>& values,
              const std::vector<IndexType>& indices,
              std::vector<ValueType>& target,
              bool addValues = false )
{
    target.resize( std::max( target.size( ), indices.size( ) ) );
    
    MLHP_CHECK( values.size( ) == indices.size( ), "Inconsistent sizes." );

    if( addValues )
    {
        for( size_t i = 0; i < indices.size( ); ++i )
        {
            target[indices[i]] += values[i];
        }
    }
    else
    {
         for( size_t i = 0; i < indices.size( ); ++i )
        {
            target[indices[i]] = values[i];
        }
    }
}

template<typename ValueType, std::integral IndexType> inline
auto scatter( const std::vector<ValueType>& values,
              const std::vector<IndexType>& indices,
              bool addValues = false )
{
    std::vector<ValueType> target;

    scatter( values, indices, target, addValues );

    return target;
}

} // mlhp::algorithm

#endif // MLHP_CORE_ALGORITHM_HPP
