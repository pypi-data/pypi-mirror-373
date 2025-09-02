// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_UTILITIES_IMPL_HPP
#define MLHP_CORE_UTILITIES_IMPL_HPP

#include <array>
#include <chrono>
#include <algorithm>
#include <functional>
#include <fstream>
#include <numeric>

namespace mlhp::utilities
{

template<typename T>
constexpr T integerPow( T base, size_t exponent )
{
    T result = 1;

    for( size_t i = 0; i < exponent; ++i )
    {
        result *= base;
    }

    return result;
}

template<typename T>
constexpr T binaryPow( size_t exponent )
{
    static_assert( std::is_integral_v<T> );

    return T { 1 } << exponent;
}

namespace detail
{

template<typename T> inline
size_t vectorInternalMemorySingle( const std::vector<T>& vec )
{
    size_t memory = vec.capacity( ) * sizeof( T );

    if constexpr( !std::is_trivial_v<T> && !is_stdpair_specialization<T> )
    {
        for( const auto& element : vec )
        {
            memory += vectorInternalMemorySingle( element );
        }
    }

    return memory;
}

template<> MLHP_PURE inline
size_t vectorInternalMemorySingle( const std::vector<bool>& vec )
{
    return vec.capacity( ) / 8;
}

} // namespace detail

template<typename... Args> inline
size_t vectorInternalMemory( const std::vector<Args>&... vec )
{
    static_assert( sizeof...( Args ) > 0 );

    return ( detail::vectorInternalMemorySingle( vec ) + ... );
}

template<typename T> inline
void scaleVector( std::vector<T>& vec, const T& factor, const T& offset )
{
    for( auto& entry : vec ) entry = factor * entry + offset;
}

template<typename T> inline
void scaleVector( std::vector<T>& vec, const T& factor )
{
    scaleVector( vec, factor, T { 0 } );
}

template<typename Target, typename SourceVector>
auto convertVector( SourceVector&& source )
{
    auto result = std::vector<Target>( source.size( ) );

    for( size_t i = 0; i < source.size( ); ++i )
    {
        result[i] = static_cast<Target>( source[i] );
    }

    return result;
}

template<typename T, size_t N> inline
auto spans( std::array<std::vector<T>, N>& vector )
{
    auto result = std::array<std::span<T>, N> { };

    for( size_t i = 0; i < N; ++i )
    {
        result[i] = std::span { vector[i].begin( ), vector[i].end( ) };
    }

    return result;
}

template<typename T, size_t N> inline
auto cspans( const std::array<std::vector<T>, N>& vector )
{
    auto result = std::array<std::span<const T>, N> { };

    for( size_t i = 0; i < N; ++i )
    {
        result[i] = std::span { vector[i].begin( ), vector[i].end( ) };
    }

    return result;
}

template<typename T, size_t N1, size_t N2> inline
auto cspans( const std::array<std::array<T, N1>, N2>& arrays )
{
    auto extractSpans = [&]<size_t I = 0>( auto && self, auto&&... args )
    {
        if constexpr ( I < N2 )
        {
            auto span = std::span<const double, N1>( arrays[I].begin( ), arrays[I].end( ) );

            return self.template operator()<I + 1>( self, std::forward<decltype( args )>( args )..., std::move( span ) );
        }
        else
        {
            return std::array { args... };
        }
    };

    return extractSpans( extractSpans );
}

template<typename T, size_t N>
inline auto span( std::array<T, N>& arr )
{
    return std::span<T, N>( arr.begin( ), arr.end( ) );
}

template<typename T, size_t N>
inline auto span( const std::array<T, N>& arr )
{
    return std::span<const T, N>( arr.begin( ), arr.end( ) );
}

template<typename T, size_t N>
inline auto cspan( const std::array<T, N>& arr )
{
    return utilities::span( arr );
}

template<typename T, size_t N>
inline auto cspan( std::span<T, N> span )
{
    return std::span<const T, N>( span );
}

template<typename T> inline
void addVectorsInplace( std::vector<T>& v1, const std::vector<T>& v2 )
{
    std::transform( v1.begin( ), v1.end( ), v2.begin( ), v1.begin( ), std::plus<T>( ) );
}

template<typename Iterator1, typename Iterator2> inline MLHP_PURE
auto floatingPointEqual( Iterator1 begin1, Iterator1 end1, Iterator2 begin2, double tolerance )
{
    return std::equal( begin1, end1, begin2, [=]( double v1, double v2 )
    {
        if( v2 > tolerance )
        {
            return std::abs( ( v1 - v2 ) / v2 ) <= tolerance;
        }
        else
        {
            return std::abs( v1 - v2 ) <= tolerance;
        }
    } );
}

inline double interpolate( double x0, double y0, double x1, double y1, double x )
{
    return ( x - x0 ) / ( x1 - x0 ) * ( y1 - y0 ) + y0;
}

// maps to [0, 1]
inline double mapToLocal0( double begin, double end, double x )
{
    return ( x - begin ) / ( end - begin );
}

// maps to [-1, 1]
inline double mapToLocal1( double begin, double end, double x )
{
    return 2.0 * mapToLocal0( begin, end, x ) - 1.0;
}

template<std::integral Int1, std::integral Int2>
constexpr auto divideCeil( Int1 a, Int2 b )
{
    return a / b + ( a % b != 0 );
}

template<std::integral Int> inline
auto divideIntoChunks( Int size, Int nchunks, Int minChunkSize )
{
    MLHP_CHECK( nchunks > 0, "Zero number of chunks." );
    MLHP_CHECK( minChunkSize > 0, "Zero chunk size." );

    if( size == 0 )
    {
        return std::array<Int, 3> { size, 0, 0 };
    }

    nchunks = std::min( std::max<Int>( size / minChunkSize, Int { 1 } ), nchunks );

    if( size <= nchunks )
    {
        return std::array<Int, 3> { size, 1, 0 };
    }

    Int chunkSize = size / nchunks;
    Int blockLimit = size - chunkSize * nchunks;

    return std::array { nchunks, chunkSize, blockLimit };
}

template<std::integral Int> inline
auto chunkRange( Int iChunk, std::array<Int, 3> data )
{
    auto [nchunks, chunkSize, blockLimit] = data;

    MLHP_CHECK( iChunk < nchunks, "Chunk index out of bounds" );

    Int begin = iChunk * chunkSize + std::min( iChunk, blockLimit );
    Int end = begin + chunkSize + ( iChunk < blockLimit ? 1 : 0 );

    return std::array<Int, 2>{ begin, end };
}

template<std::integral IndexType> inline
std::ptrdiff_t ptrdiff( IndexType index )
{
    return static_cast<std::ptrdiff_t>( index );
}

template<typename T> inline
auto copyShared( const T& obj )
{
    return std::make_shared<T>( obj );
}

template<typename T> inline
auto moveShared( T&& obj )
{
    return std::make_shared<std::remove_reference_t<T>>( std::move( obj ) );
}

template<typename Container, std::integral IndexType>
inline auto begin( Container& container, IndexType index )
{
    return std::begin( container ) + utilities::ptrdiff( index );
}

template<typename T> inline
std::vector<T> linearizeVectors( const std::vector<std::vector<T>>& vectors )
{
    std::vector<T> target;

    for( const auto& vector : vectors )
    {
        target.insert( target.end( ), vector.begin( ), vector.end( ) );
    }

    return target;
}

template<typename IndexType> inline
auto allocateLinearizationIndices( size_t size )
{
    std::vector<IndexType> result( size + 1, IndexType { 0 } );

    return result;
}

template<typename IndexType> inline
auto sumLinearizationIndices( std::vector<IndexType>& indices )
{
    std::partial_sum( indices.begin( ) + 1, indices.end( ), indices.begin( ) + 1 );

    return indices.back( );
}

template<typename DataType, typename IndexType> inline
auto sumAndAllocateData( std::vector<IndexType>& indices, DataType value )
{
    auto n = sumLinearizationIndices( indices );

    return std::vector<DataType>( n, value );
}

template<typename T> inline
void clearMemory( std::vector<T>& vector )
{
    vector.clear( );
    vector.shrink_to_fit( );
}

template<typename T> inline
auto& resize0( std::vector<T>& vector )
{
    vector.resize( 0 );

    return vector;
}

template<typename T, size_t N> inline
auto& resize0( std::array<std::vector<T>, N>& vectors )
{
    for( auto& v : vectors ) 
    {
        resize0( v );
    }

    return vectors;
}

template<typename... T> inline
void resize0( T&&... vectors )
{
    [[maybe_unused]] std::initializer_list<int> tmp{ ( resize0( vectors ), 0 )... };
}

inline auto containerSizes( auto&&... containers )
{
    return std::array { containers.size( )... };
}

template<typename... Containers> inline
auto increaseSizes( size_t n, Containers&... containers )
{
    auto sizes0 = utilities::containerSizes( containers... );

    [[maybe_unused]] std::initializer_list<int> tmp { ( containers.resize( containers.size( ) + n ), 0 )... };

    return sizes0;
}

template<typename T, std::integral Index1, std::integral Index2> inline
auto linearizedSpan( const std::pair<std::vector<Index1>, std::vector<T>>& linearized, Index2 index )
{
    return std::span( linearized.second.begin( ) + ptrdiff( linearized.first[index] ),
                      linearized.second.begin( ) + ptrdiff( linearized.first[index + 1] ) );
}

inline std::vector<double> linspace( double min, double max, size_t n )
{
    std::vector<double> indices( n );

    if( n > 0 )
    {
        indices[0] = min;
    }

    if( n > 1 )
    {
        double increment = ( max - min ) / ( n - 1.0 ) ;

        for( size_t i = 1; i < n; ++i )
        {
            indices[i] = increment * i + min;
        }
    }

    return indices;
}

inline size_t findInterval( const std::vector<double>& positions, double x )
{
    auto it = std::lower_bound( positions.begin( ) + 1, positions.end( ) - 1, x );

    return static_cast<size_t>( std::distance( positions.begin( ), it ) ) - 1;
}

template<typename T> struct IndexRangeFunction;

template<typename ReturnType, typename IndexType, typename... Args>
struct IndexRangeFunction<ReturnType( IndexType, Args... )>
{
    using Function = std::function<ReturnType( IndexType, Args... )>;

    IndexRangeFunction( IndexType size, const Function& function ) :
        size_( size ), function_( function )
    { }

    template<typename... Args2>
    auto operator() ( IndexType index, Args2&&... args ) const
    {
        return function_( index, std::forward<Args2>( args )... );
    }

    auto size( ) const
    {
        return size_;
    }

    IndexType size_;
    Function function_;
};

template<typename IndexType, typename ReturnType, typename... Args> inline
auto makeIndexRangeFunction( IndexType size,
                             const std::function<ReturnType( IndexType, Args... )>& evaluate )
{
    return IndexRangeFunction<ReturnType( IndexType, Args... )>( size, evaluate );
}

template<typename IndexType, typename ObjectType, typename Return, typename... Args> inline
auto makeIndexRangeFunction( IndexType size, 
                             const ObjectType& object, 
                             Return( ObjectType::* function )( IndexType, Args... ) const )
{
    auto f = [&object, function]( IndexType index, Args... args ) -> Return
    {
        return ( object.*function )( index, args... );
    };

    return IndexRangeFunction<Return( IndexType, Args... )>( size, f );
}

} // namespace mlhp::utilities

#endif // MLHP_CORE_UTILITIES_IMPL_HPP
