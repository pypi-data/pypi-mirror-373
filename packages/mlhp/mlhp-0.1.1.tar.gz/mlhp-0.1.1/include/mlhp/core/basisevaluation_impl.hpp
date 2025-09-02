// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_BASISEVALUATION_IMPL_HPP
#define MLHP_CORE_BASISEVALUATION_IMPL_HPP

#include "mlhp/core/derivativeHelper.hpp"
#include "mlhp/core/utilities.hpp"

namespace mlhp
{

template<size_t D> inline
size_t BasisFunctionEvaluation<D>::nfields( ) const
{
    return nfields_;
}

template<size_t D> inline
size_t BasisFunctionEvaluation<D>::maxdifforder( ) const
{
    return maxdifforder_;
}

template<size_t D> inline
size_t BasisFunctionEvaluation<D>::ndof( ) const
{
    return ndof_;
}

template<size_t D> inline
size_t BasisFunctionEvaluation<D>::ndof( size_t ifield ) const
{
    return info_[ifield];
}


template<size_t D> inline
size_t BasisFunctionEvaluation<D>::nblocks( ) const
{
    return nblocks_;
}

template<size_t D> inline
size_t BasisFunctionEvaluation<D>::nblocks( size_t ifield ) const
{
    return info_[nfields_ + ifield];
}

template<size_t D> inline
size_t BasisFunctionEvaluation<D>::ndofpadded( ) const
{
    return nblocks( ) * blocksize( );
}

template<size_t D> inline
size_t BasisFunctionEvaluation<D>::ndofpadded( size_t ifield ) const
{
    return nblocks( ifield ) * blocksize( );
}

template<size_t D> 
auto BasisFunctionEvaluation<D>::sizes( ) const
{
    return std::tuple { ndof( ), nblocks( ), ndofpadded( ) };
}


template<size_t D> 
auto BasisFunctionEvaluation<D>::sizes( size_t ifield ) const
{
    return std::tuple { ndof( ifield ), nblocks( ifield ), ndofpadded( ifield ) };
}

template<size_t D> inline
size_t BasisFunctionEvaluation<D>::memoryUsage( ) const
{
    return info_.capacity( ) * sizeof( info_[0] ) + 
           data_.capacity( ) * sizeof( data_[0] );
}

template<size_t D> constexpr
size_t BasisFunctionEvaluation<D>::blocksize( )
{
    return memory::simdVectorSize<double>( );
}

template<size_t D> constexpr
size_t BasisFunctionEvaluation<D>::ncomponents( size_t difforder )
{
    constexpr auto ncomponents = diff::ncomponents<D>( );
 
    return ncomponents[difforder];
}

template<size_t D> inline
auto BasisFunctionEvaluation<D>::get( size_t ifield, size_t difforder )
{
    return memory::assumeAligned( data_.data( ) + offset( ifield, difforder ) );
}

template<size_t D> inline
auto BasisFunctionEvaluation<D>::get( size_t ifield, size_t difforder ) const
{
    return memory::assumeAligned( data_.data( ) + offset( ifield, difforder ) );
}

template<size_t D> inline
auto BasisFunctionEvaluation<D>::noalias( size_t ifield, size_t difforder )
{
    return memory::assumeNoalias( get( ifield, difforder ) );
}

template<size_t D> inline
auto BasisFunctionEvaluation<D>::noalias( size_t ifield, size_t difforder ) const
{
    return memory::assumeNoalias( get( ifield, difforder ) );
}

template<size_t D> 
template<size_t MaxDiff> inline
auto BasisFunctionEvaluation<D>::noalias( size_t ifield )
{
    // Create lambda to generate variadic diff indices 
    return [&] <size_t... Indices>( std::index_sequence<Indices...>&& )
    { 
        return std::array { noalias( ifield, Indices ) ... }; 
    }
    // Call lambda and return result
    ( std::make_index_sequence<MaxDiff + 1>( ) );
}

template<size_t D> 
template<size_t MaxDiff> inline
auto BasisFunctionEvaluation<D>::noalias( size_t ifield ) const
{
    // Create lambda to generate variadic diff indices 
    return [&] <size_t... Indices>( std::index_sequence<Indices...>&&  )
    { 
        return std::array { noalias( ifield, Indices ) ... }; 
    }
    // Call lambda and return result
    ( std::make_index_sequence<MaxDiff + 1>( ) );
}

template<size_t D> inline
size_t BasisFunctionEvaluation<D>::offset( size_t ifield, size_t difforder ) const
{
    return info_[2 * nfields_ + ifield * ( maxdifforder_ + 1 ) + difforder];
}

template<size_t D> inline
std::array<double, D> BasisFunctionEvaluation<D>::rst( ) const
{
    return rst_;
}

template<size_t D> inline
std::array<double, D> BasisFunctionEvaluation<D>::xyz( ) const
{
    return xyz_;
}

template<size_t D> inline
CellIndex BasisFunctionEvaluation<D>::elementIndex( ) const
{
    return ielement_;
}

template<size_t D> inline
void BasisFunctionEvaluation<D>::initialize( CellIndex ielement, size_t nfields, size_t maxdifforder )
{
    MLHP_CHECK( nfields != 0, "Zero field components." );
    MLHP_CHECK( maxdifforder <= 2, "Higher than second derivatives." );

    ielement_ = ielement;
    nfields_ = nfields;
    maxdifforder_ = maxdifforder;

    info_.resize( 2 * nfields + ( maxdifforder + 1 ) * nfields + 1 );

    std::fill( info_.data( ), info_.data( ) + nfields, 0 );
}

template<size_t D> inline
void BasisFunctionEvaluation<D>::addDofs( size_t ifield, size_t ndof )
{
    info_[ifield] += ndof;
}

template<size_t D> inline
void BasisFunctionEvaluation<D>::allocate( )
{
    size_t index = 2 * nfields_;

    info_[index] = 0;
    ndof_ = 0;

    for( size_t ifield = 0; ifield < nfields_; ++ifield )
    {
        info_[nfields_ + ifield] = memory::paddedNumberOfBlocks<double>( info_[ifield] );

        for( size_t idifforder = 0; idifforder <= maxdifforder_; ++idifforder )
        {
            info_[index + 1] = info_[index] + ndofpadded( ifield ) * ncomponents( idifforder );

            index += 1;
        }
    }

    data_.resize( info_.back( ) );

    for( size_t ifield = 0; ifield < nfields_; ++ifield )
    {
        ndof_ += info_[ifield];
    }

    nblocks_ = memory::paddedNumberOfBlocks<double>( ndof_ );
}

template<size_t D> inline
void BasisFunctionEvaluation<D>::setRst( std::array<double, D> rst )
{
    rst_ = rst;
}

template<size_t D> inline
void BasisFunctionEvaluation<D>::setXyz( std::array<double, D> xyz )
{
    xyz_ = xyz;
}

template<size_t D> inline
void BasisFunctionEvaluation<D>::setElementIndex( CellIndex ielement )
{
    ielement_ = ielement;
}

template<size_t diffOrder, size_t D> inline
auto evaluateSolution( const BasisFunctionEvaluation<D>& shapes,
                       std::span<const DofIndex> locationMap,
                       std::span<const double> dofs,
                       size_t ifield )
{
    static constexpr auto ncomponents = diff::ncomponents<D, diffOrder>( );

    auto target = std::array<double, ncomponents> { };

    evaluateSolution( shapes, locationMap, dofs, target, diffOrder, ifield );

    return target;
}

template<size_t nfields, size_t difforder, size_t D> inline
auto evaluateSolutions( const BasisFunctionEvaluation<D>& shapes,
                        std::span<const DofIndex> locationMap,
                        std::span<const double> dofs )
{
    static constexpr auto ncomponents = diff::ncomponents<D, difforder>( );

    auto target = std::array<double, nfields * ncomponents> { };

    evaluateSolutions( shapes, locationMap, dofs, target, difforder );

    auto result = std::array<std::array<double, ncomponents>, nfields> { };

    for( size_t ifield = 0; ifield < nfields; ++ifield )
    {
        for( size_t idiff = 0; idiff < ncomponents; ++idiff )
        {
            result[ifield][idiff] = target[ifield * ncomponents + idiff];
        }
    }

    return result;
}

template<size_t D>
auto evaluateSolution( const BasisFunctionEvaluation<D>& shapes,
                       std::span<const DofIndex> locationMap,
                       std::span<const double> dofs,
                       size_t ifield )
{
    return evaluateSolution<0, D>( shapes, locationMap, dofs, ifield )[0];
}

template<size_t nfields, size_t D>
auto evaluateSolutions( const BasisFunctionEvaluation<D>& shapes,
                        std::span<const DofIndex> locationMap,
                        std::span<const double> dofs )
{
    auto result = std::array<double, nfields> { };

    evaluateSolutions( shapes, locationMap, dofs, result, 0 );

    return result;
}

template<size_t D>
auto evaluateGradient( const BasisFunctionEvaluation<D>& shapes,
                       std::span<const DofIndex> locationMap,
                       std::span<const double> dofs,
                       size_t ifield )
{
    return evaluateSolution<1, D>( shapes, locationMap, dofs, ifield );
}

template<size_t nfields, size_t D>
auto evaluateGradients( const BasisFunctionEvaluation<D>& shapes,
                        std::span<const DofIndex> locationMap,
                        std::span<const double> dofs )
{
    return evaluateSolutions<nfields, 1, D>( shapes, locationMap, dofs );
}

template<size_t nfields, size_t D> inline
auto fieldSizes( const BasisFunctionEvaluation<D>& shapes )
{
    auto sizes = std::array<size_t, nfields> { };

    for( size_t ifield = 0; ifield < nfields; ++ifield )
    { 
        sizes[ifield] = shapes.ndof( ifield );
    }

    return sizes;
}

template<size_t nfields, size_t D> inline
auto fieldOffsets( const BasisFunctionEvaluation<D>& shapes )
{
    auto offsets = std::array<size_t, nfields + 1> { 0 };

    for( size_t ifield = 0; ifield < nfields; ++ifield )
    { 
        offsets[ifield + 1] = offsets[ifield] + shapes.ndof( ifield );
    }

    return offsets;
}

} // mlhp

#endif // MLHP_CORE_BASISEVALUATION_IMPL_HPP
