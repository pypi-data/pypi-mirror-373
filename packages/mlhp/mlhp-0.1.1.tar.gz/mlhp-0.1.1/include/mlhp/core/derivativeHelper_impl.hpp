// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_DERIVATIVE_HELPER_IMPL_HPP
#define MLHP_CORE_DERIVATIVE_HELPER_IMPL_HPP

#include "mlhp/core/utilities.hpp"
#include "mlhp/core/arrayfunctions.hpp"

#include <array>

namespace mlhp::diff
{
namespace detail
{

// Partially specialized for diff orders 0, 1, 2 (and any D)
template<size_t D, size_t diffOrder>
struct DerivativeIndices
{
    static consteval decltype( auto ) indices( );
};

template<size_t D>
struct DerivativeIndices<D, 0>
{
    static consteval decltype( auto ) indices( )
    {
        return std::array<std::array<size_t, D>, 1> { array::makeSizes<D>( 0 ) };
    }
};

template<size_t D>
struct DerivativeIndices<D, 1>
{
    static consteval decltype( auto ) indices( )
    {
        std::array<std::array<size_t, D>, D> result { };

        for( size_t i = 0; i < D; ++i )
        {
            for( size_t j = 0; j < D; ++j )
            {
                result[i][j] = i == j ? 1 : 0;
            }
        }

        return result;
    }
};

template<size_t D>
struct DerivativeIndices<D, 2>
{
    static consteval decltype( auto ) indices( )
    {
        constexpr size_t numberOfComponents = ( D * ( D + 1 ) ) / 2;

        std::array<std::array<size_t, D>, numberOfComponents> result { };

        size_t index = 0;

        for( size_t i = 0; i < D; ++i )
        {
            for( size_t j = i; j < D; ++j )
            {
                for( size_t axis = 0; axis < D; ++axis )
                {
                    result[index][axis] = ( axis == i ? size_t { 1 } : size_t { 0 } ) + 
                                          ( axis == j ? size_t { 1 } : size_t { 0 } );
                }

                index++;
            }
        }

        return result;
    }
};

} // namespace detail

template<size_t D, size_t diffOrder>
consteval size_t ncomponents( )
{
    return detail::DerivativeIndices<D, diffOrder>::indices( ).size( );
}

template<size_t D>
consteval std::array<size_t, 3> ncomponents( )
{
    return std::array { ncomponents<D, 0>( ),
                        ncomponents<D, 1>( ),
                        ncomponents<D, 2>( ) };
}

template<size_t D, size_t diffOrder>
consteval auto indices( )
{
    return detail::DerivativeIndices<D, diffOrder>::indices( );
}

template<size_t D, size_t Diff>
consteval size_t allNComponents( )
{
    size_t value = 1;

    if constexpr( Diff > 0 )
    {
        value = diff::ncomponents<D, Diff>( ) + allNComponents<D, Diff - 1>( );
    }

    return value;
}

template<size_t D, size_t MaxDiff>
consteval auto allIndices( )
{
    static_assert( MaxDiff <= 2 );

    constexpr auto totalSize = allNComponents<D, MaxDiff>( );

    std::array<std::array<size_t, D>, totalSize> result { };

    constexpr auto indices0 = diff::indices<D, 0>( );

    std::copy( indices0.begin( ), indices0.end( ), result.begin( ) );

    size_t offset = indices0.size( );

    if constexpr( MaxDiff >= 1 )
    {
        constexpr auto indices1 = diff::indices<D, 1>( );

        std::copy( indices1.begin( ), indices1.end( ), result.begin( ) + static_cast<std::ptrdiff_t>( offset ) );

        offset += indices1.size( );
    }
    if constexpr( MaxDiff >= 2 )
    {
        constexpr auto indices2 = diff::indices<D, 2>( );

        std::copy( indices2.begin( ), indices2.end( ), result.begin( ) + static_cast<std::ptrdiff_t>( offset ) );
    }

    return result;
}

} // mlhp::diff

#endif // MLHP_CORE_DERIVATIVE_HELPER_IMPL_HPP
