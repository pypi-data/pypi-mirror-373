// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_MESH_HPP
#define MLHP_CORE_MESH_HPP

#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/utilities.hpp"
#include "mlhp/core/alias.hpp"
#include "mlhp/core/compilermacros.hpp"
#include "mlhp/core/mapping.hpp"
#include "mlhp/core/arrayfunctions.hpp"

namespace mlhp
{

/* 
 * Terminology and general info:
 * 
 * - cell: single element of a mesh. Called cell to distinguish from a finite element, which
 *   would have more attributes, such as location maps and shape functions.
 * 
 * - face: D - 1 dimensional bounding topology of a cell. For a cubic cell we have 6 faces,
 *   for a rectangular cell we have 4 edges and so on.
 * 
 * - axis, side: for n-cubes we have 2*n faces, characterized by their normal axis and side,
 *   so in 3D, left, right, front, back, bottom, top have face indices [0, 1, 2, 3, 4, 5],
 *   and (axis, side) tuples of [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)].
 * 
 * - full vs leaf indices: For hierarchical meshes we have two index sets, one for all cells 
 *   in the hierarchy, and another considering leaves only (who form a non-overlapping par-
 *   tition of the domain). Both have the same data index type, but some functions only make 
 *   sense in a hierarchical context (e.g. parent index), others only in leaf context (e.g. 
 *   when defining a finite element basis, where only leaves are considered finite elements 
 *   and we don't want "gaps" in the numbering). For the hierarchical mesh types, cell indi-
 *   ces are leaf indices, unless specified otherwise (by parameter name or comments).
 * 
 */
    
//! General mesh type that could have hanging nodes and non-cubic cell types.
template<size_t D>
class MLHP_EXPORT AbsMesh : utilities::DefaultVirtualDestructor
{
public:

    //! Total number of (non-overlapping / leaf) cells. 
    virtual CellIndex ncells( ) const = 0;

    //! Reference coordinate system type
    virtual CellType cellType( CellIndex icell ) const = 0;

    //! Number of faces of the reference coordinate system.
    size_t nfaces( CellIndex icell ) const;

    //! For given face, return a list of neighbours with corresponding local face index. Target size is un-
    //! changed if face is part of the boundary and can carry more than one cell in case of hanging nodes.
    virtual void neighbours( CellIndex icell, size_t iface, std::vector<MeshCellFace>& target ) const = 0;

    //! Create uninitialized mapping from rst to xyz
    virtual MeshMapping<D> createMapping( ) const = 0;

    //! Initialize mapping from rst to xyz for a cell
    virtual void prepareMapping( CellIndex icell, MeshMapping<D>& mapping ) const = 0;
    
    //! Find cell and local coordinates at given global coordinates (see class definition below)
    std::unique_ptr<AbsBackwardMapping<D>> createBackwardMapping( ) const;

    //! Create factory for concurrent backward mapping
    virtual BackwardMappingFactory<D> createBackwardMappingFactory( ) const = 0;
        
    virtual std::unique_ptr<AbsMapping<D, D - 1>> createInterfaceMapping( ) const = 0;

    virtual void prepareInterfaceMappings( MeshCellFace face0, 
                                           MeshCellFace face1, 
                                           AbsMapping<D, D - 1>& mapping0, 
                                           AbsMapping<D, D - 1>& mapping1 ) const = 0;
    
    //! The amount of memory used by mesh in bytes
    virtual size_t memoryUsage( ) const = 0;

    //! Create copy without cloning aggregated meshes
    virtual MeshUniquePtr<D> clone( ) const = 0;
};

template<size_t D>
class AbsBackwardMapping : public utilities::DefaultVirtualDestructor
{
public:
    MLHP_EXPORT
    explicit AbsBackwardMapping( const AbsMesh<D>* mesh );

    //! Find cells and local coordinates at given global coordinate
    MLHP_EXPORT 
    void map( std::array<double, D> xyz, 
              BackwardMapVector<D>& target, 
              double epsilon = 1e-10 );

    //! Find first cell with local coordinate or none
    MLHP_EXPORT
    BackwardMapResult<D> map( std::array<double, D> xyz, 
                              double epsilon = 1e-10 );

    MLHP_EXPORT MLHP_PURE
    const AbsMesh<D>& mesh( ) const;

private:
    virtual void mapInternal( std::array<double, D> xyz, 
                              BackwardMapVector<D>& target, 
                              double epsilon ) = 0;

