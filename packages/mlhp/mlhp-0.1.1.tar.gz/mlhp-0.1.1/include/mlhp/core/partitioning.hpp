// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_PARTITIONING_HPP
#define MLHP_CORE_PARTITIONING_HPP

#include "mlhp/core/alias.hpp"
#include "mlhp/core/mapping.hpp"
#include "mlhp/core/sparse.hpp"

#include <any>

namespace mlhp
{

//! For given input degreee, returns max(ceil(degree * factor) + offset, 0)
template<size_t D> MLHP_EXPORT
QuadratureOrderDeterminor<D> relativeQuadratureOrder( int offset = 1, double factor = 1.0 );

//! Disregards input degree and simply returns orders
template<size_t D> MLHP_EXPORT
QuadratureOrderDeterminor<D> absoluteQuadratureOrder( std::array<size_t, D> orders );

//! Simple depth-first quadtree refined towards the implicitly defined boundary 
template<size_t D> MLHP_EXPORT
void generateSpaceTreeLeaves( const ImplicitFunction<D>& function,
                              const AbsMapping<D>& mapping,
                              size_t depth, 
                              size_t nseedpoints,
                              std::vector<CartesianMapping<D>>& cells );

//! Also store whether cells were outside (-1), cut (0), or inside (1). Cells at full depth are 
//! not refined, making an intersection test unnecessary. When computeCutStateOfFinestCells is 
//! active, this test is done regardless, otherwise full depth cells are always considered cut.
template<size_t D> MLHP_EXPORT
void generateSpaceTreeLeaves( const ImplicitFunction<D>& function,
                              const AbsMapping<D>& mapping,
                              size_t depth, 
                              size_t nseedpoints,
                              std::vector<CartesianMapping<D>>& cells,
                              std::vector<int>& cutState,
                              bool computeCutStateOfFinestCells = false );

template<size_t D> MLHP_EXPORT
void mapQuadraturePointGrid( const AbsMapping<D>& mapping,
                             const CoordinateGrid<D>& rstGrid,
                             CoordinateList<D>& xyzList,
                             std::vector<double>& weights );

template<size_t D> MLHP_EXPORT
void mapQuadraturePointLists( const AbsMapping<D>& mapping,
                              const CoordinateGrid<D>& rstLists,
                              CoordinateList<D>& xyzList,
                              std::vector<double>& weights );

template<size_t D>
using QuadratureCache = utilities::Cache<AbsQuadrature<D>>;

template<size_t D>
class AbsQuadrature : utilities::DefaultVirtualDestructor
{
public:

    // Initialize thread-local data
    virtual QuadratureCache<D> initialize( ) const = 0;
    
    // Generate partition and store data in cache
    virtual size_t partition( const MeshMapping<D>& mapping,
                              QuadratureCache<D>& anyCache ) const = 0;

    // Distribute integration points for given partition. Returns true if points form
    // a grid. If so, rst contains the grid coordinate ticks, so that an integration point
    // in 3D at grid indices i, j, k is accessed as (rst[0][i], rst[1][j], rst[2][k]). 
    // If no grid, the coordinates at index i are (rst[0][i], rst[1][i], rst[2][i]).
    // The global coordinates in xyz are never considered grids.
    virtual bool distribute( size_t ipartition,
                             std::array<size_t, D> orders,
                             CoordinateGrid<D>& rst,
                             CoordinateList<D>& xyzList,
                             std::vector<double>& weights,
                             QuadratureCache<D>& anyCache ) const = 0;
};

//! Helper return type for evaluateQuadrature(...) below
template<size_t D>
struct EvaluateQuadraturePartition
{
    std::vector<std::array<double, D>> rst;
    std::vector<std::array<double, D>> xyz;
    std::vector<double> weights;
    bool isgrid;

