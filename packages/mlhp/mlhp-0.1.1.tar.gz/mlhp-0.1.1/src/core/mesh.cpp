// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/utilities.hpp"
#include "mlhp/core/topologycore.hpp"
#include "mlhp/core/mesh.hpp"
#include "mlhp/core/ndarray.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/kdtree.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/algorithm.hpp"
#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/derivativeHelper.hpp"
#include "mlhp/core/dense.hpp"
#include "mlhp/core/refinement.hpp"

#include <numeric>
#include <cmath>
#include <map>

namespace mlhp
{

template<size_t D>
CellType AbsGrid<D>::cellType( CellIndex ) const
{
    return CellType::NCube;
}

template<size_t D>
void AbsGrid<D>::neighbours( CellIndex cell, size_t face, std::vector<MeshCellFace>& target ) const
{
    auto [normal, side] = normalAxisAndSide( face );

    if( auto index = neighbour( cell, normal, side ); index != NoCell )
    {
        target.push_back( { index, ncubeFaceIndex( normal, 1 - side ) } );
    }
}

template<size_t D>
std::unique_ptr<AbsMapping<D, D - 1>> AbsGrid<D>::createInterfaceMapping( ) const
{
    return std::make_unique<FaceMapping<D>>( CellType::NCube, 0 );
}

template<size_t D>
void AbsGrid<D>::prepareInterfaceMappings( MeshCellFace face0,
                                           MeshCellFace face1,
                                           AbsMapping<D, D - 1>& mapping0,
                                           AbsMapping<D, D - 1>& mapping1 ) const
{
    MLHP_CHECK_DBG( dynamic_cast<FaceMapping<D>*>( &mapping0 ) != nullptr &&
                    dynamic_cast<FaceMapping<D>*>( &mapping1 ) != nullptr,
                    "Invalid mapping type (not convertible to FaceMapping)." );

    MLHP_CHECK_DBG( face0.second / 2 == face0.second / 2 && 
                    face0.second % 2 != face1.second % 2, 
                    "Invalid faces in prepareInterfaceMappings." );

    static_cast<FaceMapping<D>*>( &mapping0 )->resetNCube( face0.second, { }, array::make<D>( 1.0 ) );
    static_cast<FaceMapping<D>*>( &mapping1 )->resetNCube( face1.second, { }, array::make<D>( 1.0 ) );
}

template<size_t D>
MeshUniquePtr<D> AbsGrid<D>::clone( ) const
{
    return cloneGrid( );
}

template<size_t D>
CartesianGrid<D>::CartesianGrid( const CoordinateGrid<D>& indexVectors ) :
    coordinates_( indexVectors )
{
    auto sizes = array::subtract<size_t>( array::elementSizes( indexVectors ), 1 );

    MLHP_CHECK( array::product( sizes ) < NoCell,
                "CellIndexType too small to represent number of cells." );

    numberOfCells_ = array::convert<CellIndex>( sizes );
    strides_ = nd::stridesFor( numberOfCells_ );
        
    for( size_t axis = 0; axis < D; ++axis )
    {
        MLHP_CHECK( coordinates_[axis].size( ) >= 2, 
            "Grid needs least two coordinates per direction." );

        for( size_t i = 0; i + 1 < coordinates_[axis].size( ); ++i )
        {
            MLHP_CHECK( coordinates_[axis][i] < coordinates_[axis][i + 1],
                        "Grid coordinates need to be unique and sorted." );
        }
    }
}

template<size_t D>
CartesianGrid<D>::CartesianGrid( std::array<size_t, D> numberOfCells,
                                 std::array<double, D> lengths,
                                 std::array<double, D> origin ) :
    CartesianGrid( spatial::cartesianTickVectors( numberOfCells, lengths, origin ) )
{ }

template<size_t D>
CoordinateGrid<D> CartesianGrid<D>::coordinates( ) const
{
    return coordinates_;
}

template<size_t D>
CellIndex CartesianGrid<D>::ncells( ) const
{
    return static_cast<CellIndex>( array::product( numberOfCells_ ) );
}

template<size_t D>
CellIndex CartesianGrid<D>::neighbour( CellIndex cell, size_t axis, size_t side ) const
{
    auto index = nd::unravelWithStrides( cell, strides_, axis );

    if( side == 0 && index > 0 )
    {
        return cell - strides_[axis];
    }
    else if( side == 1 && index + 1 < numberOfCells_[axis] )
    {
        return cell + strides_[axis];
    }
    else
    {
        return NoCell;
    }
}

template<size_t D>
std::array<CellIndex, D> CartesianGrid<D>::gridIndices( CellIndex icell ) const
{
    return nd::unravelWithStrides( icell, strides_ );
}

template<size_t D>
spatial::BoundingBox<D> CartesianGrid<D>::boundingBox( ) const
{
    std::array<double, D> x0, x1;

    for( size_t axis = 0; axis < D; ++axis )
    {
        x0[axis] = coordinates_[axis].front( );
        x1[axis] = coordinates_[axis].back( );
    }

    return { x0, x1 };
}

template<size_t D>
spatial::BoundingBox<D> CartesianGrid<D>::boundingBox( CellIndex cellIndex ) const
{
    MLHP_CHECK_DBG( cellIndex < ncells( ), "Invalid cell index." );

    auto ijk = gridIndices( cellIndex );

    std::array<double, D> min, max;

    for( size_t axis = 0; axis < D; ++axis )
    {
        min[axis] = coordinates_[axis][ijk[axis]];
        max[axis] = coordinates_[axis][ijk[axis] + 1];
    }

    return { min, max };
}

template<size_t D>
size_t CartesianGrid<D>::memoryUsage( ) const
{
    size_t memory = 0;

    for( size_t axis = 0; axis < D; ++axis )
    {
        memory += utilities::vectorInternalMemory( coordinates_[axis] );
    }

    return memory;
}

template<size_t D>
MeshMapping<D> CartesianGrid<D>::createMapping( ) const
{
    auto mapping = MeshMapping<D> { };

    mapping.mapping = std::make_shared<CartesianMapping<D>>( );
    mapping.mesh = this;

    return mapping;
}

template<size_t D>
void CartesianGrid<D>::prepareMapping( CellIndex cell,
                                       MeshMapping<D>& mapping ) const
{
    auto& cartesianMapping = dynamic_cast<CartesianMapping<D>&>( *mapping.mapping.get( ) );

    cartesianMapping.resetBounds( boundingBox( cell ) );

    mapping.icell = cell;
}

template<size_t D>
GridUniquePtr<D> CartesianGrid<D>::cloneGrid( ) const
{
    return std::make_unique<CartesianGrid<D>>( *this );
}

template<size_t D>
struct FunctionBackwardMapping : public AbsBackwardMapping<D>
{
    using Type = void( std::array<double, D> xyz, BackwardMapVector<D>& target, double eps );

    FunctionBackwardMapping( const AbsMesh<D>* mesh, std::function<Type>&& map ) : 
        AbsBackwardMapping<D>( mesh ), map_ { std::move( map ) } 
    { }

    void mapInternal( std::array<double, D> xyz, BackwardMapVector<D>& target, double eps ) override
    {
        map_( xyz, target, eps );
    }

