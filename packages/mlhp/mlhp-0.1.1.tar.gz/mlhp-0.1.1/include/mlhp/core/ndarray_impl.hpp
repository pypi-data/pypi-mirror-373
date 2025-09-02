// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_NDARRAY_IMPL_HPP
#define MLHP_CORE_NDARRAY_IMPL_HPP

namespace mlhp
{
namespace nd
{

template<std::integral Integer, size_t N, typename FunctionType> inline
void execute( std::array<Integer, N> limits, 
              FunctionType&& function )
{
    auto recursive = [&]<std::integral... Indices>( auto&& self, Indices... indices )
    {    
        constexpr auto axis = sizeof...( Indices );

        for( Integer i = 0; i < limits[axis]; ++i )
        {
            if constexpr( axis + 1 < N )
            {
                self( self, indices..., i );
            }
            else
            {
                function( std::array<Integer, N> { indices..., i } );
            }
        }
    };

    recursive( recursive );
}

template<std::integral Integer, size_t N, typename FunctionType, std::integral... Indices>
inline void executeBoundary( std::array<Integer, N> limits, FunctionType&& function )
{
    nd::execute( limits, [=, function = std::forward<FunctionType>( function )]( std::array<size_t, N> ijk )
    {                
        for( size_t axis = 0; axis < N; ++axis )
        {
            if( ijk[axis] == 0 || ijk[axis] + 1 == limits[axis] )
            {
                function( ijk );

                return;
            }
        }
    } );
}

template<std::integral Integer, size_t N, typename FunctionType> inline
void executeWithIndex( std::array<Integer, N> limits, 
                       FunctionType&& function )
{
    auto index = size_t { 0 };

    auto recursive = [&]<std::integral... Indices>( auto&& self, Indices... indices )
    {    
        constexpr size_t axis = sizeof...( Indices );

        for( Integer i = 0; i < limits[axis]; ++i )
        {
            if constexpr( axis + 1 < N )
            {
                self( self, indices..., i );
            }
            else
            {
                function( std::array<Integer, N> { indices..., i }, index++ );
            }
        }
    };

    recursive( recursive );
}

template<size_t N, std::integral Integer, typename FunctionType> inline
void executeTriangular( Integer limit, FunctionType&& function )
{
    auto recursive = [function = std::forward<FunctionType>(function)]
	<std::integral... Indices>( auto&& self, auto currenLimit, Indices... indices )
    {    
        for( size_t i = 0; i < currenLimit; ++i )
        {
            if constexpr( sizeof...( Indices ) + 1 < N )
            {
                self( self, currenLimit - i, indices..., i );
            }
            else
            {
                function( std::array<Integer, N> { indices..., i } );
            }
        }
    };

    recursive( recursive, limit );
}

template<size_t N, std::integral Integer, typename FunctionType>
inline void executeTriangularBoundary( Integer limit, FunctionType&& function )
{
    nd::executeTriangular<N>( limit, [=, function = std::forward<FunctionType>( function )]( std::array<size_t, N> ijk )
    {                
        if( array::minElement( ijk ) == 0 || array::sum( ijk ) + 1 == limit )
        {
            function( ijk );
        }
    } );
}

template<std::integral Integer, size_t N, size_t M>
constexpr size_t linearIndex( std::array<size_t, M> strides,
                              std::array<Integer, N> indices )
{
    static_assert( M == N || M + 1 == N );

    size_t index = 0;

    for( size_t i = 0; i < M; ++i )
    {
        index += strides[i] * indices[i];
    }

    if constexpr( M + 1 == N )
    {
        index += indices[N - 1];
    }

    return index;
}

template<std::integral Integer1, std::integral Integer2, size_t N>
constexpr auto unravel( Integer1 index, std::array<Integer2, N> limits )
{
    return unravelWithStrides( index, stridesFor( limits ) );
}

template<std::integral Integer1, std::integral Integer2, size_t N>
constexpr auto unravelWithStrides( Integer1 index, std::array<Integer2, N> strides, size_t axis )
{
    for( size_t i = 0; i < axis; ++i )
    {
        index %= strides[i];
    }

    return index / strides[axis];
}

template<std::integral Integer, size_t N>
constexpr auto unravelWithStrides( Integer index, std::array<Integer, N> strides )
{
    std::array<Integer, N> indices { };

    for( size_t axis = 0; axis < N; ++axis )
    {
        indices[axis] = index / strides[axis];

        index -= indices[axis] * strides[axis];
    }

    return indices;
}

template<std::integral Integer>
constexpr auto binaryUnravel( Integer index, size_t ndim, size_t axis )
{
    auto shift = ndim - 1 - axis;

    return ( index & utilities::binaryPow<Integer>( shift ) ) >> shift;
}

template<std::integral ResultInteger, size_t N, std::integral SourceInteger>
constexpr auto binaryUnravel( SourceInteger index )
{
    std::array<ResultInteger, N> result { };

    if constexpr( N > 0 ) // to silence axis < N always false warning
    {
        for( size_t axis = 0; axis < N; ++axis )
        {
            result[axis] = static_cast<ResultInteger>( binaryUnravel( index, N, axis ) );
        }
    }

    return result;
}

template<std::integral ResultInteger, std::integral SourceInteger, size_t N>
constexpr auto binaryRavel( std::array<SourceInteger, N> indices )
{
    ResultInteger result { 0 };

    for( size_t axis = 0; axis < N; ++axis )
    {
        result += indices[axis] * binaryStride<ResultInteger>( N, axis );
    }

    return result;
}

template<std::integral ResultInteger>
constexpr auto binaryStride( size_t ndim, size_t axis )
{
    return utilities::binaryPow<ResultInteger>( ndim - 1 - axis );
}

template<std::integral Return, std::integral Integer, size_t N>
constexpr std::array<Return, N> stridesWithType( std::array<Integer, N> shape )
{
    static_assert( N > 0 );

    std::array<Return, N> result { };

    result[N - 1] = 1;

    for( size_t i = 0; i + 1 < N; ++i )
    {
        result[N - 2 - i] = static_cast<Return>( shape[N - 1 - i] ) * result[N - 1 - i];
    }

    return result;
}

template<std::integral Integer, size_t N>
constexpr std::array<Integer, N> stridesFor( std::array<Integer, N> shape )
{
    return stridesWithType<Integer, Integer, N>( shape );
}

template<typename T, size_t... Shape>
constexpr StaticArray<T, Shape...>::StaticArray( ) noexcept :
    data_{ } { }

template<typename T, size_t... Shape>
constexpr StaticArray<T, Shape...>::StaticArray( T defaultValue ) :
    data_( array::make<size_, T>( defaultValue ) ) { }

template<typename T, size_t... Shape>
template<std::integral Integer>
constexpr T& StaticArray<T, Shape...>::operator[]( std::array<Integer, ndim_> indices )
{
    return data_[linearIndex( strides_, indices )];
}

template<typename T, size_t... Shape>
template<std::integral Integer>
constexpr const T& StaticArray<T, Shape...>::operator[]( std::array<Integer, ndim_> indices ) const
{
    return data_[linearIndex( strides_, indices )];
}

template<typename T, size_t... Shape>
constexpr T& StaticArray<T, Shape...>::operator[]( size_t linearIndex )
{
    return data_[linearIndex];
}

template<typename T, size_t... Shape>
constexpr const T& StaticArray<T, Shape...>::operator[]( size_t linearIndex ) const
{
    return data_[linearIndex];
}

template<typename T, size_t... Shape>
template<std::integral... IndexPack>
constexpr T& StaticArray<T, Shape...>::operator( )( size_t index0, IndexPack ...indices )
{
    static_assert( sizeof... ( IndexPack ) + 1 == ndim_, "Number of indices doesn't match dimensionality." );

    return data_[linearIndex( strides_, std::array<size_t, ndim_>{ index0, static_cast<size_t>( indices )... } )];
}

template<typename T, size_t... Shape>
template<std::integral... IndexPack>
constexpr const T& StaticArray<T, Shape...>::operator( )( size_t index0, IndexPack ...indices ) const
{
    static_assert( sizeof... ( IndexPack ) + 1 == ndim_, "Number of indices doesn't match dimensionality." );

    return data_[linearIndex( strides_, std::array<size_t, ndim_>{ index0, static_cast<size_t>( indices )... } )];
}

template<typename T, size_t... Shape>
constexpr auto StaticArray<T, Shape...>::begin( ) { return data_.begin( ); }

template<typename T, size_t... Shape>
constexpr auto StaticArray<T, Shape...>::begin( ) const { return data_.begin( ); }

template<typename T, size_t... Shape>
constexpr auto StaticArray<T, Shape...>::end( ) { return data_.end( ); }

template<typename T, size_t... Shape>
constexpr auto StaticArray<T, Shape...>::end( ) const { return data_.end( ); }

template<typename T, size_t... Shape>
constexpr size_t StaticArray<T, Shape...>::size( ) const { return size_; }

template<typename T, size_t... Shape>
constexpr size_t StaticArray<T, Shape...>::ndim( ) const { return ndim_; }

template<typename T, size_t... Shape>
constexpr auto StaticArray<T, Shape...>::shape( ) const { return shape_; }

template<typename T, size_t... Shape>
constexpr auto StaticArray<T, Shape...>::strides( ) const { return strides_; }

template<typename T, size_t D> inline
DynamicArray<T, D>::DynamicArray( std::array<size_t, D> shape ) :
    data_( array::product( shape ) ),
    shape_( shape ),
    strides_( stridesFor( shape ) )
{  }

template<typename T, size_t D> inline
DynamicArray<T, D>::DynamicArray(  ) :
    DynamicArray<T, D>::DynamicArray( array::makeSizes<D>( 0 ) )
{  }

template<typename T, size_t D> inline
DynamicArray<T, D>::DynamicArray( std::array<size_t, D> shape, T initialValue ) :
    data_( array::product( shape ), initialValue ),
    shape_( shape ),
    strides_( stridesFor( shape ) )
{ }

template<typename T, size_t D> inline
DynamicArray<T, D>::DynamicArray( std::array<size_t, D> shape, const std::vector<T>& data ) :
    data_( data ),
    shape_( shape ),
    strides_( stridesFor( shape ) )
{
    MLHP_CHECK( array::product( shape_ ) == data_.size( ), "Data vector length doesn't fit shape." );
}

template<typename T, size_t D> inline
typename DynamicArray<T, D>::reference DynamicArray<T, D>::operator[]( Indices indices )
{
    return data_[linearIndex( strides_, indices )];
}

template<typename T, size_t D> inline
typename DynamicArray<T, D>::reference DynamicArray<T, D>::operator[]( size_t linearIndex )
{
    return data_[linearIndex];
}

template<typename T, size_t D> inline
typename DynamicArray<T, D>::const_reference DynamicArray<T, D>::operator[]( Indices indices ) const
{
    return data_[linearIndex( strides_, indices )];
}

template<typename T, size_t D> inline
typename DynamicArray<T, D>::const_reference DynamicArray<T, D>::operator[]( size_t linearIndex ) const
{
    return data_[linearIndex];
}

template<typename T, size_t D>
template<std::integral... IndexPack> inline
typename DynamicArray<T, D>::reference DynamicArray<T, D>::operator( )( size_t index0, IndexPack ...indices )
{
    static_assert( sizeof... ( IndexPack ) + 1 == D, "Number of indices doesn't match dimensionality." );

    return data_[linearIndex( strides_, Indices{ index0, static_cast<size_t>( indices )... } )];
}

template<typename T, size_t D>
template<std::integral... IndexPack> inline
typename DynamicArray<T, D>::const_reference DynamicArray<T, D>::operator( )( size_t index0, IndexPack ...indices ) const
{
    static_assert( sizeof... ( IndexPack ) + 1 == D, "Number of indices doesn't match dimensionality." );

    return data_[linearIndex( strides_, Indices{ index0, static_cast<size_t>( indices )... } )];
}

template<typename T, size_t D> inline
void DynamicArray<T, D>::resize( std::array<size_t, D> shape )
{
    shape_ = shape;
    strides_ = stridesFor( shape );
    data_.resize( array::product( shape ) );
}

template<typename T, size_t D> inline
auto DynamicArray<T, D>::begin( ) { return data_.begin( ); }

template<typename T, size_t D> inline
auto DynamicArray<T, D>::begin( ) const { return data_.begin( ); }

template<typename T, size_t D> inline
auto DynamicArray<T, D>::end( ) { return data_.end( ); }

template<typename T, size_t D> inline
auto DynamicArray<T, D>::end( ) const { return data_.end( ); }

template<typename T, size_t D> inline
size_t DynamicArray<T, D>::size( ) const { return data_.size( ); }

template<typename T, size_t D> constexpr
size_t DynamicArray<T, D>::ndim( ) const { return D; }

template<typename T, size_t D> inline
auto DynamicArray<T, D>::shape( ) const { return shape_; }

template<typename T, size_t D> inline
auto DynamicArray<T, D>::strides( ) const { return strides_; }

template<typename T, size_t D> inline
size_t DynamicArray<T, D>::memoryUsage( ) const
{
    return utilities::vectorInternalMemory( data_ );
}

template<typename T1, typename T2, size_t D> inline
void nonzero( const DynamicArray<T1, D>& ndarray,
              std::vector<std::array<T2, D>>& target )
{
    target.resize( 0 );

    size_t linearIndex = 0;
    
    execute( array::convert<T2>( ndarray.shape( ) ), [&]( std::array<T2, D> ijk ) -> void
    {
        if( ndarray[linearIndex++] )
        {
            target.push_back( ijk );
        }
    } );
}

template<typename T, size_t D> inline
bool isEqual( const DynamicArray<T, D>& ndarray1,
              const DynamicArray<T, D>& ndarray2 )
{
    for( size_t axis = 0; axis < D; ++axis )
    {
        if( ndarray1.shape( )[axis] != ndarray2.shape( )[axis] )
        {
            return false;
        }
    }

    return std::equal( ndarray1.begin( ), ndarray1.end( ), ndarray2.begin( ) );
}

template<typename T, size_t D, size_t Value, size_t... Sizes>
struct EquallySizedStaticArray
{
    using type = typename EquallySizedStaticArray<T, D - 1, Value, Value, Sizes...>::type;
};

// Partial specialization for N == 0
template<typename T, size_t Value, size_t... Sizes>
struct EquallySizedStaticArray<T, 0, Value, Sizes...>
{
    using type = nd::StaticArray<T, Sizes...>;
};

} // namespace nd
} // mlhp

#endif // MLHP_CORE_NDARRAY_IMPL_HPP
