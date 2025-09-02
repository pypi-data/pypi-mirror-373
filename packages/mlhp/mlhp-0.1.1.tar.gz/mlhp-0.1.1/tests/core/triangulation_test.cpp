// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/triangulation.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/refinement.hpp"
#include "mlhp/core/postprocessing.hpp"
#include "mlhp/core/quadrature.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/integrands.hpp"

#include <map>

namespace mlhp
{

using namespace marching;

TEST_CASE( "readStl_test" )
{
    auto expected = std::vector<std::array<double, 3>>
    {
       // Triangle 0
       { 0.552139, -0.1804, -0.642338 },
       { 0.0417709, -0.857681, -0.112419 },
       { -0.275457, 0.373881, -0.730983 },

       // Triangle 1
       { -0.785825, -0.303401, -0.201064 },
       { -0.275457, 0.373881, -0.730983 },
       { 0.0417709, -0.857681, -0.112419 },

       // Triangle 2
       { -0.552139, 0.1804, 0.642338 },
       { 0.275457, -0.373881, 0.730983 },
       { -0.0417709, 0.857681, 0.112419 },

       // Triangle 3
       { 0.785825, 0.303401, 0.201064 },
       { -0.0417709, 0.857681, 0.112419 },
       { 0.275457, -0.373881, 0.730983 },

       // Triangle 4
       { 0.552139, -0.1804, -0.642338 },
       { -0.275457, 0.373881, -0.730983 },
       { 0.785825, 0.303401, 0.201064 },

       // Triangle 5
       { -0.0417709, 0.857681, 0.112419 },
       { 0.785825, 0.303401, 0.201064 },
       { -0.275457, 0.373881, -0.730983 },

       // Triangle 6
       { -0.552139, 0.1804, 0.642338 },
       { -0.785825, -0.303401, -0.201064 },
       { 0.275457, -0.373881, 0.730983 },

       // Triangle 7
       { 0.0417709, -0.857681, -0.112419 },
       { 0.275457, -0.373881, 0.730983 },
       { -0.785825, -0.303401, -0.201064 },

       // Triangle 8
       { -0.552139, 0.1804, 0.642338 },
       { -0.0417709, 0.857681, 0.112419 },
       { -0.785825, -0.303401, -0.201064 },

       // Triangle 9
       { -0.275457, 0.373881, -0.730983 },
       { -0.785825, -0.303401, -0.201064 },
       { -0.0417709, 0.857681, 0.112419 },

       // Triangle 10
       { 0.552139, -0.1804, -0.642338 },
       { 0.785825, 0.303401, 0.201064 },
       { 0.0417709, -0.857681, -0.112419 },

       // Triangle 11
       { 0.275457, -0.373881, 0.730983 },
       { 0.0417709, -0.857681, -0.112419 },
       { 0.785825, 0.303401, 0.201064 }
    };

    auto stlWritePath = testing::outputPath( "core/readStl_test.stl" );
    auto stlReadPath = testing::testfilePath( "core/readStl_test.stl" );

    writeStl( createTriangulation<3>( expected ), stlWritePath );

    auto triangles1 = readStl( stlReadPath, false );
    auto triangles2 = readStl( stlWritePath, true );

    REQUIRE( triangles1.size( ) == expected.size( ) );
    REQUIRE( triangles2.size( ) == expected.size( ) );

    for( size_t i = 0; i < expected.size( ); ++i )
    {
        CHECK( spatial::distance( triangles1[i], expected[i] ) < 1e-10 );
        CHECK( spatial::distance( triangles2[i], expected[i] ) < 1e-10 );
    }
}

TEST_CASE( "Triangulation_area3D_test" )
{
    auto t = Triangulation<3> { };

    t.vertices =
    {
        { 9.14, 4.44, 4.57 }, { 1.1 , 5.35, 7.79 }, { 7.88, 8.06, 2.04 },
        { 4.2 , 3.56, 5.07 }, { 7.67, 3.42, 2.58 }, { 3.23, 2.49, 4.21 },
        { 9.42, 9.36, 1.33 }, { 4.78, 8.98, 9.22 }, { 7.73, 0.54, 7.07 },
        { 1.62, 4.24, 0.11 }, { 6.53, 8.13, 7.5  }, { 7.94, 9.57, 3.12 },
        { 9.72, 1.79, 3.89 }, { 7.4 , 7.98, 8.43 }, { 4.03, 1.88, 3.92 }
    };

    t.cells= 
    {
        { 0, 1, 2 }, { 3, 4, 5 }, { 6, 7, 8 }, { 9, 10, 11 }, { 12, 13, 14 }
    };

    CHECK( t.area( ) == Approx( 106.07389660287483 ).epsilon( 1e-10 ) );
}

TEST_CASE( "Triangulation_area2D_test" )
{
    auto t = Triangulation<2> { };

    t.vertices =
    {
       { 0.88, 0.58 }, { 0.65, 0.45 }, { 0.91, 0.31 },
       { 0.25, 0.34 }, { 0.7 , 0.51 }, { 0.28, 0.08 },
       { 0.67, 0.57 }, { 0.91, 0.14 }, { 0.17, 0.49 },
       { 0.69, 0.62 }, { 0.48, 0.79 }, { 0.68, 0.08 },
    };

    t.cells= 
    {
        { 0, 1, 2 }, { 3, 4, 5 }, { 6, 7, 8 }, { 9, 10, 11 }
    };

    CHECK( t.area( ) == Approx( 0.2687 ).epsilon( 1e-10 ) );
}

TEST_CASE( "mergeTriangulations_test" )
{
    auto t1 = Triangulation<2> { };
    auto t2 = Triangulation<2> { };
    auto t3 = Triangulation<2> { };

    t1.vertices =
    {
       { 0.0, -1.0 }, { 0.0, 0.0 }, { 1.0, 0.0 },
    };

    t1.cells= 
    {
        { 0, 1, 2 }
    };

    t2.vertices =
    {
       { 0.0, 0.0 }, { 0.0, 1.0 }, { 0.0, 2.0 },
       { 1.0, 0.0 }, { 1.0, 1.0 }, { 1.0, 2.0 },
    };

    t2.cells= 
    {
        { 0, 1, 3 }, { 1, 3, 4 }, { 1, 2, 4 }, { 2, 4, 5 }
    };

    t3.vertices =
    {
       { 1.0, 0.0 }, { 1.0, 1.0 }, { 1.0, 2.0 },
       { 1.0, 2.0 }
    };

    t3.cells= 
    {
        { 0, 1, 3 }, { 1, 2, 3 }
    };

    auto t = mergeSimplexMeshes<2, 2>( { t1, t2, t3 } );

    auto expectedVertices = t1.vertices;

    expectedVertices.insert( expectedVertices.end( ), t2.vertices.begin( ), t2.vertices.end( ) );
    expectedVertices.insert( expectedVertices.end( ), t3.vertices.begin( ), t3.vertices.end( ) );

    auto expectedTriangles = std::vector<std::array<size_t, 3>>
    {
       { 0, 1, 2 },
       { 3, 4, 6 }, { 4, 6, 7 }, { 4, 5, 7 }, { 5, 7, 8 },
       { 9, 10, 12 }, { 10, 11, 12 }
    };

    CHECK( t.vertices == expectedVertices );
    CHECK( t.cells== expectedTriangles );
}

//TEST_CASE( "MarchingCubes_test" )
//{
//    // Build Wikipedia CSG geometry example
//    auto sphere = implicit::sphere<3>( { 0.0, 0.0, 0.0 }, 1.0 );
//    auto cube = implicit::cube<3>( { -0.85, -0.85, -0.85 }, { 0.85, 0.85, 0.85 } );
//    auto intersection = implicit::intersect( sphere, cube );
//
//    auto circle = implicit::sphere<2>( { 0, 0 }, 0.4 );
//
//    auto cylinder1 = implicit::extrude( circle, -1.0, 1.0, 0 );
//    auto cylinder2 = implicit::extrude( circle, -1.0, 1.0, 1 );
//    auto cylinder3 = implicit::extrude( circle, -1.0, 1.0, 2 );
//
//    auto cylinders = implicit::add( cylinder1, cylinder2, cylinder3 );
//
//    auto domain = implicit::subtract( intersection, cylinders );
//
//    // Triangulate
//    auto ncells = array::make<size_t, 3>( 20 );
//    auto lengths = array::make<double, 3>( 2.0 );
//    auto origin = array::make<double, 3>( -1.0 );
//
//    auto triangulation1 = marchingCubes( domain, ncells, lengths, origin );
//
//    CHECK( triangulation1.size( ) == 4660 * 9 );
//
//    // writeTriangles( triangulation1, "csg_standard.vtu" );
//
//    auto mesh = makeRefinedGrid<3>( { 4, 4, 4 }, lengths, origin );
//
//    mesh->refine( refineTowardsDomainBoundary( domain, 3 ) );
//
//    auto triangulation2 = marchingCubes( domain, *mesh, 2 );
//
//    CHECK( triangulation2.first.size( ) == 47152 * 9 );
//    CHECK( triangulation2.second.size( ) == 47152 );
//
//    // writeTriangles( triangulation2.first, "csg_mesh.vtu" );
//
//}

TEST_CASE( "intersectWithMesh_test1" )
{
    auto vertices = CoordinateList<3> { { 2.0, -3.0, 1.0 }, { 2.2, -3.1, 2.0 }, 
                                        { 2.0, -2.0, 1.0 }, { 2.2, -2.1, 2.0 },
                                        { 3.5, -3.0, 0.9 }, { 3.3, -3.1, 2.0 }, 
                                        { 3.5, -2.0, 0.9 }, { 3.3, -2.1, 2.0 },
                                        { 5.0, -3.0, 0.8 }, { 4.8, -3.1, 2.0 },
                                        { 5.0, -2.0, 0.8 }, { 4.8, -2.1, 2.0 } };

    auto cells = std::vector<size_t> { 0, 1, 2, 3, 4, 5, 6, 7, 4, 5, 6, 7, 8, 9, 10, 11 };
    auto offsets = std::vector<size_t> { 0, 8, 16 };

    auto mesh = UnstructuredMesh<3> { std::move( vertices ), std::move( cells ), std::move( offsets ) };

    auto triangulation = Triangulation<3>
    {  
        .vertices = { { 3.7, -2.9, -0.2 }, { 3.2, -2.6, 2.55 }, { 3.4, -2.1, 1.45 } },
        .cells= { { 0, 1, 2 } }
    };

    auto [intersected, celldata] = intersectWithMesh( triangulation, mesh, buildKdTree( triangulation ) );

    MLHP_CHECK( intersected.ncells( ) == 3, "" );

    //writeOutput( mesh, cellmesh::createGrid<3>( { 2, 2, 2 } ), CellProcessor<3> { }, VtuOutput { "mesh.vtu" } );
    //writeStl( triangulation, "triangle.stl" );
    //writeStl( intersected, "triangleIntersected.stl" );
}

TEST_CASE( "intersectWithMesh_test2" )
{
    auto triangulation = Triangulation<3>
    {
        .vertices = { { -1.8, -4.0, -0.2 }, { -1.8, -2.6, 2.55 }, { -1.8, -2.1, 1.45 } },
        .cells= { { 0, 1, 2 } }
    };

    // Unrefined
    auto mesh = makeRefinedGrid<3>( { 2, 1, 1 }, { 2.4, 1.8, 1.4 }, { -3.0, -4.0, 1.0 } );

    auto result = intersectWithMesh( triangulation, *mesh, buildKdTree( triangulation ) );

    auto area = 0.9687715311;
    auto intersected = std::get<0>( result );
    auto celldata = std::get<1>( result );

    CHECK( intersected.ncells( ) == 4 );
    CHECK( intersected.measure( ) == Approx( area ).epsilon( 1e-10 ) );

    // Right side refined
    mesh->refine( refineCellIndices<3>( { { 1 }, { 1, 3 } } ) );

    intersected = intersectWithMesh( triangulation, *mesh, buildKdTree( triangulation ) ).first;

    CHECK( intersected.ncells( ) == 4 );
    CHECK( intersected.measure( ) == Approx( area ).epsilon( 1e-10 ) );

    // Left side refined
    mesh = makeRefinedGrid<3>( { 2, 1, 1 }, { 2.4, 1.8, 1.4 }, { -3.0, -4.0, 1.0 } );

    mesh->refine( refineCellIndices<3>( { { 0 }, { 5, 7 } } ) );
    
    intersected = intersectWithMesh( triangulation, *mesh, buildKdTree( triangulation ) ).first;

    CHECK( intersected.ncells( ) == 4 );
    CHECK( intersected.measure( ) == Approx( area ).epsilon( 1e-10 ) );

    // Both sides refined and on same level
    mesh = makeRefinedGrid<3>( { 2, 1, 1 }, { 2.4, 1.8, 1.4 }, { -3.0, -4.0, 1.0 } );

    mesh->refine( refineCellIndices<3>( { { 0, 1 }, { 12, 14 } } ) );

    intersected = intersectWithMesh( triangulation, *mesh, buildKdTree( triangulation ) ).first;

    CHECK( intersected.ncells( ) == 8 );
    CHECK( intersected.measure( ) == Approx( area ).epsilon( 1e-10 ) );

    // Both sides refined once and some elements twice
    mesh = makeRefinedGrid<3>( { 2, 1, 1 }, { 2.4, 1.8, 1.4 }, { -3.0, -4.0, 1.0 } );

    mesh->refine( refineCellIndices<3>( { { 0, 1 }, { 5, 7, 8, 10 } } ) );

    intersected = intersectWithMesh( triangulation, *mesh, buildKdTree( triangulation ) ).first;

    CHECK( intersected.ncells( ) == 8 );
    CHECK( intersected.measure( ) == Approx( area ).epsilon( 1e-10 ) );

    //writeOutput( *mesh, cellmesh::createGrid<3>( { 1, 1, 1 } ), CellProcessor<3> { }, VtuOutput { "mesh.vtu" } );
    //writeStl( triangulation, "triangle.stl" );
    //writeStl( intersected, "triangleIntersected.stl" );
}

TEST_CASE( "intersectWithMesh_test" )
{ 
    /*                    
     *  10 ---   3__________4______________5
     *      |     \          \              \
     *      |      \     0    \      1       \
     *      |       \          \              \ 
     *  6  ---      6\_________7\_____________8\
     *      |        /          /              /
     *      |       /    2     /      3       /
     *      |      /          /              /
     *  2  ---   0/_________1/_____________2/
     *            
     *           |---|------|---|----------|---|
     *           1   2      5   6          11  12
     * 
     * Path starts bottom left and goes clockwise 
     * around until crossing from bottom to top:
     *                        End
     *                         |
     *            ____=========|=================
     *            \  /       \ |            \  /
     *             \/         \|             \/
     *             /\          |             /\ 
     *            /  \_________|\___________/__\
     *            \  /         |/          /   /
     *             \/          |          /   /
     *             /\         /|         /   /
     *            /__\_______/_|________/___/
     *                \        |    .
     *                 \       | .
     *               Start
     */

    auto meshVertices = std::vector
    {
        std::array { 1.0, 2.0 }, std::array { 5.0, 2.0 }, std::array { 11.0, 2.0 },
        std::array { 1.0, 10.0 }, std::array { 5.0, 10.0 }, std::array { 11.0, 10.0 },
        std::array { 2.0, 6.0 }, std::array { 6.0, 6.0 }, std::array { 12.0, 6.0 },
    };

    auto cells = std::vector<size_t>
    {
        3, 4, 6, 7,
        8, 7, 5, 4,
        0, 6, 1, 7,
        8, 2, 7, 1
    };

    auto offsets = std::vector<size_t>
    {
        0, 4, 8, 12, 16
    };

    auto mesh = UnstructuredMesh<2> { std::move( meshVertices ), std::move( cells ), std::move( offsets ) };

    auto vertices = std::vector
    {
        std::array {  3.0 , -2.0 }, // 0
        std::array {  1.75,  3.0 }, // 1
        std::array {  1.0 ,  6.0 }, // 2
        std::array {  2.0 , 10.0 }, // 3
        std::array { 12.0 , 10.0 }, // 4
        std::array { 10.0 ,  2.0 }, // 5
        std::array {  5.5 ,  0.0 }, // 6
        std::array {  5.5 , 90.0 }, // 7
        std::array { -9.0 , -2.0 }  // 8
    };

    auto segments = std::vector
    { 
        std::array<size_t, 2> { 0, 1 }, // 0
        std::array<size_t, 2> { 1, 2 }, // 1
        std::array<size_t, 2> { 2, 3 }, // 2
        std::array<size_t, 2> { 3, 4 }, // 3
        std::array<size_t, 2> { 4, 5 }, // 4
        std::array<size_t, 2> { 6, 7 }, // 5
        std::array<size_t, 2> { 7, 8 }  // 6
    };

    auto lineSegments = SimplexMesh<2, 1>
    {
        .vertices = vertices,
        .cells = segments
    };

    auto tree = buildKdTree<2>( lineSegments );

    //auto output = VtuOutput { testing::outputPath( "core/intersectWithMesh_mesh.vtu" ) };
    //writeOutput( mesh, cellmesh::createGrid<2>( { 1, 1 } ), CellProcessor<2> { }, output );
    //writeVtu( tree, testing::outputPath( "core/intersectWithMesh_kdtree.vtu" ) );

    auto [intersected, celldata] = intersectWithMesh( lineSegments, mesh, tree );

    REQUIRE( intersected.cells.size( ) == 11 );

    auto expectedXyz = std::vector
    {
        std::array { std::array { 1.5, 8.0 }, std::array { 2.0, 10.0 } },
        std::array { std::array { 2.0, 10.0 }, std::array { 5.0, 10.0 } },
        std::array { std::array { 5.5, 6.0 }, std::array { 5.5, 8.0 } },
        std::array { std::array { 5.0, 10.0 }, std::array { 11.0, 10.0 } },
        std::array { std::array { 11.5, 8.0 }, std::array { 11.0, 6.0 } },
        std::array { std::array { 5.5, 8.0 }, std::array { 5.5, 10.0 } },
        std::array { std::array { 2.0, 2.0 }, std::array {  1.75,  3.0 } },
        std::array { std::array {  1.75,  3.0 }, std::array { 1.5, 4.0 } },
        std::array { std::array { 5.5, 4.0 }, std::array { 5.5, 6.0 } },
        std::array { std::array { 11.0, 6.0 }, std::array { 10.0, 2.0 } },
        std::array { std::array { 5.5, 2.0 }, std::array { 5.5, 4.0 } }
    };

    auto expectedRst = std::vector
    {
        std::array { std::array { 0.0, -1.0 }, std::array { -1.0, -0.5 } },
        std::array { std::array { -1.0, -0.5 }, std::array { -1.0, 1.0 } },
        std::array { std::array { 1.0, 0.75 }, std::array { 0.0, 1.0 } },
        std::array { std::array { 1.0, 1.0 }, std::array { 1.0, -1.0 } },
        std::array { std::array { 0.0, -1.0 }, std::array { -1.0, -2.0 / 3.0 } },
        std::array { std::array { 0.0, 1.0 }, std::array { 1.0, 5.0 / 6.0 } },
        std::array { std::array { -0.5, -1.0 }, std::array { -0.75, -0.5 } },
        std::array { std::array { -0.75, -0.5 }, std::array { -1.0, 0.0 } },
        std::array { std::array { 1.0, 0.0 }, std::array { 0.75, 1.0 } },
        std::array { std::array { -2.0 / 3.0, -1.0 }, std::array { -2.0 / 3.0, 1.0 } },
        std::array { std::array { 5.0 / 6.0, 1.0 }, std::array { 1.0, 0.0 } }
    };

    auto expectedOffsets = std::vector<size_t> { 0, 3, 6, 9, 11 };

    for( size_t icell = 0; icell + 1 < expectedOffsets.size( ); ++icell )
    {
        auto begin = expectedOffsets[icell];
        auto end = expectedOffsets[icell + 1];

        REQUIRE( celldata.offsets[icell + 1] - celldata.offsets[icell] == end - begin );

        for( size_t isegment = 0; isegment < end - begin; ++isegment )
        {
            auto segmentIndex = celldata.offsets[icell] + isegment;
            auto [ipoint0, ipoint1] = intersected.cells[segmentIndex];

            auto computedXyz0 = intersected.vertices[ipoint0];
            auto computedXyz1 = intersected.vertices[ipoint1];
            auto computedRst0 = celldata.rst[ipoint0];
            auto computedRst1 = celldata.rst[ipoint1];

            CHECK( spatial::distance( computedXyz0, expectedXyz[begin + isegment][0] ) < 1e-10 );
            CHECK( spatial::distance( computedXyz1, expectedXyz[begin + isegment][1] ) < 1e-10 );
            CHECK( spatial::distance( computedRst0, expectedRst[begin + isegment][0] ) < 1e-10 );
            CHECK( spatial::distance( computedRst1, expectedRst[begin + isegment][1] ) < 1e-10 );
        }
    }
}


TEST_CASE( "LineSegmentQuadrature_test" )
{
    /*
     *      1 ___
     *     /  \   ```---5
     *    /     \         \        Line
     *   /        \     0   \ <--- ends
     * 2     1     3 ___      \    here
     *  \         /      ```---4
     *    \      /            /
     *      \   /      2     /
     *     A  0 ___         /
     *     |        ```---6
     *   Line
     *  starts
     *   here
     */

    auto meshVertices = std::vector
    {
        std::array { 3.0,  0.0 }, // 0
        std::array { 1.0,  9.0 }, // 1
        std::array { 0.0,  4.0 }, // 2
        std::array { 4.0,  5.0 }, // 3
        std::array { 9.0,  4.5 }, // 4
        std::array { 6.0,  8.5 }, // 5
        std::array { 8.0, -0.5 }  // 6
    };

    auto cells = std::vector<size_t>
    {
        5, 4, 1, 3, // 0
        2, 1, 0, 3, // 1
        0, 3, 6, 4  // 2
    };

    auto offsets = std::vector<size_t>
    {
        0, 4, 8, 12
    };

    auto mesh = UnstructuredMesh<2> { std::move( meshVertices ), std::move( cells ), std::move( offsets ) };

    auto lineSegments = LineSegments<2>
    {
        .vertices = 
        {
            std::array { 1.5 - 4.0, 2.0 - 3.0 },
            std::array { 9.5, 8.0 }
        },
        .cells = 
        {
            std::array<size_t, 2> { 0, 1 }
        }
    };

    auto expectedRst = std::vector
    {
        std::array {  0.30485049208932546,  0.88729833462074170 },
        std::array { -0.26470588235294146,  0.50000000000000011 },
        std::array { -0.83426225679520849,  0.11270166537925852 },
        std::array {  0.11270166537925845, -0.83426225679520838 },
        std::array {  0.50000000000000000, -0.26470588235294135 },
        std::array {  0.88729833462074170,  0.30485049208932580 },
        std::array { -0.94033441244627491,  0.53025382284784273 },
        std::array { -0.73529411764705876,  0.73529411764705888 },
        std::array { -0.53025382284784262,  0.94033441244627503 },
    };

    auto expectedWeights = std::array
    {
        0.75571895424836510,
        1.2091503267973851 ,
        0.75571895424836610,
        0.77614379084967244,
        1.2418300653594767 ,
        0.77614379084967355,
        0.55147058823529349,
        0.88235294117647034,
        0.55147058823529438,
    };

    auto expectedNormal = std::array { 0.6, -0.8 };

    auto check = [&]( auto& quadrature )
    {
        auto cache = quadrature.initialize( );
        auto mapping = mesh.createMapping( );
        auto rst = CoordinateList<2> { };
        auto normals = CoordinateList<2> { };
        auto weights = std::vector<double> { };

        for( CellIndex icell = 0; icell < 3; ++icell )
        {
            mesh.prepareMapping( icell, mapping );
            quadrature.distribute( mapping, { 2, 2 }, rst, normals, weights, cache );
        }

        REQUIRE( rst.size( ) == expectedRst.size( ) );
        REQUIRE( normals.size( ) == expectedRst.size( ) );
        REQUIRE( weights.size( ) == expectedRst.size( ) );

        for( size_t i = 0; i < rst.size( ); ++i )
        {
            CHECK( spatial::distance( rst[i], expectedRst[i] ) < 1e-10 );
            CHECK( spatial::distance( normals[i], expectedNormal ) < 1e-10 );
            CHECK( weights[i] == Approx( expectedWeights[i] ).epsilon( 1e-10 ) );
        }
    };

    // Check original configuration
    auto kdtree = buildKdTree<2>( lineSegments );
    auto [intersected, celldata] = intersectWithMesh<2>( lineSegments, mesh, kdtree );
    auto quadrature = SimplexQuadrature<2>( intersected, celldata, relativeQuadratureOrder<2>( 1 ) );

    check( quadrature );

    //auto output1 = VtuOutput { testing::outputPath( "core/LineSegmentQuadrature_mesh.vtu" ) };
    //auto output2 = VtuOutput { testing::outputPath( "core/LineSegmentQuadrature_points.vtu" ) };
    //writeOutput( mesh, cellmesh::grid<2>( { 1, 1 } ), CellProcessor<2> { }, output1 );
    //writeOutput( mesh, cellmesh::quadraturePoints( quadrature ), CellProcessor<2> { }, output2 );
    //writeVtu<2>( lineVertices, lineSegments, testing::outputPath( "core/LineSegmentQuadrature_line_original.vtu" ) );
    //writeVtu<2>( intersected.xyz, intersected.lines, testing::outputPath( "core/LineSegmentQuadrature_line_intersected.vtu" ) );

    // Reverse line direction
    std::reverse( lineSegments.vertices.begin( ), lineSegments.vertices.end( ) );

    kdtree = buildKdTree<2>( lineSegments );
    std::tie( intersected, celldata ) = intersectWithMesh<2>( lineSegments, mesh, kdtree );
    quadrature = SimplexQuadrature<2>( intersected, celldata, absoluteQuadratureOrder( array::makeSizes<2>( 3 ) ) );

    std::swap( expectedRst[0], expectedRst[2] );
    std::swap( expectedRst[3], expectedRst[5] );
    std::swap( expectedRst[6], expectedRst[8] );

    std::swap( expectedWeights[0], expectedWeights[2] );
    std::swap( expectedWeights[3], expectedWeights[5] );
    std::swap( expectedWeights[6], expectedWeights[8] );

    expectedNormal = -1.0 * expectedNormal;

    check( quadrature );

    // Check other configurations by just integrating a function
    auto function = []( std::array<double, 2> xy )
    {
        // Our line can be expressed as y = 3 * x / 4 + 0.875, which allows us to eliminate y
        // and integrate for x from 1.5 to 7.5 (result: 1288.779) using the factor 5/4 to go 
        // from dt to dx.
        return 1.5 * xy[0] * xy[1] + std::pow( 5.42 * xy[0] - 3.14 * xy[1], 2 ) - 10.4;
    };

    auto checkIntegral = [&]( )
    {
        auto cache = quadrature.initialize( );
        auto mapping = mesh.createMapping( );
        auto rst = CoordinateList<2> { };
        auto normals = CoordinateList<2> { };
        auto weights = std::vector<double> { };
        auto integral = 0.0;

        for( CellIndex icell = 0; icell < 3; ++icell )
        {
            utilities::resize0( rst, normals, weights );

            mesh.prepareMapping( icell, mapping );

            quadrature.distribute( mapping, { 1, 1 }, rst, normals, weights, cache );

            for( size_t ipoint = 0; ipoint < rst.size( ); ++ipoint )
            {
                CHECK( spatial::distance( normals[ipoint], expectedNormal ) < 1e-10 );

                integral += weights[ipoint] * function( mapping( rst[ipoint] ) );
            }
        }

        CHECK( integral == Approx( 1288.779 ).epsilon( 1e-10 ) );
    };
    
    // Try linear
    auto degree = relativeQuadratureOrder<2>( 1 );

    quadrature = SimplexQuadrature<2>( intersected, celldata, degree );

    checkIntegral( );

    // Other way
    std::reverse( lineSegments.vertices.begin( ), lineSegments.vertices.end( ) );
    
    expectedNormal = -1.0 * expectedNormal;

    kdtree = buildKdTree<2>( lineSegments );
    std::tie( intersected, celldata ) = intersectWithMesh<2>( lineSegments, mesh, kdtree );
    quadrature = SimplexQuadrature<2>( intersected, celldata, degree );

    checkIntegral( );

    // Many segments
    degree = absoluteQuadratureOrder( array::makeSizes<2>( 4 ) );
    
    auto oldVertices = lineSegments.vertices;

    utilities::resize0( lineSegments.vertices, lineSegments.cells );

    lineSegments.vertices.push_back( oldVertices[0] );

    for( size_t i = 1; i <= 10; ++i )
    {
        lineSegments.vertices.push_back( spatial::interpolate( oldVertices[0], oldVertices[1], 0.1 * i ) );
        lineSegments.cells.push_back( std::array { size_t { i - 1 }, size_t { i } } );
    }

    kdtree = buildKdTree<2>( lineSegments );
    std::tie( intersected, celldata ) = intersectWithMesh<2>( lineSegments, mesh, kdtree );
    quadrature = SimplexQuadrature<2>( intersected, celldata, degree );

    checkIntegral( );

    // Other way
    std::reverse( lineSegments.vertices.begin( ), lineSegments.vertices.end( ) );
    
    expectedNormal = -1.0 * expectedNormal;

    kdtree = buildKdTree<2>( lineSegments );
    std::tie( intersected, celldata ) = intersectWithMesh<2>( lineSegments, mesh, kdtree );
    quadrature = SimplexQuadrature<2>( intersected, celldata, degree );

    checkIntegral( );
}

TEST_CASE( "linesegment_domain_test" )
{
    auto directions = std::vector
    {
        std::array { 1.231, 0.818 },
        std::array { 0.32, -0.818 },
        std::array { -0.71, -0.43 },
        std::array { 1.0, 0.0 },
        std::array { 0.0, 1.0 },
        std::array { -1.0, 0.0 },
        std::array { 0.0, -1.0 }
    };

    for( auto& direction : directions )
    {
        auto lineSegments = LineSegments<2> { };

        auto n = size_t { 100 };
        auto origin = std::array<double, 2> { 3.2, -5.8 };
        auto radius = 1.713;

        for( size_t i = 0; i < n; ++i )
        {
            auto phi = 0.23 + i * 2.0 * std::numbers::pi / n;

            lineSegments.vertices.push_back( origin + radius * std::array { std::cos( phi ), std::sin( phi ) } );
            lineSegments.cells.push_back( std::array { i, i + 1 } );
        }

        lineSegments.cells.back( )[1] = 0;

        auto tree = buildKdTree<2>( lineSegments );
        auto segmentDomain = rayIntersectionDomain<2>( lineSegments, tree, { direction } );

        //print( tree, std::cout );
        //writeVtu( tree, testing::outputPath( "core/makeLineSegmentDomain_tree.vtu" ) );
        //writeVtu<2>( lineVertices, lineSegments, testing::outputPath( "core/makeLineSegmentDomain_line.vtu" ) );

        //auto testpoints = std::vector<std::array<double, 2>> { };
        auto allcorrect = true;

        for( size_t i = 0; i < 231; ++i )
        {
            auto phi = 0.54 + i * 2.0 * std::numbers::pi / 231.0;
            auto d = std::array { std::cos( phi ), std::sin( phi ) };

            auto epsilon = 0.001 * ( i % 2 + 1 ) * ( i % 4 + 1 );
            auto inside = origin + ( 1.0 - epsilon ) * radius * d;
            auto outside = origin + ( 1.0 + epsilon ) * radius * d;

            //testpoints.push_back( inside );
            //testpoints.push_back( outside );

            allcorrect = allcorrect && segmentDomain( inside ) == true;
            allcorrect = allcorrect && segmentDomain( outside ) == false;
        }

        CHECK( allcorrect );

        auto npoints = std::array { size_t { 21 }, size_t { 21 } };
        auto pointGenerator = spatial::makeGridPointGenerator<2>( npoints, 
            array::make<2>( 2.4 * radius ), origin - 1.2 * radius );
    
        allcorrect = true;

        nd::execute( npoints, [&]( std::array<size_t, 2> ij ) 
        { 
            auto xy = pointGenerator( ij );
            auto inside = spatial::norm( xy - origin ) < radius;

            allcorrect = allcorrect && segmentDomain( xy ) == inside;
            //testpoints.push_back( xy );
        } );

        CHECK( allcorrect );

        //writeVtu<2>( testpoints, "outputs/testpoints.vtu" );
    
        auto xyz = std::array { origin[0] - 1.2 * radius, origin[1] - 1.2 * radius + 2.4 * radius };

        CHECK( !segmentDomain( xyz ) );

        //writeOutput<2>( tree, cellmesh::grid<2>( ), makeKdTreeInfoProcessor<2>( ), VtuOutput { "outputs/tree" } );
        //writeOutput<2>( CartesianGrid<2>( { 100, 100 }, array::make<2>( 2.4 * radius ), origin - 1.2 * radius ), 
        //    cellmesh::domain<2>( segmentDomain, { 1, 1 } ), CellProcessor<2> { },
        //    VtuOutput { "outputs/segmentdomain.vtu" } );
    }
}

// Has some weird cases that happen when the ray traversal gathers a few triangles, but
// then hits an empty cell, but with the intersection points of the gathered triangles
// lying behind the cell. So we get wrong results if we count these intersection points.
TEST_CASE( "triangle_domain_test2" )
{
    auto testDirections = std::vector
    {
        std::array { 0.3123, -0.423, 0.8323 },
        std::array { 0.3123, 0.423, 0.8323 },
        std::array { 1.0, -1.2e-9, 3.2e-10 },
        std::array { 1e-12, -1.0, -1.3e-11 }
    };

    auto domain = implicit::sphere<3>( { 1.0, 1.0, 1.0 }, 0.8 );
    auto origin = std::array { 0.0, 0.0, 0.0 };
    auto lengths = std::array { 2.0, 2.0, 2.0 };

    auto mesh = makeCartesianGrid<3>( { 4, 4, 4 }, lengths, origin );
    auto triangles = recoverDomainBoundary( *mesh, domain, { 1, 1, 1 } ).first;

    for( auto& direction : testDirections )
    {
        auto tree = buildKdTree( triangles );
        auto domain2 = rayIntersectionDomain<3>( triangles, tree, { direction } );

        CHECK( !domain2( { 0.225, 1.5, 0.5626 } ) );
        CHECK( domain2( { 0.61, 0.49, 1.08 } ) );
        CHECK( domain2( { 1.51, 0.61, 1.05 } ) );
            
        auto allcorrect1 = true;
        auto npoints1 = array::makeSizes<3>( 5 );
        auto xyz1 = spatial::makeGridPointGenerator( npoints1, lengths, origin );

        nd::execute( npoints1, [&]( std::array<size_t, 3> ij ) 
        { 
            allcorrect1 = allcorrect1 && domain( xyz1( ij ) ) == domain2( xyz1( ij ) );
        } );

        CHECK( allcorrect1 );

        auto allcorrect2 = true;
        auto npoints2 = array::makeSizes<3>( 4 * 4 + 1 );
        auto xyz2 = spatial::makeGridPointGenerator( npoints2, lengths, origin );
        
        nd::execute( npoints2, [&]( std::array<size_t, 3> ij ) 
        { 
            // Skip points between 0.716 and 0.8 since all triangles are inbetween 
            if( std::abs( spatial::norm( xyz2( ij ) - array::make<3>( 1.0 ) ) - 0.758 ) > 0.042 )
            {
                allcorrect2 = allcorrect2 && domain( xyz2( ij ) ) == domain2( xyz2( ij ) );
            }
        } );

        CHECK( allcorrect2 );

        auto mesh2 = makeCartesianGrid<3>( { 20, 20, 20 }, { 2.0, 2.0, 2.0 } );

        //writeVtu( triangles, "outputs/triangles.vtu" );

        //writeOutput( tree, cellmesh::grid<3>( ),
        //    makeKdTreeInfoProcessor<3>( ), PVtuOutput { "outputs/tree" } );

        //writeOutput( *mesh2, cellmesh::domain( domain2, { 8, 8, 8 } ), 
        //    CellProcessor<3> { }, PVtuOutput { "outputs/recovered" } );
    }
}

TEST_CASE( "triangle_domain_test3" )
{
    auto ticks = spatial::cartesianTickVectors<3>( { 1, 1, 1 } );

    auto boundary = Triangulation<3>
    { 
        .vertices = spatial::tensorProduct( ticks ),
        .cells = 
        {
            { 0, 1, 2 }, { 1, 2, 3 }, 
            { 4, 5, 6 }, { 5, 6, 7 },
            { 0, 1, 4 }, { 1, 4, 5 }, 
            { 2, 3, 6 }, { 3, 6, 7 },
            { 0, 2, 4 }, { 2, 4, 6 }, 
            { 1, 3, 5 }, { 3, 5, 7 }
        }
    };

    auto domain = implicit::cube<3>( boundary.boundingBox( ) );

    auto tree = buildKdTree( boundary );

    auto domain1 = rayIntersectionDomain<3>( boundary, tree );
    auto domain2 = rayIntersectionDomain<3>( boundary, tree, 
        { { 1.0, 0.0, 0.0 }, { 0.0, 1.0, 0.0 }, { 0.0, 0.0, 1.0 } } );

    CHECK( boundary.boundingBox( )[0] == std::array { 0.0, 0.0, 0.0 } );
    CHECK( boundary.boundingBox( )[1] == std::array { 1.0, 1.0, 1.0 } );

    // Check if tree is still the same as when writing this test
    REQUIRE( tree.nfull( ) == 13 );
    REQUIRE( tree.nleaves( ) == 7 );

    CHECK( tree.boundingBox( )[0] == std::array { 0.0, 0.0, 0.0 } );
    CHECK( tree.boundingBox( )[1] == std::array { 1.0, 1.0, 1.0 } );

    auto equalState = [&]( CellIndex ileaf, std::int16_t state, const auto& items )
    {
        auto computed = tree.itemsFull( tree.fullIndex( ileaf ) );

        CHECK( tree.stateFull( tree.fullIndex( ileaf ) ) == state );
        CHECK( std::equal( computed.begin( ), computed.end( ), items.begin( ), items.end( ) ) );
    };

    equalState( 0, 0, std::array<size_t, 2>{ 0, 1 } );
    equalState( 1, 0, std::array<size_t, 2>{ 4, 5 } );
    equalState( 2, 0, std::array<size_t, 2>{ 8, 9 } );
    equalState( 3, 0, std::array<size_t, 2>{ 2, 3 } );
    equalState( 4, 0, std::array<size_t, 2>{ 6, 7 } );
    equalState( 5, 1, std::array<size_t, 0>{ } );
    equalState( 6, 0, std::array<size_t, 2>{ 10, 11 } );

    // Test domain on a grid of points
    auto npoints = array::makeSizes<3>( 13 );

    auto generator = spatial::makeGridPointGenerator<3>( 
        npoints, array::make<3>( 1.5 ), array::make<3>( -0.25 ) );

    //auto points = CoordinateList<3> { };
    auto allcorrect1 = true;
    auto allcorrect2 = true;
    auto count = size_t { 0 };

    nd::execute( npoints, [&]( std::array<size_t, 3> ijk )
    { 
        auto xyz = generator( ijk );

        auto onface = false;
        auto outside = false;

        for( size_t axis = 0; axis < 3; ++axis )
        {
            onface = onface || std::abs( xyz[axis] - 0.5 ) == 0.5;
            outside = outside || std::abs( xyz[axis] - 0.5 ) > 0.5;
        }

        if( outside || !onface )
        {
            allcorrect1 = allcorrect1 && domain( xyz ) == domain2( xyz );
            allcorrect2 = allcorrect2 && domain( xyz ) == domain2( xyz );

            //points.push_back( xyz );
            count += 1;
        }
    } );

    CHECK( count == 1811 );
    CHECK( allcorrect1 );
    CHECK( allcorrect2 );

    //writeVtu<3>( points, "points.vtu" );
    //writeVtu<3>( boundary, "triangles.vtu" );
    //writeOutput( CartesianGrid<3>( { 4, 4, 4 }, { 1.0, 1.0, 1.0 } ), cellmesh::domain( 
    //    domain2, { 8, 8, 8 } ), CellProcessor<3> { }, VtuOutput { "recovered" } );
}

TEST_CASE( "marching_squares_test" )
{
    auto circle1 = implicit::sphere<2>( { 0.62, 0.5 }, 0.432 );
    auto circle2 = implicit::sphere<2>( { 0.73, 0.48 }, 0.23 );

    auto domain = implicit::subtract( circle1, circle2 );

    auto mesh = makeCartesianGrid<2>( { 4, 2 }, { 1.385, 1.143 } );

    auto [lines, celldata] = recoverDomainBoundary<2>( *mesh, domain, { 3, 4 } );

    REQUIRE( lines.ncells( ) == 42 );
    REQUIRE( lines.nvertices( ) == 54 );
    REQUIRE( celldata.rst.size( ) == 54 );
    REQUIRE( celldata.offsets.size( ) == 9 );

    auto integratedNormal0 = integrateNormalComponents<2>( lines, false );
    auto integratedNormal1 = integrateNormalComponents<2>( lines, true );

    CHECK( lines.length( ) == Approx( 4.2507128392517 ).epsilon( 1e-12 ) );

    CHECK( spatial::distance<2>( integratedNormal0, { 0.0, 0.0 } ) < 1e-12 );
    CHECK( spatial::distance<2>( integratedNormal1, { 2.69251007080078, 2.70259847005208 } ) < 1e-12 );

    auto basis = DummyBasis<2> { mesh };

    // Compute volume through dot product with position vector
    auto positionVector = []( std::array<double, 2> xy ) 
    { 
        return 0.5 * std::array { xy[0], xy[1] }; 
    };

    auto dotProductIntegrand = makeNormalDotProductIntegrand<2>( 
        spatial::VectorFunction<2, 2> { positionVector } );

    auto lineQuadrature = SimplexQuadrature<2> { lines, celldata };
    auto volume = 0.0;

    integrateOnSurface( basis, dotProductIntegrand, lineQuadrature, { volume } );

    CHECK( volume == Approx( 0.40353845240023 ).epsilon( 1e-12 ) );

    //writeVtu( lines, "outputs/lines.vtu" );
    //writeVtu( *mesh, "outputs/mesh2D.vtu" );

    // Compute volume through domain recovery
    for( size_t coarsen = 0; coarsen < 2; ++coarsen )
    {
        auto domainMesh1 = cellmesh::domain( domain, { 3, 4 }, coarsen, false );
        auto domainMesh2 = cellmesh::domain( domain, { 3, 4 }, coarsen, true );

        auto domainQuadrature1 = CellmeshQuadrature<2>( domainMesh1 );
        auto domainQuadrature2 = CellmeshQuadrature<2>( domainMesh2 );

        auto areaIntegrand = makeFunctionIntegrand<2>( spatial::constantFunction<2>( 1.0 ) );

        auto volume1 = 0.0;
        auto volume2 = 0.0;

        integrateOnDomain( basis, areaIntegrand, { volume1 }, domainQuadrature1 );
        integrateOnDomain( basis, areaIntegrand, { volume2 }, domainQuadrature2 );

        auto meshArea = spatial::boundingBoxVolume( mesh->boundingBox( ) );

        CHECK( volume1 == Approx( volume ).epsilon( 1e-12 ) );
        CHECK( volume2 == Approx( meshArea ).epsilon( 1e-12 ) );

        //writeOutput( *mesh, domainMesh2, CellProcessor<2> { }, VtuOutput { "outputs/domain2D.vtu" } );
    }
}

TEST_CASE( "filter_segmentation_test" )
{
    auto vertices = CoordinateList<2> { };
    auto cells = std::vector<std::array<size_t, 2>> { };

    for( size_t i = 0; i < 20; ++i )
    {
        auto phi = 2.0 * std::numbers::pi * i / 20.0 + 1.32;

        vertices.push_back( { 0.8 * std::sin( phi ) + 2.5, 1.2 * std::cos( phi ) - 2.0 } );
        cells.push_back( { i, i + 1 } );
    }

    cells.back( )[1] = cells.front( )[0];

    auto lines = SimplexMesh<2, 1>
    { 
        .vertices = std::move( vertices ),
        .cells = std::move( cells )
    };

    writeVtu( lines, "outputs/lines.vtu" );

    auto filtered1 = filterSimplexMesh( lines, implicit::halfspace<2>( 0, 2.5 ) );
    auto filtered2 = filterSimplexMesh( lines, implicit::halfspace<2>( 1, -2.0, false ) );

    CHECK( filtered1.vertices.size( ) == 10 );
    CHECK( filtered2.vertices.size( ) == 10 );

    CHECK( filtered1.cells.size( ) == 9 );
    CHECK( filtered2.cells.size( ) == 9 );

    auto bounds1 = filtered1.boundingBox( );
    auto bounds2 = filtered2.boundingBox( );

    CHECK( spatial::distance<2>( bounds1[0], { 2.5506564385325535, -3.1624581201419186 } ) < 1e-12 );
    CHECK( spatial::distance<2>( bounds1[1], { 3.2983945924385996, -0.8024081113421004 } ) < 1e-12 );
    CHECK( spatial::distance<2>( bounds2[0], { 1.7250279199053877, -3.1975918886578993 } ) < 1e-12 );
    CHECK( spatial::distance<2>( bounds2[1], { 3.2983945924385996, -2.0759846577988288 } ) < 1e-12 );
}

TEST_CASE( "simplexQuadrature_skipSingular_test" )
{
    // Create one quarter of a plate with a hole
    auto boundary = SimplexMesh<2, 1> { };

    boundary.vertices = { { -1.0, 0.0 }, { 0.0, 1.0 }, { 0.0, 1.0 }, { 1.0, 2.0 } };
    boundary.cells = { { 0, 1 }, { 1, 2 }, { 2, 3 }, { 0, 3 } };

    auto mesh = makeCartesianGrid<2>( { 1, 1 } );

    // Intersect segments and mesh
    auto [intersected, celldata] = intersectWithMesh( boundary, *mesh, buildKdTree( boundary ) );
    
    REQUIRE( !celldata.offsets.empty( ) );
    
    CHECK( intersected.cells.size( ) == 0 );
    CHECK( celldata.offsets.back( ) == 0 );

    // Create new segments with one collapsed segment
    intersected.vertices = { { 0.0, 0.0 }, { 0.0, 1.0 }, { 0.0, 1.0 }, { 0.5, 1.0 } };
    intersected.cells = { { 0, 1 }, { 1, 2 }, { 2, 3 } };
    celldata.rst = { { -1.0, -1.0 }, { -1.0, 1.0 }, { -1.0, 1.0 }, { 0.0, 1.0 } };
    celldata.offsets = { 0, 3 };

    // Evaluate and check result
    auto quadrature = SimplexQuadrature<2> { intersected, celldata, absoluteQuadratureOrder<2>( { 1, 2 } ) };
    auto partitions = evaluateQuadrature( quadrature, *mesh, 0, { 0, 0 } );

    REQUIRE( partitions.size( ) == 1 );
    CHECK( partitions[0].icell == 0 );

    CHECK( partitions[0].mesh == mesh.get( ) );
    CHECK( partitions[0].isgrid == false );

    REQUIRE( partitions[0].weights.size( ) == 4 );
    REQUIRE( partitions[0].xyz.size( ) == 4 );
    REQUIRE( partitions[0].rst.size( ) == 4 );

    auto [x, w] = gaussLegendrePoints( 2 );

    auto expected = std::array
    { 
        std::tuple { std::array { -1.0, x[0] }, std::array { 0.0, 0.5 * x[0] + 0.5 }, 0.5 * w[0] },
        std::tuple { std::array { -1.0, x[1] }, std::array { 0.0, 0.5 * x[1] + 0.5 }, 0.5 * w[1] },
        std::tuple { std::array { 0.5 * x[0] - 0.5, 1.0 }, std::array { 0.25 * x[0] + 0.25, 1.0 }, 0.25 * w[0] }, 
        std::tuple { std::array { 0.5 * x[1] - 0.5, 1.0 }, std::array { 0.25 * x[1] + 0.25, 1.0 }, 0.25 * w[1] } 
    };

    for( size_t i = 0; i < 4; ++i )
    {
        CHECK( spatial::distance<2>( partitions[0].rst[i], std::get<0>( expected[i] ) ) < 1e-12 );
        CHECK( spatial::distance<2>( partitions[0].xyz[i], std::get<1>( expected[i] ) ) < 1e-12 );
        CHECK( partitions[0].weights[i] == Approx( std::get<2>( expected[i] ) ).epsilon( 1e-12 ) );
    }
}

TEST_CASE( "linesegment_domain_test2" )
{
    auto boundary = SimplexMesh<2, 1> { };
    
    boundary.vertices = 
    { 
        { -1.0, -1.0 }, { 0.0, -1.0 }, { 0.0, 0.0 }, { 1.0, 0.0 }, 
        { 1.0, 1.0 }, { -1.0, 1.0 }, { -1.0, -1.0 } 
    };

    boundary.cells = { { 0, 1 }, { 1, 2 }, { 2, 3 }, { 3, 4 }, { 4, 5 }, { 5, 6 } };

    auto tree = buildKdTree( boundary );

    //print( tree, std::cout );
    //printFull( tree, std::cout );

    auto domain1 = rayIntersectionDomain<2>( boundary, tree );
    auto domain2 = implicit::invert( implicit::cube<2>( { 0.0, -1.0 }, { 1.0, 0.0 } ) );

    CHECK( domain1( { -0.5, -0.5 } ) );

    auto allequal = true;

    for( size_t i = 0 ; i < 20; ++i )
    {
        for( size_t j = 0; j < 20; ++j )
        {
            auto x = ( 0.5 * i / 19.0 - 1.0 ) * ( 1.0 - 1e-10 );
            auto y = ( 0.5 * j / 19.0 - 1.0 ) * ( 1.0 - 1e-10 );

            allequal = allequal && domain1( { x, y } ) == domain2( { x, y } );
        }
    }

    CHECK( allequal );

    //auto mesh = makeCartesianGrid<2>( { 100, 100 }, { 2.0, 2.0 }, { -1.0, -1.0 } );
    //
    //writeVtu( boundary, "outputs/lineboundary.vtu" );
    //writeOutput( *mesh, cellmesh::domain( domain1 ), CellProcessor<2> { }, VtuOutput { "outputs/domain.vtu" } );
    //writeOutput( tree, cellmesh::grid<2>( ), makeKdTreeInfoProcessor<2>( ), VtuOutput { "outputs/tree.vtu" } );
}

TEST_CASE( "linesegment_domain_test3" )
{
    auto boundary = SimplexMesh<2, 1> { };
    
    boundary.vertices = 
    { 
        { -1.0, -1.0 }, { 1.0, -1.0 }, { 1.0, 10.0 }, { -1.0, 1.0 }
    };

    boundary.cells = { { 0, 1 }, { 1, 2 }, { 2, 3 }, { 3, 0 } };

    auto tree = buildKdTree( boundary );

    //print( tree, std::cout );
    //printFull( tree, std::cout );

    auto box = implicit::cube<2>( { -1.0, -1.0 }, { 1.0, 1.0 } );
    
    auto line0 = implicit::halfspace<2>( { 1.0, 1.0 }, { 0.0, -1.0 } );
    auto line1 = implicit::halfspace<2>( { 1.0, 1.0 }, { 1.0, 0.0 } );
    auto line2 = implicit::halfspace<2>( { -1.0, 1.0 }, { -9.0, 2.0 } );

    auto domain1 = rayIntersectionDomain<2>( boundary, tree );
    auto domain2 = implicit::add( box, implicit::intersect( line0, line1, line2 ) );

    CHECK( domain1( { 0.0, 1.5 } ) );
    CHECK( !domain1( { -0.9, 1.5 } ) );

    auto allequal = true;

    for( size_t i = 0 ; i < 10; ++i )
    {
        for( size_t j = 0; j < 40; ++j )
        {
            auto x = ( 0.5 * i / 9.0 - 1.0 ) * ( 1.0 - 1e-10 );
            auto y = ( 12.0 * j / 39.0 - 1.0 ) * ( 1.0 - 1e-10 );

            allequal = allequal && domain1( { x, y } ) == domain2( { x, y } );
        }
    }

    CHECK( allequal );

    //auto mesh = makeCartesianGrid<2>( { 40, 440 }, { 2.0, 11.0 }, { -1.0, -1.0 } );
    //
    //writeVtu( boundary, "outputs/lineboundary.vtu" );
    //writeOutput( *mesh, cellmesh::domain( domain1 ), CellProcessor<2> { }, VtuOutput { "outputs/domain.vtu" } );
    //writeOutput( tree, cellmesh::grid<2>( ), makeKdTreeInfoProcessor<2>( ), VtuOutput { "outputs/tree.vtu" } );
}

TEST_CASE( "skeletonMesh_test" )
{
    auto mesh = makeRefinedGrid<2>( { 4, 3 }, { 4.0, 3.0 }, { 1.0, 2.0 } );

    mesh->refine( { 1, 4, 7, 8, 10, 11 } );
    mesh->refine( { 12, 13, 14, 15 } );

    auto skeleton = createSkeletonMesh( *mesh );

    REQUIRE( skeleton.ncells( ) == 49 + 52 );
    REQUIRE( skeleton.nvertices( ) == 2 * skeleton.ncells( ) );

    // Two consecutive vertices form a line
    auto expected = std::vector<std::array<double, 2>>
    {
        { 2.0, 2.0 }, { 2.0, 3.0 }, { 2.0, 2.0 }, { 3.0, 2.0 }, { 1.0, 3.0 }, { 1.0, 3.5 }, { 1.0, 3.0 }, { 1.5, 3.0 },
        { 2.0, 3.0 }, { 2.0, 3.5 }, { 2.0, 3.0 }, { 2.5, 3.0 }, { 2.0, 3.5 }, { 2.0, 4.0 }, { 2.0, 3.5 }, { 2.5, 3.5 },
        { 2.0, 4.0 }, { 2.5, 4.0 }, { 3.5, 3.0 }, { 4.0, 3.0 }, { 3.5, 4.0 }, { 3.5, 4.5 }, { 3.5, 4.0 }, { 4.0, 4.0 },
        { 3.5, 4.5 }, { 3.5, 5.0 }, { 3.5, 4.5 }, { 4.0, 4.5 }, { 3.5, 5.0 }, { 4.0, 5.0 }, { 4.5, 4.5 }, { 4.5, 5.0 },
        { 5.0, 4.5 }, { 5.0, 5.0 }, { 4.5, 4.5 }, { 5.0, 4.5 }, { 4.5, 5.0 }, { 5.0, 5.0 }, { 3.0, 3.25 }, { 3.0, 3.5 },
        { 3.0, 3.25 }, { 3.25, 3.25 }, { 1.0, 2.0 }, { 1.0, 3.0 }, { 1.0, 2.0 }, { 2.0, 2.0 }, { 1.5, 3.0 }, { 1.5, 3.5 },
        { 1.5, 3.0 }, { 2.0, 3.0 }, { 4.5, 3.5 }, { 4.5, 4.0 }, { 5.0, 3.5 }, { 5.0, 4.0 }, { 4.5, 3.5 }, { 5.0, 3.5 },
        { 4.0, 4.0 }, { 4.0, 4.5 }, { 4.0, 4.0 }, { 4.5, 4.0 }, { 4.0, 4.5 }, { 4.0, 5.0 }, { 4.0, 4.5 }, { 4.5, 4.5 },
        { 4.0, 5.0 }, { 4.5, 5.0 }, { 2.75, 3.0 }, { 2.75, 3.25 }, { 2.75, 3.0 }, { 3.0, 3.0 }, { 2.75, 3.25 }, { 2.75, 3.5 },
        { 2.75, 3.25 }, { 3.0, 3.25 }, { 2.0, 4.0 }, { 2.0, 5.0 }, { 2.0, 5.0 }, { 3.0, 5.0 }, { 1.5, 3.5 }, { 1.5, 4.0 },
        { 1.5, 3.5 }, { 2.0, 3.5 },  { 1.5, 4.0 }, { 2.0, 4.0 }, { 3.0, 4.5 }, { 3.0, 5.0 }, { 3.0, 4.5 }, { 3.5, 4.5 },
        { 3.0, 5.0 }, { 3.5, 5.0 }, { 4.0, 3.5 }, { 4.0, 4.0 }, { 4.0, 3.5 }, { 4.5, 3.5 }, { 4.5, 4.0 }, { 4.5, 4.5 },
        { 5.0, 4.0 }, { 5.0, 4.5 }, { 4.5, 4.0 }, { 5.0, 4.0 }, { 2.5, 3.25 }, { 2.5, 3.5 }, { 2.5, 3.25 }, { 2.75, 3.25 },
        { 2.5, 3.5 }, { 2.5, 3.75 }, { 2.5, 3.5 }, { 2.75, 3.5 }, { 2.5, 3.75 }, { 2.5, 4.0 }, { 2.5, 3.75 }, { 2.75, 3.75 },
        { 2.5, 4.0 }, { 2.75, 4.0 }, { 3, 3.5 }, { 3, 3.75 }, { 3, 3.5 }, { 3.25, 3.5 }, { 3.25, 3.5 }, { 3.25, 3.75 },
        { 3.5, 3.5 }, { 3.5, 3.75 }, { 3.25, 3.5 }, { 3.5, 3.5 }, { 1.0, 4.0 }, { 1.0, 5.0 }, { 1.0, 5.0 }, { 2.0, 5.0 },
        { 1.0, 3.5 }, { 1.0, 4.0 }, { 1.0, 3.5 }, { 1.5, 3.5 }, { 1.0, 4.0 }, { 1.5, 4.0 }, { 3.5, 3.5 }, { 4.0, 3.5 },
        { 3.0, 4.0 }, { 3.0, 4.5 }, { 4.0, 3.0 }, { 4.0, 3.5 }, { 4.0, 3.0 }, { 4.5, 3.0 }, { 4.5, 3.0 }, { 4.5, 3.5 },
        { 5.0, 3.0 }, { 5.0, 3.5 }, { 4.5, 3.0 }, { 5.0, 3.0 }, { 2.75, 3.5 }, { 2.75, 3.75 }, { 2.75, 3.5 }, { 3.0, 3.5 },
        { 2.75, 3.75 }, { 2.75, 4.0 }, { 2.75, 3.75 }, { 3.0, 3.75 }, { 2.75, 4.0 }, { 3.0, 4.0 }, { 3.25, 3.25 }, { 3.25, 3.5 },
        { 3.5, 3.25 }, { 3.5, 3.5 }, { 3.25, 3.25 }, { 3.5, 3.25 }, { 3.0, 2.0 }, { 3.0, 3.0 }, { 3.0, 2.0 }, { 4.0, 2.0 },
        { 4.0, 2.0 }, { 4.0, 3.0 }, { 5.0, 2.0 }, { 5.0, 3.0 }, { 4.0, 2.0 }, { 5.0, 2.0 }, { 2.5, 3.0 }, { 2.5, 3.25 },
        { 2.5, 3.0 }, { 2.75, 3.0 }, { 3.0, 3.0 }, { 3.0, 3.25 }, { 3.0, 3.0 }, { 3.25, 3.0 }, { 3.25, 3.0 }, { 3.25, 3.25 },
        { 3.5, 3.0 }, { 3.5, 3.25 }, { 3.25, 3.0 }, { 3.5, 3.0 }, { 3, 3.75 }, { 3.0, 4.0 }, { 3, 3.75 }, { 3.25, 3.75 },
        { 3, 4.0 }, { 3.25, 4.0 }, { 3.25, 3.75 }, { 3.25, 4.0 }, { 3.5, 3.75 }, { 3.5, 4 }, { 3.25, 3.75 }, { 3.5, 3.75 },
        { 3.25, 4.0 }, { 3.5, 4.0 },
    };
    
    auto count = std::vector<size_t>( skeleton.ncells( ), 0 );

    for( size_t i = 0; i < 101; ++i )
    {
        auto [v0, v1] = skeleton.cellVertices( i );

        for( size_t j = 0; j < 101; ++j )
        {
            auto d0 = spatial::distance( v0, expected[2 * j] );
            auto d1 = spatial::distance( v1, expected[2 * j + 1] );

            if( d0 < 1e-12 && d1 < 1e-12 )
            {
                count[j] += 1;
            }
        }
    }

    CHECK( count == std::vector<size_t>( skeleton.ncells( ), 1 ) );

    writeVtu( *mesh, "mesh.vtu" );

    auto mesh1D = makeRefinedGrid<1>( { 3 } );
    auto skeleton1D = createSkeletonMesh( *mesh1D );

    CHECK( skeleton1D.nvertices( ) == 4 );
    CHECK( skeleton1D.ncells( ) == 4 );
    CHECK( skeleton1D.normals.size( ) == 4 );

    auto expected1D = std::vector<double> { 0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0 };
    auto count1D = std::vector<size_t>( skeleton1D.ncells( ), 0 );

    for( size_t i = 0; i < 4; ++i )
    {
        auto x = skeleton1D.cellVertices( i )[0][0];

        for( size_t j = 0; j < 4; ++j )
        {
            count1D[j] += ( std::abs( x - expected1D[j] ) < 1e-12 );
        }
    }

    CHECK( count1D == std::vector<size_t>( skeleton1D.ncells( ), 1 ) );
}

TEST_CASE( "marching_1D_test" )
{
    auto domain = implicit::sphere<1>( { 0.5 }, 0.23 );
    auto mesh = makeCartesianGrid<1>( { 7 }, { 0.9 }, { 0.1 } );

    auto [points, celldata] = recoverDomainBoundary<1>( *mesh, domain, { 5 }, 50 );

    auto expectedCells = std::vector 
    { 
        std::array<size_t, 1> { 0 },
        std::array<size_t, 1> { 1 } 
    };

    REQUIRE( points.ncells( ) == 2 );
    REQUIRE( points.nvertices( ) == 2 );
    REQUIRE( points.normals.size( ) == 2 );
    REQUIRE( celldata.rst.size( ) == 2 );
    REQUIRE( celldata.offsets.size( ) == 8 );
    REQUIRE( points.cells == expectedCells );

    CHECK( points.vertices[0][0] == Approx( 0.27 ).epsilon( 1e-12 ) );
    CHECK( points.vertices[1][0] == Approx( 0.73 ).epsilon( 1e-12 ) );
    CHECK( points.normals[0][0] == -1.0 );
    CHECK( points.normals[1][0] == 1.0 );

    auto integratedNormal1 = integrateNormalComponents<1>( points, false );
    auto integratedNormal2 = integrateNormalComponents<1>( points, true );

    CHECK( points.measure( ) == Approx( 2.0 ).epsilon( 1e-12 ) );

    CHECK( spatial::distance<1>( integratedNormal1, { 0.0 } ) < 1e-12 );
    CHECK( spatial::distance<1>( integratedNormal2, { 2.0 } ) < 1e-12 );

    auto basis = DummyBasis<1> { mesh };

    // Compute volume through dot product with position vector
    auto positionVector = []( std::array<double, 1> x ) { return std::array { x[0] }; };

    auto dotProductIntegrand = makeNormalDotProductIntegrand<1>( 
        spatial::VectorFunction<1, 1> { positionVector } );

    auto lineQuadrature = SimplexQuadrature<1> { points, celldata };
    auto volume = 0.0;

    integrateOnSurface( basis, dotProductIntegrand, lineQuadrature, { volume } );

    CHECK( volume == Approx( 0.46 ).epsilon( 1e-12 ) );

    volume = 0.46;

    //writeVtu( points, "outputs/points.vtu" );
    //writeVtu( *mesh, "outputs/mesh1D.vtu" );

    // Compute volume through domain recovery
    for( size_t coarsen = 0; coarsen < 2; ++coarsen )
    {
        auto domainMesh1 = cellmesh::domain( domain, { 5 }, coarsen, false, 50 );
        auto domainMesh2 = cellmesh::domain( domain, { 5 }, coarsen, true );

        auto domainQuadrature1 = CellmeshQuadrature<1>( domainMesh1 );
        auto domainQuadrature2 = CellmeshQuadrature<1>( domainMesh2 );

        auto areaIntegrand = makeFunctionIntegrand<1>( spatial::constantFunction<1>( 1.0 ) );

        auto volume1 = 0.0;
        auto volume2 = 0.0;

        integrateOnDomain( basis, areaIntegrand, { volume1 }, domainQuadrature1 );
        integrateOnDomain( basis, areaIntegrand, { volume2 }, domainQuadrature2 );

        auto meshArea = spatial::boundingBoxVolume( mesh->boundingBox( ) );

        CHECK( volume1 == Approx( volume ).epsilon( 1e-12 ) );
        CHECK( volume2 == Approx( meshArea ).epsilon( 1e-12 ) );

        //writeOutput( *mesh, domainMesh1, CellProcessor<1> { }, VtuOutput { "outputs/domain1D.vtu" } );
    }

    // Check filtering 
    auto filtered = filterSimplexMesh( points, implicit::sphere<1>( { 0.27 }, 0.1 ) );

    REQUIRE( filtered.vertices.size( ) == 1 );
    REQUIRE( filtered.normals.size( ) == 1 );
    REQUIRE( filtered.cells == std::vector { std::array<size_t, 1> { 0 } } );

    CHECK( filtered.vertices[0][0] == Approx( 0.27 ).epsilon( 1e-12 ) );
    CHECK( filtered.normals[0][0] == -1.0 );

    filtered = filterSimplexMesh( points, implicit::sphere<1>( { 0.73 }, 0.1 ) );

    REQUIRE( filtered.vertices.size( ) == 1 );
    REQUIRE( filtered.normals.size( ) == 1 );
    REQUIRE( filtered.cells == std::vector { std::array<size_t, 1> { 0 } } );

    CHECK( filtered.vertices[0][0] == Approx( 0.73 ).epsilon( 1e-12 ) );
    CHECK( filtered.normals[0][0] == 1.0 );

    filtered = filterSimplexMesh( points, implicit::sphere<1>( { 0.0 }, 0.1 ) );

    CHECK( filtered.vertices.size( ) == 0 );
    CHECK( filtered.normals.size( ) == 0 );
    CHECK( filtered.cells == std::vector<std::array<size_t, 1>> { } );

    filtered = filterSimplexMesh( points, implicit::sphere<1>( { 0.0 }, 1.0 ) );

    CHECK( filtered.vertices.size( ) == 2 );
    CHECK( filtered.normals.size( ) == 2 );
    CHECK( filtered.cells == expectedCells );

    CHECK( filtered.vertices[0][0] == Approx( 0.27 ).epsilon( 1e-12 ) );
    CHECK( filtered.vertices[1][0] == Approx( 0.73 ).epsilon( 1e-12 ) );
    CHECK( filtered.normals[0][0] == -1.0 );
    CHECK( filtered.normals[1][0] == 1.0 );
}

TEST_CASE( "simplex_1D_test" )
{
    // Test mesh intersection
    auto points = SimplexMesh<1, 0> { };
    
    points.vertices = std::vector
    {
        std::array { -0.5 }, std::array { 0.5 }, std::array { 2.8 }, std::array { 4.0 }
    };

    points.cells = std::vector
    {
        std::array<size_t, 1> { 0 }, 
        std::array<size_t, 1> { 1 }, 
        std::array<size_t, 1> { 2 }, 
        std::array<size_t, 1> { 3 }
    };

    points.normals = std::vector
    {
        std::array { -1.0 },
        std::array { 1.0 },
        std::array { -1.0 },
        std::array { 1.0 }
    };

    auto mesh = makeCartesianGrid<1>( { 7 }, { 3.5 }, { 0.1 } );
    auto tree = buildKdTree( kdtree::makeObjectProvider<1, 0>( points ) );

    auto [intersected, celldata] = intersectWithMesh<1, 0>( points, *mesh, tree );

    REQUIRE( intersected.vertices.size( ) == 2 );
    REQUIRE( intersected.normals.size( ) == 2 );
    REQUIRE( intersected.cells == std::vector { std::array<size_t, 1> { 0 }, std::array<size_t, 1> { 1 } } );
    REQUIRE( celldata.rst.size( ) == 2 );
    REQUIRE( celldata.offsets.size( ) == 8 );

    CHECK( intersected.vertices[0][0] == Approx( 0.5 ).epsilon( 1e-12 ) );
    CHECK( intersected.vertices[1][0] == Approx( 2.8 ).epsilon( 1e-12 ) );
    CHECK( intersected.normals[0][0] == 1.0 );
    CHECK( intersected.normals[1][0] == -1.0 );
    CHECK( celldata.rst[0][0] == Approx( 0.6 ).epsilon( 1e-12 ) );
    CHECK( celldata.rst[1][0] == Approx( -0.2 ).epsilon( 1e-12 ) );
    CHECK( celldata.offsets == std::vector<size_t> { 0, 1, 1, 1, 1, 1, 2, 2 } );

    auto domain = rayIntersectionDomain<1>( points );

    CHECK( !domain( { -0.6 } ) );
    CHECK(  domain( { -0.49 } ) );
    CHECK(  domain( { 0.49 } ) );
    CHECK( !domain( { 0.56 } ) );
    CHECK( !domain( { 2.0 } ) );
    CHECK( !domain( { 2.7 } ) );
    CHECK(  domain( { 2.82 } ) );
    CHECK(  domain( { 4.0 - 1e-8 } ) );
    CHECK( !domain( { 4.0 + 1e-8 } ) );

    auto p1 = SimplexMesh<1, 0> { };
    auto p2 = SimplexMesh<1, 0> { };
    auto p3 = SimplexMesh<1, 0> { };
    auto p4 = SimplexMesh<1, 0> { };

    p1.vertices = { { 0.0 }, { 1.0, } };
    p1.cells = { { 0 }, { 1 } };
    p1.normals = { { -1.0 }, { 1.0 } };
    p3.vertices = { { -1.0 }, { 2.0 }, { 3.0 } };
    p3.cells = { { 1 }, { 2 }, { 0 } };
    p3.normals = { { 1.0 }, { -1.0 }, { 1.0 } };
    p4.vertices = { { 9.0 } };

    auto merged = mergeSimplexMeshes<1, 0>( { p1, p2, p3, p4 } );

    REQUIRE( merged.ncells( ) == 5 );
    REQUIRE( merged.nvertices( ) == 6 );

    auto expectedVertices = utilities::linearizeVectors( std::vector
        { p1.vertices, p2.vertices, p3.vertices, p4.vertices } );

    auto expectedNormals = utilities::linearizeVectors( std::vector
        { p1.normals, p2.normals, p3.normals, p4.normals } );
    
    auto expectedCells = std::vector<std::array<size_t, 1>>
    {
        { 0 }, { 1 }, { 3 }, { 4 }, { 2 }
    };

    CHECK( merged.vertices == expectedVertices );
    CHECK( merged.normals == expectedNormals );
    CHECK( merged.cells == expectedCells );
}

TEST_CASE( "recoverDomainBoundary_test" )
{
    auto domain = implicit::halfspace<3>( { 4.0, 2.0, 3.1 }, { 3.0, 2.0, 5.0 } );
    auto mesh = makeRefinedGrid<3>( { 2, 1, 2 }, { 3.0, 2.5, 3.2 }, { 1.4, 0.9, 1.3 } );

    // We don't expect to get these exactly since the bisection algorithm 
    // terminates early. They were determined from using many iterations.
    auto expectedXyz = std::vector<std::array<double, 3>>
    {
        { 2.9, 2.15, 3.7 }, { 2.9, 0.9, 4.2 }, { 2.4, 0.9, 4.5 }, 
        { 47.0 / 30.0, 2.15, 4.5 }, { 1.4, 2.4, 4.5 }, { 1.4, 3.4, 4.1 }, 
        { 2.9, 3.4, 3.2 }, { 4.4, 2.15, 2.8 }, { 4.4, 1.9, 2.9 }, 
        { 127.0 / 30.0, 2.15, 2.9 }, { 4.4, 3.4, 2.3 }, { 3.4, 3.4, 2.9 },
        { 4.4, 1.9, 2.9 }, { 2.9, 2.15, 3.7 }, { 127.0 / 30.0, 2.15, 2.9 },
        { 4.4, 0.9, 3.3 }, { 2.9, 0.9, 4.2 }, { 2.9, 3.4, 3.2 }, 
        { 3.4, 3.4, 2.9 }
    };

    auto expectedTriangles = std::vector<std::array<size_t, 3>>
    {
        { 0,  1,  2, }, { 3,  0,  2, }, { 3,  4,  5, }, { 3,  5,  0, },
        { 0,  5,  6, }, { 7,  8,  9, }, { 10, 7,  9, }, { 11, 10, 9, },
        { 12, 13, 14 }, { 12, 15, 13 }, { 15, 16, 13 }, { 14, 17, 18 },
        { 13, 17, 14 },
    };

    for( auto& t : expectedTriangles )
    {
        std::reverse( t.begin( ), t.end( ) );
    }

    auto expectedRst = std::vector<std::array<double, 3>>
    {
        { 1.0, 0.0, 0.0 }, { 1.0, -1.0, 0.625 }, { 1.0 / 3.0, -1.0, 1.0 },
        { -7.0 / 9.0, 0.0, 1.0 }, { -1.0, 0.2, 1.0 }, { -1.0, 1.0, 0.5 },
        { 1.0, 1.0, -0.625 }, { 1.0, 0.0, 0.875 }, { 1.0, -0.2, 1.0 },
        { 7.0 / 9.0, 0.0, 1.0 }, { 1.0, 1.0, 0.25 }, { -1.0 / 3.0, 1.0, 1.0 },
        { 1.0, -0.2, -1.0 }, { -1.0, 0.0, 0.0 }, { 7.0 / 9.0, 0.0, -1.0 },
        { 1.0, -1.0, -0.5 }, { -1.0, -1.0, 0.625 }, { -1.0, 1.0, -0.625 },
        { -1.0 / 3.0, 1.0, -1.0 }
    };

    auto expectedOffsets = std::vector<size_t> 
    { 
        0, 0, 5, 8, 13 
    };

    auto [triangulation, celldata] = recoverDomainBoundary( *mesh, domain, { 1, 2, 1 } );

    CHECK( triangulation.cells== expectedTriangles );
    CHECK( celldata.offsets == expectedOffsets );

    CHECK( triangulation.vertices.size( ) == expectedXyz.size( ) );
    CHECK( celldata.rst.size( ) == expectedRst.size( ) );

    for( size_t ivertex = 0; ivertex < expectedRst.size( ); ++ivertex )
    {
        CHECK( spatial::distance( triangulation.vertices[ivertex], expectedXyz[ivertex] ) < 1.6e-3 );
        CHECK( spatial::distance( celldata.rst[ivertex], expectedRst[ivertex] ) < 2.0e-3 );
    }

    //auto output1 = VtuOutput { "outputs/recoverDomainBoundary_global_mesh" };
    //auto output2 = VtuOutput { "outputs/recoverDomainBoundary_global_triangles" };

    //writeOutput( *mesh, cellmesh::createGrid<3>( ), CellProcessor<3> { }, output1 );
    //writeOutput( *mesh, cellmesh::associatedTriangles( triangulation, celldata ), CellProcessor<3> { }, output2 );
}

TEST_CASE( "triangulation_domain_test" )
{
    auto sphere1 = implicit::sphere<3>( { 1.0, 1.0, 1.0 }, 0.8 );
    auto sphere2 = implicit::sphere<3>( { 1.0, 1.0, 1.0 }, 0.6 );
    auto sphere3 = implicit::sphere<3>( { 1.0, 1.0, 1.0 }, 0.4 );

    auto mesh1 = makeCartesianGrid<3>( { 8, 8, 8 }, { 2.0, 2.0, 2.0 } );
    auto domain1 = implicit::add( implicit::subtract( sphere1, sphere2 ), sphere3 );
    auto triangulation = recoverDomainBoundary( *mesh1, domain1, { 3, 2, 4 } ).first;

    writeVtu( triangulation, "outputs/triangulation.vtu" );

    auto domain2 = rayIntersectionDomain<3>( triangulation );

    CHECK( !domain2( { 0.297, 0.775, 0.645 } ) );
    CHECK( domain2( { 0.87962, 1.40196, 1.6667 } ) );

    auto a = std::array { 0.999, 0.817, 0.429 };
    auto b = std::array { 0.999, 0.805, 0.41 };

    for( size_t i = 0; i < 17; ++i )
    {
        CHECK( domain2( spatial::interpolate<3>( a, b, i / 16.0 ) ) );
    }
       
    a = std::array { 1.004, 0.89, 0.6 };
    b = std::array { 1.004, 0.895, 0.617 };
    
    for( size_t i = 0; i < 13; ++i )
    {
        CHECK( !domain2( spatial::interpolate<3>( a, b, i / 12.0 ) ) );
    }
    
    a = std::array { 0.313, 0.635, 0.802 };
    b = std::array { 0.319, 0.638, 0.775 };

    for( size_t i = 0; i < 11; ++i )
    {
        CHECK( !domain2( spatial::interpolate<3>( a, b, i / 10.0 ) ) );
    }

    a = std::array { 0.6174, 0.6176, 1.1875 };
    b = std::array { 0.6176, 0.6176, 1.22 };

    for( size_t i = 0; i < 11; ++i )
    {
        CHECK( !domain2( spatial::interpolate<3>( a, b, i / 9.0 - 0.054 ) ) );
    }

    a = std::array { 0.6284, 0.4106, 1.3368 };
    b = std::array { 0.6274, 0.4182, 1.3137 };

    for( size_t i = 0; i < 11; ++i )
    {
        CHECK( domain2( spatial::interpolate<3>( a, b, i / 9.0 - 0.052 ) ) );
    }

    a = std::array { 0.902, 1.149, 1.3524 };
    b = std::array { 0.911, 1.157, 1.315 };

    for( size_t i = 1; i < 12; ++i )
    {
        CHECK( domain2( spatial::interpolate<3>( a, b, i / 10.0 ) ) );
    }

    auto generator = spatial::makeGridPointGenerator( array::makeSizes<3>( 10 ),
        array::make<3>( 1.8 ), array::make<3>( 0.1 ) );
    
    bool allcorrect = true;

    nd::execute( array::makeSizes<3>( 10 ), [&]( std::array<size_t, 3> ijk )
    {
        allcorrect = allcorrect && domain1( generator( ijk ) ) == domain2( generator( ijk ) );
    } );
    
    CHECK( allcorrect );

    //auto mesh2 = makeCartesianGrid<3>( { 51, 51, 51 }, { 2.0, 2.0, 2.0 } );
    //writeOutput( *mesh2, cellmesh::domain( domain2, { 4, 4, 4 } ), 
    //    CellProcessor<3> { }, VtuOutput { "outputs/recovered.vtu" } );
}

namespace
{

auto numberOfTetrahedra( size_t cutState )
{
    return marching::tetrahedra[cutState].size( ) / 4;
}

auto marchingCubesReferenceVertex( size_t vertexIndex, bool shift = false )
{
    //auto random1 = std::array
    //{
    //    7.42, -1.42,  0.44, -1.3 , -4.76,  3.24, -1.5 ,  0.26, -9.  ,
    //    2.08,  6.56,  5.78, -6.82, -8.14, -2.66, -6.98,  9.58, -0.02,
    //    3.86, -4.18,  6.52,  2.0 , -0.8 ,  9.52
    //};

    auto random2 = std::array
    {
        -8.08, -5.9 ,  4.32,  2.36, -3.56,  6.14, -0.64, -3.86, -8.88,
         3.7 , -0.72,  5.96
    };

    auto cornerVertex = []( size_t index )
    {
        return 2.0 * array::convert<double>( nd::binaryUnravel<size_t, 3>( index ) ) - 1.0;
    };

    if( vertexIndex < 8 )
    {
        return cornerVertex( vertexIndex );
    }
    else
    {
        auto v0 = cornerVertex( marching::numbering[vertexIndex - 8][0] );
        auto v1 = cornerVertex( marching::numbering[vertexIndex - 8][1] );

        // Random interpolation coordinates
        auto t = 0.5 + ( shift ? 0.6 * 0.05 * random2[vertexIndex - 8] : 0.0 );

        return spatial::interpolate( v0, v1, t );
    }
}

auto marchingCubesReferenceCell( size_t cutState, size_t tetIndex, bool shift = false )
{
    auto tetVertices = std::array<std::array<double, 3>, 4> { };

    // Gather vertices: Corners if index < 8, interpolrate edge otherwise
    for( size_t iTetVertex = 0; iTetVertex < 4; ++iTetVertex )
    {
        auto globalVertex = marching::tetrahedra[cutState][tetIndex * 4 + iTetVertex];

        tetVertices[iTetVertex] = marchingCubesReferenceVertex( globalVertex, shift );
    }

    return tetVertices;
}

} // namespace

TEST_CASE( "MarchingCubes_orientation_test" )
{
    CHECK( marching::tetrahedra.size( ) == 256 );

    auto rst = CoordinateList<3> { };
    auto weights = std::vector<double> { };
    auto cache = QuadraturePointCache { };

    auto sizesCorrect = true;
    auto detCorrect = true;
    auto quadratureCorrect = true;

    // Loop over different cut configurations
    for( size_t cutIndex = 0; cutIndex < 256; ++cutIndex )
    {
        auto ncells = numberOfTetrahedra( cutIndex );

        if( cutIndex > 0 && cutIndex + 1 < 256 )
        {
            auto remainder = ( marching::tetrahedra[cutIndex].size( ) % 4 );

            sizesCorrect = sizesCorrect && ( cutIndex == 0 || ncells > 0 );
            sizesCorrect = sizesCorrect && remainder == 0;
        }

        // Loop over all tetrahedra of this cut configuration
        for( size_t itet = 0; itet < ncells; ++itet )
        {
            auto tet = marchingCubesReferenceCell( cutIndex, itet );

            // Check mapping 
            auto mapping = SimplexMapping<3> { tet };
            auto volume = spatial::tetrahedronVolume( tet[0], tet[1], tet[2], tet[3] );

            detCorrect = detCorrect && volume > 1e-2;
            detCorrect = detCorrect && std::abs( mapping.detJ( { } ) - 6.0 * volume ) < 1e-12;

            // Check quadrature
            utilities::resize0( rst, weights );

            simplexQuadrature<3>( { 2, 2, 2 }, rst, weights, cache );

            for( size_t iqp = 0; iqp < rst.size( ); ++iqp )
            {
                weights[iqp] *= mapping.detJ( rst[iqp] );
            }

            auto integratedVolume = std::accumulate( weights.begin( ), weights.end( ), 0.0 );

            quadratureCorrect = quadratureCorrect && std::abs( integratedVolume - volume ) < 1e-12;
        }
    }

    CHECK( detCorrect );
    CHECK( sizesCorrect );
    CHECK( quadratureCorrect );
}

//auto writeVolumeCells( size_t index, std::string name )
//{ 
//    auto points = std::vector<double> { };
//    auto connectivity = std::vector<std::int64_t> { };
//    auto offsets = std::vector<std::int64_t> { };
//    auto types = std::vector<std::int8_t> { };
//    auto ncells = numberOfTetrahedra( index );
//
//    auto addCell = [&]( auto vertices )
//    {
//        for( size_t i = 0; i < 4; ++i )
//        {
//            connectivity.push_back( points.size( ) / 3 );
//            points.insert( points.end( ), vertices[i].begin( ), vertices[i].end( ) );
//        }
//
//        offsets.push_back( connectivity.size( ) );
//        types.push_back( 10 );
//    };
//
//    for( size_t itet = 0; itet < ncells; ++itet )
//    {
//        addCell( marchingCubesReferenceCell( index, itet, true ) );
//    }
//
//    //auto extraIndices = std::span { extraTetrahedraIndices };
//    //auto extraData = std::span { extraTetrahedraData };
//
//    //auto additional = extraData.subspan( extraIndices[index],
//    //    extraIndices[index + 1] - extraIndices[index] );
//    auto additional = extraTetrahedra[index];
//
//    for( size_t itet = 0; itet < additional.size( ) / 4; ++itet )
//    {
//        auto vertices = std::array
//        {
//            marchingCubesReferenceVertex( additional[itet * 4 + 0], true ),
//            marchingCubesReferenceVertex( additional[itet * 4 + 1], true ),
//            marchingCubesReferenceVertex( additional[itet * 4 + 2], true ),
//            marchingCubesReferenceVertex( additional[itet * 4 + 3], true ),
//        };
//
//        addCell( vertices );
//    }
//
//    writeVtu( "outputs/colume_" + name + ".vtu", points, connectivity, offsets, types );
//};
//
//auto writeTriangles( size_t index, std::string name )
//{ 
//    auto points = std::vector<double> { };
//    auto connectivity = std::vector<std::int64_t> { };
//    auto offsets = std::vector<std::int64_t> { };
//    auto types = std::vector<std::int8_t> { };
//
//    auto addCell = [&]( auto vertices )
//    {
//        for( size_t i = 0; i < 3; ++i )
//        {
//            connectivity.push_back( points.size( ) / 3 );
//            points.insert( points.end( ), vertices[i].begin( ), vertices[i].end( ) );
//        }
//
//        offsets.push_back( connectivity.size( ) );
//        types.push_back( 5 );
//    };
//
//    auto triangles = std::span { triangleData }.subspan( 3 * triangleIndices[index],
//        3 * ( triangleIndices[index + 1] - triangleIndices[index] ) );
//
//    for( size_t itri = 0; itri < triangles.size( ) / 3; ++itri )
//    {
//        auto vertices = std::array
//        {
//            marchingCubesReferenceVertex( triangles[3 * itri + 0] + 8, true ),
//            marchingCubesReferenceVertex( triangles[3 * itri + 1] + 8, true ),
//            marchingCubesReferenceVertex( triangles[3 * itri + 2] + 8, true ),
//        };
//
//        addCell( vertices );
//    }
//
//    writeVtu( "outputs/triangles_" + name + ".vtu", points, connectivity, offsets, types );
//};

// Volume of cells with inverted cut state should add to one
TEST_CASE( "MarchingCubes_volumesum_test" )
{
    auto volumeEqual = true;

    auto computeVolume = [&]( size_t cutIndex )
    { 
        auto ncells = numberOfTetrahedra( cutIndex );
        auto volume1 = 0.0, volume2 = 0.0;

        // Loop over all tetrahedra of this cut configuration
        for( size_t itet = 0; itet < ncells; ++itet )
        {
            auto vertices = marchingCubesReferenceCell( cutIndex, itet, true );
            
            volume1 += spatial::tetrahedronVolume( vertices[0], 
                vertices[1], vertices[2], vertices[3] );
            
            //if( SimplexMapping<3> { vertices }.detJ( { } ) < 0 )  std::cout << "flip1: " << cutIndex << " / " << itet << std::endl;

            volume2 += 1.0 / 6.0 * SimplexMapping<3> { vertices }.detJ( { } );
        }

        auto additional = extraTetrahedra[cutIndex];
        //auto extraIndices = std::span { extraTetrahedraIndices };
        //auto extraData = std::span { extraTetrahedraData };
        //
        //auto additional = extraData.subspan( extraIndices[cutIndex],
        //    extraIndices[cutIndex + 1] - extraIndices[cutIndex] );
        
        for( size_t itet = 0; itet < additional.size( ) / 4; ++itet )
        {
            auto vertices = std::array<std::array<double, 3>, 4> { };

            for( size_t i = 0; i < 4; ++i )
            {
                vertices[i] = marchingCubesReferenceVertex( additional[itet * 4 + i], true );
            }

            auto thisVolume = spatial::tetrahedronVolume( vertices[0], 
                vertices[1], vertices[2], vertices[3] );

            auto detJ = SimplexMapping<3> { vertices }.detJ( { } );

            //if( detJ < 0 )  std::cout << "flip2: " << cutIndex << " / " << itet << std::endl;

            volume1 += thisVolume;
            volume2 += 1.0 / 6.0 * detJ;

            volumeEqual = volumeEqual && detJ > 0.0;
        }

        volumeEqual = volumeEqual && std::abs( volume2 - volume1 ) < 1e-10;

        CHECK( volumeEqual );

        return volume2;
    };


    // Loop over different cut configurations
    for( size_t cutIndex = 0; cutIndex < 256 / 2; ++cutIndex )
    {
        auto volume1 = computeVolume( cutIndex );
        auto volume2 = computeVolume( 255 - cutIndex );

        ////////////////////////////////////////////////////////
        //if( std::abs( volume1 + volume2 - 8.0 ) > 1e-10 )
        //{
        //    std::cout << "Different at " << std::endl;
        //    std::cout << "    index 1: " << cutIndex << " (" << std::bitset<8> { cutIndex } << ")" << std::endl;
        //    std::cout << "    index 2: " << 255 - cutIndex << " (" << std::bitset<8> { 255 - cutIndex } << ")" << std::endl;
        //    std::cout << "    volume1 (" << volume1 << ") + volume2 (" << volume2 << ") = " << volume1 + volume2 << std::endl;

        //}
        //writeVolumeCells( cutIndex, "A_" + std::to_string( cutIndex ) );
        //writeVolumeCells( 255 - cutIndex, "B_" + std::to_string( cutIndex ) );
        //writeTriangles( cutIndex, "A_" + std::to_string( cutIndex ) );
        //writeTriangles( 255 - cutIndex, "B_" + std::to_string( cutIndex ) );
        ////////////////////////////////////////////////////////

        CHECK( volume1 + volume2 == Approx( 8.0 ).epsilon( 1e-12 ) );
    }

    CHECK( volumeEqual );
}

} // namespace mlhp