    std::function<Type> map_;
};

template<size_t D>
BackwardMappingFactory<D> CartesianGrid<D>::createBackwardMappingFactory( ) const
{
    return [this]( )
    {
        auto map = [this]( std::array<double, D> xyz, BackwardMapVector<D>& target, [[maybe_unused]] double eps )
        {
            std::array<double, D> rst;
            CellIndex index = 0;
        
            for( size_t axis = 0; axis < D; ++axis )
            {
                const auto& positions = this->coordinates_[axis];
        
                double t0 = positions.front( );
                double tn = positions.back( );
        
                double tolerance = ( tn - t0 ) * 1e-13;
        
                //  Completely inside
                if( xyz[axis] > t0 + tolerance && xyz[axis] < tn - tolerance )
                {
                    auto it = std::lower_bound( positions.begin( ), positions.end( ), xyz[axis] );
        
                    MLHP_CHECK( it != positions.end( ) && it != positions.begin( ), "Internal error in backward mapping." );
        
                    auto i = static_cast<CellIndex>( std::distance( positions.begin( ), it ) - 1 );
        
                    rst[axis] = utilities::mapToLocal1( positions[i], positions[i + 1], xyz[axis] );
        
                    index += i * strides_[axis];
                }
                // Completely outside
                else if( xyz[axis] < t0 - tolerance || xyz[axis] > tn + tolerance )
                {
                    return;
                }
                // In tolerance of leftmost coordinate
                else if( xyz[axis] < t0 + tolerance )
                {
                    rst[axis] = utilities::mapToLocal1( t0, positions[1], xyz[axis] );
                }
                // In tolerance of rightmost coordinate
                else
                {
                    rst[axis] = utilities::mapToLocal1( positions[positions.size( ) - 2], tn, xyz[axis] );
        
                    index += strides_[axis] * ( numberOfCells_[axis] - 1 );
                }
        
            } // for axis
        
            target.push_back( std::make_pair( index, rst ) );
        };

        return std::make_unique<FunctionBackwardMapping<D>>( this, map );
    };
}

template<size_t D>
CellType AbsHierarchicalGrid<D>::cellType( CellIndex ) const
{
    return CellType::NCube;
}

template<size_t D>
void AbsHierarchicalGrid<D>::neighbours( CellIndex leafIndex, 
                                         size_t face,
                                         std::vector<MeshCellFace>& target ) const
{
    size_t normal, side;
    std::tie( normal, side ) = normalAxisAndSide( face );

    if( auto index = neighbour( fullIndex( leafIndex ), normal, side ); index != NoCell )
    {
        auto appendLeavesOnSide = [&]( auto&& self, CellIndex icell ) -> void
        {
            if( this->child( icell, { } ) != NoCell )
            {
                for( size_t i = 0; i < utilities::binaryPow<size_t>( D - 1 ); ++i )
                {
                    auto ij = nd::binaryUnravel<LocalPosition, D - 1>( i );
                    auto ijk = array::insert( ij, normal, static_cast<LocalPosition>( side ) );

                    self( self, this->child( icell, ijk ) );
                }
            }
            else
            {
                target.push_back( { this->leafIndex( icell ), ncubeFaceIndex( normal, 1 - side ) } );
            }
        };

        appendLeavesOnSide( appendLeavesOnSide, index );
    }
}

template<size_t D>
CellLocalCoordinates<D> AbsHierarchicalGrid<D>::mapToLeaf( CellIndex fullIndex, std::array<double, D> rst ) const
{
    auto result = CellLocalCoordinates<D> { fullIndex, rst };
    auto tmp = BackwardMapResult<D> { };

    while( ( tmp = mapToChild( result.first, result.second ) ) )
    {
        result = *tmp;
    }

    result.first = this->leafIndex( result.first );

    return result;
}

template<size_t D>
MeshUniquePtr<D> AbsHierarchicalGrid<D>::clone( ) const
{
    return cloneGrid( );
}

namespace
{

template<size_t D>
void refineWithMask( AbsHierarchicalGrid<D>& grid,
                     const std::vector<std::uint8_t>& mask,
                     CellIndex offset )
{
    auto indices = algorithm::forwardIndexMap<CellIndex>( mask );

    for( auto& index : indices )
    {
        index = grid.leafIndex( index + offset );
    }

    grid.refine( indices );
}

} // namespace

template<size_t D>
void AbsHierarchicalGrid<D>::refine( const RefinementFunction<D>& strategy )
{
    auto begin = CellIndex { 0 };
    auto end = nfull( );

    while( begin != end )
    {
        auto refinementMask = std::vector<std::uint8_t>( end - begin, 0 );

        [[maybe_unused]] 
        auto chunksize = parallel::clampChunksize( refinementMask.size( ), 6, 1 );

        #pragma omp parallel 
        {
            auto mapping = this->createMapping( );

            #pragma omp for schedule(dynamic, chunksize)
            for( std::int64_t index = 0; index < static_cast<std::int64_t>( end - begin ); ++index )
            {
                if( auto icell = static_cast<CellIndex>( index ); isLeaf( begin + icell ) )
                {
                    this->prepareMapping( leafIndex( begin + icell ), mapping );

                    refinementMask[icell] = strategy( mapping, refinementLevel( begin + icell ) );
                }
            }
        }

        refineWithMask( *this, refinementMask, begin );

        begin = end;
        end = nfull( );
    }
}

template<size_t D>
RefinedGrid<D>::RefinedGrid( const GridSharedPtr<D>& baseGrid ) :
    baseGrid_( baseGrid )
{
    resetDataStructure( );
}  

template<size_t D>
void RefinedGrid<D>::refine( const std::vector<CellIndex>& leafIndices )
{
    constexpr auto twoPowN = utilities::integerPow<CellIndex>( 2, D );

    auto originalSize = static_cast<CellIndex>( parentIndex_.size( ) );
    auto numberOfCellsToRefine = static_cast<CellIndex>( leafIndices.size( ) );

    parentIndex_.resize( originalSize + numberOfCellsToRefine * twoPowN );

    for( CellIndex icell = 0; icell < numberOfCellsToRefine; ++icell )
    {
        auto* beginChildren = parentIndex_.data( ) + originalSize + icell * twoPowN;
        auto* endChildren = beginChildren + twoPowN;

        std::fill<CellIndex*, CellIndex>( beginChildren, endChildren, fullIndex( leafIndices[icell] ) );
    } 

    rebuildDataStructure( );
}

template<size_t D>
void RefinedGrid<D>::resetDataStructure( )
{
    auto basencells = baseGrid_->ncells( );

    parentIndex_.resize( basencells );
    isLeaf_.resize( basencells );
    fullIndex_.resize( basencells );
    leafIndexOrChild_.resize( basencells );

    std::fill( parentIndex_.begin( ), parentIndex_.end( ), NoCell );
    std::fill( isLeaf_.begin( ), isLeaf_.end( ), true );
    std::iota( fullIndex_.begin( ), fullIndex_.end( ), CellIndex { 0 } );
    std::iota( leafIndexOrChild_.begin( ), leafIndexOrChild_.end( ), CellIndex { 0 } );
}

template<size_t D>
void RefinedGrid<D>::rebuildDataStructure( )
{
    isLeaf_ = topology::leafMask( parentIndex_ );

    auto leafCount = CellIndex { 0 };
    auto nint = static_cast<std::int64_t>( isLeaf_.size( ) );

    #pragma omp parallel for schedule(static) reduction(+:leafCount)
    for( std::int64_t ii = 0; ii < nint; ++ii )
    {
        leafCount += isLeaf_[static_cast<size_t>( ii )];
    }

    fullIndex_.resize( leafCount );
    leafIndexOrChild_.resize( isLeaf_.size( ) );

    CellIndex index = 0;

    for( CellIndex i = 0; i < isLeaf_.size( ); ++i )
    {
        if( isLeaf_[i] )
        {
            fullIndex_[index] = i;
            leafIndexOrChild_[i] = index;
            index += 1;
        }
        else
        {
            leafIndexOrChild_[i] = NoCell;
        }

        if( auto parent = parentIndex_[i]; parent != NoCell )
        {
            leafIndexOrChild_[parent] = std::min( i, leafIndexOrChild_[parent] );
        }
    }
}

template<size_t D>
CellIndex RefinedGrid<D>::child( CellIndex cell, PositionInParent<D> position ) const
{
    MLHP_CHECK_DBG( cell < nfull( ), "Index out of range." );

    if( !isLeaf_[cell] )
    {
        return leafIndexOrChild_[cell] + nd::binaryRavel<CellIndex>( position );
    }
    else
    {
        return NoCell;
    }
}

template<size_t D>
CellIndex RefinedGrid<D>::neighbour( CellIndex cell, size_t axis, size_t side ) const
{
    MLHP_CHECK_DBG( cell < nfull( ), "Index out of range." );

    // Cell is root: Ask base grid
    if( auto parent = parentIndex_[cell]; parent == NoCell )
    {
        return baseGrid_->neighbour( cell, axis, side );
    }
    // Neighbour has same parent: Return with offset from this cell
    else if( auto position = localPosition( cell ); position[axis] != side )
    {
        auto distance = utilities::binaryPow<CellIndex>( D - 1 - axis );

        return side == 0 ? cell - distance : cell + distance;
    }
    // Neighbour has different parent: Call parent
    else
    {
        auto parentNeighbour = neighbour( parent, axis, side );

        if( parentNeighbour == NoCell || isLeaf_[parentNeighbour] )
        {
            return parentNeighbour;
        }
        else
        {
            return child( parentNeighbour, array::setEntry( position, axis, 
                static_cast<LocalPosition>( 1 - side ) ) );
        }
    }
}

template<size_t D>
HierarchicalGridUniquePtr<D> RefinedGrid<D>::cloneGrid( ) const
{
    return std::make_unique<RefinedGrid<D>>( *this );
}

template<size_t D>
size_t RefinedGrid<D>::memoryUsage( ) const
{
    size_t memory = utilities::vectorInternalMemory( isLeaf_, parentIndex_, fullIndex_, leafIndexOrChild_ );

    return memory + baseGrid_->memoryUsage( );
}

template<size_t D>
PositionInParent<D> RefinedGrid<D>::localPosition( CellIndex fullIndex ) const
{
    if( auto parent = parentIndex_[fullIndex]; parent != NoCell )
    {
        return nd::binaryUnravel<LocalPosition, D>( fullIndex - leafIndexOrChild_[parent] );
    }
    else
    {
        return array::make<D>( NoLocalPosition );
    }
}

template<size_t D>
bool RefinedGrid<D>::isLeaf( CellIndex fullIndex ) const
{
    return isLeaf_[fullIndex];
}

template<size_t D>
CellIndex RefinedGrid<D>::parent( CellIndex fullIndex ) const
{
    return parentIndex_[fullIndex];
}

template<size_t D>
RefinementLevel RefinedGrid<D>::refinementLevel( CellIndex fullIndex ) const
{
    return parentIndex_[fullIndex] != NoCell ? refinementLevel( parentIndex_[fullIndex] ) + 1 : 0;
}

template<size_t D>
CellIndex RefinedGrid<D>::fullIndex( CellIndex leafIndex ) const
{
    MLHP_EXPECTS_DBG( leafIndex < fullIndex_.size( ) )

    return fullIndex_[leafIndex];
}

template<size_t D>
CellIndex RefinedGrid<D>::leafIndex( CellIndex fullIndex ) const
{
    MLHP_EXPECTS_DBG( fullIndex < leafIndexOrChild_.size( ) )
    MLHP_EXPECTS_DBG( isLeaf_[fullIndex] )

    return leafIndexOrChild_[fullIndex];
}

template<size_t D>
BackwardMapResult<D> RefinedGrid<D>::mapToChild( CellIndex fullIndex, std::array<double, D> rst ) const
{
    auto result = BackwardMapResult<D> { };

    if( !this->isLeaf( fullIndex ) )
    {
        auto position = PositionInParent<D> { };

        for( size_t axis = 0; axis < D; ++axis )
        {
            position[axis] = rst[axis] > 0.0;

            rst[axis] *= 2.0;
            rst[axis] += position[axis] ? -1.0 : 1.0;
        }

        result = { child( fullIndex, position ), rst };
    }

    return result;
}

template<size_t D>
BackwardMappingFactory<D> RefinedGrid<D>::createBackwardMappingFactory( ) const
{
    return [this, baseFactory = baseGrid_->createBackwardMappingFactory( )]( )
    { 
        auto baseMapping = std::shared_ptr { baseFactory( ) };

        auto map = [=, this]( std::array<double, D> xyz, BackwardMapVector<D>& target, double eps )
        {
            auto size = target.size( );
            
            baseMapping->map( xyz, target, eps );

            for( size_t iroot = size; iroot < target.size( ); ++iroot )
            {
                target[iroot] = this->mapToLeaf( target[iroot].first, target[iroot].second );
            }
        };

        return std::make_unique<FunctionBackwardMapping<D>>( this, map ); 
    };
}

namespace
{
    
template<size_t D>
struct RefinedGridMappingCache
{
    MeshMapping<D> baseMapping;
    CartesianMapping<D> hierarchyMapping;
    ConcatenatedMapping<D, D, D> mapping;
};

} // namespace

template<size_t D>
MeshMapping<D> RefinedGrid<D>::createMapping( ) const
{
    auto cache = std::make_shared<RefinedGridMappingCache<D>>( );

    cache->baseMapping = baseGrid_->createMapping( );
    cache->mapping.localMapping = &cache->hierarchyMapping;
    cache->mapping.globalMapping = &cache->baseMapping;
    
    auto mapping = MeshMapping<D> { };

    mapping.mapping = &cache->mapping;
    mapping.mesh = this;
    mapping.cache = std::move( cache );

    return mapping;
}

template<size_t D>
void RefinedGrid<D>::prepareMapping( CellIndex cell,
                                     MeshMapping<D>& mapping ) const
{
    mapping.icell = cell;

    auto [rootMapping, rootIndex] = mesh::mapToRoot( *this, fullIndex( cell ) );

    auto& cache = utilities::cast<std::shared_ptr<RefinedGridMappingCache<D>>>( mapping.cache );
    
    cache->hierarchyMapping = rootMapping;

    baseGrid_->prepareMapping( rootIndex, cache->baseMapping );
}

template<size_t D>
std::unique_ptr<AbsMapping<D, D - 1>> RefinedGrid<D>::createInterfaceMapping( ) const
{
    return std::make_unique<FaceMapping<D>>( CellType::NCube, 0 );
}

template<size_t D>
void RefinedGrid<D>::prepareInterfaceMappings( MeshCellFace face0,
                                               MeshCellFace face1,
                                               AbsMapping<D, D - 1>& mapping0,
                                               AbsMapping<D, D - 1>& mapping1 ) const
{
    MLHP_CHECK_DBG( dynamic_cast<FaceMapping<D>*>( &mapping0 ) != nullptr &&
                    dynamic_cast<FaceMapping<D>*>( &mapping1 ) != nullptr,
                    "Invalid mapping type (not convertible to FaceMapping)." );
    
    auto faceCoarse = MeshCellFace { this->fullIndex( face0.first ), face0.second };
    auto faceFine = MeshCellFace { this->fullIndex( face1.first ), face1.second };

    auto levelCoarse = this->refinementLevel( faceCoarse.first );
    auto levelFine = this->refinementLevel( faceFine.first );

    auto mappingCoarse = static_cast<FaceMapping<D>*>( &mapping0 );
    auto mappingFine = static_cast<FaceMapping<D>*>( &mapping1 );

    if( levelCoarse > levelFine )
    {
        std::swap( faceCoarse, faceFine );
        std::swap( mappingCoarse, mappingFine );
        std::swap( levelCoarse, levelFine );
    }

    auto center = array::make<D>( 0.0 );
    auto halfwidth = array::make<D>( 1.0 );

    for( auto ifull = faceFine.first; levelFine > levelCoarse; --levelFine )
    {
        auto position = this->localPosition( ifull );
        ifull = this->parent( ifull );

        for( size_t axis = 0; axis < D; ++axis )
        {
            center[axis] = 0.5 * ( center[axis] + 2.0 * position[axis] - 1.0 );
            halfwidth[axis] *= 0.5;
        }
    }

    mappingCoarse->resetNCube( faceCoarse.second, center, halfwidth  );
    mappingFine->resetNCube( faceFine.second, { }, array::make<D>( 1.0 ) );
}

template<size_t D>
UnstructuredMesh<D>::UnstructuredMesh( CoordinateList<D>&& vertices,
                                       std::vector<size_t>&& connectivity,
                                       std::vector<size_t>&& offsets,
                                       bool filterVertices,
                                       bool reorderVertices ) :
    vertices_ { std::move( vertices ) }, connectivity_ { std::move( connectivity ) },
    offsets_ { std::move( offsets ) }
{
    if( offsets_.empty( ) )
    {
        offsets_.push_back( 0 );
    }

    types_.resize( offsets_.size( ) - 1 );

    // https://en.wikipedia.org/wiki/Hypercube#Faces
    // https://en.wikipedia.org/wiki/Simplex#Elements
    for( CellIndex icell = 0; icell < types_.size( ); ++icell )
    {
        auto nvertices = offsets_[icell + 1] - offsets_[icell];

        types_[icell] = nvertices == D + 1 ? CellType::Simplex : CellType::NCube;
    }
    
    topology::checkConsistency<D>( vertices_, connectivity_, offsets_, types_ );
    
    if( filterVertices )
    {
        topology::filterVertices<D>( vertices_, connectivity_ );    
    }

    if( reorderVertices )
    {
        topology::reorderVertices<D>( vertices_, connectivity_, offsets_, types_ );
    }

    neighbours_ = topology::neighbours<D>( connectivity_, offsets_, types_ );
}

template<size_t D>
CellIndex UnstructuredMesh<D>::ncells( ) const
{
    return static_cast<CellIndex>( offsets_.size( ) - 1 );
}

template<size_t D>
CellType UnstructuredMesh<D>::cellType( CellIndex icell ) const
{
    MLHP_EXPECTS_DBG( icell < ncells( ) );

    return types_[icell];
}

template<size_t D>
size_t UnstructuredMesh<D>::nvertices( ) const
{
    return vertices_.size( );
}

template<size_t D>
size_t UnstructuredMesh<D>::vertexIndex( CellIndex icell, size_t ivertex ) const
{
    return connectivity_[offsets_[icell] + ivertex]; 
}

template<size_t D>
std::array<double, D> UnstructuredMesh<D>::vertex( size_t gvertex ) const
{
    return vertices_[gvertex];
}

template<size_t D>
std::array<double, D> UnstructuredMesh<D>::vertex( CellIndex icell, size_t lvertex ) const
{
    return vertex( vertexIndex( icell, lvertex ) );
}

template<size_t D>
size_t UnstructuredMesh<D>::nvertices( CellIndex icell ) const
{
    MLHP_EXPECTS_DBG( icell < ncells( ) );

    return offsets_[icell + 1] - offsets_[icell];
}

template<size_t D>
void UnstructuredMesh<D>::neighbours( CellIndex icell,
                                      size_t iface, 
                                      std::vector<MeshCellFace>& target ) const
{
    MLHP_EXPECTS_DBG( icell < ncells( ) );

    auto [jcell, jface] = utilities::linearizedSpan( neighbours_, icell )[iface];
    
    if( jcell != NoCell )
    {
        target.push_back( { jcell, static_cast<size_t>( jface ) } );
    }
}

template<size_t D>
MeshMapping<D> UnstructuredMesh<D>::createMapping( ) const
{
    auto mapping = MeshMapping<D> { };

    mapping.mesh = this;
    mapping.icell = NoCell;
    mapping.cache = std::variant<NCubeMapping<D>, SimplexMapping<D>> { };

    return mapping;
}

template<size_t D>
void UnstructuredMesh<D>::prepareMapping( CellIndex icell,
                                          MeshMapping<D>& mapping ) const
{
    MLHP_EXPECTS_DBG( icell < ncells( ) );

    auto& cache = utilities::cast<std::variant<NCubeMapping<D>, SimplexMapping<D>>>( mapping.cache );

    auto create = [&, this]<typename Mapping>( )
    {
        auto corners = CoordinateArray<D, Mapping::nvertices> { };

        for( size_t i = 0; i < Mapping::nvertices; ++i )
        {
            corners[i] = vertices_[vertexIndex( icell, i )];
        }
            
        cache = Mapping { corners };
        mapping.mapping = &std::get<Mapping>( cache );
        mapping.type = mapping.mapping->type;
        mapping.icell = icell;
    };

    if( auto type = cellType( icell ); type == CellType::NCube )
    {
        create.template operator()<NCubeMapping<D>>( );
    }
    else if( type == CellType::Simplex )
    {
        create.template operator()<SimplexMapping<D>>( );
    }
    else
    {
        MLHP_NOT_IMPLEMENTED;
    }
}

template<size_t D>
AbsBackwardMapping<D>::AbsBackwardMapping( const AbsMesh<D>* mesh ) :
    mesh_ { mesh }
{ }

template<size_t D>
void AbsBackwardMapping<D>::map( std::array<double, D> xyz,
                                 BackwardMapVector<D>& target, 
                                 double epsilon )
{
    mapInternal( xyz, target, epsilon );
}

template<size_t D>
BackwardMapResult<D> AbsBackwardMapping<D>::map( std::array<double, D> xyz,
                                                 double epsilon )
{
    mapInternal( xyz, utilities::resize0( target_ ), epsilon );

    return target_.empty( ) ? std::nullopt : std::optional { target_[0] };
}

template<size_t D>
const AbsMesh<D>& AbsBackwardMapping<D>::mesh( ) const
{
    return *mesh_;
}

template<size_t D>
std::optional<std::array<double, D>> mapBackward( const AbsMapping<D>& mapping,
                                                  std::array<double, D> xyz,
                                                  double eps )
{
    auto rst = std::array<double, D> { };

    for( size_t it = 0; it < 50; ++it )
    {
        auto [xi, J] = map::withJ( mapping, rst );

        auto res = xi - xyz;
        auto normSquared = spatial::normSquared( res );

        if( normSquared <= eps * eps )
        {
            return rst;
        }
                
        auto perm = std::array<size_t, D> { };
        auto incr = std::array<double, D> { };

        linalg::solve( J, perm, res, incr );

        rst = rst - incr;
    }

    return std::nullopt;
}

template<size_t D>
struct BackwardMapping : public AbsBackwardMapping<D>
{
    BackwardMapping( const UnstructuredMesh<D>* mesh,
                     std::shared_ptr<KdTree<D>>&& tree_ ) :
        AbsBackwardMapping<D>( mesh ), tree { tree_ }, forwardMapping { mesh->createMapping( ) }
    { }

