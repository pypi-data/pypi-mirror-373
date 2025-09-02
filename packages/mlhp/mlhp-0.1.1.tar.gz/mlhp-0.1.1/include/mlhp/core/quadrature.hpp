// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_QUADRATURE_HPP
#define MLHP_CORE_QUADRATURE_HPP

#include "mlhp/core/alias.hpp"
#include "mlhp/core/coreexport.hpp"

#include <array>
#include <vector>

namespace mlhp
{

MLHP_EXPORT
QuadraturePoints1D gaussLegendrePoints( size_t order );

MLHP_EXPORT
void gaussLegendrePoints( size_t order, QuadraturePoints1D& target );

MLHP_EXPORT
QuadraturePoints1D gaussLobattoPoints( size_t n );

MLHP_EXPORT
void gaussLobattoPoints( size_t n, QuadraturePoints1D& target );

MLHP_EXPORT
void gaussLobattoPoints( size_t n, std::span<double> x, std::span<double> w );

struct QuadraturePointCache
{
    std::vector<std::shared_ptr<QuadraturePoints1D>> data;
    QuadratureRule1D quadrature;
    
    MLHP_EXPORT
    QuadraturePointCache( ); // Use Gauss-Legendre

    MLHP_EXPORT
    QuadraturePointCache( const QuadratureRule1D& quadrature_ );

    MLHP_EXPORT
    const QuadraturePoints1D& operator() ( size_t order );
};

template<size_t D> MLHP_EXPORT
void tensorProductQuadrature( std::array<size_t, D> orders,
                              CoordinateGrid<D>& rst,
                              QuadraturePointCache& cache );

template<size_t D> MLHP_EXPORT
void tensorProductQuadrature( std::array<size_t, D> orders,
                              CoordinateGrid<D>& rst,
                              CoordinateGrid<D>& weightsGrid,
                              QuadraturePointCache& cache );

template<size_t D> MLHP_EXPORT
void tensorProductQuadrature( std::array<size_t, D> orders,
                              CoordinateGrid<D>& rst,
                              std::vector<double>& weights,
                              QuadraturePointCache& cache );

template<size_t D> MLHP_EXPORT
void tensorProductQuadrature( std::array<size_t, D> orders,
                              CoordinateList<D>& rst,
                              std::vector<double>& weights,
                              QuadraturePointCache& cache );

//! Gauss-Legendre tensor product collapsed into simplex
template<size_t D> MLHP_EXPORT
void simplexQuadrature( std::array<size_t, D> orders,
                        CoordinateList<D>& rst,
                        std::vector<double>& weights,
                        QuadraturePointCache& cache );

template<size_t D> MLHP_EXPORT
void simplexQuadrature( std::array<size_t, D> orders,
                        CoordinateVectors<D>& rst,
                        std::vector<double>& weights,
                        QuadraturePointCache& cache );

// Integrate triangle (0, 0), (1, 0), (0, 1) with weights 1/6 each
MLHP_EXPORT
void triangleTrapezoidalRule( CoordinateList<2>& coordinates,
                              std::vector<double>& weights );

} // mlhp 

#endif // MLHP_CORE_QUADRATURE_HPP
