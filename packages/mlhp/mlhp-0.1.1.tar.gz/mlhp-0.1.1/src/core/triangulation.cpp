// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/triangulation.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/algorithm.hpp"
#include "mlhp/core/quadrature.hpp"

#include <execution>
#include <filesystem>
#include <climits>

namespace mlhp
{

using namespace marching;

template<size_t D>
std::array<double, D> integrateNormalComponents( const SimplexMesh<D, D - 1>& simplexMesh, bool abs )
{
    auto result = std::array<double, D> { };

    #pragma omp parallel
    {   
        auto local = std::array<double, D> { };
        auto ncells = static_cast<std::int64_t>( simplexMesh.ncells( ) );

        #pragma omp for schedule(static)
        for( std::int64_t ii = 0; ii < ncells; ++ii )
        {
            auto weightedNormal = simplexMesh.cellWeightedNormal( static_cast<size_t>( ii ) );

            for( size_t axis = 0; axis < D; ++axis )
            {
                local[axis] += abs ? std::abs( weightedNormal[axis] ) : weightedNormal[axis];
            }
        }

        #pragma omp critical
        {
            result = result + local;
        }
    }

    return result;
}

template<size_t G, size_t L>
double SimplexMesh<G, L>::measure( ) const
{
    auto limit = static_cast<std::int64_t>( ncells( ) );
    auto result = 0.0;

    #pragma omp parallel for schedule( dynamic, 512 ) reduction(+:result)
    for( std::int64_t ii = 0; ii < limit; ++ii )
    {
        result += spatial::simplexMeasure<G, L>( cellVertices( static_cast<size_t>( ii ) ) );
    }

    return result;
}

// https://stackoverflow.com/a/26171886
CoordinateList<3> readStl( const std::string& filename, bool flipOnOppositeNormal )
{
    auto path = std::filesystem::path { filename };
    auto file = std::ifstream { filename };
    auto line = std::string { };
    auto word = std::string { };
    
    MLHP_CHECK( file.is_open( ), "Error parsing stl file (unable to open file)." );

    auto filesize = std::filesystem::file_size( path );

    MLHP_CHECK( filesize >= 15, "Error parsing stl file (smaller than 15 bytes)." );

    auto vertices = CoordinateList<3> { };
    auto normals = CoordinateList<3> { };

    file >> line;

    auto ascii = false;

    // Parse Ascii
    if( line == "solid" )
    {
        while( std::getline( file, line ) )
        {
            auto sstream = std::istringstream { line };

            if( !sstream )
            {
                continue;
            }

            auto parseCoordinates = [&]( auto& target )
            { 
                auto coordinates = std::array<double, 3> { };
            
                for( size_t axis = 0; axis < 3; ++axis )
                {
                    sstream >> coordinates[axis];
                }

                target.push_back( coordinates );
            };
        
            sstream >> word;

            if( word == "vertex" )
            {
                parseCoordinates( vertices );
            }
            else if( word == "facet" )
            {
                sstream >> word;

                MLHP_CHECK( word == "normal", "Error parsing stl file (missing normal)." );

                parseCoordinates( normals );
            }
        }

        if( word == "endsolid" )
        {
            ascii = true;
        }
    }
    
    file.close( );

    // Parse binary
    if( !ascii )
    {
        MLHP_CHECK( sizeof( float ) * CHAR_BIT == 32, "Floats are not 32 bit (required for parsing binary STL)." );
        
        file = std::ifstream( filename, std::ifstream::binary );

        MLHP_CHECK( filesize >= 84, "Error parsing stl file (not ascii and smaller than 84 bytes)." );
        MLHP_CHECK( file.seekg( 80 ), "Error parsing stl file (Unable to seekg after header bytes)." );

        char header[4];

        file.read( header, 4 );

        MLHP_CHECK( file.good( ), "Error parsing stl file (binary header read failed)" );

        constexpr auto facetsize = 3 * 4 * sizeof( float ) + sizeof( int16_t );
        
        auto ntriangles = *reinterpret_cast<uint32_t*>( header );
        auto targetsize = 84 + ntriangles * facetsize;

        MLHP_CHECK( filesize == targetsize, "Error parsing stl file (not ascii and inconsistent size)." );

        vertices.resize( 3 * ntriangles );
        normals.resize( ntriangles );

        for( size_t itriangle = 0; itriangle < ntriangles; ++itriangle )
        {
            char buffer[facetsize];

            auto read = [&, index = size_t { 0 }]( ) mutable
            { 
                return *( reinterpret_cast<float*>( buffer ) + index++ );
            };
            
            file.read( buffer, facetsize );

            MLHP_CHECK( file.good( ), "Error parsing stl file (binary data read failed)" );

            for( size_t axis = 0; axis < 3; ++axis )
            {
                normals[itriangle][axis] = read( );
            }
            
            for( size_t ivertex = 0; ivertex < 3; ++ivertex )
            {
                for( size_t axis = 0; axis < 3; ++axis )
                {
                    vertices[3 * itriangle + ivertex][axis] = read( );
                }
            }

        } // for itriangle

        MLHP_CHECK( file.tellg( ) == static_cast<std::streamoff>( filesize ), 
                    "Error parsing stl file (not at end of file)." );
    
        file.close( );
    }

    // Fix vertex order based on normal vectors
    if( flipOnOppositeNormal )
    {
        for( size_t itriangle = 0; itriangle < normals.size( ); ++itriangle )
        {
            auto& v0 = vertices[3 * itriangle + 0];
            auto& v1 = vertices[3 * itriangle + 1];
            auto& v2 = vertices[3 * itriangle + 2];
        
            auto normal = spatial::triangleNormal( v0, v1, v2 );
            auto dot = spatial::dot( normal, normals[itriangle] );

            // Reverse order with inconsistent normals
            if( std::abs( dot + 1.0 ) < 0.01 )
            {
                std::swap( v1, v2 );
            }
        }
    }

    MLHP_CHECK( vertices.size( ) == 3 * normals.size( ), "Inconsistent sizes." );

    return vertices;
}

template<size_t D>
Triangulation<D> createTriangulation( CoordinateConstSpan<D> vertices )
{
    Triangulation<D> result;

    MLHP_CHECK( vertices.size( ) % 3 == 0, "Vertex number not a multiple of three." );

    result.vertices.resize( vertices.size( ) );
    result.cells.resize( vertices.size( ) / 3 );

    std::copy( vertices.begin( ), vertices.end( ), result.vertices.begin( ) );

    for( size_t i = 0; i < result.cells.size( ); ++i )
    {
        result.cells[i][0] = 3 * i + 0;
        result.cells[i][1] = 3 * i + 1;
        result.cells[i][2] = 3 * i + 2;
    }

    return result;
}

template<size_t G, size_t L> requires( G >= L )
SimplexMesh<G, L> mergeSimplexMeshes( ReferenceVector<const SimplexMesh<G, L>> simplexMeshes )
{
    auto nvertices = size_t { 0 };
    auto nsimplices = size_t { 0 };

    for( auto& simplexMesh : simplexMeshes )
    {
        nvertices += simplexMesh.get( ).nvertices( );
        nsimplices += simplexMesh.get( ).ncells( );
    }

    auto result = SimplexMesh<G, L> { };
    
    result.vertices.resize( nvertices );
    result.cells.resize( nsimplices );

    if constexpr( L == 0 && G == 1 )
    {
        result.normals.resize( nsimplices );
    }

    auto voffset = size_t { 0 };
    auto soffset = size_t { 0 };

    for( auto& wrapper : simplexMeshes )
    {
        auto& simplexMesh = wrapper.get( );

        for( size_t isimplex = 0; isimplex < simplexMesh.cells.size( ); ++isimplex )
        {
            if constexpr( L == 0 && G == 1 )
            {
                result.normals[soffset] = simplexMesh.normals[isimplex];
            }

            result.cells[soffset++] = array::add( simplexMesh.cells[isimplex], voffset );
        }

        for( size_t ivertex = 0; ivertex < simplexMesh.vertices.size( ); ++ivertex )
        {
            result.vertices[voffset++] = simplexMesh.vertices[ivertex];
        }
    }

    return result;
}

template<size_t D>
std::shared_ptr<Triangulation<D>> createSharedTriangulation( CoordinateConstSpan<D> vertices )
{
    return std::make_shared<Triangulation<D>>( createTriangulation( vertices ) );
}

namespace
{

template<size_t D>
std::vector<std::array<double, D>> defaultRayDirections( )
{
    static_assert( D > 0 && D <= 3, "Not implemented." );

    if constexpr( D == 1 )
    {
        return { std::array { 1.0 } };
    }

    if constexpr( D == 2 )
    {
        return
        {
            std::array {  1.231,  -0.818 },
            //std::array { -1.473,  0.236 },
            //std::array {  0.153, -1.348 }
        };
    }

    if constexpr( D == 3 )
    {
        return
        {
            std::array { 0.3123, -0.423, 0.8323 },
            //std::array { 0.1123, 0.923, -0.2323 },
            //std::array { -0.7123, 0.123, -0.5323 }
        };
    }
}

template<size_t D>
auto normalizeAndInvert( std::span<std::array<double, D>> rayDirections )
{
    auto invDirections = std::vector<std::array<double, D>>( rayDirections.size( ) );

    for( size_t i = 0; i < rayDirections.size( ); ++i )
    {
        MLHP_CHECK( spatial::norm( rayDirections[i] ) > 1e-10, "Zero length ray." );

        rayDirections[i] = spatial::normalize( rayDirections[i] );
        invDirections[i] = spatial::invert( rayDirections[i] );
    }

    return invDirections;
}

} // namespace

template<size_t D>
bool pointMembershipTest( const SimplexMesh<D, D - 1>& simplexMesh,
                          const KdTree<D>& tree, 
                          const std::array<double, D>& rayOrigin,
                          std::span<const std::array<double, D>> rayDirections,
                          std::span<const std::array<double, D>> invDirections,
                          std::vector<size_t>& itemTarget )
{
    auto ninside = size_t { 0 };

    for( size_t i = 0; i < rayDirections.size( ); ++i )
    {
        // Gather simplex indices along the ray direction until we encounter
        // and empty cell (whos cut state is stored in the tree data structure)
        auto result = kdtree::accumulateItemsInv( tree, rayOrigin, 
            invDirections[i], utilities::resize0( itemTarget ) );

        // First tree cell is empty or point was outside tree bounding box, 
        // so we directly know our state
        if( result.cellCount <= 1 && result.cellState != 0 )
        {
            return result.cellState > 0;
        }

        auto count = size_t { 0 };

        // There are two cases handled in this loop:
        // - result.cellState == 0: Tree traversal stopped early, so we must count only
        //   intersections that occur before the tree cell the traveral stopped at.
        // - result.cellState != 0: Tree traversal stopped at a "cut cell", i.e. it exited 
        //   the tree bounding box, so we just count intersections without distance checking.
        for( auto itemIndex : itemTarget )
        {
            auto vertices = simplexMesh.cellVertices( itemIndex );
            auto t = spatial::simplexRayIntersection<D>( vertices, rayOrigin, rayDirections[i] );

            // I hope the midpoint makes this more robust. The problem is that there can be
            // triangles/lines lying flat directly on the faces of the bounding box we stopped at.
            // So mathematically the condition could be t <= tmin or alternatively t < tmax. 
            // But numerically who knows. Also, we make sure in the kd tree state initialization
            // that we don't assign states to empty cells. 
            count += t != std::nullopt && ( result.cellState == 0 || t < 
                std::midpoint( result.tminmax[0], result.tminmax[1] ) );
        }

        // Check if number of intersections is even or odd, but invert result 
        // if the tree search stopped at an empty tree cell that is inside
        ninside += ( count % 2 ) != ( result.cellState == 1 );
    }

    // Return ninside / ntotal >= 0.5 (something like the average result)
    return ( 2 * ninside ) / rayDirections.size( );
}

template<size_t D>
auto initializeTreeState( const SimplexMesh<D, D - 1>& simplexMesh,
                          KdTree<D>& kdTree,
                          std::span<const std::array<double, D>> rayDirections,
                          std::span<const std::array<double, D>> invDirections )
{
    auto states = std::vector<std::int16_t>( kdTree.nfull( ), 0 );
    auto center = 5.083034105565482e-3 * defaultRayDirections<D>( )[0];

    #pragma omp parallel
    {
        auto nleaves = static_cast<std::int64_t>( kdTree.ncells( ) );
        auto mapping = kdTree.createMapping( );
        auto items = std::vector<size_t> { };

        #pragma omp for
        for( std::int64_t ii = 0; ii < nleaves; ++ii )
        {
            auto ileaf = static_cast<CellIndex>( ii );
            auto ifull = kdTree.fullIndex( ileaf );
            auto state = std::int16_t { 0 };
            auto bounds = kdTree.boundingBox( );
            auto minLength = array::minElement( bounds[1] - bounds[0] );

            if( kdTree.itemsFull( ifull ).empty( ) && minLength > 0.0 )
            {
                kdTree.prepareMapping( ileaf, mapping );

                state = pointMembershipTest<D>( simplexMesh, kdTree, mapping( 
                    center ), rayDirections, invDirections, items ) ? 1 : -1;
            }

            states[ifull] = state;
        }

        #pragma omp barrier
        { }

        #pragma omp for schedule(static)
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( states.size( ) ); ++ii )
        {
            auto icell = static_cast<CellIndex>( ii );

            kdTree.stateFull( icell, states[icell] );
        }
    }
}

ImplicitFunction<3> rayIntersectionDomainFromStl( const std::string& stlfile,
                                                  const CoordinateList<3>& rays )
{
    return rayIntersectionDomain<3>( std::make_shared<Triangulation<3>>(
        createTriangulation<3>( readStl( stlfile ) ) ), nullptr, rays );
}

template<size_t D>
ImplicitFunction<D> rayIntersectionDomain( memory::vptr<const SimplexMesh<D, D - 1>> simplexMesh,
                                           memory::vptr<KdTree<D>> kdTree,
                                           const CoordinateList<D>& rays )
{
    auto rayDirections = utilities::copyShared( rays );

    if( kdTree.get( ) == nullptr )
    {
        kdTree = utilities::moveShared( buildKdTree( kdtree::makeObjectProvider( simplexMesh ) ) );
    }

    // Initialize rays for point membership if none are given
    if( rayDirections->empty( ) )
    {
        *rayDirections = defaultRayDirections<D>( );
    }

    auto invDirections = utilities::moveShared( normalizeAndInvert<D>( *rayDirections ) );

    // Initialize uncut cells of the kdtree by testing their midpoint
    initializeTreeState<D>( *simplexMesh, *kdTree, *rayDirections, *invDirections );

    // Create inside-outside test function that first checks tree and then lines
    auto cache = std::make_shared<utilities::ThreadLocalContainer<std::vector<size_t>>>( );

    return [=]( std::array<double, D> xyz ) -> bool
    {
        // These checks are not necessary, but are a bit faster
        if( auto index = kdTree->fullIndexAt( xyz ); index == NoCell )
        {
            return false;
        }
        else if( auto state = kdTree->stateFull( index ); state != 0 )
        {
            return state > 0;
        }

        return pointMembershipTest<D>( *simplexMesh, *kdTree, xyz, 
            *rayDirections, *invDirections, cache->get( ) );
    };
}

namespace
{

template<size_t D>
std::optional<std::pair<size_t, size_t>> planarOnFace( std::span<const std::array<double, D>> vertices )
{
    for( size_t axis = 0; axis < D; ++axis )
    {
        for( size_t side = 0; side < 2; ++side )
        {
            auto x = side ? 1.0 : -1.0;
            auto planar = true;

            for( size_t ivertex = 0; ivertex < vertices.size( ); ++ivertex )
            {
                planar = planar && std::abs( vertices[ivertex][axis] - x ) < 1e-8;
            }

            if( planar )
            {
                return std::pair { axis, side };
            }
        }
    }

    return std::nullopt;
}

// If we have triangles/lines that are aligned with a face in the local coordinate system we have
// to choose which side to take. When the refinement level is different, we have two options:
// choose the finer element or the coarse one. The coarser one makes more sense since continuity
// or weak coupling should keep elements together. There may still be corner cases where points
// are not on the coarse element's face, but end up being on fine elements' face.
template<size_t D>
bool intersectThisSide( const AbsMesh<D>& mesh, CellIndex icell, MeshCellFaces& neighbors, size_t iface )
{
    mesh.neighbours( icell, iface, utilities::resize0( neighbors ) );

    // This element is either on the boundary (0 neighbours) or the coarser neighbor (multiple neighbours)
    if( neighbors.size( ) != 1 )
    {
        return true;
    }

    // This element must be finer or on the same level
    auto [neighborIndex, neighborFace] = neighbors[0];

    mesh.neighbours( neighborIndex, neighborFace, utilities::resize0( neighbors ) );

    MLHP_CHECK_DBG( !neighbors.empty( ), "Invalid mesh topology (this "
                    "cell is not a neighbour of the neighbour of this cell)." );

    // If on the same level, choose the cell with smaller index
    if( neighbors.size( ) == 1 )
    {
        return icell < neighborIndex;
    }

    // The other element has multiple neighbours, so this element is finer (we want to select the other one)
    return false;
}

template<size_t D>
auto backwardsMapVertices( std::span<std::array<double, D>> vertices,
                           const MeshMapping<D>& forwardMapping )
{
    for( auto& vertex : vertices )
    {
        if( auto rst = mapBackward( forwardMapping, vertex ) )
        {
            vertex = *rst;
        }
        else
        {
            // One can probably make it work for general linear quads/hexahedra by performing
            // the intersection in global coordinates instead of reference coordinates, but 
            // simplices already work, so not sure this would be worth the effort. It should
            // not be hard to do the classification in the polygon clipping algorithm with a 
            // dot product and then intersect/interpolate with non-aligned plane.
            MLHP_THROW(
                "Backward mapping did not converge. Mesh intersection currently works only for "
                "elements whose mappings are affine transformations, i.e. the mapping must be "
                "invertible. Triangles, for example are affine, but quadrilaterals are only aff"
                "ine in the case of rectangles or parallelograms (orientation does not matter)."
            );
        }
    }
}

template<size_t D>
auto determineLocalBoundingBox( const AbsMesh<D>& mesh,
                                CellIndex icell,
                                std::span<std::array<double, D>> vertices,
                                std::vector<MeshCellFace>& neighbours )
{
    auto localBounds = std::optional { std::array { array::make<D>( -1.0 ), array::make<D>( 1.0 ) } };

    if( auto planar = planarOnFace<D>( vertices ) )
    {
        if( intersectThisSide( mesh, icell, neighbours, 2 * planar->first + planar->second ) )
        {
            ( *localBounds )[0][planar->first] = std::numeric_limits<double>::lowest( );
            ( *localBounds )[1][planar->first] = std::numeric_limits<double>::max( );
        }
        else
        {
            localBounds = std::nullopt;
        }
    }

    return localBounds;
}

template<size_t G, size_t L>
void appendClippedSimplex( std::span<const std::array<double, G>> polygon,
                           std::vector<std::array<size_t, L + 1>>& indices, 
                           double reference )
{
    if constexpr ( L == 0 )
    {
        indices.push_back( std::array<size_t, 1> { 0 } );
    }

    if constexpr ( L == 1 )
    {
        if( spatial::distance( polygon[0], polygon[1] ) > 1e-12 * reference )
        {
            indices.push_back( std::array<size_t, 2> { 0, 1 } );
        }
    }

    if constexpr ( L == 2 )
    {
        for( size_t ivertex = 1; ivertex + 1 < polygon.size( ); ++ivertex )
        {
            auto area = spatial::triangleArea( polygon[0], polygon[ivertex], polygon[ivertex + 1] );

            if( area > 1e-8 * reference )
            {
                indices.push_back( std::array<size_t, 3> { 0, ivertex, ivertex + 1 } );
            }
        }
    }
}

} // namespace

