// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/mapping.hpp"

namespace mlhp
{
namespace spatial
{
namespace
{

template<size_t D>
std::array<double, D> inverseDiagonal( const JacobianMatrix<D, D>& J )
{
    std::array<double, D> diagonal;

    for( size_t axis = 0; axis < D; ++axis )
    {
        diagonal[axis] = 1.0 / J[axis * D + axis];
    }

    return diagonal;
}

} // namespace
} // namespace spatial

namespace 
{

template<size_t D>
void scaleFirstDerivatives( BasisFunctionEvaluation<D>& shapes,
                            std::array<double, D> factors )
{
    for( size_t ifield = 0; ifield < shapes.nfields( ); ++ifield )
    {
        auto dN = shapes.noalias( ifield, 1 );
        auto ndofpadded = shapes.ndofpadded( ifield );

        for( size_t axis = 0; axis < D; ++axis )
        {
            for( size_t dof = 0; dof < ndofpadded; ++dof )
            {
                dN[dof] *= factors[axis];
            }

            dN += ndofpadded;

        } // for axis
    } // for ifield
}

template<size_t D>
void transformFirstDerivatives( BasisFunctionEvaluation<D>& shapes,
                                const JacobianMatrix<D>& invJ )
{

    for( size_t ifield = 0; ifield < shapes.nfields( ); ++ifield )
    {
        auto ndof = shapes.ndof( ifield );
        auto ndofpadded = shapes.ndofpadded( ifield );

        auto dNspan = std::span( shapes.get( ifield, 1 ), D * ndofpadded );
        auto dN = linalg::adapter( dNspan, ndofpadded );
        auto inv = linalg::adapter( invJ, D );

        // Compute dNdx = inv(J)^T * dNdr
        for( size_t jdof = 0; jdof < ndof; ++jdof )
        {
            auto dNdx = std::array<double, D> { };

            for( size_t iaxis = 0; iaxis < D; ++iaxis )
            {
                for( size_t kaxis = 0; kaxis < D; ++kaxis )
                {
                    dNdx[iaxis] += inv( kaxis, iaxis ) * dN( kaxis, jdof );
                }
            }

            for( size_t iaxis = 0; iaxis < D; ++iaxis )
            {
                dN( iaxis, jdof ) = dNdx[iaxis];
            }
        } // for idof
    } // for ifield
}

template<size_t D>
void scaleSecondDerivatives( BasisFunctionEvaluation<D>& shapes,
                             std::array<double, D> factors )
{
    for( size_t ifield = 0; ifield < shapes.nfields( ); ++ifield )
    {
        auto ddN = shapes.noalias( ifield, 2 );
        auto ndofpadded = shapes.ndofpadded( ifield );

        constexpr auto diffindices = diff::indices<D, 2>( );

        for( auto indices : diffindices )
        {
            double factor = 1.0;

            for( size_t axis = 0; axis < D; ++axis )
            {
                factor *= utilities::integerPow( factors[axis], indices[axis] );
            }

            for( size_t dof = 0; dof < ndofpadded; ++dof )
            {
                ddN[dof] *= factor;

            } // dof

            ddN += ndofpadded;

        } // for diff indices
    } // for ifield
}

} // namespace

template<size_t D>
double mapBasisEvaluation( BasisFunctionEvaluation<D>& shapes,
                           const AbsMapping<D>& mapping )
{
    auto maxdifforder = shapes.maxdifforder( );
    auto rst = shapes.rst( );

    if( maxdifforder == 0 )
    {
        auto [xyz, detJ] = map::withDetJ( mapping, rst );

        shapes.setXyz( xyz );

        return detJ;
    }
    else
    {
        MLHP_CHECK_DBG( maxdifforder <= 2, "Invalid diff order." );

        auto [xyz, J, detJ] = map::withJDetJ( mapping, rst );

        shapes.setXyz( xyz );

        if( spatial::isDiagonal<D>( J ) )
        {
            auto factors = spatial::inverseDiagonal<D>( J );
            
            scaleFirstDerivatives( shapes, factors );

            if( maxdifforder >= 2 )
            {
                scaleSecondDerivatives( shapes, factors );
            }
        }
        else
        {
            auto invJ = J;
            auto p = std::array<size_t, D> { };

            linalg::invert( J, p, invJ );

            transformFirstDerivatives( shapes, invJ );

            MLHP_CHECK( maxdifforder < 2, "Mapping second derivatives "
                "of basis functions not implemented." );

            // First derivatives: Multiply with inverse jacobian
            // Second derivatives from Nils thesis page 69: 
            //     ddNddx = J^-T * (ddNddr - dNdr * H) * J^-1
            //     DxD = DxD * ( DxD - Dx1 * DxDxD) * DxD
            //     (but ddNddr and H are symmetric, so they 
            //     can be linearized into 6x1, I think)
        }

        return detJ;
    }
}

template<size_t D> 
size_t fieldOffset( const BasisFunctionEvaluation<D>& shapes, size_t ifield )
{
    auto offset = size_t { 0 };

    for( size_t jfield = 0; jfield < ifield; ++jfield )
    {
        offset += shapes.ndof( jfield );
    }

    return offset;
}

namespace
{

//! Evaluate solution for the given diff order and field index into target memory.
template<bool singleComponent, size_t D>
void internalEvaluateSolution( const BasisFunctionEvaluation<D>& shapes,
                               std::span<const DofIndex> locationMap,
                               std::span<const double> dofs,
                               std::span<double> target,
                               size_t difforder,
                               size_t icomponent,
                               size_t ifield )
{
    MLHP_CHECK( difforder <= shapes.maxdifforder( ), "Invalid diff order." );
    MLHP_CHECK( ifield <= shapes.nfields( ), "Invalid diff order." );

    auto map = locationMap.data( ) + fieldOffset( shapes, ifield );
    auto ncomponents = singleComponent ? size_t { 1 } : shapes.ncomponents( difforder );

    MLHP_CHECK( target.size( ) >= ncomponents, "Invalid target size." );

    for( size_t axis = 0; axis < ncomponents; ++axis )
    {
        target[axis] = 0.0;
    }

    auto ndof = shapes.ndof( ifield );
    auto ndofpadded = shapes.ndofpadded( ifield );
    auto N = shapes.noalias( ifield, difforder );

    for( size_t idof = 0; idof < ndof; ++idof)
    {
        auto dof = dofs[map[idof]];

        if constexpr( singleComponent )
        {
            target[0] += N[icomponent * ndofpadded + idof] * dof;
        }
        else
        {
            for( size_t axis = 0; axis < ncomponents; ++axis )
            {
                target[axis] += N[axis * ndofpadded + idof] * dof;
            }
        }
    }
}

} // namespace

//! Evaluate solution for the given diff order and field index into target memory.
template<size_t D>
void evaluateSolution( const BasisFunctionEvaluation<D>& shapes,
                       std::span<const DofIndex> locationMap,
                       std::span<const double> dofs,
                       std::span<double> target,
                       size_t difforder,
                       size_t ifield )
{
    internalEvaluateSolution<false>( shapes, locationMap, dofs, target, difforder, 0, ifield );
}

template<size_t D>
void evaluateSolution( const BasisFunctionEvaluation<D>& shapes,
                       std::span<const DofIndex> locationMap,
                       std::span<const double> dofs,
                       std::span<double> target,
                       size_t difforder,
                       size_t icomponent,
                       size_t ifield )
{
    internalEvaluateSolution<true>( shapes, locationMap, dofs, target, difforder, icomponent, ifield );
}

template<size_t D>
void evaluateSolutions( const BasisFunctionEvaluation<D>& shapes,
                        std::span<const DofIndex> locationMap,
                        std::span<const double> dofs,
                        std::span<double> target,
                        size_t difforder )
{
    MLHP_CHECK( difforder <= shapes.maxdifforder( ), "Invalid diff order." );

    auto map = locationMap.data( );
    auto nfields = shapes.nfields( );
    auto ncomponents = shapes.ncomponents( difforder );

    MLHP_CHECK( target.size( ) >= ncomponents * nfields, "Invalid target size." );

    for( size_t ifield = 0; ifield < nfields; ++ifield )
    {
        for( size_t axis = 0; axis < ncomponents; ++axis )
        {
            target[ifield * ncomponents + axis] = 0.0;
        }

        auto ndof = shapes.ndof( ifield );
        auto ndofpadded = shapes.ndofpadded( ifield );
        auto N = shapes.noalias( ifield, difforder );

        for( size_t idof = 0; idof < ndof; ++idof)
        {
            auto dof = dofs[map[idof]];

            for( size_t axis = 0; axis < ncomponents; ++axis )
            {
                target[ifield * ncomponents + axis] += N[axis * ndofpadded + idof] * dof;
            }
        }

        map += ndof;
    }
}

#define MLHP_INSTANTIATE_DIM( D )                                     \
                                                                      \
    template MLHP_EXPORT                                              \
    double mapBasisEvaluation( BasisFunctionEvaluation<D>& shapes,    \
                               const AbsMapping<D>& mapping );        \
                                                                      \
    template MLHP_EXPORT                                              \
    size_t fieldOffset( const BasisFunctionEvaluation<D>& shapes,     \
                        size_t ifield );                              \
                                                                      \
    template MLHP_EXPORT                                              \
    void evaluateSolution( const BasisFunctionEvaluation<D>& shapes,  \
                           std::span<const DofIndex> locationMap,     \
                           std::span<const double> dofs,              \
                           std::span<double> target,                  \
                           size_t difforder,                          \
                           size_t ifield );                           \
                                                                      \
    template MLHP_EXPORT                                              \
    void evaluateSolution( const BasisFunctionEvaluation<D>& shapes,  \
                           std::span<const DofIndex> locationMap,     \
                           std::span<const double> dofs,              \
                           std::span<double> target,                  \
                           size_t difforder,                          \
                           size_t icomponent,                         \
                           size_t ifield );                           \
                                                                      \
    template MLHP_EXPORT                                              \
    void evaluateSolutions( const BasisFunctionEvaluation<D>& shapes, \
                            std::span<const DofIndex> locationMap,    \
                            std::span<const double> dofs,             \
                            std::span<double> target,                 \
                            size_t difforder );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // mlhp