    void mapInternal( std::array<double, D> xyz, BackwardMapVector<D>& target, double epsilon ) override
    {
        auto maxwidth = array::maxElement( tree->boundingBox( )[1] - tree->boundingBox( )[0] );
        auto eps = maxwidth * 100.0 * std::numeric_limits<double>::epsilon( );

        kdtree::accumulateItems( *tree, spatial::boundingBoxAt( xyz, eps ), utilities::resize0( cells ) );

        for( auto ii : cells )
        {
            this->mesh( ).prepareMapping( static_cast<CellIndex>( ii ), forwardMapping );

            auto rst = mapBackward( forwardMapping, xyz, eps );

            MLHP_CHECK( rst, "Backward mapping did not converge." );

            if( topology::isinside( forwardMapping.type, *rst, epsilon ) )
            {
                target.push_back( std::pair { static_cast<CellIndex>( ii ), *rst } );
            }
        }
    }
    
    // Shared data
    std::shared_ptr<KdTree<D>> tree;

    // Local data
    MeshMapping<D> forwardMapping;
    std::vector<size_t> cells = { };
};

template<size_t D>
BackwardMappingFactory<D> UnstructuredMesh<D>::createBackwardMappingFactory( ) const
{
    auto provider = mesh::boundingBoxProvider( *this );
    auto kdtree = buildKdTree( provider, this->boundingBox( ) );

    return [this, tree = std::make_shared<KdTree<D>>( std::move( kdtree ) )]( )
    {
        return std::make_unique<BackwardMapping<D>>( this, std::shared_ptr { tree } );
    };
}

template<size_t D>
std::unique_ptr<AbsMapping<D, D - 1>> UnstructuredMesh<D>::createInterfaceMapping( ) const
{
    MLHP_NOT_IMPLEMENTED;
}

template<size_t D>
void UnstructuredMesh<D>::prepareInterfaceMappings( [[maybe_unused]] MeshCellFace face0,
                                                 [[maybe_unused]] MeshCellFace face1,
                                                 [[maybe_unused]] AbsMapping<D, D - 1>& mapping0,
                                                 [[maybe_unused]] AbsMapping<D, D - 1>& mapping1 ) const
{
    MLHP_NOT_IMPLEMENTED;
}

template<size_t D>
size_t UnstructuredMesh<D>::memoryUsage( ) const
{
    return utilities::vectorInternalMemory( vertices_, connectivity_, 
        offsets_, neighbours_.first, neighbours_.second );
}

template<size_t D>
spatial::BoundingBox<D> UnstructuredMesh<D>::boundingBox( ) const
{
    return spatial::boundingBox<D>( vertices_ );
}

template<size_t D>
spatial::BoundingBox<D> UnstructuredMesh<D>::boundingBox( CellIndex icell ) const
{
    auto bounds = spatial::makeEmptyBoundingBox<D>( );
    auto nvertices_ = nvertices( icell );

    for( size_t ivertex = 0; ivertex < nvertices_; ++ivertex )
    {
        auto iglobal = vertexIndex( icell, ivertex );

        // Without this check clang++ versions <= 15 won't work ...
        MLHP_CHECK( iglobal < nvertices( ), "Invalid vertex index." );

        bounds = spatial::boundingBoxOr( bounds, vertices_[iglobal] );
    }

    return bounds;
}

template<size_t D>
MeshUniquePtr<D> UnstructuredMesh<D>::clone( ) const
{
    return std::make_unique<UnstructuredMesh<D>>( *this );
}


template<size_t D>
AggregateMesh<D>::AggregateMesh( const std::vector<MeshPtr>& meshes ) :
    meshes_( meshes ), offsets_( meshes.size( ) + 1, 0 )
{
    for( size_t imesh = 0; imesh < meshes.size( ); ++imesh )
    {
        offsets_[imesh + 1] = offsets_[imesh] + meshes[imesh]->ncells( );
    }
}

template<size_t D>
AggregateMesh<D>::AggregateMesh( std::initializer_list<MeshPtr> list ) :
    AggregateMesh( std::vector<MeshPtr>( list ) )
{ }

template<size_t D>
std::pair<size_t, CellIndex> AggregateMesh<D>::findMeshIndex( CellIndex icell ) const
{
    auto it = std::upper_bound( offsets_.begin( ), offsets_.end( ), icell );

    MLHP_CHECK( it < offsets_.end( ) && it > offsets_.begin( ), "Cell index out of bounds.");

    auto meshIndex = static_cast<size_t>( std::distance( offsets_.begin( ) + 1, it ) );
    auto cellIndex = icell - *( it - 1 );

    return std::pair { meshIndex, cellIndex };
}

template<size_t D>
CellType AggregateMesh<D>::cellType( CellIndex icell ) const
{
    auto [imesh, jcell] = findMeshIndex( icell );

    return meshes_[imesh]->cellType( jcell );
}

template<size_t D>
void AggregateMesh<D>::neighbours( CellIndex icell, size_t iface, std::vector<MeshCellFace>& target ) const
{
    auto [imesh, jcell] = findMeshIndex( icell );

    auto begin = target.size( );

    meshes_[imesh]->neighbours( jcell, iface, target );

    for( size_t ineighbour = begin; ineighbour < target.size( ); ++ineighbour )
    {
        target[ineighbour].first += offsets_[imesh];
    }
}

template<size_t D>
MeshMapping<D> AggregateMesh<D>::createMapping( ) const
{
    auto mappings = std::make_shared<std::vector<MeshMapping<D>>>( );

    for( size_t imesh = 0; imesh < meshes_.size( ); ++imesh )
    {
        mappings->push_back( std::move( meshes_[imesh]->createMapping( ) ) );
    }

    auto meshMapping = MeshMapping<D> { };

    meshMapping.mesh = this;
    meshMapping.cache = std::move( mappings );

    return meshMapping;
}

template<size_t D>
void AggregateMesh<D>::prepareMapping( CellIndex icell, MeshMapping<D>& mapping ) const
{
    auto& mappings = utilities::cast<std::shared_ptr<std::vector<MeshMapping<D>>>>( mapping.cache );

    auto [imesh, jcell] = findMeshIndex( icell );

    auto& meshMapping = mappings->at( imesh );

    meshes_[imesh]->prepareMapping( jcell, meshMapping );

    mapping.icell = icell;
    mapping.mapping = &meshMapping;
}

template<size_t D>
BackwardMappingFactory<D> AggregateMesh<D>::createBackwardMappingFactory( ) const 
{
    MLHP_NOT_IMPLEMENTED;
}

template<size_t D>
std::unique_ptr<AbsMapping<D, D - 1>> AggregateMesh<D>::createInterfaceMapping( ) const
{
    MLHP_NOT_IMPLEMENTED;
}

template<size_t D>
void AggregateMesh<D>::prepareInterfaceMappings( [[maybe_unused]] MeshCellFace face0,
                                                 [[maybe_unused]] MeshCellFace face1,
                                                 [[maybe_unused]] AbsMapping<D, D - 1>& mapping0,
                                                 [[maybe_unused]] AbsMapping<D, D - 1>& mapping1 ) const
{
    MLHP_NOT_IMPLEMENTED;
}

template<size_t D>
MeshUniquePtr<D> AggregateMesh<D>::clone( ) const
{
    return std::make_unique<AggregateMesh<D>>( *this );
}

template<size_t D>
size_t AggregateMesh<D>::memoryUsage( ) const 
{
    size_t usage = utilities::vectorInternalMemory( offsets_ );

    for( auto& mesh : meshes_ )
    {
        usage += mesh->memoryUsage( );
    }

    return usage + sizeof( MeshPtr ) * meshes_.capacity( );
}

template<size_t D>
void print( const AbsHierarchicalGrid<D>& grid, std::ostream& os )
{
    auto baseNCells = grid.baseGrid( ).ncells( );
    auto maxLevel = static_cast<size_t>( mesh::maxRefinementLevel( grid ) );

    os << "AbsHierarchicalGrid<" << D << "> (address: " << &grid << ")\n";
    os << "    number of cells: " << "\n";
    os << "        total                : " << grid.ncells( ) << "\n";
    os << "        base grid            : " << baseNCells << "\n";
    os << "        leaves               : " << grid.nleaves( ) << "\n";
    os << "    maximum refinement depth : " << maxLevel << "\n";
    os << "    heap memory usage        : " << utilities::memoryUsageString( grid.memoryUsage( ) );
    os << std::endl;
}

template<size_t D>
void print( const UnstructuredMesh<D>& mesh, std::ostream& os )
{
    auto cellstr = mesh::analyzeCellTypes( mesh );

    os << "UnstructuredMesh<" << D << "> (address: " << &mesh << ")\n";
    os << "    number of cells    : " << cellstr << "\n";
    os << "    number of vertices : " << mesh.nvertices( ) << "\n";
    os << "    heap memory usage  : " << utilities::memoryUsageString( mesh.memoryUsage( ) );
    os << std::endl;
}

namespace detail
{ 

CellIndexVectorPair filteredIndexMaps( const std::vector<bool>& mask )
{
    auto expand = algorithm::forwardIndexMap<CellIndex>( mask );
    auto reduce = algorithm::backwardIndexMap<CellIndex>( mask );

    return { std::move( expand ), std::move( reduce ) };
}

MLHP_EXPORT
CellIndexVectorPair filteredIndexMaps( const std::vector<std::int8_t>& cutstate,
                                       bool removeCutCells )
{
    auto boolMask = std::vector<bool>( cutstate.size( ) );
    auto predicate =  [=]( auto v ) { return v >= static_cast<std::int8_t>( removeCutCells ); };

    std::transform( cutstate.begin( ), cutstate.end( ), boolMask.begin( ), predicate );

    return filteredIndexMaps( boolMask );
}

CellIndexVectorPair filteredIndexMaps( const CellIndexVector& filteredCells,
                                       CellIndex ncells )
{
    auto mask = algorithm::indexMask( filteredCells, ncells, true );

    return filteredIndexMaps( mask );
}

template<size_t D>
void filteredNeighbours( const AbsFilteredMesh<D>& mesh,
                         CellIndex cell, size_t face, 
                         std::vector<MeshCellFace>& target )
{
    auto ineighbour = target.size( );

    mesh.unfilteredMesh( ).neighbours( mesh.unfilteredIndex( cell ), face, target );

    while( ineighbour < target.size( ) )
    {
        if( auto filtered = mesh.filteredIndex( target[ineighbour].first ); filtered != NoCell )
        {
            target[ineighbour] = { filtered, target[ineighbour].second };

            ineighbour += 1;
        }
        else
        {
            target.erase( target.begin( ) + utilities::ptrdiff( ineighbour ) );
        }
    }
}

template<size_t D>
BackwardMappingFactory<D> filteredBackwardMapping( const AbsFilteredMesh<D>& mesh )
{
    return [&mesh, factory = mesh.unfilteredMesh( ).createBackwardMappingFactory( )]( )
    { 
        auto filtered = std::shared_ptr { factory( ) };

        auto map = [&mesh, filtered]( std::array<double, D> xyz, BackwardMapVector<D>& target, double eps )
        {
            auto size = target.size( );

            filtered->map( xyz, target, eps );

            for( auto ilocal = size; ilocal < target.size( ); ++ilocal )
            {
                target[ilocal].first = mesh.filteredIndex( target[ilocal].first );
            }

            auto predicate = []( auto v ) { return v.first == NoCell; };
            auto it = std::remove_if( target.begin( ), target.end( ), predicate );
            
            if( it != target.end( ) ) target.erase( it );
        };

        return std::make_unique<FunctionBackwardMapping<D>>( &mesh, map ); 
    };
}

} // namespace detail

namespace mesh
{

template<size_t D>
PositionInParentVector<D> positionsInParent( const AbsHierarchicalGrid<D>& grid )
{
    PositionInParentVector<D> result( grid.nfull( ) );

    for( CellIndex iCell = 0; iCell < grid.nfull( ); ++iCell )
    {
        result[iCell] = grid.localPosition( iCell );
    }

    return result;
}

template<size_t D>
std::vector<CellIndex> parents( const AbsHierarchicalGrid<D>& grid )
{
    std::vector<CellIndex> parents( grid.nfull( ) );

    for( CellIndex icell = 0; icell < grid.nfull( ); ++icell )
    {
        parents[icell] = grid.parent( icell );
    }

    return parents;
}

template<size_t D>
std::vector<bool> leafMask( const AbsHierarchicalGrid<D>& grid )
{
    auto leafMask = std::vector<bool>( grid.nfull( ) );
    auto nint = static_cast<std::int64_t>( grid.nfull( ) );

    #pragma omp parallel for schedule(static, 64)
    for( std::int64_t ii = 0; ii < nint; ++ii )
    {
        leafMask[static_cast<CellIndex>( ii )] = grid.isLeaf( static_cast<CellIndex>( ii ) );
    }

    return leafMask;
}

template<size_t D>
CellIndex root( const AbsHierarchicalGrid<D>& grid, CellIndex fullIndex )
{
    CellIndex root = fullIndex;

    for( CellIndex current = fullIndex; current != NoCell; current = grid.parent( current ) )
    {
        root = current;
    }

    return root;
}

// Root (full) indices for all cells in the hierarchy (or only leaves if fullHierarchy = false)
template<size_t D>
std::vector<CellIndex> roots( const AbsHierarchicalGrid<D>& grid, 
                              bool fullHierarchy )
{
    auto ncells = fullHierarchy ? grid.nfull( ) : grid.nleaves( );
    auto result = std::vector<CellIndex>( ncells );

    for( CellIndex icell = 0; icell < ncells; ++icell )
    {
        result[icell] = mesh::root( grid, fullHierarchy ? icell : grid.fullIndex( icell ) );
    }

    return result;
}

template<size_t D>
void pathToRoot( const AbsHierarchicalGrid<D>& grid,
                 CellIndex fullIndex,
                 std::vector<CellIndex>& path )
{
    path.resize( 0 );
    
    for( CellIndex current = fullIndex; current != NoCell; current = grid.parent( current ) )
    {
        path.push_back( current );
    }
}

template<size_t D>
void leaves( const AbsHierarchicalGrid<D>& grid,
             CellIndex cell,
             std::vector<CellIndex>& target,
             size_t maxdepth )
{
    auto accumulate = [&]( auto&& self, auto subcell, size_t depth ) -> void
    {
        if( grid.child( subcell, PositionInParent<D>{ } ) != NoCell && depth < maxdepth )
        {
            nd::execute( array::make<D, LocalPosition>( 2 ), [&]( PositionInParent<D> ijk )
            {
                self( self, grid.child( subcell, ijk ), depth + 1 );
            } );
        }
        else
        {
            target.push_back( subcell );
        }
    };

    accumulate( accumulate, cell, 0 );
}

template<size_t D>
ThreadLocalBackwardMappings<D> threadLocalBackwardMappings( const AbsMesh<D>& mesh )
{
    auto container = ThreadLocalBackwardMappings<D> { };
    auto factory = mesh.createBackwardMappingFactory ( );
    auto nthreads = parallel::getMaxNumberOfThreads( );

    for( size_t ithread = 0; ithread < nthreads; ++ithread )
    {
        container.data[ithread] = factory( );
    }

    return container;
}

namespace
{

template<size_t D>
auto traverseFromCommonParent( const AbsHierarchicalGrid<D>& thisMesh,
                               const AbsHierarchicalGrid<D>& otherMesh,
                               CellIndex thisFullIndex,
                               auto&& coarserPath )
{
    auto result = CellInOtherGrid { NoCell, thisFullIndex, 0, 0 };

    // Traverse to root and back and accumulate other index and mapping if coarser
    auto recursive = [&]( auto&& self, auto thisCell ) -> CellIndex
    {
        auto otherCell = thisCell;

        if( auto thisParent = thisMesh.parent( thisCell ); thisParent != NoCell )
        {
            auto otherParent = self( self, thisParent );
            auto localPosition = thisMesh.localPosition( thisCell );

            // Other parent exists ...
            if( otherParent != NoCell )
            {
                otherCell = otherMesh.child( otherParent, localPosition );

                // It has no children
                if( otherCell == NoCell )
                {
                    result.thisParent = thisParent;
                }
                // It has children
                else
                {
                    result.otherCell = otherCell;
                    result.otherLevel += 1;
                }
            }
            // Other parent doesn't exist so other cell doesn't either
            else
            {
                otherCell = NoCell;
            }

            // Transform other mapping to child if this cell doesnt exists in other mesh
            if( otherCell == NoCell )
            {
                coarserPath( localPosition, thisParent, thisCell );
            }

            result.thisLevel += 1;
        }
        else
        {
            result.otherCell = otherCell;
        }

        return otherCell;
    };

    recursive( recursive, thisFullIndex );

    return result;
}

} // namespace

template<size_t D> MLHP_EXPORT
CellInOtherGrid findInOtherGrid( const AbsHierarchicalGrid<D>& thisMesh,
                                 const AbsHierarchicalGrid<D>& otherMesh,
                                 CellIndex thisFullIndex )
{
    return traverseFromCommonParent( thisMesh, otherMesh, 
        thisFullIndex, utilities::doNothing( ) );
}

template<size_t D> MLHP_EXPORT
CellInOtherGrid findInOtherGrid( const AbsHierarchicalGrid<D>& thisMesh,
                                 const AbsHierarchicalGrid<D>& otherMesh,
                                 std::vector<CellIndex>& target,
                                 CellIndex thisFullIndex,
                                 size_t maxdepth )
{
    auto result = findInOtherGrid( thisMesh, otherMesh, thisFullIndex );

    if( result.otherLevel < result.thisLevel )
    {
        target.push_back( result.otherCell );
    }
    else 
    {
        leaves( otherMesh, result.otherCell, target, maxdepth );
    }

    return result;
}

template<size_t D>
CellInOtherGrid findInOtherGrid( const AbsHierarchicalGrid<D>& thisMesh,
                                 const AbsHierarchicalGrid<D>& otherMesh,
                                 std::vector<SharedSupport<D>>& target,
                                 CellIndex thisFullIndex,
                                 size_t maxdepth )
{
    auto identityMapping = CartesianMapping<D> { { array::make<D>( -1.0 ), array::make<D>( 1.0 ) } };
    auto childMapping = makeCartesianMappingSplitter( identityMapping, array::makeSizes<D>( 2 ) );
    auto otherMapping = identityMapping;

    auto coarser = [&]( auto position, auto&&... )
    {
        otherMapping = concatenateCartesianMappings( otherMapping, 
            childMapping( array::convert<size_t>( position ) ) );
    };
    
    auto result = traverseFromCommonParent( thisMesh, otherMesh, thisFullIndex, coarser );

    // Other cell is coarser --> target already set up during traversal to root
    if( result.otherLevel < result.thisLevel )
    {
        target.push_back( SharedSupport<D> { identityMapping, otherMapping, result.otherCell } );
    }
    else 
    {
        // Other is equal or finer --> accumulate leaves of other mesh
        auto accumulate = [&]( auto&& self, auto&& mapping, auto cell, size_t depth ) -> void
        {
            if( otherMesh.child( cell, PositionInParent<D>{ } ) != NoCell && depth < maxdepth )
            {
                nd::execute( array::make<D, LocalPosition>( 2 ), [&]( PositionInParent<D> ijk )
                {
                    auto localMapping = childMapping( array::convert<size_t>( ijk ) );
                    auto rootMapping = concatenateCartesianMappings( mapping, localMapping );

                    self( self, rootMapping, otherMesh.child( cell, ijk ), depth + 1 );
                } );
            }
            else
            {
                target.push_back( SharedSupport<D> { mapping, identityMapping, cell } );
            }
        };

        accumulate( accumulate, identityMapping, result.otherCell, 0 );
    }

    return result;
}

template<size_t D>
CellLocalCoordinates<D> mapToOtherGrid( const AbsHierarchicalGrid<D>& thisMesh,
                                        const AbsHierarchicalGrid<D>& otherMesh,
                                        CellIndex thisLeafIndex,
                                        std::array<double, D> thisRst )
{
    auto thisFullIndex = thisMesh.fullIndex( thisLeafIndex );
    auto info = mesh::findInOtherGrid( thisMesh, otherMesh, thisFullIndex );

    for( auto index = thisFullIndex; index != info.thisParent; index = thisMesh.parent( index ) )
    {
        thisRst = mesh::mapToParent( thisMesh.localPosition( index ) )( thisRst );
    }

    return otherMesh.mapToLeaf( info.otherCell, thisRst );
}

template<size_t D>
void mapToParent( CoordinateGrid<D>& rst,
                  PositionInParent<D> positionInParent )
{
    if( positionInParent[0] != NoLocalPosition )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            double shift = positionInParent[axis] ? 0.5 : - 0.5;

            for( double& coordinate : rst[axis] )
            {
                coordinate = coordinate / 2.0 + shift;
            }

        } // for axis
    }
}

