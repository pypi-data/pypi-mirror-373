// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_UTILITIES_HPP
#define MLHP_CORE_UTILITIES_HPP

#include "mlhp/core/compilermacros.hpp"
#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/parallel.hpp"

#include <vector>
#include <array>
#include <span>
#include <string>
#include <iostream>
#include <stdexcept>
#include <functional>
#include <typeindex>
#include <chrono>

// Defined and initialized in logging.cpp
MLHP_EXPORT extern bool MLHP_DISABLE_EXCEPTION_LOGS;

#ifndef MLHP_LOG_EXCEPTION
#define MLHP_LOG_EXCEPTION( message ) if( !MLHP_DISABLE_EXCEPTION_LOGS ) std::cout << "MLHP check failed in " << __FUNCTION__ << ".\nMessage: " << ( message ) << std::endl
#endif

#define MLHP_CHECK( expression, message ) if( !( expression ) ) \
{                                                               \
    MLHP_LOG_EXCEPTION( message );                              \
    throw std::runtime_error( message );                        \
}

#ifndef MLHP_DEBUG_CHECKS
#define MLHP_CHECK_DBG( expression, message )
#else
#define MLHP_CHECK_DBG( expression, message ) MLHP_CHECK( expression, message )
#endif

namespace mlhp::utilities
{

// ================== Concepts ===================
    
template<typename T> 
concept DoubleCastable = ( static_cast<double>( T { } ), true );

// Following https://stackoverflow.com/a/51032862
template<typename, template<typename...> typename>
inline constexpr bool is_specialization = false;

template<template<typename...> typename T, typename... Args>
inline constexpr bool is_specialization<T<Args...>, T> = true;

template<typename T> 
inline constexpr bool is_stdarray_specialization = false;

template<typename T, size_t N> 
inline constexpr bool is_stdarray_specialization<std::array<T, N>> = true;

template<typename T> 
inline constexpr bool is_stdpair_specialization = false;

template<typename T1, typename T2> 
inline constexpr bool is_stdpair_specialization<std::pair<T1, T2>> = true;

template<typename T> 
concept StdVector = is_specialization<T, std::vector>;

template<typename T> 
concept StdArray = is_stdarray_specialization<T>;

template<typename T, typename V> 
concept StdVectorOf = StdVector<T> && std::is_same_v<V, typename T::value_type>;

template<typename T, typename V> 
concept StdArrayOf = StdArray<T> && std::is_same_v<V, typename T::value_type>;

// ================ Simple math ==================

template<typename T>
constexpr T integerPow( T base, size_t exponent );

template<typename T>
constexpr T binaryPow( size_t exponent );

// interpolate at given x between (x0, y0) and (x1, y1)
double interpolate( double x0, double y0, double x1, double y1, double x );

// maps to [0, 1]
double mapToLocal0( double begin, double end, double x );

// maps to [-1, 1]
double mapToLocal1( double begin, double end, double x );

template<std::integral Int1, std::integral Int2>
constexpr auto divideCeil( Int1 a, Int2 b );

// =============== Vector function ===============

template<typename T>
void scaleVector( std::vector<T>& vec, const T& value );

template<typename Target, typename SourceVector>
auto convertVector( SourceVector&& source );

template<typename T, size_t N>
auto spans( std::array<std::vector<T>, N>& vector );

template<typename T, size_t N>
auto cspans( const std::array<std::vector<T>, N>& vector );

template<typename T, size_t N1, size_t N2>
auto cspans( const std::array<std::array<T, N1>, N2>& arrays );

template<typename T, size_t N>
auto span( std::array<T, N>& arr );

template<typename T, size_t N>
auto span( const std::array<T, N>& arr );

template<typename T, size_t N>
auto cspan( const std::array<T, N>& arr );

template<typename T, size_t N>
auto cspan( std::span<T, N> span );

template<typename T>
void addVectorsInplace( std::vector<T>& v1, const std::vector<T>& v2 );

// E.g. parameters (0.5, 1.5, 3) return [0.5, 1.0, 1.5]
std::vector<double> linspace( double min, double max, size_t n );

// Find internal interval in increasing sequence of coordinates.
// For example:
//     positions = [1.0, 2.0, 3.0], x = 0.5 --> returns 0
//     positions = [1.0, 2.0, 3.0], x = 1.5 --> returns 0
//     positions = [1.0, 2.0, 3.0], x = 2.5 --> returns 1
//     positions = [1.0, 2.0, 3.0], x = 3.5 --> returns 1
MLHP_PURE size_t findInterval( const std::vector<double>& positions, double x );

template<typename T>
std::vector<T> linearizeVectors( const std::vector<std::vector<T>>& vectors );

template<typename T, std::integral Index1, std::integral Index2>
auto linearizedSpan( const std::pair<std::vector<Index1>, std::vector<T>>& linearized, 
                     Index2 index );

template<typename IndexType>
auto allocateLinearizationIndices( size_t size );

template<typename IndexType>
auto sumLinearizationIndices( std::vector<IndexType>& indices );

template<typename DataType, typename IndexType>
auto sumAndAllocateData( std::vector<IndexType>& indices, DataType value = 0 );

template<typename T> inline
auto& resize0( std::vector<T>& vector );

template<typename T, size_t N> inline
auto& resize0( std::array<std::vector<T>, N>& vectors );

template<typename... T>
void resize0( T&&... vectors );

template<typename T>
void clearMemory( std::vector<T>& vector );

//! Returns an std::array with results of calling .size( ) on each argument
auto containerSizes( auto&&... containers );

//! Resizes each container by n and returns the container sizes before this operation
template<typename... Containers>
auto increaseSizes( size_t n, Containers&... containers );

template<typename... Args>
size_t vectorInternalMemory( const std::vector<Args>&... vec );

template<typename T>
struct ThreadLocalContainer
{
    ThreadLocalContainer( ) :
        data( parallel::getMaxNumberOfThreads( ) )
    { }
    