template<size_t G, size_t L> requires( G >= L )
CellAssociatedSimplices<G, L> intersectWithMesh( const SimplexMesh<G, L>& simplexMesh,
                                                 const AbsMesh<G>& mesh,
                                                 const KdTree<G>& tree )
{
    static constexpr bool separateNormals = G == 1 && L == 0;

    auto ncells = static_cast<std::int64_t>( mesh.ncells( ) );
    auto intersected = SimplexMesh<G, L> { };
    auto celldata = SimplexCellAssociation<G> { };
    auto vertexOffsets = std::vector<size_t>( mesh.ncells( ) + 1, 0 );

    celldata.offsets.resize( mesh.ncells( ) + 1, 0 );

    #pragma omp parallel
    {
        auto localXyz = CoordinateList<G> { };
        auto localRst = CoordinateList<G> { };
        auto localNormals = CoordinateList<G> { };
        auto localCells = std::vector<CellIndex> { };
        auto localSimplices = std::vector<std::array<size_t, L + 1>> { };

        auto simplices = std::vector<size_t> { };
        auto polygonTarget = std::array<std::array<double, G>, 3 * ( L + 1 )> { };
        auto neighbors = std::vector<MeshCellFace> { };

        auto forwardMapping = mesh.createMapping( );

        #pragma omp for schedule(dynamic)
        for( std::int64_t ii = 0; ii < ncells; ++ii )
        {
            utilities::resize0( simplices );

            auto icell = static_cast<CellIndex>( ii );

            // Get mesh cell bounding box
            mesh.prepareMapping( icell, forwardMapping );

            MLHP_CHECK( forwardMapping.type == CellType::NCube, "Cell type not implemented." );

            auto beforeSize = localSimplices.size( );
            auto bounds = mesh::boundingBox( forwardMapping, 2 );
            auto reference = array::maxElement( bounds[1] - bounds[0] );

            // Accumulate simplices inside mesh cell bounding box
            kdtree::accumulateItems( tree, bounds, simplices );

            // Loop over candidate simplices
            for( auto isimplex : simplices )
            {
                // Map triangle vertices to cell local coordinates
                auto vertices = simplexMesh.cellVertices( isimplex );
                    
                backwardsMapVertices<G>( std::span { vertices }, forwardMapping );

                if( auto localBounds = determineLocalBoundingBox<G>( mesh, icell, vertices, neighbors ) )
                {
                    std::copy( vertices.begin( ), vertices.end( ), polygonTarget.begin( ) );

                    // Clip mapped triangle to local coordinate bounds
                    auto polygon = spatial::clipSimplex<G, L>( polygonTarget, *localBounds );

                    // Remesh and append new simplices
                    if( !polygon.empty( ) )
                    {
                        auto simplexOffset = localSimplices.size( );
                        auto vertexOffset = vertexOffsets[icell + 1];

                        for( auto& vertex : polygon )
                        {
                            localRst.push_back( vertex );
                            
                            vertex = forwardMapping( vertex );

                            localXyz.push_back( vertex );

                            vertexOffsets[icell + 1] += 1;
                        }

                        appendClippedSimplex<G, L>( polygon, localSimplices, reference );
                        
                        celldata.offsets[icell + 1] += localSimplices.size( ) - simplexOffset;

                        for( size_t isubcell = simplexOffset; isubcell < localSimplices.size( ); ++isubcell )
                        {
                            localSimplices[isubcell] = array::add( localSimplices[isubcell], vertexOffset );

                            // Add point normals
                            if constexpr( separateNormals )
                            {
                                localNormals.push_back( simplexMesh.normals[isimplex] );
                            }
                        }
                    }
                }
            } // for isimplex
            
            if( localSimplices.size( ) != beforeSize )
            {
                localCells.push_back( icell );
            }

        } // for icell

        #pragma omp single
        {
            std::partial_sum( celldata.offsets.begin( ), celldata.offsets.end( ), celldata.offsets.begin( ) );
            std::partial_sum( vertexOffsets.begin( ), vertexOffsets.end( ), vertexOffsets.begin( ) );

            intersected.vertices.resize( vertexOffsets.back( ) );
            intersected.cells.resize( celldata.offsets.back( ) );
            celldata.rst.resize( vertexOffsets.back( ) );

            if constexpr( separateNormals )
            {
                intersected.normals.resize( celldata.offsets.back( ) );
            }
        }

        auto localVertexOffset = size_t { 0 };
        auto localSimplexOffset = size_t { 0 };

        for( auto icell : localCells )
        {
            auto nvertices = vertexOffsets[icell + 1] - vertexOffsets[icell];
            auto nsimplices = celldata.offsets[icell + 1] - celldata.offsets[icell];

            for( size_t ivertex = 0; ivertex < nvertices; ++ivertex )
            {
                auto globalIndex = vertexOffsets[icell] + ivertex;
                auto localIndex = localVertexOffset + ivertex;

                intersected.vertices[globalIndex] = localXyz[localIndex];
                celldata.rst[globalIndex] = localRst[localIndex];
            }

            for( size_t isimplex = 0; isimplex < nsimplices; ++isimplex )
            {
                auto globalIndex = celldata.offsets[icell] + isimplex;
                auto localIndex = localSimplexOffset + isimplex;

                intersected.cells[globalIndex] = array::add( localSimplices[localIndex], vertexOffsets[icell] );

                if constexpr( separateNormals )
                {
                    intersected.normals[globalIndex] = localNormals[localIndex];
                }
            }

            localVertexOffset += nvertices;
            localSimplexOffset += nsimplices;
        }
    }

    return std::pair { std::move( intersected ), std::move( celldata ) };
}

template<size_t D>
SimplexMesh<D, D - 1> createSkeletonMesh( const AbsMesh<D>& mesh )
{
    auto ncells = static_cast<std::int64_t>( mesh.ncells( ) );
    auto results = std::vector<SimplexMesh<D, D - 1>> { };

    #pragma omp parallel
    {
        auto neighbors = MeshCellFaces { };
        auto cellMapping = mesh.createMapping( );
        auto interface0 = mesh.createInterfaceMapping( );
        auto interface1 = mesh.createInterfaceMapping( );
        auto boundaryMapping = FaceMapping<D>( CellType::NCube, 0 );
        auto simplexMesh = SimplexMesh<D, D - 1> { };

        auto createFaceMesh = [&]( const AbsMapping<D, D - 1>& faceMapping )
        {
            MLHP_CHECK( faceMapping.type == CellType::NCube, "Cell type not implemented." );

            auto offset = simplexMesh.vertices.size( );

            if constexpr( D > 1 )
            {
                nd::execute( array::makeSizes<D - 1>( 2 ), [&]( std::array<size_t, D - 1> ij ) 
                { 
                    auto cellRst = faceMapping( 2 * array::convert<double>( ij ) - 1.0 );

                    simplexMesh.vertices.push_back( cellMapping( cellRst ) );
                } );
            }
            else
            {
                simplexMesh.vertices.push_back( cellMapping( faceMapping( { } ) ) );
            }

            for( const auto& index : spatial::simplexSubdivisionIndices<D - 1>( ) )
            {
                simplexMesh.cells.push_back( array::add( index, offset ) );

                if constexpr( D == 1 )
                {
                    simplexMesh.normals.push_back( std::array { 1.0 } );
                }
            }
        };

        #pragma omp for schedule(dynamic)
        for( std::int64_t ii = 0; ii < ncells; ++ii )
        {
            auto icell = static_cast<CellIndex>( ii );
            auto nfaces = mesh.nfaces( icell );
            
            mesh.prepareMapping( icell, cellMapping );

            for( size_t iface = 0; iface < nfaces; ++iface )
            {
                mesh.neighbours( icell, iface, utilities::resize0( neighbors ) );

                if( neighbors.empty( ) )
                {
                    boundaryMapping.reset( mesh.cellType( icell ), iface );

                    createFaceMesh( boundaryMapping );
                }

                for( size_t ineighbor = 0; ineighbor < neighbors.size( ); ++ineighbor )
                {
                    if( neighbors[ineighbor].first < icell )
                    {
                        mesh.prepareInterfaceMappings( { icell, iface }, 
                            neighbors[ineighbor], *interface0, *interface1 );

                        createFaceMesh( *interface0 );
                    }
                } // for ineighbor
            } // for iface
        } // for icell

        #pragma omp critical
        {
            results.push_back( simplexMesh );
        }
    } // omp parallel

    auto references = std::vector<std::reference_wrapper<const SimplexMesh<D, D - 1>>> { };

    for( auto& result : results )
    {
        references.emplace_back( result );
    }

    return mergeSimplexMeshes( references );
}

template<size_t D>
SimplexQuadrature<D>::SimplexQuadrature( memory::vptr<const SimplexMesh<D, D - 1>> simplexMesh,
                                         memory::vptr<const SimplexCellAssociation<D>> celldata,
                                         const QuadratureOrderDeterminor<D>& order ) :
    simplexMesh_ { std::move( simplexMesh ) }, celldata_ { std::move( celldata ) }, order_ { order }
{ }

template<size_t D>
typename AbsQuadratureOnMesh<D>::AnyCache SimplexQuadrature<D>::initialize( ) const
{
    using ThisCache = std::tuple<QuadraturePointCache, std::vector<std::array<double, D - 1>>, std::vector<double>>;

    return ThisCache { };
}

template<size_t D>
void SimplexQuadrature<D>::distribute( const MeshMapping<D>& mapping,
                                       std::array<size_t, D> orders,
                                       CoordinateList<D>& rst,
                                       CoordinateList<D>& normals,
                                       std::vector<double>& weights,
                                       typename AbsQuadratureOnMesh<D>::AnyCache& anyCache ) const
{ 
    using ThisCache = std::tuple<QuadraturePointCache, std::vector<std::array<double, D - 1>>, std::vector<double>>;

    auto& [quadratureCache, rs_, weights_] = utilities::cast<ThisCache>( anyCache );

    utilities::resize0( rs_, weights_ );

    auto order = array::maxElement( order_( mapping.icell, orders ) );

    simplexQuadrature( array::make<D - 1>( order ), rs_, weights_, quadratureCache );

    auto begin = celldata_->offsets[mapping.icell];
    auto end = celldata_->offsets[mapping.icell + 1];

    for( size_t icell = begin; icell < end; ++icell )
    {
        auto localVertices = celldata_->cellLocalVertices( *simplexMesh_, icell );
        auto globalNormal = simplexMesh_->cellNormal( icell );

        auto localTriangle = SimplexMapping<D, D - 1> { localVertices };
        auto localMeasure = spatial::simplexMeasure<D, D - 1>( localVertices );

        if( localMeasure <= 1e-12 || globalNormal == array::make<D>( 0.0 ) )
        {
            continue;
        }

        auto [rsize, wsize, nsize] = utilities::increaseSizes( rs_.size( ), rst, weights, normals );

        for( size_t ipoint = 0; ipoint < rs_.size( ); ++ipoint )
        {
            auto [coords, J0] = map::withJ( localTriangle, rs_[ipoint] );
            auto [xyz, J1] = map::withJ( mapping, coords );

            auto J = spatial::concatenateJacobians<D, D, D - 1>( J0, J1 );
            auto detJ = spatial::computeDeterminant<D, D - 1>( J );
                
            rst[rsize + ipoint] = coords;
            weights[wsize + ipoint] = weights_[ipoint] * detJ;
            normals[nsize + ipoint] = globalNormal;
        }
    }
}

namespace
{

template<size_t G, size_t L>
auto internalFilterSimplexMesh( const SimplexMesh<G, L>& simplexMesh,
                                const ImplicitFunction<G>& function,
                                size_t nseedpoints )
{
    // Compute masks
    auto ncells0 = simplexMesh.ncells( );
    auto vertexMask = std::vector<std::uint8_t>( simplexMesh.nvertices( ), false );
    auto cellMask = std::vector<std::uint8_t>( ncells0, false );

    for( size_t icell = 0; icell < ncells0; ++icell )
    {
        bool keep = true;

        if constexpr( L > 0 )
        { 
            auto rstGenerator = spatial::makeGridPointGenerator<L>( 
                array::make<L>( nseedpoints ), array::make<L>( 1.0 ), { } );

            auto mapping = SimplexMapping<G, L> { simplexMesh.cellVertices( icell ) };
            auto count = size_t { 0 }, total = size_t { 0 };
        
            nd::executeTriangularBoundary<L>( nseedpoints, [&]( std::array<size_t, L> ijk )
            {
                count += function( mapping( rstGenerator( ijk ) ) );
                total += 1;
            } );

            keep = count == total;
        }
        else
        {
            keep = function( simplexMesh.cellVertices( icell )[0] );
        }

        if( keep )
        {
            cellMask[icell] = true;

            for( size_t ivertex = 0; ivertex < L + 1; ++ivertex )
            {
                vertexMask[simplexMesh.cells[icell][ivertex]] = true;
            }
        }
    }

    // Construct filtered simplexMesh
    auto vertexForwardMap = algorithm::forwardIndexMap<size_t>( vertexMask );
    auto vertexBackwardMap = algorithm::backwardIndexMap<size_t>( std::move( vertexMask ) );
    auto cellForwardMap = algorithm::forwardIndexMap<size_t>( std::move( cellMask ) );

    auto filtered = SimplexMesh<G, L> { };

    filtered.vertices.resize( vertexForwardMap.size( ) );
    filtered.cells.resize( cellForwardMap.size( ) );

    if constexpr ( L == 0 )
    {
        MLHP_CHECK( simplexMesh.normals.size( ) == simplexMesh.cells.size( ), 
            "Invalid number of normals in SimplexMesh." );

        filtered.normals.resize( cellForwardMap.size( ) );
    }

    for( size_t ivertex = 0; ivertex < vertexForwardMap.size( ); ++ivertex )
    {
        filtered.vertices[ivertex] = simplexMesh.vertices[vertexForwardMap[ivertex]];
    }

    for( size_t icell = 0; icell < cellForwardMap.size( ); ++icell )
    {
        filtered.cells[icell] = simplexMesh.cells[cellForwardMap[icell]];

        for( size_t ivertex = 0; ivertex < L + 1; ++ivertex )
        {
            filtered.cells[icell][ivertex] = vertexBackwardMap[filtered.cells[icell][ivertex]];
        }

        if constexpr( L == 0 )
        {
            filtered.normals[icell] = simplexMesh.normals[cellForwardMap[icell]];
        }
    }

    return std::tuple { std::move( filtered ), std::move( vertexForwardMap ), std::move( cellMask ) };
}

} // namespace

template<size_t G, size_t L> requires( G >= L ) 
SimplexMesh<G, L> filterSimplexMesh( const SimplexMesh<G, L>& simplexMesh,
                                     const ImplicitFunction<G>& function,
                                     size_t nseedpoints )
{
    return std::get<0>( internalFilterSimplexMesh( simplexMesh, function, nseedpoints ) );
}

template<size_t G, size_t L> requires( G >= L ) 
CellAssociatedSimplices<G, L> filterSimplexMesh( const SimplexMesh<G, L>& simplexMesh,
                                                 const SimplexCellAssociation<G>& celldata,
                                                 const ImplicitFunction<G>& function,
                                                 size_t nseedpoints )
{
    MLHP_CHECK( !celldata.offsets.empty( ), "Empty offset vector." );

    auto [filteredSimplexMesh, vertexMap, cellMask] = 
        internalFilterSimplexMesh( simplexMesh, function, nseedpoints );

    auto filteredCelldata = SimplexCellAssociation<G> { };
    auto nvertices = filteredSimplexMesh.vertices.size( );
    auto ncells = celldata.offsets.size( ) - 1;

    filteredCelldata.rst.resize( nvertices );
    filteredCelldata.offsets.resize( ncells + 1 );
    filteredCelldata.offsets[0] = 0;

    for( size_t ivertex = 0; ivertex < nvertices; ++ivertex )
    {
        filteredCelldata.rst[ivertex] = celldata.rst[vertexMap[ivertex]];
    }

    for( auto icell = size_t { 0 }; icell < ncells; ++icell )
    {
        auto nsimplices = std::accumulate( utilities::begin( cellMask, celldata.offsets[icell] ),
                                           utilities::begin( cellMask, celldata.offsets[icell + 1] ),
                                           size_t { 0 } );

        filteredCelldata.offsets[icell + 1] = filteredCelldata.offsets[icell] + nsimplices;
    }

    return std::pair { std::move( filteredSimplexMesh ), std::move( filteredCelldata ) };
}

template<size_t D>
size_t SimplexCellAssociation<D>::memoryUsage( ) const
{
    return utilities::vectorInternalMemory( rst, offsets );
}

namespace kdtree
{

template<size_t G, size_t L> requires ( G >= L )
kdtree::ObjectProvider<G> makeObjectProvider( memory::vptr<const SimplexMesh<G, L>> simplexMesh, bool clip )
{
    auto create = [simplexMesh]<bool noclip>( )
    {
        std::function provider = [simplexMesh]( size_t icell, const spatial::BoundingBox<G>& box )
        {
            auto vertices = simplexMesh->cellVertices( icell );

            return spatial::boundingBoxAnd( noclip ? spatial::boundingBox<G>( vertices ) :
                spatial::simplexClippedBoundingBox<G, L>( vertices, box ), box );
        };

        return utilities::makeIndexRangeFunction( simplexMesh->ncells( ), provider );
    };

    return clip ? create.template operator()<false>( ) : create.template operator()<true>( );
}

} // kdtree

// Contains logic for creating grid vertices and corner-subdivision vertices
// for a non-parallel setting (e.g. used within the element reference coordinates)
template<size_t D, marching::InstantiatedIndex Index>
struct SmallMarchingCubes
{
    static constexpr Index NoVertex = std::numeric_limits<Index>::max( );
	
    std::array<size_t, D> ncells;                     // number of cells for grid
    std::array<size_t, D> npoints;                    // ncells + 1
    std::array<size_t, D> cornerStrides;              // Strides for indexing ND-array of corner vertices
    std::array<size_t, D + 1> edgeOffset;             // Offset to the edge subdivision vertices (placed after corners)
    std::array<std::array<size_t, D>, D> edgeStrides; // Strides for indexing ND-array of edge subdivision vertices

    // Maps "theoretical index" to the actually created vertex
    std::vector<Index> vertexMap;

    // Pointer to the vertex vector that we should use when creating new vertices
    CoordinateList<D>* xyz;

    void reset( std::array<size_t, D> resolution, 
                CoordinateList<D>* coordinateList )
    {
        xyz = coordinateList;

        bool rebuild = resolution != ncells || resolution == array::makeSizes<D>( 0 );

        if( rebuild  )
        {
            ncells = resolution;
            npoints = array::add( ncells, size_t { 1 } );
            cornerStrides = nd::stridesFor( npoints );
            edgeOffset[0] = array::product( npoints );

            for( size_t axis = 0; axis < D; ++axis )
            {
                auto nedges = array::setEntry( npoints, axis, ncells[axis] );

                edgeStrides[axis] = nd::stridesFor( nedges );
                edgeOffset[axis + 1] = edgeOffset[axis] + edgeStrides[axis][0] * nedges[0];
            }
        }

        vertexMap.resize( edgeOffset.back( ) );
    
        std::fill( vertexMap.begin( ), vertexMap.end( ), NoVertex );
    }
    
    template<typename Create>
    Index vertexIndex( std::array<size_t, D> ijk, Create&& create ) 
    { 
        auto index = nd::linearIndex( ijk, cornerStrides );

        if( vertexMap[index] == NoVertex )
        {
            vertexMap[index] = static_cast<Index>( xyz->size( ) );

            xyz->push_back( create( ijk ) );
        }

        return vertexMap[index];
    }

    template<typename Create>
    Index edgeIndex( std::array<size_t, D> ijk0, std::array<size_t, D> ijk1, Create&& create ) 
    { 
        auto axis = size_t { 0 };

        for( size_t i = 0; i < D; ++i )
        {
            if( ijk0[i] != ijk1[i] )
            {
                axis = i;
                break;
            }
        }

        auto ijk = array::setEntry( ijk0, axis, std::min( ijk0[axis], ijk1[axis] ) );
        auto index = nd::linearIndex( ijk, edgeStrides[axis] ) + edgeOffset[axis];

        if( vertexMap[index] == NoVertex )
        {
            vertexMap[index] = static_cast<Index>( xyz->size( ) );
                
            xyz->push_back( create( ijk0, ijk1 ) );
        }

        return vertexMap[index];
    }
};

namespace marching
{

template<size_t D>
void evaluateGrid( const AbsMapping<D>& mapping,
                   const ImplicitFunction<D>& function,
                   std::array<size_t, D> resolution,
                   std::array<std::vector<double>, D>& rstGrid,
                   std::vector<bool>& evaluations )
{
    spatial::cartesianTickVectors( resolution, array::make<D>( 2.0 ), array::make<D>( -1.0 ), rstGrid );

    auto npoints = array::add<size_t, D>( resolution, 1 );

    evaluations.resize( array::product( npoints ) );

    nd::executeWithIndex( npoints, [&]( std::array<size_t, D> ijk, size_t index )
    { 
        evaluations[index] = function( mapping.map( array::extract( rstGrid, ijk ) ) );
    } );
}

} // marching