template<size_t D>
void mapToParent( const AbsHierarchicalGrid<D>& grid,
                  CellIndex cell,
                  CoordinateGrid<D>& rst )
{
    auto position = grid.localPosition( cell );

    mapToParent( rst, position );
}

template<size_t D> MLHP_EXPORT
CartesianMapping<D> mapToParent( CartesianMapping<D> mapping,
                                 PositionInParent<D> localPosition )
{
    if( localPosition[0] != NoLocalPosition )
    {
        auto center = mapping.center( );
        auto halflengths = mapping.halflengths( );

        for( size_t axis = 0; axis < D; ++axis )
        {
            center[axis] = 0.5 * center[axis] + ( localPosition[axis] ? 0.5 : -0.5 );
            halflengths[axis] *= 0.5;
        }

        mapping.resetCenterHalflengths( center, halflengths );
    }

    return mapping;
}

template<size_t D>
CartesianMapping<D> mapToParent( PositionInParent<D> localPosition )
{
    return mapToParent( CartesianMapping<D>{ }, localPosition );
}

template<size_t D>
HierarchyMapping<D> mapToRoot( const AbsHierarchicalGrid<D>& grid,
                               CellIndex fullIndex )
{
    auto mapping = CartesianMapping<D> { };
    auto root = fullIndex;

    for( auto icell = grid.parent( fullIndex ); icell != NoCell; icell = grid.parent( icell ) )
    {
        mapping = mapToParent( mapping, grid.localPosition( root ) );

        root = icell;
    }

    return { std::move( mapping ), root };
}