    ThreadLocalContainer( const T& defaultValue ) :
        data( parallel::getMaxNumberOfThreads( ), defaultValue )
    { }

    T& get( ) { return data[parallel::getThreadNum( )]; }
    const T& get( ) const { return data[parallel::getThreadNum( )]; }

    std::vector<T> data;
};

// ==================== Logging ====================

inline auto tic( const std::string& msg = "" )
{
    std::cout << msg << std::flush;

    return std::chrono::high_resolution_clock::now( );
}

template<typename TimePoint>
inline double seconds( const TimePoint& t0,
                       const TimePoint& t1 )
{
    return std::chrono::duration_cast<std::chrono::duration<double>>( t1 - t0 ).count( );
}

template<typename TicType>
inline auto toc( TicType ticPoint,
                 const std::string& msg,
                 const std::string& postMsg = " s.\n" )
{
    auto now = std::chrono::high_resolution_clock::now( );

    std::cout << msg << seconds( ticPoint, now ) << postMsg << std::flush;

    return now;
}

template<typename TicType>
inline auto toc( TicType ticPoint )
{
    return seconds( ticPoint, std::chrono::high_resolution_clock::now( ) );
}

template<typename T, size_t D>
std::string toString( std::array<T, D> arr )
{
    if constexpr( D == 0 ) return "()";

    std::string result = "(" + std::to_string( arr[0] );

    for( size_t i = 1; i < D; ++i )
    {
        result += ", " + std::to_string( arr[i] );
    }

    return result + ")";
}

MLHP_EXPORT std::string thousandSeparator( std::uint64_t integer );

//! Converts result to fixed notation string with precision 1 or 2 if result < 10
MLHP_EXPORT std::string roundNumberString( double result );

//! Prints memory usage with suitable unit
MLHP_EXPORT std::string memoryUsageString( size_t bytes );

// ==================== Other ====================

// Divides [0, size) into chunks. The index range from each chunk 
// can be computed using chunkRange below.
// * Returns [actual nchunks, actual minimum chunk size, first index of small block]
// * If size < approximateNChunks, then the number of chunks is set to size.
// * If size < minimumChunkSize, then one chunk with size is created.
template<std::integral Int>
auto divideIntoChunks( Int size, Int approximateNChunks, Int minimumChunkSize = 1 );

// Returns [begin, end) of given chunk according to the result of divideIntoChunks
template<std::integral Int>
auto chunkRange( Int iChunk, std::array<Int, 3> data );

template<typename Container, std::integral IndexType>
auto begin( Container& container, IndexType index = 0 );

template<std::integral IndexType>
std::ptrdiff_t ptrdiff( IndexType index );

template<typename T>
auto copyShared( const T& obj );

template<typename T>
auto moveShared( T&& obj );

template<typename Iterator1, typename Iterator2> MLHP_PURE
auto floatingPointEqual( Iterator1 begin1, Iterator1 end1, Iterator2 begin2, double tolerance );

class MLHP_EXPORT DefaultVirtualDestructor
{
protected:
    virtual ~DefaultVirtualDestructor( ) = default;
   