namespace
{

template<size_t D>
auto boundaryCellSpan( size_t index )
{
    static_assert( D > 0 && D <= 3, "Not implemented." );

    std::span<const std::uint16_t> indices;
    std::span<const std::uint8_t> data;

    if constexpr( D == 1 )
    {
        // 0 (00), 1 (01), 2 (10), 3 (11)
        static constexpr std::array<std::uint16_t, 5> indices1D = { 0, 0, 1, 2, 2 };
        static constexpr std::array<std::uint8_t, 2> data1D = { 0, 0 };

        indices = indices1D;
        data = data1D;
    }

    if constexpr( D == 2 )
    {
        indices = lineIndices;
        data = lineData;
    }

    if constexpr( D == 3 )
    {
        indices = triangleIndices;
        data = triangleData;
    }

    auto begin = indices[index];
    auto end = indices[index + 1];
    auto n = static_cast<size_t>( end - begin );

    return std::pair { n, data.subspan( D * begin, D * n ) };
}

template<size_t D>
size_t edgeVertex( size_t edgeId, size_t ivertex )
{
    static_assert( D > 0 && D <= 3, "Not implemented." );

    if constexpr( D == 1 )
    {
        return ivertex;
    }

    if constexpr( D == 2 )
    {
        auto numbering = std::array<std::array<size_t, 2>, 4> 
        { 
            std::array<size_t, 2> { 0, 2 }, // bottom
            std::array<size_t, 2> { 1, 3 }, // top
            std::array<size_t, 2> { 0, 1 }, // left
            std::array<size_t, 2> { 2, 3 }  // right
        };

        return numbering[edgeId][ivertex];
    }

    if constexpr( D == 3 )
    {
        return marching::numbering[edgeId][ivertex];
    }
}

} // namespace

template<size_t D, marching::InstantiatedIndex IndexType> 
void cellLocalBoundaryRecovery( const AbsMapping<D>& mapping,
                                const ImplicitFunction<D>& function,
                                const std::vector<bool>& evaluations,
                                const CoordinateGrid<D>& rstGrid,
                                std::array<size_t, D> resolution,
                                CoordinateList<D>& rstList,
                                std::vector<IndexType>& cells,
                                size_t niterations,
                                std::any& anyCache )
{
    if( !anyCache.has_value( ) )
    {
        anyCache = SmallMarchingCubes<D, IndexType> { };
    }

    // Prepare vertex map that reduces Cartesian indices to the existing ones
    auto& vertexMap = std::any_cast<SmallMarchingCubes<D, IndexType>&>( anyCache );

    vertexMap.reset( resolution, &rstList );

    auto strides = vertexMap.cornerStrides;

    // Traverse cells
    nd::execute( resolution, [&]( std::array<size_t, D> ijkCell )
    {
        auto vertexIjk = [=]( size_t index ) { return array::add( ijkCell, nd::binaryUnravel<size_t, D>( index ) ); };
        auto index = std::uint8_t { 0 };
        
        for( size_t ivertex = 0; ivertex < utilities::binaryPow<size_t>( D ); ++ivertex )
        {
            auto linearIndex = nd::linearIndex( vertexIjk( ivertex ), strides );

            index |= evaluations[linearIndex] * utilities::binaryPow<std::uint8_t>( ivertex );
        }

        auto createEdge = [&]( std::array<size_t, D> ijk0, 
                               std::array<size_t, D> ijk1 ) 
        {
            auto inside0 = evaluations[nd::linearIndex( ijk0, strides )];
            auto inside1 = evaluations[nd::linearIndex( ijk1, strides )];

            return marching::interpolate<D>( function, mapping, 
                array::extract( rstGrid, ijk0 ), inside0, 
                array::extract( rstGrid, ijk1 ), inside1, niterations );
        };

        auto [n, edgeSpan] = boundaryCellSpan<D>( index );

        for( size_t icell = 0; icell < n; ++icell )
        {
            for( size_t ivertex = 0; ivertex < D; ++ivertex )
            {
                auto id = edgeSpan[D * icell + ivertex];

                cells.push_back( vertexMap.edgeIndex(
                    vertexIjk( edgeVertex<D>( id, 0 ) ),
                    vertexIjk( edgeVertex<D>( id, 1 ) ), createEdge ) );
            }

            // Normal vector would point inwards otherwise
            std::reverse( cells.end( ) - D, cells.end( ) );
        }
    } );
}

template<size_t D>
CellAssociatedSimplices<D> recoverDomainBoundary( const AbsMesh<D>& mesh,
                                                  const ImplicitFunction<D>& function,
                                                  std::array<size_t, D> resolution,
                                                  size_t niterations )
{
    auto simplexMesh = SimplexMesh<D, D - 1> { };
    auto celldata = SimplexCellAssociation<D> { };
    auto vertexOffsets = std::vector<size_t>( mesh.ncells( ) + 1, 0 );
    auto ncells = static_cast<std::int64_t>( mesh.ncells( ) );

    [[maybe_unused]]
    auto chunksize = parallel::clampChunksize( mesh.ncells( ), 73 );

    celldata.offsets.resize( mesh.ncells( ) + 1, 0 );

    #pragma omp parallel
    {
        auto rstGrid = CoordinateGrid<D> { };
        auto evaluations = std::vector<bool> { };
        auto mapping = mesh.createMapping( );
        auto cache = std::any { };

        auto localMeshCells = std::vector<CellIndex> { };
        auto localRst = CoordinateList<D> { };
        auto localXyz = CoordinateList<D> { };
        auto localSimplices = std::vector<size_t> { };
        auto localNormals = CoordinateList<D> { }; // 1D only

        #pragma omp for schedule( dynamic, chunksize )
        for( std::int64_t ii = 0; ii < ncells; ++ii )
        {
            utilities::resize0( rstGrid, evaluations );

            auto icell = static_cast<CellIndex>( ii );

            mesh.prepareMapping( icell, mapping );
            
            marching::evaluateGrid( mapping, function, 
                resolution, rstGrid, evaluations );
   
            auto nvertices0 = localRst.size( );
            auto ncells0 = localSimplices.size( ) / D;

            cellLocalBoundaryRecovery<D>( mapping, function, evaluations, 
                rstGrid, resolution, localRst, localSimplices, niterations, cache );

            celldata.offsets[icell + 1] = localSimplices.size( ) / D - ncells0;
            vertexOffsets[icell + 1] = localRst.size( ) - nvertices0;

            if( celldata.offsets[icell + 1] )
            {
                localMeshCells.push_back( icell );
                localXyz.resize( localRst.size( ) );

                for( auto ivertex = nvertices0; ivertex < localRst.size( ); ++ivertex )
                {
                    localXyz[ivertex] = mapping( localRst[ivertex] );
                }

                for( auto ivertex = D * ncells0; ivertex < localSimplices.size( ); ++ivertex )
                {
                    localSimplices[ivertex] -= nvertices0;
                }
            }

            // Add normal direction in 1D since we cannot determine it from the vertex ordering
            if constexpr ( D == 1 )
            {
                for( size_t isegment = 0; isegment + 1 < evaluations.size( ); ++isegment )
                {
                    if( evaluations[isegment] != evaluations[isegment + 1] )
                    {
                        localNormals.push_back( std::array { 2.0 * evaluations[isegment] - 1.0 } );
                    }
                }

                MLHP_CHECK( localNormals.size( ) * D == localSimplices.size( ), 
                    "Internal error: inconsistent number of normals." );
            }
        }

        #pragma omp barrier 
        { }

        #pragma omp single
        {
            std::partial_sum( celldata.offsets.begin( ), celldata.offsets.end( ), celldata.offsets.begin( ) );
            std::partial_sum( vertexOffsets.begin( ), vertexOffsets.end( ), vertexOffsets.begin( ) );

            celldata.rst.resize( vertexOffsets.back( ) );
            simplexMesh.vertices.resize( vertexOffsets.back( ) );
            simplexMesh.cells.resize( celldata.offsets.back( ) );

            if constexpr( D == 1 )
            {
                simplexMesh.normals.resize( celldata.offsets.back( ) );
            }
        }

        auto vertexOffset = size_t { 0 };
        auto cellOffset = size_t { 0 };

        for( size_t ilocal = 0; ilocal < localMeshCells.size( ); ++ilocal )
        {
            auto icell = localMeshCells[ilocal];
            auto nvertices = vertexOffsets[icell + 1] - vertexOffsets[icell];
            auto nsimplices = celldata.offsets[icell + 1] - celldata.offsets[icell];

            std::copy( utilities::begin( localRst, vertexOffset ),
                       utilities::begin( localRst, vertexOffset + nvertices ),
                       utilities::begin( celldata.rst, vertexOffsets[icell] ) );

            std::copy( utilities::begin( localXyz, vertexOffset ),
                       utilities::begin( localXyz, vertexOffset + nvertices ),
                       utilities::begin( simplexMesh.vertices, vertexOffsets[icell] ) );

            auto cells = std::span( utilities::begin( simplexMesh.cells, celldata.offsets[icell] ), nsimplices );

            for( size_t isimplex = 0; isimplex < nsimplices; ++isimplex )
            {
                for( size_t ivertex = 0; ivertex < D; ++ivertex )
                {
                    auto index = D * ( cellOffset + isimplex ) + ivertex;

                    cells[isimplex][ivertex] = localSimplices[index] + vertexOffsets[icell];
                }

                if constexpr( D == 1 )
                {
                    simplexMesh.normals[celldata.offsets[icell] + isimplex] = localNormals[cellOffset + isimplex];
                }
            }

            vertexOffset += nvertices;
            cellOffset += nsimplices;
        }
    } // omp parallel

    return std::pair { std::move( simplexMesh ), std::move( celldata ) };
}


namespace
{

template<size_t D>
auto volumeCellSpan( size_t index )
{
    static_assert( D > 0 && D <= 3, "Not implemented." );

    if constexpr( D == 1 )
    {
        if( index == 0 )
        {
            return std::span<const std::uint8_t> { };
        }

        static constexpr auto data = std::array<std::uint8_t, 6> { 0, 2, 2, 1, 0, 1 };
        
        return std::span { utilities::begin( data, 2 * ( index - 1 ) ), 2 };
    }

    if constexpr( D == 2 )
    {
        return std::span { triangles2D[index] };
    }

    if constexpr( D == 3 )
    {
        return std::span { tetrahedra[index] };
    }
}

template<size_t D>
auto extraCellSpan( size_t index )
{
    static_assert( D > 0 && D <= 3, "Not implemented." );

    if constexpr( D == 3 )
    {
        return std::span { extraTetrahedra[index] };
    }
    else
    {
        return std::span<std::uint8_t, 0> { };
    }
}

template<size_t D>
auto vtkCornerOrdering( )
{
    static_assert( D >= 1 && D <= 3 );

    if constexpr ( D == 1 )
    {
        return std::array<size_t, 2> { 0, 1 };
    }

    if constexpr ( D == 2 )
    {
        return std::array<size_t, 4> { 0, 2, 3, 1 };
    }

    if constexpr ( D == 3 )
    {
        return std::array<size_t, 8> { 0, 4, 6, 2, 1, 5, 7, 3 };
    }
}

}

template<size_t D, marching::InstantiatedIndex IndexType>
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
                              std::any& anyCache )
{
    static constexpr auto ncorners = utilities::binaryPow<size_t>( D );
    static constexpr auto lastIndex = utilities::binaryPow<size_t>( ncorners ) - 1;

    if( !anyCache.has_value( ) )
    {
        anyCache = SmallMarchingCubes<D, IndexType> { };
    }

    // Prepare vertex map that reduces Cartesian indices to the existing ones
    auto& vertexMap = std::any_cast<SmallMarchingCubes<D, IndexType>&>( anyCache );

    vertexMap.reset( resolution, &rstList );

    auto strides = vertexMap.cornerStrides;
        
    // Get cell ijk + local vertex index and return local vertex ijk
    auto vertexIjk = [=]( auto ijkCell, size_t index ) 
    { 
        return array::add( ijkCell, nd::binaryUnravel<size_t, D>( index ) ); 
    };

    // Callback function for creating a vertex with given global vertex ijk
    auto createCorner = [&]( std::array<size_t, D> ijk )
    { 
        return array::extract( rstGrid, ijk ); 
    };

    // Callback function for creating an edge between two vertices with given global vertex ijk
    auto createEdge = [&]( std::array<size_t, D> ijk0, std::array<size_t, D> ijk1 ) 
    {
        return marching::interpolate( function, mapping,
            array::extract( rstGrid, ijk0 ), evaluations[nd::linearIndex( ijk0, strides )],
            array::extract( rstGrid, ijk1 ), evaluations[nd::linearIndex( ijk1, strides )], 
            niterations ); 
    };

    auto createCell = [&]( auto ijkCell, std::span<const std::uint8_t, D + 1> vertices )
    {
        for( auto id : vertices )
        {
            if( id >= ncorners )
            {
                auto localVertexIndex1 = vertexIjk( ijkCell, edgeVertex<D>( id - ncorners, 0 ) );
                auto localVertexIndex2 = vertexIjk( ijkCell, edgeVertex<D>( id - ncorners, 1 ) );

                connectivity.push_back( vertexMap.edgeIndex( localVertexIndex1, localVertexIndex2, createEdge ) );
            }
            else
            {
                connectivity.push_back( vertexMap.vertexIndex( vertexIjk( ijkCell, id ), createCorner ) );
            }
        }
                
        offsets.push_back( static_cast<IndexType>( connectivity.size( ) ) );
    };

    // Create all tests in cell with given cell ijk. The bits of cutConfig store the inside-outside state of the corners.
    auto createCells = [&]( auto ijkCell, std::span<const std::uint8_t> cellCorners )
    {
        for( size_t isimplex = 0; isimplex < cellCorners.size( ) / ( D + 1 ); ++isimplex )
        {
            createCell( ijkCell, cellCorners.subspan( ( D + 1 ) * isimplex ).first<D + 1>( ) );
        }
    };

    // Loop over cell grid
    nd::execute( resolution, [&]( std::array<size_t, D> ijkCell )
    {
        auto index = std::uint8_t { 0 };
    
        for( size_t ivertex = 0; ivertex < ncorners; ++ivertex )
        {
            auto linearIndex = nd::linearIndex( vertexIjk( ijkCell, ivertex ), strides );

            index |= evaluations[linearIndex] * utilities::binaryPow<std::uint8_t>( ivertex );
        }

        // Full cell (or empty when we mesh both sides)
        if( index == lastIndex || ( meshBothSides && index == 0 ) )
        {
            // Reorder to be consistent with vtk numbering
            for( size_t ivertex : vtkCornerOrdering<D>( ) )
            {
                connectivity.push_back( vertexMap.vertexIndex( 
                    vertexIjk( ijkCell, ivertex ), createCorner ) );
            }
        
            offsets.push_back( static_cast<IndexType>( connectivity.size( ) ) );
        }
        else
        {
            createCells( ijkCell, volumeCellSpan<D>( index ) );

            if( meshBothSides )
            {
                createCells( ijkCell, extraCellSpan<D>( index ) );
                createCells( ijkCell, extraCellSpan<D>( lastIndex - index ) );
                createCells( ijkCell, volumeCellSpan<D>( lastIndex - index ) );
            }
        }
    } );
}

#define MLHP_INSTANTIATE_MARCHING_CUBES( D, INDEX_TYPE )                  \
                                                                          \
    template MLHP_EXPORT                                                  \
    void cellLocalBoundaryRecovery( const AbsMapping<D>& mapping,         \
                                    const ImplicitFunction<D>& function,  \
                                    const std::vector<bool>& evaluations, \
                                    const CoordinateGrid<D>& rstGrid,     \
                                    std::array<size_t, D> resolution,     \
                                    CoordinateList<D>& rstList,           \
                                    std::vector<INDEX_TYPE>& cells,       \
                                    size_t niterations,                   \
                                    std::any& anyCache );                 \
                                                                          \
    template MLHP_EXPORT                                                  \
    void cellLocalVolumeRecovery( const AbsMapping<D>& mapping,           \
                                  const ImplicitFunction<D>& function,    \
                                  const std::vector<bool>& evaluations,   \
                                  const CoordinateGrid<D>& rstGrid,       \
                                  std::array<size_t, D> resolution,       \
                                  CoordinateList<D>& rstList,             \
                                  std::vector<INDEX_TYPE>& connectivity,  \
                                  std::vector<INDEX_TYPE>& offsets,       \
                                  bool meshBothSides,                     \
                                  size_t niterations,                     \
                                  std::any& anyCache );

#define MLHP_INSTANTIATE_SIMPLEXMESH( G, L )                                                   \
                                                                                               \
    template struct SimplexMesh<G, L>;                                                         \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    SimplexMesh<G, L> filterSimplexMesh( const SimplexMesh<G, L>& triangulation,               \
                                         const ImplicitFunction<G>& function,                  \
                                         size_t nseedpoints );                                 \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    CellAssociatedSimplices<G, L> filterSimplexMesh( const SimplexMesh<G, L>& simplexMesh,     \
                                                     const SimplexCellAssociation<G>& celldata,\
                                                     const ImplicitFunction<G>& function,      \
                                                     size_t nseedpoints );                     \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    SimplexMesh<G, L> mergeSimplexMeshes( ReferenceVector<const SimplexMesh<G, L>> );          \
                                                                                               \
    namespace kdtree                                                                           \
    {                                                                                          \
        template MLHP_EXPORT                                                                   \
        kdtree::ObjectProvider<G> makeObjectProvider( memory::vptr<const SimplexMesh<G, L>>,   \
                                                      bool clip );                             \
    }

// Points
MLHP_INSTANTIATE_SIMPLEXMESH( 1, 0 )

// Line segments
MLHP_INSTANTIATE_SIMPLEXMESH( 1, 1 )
MLHP_INSTANTIATE_SIMPLEXMESH( 2, 1 )
MLHP_INSTANTIATE_SIMPLEXMESH( 3, 1 )

// Triangles
MLHP_INSTANTIATE_SIMPLEXMESH( 2, 2 )
MLHP_INSTANTIATE_SIMPLEXMESH( 3, 2 )

#define MLHP_INSTANTIATE_THREE( D )                                                            \
                                                                                               \
    MLHP_INSTANTIATE_MARCHING_CUBES( D, size_t )                                               \
    MLHP_INSTANTIATE_MARCHING_CUBES( D, std::int64_t )                                         \
                                                                                               \
    template class SimplexQuadrature<D>;                                                       \
    template struct SimplexCellAssociation<D>;                                                 \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    ImplicitFunction<D> rayIntersectionDomain( memory::vptr<const SimplexMesh<D, D - 1>>,      \
                                               memory::vptr<KdTree<D>> kdTree,                 \
                                               const CoordinateList<D>& rays );                \
    template MLHP_EXPORT                                                                       \
    CellAssociatedSimplices<D> recoverDomainBoundary( const AbsMesh<D>& mesh,                  \
                                                      const ImplicitFunction<D>& function,     \
                                                      std::array<size_t, D> resolution,        \
                                                      size_t niterations );                    \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    std::array<double, D> integrateNormalComponents( const SimplexMesh<D, D - 1>&, bool abs ); \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    CellAssociatedSimplices<D> intersectWithMesh( const SimplexMesh<D, D - 1>& simplices,      \
                                                  const AbsMesh<D>& mesh,                      \
                                                  const KdTree<D>& tree );                     \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    SimplexMesh<D, D - 1> createSkeletonMesh( const AbsMesh<D>& mesh );

MLHP_INSTANTIATE_THREE( 1 )
MLHP_INSTANTIATE_THREE( 2 )
MLHP_INSTANTIATE_THREE( 3 )