    BackwardMapVector<D> target_;
    const AbsMesh<D>* mesh_;
};

template<size_t D>
using ThreadLocalBackwardMappings = utilities::ThreadLocalContainer<std::shared_ptr<AbsBackwardMapping<D>>>;

//! Regular grid of n-cubes with one or no neighbour per face. Allows arbitrary
//! mapping functions and also allows removing cells.
template<size_t D>
class MLHP_EXPORT AbsGrid : public virtual AbsMesh<D>
{
public:

    //! Obtain neighbour in given (local) coordinate axis
    virtual CellIndex neighbour( CellIndex cell, size_t axis, size_t side ) const = 0;
    
    //! Clone with AbsGrid return type
    virtual GridUniquePtr<D> cloneGrid( ) const = 0;

    MLHP_PURE
    virtual CellType cellType( CellIndex cell ) const override;

    void neighbours( CellIndex cell, size_t face, std::vector<MeshCellFace>& target ) const override;

    std::unique_ptr<AbsMapping<D, D - 1>> createInterfaceMapping( ) const override;

    void prepareInterfaceMappings( MeshCellFace face0,
                                   MeshCellFace face1,
                                   AbsMapping<D, D - 1>& mapping0,
                                   AbsMapping<D, D - 1>& mapping1 ) const override;

    MeshUniquePtr<D> clone( ) const override;
};

//! Axis aligned potentially non-uniformly spaced grid. So techically a rectilinear grid.
template<size_t D>
class CartesianGrid final : public AbsGrid<D>
{
public:
    MLHP_EXPORT 
    CartesianGrid( const CoordinateGrid<D>& indexVectors );
    
    MLHP_EXPORT 
    CartesianGrid( std::array<size_t, D> numberOfCells,
                   std::array<double, D> lengths,
                   std::array<double, D> origin = array::make<D>( 0.0 ) );
    
    //! Number of cells in given direction
    MLHP_PURE size_t ncells( size_t axis ) const;

    //! Array of number of cells in each direction
    MLHP_PURE std::array<size_t, D> shape( ) const;

    //! First coordinate in each direction
    MLHP_PURE std::array<double, D> origin( ) const;

    //! Last minus first coordinate in each direction
    MLHP_PURE std::array<double, D> lengths( ) const;
    
    //! Coordinate vector for each direction
    MLHP_EXPORT CoordinateGrid<D> coordinates( ) const;

    MLHP_PURE MLHP_EXPORT
    spatial::BoundingBox<D> boundingBox( ) const;

    MLHP_PURE
    spatial::BoundingBox<D> boundingBox( CellIndex cellIndex ) const;

    MLHP_PURE MLHP_EXPORT
    CellIndex ncells( ) const override;
    
    MLHP_PURE MLHP_EXPORT
    CellIndex neighbour( CellIndex cell, size_t axis, size_t side ) const override;
    
    std::array<CellIndex, D> gridSizes( ) const { return numberOfCells_; }

    MLHP_PURE MLHP_EXPORT
    std::array<CellIndex, D> gridIndices( CellIndex icell ) const;

    //MLHP_PURE 
    //BackwardMapResult<D> mapToLocal( std::array<double, D> xyz ) const override;

    MLHP_EXPORT
    BackwardMappingFactory<D> createBackwardMappingFactory( ) const override;

    MLHP_PURE MLHP_EXPORT
    size_t memoryUsage( ) const override;

    MLHP_EXPORT
    MeshMapping<D> createMapping( ) const override;

    MLHP_EXPORT
    void prepareMapping( CellIndex cell, 
                         MeshMapping<D>& mapping ) const override;

    MLHP_EXPORT
    GridUniquePtr<D> cloneGrid( ) const override;

private:
    std::array<CellIndex, D> numberOfCells_;
    std::array<CellIndex, D> strides_;
    CoordinateGrid<D> coordinates_;
};

//! Hierarchically refined grid
template<size_t D>
class MLHP_EXPORT AbsHierarchicalGrid : public AbsMesh<D>
{
public:    

    void refine( const RefinementFunction<D>& strategy );

    virtual void refine( const std::vector<CellIndex>& leafIndices ) = 0;

    virtual const AbsGrid<D>& baseGrid( ) const = 0;
    virtual GridConstSharedPtr<D> baseGridPtr( ) const = 0;
    
