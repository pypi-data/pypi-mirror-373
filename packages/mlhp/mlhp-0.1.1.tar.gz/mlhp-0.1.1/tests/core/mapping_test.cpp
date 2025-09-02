// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"
#include "mlhp/core/mapping.hpp"
#include "mlhp/core/spatial.hpp"

#include <cmath>

namespace mlhp
{

TEST_CASE( "computeDeterminant_test" )
{
    auto J = std::array { -2.0, -5.0,
                          -1.0,  1.0,
                           2.0,  2.0 };

    CHECK( spatial::computeDeterminant<3, 2>( J ) == Approx( std::sqrt( 101 ) ).epsilon( 1e-6 ) );
}

TEST_CASE( "TriangleMapping_test" )
{
    auto v1 = std::array { 2.0, 3.0, -1.0 };
    auto v2 = std::array { 0.0, 2.0, 1.0 };
    auto v3 = std::array { -3.0, 4.0, 1.0 };

    auto mapping = TriangleMapping<3> ( v1, v2, v3 );
    
    CHECK( mapping.gdim == 3 );
    CHECK( mapping.ldim == 2 );
    CHECK( mapping.type == map::Type::Simplex );

    CHECK( spatial::distance( mapping.map( { 0.0, 0.0 } ), v1 ) < 1e-8 );
    CHECK( spatial::distance( mapping.map( { 1.0, 0.0 } ), v2 ) < 1e-8 );
    CHECK( spatial::distance( mapping.map( { 0.0, 1.0 } ), v3 ) < 1e-8 );
    
    CHECK( spatial::distance( mapping.map( { 0.5, 0.0 } ), 0.5 * ( v1 + v2 ) ) < 1e-8 );
    CHECK( spatial::distance( mapping.map( { 0.0, 0.5 } ), 0.5 * ( v1 + v3 ) ) < 1e-8 );
    CHECK( spatial::distance( mapping.map( { 0.5, 0.5 } ), 0.5 * ( v2 + v3 ) ) < 1e-8 );

    auto mapping2 = TriangleMapping<3>( std::array { v1, v2, v3 } );

    CHECK( spatial::distance( mapping2( { 0.5, 0.5 } ), 0.5 * ( v2 + v3 ) ) < 1e-8 );
    
    auto v = v1 + 0.2 * ( v2 - v1 ) + 0.3 * ( v3 - v1 );

    CHECK( spatial::distance( mapping.map( { 0.2, 0.3 } ), v ) < 1e-8 );
    CHECK( spatial::distance( map::withDetJ( mapping, { 0.2, 0.3 } ).first, v ) < 1e-8 );
    CHECK( spatial::distance( map::withJ( mapping, { 0.2, 0.3 } ).first, v ) < 1e-8 );
    
    auto area = spatial::norm( spatial::cross( v2 - v1, v3 - v1 ) ) / 2.0; 

    CHECK( std::abs( mapping.detJ( { 0.4, 0.2 } ) - 2.0 * area ) < 1e-8 );
    CHECK( std::abs( mapping.detJ( { 0.1, 0.4 } ) - 2.0 * area ) < 1e-8 );

    CHECK( std::abs( map::withDetJ( mapping, { 0.4, 0.2 } ).second - 2.0 * area ) < 1e-8 );
    CHECK( std::abs( map::withDetJ( mapping, { 0.1, 0.4 } ).second - 2.0 * area ) < 1e-8 );

    auto Ja = mapping.J( { 0.0, 0.0 } );
    auto Jb = map::withJ( mapping, { 0.0, 0.0 } ).second;

    for( const auto& J : { Ja, Jb } )
    {
        auto d2 = v1 + linalg::mvproduct<3, 2>( J, std::array { 1.0, 0.0 } );
        auto d3 = v1 + linalg::mvproduct<3, 2>( J, std::array { 0.0, 1.0 } );
        auto d4 = v1 + linalg::mvproduct<3, 2>( J, std::array { 0.5, 0.5 } );

        CHECK( spatial::distance( d2, v2 ) < 1e-8 );
        CHECK( spatial::distance( d3, v3 ) < 1e-8 );
        CHECK( spatial::distance( d4, 0.5 * ( v2 + v3 ) ) < 1e-8 );    
    }

} // TriangleMapping_test

TEST_CASE( "CartesianMapping_test" )
{
    auto bounds = std::array { std::array { 2.0, -3.0 }, std::array { 5.0, -2.0 } };
    auto mapping = CartesianMapping<2> { bounds };
    
    CHECK( mapping.gdim == 2 );
    CHECK( mapping.ldim == 2 );
    CHECK( mapping.type == map::Type::NCube );

    CHECK( spatial::distance<2>( mapping( {  0.0, 0.0 } ), { 3.5, -2.5  } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping( { -0.4, 0.7 } ), { 2.9, -2.15 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping( {  0.8, 0.1 } ), { 4.7, -2.45 } ) < 1e-8 );

    CHECK( spatial::distance<2>( mapping.map( {  0.0, 0.0 } ), { 3.5, -2.5  } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping.map( { -0.4, 0.7 } ), { 2.9, -2.15 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping.map( {  0.8, 0.1 } ), { 4.7, -2.45 } ) < 1e-8 );
    
    auto rst = std::array { 0.3, -0.9 };
    auto xyz = std::array { 3.95, -2.95 };
    auto J = std::array { 1.5, 0.0, 0.0, 0.5 };
    auto detJ = Approx( 1.5 * 0.5 ).epsilon( 1e-8 );

    CHECK( mapping( rst, map::DetJ ).detJ == detJ );
    CHECK( mapping.detJ( rst ) == detJ );
    
    CHECK( spatial::distance( mapping( rst, map::J ).J, J ) < 1e-8 );
    CHECK( spatial::distance( mapping.J( rst ), J ) < 1e-8 );

    auto [xyz1, J1] = map::withJ( mapping, rst );
    auto [xyz2, detJ2] = map::withDetJ( mapping, rst );
    
    CHECK( spatial::distance<2>( xyz1, xyz ) < 1e-8 );
    CHECK( spatial::distance<2>( xyz2, xyz ) < 1e-8 );
    
    CHECK( detJ2 == detJ );
    CHECK( spatial::distance<4>( J1, J ) < 1e-8 );
}

TEST_CASE( "NCubeMapping_test" )
{   
    /*
     *       [3] O
     *          /  \ _
     *        /        \ _
     *       /              \ _
     *      /                   \
     * [2] O                      O [1]
     *      \                   /
     *        \              /
     *          \         /
     *            \    /
     *              O
     *             [0]
     */     

    auto v0 = std::array { 1.5, 2.0 };
    auto v1 = std::array { 3.0, 3.0 };
    auto v2 = std::array { 0.5, 3.2 };
    auto v3 = std::array { 1.0, 4.0 };

    auto mapping = NCubeMapping<2> { { v0, v1, v2, v3 } };
    
    CHECK( spatial::distance( mapping( { -1.0, -1.0 } ), v0 ) < 1e-8 );
    CHECK( spatial::distance( mapping( { -1.0,  1.0 } ), v1 ) < 1e-8 );
    CHECK( spatial::distance( mapping( {  1.0, -1.0 } ), v2 ) < 1e-8 );
    CHECK( spatial::distance( mapping( {  1.0,  1.0 } ), v3 ) < 1e-8 );
}

TEST_CASE( "NCubeCollapsedToSimplex_test" )
{
    auto mapping0 = NCubeCollapsedToSimplex<0>{ };
    
    CHECK( mapping0( { } ) == std::array<double, 0> { } );
    CHECK( mapping0.detJ( { } ) == Approx( 1.0 ).epsilon( 1e-8 ) );

    auto mapping1 = NCubeCollapsedToSimplex<1>{ };
    
    CHECK( spatial::distance( mapping1( { -1.0 } ), { 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping1( {  1.0 } ), { 1.0 } ) < 1e-8 );
    
    CHECK( mapping1.detJ( { -1.0 } ) == Approx( 1.0 / 2.0 ).epsilon( 1e-8 ) );
    CHECK( mapping1.detJ( {  1.0 } ) == Approx( 1.0 / 2.0 ).epsilon( 1e-8 ) );

    auto mapping2 = NCubeCollapsedToSimplex<2>{ };
    
    CHECK( spatial::distance( mapping2( { -1.0, -1.0 } ), { 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping2( { -1.0,  1.0 } ), { 0.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping2( {  1.0, -1.0 } ), { 1.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping2( {  1.0,  1.0 } ), { 0.5, 0.5 } ) < 1e-8 );

    CHECK( mapping2.detJ( { -1.0, -1.0 } ) == Approx( 1.0 / 4.0 ).epsilon( 1e-8 ) );
    CHECK( mapping2.detJ( { -1.0,  1.0 } ) == Approx( 1.0 / 8.0 ).epsilon( 1e-8 ) );
    CHECK( mapping2.detJ( {  1.0, -1.0 } ) == Approx( 1.0 / 8.0 ).epsilon( 1e-8 ) );
    CHECK( mapping2.detJ( {  1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );

    auto mapping3 = NCubeCollapsedToSimplex<3>{ };

    CHECK( spatial::distance( mapping3( { -1.0, -1.0, -1.0 } ), { 0.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping3( { -1.0, -1.0,  1.0 } ), { 0.0, 0.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping3( { -1.0,  1.0, -1.0 } ), { 0.0, 1.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping3( { -1.0,  1.0,  1.0 } ), { 0.0, 0.5, 0.5 } ) < 1e-8 );
    CHECK( spatial::distance( mapping3( {  1.0, -1.0, -1.0 } ), { 1.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping3( {  1.0, -1.0,  1.0 } ), { 0.5, 0.0, 0.5 } ) < 1e-8 );
    CHECK( spatial::distance( mapping3( {  1.0,  1.0, -1.0 } ), { 0.5, 0.5, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping3( {  1.0,  1.0,  1.0 } ), { 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0 } ) < 1e-8 );

    CHECK( mapping3.detJ( { -1.0, -1.0, -1.0 } ) == Approx( 1.0 / 8.0 ).epsilon( 1e-8 ) );
    CHECK( mapping3.detJ( { -1.0, -1.0,  1.0 } ) == Approx( 1.0 / 32.0 ).epsilon( 1e-8 ) );
    CHECK( mapping3.detJ( { -1.0,  1.0, -1.0 } ) == Approx( 1.0 / 32.0 ).epsilon( 1e-8 ) );
    CHECK( mapping3.detJ( { -1.0,  1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping3.detJ( {  1.0, -1.0, -1.0 } ) == Approx( 1.0 / 32.0 ).epsilon( 1e-8 ) );
    CHECK( mapping3.detJ( {  1.0, -1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping3.detJ( {  1.0,  1.0, -1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping3.detJ( {  1.0,  1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );

    auto mapping4 = NCubeCollapsedToSimplex<4>{ };

    CHECK( spatial::distance( mapping4( { -1.0, -1.0, -1.0, -1.0 } ), { 0.0, 0.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( { -1.0, -1.0, -1.0,  1.0 } ), { 0.0, 0.0, 0.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( { -1.0, -1.0,  1.0, -1.0 } ), { 0.0, 0.0, 1.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( { -1.0, -1.0,  1.0,  1.0 } ), { 0.0, 0.0, 0.5, 0.5 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( { -1.0,  1.0, -1.0, -1.0 } ), { 0.0, 1.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( { -1.0,  1.0, -1.0,  1.0 } ), { 0.0, 0.5, 0.0, 0.5 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( { -1.0,  1.0,  1.0, -1.0 } ), { 0.0, 0.5, 0.5, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( { -1.0,  1.0,  1.0,  1.0 } ), { 0.0, 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( {  1.0, -1.0, -1.0, -1.0 } ), { 1.0, 0.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( {  1.0, -1.0, -1.0,  1.0 } ), { 0.5, 0.0, 0.0, 0.5 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( {  1.0, -1.0,  1.0, -1.0 } ), { 0.5, 0.0, 0.5, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( {  1.0, -1.0,  1.0,  1.0 } ), { 1.0 / 3.0, 0.0, 1.0 / 3.0, 1.0 / 3.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( {  1.0,  1.0, -1.0, -1.0 } ), { 0.5, 0.5, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( {  1.0,  1.0, -1.0,  1.0 } ), { 1.0 / 3.0, 1.0 / 3.0, 0.0, 1.0 / 3.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( {  1.0,  1.0,  1.0, -1.0 } ), { 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance( mapping4( {  1.0,  1.0,  1.0,  1.0 } ), { 0.25, 0.25, 0.25, 0.25 } ) < 1e-8 );
    
    CHECK( mapping4.detJ( { -1.0, -1.0, -1.0, -1.0 } ) == Approx( 1.0 / 16.0 ).epsilon( 1e-8 ) );
    CHECK( mapping4.detJ( { -1.0, -1.0, -1.0,  1.0 } ) == Approx( 1.0 / 128.0 ).epsilon( 1e-8 ) );
    CHECK( mapping4.detJ( { -1.0, -1.0,  1.0, -1.0 } ) == Approx( 1.0 / 128.0 ).epsilon( 1e-8 ) );
    CHECK( mapping4.detJ( { -1.0, -1.0,  1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping4.detJ( { -1.0,  1.0, -1.0, -1.0 } ) == Approx( 1.0 / 128.0 ).epsilon( 1e-8 ) );
    CHECK( mapping4.detJ( { -1.0,  1.0, -1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping4.detJ( { -1.0,  1.0,  1.0, -1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping4.detJ( { -1.0,  1.0,  1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping4.detJ( {  1.0, -1.0, -1.0, -1.0 } ) == Approx( 1.0 / 128.0 ).epsilon( 1e-8 ) );
    CHECK( mapping4.detJ( {  1.0, -1.0, -1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping4.detJ( {  1.0, -1.0,  1.0, -1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping4.detJ( {  1.0, -1.0,  1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping4.detJ( {  1.0,  1.0, -1.0, -1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping4.detJ( {  1.0,  1.0, -1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping4.detJ( {  1.0,  1.0,  1.0, -1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
    CHECK( mapping4.detJ( {  1.0,  1.0,  1.0,  1.0 } ) == Approx( 0.0 ).margin( 1e-8 ) );
}

TEST_CASE( "ConcatenatedMapping_test" )
{
    auto mapping1 = SimplexMapping<2, 1> 
    { 
        std::array { 0.0, 1.0 / 3.0 }, 
        std::array { 1.0 / 3.0, 2.0 / 3.0 } 
    };

    auto mapping2 = SimplexMapping<3, 2> 
    { 
        std::array { 3.0, 1.0, -2.0 }, 
        std::array { 0.0, -2.0, 2.0 }, 
        std::array { 6.0, -2.0, 1.0 } 
    };

    auto mapping = ConcatenatedMapping<3, 1, 2> { &mapping2, &mapping1 };

    CHECK( spatial::distance<3>( mapping( { 0.0 } ), { 4.0, 0.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping( { 0.5 } ), { 4.0, -1.0, 1.0 / 6.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping( { 1.0 } ), { 4.0, -2.0, 4.0 / 3.0 } ) < 1e-8 );

    CHECK( spatial::distance<2>( mapping1.J( { 0.3 } ), { 1.0 / 3.0, 1.0 / 3.0 } ) < 1e-8 );
    CHECK( mapping1.detJ( { 0.6 } ) == Approx( std::sqrt( 2.0 / 9.0 ) ).epsilon( 1e-8 ) );
    
    CHECK( spatial::distance<6>( mapping2.J( { 0.0, 1.0 / 3.0 } ), 
        { -3.0, 3.0, -3.0, -3.0, 4.0, 3.0 } ) < 1e-8 );
    CHECK( mapping2.detJ( { 0.0, 1.0 / 3.0 } ) == Approx( std::sqrt( 774.0 ) ).epsilon( 1e-8 ) );
    
    CHECK( spatial::distance<3>( mapping.J( { 0.8 } ), { 0.0, -2.0, 7.0 / 3.0 } ) < 1e-8 );
    CHECK( mapping.detJ( { 0.8 } ) == Approx( std::sqrt( 85.0 / 9.0 ) ).epsilon( 1e-8 ) );
}

TEST_CASE( "faceMapping_test" )
{
    // Edge - left
    auto mapping1 = FaceMapping<1>( CellType::NCube, 0 );

    CHECK( spatial::distance<1>( mapping1( { } ), { -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<1>( mapping1.normal( ), { -1.0 } ) < 1e-8 );
    
    // Edge - right
    mapping1 = FaceMapping<1>( CellType::NCube, 1 );

    CHECK( spatial::distance<1>( mapping1( { } ), {  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<1>( mapping1.normal( ), {  1.0 } ) < 1e-8 );

    // Quad - left
    auto mapping2 = FaceMapping<2>( CellType::NCube, 0 );

    CHECK( spatial::distance<2>( mapping2( { -1.0 } ), { -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2( {  1.0 } ), { -1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2.normal( ), { -1.0, 0.0 } ) < 1e-8 );

    // Quad - right
    mapping2 = FaceMapping<2>( CellType::NCube, 1 );

    CHECK( spatial::distance<2>( mapping2( { -1.0 } ), { 1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2( {  1.0 } ), { 1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2.normal( ), { 1.0, 0.0 } ) < 1e-8 );

    // Quad - bottom
    mapping2 = FaceMapping<2>( CellType::NCube, 2 );

    CHECK( spatial::distance<2>( mapping2( { -1.0 } ), { -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2( {  1.0 } ), {  1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2.normal( ), { 0.0, -1.0 } ) < 1e-8 );

    // Quad - top
    mapping2 = FaceMapping<2>( CellType::NCube, 3 );

    CHECK( spatial::distance<2>( mapping2( { -1.0 } ), { -1.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2( {  1.0 } ), {  1.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2.normal( ), { 0.0, 1.0 } ) < 1e-8 );

    // Cube - left
    auto mapping3 = FaceMapping<3>( CellType::NCube, 0 );

    CHECK( spatial::distance<3>( mapping3( { -1.0, -1.0 } ), { -1.0, -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { -1.0,  1.0 } ), { -1.0, -1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0, -1.0 } ), { -1.0,  1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0,  1.0 } ), { -1.0,  1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3.normal( ), { -1.0, 0.0, 0.0 } ) < 1e-8 );

    // Cube - right
    mapping3 = FaceMapping<3>( CellType::NCube, 1 );

    CHECK( spatial::distance<3>( mapping3( { -1.0, -1.0 } ), {  1.0, -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { -1.0,  1.0 } ), {  1.0, -1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0, -1.0 } ), {  1.0,  1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0,  1.0 } ), {  1.0,  1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3.normal( ), { 1.0, 0.0, 0.0 } ) < 1e-8 );

    // Cube - front
    mapping3 = FaceMapping<3>( CellType::NCube, 2 );

    CHECK( spatial::distance<3>( mapping3( { -1.0, -1.0 } ), { -1.0, -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { -1.0,  1.0 } ), { -1.0, -1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0, -1.0 } ), {  1.0, -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0,  1.0 } ), {  1.0, -1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3.normal( ), { 0.0, -1.0, 0.0 } ) < 1e-8 );

    // Cube - back
    mapping3 = FaceMapping<3>( CellType::NCube, 3 );

    CHECK( spatial::distance<3>( mapping3( { -1.0, -1.0 } ), { -1.0,  1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { -1.0,  1.0 } ), { -1.0,  1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0, -1.0 } ), {  1.0,  1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0,  1.0 } ), {  1.0,  1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3.normal( ), { 0.0, 1.0, 0.0 } ) < 1e-8 );

    // Cube - bottom
    mapping3 = FaceMapping<3>( CellType::NCube, 4 );

    CHECK( spatial::distance<3>( mapping3( { -1.0, -1.0 } ), { -1.0, -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { -1.0,  1.0 } ), { -1.0,  1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0, -1.0 } ), {  1.0, -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0,  1.0 } ), {  1.0,  1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3.normal( ), { 0.0, 0.0, -1.0 } ) < 1e-8 );

    // Cube - top
    mapping3 = FaceMapping<3>( CellType::NCube, 5 );

    CHECK( spatial::distance<3>( mapping3( { -1.0, -1.0 } ), { -1.0, -1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { -1.0,  1.0 } ), { -1.0,  1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0, -1.0 } ), {  1.0, -1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( {  1.0,  1.0 } ), {  1.0,  1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3.normal( ), { 0.0, 0.0, 1.0 } ) < 1e-8 );

    CHECK( mapping3.type == map::Type::NCube );

    // 4-cube - all faces 
    for( size_t axis = 0; axis < 4; ++axis )
    {
        for( size_t side = 0; side < 2; ++side )
        {   
            auto limits = array::makeSizes<3>( 3 );
            auto rst = spatial::makeRstGenerator( limits );
            auto mapping4 = FaceMapping<4>( CellType::NCube, 2 * axis + side );

            nd::execute( limits, [&]( auto ijk )
            { 
                auto expected = array::insert( rst( ijk ), axis, side ? 1.0 : -1.0 );

                CHECK( spatial::distance( mapping4( rst( ijk ) ), expected ) < 1e-8 );
            } );
            
            auto normal = std::array<double, 4> { };
            
            normal[axis] = side ? 1.0 : -1.0;

            CHECK( spatial::distance( mapping4.normal( ), normal ) < 1e-8 );
        }
    }

    // Simplex 1D - left
    mapping1 = FaceMapping<1>( CellType::Simplex, 0 );

    CHECK( spatial::distance<1>( mapping1( { } ), { 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<1>( mapping1.normal( ), { -1.0 } ) < 1e-8 );

    // Simplex 1D - right
    mapping1 = FaceMapping<1>( CellType::Simplex, 1 );

    CHECK( spatial::distance<1>( mapping1( { } ), { 1.0 } ) < 1e-8 );
    CHECK( spatial::distance<1>( mapping1.normal( ), { 1.0 } ) < 1e-8 );
    
    // Triangle - left
    mapping2 = FaceMapping<2>( CellType::Simplex, 0 );

    CHECK( spatial::distance<2>( mapping2( { 0.0 } ), { 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2( { 1.0 } ), { 0.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2.normal( ), { -1.0, 0.0 } ) < 1e-8 );
    
    // Triangle - bottom
    mapping2 = FaceMapping<2>( CellType::Simplex, 1 );

    CHECK( spatial::distance<2>( mapping2( { 0.0 } ), { 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2( { 1.0 } ), { 1.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2.normal( ), { 0.0, -1.0 } ) < 1e-8 );
    
    // Triangle - diagonal
    mapping2 = FaceMapping<2>( CellType::Simplex, 2 );
    
    CHECK( spatial::distance<2>( mapping2( { 0.0 } ), { 1.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2( { 1.0 } ), { 0.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( mapping2.normal( ), spatial::normalize<2>( { 1.0, 1.0 } ) ) < 1e-8 );
    
    // Tetrahedron - left
    mapping3 = FaceMapping<3>( CellType::Simplex, 0 );
    
    CHECK( spatial::distance<3>( mapping3( { 0.0, 0.0 } ), { 0.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 1.0, 0.0 } ), { 0.0, 1.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 0.0, 1.0 } ), { 0.0, 0.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 0.5, 0.5 } ), { 0.0, 0.5, 0.5 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3.normal( ), { -1.0, 0.0, 0.0 } ) < 1e-8 );

    // Tetrahedron - front
    mapping3 = FaceMapping<3>( CellType::Simplex, 1 );
    
    CHECK( spatial::distance<3>( mapping3( { 0.0, 0.0 } ), { 0.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 1.0, 0.0 } ), { 1.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 0.0, 1.0 } ), { 0.0, 0.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 0.5, 0.5 } ), { 0.5, 0.0, 0.5 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3.normal( ), { 0.0, -1.0, 0.0 } ) < 1e-8 );

    // Tetrahedron - bottom
    mapping3 = FaceMapping<3>( CellType::Simplex, 2 );

    CHECK( spatial::distance<3>( mapping3( { 0.0, 0.0 } ), { 0.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 1.0, 0.0 } ), { 1.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 0.0, 1.0 } ), { 0.0, 1.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 0.5, 0.5 } ), { 0.5, 0.5, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3.normal( ), { 0.0, 0.0, -1.0 } ) < 1e-8 );

    // Tetrahedron - diagonal
    mapping3 = FaceMapping<3>( CellType::Simplex, 3 );
    
    CHECK( spatial::distance<3>( mapping3( { 0.0, 0.0 } ), { 1.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 1.0, 0.0 } ), { 0.0, 1.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( mapping3( { 0.0, 1.0 } ), { 0.0, 0.0, 1.0 } ) < 1e-8 );

    CHECK( spatial::distance<3>( mapping3( { 1.0 / 3.0, 1.0 / 3.0 } ), 
        { 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0 } ) < 1e-8 );

    CHECK( spatial::distance<3>( mapping3.normal( ), 
        spatial::normalize<3>( { 1.0, 1.0, 1.0 } ) ) < 1e-8 );

    // 4-simplex - faces 0 - 3
    for( size_t axis = 0; axis < 4; ++axis )
    {
        auto mapping4 = FaceMapping<4>( CellType::Simplex, axis );

        CHECK( spatial::distance<4>( mapping4( { } ), { } ) < 1e-8 );

        for( size_t axis2 = 0; axis2 < 3; ++axis2 )
        {
            auto rs = array::setEntry<double, 3>( { }, axis2, 1.0 );
            auto rst = array::insert( rs, axis, 0.0 );

            CHECK( spatial::distance<4>( mapping4( rs ), rst ) < 1e-8 );
        }
        
        auto normal = array::setEntry<double, 4>( { }, axis, -1.0 );

        CHECK( spatial::distance<4>( mapping4.normal( ), normal ) < 1e-8 );
    }
        
    // 4-simplex - diagonal
    auto mapping4 = FaceMapping<4>( CellType::Simplex, 4 );
    
    CHECK( spatial::distance<4>( mapping4( { 0.0, 0.0, 0.0 } ), { 1.0, 0.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<4>( mapping4( { 1.0, 0.0, 0.0 } ), { 0.0, 1.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<4>( mapping4( { 0.0, 1.0, 0.0 } ), { 0.0, 0.0, 1.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<4>( mapping4( { 0.0, 0.0, 1.0 } ), { 0.0, 0.0, 0.0, 1.0 } ) < 1e-8 );

    CHECK( spatial::distance<4>( mapping4( { 1.0 / 4.0, 1.0 / 4.0, 1.0 / 4.0 } ), 
        { 1.0 / 4.0, 1.0 / 4.0, 1.0 / 4.0, 1.0 / 4.0 } ) < 1e-8 );

    CHECK( spatial::distance<4>( mapping4.normal( ), 
        spatial::normalize<4>( { 1.0, 1.0, 1.0, 1.0 } ) ) < 1e-8 );
    
    CHECK( mapping4.type == map::Type::Simplex );
}

} // namespace mlhp