#define MLHP_INSTANTIATE_DIM( D )                                                              \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    Triangulation<D> createTriangulation( CoordinateConstSpan<D> vertices );                   \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    std::shared_ptr<Triangulation<D>> createSharedTriangulation( CoordinateConstSpan<D> );     \
                                                                                               \
    namespace marching                                                                         \
    {                                                                                          \
        template MLHP_EXPORT                                                                   \
        std::array<double, D> interpolate( const ImplicitFunction<D>& function,                \
                                           std::array<double, D> c1, bool v1,                  \
                                           std::array<double, D> c2, bool v2,                  \
                                           size_t niterations );                               \
                                                                                               \
        template MLHP_EXPORT                                                                   \
        std::array<double, D> interpolate( const ImplicitFunction<D>& function,                \
                                           const AbsMapping<D>& mapping,                       \
                                           std::array<double, D> c1, bool v1,                  \
                                           std::array<double, D> c2, bool v2,                  \
                                           size_t niterations );                               \
                                                                                               \
        template MLHP_EXPORT                                                                   \
        void evaluateGrid( const AbsMapping<D>& mapping,                                       \
                           const ImplicitFunction<D>& function,                                \
                           std::array<size_t, D> resolution,                                   \
                           std::array<std::vector<double>, D>& rstGrid,                        \
                           std::vector<bool>& evaluations );                                   \
    }

MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

//      8: { 0, 4 },
//      9: { 4, 6 },
//     10: { 6, 2 },
//     11: { 2, 0 },
//     12: { 1, 5 },
//     13: { 5, 7 },
//     14: { 7, 3 },
//     15: { 3, 1 },
//     16: { 0, 1 },
//     17: { 4, 5 },
//     18: { 6, 7 },
//     19: { 2, 3 }   


// void printBinary( auto number, size_t length, std::string before )
// {
//     std::cout << before << " = ";
//     for( size_t i = 0; i < length; ++i )
//     {
//         std::cout << (( number & utilities::binaryPow<decltype(number)>( i ) ) > 0);
//     }
//     std::cout << std::endl;
// }

// http://www.paulbourke.net/geometry/polygonise/
// https://gist.github.com/dwilliamson/c041e3454a713e58baf6e4f8e5fffecd

namespace marching
{

/*
 * 
 *                 [3]--------(14)-----------[7]
 *              _-' |                     _-' |
 *          (15)    |                  _-'    |
 *        _-'      (19)             (13)     (18)
 *     _-'          |            _-'          |
 *  [1]------(12)-------------[5]             |
 *   |              |          |              |
 *   |              |          |              |
 *  (16)            |         (17)            |
 *   |              |          |              |
 *   |             [2]---------|----(10)-----[6]
 *   |          _-'            |          _-' 
 *   |       (11)              |       _-'
 *   |    _-'                  |    (9)
 *   | _-'                     | _-'
 *  [0]----------(8)----------[4]
 *                
 */

std::array<std::array<size_t, 2>, 12> numbering = 
{
    std::array<size_t, 2>{ 0, 4 }, //  0 ( 8)
    std::array<size_t, 2>{ 4, 6 }, //  1 ( 9)
    std::array<size_t, 2>{ 6, 2 }, //  2 (10)
    std::array<size_t, 2>{ 2, 0 }, //  3 (11)
    std::array<size_t, 2>{ 1, 5 }, //  4 (12)
    std::array<size_t, 2>{ 5, 7 }, //  5 (13)
    std::array<size_t, 2>{ 7, 3 }, //  6 (14)
    std::array<size_t, 2>{ 3, 1 }, //  7 (15)
    std::array<size_t, 2>{ 0, 1 }, //  8 (16)
    std::array<size_t, 2>{ 4, 5 }, //  9 (17)
    std::array<size_t, 2>{ 6, 7 }, // 10 (18)
    std::array<size_t, 2>{ 2, 3 }  // 11 (19)
};

namespace
{

template<size_t D>
auto interpolateImpl( auto&& function,
                      std::array<double, D> c1, bool v1, 
                      std::array<double, D> c2, bool v2,
                      size_t niterations )
{
    if( !v1 )
    {
        std::swap( c1, c2 );
        std::swap( v1, v2 );
    }

    std::array<double, D> m;

    for( size_t it = 0; it < niterations; ++it )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            m[axis] = 0.5 * ( c1[axis] + c2[axis] );
        }

        if( function( m ) == v1 )
        {
            c1 = m;
        }
        else
        {
            c2 = m;
        }
    }

    // Return point inside (may not be the closest)
    return c1;
}

} // namespace detail

template<size_t D>
std::array<double, D> interpolate( const ImplicitFunction<D>& function,
                                   const AbsMapping<D>& mapping,
                                   std::array<double, D> c1, bool v1,
                                   std::array<double, D> c2, bool v2,
                                   size_t niterations )
{
    auto mappedFunction = [&]( std::array<double, D> rst )
    {
        return function( mapping.map( rst ) );
    };

    return interpolateImpl<D>( mappedFunction, c1, v1, c2, v2, niterations );
}

template<size_t D>
std::array<double, D> interpolate( const ImplicitFunction<D>& function,
                                   std::array<double, D> c1, bool v1,
                                   std::array<double, D> c2, bool v2,
                                   size_t niterations )
{
    return interpolateImpl<D>( function, c1, v1, c2, v2, niterations );
}

std::vector<std::uint8_t> lineData =
{
                // Case  0 (0000): offsets  0 -  0 
    2, 0,       // Case  1 (0001): offsets  0 -  1 
    1, 2,       // Case  2 (0010): offsets  1 -  1 
    1, 0,       // Case  3 (0011): offsets  2 -  3 
    0, 3,       // Case  4 (0100): offsets  3 -  4 
    2, 3,       // Case  5 (0101): offsets  4 -  5 
    0, 2, 1, 3, // Case  6 (0110): offsets  5 -  7 
    1, 3,       // Case  7 (0111): offsets  7 -  8 
    3, 1,       // Case  8 (1000): offsets  8 -  9 
    2, 0, 3, 1, // Case  9 (1001): offsets  9 - 11 
    3, 2,       // Case 10 (1010): offsets 11 - 12 
    3, 0,       // Case 11 (1011): offsets 12 - 13 
    0, 1,       // Case 12 (1100): offsets 13 - 15 
    2, 1,       // Case 13 (1101): offsets 14 - 15 
    0, 2,       // Case 14 (1110): offsets 15 - 16 
                // Case 15 (1111): offsets 16 - 16 
};

std::vector<std::uint16_t> lineIndices =
{
    0, 0, 1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 16
};

std::vector<std::vector<std::uint8_t>> triangles2D =
{
    /*   0: 0000 */ { },
    /*   1: 0001 */ { 0, 4, 6 },
    /*   2: 0010 */ { 1, 6, 5 },
    /*   3: 0011 */ { 0, 4, 5, 0, 5, 1 },
    /*   4: 0100 */ { 2, 7, 4 },
    /*   5: 0101 */ { 0, 2, 6, 6, 2, 7 },
    /*   6: 0110 */ { 1, 6, 5, 2, 7, 4, 4, 5, 6, 4, 7, 5 },
    /*   7: 0111 */ { 0, 5, 1, 0, 7, 5, 0, 2, 7 },
    /*   8: 1000 */ { 7, 3, 5 },
    /*   9: 1001 */ { 0, 4, 6, 7, 3, 5 },
    /*  10: 1010 */ { 1, 6, 7, 1, 7, 3 },
    /*  11: 1011 */ { 1, 0, 4, 1, 4, 7, 1, 7, 3 },
    /*  12: 1100 */ { 2, 3, 4, 4, 3, 5 },
    /*  13: 1101 */ { 0, 2, 6, 6, 2, 5, 5, 2, 3 },
    /*  14: 1110 */ { 3, 1, 6, 3, 6, 4, 3, 4, 2 },
    /*  15: 1111 */ { 0, 2, 1, 2, 3, 1 },
};

std::array<std::uint8_t, 2460> triangleData =
{ 
                                                      //   0: 00000000
    0, 8, 3,                                          //   1: 00000001 
    4, 7, 8,                                          //   2: 00000010
    4, 3, 0, 7, 3, 4,                                 //   3: 00000011
    3, 11, 2,                                         //   4: 00000100 
    0, 11, 2, 8, 11, 0,                               //   5: 00000101 
    8, 4, 7, 3, 11, 2,                                //   6: 00000110 
    11, 4, 7, 11, 2, 4, 2, 0, 4,                      //   7: 00000111 
    7, 6, 11,                                         //   8: 00001000 
    3, 0, 8, 11, 7, 6,                                //   9: 00001001 
    6, 8, 4, 11, 8, 6,                                //  10: 00001010 
    3, 6, 11, 3, 0, 6, 0, 4, 6,                       //  11: 00001011 
    7, 2, 3, 6, 2, 7,                                 //  12: 00001100 
    7, 0, 8, 7, 6, 0, 6, 2, 0,                        //  13: 00001101 
    8, 2, 3, 8, 4, 2, 4, 6, 2,                        //  14: 00001110 
    0, 4, 2, 4, 6, 2,                                 //  15: 00001111 
    0, 1, 9,                                          //  16: 00010000 
    1, 8, 3, 9, 8, 1,                                 //  17: 00010001  
    0, 1, 9, 8, 4, 7,                                 //  18: 00010010 
    4, 1, 9, 4, 7, 1, 7, 3, 1,                        //  19: 00010011 
    1, 9, 0, 2, 3, 11,                                //  20: 00010100  
    1, 11, 2, 1, 9, 11, 9, 8, 11,                     //  21: 00010101  
    9, 0, 1, 8, 4, 7, 2, 3, 11,                       //  22: 00010110  
    4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1,            //  23: 00010111  
    0, 1, 9, 11, 7, 6,                                //  24: 00011000  
    8, 1, 9, 8, 3, 1, 11, 7, 6,                       //  25: 00011001  
    8, 6, 11, 8, 4, 6, 9, 0, 1,                       //  26: 00011010  
    9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6,              //  27: 00011011  
    2, 7, 6, 2, 3, 7, 0, 1, 9,                        //  28: 00011100  
    1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6,               //  29: 00011101  
    1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8,               //  30: 00011110  
    1, 9, 4, 1, 4, 2, 2, 4, 6,                        //  31: 00011111
    9, 5, 4,                                          //  32: 00100000  
    9, 5, 4, 0, 8, 3,                                 //  33: 00100001 
    9, 7, 8, 5, 7, 9,                                 //  34: 00100010 
    9, 3, 0, 9, 5, 3, 5, 7, 3,                        //  35: 00100011 
    9, 5, 4, 2, 3, 11,                                //  36: 00100100 
    0, 11, 2, 0, 8, 11, 4, 9, 5,                      //  37: 00100101 
    7, 9, 5, 7, 8, 9, 3, 11, 2,                       //  38: 00100110 
    9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11,              //  39: 00100111 
    4, 9, 5, 7, 6, 11,                                //  40: 00101000 
    0, 8, 3, 4, 9, 5, 11, 7, 6,                       //  41: 00101001 
    6, 9, 5, 6, 11, 9, 11, 8, 9,                      //  42: 00101010 
    3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5,              //  43: 00101011 
    7, 2, 3, 7, 6, 2, 5, 4, 9,                        //  44: 00101100 
    9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7,               //  45: 00101101 
    5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2,               //  46: 00101110 
    9, 5, 6, 9, 6, 0, 0, 6, 2,                        //  47: 00101111 
    0, 5, 4, 1, 5, 0,                                 //  48: 00110000 
    8, 5, 4, 8, 3, 5, 3, 1, 5,                        //  49: 00110001 
    0, 7, 8, 0, 1, 7, 1, 5, 7,                        //  50: 00110010 
    1, 5, 3, 3, 5, 7,                                 //  51: 00110011 
    0, 5, 4, 0, 1, 5, 2, 3, 11,                       //  52: 00110100 
    2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5,              //  53: 00110101 
    2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7,              //  54: 00110110 
    11, 2, 1, 11, 1, 7, 7, 1, 5,                      //  55: 00110111 
    5, 0, 1, 5, 4, 0, 7, 6, 11,                       //  56: 00111000 
    11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5,              //  57: 00111001 
    0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11,            //  58: 00111010 
    6, 11, 3, 6, 3, 5, 5, 3, 1,                       //  59: 00111011 
    3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0,               //  60: 00111100 
    6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8,      //  61: 00111101 
    1, 5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8,      //  62: 00111110 
    1, 5, 6, 2, 1, 6,                                 //  63: 00111111 
    1, 2, 10,                                         //  64: 01000000 
    0, 8, 3, 1, 2, 10,                                //  65: 01000001 
    1, 2, 10, 8, 4, 7,                                //  66: 01000010 
    3, 4, 7, 3, 0, 4, 1, 2, 10,                       //  67: 01000011 
    3, 10, 1, 11, 10, 3,                              //  68: 01000100 
    0, 10, 1, 0, 8, 10, 8, 11, 10,                    //  69: 01000101 
    3, 10, 1, 3, 11, 10, 7, 8, 4,                     //  70: 01000110 
    1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4,           //  71: 01000111 
    10, 1, 2, 6, 11, 7,                               //  72: 01001000 
    1, 2, 10, 3, 0, 8, 6, 11, 7,                      //  73: 01001001 
    6, 8, 4, 6, 11, 8, 2, 10, 1,                      //  74: 01001010 
    1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6,            //  75: 01001011 
    10, 7, 6, 10, 1, 7, 1, 3, 7,                      //  76: 01001100 
    10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8,             //  77: 01001101 
    8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1,              //  78: 01001110 
    10, 1, 0, 10, 0, 6, 6, 0, 4,                      //  79: 01001111 
    9, 2, 10, 0, 2, 9,                                //  80: 01010000 
    2, 8, 3, 2, 10, 8, 10, 9, 8,                      //  81: 01010001 
    9, 2, 10, 9, 0, 2, 8, 4, 7,                       //  82: 01010010 
    2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4,              //  83: 01010011 
    3, 9, 0, 3, 11, 9, 11, 10, 9,                     //  84: 01010100 
    9, 8, 10, 10, 8, 11,                              //  85: 01010101 
    4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3,           //  86: 01010110 
    4, 7, 11, 4, 11, 9, 9, 11, 10,                    //  87: 01010111 
    2, 9, 0, 2, 10, 9, 6, 11, 7,                      //  88: 01011000 
    6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8,           //  89: 01011001 
    4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9,            //  90: 01011010 
    10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3,   //  91: 01011011 
    0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7,            //  92: 01011100 
    7, 6, 10, 7, 10, 8, 8, 10, 9,                     //  93: 01011101 
    4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3,    //  94: 01011110 
    10, 9, 4, 6, 10, 4,                               //  95: 01011111 
    1, 2, 10, 9, 5, 4,                                //  96: 01100000 
    3, 0, 8, 1, 2, 10, 4, 9, 5,                       //  97: 01100001 
    9, 7, 8, 9, 5, 7, 10, 1, 2,                       //  98: 01100010 
    10, 1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3,              //  99: 01100011 
    10, 3, 11, 10, 1, 3, 9, 5, 4,                     // 100: 01100100
    4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10,            // 101: 01100101
    9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11,            // 102: 01100110
    5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0,  // 103: 01100111
    9, 5, 4, 10, 1, 2, 7, 6, 11,                      // 104: 01101000
    6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5,             // 105: 01101001
    1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6,           // 106: 01101010
    0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10,   // 107: 01101011
    9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7,              // 108: 01101100
    1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4,     // 109: 01101101
    1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6,     // 110: 01101110
    10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0,             // 111: 01101111
    5, 2, 10, 5, 4, 2, 4, 0, 2,                       // 112: 01110000
    2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8,              // 113: 01110001
    8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2,              // 114: 01110010
    2, 10, 5, 2, 5, 3, 3, 5, 7,                       // 115: 01110011
    5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3,           // 116: 01110100
    5, 4, 8, 5, 8, 10, 10, 8, 11,                     // 117: 01110101
    11, 10, 0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0,  // 118: 01110110
    11, 10, 5, 7, 11, 5,                              // 119: 01110111
    7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2,            // 120: 01111000
    3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6,    // 121: 01111001
    11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5,   // 122: 01111010
    6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3,            // 123: 01111011
    4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10, // 124: 01111100
    7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10,           // 125: 01111101
    0, 3, 8, 5, 6, 10,                                // 126: 01111110
    10, 5, 6,                                         // 127: 01111111
    10, 6, 5,                                         // 128: 10000000
    0, 8, 3, 5, 10, 6,                                // 129: 10000001
    5, 10, 6, 4, 7, 8,                                // 130: 10000010
    4, 3, 0, 4, 7, 3, 6, 5, 10,                       // 131: 10000011
    2, 3, 11, 10, 6, 5,                               // 132: 10000100
    11, 0, 8, 11, 2, 0, 10, 6, 5,                     // 133: 10000101
    3, 11, 2, 7, 8, 4, 10, 6, 5,                      // 134: 10000110
    5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11,             // 135: 10000111
    11, 5, 10, 7, 5, 11,                              // 136: 10001000
    11, 5, 10, 11, 7, 5, 8, 3, 0,                     // 137: 10001001
    5, 8, 4, 5, 10, 8, 10, 11, 8,                     // 138: 10001010
    5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0,           // 139: 10001011
    2, 5, 10, 2, 3, 5, 3, 7, 5,                       // 140: 10001100
    8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5,              // 141: 10001101
    2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4,              // 142: 10001110
    5, 10, 2, 5, 2, 4, 4, 2, 0,                       // 143: 10001111
    9, 0, 1, 5, 10, 6,                                // 144: 10010000
    1, 8, 3, 1, 9, 8, 5, 10, 6,                       // 145: 10010001
    1, 9, 0, 5, 10, 6, 8, 4, 7,                       // 146: 10010010
    10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4,              // 147: 10010011
    0, 1, 9, 2, 3, 11, 5, 10, 6,                      // 148: 10010100
    5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11,            // 149: 10010101
    0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6,             // 150: 10010110
    9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6,  // 151: 10010111
    5, 11, 7, 5, 10, 11, 1, 9, 0,                     // 152: 10011000
    10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1,            // 153: 10011001
    0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5,           // 154: 10011010
    10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4,  // 155: 10011011
    9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2,             // 156: 10011100
    9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2,     // 157: 10011101
    3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9,    // 158: 10011110
    5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2,              // 159: 10011111
    10, 4, 9, 6, 4, 10,                               // 160: 10100000
    4, 10, 6, 4, 9, 10, 0, 8, 3,                      // 161: 10100001
    7, 10, 6, 7, 8, 10, 8, 9, 10,                     // 162: 10100010
    0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10,            // 163: 10100011
    10, 4, 9, 10, 6, 4, 11, 2, 3,                     // 164: 10100100
    0, 8, 2, 2, 8, 11, 4, 9, 10, 4, 10, 6,            // 165: 10100101
    2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7,            // 166: 10100110
    2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7,   // 167: 10100111
    4, 11, 7, 4, 9, 11, 9, 10, 11,                    // 168: 10101000
    0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11,            // 169: 10101001
    9, 10, 8, 10, 11, 8,                              // 170: 10101010
    3, 0, 9, 3, 9, 11, 11, 9, 10,                     // 171: 10101011
    2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9,              // 172: 10101100
    9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7,    // 173: 10101101
    2, 3, 8, 2, 8, 10, 10, 8, 9,                      // 174: 10101110
    9, 10, 2, 0, 9, 2,                                // 175: 10101111
    10, 0, 1, 10, 6, 0, 6, 4, 0,                      // 176: 10110000
    8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10,              // 177: 10110001
    10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0,             // 178: 10110010
    10, 6, 7, 10, 7, 1, 1, 7, 3,                      // 179: 10110011
    3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10,             // 180: 10110100
    6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1,   // 181: 10110101
    1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11,   // 182: 10110110
    11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1,            // 183: 10110111
    1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11,           // 184: 10111000
    3, 1, 4, 3, 4, 8, 1, 10, 4, 7, 4, 11, 10, 11, 4,  // 185: 10111001
    0, 1, 10, 0, 10, 8, 8, 10, 11,                    // 186: 10111010
    3, 1, 10, 11, 3, 10,                              // 187: 10111011
    3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10, // 188: 10111100
    1, 10, 2, 8, 7, 4,                                // 189: 10111101
    2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8,             // 190: 10111110
    1, 10, 2,                                         // 191: 10111111
    1, 6, 5, 2, 6, 1,                                 // 192: 11000000
    1, 6, 5, 1, 2, 6, 3, 0, 8,                        // 193: 11000001
    6, 1, 2, 6, 5, 1, 4, 7, 8,                        // 194: 11000010
    1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4, 7,               // 195: 11000011
    6, 3, 11, 6, 5, 3, 5, 1, 3,                       // 196: 11000100
    0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6,            // 197: 11000101
    8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6,             // 198: 11000110
    5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11, // 199: 11000111
    11, 1, 2, 11, 7, 1, 7, 5, 1,                      // 200: 11001000
    0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11,              // 201: 11001001
    2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8,              // 202: 11001010
    0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11, // 203: 11001011
    1, 3, 5, 3, 7, 5,                                 // 204: 11001100
    0, 8, 7, 0, 7, 1, 1, 7, 5,                        // 205: 11001101
    8, 4, 5, 8, 5, 3, 3, 5, 1,                        // 206: 11001110
    0, 4, 5, 1, 0, 5,                                 // 207: 11001111
    9, 6, 5, 9, 0, 6, 0, 2, 6,                        // 208: 11010000
    5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8,               // 209: 11010001
    8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6,               // 210: 11010010
    7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9,      // 211: 11010011
    3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9,              // 212: 11010100
    6, 5, 9, 6, 9, 11, 11, 9, 8,                      // 213: 11010101
    0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7,     // 214: 11010110
    6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9,             // 215: 11010111
    9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7,              // 216: 11011000
    7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2,     // 217: 11011001
    0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5,    // 218: 11011010
    9, 4, 5, 2, 11, 3,                                // 219: 11011011
    9, 0, 3, 9, 3, 5, 5, 3, 7,                        // 220: 11011100
    9, 8, 7, 5, 9, 7,                                 // 221: 11011101
    8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5,               // 222: 11011110
    9, 4, 5,                                          // 223: 11011111
    1, 4, 9, 1, 2, 4, 2, 6, 4,                        // 224: 11100000
    3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4,               // 225: 11100001
    1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7,               // 226: 11100010
    2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9,      // 227: 11100011
    9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3,              // 228: 11100100
    8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1,    // 229: 11100101
    8, 9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6,     // 230: 11100110
    0, 9, 1, 11, 6, 7,                                // 231: 11100111
    4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2,            // 232: 11101000
    9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3,   // 233: 11101001
    1, 2, 11, 1, 11, 9, 9, 11, 8,                     // 234: 11101010
    3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9,             // 235: 11101011
    4, 9, 1, 4, 1, 7, 7, 1, 3,                        // 236: 11101100
    4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1,               // 237: 11101101
    1, 3, 8, 9, 1, 8,                                 // 238: 11101110
    0, 9, 1,                                          // 239: 11101111
    0, 2, 4, 4, 2, 6,                                 // 240: 11110000
    8, 3, 2, 8, 2, 4, 4, 2, 6,                        // 241: 11110001
    7, 8, 0, 7, 0, 6, 6, 0, 2,                        // 242: 11110010
    7, 3, 2, 6, 7, 2,                                 // 243: 11110011
    3, 11, 6, 3, 6, 0, 0, 6, 4,                       // 244: 11110100
    6, 4, 8, 11, 6, 8,                                // 245: 11110101
    7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0,             // 246: 11110110
    7, 11, 6,                                         // 247: 11110111
    11, 7, 4, 11, 4, 2, 2, 4, 0,                      // 248: 11111000
    11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4,             // 249: 11111001
    0, 2, 11, 8, 0, 11,                               // 250: 11111010
    3, 2, 11,                                         // 251: 11111011
    4, 0, 3, 7, 4, 3,                                 // 252: 11111100
    4, 8, 7,                                          // 253: 11111101
    0, 3, 8                                           // 254: 11111110
                                                      // 255: 11111111
};

