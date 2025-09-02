// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/spatial.hpp"
#include "mlhp/core/postprocessing.hpp"

namespace mlhp
{

TEST_CASE( "spatial_test" )
{
    double tolerance = 1e-12;

    double computed1 = spatial::dot<3>( { 3.0, -0.5, 1.2 }, { -2.1, 5.2, 0.9 } );
    double expected1 = -3.0 * 2.1 - 0.5 * 5.2 + 1.2 * 0.9;

    CHECK( computed1 == Approx( expected1 ).epsilon( tolerance ) );

    auto [xyz2, r2] = spatial::projectOntoLine<3>( 
        { 1.0, 0.0, 2.0 }, { 2.0, 3.0, 1.0 }, { 1.5, 1.5, 1.5 } );

    auto [xyz3, r3] = spatial::projectOntoLine<3>(
        { 1.0, 0.0, 2.0 }, { 2.0, 3.0, 1.0 }, { -1.7, 1.4, 1.3 } );

    std::array<double, 3> expectedXyz2 { 1.5, 1.5, 1.5 };
    std::array<double, 3> expectedXyz3 { 1.2, 0.6, 1.8 };

    CHECK( r2 == Approx( 0.5 ).epsilon( tolerance ) );
    CHECK( r3 == Approx( 0.2 ).epsilon( tolerance ) );

    for( size_t axis = 0; axis < 3; ++axis )
    {
        CHECK( xyz2[axis] == Approx( expectedXyz2[axis] ).epsilon( tolerance ) );
        CHECK( xyz3[axis] == Approx( expectedXyz3[axis] ).epsilon( tolerance ) );
    }

    auto axes = std::array { std::array { 0.43, -0.13, 12.1 },
                             std::array { 1.0, 0.0, 0.0 },
                             std::array { 0.0, 1.0, 0.0 },
                             std::array { 0.0, 0.0, 1.0 },
                             std::array { 1.0, 1.0, 1.0 } };

    for( const auto& axis : axes )
    {
        auto [n1, n2] = spatial::findPlaneVectors( axis );
        
        CHECK( spatial::normSquared( n1 ) == Approx( 1.0 ).epsilon( tolerance ) );
        CHECK( spatial::normSquared( n2 ) == Approx( 1.0 ).epsilon( tolerance ) );
        CHECK( spatial::dot( n1, n2 ) == Approx( 0.0 ).margin( tolerance ) );
        CHECK( spatial::dot( n1, axis ) == Approx( 0.0 ).margin( tolerance ) );
        CHECK( spatial::dot( n2, axis ) == Approx( 0.0 ).margin( tolerance ) );
    }

    // Check closest point on segment
    auto [xyz4, r4] = spatial::closestPointOnSegment<2>( { 1.0, 3.0 }, { 2.0, 1.0 }, { 2.0, 4.0 } );
    auto [xyz5, r5] = spatial::closestPointOnSegment<2>( { 1.0, 3.0 }, { 2.0, 1.0 }, { 1.0, 0.0 } );
    auto [xyz6, r6] = spatial::closestPointOnSegment<2>( { 1.0, 3.0 }, { 2.0, 1.0 }, { 2.5, 2.5 } );

    CHECK( xyz4 == std::array { 1.0, 3.0 } );
    CHECK( xyz5 == std::array { 2.0, 1.0 } );

    CHECK( xyz6[0] == Approx( 1.5 ) );
    CHECK( xyz6[1] == Approx( 2.0 ) );

    CHECK( r4 == 0.0 );
    CHECK( r5 == 1.0 );
    CHECK( r6 == Approx( 0.5 ) );

    auto v0 = std::array { 3.0, -1.0, 2.0 };
    auto v1 = std::array { -4.0, 1.0, 5.0 };

    CHECK( spatial::distance<3>( spatial::cross( v0, v1 ), { -7.0, -23.0, -1.0 } ) < 1e-10 );
    CHECK( spatial::projectionFactor( v0, v1 ) == Approx( -0.21428571428571427 ).margin( 1e-12 ) );

    auto projection = std::array { -3.357142857142857, 0.785714285714286, 5.428571428571429 };

    CHECK( spatial::distance( spatial::orthogonalize( v0, v1 ), projection ) < 1e-10 );
    CHECK( spatial::distance( spatial::orthogonalize<3>( { }, v1 ), v1 ) == 0.0 );

    CHECK( spatial::distance<2>( { 5.0, 2.0 }, { 2.0, 6.0 } ) == Approx( 5.0 ).epsilon( 1e-10 ) );

    auto cross = spatial::cross( std::array { 3.0, -4.0 }, std::array { 4.0, 3.0 } );

    CHECK( cross == Approx( 25.0 ).epsilon( 1e-10 ) );
}

TEST_CASE( "mapPlane_test" )
{
    SECTION( "2D" )
    {
        auto J = std::array { 3.2, 0.0,
                              0.0, 0.4 };

        auto l = spatial::normalize<2>( { 1.0, 1.0 } );
        auto g = spatial::normalize<2>( { 1.0 / 3.2, 1.0 / 0.4 } );

        CHECK( spatial::distance<2>( spatial::mapPlaneNormal<2>( J, l ), g ) < 1e-10 );
    }

    SECTION( "3D" )
    {
        auto J = std::array { 3.0, 0.0, 0.0,
                              0.0, 2.0, 0.0,
                              0.0, 0.0, 4.0 };

        for( const auto& normal : { std::array { 1.0, 0.0, 0.0 },
                                    std::array { 0.0, 1.0, 0.0 },
                                    std::array { 0.0, 0.0, 1.0 } } )
        {
            CHECK( spatial::distance<3>( spatial::mapPlaneNormal<3>( J, normal ), normal ) < 1e-10 );
        }

        auto l = spatial::normalize<3>( { 1.0, 1.0, 1.0 } );
        auto g = spatial::normalize<3>( { 1.0 / 3.0, 1.0 / 2.0, 1.0 / 4.0 } );

        CHECK( spatial::distance<3>( spatial::mapPlaneNormal<3>( J, l ), g ) < 1e-10 );
    }
}

TEST_CASE( "VectorFunction_test" )
{
    auto testfunction1 = []( const spatial::VectorFunction<3>& dynamic )
    {
        auto out = std::vector<double>( 2, 0.0 );

        dynamic( { 3.0, 2.0, 5.0 }, out );

        CHECK( out == std::vector { 2.0, 3.0 } );
    };

    auto testfunction2 = []( const spatial::VectorFunction<3, 2>& stat )
    {
        auto out1 = stat( { 3.0, 2.0, 5.0 } );

        CHECK( out1 == std::array { 2.0, 3.0 } );

        auto out2 = std::array<double, 2> { };

        stat( { 3.0, 2.0, 5.0 }, out2 );

        CHECK( out2 == std::array { 2.0, 3.0 } );
    };
        
    // dynamic
    {
        auto v1 = spatial::VectorFunction<3> { 2, []( std::array<double, 3> xyz, std::span<double> out ) noexcept
        { 
            out[0] = xyz[1];
            out[1] = xyz[0];
        } };

        testfunction1( v1 );
        testfunction2( v1 );
    }

    // static
    {
        auto v1 = spatial::VectorFunction<3, 2> { []( std::array<double, 3> xyz, std::span<double, 2> out ) noexcept
        {
            out[0] = xyz[1];
            out[1] = xyz[0];
        } };

        auto v2 = spatial::VectorFunction<3, 2> { []( std::array<double, 3> xyz ) noexcept
        {
            return std::array { xyz[1], xyz[0] };
        } };

        testfunction1( v1 );
        testfunction2( v1 );
        testfunction1( v2 );
        testfunction2( v2 );
    }
}

TEST_CASE( "transformations_test" )
{
    // Translate
    auto translate1 = spatial::translate<3>( { 0.2, 0.4, -0.3 } );

    auto translated = translate1( { 1.1, -0.8, 1.7 } );

    CHECK( translated[0] == Approx( 1.3 ).epsilon( 1e-12 ) );
    CHECK( translated[1] == Approx( -0.4 ).epsilon( 1e-12 ) );
    CHECK( translated[2] == Approx( 1.4 ).epsilon( 1e-12 ) );

    // Scale
    auto scale1 = spatial::scale<3>( { 0.4, 0.6, 0.8 } );

    auto scaled = scale1( { 2.1, 2.2, 2.3 } );

    CHECK( scaled[0] == Approx( 0.4 * 2.1 ).epsilon( 1e-12 ) );
    CHECK( scaled[1] == Approx( 0.6 * 2.2 ).epsilon( 1e-12 ) );
    CHECK( scaled[2] == Approx( 0.8 * 2.3 ).epsilon( 1e-12 ) );

    // Rotate
    auto rotate1 = spatial::rotate( { 1.0, 1.0, 1.0 }, 2.0 * std::numbers::pi / 3.0 );

    auto rotated = rotate1( { 2.0, 0.0, 0.0 } );

    CHECK( rotated[0] == Approx( 0.0 ).margin( 1e-12 ) );
    CHECK( rotated[1] == Approx( 2.0 ).epsilon( 1e-12 ) );
    CHECK( rotated[2] == Approx( 0.0 ).margin( 1e-12 ) );

    // Rotate.scale
    rotate1.scale( { 2.0, 3.0, 4.0 } );

    auto rotatedScaled = rotate1( rotated );

    CHECK( rotatedScaled[0] == Approx( 0.0 ).margin( 1e-12 ) );
    CHECK( rotatedScaled[1] == Approx( 0.0 ).margin( 1e-12 ) );
    CHECK( rotatedScaled[2] == Approx( 8.0 ).epsilon( 1e-12 ) );

    // concatenate( rotate, scale, translate )
    auto rotate2 = spatial::rotate( { 1.0, 1.0, 1.0 }, -2.0 * std::numbers::pi / 3.0 );
    auto scale2 = spatial::scale<3>( { 2.0, 3.0, 4.0 } );
    auto translate2 = spatial::translate<3>( { 3.2, -4.1, 0.9 } );

    auto concatenate = spatial::concatenate( rotate2, scale2, translate2 );

    auto concatenated1 = concatenate( { 0.0, 1.0, 0.0 } );

    CHECK( concatenated1[0] == Approx( 5.2 ).epsilon( 1e-12 ) );
    CHECK( concatenated1[1] == Approx( -4.1 ).epsilon( 1e-12 ) );
    CHECK( concatenated1[2] == Approx( 0.9 ).epsilon( 1e-12 ) );

    // concatenate( rotate, scale, translate )^(-1)
    auto inverted = concatenate.invert( )( { 5.2, -4.1, 0.9 } );

    CHECK( inverted[0] == Approx( 0.0 ).margin( 1e-12 ) );
    CHECK( inverted[1] == Approx( 1.0 ).epsilon( 1e-12 ) );
    CHECK( inverted[2] == Approx( 0.0 ).margin( 1e-12 ) );

    // rotate.scale.translate
    rotate2.scale( { 2.0, 3.0, 4.0 } )
           .translate( { 3.2, -4.1, 0.9 } );

    auto concatenated2 = rotate2( { 0.0, 1.0, 0.0 } );

    CHECK( concatenated2[0] == Approx( 5.2 ).margin( 1e-12 ) );
    CHECK( concatenated2[1] == Approx( -4.1 ).epsilon( 1e-12 ) );
    CHECK( concatenated2[2] == Approx( 0.9 ).margin( 1e-12 ) );
}

TEST_CASE( "clipPolygon_test1" )
{
    auto points = std::array
    {
        std::array { 1.2, 0.5, 1.2 },
        std::array { 0.7, 2.1, 0.9 },
        std::array { 2.0, 0.5, 1.7 }
    };
    
    auto expected = std::array
    { 
        std::array { 1.52,   0.5, 1.4  },
        std::array { 1.2,    0.5, 1.2  },
        std::array { 0.95,   1.3, 1.05 },
        std::array { 1.35,   1.3, 1.3  },
        std::array { 1.5125, 1.1, 1.4  }
    };

    auto bounds = std::array { std::array { 0.9, 0.1, 0.4 }, 
                               std::array { 1.7, 1.3, 1.4 } };

    auto target = CoordinateList<3>( points.size( ) * 3 );
    auto clipped = spatial::clipPolygon<3>( points, target, bounds );

    REQUIRE( clipped.size( ) == expected.size( ) );

    for( size_t ivertex = 0; ivertex < expected.size( ); ++ivertex )
    {
        CHECK( spatial::distance( clipped[ivertex], expected[ivertex] ) < 1e-10 );
    }

    auto clippedBounds = spatial::triangleClippedBoundingBox( 
        points[0], points[1], points[2], bounds );

    CHECK( spatial::distance<3>( clippedBounds[0], { 0.95, 0.5, 1.05 } ) < 1e-8 );
    CHECK( spatial::distance<3>( clippedBounds[1], { 1.52, 1.3, 1.40 } ) < 1e-8 );
}

TEST_CASE( "clipPolygon_test2" )
{
    auto points = std::vector
    {
        std::array { 0.9, 0.5, 1.4 },
        std::array { 0.9, 0.5, 1.2 },
        std::array { 0.9, 1.3, 1.1 },
        std::array { 0.9, 1.5, 1.3 },
        std::array { 0.9, 1.6, 1.7 }
    };

    auto expected = std::array
    {
        std::array { 0.9, 1.3, 1.4 },
        std::array { 0.9, 0.5, 1.4 },
        std::array { 0.9, 0.5, 1.2 },
        std::array { 0.9, 1.3, 1.1 },
    };
    
    auto bounds = std::array { std::array { 0.9, 0.1, 0.4 }, 
                               std::array { 1.7, 1.3, 1.4 } };

    auto target = CoordinateList<3>( points.size( ) * 3 );
    auto clipped = spatial::clipPolygon<3>( points, target, bounds );
    
    REQUIRE( clipped.size( ) == expected.size( ) );

    for( size_t ivertex = 0; ivertex < expected.size( ); ++ivertex )
    {
        CHECK( spatial::distance( clipped[ivertex], expected[ivertex] ) < 1e-10 );
    }
}

TEST_CASE( "clipPolygon_test3" )
{
    auto points = std::array
    {
        std::array { 0.6, 0.6, 1.3 },
        std::array { 2.1, 0.6, 1.3 },
        std::array { 1.6, 0.1, 0.8 },
        std::array { 0.7, 0.1, 0.8 },
        std::array { 0.9, 0.3, 1.0 },
        std::array { 0.9, 0.4, 1.1 }
    };

    auto expected = std::array
    {
        std::array { 0.9, 0.4, 1.1 },
        std::array { 0.9, 0.6, 1.3 },
        std::array { 1.7, 0.6, 1.3 },
        std::array { 1.7, 0.2, 0.9 },
        std::array { 1.6, 0.1, 0.8 },
        std::array { 0.9, 0.1, 0.8 },
        std::array { 0.9, 0.3, 1.0 }
    };
    
    auto bounds = std::array { std::array { 0.9, 0.1, 0.4 }, 
                               std::array { 1.7, 1.3, 1.4 } };

    auto target = std::array<std::array<double, 3>, 18> { };
    auto clipped = spatial::clipPolygon<3>( points, target, bounds );
    
    REQUIRE( clipped.size( ) == expected.size( ) );

    for( size_t ivertex = 0; ivertex < expected.size( ); ++ivertex )
    {
        CHECK( spatial::distance( clipped[ivertex], expected[ivertex] ) < 1e-10 );
    }
}

TEST_CASE( "clipPolygon_test4" )
{
    auto points = std::array
    {
        std::array { -2.94, 0.7, 3.56 },
        std::array { 0.27, -3.9, -0.76 },
        std::array { 5.54, 0.7, -1.75 },
        std::array { 2.33, 5.3, 2.56 }
    };

    auto expected = std::array
    {
        std::array { 1.62005963787, 0.1, 0.4  },
        std::array { 1.7, 0.199894261275, 0.4 },
        std::array { 1.7, 1.3, 0.951127367636 },
        std::array { 0.983332365616, 1.3, 1.4 },
        std::array { 0.9, 1.19585851956, 1.4  },
        std::array { 0.9, 0.1, 0.850775644912 }
    };

    auto bounds = std::array { std::array { 0.9, 0.1, 0.4 }, 
                               std::array { 1.7, 1.3, 1.4 } };

    auto target = std::array<std::array<double, 3>, 12> { };
    auto clipped = spatial::clipPolygon<3>( points, target, bounds );
    
    REQUIRE( clipped.size( ) == expected.size( ) );

    for( size_t ivertex = 0; ivertex < expected.size( ); ++ivertex )
    {
        CHECK( spatial::distance( clipped[ivertex], expected[ivertex] ) < 1e-10 );
    }
}

TEST_CASE( "clipPolygon_test5" )
{
    auto points = std::array
    {
        std::array { -2.94, 0.7, 3.56 },
        std::array { 0.27, -3.9, -0.76 },
        std::array { 5.54, 0.7, -1.75 },
        std::array { 2.33, 5.3, 2.56 }
    };    
    
    std::array<std::array<double, 3>, 8> targetX0, targetX1, 
        targetY0, targetY1, targetZ0, targetZ1;

    // Cut with plane normal to x-axis at x = -2.7
    auto expectedX0 = std::array
    {
        std::array { -2.7, 0.909487666034, 3.51445920304 },
        std::array { -2.94, 0.7, 3.56 },
        std::array { -2.7, 0.356074766355, 3.23700934579 }
    };
    
    auto clippedX0 = spatial::clipPolygon<3>( points, targetX0, 0, -2.7, false );
    auto clippedX1 = spatial::clipPolygon<3>( points, targetX1, 0, -2.7, true );
    
    auto expectedX1 = std::array
    {
        std::array { -2.7, 0.909487666034, 3.51445920304 },
        std::array { -2.7, 0.356074766355, 3.23700934579 },
        std::array { 0.27, -3.9, -0.76 },
        std::array { 5.54, 0.7, -1.75 },
        std::array { 2.33, 5.3, 2.56 }
    };

    // Cut with plane normal to y-axis at y = 2.0
    auto expectedY0 = std::array
    {
        std::array { -1.45065217391, 2.0, 3.27739130435 },
        std::array { -2.94, 0.7, 3.56 },
        std::array { 0.27, -3.9, -0.76 },
        std::array { 5.54, 0.7, -1.75 },
        std::array { 4.63282608696, 2.0, -0.531956521739 }
    };

    auto expectedY1 = std::array
    {
        std::array { -1.45065217391, 2.0, 3.27739130435 },
        std::array { 4.63282608696, 2.0, -0.531956521739 },
        std::array { 2.33, 5.3, 2.56 }
    };

    auto clippedY0 = spatial::clipPolygon<3>( points, targetY0, 1, 2.0, false );
    auto clippedY1 = spatial::clipPolygon<3>( points, targetY1, 1, 2.0, true );

    // Cut with plane normal to Z-axis at y = 1.0
    auto expectedZ0 = std::array
    {
        std::array { -1.03777777778, -2.02592592593, 1.0 },
        std::array { 0.27, -3.9, -0.76 },
        std::array { 5.54, 0.7, -1.75 },
        std::array { 3.49185614849, 3.63503480278, 1.0 }
    };

    auto expectedZ1 = std::array
    {
        std::array { -2.94, 0.7, 3.56 },
        std::array { -1.03777777778, -2.02592592593, 1.0 },
        std::array { 3.49185614849, 3.63503480278, 1.0 },
        std::array { 2.33, 5.3, 2.56 }
    };

    auto clippedZ0 = spatial::clipPolygon<3>( points, targetZ0, 2, 1.0, false );
    auto clippedZ1 = spatial::clipPolygon<3>( points, targetZ1, 2, 1.0, true );

    // Check results
    REQUIRE( clippedX0.size( ) == expectedX0.size( ) );
    REQUIRE( clippedX1.size( ) == expectedX1.size( ) );
    REQUIRE( clippedY0.size( ) == expectedY0.size( ) );
    REQUIRE( clippedY1.size( ) == expectedY1.size( ) );
    REQUIRE( clippedZ0.size( ) == expectedZ0.size( ) );
    REQUIRE( clippedZ1.size( ) == expectedZ1.size( ) );

    for( size_t ivertex = 0; ivertex < expectedX0.size( ); ++ivertex )
    {
        CHECK( spatial::distance( clippedX0[ivertex], expectedX0[ivertex] ) < 1e-10 );
    }
    
    for( size_t ivertex = 0; ivertex < expectedX1.size( ); ++ivertex )
    {
        CHECK( spatial::distance( clippedX1[ivertex], expectedX1[ivertex] ) < 1e-10 );
    }

    for( size_t ivertex = 0; ivertex < expectedY0.size( ); ++ivertex )
    {
        CHECK( spatial::distance( clippedY0[ivertex], expectedY0[ivertex] ) < 1e-10 );
    }
    
    for( size_t ivertex = 0; ivertex < expectedY1.size( ); ++ivertex )
    {
        CHECK( spatial::distance( clippedY1[ivertex], expectedY1[ivertex] ) < 1e-10 );
    }

    for( size_t ivertex = 0; ivertex < expectedZ0.size( ); ++ivertex )
    {
        CHECK( spatial::distance( clippedZ0[ivertex], expectedZ0[ivertex] ) < 1e-10 );
    }
    
    for( size_t ivertex = 0; ivertex < expectedZ1.size( ); ++ivertex )
    {
        CHECK( spatial::distance( clippedZ1[ivertex], expectedZ1[ivertex] ) < 1e-10 );
    }
}

TEST_CASE( "triangleClippedBoundingBox_test" )
{
    auto v0 = std::array { 1.0, 0.0, 0.0 };
    auto v1 = std::array { 0.0, 1.0, 0.0 };
    auto v2 = std::array { 0.0, 0.0, 1.0 };
    
    auto v3 = std::array { 1.0, 0.0, 1.0 };
    auto v4 = std::array { 0.0, 1.0, 1.0 };
    
    auto expected = std::array
    {
        std::array { std::array { 0.0, 0.0, 0.0 }, std::array { 0.5, 1.0, 1.0 } },
        std::array { std::array { 0.5, 0.0, 0.0 }, std::array { 1.0, 0.5, 0.5 } },
        std::array { std::array { 0.0, 0.0, 0.0 }, std::array { 1.0, 0.9, 1.0 } },
        std::array { std::array { 0.0, 0.9, 0.0 }, std::array { 0.1, 1.0, 0.1 } },
        std::array { std::array { 0.0, 0.0, 0.0 }, std::array { 1.0, 1.0, 0.2 } },
        std::array { std::array { 0.0, 0.0, 0.2 }, std::array { 0.8, 0.8, 1.0 } },
        std::array { std::array { 0.0, 0.0, 1.0 }, std::array { 1.0, 1.0, 1.0 } },
        std::array { std::array { 0.0, 0.0, 1.0 }, std::array { 1.0, 1.0, 1.0 } },
        std::array { std::array { 0.0, 0.0, 1.0 }, std::array { 0.0, 1.0, 1.0 } },
        std::array { std::array { 0.0, 0.0, 1.0 }, std::array { 1.0, 1.0, 1.0 } }
    };
    
    auto computed = std::array
    {
        spatial::triangleClippedBoundingBox( v0, v1, v2, 0, 0.5, false ),
        spatial::triangleClippedBoundingBox( v0, v1, v2, 0, 0.5, true  ),
        spatial::triangleClippedBoundingBox( v0, v1, v2, 1, 0.9, false ),
        spatial::triangleClippedBoundingBox( v0, v1, v2, 1, 0.9, true  ),
        spatial::triangleClippedBoundingBox( v0, v1, v2, 2, 0.2, false ),
        spatial::triangleClippedBoundingBox( v0, v1, v2, 2, 0.2, true  ),
        spatial::triangleClippedBoundingBox( v2, v3, v4, 2, 1.0, false ),
        spatial::triangleClippedBoundingBox( v2, v3, v4, 2, 1.0, true  ),
        spatial::triangleClippedBoundingBox( v2, v3, v4, 0, 0.0, false ),
        spatial::triangleClippedBoundingBox( v2, v3, v4, 0, 0.0, true  )
    };

    for( size_t i = 0; i < expected.size( ); ++i )
    {
        CHECK( spatial::distance( computed[i][0], expected[i][0] ) < 1e-10 );
        CHECK( spatial::distance( computed[i][1], expected[i][1] ) < 1e-10 );
    }
}

TEST_CASE( "clipTriangle2D_test" )
{
    auto vertex0 = std::array { 2.0, 0.0 };
    auto vertex1 = std::array { 3.0, 4.0 };
    auto vertex2 = std::array { 4.0, 0.0 };

    auto bounds = std::array { std::array { 2.0, 1.0 }, std::array { 4.0, 2.0 } };
    auto target = std::array<std::array<double, 2>, 9> { };

    auto result = spatial::clipTriangle<2>( vertex0, vertex1, vertex2, bounds, target );

    REQUIRE( result.size( ) == 4 );

    CHECK( spatial::distance( result[0], std::array { 2.25, 1.0 } ) < 1e-10 );
    CHECK( spatial::distance( result[1], std::array { 2.50, 2.0 } ) < 1e-10 );
    CHECK( spatial::distance( result[2], std::array { 3.50, 2.0 } ) < 1e-10 );
    CHECK( spatial::distance( result[3], std::array { 3.75, 1.0 } ) < 1e-10 );
}

TEST_CASE( "clipLineSegment_test" )
{
    auto v0 = std::array { -2.0, 0.0 };
    auto v1 = std::array { 7.0, 12.0 };

    auto bounds = std::array 
    { 
        std::array { 1.0, 2.0 }, 
        std::array { 6.0, 8.0 } 
    };

    auto test1 = std::array { v0, v1 };
    auto test2 = std::array { v1, v0 };

    auto expected0 = std::array { 1.0, 4.0 };
    auto expected1 = std::array { 4.0, 8.0 };

    CHECK( spatial::clipLineSegment( test1[0], test1[1], bounds ) );
    CHECK( spatial::clipLineSegment( test2[0], test2[1], bounds ) );

    CHECK( spatial::distance( test1[0], expected0 ) < 1e-10 );
    CHECK( spatial::distance( test1[1], expected1 ) < 1e-10 );

    CHECK( spatial::distance( test2[0], expected1 ) < 1e-10 );
    CHECK( spatial::distance( test2[1], expected0 ) < 1e-10 );

    v0 = std::array { 8.0, 2.0 };
    v1 = std::array { 0.0, 2.0 };

    CHECK( spatial::clipLineSegment( v0, v1, bounds ) );

    CHECK( spatial::distance<2>( v0, { 6.0, 2.0 } ) < 1e-10 );
    CHECK( spatial::distance<2>( v1, { 1.0, 2.0 } ) < 1e-10 );

    v0 = std::array { -8.0, 0.0 };
    v1 = std::array { 0.0, -8.0 };

    auto clippedBounds = spatial::lineSegmentClippedBoundingBox( v0, v1, bounds );

    CHECK( clippedBounds == spatial::makeEmptyBoundingBox<2>( ) );
    CHECK( !spatial::clipLineSegment( v0, v1, bounds ) );

    CHECK( v0 == std::array { -8.0, 0.0 } );
    CHECK( v1 == std::array { 0.0, -8.0 } );

    v0 = std::array { 7.0, 0.0 };
    v1 = std::array { 0.0, 7.0 };
    
    clippedBounds = spatial::lineSegmentClippedBoundingBox( v0, v1, bounds );

    CHECK( spatial::clipLineSegment( v0, v1, bounds ) );

    CHECK( spatial::distance<2>( v0, { 5.0, 2.0 } ) < 1e-10 );
    CHECK( spatial::distance<2>( v1, { 1.0, 6.0 } ) < 1e-10 );

    CHECK( spatial::distance<2>( clippedBounds[0], { 1.0, 2.0 } ) < 1e-10 );
    CHECK( spatial::distance<2>( clippedBounds[1], { 5.0, 6.0 } ) < 1e-10 );

    v0 = std::array { 4.0, 3.0 };
    v1 = std::array { 0.0, 7.0 };

    CHECK( spatial::clipLineSegment( v0, v1, bounds ) );

    CHECK( spatial::distance<2>( v0, { 4.0, 3.0 } ) < 1e-10 );
    CHECK( spatial::distance<2>( v1, { 1.0, 6.0 } ) < 1e-10 );

    v0 = std::array { 7.0, 0.0 };
    v1 = std::array { 3.0, 4.0 };

    CHECK( spatial::clipLineSegment( v0, v1, bounds ) );

    CHECK( spatial::distance<2>( v0, { 5.0, 2.0 } ) < 1e-10 );
    CHECK( spatial::distance<2>( v1, { 3.0, 4.0 } ) < 1e-10 );
}

TEST_CASE( "clipLineSegment_test2" )
{
    auto polygon = std::array<std::array<double, 2>, 6>
    {
        std::array { 0.99999999999999645, 1.0 },
        std::array { 1.0, 33.0 }
    };

    auto bounds = std::array 
    { 
        std::array { std::numeric_limits<double>::lowest( ), -1.0 },
        std::array { std::numeric_limits<double>::max( ), 1.0 }
    };

    auto result = spatial::clipSimplex<2, 1>( polygon, bounds );

    // Collapsed segment might also be okay, but it must be zero or two vertices
    CHECK( result.size( ) == 0 );
}

TEST_CASE( "segmentRayIntersection_test" )
{
    auto v1 = std::array { 3.0, -2.0 };
    auto v2 = std::array { 11.0, 4.0 };

    CHECK( !spatial::segmentRayIntersection( v1, v2, { 4.0, -3.0 }, { -1.5, -2.0 } ) );
    CHECK( !spatial::segmentRayIntersection( v1, v2, { 4.0, -3.0 }, { 1.5, -2.0 } ) );
    CHECK( !spatial::segmentRayIntersection( v1, v2, { 4.0, -3.0 }, { 2.0, 1.5 } ) );
    CHECK( !spatial::segmentRayIntersection( v1, v2, { 10.0, 5.0 }, { 1.5, 2.0 } ) );
    CHECK( !spatial::segmentRayIntersection( v1, v2, { -12.0, -3.0 }, { 1.5, 2.0 } ) );

    auto result1 = spatial::segmentRayIntersection( v1, v2, { 4.0, -3.0 }, { 1.5, 2.0 } );
    auto result2 = spatial::segmentRayIntersection( v1, v2, { 10.0, 5.0 }, { -1.5, -2.0 } );

    REQUIRE( result1 );
    REQUIRE( result2 );

    auto point1 = std::array { 4.0, -3.0 } + ( *result1 ) * std::array { 1.5, 2.0 };
    auto point2 = std::array { 10.0, 5.0 } + ( *result2 ) * std::array { -1.5, -2.0 };

    CHECK( spatial::distance<2>( point1, { 7.0, 1.0 } )  < 1e-10 );
    CHECK( spatial::distance<2>( point2, { 7.0, 1.0 } ) < 1e-10 );
}

TEST_CASE( "triangleRayIntersection" )
{
    auto transform = spatial::scale<3>( { 1.0, 1.0, 1.0 } );
    
    transform.translate( { 4.97, 1.42, -3.53 } );
    transform.scale( { 2.12, 0.89, 1.18 } );
    transform.rotate( { 1.0, 0.0, 0.0 }, 0.532 );
    //transform.rotate( { 0.0, 1.0, 0.0 }, -4.21 );
    transform.rotate( { 0.0, 0.0, 1.0 }, 2.776 );

    auto v0 = std::array { 0.0, 0.0, 0.0 };
    auto v1 = std::array { 1.0, 0.0, 0.0 };
    auto v2 = std::array { 0.0, 1.0, 0.0 };

    auto rays = std::array
    {
        std::tuple { std::array { 0.0, 0.0, -0.0000001 },
                     std::array { 0.0, 0.0, 1.0 },
                     std::optional { std::array { 0.0, 0.0, 0.0 } } },
        std::tuple { std::array { 0.499999, 0.499999, 0.0001 },
                     std::array { 0.0, 0.0, -0.01 },
                     std::optional { std::array { 0.499999, 0.499999, 0.0 } } },
        std::tuple { std::array { 0.0, 0.0, -1.0 },
                     std::array { 1.0, 2.0, 4.0 },
                     std::optional { std::array { 0.25, 0.5, 0.0 } } },
        std::tuple { std::array { 0.0, 0.0, -1.0 },
                     std::array { 2.0000001, 0.0, 1.0 },
                     OptionalCoordinates<3> { } },
        std::tuple { std::array { 0.0, 0.0, -0.0000001 },
                     std::array { 0.0, 1000000.0, -0.001 },
                     OptionalCoordinates<3> { } },
        std::tuple { std::array { 0.0, 0.0, 0.0 },
                     std::array { 1.1, 1.1, 1.0 },
                     OptionalCoordinates<3> { } },
    };

    v0 = transform( v0 );
    v1 = transform( v1 );
    v2 = transform( v2 );

    for( const auto& [rayOrigin, rayAxis, expected] : rays )
    {
        auto origin = transform( rayOrigin );
        auto axis = transform( rayOrigin + rayAxis ) - origin;

        auto computed = spatial::triangleRayIntersection( v0, v1, v2, origin, axis );

        CHECK( computed.has_value( ) == expected.has_value( ) );

        if( computed.has_value( ) && expected.has_value( ) )
        {
            auto point = origin + ( *computed ) * axis;

            CHECK( spatial::distance( point, transform( *expected ) ) < 1e-10 );
        }
    }

}

TEST_CASE( "fibonacciSphere_test" )
{
    auto expected = std::array
    {
        std::array {  0.0, 1.0, 0.0 },
        std::array { -0.463465363489,  0.777777777778, -0.424572237954 },
        std::array {  0.0726926908181, 0.555555555556,  0.828295718565 },
        std::array {  0.573641659381,  0.333333333333, -0.748213963724 },
        std::array { -0.978616129567,  0.111111111111,  0.173103414001 },
        std::array {  0.838530753589, -0.111111111111,  0.533404627157 },
        std::array { -0.244757285895, -0.333333333333, -0.910484903714 },
        std::array { -0.383234705252, -0.555555555556,  0.737895104593 },
        std::array {  0.590400407417, -0.777777777778, -0.215613281867 },
        std::array { -0.0, -1.0, -0.0 }
    };

    auto points = spatial::fibonacciSphere( expected.size( ) );

    writeVtu<3>( points, testing::outputPath( "core/fibonacciSphere_test.vtu" ) );

    REQUIRE( points.size( ) == expected.size( ) );

    for( size_t i = 0; i < expected.size( ); ++i )
    {
        CHECK( spatial::distance( points[i], expected[i] ) < 1e-6 );
    }
}

TEST_CASE( "boundingBoxIntersectsOther_test" )
{
    auto boundsA0 = std::array { std::array { 0.0, 0.0 }, std::array { 1.0, 1.0 } };
    auto boundsA1 = std::array { std::array { 0.0, 1.1 }, std::array { 1.2, 1.1 } };

    CHECK( spatial::boundingBoxIntersectsOther( boundsA0, boundsA1 ) == false );

    auto boundsB0 = std::array { std::array { 1.0, 1.0 }, std::array { 2.0, 2.0 } };
    auto boundsB1 = std::array { std::array { 1.9, 1.5 }, std::array { 2.0, 1.8 } };

    CHECK( spatial::boundingBoxIntersectsOther( boundsB0, boundsB1 ) == true );

    auto boundsC0 = std::array { std::array { 1.0, 1.0 }, std::array { 2.0, 2.0 } };
    auto boundsC1 = std::array { std::array { 1.3, 1.3 }, std::array { 1.5, 1.5 } };
    
    CHECK( spatial::boundingBoxIntersectsOther( boundsC0, boundsC1 ) == true );
    
    auto boundsD0 = std::array { std::array { 1.0, 1.0 }, std::array { 2.0, 2.0 } };
    auto boundsD1 = std::array { std::array { 0.0, 0.5 }, std::array { 0.5, 1.5 } };

    CHECK( spatial::boundingBoxIntersectsOther( boundsD0, boundsD1 ) == false );
}

TEST_CASE( "boundingBoxIntersectsRay_test" )
{
    auto rayOrigin = std::array { 3.0, 1.0 };
    auto rayDirection0 = std::array { -1.0, 1.0 };

    auto bounds0 = std::array { std::array { -3.0, 1.0 }, std::array { -1.0, 4.0 } };
    auto bounds1 = std::array { std::array { -1.0, 4.0 }, std::array { 2.0, 5.0 } };
    auto bounds2 = std::array { std::array { 2.0, -1.0 }, std::array { 3.0, 0.5 } };

    CHECK( spatial::boundingBoxIntersectsRay( bounds0, rayOrigin, rayDirection0 ) == std::nullopt );
    CHECK( spatial::boundingBoxIntersectsRay( bounds2, rayOrigin, rayDirection0 ) == std::nullopt );
    
    auto result = spatial::boundingBoxIntersectsRay( bounds1, rayOrigin, rayDirection0 );
 
    REQUIRE( result != std::nullopt );

    CHECK( ( *result )[0] == Approx( 3.0 ).epsilon( 1e-12 ) );
    CHECK( ( *result )[1] == Approx( 4.0 ).epsilon( 1e-12 ) );
    
    auto rayDirection1 = std::array { 0.1, 0.0 };
    auto rayDirection2 = std::array { 0.0, 8.0 };

    auto test1 = std::array
    {
        std::pair { 0.99, false }, std::pair { 1.01, true  }, 
        std::pair { 3.99, true  }, std::pair { 4.01, false } 
    };

    for( auto [y, expected] : test1 )
    {
        auto result0 = spatial::boundingBoxIntersectsRay<2>( bounds0, { -4.0, y }, rayDirection1 );
        auto result1 = spatial::boundingBoxIntersectsRay<2>( bounds0, { -3.0, y }, rayDirection1 );
        auto result2 = spatial::boundingBoxIntersectsRay<2>( bounds0, { -2.0, y }, rayDirection1 );

        REQUIRE( ( result0 != std::nullopt ) == expected );
        REQUIRE( ( result1 != std::nullopt ) == expected );
        REQUIRE( ( result2 != std::nullopt ) == expected );

        CHECK( spatial::boundingBoxIntersectsRay<2>( bounds0, { -0.5, y }, rayDirection1 ) == std::nullopt );
    }

    auto test2 = std::array
    {
        std::pair { -3.01, false }, std::pair { -2.99, true  },
        std::pair { -1.01, true  }, std::pair { -0.99, false } 
    };

    for( auto [x, expected] : test2 )
    {
        auto result0 = spatial::boundingBoxIntersectsRay<2>( bounds0, { x, 0.0 }, rayDirection2 );
        auto result1 = spatial::boundingBoxIntersectsRay<2>( bounds0, { x, 1.0 }, rayDirection2 );
        auto result2 = spatial::boundingBoxIntersectsRay<2>( bounds0, { x, 2.5 }, rayDirection2 );

        REQUIRE( ( result0 != std::nullopt ) == expected );
        REQUIRE( ( result1 != std::nullopt ) == expected );
        REQUIRE( ( result2 != std::nullopt ) == expected );

        CHECK( spatial::boundingBoxIntersectsRay<2>( bounds0, { x, 5.0 }, rayDirection2 ) == std::nullopt );
    }

    auto bounds3 = std::array { std::array { 6.0, 6.0 }, std::array { 7.0, 6.0 } };
    auto bounds4 = std::array { std::array { 6.0, 6.0 }, std::array { 6.0, 7.0 } };

    CHECK( spatial::boundingBoxIntersectsRay<2>( bounds3, { -1.0, 1.0 }, { 12.3, 8.4 } ) != std::nullopt );
    CHECK( spatial::boundingBoxIntersectsRay<2>( bounds4, { -1.0, 1.0 }, { 12.3, 8.4 } ) == std::nullopt );
    CHECK( spatial::boundingBoxIntersectsRay<2>( bounds3, { -1.0, 1.0 }, { 12.3, 9.0 } ) == std::nullopt );
    CHECK( spatial::boundingBoxIntersectsRay<2>( bounds4, { -1.0, 1.0 }, { 12.3, 9.0 } ) != std::nullopt );
}

TEST_CASE("boundingbox_collection_test")
{
    // Test boundingBoxIsValid
    CHECK( !spatial::boundingBoxIsValid( spatial::makeEmptyBoundingBox<3>( ) ) );
    CHECK( spatial::boundingBoxIsValid( spatial::makeFullBoundingBox<3>( ) ) );

    CHECK( spatial::boundingBoxIsValid<2>( { std::array { 1.0, -0.5 }, std::array { 1.0, -0.5 } } ) );
    CHECK( spatial::boundingBoxIsValid<2>( { std::array { 1.0, -0.5 }, std::array { 1.0, -0.5 } }, 1e-12 ) );

    CHECK( !spatial::boundingBoxIsValid<2>( { std::array { 1.0, -0.5 }, std::array { 1.0, -0.5 - 1e-10 } } ) );
    CHECK( spatial::boundingBoxIsValid<2>( { std::array { 1.0, -0.5 }, std::array { 1.0, -0.5 - 1e-10 } }, 1e-9 ) );
    CHECK( !spatial::boundingBoxIsValid<2>( { std::array { 1.0, -0.5 }, std::array { 1.0, -0.5 - 1e-10 } }, 1e-11 ) );

    CHECK( !spatial::boundingBoxIsValid<2>( { std::array { 1.0 + 1e-10, -0.5 }, std::array { 1.0, -0.5 } } ) );
    CHECK( spatial::boundingBoxIsValid<2>( { std::array { 1.0 + 1e-10, -0.5 }, std::array { 1.0, -0.5 - 1e-10 } }, 1e-9 ) );
    CHECK( !spatial::boundingBoxIsValid<2>( { std::array { 1.0 + 1e-10, -0.5 }, std::array { 1.0, -0.5 - 1e-10 } }, 1e-11 ) );
    
    CHECK( spatial::boundingBoxIsValid<2>( { std::array { 4.0, 3.0 }, std::array { 5.0, 4.5 } } ) );
    CHECK( spatial::boundingBoxIsValid<2>( { std::array { -4.0, -2.0 }, std::array { -3.0, -1.5 } } ) );
    CHECK( !spatial::boundingBoxIsValid<2>( { std::array { -4.0, -2.0 }, std::array { -5.0, -1.5 } } ) );
    CHECK( !spatial::boundingBoxIsValid<2>( { std::array { -4.0, -2.0 }, std::array { -3.0, -2.5 } } ) );

    // Test boundingBoxVolume
    CHECK( spatial::boundingBoxVolume<3>( spatial::makeEmptyBoundingBox<3>( ) ) == 0 );

    CHECK( spatial::boundingBoxVolume<2>( { std::array { 1.0 + 1e-10, -0.5 }, std::array { 1.0, -0.5 } } ) == 0 );
    CHECK( spatial::boundingBoxVolume<2>( { std::array { 1.0, -0.5 }, std::array { 1.0, -0.5 - 1e-10 } } ) == 0 );
    CHECK( spatial::boundingBoxVolume<2>( { std::array { 1.0, -4.5 }, std::array { 3.0, -3.5 } } ) == 2 );
    CHECK( spatial::boundingBoxVolume<2>( { std::array { -1.5, 2.5 }, std::array { 1.0, 8.2 } } ) == Approx( 14.25 ).epsilon( 1e-10 ) );

    // Test boundingBoxAnd
    auto bounds1 = std::array { std::array { 2.0, -3.0 }, std::array { 4.0, -2.0 } };
    auto bounds2 = std::array { std::array { 3.0, -0.5 }, std::array { 4.5, 1.5 } };
    auto bounds3 = std::array { std::array { -0.5, -5.0 }, std::array { 3.5, 0.0 } };

    auto and1 = spatial::boundingBoxAnd( bounds1, bounds3 );
    auto and2 = spatial::boundingBoxAnd( bounds3, bounds2 );

    CHECK( !spatial::boundingBoxIsValid( spatial::boundingBoxAnd( bounds1, bounds2 ) ) );
    CHECK( !spatial::boundingBoxIsValid( spatial::boundingBoxAnd( bounds1, spatial::makeEmptyBoundingBox<2>( ) ) ) );
    CHECK( !spatial::boundingBoxIsValid( spatial::boundingBoxAnd( spatial::makeEmptyBoundingBox<2>( ), bounds1 ) ) );

    CHECK( spatial::distance<2>( and1[0], { 2.0, -3.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( and1[1], { 3.5, -2.0 } ) < 1e-8 );

    CHECK( spatial::distance<2>( and2[0], { 3.0, -0.5 } ) < 1e-8 );
    CHECK( spatial::distance<2>( and2[1], { 3.5, 0.0 } ) < 1e-8 );
}

TEST_CASE( "distributeSeedPoints_test" )
{
    // Line (NCube)
    auto rst1 = CoordinateList<1> { };
    
    spatial::distributeSeedPoints( CellType::NCube, 1, rst1 );

    REQUIRE( rst1.size( ) == 1 );

    CHECK( spatial::distance<1>( rst1[0], { 0.0 } ) < 1e-8 );

    spatial::distributeSeedPoints( CellType::NCube, 5, utilities::resize0( rst1 ) );
    
    REQUIRE( rst1.size( ) == 5 );
    
    CHECK( spatial::distance<1>( rst1[0], { -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<1>( rst1[1], { -0.5 } ) < 1e-8 );
    CHECK( spatial::distance<1>( rst1[2], {  0.0 } ) < 1e-8 );
    CHECK( spatial::distance<1>( rst1[3], {  0.5 } ) < 1e-8 );
    CHECK( spatial::distance<1>( rst1[4], {  1.0 } ) < 1e-8 );

    // Line (Simplex)
    spatial::distributeSeedPoints( CellType::Simplex, 1, utilities::resize0( rst1 ) );
    
    REQUIRE( rst1.size( ) == 1 );
    
    CHECK( spatial::distance<1>( rst1[0], { 0.5 } ) < 1e-8 );
    
    spatial::distributeSeedPoints( CellType::Simplex, 4, utilities::resize0( rst1 ) );
    
    REQUIRE( rst1.size( ) == 4 );
    
    CHECK( spatial::distance<1>( rst1[0], { 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<1>( rst1[1], { 1.0 / 3.0 } ) < 1e-8 );
    CHECK( spatial::distance<1>( rst1[2], { 2.0 / 3.0 } ) < 1e-8 );
    CHECK( spatial::distance<1>( rst1[3], { 1.0 } ) < 1e-8 );

    // Quad
    auto rst2 = CoordinateList<2> { };
    
    spatial::distributeSeedPoints( CellType::NCube, 1, rst2 );
    
    REQUIRE( rst2.size( ) == 1 );
    
    CHECK( spatial::distance<2>( rst2[0], { } ) < 1e-8 );
        
    spatial::distributeSeedPoints( CellType::NCube, 2, utilities::resize0( rst2 ) );
    
    REQUIRE( rst2.size( ) == 4 );
    
    CHECK( spatial::distance<2>( rst2[0], { -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( rst2[1], { -1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( rst2[2], {  1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( rst2[3], {  1.0,  1.0 } ) < 1e-8 );
    
    spatial::distributeSeedPoints( CellType::NCube, 4, utilities::resize0( rst2 ) );
    
    REQUIRE( rst2.size( ) == 16 );
    
    for( size_t i = 0; i < 4; ++i )
    {
        for( size_t j = 0; j < 4; ++j )
        {
            auto rst = std::array { 2.0 * i / 3.0 - 1.0, 2.0 * j / 3.0 -1.0 };

            CHECK( spatial::distance<2>( rst2[i * 4 + j], rst ) < 1e-8 );
        }
    }
    
    // Triangle
    spatial::distributeSeedPoints( CellType::Simplex, 1, utilities::resize0( rst2 ) );
    
    REQUIRE( rst2.size( ) == 1 );
    
    CHECK( spatial::distance<2>( rst2[0], { 1.0 / 3.0, 1.0 / 3.0 } ) < 1e-8 );
    
    spatial::distributeSeedPoints( CellType::Simplex, 2, utilities::resize0( rst2 ) );
    
    REQUIRE( rst2.size( ) == 3 );
    
    CHECK( spatial::distance<2>( rst2[0], { 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( rst2[1], { 0.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( rst2[2], { 1.0, 0.0 } ) < 1e-8 );
    
    spatial::distributeSeedPoints( CellType::Simplex, 3, utilities::resize0( rst2 ) );
    
    REQUIRE( rst2.size( ) == 6 );
    
    CHECK( spatial::distance<2>( rst2[0], { 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( rst2[1], { 0.0, 0.5 } ) < 1e-8 );
    CHECK( spatial::distance<2>( rst2[2], { 0.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( rst2[3], { 0.5, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<2>( rst2[4], { 0.5, 0.5 } ) < 1e-8 );
    CHECK( spatial::distance<2>( rst2[5], { 1.0, 0.0 } ) < 1e-8 );
    
    // Cube 
    auto rst3 = CoordinateList<3> { { 0.0, 0.0, 0.0 } };
    
    spatial::distributeSeedPoints( CellType::NCube, 1, rst3 );

    REQUIRE( rst3.size( ) == 2 );

    CHECK( spatial::distance<3>( rst3[1], { } ) < 1e-8 );

    spatial::distributeSeedPoints( CellType::NCube, 2, utilities::resize0( rst3 ) );
    
    REQUIRE( rst3.size( ) == 8 );

    CHECK( spatial::distance<3>( rst3[0], { -1.0, -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( rst3[1], { -1.0, -1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( rst3[2], { -1.0,  1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( rst3[3], { -1.0,  1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( rst3[4], {  1.0, -1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( rst3[5], {  1.0, -1.0,  1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( rst3[6], {  1.0,  1.0, -1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( rst3[7], {  1.0,  1.0,  1.0 } ) < 1e-8 );

    // Tetrahedron
    rst3 = { { 0.0, 0.0, 0.0 } };

    spatial::distributeSeedPoints( CellType::Simplex, 1, rst3 );
    
    REQUIRE( rst3.size( ) == 2 );
    
    CHECK( spatial::distance<3>( rst3[1], { 1.0 / 4.0, 1.0 / 4.0, 1.0 / 4.0 } ) < 1e-8 );

    spatial::distributeSeedPoints(CellType::Simplex, 2, utilities::resize0( rst3 ) );
    
    REQUIRE( rst3.size( ) == 4 );
    
    CHECK( spatial::distance<3>( rst3[0], { 0.0, 0.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( rst3[1], { 0.0, 0.0, 1.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( rst3[2], { 0.0, 1.0, 0.0 } ) < 1e-8 );
    CHECK( spatial::distance<3>( rst3[3], { 1.0, 0.0, 0.0 } ) < 1e-8 );
}

TEST_CASE( "simplexShapeFunctions_test" )
{
    // Line segment
    auto N1 = spatial::simplexShapeFunctions<1>( { 0.7 } );
    
    CHECK( spatial::distance<2>( N1, { 0.3, 0.7 } ) < 1e-8 );
    
    N1 = spatial::simplexShapeFunctions<1>( { 0.4 }, { 1 } );
    
    CHECK( spatial::distance<2>( N1, { -1.0, 1.0 } ) < 1e-8 );

    // Triangle
    auto N2 = spatial::simplexShapeFunctions<2>( { 0.1, 0.2 } );

    CHECK( spatial::distance<3>( N2, { 0.7, 0.1, 0.2 } ) < 1e-8 );

    N2 = spatial::simplexShapeFunctions<2>( { 0.4, 0.3 }, { 0, 0 } );

    CHECK( spatial::distance<3>( N2, { 0.3, 0.4, 0.3 } ) < 1e-8 );
    
    N2 = spatial::simplexShapeFunctions<2>( { 0.4, 0.3 }, { 1, 0 } );

    CHECK( spatial::distance<3>( N2, { -1.0, 1.0, 0.0 } ) < 1e-8 );
    
    N2 = spatial::simplexShapeFunctions<2>( { 0.4, 0.3 }, { 0, 1 } );

    CHECK( spatial::distance<3>( N2, { -1.0, 0.0, 1.0 } ) < 1e-8 );

    // Hexaedron
    auto N3 = spatial::simplexShapeFunctions<3>( { 0.3, 0.2, 0.4 } );

    CHECK( spatial::distance<4>( N3, { 0.1, 0.3, 0.2, 0.4 } ) < 1e-8 );

    N3 = spatial::simplexShapeFunctions<3>( { 0.3, 0.2, 0.4 }, { 1, 0, 0 } );
    
    CHECK( spatial::distance<4>( N3, { -1.0, 1.0, 0.0, 0.0 } ) < 1e-8 );

    N3 = spatial::simplexShapeFunctions<3>( { 0.3, 0.2, 0.4 }, { 0, 1, 0 } );
    
    CHECK( spatial::distance<4>( N3, { -1.0, 0.0, 1.0, 0.0 } ) < 1e-8 );

    N3 = spatial::simplexShapeFunctions<3>( { 0.3, 0.2, 0.4 }, { 0, 0, 1 } );
    
    CHECK( spatial::distance<4>( N3, { -1.0, 0.0, 0.0, 1.0 } ) < 1e-8 );
    
    N3 = spatial::simplexShapeFunctions<3>( { 0.3, 0.2, 0.4 }, { 0, 1, 1 } );
    
    CHECK( spatial::distance<4>( N3, { 0.0, 0.0, 0.0, 0.0 } ) < 1e-8 );
    
    N3 = spatial::simplexShapeFunctions<3>( { 0.3, 0.2, 0.4 }, { 2, 0, 0 } );
    
    CHECK( spatial::distance<4>( N3, { 0.0, 0.0, 0.0, 0.0 } ) < 1e-8 );
}

TEST_CASE( "multilinearShapeFunctions_test" )
{
    // Line segment
    auto N1 = std::vector
    {
        spatial::multilinearShapeFunctions<1>( { 0.6 } ),
        spatial::multilinearShapeFunctions<1>( { -0.2 }, { 0 } ),
        spatial::multilinearShapeFunctions<1>( { 0.4 }, { 1 } ),
        spatial::multilinearShapeFunctions<1>( { -0.8 }, { 2 } ),
    };

    auto expectedN1 = std::vector
    {
        std::array { 0.2, 0.8 },
        std::array { 0.6, 0.4 },
        std::array { -0.5, 0.5 },
        std::array { 0.0, 0.0 }
    };

    for( size_t i = 0; i < N1.size( ); ++i )
    {
        CHECK( spatial::distance( N1[i], expectedN1[i] ) < 1e-8 );
    }

    // Quad
    auto N2 = std::vector
    {
        spatial::multilinearShapeFunctions<2>( { 0.2, -0.7 } ),
        spatial::multilinearShapeFunctions<2>( { 0.2, -0.7 }, { 1, 0 } ),
        spatial::multilinearShapeFunctions<2>( { 0.2, -0.7 }, { 0, 1 } ),
        spatial::multilinearShapeFunctions<2>( { 0.2, -0.7 }, { 1, 1 } ),
        spatial::multilinearShapeFunctions<2>( { 0.2, -0.7 }, { 2, 0 } ),
    };

    auto expectedN2 = std::vector
    {
        std::array { 0.4 * 0.85, 0.4 * 0.15, 0.6 * 0.85, 0.6 * 0.15 },
        std::array { -0.5 * 0.85, -0.5 * 0.15, 0.5 * 0.85, 0.5 * 0.15 },
        std::array { 0.4 * -0.5, 0.4 * 0.5, 0.6 * -0.5, 0.6 * 0.5 },
        std::array { -0.5 * -0.5, -0.5 * 0.5, 0.5 * -0.5, 0.5 * 0.5 },
        std::array { 0.0, 0.0, 0.0, 0.0 }
    };

    for( size_t i = 0; i < N2.size( ); ++i )
    {
        CHECK( spatial::distance( N2[i], expectedN2[i] ) < 1e-8 );
    }

    
    // Cube
    auto N3 = std::vector
    {
        spatial::multilinearShapeFunctions<3>( { -0.6, 0.8, 0.2 } ),
        spatial::multilinearShapeFunctions<3>( { 0.1, 0.5, -0.7 } ),
        spatial::multilinearShapeFunctions<3>( { -0.6, 0.8, 0.2 }, { 1, 0, 0 } ),
        spatial::multilinearShapeFunctions<3>( { -0.6, 0.8, 0.2 }, { 1, 1, 0 } ),
        spatial::multilinearShapeFunctions<3>( { -0.6, 0.8, 0.2 }, { 1, 1, 1 } ),
        spatial::multilinearShapeFunctions<3>( { -0.6, 0.8, 0.2 }, { 0, 1, 1 } ),
        spatial::multilinearShapeFunctions<3>( { -0.6, 0.8, 0.2 }, { 0, 0, 2 } ),
    };

    auto expectedN3 = std::vector
    {
        std::array { 0.8 * 0.1 * 0.4,   0.8 * 0.1 * 0.6,   0.8 * 0.9 * 0.4,   0.8 * 0.9 * 0.6,
                     0.2 * 0.1 * 0.4,   0.2 * 0.1 * 0.6,   0.2 * 0.9 * 0.4,   0.2 * 0.9 * 0.6 },
        std::array { 0.45 * 0.25 * 0.85,   0.45 * 0.25 * 0.15,   0.45 * 0.75 * 0.85,   0.45 * 0.75 * 0.15,
                     0.55 * 0.25 * 0.85,   0.55 * 0.25 * 0.15,   0.55 * 0.75 * 0.85,   0.55 * 0.75 * 0.15 },
        std::array { -0.5 * 0.1 * 0.4,  -0.5 * 0.1 * 0.6,  -0.5 * 0.9 * 0.4,   -0.5 * 0.9 * 0.6,
                      0.5 * 0.1 * 0.4,   0.5 * 0.1 * 0.6,   0.5 * 0.9 * 0.4,    0.5 * 0.9 * 0.6 },
        std::array { -0.5 * -0.5 * 0.4,  -0.5 * -0.5 * 0.6,  -0.5 * 0.5 * 0.4,   -0.5 * 0.5 * 0.6,
                      0.5 * -0.5 * 0.4,   0.5 * -0.5 * 0.6,   0.5 * 0.5 * 0.4,    0.5 * 0.5 * 0.6 },
        std::array { -0.5 * -0.5 * -0.5,  -0.5 * -0.5 * 0.5,  -0.5 * 0.5 * -0.5,   -0.5 * 0.5 * 0.5,
                      0.5 * -0.5 * -0.5,   0.5 * -0.5 * 0.5,   0.5 * 0.5 * -0.5,    0.5 * 0.5 * 0.5 },
        std::array { 0.8 * -0.5 * -0.5,  0.8 * -0.5 * 0.5,  0.8 * 0.5 * -0.5,   0.8 * 0.5 * 0.5,
                     0.2 * -0.5 * -0.5,  0.2 * -0.5 * 0.5,  0.2 * 0.5 * -0.5,   0.2 * 0.5 * 0.5 },
        std::array { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },
    };

    for( size_t i = 0; i < N3.size( ); ++i )
    {
        CHECK( spatial::distance( N3[i], expectedN3[i] ) < 1e-8 );
    }
}

TEST_CASE( "findVoxel_test" )
{
    auto nvoxels = std::array<size_t, 3> { 3, 2, 4 };
    auto origin = std::array { 2.0, 3.0, 1.0 };
    auto lengths = std::array { 9.0, 8.0, 8.0 };

    static constexpr auto eps = 50.0 * std::numeric_limits<double>::epsilon( );

    auto index0 = spatial::findVoxel<3>( nvoxels, lengths, origin, { 5.3, 4.5, 7.0 } );
    auto index1 = spatial::findVoxel<3>( nvoxels, lengths, origin, { 10.3, 9.7, 4.2 } );
    auto index2 = spatial::findVoxel<3>( nvoxels, lengths, origin, { 6.3, 3.0 - eps, 5.9 } );
    auto index3 = spatial::findVoxel<3>( nvoxels, lengths, origin, { 11.0 + eps, 10.1, 1.0 - eps } );

    CHECK( index0 == 11 );
    CHECK( index1 == 21 );
    CHECK( index2 == 10 ); 
    CHECK( index3 == 20 );

    CHECK( !spatial::findVoxel<3>( nvoxels, lengths, origin, { 1.9, 5.0, 5.0 } ) );
    CHECK( !spatial::findVoxel<3>( nvoxels, lengths, origin, { 11.7, 5.0, 5.0 } ) );
    CHECK( !spatial::findVoxel<3>( nvoxels, lengths, origin, { 5.0, 2.9, 5.0 } ) );
    CHECK( !spatial::findVoxel<3>( nvoxels, lengths, origin, { 5.0, 11.1, 5.0 } ) );
    CHECK( !spatial::findVoxel<3>( nvoxels, lengths, origin, { 5.0, 5.0, 0.9 } ) );
    CHECK( !spatial::findVoxel<3>( nvoxels, lengths, origin, { 5.0, 5.0, 9.1 } ) );
}

TEST_CASE("voxelFunction_test")
{
    auto data = std::vector { 3.0, 2.0, 5.0, 4.0, 7.0, 9.0 };

    auto f = spatial::voxelFunction<2>( data, { 3, 2 }, { 3.0, 3.0 }, { 1.0, 2.0 } );
    
    CHECK( f( { 1.0, 2.0 } ) == Approx( 3.0 ).epsilon( 1e-12 ) );
    CHECK( f( { 2.1, 2.0 } ) == Approx( 5.0 ).epsilon( 1e-12 ) );
    CHECK( f( { 3.9, 5.0 } ) == Approx( 9.0 ).epsilon( 1e-12 ) );
}

} // namespace mlhp

