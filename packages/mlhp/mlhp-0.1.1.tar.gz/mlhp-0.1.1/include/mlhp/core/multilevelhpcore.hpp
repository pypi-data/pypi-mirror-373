// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_MULTILEVELHPCORE_HPP
#define MLHP_CORE_MULTILEVELHPCORE_HPP

#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/alias.hpp"
#include "mlhp/core/ndarray.hpp"
#include "mlhp/core/compilermacros.hpp"

namespace mlhp
{

template<size_t D> MLHP_EXPORT
void initializeTensorSpaceMasks( BooleanMask<D>& mask, std::array<size_t, D> polynomialDegrees );

template<size_t D> MLHP_EXPORT
void initializeTrunkSpaceMasks( BooleanMask<D>& mask, std::array<size_t, D> polynomialDegrees );

template<size_t D> MLHP_EXPORT
LinearizedTensorProductIndices<D> constructTensorProductIndices( const NCubeNeighboursVector<D>& neighbours,
                                                                 const std::vector<bool>& leafMask,
                                                                 const RefinementLevelVector& levels,
                                                                 const PolynomialDegreesVector<D>& polynomialDegrees,
                                                                 const InitialMaskProvider<D>& initialMaskProvider );

template<size_t D> MLHP_EXPORT
DofIndexVector generateLocationMaps( const TensorProductIndicesVector<D>& entries,
                                     const DofIndexVector& indices,
                                     const NCubeNeighboursVector<D>& neighbours,
                                     const RefinementLevelVector& levels );

template<size_t D> MLHP_EXPORT
TensorProductIndices<D> compressIndices( const TensorProductIndices<D>* begin,
                                         const TensorProductIndices<D>* end,
                                         std::vector<PolynomialDegree>& target );

template<size_t D> MLHP_EXPORT
void compressedTensorProduct( const PolynomialDegree* compressedIndices,
                              std::array<const double*, D> bases1D,
                              double scaling,
                              double* target );

} // mlhp

#endif // MLHP_CORE_MULTILEVELHPCORE_HPP