std::array<std::uint16_t, 257> triangleIndices =
{
    0, 0, 1, 2, 4, 5, 7, 9, 12, 13, 15, 17, 20, 22, 25, 28, 30, 31, 33, 35, 38, 40, 43, 
    46, 50, 52, 55, 58, 62, 65, 69, 73, 76, 77, 79, 81, 84, 86, 89, 92, 96, 98, 101, 104, 
    108, 111, 115, 119, 122, 124, 127, 130, 132, 135, 139, 143, 146, 149, 153, 157, 160, 
    164, 169, 174, 176, 177, 179, 181, 184, 186, 189, 192, 196, 198, 201, 204, 208, 211, 
    215, 219, 222, 224, 227, 230, 234, 237, 239, 243, 246, 249, 253, 257, 262, 266, 269, 
    274, 276, 278, 281, 284, 288, 291, 295, 299, 304, 307, 311, 315, 320, 324, 329, 334, 
    338, 341, 345, 349, 352, 356, 359, 364, 366, 370, 375, 380, 384, 389, 393, 395, 396, 
    397, 399, 401, 404, 406, 409, 412, 416, 418, 421, 424, 428, 431, 435, 439, 442, 444, 
    447, 450, 454, 457, 461, 465, 470, 473, 477, 481, 486, 490, 495, 500, 504, 506, 509, 
    512, 516, 519, 523, 527, 532, 535, 539, 541, 544, 548, 553, 556, 558, 561, 565, 569, 
    572, 576, 581, 586, 590, 594, 599, 602, 604, 609, 611, 615, 616, 618, 621, 624, 628, 
    631, 635, 639, 644, 647, 651, 655, 660, 662, 665, 668, 670, 673, 677, 681, 686, 690, 
    693, 698, 702, 706, 711, 716, 718, 721, 723, 727, 728, 731, 735, 739, 744, 748, 753, 
    758, 760, 764, 769, 772, 776, 779, 783, 785, 786, 788, 791, 794, 796, 799, 801, 805, 
    806, 809, 813, 815, 816, 818, 819, 820, 820
};

//std::array<std::uint16_t, 256> edgeTable =
//{
//    0, 265, 400, 153, 2060, 2309, 2460, 2197, 2240, 2505, 2384, 2137, 204, 453, 348, 85, 
//    515, 778, 915, 666, 2575, 2822, 2975, 2710, 2755, 3018, 2899, 2650, 719, 966, 863, 
//    598, 560, 825, 928, 681, 2620, 2869, 2988, 2725, 2800, 3065, 2912, 2665, 764, 1013, 
//    876, 613, 51, 314, 419, 170, 2111, 2358, 2479, 2214, 2291, 2554, 2403, 2154, 255, 
//    502, 367, 102, 1030, 1295, 1430, 1183, 3082, 3331, 3482, 3219, 3270, 3535, 3414, 3167, 
//    1226, 1475, 1370, 1107, 1541, 1804, 1941, 1692, 3593, 3840, 3993, 3728, 3781, 4044, 
//    3925, 3676, 1737, 1984, 1881, 1616, 1590, 1855, 1958, 1711, 3642, 3891, 4010, 3747, 
//    3830, 4095, 3942, 3695, 1786, 2035, 1898, 1635, 1077, 1340, 1445, 1196, 3129, 3376, 
//    3497, 3232, 3317, 3580, 3429, 3180, 1273, 1520, 1385, 1120, 1120, 1385, 1520, 1273, 
//    3180, 3429, 3580, 3317, 3232, 3497, 3376, 3129, 1196, 1445, 1340, 1077, 1635, 1898, 
//    2035, 1786, 3695, 3942, 4095, 3830, 3747, 4010, 3891, 3642, 1711, 1958, 1855, 1590, 
//    1616, 1881, 1984, 1737, 3676, 3925, 4044, 3781, 3728, 3993, 3840, 3593, 1692, 1941,
//    1804, 1541, 1107, 1370, 1475, 1226, 3167, 3414, 3535, 3270, 3219, 3482, 3331, 3082, 
//    1183, 1430, 1295, 1030, 102, 367, 502, 255, 2154, 2403, 2554, 2291, 2214, 2479, 2358, 
//    2111, 170, 419, 314, 51, 613, 876, 1013, 764, 2665, 2912, 3065, 2800, 2725, 2988, 2869, 
//    2620, 681, 928, 825, 560, 598, 863, 966, 719, 2650, 2899, 3018, 2755, 2710, 2975, 2822, 
//    2575, 666, 915, 778, 515, 85, 348, 453, 204, 2137, 2384, 2505, 2240, 2197, 2460, 2309, 
//    2060, 153, 400, 265, 0
//};