    CellIndex icell;
    const AbsMesh<D>* mesh;
};

template<size_t D>
using EvaluateQuadratureResult = std::vector<EvaluateQuadraturePartition<D>>;

//! Inefficient helper function to evaluate quadrature
template<size_t D> MLHP_EXPORT
EvaluateQuadratureResult<D> evaluateQuadrature( const AbsQuadrature<D>& quadrature,
                                                const AbsMesh<D>& mesh,
                                                CellIndex icell,
                                                std::array<size_t, D> orders );

// Work in progress
template<size_t D>
class AbsQuadratureOnMesh : utilities::DefaultVirtualDestructor
{
public:

    using AnyCache = utilities::Cache<AbsQuadratureOnMesh<D>>;

    MLHP_EXPORT
    virtual ~AbsQuadratureOnMesh( ) { }

    virtual AnyCache initialize( ) const = 0;

    virtual void distribute( const MeshMapping<D>& mapping,
                             std::array<size_t, D> orders,
                             CoordinateList<D>& rst, 
                             CoordinateList<D>& normals,
                             std::vector<double>& weights, 
                             AnyCache& cache ) const = 0;
};

//! Helper return type for evaluateQuadrature(...) below
template<size_t D>
struct EvaluateQuadraturePartition2
{
    std::vector<std::array<double, D>> rst;
    std::vector<std::array<double, D>> xyz;
    std::vector<std::array<double, D>> normals;
    std::vector<double> weights;
    bool isgrid;

    CellIndex icell;
    const AbsMesh<D>* mesh;
};

template<size_t D>
using EvaluateQuadrature2Result = std::vector<EvaluateQuadraturePartition2<D>>;

//! Inefficient helper function to evaluate quadrature
template<size_t D> MLHP_EXPORT
EvaluateQuadrature2Result<D> evaluateQuadrature( const AbsQuadratureOnMesh<D>& quadrature,
                                                 const AbsMesh<D>& mesh,
                                                 CellIndex icell,
                                                 std::array<size_t, D> orders );

template<size_t D>
class StandardQuadrature final : public AbsQuadrature<D>
{
public:
    MLHP_EXPORT 
    QuadratureCache<D> initialize( ) const override;

    MLHP_EXPORT 
    size_t partition( const MeshMapping<D>& mapping,
                      QuadratureCache<D>& anyCache ) const override;
        
    MLHP_EXPORT 
    bool distribute( size_t ipartition,
                     std::array<size_t, D> orders,
                     CoordinateGrid<D>& rst,
                     CoordinateList<D>& xyzList,
                     std::vector<double>& weights,
                     QuadratureCache<D>& anyCache ) const override;

private:
    struct Cache;
};

template<size_t D>
class GridQuadrature final : public AbsQuadrature<D>
{
public:

    //! Subdivide each cell into the given number of quadrature partitions per direction
    MLHP_EXPORT
    GridQuadrature( std::array<size_t, D> nvoxels,
                    const spatial::ScalarFunction<D>& scaling = spatial::constantFunction<D>( 1.0 ) );
    
    //! Reduce number of voxels based on grid refinement level
    MLHP_EXPORT
    GridQuadrature( memory::vptr<const AbsHierarchicalGrid<D>> grid,
                    std::array<size_t, D> rootsubcells,
                    const spatial::ScalarFunction<D>& scaling = spatial::constantFunction<D>( 1.0 ) );
    
    //! Reduce number of voxels based on grid refinement level, limited to maxsubcells
    MLHP_EXPORT
    GridQuadrature( memory::vptr<const AbsHierarchicalGrid<D>> grid,
                    std::array<size_t, D> rootsubcells,
                    std::array<size_t, D> maxsubcells,
                    const spatial::ScalarFunction<D>& scaling = spatial::constantFunction<D>( 1.0 ) );

    MLHP_EXPORT 
    QuadratureCache<D> initialize( ) const override;

    MLHP_EXPORT 
    size_t partition( const MeshMapping<D>& mapping,
                      QuadratureCache<D>& anyCache ) const override;
        
    MLHP_EXPORT 
    bool distribute( size_t ipartition,
                     std::array<size_t, D> orders,
                     CoordinateGrid<D>& rst,
                     CoordinateList<D>& xyzList,
                     std::vector<double>& weights,
                     QuadratureCache<D>& anyCache ) const override;

private:
    struct Cache;

