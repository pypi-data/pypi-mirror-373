// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_SPATIAL_IMPL_HPP
#define MLHP_CORE_SPATIAL_IMPL_HPP

#include <numbers>
#include "mlhp/core/dense.hpp"

namespace mlhp::spatial
{

template<size_t G, size_t I, size_t L> inline
JacobianMatrix<G, L> concatenateJacobians( const JacobianMatrix<I, L>& inner,
                                           const JacobianMatrix<G, I>& outer )
{
    auto target = JacobianMatrix<G, L> { };

    linalg::mmproduct( outer.data( ), inner.data( ), target.data( ), G, I, L );
    
    return target;
}

template<size_t G, size_t L> inline
double computeDeterminant( const JacobianMatrix<G, L>& matrix )
{
    auto det = []( auto&& squareMatrix )
    {
        std::array<size_t, L> permutation { };

        return linalg::det( squareMatrix, permutation );
    };

    if constexpr( L == 0 )
    {
        return 1.0;
    }
    else if constexpr( G == L )
    {
        if( isDiagonal<G>( matrix ) )
        {
            auto detJ = 1.0;

            for( size_t axis = 0; axis < G; ++axis )
            {
                detJ *= matrix[axis * G + axis];
            }

            return detJ;
        }
        else
        {
            return det( JacobianMatrix<G, L> { matrix } );
        }
    }
    else
    {
        JacobianMatrix<L, L> product { };

        // Compute J^T * J
        for( size_t i = 0; i < L; ++i )
        {
            for( size_t j = 0; j < L; ++j )
            {
                for( size_t k = 0; k < G; ++k )
                {
                    product[i * L + j] += matrix[k * L + i] * matrix[k * L + j];
                }
            }
        }

        return std::sqrt( det( std::move( product ) ) );
    }
}

template<size_t D> inline
bool isDiagonal( const JacobianMatrix<D, D>& matrix, double eps )
{
    for( size_t i = 0; i < D; ++i )
    {
        for( size_t j = 0; j < D; ++j )
        {
            if( i != j && std::abs( matrix[i * D + j] ) > eps )
            {
                return false;
            }
        }
    }

    return true;
}

template<size_t D, typename... Args> inline
auto constantFunction( double value )
{
    return std::function( [=]( std::array<double, D>, Args... ) noexcept
    {
        return value;
    } );
}

template<size_t I, size_t O> inline
auto constantFunction( std::array<double, O> value )
{
    return VectorFunction<I, O>( [=]( std::array<double, I>, std::span<double, O> out ) noexcept
    {
        std::copy( value.begin( ), value.end( ), out.begin( ) );
    } );
}

template<size_t I> inline
auto constantFunction( std::vector<double> value )
{
    return VectorFunction<I>( value.size( ), [=]( std::array<double, I>, std::span<double> out )
    {
        MLHP_CHECK( out.size( ) == value.size( ), "Inconsistent number of components." );

        std::copy( value.begin( ), value.end( ), out.begin( ) );
    } );
}

template<size_t D, typename ReturnType, typename... Args> inline
auto slice( const std::function<ReturnType(std::array<double, D>, Args...)>& function, size_t axis, double value )
{
    return std::function { [=]( std::array<double, D - 1> xy, Args&&... args )
    {
        return function( array::insert( xy, axis, value ), args... );
    } };
}

template<size_t L, size_t G> inline
auto slice( const VectorFunction<L, G>& function, size_t axis, double value )
{
    return VectorFunction<L - 1, G> { [=]( std::array<double, L - 1> xy, std::span<double, G> out )
    {
        return function( array::insert( xy, axis, value ), out );
    } };
}

template<size_t D, typename ReturnType, typename... Args> inline
auto sliceLast( const std::function<ReturnType( std::array<double, D>, Args...)>& function, double value )
{
    return slice( function, D - 1, value );
}

template<size_t L, size_t G> inline
auto sliceLast( const VectorFunction<L, G>& function, double value )
{
    return slice( function, L - 1, value );
}

template<size_t D> inline
auto peelLast( const ScalarFunction<D>& function )
{
    return [=]( std::array<double, D - 1> xy, double t )
    {
        return function( array::insert( xy, D - 1, t ) );
    };
}

template<size_t I, size_t O> requires ( O != std::dynamic_extent ) inline
ScalarFunction<I> extractComponent( const VectorFunction<I, O>& function, size_t icomponent )
{
    MLHP_CHECK( icomponent < O, "Invalid component index." );

    return [=]( std::array<double, I> xyz )
    { 
        return function( xyz )[icomponent];
    };
}

template<size_t N, size_t D> inline
auto expandDimension( const ScalarFunction<D>& function,
                      std::array<size_t, N> positions )
{
    auto other = std::array<size_t, D> { };
    auto index = size_t { 0 };

    for( size_t axis = 0; axis < D + N; ++axis )
    {
        if( std::find( positions.begin( ), positions.end( ), axis ) == positions.end( ) )
        {
            other[index++] = axis;
        }
    }

    MLHP_CHECK( index == D, "Double entry in positions." );

    return [=]( std::array<double, D + N> xyz )
    {
        std::array<double, D> xy { };

        for( size_t axis = 0; axis < D; ++axis )
        {
            xy[axis] = xyz[other[axis]];
        }

        return function( xy );
    };
}

//! Adds one dimension
template<size_t D> inline
auto expandDimension( const ScalarFunction<D>& function,
                      size_t index )
{
    return expandDimension( function, std::array { index } );
}

template<size_t D> inline
auto centerNormalizedGaussBell( std::array<double, D> center,
                                double sigma,
                                double scaling )
{
    double factor = 1.0 / ( 2.0 * sigma * sigma );

    return [=]( std::array<double, D> xyz )
    {
        return scaling * std::exp( -factor * distanceSquared( xyz, center ) );
    };
}

template<size_t D> inline
auto integralNormalizedGaussBell( std::array<double, D> center,
                                  double sigma,
                                  double scaling )
{
    double oneOverIntegral = std::pow( std::numbers::inv_sqrtpi / ( std::numbers::sqrt2 * sigma ), D );

    return centerNormalizedGaussBell( center, sigma, scaling * oneOverIntegral );
}

template<size_t D> inline
auto revolveAroundPath( const ScalarFunction<D>& function,
                        const ParameterFunction<D>& path,
                        const RealFunction& scaling )
{
    return [=]( std::array<double, D + 1> xyt )
    {
        return scaling( xyt[D] ) * function( array::slice( xyt, D ) - path( xyt[D] ) );
    };
}

template<size_t D, typename T> inline
ScalarFunction<D> voxelFunction( const std::vector<T>& data,
                                 std::array<size_t, D> nvoxels,
                                 std::array<double, D> lengths,
                                 std::array<double, D> origin,
                                 std::optional<T> outside )
{
    return voxelFunction<D, T>( utilities::copyShared( data ), nvoxels, lengths, origin, outside );
}

namespace detail
{

template<size_t D> inline
auto prepareGridIncrements( std::array<size_t, D> npoints,
                            std::array<double, D> lengths,
                            std::array<double, D> origin  )
{
    auto dx = std::array<double, D> { };

    for( size_t axis = 0; axis < D; ++axis )
    {
        if( npoints[axis] > 1 )
        {
            dx[axis] = lengths[axis] / ( npoints[axis] - 1.0 );
        }
        else
        {
            MLHP_CHECK( npoints[axis] != 0, "Need at least one point" );

            origin[axis] += lengths[axis] / 2.0;
        }
    }

    return std::pair { origin, dx };
}

} // detail

template<size_t D> inline
auto makeGridPointGenerator( std::array<size_t, D> npoints,
                             std::array<double, D> lengths,
                             std::array<double, D> origin )
{
    auto data = detail::prepareGridIncrements( npoints, lengths, origin );

    return [=]( std::array<size_t, D> ijk )
    {
        return std::get<0>( data ) + std::get<1>( data ) * array::convert<double>( ijk );
    };
}

template<size_t D> inline
auto makeRstGenerator( std::array<size_t, D> npoints, double scaling )
{
    auto lengths = array::make<D>( 2.0 * scaling );
    auto origin = array::make<D>( -scaling );

    return makeGridPointGenerator( npoints, lengths, origin );
}

template<size_t D>
constexpr auto dot( std::array<double, D> v1, std::array<double, D> v2 )
{
    double value = 0.0;

    for( size_t axis = 0; axis < D; ++axis )
    {
        value += v1[axis] * v2[axis];
    }

    return value;
}

template<typename T1, size_t D1, typename T2, size_t D2>
inline auto dot( std::span<T1, D1> v1, std::span<T2, D2> v2 )
{
    MLHP_CHECK_DBG( v1.size( ) == v2.size( ) && !v1.empty( ), "Inconsistent sizes" );
    
    auto value = v1[0] * v2[0];

    for( size_t axis = 1; axis < v1.size( ); ++axis )
    {
        value += static_cast<double>( v1[axis] ) * static_cast<double>( v2[axis] );
    }

    return value;
}

template<size_t N> inline
auto norm( const std::array<double, N>& arr )
{
    return std::sqrt( normSquared( arr ) );
}

template<size_t D> inline
auto normalize( std::array<double, D> v )
{
    return array::divide( v, norm( v ) );
}

template<size_t D> inline
auto normalizeChecked( std::array<double, D> v,
                       std::array<double, D> zero,
                       double tolerance )
{
    auto norm2 = spatial::normSquared( v );

    if( norm2 <= tolerance )
    {
        return zero;
    }

    return v / std::sqrt( norm2 );
}

template<size_t N> inline
auto interpolate( std::array<double, N> v1,
                  std::array<double, N> v2,
                  double t )
{
    auto result = std::array<double, N> { };

    for( size_t axis = 0; axis < N; ++axis )
    {
        result[axis] = v1[axis] + t * ( v2[axis] - v1[axis] );
    }

    return result;
}

template<size_t N> inline
auto distance( const std::array<double, N>& arr1,
               const std::array<double, N>& arr2 )
{
    return norm( array::subtract( arr1, arr2 ) );
}

template<size_t D> inline
auto invert( std::array<double, D> v )
{
    constexpr auto inf = 0.1 * std::numeric_limits<double>::max( );
    auto inv = std::array<double, D> { };

    for( size_t axis = 0; axis < D; ++axis )
    {
        inv[axis] = v[axis] ? 1.0 / v[axis] : inf;
    }

    return inv;
}

template<size_t N>
constexpr auto normSquared( const std::array<double, N>& arr )
{
    return array::sum( array::multiply( arr, arr ) );
}

template<size_t N>
constexpr auto distanceSquared( const std::array<double, N>& arr1,
                                const std::array<double, N>& arr2 )
{
    return normSquared( array::subtract( arr1, arr2 ) );
}

template<typename T1, size_t D1, typename T2, size_t D2>
inline double projectionFactor( std::span<T1, D1> u,
                                std::span<T2, D2> v )
{
    auto dot = static_cast<double>( spatial::dot( u, v ) );
    auto norm = static_cast<double>( spatial::dot( u, u ) );
    auto eps = 10 * std::numeric_limits<double>::epsilon( ) * std::abs( dot );

    return std::abs( norm ) > eps ? dot / norm : 0.0;
}

template<size_t D>
inline double projectionFactor( std::array<double, D> u,
                                std::array<double, D> v )
{
    return projectionFactor( utilities::cspan( u ), utilities::cspan( v ) );
}

template<size_t D>
inline std::array<double, D> orthogonalize( std::array<double, D> u,
                                            std::array<double, D> v )
{
    auto result = std::array<double, D> { };

    orthogonalize( utilities::cspan( u ), utilities::cspan( v ), utilities::span( result ) );

    return result;
}

template<typename T1, size_t D1, typename T2, size_t D2, size_t D3>
inline void orthogonalize( std::span<T1, D1> u,
                           std::span<T2, D2> v,
                           std::span<double, D3> target )
{
    MLHP_CHECK_DBG( target.size( ) == u.size( ), "Inconsistent sizes." );

    auto factor = projectionFactor( u, v );

    for( size_t i = 0; i < u.size( ); ++i )
    {
        target[i] = v[i] - factor * u[i];
    }
}

constexpr 
std::array<double, 3> cross( std::array<double, 3> v1,
                             std::array<double, 3> v2 )
{
    return std::array<double, 3>
    {
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    };
}

constexpr 
double cross( std::array<double, 2> v1,
              std::array<double, 2> v2 )
{
    return v1[0] * v2[1] - v1[1] * v2[0];
}

template<size_t N> 
constexpr auto standardBasisVector( size_t axis )
{
    return array::setEntry<double, N>( { }, axis, 1.0 );
}

// Returns { point, coordinate }
template<size_t D> 
constexpr auto projectOntoLine( std::array<double, D> line0,
                                std::array<double, D> line1,
                                std::array<double, D> point )
{
    auto ap = array::subtract( point, line0 );
    auto ab = array::subtract( line1, line0 );

    double r = dot( ap, ab ) / dot( ab, ab );

    return std::make_tuple( line0 + ab * r, r );
}

template<size_t D>
constexpr auto closestPointOnSegment( std::array<double, D> line0,
                                      std::array<double, D> line1,
                                      std::array<double, D> point )
{
    auto ap = point - line0;
    auto ab = line1 - line0;

    auto d0 = dot( ap, ab );
    auto d1 = dot( ab, ab );

    // t < 0.0
    if( ( d0 < 0.0 ) != ( d1 < 0.0 ) )
    {
        return std::make_tuple( line0, 0.0 );
    }
    else if( std::abs( d0 ) > std::abs( d1 ) )
    {
        return std::make_tuple( line1, 1.0 );
    }

    double r = d0 / d1;

    return std::make_tuple( line0 + ab * r, r );
}

template<size_t D>
constexpr auto triangleCentroid( std::array<double, D> vertex0,
                                 std::array<double, D> vertex1,
                                 std::array<double, D> vertex2 )
{
    auto result = std::array<double, D> { };

    for( size_t axis = 0; axis < D; ++axis )
    {
        result[axis] = ( vertex0[axis] + vertex1[axis] + vertex2[axis] ) / 3.0;
    }

    return result;
}

template<size_t D> inline
auto triangleCross( std::array<double, D> vertex0,
                    std::array<double, D> vertex1,
                    std::array<double, D> vertex2 )
{
    return spatial::cross( vertex1 - vertex0, vertex2 - vertex0 );
}

template<size_t D> inline
auto triangleNormal( std::array<double, D> vertex0,
                     std::array<double, D> vertex1,
                     std::array<double, D> vertex2 )
{
    return spatial::normalize( triangleCross( vertex0, vertex1, vertex2 ) );
}

template<size_t D> inline
auto triangleArea( std::array<double, D> vertex0,
                   std::array<double, D> vertex1,
                   std::array<double, D> vertex2 )
{
    static_assert( D == 2 || D == 3, "Not implemented." );

    if constexpr( D == 2 )
    {
        return 0.5 * std::abs( spatial::triangleCross( vertex0, vertex1, vertex2 ) );
    }

    if constexpr( D == 3 )
    {
        return 0.5 * spatial::norm( spatial::triangleCross( vertex0, vertex1, vertex2 ) );
    }
}

template<size_t D> inline
auto triangleArea( std::span<const std::array<double, D>> vertices )
{
    MLHP_CHECK( vertices.size( ) == 3, "Invalid span size." );

    return triangleArea( vertices[0], vertices[1], vertices[2] );
}

inline
double tetrahedronVolume( const std::array<double, 3>& vertex0,
                          const std::array<double, 3>& vertex1,
                          const std::array<double, 3>& vertex2,
                          const std::array<double, 3>& vertex3 )
{
    auto BA = array::subtract( vertex1, vertex0 );
    auto CA = array::subtract( vertex2, vertex0 );
    auto DA = array::subtract( vertex3, vertex0 );

    return 1.0 / 6.0 * std::abs( spatial::dot( spatial::cross( BA, CA ), DA ) );
}

template<size_t D> inline
CoordinateSpan<D> clipTriangle( const std::array<double, D>& vertex0,
                                const std::array<double, D>& vertex1,
                                const std::array<double, D>& vertex2,
                                size_t axis, double position, bool side,
                                CoordinateSpan<D> targetPolygon )
{
    targetPolygon[0] = vertex0;
    targetPolygon[1] = vertex1;
    targetPolygon[2] = vertex2;
    
    return clipPolygon<D>( targetPolygon.subspan( 0, 3 ), 
        targetPolygon, axis, position, side );
}

template<size_t D> inline
CoordinateSpan<D> clipTriangle( const std::array<double, D>& vertex0,
                                const std::array<double, D>& vertex1,
                                const std::array<double, D>& vertex2,
                                const BoundingBox<D>& bounds,
                                std::span<std::array<double, D>, 9> targetPolygon )
{
    targetPolygon[0] = vertex0;
    targetPolygon[1] = vertex1;
    targetPolygon[2] = vertex2;

    return clipSimplex<D, 2>( targetPolygon, bounds );
}

template<size_t D> inline
BoundingBox<D> triangleClippedBoundingBox( const std::array<double, D>& vertex0,
                                           const std::array<double, D>& vertex1,
                                           const std::array<double, D>& vertex2,
                                           size_t axis, double position, bool side )
{
    auto target = std::array<std::array<double, D>, 6> { };

    auto clipped = clipTriangle<D>( vertex0, vertex1, 
        vertex2, axis, position, side, target );

    return boundingBox<D>( clipped );
}

template<size_t D> inline
BoundingBox<D> triangleClippedBoundingBox( const std::array<double, D>& vertex0,
                                           const std::array<double, D>& vertex1,
                                           const std::array<double, D>& vertex2,
                                           const spatial::BoundingBox<D>& bounds )
{
    return simplexClippedBoundingBox<D, 2>( std::array { vertex0, vertex1, vertex2 }, bounds );
}

template<size_t D> inline
bool clipLineSegment( std::array<double, D>& vertex0,
                      std::array<double, D>& vertex1,
                      const BoundingBox<D>& bounds )
{
    auto target = std::array<std::array<double, D>, 6> { };

    target[0] = vertex0;
    target[1] = vertex1;

    auto polygon = spatial::clipSimplex<D, 1>( target, bounds );

    if( polygon.size( ) >= 2 )
    {
        vertex0 = polygon[0];
        vertex1 = polygon[1];
    }

    return polygon.size( ) >= 2;
}

template<size_t G, size_t L> inline
std::span<std::array<double, G>> clipSimplex( std::span<std::array<double, G>, 3 * ( L + 1 )> vertices,
                                              const BoundingBox<G>& bounds )
{
    static_assert( L <= 2, "Simplex clipping only implemented up to triangles." );

    if constexpr( L == 0 )
    {
        return vertices.subspan( 0, static_cast<size_t>( insideBoundingBox( bounds, vertices[0] ) ) );
    }

    auto result = clipPolygon<G>( vertices.subspan( 0, L + 1 ), vertices, bounds, L == 2 );

    return result.size( ) >= L + 1 ? result : result.subspan( 0, 0 );
}

template<size_t G, size_t L> inline
BoundingBox<G> simplexClippedBoundingBox( std::span<const std::array<double, G>, L + 1> vertices,
                                          const BoundingBox<G>& bounds )
{
    auto target = std::array<std::array<double, G>, 3 * ( L + 1 )> { };
    
    std::copy( vertices.begin( ), vertices.end( ), target.begin( ) );

    return boundingBox<G>( clipSimplex<G, L>( target, bounds ) );
}

template<size_t D> inline
BoundingBox<D> lineSegmentClippedBoundingBox( std::array<double, D> vertex0,
                                              std::array<double, D> vertex1,
                                              const spatial::BoundingBox<D>& bounds )
{
    return simplexClippedBoundingBox<D, 1>( std::array { vertex0, vertex1 }, bounds );
}

inline
std::array<double, 2> lineSegmentNormal( std::array<double, 2> v0,
                                         std::array<double, 2> v1 )
{
    return spatial::normalize<2>( measureWeightedSimplexNormal<2>( std::array { v0, v1 } ) );
}

template<size_t D> requires ( D <= 3 )
constexpr auto simplexSubdivisionIndices( )
{
    static_assert( D <= 3, "Subdivision not implemented" );

    if constexpr( D == 0 )
    {
        return std::array<std::array<size_t, 1>, 1>
        { 
            std::array<size_t, 1> { 0 } 
        };
    }
    else if constexpr( D == 1 )
    {
        return std::array<std::array<size_t, 2>, 1>
        { 
            std::array<size_t, 2> { 0, 1 }
        };
    }
    else if constexpr( D == 2 )
    {
        return std::array<std::array<size_t, 3>, 2>
        { 
            std::array<size_t, 3> { 0, 1, 2 }, 
            std::array<size_t, 3> { 1, 2, 3 } 
        };
    }
    else if constexpr( D == 3 )
    {
        return std::array<std::array<size_t, 4>, 6>
        { 
            std::array<size_t, 4> { 0, 1, 2, 4 }, 
            std::array<size_t, 4> { 1, 2, 3, 4 }, 
            std::array<size_t, 4> { 1, 3, 4, 5 }, 
            std::array<size_t, 4> { 3, 5, 6, 7 }, 
            std::array<size_t, 4> { 2, 3, 4, 6 }, 
            std::array<size_t, 4> { 3, 4, 5, 6 }, 
        };
    }
}

template<size_t G> inline
std::array<double, G> simplexNormal( std::span<const std::array<double, G>, G> vertices )
{
    return normalizeChecked( measureWeightedSimplexNormal( vertices ) );
}

template<size_t G> requires ( G <= 3 && G > 1 ) inline
std::array<double, G> measureWeightedSimplexNormal( std::span<const std::array<double, G>, G> vertices )
{
    static_assert( G <= 3, "Not implemented." );
    static_assert( G > 1, "Can't determine point normal." );

    if constexpr( G == 2 )
    {
        return { vertices[1][1] - vertices[0][1], vertices[0][0] - vertices[1][0] };
    }

    if constexpr( G == 3 )
    {
        return 0.5 * spatial::triangleCross( vertices[0], vertices[1], vertices[2] );
    }
}

template<size_t G, size_t L> inline
double simplexMeasure( std::span<const std::array<double, G>, L + 1> vertices )
{
    static_assert( L <= G );

    if constexpr( L == 3 && G == 3 )
    {
        return tetrahedronVolume( vertices[0], vertices[1], vertices[2], vertices[3] );
    }

    if constexpr( L == 2 )
    {
        return triangleArea<G>( vertices );
    }
    
    if constexpr( L == 1 )
    {
        return spatial::distance( vertices[0], vertices[1] );
    }
    
    if constexpr( L == 0 )
    {
        return 1.0;
    }

    MLHP_NOT_IMPLEMENTED;
}

template<size_t D> constexpr
BoundingBox<D> makeFullBoundingBox( )
{
    return { array::make<D>( std::numeric_limits<double>::lowest( ) ), 
             array::make<D>( std::numeric_limits<double>::max( ) ) };
}

template<size_t D> constexpr
BoundingBox<D> makeEmptyBoundingBox( )
{
    return { array::make<D>( std::numeric_limits<double>::max( ) ), 
             array::make<D>( std::numeric_limits<double>::lowest( ) ) };
}

template<size_t D> constexpr
BoundingBox<D> boundingBoxOr( const BoundingBox<D>& bounds1,
                              const BoundingBox<D>& bounds2 )
{
    return { array::minArray( bounds1[0], bounds2[0] ),
             array::maxArray( bounds1[1], bounds2[1] )};
}

template<size_t D> constexpr
BoundingBox<D> boundingBoxOr( const BoundingBox<D>& bounds,
                              std::array<double, D> xyz )
{
    return { array::minArray( bounds[0], xyz ),
             array::maxArray( bounds[1], xyz )};
}

template<size_t D> constexpr
BoundingBox<D> boundingBoxAnd( const BoundingBox<D>& bounds1,
                               const BoundingBox<D>& bounds2 )
{
    return { array::maxArray( bounds1[0], bounds2[0] ),
             array::minArray( bounds1[1], bounds2[1] )};
}

template<size_t D> constexpr
BoundingBox<D> extendBoundingBox( const BoundingBox<D>& bounds,
                                  double relative, double absolute )
{
    auto result = BoundingBox<D> { };

    for( size_t axis = 0; axis < D; ++axis )
    {
        auto dx = relative * ( bounds[1][axis] - bounds[0][axis] ) + absolute;

        result[0][axis] = bounds[0][axis] - dx;
        result[1][axis] = bounds[1][axis] + dx;
    }

    return result;
}

template<size_t D> constexpr
BoundingBox<D> boundingBoxAt( const std::array<double, D>& xyz, 
                              double width )
{
    return boundingBoxAt( xyz, array::make<D>( width ) );
}

template<size_t D> constexpr
BoundingBox<D> boundingBoxAt( const std::array<double, D>& xyz,
                              const std::array<double, D>& lengths )
{
    auto halflengths = array::multiply( lengths, 0.5 );

    return std::array { xyz - halflengths, xyz + halflengths };
}

template<size_t D> constexpr
bool insideBoundingBox( const BoundingBox<D>& bounds, 
                        std::array<double, D> xyz )
{
    for( size_t axis = 0; axis < D; ++axis )
    {
        if( xyz[axis] < bounds[0][axis] || xyz[axis] > bounds[1][axis] )
        {
            return false;
        }
    }

    return true;
}

template<size_t D> constexpr
bool boundingBoxIsValid( const BoundingBox<D>& bounds, double epsilon )
{
    auto result = true;

    for( size_t axis = 0; axis < D; ++axis )
    {
        result = result && ( bounds[1][axis] >= bounds[0][axis] - epsilon );
    }

    return result;
}

template<size_t D> constexpr
double boundingBoxVolume( const BoundingBox<D>& bounds )
{
    auto volume = 1.0;

    for( size_t axis = 0; axis < D; ++axis )
    {
        volume *= std::max( bounds[1][axis] - bounds[0][axis], 0.0 );
    }

    return volume;
}

template<size_t D> inline
BoundingBox<D> boundingBox( const std::array<double, D>& vertex0,
                            const std::array<double, D>& vertex1,
                            const std::array<double, D>& vertex2 )
{
    auto result = spatial::makeEmptyBoundingBox<D>( );

    for( size_t axis = 0; axis < D; ++axis )
    {
        result[0][axis] = std::min(std::min(vertex0[axis], vertex1[axis]), vertex2[axis]);
        result[1][axis] = std::max( std::max( vertex0[axis], vertex1[axis] ), vertex2[axis] );
    }

    return result;
}

template<size_t D> constexpr
bool boundingBoxIntersectsOther( const BoundingBox<D>& bounds0, 
                                 const BoundingBox<D>& bounds1 )
{
    bool intersect = true;

    for( size_t axis = 0; axis < D; ++axis )
    {
        auto minMax0 = bounds0[0][axis] <= bounds1[1][axis]; 
        auto minMax1 = bounds1[0][axis] <= bounds0[1][axis]; 
        auto maxMin0 = bounds0[1][axis] >= bounds1[0][axis]; 
        auto maxMin1 = bounds1[1][axis] >= bounds0[0][axis];

        intersect = intersect && minMax0 && minMax1 && maxMin0 && maxMin1;
    }

    return intersect;
}

template<size_t D> inline
OptionalTBounds boundingBoxIntersectsInvRay( const spatial::BoundingBox<D>& bounds,
                                             const std::array<double, D>& rayOrigin,
                                             const std::array<double, D>& invDirection )
{
    // Similar to this: https://tavianator.com/2022/ray_box_boundary.html 
    // Unfortunately all versions rely on IEEE handling of inf so that  
    // they don't work when compiling with fast math

    auto min = []( auto a, auto b ) { return a < b ? a : b; };
    auto max = []( auto a, auto b ) { return a > b ? a : b; };

    constexpr auto inf = 0.1 * std::numeric_limits<double>::max( );

    auto tmin = 0.0;
    auto tmax = inf; 

    //for( int axis = 0; axis < D; ++axis )
    for( size_t axis = 0; axis < D; ++axis )
    {
        auto t1 = ( bounds[0][axis] - rayOrigin[axis] ) * invDirection[axis];
        auto t2 = ( bounds[1][axis] - rayOrigin[axis] ) * invDirection[axis];

        tmin = max( tmin, min( t1, t2 ) );
        tmax = min( tmax, max( t1, t2 ) );
    }

    return tmin <= tmax ? std::optional { std::array { tmin, tmax } } : std::nullopt;
}

template<size_t D> inline
OptionalTBounds boundingBoxIntersectsRay( const spatial::BoundingBox<D>& bounds,
                                          const std::array<double, D>& rayOrigin,
                                          const std::array<double, D>& rayDirection )
{

    return boundingBoxIntersectsInvRay( bounds, rayOrigin, spatial::invert( rayDirection ) );
}

template<size_t D>
using HomogeneousTransformationMatrix = std::array<double, ( D + 1 ) * ( D + 1 )>;

namespace detail
{

template<size_t D> constexpr
std::array<double, D> multiply( const HomogeneousTransformationMatrix<D>& matrix,
                                std::array<double, D> xyz )
{
    std::array<double, D> result { };

    for( size_t i = 0; i < D; ++i )
    {
        for( size_t j = 0; j < D; ++j )
        {
            result[i] += matrix[i * ( D + 1 ) + j] * xyz[j];
        }

        result[i] += matrix[i * ( D + 1 ) + D];
    }

    return result;
}

} // namespace detail

template<typename Derived, size_t D>
struct MLHP_EXPORT HomogeneousTransformationBase
{
public:
    Derived& translate( std::array<double, D> vector );
    Derived& scale( std::array<double, D> factors );