std::vector<std::vector<std::uint8_t>> tetrahedra =
{
/*   0: 00000000 */ { },
/*   1: 00000001 */ { 8, 16, 11, 0 },
/*   2: 00000010 */ { 12, 16, 1, 15 },
/*   3: 00000011 */ { 12, 11, 8, 0, 15, 11, 12, 1, 0, 1, 12, 11 },
/*   4: 00000100 */ { 10, 19, 2, 11 },
/*   5: 00000101 */ { 8, 10, 2, 19, 0, 8, 2, 16, 8, 16, 19, 2 },
/*   6: 00000110 */ { 16, 12, 15, 1, 11, 19, 10, 2 },
/*   7: 00000111 */ { 19, 12, 15, 0, 19, 10, 12, 0, 10, 8, 12, 0, 0, 1, 12, 15, 0, 2, 19, 10 },
/*   8: 00001000 */ { 14, 19, 15, 3 },
/*   9: 00001001 */ { 16, 8, 0, 11, 15, 19, 3, 14 },
/*  10: 00001010 */ { 16, 14, 19, 3, 12, 14, 16, 1, 3, 1, 16, 14 },
/*  11: 00001011 */ { 14, 12, 1, 8, 1, 0, 11, 8, 1, 3, 14, 19, 8, 11, 1, 14, 11, 1, 14, 19 },
/*  12: 00001100 */ { 2, 10, 15, 11, 2, 10, 3, 15, 14, 10, 15, 3 },
/*  13: 00001101 */ { 8, 10, 2, 14, 2, 3, 15, 14, 2, 0, 8, 16, 8, 14, 2, 15, 8, 16, 15, 2 },
/*  14: 00001110 */ { 16, 10, 11, 3, 16, 12, 10, 3, 12, 14, 10, 3, 3, 2, 10, 11, 3, 1, 16, 12 },
/*  15: 00001111 */ { 8, 12, 10, 0, 12, 14, 10, 3, 0, 3, 12, 10, 0, 1, 12, 3, 0, 2, 3, 10 },
/*  16: 00010000 */ { 8, 17, 4, 9 },
/*  17: 00010001 */ { 0, 11, 16, 9, 0, 4, 9, 16, 4, 9, 16, 17 },
/*  18: 00010010 */ { 16, 15, 1, 12, 8, 17, 4, 9 },
/*  19: 00010011 */ { 9, 11, 0, 15, 0, 1, 12, 15, 0, 4, 9, 17, 9, 0, 12, 15, 9, 0, 17, 12 },
/*  20: 00010100 */ { 8, 17, 4, 9, 11, 10, 2, 19 },
/*  21: 00010101 */ { 19, 16, 0, 17, 0, 4, 9, 17, 0, 2, 19, 10, 0, 10, 19, 9, 0, 17, 9, 19 },
/*  22: 00010110 */ { 17, 8, 9, 4, 16, 12, 15, 1, 10, 11, 19, 2 },
/*  23: 00010111 */ { 0, 1, 12, 15, 0, 19, 15, 12, 0, 19, 12, 17, 0, 19, 17, 10, 0, 9, 10, 17, 0, 9, 17, 4, 0, 2, 19, 10 },
/*  24: 00011000 */ { 8, 9, 17, 4, 19, 15, 14, 3 },
/*  25: 00011001 */ { 16, 9, 17, 4, 16, 11, 9, 4, 19, 15, 14, 3, 0, 4, 11, 16 },
/*  26: 00011010 */ { 16, 14, 19, 3, 16, 12, 14, 3, 17, 8, 9, 4, 1, 3, 12, 16 },
/*  27: 00011011 */ { 19, 11, 12, 1, 17, 12, 11, 0, 0, 11, 1, 12, 0, 11, 17, 4, 19, 3, 1, 12, 12, 14, 19, 3, 4, 9, 11, 17, 11, 14, 19, 12, 11, 14, 12, 17 },
/*  28: 00011100 */ { 10, 15, 14, 3, 10, 11, 15, 3, 8, 9, 17, 4, 2, 3, 11, 10 },
/*  29: 00011101 */ { 9, 10, 16, 14, 2, 10, 14, 16, 2, 15, 16, 14, 2, 15, 14, 3, 4, 9, 16, 17, 4, 9, 0, 16, 10, 9, 16, 0, 10, 2, 0, 16 },
/*  30: 00011110 */ { 4, 8, 17, 9, 10, 14, 3, 12, 16, 12, 11, 1, 2, 3, 12, 10, 11, 2, 12, 10, 1, 12, 2, 3, 1, 12, 11, 2 },
/*  31: 00011111 */ { 12, 14, 10, 3, 4, 0, 17, 9, 3, 2, 10, 12, 2, 10, 12, 0, 3, 2, 12, 0, 3, 1, 0, 12, 0, 10, 12, 9, 0, 9, 12, 17 },
/*  32: 00100000 */ { 12, 17, 13, 5 },
/*  33: 00100001 */ { 16, 11, 8, 0, 12, 17, 13, 5 },
/*  34: 00100010 */ { 17, 15, 16, 1, 13, 15, 17, 5, 1, 5, 17, 15 },
/*  35: 00100011 */ { 17, 11, 8, 1, 17, 13, 11, 1, 13, 15, 11, 1, 1, 0, 11, 8, 1, 5, 17, 13 },
/*  36: 00100100 */ { 12, 13, 5, 17, 19, 11, 2, 10 },
/*  37: 00100101 */ { 17, 12, 5, 13, 0, 2, 16, 8, 8, 2, 19, 10, 2, 16, 8, 19 },
/*  38: 00100110 */ { 19, 11, 2, 10, 16, 15, 1, 17, 17, 15, 5, 13, 1, 5, 17, 15 },
/*  39: 00100111 */ { 19, 15, 0, 8, 17, 8, 1, 15, 1, 15, 8, 0, 1, 15, 5, 17, 19, 2, 8, 0, 8, 10, 2, 19, 5, 13, 17, 15, 15, 10, 8, 19, 15, 10, 17, 8 },
/*  40: 00101000 */ { 12, 17, 13, 5, 15, 14, 19, 3 },
/*  41: 00101001 */ { 17, 12, 5, 13, 16, 8, 0, 11, 14, 15, 3, 19 },
/*  42: 00101010 */ { 14, 17, 13, 1, 14, 19, 17, 1, 19, 16, 17, 1, 1, 5, 17, 13, 1, 3, 14, 19 },
/*  43: 00101011 */ { 8, 11, 1, 14, 8, 13, 14, 1, 8, 13, 1, 17, 11, 14, 19, 1, 14, 19, 1, 3, 0, 1, 8, 11, 1, 5, 17, 13 },
/*  44: 00101100 */ { 12, 13, 5, 17, 2, 10, 15, 11, 3, 10, 14, 15, 2, 3, 15, 10 },
/*  45: 00101101 */ { 5, 12, 13, 17, 2, 8, 10, 14, 2, 14, 15, 16, 2, 8, 14, 16,  2, 3, 15, 14, 0, 8, 2, 16 },
/*  46: 00101110 */ { 2, 10, 16, 11, 13, 16, 17, 5, 13, 16, 5, 1, 2, 10, 13, 16, 2, 10, 14, 13, 2, 3, 13, 14, 2, 3, 1, 13, 2, 16, 13, 1 },
/*  47: 00101111 */ { 17, 14, 1, 13, 17, 8, 1, 14, 8, 10, 2, 14, 5, 1, 13, 17, 2, 3, 8, 14, 3, 14, 1, 8, 2, 3, 1, 8, 2, 0, 8, 1 },
/*  48: 00110000 */ { 8, 13, 12, 5, 8, 9, 13, 5, 4, 5, 9, 8 },
/*  49: 00110001 */ { 16, 13, 12, 4, 16, 11, 13, 4, 11, 9, 13, 4, 4, 5, 13, 12, 4, 0, 16, 11 },
/*  50: 00110010 */ { 9, 13, 15, 5, 8, 16, 1, 15, 8, 9, 15, 1, 1, 5, 9, 15, 1, 4, 9, 5, 1, 4, 8, 9 },
/*  51: 00110011 */ { 11, 13, 15, 1, 9, 11, 5, 13, 1, 5, 11, 13, 0, 1, 5, 11, 11, 4, 9, 5, 0, 4, 11, 5 },
/*  52: 00110100 */ { 8, 13, 12, 5, 8, 9, 13, 5, 10, 11, 19, 2, 4, 5, 9, 8 },
/*  53: 00110101 */ { 2, 10, 19, 16, 2, 10, 16, 0, 5, 12, 13, 16, 0, 4, 10, 16, 4, 9, 10, 13, 4, 10, 16, 13, 4, 5, 13, 16 },
/*  54: 00110110 */ { 2, 11, 10, 19, 1, 9, 16, 15, 9, 13, 15, 5, 4, 8, 16, 9, 1, 5, 9, 15, 4, 5, 9, 1, 1, 4, 16, 9 },
/*  55: 00110111 */ { 19, 9, 0, 10, 19, 15, 0, 9, 15, 13, 5, 9, 2, 0, 10, 19, 5, 4, 15, 9, 4, 9, 0, 15, 5, 4, 0, 15, 5, 1, 15, 0 },
/*  56: 00111000 */ { 14, 15, 3, 19, 8, 12, 5, 13, 4, 8, 13, 9, 8, 4, 13, 5 },
/*  57: 00111001 */ { 3, 15, 19, 14, 0, 9, 11, 16, 13, 9, 12, 11, 13, 9, 5, 12, 12, 11, 9, 16, 5, 12, 9, 4, 12, 16, 9, 4, 16, 0, 9, 4 },
/*  58: 00111010 */ { 14, 13, 1, 16, 8, 16, 5, 13, 5, 13, 16, 1, 5, 13, 4, 8, 14, 3, 16, 1, 16, 19, 3, 14, 4, 9, 8, 13, 13, 19, 16, 14, 13, 19, 8, 16 },
/*  59: 00111011 */ { 11, 9, 13, 4, 3, 1, 19, 14, 4, 5, 13, 11, 5, 13, 11, 1, 4, 5, 11, 1, 4, 0, 1, 11, 1, 11, 19, 14, 1, 11, 14, 13 },
/*  60: 00111100 */ { 11, 15, 14, 3, 8, 12, 5, 13, 8, 13, 4, 9, 8, 4, 13, 5, 11, 10, 3, 14, 2, 3, 11, 10 },
/*  61: 00111101 */ { 5, 12, 13, 16, 3, 14, 15, 16, 9, 10, 0, 16, 9, 13, 16, 5, 10, 14, 3, 16, 4, 5, 9, 16, 0, 2, 16, 10, 0, 4, 9, 16, 2, 10, 3, 16 },
/*  62: 00111110 */ { 2, 11, 10, 16, 8, 16, 4, 9, 16, 1, 13, 14, 16, 9, 13, 5, 16, 10, 3, 14, 16, 1, 5, 13, 16, 4, 9, 5, 16, 1, 14, 3, 16, 2, 3, 10 },
/*  63: 00111111 */ { 9, 13, 14, 1, 10, 9, 14, 0, 9, 14, 0, 1, 0, 1, 4, 9, 1, 4, 9, 5, 1, 5, 9, 13, 0, 1, 14, 3, 0, 2, 3, 14, 0, 2, 14, 10 },
/*  64: 01000000 */ { 10, 18, 9, 6 },
/*  65: 01000001 */ { 10, 18, 9, 6, 11, 8, 16, 0 },
/*  66: 01000010 */ { 10, 9, 6, 18, 16, 15, 1, 12 },
/*  67: 01000011 */ { 10, 9, 6, 18, 0, 8, 11, 12, 1, 11, 15, 12, 0, 1, 12, 11 },
/*  68: 01000100 */ { 18, 11, 19, 2, 9, 11, 18, 6, 2, 6, 18, 11 },
/*  69: 01000101 */ { 8, 18, 9, 2, 8, 16, 18, 2, 16, 19, 18, 2, 2, 6, 18, 9, 2, 0, 8, 16 },
/*  70: 01000110 */ { 16, 15, 1, 12, 11, 18, 2, 19, 6, 9, 18, 11, 2, 6, 18, 11 },
/*  71: 01000111 */ { 6, 9, 18, 19, 2, 9, 6, 19, 2, 8, 9, 19, 2, 8, 19, 0, 8, 9, 19, 12, 1, 12, 19, 15, 0, 1, 8, 19, 1, 8, 19, 12 },
/*  72: 01001000 */ { 19, 15, 14, 3, 10, 18, 9, 6 },
/*  73: 01001001 */ { 18, 10, 6, 9, 19, 14, 3, 15, 8, 11, 0, 16 },
/*  74: 01001010 */ { 18, 10, 6, 9, 12, 14, 16, 1, 14, 16, 3, 19, 14, 16, 1, 3 },
/*  75: 01001011 */ { 6, 10, 9, 18, 0, 8, 11, 19, 8, 12, 14, 1, 14, 19, 8, 1, 0, 8, 19, 1, 1, 19, 3, 14 },
/*  76: 01001100 */ { 18, 15, 14, 2, 18, 9, 15, 2, 9, 11, 15, 2, 2, 3, 15, 14, 2, 6, 18, 9 },
/*  77: 01001101 */ { 3, 14, 15, 18, 0, 9, 16, 8, 15, 9, 6, 18, 15, 3, 18, 6, 15, 3, 6, 2, 0, 6, 16, 9, 15, 6, 9, 16, 0, 2, 16, 6, 15, 2, 6, 16 },
/*  78: 01001110 */ { 6, 9, 18, 14, 1, 12, 16, 14, 1, 3, 14, 16, 2, 6, 14, 9, 2, 11, 9, 14, 16, 11, 14, 9, 11, 2, 3, 14, 11, 16, 14, 3 },
/*  79: 01001111 */ { 18, 8, 2, 9, 18, 14, 2, 8, 14, 12, 1, 8, 6, 2, 9, 18, 1, 0, 14, 8, 0, 8, 2, 14, 1, 0, 2, 14, 1, 3, 14, 2 },
/*  80: 01010000 */ { 17, 10, 18, 6, 8, 10, 17, 4, 6, 4, 17, 10 },
/*  81: 01010001 */ { 10, 16, 11, 4, 10, 18, 16, 4, 18, 17, 16, 4, 4, 0, 16, 11, 4, 6, 10, 18 },
/*  82: 01010010 */ { 17, 10, 18, 6, 17, 8, 10, 6, 16, 12, 15, 1, 4, 6, 8, 17 },
/*  83: 01010011 */ { 6, 10, 17, 18, 6, 10, 4, 17, 10, 15, 11, 0, 0, 10, 15, 17, 0, 4, 10, 17, 0, 12, 17, 15, 0, 1, 12, 15 },
/*  84: 01010100 */ { 17, 18, 6, 19, 6, 2, 11, 19, 6, 4, 17, 8, 11, 17, 6, 19, 8, 11, 17, 6 },
/*  85: 01010101 */ { 16, 17, 4, 18, 16, 18, 2, 19, 2, 4, 18, 16, 2, 4, 16, 0, 2, 4, 6, 18 },
/*  86: 01010110 */ { 1, 16, 15, 12, 17, 19, 2, 8, 17, 19, 18, 2, 8, 2, 17, 4, 2, 4, 6, 17, 6, 18, 2, 17, 8, 11, 19, 2 },
/*  87: 01010111 */ { 12, 19, 0, 15, 12, 17, 0, 19, 17, 18, 6, 19, 1, 0, 15, 12, 6, 2, 17, 19, 2, 19, 0, 17, 6, 2, 0, 17, 6, 4, 17, 0 },
/*  88: 01011000 */ { 19, 14, 3, 15, 8, 10, 17, 4, 10, 17, 6, 18, 4, 17, 6, 10 },
/*  89: 01011001 */ { 3, 19, 14, 15, 16, 17, 4, 18, 11, 16, 4, 18, 11, 10, 18, 4, 0, 4, 11, 16, 4, 10, 18, 6 },
/*  90: 01011010 */ { 1, 16, 19, 12, 12, 14, 19, 3, 8, 10, 17, 4, 10, 17, 6, 18, 4, 17, 6, 10, 1, 12, 19, 3 },
/*  91: 01011011 */ { 0, 11, 12, 17, 11, 17, 4, 18, 11, 12, 14, 1, 11, 19, 1, 14, 0, 11, 1, 12, 3, 19, 14, 1, 0, 11, 17, 4, 11, 18, 6, 10, 11, 4, 6, 18 },
/*  92: 01011100 */ { 8, 11, 15, 2, 8, 15, 18, 2, 15, 14, 2, 3, 8, 17, 4, 18, 14, 15, 2, 18, 8, 2, 18, 6, 8, 4, 6, 18 },
/*  93: 01011101 */ { 18, 17, 16, 4, 3, 2, 14, 15, 4, 0, 16, 18, 0, 16, 18, 2, 4, 0, 18, 2, 4, 6, 2, 18, 2, 18, 14, 15, 16, 15, 18, 2 },
/*  94: 01011110 */ { 11, 17, 8, 4, 11, 17, 4, 18, 16, 12, 11, 1, 11, 12, 14, 1, 11, 14, 18, 2, 4, 11, 18, 6, 11, 2, 18, 6, 1, 11, 3, 14, 2, 11, 14, 3 },
/*  95: 01011111 */ { 12, 17, 0, 18, 12, 18, 0, 14, 0, 4, 18, 17, 0, 1, 12, 14, 0, 4, 6, 18, 0, 2, 18, 6, 0, 2, 14, 18, 2, 1, 0, 14, 1, 2, 3, 14 },
/*  96: 01100000 */ { 17, 12, 5, 13, 9, 18, 6, 10 },
/*  97: 01100001 */ { 16, 8, 0, 11, 17, 12, 5, 13, 10, 9, 6, 18 },
/*  98: 01100010 */ { 17, 15, 16, 1, 17, 13, 15, 1, 18, 9, 10, 6, 5, 1, 13, 17 },
/*  99: 01100011 */ { 6, 9, 18, 10, 5, 15, 13, 17, 11, 15, 8, 13, 11, 15, 0, 8, 8, 13, 15, 17, 0, 8, 15, 1, 8, 17, 15, 1, 17, 5, 15, 1 },
/* 100: 01100100 */ { 18, 11, 19, 2, 18, 9, 11, 2, 17, 13, 12, 5, 6, 2, 9, 18 },
/* 101: 01100101 */ { 5, 17, 12, 13, 16, 19, 18, 2, 16, 18, 9, 6, 16, 18, 6, 2, 0, 16, 6, 2, 0, 16, 9, 6, 16, 9, 8, 0 },
/* 102: 01100110 */ { 13, 15, 16, 1, 13, 16, 17, 5, 11, 18, 9, 6, 11, 18, 2, 19, 16, 13, 1, 5, 11, 18, 6, 2 },
/* 103: 01100111 */ { 8, 13, 15, 1, 8, 13, 1, 17, 8, 18, 2, 19, 8, 18, 9, 2, 9, 2, 18, 6, 8, 0, 15, 19, 8, 0, 1, 15, 8, 0, 19, 2, 1, 5, 17, 13 },
/* 104: 01101000 */ { 19, 14, 3, 15, 18, 10, 6, 9, 12, 13, 5, 17 },
/* 105: 01101001 */ { 0, 8, 11, 16, 3, 14, 15, 19, 5, 12, 13, 17, 6, 9, 18, 10 },
/* 106: 01101010 */ { 6, 18, 10, 9, 19, 17, 13, 1, 13, 19, 1, 14, 16, 17, 19, 1, 1, 5, 17, 13, 1, 3, 14, 19 },
/* 107: 01101011 */ { 6, 9, 18, 10, 17, 14, 1, 13, 17, 14, 8, 1, 8, 14, 19, 1, 19, 1, 14, 3, 1, 5, 17, 13, 11, 1, 8, 19, 0, 1, 8, 11 },
/* 108: 01101100 */ { 5, 13, 17, 12, 11, 9, 2, 15, 14, 9, 15, 2, 14, 9, 6, 18, 9, 2, 14, 6, 2, 3, 15, 14 },
/* 109: 01101101 */ { 5, 12, 13, 17, 16, 8, 2, 15, 8, 15, 9, 2, 15, 9, 2, 14, 9, 14, 18, 2, 0, 8, 2, 16, 14, 15, 3, 2, 2, 6, 18, 9 },
/* 110: 01101110 */ { 17, 14, 5, 13, 16, 17, 14, 1, 11, 16, 14, 3, 9, 18, 6, 14, 9, 11, 14, 2, 1, 5, 17, 14, 1, 3, 14, 16, 11, 2, 3, 14, 2, 6, 14, 9 },
/* 111: 01101111 */ { 8, 17, 13, 1, 8, 13, 14, 1, 8, 9, 2, 18, 8, 18, 2, 14, 1, 2, 14, 8, 6, 18, 2, 9, 0, 1, 8, 2, 1, 2, 3, 14, 1, 17, 13, 5 },
/* 112: 01110000 */ { 8, 12, 4, 10, 10, 12, 4, 13, 10, 13, 4, 18, 4, 5, 13, 12, 4, 10, 18, 6 },
/* 113: 01110001 */ { 16, 12, 4, 11, 12, 11, 13, 4, 11, 13, 4, 10, 13, 10, 18, 4, 0, 4, 11, 16, 4, 5, 13, 12, 4, 6, 10, 18 },
/* 114: 01110010 */ { 18, 13, 8, 4, 16, 8, 13, 5, 5, 13, 4, 8, 5, 13, 16, 1, 18, 6, 4, 8, 8, 10, 18, 6, 1, 15, 13, 16, 13, 10, 18, 8, 13, 10, 8, 16 },
/* 115: 01110011 */ { 13, 15, 11, 1, 6, 4, 18, 10, 1, 0, 11, 13, 0, 11, 13, 4, 1, 0, 13, 4, 1, 5, 4, 13, 10, 13, 4, 18, 10, 13, 11, 4 },
/* 116: 01110100 */ { 11, 8, 6, 18, 13, 18, 4, 8, 4, 8, 18, 6, 4, 8, 5, 13, 11, 2, 18, 6, 18, 19, 2, 11, 5, 12, 13, 8, 8, 19, 18, 11, 8, 19, 13, 18 },
/* 117: 01110101 */ { 16, 19, 18, 2, 5, 4, 12, 13, 2, 6, 18, 16, 6, 18, 16, 4, 2, 6, 16, 4, 2, 0, 4, 16, 12, 13, 4, 16, 13, 16, 18, 4 },
/* 118: 01110110 */ { 8, 16, 1, 15, 8, 15, 5, 13, 8, 13, 5, 18, 8, 18, 2, 19, 8, 11, 19, 2, 8, 1, 5, 15, 8, 5, 4, 18, 8, 2, 18, 6, 8, 4, 6, 18 },
/* 119: 01110111 */ { 13, 15, 19, 0, 13, 18, 0, 19, 0, 1, 13, 15, 0, 4, 18, 13, 0, 1, 5, 13, 0, 13, 5, 4, 0, 2, 19, 18, 0, 4, 6, 18, 0, 2, 18, 6 },
/* 120: 01111000 */ { 3, 14, 15, 19, 8, 10, 12, 4, 10, 12, 4, 18, 12, 13, 4, 18, 4, 6, 10, 18, 4, 5, 13, 12 },
/* 121: 01111001 */ { 3, 15, 19, 14, 16, 12, 4, 11, 12, 11, 13, 4, 11, 13, 4, 10, 13, 10, 18, 4, 0, 4, 11, 16, 4, 5, 13, 12, 4, 6, 10, 18 },
/* 122: 01111010 */ { 16, 19, 1, 13, 13, 19, 3, 14, 8, 16, 5, 13, 10, 13, 6, 18, 1, 13, 19, 3, 16, 1, 5, 13, 8, 4, 13, 5, 8, 13, 4, 10, 4, 10, 13, 6 },
/* 123: 01111011 */ { 11, 14, 19, 1, 11, 14, 1, 13, 11, 18, 13, 4, 11, 18, 4, 10, 1, 4, 11, 13, 4, 18, 6, 10, 0, 1, 4, 11, 1, 4, 13, 5, 1, 3, 14, 19 },
/* 124: 01111100 */ { 12, 18, 4, 8, 12, 18, 13, 4, 8, 18, 6, 11, 11, 18, 2, 15, 15, 18, 2, 14, 4, 5, 13, 12, 4, 6, 8, 18, 2, 11, 6, 18, 2, 3, 15, 14 },
/* 125: 01111101 */ { 12, 18, 4, 16, 12, 18, 13, 4, 15, 18, 2, 14, 15, 18, 16, 2, 16, 18, 4, 2, 4, 5, 13, 12, 2, 3, 15, 14, 0, 2, 16, 4, 2, 4, 6, 18 },
/* 126: 01111110 */ { 8, 11, 16, 6, 13, 14, 18, 1, 1, 13, 5, 18, 1, 18, 3, 14, 16, 6, 4, 8, 16, 6, 11, 2, 16, 6, 2, 1, 16, 6, 1, 4, 1, 18, 4, 6, 1, 18, 6, 2, 1, 18, 5, 4, 1, 18, 2, 3 },
/* 127: 01111111 */ { 18, 13, 14, 4, 18, 4, 2, 6, 18, 14, 2, 4, 4, 5, 13, 1, 1, 4, 14, 13, 0, 1, 4, 14, 0, 2, 14, 4, 1, 2, 3, 14, 0, 1, 14, 2 },
/* 128: 10000000 */ { 14, 18, 7, 13 },
/* 129: 10000001 */ { 14, 13, 18, 7, 16, 11, 8, 0 },
/* 130: 10000010 */ { 14, 18, 7, 13, 15, 12, 1, 16 },
/* 131: 10000011 */ { 12, 11, 8, 0, 12, 15, 11, 0, 14, 13, 18, 7, 1, 0, 15, 12 },
/* 132: 10000100 */ { 19, 11, 2, 10, 14, 18, 7, 13 },
/* 133: 10000101 */ { 19, 8, 16, 0, 19, 10, 8, 0, 18, 14, 13, 7, 2, 0, 10, 19 },
/* 134: 10000110 */ { 18, 14, 13, 7, 19, 10, 11, 2, 12, 15, 16, 1 },
/* 135: 10000111 */ { 7, 14, 18, 13, 10, 12, 0, 8, 10, 12, 15, 1, 10, 15, 19, 2, 0, 1, 12, 10, 0, 1, 10, 2, 2, 10, 15, 1 },
/* 136: 10001000 */ { 13, 15, 3, 19, 19, 18, 7, 13, 19, 13, 7, 3 },
/* 137: 10001001 */ { 19, 13, 18, 7, 19, 15, 13, 7, 16, 11, 8, 0, 3, 7, 15, 19 },
/* 138: 10001010 */ { 16, 18, 3, 13, 12, 16, 3, 13, 16, 19, 3, 18, 3, 7, 13, 18, 3, 1, 16, 12 },
/* 139: 10001011 */ { 8, 13, 1, 12, 8, 13, 19, 1, 8, 11, 1, 19, 8, 11, 0, 1, 1, 19, 3, 13, 18, 19, 13, 7, 13, 19, 3, 7 },
/* 140: 10001100 */ { 11, 15, 13, 3, 11, 13, 10, 3, 10, 13, 18, 7, 10, 13, 7, 3, 10, 11, 3, 2 },
/* 141: 10001101 */ { 16, 15, 13, 3, 16, 13, 10, 3, 10, 13, 18, 7, 0, 8, 10, 16, 3, 7, 13, 10, 0, 16, 10, 2, 10, 16, 3, 2 },
/* 142: 10001110 */ { 16, 12, 11, 3, 12, 11, 3, 13, 11, 13, 10, 3, 13, 10, 3, 18, 13, 18, 3, 7, 2, 10, 3, 11, 16, 12, 3, 1 },
/* 143: 10001111 */ { 10, 13, 3, 12, 10, 13, 18, 7, 8, 12, 10, 0, 10, 13, 7, 3, 10, 12, 3, 2, 0, 2, 12, 10, 1, 2, 12, 0, 1, 2, 3, 12 },
/* 144: 10010000 */ { 17, 8, 9, 4, 13, 18, 14, 7 },
/* 145: 10010001 */ { 18, 13, 7, 14, 0, 9, 11, 16, 9, 16, 4, 17, 9, 16, 0, 4 },
/* 146: 10010010 */ { 16, 12, 15, 1, 17, 8, 9, 4, 14, 13, 18, 7 },
/* 147: 10010011 */ { 7, 13, 14, 18, 12, 15, 17, 0, 15, 17, 0, 9, 15, 9, 0, 11, 0, 4, 9, 17, 0, 1, 12, 15 },
/* 148: 10010100 */ { 19, 10, 11, 2, 18, 14, 13, 7, 8, 9, 17, 4 },
/* 149: 10010101 */ { 7, 18, 13, 14, 19, 17, 16, 0, 19, 17, 0, 10, 9, 10, 0, 17, 0, 4, 9, 17, 0, 2, 19, 10 },
/* 150: 10010110 */ { 1, 12, 16, 15, 2, 10, 19, 11, 4, 8, 17, 9, 7, 13, 14, 18 },
/* 151: 10010111 */ { 7, 13, 14, 18, 15, 12, 0, 19, 12, 19, 17, 0, 19, 17, 0, 10, 17, 10, 9, 0, 0, 1, 12, 15, 0, 4, 9, 17, 0, 2, 19, 10 },
/* 152: 10011000 */ { 17, 9, 4, 8, 15, 19, 3, 13, 19, 18, 7, 13, 19, 13, 7, 3 },
/* 153: 10011001 */ { 13, 15, 7, 18, 19, 15, 18, 3, 15, 18, 3, 7, 16, 17, 4, 9, 11, 16, 0, 9, 16, 9, 4, 0 },
/* 154: 10011010 */ { 4, 17, 9, 8, 12, 18, 16, 3, 12, 18, 3, 13, 16, 18, 19, 3, 13, 18, 3, 7, 16, 12, 3, 1 },
/* 155: 10011011 */ { 11, 12, 19, 1, 11, 12, 0, 9, 9, 12, 4, 17, 0, 9, 12, 4, 0, 11, 1, 12, 1, 12, 19, 3, 12, 7, 13, 18, 12, 18, 19, 3, 12, 18, 3, 7 },
/* 156: 10011100 */ { 4, 9, 8, 17, 11, 15, 13, 3, 11, 13, 18, 3, 11, 18, 10, 3, 10, 11, 3, 2, 3, 18, 7, 13 },
/* 157: 10011101 */ { 10, 17, 4, 9, 10, 17, 16, 0, 10, 16, 15, 2, 10, 13, 3, 15, 10, 15, 3, 2, 0, 16, 10, 2, 10, 0, 4, 17, 7, 10, 18, 13, 3, 7, 13, 10 },
/* 158: 10011110 */ { 4, 9, 8, 17, 12, 16, 3, 13, 16, 13, 11, 3, 13, 11, 3, 18, 11, 18, 10, 3, 16, 12, 3, 1, 3, 13, 18, 7, 11, 3, 10, 2 },
/* 159: 10011111 */ { 10, 13, 18, 3, 10, 13, 3, 12, 10, 17, 12, 0, 10, 17, 0, 9, 10, 12, 3, 0, 3, 7, 13, 18, 0, 4, 9, 17, 0, 3, 1, 12, 0, 3, 10, 2 },
/* 160: 10100000 */ { 12, 18, 5, 17, 12, 18, 14, 7, 12, 18, 7, 5 },
/* 161: 10100001 */ { 12, 18, 5, 17, 12, 18, 14, 7, 12, 18, 7, 5, 0, 8, 11, 16 },
/* 162: 10100010 */ { 18, 17, 5, 16, 5, 1, 15, 16, 5, 7, 18, 14, 15, 18, 14, 5, 15, 18, 5, 16 },
/* 163: 10100011 */ { 14, 15, 17, 5, 8, 17, 15, 1, 1, 15, 5, 17, 1, 15, 8, 0, 14, 7, 5, 17, 17, 18, 14, 7, 0, 11, 15, 8, 15, 18, 14, 17, 15, 18, 17, 8 },
/* 164: 10100100 */ { 18, 12, 17, 5, 18, 14, 12, 5, 19, 10, 11, 2, 7, 5, 14, 18 },
/* 165: 10100101 */ { 16, 8, 0, 10, 16, 0, 2, 10, 16, 19, 10, 2, 5, 12, 18, 17, 5, 7, 18, 12, 7, 12, 14, 18 },
/* 166: 10100110 */ { 2, 19, 11, 10, 16, 15, 5, 14, 16, 14, 5, 18, 16, 18, 5, 17, 16, 1, 5, 15, 5, 14, 7, 18 },
/* 167: 10100111 */ { 15, 18, 5, 17, 15, 18, 14, 5, 8, 15, 1, 17, 8, 10, 0, 15, 10, 15, 19, 0, 5, 7, 18, 14, 1, 15, 5, 17, 0, 8, 15, 1, 0, 2, 19, 10 },
/* 168: 10101000 */ { 12, 19, 15, 7, 12, 17, 19, 7, 17, 18, 19, 7, 7, 3, 19, 15, 7, 5, 12, 17 },
/* 169: 10101001 */ { 0, 16, 8, 11, 17, 19, 7, 18, 17, 15, 7, 19, 17, 12, 7, 15, 7, 15, 3, 19, 12, 17, 7, 5 },
/* 170: 10101010 */ { 16, 17, 18, 5, 16, 18, 19, 3, 16, 18, 3, 5, 16, 1, 5, 3, 18, 3, 5, 7 },
/* 171: 10101011 */ { 8, 11, 1, 17, 11, 17, 19, 1, 19, 17, 18, 7, 17, 19, 1, 7, 0, 8, 11, 1, 1, 7, 5, 17, 1, 7, 19, 3 },
/* 172: 10101100 */ { 17, 18, 10, 7, 17, 10, 15, 7, 10, 11, 15, 2, 17, 15, 12, 7, 10, 15, 7, 2, 12, 17, 7, 5, 2, 3, 15, 7 },
/* 173: 10101101 */ { 12, 15, 7, 17, 15, 17, 18, 7, 16, 8, 2, 15, 8, 10, 2, 15, 10, 18, 3, 15, 12, 17, 7, 5, 0, 8, 2, 16, 10, 15, 3, 2, 15, 3, 7, 18 },
/* 174: 10101110 */ { 16, 17, 18, 3, 16, 18, 10, 3, 16, 10, 11, 3, 1, 7, 17, 3, 1, 7, 5, 17, 2, 3, 11, 10, 16, 1, 17, 3, 17, 3, 7, 18 },
/* 175: 10101111 */ { 8, 10, 3, 17, 10, 17, 18, 3, 1, 8, 3, 17, 3, 17, 18, 7, 3, 17, 5, 1, 3, 17, 7, 5, 0, 1, 8, 3, 0, 8, 10, 3, 0, 2, 3, 10 },
/* 176: 10110000 */ { 18, 8, 9, 5, 18, 14, 8, 5, 14, 12, 8, 5, 5, 4, 8, 9, 5, 7, 18, 14 },
/* 177: 10110001 */ { 12, 16, 14, 5, 16, 14, 5, 9, 9, 14, 5, 18, 9, 11, 0, 16, 0, 16, 4, 9, 4, 9, 16, 5, 5, 14, 7, 18 },
/* 178: 10110010 */ { 8, 16, 5, 9, 16, 9, 15, 5, 9, 15, 5, 18, 15, 18, 14, 5, 1, 15, 5, 16, 4, 8, 5, 9, 7, 14, 18, 5 },
/* 179: 10110011 */ { 18, 15, 5, 14, 18, 9, 5, 15, 9, 11, 0, 15, 7, 5, 14, 18, 0, 1, 9, 15, 1, 15, 5, 9, 0, 1, 5, 9, 0, 4, 9, 5 },
/* 180: 10110100 */ { 11, 10, 2, 19, 8, 12, 5, 14, 8, 14, 5, 9, 9, 14, 5, 18, 14, 18, 7, 5, 8, 4, 9, 5 },
/* 181: 10110101 */ { 9, 12, 5, 14, 9, 18, 14, 5, 16, 12, 4, 9, 9, 10, 2, 19, 9, 19, 2, 16, 4, 5, 9, 12, 5, 14, 7, 18, 0, 4, 9, 16, 0, 16, 9, 2 },
/* 182: 10110110 */ { 10, 11, 19, 2, 8, 16, 5, 9, 16, 9, 15, 5, 9, 15, 5, 18, 15, 18, 14, 5, 16, 1, 5, 15, 18, 14, 5, 7, 8, 9, 5, 4 },
/* 183: 10110111 */ { 9, 14, 15, 5, 9, 18, 14, 5, 9, 10, 0, 19, 9, 19, 0, 15, 0, 2, 19, 10, 9, 15, 0, 5, 5, 7, 18, 14, 0, 5, 15, 1, 0, 4, 9, 5 },
/* 184: 10111000 */ { 12, 15, 7, 19, 12, 19, 7, 9, 9, 19, 7, 18, 8, 12, 4, 9, 9, 12, 4, 5, 9, 7, 12, 5, 15, 7, 19, 3 },
/* 185: 10111001 */ { 12, 15, 7, 19, 12, 19, 7, 18, 12, 18, 5, 9, 12, 16, 11, 4, 12, 11, 9, 4, 4, 5, 9, 12, 4, 0, 16, 11, 5, 7, 18, 12, 3, 7, 15, 19 },
/* 186: 10111010 */ { 19, 16, 18, 5, 16, 18, 5, 8, 18, 8, 9, 5, 4, 5, 9, 8, 1, 5, 16, 19, 1, 3, 5, 19, 5, 7, 18, 19, 3, 5, 19, 7 },
/* 187: 10111011 */ { 9, 11, 5, 18, 11, 18, 19, 3, 11, 18, 3, 5, 3, 5, 18, 7, 11, 3, 1, 5, 0, 1, 5, 11, 9, 11, 4, 5, 0, 4, 11, 5 },
/* 188: 10111100 */ { 8, 12, 5, 18, 8, 18, 5, 9, 12, 15, 7, 18, 11, 15, 18, 3, 11, 10, 3, 18, 12, 5, 18, 7, 3, 7, 15, 18, 10, 11, 3, 2, 8, 9, 5, 4 },
/* 189: 10111101 */ { 16, 12, 5, 15, 9, 10, 2, 18, 15, 16, 2, 5, 9, 2, 5, 18, 2, 5, 18, 15, 2, 5, 16, 9, 15, 5, 18, 7, 0, 16, 9, 2, 0, 16, 4, 9, 4, 9, 16, 5, 2, 3, 15, 18, 3, 15, 18, 7 },
/* 190: 10111110 */ { 8, 9, 16, 5, 9, 16, 5, 18, 16, 10, 11, 3, 10, 16, 18, 3, 16, 18, 3, 5, 8, 9, 5, 4, 10, 11, 3, 2, 3, 5, 1, 16, 3, 5, 18, 7 },
/* 191: 10111111 */ { 9, 10, 1, 18, 9, 10, 0, 1, 9, 18, 1, 5, 10, 18, 3, 1, 1, 9, 4, 0, 1, 9, 5, 4, 1, 18, 7, 5, 1, 18, 3, 7, 1, 10, 0, 2, 1, 10, 2, 3 },
/* 192: 11000000 */ { 14, 9, 10, 6, 13, 9, 14, 7, 6, 7, 14, 9 },
/* 193: 11000001 */ { 14, 9, 10, 6, 13, 9, 14, 7, 6, 7, 14, 9, 8, 11, 0, 16 },
/* 194: 11000010 */ { 14, 9, 10, 6, 14, 13, 9, 6, 12, 15, 16, 1, 7, 6, 13, 14 },
/* 195: 11000011 */ { 8, 11, 0, 12, 11, 15, 1, 12, 12, 11, 0, 1, 9, 10, 13, 6, 10, 13, 7, 14, 10, 13, 6, 7 },
/* 196: 11000100 */ { 9, 13, 6, 11, 13, 11, 14, 6, 11, 14, 6, 19, 6, 7, 14, 13, 2, 6, 19, 11 },
/* 197: 11000101 */ { 0, 2, 16, 8, 2, 19, 16, 8, 8, 9, 6, 13, 7, 13, 14, 19, 6, 19, 8, 13, 6, 7, 19, 13, 2, 6, 19, 8 },
/* 198: 11000110 */ { 9, 11, 13, 6, 11, 13, 6, 19, 19, 14, 13, 6, 1, 12, 16, 15, 6, 7, 14, 13, 2, 6, 19, 11 },
/* 199: 11000111 */ { 12, 19, 8, 1, 19, 15, 1, 12, 13, 14, 7, 19, 9, 19, 13, 7, 8, 19, 9, 2, 0, 8, 19, 1, 9, 6, 19, 7, 19, 2, 6, 9, 19, 2, 8, 0 },
/* 200: 11001000 */ { 19, 9, 10, 7, 19, 15, 9, 7, 15, 13, 9, 7, 7, 6, 9, 10, 7, 3, 19, 15 },
/* 201: 11001001 */ { 0, 11, 16, 8, 19, 10, 7, 15, 10, 15, 9, 7, 15, 9, 7, 13, 3, 15, 19, 7, 9, 10, 7, 6 },
/* 202: 11001010 */ { 16, 19, 3, 10, 16, 10, 3, 13, 16, 13, 3, 12, 9, 10, 13, 6, 10, 6, 7, 13, 10, 13, 7, 3, 16, 12, 3, 1 },
/* 203: 11001011 */ { 8, 11, 1, 19, 8, 19, 1, 12, 12, 19, 3, 13, 9, 10, 19, 7, 9, 19, 13, 7, 13, 3, 7, 19, 1, 12, 19, 3, 0, 8, 11, 1, 9, 6, 10, 7 },
/* 204: 11001100 */ { 11, 13, 3, 15, 11, 13, 9, 6, 11, 13, 6, 3, 3, 6, 7, 13, 6, 11, 3, 2 },
/* 205: 11001101 */ { 16, 8, 2, 15, 8, 15, 9, 2, 15, 9, 7, 13, 8, 16, 2, 0, 9, 15, 7, 2, 2, 3, 15, 7, 2, 7, 9, 6 },
/* 206: 11001110 */ { 16, 13, 3, 12, 16, 11, 3, 13, 11, 9, 6, 13, 1, 3, 12, 16, 6, 7, 11, 13, 7, 13, 3, 11, 6, 7, 3, 11, 6, 2, 11, 3 },
/* 207: 11001111 */ { 8, 12, 13, 3, 8, 9, 6, 13, 3, 6, 13, 8, 6, 13, 7, 3, 6, 8, 3, 2, 1, 12, 8, 3, 0, 8, 2, 3, 0, 8, 3, 1 },
/* 208: 11010000 */ { 17, 14, 13, 6, 17, 8, 14, 6, 8, 10, 14, 6, 6, 7, 14, 13, 6, 4, 17, 8 },
/* 209: 11010001 */ { 0, 10, 11, 16, 10, 13, 7, 14, 10, 7, 13, 6, 0, 4, 10, 16, 4, 13, 16, 17, 16, 10, 13, 4, 6, 10, 4, 13 },
/* 210: 11010010 */ { 1, 12, 16, 15, 10, 8, 6, 14, 8, 14, 13, 6, 13, 8, 6, 17, 6, 7, 14, 13, 6, 4, 17, 8 },
/* 211: 11010011 */ { 17, 15, 11, 0, 17, 15, 0, 12, 17, 14, 13, 6, 17, 14, 6, 10, 0, 1, 12, 15, 6, 7, 14, 13, 10, 11, 4, 17, 4, 11, 0, 17, 4, 10, 17, 6 },
/* 212: 11010100 */ { 8, 11, 14, 6, 8, 13, 6, 14, 8, 13, 17, 6, 11, 14, 6, 19, 2, 6, 19, 11, 8, 17, 4, 6, 13, 14, 7, 6 },
/* 213: 11010101 */ { 14, 17, 6, 13, 14, 19, 6, 17, 19, 16, 0, 17, 7, 6, 13, 14, 0, 4, 19, 17, 4, 17, 6, 19, 0, 4, 6, 19, 0, 2, 19, 6 },
/* 214: 11010110 */ { 1, 12, 16, 15, 19, 11, 6, 14, 11, 14, 8, 6, 14, 8, 6, 13, 8, 13, 17, 6, 8, 4, 6, 17, 6, 13, 7, 14, 6, 11, 19, 2 },
/* 215: 11010111 */ { 15, 17, 12, 0, 15, 17, 0, 19, 14, 17, 19, 6, 14, 17, 6, 13, 17, 19, 6, 0, 0, 6, 17, 4, 0, 6, 2, 19, 0, 1, 12, 15, 6, 7, 14, 13 },
/* 216: 11011000 */ { 10, 13, 15, 17, 4, 8, 17, 10, 4, 6, 10, 17, 13, 6, 17, 10, 6, 7, 10, 13, 13, 15, 7, 10, 7, 10, 15, 19, 3, 7, 15, 19 },
/* 217: 11011001 */ { 16, 10, 4, 11, 16, 10, 17, 4, 10, 15, 7, 19, 10, 15, 13, 7, 10, 13, 17, 6, 3, 7, 15, 19, 0, 4, 11, 16, 6, 10, 4, 17, 6, 10, 13, 7 },
/* 218: 11011010 */ { 16, 13, 1, 12, 16, 13, 19, 3, 8, 13, 17, 4, 8, 13, 6, 10, 10, 19, 13, 7, 8, 6, 13, 4, 13, 16, 1, 3, 3, 7, 13, 19, 6, 7, 10, 13 },
/* 219: 11011011 */ { 10, 11, 7, 19, 13, 12, 0, 17, 11, 19, 3, 7, 0, 13, 17, 4, 11, 7, 6, 10, 0, 12, 13, 1, 11, 3, 1, 7, 0, 4, 6, 13, 1, 6, 13, 0, 1, 6, 11, 7, 1, 6, 7, 13, 1, 6, 0, 11 },
/* 220: 11011100 */ { 17, 11, 6, 8, 17, 13, 6, 11, 13, 15, 3, 11, 4, 6, 8, 17, 3, 2, 13, 11, 2, 11, 6, 13, 3, 2, 6, 13, 3, 7, 13, 6 },
/* 221: 11011101 */ { 15, 13, 17, 6, 16, 15, 17, 2, 15, 17, 2, 6, 2, 6, 3, 15, 6, 3, 15, 7, 6, 7, 15, 13, 2, 6, 17, 4, 2, 0, 4, 17, 2, 0, 17, 16 },
/* 222: 11011110 */ { 16, 13, 3, 12, 16, 13, 11, 3, 8, 13, 17, 6, 8, 13, 6, 11, 11, 13, 6, 3, 16, 12, 3, 1, 8, 6, 17, 4, 3, 6, 7, 13, 11, 2, 3, 6 },
/* 223: 11011111 */ { 17, 13, 6, 12, 17, 6, 4, 0, 17, 12, 6, 0, 6, 7, 3, 13, 3, 6, 13, 12, 2, 3, 12, 6, 2, 0, 6, 12, 3, 0, 12, 1, 2, 3, 0, 12 },
/* 224: 11100000 */ { 9, 12, 17, 7, 9, 12, 7, 10, 10, 12, 7, 14, 5, 12, 7, 17, 9, 6, 10, 7 },
/* 225: 11100001 */ { 0, 8, 11, 16, 14, 12, 10, 7, 12, 10, 7, 17, 10, 17, 9, 7, 9, 10, 7, 6, 5, 7, 17, 12 },
/* 226: 11100010 */ { 16, 9, 5, 17, 16, 9, 14, 5, 16, 14, 15, 5, 9, 14, 6, 10, 16, 1, 5, 15, 9, 14, 5, 6, 5, 6, 14, 7 },
/* 227: 11100011 */ { 11, 17, 1, 8, 11, 17, 15, 1, 17, 15, 5, 14, 9, 10, 17, 7, 17, 10, 14, 7, 17, 15, 1, 5, 17, 14, 5, 7, 0, 8, 11, 1, 9, 10, 7, 6 },
/* 228: 11100100 */ { 12, 14, 5, 17, 7, 14, 17, 5, 7, 14, 6, 17, 11, 14, 17, 6, 9, 6, 11, 17, 2, 11, 14, 19, 2, 14, 11, 6 },
/* 229: 11100101 */ { 9, 16, 2, 8, 9, 16, 19, 2, 9, 12, 17, 7, 9, 12, 7, 14, 8, 2, 0, 16, 12, 17, 7, 5, 9, 14, 6, 19, 9, 19, 6, 2, 9, 14, 7, 6 },
/* 230: 11100110 */ { 16, 14, 15, 1, 16, 14, 1, 17, 11, 19, 14, 2, 11, 14, 9, 2, 14, 9, 7, 17, 5, 14, 17, 1, 5, 14, 7, 17, 9, 14, 6, 2, 9, 14, 7, 6 },
/* 231: 11100111 */ { 15, 19, 14, 0, 8, 9, 7, 17, 0, 14, 15, 1, 8, 17, 7, 5, 0, 14, 2, 19, 8, 7, 9, 6, 0, 14, 6, 2, 6, 7, 14, 8, 0, 6, 14, 8, 8, 7, 14, 5, 0, 8, 14, 1, 8, 14, 1, 5 },
/* 232: 11101000 */ { 6, 7, 10, 9, 17, 7, 9, 10, 17, 7, 10, 19, 3, 7, 15, 19, 12, 7, 19, 15, 12, 7, 17, 19, 12, 7, 5, 17 },
/* 233: 11101001 */ { 0, 11, 16, 8, 12, 17, 15, 7, 17, 15, 7, 19, 19, 17, 9, 7, 9, 19, 7, 10, 17, 12, 5, 7, 15, 7, 19, 3, 9, 10, 7, 6 },
/* 234: 11101010 */ { 19, 16, 17, 1, 9, 19, 7, 10, 9, 19, 17, 7, 9, 10, 7, 6, 17, 19, 1, 7, 1, 7, 5, 17, 1, 7, 19, 3 },
/* 235: 11101011 */ { 11, 17, 1, 8, 11, 17, 19, 1, 10, 17, 9, 7, 10, 17, 7, 19, 17, 19, 1, 7, 1, 7, 5, 17, 1, 7, 19, 3, 0, 8, 11, 1, 9, 10, 7, 6 },
/* 236: 11101100 */ { 9, 11, 15, 2, 9, 12, 17, 7, 9, 12, 7, 15, 9, 15, 7, 2, 2, 7, 3, 15, 2, 7, 9, 6, 12, 17, 7, 5 },
/* 237: 11101101 */ { 9, 16, 2, 8, 9, 16, 15, 2, 9, 12, 17, 7, 9, 12, 7, 15, 9, 15, 7, 2, 2, 7, 3, 15, 2, 7, 9, 6, 5, 12, 7, 17, 0, 8, 2, 16 },
/* 238: 11101110 */ { 9, 16, 3, 11, 9, 16, 17, 3, 16, 17, 3, 1, 9, 11, 3, 2, 17, 5, 3, 1, 9, 2, 3, 6, 9, 3, 7, 6, 9, 3, 17, 7, 5, 17, 3, 7 },
/* 239: 11101111 */ { 8, 9, 3, 17, 8, 17, 3, 1, 17, 9, 3, 7, 9, 8, 3, 2, 17, 3, 1, 5, 17, 3, 5, 7, 0, 3, 1, 8, 0, 3, 8, 2, 9, 3, 6, 2, 9, 3, 7, 6 },
/* 240: 11110000 */ { 8, 12, 4, 10, 12, 14, 7, 10, 4, 7, 10, 12, 4, 5, 7, 12, 4, 6, 10, 7 },
/* 241: 11110001 */ { 16, 10, 4, 11, 16, 12, 4, 10, 12, 14, 7, 10, 0, 4, 11, 16, 7, 6, 12, 10, 6, 10, 4, 12, 7, 6, 4, 12, 7, 5, 12, 4 },
/* 242: 11110010 */ { 8, 15, 16, 5, 8, 15, 5, 14, 8, 14, 6, 10, 8, 14, 5, 6, 1, 5, 16, 15, 5, 6, 4, 8, 5, 6, 14, 7 },
/* 243: 11110011 */ { 4, 10, 11, 15, 4, 10, 15, 14, 4, 0, 15, 11, 4, 15, 5, 14, 4, 6, 10, 14, 4, 14, 7, 6, 4, 15, 0, 1, 4, 15, 1, 5, 4, 14, 5, 7 },
/* 244: 11110100 */ { 19, 14, 11, 6, 14, 11, 6, 8, 8, 12, 5, 14, 8, 14, 5, 6, 11, 19, 6, 2, 8, 4, 6, 5, 14, 7, 5, 6 },
/* 245: 11110101 */ { 16, 14, 6, 19, 16, 14, 12, 6, 2, 19, 16, 6, 16, 6, 0, 2, 0, 16, 4, 6, 16, 6, 12, 4, 12, 6, 5, 4, 12, 6, 14, 7, 12, 6, 7, 5 },
/* 246: 11110110 */ { 8, 15, 5, 14, 8, 15, 16, 5, 8, 19, 6, 11, 8, 19, 14, 6, 15, 16, 5, 1, 8, 14, 5, 6, 11, 6, 2, 19, 14, 7, 5, 6, 5, 6, 4, 8 },
/* 247: 11110111 */ { 14, 15, 19, 4, 15, 19, 4, 0, 15, 14, 5, 4, 19, 14, 4, 6, 4, 15, 1, 5, 4, 15, 0, 1, 4, 14, 5, 7, 4, 14, 7, 6, 4, 19, 2, 0, 4, 19, 6, 2 },
/* 248: 11111000 */ { 19, 12, 7, 15, 19, 10, 7, 12, 10, 8, 4, 12, 3, 7, 15, 19, 4, 5, 10, 12, 5, 12, 7, 10, 4, 5, 7, 10, 4, 6, 10, 7 },
/* 249: 11111001 */ { 11, 12, 16, 4, 11, 12, 4, 10, 19, 12, 7, 15, 19, 12, 10, 7, 15, 19, 3, 7, 0, 4, 11, 16, 10, 12, 4, 7, 4, 7, 12, 5, 4, 7, 6, 10 },
/* 250: 11111010 */ { 8, 19, 16, 5, 8, 19, 5, 10, 8, 4, 10, 5, 16, 1, 5, 19, 5, 10, 19, 7, 19, 5, 3, 1, 19, 5, 7, 3, 10, 5, 4, 6, 10, 5, 6, 7 },
/* 251: 11111011 */ { 19, 11, 10, 1, 19, 1, 7, 3, 19, 10, 7, 1, 1, 0, 11, 4, 4, 1, 10, 11, 5, 4, 1, 10, 5, 7, 10, 1, 4, 7, 6, 10, 5, 4, 10, 7 },
/* 252: 11111100 */ { 11, 15, 12, 7, 6, 7, 2, 11, 7, 2, 11, 3, 7, 3, 11, 15, 8, 11, 7, 6, 4, 8, 7, 6, 8, 11, 12, 7, 8, 12, 5, 7, 8, 4, 7, 5 },
/* 253: 11111101 */ { 16, 15, 12, 2, 2, 3, 15, 7, 7, 2, 12, 15, 6, 7, 2, 12, 7, 4, 5, 12, 6, 7, 12, 4, 0, 6, 2, 16, 2, 16, 6, 12, 4, 12, 6, 16, 0, 16, 4, 6 },
/* 254: 11111110 */ { 8, 11, 16, 7, 8, 11, 7, 6, 11, 16, 7, 3, 8, 16, 5, 7, 16, 7, 1, 5, 16, 7, 3, 1, 8, 5, 4, 7, 8, 6, 7, 4, 11, 2, 3, 7, 11, 2, 7, 6 },
/* 255: 11111111 */ { 0, 3, 1, 7, 0, 5, 7, 1, 0, 5, 4, 7, 0, 3, 7, 2, 0, 6, 2, 7, 0, 6, 7, 4 },
};

