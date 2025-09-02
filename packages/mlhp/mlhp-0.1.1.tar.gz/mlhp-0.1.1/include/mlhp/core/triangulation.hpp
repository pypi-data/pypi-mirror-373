// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_TRIANGULATION_HPP
#define MLHP_CORE_TRIANGULATION_HPP

#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/alias.hpp"
#include "mlhp/core/mesh.hpp"
#include "mlhp/core/partitioning.hpp"
#include "mlhp/core/kdtree.hpp"

namespace mlhp::marching
{

inline size_t bisectionDefault = 12;

}

namespace mlhp
{

// Inject dimension-dependent members to SimplexMesh
template<typename Derived> 
struct SimplexCRTP : utilities::DefaultVirtualDestructor { };

// 1D: add normal vectors since we can't determine normal direction from a point
template<> struct SimplexCRTP<SimplexMesh<1, 0>> : utilities::DefaultVirtualDestructor
{ 
    CoordinateList<1> normals; 
};

// 2D: add length function
template<size_t G> struct SimplexCRTP<SimplexMesh<G, 1>> 
{ 
    double length( ) const { return static_cast<const SimplexMesh<G, 1>*>( this )->measure( ); }
};

// 3D: add area function
template<size_t G> struct SimplexCRTP<SimplexMesh<G, 2>> 
{ 
    double area( ) const { return static_cast<const SimplexMesh<G, 2>*>( this )->measure( ); }
};

// E.g. 3D triangulation for G = 3, L = 2
template<size_t G, size_t L>
struct SimplexMesh final : public SimplexCRTP<SimplexMesh<G, L>>
{
    auto ncells( ) const { return cells.size( ); }
    auto nvertices( ) const { return vertices.size( ); }
    
    auto cellVertices( size_t icell ) const;
    auto cellNormal( size_t icell ) const requires ( G == L + 1 );

    //! Vector length is cell measure
    auto cellWeightedNormal( size_t icell ) const requires ( G == L + 1 );

    spatial::BoundingBox<G> boundingBox( ) const;
    spatial::BoundingBox<G> boundingBox( size_t icell ) const;

    MLHP_EXPORT MLHP_PURE
    double measure( ) const;

    size_t memoryUsage( ) const;

    std::vector<std::array<double, G>> vertices;
    std::vector<std::array<size_t, L + 1>> cells;
};

//! Additional information to uniquely associate each simplex with a mesh cell.
//! There are essentially two ways of creating such an association:
//! - Running a marching cubes locally on each mesh cell (see recoverDomainBoundary)
//! - Intersecting a given simplex set with a mesh, i.e. clipping each simplex to
//!   each of the elements that it crosses (see intersectWithMesh).
template<size_t G>
struct SimplexCellAssociation
{
    //! Local coordinates corresponding to Triangulation<D>::vertices
    std::vector<std::array<double, G>> rst;

    //! For each cell gives the range of triangles in Triangulation<D>::triangles.
    //! In other words: a given cell with index icell is associated with the 
    //! triangles with indices in the range [offsets[icell], offsets[icell + 1])
    std::vector<size_t> offsets;

    template<size_t L>
    auto cellLocalVertices( const SimplexMesh<G, L>& mesh, size_t itriangle ) const;

