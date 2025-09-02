// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_NDARRAY_HPP
#define MLHP_CORE_NDARRAY_HPP

#include "mlhp/core/utilities.hpp"
#include "mlhp/core/arrayfunctions.hpp"

#include <array>
#include <vector>

#ifndef __cpp_lib_concepts
#define __cpp_lib_concepts
#endif

#include <concepts>

namespace mlhp
{
namespace nd
{

template<std::integral Integer, size_t N, typename FunctionType>
inline void execute( std::array<Integer, N> limits, FunctionType&& function );

template<std::integral Integer, size_t N, typename FunctionType, std::integral... Indices>
inline void executeBoundary( std::array<Integer, N> limits, FunctionType&& function );

template<std::integral Integer, size_t N, typename FunctionType>
inline void executeWithIndex( std::array<Integer, N> limits, FunctionType&& function );

template<size_t N, std::integral Integer, typename FunctionType>
inline void executeTriangular( Integer limit, FunctionType&& function );

template<size_t N, std::integral Integer, typename FunctionType>
inline void executeTriangularBoundary( Integer limit, FunctionType&& function );

template<std::integral Integer, size_t N, size_t M>
constexpr size_t linearIndex( std::array<size_t, M> strides,
                              std::array<Integer, N> indices );

template<std::integral Integer1, std::integral Integer2, size_t N>
constexpr auto unravel( Integer1 index, std::array<Integer2, N> limits );

template<std::integral Integer1, std::integral Integer2, size_t N>
constexpr auto unravelWithStrides( Integer1 index, std::array<Integer2, N> strides, size_t axis );

template<std::integral Integer, size_t N>
constexpr auto unravelWithStrides( Integer index, std::array<Integer, N> strides );

template<std::integral Integer>
constexpr auto binaryUnravel( Integer index, size_t ndim, size_t axis );

template<std::integral ResultInteger, size_t N, std::integral SourceInteger>
constexpr auto binaryUnravel( SourceInteger index );

template<std::integral ResultInteger, std::integral SourceInteger, size_t N>
constexpr auto binaryRavel( std::array<SourceInteger, N> indices );

template<std::integral ResultInteger>
constexpr auto binaryStride( size_t ndim, size_t axis );

template<std::integral Return, std::integral Integer, size_t N>
constexpr std::array<Return, N> stridesWithType( std::array<Integer, N> shape );

template<std::integral Integer, size_t N>
constexpr std::array<Integer, N> stridesFor( std::array<Integer, N> shape );

// --------------------------- static ND array ----------------------------------

//! N-dimensional of type T, but same size for each axis
template<typename T, size_t D, size_t Value, size_t... Sizes>
struct EquallySizedStaticArray;

template<typename T, size_t... Shape>
class StaticArray
{
    static_assert( sizeof...( Shape ) > 0, "Zero dimensional arrays are not allowed." );

    static constexpr size_t ndim_ = sizeof...( Shape );
    static constexpr std::array<size_t, ndim_> shape_ = { Shape... };
    static constexpr std::array<size_t, ndim_> strides_ = stridesFor( shape_ );
    static constexpr size_t size_ = array::product( shape_ );

    static_assert( size_ > 0, "Zero sized axes not are not allowed." );

    std::array<T, size_> data_;

public:
    explicit constexpr StaticArray( ) noexcept;
    explicit constexpr StaticArray( T defaultValue );
    
    constexpr StaticArray( std::initializer_list<T> initializerList )
    { 
        std::copy( initializerList.begin( ), initializerList.end( ), data_.begin( ) );
    }

    template<std::integral Integer>
    constexpr T& operator[]( std::array<Integer, ndim_> indices );
    
    template<std::integral Integer>
    constexpr const T& operator[]( std::array<Integer, ndim_> indices ) const;

    constexpr T& operator[]( size_t linearIndex );
    constexpr const T& operator[]( size_t linearIndex ) const;

    template<std::integral... IndexPack>
    constexpr T& operator( )( size_t index0, IndexPack ...indices );

    template<std::integral... IndexPack>
    constexpr const T& operator( )( size_t index0, IndexPack ...indices ) const;

    constexpr auto begin( );
    constexpr auto begin( ) const;
    constexpr auto end( );
    constexpr auto end( ) const;

    constexpr size_t size( ) const;
    constexpr size_t ndim( ) const;
    constexpr auto shape( ) const;
    constexpr auto strides( ) const;
};

//--------------------------- dynamic ND array ----------------------------------

template<typename T, size_t D>
class DynamicArray
{
    static_assert( D > 0, "Zero dimensional arrays are not allowed." );

    std::vector<T> data_;

    std::array<size_t, D> shape_;
    std::array<size_t, D> strides_;

public:
    using Indices = std::array<size_t, D>;

    using reference = typename std::vector<T>::reference;
    using const_reference = typename std::vector<T>::const_reference;

    explicit DynamicArray( );
    explicit DynamicArray( std::array<size_t, D> shape );

    DynamicArray( std::array<size_t, D> shape, T initialValue );
    DynamicArray( std::array<size_t, D> shape, const std::vector<T>& data );

    reference operator[]( Indices indices );
    reference operator[]( size_t linearIndex );
    const_reference operator[]( Indices indices ) const;
    const_reference operator[]( size_t linearIndex ) const;

    template<std::integral... IndexPack>
    reference operator( )( size_t index1, IndexPack ...indices );

    template<std::integral... IndexPack>
    const_reference operator( )( size_t index1, IndexPack ...indices ) const;

    void resize( std::array<size_t, D> shape );

    auto begin( );
    auto begin( ) const;
    auto end( );
    auto end( ) const;

    size_t size( ) const;
    auto shape( ) const;
    auto strides( ) const;

    constexpr size_t ndim( ) const;

    //! The amount dynamic memory used, excludes sizeof( *this )
    size_t memoryUsage( ) const;
};

template<typename T1, typename T2, size_t D>
void nonzero( const DynamicArray<T1, D>& ndarray,
              std::vector<std::array<T2, D>>& target );

template<typename T, size_t D>
bool isEqual( const DynamicArray<T, D>& ndarray1,
              const DynamicArray<T, D>& ndarray2 );

} // namespace nd

template<size_t D>
using BooleanMask = nd::DynamicArray<bool, D>;

template<size_t D>
using BooleanMasks = std::vector<BooleanMask<D>>;

//! N-dimensional Boolean array with size 3 in each direction
template<size_t D>
using TopologyMask = typename nd::EquallySizedStaticArray<bool, D, 3>::type;

template<size_t D>
using TopologyMasks = std::vector<TopologyMask<D>>;

//! std::vector of N-dimensional arrays
template<typename T, size_t... Shape>
using CellDataArray = std::vector<nd::StaticArray<T, Shape...>>;

} // mlhp

#include "mlhp/core/ndarray_impl.hpp"

#endif // MLHP_CORE_NDARRAY_HPP