std::vector<std::vector<std::uint8_t>> extraTetrahedra = 
{
/*   0: 00000000 */ { },
/*   1: 00000001 */ { },
/*   2: 00000010 */ { },
/*   3: 00000011 */ { },
/*   4: 00000100 */ { },
/*   5: 00000101 */ { },
/*   6: 00000110 */ { 10, 11, 12, 19, 11, 12, 19, 15, 11, 12, 15, 16 },
/*   7: 00000111 */ { },
/*   8: 00001000 */ { },
/*   9: 00001001 */ { 8, 14, 19, 15, 8, 11, 16, 19, 8, 16, 15, 19 },
/*  10: 00001010 */ { },
/*  11: 00001011 */ { },
/*  12: 00001100 */ { },
/*  13: 00001101 */ { },
/*  14: 00001110 */ { },
/*  15: 00001111 */ { },
/*  16: 00010000 */ { },
/*  17: 00010001 */ { },
/*  18: 00010010 */ { 9, 12, 15, 16, 8, 9, 16, 12, 8, 9, 12, 17 },
/*  19: 00010011 */ { },
/*  20: 00010100 */ { 8, 10, 11, 17, 8, 9, 10, 17, 10, 11, 17, 19 },
/*  21: 00010101 */ { },
/*  22: 00010110 */ { 9, 19, 10, 11, 16, 17, 15, 12, 15, 19, 17, 16, 8, 9, 11, 19, 8, 19, 17, 9, 8, 16, 19, 11, 8, 16, 17, 19 },
/*  23: 00010111 */ { },
/*  24: 00011000 */ { },
/*  25: 00011001 */ { 9, 16, 17, 14, 9, 11, 16, 14, 11, 16, 14, 15, 11, 14, 19, 15 },
/*  26: 00011010 */ { 14, 16, 19, 9, 9, 16, 12, 14, 8, 16, 12, 9, 8, 9, 12, 17 },
/*  27: 00011011 */ { },
/*  28: 00011100 */ { 10, 15, 17, 14, 10, 11, 17, 15, 9, 10, 11, 17, 8, 9, 11, 17 },
/*  29: 00011101 */ { },
/*  30: 00011110 */ { 8, 10, 11, 12, 8, 12, 11, 16, 8, 10, 17, 9, 8, 10, 12, 17 },
/*  31: 00011111 */ { },
/*  32: 00100000 */ { },
/*  33: 00100001 */ { 8, 11, 16, 13, 12, 13, 17, 16, 13, 17, 16, 8 },
/*  34: 00100010 */ { },
/*  35: 00100011 */ { },
/*  36: 00100100 */ { },
/*  37: 00100101 */ { 8, 10, 19, 13, 8, 16, 13, 19, 8, 16, 12, 13, 8, 13, 12, 17 },
/*  38: 00100110 */ { 17, 10, 15, 13, 17, 10, 16, 15, 10, 11, 15, 19, 10, 11, 16, 15 },
/*  39: 00100111 */ { },
/*  40: 00101000 */ { 14, 15, 19, 17, 13, 15, 14, 17, 13, 15, 17, 12 },
/*  41: 00101001 */ { 11, 14, 19, 15, 11, 14, 15, 8, 8, 11, 16, 15, 8, 12, 13, 14, 8, 12, 14, 15, 8, 12, 15, 16, 8, 12, 17, 13 },
/*  42: 00101010 */ { },
/*  43: 00101011 */ { },
/*  44: 00101100 */ { 17, 10, 11, 15, 17, 10, 15, 14, 17, 14, 15, 13, 17, 13, 15, 12 },
/*  45: 00101101 */ { 16, 12, 14, 15, 8, 12, 13, 14, 8, 12, 14, 16, 8, 12, 17, 13 },
/*  46: 00101110 */ { },
/*  47: 00101111 */ { },
/*  48: 00110000 */ { },
/*  49: 00110001 */ { },
/*  50: 00110010 */ { },
/*  51: 00110011 */ { },
/*  52: 00110100 */ { 8, 12, 13, 19, 8, 19, 13, 9, 8, 19, 9, 11, 9, 11, 19, 10 },
/*  53: 00110101 */ { },
/*  54: 00110110 */ { 11, 19, 15, 10, 9, 10, 11, 15, 9, 11, 16, 15, 9, 11, 8, 16 },
/*  55: 00110111 */ { },
/*  56: 00111000 */ { 8, 9, 19, 13, 8, 12, 13, 19, 19, 15, 13, 14, 12, 13, 19, 15 },
/*  57: 00111001 */ { 11, 12, 15, 16, 13, 14, 19, 15, 13, 15, 19, 11, 11, 12, 13, 15 },
/*  58: 00111010 */ { },
/*  59: 00111011 */ { },
/*  60: 00111100 */ { 8, 9, 10, 13, 8, 10, 11, 14, 8, 11, 12, 14, 12, 14, 11, 15, 8, 10, 14, 13, 8, 12, 13, 14 },
/*  61: 00111101 */ { 16, 9, 10, 14, 16, 9, 14, 13, 16, 15, 12, 14, 16, 13, 14, 12 },
/*  62: 00111110 */ { 16, 9, 14, 13, 16, 10, 14, 9, 16, 11, 10, 8, 8, 16, 9, 10 },
/*  63: 00111111 */ { },
/*  64: 01000000 */ { },
/*  65: 01000001 */ { 9, 10, 16, 18, 10, 11, 8, 16, 8, 10, 16, 9 },
/*  66: 01000010 */ { },
/*  67: 01000011 */ { 11, 15, 12, 18, 8, 11, 12, 18, 9, 10, 11, 18, 8, 9, 11, 18 },
/*  68: 01000100 */ { },
/*  69: 01000101 */ { },
/*  70: 01000110 */ { 9, 11, 12, 18, 11, 18, 19, 12, 11, 19, 15, 12, 11, 15, 16, 12 },
/*  71: 01000111 */ { },
/*  72: 01001000 */ { 14, 15, 19, 9, 14, 18, 9, 19, 10, 18, 19, 9 },
/*  73: 01001001 */ { 15, 11, 9, 16, 9, 10, 11, 18, 9, 11, 15, 18, 14, 15, 19, 18, 18, 15, 19, 11, 10, 11, 18, 19, 8, 11, 16, 9 },
/*  74: 01001010 */ { 14, 16, 9, 12, 14, 16, 19, 9, 9, 10, 19, 18, 9, 14, 18, 19 },
/*  75: 01001011 */ { 8, 10, 11, 19, 8, 10, 19, 14, 8, 10, 14, 9, 10, 14, 9, 18 },
/*  76: 01001100 */ { },
/*  77: 01001101 */ { },
/*  78: 01001110 */ { },
/*  79: 01001111 */ { },
/*  80: 01010000 */ { },
/*  81: 01010001 */ { },
/*  82: 01010010 */ { 10, 17, 18, 15, 8, 10, 15, 17, 8, 12, 17, 15, 8, 12, 15, 16 },
/*  83: 01010011 */ { },
/*  84: 01010100 */ { },
/*  85: 01010101 */ { },
/*  86: 01010110 */ { 8, 11, 16, 19, 8, 17, 19, 16, 15, 16, 19, 17, 16, 17, 15, 12 },
/*  87: 01010111 */ { },
/*  88: 01011000 */ { 8, 17, 10, 15, 15, 17, 10, 18, 15, 10, 19, 18, 18, 19, 15, 14 },
/*  89: 01011001 */ { 11, 10, 19, 18, 11, 18, 19, 16, 16, 18, 19, 14, 16, 19, 15, 14 },
/*  90: 01011010 */ { 18, 19, 12, 14, 10, 12, 18, 19, 10, 12, 19, 16, 10, 12, 17, 18, 8, 10, 16, 12, 8, 10, 12, 17 },
/*  91: 01011011 */ { 17, 18, 11, 12, 18, 11, 12, 14, 11, 18, 10, 14, 11, 19, 14, 10 },
/*  92: 01011100 */ { },
/*  93: 01011101 */ { },
/*  94: 01011110 */ { 11, 18, 14, 12, 11, 17, 18, 12, 11, 16, 8, 17, 11, 16, 17, 12 },
/*  95: 01011111 */ { },
/*  96: 01100000 */ { 12, 13, 17, 10, 9, 10, 17, 13, 9, 10, 13, 18 },
/*  97: 01100001 */ { 9, 11, 18, 10, 12, 13, 17, 16, 11, 9, 18, 13, 8, 9, 11, 16, 9, 11, 16, 13, 9, 13, 16, 17, 8, 16, 17, 9 },
/*  98: 01100010 */ { 10, 15, 16, 17, 10, 15, 17, 13, 9, 10, 17, 13, 9, 10, 13, 18 },
/*  99: 01100011 */ { 9, 10, 11, 18, 9, 11, 13, 18, 9, 11, 8, 13, 9, 17, 13, 8 },
/* 100: 01100100 */ { 18, 19, 11, 12, 18, 9, 12, 11, 9, 12, 13, 18, 9, 12, 17, 13 },
/* 101: 01100101 */ { 8, 16, 17, 9, 17, 18, 12, 13, 16, 17, 9, 18, 16, 17, 18, 12 },
/* 102: 01100110 */ { 16, 17, 9, 13, 16, 18, 9, 11, 16, 18, 15, 13, 9, 13, 18, 16, 11, 15, 16, 18, 11, 15, 18, 19 },
/* 103: 01100111 */ { 8, 15, 13, 19, 8, 18, 19, 13, 8, 9, 13, 17, 9, 8, 13, 18 },
/* 104: 01101000 */ { 12, 14, 19, 15, 9, 10, 17, 18, 13, 14, 18, 17, 12, 13, 17, 14, 17, 19, 12, 14, 17, 18, 19, 14, 17, 18, 10, 19 },
/* 105: 01101001 */ { 9, 18, 10, 11, 10, 11, 18, 19, 14, 15, 19, 18, 18, 13, 14, 15, 11, 18, 19, 15, 8, 9, 11, 17, 9, 11, 17, 18, 11, 15, 17, 18, 15, 17, 18, 13, 8, 11, 16, 17, 13, 17, 12, 15, 15, 16, 11, 17, 15, 16, 17, 12 },
/* 106: 01101010 */ { 18, 19, 13, 14, 17, 18, 10, 19, 17, 18, 19, 13, 17, 18, 9, 10, },
/* 107: 01101011 */ { 8, 10, 11, 19, 8, 10, 19, 14, 8, 10, 14, 18, 8, 14, 17, 18, 8, 9, 10, 18, 8, 9, 18, 17, 17, 18, 14, 13 },
/* 108: 01101100 */ { 9, 13, 18, 14, 9, 13, 14, 15, 9, 13, 15, 17, 17, 13, 15, 12 },
/* 109: 01101101 */ { 9, 14, 13, 18, 9, 13, 14, 15, 9, 13, 15, 17, 17, 13, 15, 12, 8, 9, 15, 17, 8, 15, 12, 17, 8, 15, 16, 12 },
/* 110: 01101110 */ { 9, 11, 16, 14, 9, 17, 14, 16, 17, 9, 14, 13, 9, 13, 18, 14 },
/* 111: 01101111 */ { 8, 18, 14, 13, 8, 9, 13, 17, 8, 9, 18, 13 },
/* 112: 01110000 */ { },
/* 113: 01110001 */ { },
/* 114: 01110010 */ { },
/* 115: 01110011 */ { },
/* 116: 01110100 */ { },
/* 117: 01110101 */ { },
/* 118: 01110110 */ { 8, 18, 19, 13, 8, 13, 19, 15, 8, 15, 19, 16, 8, 16, 19, 11 },
/* 119: 01110111 */ { },
/* 120: 01111000 */ { 10, 14, 19, 15, 10, 14, 12, 18, 10, 12, 14, 15, 12, 13, 18, 14 },
/* 121: 01111001 */ { 10, 14, 13, 18, 11, 12, 15, 16, 11, 13, 15, 12, 11, 15, 13, 19, 14, 15, 19, 13, 10, 11, 13, 19, 19, 13, 10, 14 },
/* 122: 01111010 */ { 8, 16, 13, 19, 8, 10, 19, 13, 10, 13, 18, 14, 10, 13, 14, 19 },
/* 123: 01111011 */ { 11, 13, 18, 14, 11, 10, 19, 14, 11, 10, 14, 18, },
/* 124: 01111100 */ { 8, 11, 12, 18, 12, 15, 18, 11, 13, 14, 18, 15, 13, 12, 15, 18 },
/* 125: 01111101 */ { 16, 18, 15, 12, 13, 14, 18, 15, 13, 12, 15, 18 },
/* 126: 01111110 */ { },
/* 127: 01111111 */ { },
/* 128: 10000000 */ { },
/* 129: 10000001 */ { },
/* 130: 10000010 */ { },
/* 131: 10000011 */ { },
/* 132: 10000100 */ { },
/* 133: 10000101 */ { },
/* 134: 10000110 */ { },
/* 135: 10000111 */ { },
/* 136: 10001000 */ { },
/* 137: 10001001 */ { },
/* 138: 10001010 */ { },
/* 139: 10001011 */ { },
/* 140: 10001100 */ { },
/* 141: 10001101 */ { },
/* 142: 10001110 */ { },
/* 143: 10001111 */ { },
/* 144: 10010000 */ { },
/* 145: 10010001 */ { },
/* 146: 10010010 */ { },
/* 147: 10010011 */ { },
/* 148: 10010100 */ { },
/* 149: 10010101 */ { },
/* 150: 10010110 */ { },
/* 151: 10010111 */ { },
/* 152: 10011000 */ { },
/* 153: 10011001 */ { },
/* 154: 10011010 */ { },
/* 155: 10011011 */ { },
/* 156: 10011100 */ { },
/* 157: 10011101 */ { },
/* 158: 10011110 */ { },
/* 159: 10011111 */ { },
/* 160: 10100000 */ { },
/* 161: 10100001 */ { },
/* 162: 10100010 */ { },
/* 163: 10100011 */ { },
/* 164: 10100100 */ { },
/* 165: 10100101 */ { },
/* 166: 10100110 */ { },
/* 167: 10100111 */ { },
/* 168: 10101000 */ { },
/* 169: 10101001 */ { },
/* 170: 10101010 */ { },
/* 171: 10101011 */ { },
/* 172: 10101100 */ { },
/* 173: 10101101 */ { },
/* 174: 10101110 */ { },
/* 175: 10101111 */ { },
/* 176: 10110000 */ { },
/* 177: 10110001 */ { },
/* 178: 10110010 */ { },
/* 179: 10110011 */ { },
/* 180: 10110100 */ { },
/* 181: 10110101 */ { },
/* 182: 10110110 */ { },
/* 183: 10110111 */ { },
/* 184: 10111000 */ { },
/* 185: 10111001 */ { },
/* 186: 10111010 */ { },
/* 187: 10111011 */ { },
/* 188: 10111100 */ { },
/* 189: 10111101 */ { },
/* 190: 10111110 */ { },
/* 191: 10111111 */ { },
/* 192: 11000000 */ { },
/* 193: 11000001 */ { },
/* 194: 11000010 */ { },
/* 195: 11000011 */ { },
/* 196: 11000100 */ { },
/* 197: 11000101 */ { },
/* 198: 11000110 */ { },
/* 199: 11000111 */ { },
/* 200: 11001000 */ { },
/* 201: 11001001 */ { },
/* 202: 11001010 */ { },
/* 203: 11001011 */ { },
/* 204: 11001100 */ { },
/* 205: 11001101 */ { },
/* 206: 11001110 */ { },
/* 207: 11001111 */ { },
/* 208: 11010000 */ { },
/* 209: 11010001 */ { },
/* 210: 11010010 */ { },
/* 211: 11010011 */ { },
/* 212: 11010100 */ { },
/* 213: 11010101 */ { },
/* 214: 11010110 */ { },
/* 215: 11010111 */ { },
/* 216: 11011000 */ { },
/* 217: 11011001 */ { },
/* 218: 11011010 */ { },
/* 219: 11011011 */ { },
/* 220: 11011100 */ { },
/* 221: 11011101 */ { },
/* 222: 11011110 */ { },
/* 223: 11011111 */ { },
/* 224: 11100000 */ { },
/* 225: 11100001 */ { },
/* 226: 11100010 */ { },
/* 227: 11100011 */ { },
/* 228: 11100100 */ { },
/* 229: 11100101 */ { },
/* 230: 11100110 */ { },
/* 231: 11100111 */ { },
/* 232: 11101000 */ { },
/* 233: 11101001 */ { },
/* 234: 11101010 */ { },
/* 235: 11101011 */ { },
/* 236: 11101100 */ { },
/* 237: 11101101 */ { },
/* 238: 11101110 */ { },
/* 239: 11101111 */ { },
/* 240: 11110000 */ { },
/* 241: 11110001 */ { },
/* 242: 11110010 */ { },
/* 243: 11110011 */ { },
/* 244: 11110100 */ { },
/* 245: 11110101 */ { },
/* 246: 11110110 */ { },
/* 247: 11110111 */ { },
/* 248: 11111000 */ { },
/* 249: 11111001 */ { },
/* 250: 11111010 */ { },
/* 251: 11111011 */ { },
/* 252: 11111100 */ { },
/* 253: 11111101 */ { },
/* 254: 11111110 */ { },
/* 255: 11111111 */ { }
};

} // namespace marching

} // mlhp
