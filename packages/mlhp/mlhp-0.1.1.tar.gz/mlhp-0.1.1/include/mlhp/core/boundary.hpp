// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_BOUNDARY_HPP
#define MLHP_CORE_BOUNDARY_HPP

#include <vector>
#include <array>

#include "mlhp/core/alias.hpp"
#include "mlhp/core/coreexport.hpp"

namespace mlhp::boundary
{

// For all dimensions
constexpr size_t left   = 0;
constexpr size_t right  = 1;
constexpr size_t front  = 2;
constexpr size_t back   = 3;
constexpr size_t bottom = 4;
constexpr size_t top    = 5;

MLHP_EXPORT
std::vector<size_t> allFaces( size_t D );

MLHP_EXPORT
size_t face( size_t axis, size_t side );

//MLHP_EXPORT

//! Dof mask with true entries if dof is active on one of the given faces
template<size_t D> MLHP_EXPORT
std::vector<bool> boundaryDofMask( const AbsBasis<D>& basis, 
                                   const MeshCellFaces& faces, 
                                   size_t ifield = 0 );

//! Indices of dofs active on one of the given faces
template<size_t D> MLHP_EXPORT
std::vector<DofIndex> boundaryDofIndices( const AbsBasis<D>& basis,
                                          const MeshCellFaces& faces,
                                          size_t ifield = 0 );

//! Generic function accepting a vector of cell faces
template<size_t D> MLHP_EXPORT
DofIndicesValuesPair boundaryDofs( const spatial::ScalarFunction<D>& function,
                                   const MeshCellFaces& faces,
                                   const AbsBasis<D>& basis,
                                   const QuadratureOrderDeterminor<D>& determinor,
                                   size_t ifield = 0 );

//! Single field component, with order determinor
template<size_t D> MLHP_EXPORT
DofIndicesValuesPair boundaryDofs( const spatial::ScalarFunction<D>& function,
                                   const AbsBasis<D>& basis,
                                   const std::vector<size_t>& faces,
                                   const QuadratureOrderDeterminor<D>& determinor,
                                   size_t ifield = 0 );

//! Single field Component, without order determinor
template<size_t D> MLHP_EXPORT
DofIndicesValuesPair boundaryDofs( const spatial::ScalarFunction<D>& function,
                                   const AbsBasis<D>& basis,
                                   const std::vector<size_t>& faces,
                                   size_t ifield = 0 );

//! Multiple field components
template<size_t D> MLHP_EXPORT
DofIndicesValuesPair boundaryDofs( const spatial::VectorFunction<D>& function,
                                   const AbsBasis<D>& basis,
                                   const std::vector<size_t>& faces,
                                   const QuadratureOrderDeterminor<D>& determinor =
                                       relativeQuadratureOrder<D>( 1 ) );

MLHP_EXPORT
DofIndicesValuesPair makeUnique( const DofIndicesValuesPair& dofs );

MLHP_EXPORT 
DofIndicesValuesPair combine( const std::vector<DofIndicesValuesPair>& boundaryDofs );

MLHP_EXPORT
std::vector<double> inflate( std::span<const double> interiorDofs,
                             const DofIndicesValuesPair& boundaryDofs );

MLHP_EXPORT
std::vector<double> inflate( std::span<const double> interiorDofs,
                             const DofIndicesValuesPair& boundaryDofs,
                             std::vector<double>& target );

// xyz coordinates: [x0, y0, z0, x1, y1, z1, ...], rst coordinates: [r0, s0, t0, r1, s1, t1, ...], cell indices: [4, 2, ...]
using CellAssociatedTriangles = std::tuple<std::vector<double>, std::vector<double>, std::vector<CellIndex>>;

MLHP_EXPORT
std::vector<CellAssociatedTriangles> triangulateFaces( const AbsMesh<3>& mesh, 
                                                       const std::vector<size_t>& faces );

template<size_t D>
class QuadratureOnMeshFaces : public AbsQuadratureOnMesh<D>
{
public:

    // Find all boundary cells for the given mesh
    MLHP_EXPORT
    QuadratureOnMeshFaces( const AbsMesh<D>& mesh,
                           const std::vector<size_t>& meshFaces,
                           const QuadratureOrderDeterminor<D>& order = relativeQuadratureOrder<D>( 1 ) );

    // Give specific cell faces
    MLHP_EXPORT
    QuadratureOnMeshFaces( const std::vector<MeshCellFace>& cellFaces,
                           const QuadratureOrderDeterminor<D>& order = relativeQuadratureOrder<D>( 1 ) );

    MLHP_EXPORT
    typename AbsQuadratureOnMesh<D>::AnyCache initialize( ) const override;

    // TODO: grid evaluation and either keep weights in local coordinates or pass xyz additionally
    MLHP_EXPORT
    void distribute( const MeshMapping<D>& mapping,
                     std::array<size_t, D> orders,
                     CoordinateList<D>& rst,
                     CoordinateList<D>& normals,
                     std::vector<double>& weights,
                     typename AbsQuadratureOnMesh<D>::AnyCache& cache ) const override;

private:
    std::vector<size_t> indices_;
    std::vector<size_t> faces_;
 
    QuadratureOrderDeterminor<D> order_;
    struct Cache;
};

} // namespace mlhp::boundary

#endif // MLHP_CORE_BOUNDARY_HPP