    MLHP_EXPORT MLHP_PURE
    size_t memoryUsage( ) const;
};

template<size_t G, size_t L = G - 1>
using CellAssociatedSimplices = std::pair<SimplexMesh<G, L>, SimplexCellAssociation<G>>;

// ============ Simplex mesh creation ============

//! Read stl into vertex list
MLHP_EXPORT
CoordinateList<3> readStl( const std::string& filename,
                           bool flipOnOppositeNormal = false );

//! Create triangulation from vertex list (coordinate triplets assumed to be triangles)
template<size_t D> MLHP_EXPORT
Triangulation<D> createTriangulation( CoordinateConstSpan<D> vertices );

//! Same as above but dynamically allocates into a shared pointer
template<size_t D> MLHP_EXPORT
std::shared_ptr<Triangulation<D>> createSharedTriangulation( CoordinateConstSpan<D> vertices );

//! Create boundary approximation by running a marching cubes surface recovery performed 
//! on each mesh cell locally and merged into a simplex mesh. 
template<size_t D> MLHP_EXPORT
CellAssociatedSimplices<D> recoverDomainBoundary( const AbsMesh<D>& mesh,
                                                  const ImplicitFunction<D>& function,
                                                  std::array<size_t, D> resolution = array::makeSizes<D>( 1 ),
                                                  size_t niterations = marching::bisectionDefault );

//! For each cell in mesh, find the simplices it intersects and clip them to the cell
//! boundaries. This results in a refined version of simplexMesh where each simplex is 
//! now uniquely associated to one mesh cell.
template<size_t G, size_t L> requires( G >= L ) MLHP_EXPORT
CellAssociatedSimplices<G, L> intersectWithMesh( const SimplexMesh<G, L>& simplexMesh,
                                                 const AbsMesh<G>& mesh,
                                                 const KdTree<G>& tree );

//! Create simplices for all internal and boundary faces of a mesh
template<size_t D> MLHP_EXPORT
SimplexMesh<D, D - 1> createSkeletonMesh( const AbsMesh<D>& mesh );

// ======== Manipulation and computation =========

template<size_t G, size_t L> requires( G >= L ) MLHP_EXPORT
SimplexMesh<G, L> mergeSimplexMeshes( ReferenceVector<const SimplexMesh<G, L>> simplexMeshes );

template<size_t G, size_t L> requires( G >= L ) MLHP_EXPORT
SimplexMesh<G, L> filterSimplexMesh( const SimplexMesh<G, L>& triangulation,
                                     const ImplicitFunction<G>& function,
                                     size_t nseedpoints = 2 );

template<size_t G, size_t L> requires( G >= L ) MLHP_EXPORT
CellAssociatedSimplices<G, L> filterSimplexMesh( const SimplexMesh<G, L>& simplexMesh,
                                                 const SimplexCellAssociation<G>& celldata,
                                                 const ImplicitFunction<G>& function,
                                                 size_t nseedpoints = 2 );

template<size_t D> MLHP_EXPORT
std::array<double, D> integrateNormalComponents( const SimplexMesh<D, D - 1>& simplexMesh, bool abs );

// ============== kd-tree creation ===============

template<size_t G, size_t L> requires ( G >= L ) inline
KdTree<G> buildKdTree( const SimplexMesh<G, L>& simplexMesh,
                       const kdtree::Parameters& parameters = { } );

template<size_t G, size_t L> requires ( G >= L )
KdTree<G> buildKdTree( const SimplexMesh<G, L>& simplexMesh,
                       const spatial::BoundingBox<G>& bounds,
                       const kdtree::Parameters& parameters = { } );

// ====== Implicit functions and quadrature ======

MLHP_EXPORT
ImplicitFunction<3> rayIntersectionDomainFromStl( const std::string& stlfile,
                                                  const CoordinateList<3>& rays = { } );

template<size_t D> MLHP_EXPORT
ImplicitFunction<D> rayIntersectionDomain( memory::vptr<const SimplexMesh<D, D - 1>> simplexMesh,
                                           memory::vptr<KdTree<D>> kdTree = nullptr,
                                           const CoordinateList<D>& rays = { } );

template<size_t D>
class SimplexQuadrature final : public AbsQuadratureOnMesh<D>
{
public:
    MLHP_EXPORT
    SimplexQuadrature( memory::vptr<const SimplexMesh<D, D - 1>> simplexMesh,
                       memory::vptr<const SimplexCellAssociation<D>> celldata,
                       const QuadratureOrderDeterminor<D>& order = relativeQuadratureOrder<D>( 3 ) );
    
