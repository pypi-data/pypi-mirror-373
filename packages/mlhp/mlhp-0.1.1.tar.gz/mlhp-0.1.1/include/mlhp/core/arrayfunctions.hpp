// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_ARRAYFUNCTIONS_HPP
#define MLHP_CORE_ARRAYFUNCTIONS_HPP

#include "utilities.hpp"
#include "compilermacros.hpp"

#include <array>
#include <cmath>
#include <sstream>

namespace mlhp
{
namespace array
{
namespace detail
{
    
template<template<typename> typename Compare, typename T, size_t N> MLHP_PURE
constexpr auto compareElements( const std::array<T, N>& arr )
{
    static_assert( N > 0 );

    auto result = arr[0];

    if constexpr( N > 1 )
    {
        for( size_t i = 1; i < N; ++i )
        {
            result = Compare<T> { } ( arr[i], result ) ? arr[i] : result;
        }
    }

    return result;
}

template<template<typename> typename Compare, typename T, size_t N>
constexpr auto compareArrays( const std::array<T, N>& arr1,
                              const std::array<T, N>& arr2 )
{
    std::array<T, N> result { };

    for( size_t i = 0; i < N; ++i )
    {
        result[i] = Compare<T> { } ( arr1[i], arr2[i] ) ? arr1[i] : arr2[i];
    }

    return result;
}

template<template<typename> typename Operation, typename T, size_t N>
constexpr auto binaryOperation( const std::array<T, N>& arr1,
                                const std::array<T, N>& arr2 )
{
    std::array<T, N> result { };

    for( size_t i = 0; i < N; ++i )
    {
        result[i] = Operation<T> { }( arr1[i], arr2[i] );
    }

    return result;
}

template<template<typename> typename Operation, typename T, size_t N>
constexpr auto binaryOperation( const std::array<T, N>& arr1,
                                const T& value )
{
    std::array<T, N> result { };

    for( size_t i = 0; i < N; ++i )
    {
        result[i] = Operation<T> { }( arr1[i], value );
    }

    return result;
}

template<template<typename> typename Operation, typename T, size_t N>
constexpr auto binaryOperation( const T& value,
                                const std::array<T, N>& arr1 )
{
    std::array<T, N> result { };

    for( size_t i = 0; i < N; ++i )
    {
        result[i] = Operation<T> { }( value, arr1[i] );
    }

    return result;
}

} // namespace detail

template<size_t N, typename T>
constexpr std::array<T, N> make( const T& value )
{
    std::array<T, N> result { };

    for( size_t i = 0; i < N; ++i )
    {
        result[i] = value;
    }

    return result;
}

template<typename T, size_t N>
constexpr std::array<T, N> range( T start = 0, T step = 1 )
{
    std::array<T, N> result { };

    if constexpr ( N != 0 )
    {
        result[0] = start;
    }

    for( size_t i = 1; i < N; ++i )
    {
        result[i] = result[i - 1] + step;
    }

    return result;
}

template<typename T, size_t N>
constexpr auto maxArray( const std::array<T, N>& arr1,
                         const std::array<T, N>& arr2 )
{
    return detail::compareArrays<std::greater>( arr1, arr2 );
}

template<typename T, size_t N>
constexpr auto maxArray( const std::array<T, N>& arr1, 
                         const T& value2 )
{
    return maxArray( arr1, array::make<N>( value2 ) );
}

template<typename T, size_t N>
constexpr auto maxArray( const T& value1,
                         const std::array<T, N>& arr2 )
{
    return maxArray( array::make<N>( value1 ), arr2 );
}

template<typename T, size_t N> MLHP_PURE
constexpr auto maxElement( std::array<T, N> arr )
{
    return detail::compareElements<std::greater>( arr );
}

template<typename T, size_t N>
constexpr auto minArray( const std::array<T, N>& arr1,
                         const std::array<T, N>& arr2 )
{
    return detail::compareArrays<std::less>( arr1, arr2 );
}

template<typename T, size_t N>
constexpr auto minArray( const std::array<T, N>& arr1,
                         const T& value2 )
{
    return minArray( arr1, array::make<N>( value2 ) );
}

template<typename T, size_t N>
constexpr auto minArray( const T& value1,
                         const std::array<T, N>& arr2 )
{
    return minArray( array::make<N>( value1 ), arr2 );
}

template<typename T, size_t N> MLHP_PURE
constexpr auto minElement( const std::array<T, N>& arr )
{
    return detail::compareElements<std::less>( arr );
}

template<typename T, size_t N>
constexpr auto add( std::array<T, N> arr1, std::array<T, N> arr2 )
{
    return detail::binaryOperation<std::plus>( arr1, arr2 );
}

template<typename T, size_t N>
constexpr auto add( std::array<T, N> arr, T value )
{
    return detail::binaryOperation<std::plus>( arr, value );
}

template<typename T, size_t N>
constexpr auto add( const T& value, const std::array<T, N>& arr )
{
    return detail::binaryOperation<std::plus>( value, arr );
}

template<typename T, size_t N>
constexpr auto subtract( const std::array<T, N>& arr1,
                         const std::array<T, N>& arr2 )
{
    return detail::binaryOperation<std::minus>( arr1, arr2 );
}

template<typename T, size_t N>
constexpr auto subtract( const std::array<T, N>& arr, 
                         const T& value )
{
    return detail::binaryOperation<std::minus>( arr, value );
}

template<typename T, size_t N>
constexpr auto subtract( const T& value, 
                         const std::array<T, N>& arr )
{
    return detail::binaryOperation<std::minus>( value, arr );
}

template<typename T, size_t N>
constexpr auto multiply( const std::array<T, N>& arr1,
                         const std::array<T, N>& arr2 )
{
    return detail::binaryOperation<std::multiplies>( arr1, arr2 );
}

template<typename T, size_t N>
constexpr auto multiply( const std::array<T, N>& arr,
                         const T& value )
{
    return detail::binaryOperation<std::multiplies>( arr, value );
}

template<typename T, size_t N>
constexpr auto multiply( const T& value,
                         const std::array<T, N>& arr )
{
    return detail::binaryOperation<std::multiplies>( value, arr );
}

template<typename T, size_t N>
constexpr auto divide( const std::array<T, N>& arr1,
                       const std::array<T, N>& arr2 )
{
    return detail::binaryOperation<std::divides>( arr1, arr2 );
}

template<typename T, size_t N>
constexpr auto divide( const std::array<T, N>& arr,
                       const T& value )
{
    return detail::binaryOperation<std::divides>( arr, value );
}

template<typename T, size_t N>
constexpr auto divide( const T& value,
                       const std::array<T, N>& arr )
{
    return detail::binaryOperation<std::divides>( value, arr );
}

template<typename T, size_t N>
constexpr auto square( const std::array<T, N>& arr )
{
    return array::multiply( arr, arr );
}

template<typename T, size_t N>
constexpr auto inverse( const std::array<T, N>& arr )
{
    return array::divide<T>( 1, arr );
}

template<typename T, size_t N, size_t times = 2>
constexpr auto duplicate( const std::array<T, N>& array )
{
    std::array<std::array<T, N>, times> result { };

    for( size_t i = 0; i < times; ++i )
    {
        result[i] = array;
    }

    return result;
}

template<typename T, size_t N> inline
auto extract( const std::array<std::vector<T>, N>& vectors, std::array<size_t, N> ijk )
{
    std::array<T, N> result { };

    for( size_t axis = 0; axis < N; ++axis )
    {
        result[axis] = vectors[axis][ijk[axis]];
    }

    return result;
}

template<typename T, size_t N> 
constexpr auto reverse( std::array<T, N> array )
{
    auto result = std::array<T, N> { };

    for( size_t axis = 0; axis < N; ++axis )
    {
        result[N - 1 - axis] = array[axis];
    }

    return result;
}

template<size_t N, typename T> inline
auto resize( std::array<std::vector<T>, N>& vectors, std::array<size_t, N> sizes )
{
    for( size_t axis = 0; axis < N; ++axis )
    {
        vectors[axis].resize( sizes[axis] );
    }
}

template<size_t N, typename T> inline
auto resize0( std::array<std::vector<T>, N>& vectors )
{
    resize<N>( vectors, { } );
}

template<typename T, size_t N> MLHP_PURE
constexpr auto slice( std::array<T, N> arr, size_t normal )
{
    std::array<T, N - 1> result { };

    for( size_t i = 0; i < normal; ++i )
    {
        result[i] = arr[i];
    }

    for( size_t i = normal; i + 1 < N; ++i )
    {
        result[i] = arr[i + 1];
    }

    return result;
}

template<typename T, size_t N>
constexpr auto midpoint( std::array<T, N> arr0, std::array<T, N> arr1 )
{
    auto result = std::array<T, N> { };

    for( size_t i = 0; i < N; ++i )
    {
        result[i] = std::midpoint( arr0[i], arr1[i] );
    }
    
    return result;
}

template<typename T, size_t N>
constexpr auto peel( std::array<T, N> arr, size_t index = N - 1 )
{
    return std::tuple { slice( arr, index ), arr[index] };
}

template<typename T, size_t N>
constexpr auto sliceIfNotOne( std::array<T, N> arr, [[maybe_unused]] size_t normal )
{
    if constexpr( N > 1 )
    {
        return slice( arr, normal );
    }
    else
    {
        return arr;
    }
}

template<typename T, size_t N> MLHP_PURE
constexpr auto insert( std::array<T, N> arr, size_t index, T value )
{
    std::array<T, N + 1> result { };

    for( size_t i = 0; i < index; ++i )
    {
        result[i] = arr[i];
    }

    result[index] = value;

    if constexpr ( N > 0 ) // to silence comparison always false warning
    { 
        for( size_t i = index; i < N; ++i )
        {
            result[i + 1] = arr[i];
        }
    }

    return result;
}

template<typename T, size_t N>
constexpr auto append( std::array<T, N> arr, T value )
{
    return insert( arr, N, value );
}

template<typename T, size_t N>
constexpr auto setEntry( std::array<T, N> arr, size_t index, T value )
{
    auto result = arr;

    result[index] = value;

    return result;
}

template<size_t N>
constexpr std::array<size_t, N> makeSizes( size_t value )
{
    return make<N>( value );
}

template<typename T, size_t N>
constexpr std::array<T, N> makeAndSet( const T& defaultValue, size_t index, T valueAtIndex )
{
    std::array<T, N> result { };

    for( size_t i = 0; i < N; ++i )
    {
        result[i] = defaultValue;
    }

    result[index] = valueAtIndex;

    return result;
}

template<size_t D, typename Containers> inline
auto elementSizes( const std::array<Containers, D>& containers )
{
    std::array<size_t, D> result;

    for( size_t axis = 0; axis < D; ++axis )
    {
        result[axis] = containers[axis].size( );
    }

    return result;
}

template<typename T, size_t N, typename Operation> MLHP_PURE
constexpr auto accumulate( const std::array<T, N>& arr, Operation operation, T initial )
{
    auto result = initial;

    if constexpr( N > 0 )
    {
        for( size_t i = 0; i < N; ++i )
        {
            result = operation( result, arr[i] );
        }
    }

    return result;
}

template<typename T, size_t N>
constexpr T product( std::array<T, N> values )
{
    return accumulate( values, std::multiplies<T>{ }, T { 1 } );
}

template<typename T, size_t N>
constexpr T sum( std::array<T, N> values )
{
    return accumulate( values, std::plus<T>{ }, T { 0 } );
}

template<typename TargetType, typename SourceType, size_t N>
constexpr auto convert( std::array<SourceType, N> source )
{
    std::array<TargetType, N> target;

    for( size_t axis = 0; axis < N; ++axis )
    {
        target[axis] = static_cast<TargetType>( source[axis] );
    }

    return target;
}

template<size_t D, typename T> 
std::string to_string( std::array<T, D> values )
{
    auto sstream = std::ostringstream { };
    
    sstream << "(";

    if constexpr( D > 0 )
    {
        sstream << values[0];

        for( size_t i = 1; i < D; ++i )
        {
            sstream << ", " << values[i];
        }
    }

    sstream << ")";

    return sstream.str( );
}

} // namespace array
} // namespace mlhp

#endif // MLHP_CORE_ARRAYFUNCTIONS_HPP
