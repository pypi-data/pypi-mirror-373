// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_REFINEMENT_HPP
#define MLHP_CORE_REFINEMENT_HPP

#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/alias.hpp"

namespace mlhp
{

template<size_t D> MLHP_EXPORT
RefinementFunction<D> refineTowardsDomainBoundary( const ImplicitFunction<D>& function,
                                                   size_t maxDepth,
                                                   size_t numberOfSeedPoints = 7 );

template<size_t D> MLHP_EXPORT
RefinementFunction<D> refineInsideDomain( const ImplicitFunction<D>& function,
                                          size_t maxDepth,
                                          size_t numberOfSeedPoints = 7 );

template<size_t D>
using LevelFunction = std::function<RefinementLevel( std::array<double, D> )>;

template<size_t D> MLHP_EXPORT
RefinementFunction<D> refineWithLevelFunction( const LevelFunction<D>& level,
                                               size_t numberOfSeedPoints = 5 );

template<size_t D> MLHP_EXPORT
RefinementFunction<D> refineUniformly( RefinementLevel level = 0 );

//! Pass vector of leaf indices for each refinement level
template<size_t D> MLHP_EXPORT
RefinementFunction<D> refineCellIndices( const std::vector<CellIndexVector>& indices );

template<size_t D, typename... RefinementFunctions > inline
RefinementFunction<D> refinementOr( const RefinementFunction<D>& function1,
                                    const RefinementFunctions&... functions )
{
    return [=]( const MeshMapping<D>& mapping, RefinementLevel level ) -> bool
    {
        return function1( mapping, level ) || ( functions( mapping, level ) || ... || false );
    };
}

template<size_t D, typename... RefinementFunctions > inline
RefinementFunction<D> refinementAnd( const RefinementFunction<D>& function1,
                                     const RefinementFunctions&... functions )
{
    return [=]( const MeshMapping<D>& mapping, RefinementLevel level ) -> bool
    {
        return function1( mapping, level ) && ( functions( mapping, level ) && ... && true );
    };
}

// -1 --> outside
//  0 --> cut
//  1 --> inside
template<size_t D> MLHP_EXPORT
int intersectionTest( const ImplicitFunction<D>& function,
                      const AbsMapping<D>& mapping,
                      size_t numberOfSeedPoints,
                      double scaleLocalCoordinates = 1.0 );

template<size_t D>
using PathInTime = std::function<std::array<double, D>( double )>;

template<size_t D> MLHP_EXPORT
RefinementFunction<D + 1> refineAroundPath( const PathInTime<D>& path, double radius, size_t refinementDepth );

} // mlhp

#endif // MLHP_CORE_REFINEMENT_HPP