    //! Clone with AbsGrid return type
    virtual HierarchicalGridUniquePtr<D> cloneGrid( ) const = 0;

    // Sizes
    virtual CellIndex nleaves( ) const = 0;
    virtual CellIndex nfull( ) const = 0;

    CellIndex ncells( ) const override final { return nleaves( ); }

    // Indices
    virtual CellIndex fullIndex( CellIndex leafIndex ) const = 0;
    virtual CellIndex leafIndex( CellIndex fullIndex ) const = 0;

    // Topology (all functions in the block below use full indices!)
    virtual CellIndex parent( CellIndex fullIndex ) const = 0;
    virtual CellIndex neighbour( CellIndex fullIndex, size_t axis, size_t side ) const = 0;
    virtual CellIndex child( CellIndex fullIndex, PositionInParent<D> position ) const = 0;
    virtual RefinementLevel refinementLevel( CellIndex fullIndex ) const = 0;
    virtual PositionInParent<D> localPosition( CellIndex fullIndex ) const = 0;
    virtual bool isLeaf( CellIndex fullIndex ) const = 0;

    MLHP_PURE
    virtual CellType cellType( CellIndex leafIndex ) const override;

    void neighbours( CellIndex leafIndex, size_t side, std::vector<MeshCellFace>& target ) const override;

    //! Returns leaf index
    CellLocalCoordinates<D> mapToLeaf( CellIndex fullIndex, std::array<double, D> rst ) const;

    //! Returns full index
    virtual BackwardMapResult<D> mapToChild( CellIndex fullIndex, std::array<double, D> rst ) const = 0;

    //// Mapping
    //virtual BackwardMapResult<D> mapToLocalFull( std::array<double, D> xyz ) const = 0;

    //MLHP_EXPORT
    //BackwardMapResult<D> mapToLocal( std::array<double, D> xyz ) const override;

    MeshUniquePtr<D> clone( ) const override;
};

template<size_t D>
class RefinedGrid final : public AbsHierarchicalGrid<D>
{
public:

    MLHP_EXPORT
    RefinedGrid( const GridSharedPtr<D>& baseGrid );

    MLHP_EXPORT
    void refine( const std::vector<CellIndex>& leafIndices ) override;

    MLHP_PURE
    CellIndex nleaves( ) const override;
    
    MLHP_PURE
    CellIndex nfull( ) const override;

    MLHP_EXPORT MLHP_PURE
    CellIndex fullIndex( CellIndex leafIndex ) const override;
    
    MLHP_EXPORT MLHP_PURE
    CellIndex leafIndex( CellIndex fullIndex ) const override;

    MLHP_EXPORT MLHP_PURE
    CellIndex parent( CellIndex fullIndex ) const override;
    
    MLHP_EXPORT MLHP_PURE
    CellIndex child( CellIndex cell, PositionInParent<D> position ) const override;
    
    MLHP_EXPORT  MLHP_PURE
    CellIndex neighbour( CellIndex cell, size_t axis, size_t side ) const override;
    
    MLHP_EXPORT MLHP_PURE
    RefinementLevel refinementLevel( CellIndex fullIndex ) const override;
    
    MLHP_EXPORT MLHP_PURE
    PositionInParent<D> localPosition( CellIndex fullIndex ) const override;
    
    MLHP_EXPORT MLHP_PURE
    bool isLeaf( CellIndex fullIndex ) const override;
    
    const AbsGrid<D>& baseGrid( ) const override { return *baseGrid_; }
    GridConstSharedPtr<D> baseGridPtr( ) const override { return baseGrid_; }
    
    MLHP_EXPORT HierarchicalGridUniquePtr<D> cloneGrid( ) const override;

    MLHP_EXPORT MLHP_PURE
    size_t memoryUsage( ) const override;

    //MLHP_PURE 
    //BackwardMapResult<D> mapToLocalFull( std::array<double, D> xyz ) const override;

    //! Returns full index
    MLHP_EXPORT
    BackwardMapResult<D> mapToChild( CellIndex fullIndex, std::array<double, D> rst ) const override;

    MLHP_EXPORT
    BackwardMappingFactory<D> createBackwardMappingFactory( ) const override;

    MLHP_EXPORT
    MeshMapping<D> createMapping( ) const override;

