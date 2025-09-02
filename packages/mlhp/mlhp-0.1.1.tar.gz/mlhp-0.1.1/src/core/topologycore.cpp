// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/topologycore.hpp"
#include "mlhp/core/algorithm.hpp"
#include "mlhp/core/mapping.hpp"

namespace mlhp::topology
{

std::vector<bool> leafMask( const CellIndexVector& parents )
{
    std::vector<bool> mask( parents.size( ), true );

    for( CellIndex iCell = 0; iCell < parents.size( ); ++iCell )
    {
        if( auto parent = parents[iCell]; parent != NoCell )
        {
            mask[parents[iCell]] = false;
        }
    }

    return mask;
}

CellIndexVector leafIndexOrChild( const CellIndexVector& parents,
                                  const std::vector<bool>& leafMask )
{
    auto leafOrChild = algorithm::backwardIndexMap<CellIndex>( leafMask );

    for( CellIndex i = 0; i < parents.size( ); ++i )
    {
        if( auto parent = parents[i]; parent != NoCell )
        {
            leafOrChild[parent] = std::min( i, leafOrChild[parent] );
        }
    }

    return leafOrChild;
}

RefinementLevelVector refinementLevels( const CellIndexVector& parents )
{
    auto levels = RefinementLevelVector( parents.size( ) );
    auto nint = static_cast<std::int64_t>( parents.size( ) );

    [[maybe_unused]]
    auto chunksize = parallel::clampChunksize( levels.size( ), 29 );

    #pragma omp parallel for schedule(dynamic, chunksize)
    for( std::int64_t ii = 0; ii < nint; ++ii )
    {
        auto icell = static_cast<CellIndex>( ii );

        levels[icell] = 0;

        for( auto iparent = parents[icell]; iparent != NoCell; iparent = parents[iparent] )
        {
            levels[icell] += 1;
        }
    }

    return levels;
}

RefinementLevel maxRefinementLevel( const CellIndexVector& parents )
{
    auto maxlevel = RefinementLevel { 0 };
    auto nint = static_cast<std::int64_t>( parents.size( ) );

    [[maybe_unused]]
    auto chunksize = parallel::clampChunksize( parents.size( ), 29 );

    #pragma omp parallel
    { 
        auto localMaxlevel = RefinementLevel { 0 };

        #pragma omp parallel for schedule(dynamic, chunksize)
        for( std::int64_t ii = 0; ii < nint; ++ii )
        {
            auto icell = static_cast<CellIndex>( ii );
            auto level = RefinementLevel { 0 };

            for( auto iparent = parents[icell]; iparent != NoCell; iparent = parents[iparent] )
            {
                level += 1;
            }

            localMaxlevel = std::max( level, localMaxlevel );
        }

        #pragma omp critical
        { 
            maxlevel = std::max( maxlevel, localMaxlevel );
        }
    }

    return maxlevel;
}

template<size_t D>
void checkConsistency( CoordinateConstSpan<D> vertices, 
                       std::span<const size_t> connectivity,
                       std::span<const size_t> offsets,
                       std::span<const CellType> types )
{
    auto str = []( auto value ) { return std::to_string( value ); };

    MLHP_CHECK( offsets.size( ) >= 1 || offsets[0] == 0, "Nonzero offset value at index zero.");

    MLHP_CHECK( offsets.size( ) == types.size( ) + 1, "Inconsistent container sizes: (" + str( 
        offsets.size( ) ) + " offsets vs. " + str( types.size( ) ) + " types." );

    MLHP_CHECK( offsets.size( ) < std::numeric_limits<CellIndex>::max( ), "Requested number "
        "of mesh cells(" + str( offsets.size( ) ) + ") too large for cell index type.");

    for( size_t icell = 0; icell + 1 < offsets.size( ); ++icell )
    {
        MLHP_CHECK( offsets[icell + 1] > offsets[icell], "Offset value " + str( offsets[icell + 1] ) + " at "
            "index " + str( icell + 1 ) + " not larger than previous offset value " + str( offsets[icell] ) + "." );
        MLHP_CHECK( offsets[icell + 1] <= connectivity.size( ), "Offset value " + str( offsets[icell + 1] ) + " is "
            "larger than connectivity array size (" + str( connectivity.size( ) ) + ")." );

        MLHP_CHECK( types[icell] == CellType::NCube || types[icell] == CellType::Simplex, "Cell type not implemented." );
        
        auto nvertices = offsets[icell + 1] - offsets[icell];

        MLHP_CHECK( nvertices == topology::nvertices<D>( types[icell] ), "Invalid number of vertices (" + str(
            nvertices ) + ") for cell " + str( icell ) + " with type " + cellTypeString( types[icell], D, false ) );

        for( size_t ivertex = offsets[icell]; ivertex < offsets[icell + 1]; ++ivertex )
        {
            MLHP_CHECK( connectivity[ivertex] < vertices.size( ), "Connectivity index (" +
                str( connectivity[ivertex] ) + ") of cell " + str( icell ) + " must be " +
                "lower than the number of vertices (" + str( vertices.size( ) ) + ")." );
        }
    }
}

template<size_t D>
void faceVertices( CellType type, size_t iface, std::vector<size_t>& target )
{
    auto size = target.size( );

    // Could make this faster by creating a lookup table
    if( auto subtype = facetype<D>( type, iface ); subtype == CellType::NCube )
    {
        auto [normal, side] = normalAxisAndSide( iface );
        auto n = utilities::binaryPow<size_t>( D - 1 );

        target.resize( size + n );

        for( size_t i = 0; i < n; ++i )
        { 
            auto ijk = array::insert( nd::binaryUnravel<size_t, D - 1>( i ), normal, side );

            target[size + i] = nd::binaryRavel<size_t>( ijk );
        }

    }
    else if( subtype == CellType::Simplex )
    {
        target.resize( size + D );

        auto count = size_t { 0 };

        for( size_t i = 0; i < D + 1; ++i )
        {
            if( i != ( iface + 1 ) % ( D + 1 ) ) 
            {
                target[size + count++] = i;
            }
        }
    }
    else
    {
        MLHP_NOT_IMPLEMENTED;
    }
}

template<size_t D>
NeighboursVector neighbours( std::span<const size_t> connectivity,
                             std::span<const size_t> offsets,
                             std::span<const CellType> types )
{
    if( offsets.empty( ) )
    {
        return { };
    }
    
    auto ncells = offsets.size( ) - 1;

    // Create empty neighbuor data
    auto indices = utilities::allocateLinearizationIndices<CellIndex>( ncells );

    #pragma omp parallel for schedule(static)
    for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( ncells ); ++ii )
    {
        auto icell = static_cast<size_t>( ii );

        indices[icell + 1] = static_cast<CellIndex>( nfaces<D>( types[icell] ) );
    }