    std::function<std::array<size_t, D>( CellIndex icell )> nvoxels_;
    spatial::ScalarFunction<D> scaling_;
};

template<size_t D>
class SpaceTreeQuadrature final : public AbsQuadrature<D>
{
public:
    MLHP_EXPORT 
    SpaceTreeQuadrature( const ImplicitFunction<D>& function, 
                         double alpha, 
                         size_t depth,
                         size_t nseedpoints = 5 );

    MLHP_EXPORT 
    QuadratureCache<D> initialize( ) const override;

    MLHP_EXPORT 
    size_t partition( const MeshMapping<D>& mapping,
                      QuadratureCache<D>& anyCache ) const override;

    MLHP_EXPORT 
    bool distribute( size_t ipartition,
                     std::array<size_t, D> orders,
                     CoordinateGrid<D>& rst,
                     CoordinateList<D>& xyzList,
                     std::vector<double>& weights,
                     QuadratureCache<D>& anyCache ) const override;

    MLHP_EXPORT 
    void setNumberOfSeedPoints( size_t numberOfSeedPoints );

    //! For moment fitting
    MLHP_EXPORT 
    bool distributeForMomentFitting( size_t ipartition,
                                     std::array<size_t, D> orders,
                                     CoordinateGrid<D>& rst,
                                     CoordinateGrid<D>& weightsGrid,
                                     std::vector<double>& weights,
                                     QuadratureCache<D>& anyCache ) const;

private:
    ImplicitFunction<D> function_;
    size_t depth_;
    double alphaFCM_;
    size_t numberOfSeedPoints_;

    struct Cache;
};

template<size_t D>
class MomentFittingQuadrature final : public AbsQuadrature<D>
{
public:
    
    MLHP_EXPORT 
    MomentFittingQuadrature( const ImplicitFunction<D>& function, 
                             double alpha, 
                             size_t depth,
                             size_t nseedpoints = 5,
                             QuadratureOrderDeterminor<D> cutOrders = relativeQuadratureOrder<D>( 0, 2.0 ) );

    MLHP_EXPORT 
    QuadratureCache<D> initialize( ) const override;

    MLHP_EXPORT 
    size_t partition( const MeshMapping<D>& mapping,
                      QuadratureCache<D>& anyCache ) const override;

    MLHP_EXPORT 
    bool distribute( size_t ipartition,
                     std::array<size_t, D> orders,
                     CoordinateGrid<D>& rst,
                     CoordinateList<D>& xyzList,
                     std::vector<double>& weights,
                     QuadratureCache<D>& anyCache ) const override;

    MLHP_EXPORT 
    void setNumberOfSeedPoints( size_t numberOfSeedPoints );

private:
    ImplicitFunction<D> function_;
    SpaceTreeQuadrature<D> rhsPartitioner_;
    
    QuadratureOrderDeterminor<D> cutOrders_;

    struct Cache;
};

//! Not tested, pretty much only there to use marching cubes for quadrature
template<size_t D>
class CellmeshQuadrature final : public AbsQuadrature<D>
{
public:
    MLHP_EXPORT 
    CellmeshQuadrature( CellMeshCreator<D> meshCreator,
                        spatial::ScalarFunction<D> scaling = spatial::constantFunction<D>( 1.0 ) );

    MLHP_EXPORT 
    QuadratureCache<D> initialize( ) const override;

    MLHP_EXPORT 
    size_t partition( const MeshMapping<D>& mapping,
                      QuadratureCache<D>& anyCache ) const override;

    MLHP_EXPORT 
    bool distribute( size_t ipartition,
                     std::array<size_t, D> orders,
                     CoordinateGrid<D>& rst,
                     CoordinateList<D>& xyzList,
                     std::vector<double>& weights,
                     QuadratureCache<D>& anyCache ) const override;

private:
    CellMeshCreator<D> meshCreator_;
    spatial::ScalarFunction<D> scaling_;