    MLHP_EXPORT
    void prepareMapping( CellIndex cell, 
                         MeshMapping<D>& mapping ) const override;

    MLHP_EXPORT
    std::unique_ptr<AbsMapping<D, D - 1>> createInterfaceMapping( ) const override;

    MLHP_EXPORT
    void prepareInterfaceMappings( MeshCellFace face0,
                                   MeshCellFace face1,
                                   AbsMapping<D, D - 1>& mapping0,
                                   AbsMapping<D, D - 1>& mapping1 ) const override;

private:
    void resetDataStructure( );
    void rebuildDataStructure( );

    GridSharedPtr<D> baseGrid_;

    std::vector<bool> isLeaf_;
    
    std::vector<CellIndex> parentIndex_;
    std::vector<CellIndex> fullIndex_;
    std::vector<CellIndex> leafIndexOrChild_;
};

template<size_t D>
class MLHP_EXPORT UnstructuredMesh final : public AbsMesh<D>
{
public:

    //! VTK-like data structure. Offsets must be one larger than the number of cells.
    //! Types are automatically deduced from the dimensionality and the number of vertices
    //! filterVertices  : remove vertices not referenced by any cell (will change node ids!)
    //! reorderVertices : prevent negative Jacobian determinant by flipping vertices
    UnstructuredMesh( CoordinateList<D>&& vertices,
                      std::vector<size_t>&& cells,
                      std::vector<size_t>&& offsets,
                      bool filterVertices = true,
                      bool reorderVertices = true );

    MLHP_PURE CellIndex ncells( ) const override;
    MLHP_PURE CellType cellType( CellIndex icell ) const override;
    MLHP_PURE size_t nvertices( ) const;
    MLHP_PURE size_t nvertices( CellIndex icell ) const;
    MLHP_PURE size_t vertexIndex( CellIndex icell, size_t ivertex ) const;
    MLHP_PURE size_t memoryUsage( ) const override;

    MLHP_PURE 
    std::array<double, D> vertex( size_t gvertex ) const;
    
    MLHP_PURE 
    std::array<double, D> vertex( CellIndex icell, size_t lvertex ) const;

    void neighbours( CellIndex icell, size_t iface, std::vector<MeshCellFace>& target ) const override;

    MeshMapping<D> createMapping( ) const override;

    void prepareMapping( CellIndex icell, MeshMapping<D>& mapping ) const override;

    //MLHP_EXPORT
    //BackwardMapResult<D> mapToLocal( std::array<double, D> xyz ) const override;

    BackwardMappingFactory<D> createBackwardMappingFactory( ) const override ;

    std::unique_ptr<AbsMapping<D, D - 1>> createInterfaceMapping( ) const override;

    void prepareInterfaceMappings( MeshCellFace face0,
                                   MeshCellFace face1,
                                   AbsMapping<D, D - 1>& mapping0,
                                   AbsMapping<D, D - 1>& mapping1 ) const override;

    MLHP_PURE 
    spatial::BoundingBox<D> boundingBox( ) const;
    
    MLHP_PURE 
    spatial::BoundingBox<D> boundingBox( CellIndex icell ) const;

    MeshUniquePtr<D> clone( ) const override;

private:
    CoordinateList<D> vertices_;
    std::vector<size_t> connectivity_;
    std::vector<size_t> offsets_;
    std::vector<CellType> types_;
    NeighboursVector neighbours_;
};

// "Removes" cells of another mesh
template<size_t D>
class MLHP_EXPORT AbsFilteredMesh : public virtual AbsMesh<D>
{
public:
    virtual const AbsMesh<D>& unfilteredMesh( ) const = 0;

    virtual CellIndex filteredIndex( CellIndex unfilteredIndex ) const = 0;
    virtual CellIndex unfilteredIndex( CellIndex filteredIndex ) const = 0;