    auto data = utilities::sumAndAllocateData<std::pair<CellIndex, std::uint8_t>>( indices, { NoCell, 0 } );

    // Could pre-compute this to trade memory for performance 
    auto globalSortedFaceVertices = [&]( size_t icell, size_t iface, auto& tmp )
    {
        faceVertices<D>( types[icell], iface, utilities::resize0( tmp ) );
                
        for( auto& vertex : tmp )
        {
            vertex = connectivity[offsets[icell] + vertex];
        }

        std::sort( tmp.begin( ), tmp.end( ) );
    };
    
    // For each vertex, list the connected cells
    auto connectedCells = algorithm::invertRelation( offsets, connectivity );

    #pragma omp parallel
    {
        auto faceVertices0 = std::vector<size_t> { };
        auto faceVertices1 = std::vector<size_t> { };

        #pragma omp for schedule(dynamic, 7)
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( ncells ); ++ii )
        {
            auto icell = static_cast<size_t>( ii );
            auto nfacesI = static_cast<size_t>( indices[icell + 1] - indices[icell] );

            for( size_t iface = 0; iface < nfacesI; ++iface )
            {
                // Local vertex indices for current face
                globalSortedFaceVertices( icell, iface, faceVertices0 );

                for( auto vertex : faceVertices0 )
                {
                    // Loop over connected cells and check if cell contains all face vertices
                    for( auto jcell : utilities::linearizedSpan( connectedCells, vertex ) )
                    {
                        if( jcell <= icell )
                        {
                            continue;
                        }

                        auto nfacesJ = static_cast<size_t>( indices[jcell + 1] - indices[jcell] );

                        for( size_t jface = 0; jface < nfacesJ; ++jface )
                        {
                            globalSortedFaceVertices( jcell, jface, faceVertices1 );

                            if( faceVertices0 == faceVertices1 )
                            {
                                data[indices[jcell] + jface] = { static_cast<CellIndex>( icell ), 
                                                                 static_cast<std::uint8_t>( iface ) };

                                data[indices[icell] + iface] = { static_cast<CellIndex>( jcell ), 
                                                                 static_cast<std::uint8_t>( jface ) };
                            }
                        }
                    }
                }
            } 

        } // for icell
    } // omp parallel

    return NeighboursVector { std::move( indices ), std::move( data ) };
}