template<size_t D>
CoordinateList<D> map( const AbsMesh<D>& mesh,
                       std::span<const CellIndex> indices,
                       CoordinateConstSpan<D> rst )
{
    MLHP_CHECK( indices.size( ) == rst.size( ), "Inconsistent input." );

    auto result = CoordinateList<D>( rst.size( ) );
    auto ncells = mesh.ncells( );

    if( result.empty( ) )
    {
        return result;
    }

    #pragma omp parallel 
    {
        auto mapping = mesh.createMapping( );

        mapping.icell = NoCell;

        #pragma omp for schedule( dynamic, 17 )
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( rst.size( ) ); ++ii )
        {
            auto index = static_cast<size_t>( ii );

            MLHP_CHECK( indices[index] < ncells, "Cell index out of bounds." );

            if( mapping.icell != indices[index] )
            {
                mesh.prepareMapping( indices[index], mapping );
            }

            result[index] = mapping( rst[index] );
        }
    }

    return result;
}

template<size_t D>
std::vector<BackwardMapResult<D>> mapBackwardSingle( const AbsMesh<D>& mesh,
                                                     CoordinateConstSpan<D> xyz,
                                                     double epsilon )
{
    if( xyz.empty( ) )
    {
        return { };
    }

    auto result = std::vector<BackwardMapResult<D>>( xyz.size( ) );
    auto creator = mesh.createBackwardMappingFactory( );

    #pragma omp parallel
    {
        auto backwardMapping = creator( );
        
        #pragma omp for schedule( dynamic, 16 )
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( xyz.size( ) ); ++ii )
        {
            auto index = static_cast<size_t>( ii );

            result[index] = backwardMapping->map( xyz[index], epsilon );
        }
    }

    return result;
}

