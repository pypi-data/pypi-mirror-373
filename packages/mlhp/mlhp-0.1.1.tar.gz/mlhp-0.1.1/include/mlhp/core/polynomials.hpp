// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_POLYNOMIALS_HPP
#define MLHP_CORE_POLYNOMIALS_HPP

#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/alias.hpp"

#include <array>
#include <functional>
#include <span>

namespace mlhp::polynomial
{

template<size_t MaxDiffOrder> MLHP_EXPORT
void integratedLegendre( size_t ansatzOrder,
                         double coordinate,
                         std::array<double*, MaxDiffOrder + 1> target );

// All shapes of one diff order contiguous
template<size_t MaxDiffOrder> MLHP_EXPORT
void integratedLegendre( size_t ansatzOrder,
                         double coordinate,
                         double* target );

// Same as above but with if statements
MLHP_EXPORT
void integratedLegendre( size_t ansatzOrder,
                         size_t maxDiffOrder,
                         double coordinate,
                         double* target );

// Single Lagrange polynomial
MLHP_EXPORT
double lagrange( std::span<const double> points, size_t i, double x, size_t diff );

// Lagrange basis at multiple evaluation coordinates
MLHP_EXPORT 
void lagrange( size_t ansatzOrder,
               size_t numberOfEvaluationCoordinate,
               const double* evaluationCoordinates,
               const double* lagrangePoints,
               double* target );

// Compute B-Spline on knot span [ispan, ispan + 1]
MLHP_EXPORT
void bspline( std::span<const double> U,
              size_t degree, 
              size_t maxdiff, 
              size_t ispan,
              double x,
              std::span<double> target );

//! Pass temporary storage with size (p + 1) * (p + 5) for efficiency
MLHP_EXPORT
void bspline( std::span<const double> U,
              size_t degree,
              size_t maxdiff,
              size_t ispan,
              double x,
              std::span<double> target,
              std::span<double> tmp );

template<size_t D> MLHP_EXPORT MLHP_PURE
std::array<double, D> deBoor( std::span<const double> knotVector,
                              const CoordinateList<D>& controlPoints,
                              size_t degree, 
                              size_t ispan, 
                              double x );

MLHP_EXPORT MLHP_PURE
size_t findKnotSpan( std::span<const double> U, 
                     size_t npoints, 
                     size_t degree, 
                     double x );

//! p + 1 multiplicity on boundary positions, degree - continuity multiplicity inside
//! Appends to target, does not resize to zero.
MLHP_EXPORT
void openKnotVector( std::span<double> x, 
                     size_t degree, 
                     size_t continuity, 
                     std::vector<double>& target );

MLHP_EXPORT
PolynomialBasis makeIntegratedLegendreBasis( );

// If reorder is true, the end points are moved to first two indices: [-1.0, 1.0, ...]
MLHP_EXPORT
PolynomialBasis makeEquallySpacedLagrangeBasis( bool reorder = false );

// Cubic hermite polynomials on [0, 1]. Returns [f0, f1, f2, f3], 
// such that f0(0) = 1, f1'(0) = 1, f2(1) = 1, f3'(1) = 1.
MLHP_EXPORT
std::array<double, 4> cubicHermite( double t );

MLHP_EXPORT
std::array<double, 4> cubicHermiteDerivatives( double t );

// Linearly interpolate between P0 = (0, 0), P1 = (1, 0), and P2 = (0, 1) using
// N0(r, s) = (1 - r - s)
// N1(r, s) = r
// N2(r, s) = s
MLHP_EXPORT MLHP_PURE
std::array<double, 3> linearTriangle( std::array<double, 2> rs );

} // mlhp::polynomial

namespace mlhp::interpolation
{

enum class Extrapolate : int { Default = -1, Constant = 0, Linear = 1 };

MLHP_EXPORT
RealFunctionWithDerivative makeConstantInterpolation( const std::vector<double>& positions,
                                                      const std::vector<double>& values );

MLHP_EXPORT
RealFunctionWithDerivative makeCubicHermiteSpline( const std::vector<double>& positions,
                                                   const std::vector<double>& values,
                                                   const std::vector<double>& derivatives,
                                                   Extrapolate extrapolate = Extrapolate::Linear );

MLHP_EXPORT
RealFunctionWithDerivative makeLinearInterpolation( const std::vector<double>& positions,
                                                    const std::vector<double>& values,
                                                   Extrapolate extrapolate = Extrapolate::Linear );

MLHP_EXPORT
RealFunctionWithDerivative makeBSplineInterpolation( const std::vector<double>& positions,
                                                     const std::vector<double>& values,
                                                     size_t degree = 3,
                                                     Extrapolate extrapolate = Extrapolate::Linear );

template<size_t D> MLHP_EXPORT
spatial::ParameterFunction<D> makeBSpline( const CoordinateList<D>& controlPoints,
                                           std::span<const double> knotVector );

//! Different ways of defining knot spans for b-spline interpolation
template<size_t D> MLHP_EXPORT
std::vector<double> equidistantLocalCoordinates( const CoordinateList<D>& xyz );

template<size_t D> MLHP_EXPORT
std::vector<double> centripetralLocalCoordinates( const CoordinateList<D>& xyz );

MLHP_EXPORT
std::vector<double> averagedKnotVector( const std::vector<double>& localCoordinates, size_t degree );

template<size_t D> MLHP_EXPORT
CoordinateList<D> computeControlPoints( const CoordinateList<D>& xyzValues,
                                        std::span<const double> tvalues,
                                        std::span<const double> knotVector );

} // mlhp::interpolation

#endif // MLHP_CORE_POLYNOMIALS_HPP
