// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_IMPLICIT_HPP
#define MLHP_CORE_IMPLICIT_HPP

#include "mlhp/core/alias.hpp"
#include "mlhp/core/coreexport.hpp"

namespace mlhp::implicit
{

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> sphere( std::array<double, D> origin, double radius );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> ellipsoid( std::array<double, D> origin,
                               std::array<double, D> radii );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> cube( std::array<double, D> x1,
                          std::array<double, D> x2 );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> cube( spatial::BoundingBox<D> bounds );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> halfspace( std::array<double, D> origin,
                               std::array<double, D> outwardNormal );

//! sign == true -> right side, sign == false -> left side
template<size_t D> MLHP_EXPORT
ImplicitFunction<D> halfspace( size_t axis, 
                               double offset = 0.0, 
                               bool sign = true );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> threshold( const spatial::ScalarFunction<D>& function, 
                               double threshold = 0.0, bool sign = true );

//! Extrude using interval
template<size_t D> MLHP_EXPORT
ImplicitFunction<D + 1> extrude( const ImplicitFunction<D>& function,
                                 double z1, double z2, size_t axis = D );

//! Extrude infinitely
template<size_t D> MLHP_EXPORT
ImplicitFunction<D + 1> extrude( const ImplicitFunction<D>& function,
                                 size_t axis = D );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> clip( const ImplicitFunction<D>& function,
                          std::array<double, D> origin,
                          std::array<double, D> outwardNormal );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> clip( const ImplicitFunction<D>& function,
                          size_t axis, 
                          double offset = 0.0, 
                          bool sign = true );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> invert( const ImplicitFunction<D>& function );

template<size_t D, typename... ImplicitFunctions >
ImplicitFunction<D> add( const ImplicitFunction<D>& function1,
                         const ImplicitFunctions&... functions );

template<size_t D, typename... ImplicitFunctions >
ImplicitFunction<D> intersect( const ImplicitFunction<D>& function1,
                               const ImplicitFunctions&... functions );

template<size_t D, typename... ImplicitFunctions >
ImplicitFunction<D> subtract( const ImplicitFunction<D>& function1,
                              const ImplicitFunctions&... functions );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> transform( const ImplicitFunction<D>& function,
                               const spatial::HomogeneousTransformation<D>& matrix );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D + 1> revolveSphereAroundPath( const TemporalPath<D>& path, double radius );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D - 1> sliceLast( const ImplicitFunction<D>& function, double value );

} // namespace mlhp::implicit

#include "mlhp/core/implicit_impl.hpp"

#endif // MLHP_CORE_IMPLICIT_HPP
