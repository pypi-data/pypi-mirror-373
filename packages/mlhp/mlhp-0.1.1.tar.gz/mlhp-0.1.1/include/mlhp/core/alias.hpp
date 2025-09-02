// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_ALIAS
#define MLHP_CORE_ALIAS

#include "mlhp/core/forwarddeclare.hpp"
#include "mlhp/core/config.hpp"

#include <vector>
#include <variant>
#include <cstdint>
#include <limits>
#include <functional>
#include <memory>
#include <optional>
#include <any>

#include "ndarray.hpp"

namespace mlhp
{

// CellIndexType is defined in core/config.hpp
// DofIndexType is defined in core/config.hpp

using RefinementLevel = std::uint8_t;
using LocalPosition = std::uint8_t;
using PolynomialDegree = std::uint8_t;

template<typename Arithmetic> requires std::is_arithmetic_v<Arithmetic>
constexpr Arithmetic NoValue = std::numeric_limits<Arithmetic>::max( );

constexpr CellIndex NoCell = NoValue<CellIndex>;
constexpr DofIndex NoDof = NoValue<DofIndex>;
constexpr LocalPosition NoLocalPosition = NoValue<LocalPosition>;

using DofIndexVector = std::vector<DofIndex>;
using CellIndexVector = std::vector<CellIndex>;
using RefinementLevelVector = std::vector<RefinementLevel>;
using PolynomialDegreeVector = std::vector<PolynomialDegree>;

template<typename T, typename IndexType = size_t>
using LinearizedVectors = std::pair<std::vector<IndexType>, std::vector<T>>;

template<typename T>
using ReferenceVector = std::vector<std::reference_wrapper<T>>;

using LocationMap = DofIndexVector;
using LocationMapVector = std::vector<LocationMap>;
using LocationMapRange = utilities::IndexRangeFunction<void( CellIndex, LocationMap& )>;
using LinearizedLocationMaps = LinearizedVectors<DofIndex>;
using DofIndicesValuesPair = std::pair<DofIndexVector, std::vector<double>>;

template<size_t D> using PositionInParent = std::array<LocalPosition, D>;
template<size_t D> using PolynomialDegrees = std::array<PolynomialDegree, D>;
template<size_t D> using TensorProductIndices = std::array<PolynomialDegree, D>;

template<size_t D> using PositionInParentVector = std::vector<PositionInParent<D>>;
template<size_t D> using PolynomialDegreesVector = std::vector<std::array<size_t, D>>;
template<size_t D> using TensorProductIndicesVector = std::vector<TensorProductIndices<D>>;
template<size_t D> using ChildrenVector = std::vector<typename nd::EquallySizedStaticArray<CellIndex, D, 2>::type>;
template<size_t D> using NCubeNeighboursVector = std::vector<nd::StaticArray<CellIndex, D, 2>>;

using NeighboursVector = LinearizedVectors<std::pair<CellIndex, std::uint8_t>, CellIndex>;

template<size_t D> using LinearizedTensorProductIndices = std::pair<TensorProductIndicesVector<D>, DofIndexVector>;

template<size_t D> using OptionalCoordinates = std::optional<std::array<double, D>>;
template<size_t D> using CoordinateSpan = std::span<std::array<double, D>>;
template<size_t D> using CoordinateConstSpan = std::span<const std::array<double, D>>;
template<size_t D> using CoordinateGrid = std::array<std::vector<double>, D>;
template<size_t D> using CoordinateList = std::vector<std::array<double, D>>;
template<size_t D> using CoordinateVectors = std::array<std::vector<double>, D>;
template<size_t D, size_t N> using CoordinateArray = std::array<std::array<double, D>, N>;

template<size_t D> using CellLocalCoordinates = std::pair<CellIndex, std::array<double, D>>;
template<size_t D> using BackwardMapVector = std::vector<CellLocalCoordinates<D>>;
template<size_t D> using BackwardMapResult = std::optional<CellLocalCoordinates<D>>;

template<size_t D>
using RefinementFunction = std::function<bool( const MeshMapping<D>&, RefinementLevel level )>;

template<size_t D>
using InitialMaskProvider = std::function<void( BooleanMask<D> & mask, std::array<size_t, D> degrees )>;

using AnsatzTemplateVector = nd::DynamicArray<size_t, 3>;

template<size_t D> using ImplicitFunction = std::function<bool( std::array<double, D> xyz )>;

using RealFunction = std::function<double( double )>;
using RealFunctionWithDerivative = std::function<std::array<double, 2>( double )>;

template<size_t D>
using TemporalPath = std::function<std::array<double, D>( double t )>;

// CellIndex + local face index
using MeshCellFace = std::pair<CellIndex, size_t>;
using MeshCellFaces = std::vector<MeshCellFace>;

template<size_t D> using MeshSharedPtr = std::shared_ptr<AbsMesh<D>>;
template<size_t D> using MeshUniquePtr = std::unique_ptr<AbsMesh<D>>;
template<size_t D> using MeshConstSharedPtr = std::shared_ptr<const AbsMesh<D>>;
template<size_t D> using GridSharedPtr = std::shared_ptr<AbsGrid<D>>;
template<size_t D> using GridUniquePtr = std::unique_ptr<AbsGrid<D>>;
template<size_t D> using GridConstSharedPtr = std::shared_ptr<const AbsGrid<D>>;
template<size_t D> using HierarchicalGridSharedPtr = std::shared_ptr<AbsHierarchicalGrid<D>>;
template<size_t D> using HierarchicalGridUniquePtr = std::unique_ptr<AbsHierarchicalGrid<D>>;
template<size_t D> using BasisSharedPtr = std::shared_ptr<AbsBasis<D>>;
template<size_t D> using BasisConstSharedPtr = std::shared_ptr<const AbsBasis<D>>;

template<size_t D>
using MultilevelHpBasisSharedPtr = std::shared_ptr<MultilevelHpBasis<D>>;

template<size_t D> using PolynomialDegreeDistributor = std::function<
    AnsatzTemplateVector( const AbsHierarchicalGrid<D>& grid, size_t nfields )>;

template<size_t D> using MultilevelHpBasisFactory = std::function<
    MultilevelHpBasisSharedPtr<D>( const HierarchicalGridSharedPtr<D>& grid, size_t nfields )>;

template<size_t D>
using MappingRange = utilities::IndexRangeFunction<std::array<double, D>( CellIndex, std::array<double, D> )>;

//! Creates backward mapping that can be accessed concurrently
template<size_t D>
using BackwardMappingFactory = std::function<std::unique_ptr<AbsBackwardMapping<D>>( )>;

//! Result (outer to inner): Coordinate -> diff order -> shape function index
using PolynomialBasis = std::function<void( size_t polynomialDegree,
                                            size_t maxDiffOrder,
                                            double coordinate,
                                            double* targetMemory )>;

using QuadraturePoints1D = std::array<std::vector<double>, 2>;
using QuadratureRule1D = std::function<void( size_t order, QuadraturePoints1D& target )>;

template<size_t D>
using QuadratureOrderDeterminor = std::function<std::array<size_t, D>( CellIndex element, std::array<size_t, D> maxDegrees )>;

enum class DiffOrders : int
{
    NoShapes = -1,
    Shapes = 0,
    FirstDerivatives = 1,
    SecondDerivatives = 2
};

enum class AssemblyType : size_t 
{ 
    Scalar = 0, 
    Vector = 1, 
    UnsymmetricMatrix = 2, 
    SymmetricMatrix = 3 
};

using AssemblyTarget = std::variant
<
    std::reference_wrapper<double>,
    std::reference_wrapper<std::vector<double>>,
    std::reference_wrapper<linalg::UnsymmetricSparseMatrix>,
    std::reference_wrapper<linalg::SymmetricSparseMatrix>
>;

using AssemblyTargetVector = std::vector<AssemblyTarget>;
using AssemblyTypeVector = std::vector<AssemblyType>;

template<size_t D>
using ResolutionDeterminor = std::function<std::array<size_t, D>( const MeshMapping<D>& mapping )>;

template<size_t D>
using CellMeshCreator = std::function<bool( const MeshMapping<D>& mapping,
                                            std::array<std::vector<double>, D>& localCoordinates,
                                            std::vector<std::int64_t>& connectivity,
                                            std::vector<std::int64_t>& offsets,
                                            std::vector<std::int8_t>& vtkTypes,
                                            std::any& cache )>;

template<size_t D>
using CoordinatesWithScalar = std::pair<std::array<double, D>, double>;

// Row major matrix of mapping derivatives
// For example if we map from (r0, r1) --> (x0, x1, x2), then J 
// is a 3 x 2 matrix with J_ij = dx_i / dr_j
template<size_t GlobalDim, size_t LocalDim = GlobalDim>
using JacobianMatrix = std::array<double, GlobalDim * LocalDim>;

template<size_t G, size_t L = G>
using CoordinatesWithMatrix = std::pair<std::array<double, G>, JacobianMatrix<G, L>>;

template<size_t D = 3>
using Triangulation = SimplexMesh<D, 2>;

template<size_t D = 2>
using LineSegments = SimplexMesh<D, 1>;

namespace map
{

enum class Type : size_t
{
    NCube = 1,  // Line, square, cube, ...
    Simplex = 2 // Line, triangle, tetrahedron, ...
};

} // map

using CellType = map::Type;

} // mlhp

namespace mlhp::spatial
{

template<size_t L, size_t G = std::dynamic_extent>
struct VectorFunction;

//! Is this a good idea?
template<size_t D, typename... Args>
using ScalarFunction = std::function<double( std::array<double, D>, Args... )>;

template<size_t D> 
using ParameterFunction = std::function<std::array<double, D>( double )>;

template<size_t D> 
using BoundingBox = std::array<std::array<double, D>, 2>;

template<size_t D>
using Triangle = std::array<std::array<double, D>, 3>;

} // mlhp::spatial

namespace mlhp::kdtree 
{ 

template<size_t D>
using ObjectProvider = utilities::IndexRangeFunction<spatial::BoundingBox<D>( 
    size_t iobject, const spatial::BoundingBox<D>& bounds )>;

}

namespace mlhp::linalg
{

using SparseIndex = DofIndex;
using SparsePtr = std::size_t;

using SparseSolver = std::function<std::vector<double>( const AbsSparseMatrix& matrix,
                                                        const std::vector<double>& rhs )>;

using LinearOperator = std::function<void( const double* vector, double* target, std::uint64_t n )>;

} // mlhp::linalg

#endif
