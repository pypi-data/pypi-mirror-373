// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/triangulation.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/refinement.hpp"

#include "mlhp/core/postprocessing.hpp"

namespace mlhp
{

using namespace marching;

TEST_CASE( "kdtree3D_test1" )
{
    auto sphere = implicit::sphere<3>( { 0.0, 0.0, 0.0 }, 0.5 );
    auto mesh = CartesianGrid<3>( { 1, 1, 1 }, { 1.02, 1.02, 1.02 }, { -0.51, -0.51, -0.51 } );
    auto triangulation = recoverDomainBoundary( mesh, sphere, { 2, 2, 2 }, 12 ).first;
    
    CHECK( triangulation.ncells( ) == 8 );

    writeVtu( triangulation, testing::outputPath( "core/kdtree3D_test_triangulation.vtu" ) );

    auto parameters = kdtree::Parameters
    {
        .KT = 1.0,
        .KL = 2.0,
        .emptyCellBias = 0.8
    };

    auto bounds = triangulation.boundingBox( );
    auto events = kdtree::createSortedEventList( kdtree::makeObjectProvider<3, 2>( triangulation ), bounds );

    for( size_t axis = 0; axis < 3; ++axis )
    {   
        CHECK( bounds[0][axis] > -0.5 );
        CHECK( bounds[0][axis] < -0.4999 );

        CHECK( bounds[1][axis] < 0.5 );
        CHECK( bounds[1][axis] > 0.4999 );
    }

    bounds = std::array { array::make<3>( -0.5 ), array::make<3>( 0.5 ) };

    for( size_t i = 0; i <= 4; i += 4 )
    {
        for( size_t axis = 0; axis < 3; ++axis )
        {
            auto ratios = kdtree::computeSurfaceAreaRatios<3>( bounds, axis, i / 4.0 - 0.5 );
        
            CHECK( ratios[0] == Approx( ( i + 2.0 ) / 6.0 ).epsilon( 1e-10 ) );
            CHECK( ratios[1] == Approx( ( 6.0 - i ) / 6.0 ).epsilon( 1e-10 ) );
            CHECK( ratios[2] == Approx( i / 4.0 ).margin( 1e-10 ) );
        }
    }

    auto [position, axis, side, C] = kdtree::findPlane( triangulation.ncells( ), bounds, events, parameters );

    CHECK( position == Approx( 0.0 ).margin( 1e-12 ) );
    CHECK( axis == 0 );

    auto tree = buildKdTree( triangulation, parameters );
    
    writeVtu( tree, testing::outputPath( "core/kdtree3D_test_kdtree.vtu" ) );

    auto ray0 = std::array { std::array { 0.5, 0.1, -0.1 }, std::array { 0.4, 0.2, -0.3 } };
    auto ray1 = std::array { std::array { 0.0, 0.0, 0.0 }, std::array { 3.2, 0.53, -1.02 } };
    auto ray2 = std::array { std::array { 0.5, 0.1, -0.1 }, std::array { -0.4, -0.2, 0.2 } };

    auto target = std::vector<size_t> { };

    //CHECK( countIntersections( tree, triangulation, ray0[0], ray0[1], spatial::invert( ray0[1] ), target ) == 0 );
    //CHECK( countIntersections( tree, triangulation, ray1[0], ray1[1], spatial::invert( ray1[1] ), target ) == 1 );
    //CHECK( countIntersections( tree, triangulation, ray2[0], ray2[1], spatial::invert( ray2[1] ), target ) == 2 );

    auto domain = rayIntersectionDomain<3>( &triangulation );

    CHECK( domain( ray0[0] ) == false );
    CHECK( domain( ray1[0] ) == true  );
    CHECK( domain( ray2[0] ) == false );
}

TEST_CASE( "stlkdtree_test" )
{
    auto filename = testing::testfilePath( "core/csg_binary.stl" );

    auto vertices = readStl( filename );

    REQUIRE( vertices.size( ) == 3 * 2282 );

    auto triangulation = createTriangulation<3>( vertices );

    REQUIRE( triangulation.ncells( ) == 2282 );
    REQUIRE( triangulation.nvertices( ) == 3 * 2282 );

    auto rotate = spatial::rotate( { 0.2, 0.1, 0.3 }, 0.334 );
    for( auto& v : triangulation.vertices )
    {
        v = rotate( v );
    }

    writeVtu( triangulation, testing::outputPath( "core/stlkdtree_test_triangulation.vtu" ) );

    auto parameters = kdtree::Parameters
    {
        .maxdepth = 14,
        .KT = 1.0,
        .KL = 2.0,
        .emptyCellBias = 0.8
    };

    auto tree = buildKdTree( triangulation, parameters );

    // Test consistency with earlier runs
    CHECK( tree.nfull( ) == 4055 );
    CHECK( tree.nleaves( ) == 2028 );

    writeVtu( tree, testing::outputPath( "core/stlkdtree_test_kdtree.vtu" ) );
}

TEST_CASE( "kdtree3D_collection1_test" )
{
    auto parameters = kdtree::Parameters
    {
        .KT = 1.0,
        .KL = 3.0,
        .emptyCellBias = 0.8
    };

    // Test 1
    auto triangulation = Triangulation<3>
    {
        .vertices = { { -5.0, 2.11018, -2.55874 },
                      { -5.0, 1.41421, -1.41421 },
                      { -5.0, 1.41421, -1.41421 } },
        .cells = { { 0, 1, 2 } }
    };
    
    auto tree = buildKdTree( triangulation, parameters );

    // Test 2
    triangulation.vertices = { { 4.0, 4.0, 5.0 },
                               { 5.0, 1.0, 5.0 },
                               { 2.0, 4.0, 5.0 },
                               { 0.0, 0.0, 0.0 } };

    tree = buildKdTree( triangulation, parameters );
    
    // Test 3
    triangulation.vertices =
    {
        { 1.8879256248474121094, -0.66010379791259765625, -1.8879256248474121094 },
        { 5, -0.7653668522834777832, -1.8477590084075927734 },
        { 5, -0.39018064737319946289, -1.9615705013275146484 },
        { 1.9717823266983032227, -0.33477520942687988281, -1.9717823266983032227 },
        { 1.8879256248474121094, -0.66010379791259765625, -1.8879256248474121094 },
        { 5, -0.39018064737319946289, -1.9615705013275146484 },
        { 2, -4.8985874103406714178e-16, -2 },
        { 1.9717823266983032227, -0.33477520942687988281, -1.9717823266983032227 },
        { 5, -4.8985874103406714178e-16, -2 },
    };

    triangulation.cells = { { 0, 1, 2 }, { 3, 4, 5 }, { 6, 7, 8 } };

    tree = buildKdTree( triangulation, parameters );
    
    // Test 4
    parameters.emptyCellBias = 1.0;

    triangulation.vertices =
    {
        { -5.0, 2.11018, -2.55874 }, { -5.0, 1.41421, -1.41421 }, { -5.0, 2.47604, -2.20664 },
        { -5.0, 2.47604, -2.20664 }, { -5.0, 1.66294, -1.11114 }, { -5.0, 2.78386, -1.80281 },
        { -5.0, 2.78386, -1.80281 }, { -5.0, 1.66294, -1.11114 }, { -5.0, 3.02643, -1.35673 }
    };
    
    triangulation.cells = { { 0, 1, 2 }, { 3, 4, 5 }, { 6, 7, 8 } };

    tree = buildKdTree( triangulation, parameters );

    // Test 5
    triangulation.vertices = { { 0.0, 0.0, 0.0 },
                               { 0.0, 0.0, 1.0 },
                               { 0.0, 1.0, 0.0 },
                               { 0.0, 1.0, 1.0 } };

    triangulation.cells = { { 0, 1, 2 }, { 1, 2, 3 } };

    tree = buildKdTree( triangulation, parameters );

    // Check consistency with previous versions
    CHECK( tree.nleaves( ) == 1 );
    CHECK( tree.nfull( ) == 1 );

    // Test 6
    triangulation.vertices.push_back( { 1.0, 0.0, 0.0 } );
    triangulation.vertices.push_back( { 1.0, 0.0, 1.0 } );
    triangulation.vertices.push_back( { 1.0, 1.0, 0.0 } );
    triangulation.vertices.push_back( { 1.0, 1.0, 1.0 } );
        
    triangulation.cells.push_back( { 4, 0, 5 } );

    tree = buildKdTree( triangulation, parameters );

    // Check consistency with previous versions
    CHECK( tree.nleaves( ) == 3 );
    CHECK( tree.nfull( ) == 5 );

    // Test 7
    triangulation.cells.push_back( { 0, 5, 1 } );
    
    tree = buildKdTree( triangulation, parameters );

    // Check consistency with previous versions
    CHECK( tree.nleaves( ) == 3 );
    CHECK( tree.nfull( ) == 5 );

    // Test 8
    triangulation.cells = { { 0, 1, 2 }, { 1, 2, 3 }, { 6, 7, 5 }, { 6, 4, 5 } };
        
    tree = buildKdTree( triangulation, parameters );

    // Check consistency with previous versions
    CHECK( tree.nleaves( ) == 3 );
    CHECK( tree.nfull( ) == 5 );

    // Test 9
    triangulation.cells.push_back( { 0, 1, 4 } );
    triangulation.cells.push_back( { 1, 5, 4 } );
    triangulation.cells.push_back( { 7, 6, 3 } );
    triangulation.cells.push_back( { 6, 2, 3 } );
    
    tree = buildKdTree( triangulation, parameters );

    // Check consistency with previous versions
    CHECK( tree.nleaves( ) == 5 );
    CHECK( tree.nfull( ) == 9 );

    //writeVtu( triangulation, testing::outputPath( "core/asdf1.vtu" ) );
    //writeVtu( tree, testing::outputPath( "core/asdf2.vtu" ) );
}

TEST_CASE( "kdtree3D_collection2_test" )
{
    // Test 1
    auto triangulation = Triangulation<3> 
    {
        .vertices = 
        {
            // Triangle 1
            { -2.91957, -5.21413, -0.537592 }, 
            { -3.49319, -4.86072, -0.413559 }, 
            { -3.26535, -4.90837, -1.116000 },

            // Triangle 2
            { -2.91957, -5.21413, -0.537592 }, 
            { -3.26535, -4.90837, -1.116000 }, 
            { -2.67528, -5.22639, -1.236000 },

            // Triangle 3
            { -3.11945, -5.12255,  0.168992 }, 
            { -3.49319, -4.86072, -0.413559 }, 
            { -2.91957, -5.21413, -0.537592 }
        },
        .cells = 
        { 
            { 0, 1, 2 }, 
            { 3, 4, 5 }, 
            { 6, 7, 8 } 
        }
    };

    auto parameters = kdtree::Parameters
    {
        .KT = 1.0,
        .KL = 2.0,
        .emptyCellBias = 0.8
    };

    auto bounds = std::array 
    { 
        std::array { -3.4886750408909650, -5.4547228409978157, -1.1159960722711717 },
        std::array { -2.9507212424862890, -4.9083675113346663, -0.4274709028296754 } 
    };

    auto tree = buildKdTree( triangulation, bounds, parameters );

    // Check consistency with previous versions
    CHECK( tree.nleaves( ) == 6 );
    CHECK( tree.nfull( ) == 11 );

    // Test 2
    triangulation.vertices = 
    {
        // Triangle 0
        { -2.9195702583855638, -5.2141252873650217, -0.53759185669013021 },
        { -3.4931873728092619, -4.8607213090326624, -0.41355940736073654 },
        { -3.2653450541502438, -4.9083675113346663, -1.1159960722711717 },

        // Triangle 1
        { -3.1194486224127966, -5.1225461472428071, 0.16899243713427098 },
        { -3.4931873728092619, -4.8607213090326624, -0.41355940736073654 },
        { -2.9195702583855638, -5.2141252873650217, -0.53759185669013021 },

        // Triangle 2
        { -2.5293855001662098, -5.4405704446018230, 0.048989718743441268 },
        { -3.1194486224127966, -5.1225461472428071, 0.16899243713427098 },
        { -2.9195702583855638, -5.2141252873650217, -0.53759185669013021 },

        // Triangle 3
        { -2.5293855001662098, -5.4405704446018230, 0.048989718743441268 },
        { -2.9195702583855638, -5.2141252873650217, -0.53759185669013021 },
        { -2.3078922007745204, -5.4995554477160224, -0.65461600692019017 },
    };

    triangulation.cells =
    {
        { 0, 1, 2 }, { 3, 4, 5 }, { 6, 7, 8 }, { 9, 10, 11 }
    };

    bounds = { std::array { -3.2653450541502438, -5.2858202580120075, -0.53759185669013021 },
               std::array { -2.7854534220924578, -4.9360464884569764, -0.42747090282967543 } };

    auto expected = std::vector<kdtree::Event>
    {
        { .itriangle = 3, .position = -5.2858202580120075,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 0
        { .itriangle = 2, .position = -5.2566366067728394,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 1
        { .itriangle = 3, .position = -5.2141252873650217,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 4
        { .itriangle = 0, .position = -5.2141252873650217,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 2
        { .itriangle = 1, .position = -5.2141252873650217,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 3
        { .itriangle = 2, .position = -5.1998527053785262,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 5
        { .itriangle = 1, .position = -5.0010943554810119,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 6
        { .itriangle = 0, .position = -4.9904802014908736,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 7
        { .itriangle = 0, .position = -3.2653450541502438,  .axis = 0, .type = kdtree::Event::Type::Starts }, // 8
        { .itriangle = 1, .position = -3.2653450541502438,  .axis = 0, .type = kdtree::Event::Type::Starts }, // 9
        { .itriangle = 2, .position = -2.9507212424862890,  .axis = 0, .type = kdtree::Event::Type::Starts }, // 10
        { .itriangle = 0, .position = -2.9195702583855638,  .axis = 0, .type = kdtree::Event::Type::Ends   }, // 11
        { .itriangle = 1, .position = -2.9195702583855638,  .axis = 0, .type = kdtree::Event::Type::Ends   }, // 12
        { .itriangle = 3, .position = -2.9195702583855638,  .axis = 0, .type = kdtree::Event::Type::Starts }, // 13
        { .itriangle = 2, .position = -2.8463195468793820,  .axis = 0, .type = kdtree::Event::Type::Ends   }, // 14
        { .itriangle = 3, .position = -2.7854534220924578,  .axis = 0, .type = kdtree::Event::Type::Ends   }, // 15
        { .itriangle = 0, .position = -0.53759185669013021, .axis = 2, .type = kdtree::Event::Type::Starts }, // 16
        { .itriangle = 1, .position = -0.53759185669013021, .axis = 2, .type = kdtree::Event::Type::Starts }, // 17
        { .itriangle = 2, .position = -0.53759185669013021, .axis = 2, .type = kdtree::Event::Type::Starts }, // 18
        { .itriangle = 3, .position = -0.53759185669013021, .axis = 2, .type = kdtree::Event::Type::Starts }, // 19
        { .itriangle = 0, .position = -0.46282544237532697, .axis = 2, .type = kdtree::Event::Type::Ends   }, // 20
        { .itriangle = 1, .position = -0.42747090282967543, .axis = 2, .type = kdtree::Event::Type::Ends   }, // 21
        { .itriangle = 2, .position = -0.42747090282967543, .axis = 2, .type = kdtree::Event::Type::Ends   }, // 22
        { .itriangle = 3, .position = -0.42747090282967543, .axis = 2, .type = kdtree::Event::Type::Ends   }, // 23
    };

    auto computed = kdtree::createSortedEventList( kdtree::makeObjectProvider<3, 2>( triangulation ), bounds );

    REQUIRE( computed.size( ) == expected.size( ) );

    for( size_t i = 0; i < expected.size( ); ++i )
    {
        // These might be ambiguous again since some can be ordered differently
        CHECK( computed[i].axis == expected[i].axis );
        CHECK( computed[i].itriangle == expected[i].itriangle );
        CHECK( computed[i].type == expected[i].type );
        CHECK( computed[i].position == Approx( expected[i].position ).epsilon( 1e-10 ) );
    }

    auto plane = kdtree::findPlane( 4, bounds, expected, parameters );

    CHECK( std::get<0>( plane ) == Approx( -4.9904802014908736 ).epsilon( 1e-10 ) );
    CHECK( std::get<1>( plane ) == 1 );
    CHECK( std::get<2>( plane ) == 1 );
    CHECK( std::get<3>( plane ) == Approx( 6.4070502900101651 ).epsilon( 1e-10 ) );

    tree = buildKdTree( triangulation, bounds, parameters );

    // Check consistency with previous versions
    CHECK( tree.nleaves( ) == 5 );
    CHECK( tree.nfull( ) == 9 );

    // Test 3
    bounds[1][1] = -4.9904802014908736;

    plane = kdtree::findPlane( 4, bounds, expected, parameters );

    CHECK( std::get<0>( plane ) == Approx( -2.9195702583855638 ).epsilon( 1e-10 ) );
    CHECK( std::get<1>( plane ) == 0 );
    //CHECK( std::get<2>( plane ) == 1 );
    CHECK( std::get<3>( plane ) == Approx( 7.0939417633010464 ).epsilon( 1e-10 ) );

    tree = buildKdTree( triangulation, bounds, parameters );

    CHECK( tree.nleaves( ) == 4 );
    CHECK( tree.nfull( ) == 7 );

    // Test 4
    triangulation.vertices = 
    {
        // Triangle 0
        { -2.5831159267019626, -4.0717663560820503, -3.5704663720099239 },
        { -2.7199714597136913, -3.5309890187584987, -4.0166990191093443 },
        { -2.2355307324628306, -3.7570457855251522, -4.1093805509412409 },

        // Triangle 1
        { -2.5831159267019626, -4.0717663560820503, -3.5704663720099239 },
        { -3.0900288111779264, -3.7985574189739277, -3.4673741672587663 },
        { -2.7199714597136913, -3.5309890187584987, -4.0166990191093443 },
    };
    
    triangulation.cells =
    {
        { 0, 1, 2 }, { 3, 4, 5 }
    };

    bounds = { std::array { -2.8772678824505578, -4.4679701732611781, -4.0633284723583438 }, 
               std::array { -2.4762421449649121, -3.6447215308266472, -3.7361690466022210 } };

    expected = std::vector<kdtree::Event>
    {
        { .itriangle = 0, .position = -4.0633284723583438, .axis = 2, .type = kdtree::Event::Type::Starts }, // 0
        { .itriangle = 0, .position = -3.9749976267940088, .axis = 1, .type = kdtree::Event::Type::Starts }, // 1
        { .itriangle = 1, .position = -3.9228504858615989, .axis = 2, .type = kdtree::Event::Type::Starts }, // 2
        { .itriangle = 1, .position = -3.8709557436450615, .axis = 1, .type = kdtree::Event::Type::Starts }, // 3
        { .itriangle = 0, .position = -3.7361690466022210, .axis = 2, .type = kdtree::Event::Type::Ends   }, // 4
        { .itriangle = 1, .position = -3.7361690466022210, .axis = 2, .type = kdtree::Event::Type::Ends   }, // 5
        { .itriangle = 0, .position = -3.6447215308266472, .axis = 1, .type = kdtree::Event::Type::Ends   }, // 6
        { .itriangle = 1, .position = -3.6447215308266472, .axis = 1, .type = kdtree::Event::Type::Ends   }, // 7
        { .itriangle = 1, .position = -2.8772678824505578, .axis = 0, .type = kdtree::Event::Type::Starts }, // 8
        { .itriangle = 0, .position = -2.6911889599941503, .axis = 0, .type = kdtree::Event::Type::Starts }, // 9
        { .itriangle = 1, .position = -2.6339354442791816, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 10
        { .itriangle = 0, .position = -2.4762421449649121, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 11
    };
    
    computed = kdtree::createSortedEventList( kdtree::makeObjectProvider<3, 2>( triangulation ), bounds );

    REQUIRE( computed.size( ) == expected.size( ) );

    for( size_t i = 0; i < expected.size( ); ++i )
    {
        CHECK( computed[i].axis == expected[i].axis );
        CHECK( computed[i].itriangle == expected[i].itriangle );
        CHECK( computed[i].type == expected[i].type );
        CHECK( computed[i].position == Approx( expected[i].position ).epsilon( 1e-10 ) );
    }

    plane = kdtree::findPlane( 2, bounds, expected, parameters );

    CHECK( std::get<0>( plane ) == Approx( -3.9749976267940088 ).epsilon( 1e-10 ) );
    CHECK( std::get<1>( plane ) == 1 );
    CHECK( std::get<2>( plane ) == 1 );
    CHECK( std::get<3>( plane ) == Approx( 2.4278672237557739 ).epsilon( 1e-10 ) );

    tree = buildKdTree( triangulation, bounds, parameters );

    // Check consistency with previous versions
    CHECK( tree.nleaves( ) == 2 );
    CHECK( tree.nfull( ) == 3 );
        
    // Test 5
    triangulation.vertices = 
    {
        // Triangle 0
        { -4.1820505973852553, -4.0031549965131896, -1.5764525244930594 },
        { -4.0851047343478974, -4.2440629107954368, -1.1401090583491651 },
        { -4.4167358320431029, -2.9815856996912329, -0.77626740049352849 },

        // Triangle 1
        { -4.0703168234402751, -4.1249937111780319, -1.5546528982786698 },
        { -4.1820505973852553, -4.0031549965131896, -1.5764525244930594 },
        { -3.7776469080486654, -4.0947949922277775, -2.2275628575393966 },

        // Triangle 2
        { -4.0703168234402751, -4.1249937111780319, -1.5546528982786698 },
        { -4.0851047343478974, -4.2440629107954368, -1.1401090583491651 },
        { -4.1820505973852553, -4.0031549965131896, -1.5764525244930594 },
    };
    
    triangulation.cells =
    {
        { 0, 1, 2 }, { 3, 4, 5 }, { 6, 7, 8 }
    };
    
    bounds = { std::array { -4.1820505973852553, -4.1249937111780319, -1.5764525244930594 },
               std::array { -4.0703168234402751, -4.0031549965131896, -1.5546528982786698 } };

    
    expected = std::vector<kdtree::Event>
    {
        { .itriangle = 0, .position = -4.1820505973852553, .axis = 0, .type = kdtree::Event::Type::Starts }, // 0
        { .itriangle = 1, .position = -4.1820505973852553, .axis = 0, .type = kdtree::Event::Type::Starts }, // 1
        { .itriangle = 2, .position = -4.1820505973852553, .axis = 0, .type = kdtree::Event::Type::Starts }, // 2
        { .itriangle = 0, .position = -4.1772072028091376, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 3
        { .itriangle = 1, .position = -4.1249937111780319, .axis = 1, .type = kdtree::Event::Type::Starts }, // 4
        { .itriangle = 2, .position = -4.1249937111780319, .axis = 1, .type = kdtree::Event::Type::Starts }, // 5
        { .itriangle = 1, .position = -4.0703168234402751, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 6
        { .itriangle = 2, .position = -4.0703168234402751, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 7
        { .itriangle = 0, .position = -4.0151907043693242, .axis = 1, .type = kdtree::Event::Type::Starts }, // 8
        { .itriangle = 0, .position = -4.0031549965131896, .axis = 1, .type = kdtree::Event::Type::Ends   }, // 9
        { .itriangle = 1, .position = -4.0031549965131896, .axis = 1, .type = kdtree::Event::Type::Ends   }, // 10
        { .itriangle = 2, .position = -4.0031549965131896, .axis = 1, .type = kdtree::Event::Type::Ends   }, // 11
        { .itriangle = 0, .position = -1.5764525244930594, .axis = 2, .type = kdtree::Event::Type::Starts }, // 12
        { .itriangle = 1, .position = -1.5764525244930594, .axis = 2, .type = kdtree::Event::Type::Starts }, // 13
        { .itriangle = 2, .position = -1.5764525244930594, .axis = 2, .type = kdtree::Event::Type::Starts }, // 14
        { .itriangle = 0, .position = -1.5546528982786698, .axis = 2, .type = kdtree::Event::Type::Ends   }, // 15
        { .itriangle = 1, .position = -1.5546528982786698, .axis = 2, .type = kdtree::Event::Type::Ends   }, // 16
        { .itriangle = 2, .position = -1.5546528982786698, .axis = 2, .type = kdtree::Event::Type::Ends   }, // 17
    };
    
    computed = kdtree::createSortedEventList( kdtree::makeObjectProvider<3, 2>( triangulation ), bounds );

    REQUIRE( computed.size( ) == expected.size( ) );

    for( size_t i = 0; i < expected.size( ); ++i )
    {
        CHECK( computed[i].axis == expected[i].axis );
        CHECK( computed[i].itriangle == expected[i].itriangle );
        CHECK( computed[i].type == expected[i].type );
        CHECK( computed[i].position == Approx( expected[i].position ).epsilon( 1e-10 ) );
    }

    plane = kdtree::findPlane( 3, bounds, expected, parameters );

    CHECK( std::get<0>( plane ) == Approx( -4.1772072028091376 ).epsilon( 1e-10 ) );
    CHECK( std::get<1>( plane ) == 0 );
    CHECK( std::get<2>( plane ) == 1 );
    CHECK( std::get<3>( plane ) == Approx( 5.9263487909695050 ).epsilon( 1e-10 ) );

    parameters.maxdepth = 4;

    tree = buildKdTree( triangulation, bounds, parameters );
    
    // Check consistency with previous versions
    CHECK( tree.nleaves( ) == 7 );
    CHECK( tree.nfull( ) == 13 );

} // kdtree3D_collection2_test

TEST_CASE( "kdtree3D_collection3_test" )
{
    //std::cout << "Not working" << std::endl;

    auto parameters = kdtree::Parameters
    {
        .maxdepth = 80,
        .KT = 1.0,
        .KL = 2.0,
        .emptyCellBias = 0.8
    };

    // Test 1
    auto triangulation = Triangulation<3>
    {
        .vertices = 
        { 
            { 11.391693115234375,     -28.377023696899414062, 5.27508544921875 }, // 0
            { -3.3503148555755615234, -21.11417388916015625,  5.27508544921875 }, // 1
            { 13.156062126159667969,  -29.138729095458984375, 5.27508544921875 }, // 2
            { 13.156062126159667969,  -29.138729095458984375, 5.27508544921875 }, // 3
            { -3.3503148555755615234, -21.11417388916015625,  5.27508544921875 }, // 4
            { 32.38727569580078125,   -33.63729095458984375,  5.27508544921875 }, // 5
            { -3.3503148555755615234, -21.11417388916015625,  5.27508544921875 }, // 6
            { -2.2618880271911621094, -19.3901214599609375,   5.27508544921875 }, // 7
            { 32.38727569580078125,   -33.63729095458984375,  5.27508544921875 }, // 8
            { -2.2618880271911621094, -19.3901214599609375,   5.27508544921875 }, // 9
            { -1.3746814727783203125, -17.957094192504882812, 5.27508544921875 }, // 10
            { 32.38727569580078125,   -33.63729095458984375,  5.27508544921875 }, // 11
            { 32.38727569580078125,   -33.63729095458984375,  5.27508544921875 }, // 12
            { -1.3746814727783203125, -17.957094192504882812, 5.27508544921875 }, // 13
            { 32.437255859375,        -33.629116058349609375, 5.27508544921875 }, // 14
            { 32.437255859375,        -33.629116058349609375, 5.27508544921875 }, // 15
            { -1.3746814727783203125, -17.957094192504882812, 5.27508544921875 }, // 16
            { 55.865238189697265625,  -28.229640960693359375, 5.27508544921875 }  // 17
        },

        .cells = { { 0, 1, 2 }, { 3, 4, 5 }, { 6, 7, 8 }, 
            { 9, 10, 11 }, { 12, 13, 14 }, { 15, 16, 17 } }
    };
    
    auto bounds = std::array 
    { 
        std::array { -12.721479415893555, -42.009937286376953, 5.2750854492187500 },
        std::array { -1.2356452941894531, -28.377023696899414, 36.069015502929688 }
    };

    auto expected = std::vector<kdtree::Event>
    {
        { .itriangle = 1, .position = -33.637290954589844, .axis = 1, .type = kdtree::Event::Type::Starts },
        { .itriangle = 2, .position = -33.637290954589844, .axis = 1, .type = kdtree::Event::Type::Starts },
        { .itriangle = 3, .position = -33.637290954589844, .axis = 1, .type = kdtree::Event::Type::Starts },
        { .itriangle = 4, .position = -33.637290954589844, .axis = 1, .type = kdtree::Event::Type::Starts },
        { .itriangle = 5, .position = -33.629116058349609, .axis = 1, .type = kdtree::Event::Type::Starts },
        { .itriangle = 0, .position = -29.138729095458984, .axis = 1, .type = kdtree::Event::Type::Starts },
        { .itriangle = 0, .position = -28.377023696899414, .axis = 1, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 1, .position = -28.377023696899414, .axis = 1, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 2, .position = -28.377023696899414, .axis = 1, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 3, .position = -28.377023696899414, .axis = 1, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 4, .position = -28.377023696899414, .axis = 1, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 5, .position = -28.377023696899414, .axis = 1, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 0, .position = -3.3503148555755615, .axis = 0, .type = kdtree::Event::Type::Starts },
        { .itriangle = 1, .position = -3.3503148555755615, .axis = 0, .type = kdtree::Event::Type::Starts },
        { .itriangle = 2, .position = -3.3503148555755615, .axis = 0, .type = kdtree::Event::Type::Starts },
        { .itriangle = 3, .position = -2.2618880271911621, .axis = 0, .type = kdtree::Event::Type::Starts },
        { .itriangle = 4, .position = -1.3746814727783203, .axis = 0, .type = kdtree::Event::Type::Starts },
        { .itriangle = 5, .position = -1.3746814727783203, .axis = 0, .type = kdtree::Event::Type::Starts },
        { .itriangle = 0, .position = -1.2356452941894531, .axis = 0, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 1, .position = -1.2356452941894531, .axis = 0, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 2, .position = -1.2356452941894531, .axis = 0, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 3, .position = -1.2356452941894531, .axis = 0, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 4, .position = -1.2356452941894531, .axis = 0, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 5, .position = -1.2356452941894531, .axis = 0, .type = kdtree::Event::Type::Ends   },
        { .itriangle = 0, .position =  5.2750854492187500, .axis = 2, .type = kdtree::Event::Type::Planar },
        { .itriangle = 1, .position =  5.2750854492187500, .axis = 2, .type = kdtree::Event::Type::Planar },
        { .itriangle = 2, .position =  5.2750854492187500, .axis = 2, .type = kdtree::Event::Type::Planar },
        { .itriangle = 3, .position =  5.2750854492187500, .axis = 2, .type = kdtree::Event::Type::Planar },
        { .itriangle = 4, .position =  5.2750854492187500, .axis = 2, .type = kdtree::Event::Type::Planar },
        { .itriangle = 5, .position =  5.2750854492187500, .axis = 2, .type = kdtree::Event::Type::Planar }
    };
    
    auto provider = kdtree::makeObjectProvider<3, 2>( triangulation, false );
    auto computed = kdtree::createSortedEventList( provider, bounds );
    
    REQUIRE( computed.size( ) == expected.size( ) );

    for( size_t i = 0; i < expected.size( ); ++i )
    {
        CHECK( computed[i].axis == expected[i].axis );
        CHECK( computed[i].itriangle == expected[i].itriangle );
        CHECK( computed[i].type == expected[i].type );
        CHECK( computed[i].position == Approx( expected[i].position ).epsilon( 1e-10 ) );
    }
    
    auto plane = kdtree::findPlane( 6, bounds, expected, parameters );

    CHECK( std::get<0>( plane ) == Approx( 5.2750854492187500 ).epsilon( 1e-10 ) );
    CHECK( std::get<1>( plane ) == 2 );
    CHECK( std::get<2>( plane ) == 0 );
    CHECK( std::get<3>( plane ) == Approx( 3.0202603121852731 ).epsilon( 1e-10 ) );

    auto tree = buildKdTree( provider, bounds, parameters );

    writeVtu( triangulation, testing::outputPath( "core/kdtree_collection3_triangles.vtu" ) );
    writeVtu( tree, testing::outputPath( "core/kdtree_collection3_kdtree.vtu" ) );

} // kdtree3D_collection3_test

TEST_CASE( "kdtree2D_test" )
{     
    /*                       
     *        A              
     *        |                                     5
     * 7.5 __ |                                  _______
     * 7.0 __ |                               4 / \   / \ 6
     * 6.5 __ |                8 |             /___\_/___\
     * 6.0 __ |                  |___          \   / \   /
     * 5.0 __ |                    7          2 \_/___\_/ 3
     *        |                                     1 
     * 1.5 __ |   _____ 
     *        |   \   / 0    
     *   0 __ |    \_/       
     *        |              
     *         ------------------------------------------------>
     *            | | |          |  |         |  |  |  |  |    
     *            0 1 2          6  7         11 12 13 14 15
     */

    auto triangulation = Triangulation<2>
    {
        // Triangulation vertices
        .vertices = std::vector
        {
            std::array { 1.0,  0.0 }, // 0
            std::array { 0.0,  1.5 }, // 1
            std::array { 2.0,  1.5 }, // 2
            std::array { 12.0, 5.0 }, // 3
            std::array { 14.0, 5.0 }, // 4
            std::array { 11.0, 6.5 }, // 5
            std::array { 13.0, 6.5 }, // 6
            std::array { 15.0, 6.5 }, // 7
            std::array { 12.0, 8.0 }, // 8
            std::array { 14.0, 8.0 }, // 9
            std::array { 6.0,  6.0 }, // 10
            std::array { 7.0,  6.0 }, // 11
            std::array { 6.0,  7.0 }, // 12

            std::array { 8.0,  2.5 }, // 13
            std::array { 10.0, 2.5 }, // 14
            std::array { 9.0,  5.0 }, // 15
            std::array { 9.0,  0.0 }, // 16
            std::array { 10.2, 0.0 }, // 17
            std::array { 10.2, 3.0 }  // 18
        },

        // Triangle indices
        .cells = std::vector
        {
            std::array<size_t, 3> { 0, 1, 2 },    // 0
            std::array<size_t, 3> { 3, 4, 6 },    // 1
            std::array<size_t, 3> { 3, 5, 6 },    // 2
            std::array<size_t, 3> { 4, 6, 7 },    // 3
            std::array<size_t, 3> { 5, 6, 8 },    // 4
            std::array<size_t, 3> { 6, 8, 9 },    // 5
            std::array<size_t, 3> { 6, 7, 9 },    // 6
            std::array<size_t, 3> { 10, 11, 10 }, // 7
            std::array<size_t, 3> { 12, 10, 12 }, // 8
            std::array<size_t, 3> { 13, 14, 15 }, // 9 
            std::array<size_t, 3> { 13, 14, 16 }, // 10
            std::array<size_t, 3> { 18, 16, 17 }  // 11
        } 
    };

    writeVtu( triangulation, testing::outputPath( "core/kdtree2D_test_triangulation.vtu" ) );
    
    auto bounds = triangulation.boundingBox( );

    CHECK( bounds[0][0] == Approx( 0.0 ).margin( 1e-12 ) );
    CHECK( bounds[0][1] == Approx( 0.0 ).margin( 1e-12 ) );
    CHECK( bounds[1][0] == Approx( 15.0 ).margin( 1e-12 ) );
    CHECK( bounds[1][1] == Approx( 8.0 ).margin( 1e-12 ) );

    auto parameters = kdtree::Parameters
    {
        .KT = 1.0,
        .KL = 3.0,
        .emptyCellBias = 0.8
    };
    
    auto provider = kdtree::makeObjectProvider<2, 2>( triangulation );

    auto computed = kdtree::createSortedEventList( provider, bounds );

    auto expected = std::vector
    {
        kdtree::Event { .itriangle = 0,  .position = 0.0,  .axis = 0, .type = kdtree::Event::Type::Starts }, // 0
        kdtree::Event { .itriangle = 0,  .position = 0.0,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 1
        kdtree::Event { .itriangle = 10, .position = 0.0,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 2
        kdtree::Event { .itriangle = 11, .position = 0.0,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 3
        kdtree::Event { .itriangle = 0,  .position = 1.5,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 4
        kdtree::Event { .itriangle = 0,  .position = 2.0,  .axis = 0, .type = kdtree::Event::Type::Ends   }, // 5
        kdtree::Event { .itriangle = 10, .position = 2.5,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 6
        kdtree::Event { .itriangle = 9,  .position = 2.5,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 7
        kdtree::Event { .itriangle = 11, .position = 3.0,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 8
        kdtree::Event { .itriangle = 9,  .position = 5.0,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 9
        kdtree::Event { .itriangle = 1,  .position = 5.0,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 10
        kdtree::Event { .itriangle = 2,  .position = 5.0,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 11
        kdtree::Event { .itriangle = 3,  .position = 5.0,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 12
        kdtree::Event { .itriangle = 8,  .position = 6.0,  .axis = 0, .type = kdtree::Event::Type::Planar }, // 13
        kdtree::Event { .itriangle = 7,  .position = 6.0,  .axis = 1, .type = kdtree::Event::Type::Planar }, // 14
        kdtree::Event { .itriangle = 7,  .position = 6.0,  .axis = 0, .type = kdtree::Event::Type::Starts }, // 15
        kdtree::Event { .itriangle = 8,  .position = 6.0,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 16
        kdtree::Event { .itriangle = 1,  .position = 6.5,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 17
        kdtree::Event { .itriangle = 2,  .position = 6.5,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 18
        kdtree::Event { .itriangle = 3,  .position = 6.5,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 19
        kdtree::Event { .itriangle = 4,  .position = 6.5,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 20
        kdtree::Event { .itriangle = 5,  .position = 6.5,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 21
        kdtree::Event { .itriangle = 6,  .position = 6.5,  .axis = 1, .type = kdtree::Event::Type::Starts }, // 22
        kdtree::Event { .itriangle = 7,  .position = 7.0,  .axis = 0, .type = kdtree::Event::Type::Ends   }, // 23
        kdtree::Event { .itriangle = 8,  .position = 7.0,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 24
        kdtree::Event { .itriangle = 4,  .position = 8.0,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 25
        kdtree::Event { .itriangle = 5,  .position = 8.0,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 26
        kdtree::Event { .itriangle = 6,  .position = 8.0,  .axis = 1, .type = kdtree::Event::Type::Ends   }, // 27
        kdtree::Event { .itriangle = 9,  .position = 8.0,  .axis = 0, .type = kdtree::Event::Type::Starts }, // 28
        kdtree::Event { .itriangle = 10, .position = 8.0,  .axis = 0, .type = kdtree::Event::Type::Starts }, // 29
        kdtree::Event { .itriangle = 11, .position = 9.0,  .axis = 0, .type = kdtree::Event::Type::Starts }, // 30
        kdtree::Event { .itriangle = 9,  .position = 10.0, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 31
        kdtree::Event { .itriangle = 10, .position = 10.0, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 32
        kdtree::Event { .itriangle = 11, .position = 10.2, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 33
        kdtree::Event { .itriangle = 2,  .position = 11.0, .axis = 0, .type = kdtree::Event::Type::Starts }, // 34
        kdtree::Event { .itriangle = 4,  .position = 11.0, .axis = 0, .type = kdtree::Event::Type::Starts }, // 35
        kdtree::Event { .itriangle = 1,  .position = 12.0, .axis = 0, .type = kdtree::Event::Type::Starts }, // 36
        kdtree::Event { .itriangle = 5,  .position = 12.0, .axis = 0, .type = kdtree::Event::Type::Starts }, // 37
        kdtree::Event { .itriangle = 2,  .position = 13.0, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 38
        kdtree::Event { .itriangle = 4,  .position = 13.0, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 39
        kdtree::Event { .itriangle = 3,  .position = 13.0, .axis = 0, .type = kdtree::Event::Type::Starts }, // 40
        kdtree::Event { .itriangle = 6,  .position = 13.0, .axis = 0, .type = kdtree::Event::Type::Starts }, // 41
        kdtree::Event { .itriangle = 1,  .position = 14.0, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 42
        kdtree::Event { .itriangle = 5,  .position = 14.0, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 43
        kdtree::Event { .itriangle = 3,  .position = 15.0, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 44
        kdtree::Event { .itriangle = 6,  .position = 15.0, .axis = 0, .type = kdtree::Event::Type::Ends   }, // 45
    };

    REQUIRE( expected.size( ) == computed.size( ) );

    for( size_t i = 0; i < expected.size( ); ++i )
    {
        // These might be ambiguous again since some can be ordered differently ?
        CHECK( computed[i].axis == expected[i].axis );
        CHECK( computed[i].itriangle == expected[i].itriangle );
        CHECK( computed[i].type == expected[i].type );
        CHECK( computed[i].position == Approx( expected[i].position ).epsilon( 1e-10 ) );
    }

    for( size_t i = 0; i <= 4; ++i )
    {
        auto ratios0 = kdtree::computeSurfaceAreaRatios<2>( bounds, 0, i * 15.0 / 4 );
        auto ratios1 = kdtree::computeSurfaceAreaRatios<2>( bounds, 1, i * 8.0 / 4 );

        auto lx = 30.0, ly = 16.0, c = 46.0, j = 4.0 - i;

        CHECK( ratios0[0] == Approx( ( i * lx / 4.0 + ly ) / c ).epsilon( 1e-10 ) );
        CHECK( ratios0[1] == Approx( ( j * lx / 4.0 + ly ) / c ).epsilon( 1e-10 ) );
        CHECK( ratios0[2] == Approx( i / 4.0 ).epsilon( 1e-10 ) );

        CHECK( ratios1[0] == Approx( ( i * ly / 4.0 + lx ) / c ).epsilon( 1e-10 ) );
        CHECK( ratios1[1] == Approx( ( j * ly / 4.0 + lx ) / c ).epsilon( 1e-10 ) );
        CHECK( ratios1[2] == Approx( i / 4.0 ).epsilon( 1e-10 ) );
    }

    auto rotate90 = [&]( )
    {
        for( auto& vertex : triangulation.vertices )
        {
            std::swap( vertex[0], vertex[1] );

            vertex[0] = -vertex[0];
        }

        return triangulation.boundingBox( );
    };

    auto plane0 = kdtree::findPlane( triangulation.ncells( ), bounds, computed, parameters );
    
    CHECK( std::get<0>( plane0 ) == Approx( 8.0 ).epsilon( 1e-10 ) );
    CHECK( std::get<1>( plane0 ) == 0 );
    CHECK( std::get<2>( plane0 ) == 1 );

    bounds = rotate90( );

    auto plane1 = kdtree::findPlane( triangulation.ncells( ), triangulation.boundingBox( ), 
        kdtree::createSortedEventList( provider, bounds ), parameters );

    CHECK( std::get<0>( plane1 ) == Approx( 8.0 ).epsilon( 1e-10 ) );
    CHECK( std::get<1>( plane1 ) == 1 );
    CHECK( std::get<2>( plane1 ) == 1 );

    bounds = rotate90( );

    auto plane2 = kdtree::findPlane( triangulation.ncells( ), triangulation.boundingBox( ), 
        kdtree::createSortedEventList( provider, bounds ), parameters );

    CHECK( std::get<0>( plane2 ) == Approx( -8.0 ).epsilon( 1e-10 ) );
    CHECK( std::get<1>( plane2 ) == 0 );
    CHECK( std::get<2>( plane1 ) == 1 );
    
    bounds = rotate90( );

    auto plane3 = kdtree::findPlane( triangulation.ncells( ), triangulation.boundingBox( ), 
        kdtree::createSortedEventList( provider, bounds ), parameters );

    CHECK( std::get<0>( plane3 ) == Approx( -8.0 ).epsilon( 1e-10 ) );
    CHECK( std::get<1>( plane3 ) == 1 );
    CHECK( std::get<2>( plane1 ) == 1 );
    
    rotate90( );

    auto indices = std::vector<size_t>( triangulation.ncells( ) );
    
    std::iota( indices.begin( ), indices.end( ), size_t { 0 } );

    auto sides0 = kdtree::classifyTriangles( indices, expected, plane0 );
    auto sides1 = kdtree::classifyTriangles( indices, expected, { 6.0, 0, 0, 0.0 } );
    auto sides2 = kdtree::classifyTriangles( indices, expected, { 6.0, 0, 1, 0.0 } );
    auto sides3 = kdtree::classifyTriangles( indices, expected, { 6.0, 1, 0, 0.0 } );
    auto sides4 = kdtree::classifyTriangles( indices, expected, { 6.0, 1, 1, 0.0 } );

    CHECK( sides0 == std::vector<size_t> { 0, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2 } );
    CHECK( sides1 == std::vector<size_t> { 0, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2 } );
    CHECK( sides2 == std::vector<size_t> { 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2 } );
    CHECK( sides3 == std::vector<size_t> { 0, 1, 1, 1, 2, 2, 2, 0, 2, 0, 0, 0 } );
    CHECK( sides4 == std::vector<size_t> { 0, 1, 1, 1, 2, 2, 2, 2, 2, 0, 0, 0 } );
    
    auto tree = buildKdTree( triangulation, parameters );

    writeVtu( tree, testing::outputPath( "core/kdtree2D_test_kdtree.vtu" ) );

    REQUIRE( tree.nfull( ) == 37 );
    REQUIRE( tree.nleaves( ) == 19 );
    REQUIRE( tree.maxdepth( ) == 7 );

    // Check each tree node
    auto isLeaf = std::vector<bool>
    {
        0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1,
        0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1,
    };

    auto leafOrChild = std::vector<CellIndex>
    {
        1, 3, 19, 5, 9, 7, 0, 1, 2, 3, 11, 13, 4, 15, 5, 6, 17, 7, 8, 21,
        29, 23, 9, 10, 25, 11, 27, 12, 13, 14, 31, 33, 35, 15, 16, 17, 18
    };

    auto data = std::vector<std::vector<size_t>>
    {
        { }, { 0 }, { }, { }, { }, { }, { 8 }, { 7 }, { }, { }, { 10, 11 }, 
        { 9 }, { 11 }, { }, { }, { 1, 2 }, { 1, 3 }, { 4, 5 }, { 5, 6 },
    };

    for( CellIndex inode = 0; inode < isLeaf.size( ); ++inode )
    {
        REQUIRE( tree.isLeaf( inode ) == isLeaf[inode] );

        if( isLeaf[inode] )
        {
            CHECK( tree.leafIndex( inode ) == leafOrChild[inode] );
            CHECK( tree.child( inode, 0 ) == NoCell );
            CHECK( tree.child( inode, 1 ) == NoCell );

            auto ileaf = tree.leafIndex( inode );
            auto span = tree.itemsLeaf( ileaf );

            REQUIRE( span.size( ) == data[ileaf].size( ) );
            CHECK( std::vector( span.begin( ), span.end( ) ) == data[ileaf] );
        }
        else
        {
            //auto split = tree.split( inode );
	        //std::cout << "test split" << std::endl;

            CHECK( tree.child( inode, 0 ) == leafOrChild[inode] );
            CHECK( tree.child( inode, 1 ) == leafOrChild[inode] + 1 );
        }
    }

    // Gather items using bounding box intersection
    {
        auto items0 = kdtree::accumulateItems( tree, spatial::boundingBoxAt<2>( { 2.0, 1.5 }, 1e-12 ) );
        auto items1 = kdtree::accumulateItems( tree, spatial::boundingBoxAt<2>( { 13.0, 6.5 }, 1e-12 ) );
        auto items2 = kdtree::accumulateItems( tree, spatial::boundingBoxAt<2>( { 7.5, 4.0 }, 6.0 ) );
        auto items3 = kdtree::accumulateItems( tree, spatial::boundingBoxAt<2>( { 2.0, 6.0 }, 6.0 ) );

        CHECK( items0 == std::vector<size_t> { 0 } );
        CHECK( items1 == std::vector<size_t> { 1, 2, 3, 4, 5, 6 } );
        CHECK( items2 == std::vector<size_t> { 7, 8, 9, 10, 11 } );
        CHECK( items3 == std::vector<size_t> { } );
    }

    // Gather items using ray intersection
    {
        auto items0  = kdtree::accumulateItemsInv( tree, std::array {  3.0,  1.0  }, spatial::invert<2>( { 8.5,  7.5 } ) );
        auto items1  = kdtree::accumulateItemsInv( tree, std::array {  3.0,  0.7  }, spatial::invert<2>( { 8.5,  7.5 } ) );
        auto items2  = kdtree::accumulateItemsInv( tree, std::array {  3.0,  0.5  }, spatial::invert<2>( { 8.5,  7.5 } ) );
        auto items3  = kdtree::accumulateItemsInv( tree, std::array {  3.0,  0.5  }, spatial::invert<2>( { 1.0,  0.0 } ) );
        auto items4  = kdtree::accumulateItemsInv( tree, std::array { 10.5, -20.0 }, spatial::invert<2>( { 0.0,  0.1 } ) );
        auto items5  = kdtree::accumulateItemsInv( tree, std::array { 10.1, -20.0 }, spatial::invert<2>( { 0.0,  0.1 } ) );
        auto items6  = kdtree::accumulateItemsInv( tree, std::array { 10.5,  20.0 }, spatial::invert<2>( { 0.0, -9.9 } ) );
        auto items7  = kdtree::accumulateItemsInv( tree, std::array { 10.1,  20.0 }, spatial::invert<2>( { 0.0, -9.9 } ) );
        auto items8  = kdtree::accumulateItemsInv( tree, std::array { -1.0,  0.0  }, spatial::invert<2>( { 1.7,  0.7 } ) );
        auto items9  = kdtree::accumulateItemsInv( tree, std::array { -1.0,  1.0  }, spatial::invert<2>( { 11.5, 9.0 } ) );
        auto items10 = kdtree::accumulateItemsInv( tree, std::array { -1.0,  1.0  }, spatial::invert<2>( { 12.3, 8.4 } ) );
        
        CHECK( items0.first == std::vector<size_t> { } );
        CHECK( items1.first == std::vector<size_t> { 4, 5 } );
        CHECK( items2.first == std::vector<size_t> { 4, 5, 9 } );
        CHECK( items3.first == std::vector<size_t> { 10, 11 } );
        CHECK( items4.first == std::vector<size_t> { } );
        CHECK( items5.first == std::vector<size_t> { 10, 11 } );
        CHECK( items6.first == std::vector<size_t> { } );
        CHECK( items7.first == std::vector<size_t> { 10, 11 } );
        CHECK( items8.first == std::vector<size_t> { 0, 1, 2, 3, 5, 6, 9 } );
        CHECK( items9.first == std::vector<size_t> { 8 } );
        CHECK( items10.first == std::vector<size_t> { 7 } );
    }

} // kdtree2D_test

} // namespace mlhp