    virtual std::unique_ptr<AbsFilteredMesh<D>> cloneFiltered( ) const = 0;
};

template<size_t D, typename MeshBase>
class FilteredMeshBase : public virtual AbsFilteredMesh<D>,
                         public virtual MeshBase
{
public:
    // Keep cells with true entries in mask, remove others.
    FilteredMeshBase( const std::shared_ptr<MeshBase>& mesh,
                      const std::vector<bool>& mask );

    // Filter elements based on cut state (-1 -> outside, 0 -> cut, 1 -> inside)
    FilteredMeshBase( const std::shared_ptr<MeshBase>& mesh,
                      const std::vector<std::int8_t>& cutstate,
                      bool removeCutCells = false );

    // Remove the given indices, keep the others.
    FilteredMeshBase( const std::shared_ptr<MeshBase>& mesh,
                      const CellIndexVector& filteredCells );

    const AbsMesh<D>& unfilteredMesh( ) const override;

    CellIndex filteredIndex( CellIndex unfilteredIndex ) const override final;
    CellIndex unfilteredIndex( CellIndex filteredIndex ) const override final;

    CellIndex ncells( ) const override;

    CellType cellType( CellIndex cell ) const override;

    void neighbours( CellIndex cell, size_t side, std::vector<MeshCellFace>& target ) const override;

    MeshMapping<D> createMapping( ) const override;

    void prepareMapping( CellIndex cell, MeshMapping<D>& mapping ) const override;

    //BackwardMapResult<D> mapToLocal( std::array<double, D> xyz ) const override;
    BackwardMappingFactory<D> createBackwardMappingFactory( ) const override;

    std::unique_ptr<AbsMapping<D, D - 1>> createInterfaceMapping( ) const override;

    void prepareInterfaceMappings( MeshCellFace face0,
                                   MeshCellFace face1,
                                   AbsMapping<D, D - 1>& mapping0,
                                   AbsMapping<D, D - 1>& mapping1 ) const override;

    size_t memoryUsage( ) const override;
    
    MeshUniquePtr<D> clone( ) const override;

protected:
    std::shared_ptr<MeshBase> mesh_;

private:
    std::vector<CellIndex> reduce_;
    std::vector<CellIndex> expand_;
};

template<size_t D>
using FilteredMeshSharedPtr = std::shared_ptr<const AbsFilteredMesh<D>>;

template<size_t D>
class FilteredMesh final : public FilteredMeshBase<D, AbsMesh<D>>
{ 
public:
    using FilteredMeshBase<D, AbsMesh<D>>::FilteredMeshBase;
    
    std::unique_ptr<AbsFilteredMesh<D>> cloneFiltered( ) const override;
};

template<size_t D>
class FilteredGrid final : public FilteredMeshBase<D, AbsGrid<D>>
{
public:
    using FilteredMeshBase<D, AbsGrid<D>>::FilteredMeshBase;
    
    const AbsGrid<D>& unfilteredGrid( ) const;
    
    std::unique_ptr<AbsFilteredMesh<D>> cloneFiltered( ) const override;
    std::unique_ptr<AbsGrid<D>> cloneGrid( ) const override;

    CellIndex neighbour( CellIndex cell, size_t axis, size_t side ) const override;
};

//! Merges multiple meshes into one
template<size_t D>
class MLHP_EXPORT AggregateMesh : public AbsMesh<D>
{
public:
    using MeshPtr = memory::vptr<const AbsMesh<D>>;

    AggregateMesh( const std::vector<MeshPtr>& meshes );
    AggregateMesh( std::initializer_list<MeshPtr> list );
    
    //! Construct from mesh references
    template<typename... Meshes> 
    AggregateMesh( const AbsMesh<D>& mesh, const Meshes&... meshes )
        requires ( std::is_convertible_v<const Meshes*, const AbsMesh<D>*> && ... && true ) :
        AggregateMesh<D>( std::vector<MeshPtr> { mesh, meshes... } )
    { }
     
    //! Construct from mesh shared pointers
    template<typename... Meshes> 
    AggregateMesh( std::shared_ptr<const AbsMesh<D>> mesh, const Meshes&... meshes )
        requires ( std::is_convertible_v<Meshes, std::shared_ptr<const AbsMesh<D>>> && ... && true ) :
        AggregateMesh<D>( std::vector<MeshPtr> { mesh, meshes... } )
    { }

    auto& componentMesh( size_t imesh ) const { return *meshes_[imesh]; }
        
    std::pair<size_t, CellIndex> findMeshIndex( CellIndex icell ) const;

    CellIndex ncells( ) const override { return offsets_.back( ); }

    CellType cellType( CellIndex icell ) const override;

    void neighbours( CellIndex icell, size_t iface, std::vector<MeshCellFace>& target ) const override;

    MeshMapping<D> createMapping( ) const override;
    
    void prepareMapping( CellIndex icell, MeshMapping<D>& mapping ) const override;