    explicit DefaultVirtualDestructor( ) = default;
    explicit DefaultVirtualDestructor( const DefaultVirtualDestructor& ) = default;
    explicit DefaultVirtualDestructor( DefaultVirtualDestructor&& ) = default;

    DefaultVirtualDestructor& operator=( const DefaultVirtualDestructor& ) = default;
    DefaultVirtualDestructor& operator=( DefaultVirtualDestructor&& ) = default;
};

// Type erased cache with tag parameter to make it unique
template<typename Tag>
class Cache final
{
public:
    Cache( ) : 
        Cache( 0 ) 
    { }

    template<typename T> requires ( !std::is_same_v<T, Cache<Tag>> )
    Cache( T&& obj ) : 
        cache { std::make_shared<T>( std::forward<T>( obj ) ) } 
#ifdef MLHP_DEBUG_CHECKS
        , info { typeid( T ) }
#endif
    { }

    Cache( const Cache& ) = delete;
    Cache( Cache&& ) = default;
    Cache& operator=( const Cache& ) = delete;
    Cache& operator=( Cache&& ) = default;

private:
    std::shared_ptr<void> cache;

#ifdef MLHP_DEBUG_CHECKS
    std::type_index info;
#endif

    template<typename T2, typename Tag2> friend
    T2& cast( Cache<Tag2>& cache );
};

template<typename T, typename Tag> inline
T& cast( Cache<Tag>& cache ) 
{
    MLHP_CHECK_DBG( typeid( T ) == cache.info, "Inconsistent Cache type." );

    return *static_cast<T*>( cache.cache.get( ) );
}

template<typename T, typename Tag> inline
const T& cast( const Cache<Tag>& cache )
{
    return cast( const_cast<Cache<Tag>&>( cache ) );
}

template<typename IndexType, typename ReturnType, typename... Args>
auto makeIndexRangeFunction( IndexType size,
                             const std::function<ReturnType( IndexType, Args... )>& evaluate );

template<typename IndexType, typename ObjectType, typename Return, typename... Args>
auto makeIndexRangeFunction( IndexType size, 
                             const ObjectType& object, 
                             Return( ObjectType::* function )( IndexType, Args... ) const );

constexpr auto doNothing( ) { return []( auto&&... ) noexcept { }; }

template<typename T>
constexpr auto returnEmpty( ) { return []( auto&&... ) noexcept { return T { }; }; }

template<typename T>
constexpr auto returnValue( T&& obj ) 
{ 
    return [obj = std::forward<T>( obj )]( auto&&... ) noexcept { return obj; }; 
}

} // namespace mlhp::utilities

// ================ Macro checks =================

#define MLHP_EXPECTS( expression ) MLHP_CHECK( expression, "Violated precondition." )
#define MLHP_EXPECTS_DBG( expression ) MLHP_CHECK_DBG( expression, "Violated precondition." )

#define MLHP_THROW( message ) throw std::runtime_error( message )
#define MLHP_NOT_IMPLEMENTED MLHP_THROW( "Function \"" + std::string { __FUNCTION__ } + "\" is not implemented." )

#include "mlhp/core/utilities_impl.hpp"

#endif // MLHP_CORE_UTILITIES_HPP