    MLHP_EXPORT
    typename AbsQuadratureOnMesh<D>::AnyCache initialize( ) const override;

    MLHP_EXPORT
    void distribute( const MeshMapping<D>& mapping,
                     std::array<size_t, D> orders,
                     CoordinateList<D>& rst,
                     CoordinateList<D>& normals,
                     std::vector<double>& weights,
                     typename AbsQuadratureOnMesh<D>::AnyCache& cache ) const override;

private:
    memory::vptr<const SimplexMesh<D, D - 1>> simplexMesh_;
    memory::vptr<const SimplexCellAssociation<D>> celldata_;
    QuadratureOrderDeterminor<D> order_;
};

// ========= Internal or niche functions =========

namespace kdtree
{

// Bounding-box provider for the kd-tree creation algorithm in kdtree.hpp
template<size_t G, size_t L> requires ( G >= L ) MLHP_EXPORT
kdtree::ObjectProvider<G> makeObjectProvider( memory::vptr<const SimplexMesh<G, L>> simplexMesh,
                                              bool clip = true );

}

namespace marching
{

// Concepts to replace linker errors due to missing instantiation with compiler errors.
template <typename T>
concept InstantiatedIndex = std::is_same_v<T, size_t> ||
                            std::is_same_v<T, std::int64_t>;

} // namespace marching

//! Marching squares in local coordinates.
template<size_t D, marching::InstantiatedIndex IndexType> MLHP_EXPORT
void cellLocalBoundaryRecovery( const AbsMapping<D>& mapping,
                                const ImplicitFunction<D>& function,
                                const std::vector<bool>& evaluations,
                                const CoordinateGrid<D>& rstGrid,
                                std::array<size_t, D> resolution,
                                CoordinateList<D>& rstList,
                                std::vector<IndexType>& cells,
                                size_t niterations,
                                std::any& anyCache );

//! Marching cubes in local coordinates. Creates actual cube shapes for uncut cubes.
template<size_t D, marching::InstantiatedIndex IndexType> MLHP_EXPORT
void cellLocalVolumeRecovery( const AbsMapping<D>& mapping,
                              const ImplicitFunction<D>& function,
                              const std::vector<bool>& evaluations,
                              const CoordinateGrid<D>& rstGrid,
                              std::array<size_t, D> resolution,
                              CoordinateList<D>& rstList,
                              std::vector<IndexType>& connectivity,
                              std::vector<IndexType>& offsets,
                              bool meshBothSides,
                              size_t niterations,
                              std::any& anyCache );

// Marching cubes implementational details
namespace marching
{

// Marching squares boundary
MLHP_EXPORT
extern std::vector<std::uint16_t> lineIndices;

MLHP_EXPORT
extern std::vector<std::uint8_t> lineData;

// Marching squares "volume" (area)
MLHP_EXPORT
extern std::vector<std::vector<std::uint8_t>> triangles2D;

// Marching cubes boundary
MLHP_EXPORT
extern std::array<std::uint16_t, 257> triangleIndices;

MLHP_EXPORT
extern std::array<std::uint8_t, 2460> triangleData;

//MLHP_EXPORT
//extern std::array<std::uint16_t, 256> edgeTable;

MLHP_EXPORT
extern std::array<std::array<size_t, 2>, 12> numbering;

// Marching cubes volume
MLHP_EXPORT
extern std::vector<std::vector<std::uint8_t>> tetrahedra;

//! For some cut configurations, the sum of all cells and all 
//! cells of the inverted cut (255 - index) does not fill the 
//! entire volume. This function gives the additional cells, 
//! such that a cell and its inverse cut add up to a full cell.
MLHP_EXPORT
extern std::vector<std::vector<std::uint8_t>> extraTetrahedra;

template<size_t D> MLHP_EXPORT
std::array<double, D> interpolate( const ImplicitFunction<D>& function,
                                   std::array<double, D> c1, bool v1,
                                   std::array<double, D> c2, bool v2,
                                   size_t niterations );

template<size_t D> MLHP_EXPORT
std::array<double, D> interpolate( const ImplicitFunction<D>& function,
                                   const AbsMapping<D>& mapping,
                                   std::array<double, D> c1, bool v1,
                                   std::array<double, D> c2, bool v2,
                                   size_t niterations );

template<size_t D> MLHP_EXPORT
void evaluateGrid( const AbsMapping<D>& mapping,
                   const ImplicitFunction<D>& function,
                   std::array<size_t, D> resolution,
                   std::array<std::vector<double>, D>& rstGrid,
                   std::vector<bool>& evaluations );

} // marching
} // mlhp