    // Generic rotation. 2D and 3D specialization exist.
    Derived& rotate( std::array<double, D> n1, 
                     std::array<double, D> n2, 
                     double phi );
    
    Derived& invert( );
    
    std::array<double, D> operator() ( std::array<double, D> xyz ) const
    {
        return detail::multiply( matrix, xyz );
    }

    HomogeneousTransformationMatrix<D> matrix;
};

template<size_t D>
struct MLHP_EXPORT HomogeneousTransformation : public HomogeneousTransformationBase<HomogeneousTransformation<D>, D> { };

template<>
struct MLHP_EXPORT HomogeneousTransformation<2> : public HomogeneousTransformationBase<HomogeneousTransformation<2>, 2>
{
    using HomogeneousTransformationBase<HomogeneousTransformation<2>, 2>::rotate;

    HomogeneousTransformation& rotate( double phi );
};

template<>
struct MLHP_EXPORT HomogeneousTransformation<3> : public HomogeneousTransformationBase<HomogeneousTransformation<3>, 3>
{
    using HomogeneousTransformationBase<HomogeneousTransformation<3>, 3>::rotate;

    HomogeneousTransformation& rotate( std::array<double, 3> normal, double phi );
};

template<size_t D> MLHP_EXPORT MLHP_PURE
HomogeneousTransformation<D> concatenate( const HomogeneousTransformation<D>& transformation1,
                                          const HomogeneousTransformation<D>& transformation2 );

// Concatenate transformations
template<size_t D, typename... HomogeneousTransformations> inline
HomogeneousTransformation<D> concatenate( const HomogeneousTransformation<D>& transformation1,
                                          const HomogeneousTransformation<D>& transformation2,
                                          HomogeneousTransformations&&... transformations )
{
    auto concatenated = concatenate( transformation1, transformation2 );

    if constexpr( sizeof...( HomogeneousTransformations ) == 0 )
    {
        return concatenated;
    }
    else
    {
        return concatenate( concatenated, std::forward<HomogeneousTransformations>( transformations )... );
    }
}

} // namespace mlhp::spatial

