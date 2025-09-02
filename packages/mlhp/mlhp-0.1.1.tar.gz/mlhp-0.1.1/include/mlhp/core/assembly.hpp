// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_ASSEMBLY_HPP
#define MLHP_CORE_ASSEMBLY_HPP

#include "mlhp/core/sparse.hpp"
#include "mlhp/core/utilities.hpp"
#include "mlhp/core/memory.hpp"
#include "mlhp/core/alias.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/partitioning.hpp"

#include <variant>

namespace mlhp
{

/*! 
 *  Convenience helper for integrateOnDomain below that automatically orders 
 *  input parameters and assigns default values to parameters without argument. 
 *  
 *  Parameter                    | Default value
 *  -----------------------------|-----------------
 *  Integration partitioner      | StandardQuadrature<D>
 *  Integration order determinor | Lambda returning p + 1
 *  Dirichlet boundary dofs      | Empty 
 */
template<size_t D, typename... Args>
void integrateOnDomain( const AbsBasis<D>& basis,
                        const DomainIntegrand<D>& integrand,
                        const AssemblyTargetVector& globalTargets,
                        const Args&... args );

// Linear system integral on domain with all parameters.
template<size_t D> MLHP_EXPORT
void integrateOnDomain( const AbsBasis<D>& basis,
                        const DomainIntegrand<D>& integrand,
                        const AssemblyTargetVector& globalTargets,
                        const AbsQuadrature<D>& quadrature,
                        const QuadratureOrderDeterminor<D>& orderDeterminor,
                        const DofIndicesValuesPair& boundaryDofs,
                        size_t chunksize = 1 );

/*!
 *  Convenience helper for integrateOnDomain below that automatically orders
 *  input parameters and assigns default values to parameters without argument.
 *  
 *  Parameter                    | Default value
 *  -----------------------------|-----------------
 *  Integration partitioner      | StandardQuadrature<D>
 *  Integration order determinor | Lambda returning p + 1
 *  Dirichlet boundary dofs      | Empty
 */
template<size_t D, typename... Args>
void integrateOnDomain( const MultilevelHpBasis<D>& basis0,
                        const MultilevelHpBasis<D>& basis1,
                        const BasisProjectionIntegrand<D>& integrand,
                        const AssemblyTargetVector& globalTargets,
                        const Args&... args );

// Linear system integral on domain with two bases.
template<size_t D> MLHP_EXPORT
void integrateOnDomain( const MultilevelHpBasis<D>& basis0,
                        const MultilevelHpBasis<D>& basis1,
                        const BasisProjectionIntegrand<D>& integrand,
                        const AssemblyTargetVector& globalTargets,
                        const AbsQuadrature<D>& quadrature,
                        const QuadratureOrderDeterminor<D>& orderDeterminor,
                        const DofIndicesValuesPair& boundaryDofs,
                        size_t chunksize = 1 );

template<size_t D> MLHP_EXPORT
void integrateOnSurface( const AbsBasis<D>& basis,
                         const SurfaceIntegrand<D>& integrand,
                         const AbsQuadratureOnMesh<D>& generator,
                         const AssemblyTargetVector& globalTargets,
                         const DofIndicesValuesPair& boundaryDofs = { { }, { } },
                         size_t chunksize = 1 );

template<typename MatrixType> MLHP_EXPORT
MatrixType allocateMatrix( const LinearizedLocationMaps& dofs,
                           const DofIndexVector& boundaryDofs,
                           DofIndex ndof = NoDof );

template<typename MatrixType>
MatrixType allocateMatrix( const LinearizedLocationMaps& maps,
                           DofIndex ndof = NoDof );

template<typename MatrixType> MLHP_EXPORT
MatrixType allocateMatrix( const LocationMapRange& locationMaps,
                           const DofIndexVector& boundaryDofs,
                           DofIndex ndof = NoDof );

template<typename MatrixType>
MatrixType allocateMatrix( const LocationMapRange& locationMaps,
                           DofIndex ndof = NoDof );

template<typename MatrixType> MLHP_EXPORT
MatrixType allocateMatrix( const LocationMapVector& locationMaps,
                           const DofIndexVector& boundaryDofs,
                           DofIndex ndof = NoDof );

template<typename MatrixType>
MatrixType allocateMatrix( const LocationMapVector& locationMaps,
                           DofIndex ndof = NoDof );

template<typename MatrixType, size_t D>
MatrixType allocateMatrix( const AbsBasis<D>& basis,
                           const DofIndexVector& boundaryDofs );

template<typename MatrixType, size_t D>
MatrixType allocateMatrix( const AbsBasis<D>& basis );

//! Allocate sparse matrix without constructing sparsity pattern
template<typename MatrixType> MLHP_EXPORT
MatrixType allocateMatrix( size_t size1, 
                           size_t size2, 
                           linalg::SparsePtr nentries );

template<size_t D> MLHP_EXPORT
std::vector<double> projectOnto( const AbsBasis<D>& basis,
                                 const spatial::ScalarFunction<D>& function );

template<size_t D> MLHP_EXPORT
std::vector<double> projectOnto( const AbsBasis<D>& basis,
                                 const spatial::ScalarFunction<D>& function,
                                 const linalg::SparseSolver& solver );

template<size_t D> MLHP_EXPORT
std::vector<double> projectOnto( const AbsBasis<D>& basis,
                                 const spatial::VectorFunction<D>& function );

template<size_t D> MLHP_EXPORT
std::vector<double> projectOnto( const AbsBasis<D>& basis,
                                 const spatial::VectorFunction<D>& function,
                                 const linalg::SparseSolver& solver );

template<size_t D> MLHP_EXPORT
std::vector<double> projectOnto( const MultilevelHpBasis<D>& basis0,
                                 const MultilevelHpBasis<D>& basis1,
                                 const std::vector<double>& dofs0 );

template<size_t D> MLHP_EXPORT
std::vector<double> projectOnto( const MultilevelHpBasis<D>& basis0,
                                 const MultilevelHpBasis<D>& basis1,
                                 const std::vector<double>& dofs0,
                                 const linalg::SparseSolver& solver );

template<size_t D, typename MatrixType> MLHP_EXPORT
std::vector<double> projectOnto( const MultilevelHpBasis<D>& basis0,
                                 const MultilevelHpBasis<D>& basis1,
                                 const std::vector<double>& dofs0,
                                 MatrixType& matrix );

template<size_t D, typename MatrixType> MLHP_EXPORT
std::vector<double> projectOnto( const MultilevelHpBasis<D>& basis0,
                                 const MultilevelHpBasis<D>& basis1,
                                 const std::vector<double>& dofs0,
                                 MatrixType& matrix,
                                 const linalg::SparseSolver& solver );


template<size_t D> MLHP_EXPORT
std::vector<std::vector<double>> projectDerivatives( const AbsBasis<D>& basis,
                                                     std::span<const double> dofs,
                                                     std::span<const std::array<size_t, D>> diffIndices,
                                                     const AbsQuadrature<D>& quadrature,
                                                     const linalg::SparseSolver& solver,
                                                     const spatial::ScalarFunction<D>& weight =
                                                          spatial::constantFunction<D>( 1.0 ) );

template<size_t D> MLHP_EXPORT
std::array<std::vector<double>, D> projectGradient( const AbsBasis<D>& basis,
                                                    const std::vector<double>& dofs,
                                                    const AbsQuadrature<D>& quadrature,
                                                    const linalg::SparseSolver& solver,
                                                    const spatial::ScalarFunction<D>& weight =
                                                        spatial::constantFunction<D>( 1.0 ) );

using AssemblyKernel = std::function<void( const AlignedDoubleVectors& localTargets,
                                           const LocationMap& locationMap,
                                           std::vector<size_t>& sortedIndices )>;

// Create function for assembling local systems into global targets. Ndof includes Dirichlet dofs.
MLHP_EXPORT
AssemblyKernel makeAssemblyKernel( const AssemblyTargetVector& globalTargets,
                                   const AssemblyTypeVector& localTypes,
                                   const DofIndicesValuesPair& boundaryDofs,
                                   DofIndex ndofAll );

// Resize local dense assembly targets and set them to zero.
MLHP_EXPORT
void initializeLocalAssemblyTargets( AlignedDoubleVectors& targets,
                                     const AssemblyTypeVector& types,
                                     size_t ndofElement );

template<size_t D>
linalg::UnsymmetricSparseMatrix makeAdditiveSchwarzPreconditioner( const linalg::UnsymmetricSparseMatrix& matrix,
                                                                   const AbsBasis<D>& basis,
                                                                   const DofIndexVector& dirichletDofs = { } );

} // mlhp

#include "mlhp/core/assembly_impl.hpp"

#endif // MLHP_CORE_ASSEMBLY_HPP