    BackwardMappingFactory<D> createBackwardMappingFactory( ) const override;

    std::unique_ptr<AbsMapping<D, D - 1>> createInterfaceMapping( ) const override;

    void prepareInterfaceMappings( MeshCellFace face0,
                                   MeshCellFace face1,
                                   AbsMapping<D, D - 1>& mapping0,
                                   AbsMapping<D, D - 1>& mapping1 ) const override;

    MeshUniquePtr<D> clone( ) const override;

    size_t memoryUsage( ) const override;


private:
    std::vector<MeshPtr> meshes_;
    std::vector<CellIndex> offsets_;
};

template<size_t D> MLHP_EXPORT
void print( const AbsHierarchicalGrid<D>& grid, std::ostream& os );

template<size_t D> MLHP_EXPORT
void print( const UnstructuredMesh<D>& grid, std::ostream& os );

template<size_t D>
using CartesianGridSharedPtr = std::shared_ptr<CartesianGrid<D>>;

template<size_t D> MLHP_EXPORT
CartesianGridSharedPtr<D> makeCartesianGrid( std::array<size_t, D> nelements,
                                             std::array<double, D> lengths = array::make<D>( 1.0 ),
                                             std::array<double, D> origin = { } );

template<size_t D> MLHP_EXPORT
HierarchicalGridSharedPtr<D> makeRefinedGrid( const GridSharedPtr<D>& baseGrid );

template<size_t D> MLHP_EXPORT
HierarchicalGridSharedPtr<D> makeRefinedGrid( const CartesianGrid<D>& baseGrid );

template<size_t D> MLHP_EXPORT
HierarchicalGridSharedPtr<D> makeRefinedGrid( const CoordinateGrid<D>& coordinates );

template<size_t D> MLHP_EXPORT
HierarchicalGridSharedPtr<D> makeRefinedGrid( std::array<size_t, D> nelements,
                                              std::array<double, D> lengths = array::make<D>( 1.0 ),
                                              std::array<double, D> origin = { } );

//! Create adapted grid
template<size_t D> MLHP_EXPORT
HierarchicalGridSharedPtr<D> makeRefinedGrid( const AbsHierarchicalGrid<D>& grid,
                                              const std::vector<int>& relativeDepth,
                                              size_t maxdepth = NoValue<size_t> );

// TODO: move to mapping
template<size_t D> MLHP_EXPORT
std::optional<std::array<double, D>> mapBackward( const AbsMapping<D>& mapping,
                                                  std::array<double, D> xyz,
                                                  double eps = 1e-10 );

namespace mesh
{

template<size_t D>
auto mapping( const AbsMesh<D>& mesh, 
              CellIndex icell );

template<size_t D>
auto map( const AbsMesh<D>& mesh, 
          CellIndex icell,
          std::array<double, D> rst );

template<size_t D> MLHP_EXPORT
CoordinateList<D> map( const AbsMesh<D>& mesh,
                       std::span<const CellIndex> indices,
                       CoordinateConstSpan<D> rst );

//! Returns first match (i.e. when coordinates are between two cells)
template<size_t D> MLHP_EXPORT
std::vector<BackwardMapResult<D>> mapBackwardSingle( const AbsMesh<D>& mesh,
                                                     CoordinateConstSpan<D> xyz,
                                                     double epsilon = 1e-10 );

template<size_t D>
using LinearizedBackwardMapResults = LinearizedVectors<CellLocalCoordinates<D>>;

//! Resturns all matches
template<size_t D> MLHP_EXPORT
LinearizedBackwardMapResults<D> mapBackwardMultiple( const AbsMesh<D>& mesh,
                                                     CoordinateConstSpan<D> xyz,
                                                     double epsilon = 1e-10 );

template<size_t D>
auto fullMapping( const AbsHierarchicalGrid<D>& grid, 
                  CellIndex fullIndex );

template<size_t D>
auto mapFull( const AbsHierarchicalGrid<D>& grid, 
              CellIndex fullIndex,
              std::array<double, D> rst );

//! Map from face coordinates to local coordinate system
template<size_t D> MLHP_EXPORT
FaceMapping<D> faceMapping( const AbsMesh<D>& mesh,  
                            CellIndex icell, 
                            size_t iface );

//! Extract all boundaries as vector of (cell, side) tuples
template<size_t D> MLHP_EXPORT
MeshCellFaces boundaries( const AbsMesh<D>& mesh );

//! Extract vector of (cell, side) tuples for each side given
template<size_t D> MLHP_EXPORT
std::vector<MeshCellFaces> boundariesByFaceIndex( const AbsMesh<D>& mesh,
                                                  const std::vector<size_t>& sides );

//! Find boundaries intersecting the mesh bounding box on the given sides
template<size_t D> MLHP_EXPORT
std::vector<MeshCellFaces> boundariesByBoundingBox( const AbsMesh<D>& mesh,
                                                    const std::vector<size_t>& sides,
                                                    double epsilon = 1e-8 );

template<size_t D> MLHP_EXPORT
spatial::BoundingBox<D> boundingBox( const AbsMesh<D>& mesh,
                                     size_t nseedpoints = 2 );

//! TODO: Move to mapping
template<size_t D> MLHP_EXPORT
spatial::BoundingBox<D> boundingBox( const AbsMapping<D>& mapping,
                                     size_t nseedpoints = 2 );

template<size_t D> MLHP_EXPORT
MeshCellFaces facesInBoundingBox( const AbsMesh<D>& mesh, 
                                  spatial::BoundingBox<D> bounds,
                                  size_t nseedpoints,
                                  double epsilon = 1e-8 );

template<size_t D> MLHP_EXPORT
MeshCellFaces facesInsideDomain( const AbsMesh<D>& mesh, 
                                 const ImplicitFunction<D>& domain,
                                 size_t nseedpoints );

template<size_t D> MLHP_EXPORT
MeshCellFaces facesInsideDomain( const AbsMesh<D>& mesh, 
                                 const MeshCellFaces& faces,
                                 const ImplicitFunction<D>& domain,
                                 size_t nseedpoints );

template<size_t D> MLHP_EXPORT
kdtree::ObjectProvider<D> boundingBoxProvider( const UnstructuredMesh<D>& mesh );

// Parent cell indices of all (leaf and non-leaf cells)
template<size_t D> MLHP_EXPORT
std::vector<CellIndex> parents( const AbsHierarchicalGrid<D>& grid );

template<size_t D> MLHP_EXPORT
std::vector<bool> leafMask( const AbsHierarchicalGrid<D>& grid );

// Recursively gather full indices for leaves below given (parent) cell
template<size_t D> MLHP_EXPORT
void leaves( const AbsHierarchicalGrid<D>& grid,
             CellIndex cell,
             std::vector<CellIndex>& target,
             size_t maxdepth = NoValue<size_t> );

template<size_t D> MLHP_EXPORT
ThreadLocalBackwardMappings<D> threadLocalBackwardMappings( const AbsMesh<D>& mesh );

//! POD for findInOtherGrid
struct CellInOtherGrid
{
    CellIndex otherCell;           // full index of corresponding cell in other grid (may have children)
    CellIndex thisParent;          // full index of corresponding parent of this cell if other mesh is coarser
    RefinementLevel otherLevel;    // level of otherCell (not the maximum since it may have children)
    RefinementLevel thisLevel;     // level of this cell (not thisParent)
};

//! Find the corresponding cell in other mesh (may be coarser)
//! See also the 1D example in test findInOtherGrid1D_test in mesh_test.cpp 
template<size_t D> MLHP_EXPORT
CellInOtherGrid findInOtherGrid( const AbsHierarchicalGrid<D>& thisMesh,
                                 const AbsHierarchicalGrid<D>& otherMesh,
                                 CellIndex thisFullIndex );

//! POD for findInOtherGrid with leaf accumulation (but as full indices)
template<size_t D>
struct SharedSupport
{                                  // At least one mapping is identity:
    CartesianMapping<D> thisCell;  // If other is finer: Map from other cell to this cell; identity otherwise
    CartesianMapping<D> otherCell; // If other is coarser: Map from this cell into other cell; identity otherwise
    CellIndex otherIndex;          // Full index (!) of other cell
};

//! Gather cells from otherMesh that lie within thisMesh at thisFullIndex
//! See also the 1D example in test findInOtherGrid1D_test in mesh_test.cpp 
template<size_t D> MLHP_EXPORT
CellInOtherGrid findInOtherGrid( const AbsHierarchicalGrid<D>& thisMesh,
                                 const AbsHierarchicalGrid<D>& otherMesh,
                                 std::vector<CellIndex>& target,
                                 CellIndex thisFullIndex,
                                 size_t maxdepth = NoValue<size_t> );

//! In addition to the function above gather mappings for each subcell
//! See also the 1D example in test findInOtherGrid1D_test in mesh_test.cpp 
template<size_t D> MLHP_EXPORT
CellInOtherGrid findInOtherGrid( const AbsHierarchicalGrid<D>& thisMesh,
                                 const AbsHierarchicalGrid<D>& otherMesh,
                                 std::vector<SharedSupport<D>>& target,
                                 CellIndex thisFullIndex,
                                 size_t maxdepth = NoValue<size_t> );

//! Map coordinates from leaf of one mesh to leaf of another mesh (returns leaf index).
template<size_t D> MLHP_EXPORT
CellLocalCoordinates<D> mapToOtherGrid( const AbsHierarchicalGrid<D>& thisGrid,
                                        const AbsHierarchicalGrid<D>& otherGrid,
                                        CellIndex thisLeafIndex,
                                        std::array<double, D> thisRst );

template<size_t D> MLHP_EXPORT MLHP_PURE
CellIndex root( const AbsHierarchicalGrid<D>& grid,
                CellIndex fullIndex );

// Root (full) indices for all cells in the hierarchy (or only leaves if fullHierarchy = false)
template<size_t D> MLHP_EXPORT
std::vector<CellIndex> roots( const AbsHierarchicalGrid<D>& grid, 
                              bool fullHierarchy = true );

template<size_t D> MLHP_EXPORT
void pathToRoot( const AbsHierarchicalGrid<D>& grid,
                 CellIndex fullIndex,
                 std::vector<CellIndex>& path );

template<size_t D> MLHP_EXPORT
PositionInParentVector<D> positionsInParent( const AbsHierarchicalGrid<D>& grid );

template<size_t D> MLHP_EXPORT
void mapToParent( CoordinateGrid<D>& rst,
                  PositionInParent<D> positionInParent );

template<size_t D> MLHP_EXPORT
CartesianMapping<D> mapToParent( PositionInParent<D> localPosition );

template<size_t D> MLHP_EXPORT
CartesianMapping<D> mapToParent( CartesianMapping<D> mapping,
                                 PositionInParent<D> localPosition );

template<size_t D>
using HierarchyMapping = std::pair<CartesianMapping<D>, CellIndex>;

template<size_t D> MLHP_EXPORT
HierarchyMapping<D> mapToRoot( const AbsHierarchicalGrid<D>& grid,
                               CellIndex fullIndex );

template<size_t D> MLHP_EXPORT
RefinementLevelVector refinementLevels( const AbsHierarchicalGrid<D>& grid,
                                        bool fullHierarchy = false );

template<size_t D> MLHP_EXPORT
RefinementLevel maxRefinementLevel( const AbsHierarchicalGrid<D>& grid );

template<size_t D> MLHP_EXPORT
NCubeNeighboursVector<D> hierarchicalNeighbours( const AbsHierarchicalGrid<D>& grid );

template<size_t D> MLHP_EXPORT
CellIndexVector reductionMap( const AbsFilteredMesh<D>& mesh );

//! Construct strategy for adaptively refining a new mesh
//! - relativeDepth values mean -1 --> coarsen, 0 --> keep, 1 --> refine.
//! - Coarsens only when all children are marked for coarsening
template<size_t D> MLHP_EXPORT
RefinementFunction<D> refineAdaptively( const AbsHierarchicalGrid<D>& old,
                                        const std::vector<int>& relativeDepth,
                                        size_t maxdepth = NoValue<size_t> );

template<size_t D> MLHP_EXPORT
std::string analyzeCellTypes( const AbsMesh<D>& mesh );

template<size_t D> MLHP_EXPORT
std::vector<std::int8_t> cutstate( const AbsMesh<D>& grid,
                                   const ImplicitFunction<D>& function,
                                   size_t nseedpoints = 4 );

//! Determins grid spacing that roughly yields the total number 
//! of elements while trying to maintain equal side lengths
template<size_t D>
std::array<size_t, D> gridsplit( std::array<double, D> lengths,
                                 size_t targetNumber );

} // namespace mesh
} // mlhp

#include "mlhp/core/mesh_impl.hpp"

#endif // MLHP_CORE_MESH_HPP