template<size_t D>
LinearizedBackwardMapResults<D> mapBackwardMultiple( const AbsMesh<D>& mesh,
                                                     CoordinateConstSpan<D> xyz,
                                                     double epsilon )
{
    auto result = LinearizedBackwardMapResults<D> { };

    result.first.resize( xyz.size( ) + 1 );

    if( !xyz.empty( ) )
    {
        auto creator = mesh.createBackwardMappingFactory( );

        #pragma omp parallel
        {
            auto backwardMapping = creator( );
            auto localIndices = std::vector<size_t> { };
            auto localOffsets = std::vector<size_t> { 0 };
            auto localResults = std::vector<CellLocalCoordinates<D>> { };
            auto singleResult = std::vector<CellLocalCoordinates<D>> { };

            #pragma omp for schedule( dynamic, 16 )
            for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( xyz.size( ) ); ++ii )
            {
                auto index = static_cast<size_t>( ii );

                backwardMapping->map( xyz[index], utilities::resize0( singleResult ), epsilon );

                localResults.insert( localResults.end( ), singleResult.begin( ), singleResult.end( ) );
                localIndices.push_back( index );
                localOffsets.push_back( localResults.size( ) );

                result.first[index + 1] = singleResult.size( );
            }

            #pragma omp barrier
            { }

            #pragma omp single
            {
                std::partial_sum( result.first.begin( ), result.first.end( ), result.first.begin( ) );

                result.second.resize( result.first.back( ) );
            }

            for( size_t ilocal = 0; ilocal < localIndices.size( ); ++ilocal )
            {
                std::copy( utilities::begin( localResults, localOffsets[ilocal] ),
                           utilities::begin( localResults, localOffsets[ilocal + 1] ),
                           utilities::begin( result.second, result.first[localIndices[ilocal]] ) );
            }
        }
    }

    return result;
}

template<size_t D>
FaceMapping<D> faceMapping( const AbsMesh<D>& mesh, CellIndex icell, size_t iface )
{
    return FaceMapping<D>( mesh.cellType( icell ), iface );
}

template<size_t D> MLHP_EXPORT
CellIndexVector reductionMap( const AbsFilteredMesh<D>& mesh )
{
    auto ncells = mesh.unfilteredMesh( ).ncells( );

    CellIndexVector result( ncells );

    for( CellIndex icell = 0; icell < ncells; ++icell )
    {
        result[icell] = mesh.filteredIndex( icell );
    }

    return result;
}

template<size_t D>
RefinementLevelVector refinementLevels( const AbsHierarchicalGrid<D>& grid, bool fullHierarchy )
{
    auto levels = topology::refinementLevels( mesh::parents( grid ) );

    if( !fullHierarchy )
    {
        auto count = size_t { 0 };
    
        for( CellIndex ifull = 0; ifull < levels.size( ); ++ifull )
        {
            if( grid.isLeaf( ifull ) )
            {
                levels[count++] = levels[ifull];
            }
        }

        levels.resize( count );
        levels.shrink_to_fit( );
    }

    return levels;
}

template<size_t D>
RefinementLevel maxRefinementLevel( const AbsHierarchicalGrid<D>& grid )
{
    return topology::maxRefinementLevel( mesh::parents( grid ) );
}

template<size_t D>
NCubeNeighboursVector<D> hierarchicalNeighbours( const AbsHierarchicalGrid<D>& grid )
{
    auto ncells = static_cast<std::int64_t>( grid.nfull( ) );

    NCubeNeighboursVector<D> neighbours( grid.nfull( ) );
        
    #pragma omp parallel for schedule( dynamic, 7 )
    for( std::int64_t iInt = 0; iInt < ncells; ++iInt )
    {
        auto iCell = static_cast<CellIndex>( iInt );

        for( size_t axis = 0; axis < D; ++axis )
        {
            neighbours[iCell]( axis, 0 ) = grid.neighbour( iCell, axis, 0 );
            neighbours[iCell]( axis, 1 ) = grid.neighbour( iCell, axis, 1 );

        } // for axis
    } // for iCell

    return neighbours;
}

template<size_t D>
MeshCellFaces boundaries( const AbsMesh<D>& mesh )
{
    MeshCellFaces segments;
    std::vector<MeshCellFace> target;

    for( CellIndex iCell = 0; iCell < mesh.ncells( ); ++iCell )
    {
        for( size_t iface = 0; iface < mesh.nfaces( iCell ); ++iface )
        {
            mesh.neighbours( iCell, iface, utilities::resize0( target ) );

            if( target.empty( ) )
            {
                segments.push_back( { iCell, iface } );
            }
        }
    }

    return segments;
}

template<size_t D>
std::vector<MeshCellFaces> boundariesByFaceIndex( const AbsMesh<D>& mesh,
                                                  const std::vector<size_t>& faces )
{
    std::vector<MeshCellFaces> segments( faces.size( ) );
    std::vector<MeshCellFace> target;

    auto map = algorithm::backwardIndexMap( faces, size_t { 2 * D } );

    for( CellIndex iCell = 0; iCell < mesh.ncells( ); ++iCell )
    {
        for( size_t iface = 0; iface < mesh.nfaces( iCell ); ++iface )
        {
            if( map[iface] != NoValue<size_t> )
            {
                mesh.neighbours( iCell, iface, utilities::resize0( target ) );

                if( target.empty( ) )
                {
                    segments[map[iface]].push_back( { iCell, iface } );
                }
            }
        }
    }

    return segments;
}

template<size_t D> MLHP_EXPORT
std::vector<MeshCellFaces> boundariesByBoundingBox( const AbsMesh<D>& mesh,
                                                    const std::vector<size_t>& sides,
                                                    double epsilon )
{
    auto nseedpoints = size_t { 3 };
    auto boundaries = mesh::boundaries( mesh );
    auto boundingBox = mesh::boundingBox( mesh, nseedpoints );
    auto result = std::vector<MeshCellFaces>( );

    for( size_t iside = 0; iside < sides.size( ); ++iside )
    {
        auto [normal, side] = normalAxisAndSide( sides[iside] );
        auto collapsed = boundingBox;

        MLHP_CHECK( normal < D, "Invalid boundary index." );

        collapsed[1 - side][normal] = collapsed[side][normal];
        collapsed = spatial::extendBoundingBox( collapsed, epsilon, epsilon );

        result.push_back( facesInsideDomain( mesh, boundaries,
            implicit::cube( collapsed[0], collapsed[1] ), nseedpoints ) );
    }

    return result;
}

template<size_t D>
spatial::BoundingBox<D> boundingBox( const AbsMesh<D>& mesh, size_t nseedpoints )
{
    MLHP_CHECK( nseedpoints >= 2, "Need at least two seed points." );

    auto global = spatial::makeEmptyBoundingBox<D>( );
    auto ncells = static_cast<std::int64_t>( mesh.ncells( ) );

    #pragma omp parallel
    {
        auto local = spatial::makeEmptyBoundingBox<D>( );
        auto mapping = mesh.createMapping( );

        #pragma omp for
        for( std::int64_t ii = 0; ii < ncells; ++ii )
        {
            auto icell = static_cast<CellIndex>( ii ); 

            mesh.prepareMapping( icell, mapping );

            local = spatial::boundingBoxOr( local, mesh::boundingBox( mapping, nseedpoints ) );
        }

        #pragma omp critical
        {
            global = spatial::boundingBoxOr( global, local );
        }
    }

    return global;
}

template<size_t D>
spatial::BoundingBox<D> boundingBox( const AbsMapping<D>& mapping,
                                     size_t nseedpoints )
{
    auto bounds = spatial::makeEmptyBoundingBox<D>( );

    if( mapping.type == CellType::NCube )
    {
        auto limits = array::make<D>( nseedpoints );
        auto rstGenerator = spatial::makeRstGenerator( limits );

        nd::executeBoundary( limits, [&]( std::array<size_t, D> ijk )
        {
            bounds = spatial::boundingBoxOr( bounds, mapping( rstGenerator( ijk ) ) );
        } );
    }
    else
    {
        MLHP_CHECK( mapping.type == CellType::Simplex, "Bounding box not implemented for cell type." );

        auto rstGenerator = spatial::makeGridPointGenerator<D>( array::make<D>( nseedpoints ), array::make<D>( 1.0 ), { } );

        nd::executeTriangularBoundary<D>( nseedpoints, [&]( std::array<size_t, D> ijk )
        {
            bounds = spatial::boundingBoxOr( bounds, mapping( rstGenerator( ijk ) ) );
        } );
    }

    return bounds;
}

template<size_t D> MLHP_EXPORT
MeshCellFaces facesInBoundingBox( const AbsMesh<D>& mesh, 
                                  spatial::BoundingBox<D> bounds,
                                  size_t nseedpoints,
                                  double epsilon )
{
    bounds = spatial::extendBoundingBox( bounds, epsilon );

    return facesInsideDomain( mesh, implicit::cube( bounds ), nseedpoints );
}

template<size_t D> MLHP_EXPORT
MeshCellFaces facesInsideDomain( const AbsMesh<D>& mesh, 
                                 const ImplicitFunction<D>& domain,
                                 size_t nseedpoints )
{
    auto ncells = static_cast<std::int64_t>( mesh.ncells( ) );
    auto limits = array::makeSizes<D>( nseedpoints );
    auto rstGenerator = spatial::makeRstGenerator( limits );
    auto all = utilities::integerPow( nseedpoints, D - 1 );

    auto globalFaces = MeshCellFaces { };
    auto count = std::vector<size_t> ( mesh.ncells( ) + 1, 0 );

    #pragma omp parallel
    {
        auto localFaces = MeshCellFaces { };
        auto mapping = mesh.createMapping( );

        #pragma omp for schedule( dynamic )
        for( std::int64_t ii = 0; ii < ncells; ++ii )
        {
            auto icell = static_cast<CellIndex>( ii ); 
            auto found = std::array<size_t, 2 * D> { };

            MLHP_CHECK( mesh.cellType( icell ) == CellType::NCube, "Invalid cell type." );

            mesh.prepareMapping( icell, mapping );

            nd::executeBoundary( limits, [&]( std::array<size_t, D> ijk )
            {
                auto xyz = mapping( rstGenerator( ijk ) );

                if( domain( xyz ) )
                {
                    for( size_t axis = 0; axis < D; ++axis )
                    {
                        if( ijk[axis] == 0 )
                        {
                            found[2 * axis] += 1;
                        }
                        if( ijk[axis] + 1 == nseedpoints )
                        {
                            found[2 * axis + 1] += 1;
                        }
                    }
                }
            } ); // nd::executeBoundary

            for( size_t iface = 0; iface < 2 * D; ++iface )
            {
                if( found[iface] == all )
                {
                    count[icell + 1] += 1;
                    localFaces.emplace_back( icell, iface );
                }
            }

        } // for icell

        #pragma omp barrier
        { }

        #pragma omp single
        {
            std::partial_sum( count.begin( ), count.end( ), count.begin( ) );

            globalFaces.resize( count.back( ) );
        }

        auto ilast = NoCell;
        auto nfaces = size_t { 0 };
        auto size = static_cast<std::int64_t>( localFaces.size( ) );

        for( std::int64_t ii = 0; ii < size; ++ii )
        {
            auto [icell, iface] = localFaces[static_cast<size_t>( ii )];

            nfaces = icell == ilast ? nfaces : size_t { 0 };

            globalFaces[count[icell] + nfaces] = { icell, iface };

            nfaces += 1;
            ilast = icell;
        }

    } // omp parallel

    return globalFaces;
}

