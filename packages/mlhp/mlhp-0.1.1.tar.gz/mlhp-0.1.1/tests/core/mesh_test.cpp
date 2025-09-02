// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"
#include "tests/core/singleBaseCell_2D.hpp"

#include "mlhp/core/mesh.hpp"
#include "mlhp/core/topologycore.hpp"
#include "mlhp/core/refinement.hpp"
#include "mlhp/core/implicit.hpp"

#include <array>
#include <vector>
#include <memory>

namespace mlhp
{

TEST_CASE( "basegrid_test" )
{
    auto grid = makeRefinedGrid<2>( { 3, 4 }, { 1.0, 1.0 }, { 0.0, 0.0 } );

    std::vector<std::array<CellIndex, 4>> expectedNeighbours
    {
        { NoCell,      4, NoCell,      1 },
        { NoCell,      5,      0,      2 },
        { NoCell,      6,      1,      3 },
        { NoCell,      7,      2, NoCell },
        {      0,      8, NoCell,      5 },
        {      1,      9,      4,      6 },
        {      2,     10,      5,      7 },
        {      3,     11,      6, NoCell },
        {      4, NoCell, NoCell,      9 },
        {      5, NoCell,      8,     10 },
        {      6, NoCell,      9,     11 },
        {      7, NoCell,     10, NoCell }
    };

    CHECK( grid->nfull( ) == 12 );
    CHECK( grid->nleaves( ) == 12 );

    auto neighbours = mesh::hierarchicalNeighbours( *grid );
    auto levels = mesh::refinementLevels( *grid, true );
    auto leafMask = mesh::leafMask( *grid );
    auto parents = mesh::parents( *grid );

    REQUIRE( neighbours.size( ) == 12 );
    REQUIRE( levels.size( ) == 12 );
    REQUIRE( leafMask.size( ) == 12 );
    REQUIRE( parents.size( ) == 12 );

    for( size_t i = 0; i < 12; ++i )
    {
        CHECK( levels[i] == 0 );
        CHECK( leafMask[i] == true );
        CHECK( parents[i] == NoCell );

        for( size_t axis = 0; axis < 2; ++axis )
        {
            CHECK( neighbours[i]( axis, 0 ) == expectedNeighbours[i][2 * axis + 0] );
            CHECK( neighbours[i]( axis, 1 ) == expectedNeighbours[i][2 * axis + 1] );
        }
    }
    
} // basegrid_test

TEST_CASE( "CartesianGrid_mapping_test" )
{
    CoordinateGrid<3> gridCoordinates
    {{
        { 5.0, 6.0, 8.0, 8.5 },
        { 0.5, 2.5, 3.0, 4.0, 5.5 },
        { 6.2, 6.5, 7.2 }
    }};

    CoordinateList<3> rst
    {
        { -0.5, 0.2, 0.7 },
        {  0.5,-0.3, 0.5 },
        {  0.9, 0.4,-0.6 },
    };

    std::vector<CoordinateList<3>> xyz
    {
        CoordinateList<3>{ { 5.25,  1.7, 6.455 }, { 5.75,  1.2,   6.425 }, { 5.95,  1.9,  6.26 } },
        CoordinateList<3>{ { 5.25,  1.7, 7.095 }, { 5.75,  1.2,   7.025 }, { 5.95,  1.9,  6.64 } },
        CoordinateList<3>{ { 5.25,  2.8, 6.455 }, { 5.75,  2.675, 6.425 }, { 5.95,  2.85, 6.26 } },
        CoordinateList<3>{ { 5.25,  2.8, 7.095 }, { 5.75,  2.675, 7.025 }, { 5.95,  2.85, 6.64 } },
        CoordinateList<3>{ { 5.25,  3.6, 6.455 }, { 5.75,  3.35,  6.425 }, { 5.95,  3.7,  6.26 } },
        CoordinateList<3>{ { 5.25,  3.6, 7.095 }, { 5.75,  3.35,  7.025 }, { 5.95,  3.7,  6.64 } },
        CoordinateList<3>{ { 5.25,  4.9, 6.455 }, { 5.75,  4.525, 6.425 }, { 5.95,  5.05, 6.26 } },
        CoordinateList<3>{ { 5.25,  4.9, 7.095 }, { 5.75,  4.525, 7.025 }, { 5.95,  5.05, 6.64 } },
        CoordinateList<3>{ { 6.5,   1.7, 6.455 }, { 7.5,   1.2,   6.425 }, { 7.9,   1.9,  6.26 } },
        CoordinateList<3>{ { 6.5,   1.7, 7.095 }, { 7.5,   1.2,   7.025 }, { 7.9,   1.9,  6.64 } },
        CoordinateList<3>{ { 6.5,   2.8, 6.455 }, { 7.5,   2.675, 6.425 }, { 7.9,   2.85, 6.26 } },
        CoordinateList<3>{ { 6.5,   2.8, 7.095 }, { 7.5,   2.675, 7.025 }, { 7.9,   2.85, 6.64 } },
        CoordinateList<3>{ { 6.5,   3.6, 6.455 }, { 7.5,   3.35,  6.425 }, { 7.9,   3.7,  6.26 } },
        CoordinateList<3>{ { 6.5,   3.6, 7.095 }, { 7.5,   3.35,  7.025 }, { 7.9,   3.7,  6.64 } },
        CoordinateList<3>{ { 6.5,   4.9, 6.455 }, { 7.5,   4.525, 6.425 }, { 7.9,   5.05, 6.26 } },
        CoordinateList<3>{ { 6.5,   4.9, 7.095 }, { 7.5,   4.525, 7.025 }, { 7.9,   5.05, 6.64 } },
        CoordinateList<3>{ { 8.125, 1.7, 6.455 }, { 8.375, 1.2,   6.425 }, { 8.475, 1.9,  6.26 } },
        CoordinateList<3>{ { 8.125, 1.7, 7.095 }, { 8.375, 1.2,   7.025 }, { 8.475, 1.9,  6.64 } },
        CoordinateList<3>{ { 8.125, 2.8, 6.455 }, { 8.375, 2.675, 6.425 }, { 8.475, 2.85, 6.26 } },
        CoordinateList<3>{ { 8.125, 2.8, 7.095 }, { 8.375, 2.675, 7.025 }, { 8.475, 2.85, 6.64 } },
        CoordinateList<3>{ { 8.125, 3.6, 6.455 }, { 8.375, 3.35,  6.425 }, { 8.475, 3.7,  6.26 } },
        CoordinateList<3>{ { 8.125, 3.6, 7.095 }, { 8.375, 3.35,  7.025 }, { 8.475, 3.7,  6.64 } },
        CoordinateList<3>{ { 8.125, 4.9, 6.455 }, { 8.375, 4.525, 6.425 }, { 8.475, 5.05, 6.26 } },
        CoordinateList<3>{ { 8.125, 4.9, 7.095 }, { 8.375, 4.525, 7.025 }, { 8.475, 5.05, 6.64 } },
    };

    std::vector<double> widths { 0.6, 1.4, 0.15, 0.35, 0.3, 0.7, 0.45, 1.05, 1.2, 2.8, 0.3, 0.7, 0.6,
                                 1.4, 0.9, 2.1, 0.3, 0.7, 0.075, 0.175, 0.15, 0.35, 0.225, 0.525 };

    CartesianGrid grid( gridCoordinates );

    REQUIRE( grid.ncells( ) == 24 );

    double tolerance = 2e-14;

    auto backwardMapping = grid.createBackwardMapping( );
    
    // Test inside points
    for( CellIndex iCell = 0; iCell < xyz.size( ); ++iCell )
    {
        for( size_t iPoint = 0; iPoint < rst.size( ); ++iPoint )
        {
            auto global1 = mesh::map( grid, iCell, rst[iPoint] );
            auto [global2, detJ] = map::withDetJ( mesh::mapping( grid, iCell ), rst[iPoint] );

            auto local = backwardMapping->map( xyz[iCell][iPoint] );

            REQUIRE( local );
            REQUIRE( local->first == iCell );

            CHECK( detJ == Approx( widths[iCell] / 8.0 ).epsilon( tolerance ) );

            for( size_t axis = 0; axis < 3; ++axis )
            {
                CHECK( global1[axis] == Approx( xyz[iCell][iPoint][axis] ).epsilon( tolerance ) );
                CHECK( global2[axis] == Approx( xyz[iCell][iPoint][axis] ).epsilon( tolerance ) );

                CHECK( local->second[axis] == Approx( rst[iPoint][axis] ).epsilon( tolerance ) );
            }
        }
    }

    std::array<double, 3> mid { 0.5 * ( gridCoordinates[0][0] + gridCoordinates[0][1] ),
                                0.5 * ( gridCoordinates[1][0] + gridCoordinates[1][1] ),
                                0.5 * ( gridCoordinates[2][0] + gridCoordinates[2][1] ) };

    std::array<size_t, 3> endIndices { 16, 6, 1 };

    // Test corner cases for reverse mapping
    for( size_t axis = 0; axis < 3; ++axis )
    {
        double t0 = gridCoordinates[axis].front( );
        double tn = gridCoordinates[axis].back( );

        size_t n = gridCoordinates[axis].size( );

        double eps = 1e-13 * ( tn - t0 );

        // Outside of grid
        CHECK( !backwardMapping->map( array::setEntry( mid, axis, t0 - 2.0 * eps ) ) );
        CHECK( !backwardMapping->map( array::setEntry( mid, axis, tn + 2.0 * eps ) ) );

        double localEps1 = eps * 2.0 / ( gridCoordinates[axis][1] - t0 );
        double localEps2 = eps * 2.0 / ( tn - gridCoordinates[axis][n - 2] );

        std::array<double, 4> xValue { t0 - 0.5 * eps, t0, tn, tn + 0.5 * eps };
        std::array<double, 4> rValue { -1.0 - 0.5 * localEps1, -1.0, 1.0, 1.0 + 0.5 * localEps2 };

        std::array<size_t, 4> indices { 0, 0, endIndices[axis], endIndices[axis] };

        // Two on left and two on right coordinate
        for( size_t i = 0; i < 4; ++i )
        {
            auto result = backwardMapping->map( array::setEntry( mid, axis, xValue[i] ) );

            REQUIRE( result );
            REQUIRE( result->first == indices[i] );

            auto expected = array::setEntry( array::make<3>( 0.0 ), axis, rValue[i] );

            for( size_t axis2 = 0; axis2 < 3; ++axis2 )
            {
                CHECK( result->second[axis2] == Approx( expected[axis2] ).margin( tolerance ).epsilon( tolerance ) );

            } // for axis2
        } // for i
    } // for axis

} // CartesianGrid_mapping_test

TEST_CASE( "refine_base_test" )
{
    auto grid = makeRefinedGrid<2>( { 2, 3 }, { 1.0, 1.0 } );

    auto circle = implicit::sphere<2>( { 0.0, 0.0 }, 1.0 );

    auto refineTowardsCircle = refineTowardsDomainBoundary<2>( circle, 3 );

    REQUIRE_NOTHROW( grid->refine( refineTowardsCircle ) );
}

TEST_CASE( "refine_single_test" )
{
    auto grid = makeRefinedGrid<2>( { 1, 1 }, { 1.0, 1.0 } );

    auto circle = implicit::sphere<2>( { 0.0, 0.0 }, 0.8 );

    auto refineTowardsCircle = refineTowardsDomainBoundary<2>( circle, 3 );

    REQUIRE_NOTHROW( grid->refine( refineTowardsCircle ) );

    auto parents = mesh::parents( *grid );
    auto neighbours = mesh::hierarchicalNeighbours( *grid );
    auto leafMask = mesh::leafMask( *grid );
    auto levels = mesh::refinementLevels( *grid, true );
    auto positions = mesh::positionsInParent( *grid );
    auto boundaries = mesh::boundaries( *grid );

    REQUIRE( neighbours.size( ) == singlebasecell2d::numberOfElements );
    REQUIRE( parents.size( ) == singlebasecell2d::numberOfElements );
    REQUIRE( leafMask.size( ) == singlebasecell2d::numberOfElements );
    REQUIRE( levels.size( ) == singlebasecell2d::levels.size( ) );
    REQUIRE( positions.size( ) == singlebasecell2d::positionsInParent.size( ) );

    auto expectedNeighbours = singlebasecell2d::neighbours( );
    auto expectedBoundaries = singlebasecell2d::boundaries( );

    CellIndex iLeaf = 0;

    for( CellIndex iCell = 0; iCell < singlebasecell2d::numberOfElements; ++iCell )
    {
        CHECK( parents[iCell] == singlebasecell2d::parents[iCell] );
        CHECK( leafMask[iCell] == singlebasecell2d::isLeaf[iCell] );
        CHECK( levels[iCell] == singlebasecell2d::levels[iCell] );

        CHECK( positions[iCell] == singlebasecell2d::positionsInParent[iCell] );

        for( size_t axis = 0; axis < 2; ++axis )
        {
            CHECK( neighbours[iCell]( axis, 0 ) == expectedNeighbours[iCell]( axis, 0 ) );
            CHECK( neighbours[iCell]( axis, 1 ) == expectedNeighbours[iCell]( axis, 1 ) );
        }

        if( leafMask[iCell] )
        {
            CHECK( grid->fullIndex( iLeaf ) == iCell );
            CHECK( grid->leafIndex( iCell ) == iLeaf );

            iLeaf++;
        }

        CHECK( grid->child( iCell, { 0, 0 } ) == singlebasecell2d::children[iCell][0] );
        CHECK( grid->child( iCell, { 0, 1 } ) == singlebasecell2d::children[iCell][1] );
        CHECK( grid->child( iCell, { 1, 0 } ) == singlebasecell2d::children[iCell][2] );
        CHECK( grid->child( iCell, { 1, 1 } ) == singlebasecell2d::children[iCell][3] );
    }

    REQUIRE( boundaries.size( ) == expectedBoundaries.size( ) );

    CHECK( std::equal( boundaries.begin( ), boundaries.end( ), expectedBoundaries.begin( ) ) );
}

TEST_CASE( "RefinedGrid_mapping_test1", "[refined_mesh]" )
{
    std::array<size_t, 3> numberOfCells { 3, 2, 4 };
    std::array<double, 3> lengths { 2.0, 4.0, 3.0 };
    std::array<double, 3> origin { 7.0, 5.0, 6.0 };

    auto grid = makeRefinedGrid( numberOfCells, lengths, origin );

    REQUIRE( grid->baseGrid( ).ncells( ) == 3 * 2 * 4 );

    auto index = static_cast<CellIndex>( ( 0 * numberOfCells[1] + 1 ) * numberOfCells[2] + 3 );

    std::array<double, 3> rst { -0.6, 0.2, 0.7 };

    auto xyz1 = mesh::map( grid->baseGrid( ), index, rst );
    auto xyz2 = mesh::map( *grid, index, rst );

    std::array<double, 3> d { 2.0 / 3.0, 4.0 / 2.0, 3.0 / 4.0 };
    std::array<double, 3> expected1 { 7.0 + d[0] * 0.2, 5.0 + d[1] * 1.6, 6.0 + d[2] * 3.85 };

    for( size_t axis = 0; axis < 3; ++axis )
    {
        CHECK( xyz1[axis] == Approx( expected1[axis] ).epsilon( 1e-12 ) );
        CHECK( xyz2[axis] == Approx( expected1[axis] ).epsilon( 1e-12 ) );
    }

    // --------------- 1 level of refinement -------------------

    auto circle = implicit::sphere( mesh::map( *grid, index, { -1.0, 1.0, 1.0 } ), 0.05 );
    auto strategy1 = refineInsideDomain( circle, 1, 5 );
    
    grid->refine( strategy1 );

    REQUIRE( grid->nfull( ) == 3 * 2 * 4 + 8 );

    std::array<std::array<double, 3>, 8> expected2
    {
        7.0 + d[0] * 0.1, 5.0 + d[1] * 1.3, 6.0 + d[2] * 3.425,
        7.0 + d[0] * 0.1, 5.0 + d[1] * 1.3, 6.0 + d[2] * 3.925,
        7.0 + d[0] * 0.1, 5.0 + d[1] * 1.8, 6.0 + d[2] * 3.425,
        7.0 + d[0] * 0.1, 5.0 + d[1] * 1.8, 6.0 + d[2] * 3.925,
        7.0 + d[0] * 0.6, 5.0 + d[1] * 1.3, 6.0 + d[2] * 3.425,
        7.0 + d[0] * 0.6, 5.0 + d[1] * 1.3, 6.0 + d[2] * 3.925,
        7.0 + d[0] * 0.6, 5.0 + d[1] * 1.8, 6.0 + d[2] * 3.425,
        7.0 + d[0] * 0.6, 5.0 + d[1] * 1.8, 6.0 + d[2] * 3.925
    };

    for( CellIndex child = 0; child < 8; ++child )
    {
        auto xyz3 = mesh::mapFull( *grid, 3 * 2 * 4 + child, rst );

        for( size_t axis = 0; axis < 3; ++axis )
        {
            CHECK( xyz3[axis] == Approx( expected2[child][axis] ).epsilon( 1e-12 ) );
        }
    }

    // --------------- 2 levels of refinement -------------------

    auto strategy2 = refineInsideDomain( circle, 2, 5 );

    grid->refine( strategy2 );

    REQUIRE( grid->nfull( ) == 3 * 2 * 4 + 8 + 8 );
    
    double origin2[] = { 7.0, 8.0, 8.0 + 5.0 / 8.0 };
    double length2[] = { 1.0 / 6.0, 1.0 / 2.0, 3.0 / 16.0 };

    std::array<std::array<double, 3>, 8> expected3
    {
        origin2[0] + 0.2 * length2[0], origin2[1] + 0.6 * length2[1], origin2[2] + 0.85 * length2[2],
        origin2[0] + 0.2 * length2[0], origin2[1] + 0.6 * length2[1], origin2[2] + 1.85 * length2[2],
        origin2[0] + 0.2 * length2[0], origin2[1] + 1.6 * length2[1], origin2[2] + 0.85 * length2[2],
        origin2[0] + 0.2 * length2[0], origin2[1] + 1.6 * length2[1], origin2[2] + 1.85 * length2[2],
        origin2[0] + 1.2 * length2[0], origin2[1] + 0.6 * length2[1], origin2[2] + 0.85 * length2[2],
        origin2[0] + 1.2 * length2[0], origin2[1] + 0.6 * length2[1], origin2[2] + 1.85 * length2[2],
        origin2[0] + 1.2 * length2[0], origin2[1] + 1.6 * length2[1], origin2[2] + 0.85 * length2[2],
        origin2[0] + 1.2 * length2[0], origin2[1] + 1.6 * length2[1], origin2[2] + 1.85 * length2[2]
    };

    for( CellIndex child = 0; child < 8; ++child )
    {
        auto xyz3 = mesh::mapFull( *grid, 3 * 2 * 4 + 8 + child, rst );

        for( size_t axis = 0; axis < 3; ++axis )
        {
            CHECK( xyz3[axis] == Approx( expected3[child][axis] ).epsilon( 1e-12 ) );
        }
    }
}

TEST_CASE( "RefinedGrid_mapping_test2", "[refined_mesh]" )
{
    CoordinateGrid<3> gridCoordinates
    {{
        { -3.1, -0.1, 0.3, 0.5 },
        { 2.5, 3.6, 4.7 },
        { 0.0, 0.8, 2.0, 2.3, 2.7 }
    }};

    auto grid = makeRefinedGrid( gridCoordinates );

    std::array<size_t, 3> limits { 7, 5, 8 };
    std::array<double, 3> min, midPoint, step, boundingBoxMin, boundingBoxMax;

    for( size_t axis = 0; axis < 3; ++axis )
    {
        boundingBoxMin[axis] = gridCoordinates[axis][0];
        boundingBoxMax[axis] = gridCoordinates[axis].back( );

        double diff = boundingBoxMax[axis] - boundingBoxMin[axis];

        min[axis] = boundingBoxMin[axis] - 0.0174 * diff;

        double max = boundingBoxMax[axis] + 0.039 * diff;

        midPoint[axis] = boundingBoxMin[axis] + 0.5 * diff;

        step[axis] = ( max - min[axis] ) / ( limits[axis] - 1.0 );
    }

    auto strategy = refineInsideDomain( implicit::sphere( midPoint, 1.3 ), 3, 5 );

    grid->refine( strategy );

    auto boundingBox = implicit::cube<3>( boundingBoxMin, boundingBoxMax );
    auto backwardMapping = grid->createBackwardMapping( );

    nd::execute( limits, [&]( std::array<size_t, 3> ijk )
    {
        auto xyz = array::add( min, array::multiply( array::convert<double>( ijk ), step ) );

        auto result1 = backwardMapping->map( xyz );
        //auto result2 = grid->mapToLocalFull( xyz );

        CHECK( result1.has_value( ) == boundingBox( xyz ) );
        //CHECK( result2.has_value( ) == boundingBox( xyz ) );

        if( result1 )
        {
            REQUIRE( result1->first != NoCell );
            //REQUIRE( result2->first == grid->fullIndex( result1->first ) );

            auto mappedResult = mesh::map( *grid, result1->first, result1->second );

            for( size_t axis = 0; axis < 3; ++axis )
            {
                CHECK( mappedResult[axis] == Approx( xyz[axis] ).epsilon( 1e-12 ) );
            }
        }
    } );
}

TEST_CASE( "RefinedGrid_interfacemapping_test", "[refined_mesh]" )
{
    auto gridCoordinates = CoordinateGrid<2>
    { {
        { 2.0, 4.0, 7.0 },
        { -3.0, -1.0, 0.5, 2.0 },
    } };

    auto grid = makeRefinedGrid( gridCoordinates );
    
    grid->refine( { 0, 1, 3, 5 } );
    grid->refine( { 5, 8, 9, 16 } );
    grid->refine( { 26 } );

    auto mapping0 = grid->createInterfaceMapping( );
    auto mapping1 = grid->createInterfaceMapping( );

    grid->prepareInterfaceMappings( { 21, 1 }, { 1, 0 }, *mapping0, *mapping1 );

    CHECK( spatial::distance<2>( mapping0->map( { -0.5 } ), { 1.0, -0.5 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping1->map( { -0.5 } ), { -1.0, -0.375 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping1->map( { 0.5 } ), { -1.0, -0.125 } ) < 1e-9 );

    grid->prepareInterfaceMappings( { 1, 0 }, { 21, 1 }, *mapping0, *mapping1 );

    CHECK( spatial::distance<2>( mapping1->map( { -0.5 } ), { 1.0, -0.5 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping0->map( { -0.5 } ), { -1.0, -0.375 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping0->map( { 0.5 } ), { -1.0, -0.125 } ) < 1e-9 );

    grid->prepareInterfaceMappings( { 29, 2 }, { 1, 3 }, *mapping0, *mapping1 );

    CHECK( spatial::distance<2>( mapping0->map( { -0.6 } ), { -0.6, -1.0 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping0->map( { 0.2 } ), { 0.2, -1.0 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping1->map( { 0.4 } ), { 0.175, 1.0 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping1->map( { 0.9 } ), { 0.2375, 1.0 } ) < 1e-9 );

    grid->prepareInterfaceMappings( { 1, 3 }, { 29, 2 }, *mapping0, *mapping1 );

    CHECK( spatial::distance<2>( mapping1->map( { -0.6 } ), { -0.6, -1.0 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping1->map( { 0.2 } ), { 0.2, -1.0 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping0->map( { 0.4 } ), { 0.175, 1.0 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping0->map( { 0.9 } ), { 0.2375, 1.0 } ) < 1e-9 );

    grid->prepareInterfaceMappings( { 14, 1 }, { 30, 0 }, *mapping0, *mapping1 );

    CHECK( spatial::distance<2>( mapping0->map( { -0.8 } ), { 1.0, 0.1 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping1->map( { 0.2 } ), { -1.0, 0.2 } ) < 1e-9 );

    grid->prepareInterfaceMappings( { 30, 0 }, { 14, 1 }, *mapping0, *mapping1 );

    CHECK( spatial::distance<2>( mapping1->map( { -0.8 } ), { 1.0, 0.1 } ) < 1e-9 );
    CHECK( spatial::distance<2>( mapping0->map( { 0.2 } ), { -1.0, 0.2 } ) < 1e-9 );

    //writeOutput( *grid, cellmesh::createGrid<2>( { 1, 1 } ), CellProcessor<2> { }, VtuOutput { "test.vtu" } );
}

TEST_CASE( "Mesh_freeFloatingFunctions_test" )
{
    CoordinateGrid<3> gridCoordinates
    { {
        { -3.1, -0.1, 0.3, 0.5 },
        { 2.5, 3.6, 4.7 },
        { 0.0, 0.8, 2.0, 2.3, 2.7 }
    } };

    auto grid = makeRefinedGrid( gridCoordinates );

    auto strategy = refineInsideDomain( implicit::sphere<3>( { -1.3, 3.6, 1.35 }, 1.3 ), 2, 5 );

    grid->refine( strategy );

    REQUIRE( grid->nfull( ) == 632 );
    REQUIRE( grid->nleaves( ) == 556 );
    REQUIRE( grid->baseGrid( ).ncells( ) == 24 );

    // test root
    CHECK( mesh::root( *grid, 8 ) == 8 );
    CHECK( mesh::root( *grid, 176 ) == 1 );
    CHECK( mesh::root( *grid, 423 ) == 5 );
    CHECK( mesh::root( *grid, 617 ) == 13 );

    // test pathToRoot
    std::vector<CellIndex> path1, path2, path3, path4;

    REQUIRE_NOTHROW( mesh::pathToRoot( *grid, 8, path1 ) );
    REQUIRE_NOTHROW( mesh::pathToRoot( *grid, 176, path2 ) );
    REQUIRE_NOTHROW( mesh::pathToRoot( *grid, 423, path3 ) );
    REQUIRE_NOTHROW( mesh::pathToRoot( *grid, 617, path4 ) );

    CHECK( path1 == std::vector<CellIndex>{ 8 } );
    CHECK( path2 == std::vector<CellIndex>{ 176, 33,  1 } );
    CHECK( path3 == std::vector<CellIndex>{ 423, 64,  5 } );
    CHECK( path4 == std::vector<CellIndex>{ 617, 96, 13 } );

    // test gatherLeaves
    std::vector<CellIndex> leaves1, leaves2;

    REQUIRE_NOTHROW( mesh::leaves( *grid, 23, leaves1 ) );
    REQUIRE_NOTHROW( mesh::leaves( *grid, 5, leaves2 ) );

    std::vector<CellIndex> expectedLeaves2
    {
        416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428,
        429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441,
        442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454,
        455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467,
        468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479
    };

    CHECK( leaves1 == std::vector<CellIndex>{ 23 } );
    CHECK( leaves2 == expectedLeaves2 );

    // test mapToParentIndexSpace
    CoordinateGrid<3> rst;

    std::fill( rst.begin( ), rst.end( ), std::vector<double>{ -1.0, 0.0, 1.0 } );

    auto rst1 = rst;
    auto rst2 = rst;

    mesh::mapToParent( rst1, PositionInParent<3>{ 0, 1, 0 } );
    mesh::mapToParent( rst2, PositionInParent<3>{ 1, 0, 1 } );

    auto map0 = std::vector { -1.0, -0.5, 0.0 };
    auto map1 = std::vector {  0.0,  0.5, 1.0 };

    auto expectedRst1 = CoordinateGrid<3> { map0, map1, map0 };
    auto expectedRst2 = CoordinateGrid<3> { map1, map0, map1 };

    for( size_t axis = 0; axis < 3; ++axis )
    {
        for( size_t i = 0; i < 3; ++i )
        {
            CHECK( rst1[axis][i] == Approx( expectedRst1[axis][i] ).epsilon( 1e-12 ) );
            CHECK( rst2[axis][i] == Approx( expectedRst2[axis][i] ).epsilon( 1e-12 ) );
        }
    }
}

TEST_CASE( "roots_test" )
{
    auto grid = makeRefinedGrid<2>( { 2, 2 }, { 1.0, 1.0 } );

    auto refineTowardsCircle = refineTowardsDomainBoundary<2>( implicit::sphere<2>( { 0.0, 0.0 }, 0.8 ), 2 );

    REQUIRE_NOTHROW( grid->refine( refineTowardsCircle ) );
    REQUIRE( grid->ncells( ) == 34 );

    auto expectedFull = std::vector<CellIndex> 
    { 
        0, 1, 2, 3,                         // Base mesh
        1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, // level 1
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, // top left of level 2 
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, // bottom right of level 2 
        3, 3, 3, 3                          // top right of level 2
    };

    auto expectedLeaf = std::vector<CellIndex>
    {
        0,                                  // Base mesh
        1,          2,             3, 3, 3, // level 1
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, // top left of level 2 
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, // bottom right of level 2 
        3, 3, 3, 3                          // top right of level 2
    };

    CHECK( mesh::roots( *grid ) == expectedFull );
    CHECK( mesh::roots( *grid, false ) == expectedLeaf );
}

TEST_CASE( "FilteredGrid_test" )
{
    /*
     *     _______ _______ _______ _______     _ _  5.0
     *    | /  /  |       |       | /  /  |     |
     *    |/  /  /|  3/5  |  5/8  |/  /  /|     |
     *    |__/__/_|_______|_______|__/__/_|    _|_  4.0
     *    | /  /  |       |       |       |     |
     *    |/  /  /|  2/4  |  4/7  |  6/10 |     |
     *    |__/__/_|_______|_______|_______|    _|_  3.0
     *    |       |       | /  /  | /  /  |     |
     *    |  0/0  |  1/3  |/  /  /|/  /  /|     |
     *    |_______|_______|__/__/_|__/__/_|    _|_  2.0
     *    
     *    |-------|-------|-------|-------|
     *   1.0     2.0     3.0     4.0     5.0
     */ 

    CellIndexVector filteredCells = { 1, 2, 6, 9, 11 };
    CellIndexVector remainingCells = { 0, 3, 4, 5, 7, 8, 10 };

    auto unfiltered = makeCartesianGrid<2>( { 4, 3 }, { 4.0, 3.0 }, { 1.0, 2.0 } );
    auto filtered = FilteredGrid<2>( unfiltered, filteredCells );

    REQUIRE( filtered.ncells( ) == remainingCells.size( ) );
    REQUIRE( &filtered.unfilteredMesh( ) == unfiltered.get( ) );

    // Check index mapping

    for( auto icell : filteredCells )
    {
        CHECK( filtered.filteredIndex( icell ) == NoCell );
    }

    for( CellIndex icell = 0; icell < remainingCells.size( ); ++icell )
    {
        auto index = remainingCells[icell];

        CHECK( filtered.filteredIndex( index ) == icell );
        CHECK( filtered.unfilteredIndex( icell ) == index );
    }

    // Check neighbours

    auto expectedNeighbours = CellIndexVector
    {
        NoCell,      1, NoCell, NoCell, // cell 0
             0, NoCell, NoCell,      2, // cell 1
        NoCell,      4,      1,      3, // cell 2
        NoCell,      5,      2, NoCell, // cell 3
             2,      6, NoCell,      5, // cell 4
             3, NoCell,      4, NoCell, // cell 5
             4, NoCell, NoCell, NoCell, // cell 6
    };

    auto expectedFace = std::array<size_t, 4> { 1, 0, 3, 2 };

    auto neighbours = std::vector<MeshCellFace> { };

    for( CellIndex icell = 0; icell < filtered.ncells( ); ++icell )
    {
        CHECK( filtered.nfaces( icell ) == 4 );

        for( size_t side = 0; side < 4; ++side )
        {
            auto expected = expectedNeighbours[icell * 4 + side];

            // Function from AbsGrid implemented in FilteredGrid
            CHECK( filtered.neighbour( icell, side / 2, side % 2 ) == expected );

            // Function from AbsMesh implemented in FilteredMesh
            filtered.neighbours( icell, side, utilities::resize0( neighbours ) );

            REQUIRE( neighbours.size( ) == ( expected != NoCell ? 1 : 0 ) );

            if( expected != NoCell )
            {
                CHECK( neighbours[0].first == expected );
                CHECK( neighbours[0].second == expectedFace[side] );
            }
        }
    }
    
    // Check forward mapping

    auto mapping = filtered.createMapping( );

    filtered.prepareMapping( 6, mapping );

    auto xyz = mapping( { 0.0, 0.0 } );

    CHECK( xyz[0] == Approx( 4.5 ) );
    CHECK( xyz[1] == Approx( 3.5 ) );

    CHECK( mapping.detJ( { 0.2, -0.5 } ) == Approx( 0.25 ) );

    auto J = mapping.J( { 0.4, 0.5 } );

    CHECK( J[0] == Approx( 0.5 ) );
    CHECK( J[1] == 0.0 );
    CHECK( J[2] == 0.0 );
    CHECK( J[3] == Approx( 0.5 ) );

    // Check backward mapping
    auto backwardMapping = filtered.createBackwardMapping( );

    auto result1 = backwardMapping->map( { 3.25, 3.75 } );
    auto result2 = backwardMapping->map( { 1.5, 3.5 } );
    auto result3 = backwardMapping->map( { 0.0, 0.0 } );

    REQUIRE( result1 );

    CHECK( result1->first == 4 );
    
    CHECK( result1->second[0] == Approx( -0.5 ) );
    CHECK( result1->second[1] == Approx( 0.5 ) );

    CHECK( !result2 );
    CHECK( !result3 );
}

TEST_CASE( "facesInBoundingBox_test" )
{
    auto min = std::array { 5.0, 4.0, 3.0 };
    auto max = std::array { 8.0, 5.0, 6.0 };

    auto mesh = makeRefinedGrid<3>( { 3, 3, 2 }, max - min, min );

    mesh->refine( refineCellIndices<3>( { { 4, 7, 8 } } ) );

    auto [computedMin, computedMax] = mesh::boundingBox( *mesh, 2 );
    
    CHECK( computedMin[0] == Approx( min[0] ).epsilon( 1e-10 ) );
    CHECK( computedMin[1] == Approx( min[1] ).epsilon( 1e-10 ) );
    CHECK( computedMin[2] == Approx( min[2] ).epsilon( 1e-10 ) );
    
    CHECK( computedMax[0] == Approx( max[0] ).epsilon( 1e-10 ) );
    CHECK( computedMax[1] == Approx( max[1] ).epsilon( 1e-10 ) );
    CHECK( computedMax[2] == Approx( max[2] ).epsilon( 1e-10 ) );

    auto allFaces = mesh::facesInBoundingBox<3>( *mesh, { min, max }, 5 );

    REQUIRE( allFaces.size( ) == 39 * 6 );

    for( CellIndex icell = 0; icell < 39; ++icell)
    {
        for( size_t iface = 0; iface < 6; ++iface)
        {
            CHECK( allFaces[icell * 6 + iface].first == icell );
            CHECK( allFaces[icell * 6 + iface].second == iface );
        }
    }

    auto mins = std::vector
    {
        min, std::array { max[0], min[1], min[2] },
        min, std::array { min[0], max[1], min[2] },
        min, std::array { min[0], min[1], max[2] }
    };
    
    auto maxs = std::vector
    {
        std::array { min[0], max[1], max[2] }, max,
        std::array { max[0], min[1], max[2] }, max,
        std::array { max[0], max[1], min[2] }, max
    };

    for( size_t iface = 1; iface < 6; iface += 2 )
    {
        auto computed = mesh::facesInBoundingBox<3>( *mesh, { mins[iface], maxs[iface] }, 5 );
        auto expected = mesh::boundariesByFaceIndex( *mesh, { iface } )[0];

        REQUIRE( computed.size( ) == expected.size( ) );

        for( size_t i = 0; i < expected.size( ); ++i )
        {
            CHECK( computed[i].first == expected[i].first );
            CHECK( computed[i].second == expected[i].second );
        }
    }
}

TEST_CASE( "adaptive_refinement_test" )
{
    /*
     * +-------------------+----+----+----+----+      +----+----+----+----+---------+----+----+ 
     * |                   | 27 | 29 | 31 | 33 |      | 15 | 17 | 23 | 25 |         | 31 | 33 | 
     * |                   +----+----+----+----+      +----+----+----+----+    4    +----+----+ 
     * |                   | 26 | 28 | 30 | 32 |      | 14 | 16 | 22 | 24 |         | 30 | 32 | 
     * |         0         +----+----+----+----+      +----+----+----+----+----+----+----+----+
     * |                   |         |         |      | 11 | 13 | 19 | 21 | 27 | 29 |         |
     * |                   |    4    |    5    |      +----+----+----+----+----+----+    5    |
     * |                   |         |         |      | 10 | 12 | 18 | 20 | 26 | 28 |         |
     * +----+----+----+----+---------+----+----+  =>  +----+----+----+----+-------------------+
     * |  7 |  9 | 15 | 17 |         | 23 | 25 |      |         |  7 |  9 |                   |  
     * +----+----+----+----+    2    +----+----+      |    2    +----+----+                   | 
     * |  6 |  8 | 14 | 16 |         | 22 | 24 |      |         |  6 |  8 |                   |  
     * +----+----+----+----+----+----+----+----+      +---------+----+----+         0         | 
     * |         | 11 | 13 | 19 | 21 |         |      |         |         |                   |  
     * |    1    +----+----+----+----+    3    |      |    1    |    3    |                   |  
     * |         | 10 | 12 | 18 | 20 |         |      |         |         |                   |  
     * +---------+----+----+----+----+---------+      +---------+---------+----+----+----+----+ 
     * 
     */

    auto refine = std::vector<int> 
    { 
         2,             // cell  0       -> refine twice
         0,             // cell  1       -> keep
        -1, -3,         // cells 2  - 3  -> coarsen once
         1,             // cell  4       -> refine once
        -1,             // cell  5       -> keep
        -1, -2, -3, -2, // cells 6  - 9  -> coarsen once
        -1, -1, -1, -1, // cells 10 - 13 -> coarsen once
        -2, -1,  0, -2, // cells 14 - 17 -> keep
        -2, -2, -2, -2, // cells 18 - 21 -> coarsen twice
        -3, -2, -4, -2, // cells 22 - 25 -> coarsen twice
        -3, -2, -4, -2, // cells 26 - 29 -> coarsen once
         0,  0,  0,  0  // cells 30 - 33 -> keep
    };
  
    auto grid1 = makeRefinedGrid<2>( { 2, 2 }, { 3.0, 4.0 } );

    grid1->refine( refineCellIndices<2>( { { 0, 2, 3 }, { 2, 3, 4, 5, 8, 10, 12 } } ) );

    REQUIRE( grid1->ncells( ) == 34 );

    // Using refinement strategy
    auto grid2 = makeRefinedGrid<2>( grid1->baseGrid( ).cloneGrid( ) );

    grid2->refine( mesh::refineAdaptively( *grid1, refine ) );

    // Using direct construction
    auto grid3 = makeRefinedGrid( *grid1, refine );

    // Check correctness of both
    REQUIRE( grid2->ncells( ) == 34 );
    //REQUIRE( grid3->ncells( ) == 34 );

    auto expectedParents = std::vector<CellIndex>
    { 
        NoCell, NoCell, NoCell, NoCell, 
        0, 0, 0, 0, 1, 1, 1, 1, 3, 3, 3, 3, 7, 7, 7, 7, 
        8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 
        12, 12, 12, 12, 15, 15, 15, 15 
    };

    CHECK( mesh::parents( *grid2 ) == expectedParents );
    //CHECK( mesh::parents( *grid3 ) == expectedParents );
}

TEST_CASE( "findInOtherGrid1D_test" )
{
    // mesh 0: |-------------------------------|-------------------------------|
    //         |---------------|---------------|               0
    //                 1       |-------|-------|
    //                         |---|---|---|---|
    //                           2   3   4   5
    // 
    // mesh 1: |-------------------------------|-------------------------------|
    //         |---------------|---------------|---------------|---------------|
    //         |-------|-------|-------|-------|       0               1
    //             2   |---|---|---|---|   3
    //                   4   5   6   7

    auto mesh0 = makeRefinedGrid<1>( { 2 }, { 2.0 }, { 0.0 } );
    auto mesh1 = makeRefinedGrid<1>( { 2 }, { 2.0 }, { 0.0 } );

    mesh0->refine( refineCellIndices<1>( { { 0 }, { 2 }, { 2, 3 } } ) );
    mesh1->refine( refineCellIndices<1>( { { 0, 1 }, { 0, 1 }, { 3, 4 } } ) );

    REQUIRE( mesh0->ncells( ) == 6 );
    REQUIRE( mesh0->nfull( ) == 10 );
    REQUIRE( mesh1->ncells( ) == 8 );
    REQUIRE( mesh1->nfull( ) == 14 );

    // Other index, this center, half of this width, other center, half of other width
    using Expected = std::tuple<CellIndex, std::array<double, 2>, std::array<double, 2>>;

    auto identity = std::array { 0.0, 1.0 };
    
    // Expected return values going from mesh 0 to mesh 1
    auto results = std::vector<mesh::CellInOtherGrid>
    {
        { .otherCell = 0,  .thisParent = 0, .otherLevel = 0, .thisLevel = 0 }, // cell 0
        { .otherCell = 1,  .thisParent = 1, .otherLevel = 0, .thisLevel = 0 }, // cell 1
        { .otherCell = 2,  .thisParent = 2, .otherLevel = 1, .thisLevel = 1 }, // cell 2
        { .otherCell = 3,  .thisParent = 3, .otherLevel = 1, .thisLevel = 1 }, // cell 3
        { .otherCell = 8,  .thisParent = 4, .otherLevel = 2, .thisLevel = 2 }, // cell 4
        { .otherCell = 9,  .thisParent = 5, .otherLevel = 2, .thisLevel = 2 }, // cell 5
        { .otherCell = 12, .thisParent = 6, .otherLevel = 3, .thisLevel = 3 }, // cell 6
        { .otherCell = 13, .thisParent = 7, .otherLevel = 3, .thisLevel = 3 }, // cell 7
        { .otherCell = 9,  .thisParent = 5, .otherLevel = 2, .thisLevel = 3 }, // cell 8
        { .otherCell = 9,  .thisParent = 5, .otherLevel = 2, .thisLevel = 3 }, // cell 9
    };

    // Expected leaves in mesh 1
    auto expected = std::vector<std::vector<Expected>>
    {
         { { 2, { -0.75,  0.25  }, identity }, { 4, { -0.375, 0.125 }, identity },   // cell 0
           { 5, { -0.125, 0.125 }, identity }, { 6, {  0.125, 0.125 }, identity }, 
           { 7, {  0.375, 0.125 }, identity }, { 3, {  0.75,  0.25  }, identity } },
         { { 0, { -0.5,   0.5   }, identity }, { 1, {  0.5,   0.5   }, identity } }, // cell 1
         { { 2, { -0.5,   0.5   }, identity }, { 4, {  0.25,  0.25  }, identity },   // cell 2
           { 5, {  0.75,  0.25  }, identity } },
         { { 6, { -0.75,  0.25  }, identity }, { 7, { -0.25,  0.25  }, identity },   // cell 3
           { 3, {  0.5,   0.5   }, identity } },
         { { 6, { -0.5,   0.5   }, identity }, { 7, {  0.5,   0.5   }, identity } }, // cell 4
         { { 3, identity,          identity } },                                     // cell 5
         { { 6, {  0.0,   1.0   }, identity } },                                     // cell 6
         { { 7, {  0.0,   1.0   }, identity } },                                     // cell 7
         { { 3, identity, { -0.5,   0.5   } } },                                     // cell 8
         { { 3, identity, {  0.5,   0.5   } } }                                      // cell 9
    };

    // Expected return values going from mesh 1 to mesh 0
    auto results2 = std::vector<mesh::CellInOtherGrid>
    {
        { .otherCell = 0,  .thisParent = 0,  .otherLevel = 0, .thisLevel = 0 }, // cell 0
        { .otherCell = 1,  .thisParent = 1,  .otherLevel = 0, .thisLevel = 0 }, // cell 1
        { .otherCell = 2,  .thisParent = 2,  .otherLevel = 1, .thisLevel = 1 }, // cell 2
        { .otherCell = 3,  .thisParent = 3,  .otherLevel = 1, .thisLevel = 1 }, // cell 3
        { .otherCell = 1,  .thisParent = 1,  .otherLevel = 0, .thisLevel = 1 }, // cell 4
        { .otherCell = 1,  .thisParent = 1,  .otherLevel = 0, .thisLevel = 1 }, // cell 5
        { .otherCell = 2,  .thisParent = 2,  .otherLevel = 1, .thisLevel = 2 }, // cell 6
        { .otherCell = 2,  .thisParent = 2,  .otherLevel = 1, .thisLevel = 2 }, // cell 7
        { .otherCell = 4,  .thisParent = 8,  .otherLevel = 2, .thisLevel = 2 }, // cell 8
        { .otherCell = 5,  .thisParent = 9,  .otherLevel = 2, .thisLevel = 2 }, // cell 9
        { .otherCell = 2,  .thisParent = 2,  .otherLevel = 1, .thisLevel = 3 }, // cell 10
        { .otherCell = 2,  .thisParent = 2,  .otherLevel = 1, .thisLevel = 3 }, // cell 11
        { .otherCell = 6,  .thisParent = 12, .otherLevel = 3, .thisLevel = 3 }, // cell 12
        { .otherCell = 7,  .thisParent = 13, .otherLevel = 3, .thisLevel = 3 }, // cell 13
    };

    // Expected leaves in mesh 1
    auto expected2 = std::vector<std::vector<Expected>>
    {
        { { 1, { -0.5,   0.5   }, identity }, { 2, { 0.125,  0.125 }, identity },   // cell 0
          { 3, {  0.375, 0.125 }, identity }, { 4, { 0.625,  0.125 }, identity },   
          { 5, {  0.875, 0.125 }, identity } },
        { { 0, identity,          identity } },                                     // cell 1
        { { 1, identity,          identity } },                                     // cell 2
        { { 2, { -0.75,  0.25  }, identity }, { 3, { -0.25,  0.25  }, identity },   // cell 3
          { 4, {  0.25,  0.25  }, identity }, { 5, {  0.75,  0.25  }, identity } },
        { { 0, identity, { -0.5,   0.5   } } },
        { { 0, identity, {  0.5,   0.5   } } },
        { { 1, identity, { -0.5,   0.5   } } },
        { { 1, identity, {  0.5,   0.5   } } },
        { { 2, { -0.5,   0.5   }, identity }, { 3, {  0.5,   0.5   }, identity } },
        { { 4, { -0.5,   0.5   }, identity }, { 5, {  0.5,   0.5   }, identity } },
        { { 1, identity, {  0.25,  0.25  } } },
        { { 1, identity, {  0.75,  0.25  } } },
        { { 2, identity,          identity } },
        { { 3, identity,          identity } }
    };

    REQUIRE( mesh::parents( *mesh0 ) == std::vector<CellIndex> 
        { NoCell, NoCell, 0, 0, 3, 3, 4, 4, 5, 5 } );

    REQUIRE( mesh::parents( *mesh1 ) == std::vector<CellIndex> 
        { NoCell, NoCell, 0, 0, 1, 1, 2, 2, 3, 3, 7, 7, 8, 8 } );
    
    for( size_t swapMeshes = 0; swapMeshes < 2; ++swapMeshes )
    {
        for( CellIndex thisIndex = 0; thisIndex < expected.size( ); ++thisIndex )
        {
            auto target2 = std::vector<mesh::SharedSupport<1>> { };
            auto target3 = std::vector<CellIndex> { };

            auto result1 = mesh::findInOtherGrid( *mesh0, *mesh1, thisIndex );
            auto result2 = mesh::findInOtherGrid( *mesh0, *mesh1, target2, thisIndex );
            auto result3 = mesh::findInOtherGrid( *mesh0, *mesh1, target3, thisIndex );

            REQUIRE( target2.size( ) == expected[thisIndex].size( ) );
            REQUIRE( target3.size( ) == expected[thisIndex].size( ) );

            for( auto result : { result1, result2, result3 } )
            {
                CHECK( result.otherCell == results[thisIndex].otherCell );
                CHECK( result.thisParent == results[thisIndex].thisParent );
                CHECK( result.otherLevel == results[thisIndex].otherLevel );
                CHECK( result.thisLevel == results[thisIndex].thisLevel );
            }

            for( size_t isubcell = 0; isubcell < expected[thisIndex].size( ); ++isubcell )
            {
                auto [otherIndex, thisMapping, otherMapping] = expected[thisIndex][isubcell];
        
                CHECK( target2[isubcell].otherIndex == mesh1->fullIndex( otherIndex ) );
                CHECK( target3[isubcell] == mesh1->fullIndex( otherIndex ) );

                CHECK( spatial::distance<1>( target2[isubcell].thisCell.center( ), { thisMapping[0] } ) < 1e-8 );
                CHECK( spatial::distance<1>( target2[isubcell].otherCell.center( ), { otherMapping[0] } ) < 1e-8 );
                CHECK( spatial::distance<1>( target2[isubcell].thisCell.halflengths( ), { thisMapping[1] } ) < 1e-8 );
                CHECK( spatial::distance<1>( target2[isubcell].otherCell.halflengths( ), { otherMapping[1] } ) < 1e-8 );
            }
        }

        std::swap( mesh0, mesh1 );
        std::swap( results, results2 );
        std::swap( expected, expected2 );
    }
} // findInOtherGrid1D_test

TEST_CASE( "UnstructuredMesh2D_test" )
{
    static constexpr size_t D = 2;

    /* 
     *   
     *                      _17 ----------- 14_                     --- 15   [10]
     *                  _ /   |             |   \ _                  |
     *              _ /       |             |       \ _              |
     *           12 _    [19] |     [18]    | [17]    _ 13          --- 13.5 [9]
     *           /    \ _     |             |     _ /    \           |
     *         /          \ _ |             | _ /          \         |
     *        /               7 ----------- 8               \       --- 12   [8]
     *      /      [20]      / \           / \      [16]      \      |
     *    11 _             /     \  [3]  /     \             _ 19   --- 11   [7]
     *     |   \ _        /  [4]  \     /  [2]  \        _ /   |     |
     *     |       \ _  /           \ /           \  _ /       |     |
     *     | [21]    _ 3 ----------- 1 ----------- 4 _    [15] |    --- 10   [6]
     *     |     _ /   |             |             |   \ _     |     |
     *     | _ /       |             |             |       \ _ |     |
     *    20 _    [22] |     [0]     |     [1]     | [14]    _ 23   --- 8.5  [5]
     *     |   \ _     |             |             |     _ /   |     |
     *     |       \ _ |             |             | _ /       |     |
     *     | [23]    _ 6 ----------- 9 ----------- 2 _    [13] |    --- 7    [4]
     *     |     _ /    \           / \           /    \ _     |     |
     *     | _ /          \  [7]  /     \  [5]  /          \ _ |     |
     *    10               \     /  [6]  \     /               22   --- 6    [3]
     *      \       [8]      \ /           \ /      [12]      /      |
     *        \             _ 5 ----------- 18_             /       --- 5    [2]
     *         \        _ /   |             |   \ _        /         |
     *           \  _ /       |             |       \ _  /           |
     *            0 _    [9]  |     [10]    |  [11]   _ 21          --- 3.5  [1]
     *                \ _     |             |     _ /                |
     *                    \ _ |             | _ /                    |
     *                       15 ----------- 16                      --- 2    [0]
     *   
     *     |------|----|------|------|------|------|----|------|
     *    -3     -1    0      2      4      6      8    9      11
     *    [0]    [1]  [2]    [3]    [4]    [5]    [6]  [7]    [8]
     * 
     * 
     */

    auto x = std::vector { -3.0, -1.0, 0.0, 2.0, 4.0, 6.0, 8.0, 9.0, 11.0 };
    auto y = std::vector { 2.0, 3.5, 5.0, 6.0, 7.0, 8.5, 10.0, 11.0, 12.0, 13.5, 15.0 };

    auto points = CoordinateList<D>
    {
        { x[1], y[1] }, { x[4], y[6] },  { x[6], y[4] },  { x[2], y[6] }, // vertex 0  - 3
        { x[6], y[6] }, { x[3], y[2] },  { x[2], y[4] },  { x[3], y[8] }, // vertex 4  - 7
        { x[5], y[8] }, { x[4], y[4] },  { x[0], y[3] },  { x[0], y[7] }, // vertex 8  - 11
        { x[1], y[9] }, { x[7], y[9] },  { x[5], y[10] }, { x[3], y[0] }, // vertex 12 - 15
        { x[5], y[0] }, { x[3], y[10] }, { x[5], y[2] },  { x[8], y[7] }, // vertex 16 - 19
        { x[0], y[5] }, { x[7], y[1] },  { x[8], y[3] },  { x[8], y[5] }, // vertex 20 - 23
        { x[0], y[0] }, { x[0], y[0] },                                   // unused vertices
    };

    auto connectivity = std::vector<size_t>
    {
        9,  6,  1,  3,  // cell 0  : 0  - 4 
        9,  2,  1,  4,  // cell 1  : 4  - 8 
        4,  8,  1,      // cell 2  : 8  - 11
        1,  8,  7,      // cell 3  : 11 - 14
        3,  7,  1,      // cell 4  : 14 - 17
        9,  18, 2,      // cell 5  : 17 - 20
        5,  18, 9,      // cell 6  : 20 - 23
        9,  5,  6,      // cell 7  : 23 - 26
        6,  5,  10,  0, // cell 8  : 26 - 30
        15, 5,  0,      // cell 9  : 30 - 33
        18, 5,  16, 15, // cell 10 : 33 - 37
        16, 21, 18,     // cell 11 : 37 - 40
        2,  18, 22, 21, // cell 12 : 40 - 44
        2,  22, 23,     // cell 13 : 44 - 47
        2,  4,  23,     // cell 14 : 47 - 50
        19, 23, 4,      // cell 15 : 50 - 53
        8,  4,  13, 19, // cell 16 : 53 - 57
        14, 8,  13,     // cell 17 : 57 - 60
        7,  8,  17, 14, // cell 18 : 60 - 64
        7,  17, 12,     // cell 19 : 64 - 67
        12, 11, 7,  3,  // cell 20 : 67 - 71
        20, 3,  11,     // cell 21 : 71 - 74
        3,  20, 6,      // cell 22 : 74 - 77
        6,  10, 20,     // cell 23 : 77 - 80
    };

    auto offsets = std::vector<size_t>
    {
        0, 4, 8, 11, 14, 17, 20, 23, 26, 30, 33, 37, 40,
        44, 47, 50, 53, 57, 60, 64, 67, 71, 74, 77, 80 
    };
    
    auto nfaces = std::vector<size_t> 
    {
        4, 4, 3, 3, 3, 3, 3, 3, 4, 3, 4, 3,
        4, 3, 3, 3, 4, 3, 4, 3, 4, 3, 3, 3
    };

    auto BoundaryFace = std::vector<MeshCellFace> { };

    auto expectedNeighbours = std::vector<std::vector<std::vector<MeshCellFace>>>
    {
        { { { 7,  0 } }, { { 4,  0 } }, { { 1,  2 } }, { { 22, 0 } } }, // 0
        { { { 5,  0 } }, { { 2,  0 } }, { { 0,  2 } }, { { 14, 1 } } }, // 1
        { { { 1,  1 } }, { { 16, 0 } }, { { 3,  1 } },               }, // 2
        { { { 4,  2 } }, { { 2,  2 } }, { { 18, 0 } },               }, // 3
        { { { 0,  1 } }, { { 20, 1 } }, { { 3,  0 } },               }, // 4
        { { { 1,  0 } }, { { 6,  2 } }, { { 12, 0 } },               }, // 5
        { { { 7,  1 } }, { { 10, 0 } }, { { 5,  1 } },               }, // 6
        { { { 0,  0 } }, { { 6,  0 } }, { { 8,  0 } },               }, // 7
        { { { 7,  2 } }, BoundaryFace,  { { 23, 1 } }, { { 9,  2 } } }, // 8
        { BoundaryFace,  { { 10, 3 } }, { { 8,  3 } },               }, // 9
        { { { 6,  1 } }, BoundaryFace,  { { 11, 0 } }, { { 9,  1 } } }, // 10
        { { { 10, 2 } }, BoundaryFace,  { { 12, 3 } },               }, // 11
        { { { 5,  2 } }, BoundaryFace,  { { 13, 1 } }, { { 11, 2 } } }, // 12
        { { { 14, 0 } }, { { 12, 2 } }, BoundaryFace,                }, // 13
        { { { 13, 0 } }, { { 1,  3 } }, { { 15, 2 } },               }, // 14
        { { { 16, 3 } }, BoundaryFace,  { { 14, 2 } },               }, // 15
        { { { 2,  1 } }, BoundaryFace,  { { 17, 2 } }, { { 15, 0 } } }, // 16
        { BoundaryFace,  { { 18, 3 } }, { { 16, 2 } },               }, // 17
        { { { 3,  2 } }, BoundaryFace,  { { 19, 1 } }, { { 17, 1 } } }, // 18
        { { { 20, 2 } }, { { 18, 2 } }, BoundaryFace,                }, // 19
        { BoundaryFace,  { { 4,  1 } }, { { 19, 0 } }, { { 21, 2 } } }, // 20
        { BoundaryFace,  { { 22, 1 } }, { { 20, 3 } },               }, // 21
        { { { 0,  3 } }, { { 21, 1 } }, { { 23, 0 } },               }, // 22
        { { { 22, 2 } }, { { 8,  2 } }, BoundaryFace,                }, // 23
    };

    auto memory = 24 * sizeof( std::array<double, 2> ) + connectivity.size( ) * 
       sizeof( size_t ) + offsets.size( ) * ( sizeof( size_t ) + sizeof( CellIndex ) ) + 
            ( 8 * 4 + 16 * 3 ) * sizeof( std::pair<CellIndex, std::uint8_t> );

    auto mesh = UnstructuredMesh<D>( std::move( points ), 
        std::move( connectivity ), std::move( offsets ), true, false );

    REQUIRE( mesh.ncells( ) == 24 );

    CHECK( mesh.memoryUsage( ) == memory );

    for( CellIndex icell = 0; icell < 24; ++icell )
    {
        REQUIRE( mesh.nfaces( icell ) == nfaces[icell] );

        for( size_t iface = 0; iface < nfaces[icell]; ++iface )
        {
            auto neighbours = std::vector<MeshCellFace> { };

            mesh.neighbours( icell, iface, neighbours );

            CHECK( neighbours == expectedNeighbours[icell][iface] );
        }
    }

    //auto meshProvider = createGridOnCells<D>( { 5, 5 } );
    //auto writer = VtuOutput { .filename = "outputs/UnstructuredMesh2D_test.vtu", .mode = "Ascii" };

    //writeOutput<D>( mesh, meshProvider, CellProcessor<2> { }, writer );

    auto bounds5 = mesh.boundingBox( 5 );
    auto bounds14 = mesh.boundingBox( 14 );
    auto bounds20 = mesh.boundingBox( 20 );

    CHECK( spatial::distance<2>( bounds5[0], { 4.0, 5.0 } ) < 1e-10 );
    CHECK( spatial::distance<2>( bounds5[1], { 8.0, 7.0 } ) < 1e-10 );
    CHECK( spatial::distance<2>( bounds14[0], { 8.0, 7.0 } ) < 1e-10 );
    CHECK( spatial::distance<2>( bounds14[1], { 11.0, 10.0 } ) < 1e-10 );
    CHECK( spatial::distance<2>( bounds20[0], { -3.0, 10.0 } ) < 1e-10 );
    CHECK( spatial::distance<2>( bounds20[1], { 2.0, 13.5 } ) < 1e-10 );

    auto backwardMapping = mesh.createBackwardMapping( );

    auto testdata = std::vector<std::pair<std::array<double, 2>, BackwardMapVector<2>>>
    {
        { { 1.0, 8.0 }, { { 0, { -1.0 / 3.0, 0.5 } } } },
        { { 3.0, 4.0 }, { { 10, { -1.0 / 3.0, 0.5 } } } },
        { { 4.0, 7.0 }, { { 0, { -1.0, -1.0 } }, 
                          { 1, { -1.0, -1.0 } }, 
                          { 5, { 0.0, 0.0 } }, 
                          { 6, { 0.0, 1.0 } },
                          { 7, { 0.0, 0.0 } } } },
    };

    for( auto [xy, expected] : testdata )
    {
        auto computed = BackwardMapVector<D> { };

        backwardMapping->map( xy, utilities::resize0( computed ) );
    
        REQUIRE( computed.size( ) == expected.size( ) );
        
        for( size_t iresult = 0; iresult < expected.size( ); ++iresult )
        {
            CHECK( computed[iresult].first == expected[iresult].first );
            CHECK( spatial::distance( computed[iresult].second, expected[iresult].second ) < 1e-8 );
        }
    }

    auto mapping = mesh.createMapping( );

    mesh.prepareMapping( 13, mapping );

    CHECK( spatial::distance( mesh::boundingBox( mapping )[0], { 8.0, 6.0 } ) < 1e-8 );
    CHECK( spatial::distance( mesh::boundingBox( mapping )[1], { 11.0, 8.5 } ) < 1e-8 );

    mesh.prepareMapping( 20, mapping );

    CHECK( spatial::distance( mesh::boundingBox( mapping )[0], { -3.0, 10.0 } ) < 1e-8 );
    CHECK( spatial::distance( mesh::boundingBox( mapping )[1], { 2.0, 13.5 } ) < 1e-8 );

    //auto tree = buildKdTree( mesh::boundingBoxProvider( mesh ) );
    //auto topologies = static_cast<PostprocessTopologies>( utilities::binaryPow<size_t>( D ) );
    //auto provider = createGridOnCells<D>( array::makeSizes<D>( 1 ), topologies );

    //writeOutput( tree, provider, CellProcessor<D> { }, VtuOutput { "outputs/test_tree.vtu" } );
    //writeOutput( mesh, provider, CellProcessor<D> { }, VtuOutput { "outputs/test_mesh.vtu" } );
}

TEST_CASE( "UnstructuredMesh3D_test" )
{
    static constexpr size_t D = 3;

    auto points = CoordinateList<D>
    {
        { 3.0, 2.0, 4.0 },
        { 5.0, 7.0, 3.0 },
        { 6.0, 2.0, 5.0 },
        { 4.0, 3.0, 1.0 }
    };

    auto connectivity = std::vector<size_t>
    {
        0, 1, 2, 3
    };

    auto offsets = std::vector<size_t>
    {
        0, 4
    };

    auto mesh = UnstructuredMesh<D> { std::move( points ),
        std::move( connectivity ), std::move( offsets ) };

    //auto meshProvider = createGridOnCells<D>( { 3, 3, 3 } );
    //auto writer = VtuOutput { .filename = "outputs/UnstructuredMesh3D_test.vtu", .mode = "Ascii" };

    //writeOutput<D>( mesh, meshProvider, CellProcessor<D> { }, writer );
}

TEST_CASE( "topology_constexpr_test" )
{
    static_assert( topology::nfaces<0>( CellType::NCube ) == 0 );
    static_assert( topology::nfaces<1>( CellType::NCube ) == 2 );
    static_assert( topology::nfaces<2>( CellType::NCube ) == 4 );
    static_assert( topology::nfaces<3>( CellType::NCube ) == 6 );
    static_assert( topology::nfaces<4>( CellType::NCube ) == 8 );
    
    static_assert( topology::nfaces<0>( CellType::Simplex ) == 1 );
    static_assert( topology::nfaces<1>( CellType::Simplex ) == 2 );
    static_assert( topology::nfaces<2>( CellType::Simplex ) == 3 );
    static_assert( topology::nfaces<3>( CellType::Simplex ) == 4 );
    static_assert( topology::nfaces<4>( CellType::Simplex ) == 5 );

    static_assert( topology::nvertices<0>( CellType::NCube ) == 1 );
    static_assert( topology::nvertices<1>( CellType::NCube ) == 2 );
    static_assert( topology::nvertices<2>( CellType::NCube ) == 4 );
    static_assert( topology::nvertices<3>( CellType::NCube ) == 8 );
    static_assert( topology::nvertices<4>( CellType::NCube ) == 16 );
    
    static_assert( topology::nvertices<0>( CellType::Simplex ) == 1 );
    static_assert( topology::nvertices<1>( CellType::Simplex ) == 2 );
    static_assert( topology::nvertices<2>( CellType::Simplex ) == 3 );
    static_assert( topology::nvertices<3>( CellType::Simplex ) == 4 );
    static_assert( topology::nvertices<4>( CellType::Simplex ) == 5 );
}

TEST_CASE( "faceVertices_test" )
{
    auto tmp = std::vector<size_t> { 44 };

    // Line (NCube)
    topology::faceVertices<1>( CellType::NCube, 1, tmp );

    CHECK( tmp == std::vector<size_t> { 44, 1 } );

    topology::faceVertices<1>( CellType::NCube, 0, tmp );

    CHECK( tmp == std::vector<size_t> { 44, 1, 0 } );

    // Square
    topology::faceVertices<2>( CellType::NCube, 2, utilities::resize0( tmp ) );

    CHECK( tmp == std::vector<size_t> { 0, 2 } );

    topology::faceVertices<2>( CellType::NCube, 3, tmp );
    
    CHECK( tmp == std::vector<size_t> { 0, 2, 1, 3 } );

    topology::faceVertices<2>( CellType::NCube, 1, utilities::resize0( tmp ) );
    
    CHECK( tmp == std::vector<size_t> { 2, 3 } );

    topology::faceVertices<2>( CellType::NCube, 0, utilities::resize0( tmp ) );
    
    CHECK( tmp == std::vector<size_t> { 0, 1 } );

    // Cube
    utilities::resize0( tmp );

    for( size_t iface = 0; iface < 6; ++iface )
    {
        topology::faceVertices<3>( CellType::NCube, iface, tmp );
    }

    CHECK( tmp == std::vector<size_t> { 0, 1, 2, 3,  4, 5, 6, 7,
                                        0, 1, 4, 5,  2, 3, 6, 7,
                                        0, 2, 4, 6,  1, 3, 5, 7 } );

    // Line (Simplex)
    topology::faceVertices<1>( CellType::Simplex, 0, utilities::resize0( tmp ) );

    CHECK( tmp == std::vector<size_t> { 0 } );
    
    topology::faceVertices<1>( CellType::Simplex, 1, utilities::resize0( tmp ) );

    CHECK( tmp == std::vector<size_t> { 1 } );

    // Triangle
    topology::faceVertices<2>( CellType::Simplex, 1, tmp );
    topology::faceVertices<2>( CellType::Simplex, 0, tmp );

    CHECK( tmp == std::vector<size_t> { 1,  0, 1,  0, 2 } );

    topology::faceVertices<2>( CellType::Simplex, 2, utilities::resize0( tmp ) );
    
    CHECK( tmp == std::vector<size_t> { 1, 2 } );

    // Hexaedron
    topology::faceVertices<3>( CellType::Simplex, 1, tmp );
    topology::faceVertices<3>( CellType::Simplex, 3, tmp );

    CHECK( tmp == std::vector<size_t> { 1, 2,  0, 1, 3,  1, 2, 3 } );

    topology::faceVertices<3>( CellType::Simplex, 2, utilities::resize0( tmp ) );
    topology::faceVertices<3>( CellType::Simplex, 0, tmp );
    
    CHECK( tmp == std::vector<size_t> { 0, 1, 2,  0, 2, 3 } );
}

TEST_CASE( "mapBackward_test" )
{
    auto ncells = std::array { size_t { 4 }, size_t { 3 } };
    auto resolution = std::array { size_t { 8 }, size_t { 8 } };
    auto npoints = array::add( array::multiply( ncells, resolution ), size_t { 1 } );

    // TODO: make non-unique backward mapping work with Cartesian grid
    //auto mesh = makeCartesianGrid<2>( ncells, array::convert<double>( ncells ) );

    auto mesh = MeshSharedPtr<2> { };
    {
        auto ticks = spatial::cartesianTickVectors<2>( ncells, array::convert<double>( ncells ), { } );
        auto points = spatial::tensorProduct( ticks );

        auto cells = std::vector<size_t> { };
        auto offsets = std::vector<size_t> { 0 };

        nd::execute( ncells, [&]( std::array<size_t, 2> ij )
        { 
            cells.push_back( ( ij[0] + 0 ) * ( ncells[1] + 1 ) + ( ij[1] + 0 ) );
            cells.push_back( ( ij[0] + 0 ) * ( ncells[1] + 1 ) + ( ij[1] + 1 ) );
            cells.push_back( ( ij[0] + 1 ) * ( ncells[1] + 1 ) + ( ij[1] + 0 ) );
            cells.push_back( ( ij[0] + 1 ) * ( ncells[1] + 1 ) + ( ij[1] + 1 ) );

            offsets.push_back( cells.size( ) );
        } );

        mesh = std::make_shared<UnstructuredMesh<2>>( std::move( 
            points ), std::move( cells ), std::move( offsets ) );
    }

    // Generate global coordinates
    auto xyz = CoordinateList<2> { };

    nd::execute( npoints, [&]( std::array<size_t, 2> ij )
    { 
        xyz.push_back( std::array { ( 4.0 * ij[0] ) / ( npoints[0] - 1.0 ), 
                                    ( 3.0 * ij[1] ) / ( npoints[1] - 1.0 ) } );
    } );
    
    // Determine expected results by computing forward mapping on each cell
    auto expectedIndices = std::vector<std::vector<CellIndex>>( array::product( npoints ) );
    auto expectedRst = std::vector<std::vector<std::array<double, 2>>>( array::product( npoints ) );

    nd::execute( ncells, [&]( std::array<size_t, 2> ijCell ) 
    { 
        auto linearCellIndex = ijCell[0] * ncells[1] + ijCell[1];

        nd::execute( array::add( resolution, size_t { 1 } ), [&]( std::array<size_t, 2> ijPointLocal )
        {
            auto ijPointGlobal = array::add( array::multiply( ijCell, resolution ), ijPointLocal );
            auto linearPointIndex = ijPointGlobal[0] * npoints[1] + ijPointGlobal[1];

            auto rst = 2.0 * array::convert<double>( ijPointLocal ) / array::convert<double>( resolution ) - 1.0;

            expectedIndices[linearPointIndex].push_back( static_cast<CellIndex>( linearCellIndex ) );
            expectedRst[linearPointIndex].push_back( rst );
        } );
    } );

    // Insert some outside points
    xyz.insert( xyz.begin( ), { -1.0, 2.0 } );
    xyz.insert( utilities::begin( xyz, xyz.size( ) / 2 ), { 59.0, 2.0 } );
    xyz.insert( xyz.end( ), { 1.0, 200.0 } );

    expectedIndices.insert( expectedIndices.begin( ), std::vector<CellIndex> { } );
    expectedIndices.insert( utilities::begin( expectedIndices, expectedIndices.size( ) / 2 ), std::vector<CellIndex> { } );
    expectedIndices.insert( expectedIndices.end( ), std::vector<CellIndex> { } );

    expectedRst.insert( expectedRst.begin( ), std::vector<std::array<double, 2>>{ } );
    expectedRst.insert( utilities::begin( expectedRst, expectedRst.size( ) / 2 ), std::vector<std::array<double, 2>>{ } );
    expectedRst.insert( expectedRst.end( ), std::vector<std::array<double, 2>>{ } );

    // Compute and check result
    auto computed = mesh::mapBackwardMultiple<2>( *mesh, xyz );

    REQUIRE( computed.first.size( ) == expectedIndices.size( ) + 1 );

    bool correct = true;

    for( size_t i = 0; i + 1 < computed.first.size( ); ++i )
    {
        auto backwardI = utilities::linearizedSpan( computed, i );

        correct = correct && ( backwardI.size( ) == expectedIndices[i].size( ) );
        
        if( correct )
        {
            for( size_t j = 0; j < backwardI.size( ); ++j )
            {
                correct = correct && ( backwardI[j].first == expectedIndices[i][j] );
                correct = correct && ( spatial::distance( backwardI[j].second, expectedRst[i][j] ) < 1e-10 );
            }
        }
    }

    CHECK( correct );

    // Check single version
    xyz = { { 1.9, 1.8 }, { -6.0, 1.0 }, { 0.6, 0.4 }, { 2.3, 2.2 } };

    auto computed2 = mesh::mapBackwardSingle<2>( *mesh, xyz );

    REQUIRE( computed2.size( ) == 4 );
    REQUIRE( ( computed2[0] && computed2[2] && computed2[3] ) );

    CHECK( computed2[1] == std::nullopt );
    CHECK( computed2[0]->first == 4 );
    CHECK( computed2[2]->first == 0 );
    CHECK( computed2[3]->first == 8 );

    CHECK( spatial::distance<2>( computed2[0]->second, { 0.8, 0.6 } ) < 1e-10 );
    CHECK( spatial::distance<2>( computed2[2]->second, { 0.2, -0.2 } ) < 1e-10 );
    CHECK( spatial::distance<2>( computed2[3]->second, { -0.4, -0.6 } ) < 1e-10 );
}

TEST_CASE( "AggregateMesh_test" )
{ 
    // imesh, icell:      ________
    //                 / |        |
    //              /1,1 |   2,2  |
    //           /_______|________|
    //        / |        |        |
    //     / 1,0|   1,2  |   2,1  |
    //  /_______|________|________|
    // |        |        |        |
    // |   0,0  |   0,2  |   2,0  |
    // |________|________|________|
    //

    auto vertices = CoordinateList<2> 
    { 
        { 2.0, 4.0 }, 
        { 3.0, 5.0 }, 
        { 4.0, 6.0 }, 
        { 3.0, 4.0 }, 
        { 4.0, 5.0 }, 
        { 4.0, 4.0 } 
    };

    auto cells = std::vector<size_t> { 1, 0, 3, 4, 2, 1, 3, 1, 5, 4 };
    auto offsets = std::vector<size_t> { 0, 3, 6, 10 };
 
    auto componentMesh0 = makeRefinedGrid<2>( { 2, 1 }, { 2.0, 1.0 }, { 2.0, 3.0 } );
    auto componentMesh1 = std::make_shared<UnstructuredMesh<2>>( std::move( vertices ), std::move( cells ), std::move( offsets ) );
    auto componentMesh2 = makeCartesianGrid<2>( { 1, 3 }, { 1.0, 3.0 }, { 4.0, 3.0 } );

    auto mesh = AggregateMesh<2>( *componentMesh0, *componentMesh1, *componentMesh2 );

    // Test different constructors
    auto meshVector = std::vector<typename AggregateMesh<2>::MeshPtr> { componentMesh0, componentMesh1, componentMesh2 };
    auto meshList = std::initializer_list<typename AggregateMesh<2>::MeshPtr> { componentMesh0, componentMesh1, componentMesh2 };

    auto mesh2 = AggregateMesh<2>( componentMesh0, componentMesh1, componentMesh2 );
    auto mesh3 = AggregateMesh<2>( meshVector );
    auto mesh4 = AggregateMesh<2>( meshList );

    REQUIRE( mesh.ncells( ) == 8 );

    CHECK( mesh2.ncells( ) == mesh.ncells( ) );
    CHECK( mesh3.ncells( ) == mesh.ncells( ) );
    CHECK( mesh4.ncells( ) == mesh.ncells( ) );

    // Mapping
    auto mapping = mesh.createMapping( );

    auto testpoints = std::vector
    {
        std::tuple { CellIndex { 0 }, std::array { 0.0, 0.2 }, std::array { 2.5, 3.6 } },
        std::tuple { CellIndex { 1 }, std::array { -0.6, 0.0 }, std::array { 3.2, 3.5 } },
        std::tuple { CellIndex { 2 }, std::array { 0.0, 0.5 }, std::array { 3.0, 4.5 } },
        std::tuple { CellIndex { 3 }, std::array { 1.0, 0.0 }, std::array { 4.0, 6.0 } },
        std::tuple { CellIndex { 4 }, std::array { 0.8, 0.0 }, std::array { 3.9, 4.5 } },
        std::tuple { CellIndex { 5 }, std::array { 0.4, 0.4 }, std::array { 4.7, 3.7 } },
        std::tuple { CellIndex { 6 }, std::array { 0.2, -1.0 }, std::array { 4.6, 4.0 } },
        std::tuple { CellIndex { 7 }, std::array { -0.4, 0.6 }, std::array { 4.3, 5.8 } },
    };

    for( const auto& [icell, rst, xyz] : testpoints )
    {
        mesh.prepareMapping( icell, mapping );

        CHECK( mapping.icell == icell );
        CHECK( spatial::distance<2>( mapping( rst ), xyz ) < 1e-10 );
    }
}

TEST_CASE( "gridspacing_test" )
{
    CHECK( mesh::gridsplit<2>( { 0.1, 0.1 }, 0 ) == std::array<size_t, 2> { 0, 0 } );
    CHECK( mesh::gridsplit<2>( { 0.1, 0.1 }, 1 ) == std::array<size_t, 2> { 1, 1 } );
    CHECK( mesh::gridsplit<2>( { 5.0, 2.0 }, 38 ) == std::array<size_t, 2> { 10, 4 } );
    CHECK( mesh::gridsplit<2>( { 5.0, 2.0 }, 40 ) == std::array<size_t, 2> { 10, 4 } );
    CHECK( mesh::gridsplit<2>( { 5.0, 2.0 }, 43 ) == std::array<size_t, 2> { 10, 4 } );
    CHECK( mesh::gridsplit<2>( { 1.0, 1.0 }, 12 ) == std::array<size_t, 2> { 3, 3 } );
    CHECK( mesh::gridsplit<2>( { 1.0, 1.0 }, 13 ) == std::array<size_t, 2> { 4, 4 } );
    CHECK( mesh::gridsplit<3>( { 2.0, 4.0, 3.0 }, 632 ) == std::array<size_t, 3> { 6, 12, 9 } );
    CHECK( mesh::gridsplit<3>( { 2.0, 4.0, 3.0 }, 648 ) == std::array<size_t, 3> { 6, 12, 9 } );
    CHECK( mesh::gridsplit<3>( { 2.0, 4.0, 3.0 }, 661 ) == std::array<size_t, 3> { 6, 12, 9 } );
}

} // namespace mlhp