    struct Cache;
};

template<size_t D>
class CachedQuadrature final : public AbsQuadrature<D>
{
public:
    using IntegrationOrders = std::function<std::array<size_t, D>( CellIndex ielement )>;

    MLHP_EXPORT 
    CachedQuadrature( const AbsMesh<D>& mesh, 
                      const std::vector<std::array<size_t, D>>& degrees,
                      const AbsQuadrature<D>& partitioner );

    MLHP_EXPORT 
    QuadratureCache<D> initialize( ) const override;

    MLHP_EXPORT 
    size_t partition( const MeshMapping<D>& mapping,
                      QuadratureCache<D>& anyCache ) const override;
        
    MLHP_EXPORT 
    bool distribute( size_t ipartition,
                     std::array<size_t, D> orders,
                     CoordinateGrid<D>& rst,
                     CoordinateList<D>& xyzList,
                     std::vector<double>& weights,
                     QuadratureCache<D>& anyCache ) const override;

private:
    struct CellCache;
    std::shared_ptr<std::vector<CellCache>> points_;

    std::vector<double> data_;
    std::vector<size_t> offsets_;
    std::vector<size_t> partitions_;
};

template<size_t D>
struct SubcellCache
{
    MeshMapping<D> globalMapping;       // Mapping from subcell to global (subcell -> cell -> global)
    QuadratureCache<D> quadratureCache; // quadrature cache used for this subcell
    size_t partitionOffset;             // The total number of partitions of previous subcells
};

//! Calls quadrature.partition(...) for a the given submappings, who map into the cell specified 
//! by globalMapping. For each submapping, there will be an entry in subcellData with all infor-
//! mation to call distribute. Since we don't know in advance how many partitions will be created 
//! for each subcell, mapToSubcell will tell us which subcell a partition index is associated to. 
//! Assume we have 3 subcells with 2, 3, and 1 partitions each, then subcellData.size( ) will be
//! 3 (with partitionOffset being 0, 2, and 5), and mapToSubcell will be [0, 0, 1, 1, 1, 2].
template<size_t D> MLHP_EXPORT
size_t cacheQuadratureCells( const AbsQuadrature<D>& quadrature,
                             const MeshMapping<D>& globalMapping,
                             std::span<const AbsMapping<D>*> submappings,
                             std::vector<SubcellCache<D>>& subcellData,
                             std::vector<size_t>& mapToSubcell );

//! Partitions conforming with another mesh (from e.g. a previous time step).
template<size_t D>
class MeshProjectionQuadrature final : public AbsQuadrature<D>
{
public:
    MLHP_EXPORT 
    MeshProjectionQuadrature( memory::vptr<const AbsHierarchicalGrid<D>> otherMesh,
                              memory::vptr<const AbsQuadrature<D>> partitioner,
                              size_t maxdepth = NoValue<size_t> );

    MLHP_EXPORT 
    QuadratureCache<D> initialize( ) const override;

    MLHP_EXPORT 
    size_t partition( const MeshMapping<D>& mapping,
                      QuadratureCache<D>& anyCache) const override;
             
    MLHP_EXPORT 
    bool distribute( size_t ipartition,
                     std::array<size_t, D> orders,
                     CoordinateGrid<D>& rst,
                     CoordinateList<D>& xyzList,
                     std::vector<double>& weights,
                     QuadratureCache<D>& anyCache ) const override;

    //! Returns full Index in other mesh!
    MLHP_EXPORT 
    CellIndex distribute( size_t ipartition,
                          std::array<size_t, D> orders,
                          CoordinateGrid<D>& thisRstGrid,
                          CoordinateGrid<D>& otherRstGrid,
                          CoordinateList<D>& xyzList,
                          std::vector<double>& weights,
                          QuadratureCache<D>& anyCache) const;

public:
    memory::vptr<const AbsHierarchicalGrid<D>> otherMesh_;
    memory::vptr<const AbsQuadrature<D>> partitioner_;
    size_t maxdepth_;

    struct Cache;
};

} // mlhp

#endif // MLHP_CORE_PARTITIONING_HPP
