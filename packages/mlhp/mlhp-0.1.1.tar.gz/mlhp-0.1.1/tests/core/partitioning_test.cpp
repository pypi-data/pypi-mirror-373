// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/partitioning.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/quadrature.hpp"
#include "mlhp/core/arrayfunctions.hpp"
#include "mlhp/core/mesh.hpp"
#include "mlhp/core/postprocessing.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/integrands.hpp"

#include <numbers>

namespace mlhp
{
namespace
{

template<size_t D>
auto createTestMesh( std::array<double, D> corner1, 
                     std::array<double, D> corner2 )
{
    auto mesh = makeCartesianGrid<D>( array::makeSizes<D>( 1 ), array::subtract( corner2, corner1 ), corner1 );

    auto mapping = mesh->createMapping( );
    
    mesh->prepareMapping( 0, mapping );

    return std::pair { mesh, std::move( mapping ) };
}

} // namespace

TEST_CASE( "makeCartesianMappingSplitter_test" )
{
    auto mapping = CartesianMapping<3> { {{ { 5.0, -2.0, 4.0 }, { 7.0, 1.0, 5.0 } }} };
    auto generator = makeCartesianMappingSplitter<3>( mapping, { 3, 2, 4 } );

    auto J0 = std::array { 1.0, 0.0, 0.0, 
                           0.0, 1.5, 0.0,
                           0.0, 0.0, 0.5 };

    CHECK( spatial::distance<3>( mapping( { } ), { 6.0, -0.5, 4.5 } ) < 1e-8 ); 
    CHECK( spatial::distance( mapping.J( { } ), J0 ) < 1e-8 );
    CHECK( mapping.detJ( { } ) == Approx( 2.0 * 3.0 * 1.0 / 8.0 ).epsilon( 1e-8 ) );

    using IjkRstXyz = std::tuple<std::array<size_t, 3>, std::array<double, 3>, std::array<double, 3>>;

    auto tests = std::vector<IjkRstXyz>
    {
        { { 0, 0, 0 }, { -1.0, -1.0, -1.0 }, { 5.0, -2.0, 4.0 } },
        { { 0, 0, 0 }, { 1.0, 0.5, -0.5 }, { 5.0 + 2.0 / 3.0, -0.875, 4.0625 } },
        { { 1, 0, 1 }, { -0.5, -0.5, 0.5 }, { 5.0 + 2.0 / 3.0 + 1.0 / 6.0, -1.625, 4.4375 } },
        { { 1, 1, 2 }, { 0.0, 1.0, -1.0 }, { 6.0, 1.0, 4.5 } },
        { { 2, 1, 3 }, { 1.0, 1.0, 1.0 }, { 7.0, 1.0, 5.0 } }
    };

    for( auto [ijk, rst, xyz] : tests )
    {
        CHECK( spatial::distance<3>( generator( ijk ).map( rst ), xyz ) < 1e-8 ); 
    }

    auto computedDetJ = generator( { 1, 1, 2 } ).detJ( { 0.5, -0.3, 1.0 } );
    auto expectedDetJ = 2.0 / 3.0 * 3.0 / 2.0 * 1.0 / 4.0 / 8.0;

    CHECK( computedDetJ == Approx( expectedDetJ ).epsilon( 1e-8 ) );
}

TEST_CASE( "SpaceTreeQuadrature_test" )
{
    auto circle = implicit::sphere<2>( { 1.2, 0.6 }, 0.16 );

    double epsilonFCM = 1.27e-4;

    SpaceTreeQuadrature<2> quadrature( circle, epsilonFCM, 3 );

    auto cache = quadrature.initialize( );

    CoordinateGrid<2> rstTarget;
    CoordinateList<2> xyzTarget;
    std::vector<double> weightsTarget;
    
    std::vector<std::array<double, 2>> expectedRst
    {
        { -0.5,   -0.5   }, { -0.75,   0.25  },  
        { -0.875,  0.625 }, { -0.875,  0.875 }, { -0.625,  0.625 }, { -0.625,  0.875 }, 
        { -0.375,  0.125 }, { -0.375,  0.375 }, { -0.125,  0.125 }, { -0.125,  0.375 }, 
        { -0.375,  0.625 }, { -0.375,  0.875 }, { -0.125,  0.625 }, { -0.125,  0.875 }, 
        {  0.25,  -0.75  },
        {  0.125, -0.375 }, {  0.125, -0.125 }, {  0.375, -0.375 }, {  0.375, -0.125 },
        {  0.625, -0.875 }, {  0.625, -0.625 }, {  0.875, -0.875 }, {  0.875, -0.625 },
        {  0.625, -0.375 }, {  0.625, -0.125 }, {  0.875, -0.375 }, {  0.875, -0.125 },
        {  0.125,  0.125 }, {  0.125,  0.375 }, {  0.375,  0.125 }, {  0.375,  0.375 },
        {  0.25,   0.75  }, {  0.75,   0.25  }, {  0.75,   0.75  },
    };

    auto expectedLocalDeterminants = std::vector<double> ( 34, 0.015625 );

    expectedLocalDeterminants[0] *= 16.0;
    expectedLocalDeterminants[1] *= 4.0;
    expectedLocalDeterminants[14] *= 4.0;
    expectedLocalDeterminants[31] *= 4.0;
    expectedLocalDeterminants[32] *= 4.0;
    expectedLocalDeterminants[33] *= 4.0;

    auto tolerance = 1e-12;

    auto [mesh, mapping] = createTestMesh<2>( { 1.2, 0.6 }, { 1.4, 0.8 } );

    size_t numberOfPartitions;

    REQUIRE_NOTHROW( numberOfPartitions = quadrature.partition( mapping, cache ) );

    REQUIRE( numberOfPartitions == 34 );

    double rootDetJAndWeight = 0.01 * ( 8.0 / 9.0 ) * ( 8.0 / 9.0 );

    for( size_t i = 0; i < 34; ++i )
    {
        REQUIRE_NOTHROW( quadrature.distribute( i, { 3, 3 }, rstTarget, xyzTarget, weightsTarget, cache ) );

        REQUIRE( rstTarget[0].size( ) == 3 );
        REQUIRE( rstTarget[1].size( ) == 3 );
        REQUIRE( xyzTarget.size( ) == 3 * 3 );

        auto expectedXyz = mapping( expectedRst[i] );
        double alphaFCM = circle( expectedXyz ) ? 1.0 : epsilonFCM;

        // check mid point of 3x3 gauss rule which is at (0, 0)
        CHECK( rstTarget[0][1] == Approx( expectedRst[i][0] ).epsilon( tolerance ) );
        CHECK( rstTarget[1][1] == Approx( expectedRst[i][1] ).epsilon( tolerance ) );
        CHECK( xyzTarget[4][0] == Approx( expectedXyz[0] ).epsilon( tolerance ) );
        CHECK( xyzTarget[4][1] == Approx( expectedXyz[1] ).epsilon( tolerance ) );
        CHECK( weightsTarget[4] == Approx( rootDetJAndWeight * expectedLocalDeterminants[i] * alphaFCM ).epsilon( tolerance ) );
    }

    // Test helper function
    auto partitions = evaluateQuadrature<2>( quadrature, *mesh, mapping.icell, { 3, 3 } );

    REQUIRE( partitions.size( ) == 34 );

    for( size_t i = 0; i < 34; ++i )
    {
        REQUIRE( partitions[i].rst.size( ) == 3 * 3 );
        REQUIRE( partitions[i].xyz.size( ) == 3 * 3 );
        REQUIRE( partitions[i].weights.size( ) == 3 * 3 );

        auto expectedXyz = mapping( expectedRst[i] );
        double alphaFCM = circle( expectedXyz ) ? 1.0 : epsilonFCM;

        // check mid point of 3x3 gauss rule which is at (0, 0)
        CHECK( partitions[i].isgrid );
        CHECK( spatial::distance( partitions[i].rst[4], expectedRst[i] ) < tolerance );
        CHECK( spatial::distance( partitions[i].xyz[4], expectedXyz ) < tolerance );
        CHECK( partitions[i].weights[4] == Approx( rootDetJAndWeight * 
            expectedLocalDeterminants[i] * alphaFCM ).epsilon( tolerance ) );
    }
        
} // SpaceTreeQuadrature_test

namespace partitionertest
{

template<size_t D>
double volumeUsingSpaceTree( const ImplicitFunction<D>& function, 
                             const MeshMapping<D>& mapping, 
                             std::array<size_t, D> orders,
                             size_t depth, double alphaFCM )
{

    SpaceTreeQuadrature<D> quadrature( function, alphaFCM, depth );

    auto cache = quadrature.initialize( );

    CoordinateGrid<D> rstTarget;
    CoordinateList<D> xyzTarget;
    std::vector<double> weightsTarget;

    size_t numberOfPartitions = 0;
    
    REQUIRE_NOTHROW( numberOfPartitions = quadrature.partition( mapping, cache ) );

    REQUIRE( numberOfPartitions > 0 );
     
    double integral = 0.0;

    for( size_t iPartition = 0; iPartition < numberOfPartitions; ++iPartition )
    {
        REQUIRE_NOTHROW( quadrature.distribute( iPartition, orders, rstTarget, xyzTarget, weightsTarget, cache ) );

        for( size_t i = 0; i < array::product( orders ); ++i )
        {
            integral += weightsTarget[i];
        }
    }

    return integral;
}

} // namespace partitionertest

TEST_CASE( "MomentFittingQuadrature_test" )
{
    double tolerance = 1e-12;

    std::array<double, 3> corner1 = { 2.0, 1.0, 3.0 };
    std::array<double, 3> corner2 = { 3.0, 2.0, 4.0 };

    auto sphere1 = implicit::sphere<3>( { 2.8, 1.8, 3.0 }, 0.2 );
    auto sphere2 = implicit::sphere<3>( { 2.0, 1.0, 3.0 }, 0.5 );

    auto spheres = implicit::add( sphere1, sphere2 );

    size_t depth = 3;
    double alphaFCM = 1e-3;//3.2e-5;

    MomentFittingQuadrature<3> quadrature( spheres, alphaFCM, depth, 5, relativeQuadratureOrder<3>( 0 ) );

    CoordinateGrid<3> rstTarget;
    CoordinateList<3> xyzTarget;
    std::vector<double> weightsTarget;

    std::array<size_t, 3> orders { 4, 2, 3 };

    auto cache = quadrature.initialize( );
    
    auto [mesh, mapping] = createTestMesh<3>( corner1, corner2 );
    
    for( size_t i = 0; i < 3; ++i )
    {
        size_t numberOfCells;
                
        REQUIRE_NOTHROW( numberOfCells = quadrature.partition( mapping, cache ) );

        REQUIRE( numberOfCells == 1 );

        REQUIRE_NOTHROW( quadrature.distribute( 0, orders, rstTarget, xyzTarget, weightsTarget, cache ) );

        auto strides = nd::stridesFor( orders );

        for( size_t axis = 0; axis < 3; ++axis )
        {
            auto gaussPoints = gaussLegendrePoints( orders[axis] )[0];

            REQUIRE( rstTarget[axis].size( ) == orders[axis] );
            CHECK( std::equal( rstTarget[axis].begin( ), rstTarget[axis].end( ), gaussPoints.begin( ) ) );

            auto map = [&]( double r ) { return ( r + 1.0 ) / 2.0 * ( corner2[axis] - corner1[axis] ) + corner1[axis]; };

            // Test map to global for a few points
            CHECK( xyzTarget[0][axis] == Approx( map( gaussPoints[0] ) ).epsilon( tolerance ) );
             
            for( size_t axis2 = 0; axis2 < 3; ++axis2 )
            {
                CHECK( xyzTarget[strides[axis2]][axis] == Approx( map( gaussPoints[axis == axis2] ) ).epsilon( tolerance ) );
            }

            CHECK( xyzTarget.back( )[axis] == Approx( map( gaussPoints.back( ) ) ).epsilon( tolerance ) );
        }
    }

    double volume = 0.0;

    for( size_t i = 0; i < array::product( orders ); ++i )
    {
        volume += weightsTarget[i];

    } // for i

    double spaceTreeVolume = partitionertest::volumeUsingSpaceTree<3>( spheres, mapping, orders, depth, alphaFCM );
    double exactVolume = ( 1.0 - alphaFCM ) * 4.0 / 3.0 * std::numbers::pi * ( 0.2 * 0.2 * 0.2 / 2.0 + 0.5 * 0.5 * 0.5 / 8.0 ) + alphaFCM;
    
    CHECK( spaceTreeVolume == Approx( exactVolume ).epsilon( 5e-3 ) );
    CHECK( volume == Approx( spaceTreeVolume ).epsilon( tolerance ) );
}

TEST_CASE( "StandardQuadrature_test" )
{
    StandardQuadrature<2> quadrature;

    auto cache = quadrature.initialize( );

    CoordinateGrid<2> rstTarget;
    CoordinateList<2> xyzTarget;
    std::vector<double> weightsTarget;
    
    CoordinateGrid<2> expectedRst, expectedWeights;

    std::array<size_t, 2> orders { 4, 3 };

    auto quadratureCache = QuadraturePointCache { };

    tensorProductQuadrature( orders, expectedRst, expectedWeights, quadratureCache );

    double tolerance = 1e-12;

    // Try 3 times
    for( size_t dummy = 0; dummy < 3; ++dummy )
    {
        auto testmesh = createTestMesh<2>( { 1.2, 0.6 }, { 1.4, 0.8 } );
        auto mesh = std::get<0>( testmesh );
        auto mapping = std::move( std::get<1>( testmesh ) );

        size_t numberOfPartitions;

        REQUIRE_NOTHROW( numberOfPartitions = quadrature.partition( mapping, cache ) );

        REQUIRE( numberOfPartitions == 1 );

        REQUIRE_NOTHROW( quadrature.distribute( 0, orders, rstTarget, xyzTarget, weightsTarget, cache ) );

        for( size_t axis = 0; axis < 2; ++axis )
        {
            for( size_t i = 0; i < orders[axis]; ++i )
            {
                CHECK( rstTarget[axis][i] == Approx( expectedRst[axis][i] ).epsilon( tolerance ) );
            }
        }

        nd::executeWithIndex( orders, [&]( std::array<size_t, 2> ijk, size_t index )
        { 
            double expectedWeight = array::product( array::extract( expectedWeights, ijk ) ) * 0.01;
            auto expectedXyz = mapping( array::extract( expectedRst, ijk ) );

            CHECK( weightsTarget[index] == Approx( expectedWeight ).epsilon( tolerance ) );

            for( size_t axis = 0; axis < 2; ++axis )
            {
                CHECK( xyzTarget[index][axis] == Approx( expectedXyz[axis] ).epsilon( tolerance ) );
            }
        } );
    }
}

TEST_CASE( "GridQuadrature_test1" )
{
    auto quadrature = GridQuadrature<2>( { 4, 3 } );
    
    auto cache = quadrature.initialize( );
    auto rst = CoordinateGrid<2> { };
    auto xyz = CoordinateList<2> { };
    auto weights = std::vector<double>{ };

    auto testmesh = createTestMesh<2>( { 1.2, 0.6 }, { 1.4, 0.8 } );
    auto mesh = std::get<0>( testmesh );
    auto mapping = std::move( std::get<1>( testmesh ) );

    REQUIRE( quadrature.partition( mapping, cache ) == 12 );

    auto ticks = std::array
    {
        std::vector { -1.0, -0.5, 0.0, 0.5, 1.0 },
        std::vector { -1.0, -1.0 / 3.0, 1.0 / 3.0, 1.0 }
    };

    for( size_t i = 0; i < 4; ++i )
    {
        for( size_t j = 0; j < 3; ++j )
        {
            utilities::resize0( rst, xyz, weights );

            REQUIRE_NOTHROW( quadrature.distribute( i * 3 + j, { 2, 2 }, rst, xyz, weights, cache ) );
            
            auto bounds = std::array
            { 
                std::array { ticks[0][i], ticks[0][i + 1] }, 
                std::array { ticks[1][j], ticks[1][j + 1] } 
            };

            for( size_t axis = 0; axis < 2; ++axis )
            {
                CHECK( rst[axis].size( ) == 2 );

                auto r0 = ( -1.0 / std::sqrt( 3.0 ) + 1.0 ) / 2.0 * ( bounds[axis][1] - bounds[axis][0] ) + bounds[axis][0];
                auto r1 = ( 1.0 / std::sqrt( 3.0 ) + 1.0 ) / 2.0 * ( bounds[axis][1] - bounds[axis][0] ) + bounds[axis][0];
                
                CHECK( rst[axis][0] == Approx( r0 ).epsilon( 1e-10 ) );
                CHECK( rst[axis][1] == Approx( r1 ).epsilon( 1e-10 ) );
            }
        }
    }
}

TEST_CASE( "GridQuadrature_test2" )
{
    //   _______________________
    //  |           |           |        Refined two more times,
    //  |           |           |        to a total of 4 levels.
    //  |           |           |                            |
    //  |___________|___________|            ________________|
    //  |     |     |           |                |__|__|     |
    //  |_____|_____|           |                |__|__|_____|
    //  |__|__|__|__|<-- - - - -|- - - - - -     |__|__|     |
    //  |__|__|__|__|___________|            ____|__|__|_____|
    //  |__|__|__|__|     |     |                |           |
    //  |__|__|__|__|_____|_____|                |           |
    //  |     |     |     |     |
    //  |_____|_____|_____|_____|


    auto mesh = makeRefinedGrid<2>( { 2, 3 }, { 2.0, 3.0 } );

    mesh->refine( { 0, 1, 3 } );
    mesh->refine( { 4, 6, 7, 9 } );
    mesh->refine( { 26 } );
    mesh->refine( { 26, 27 } );

    auto quadrature = GridQuadrature<2>( *mesh, { 8, 8 } );

    REQUIRE( mesh->ncells( ) == 36 );

    auto expectedNcells = std::vector<size_t> 
    { 
        8, 8, 8,                // level 0: cells 0 - 2
        4, 4, 4, 4, 4, 4, 4, 4, // level 1: cells 3 - 10
        2, 2, 2, 2, 2, 2, 2, 2, // level 2: cells 11 
        2, 2, 2, 2, 2, 2, 2,    //                   - 25
        1, 1,                   // level 3: cells 26 - 27
        1, 1, 1, 1, 1, 1, 1, 1  // level 4: cells 28 - 35
    };

    auto expectedAreas = std::vector<double>
    {
        1.0, 1.0, 1.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
        0.0625, 0.0625, 0.0625, 0.0625, 0.0625, 0.0625, 0.0625, 0.0625,
        0.0625, 0.0625, 0.0625, 0.0625, 0.0625, 0.0625, 0.0625,
        1.0 / 64.0, 1.0 / 64.0, 
        1.0 / 256.0, 1.0 / 256.0, 1.0 / 256.0, 1.0 / 256.0,
        1.0 / 256.0, 1.0 / 256.0, 1.0 / 256.0, 1.0 / 256.0
    };

    auto cache = quadrature.initialize( );
    auto mapping = mesh->createMapping( );
    auto rst = CoordinateGrid<2> { };
    auto xyzList = CoordinateList<2> { };
    auto weights = std::vector<double> { };

    for( CellIndex icell = 0; icell < 36; ++icell )
    {
        mesh->prepareMapping( icell, mapping );

        auto npartitions = quadrature.partition( mapping, cache );
        
        CHECK( mapping.detJ( { } ) == Approx( expectedAreas[icell] / 4.0 ).epsilon( 1e-10 ) );
        CHECK( npartitions == utilities::integerPow( expectedNcells[icell], 2 ) );

        auto midpoint = std::array { 0.0, 0.0 };

        for( size_t ipartition = 0; ipartition < npartitions; ++ipartition )
        {
            utilities::resize0( rst, xyzList, weights );

            quadrature.distribute( ipartition, { 2, 3 }, rst, xyzList, weights, cache );

            auto partitionArea = std::accumulate( weights.begin( ), weights.end( ), 0.0 );

            CHECK( rst[0].size( ) == 2 );
            CHECK( rst[1].size( ) == 3 );
            CHECK( xyzList.size( ) == 6 );
            CHECK( weights.size( ) == 6 );

            CHECK( partitionArea == Approx( expectedAreas[icell] / npartitions ).epsilon( 1e-10 ) );

            for( const auto& xyz : xyzList )
            {
                midpoint = midpoint + xyz * 1.0 / ( 6.0 * npartitions );
            }
        }

        CHECK( spatial::distance( midpoint, mapping( { } ) ) < 1e-10 );
    }

    // auto gridQuadrature = GridQuadrature<2>( *mesh, { 8, 8 } );
    // auto basis = makeHpBasis<TrunkSpace>( mesh, 1 );
    // auto determiner = makeIntegrationOrderDeterminor<2>( 1 );
    // auto pointGenerator = cellmesh::quadraturePoints( gridQuadrature, *basis, determiner );
    // 
    // writeOutput( *mesh, cellmesh::createGrid<2>( ), CellProcessor<2> {  }, VtuOutput { "outputs/GridQuadrature_test1_mesh" } );
    // writeOutput( *basis, pointGenerator, ElementProcessor<2> {  }, VtuOutput { "outputs/GridQuadrature_test1_points" } );
}

TEST_CASE( "marchingCubesQuadrature_test" )
{
    auto testConfiguration = []( size_t ncells, size_t resolution, double expected, bool coarsen = false )
    {
        auto sphere = implicit::sphere<3>( { 1.0, 1.0, 1.0 }, 0.7 );
        auto mesh = CartesianGrid<3>( array::make<3>( ncells ), { 2.0, 2.0, 2.0 } );
        auto basis = DummyBasis<3>( mesh );
        auto niterations = size_t { 50 };

        // Volume integral
        auto marchingCubesVolume = cellmesh::domain( sphere, 
            array::make<3>( resolution ), coarsen, false, niterations );

        auto domainQuadrature = CellmeshQuadrature<3>( marchingCubesVolume );
        auto order = absoluteQuadratureOrder( array::makeSizes<3>( 3 ) );

        auto domainFunction = []( std::array<double, 3> ) noexcept { return 1.0;  };
        auto domaniIntegrand = makeFunctionIntegrand<3>( domainFunction );
        auto domainTarget = 0.0;

        integrateOnDomain( basis, domaniIntegrand, { domainTarget }, domainQuadrature, order );
        
        CHECK( domainTarget == Approx( expected ).epsilon( 1e-10 ) );

        // Surface integral
        auto surfaceOrder = absoluteQuadratureOrder( array::makeSizes<3>( 3 ) );
        auto [triangulation, celldata] = recoverDomainBoundary( mesh, sphere, array::make<3>( resolution ), niterations );
        auto surfaceQuadrature = SimplexQuadrature<3>( triangulation, celldata, surfaceOrder );

        auto positionVector =  []( std::array<double, 3> xyz ) { return xyz; };
        auto surfaceIntegrand = makeNormalDotProductIntegrand<3>( spatial::VectorFunction<3, 3> { positionVector });
        auto surfaceTarget = 0.0;

        integrateOnSurface( basis, surfaceIntegrand, surfaceQuadrature, { surfaceTarget } );

        CHECK( 1.0 / 3.0 * surfaceTarget == Approx( expected ).epsilon( 1e-10 ) );

        //auto writer1 = VtuOutput { testing::outputPath( "core/marchingCubesQuadrature1_volume" ) };
        //auto writer2 = VtuOutput { testing::outputPath( "core/marchingCubesQuadrature1_mesh" ) };
        //auto writer3 = VtuOutput { testing::outputPath( "core/marchingCubesQuadrature1_surface" ) };

        //writeOutput( mesh, marchingCubesVolume, CellProcessor<3> { }, writer1 );
        //writeOutput( mesh, cellmesh::createGrid( array::makeSizes<3>( 1 ) ), CellProcessor<3> { }, writer2 );
        //writeOutput( mesh, cellmesh::associatedTriangles( triangulation, celldata ), CellProcessor<3> { }, writer3 );
    };

    // Very coarse (exact volume would be 4.0 / 3.0 * pi * 0.7^3)
    testConfiguration( 2, 1, 4.0 / 3.0 * std::pow( 0.7, 3 ) );
    testConfiguration( 1, 2, 4.0 / 3.0 * std::pow( 0.7, 3 ) );

    // We are just assuming these values are correct now.
    testConfiguration( 3, 1, 0.931287827687736 );
    testConfiguration( 1, 3, 0.931287827687736 );

    testConfiguration( 4, 1, 1.01502992814705 );
    testConfiguration( 2, 2, 1.01502992814705 );
    testConfiguration( 1, 4, 1.01502992814705 );

    testConfiguration( 5, 1, 1.22232905380673 );
    testConfiguration( 1, 5, 1.22232905380673 );
    testConfiguration( 5, 1, 1.22232905380673, true );
    testConfiguration( 1, 5, 1.22232905380673, true );

    testConfiguration( 6, 1, 1.28693300129717 );
    testConfiguration( 1, 6, 1.28693300129717 );
    testConfiguration( 2, 3, 1.28693300129717 );
    testConfiguration( 3, 2, 1.28693300129717 );
    testConfiguration( 1, 6, 1.28693300129717, true );

    testConfiguration( 3, 5, 1.4115531131934476, true );
}

TEST_CASE( "marchingCubesQuadrature_test2" )
{
    auto sphere1 = implicit::sphere<3>( { 1.0, 2.0, -0.1 }, 0.5 );
    auto sphere2 = implicit::sphere<3>( { 2.0, 1.0, 0.2 }, 0.4 );
    auto sphere3 = implicit::sphere<3>( { 1.5, 1.0, 1.5 }, 0.6 );
    //auto domain = implicit::add( sphere1, sphere2, sphere3 );
    auto domain = implicit::invert( implicit::add( sphere1, sphere2, sphere3 ) );

    auto niterations = size_t { 50 };
    auto resolution = std::array<size_t, 3> { 1, 1, 1 };
    auto order = absoluteQuadratureOrder( array::makeSizes<3>( 2 ) );
    auto domainFunction = []( std::array<double, 3> ) noexcept { return 1.0;  };
    auto domaniIntegrand = makeFunctionIntegrand<3>( domainFunction );

    auto lengths = std::array { 1.9, 2.1, 2.7 };
    auto origin = std::array { 0.5, 0.4, -0.6 };

    for( auto ncells : std::vector<size_t> { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 } )
    {
        auto mesh = CartesianGrid<3>( array::makeSizes<3>( ncells ), lengths, origin );
        auto basis = DummyBasis<3>( mesh );

        auto marchingCubesVolume = cellmesh::domain( domain, resolution, true, true, niterations );
        auto domainQuadrature = CellmeshQuadrature<3>( marchingCubesVolume );
        auto domainTarget = 0.0;
        auto totalVolume = array::product( lengths );

        integrateOnDomain( basis, domaniIntegrand, { domainTarget }, domainQuadrature, order );

        CHECK( std::abs( domainTarget - totalVolume ) / totalVolume  < 1e-12 );

        //auto writer1 = VtuOutput { testing::outputPath( "core/marchingCubesQuadrature2_volume1" ) };
        //auto writer2 = VtuOutput { testing::outputPath( "core/marchingCubesQuadrature2_mesh" ) };
        //
        //writeOutput( mesh, marchingCubesVolume, CellProcessor<3> { }, writer1 );
        //writeOutput( mesh, cellmesh::createGrid( array::makeSizes<3>( 1 ) ), CellProcessor<3> { }, writer2 );
    }
}

} // namespace mlhp
