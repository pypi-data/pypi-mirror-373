// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/implicit.hpp"

namespace mlhp
{

TEST_CASE( "addIntersectSubtract_test" )
{
    auto circle1 = implicit::sphere<2>( { 0.0, 0.0 }, 1.1 );
    auto circle2 = implicit::sphere<2>( { 1.0, 0.0 }, 1.1 );
    auto circle3 = implicit::sphere<2>( { 2.0, 0.0 }, 1.1 );

    auto add1 = implicit::add( circle2 );
    auto add2 = implicit::add( circle2, circle1 );
    auto add3 = implicit::add( circle2, circle1, circle3 );

    auto intersect1 = implicit::intersect( circle2 );
    auto intersect2 = implicit::intersect( circle2, circle1 );
    auto intersect3 = implicit::intersect( circle2, circle1, circle3 );

    auto subtract1 = implicit::subtract( circle2 );
    auto subtract2 = implicit::subtract( circle2, circle1 );
    auto subtract3 = implicit::subtract( circle2, circle1, circle3 );

    std::array<double, 2> onlyIn1 { 0.0, 1.0 };
    std::array<double, 2> in1and2 { 0.5, 0.0 };
    std::array<double, 2> onlyIn2 { 1.0, 1.0 };
    std::array<double, 2> in2and3 { 1.5, 0.0 };
    std::array<double, 2> onlyIn3 { 2.0, 1.0 };
    std::array<double, 2> inAll   { 1.0, 0.0 };

    std::array<std::array<double, 2>, 6> testPoints { onlyIn1, in1and2, onlyIn2, in2and3, onlyIn3,  inAll };

    std::array<bool, 6> expectedSingleOperand       {   false,    true,    true,    true,   false,   true };
    std::array<bool, 6> expectedAdd2                {    true,    true,    true,    true,   false,   true };
    std::array<bool, 6> expectedAdd3                {    true,    true,    true,    true,    true,   true };
    std::array<bool, 6> expectedIntersect2          {   false,    true,   false,   false,   false,   true };
    std::array<bool, 6> expectedIntersect3          {   false,   false,   false,   false,   false,   true };
    std::array<bool, 6> expectedSubtract2           {   false,   false,    true,    true,   false,  false };
    std::array<bool, 6> expectedSubtract3           {   false,   false,    true,   false,   false,  false };

    for( size_t i = 0; i < 6; ++i )
    {
        CHECK( add1( testPoints[i] ) == expectedSingleOperand[i] );
        CHECK( add2( testPoints[i] ) == expectedAdd2[i] );
        CHECK( add3( testPoints[i] ) == expectedAdd3[i] );

        CHECK( intersect1( testPoints[i] ) == expectedSingleOperand[i] );
        CHECK( intersect2( testPoints[i] ) == expectedIntersect2[i] );
        CHECK( intersect3( testPoints[i] ) == expectedIntersect3[i] );

        CHECK( subtract1( testPoints[i] ) == expectedSingleOperand[i] );
        CHECK( subtract2( testPoints[i] ) == expectedSubtract2[i] );
        CHECK( subtract3( testPoints[i] ) == expectedSubtract3[i] );
    }
}

TEST_CASE( "cube_test" )
{
    std::array<double, 3> x1 { 0.0, 0.0, 0.0 };
    std::array<double, 3> x2 { 1.0, 1.0, 1.0 };

    auto cube = implicit::cube( x1, x2 );

    CHECK( cube( { -1.0, -1.0, -1.0 } ) == false );
}

TEST_CASE( "sliceLast_test" )
{
    auto sphere = implicit::sphere<3>( { 3.0, 2.0, 7.0 }, 2.0 );

    auto slicedSphere = implicit::sliceLast( sphere, 6.0 );

    double slicedRadius = 1.7320508075688772;
    double epsilon = 1e-8;

    CHECK( slicedSphere( { 3.0, 2.0 } ) == true );

    CHECK( slicedSphere( { 3.0 + slicedRadius - epsilon, 2.0 } ) == true );
    CHECK( slicedSphere( { 3.0 + slicedRadius + epsilon, 2.0 } ) == false );
    CHECK( slicedSphere( { 3.0 - slicedRadius + epsilon, 2.0 } ) == true );
    CHECK( slicedSphere( { 3.0 - slicedRadius - epsilon, 2.0 } ) == false );

    CHECK( slicedSphere( { 3.0, 2.0 + slicedRadius - epsilon } ) == true );
    CHECK( slicedSphere( { 3.0, 2.0 + slicedRadius + epsilon } ) == false );
    CHECK( slicedSphere( { 3.0, 2.0 - slicedRadius + epsilon } ) == true );
    CHECK( slicedSphere( { 3.0, 2.0 - slicedRadius - epsilon } ) == false );
}

} // namespace mlhp
