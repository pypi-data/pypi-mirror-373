// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_MESH_IMPL_HPP
#define MLHP_CORE_MESH_IMPL_HPP

namespace mlhp::detail
{

using CellIndexVectorPair = std::tuple<CellIndexVector, CellIndexVector>;

MLHP_EXPORT
CellIndexVectorPair filteredIndexMaps( const CellIndexVector& filteredCells,
                                       CellIndex ncells );

MLHP_EXPORT
CellIndexVectorPair filteredIndexMaps( const std::vector<bool>& mask );

MLHP_EXPORT
CellIndexVectorPair filteredIndexMaps( const std::vector<int8_t>& cutstate,
                                       bool removeCutCells );

template<size_t D> MLHP_EXPORT
void filteredNeighbours( const AbsFilteredMesh<D>& mesh,
                         CellIndex cell, size_t side,
                         std::vector<MeshCellFace>& target );

template<size_t D> MLHP_EXPORT
BackwardMappingFactory<D> filteredBackwardMapping( const AbsFilteredMesh<D>& mesh );

} // namespace mlhp::detail

namespace mlhp
{

template<size_t D> inline
size_t AbsMesh<D>::nfaces( CellIndex icell ) const 
{ 
    return topology::nfaces<D>( cellType( icell ) ); 
}

template<size_t D> inline
std::unique_ptr<AbsBackwardMapping<D>> AbsMesh<D>::createBackwardMapping( ) const
{
    return createBackwardMappingFactory( )( );
}

template<size_t D> inline
size_t CartesianGrid<D>::ncells( size_t axis ) const
{
    return static_cast<size_t>( numberOfCells_[axis] );
}

template<size_t D> inline
std::array<size_t, D> CartesianGrid<D>::shape( ) const
{
    return array::convert<size_t>( numberOfCells_ );
}

template<size_t D> inline
std::array<double, D> CartesianGrid<D>::origin( ) const
{
    return array::extract<double, D>( coordinates_, { } );
}

template<size_t D> inline
std::array<double, D> CartesianGrid<D>::lengths( ) const
{
    std::array<double, D> result;

    for( size_t axis = 0; axis < D; ++axis )
    {
        result[axis] = coordinates_[axis].back( ) - coordinates_[axis].front( );
    }

    return result;
}

template<size_t D>
CellIndex RefinedGrid<D>::nleaves( ) const 
{ 
    return static_cast<CellIndex>( fullIndex_.size( ) ); 
}
    
template<size_t D>
CellIndex RefinedGrid<D>::nfull( ) const 
{ 
    return static_cast<CellIndex>( parentIndex_.size( ) ); 
}

template<size_t D, typename MeshBase> inline
FilteredMeshBase<D, MeshBase>::FilteredMeshBase( const std::shared_ptr<MeshBase>& mesh,
                                                 const std::vector<bool>& mask ) :
    mesh_ { mesh }
{
    MLHP_CHECK( mask.size( ) == mesh->ncells( ), "Cell filter size not equal to number of cells." );

    std::tie( expand_, reduce_ ) = detail::filteredIndexMaps( mask );
}

template<size_t D, typename MeshBase> inline
FilteredMeshBase<D, MeshBase>::FilteredMeshBase( const std::shared_ptr<MeshBase>& mesh,
                                                 const std::vector<std::int8_t>& cutstate,
                                                 bool removeCutCells ) :
    mesh_ { mesh }
{
    MLHP_CHECK( cutstate.size( ) == mesh->ncells( ), "Cut states size not equal to number of cells." );

    std::tie( expand_, reduce_ ) = detail::filteredIndexMaps( cutstate, removeCutCells );
}

template<size_t D, typename MeshBase> inline
FilteredMeshBase<D, MeshBase>::FilteredMeshBase( const std::shared_ptr<MeshBase>& mesh,
                                                 const CellIndexVector& filteredCells ) :
    mesh_ { mesh }
{
    MLHP_CHECK( filteredCells.empty( ) || *std::ranges::max_element( filteredCells ) < mesh->ncells( ), 
        "Filtered cell index larger than number of mesh cells." );

    std::tie( expand_, reduce_ ) = detail::filteredIndexMaps( filteredCells, mesh->ncells( ) );
}

template<size_t D, typename MeshBase> inline
const AbsMesh<D>& FilteredMeshBase<D, MeshBase>::unfilteredMesh( ) const
{
    return *mesh_;
}

template<size_t D, typename MeshBase> inline
CellIndex FilteredMeshBase<D, MeshBase>::filteredIndex( CellIndex unfilteredIndex ) const
{
    return reduce_[unfilteredIndex];
}

template<size_t D, typename MeshBase> inline
CellIndex FilteredMeshBase<D, MeshBase>::unfilteredIndex( CellIndex filteredIndex ) const
{
    return expand_[filteredIndex];
}

template<size_t D, typename MeshBase> inline
CellIndex FilteredMeshBase<D, MeshBase>::ncells( ) const
{
    return static_cast<CellIndex>( expand_.size( ) );
}

template<size_t D, typename MeshBase> inline
CellType FilteredMeshBase<D, MeshBase>::cellType( CellIndex cell ) const
{
    return mesh_->cellType( unfilteredIndex( cell ) );
}

template<size_t D, typename MeshBase> inline
void FilteredMeshBase<D, MeshBase>::neighbours( CellIndex cell, size_t side, std::vector<MeshCellFace>& target ) const
{
    // Defined above
    return detail::filteredNeighbours( *this, cell, side, target );
}

template<size_t D, typename MeshBase> inline
MeshMapping<D> FilteredMeshBase<D, MeshBase>::createMapping( ) const
{
    auto mapping = MeshMapping<D> { };

    mapping.mesh = static_cast<const AbsFilteredMesh<D>*>( this );
    mapping.cache = mesh_->createMapping( );

    return mapping;
}

template<size_t D, typename MeshBase> inline
void FilteredMeshBase<D, MeshBase>::prepareMapping( CellIndex cell, MeshMapping<D>& mapping ) const
{
    auto& unfilteredMapping = utilities::cast<MeshMapping<D>>( mapping.cache );

    mesh_->prepareMapping( unfilteredIndex( cell ), unfilteredMapping );

    mapping.icell = cell;
    mapping.mapping = unfilteredMapping.mapping;
}

template<size_t D, typename MeshBase> inline
BackwardMappingFactory<D> FilteredMeshBase<D, MeshBase>::createBackwardMappingFactory( ) const
{
    return detail::filteredBackwardMapping( *this );
}

template<size_t D, typename MeshBase> inline
std::unique_ptr<AbsMapping<D, D - 1>> FilteredMeshBase<D, MeshBase>::createInterfaceMapping( ) const
{
    return mesh_->createInterfaceMapping( );
}

template<size_t D, typename MeshBase> inline
void FilteredMeshBase<D, MeshBase>::prepareInterfaceMappings( MeshCellFace face0,
                                                              MeshCellFace face1,
                                                              AbsMapping<D, D - 1>& mapping0,
                                                              AbsMapping<D, D - 1>& mapping1 ) const
{
    face0.first = unfilteredIndex( face0.first );
    face1.first = unfilteredIndex( face1.first );

    mesh_->prepareInterfaceMappings( face0, face1, mapping0, mapping1 );
}

template<size_t D, typename MeshBase> inline
size_t FilteredMeshBase<D, MeshBase>::memoryUsage( ) const
{
    return utilities::vectorInternalMemory( reduce_, expand_ ) + mesh_->memoryUsage( );
}

template<size_t D> inline
std::unique_ptr<AbsFilteredMesh<D>> FilteredMesh<D>::cloneFiltered( ) const
{
    return std::make_unique<FilteredMesh<D>>( *this );
}

template<size_t D> inline
std::unique_ptr<AbsFilteredMesh<D>> FilteredGrid<D>::cloneFiltered( ) const
{
    return std::make_unique<FilteredGrid<D>>( *this );
}

template<size_t D> inline
std::unique_ptr<AbsGrid<D>> FilteredGrid<D>::cloneGrid( ) const
{
    return std::make_unique<FilteredGrid<D>>( *this );
}

template<size_t D> inline
const AbsGrid<D>& FilteredGrid<D>::unfilteredGrid( ) const 
{
    return *this->mesh_;
}

template<size_t D> inline
CellIndex FilteredGrid<D>::neighbour( CellIndex cell,
                                      size_t axis,
                                      size_t side ) const 
{
    using Base = FilteredMeshBase<D, AbsGrid<D>>;
    
    auto index = unfilteredGrid( ).neighbour( Base::unfilteredIndex( cell ), axis, side );
    
    return index != NoCell ? Base::filteredIndex( index ) : NoCell;
}

template<size_t D, typename MeshBase> inline
MeshUniquePtr<D> FilteredMeshBase<D, MeshBase>::clone( ) const
{
    return this->cloneFiltered( );
}

namespace mesh
{

template<size_t D> inline
auto mapping( const AbsMesh<D>& mesh,
              CellIndex icell )
{
    auto mapping = mesh.createMapping( );

    mesh.prepareMapping( icell, mapping );

    return mapping;
}

template<size_t D> inline
auto fullMapping( const AbsHierarchicalGrid<D>& grid, CellIndex fullIndex )
{
    return mapping( grid, grid.leafIndex( fullIndex ) );
}


template<size_t D> inline
auto map( const AbsMesh<D>& mesh, 
          CellIndex icell,
          std::array<double, D> rst )
{
    return mapping( mesh, icell )( rst );
}

template<size_t D> inline
auto mapFull( const AbsHierarchicalGrid<D>& grid, 
              CellIndex fullIndex,
              std::array<double, D> rst )
{
    return fullMapping( grid, fullIndex )( rst );
}

template<size_t D> inline
std::array<size_t, D> gridsplit( std::array<double, D> lengths,
                                 size_t targetNumber )
{
    if( targetNumber == 0 )
    {
        return array::makeSizes<D>( 0 );
    }

    auto edgeLength = std::pow( array::product( lengths ) / targetNumber, 1.0 / D );
    auto nelements = array::convert<size_t>( array::divide( lengths, edgeLength ) + 0.5 );

    return array::maxArray( nelements, size_t { 1 } );
}

} // namespace mesh
} // namespace mlhp

#endif // MLHP_CORE_MESH_IMPL_HPP
