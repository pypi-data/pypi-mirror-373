// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_FORWARDDECLARE_HPP
#define MLHP_CORE_FORWARDDECLARE_HPP

#include <cstddef>
#include <cstdint>

namespace mlhp
{

template<size_t D> class AbsMesh;
template<size_t D> class AbsBackwardMapping;
template<size_t D> class AbsGrid;
template<size_t D> class CartesianGrid;
template<size_t D> class AbsHierarchicalGrid;
template<size_t D> class RefinedGrid;

template<size_t D> class AbsBasis;
template<size_t D> class BasisFunctionEvaluation;
template<size_t D> class MultilevelHpBasis;
template<size_t D> class AbsQuadrature;
template<size_t D> class AbsQuadratureOnMesh;
template<size_t D> class DomainIntegrand;
template<size_t D> class BasisProjectionIntegrand;
template<size_t D> class AbsQuadratureOnMesh;
template<size_t D> class SurfaceIntegrand;
template<size_t D> struct KinematicEquation;
template<size_t D> struct ConstitutiveEquation;
template<size_t D> struct CellProcessor;
template<size_t D> struct ElementProcessor;

template<size_t G, size_t L = G> class AbsMapping;
template<size_t G, size_t L = G> struct MeshMapping;

template<size_t G, size_t L>
struct SimplexMesh;

template<size_t D> class KdTree;

struct QuadraturePointCache;

}

namespace mlhp::spatial
{

template<size_t D> struct HomogeneousTransformation;

}

namespace mlhp::nd
{

template<typename T, size_t... Shape>
class StaticArray;

template<typename T, size_t D>
class DynamicArray;

}

namespace mlhp::utilities
{

template<typename FunctionType>
struct IndexRangeFunction;

} 

namespace mlhp::linalg
{

class AbsSparseMatrix;
class SymmetricSparseMatrix;
class UnsymmetricSparseMatrix;

struct SymmetricDenseMatrix;
struct UnsymmetricDenseMatrix;

}

#endif // MLHP_CORE_FORWARDDECLARE_HPP
