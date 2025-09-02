// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/implicit.hpp"
#include "mlhp/core/spatial.hpp"

#include <array>

namespace mlhp
{
namespace implicit
{

template<size_t D>
ImplicitFunction<D> sphere( std::array<double, D> origin, double radius )
{
    return [=]( std::array<double, D> xyz )
    {
        return spatial::distanceSquared( xyz, origin ) <= radius * radius;
    };
}

template<size_t D>
ImplicitFunction<D> ellipsoid( std::array<double, D> origin,
                               std::array<double, D> radii )
{
    radii = array::square( radii );

    return [=]( std::array<double, D> xyz ) noexcept
    {
        return array::sum( array::divide( array::square( xyz - origin ), radii ) ) <= 1.0;
    };
}

template<size_t D>
ImplicitFunction<D> cube( spatial::BoundingBox<D> bounds )
{
    return [=]( std::array<double, D> xyz ) noexcept MLHP_PURE 
    { 
        return spatial::insideBoundingBox( bounds, xyz );
    };
}

template<size_t D>
ImplicitFunction<D> cube( std::array<double, D> x1, 
                          std::array<double, D> x2 )
{
    return cube( std::array { x1, x2 } );
}

namespace
{
        
template<size_t D, typename T>
auto genericClip( T&& function,
                  std::array<double, D> origin,
                  std::array<double, D> outwardNormal )
{
    return [=, function = std::forward<T>( function )](std::array<double, D> xyz) noexcept
    { 
        return spatial::dot( xyz - origin, outwardNormal ) <= 0.0 && function( xyz );
    };
}

template<size_t D, typename T>
auto genericClip( T&& function, size_t axis, double offset, bool sign )
{
    return genericClip( std::forward<T>( function ),
                        array::setEntry<double, D>( { }, axis, offset ), 
                        array::setEntry<double, D>( { }, axis, sign ? -1.0 : 1.0 ) );
}

} // namespace

template<size_t D>
ImplicitFunction<D> halfspace( std::array<double, D> origin,
                               std::array<double, D> outwardNormal )
{
    return genericClip<D>( []( std::array<double, D> ) { return true; }, origin, outwardNormal );
}

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> halfspace( size_t axis, double offset, bool sign )
{
    return genericClip<D>( []( std::array<double, D> ) { return true; }, axis, offset, sign );
}

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> threshold( const spatial::ScalarFunction<D>& function, double threshold, bool sign )
{
    return [=]( std::array<double, D> xyz )
    {
        return sign * function( xyz ) >= threshold;
    };
}

template<size_t D>
ImplicitFunction<D + 1> extrude( const ImplicitFunction<D>& function,
                                 double z1, double z2, size_t axis )
{
    double min = std::min( z1, z2 );
    double max = std::max( z1, z2 );

    return [=]( std::array<double, D + 1> xyz )
    { 
        return xyz[axis] >= min && xyz[axis] <= max && function( array::slice( xyz, axis ) );
    };
}

template<size_t D>
ImplicitFunction<D + 1> extrude( const ImplicitFunction<D>& function,
                                 size_t axis )
{
    return [=]( std::array<double, D + 1> xyz )
    { 
        return function( array::slice( xyz, axis ) );
    };
}

template<size_t D>
ImplicitFunction<D> clip( const ImplicitFunction<D>& function,
                          std::array<double, D> origin,
                          std::array<double, D> outwardNormal )
{
    return genericClip<D>( function, origin, outwardNormal );
}

template<size_t D>
ImplicitFunction<D> clip( const ImplicitFunction<D>& function,
                          size_t axis, double offset, bool sign )
{
    return genericClip<D>( function, axis, offset, sign );
}

template<size_t D>
ImplicitFunction<D> invert( const ImplicitFunction<D>& function )
{
    return [=]( std::array<double, D> xyz )
    {
        return !function( xyz );
    };
}

template<size_t D>
ImplicitFunction<D + 1> revolveSphereAroundPath( const TemporalPath<D>& path, double radius )
{ 
    return [=]( std::array<double, D + 1> xyt )
    {
        return spatial::distanceSquared( array::slice( xyt, D ), path( xyt[D] ) ) < radius * radius;
    };
}


template<size_t D>
ImplicitFunction<D - 1> sliceLast( const ImplicitFunction<D>& function, double value )
{
    return [=]( std::array<double, D - 1> xy )
    {
        return function( array::insert( xy, D - 1, value ) );
    };
}
template<size_t D> 
ImplicitFunction<D> transform( const ImplicitFunction<D>& function,
                               const spatial::HomogeneousTransformation<D>& transformation )
{
    auto inverse = transformation;

    inverse.invert( );

    return [=]( std::array<double, D> xyz )
    {
        return function( inverse( xyz ) );
    };
}

#define MLHP_INSTANTIATE_DIM( D )                                                                 \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> sphere( std::array<double, D> origin, double radius );                    \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> cube( std::array<double, D> x1,                                           \
                              std::array<double, D> x2 );                                         \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> cube( spatial::BoundingBox<D> bounds );                                   \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> ellipsoid( std::array<double, D> origin,                                  \
                                   std::array<double, D> radii );                                 \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> halfspace( std::array<double, D> origin,                                  \
                                   std::array<double, D> outwardNormal );                         \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> halfspace( size_t axis, double offset, bool sign );                       \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> threshold( const spatial::ScalarFunction<D>& function,                    \
                                   double threshold, bool sign );                                 \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D + 1> extrude( const ImplicitFunction<D>& function,                         \
                                     double z1, double z2, size_t axis );                         \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D + 1> extrude( const ImplicitFunction<D>& function,                         \
                                     size_t axis );                                               \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> clip( const ImplicitFunction<D>& function,                                \
                              std::array<double, D> origin,                                       \
                              std::array<double, D> outwardNormal );                              \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> clip( const ImplicitFunction<D>& function,                                \
                              size_t axis, double offset, bool sign );                            \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> invert( const ImplicitFunction<D>& function );                            \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D + 1> revolveSphereAroundPath( const TemporalPath<D>& path,                 \
                                                     double radius );                             \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> sliceLast( const ImplicitFunction<D + 1>& function,                       \
                                   double value );                                                \
                                                                                                  \
    template MLHP_EXPORT                                                                          \
    ImplicitFunction<D> transform( const ImplicitFunction<D>& function,                           \
                                   const spatial::HomogeneousTransformation<D>& transformation );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // implicit
} // mlhp