namespace mlhp
{

template<size_t G, size_t L> inline
auto SimplexMesh<G, L>::cellVertices( size_t icell ) const
{
    auto result = std::array<std::array<double, G>, L + 1> { };

    for( size_t i = 0; i < L + 1; ++i )
    {
        result[i] = vertices[cells[icell][i]];
    }

    return result;
}

template<size_t G, size_t L> inline
auto SimplexMesh<G, L>::cellNormal( size_t icell ) const requires ( G == L + 1 )
{
    if constexpr ( G == L + 1 )
    {
        return spatial::normalizeChecked( cellWeightedNormal( icell ) );
    }
}

template<size_t G, size_t L> inline
auto SimplexMesh<G, L>::cellWeightedNormal( size_t icell ) const requires ( G == L + 1 )
{
    if constexpr( G == L + 1 && L > 0 )
    {
        return spatial::measureWeightedSimplexNormal<G>( cellVertices( icell ) );
    }
    
    if constexpr ( G == 1 && L == 0 )
    {
        return this->normals[icell];
    }
}

template<size_t G, size_t L> inline
spatial::BoundingBox<G> SimplexMesh<G, L>::boundingBox( ) const
{
    return spatial::boundingBox<G>( vertices );
}

template<size_t G, size_t L> inline
spatial::BoundingBox<G> SimplexMesh<G, L>::boundingBox( size_t icell ) const
{
    return spatial::boundingBox<G>( cellVertices( icell ) );
}

template<size_t G, size_t L> inline
size_t SimplexMesh<G, L>::memoryUsage( ) const
{
    auto bytes = utilities::vectorInternalMemory( vertices, cells );
    
    if constexpr( L == 0 )
    {
        bytes += utilities::vectorInternalMemory( this->normals );
    }

    return bytes;
}

template<size_t G> template<size_t L> inline
auto SimplexCellAssociation<G>::cellLocalVertices( const SimplexMesh<G, L>& mesh, 
                                                   size_t icell ) const
{
    auto vertices = std::array<std::array<double, G>, L + 1> { };
    auto indices = mesh.cells[icell];

    for( size_t ivertex = 0; ivertex < L + 1; ++ivertex )
    {
        vertices[ivertex] = rst[indices[ivertex]];
    }

    return vertices;
}

template<size_t G, size_t L> requires ( G >= L ) inline
KdTree<G> buildKdTree( const SimplexMesh<G, L>& simplexMesh,
                       const spatial::BoundingBox<G>& bounds,
                       const kdtree::Parameters& parameters )
{
    return buildKdTree( kdtree::makeObjectProvider<G, L>( simplexMesh ), bounds, parameters );
}

template<size_t G, size_t L> requires ( G >= L ) inline
KdTree<G> buildKdTree( const SimplexMesh<G, L>& simplexMesh,
                       const kdtree::Parameters& parameters )
{
    return buildKdTree( simplexMesh, spatial::boundingBox<G>( simplexMesh.vertices ), parameters );
}

} // namespace mlhp

#endif // MLHP_CORE_TRIANGULATION_HPP
