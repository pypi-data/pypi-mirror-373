// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/refinement.hpp"
#include "mlhp/core/mapping.hpp"
#include "mlhp/core/ndarray.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/algorithm.hpp"

namespace mlhp
{

template<size_t D>
int intersectionTest( const ImplicitFunction<D>& function,
                      const AbsMapping<D>& mapping,
                      size_t numberOfSeedPoints,
                      double scaleLocalCoordinates )
{
    auto pointsPerDirection = array::make<D>( numberOfSeedPoints );
    auto totalNumberOfPoints = utilities::integerPow( numberOfSeedPoints, D );

    auto rstGenerator = spatial::makeRstGenerator( pointsPerDirection, scaleLocalCoordinates );
    auto count = size_t { 0 };

    nd::execute( pointsPerDirection, [&]( std::array<size_t, D> ijk )
    {
        auto result = function( mapping( rstGenerator( ijk ) ) );

        count += static_cast<size_t>( result );
    } );

    return count == 0 ? -1 : ( count == totalNumberOfPoints ? 1 : 0 );
}

template<size_t D, typename Operation>
RefinementFunction<D> refinementBasedOnImplicitFunction( const ImplicitFunction<D>& function,
                                                         size_t maxDepth,
                                                         size_t numberOfSeedPoints,
                                                         Operation operation )
{
    return [=]( const MeshMapping<D>& mapping, RefinementLevel level )
    {
        if( level < maxDepth )
        {
            return operation( intersectionTest( function, mapping, numberOfSeedPoints ) );
        }
        else
        {
            return false;
        }
    };
}

template<size_t D>
RefinementFunction<D> refineTowardsDomainBoundary( const ImplicitFunction<D>& function,
                                                   size_t maxDepth,
                                                   size_t numberOfSeedPoints )
{
    return refinementBasedOnImplicitFunction( function, maxDepth, numberOfSeedPoints, []( int result ){ return result == 0; } );
}

template<size_t D>
RefinementFunction<D> refineInsideDomain( const ImplicitFunction<D>& function,
                                          size_t maxDepth,
                                          size_t numberOfSeedPoints )
{
    return refinementBasedOnImplicitFunction( function, maxDepth, numberOfSeedPoints, []( int result ){ return result >= 0; } );
}

template<size_t D>
RefinementFunction<D> refineWithLevelFunction( const LevelFunction<D>& level,
                                               size_t numberOfSeedPoints )
{
    auto npoints = array::make<D>( numberOfSeedPoints );
    auto rstGenerator = spatial::makeRstGenerator( npoints );

    return [=]( const MeshMapping<D>& mapping, RefinementLevel cellLevel )
    {
        bool refine = false;

        nd::execute( npoints, [&]( std::array<size_t, D> ijk )
        {
            refine |= level( mapping( rstGenerator( ijk ) ) ) > cellLevel;
        } );

        return refine;
    };
}

template<size_t D>
RefinementFunction<D> refineUniformly( RefinementLevel level )
{
    return [=]( auto&&, RefinementLevel cellLevel ) noexcept
    {
        return cellLevel < level;
    };
}

template<size_t D> 
RefinementFunction<D> refineCellIndices( const std::vector<CellIndexVector>& indices )
{
    auto masks = std::vector<std::vector<bool>> { };

    for( size_t ilevel = 0; ilevel < indices.size( ); ++ilevel )
    { 
        auto size = indices[ilevel].empty( ) ? CellIndex { 0 } : CellIndex { 1 } + 
            *std::max_element( indices[ilevel].begin( ), indices[ilevel].end( ) );

        masks.push_back( algorithm::indexMask( indices[ilevel], static_cast<CellIndex>( size ) ) );
    }

    return [=]( const MeshMapping<D>& mapping, RefinementLevel cellLevel )
    {
        return masks.size( ) > cellLevel                &&
               masks[cellLevel].size( ) > mapping.icell && 
               masks[cellLevel][mapping.icell];
    };
}

template<size_t D>
RefinementFunction<D + 1> refineAroundPath( const PathInTime<D>& path, double radius, size_t refinementDepth )
{
    std::function implicitFunction = [=]( std::array<double, D + 1> xyt )
    {
        auto dx = array::subtract( array::slice( xyt, D ), path( xyt[D] ) );

        return array::sum( array::multiply( dx, dx ) ) < radius * radius;
    };

    return refineInsideDomain( implicitFunction, refinementDepth );
}

#define MLHP_INSTANTIATE_DIM( D )                                                                        \
                                                                                                         \
    template MLHP_EXPORT                                                                                 \
    RefinementFunction<D> refineTowardsDomainBoundary( const ImplicitFunction<D>& function,              \
                                                       size_t maxDepth,                                  \
                                                       size_t numberOfSeedPoints );                      \
    template MLHP_EXPORT                                                                                 \
    RefinementFunction<D> refineInsideDomain( const ImplicitFunction<D>& function,                       \
                                              size_t maxDepth,                                           \
                                              size_t numberOfSeedPoints );                               \
    template MLHP_EXPORT                                                                                 \
    RefinementFunction<D> refineWithLevelFunction( const LevelFunction<D>& level,                        \
                                                   size_t numberOfSeesPoints );                          \
                                                                                                         \
    template MLHP_EXPORT                                                                                 \
    RefinementFunction<D> refineUniformly( RefinementLevel level );                                      \
                                                                                                         \
    template MLHP_EXPORT                                                                                 \
    int intersectionTest( const ImplicitFunction<D>& function,                                           \
                          const AbsMapping<D>& cell,                                                     \
                          size_t numberOfSeedPoints,                                                     \
                          double scaleLocalCoordinates );                                                \
                                                                                                         \
    template MLHP_EXPORT                                                                                 \
    RefinementFunction<D> refineCellIndices( const std::vector<CellIndexVector>& indices );              \
                                                                                                         \
    template MLHP_EXPORT                                                                                 \
    RefinementFunction<D + 1> refineAroundPath( const PathInTime<D>& path,                               \
                                                double radius,                                           \
                                                size_t refinementDepth );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // mlhp