template<size_t D> MLHP_EXPORT
MeshCellFaces facesInsideDomain( const AbsMesh<D>& mesh, 
                                 const MeshCellFaces& faces,
                                 const ImplicitFunction<D>& domain,
                                 size_t nseedpoints )
{
    auto mask = std::vector<std::uint8_t>( faces.size( ) );
    auto nallfaces = static_cast<std::int64_t>( faces.size( ) );

    #pragma omp parallel
    {
        auto mapping = mesh.createMapping( );
        auto rstList = CoordinateList<D - 1> { };

        #pragma omp for schedule( dynamic )
        for( std::int64_t ii = 0; ii < nallfaces; ++ii )
        {
            auto faceIndex = static_cast<CellIndex>( ii );
            auto icell = faces[faceIndex].first;
            auto iface = faces[faceIndex].second;
            auto face = mesh::faceMapping( mesh, icell, iface );
            auto count = size_t { 0 };
            
            mesh.prepareMapping( icell, mapping );

            spatial::distributeSeedPoints( mapping.type, 
                nseedpoints, utilities::resize0( rstList ) );

            for( auto rst : rstList )
            {
                count += domain( mapping( face( rst ) ) );
            }

            mask[faceIndex] = ( count == rstList.size( ) );

        } // for icell
    } // omp parallel

    return algorithm::extract( faces, algorithm::forwardIndexMap<size_t>( mask ) );
}

template<size_t D>
kdtree::ObjectProvider<D> boundingBoxProvider( const UnstructuredMesh<D>& mesh )
{
    std::function provider = [&]( size_t icell, const spatial::BoundingBox<D>& clip )
    {
        auto bounds = mesh.boundingBox( static_cast<CellIndex>( icell ) );

        return spatial::boundingBoxAnd( bounds, clip );
    };

    auto ncells = static_cast<size_t>( mesh.ncells( ) );

    return utilities::makeIndexRangeFunction( ncells, provider );
}

namespace
{

template<size_t D>
auto adaptiveMaxDepth( const AbsHierarchicalGrid<D>& oldGrid,
                       const std::vector<int>& relativeDepth )
{
    MLHP_CHECK( relativeDepth.size( ) == oldGrid.ncells( ),
        "Inconsistent number of relativeDepth values." );
    
    auto nroots = oldGrid.baseGrid( ).ncells( );
    auto maxdepth = std::vector<int>( oldGrid.nfull( ), std::numeric_limits<int>::min( ) );

    auto traverse = [&]( auto&& self, CellIndex ifull ) -> void
    {
        if( auto child = oldGrid.child( ifull, { } ); child != NoCell )
        {
            auto limits = array::make<D>( LocalPosition { 2 } );

            nd::execute( limits, [&]( std::array<LocalPosition, D> ijk )
            {
                child = oldGrid.child( ifull, ijk );

                self( self, child );

                maxdepth[ifull] = std::max( maxdepth[ifull], maxdepth[child] + 1 );
            } );
        }
        else
        {
            maxdepth[ifull] = relativeDepth[oldGrid.leafIndex( ifull )];
        }
    };

    #pragma omp parallel for schedule(dynamic, 7)
    for( std::int64_t iroot = 0; iroot < static_cast<std::int64_t>( nroots ); ++iroot )
    {
        traverse( traverse, static_cast<CellIndex>( iroot ) );
    }

    return maxdepth;
}

template<size_t D>
auto adaptiveRefine( const AbsHierarchicalGrid<D>& oldMesh,
                     const AbsHierarchicalGrid<D>& newMesh,
                     const std::vector<int>& maxDepthChildren,
                     size_t maxdepth,
                     CellIndex ifull )
{
    if( auto result = findInOtherGrid( newMesh, oldMesh, ifull ); result.thisLevel < maxdepth )
    {
        auto levelDifferences = static_cast<int>( result.thisLevel ) - static_cast<int>( result.otherLevel );

        MLHP_CHECK_DBG( levelDifferences >= 0, "Inconsistent refinement levels in refineAdaptively." );

        return maxDepthChildren[result.otherCell] - levelDifferences > 0;
    }

    return false;
}

}

template<size_t D>
RefinementFunction<D> refineAdaptively( const AbsHierarchicalGrid<D>& oldMesh,
                                        const std::vector<int>& relativeDepth,
                                        size_t maxdepth )
{
    auto maxDepthChildren = adaptiveMaxDepth( oldMesh, relativeDepth );

    return [=, &oldMesh]( const MeshMapping<D>& mapping, RefinementLevel )
    {
        auto& newMesh = dynamic_cast<const AbsHierarchicalGrid<D>&>( *mapping.mesh );

        return adaptiveRefine( oldMesh, newMesh, maxDepthChildren, maxdepth, newMesh.fullIndex( mapping.icell ) );
    };
}

template<size_t D> MLHP_EXPORT
std::string analyzeCellTypes( const AbsMesh<D>& mesh )
{
    auto typecount = std::map<CellType, size_t> { };
    auto ncells = mesh.ncells( );

    for( CellIndex icell = 0; icell < ncells; ++icell )
    {
        if( auto type = mesh.cellType( icell ); typecount.count( type ) )
        {
            typecount[type] += 1;
        }
        else
        {
            typecount[type] = 1;
        }
    }

    auto cellsstr = std::string { " ("};

    for( auto [type, count] : typecount )
    {
        auto cellstr = topology::cellTypeString( type, D, count > 1, false );

        cellsstr += std::to_string( count ) + " " + cellstr + ", ";
    }

    cellsstr = cellsstr.substr( 0, cellsstr.size( ) - 2 ) + ( ncells ? ")" : "" );

    return std::to_string( static_cast<std::uint64_t>( mesh.ncells( ) ) ) + cellsstr;
}
template<size_t D>
std::vector<std::int8_t> cutstate( const AbsMesh<D>& grid,
                                   const ImplicitFunction<D>& function,
                                   size_t nseedpoints )
{
    auto nelements = static_cast<std::int64_t>( grid.ncells( ) );
    auto mask = std::vector<std::int8_t>( grid.ncells( ) );

    #pragma omp parallel
    {
        auto mapping = grid.createMapping( );

        #pragma omp for schedule(static)
        for( std::int64_t ii = 0; ii < nelements; ++ii )
        {
            auto icell = static_cast<CellIndex>( ii );

            grid.prepareMapping( icell, mapping );

            mask[icell] = intersectionTest( function, mapping, nseedpoints );
        }
    }

    return mask;
}

} // namespace mesh

template<size_t D>
CartesianGridSharedPtr<D> makeCartesianGrid( std::array<size_t, D> nelements,
                                             std::array<double, D> lengths,
                                             std::array<double, D> origin )
{
    return std::make_shared<CartesianGrid<D>>( nelements, lengths, origin );
}

template<size_t D>
HierarchicalGridSharedPtr<D> makeRefinedGrid( const GridSharedPtr<D>& baseGrid )
{
    return std::make_shared<RefinedGrid<D>>( baseGrid );
}

template<size_t D> MLHP_EXPORT
HierarchicalGridSharedPtr<D> makeRefinedGrid( const CartesianGrid<D>& baseGrid )
{
    return std::make_shared<RefinedGrid<D>>( std::make_shared<CartesianGrid<D>>( baseGrid ) );
}

template<size_t D> MLHP_EXPORT
HierarchicalGridSharedPtr<D> makeRefinedGrid( const CoordinateGrid<D>& coordinates )
{
    auto baseGrid = std::make_shared<CartesianGrid<D>>( coordinates );

    return makeRefinedGrid<D>( baseGrid );
}

template<size_t D>
HierarchicalGridSharedPtr<D> makeRefinedGrid( std::array<size_t, D> nelements,
                                              std::array<double, D> lengths,
                                              std::array<double, D> origin )
{
    auto baseGrid = std::make_shared<CartesianGrid<D>>( nelements, lengths, origin );

    return makeRefinedGrid<D>( baseGrid );
}

template<size_t D>
HierarchicalGridSharedPtr<D> makeRefinedGrid( const AbsHierarchicalGrid<D>& oldMesh,
                                              const std::vector<int>& relativeDepth,
                                              size_t maxdepth )
{
    auto newMesh = makeRefinedGrid<D>( oldMesh.baseGrid( ).cloneGrid( ) );
    auto maxDepthChildren = mesh::adaptiveMaxDepth( oldMesh, relativeDepth );

    auto begin = CellIndex { 0 };
    auto end = newMesh->nfull( );

    while( begin != end )
    {
        auto refinementMask = std::vector<std::uint8_t>( end - begin, 0 );

        #pragma omp parallel for schedule(dynamic, 7)
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( end - begin ); ++ii )
        {
            auto index = static_cast<CellIndex>( ii );

            refinementMask[index] = mesh::adaptiveRefine( oldMesh, 
                *newMesh, maxDepthChildren, maxdepth, index + begin );
        }

        refineWithMask( *newMesh, refinementMask, begin );

        begin = end;
        end = newMesh->nfull( );
    }

    return newMesh;
}