template<size_t D> 
std::vector<size_t> filterVertices( CoordinateList<D>& vertices,
                                    std::span<size_t> connectivity )
{
    auto ncellvertices = connectivity.size( );
    auto mask = std::vector<size_t>( vertices.size( ), 0 );

    for( size_t ii = 0; ii < ncellvertices; ++ii )
    {
        mask[connectivity[static_cast<size_t>( ii )]] = 1;
    }

    auto nfiltered = size_t { 0 };

    for( size_t ivertex = 0; ivertex < vertices.size( ); ++ivertex )
    {
        if( mask[ivertex] )
        {
            mask[ivertex] = nfiltered;
            vertices[nfiltered] = vertices[ivertex];

            nfiltered += 1;
        }
    }

    auto diff = utilities::ptrdiff( nfiltered );

    vertices.erase( vertices.begin( ) + diff, vertices.end( ) );
    vertices.shrink_to_fit( );

    for( size_t i = 0; i < ncellvertices; ++i )
    {
        connectivity[i] = mask[connectivity[i]];
    }

    return mask;
}

template<size_t D>
void reorderVertices( CoordinateConstSpan<D> vertices,
                      std::span<size_t> connectivity,
                      std::span<const size_t> offsets,
                      std::span<const CellType> types )
{
    #pragma omp parallel
    {
        auto ncells = static_cast<std::int64_t>( offsets.size( ) ) - 1;

        #pragma omp for schedule( static, 512 )
        for( std::int64_t ii = 0; ii < ncells; ++ii )
        {
            auto icell = static_cast<CellIndex>( ii );

            if( types[icell] == CellType::Simplex )
            {
                auto corners = CoordinateArray<D, D + 1> { };

                for( size_t icorner = 0; icorner < corners.size( ); ++icorner )
                {
                    corners[icorner] = vertices[connectivity[offsets[icell] + icorner]];
                }

                auto mapping = SimplexMapping<D> { corners };

                if( mapping.detJ( array::make<D>( 1.0 / ( D + 1 ) ) ) < 0.0 )
                {
                    std::swap( connectivity[offsets[icell]], connectivity[offsets[icell] + 1] );
                }
            }
        }
    } // omp parallel
}

std::string cellTypeString( CellType type, size_t D, bool plural, bool upper )
{
    const char* simplex[] = { "vertex", "line", "triangle", "tetrahedon", "simplex" };
    const char* simplices[] = { "vertices", "lines", "triangles", "tetrahedra", "simplices" };
    const char* ncube[] = { "vertex", "line", "quadrilateral", "hexaedron", "cube" };
    const char* ncubes[] = { "vertices", "lines", "quadrilaterals", "hexaedra", "cubes" };

    auto str = std::string { };
    auto D4 = std::min( D, size_t { 4 } );

    if( type == CellType::Simplex && plural ) str = simplices[D4];
    if( type == CellType::Simplex && !plural ) str = simplex[D4];
    if( type == CellType::NCube && plural ) str = ncubes[D4];
    if( type == CellType::NCube && !plural ) str = ncube[D4];
    
    MLHP_CHECK( str != "", "Cell type string not available.");

    if( upper )
    {
        str[0] = std::toupper( str[0] );
    }

    if( D >= 4 )
    {
        str = std::to_string( D ) + "-" + str;
    }

    return str;
}

#define MLHP_INSTANTIATE_DIM( D )                                                     \
                                                                                      \
    template MLHP_EXPORT                                                              \
    NeighboursVector neighbours<D>( std::span<const size_t> connectivity,             \
                                    std::span<const size_t> offsets,                  \
                                    std::span<const CellType> types );                \
                                                                                      \
    template MLHP_EXPORT                                                              \
    std::vector<size_t> filterVertices( CoordinateList<D>& vertices,                  \
                                        std::span<size_t> connectivity );             \
                                                                                      \
    template MLHP_EXPORT                                                              \
    void reorderVertices( CoordinateConstSpan<D> vertices,                            \
                          std::span<size_t> connectivity,                             \
                          std::span<const size_t> offsets,                            \
                          std::span<const CellType> types );                          \
                                                                                      \
    template MLHP_EXPORT                                                              \
    void checkConsistency( CoordinateConstSpan<D> vertices,                           \
                           std::span<const size_t> connectivity,                      \
                           std::span<const size_t> offsets,                           \
                           std::span<const CellType> types );                         \
                                                                                      \
    template MLHP_EXPORT                                                              \
    void faceVertices<D>( CellType type, size_t iface, std::vector<size_t>& target );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // mlhp::topology