namespace mlhp
{

template<size_t D>
constexpr auto operator+( std::array<double, D> arr1, std::array<double, D> arr2 )
{
    return array::add( arr1, arr2 );
}

template<size_t D>
constexpr auto operator+( std::array<double, D> arr, double value )
{
    return array::add( arr, value );
}

template<size_t D>
constexpr auto operator+( double value, std::array<double, D> arr )
{
    return array::add( arr, value );
}

template<size_t D>
constexpr auto operator-( std::array<double, D> arr1, std::array<double, D> arr2 )
{
    return array::subtract( arr1, arr2 );
}

template<size_t D>
constexpr auto operator-( std::array<double, D> arr, double value )
{
    return array::subtract( arr, value );
}

template<size_t D>
constexpr auto operator-( double value, std::array<double, D> arr )
{
    return array::subtract( value, arr );
}

template<size_t D>
constexpr auto operator*( std::array<double, D> arr1, std::array<double, D> arr2 )
{
    return array::multiply( arr1, arr2 );
}

template<size_t D>
constexpr auto operator*( std::array<double, D> arr, double value )
{
    return array::multiply( arr, value );
}

template<size_t D>
constexpr auto operator*( double value, std::array<double, D> arr )
{
    return array::multiply( arr, value );
}

template<size_t D>
constexpr auto operator/( std::array<double, D> arr1, std::array<double, D> arr2 )
{
    return array::divide( arr1, arr2 );
}

template<size_t D>
constexpr auto operator/( std::array<double, D> arr, double value )
{
    return array::divide( arr, value );
}

template<size_t D>
constexpr auto operator/( double value, std::array<double, D> arr )
{
    return array::divide( value, arr );
}

template<size_t D> inline
std::ostream& operator<<( std::ostream& stream, std::array<double, D> coordinates )
{
    stream << "(" << coordinates[0];

    for( size_t axis = 1; axis < D; ++axis )
    {
        stream << ", " << coordinates[axis];
    }

    stream << ")";

    return stream;
}

} // namespace mlhp

#endif // MLHP_CORE_SPATIAL_IMPL_HPP
