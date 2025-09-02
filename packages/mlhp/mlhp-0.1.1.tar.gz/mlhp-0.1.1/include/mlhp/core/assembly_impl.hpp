// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_ASSEMBLY_IMPL_HPP
#define MLHP_CORE_ASSEMBLY_IMPL_HPP

#include "mlhp/core/partitioning.hpp"
#include "mlhp/core/algorithm.hpp"

namespace mlhp
{
namespace detail
{

template<size_t D>
struct DomainIntegralOptionalParameters
{
    template<typename T>
    using ConstOptional = std::pair<const T*, std::unique_ptr<const T>>;

    template<typename Instantiate, typename T, typename...Args>
    auto& returnExistingOrCreate( ConstOptional<T>& member, Args&&... args )
    {
        if( member.first )
        {
            return *member.first;
        }
        else if( member.second )
        {
        return *member.second;
        }
        else
        {
            member.second = std::make_unique<Instantiate>( std::forward<Args>( args )... );

            return *member.second;
        }
    }

    void set( const AbsQuadrature<D>& integrationPartitioner )
    {
        partitioner_.first = &integrationPartitioner;
    }

    void set( QuadratureOrderDeterminor<D>&& determinor )
    {
        determinor_.second = std::make_unique<QuadratureOrderDeterminor<D>>( std::move( determinor ) );
    }

    void set( const QuadratureOrderDeterminor<D>& determinor )
    {
        determinor_.first = &determinor;
    }

    void set( DofIndicesValuesPair&& boundaryDofs )
    {
        boundaryDofs_.second = std::make_unique<DofIndicesValuesPair>( std::move( boundaryDofs ) );
    }

    void set( const DofIndicesValuesPair& boundaryDofs )
    {
        boundaryDofs_.first = &boundaryDofs;
    }

    auto& partitioner( )
    {
        return returnExistingOrCreate<StandardQuadrature<D>>( partitioner_ );
    }

    auto& orderDeterminor( )
    {
        auto defaultDeterminor = relativeQuadratureOrder<D>( 1 );

        return returnExistingOrCreate<QuadratureOrderDeterminor<D>>( determinor_, defaultDeterminor );
    }

    auto& boundaryDofs( )
    {
        return returnExistingOrCreate<DofIndicesValuesPair>( boundaryDofs_ );
    }

    // Optional parameters
    ConstOptional<AbsQuadrature<D>> partitioner_;
    ConstOptional<QuadratureOrderDeterminor<D>> determinor_;
    ConstOptional<DofIndicesValuesPair> boundaryDofs_;
};

} // namespace detail

template<size_t D, typename... Args> inline
void integrateOnDomain( const AbsBasis<D>& basis,
                        const DomainIntegrand<D>& integrand,
                        const AssemblyTargetVector& globalTargets,
                        const Args&... args )
{
    detail::DomainIntegralOptionalParameters<D> parameters;

    [[maybe_unused]] std::initializer_list<int> tmp{ ( parameters.set( args ), 0 )... };

    integrateOnDomain( basis, integrand, globalTargets,
                       parameters.partitioner( ),
                       parameters.orderDeterminor( ),
                       parameters.boundaryDofs( ) );
}

template<size_t D, typename... Args> inline
void integrateOnDomain( const MultilevelHpBasis<D>& basis0,
                        const MultilevelHpBasis<D>& basis1,
                        const BasisProjectionIntegrand<D>& integrand,
                        const AssemblyTargetVector& globalTargets,
                        const Args&... args )
{
    detail::DomainIntegralOptionalParameters<D> parameters;

    [[maybe_unused]] std::initializer_list<int> tmp{ ( parameters.set( args ), 0 )... };

    integrateOnDomain( basis0, basis1, integrand, globalTargets,
                       parameters.partitioner( ),
                       parameters.orderDeterminor( ),
                       parameters.boundaryDofs( ) );
}

template<typename MatrixType> inline
MatrixType allocateMatrix( const LinearizedLocationMaps& maps,
                           DofIndex ndof )
{
    return allocateMatrix<MatrixType>( maps, { }, ndof );
}

template<typename MatrixType> inline
MatrixType allocateMatrix( const LocationMapRange& locationMaps,
                           DofIndex ndof )
{
    return allocateMatrix<MatrixType>( locationMaps, { }, ndof );
}

template<typename MatrixType, size_t D> inline
MatrixType allocateMatrix( const AbsBasis<D>& basis,
                           const DofIndexVector& boundaryDofs )
{
    auto range = utilities::makeIndexRangeFunction( basis.nelements( ), basis, &AbsBasis<D>::locationMap );

    return allocateMatrix<MatrixType>( range, boundaryDofs, basis.ndof( ) );
}

template<typename MatrixType, size_t D> inline
MatrixType allocateMatrix( const AbsBasis<D>& basis )
{
    return allocateMatrix<MatrixType>( basis, { } );
}

template<typename MatrixType> inline
MatrixType allocateMatrix( const LocationMapVector& locationMaps,
                           DofIndex ndof )
{
    return allocateMatrix<MatrixType>( locationMaps, { }, ndof );
}

template<size_t D> inline
linalg::UnsymmetricSparseMatrix makeAdditiveSchwarzPreconditioner( const linalg::UnsymmetricSparseMatrix& matrix,
                                                                   const AbsBasis<D>& basis,
                                                                   const DofIndexVector& dirichletDofs )
{
    std::function locationMapWrapper = [&]( size_t ielement, LocationMap& locationMap )
    { 
        basis.locationMap( static_cast<CellIndex>( ielement ), locationMap );
    };
    
    auto ngroups = static_cast<size_t>( basis.nelements( ) );
    auto groupGenerator = utilities::makeIndexRangeFunction( ngroups, locationMapWrapper );

    return makeAdditiveSchwarzPreconditioner( matrix, groupGenerator, dirichletDofs, basis.ndof( ) );
}

} // mlhp

#endif // MLHP_CORE_ASSEMBLY_IMPL_HPP