#define MLHP_INSTANTIATE_DIM( D )                                                         \
    template class AbsMesh<D>;                                                            \
    template class AbsGrid<D>;                                                            \
    template class CartesianGrid<D>;                                                      \
    template class AbsHierarchicalGrid<D>;                                                \
    template class RefinedGrid<D>;                                                        \
    template class UnstructuredMesh<D>;                                                   \
    template class AbsFilteredMesh<D>;                                                    \
    template class FilteredMesh<D>;                                                       \
    template class FilteredGrid<D>;                                                       \
    template class AggregateMesh<D>;                                                      \
    template class AbsBackwardMapping<D>;                                                 \
                                                                                          \
    template MLHP_EXPORT                                                                  \
    CartesianGridSharedPtr<D> makeCartesianGrid( std::array<size_t, D> nelements,         \
                                                 std::array<double, D> lengths,           \
                                                 std::array<double, D> origin );          \
                                                                                          \
    template MLHP_EXPORT                                                                  \
    HierarchicalGridSharedPtr<D> makeRefinedGrid( const GridSharedPtr<D>& baseGrid );     \
                                                                                          \
    template MLHP_EXPORT                                                                  \
    HierarchicalGridSharedPtr<D> makeRefinedGrid( const CartesianGrid<D>& baseGrid );     \
                                                                                          \
    template MLHP_EXPORT                                                                  \
    HierarchicalGridSharedPtr<D> makeRefinedGrid( const CoordinateGrid<D>& coordinates ); \
                                                                                          \
    template MLHP_EXPORT                                                                  \
    HierarchicalGridSharedPtr<D> makeRefinedGrid( std::array<size_t, D> nelements,        \
                                                  std::array<double, D> lengths,          \
                                                  std::array<double, D> origin );         \
                                                                                          \
    template MLHP_EXPORT                                                                  \
    HierarchicalGridSharedPtr<D> makeRefinedGrid( const AbsHierarchicalGrid<D>& grid,     \
                                                  const std::vector<int>& relativeDepth,  \
                                                  size_t maxdepth );                      \
                                                                                          \
    template MLHP_EXPORT                                                                  \
    void print( const AbsHierarchicalGrid<D>& grid, std::ostream& os );                   \
                                                                                          \
    template MLHP_EXPORT                                                                  \
    void print( const UnstructuredMesh<D>& grid, std::ostream& os );                      \
                                                                                          \
    template MLHP_EXPORT                                                                  \
    std::optional<std::array<double, D>> mapBackward( const AbsMapping<D>& mapping,       \
                                                      std::array<double, D> xyz,          \
                                                      double eps );                       \
                                                                                          \
    namespace mesh                                                                        \
    {                                                                                     \
        template MLHP_EXPORT                                                              \
        RefinementLevelVector refinementLevels( const AbsHierarchicalGrid<D>& grid,       \
                                                bool fullHierarchy );                     \
                                                                                          \
        template MLHP_EXPORT                                                              \
        RefinementLevel maxRefinementLevel( const AbsHierarchicalGrid<D>& grid );         \
                                                                                          \
        template MLHP_EXPORT                                                              \
        NCubeNeighboursVector<D> hierarchicalNeighbours(                                  \
                                                    const AbsHierarchicalGrid<D>& grid ); \
                                                                                          \
        template MLHP_EXPORT                                                              \
        MeshCellFaces boundaries( const AbsMesh<D>& mesh );                               \
                                                                                          \
        template MLHP_EXPORT                                                              \
        std::vector<MeshCellFaces> boundariesByFaceIndex( const AbsMesh<D>& mesh,         \
                                                      const std::vector<size_t>& faces ); \
                                                                                          \
        template MLHP_EXPORT                                                              \
        std::vector<MeshCellFaces> boundariesByBoundingBox( const AbsMesh<D>& mesh,       \
                                                      const std::vector<size_t>& sides,   \
                                                      double epsilon );                   \
                                                                                          \
        template MLHP_EXPORT                                                              \
        MeshCellFaces facesInBoundingBox( const AbsMesh<D>& mesh,                         \
                                          spatial::BoundingBox<D>,                        \
                                          size_t nseedpoints,                             \
                                          double epsilon );                               \
                                                                                          \
        template MLHP_EXPORT                                                              \
        MeshCellFaces facesInsideDomain( const AbsMesh<D>& mesh,                          \
                                         const ImplicitFunction<D>& domain,               \
                                         size_t nseedpoints );                            \
                                                                                          \
        template MLHP_EXPORT                                                              \
        MeshCellFaces facesInsideDomain( const AbsMesh<D>& mesh,                          \
                                         const MeshCellFaces& faces,                      \
                                         const ImplicitFunction<D>& domain,               \
                                         size_t nseedpoints );                            \
                                                                                          \
        template MLHP_EXPORT                                                              \
        spatial::BoundingBox<D> boundingBox( const AbsMesh<D>& mesh,                      \
                                             size_t nseedpoints );                        \
                                                                                          \
        template MLHP_EXPORT                                                              \
        spatial::BoundingBox<D> boundingBox( const AbsMapping<D>& mapping,                \
                                             size_t nseedpoints );                        \
                                                                                          \
        template MLHP_EXPORT                                                              \
        kdtree::ObjectProvider<D> boundingBoxProvider( const UnstructuredMesh<D>& mesh ); \
                                                                                          \
        template MLHP_EXPORT                                                              \
        PositionInParentVector<D> positionsInParent( const AbsHierarchicalGrid<D>& grid );\
                                                                                          \
        template MLHP_EXPORT                                                              \
        CellIndexVector parents( const AbsHierarchicalGrid<D>& grid );                    \
                                                                                          \
        template MLHP_EXPORT                                                              \
        std::vector<bool> leafMask( const AbsHierarchicalGrid<D>& grid );                 \
                                                                                          \
        template MLHP_EXPORT                                                              \
        CellIndex root( const AbsHierarchicalGrid<D>& grid, CellIndex fullIndex );        \
                                                                                          \
        template MLHP_EXPORT                                                              \
        CellIndexVector roots( const AbsHierarchicalGrid<D>& grid, bool fullHierarchy );  \
                                                                                          \
        template MLHP_EXPORT                                                              \
        void pathToRoot( const AbsHierarchicalGrid<D>& grid,                              \
                         CellIndex fullIndex,                                             \
                         CellIndexVector& path );                                         \
                                                                                          \
        template MLHP_EXPORT                                                              \
        void leaves( const AbsHierarchicalGrid<D>& grid,                                  \
                     CellIndex cell,                                                      \
                     CellIndexVector& target,                                             \
                     size_t maxdepth );                                                   \
                                                                                          \
        template MLHP_EXPORT                                                              \
        ThreadLocalBackwardMappings<D> threadLocalBackwardMappings(                       \
                                       const AbsMesh<D>& mesh );                          \
                                                                                          \
        template MLHP_EXPORT                                                              \
        CellInOtherGrid findInOtherGrid( const AbsHierarchicalGrid<D>& thisMesh,          \
                                         const AbsHierarchicalGrid<D>& otherMesh,         \
                                         std::vector<SharedSupport<D>>& target,           \
                                         CellIndex thisFullIndex,                         \
                                         size_t maxdepth );                               \
                                                                                          \
        template MLHP_EXPORT                                                              \
        CellInOtherGrid findInOtherGrid( const AbsHierarchicalGrid<D>& thisMesh,          \
                                         const AbsHierarchicalGrid<D>& otherMesh,         \
                                         std::vector<CellIndex>& target,                  \
                                         CellIndex thisFullIndex,                         \
                                         size_t maxdepth );                               \
                                                                                          \
        template MLHP_EXPORT                                                              \
        CellInOtherGrid findInOtherGrid( const AbsHierarchicalGrid<D>& thisMesh,          \
                                         const AbsHierarchicalGrid<D>& otherMesh,         \
                                         CellIndex thisFullIndex );                       \
                                                                                          \
        template MLHP_EXPORT                                                              \
        CellLocalCoordinates<D> mapToOtherGrid( const AbsHierarchicalGrid<D>& thisGrid,   \
                                                const AbsHierarchicalGrid<D>& otherGrid,  \
                                                CellIndex thisLeafIndex,                  \
                                                std::array<double, D> thisRst );          \
                                                                                          \
        template MLHP_EXPORT                                                              \
        void mapToParent( CoordinateGrid<D>& rst,                                         \
                          PositionInParent<D> positionInParent );                         \
                                                                                          \
        template MLHP_EXPORT                                                              \
        CartesianMapping<D> mapToParent( PositionInParent<D> localPosition );             \
                                                                                          \
        template MLHP_EXPORT                                                              \
        CartesianMapping<D> mapToParent( CartesianMapping<D> mapping,                     \
                                         PositionInParent<D> localPosition );             \
                                                                                          \
        template MLHP_EXPORT                                                              \
        HierarchyMapping<D> mapToRoot( const AbsHierarchicalGrid<D>& grid,                \
                                       CellIndex fullIndex );                             \
                                                                                          \
        template MLHP_EXPORT                                                              \
        CoordinateList<D> map( const AbsMesh<D>& mesh,                                    \
                               std::span<const CellIndex> indices,                        \
                               CoordinateConstSpan<D> rst );                              \
                                                                                          \
        template MLHP_EXPORT                                                              \
        std::vector<BackwardMapResult<D>> mapBackwardSingle( const AbsMesh<D>& mesh,      \
                                                             CoordinateConstSpan<D> xyz,  \
                                                             double epsilon );            \
                                                                                          \
        template MLHP_EXPORT                                                              \
        LinearizedBackwardMapResults<D> mapBackwardMultiple( const AbsMesh<D>& mesh,      \
                                                             CoordinateConstSpan<D> xyz,  \
                                                             double epsilon );            \
                                                                                          \
        template MLHP_EXPORT                                                              \
        FaceMapping<D> faceMapping( const AbsMesh<D>& mesh,                               \
                                    CellIndex icell,                                      \
                                    size_t iface );                                       \
                                                                                          \
        template MLHP_EXPORT                                                              \
        CellIndexVector reductionMap( const AbsFilteredMesh<D>& mesh );                   \
                                                                                          \
        template MLHP_EXPORT                                                              \
        RefinementFunction<D> refineAdaptively( const AbsHierarchicalGrid<D>& old,        \
                                                const std::vector<int>& relativeDepth,    \
                                                size_t maxdepth );                        \
                                                                                          \
        template MLHP_EXPORT                                                              \
        std::string analyzeCellTypes( const AbsMesh<D>& mesh );                           \
                                                                                          \
        template MLHP_EXPORT                                                              \
        std::vector<std::int8_t> cutstate( const AbsMesh<D>& grid,                        \
                                           const ImplicitFunction<D>& function,           \
                                           size_t nseedpoints );                          \
    }                                                                                     \
                                                                                          \
    namespace detail                                                                      \
    {                                                                                     \
        template MLHP_EXPORT                                                              \
        void filteredNeighbours( const AbsFilteredMesh<D>& mesh,                          \
                                 CellIndex cell, size_t face,                             \
                                 std::vector<MeshCellFace>& target );                     \
                                                                                          \
        template MLHP_EXPORT                                                              \
        BackwardMappingFactory<D> filteredBackwardMapping( const AbsFilteredMesh<D>& );   \
    }

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // mlhp
 
