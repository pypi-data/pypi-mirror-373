// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/polynomials.hpp"
#include "mlhp/core/spatial.hpp"

namespace mlhp
{
namespace test
{

template<size_t N>
void testIntegratedLegendre( double coordinate, const std::array<std::vector<double>, N>& expectedResults )
{
    size_t polynomialDegree = expectedResults[0].size( ) - 1;
    
    std::array<std::vector<double>, N> target;
    std::array<double*, N> pointers { };

    for( size_t i = 0; i < N; ++i )
    {
        target[i].resize( polynomialDegree + 1 );

        std::fill( target[i].begin( ), target[i].end( ), -6.61234 );

        pointers[i] = &target[i][0];
    }

    REQUIRE_NOTHROW( polynomial::integratedLegendre<N - 1>( polynomialDegree, coordinate, pointers ) );

    for( size_t i = 0; i < N; ++i )
    {
        for( size_t j = 0; j < polynomialDegree; ++j )
        {
            if( std::abs( expectedResults[i][j] ) < 1e-10 )
            {
                CHECK( std::abs( target[i][j] ) < 1e-10 );
            }
            else
            {
                CHECK( target[i][j] == Approx( expectedResults[i][j] ).epsilon( 1e-10 ) );
            }
        }
    }

    // now test the same result for one diff order less    
    std::array<std::vector<double>, N - 1> reducedResults;

    for( size_t i = 0; i < N - 1; ++i )
    {
        reducedResults[i] = expectedResults[i];
    }

    testIntegratedLegendre( coordinate, reducedResults );
}

template<>
void testIntegratedLegendre<0>( double, const std::array<std::vector<double>, 0>& ){ }

} // namespace test

TEST_CASE( "IntegratedLegendre_coordinate1" )
{
    test::testIntegratedLegendre<1>( -1.0, { std::vector<double>{ 1.0, 0.0, 0.0, 0.0 } } );
    test::testIntegratedLegendre<1>( 0.0, { std::vector<double>{ 0.5, 0.5, -0.61237243569579458, 0.0 } } );
    test::testIntegratedLegendre<1>( 1.0, { std::vector<double>{ 0.0, 1.0, 0.0, 0.0 } } );
}

TEST_CASE( "IntegratedLegendre_coordinate2" )
{
    std::vector<double> expectedD0 
    { 
        +0.561700000000000000e+00, +0.438300000000000000e+00, -6.030474976888907657e-01, +9.607072192510245079e-02, 
        +2.127585977318513510e-01, -9.323454490064651823e-02, -1.142743874623741995e-01, +8.812069117556850517e-02, 
        +6.442127823830649802e-02, -8.128487753892885137e-02, -3.272551676773773066e-02, +7.303729791069984989e-02, 
        +1.049802966219313440e-02, -6.368970901303631915e-02, +5.648089605605997009e-03, +5.357654411090673890e-02, 
        -1.730665254397349348e-02, -4.304842015715738129e-02, +2.535422126132674120e-02, +3.245972929207168595e-02, 
        -3.035714339345355062e-02 
    };

    std::vector<double> expectedD1
    {
        -0.5000000000000000000-00,  0.500000000000000000e+00, -1.511335171297220892e-01, -7.544540854369397032e-01,  
         3.375017949649314342e-01,  6.765126441042697003e-01, -5.045911185909363050e-01, -5.534559125940465840e-01,  
         6.413030048139813921e-01,  3.958242674040505227e-01, -7.391054186352378208e-01, -2.137576085804855364e-01,  
         7.919669964001092577e-01,  1.850523610146588560e-02, -7.966325766512319939e-01,  1.779763672721598744e-01,  
         7.527979822974099067e-01, -3.636881552575729204e-01, -6.631205890788141044e-01,  5.273001718268763849e-01,  
         5.330542168976003525e-01
    };

    std::vector<double> expectedD2
    {
         0.0000000000000000000+00,  0.0000000000000000000+00,  1.224744871391589163e+00, -5.853375948971669684e-01, 
        -2.592581868743418561e+00,  1.893524658359580615e+00,  3.481242452186442460e+00, -3.758298749073315737e+00, 
        -3.663375857010340741e+00,  5.943008704430109646e+00,  2.990839700079742425e+00, -8.158334295156537408e+00, 
        -1.407167645156167657e+00,  1.008922894514966728e+01, -1.043847559564411220e+00, -1.142504989608605648e+01,  
         4.217823775159302180e+00,  1.189022946534410075e+01, -7.878359904107370859e+00, -1.127288596529825604e+01,  
         1.171409152099376882e+01
    };

    test::testIntegratedLegendre<3>( -0.1234, { expectedD0, expectedD1, expectedD2 } );
}

TEST_CASE( "lagragePolynomials_all_test" )
{
    std::vector<double> points { -1.0, 0.0, 1.0 };
    std::vector<double> coordinates { -0.5, 0.4 };
    std::vector<double> target( coordinates.size( ) * points.size( ), 42.0 );

    REQUIRE_NOTHROW( polynomial::lagrange( points.size( ) - 1, coordinates.size( ), points.data( ), coordinates.data( ), target.data( ) ) );

    std::vector<double> expectedValues 
    { 
         0.375, -0.12, // N0(-0.5), N0(0.4)
         0.75 ,  0.84, // N1(-0.5), N1(0.4)
        -0.125,  0.28  // N2(-0.5), N2(0.4)
    };

    for( size_t i = 0; i < expectedValues.size( ); ++i )
    {
        CHECK( target[i] == Approx( expectedValues[i] ).epsilon( 1e-12 ) );
    }
}


TEST_CASE( "makeEquallySpacedLagrage_test" )
{
    static constexpr size_t p = 2;

    // N0  = x/2 * (x - 1)   N1  = (1 - x)*(1 + x)    N2  = x/2 * (x + 1)
    // N0' = x - 1/2         N1' = -2*x               N2' = x + 1/2
    // N0" = 1               N1" = -2                 N2" = 1

    auto coordinates = std::array { -0.5, 0.4 };

    auto lagrange0 = polynomial::makeEquallySpacedLagrangeBasis( false );
    auto lagrange1 = polynomial::makeEquallySpacedLagrangeBasis( true );

    auto expected0 = std::array
    {
        std::array {  0.375,  0.75, -0.125,
                     -1.0  ,  1.0 ,  0.0  ,
                      1.0  , -2.0 ,  1.0   },
        std::array { -0.12 ,  0.84,  0.28 ,
                     -0.1  , -0.8 ,  0.9  ,
                      1.0  , -2.0 ,  1.0   }
    };
    
    auto expected1 = std::array
    {
        std::array {  0.375, -0.125,  0.75,
                     -1.0  ,  0.0  ,  1.0 ,
                      1.0  ,  1.0  , -2.0  },
        std::array { -0.12 ,  0.28 ,  0.84,
                     -0.1  ,  0.9  , -0.8 ,
                      1.0  ,  1.0  , -2.0  }
    };

    auto computed0 = std::array<double, 3 * ( p + 1 )> { };
    auto computed1 = std::array<double, 3 * ( p + 1 )> { };

    for( size_t d = 0; d <= 2; ++d )
    {
        for( size_t i = 0; i < coordinates.size( ); ++i )
        {
            REQUIRE_NOTHROW( lagrange0( p, d, coordinates[i], computed0.data( ) ) );
            REQUIRE_NOTHROW( lagrange1( p, d, coordinates[i], computed1.data( ) ) );

            CHECK( utilities::floatingPointEqual( computed0.begin( ), computed0.begin( ) + 
                3 * ( static_cast<int>( d ) + 1 ), expected0[i].begin( ), 1e-12 ) );

            CHECK( utilities::floatingPointEqual( computed1.begin( ), computed1.begin( ) + 
                3 * ( static_cast<int>( d ) + 1 ), expected1[i].begin( ), 1e-12 ) );
        }
    }
}

TEST_CASE( "cubicHermite_test" )
{
    double eps = 1e-10;

    // t = 0.0
    auto F0 = polynomial::cubicHermite( 0.0 );
    auto D0 = polynomial::cubicHermiteDerivatives( 0.0 );
    
    auto expectedF0 = std::array { 1.0, 0.0, 0.0, 0.0 };
    auto expectedD0 = std::array { 0.0, 1.0, 0.0, 0.0 };
    
    // t = 0.2
    auto F1 = polynomial::cubicHermite( 0.2 );
    auto D1 = polynomial::cubicHermiteDerivatives( 0.2 );

    auto expectedF1 = std::array { 0.896, 0.128, 0.104, -0.032 };
    auto expectedD1 = std::array { -0.96, 0.32, 0.96, -0.28 };

    // t = 0.5
    auto F2 = polynomial::cubicHermite( 0.5 );
    auto D2 = polynomial::cubicHermiteDerivatives( 0.5 );
    
    auto expectedF2 = std::array { 0.5, 0.125, 0.5, -0.125 };
    auto expectedD2 = std::array { -1.5, -0.25, 1.5, -0.25 };
    
    // t = 0.7
    auto F3 = polynomial::cubicHermite( 0.7 );
    auto D3 = polynomial::cubicHermiteDerivatives( 0.7 );

    auto expectedF3 = std::array { 0.216, 0.063, 0.784, -0.147 };
    auto expectedD3 = std::array { -1.26, -0.33, 1.26, 0.07 };

    // t = 1.0
    auto F4 = polynomial::cubicHermite( 1.0 );
    auto D4 = polynomial::cubicHermiteDerivatives( 1.0 );
    
    auto expectedF4 = std::array { 0.0, 0.0, 1.0, 0.0 };
    auto expectedD4 = std::array { 0.0, 0.0, 0.0, 1.0 };

    // Check results
    for( size_t i = 0; i < 4; ++i )
    {
        CHECK( F0[i] == Approx( expectedF0[i] ).epsilon( eps ) );
        CHECK( D0[i] == Approx( expectedD0[i] ).epsilon( eps ) );

        CHECK( F1[i] == Approx( expectedF1[i] ).epsilon( eps ) );
        CHECK( D1[i] == Approx( expectedD1[i] ).epsilon( eps ) );

        CHECK( F2[i] == Approx( expectedF2[i] ).epsilon( eps ) );
        CHECK( D2[i] == Approx( expectedD2[i] ).epsilon( eps ) );
        
        CHECK( F3[i] == Approx( expectedF3[i] ).epsilon( eps ) );
        CHECK( D3[i] == Approx( expectedD3[i] ).epsilon( eps ) );

        CHECK( F4[i] == Approx( expectedF4[i] ).epsilon( eps ) );
        CHECK( D4[i] == Approx( expectedD4[i] ).epsilon( eps ) );
    }
} // cubicHermitePolynomials_test

TEST_CASE( "cubicHermiteSpline_test" )
{
    auto positions = std::vector { 1.0, 2.0, 12.0 };
    auto values = std::vector { 1.0, 3.0, 2.0 };
    auto derivatives = std::vector { 0.1, 0.2, 0.3 };

    auto spline = interpolation::makeCubicHermiteSpline( positions, values, derivatives );

    for( size_t i = 0; i < 3; ++i )
    {
        for( auto d : { -1e-10, 1e-10 } )
        {
            CHECK( spline( positions[i] + d )[0] == Approx( values[i] ).epsilon( 1e-8 ) );
            CHECK( spline( positions[i] + d )[1] == Approx( derivatives[i] ).epsilon( 1e-7 ) );
        }
    }
} // cubicHermiteSpline_test

TEST_CASE( "linearInterpolation_test" )
{
    auto positions = std::vector { 1.0, 2.0, 12.0 };
    auto values = std::vector { 1.0, 3.0, 2.0 };

    auto interpolation0 = interpolation::makeLinearInterpolation( positions, values, interpolation::Extrapolate::Linear );
    auto interpolation1 = interpolation::makeLinearInterpolation( positions, values, interpolation::Extrapolate::Constant );

    auto testTuples = std::array 
    { 
        std::tuple { 0.9,  std::array { 0.8,   2.0 }, std::array { 1.0,   0.0 } },
        std::tuple { 1.1,  std::array { 1.2,   2.0 }, std::array { 1.2,   2.0 } },
        std::tuple { 1.9,  std::array { 2.8,   2.0 }, std::array { 2.8,   2.0 } },
        std::tuple { 2.3,  std::array { 2.97, -0.1 }, std::array { 2.97, -0.1 } },
        std::tuple { 7.0,  std::array { 2.5,  -0.1 }, std::array { 2.5,  -0.1 } },
        std::tuple { 11.0, std::array { 2.1,  -0.1 }, std::array { 2.1,  -0.1 } },
        std::tuple { 12.1, std::array { 1.99, -0.1 }, std::array { 2.0,   0.0 } },
    };

    for( auto [x, expected0, expected1] : testTuples )
    {
        CHECK( interpolation0( x )[0] == Approx( expected0[0] ).epsilon( 1e-10 ) );
        CHECK( interpolation0( x )[1] == Approx( expected0[1] ).epsilon( 1e-10 ) );

        CHECK( interpolation1( x )[0] == Approx( expected1[0] ).epsilon( 1e-10 ) );
        CHECK( interpolation1( x )[1] == Approx( expected1[1] ).epsilon( 1e-10 ) );
    }

} // linearInterpolation_test

TEST_CASE( "linearBSpline_test" )
{
    auto knotVector = std::vector { 0.0, 0.0, 0.5, 1.0, 1.0 };
    
    auto A0 = std::array<double, 2> { };
    auto A1 = std::array<double, 2> { };
    auto A2 = std::array<double, 2> { };

    polynomial::bspline( knotVector, 1, 0, 1, 0.00, A0 );
    polynomial::bspline( knotVector, 1, 0, 1, 0.25, A1 );
    polynomial::bspline( knotVector, 1, 0, 1, 0.50, A2 );
    
    CHECK( A0[0] == Approx( 1.0 ) );
    CHECK( A1[0] == Approx( 0.5 ) );
    CHECK( A2[0] == Approx( 0.0 ) );
    
    CHECK( A0[1] == Approx( 0.0 ) );
    CHECK( A1[1] == Approx( 0.5 ) );
    CHECK( A2[1] == Approx( 1.0 ) );
    
    auto B0 = std::array<double, 2> { };
    auto B1 = std::array<double, 2> { };
    auto B2 = std::array<double, 2> { };

    polynomial::bspline( knotVector, 1, 0, 2, 0.50, B0 );
    polynomial::bspline( knotVector, 1, 0, 2, 0.75, B1 );
    polynomial::bspline( knotVector, 1, 0, 2, 1.00, B2 );
    
    CHECK( B0[0] == Approx( 1.0 ) );
    CHECK( B1[0] == Approx( 0.5 ) );
    CHECK( B2[0] == Approx( 0.0 ) );
    
    CHECK( B0[1] == Approx( 0.0 ) );
    CHECK( B1[1] == Approx( 0.5 ) );
    CHECK( B2[1] == Approx( 1.0 ) );

} // linearInterpolation_test

TEST_CASE( "quadraticBSpline_test" )
{
    auto knotVector = std::vector { 0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0 };

    auto A = std::array<double, 3> { };
    auto B = std::array<double, 3> { };
    auto C = std::array<double, 3> { };

    polynomial::bspline( knotVector, 2, 0, 2, 0.00, A );
    polynomial::bspline( knotVector, 2, 0, 2, 0.25, B );
    polynomial::bspline( knotVector, 2, 0, 2, 0.50, C );
    
    CHECK( A[0] == Approx( 1.0 ) );
    CHECK( B[0] == Approx( 0.25 ) );
    CHECK( C[0] == Approx( 0.0 ) );

    CHECK( A[1] == Approx( 0.0 ) );
    CHECK( B[1] == Approx( 0.625 ) );
    CHECK( C[1] == Approx( 0.5 ) );
    
    CHECK( A[2] == Approx( 0.0 ) );
    CHECK( B[2] == Approx( 0.125 ) );
    CHECK( C[2] == Approx( 0.5 ) );

    polynomial::bspline( knotVector, 2, 0, 3, 0.50, A );
    polynomial::bspline( knotVector, 2, 0, 3, 0.75, B );
    polynomial::bspline( knotVector, 2, 0, 3, 1.00, C );
    
    CHECK( A[0] == Approx( 0.5 ) );
    CHECK( B[0] == Approx( 0.125 ) );
    CHECK( C[0] == Approx( 0.0 ) );

    CHECK( A[1] == Approx( 0.5 ) );
    CHECK( B[1] == Approx( 0.625 ) );
    CHECK( C[1] == Approx( 0.0 ) );

    CHECK( A[2] == Approx( 0.0 ) );
    CHECK( B[2] == Approx( 0.25 ) );
    CHECK( C[2] == Approx( 1.0 ) );

} // quadraticBSpline_test

TEST_CASE( "cubicBSpline_test" )
{
    auto knotVector = std::array { 0.1, 0.1, 0.1, 0.1,   
                                   0.4,                  
                                   0.6, 0.6,             
                                   1.2, 1.2, 1.2,        
                                   1.4, 1.4,             
                                   1.5, 1.5, 1.5, 1.5 }; 

    auto expected = std::array
    {
        std::tuple { 0.1, size_t { 3 }, std::array { 1.0, 0.0, 0.0, 0.0 },
                                        std::array { -10.0, 10.0, 0.0, 0.0 },
                                        std::array { 66.6666667, -66.6666667, 40.0, 0.0 } },
        std::tuple { 0.2, size_t { 3 }, std::array {  2.96296296e-1, 5.39259259e-1, 1.51111111e-1, 1.33333333e-2 },
                                        std::array { -4.44444444e+0, 1.51111111e+0, 2.53333333e+0, 4.00000000e-1 },
                                        std::array { 4.44444444e+1, -3.64444444e+1, -2.57777778e+1, 8.00000000e+0 } },
        std::tuple { 0.4, size_t { 3 }, std::array { 0.0, 0.16, 0.48, 0.36 },
                                        std::array { 0.0, -2.4, -1.2, 3.6 },
                                        std::array { 0.0, 24.0, -157.333333, 24.0 } },
        std::tuple { 0.4, size_t { 4 }, std::array { 0.16, 0.48, 0.36, 0.0 },
                                        std::array { -2.4, -1.2, 3.6, 0.0 },
                                        std::array { 24.0, -24.0, 24.0, 0.0 } },
        std::tuple { 0.5, size_t { 4 }, std::array { 0.02, 0.21, 0.73875, 0.03125 },
                                        std::array { -0.6, -3.3, 2.9625, 0.9375 },
                                        std::array { 12.0, 18.0, -78.0, 18.75 } },
        std::tuple { 0.6, size_t { 4 }, std::array { 0.0, 0.0, 0.75, 0.25 },
                                        std::array { 0.0, 0.0, -3.75, 3.75 },
                                        std::array { 0.0, 60.0, -180.0, 37.5 } },
        std::tuple { 0.6, size_t { 6 }, std::array { 0.75, 0.25, 0.0, 0.0 },
                                        std::array { -3.75, 3.75, 0.0, 0.0 },
                                        std::array { 12.5, -12.5, 16.6666667, 0.0 } },
        std::tuple { 1.1, size_t { 6 }, std::array { 3.47222222e-3, 7.06018519e-2, 3.47222222e-1, 5.78703704e-1 },
                                        std::array { -1.04166667e-1, -1.28472222e+0, -2.08333333e+0, 3.47222222e+0 },
                                        std::array { 2.08333333e+0, 1.18055556e+1, -2.84722222e+1, 1.38888889e+1 } },
        // std::tuple { 1.2, size_t { 6 }, std::array { 0.0, 0.0, 0.0, 1.0 },
        //                                 std::array { 0.0, 0.0, 0.0, -15.0 } },
        // std::tuple { 1.2, size_t { 9 }, std::array { 1.0, 0.0, 0.0, 0.0 },
        //                                 std::array { -15.0, 0.0, 0.0, 0.0 } },
        std::tuple { 1.3, size_t { 9 }, std::array { 1.25000000e-1, 3.75000000e-1, 4.16666667e-1, 8.33333333e-2 },
                                        std::array { -3.75000000e+0, -3.75000000e+0, 5.00000000e+0, 2.50000000e+0 },
                                        std::array { 7.50000000e+1, 1.70530257e-13, -3.75000000e+2, 5.00000000e+1 } },
        std::tuple { 1.4, size_t { 9 }, std::array { 0.0, 0.0, 3.33333333e-01, 6.66666667e-01 },
                                        std::array { 0.0, 0.0, -1.00000000e+01, 1.00000000e+01 },
                                        std::array { 0.0, 1.50000000e+2, -9.00000000e+2, 1.00000000e+2 } },
        std::tuple { 1.4, size_t { 11 }, std::array { 3.33333333e-1, 6.66666667e-1, 0.0, 0.0 },
                                         std::array { -1.00000000e+1, 1.00000000e+1, 0.0, 0.0 },
                                         std::array { 2.00000000e+2, -2.00000000e+2, 600.0, 0.0 } },
        std::tuple { 1.43, size_t { 11 }, std::array { 0.114333333, 0.669666667, 0.189, 0.027 },
                                          std::array { -4.9, -7.7, 9.9, 2.7 },
                                          std::array { 140.0, 40.0, -360.0, 180.0 } },
        std::tuple { 1.5, size_t { 11 }, std::array { 0.0, 0.0, 0.0, 1.0 },
                                         std::array { 0.0, 0.0, -30.0, 30.0 },
                                         std::array { 0.0, 600.0, -2600.0, 600.0 } }
    };
    
    CHECK( polynomial::findKnotSpan( knotVector, 12, 3, 0.1 ) == 3 );
    CHECK( polynomial::findKnotSpan( knotVector, 12, 3, 0.2 ) == 3 );
    CHECK( polynomial::findKnotSpan( knotVector, 12, 3, 0.5 ) == 4 );
    CHECK( polynomial::findKnotSpan( knotVector, 12, 3, 1.0 ) == 6 );
    CHECK( polynomial::findKnotSpan( knotVector, 12, 3, 1.3 ) == 9 );
    CHECK( polynomial::findKnotSpan( knotVector, 12, 3, 1.5 ) == 11 );
   
    for( const auto& [x, span, N, dN, ddN] : expected )
    {
        auto B0 = std::array<double, 4> { };
        auto B1 = std::array<double, 8> { };
        auto B2 = std::array<double, 12> { };

        polynomial::bspline( knotVector, 3, 0, span, x, B0 );
        polynomial::bspline( knotVector, 3, 1, span, x, B1 );
        polynomial::bspline( knotVector, 3, 2, span, x, B2 );

        for( size_t i = 0; i < 4; ++i )
        {
            CHECK( B0[i + 0] == Approx( N[i] ).epsilon( 1e-8 ).margin( 1e-8 ) );
            CHECK( B1[i + 0] == Approx( N[i] ).epsilon( 1e-8 ).margin( 1e-8 ) );
            CHECK( B2[i + 0] == Approx( N[i] ).epsilon( 1e-8 ).margin( 1e-8 ) );

            CHECK( B1[i + 4] == Approx( dN[i] ).epsilon( 1e-8 ).margin( 1e-8 ) );
            CHECK( B2[i + 4] == Approx( dN[i] ).epsilon( 1e-8 ).margin( 1e-8 ) );

            CHECK( B2[i + 8] == Approx( ddN[i] ).epsilon( 1e-8 ).margin( 1e-8 ) );
        }
    }

} // cubicBSpline_test

TEST_CASE( "findKnotSpan_test" )
{
    auto knotVector = std::array { 0.0, 0.0, 0.0, 0.0, 
                                   1.0, 
                                   4.0, 
                                   9.0, 9.0, 9.0, 9.0 };
    
    CHECK( polynomial::findKnotSpan( knotVector, 6, 3, -1.0 ) == 3 );
    CHECK( polynomial::findKnotSpan( knotVector, 6, 3, 0.0 ) == 3 );
    CHECK( polynomial::findKnotSpan( knotVector, 6, 3, 0.2 ) == 3 );
    CHECK( polynomial::findKnotSpan( knotVector, 6, 3, 1.1 ) == 4 );
    CHECK( polynomial::findKnotSpan( knotVector, 6, 3, 9.0 ) == 5 );
    CHECK( polynomial::findKnotSpan( knotVector, 6, 3, 9.1 ) == 5 );
}

TEST_CASE( "deBoor_test1" )
{
    auto knotVector = std::array { 0.0, 0.0, 0.0, 0.0, 
                                   1.0, 
                                   4.0, 
                                   9.0, 9.0, 9.0, 9.0 };

    auto controlPoints = CoordinateList<2>{ {  0.5, 0.5 },
                                            { 10.0, 1.0 },
                                            {  9.0, 4.0 },
                                            {  4.5, 7.5 },
                                            {  1.5, 6.0 },
                                            {  1.0, 1.0 } };

    auto expected = std::array 
    {
        std::tuple { 0.0, size_t { 3 }, controlPoints.front( ) },
        std::tuple { 1.0, size_t { 4 }, std::array { 9.4375,       2.4097222222 } },
        std::tuple { 1.1, size_t { 4 }, std::array { 9.3419010417, 2.6049366319 } },
        std::tuple { 2.0, size_t { 4 }, std::array { 8.3385416667, 4.1241319444 } },
        std::tuple { 3.0, size_t { 4 }, std::array { 7.0208333333, 5.3333333333 } },
        std::tuple { 4.0, size_t { 5 }, std::array { 5.640625,     6.0737847222 } },
        std::tuple { 5.0, size_t { 5 }, std::array { 4.336,        6.3577777778 } },
        std::tuple { 6.0, size_t { 5 }, std::array { 3.172375,     6.1009375    } },
        std::tuple { 7.0, size_t { 5 }, std::array { 2.197,        5.1947222222 } },
        std::tuple { 8.0, size_t { 5 }, std::array { 1.457125,     3.5305902778 } },
        std::tuple { 9.0, size_t { 5 }, controlPoints.back( ) }
    };
    
    auto n = controlPoints.size( );
    auto m = knotVector.size( );
    auto p = m - n - 1;

    auto bspline = interpolation::makeBSpline( controlPoints, knotVector );

    for( const auto& [t, ispan, xyz] : expected )
    {
        CHECK( polynomial::findKnotSpan( knotVector, n, p, t ) == ispan );

        auto P1 = polynomial::deBoor( knotVector, controlPoints, p, ispan, t );
        auto P2 = bspline( t );

        CHECK( spatial::distanceSquared( P1, xyz ) < 1e-20 );
        CHECK( spatial::distanceSquared( P2, xyz ) < 1e-20 );
    }
}

//TEST_CASE( "bspline_test2" )
//{
//    // from scipy.interpolate import BSpline
//    // eps = lambda v, i: (1.0 + 1e5* i * 2.23e-16) * v
//    // t =  [eps(v, i) for v, m in ((6.0, 4), (8.0, 2), (10.0, 4)) for i in range(m)]
//    // x = [6.1, 7.0, 7.7, 8.2, 9.4, 9.9]
//
//    auto x = std::array { 6.0, 8.0, 10.0 };
//    auto U = std::vector<double> { };
//
//    polynomial::openKnotVector( x, 3, 0, U );
//
//    auto N = std::array<double, 12> { };
//    
//    polynomial::bspline( U, 3, 2, 3, 6.2, N );
//
//    std::cout << N << std::endl;
//}

TEST_CASE( "deBoor_test2" )
{
    auto knotVector = std::array { 0.0, 0.0, 0.5, 1.0, 1.0 };
    auto controlPoints = CoordinateList<2> { { 2.0, 1.0 }, { 3.0, 3.0 }, { 0.5, 3.0 } };

    auto expectedCurve = CoordinateList<2>{ { 2.0, 1.0 },   // t = 0.0
                                            { 2.2, 1.4 },   // t = 0.1
                                            { 2.4, 1.8 },   // t = 0.2
                                            { 2.6, 2.2 },   // t = 0.3
                                            { 2.8, 2.6 },   // t = 0.4
                                            { 3.0, 3.0 },   // t = 0.5
                                            { 2.5, 3.0 },   // t = 0.6
                                            { 2.0, 3.0 },   // t = 0.7
                                            { 1.5, 3.0 },   // t = 0.8
                                            { 1.0, 3.0 },   // t = 0.9
                                            { 0.5, 3.0 } }; // t = 1.0

    auto n = controlPoints.size( );
    auto m = knotVector.size( );
    auto p = m - n - 1;

    for( size_t i = 0; i <= 10; ++i )
    {
        auto t = 0.1 * i;

        auto ispan = polynomial::findKnotSpan( knotVector, n, p, t );
        auto P = polynomial::deBoor( knotVector, controlPoints, p, ispan, t );

        CHECK( spatial::distance( P, expectedCurve[i] ) < 1e-10 );
    }
}

TEST_CASE( "interpolationLocalCoordinates_test" )
{
    // Define points to be interpolated
    auto points = CoordinateList<2> { { 0.0,   0.0   }, 
                                      { 15.0,  20.0  }, 
                                      { 171.0, 85.0  }, 
                                      { 307.0, 340.0 }, 
                                      { 907.0, 515.0 } };

    auto tvalues0 = interpolation::equidistantLocalCoordinates( points );
    auto tvalues1 = interpolation::centripetralLocalCoordinates( points );

    REQUIRE( tvalues0.size( ) == points.size( ) );
    REQUIRE( tvalues1.size( ) == points.size( ) );

    // Check parameter positions
    double d0 = 25.0 + 169.0 + 289.0 + 625.0;
    double d1 = 5.0 + 13.0 + 17.0 + 25.0;

    CHECK( tvalues0[0] == Approx( 0.0 ) );
    CHECK( tvalues0[1] == Approx( 25.0 / d0 ) );
    CHECK( tvalues0[2] == Approx( ( 25.0 + 169.0 ) / d0 ) );
    CHECK( tvalues0[3] == Approx( ( 25.0 + 169.0 + 289.0 ) / d0 ) );
    CHECK( tvalues0[4] == Approx( 1.0 ) );

    CHECK( tvalues1[0] == Approx( 0.0 ) );
    CHECK( tvalues1[1] == Approx( 5.0 / d1 ) );
    CHECK( tvalues1[2] == Approx( ( 5.0 + 13.0 ) / d1 ) );
    CHECK( tvalues1[3] == Approx( ( 5.0 + 13.0 + 17.0 ) / d1 ) );
    CHECK( tvalues1[4] == Approx( 1.0 ) );
}

TEST_CASE( "knotVectorUsingAveraging_test" )
{
    auto localCoordinates = std::vector { 0.0, 1.0 / 2.0, 2.0 / 3.0, 3.0 / 4.0, 1.0 };

    auto eps = 1e-10;

    auto knotVector2 = interpolation::averagedKnotVector( localCoordinates, 2 );
    auto knotVector3 = interpolation::averagedKnotVector( localCoordinates, 3 );
    auto knotVector4 = interpolation::averagedKnotVector( localCoordinates, 4 );

    REQUIRE( knotVector2.size( ) == localCoordinates.size( ) + 3 );
    REQUIRE( knotVector3.size( ) == localCoordinates.size( ) + 4 );
    REQUIRE( knotVector4.size( ) == localCoordinates.size( ) + 5 );

    auto expected2 = std::array { 0.0, 0.0, 0.0, 7.0 / 12.0, 17.0 / 24.0, 1.0, 1.0, 1.0 };
    auto expected3 = std::array { 0.0, 0.0, 0.0, 0.0, 23.0 / 36.0, 1.0, 1.0, 1.0, 1.0 };
    auto expected4 = std::array { 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0 };

    CHECK( utilities::floatingPointEqual( knotVector2.begin( ), knotVector2.end( ), expected2.begin( ), eps ) );
    CHECK( utilities::floatingPointEqual( knotVector3.begin( ), knotVector3.end( ), expected3.begin( ), eps ) );
    CHECK( utilities::floatingPointEqual( knotVector4.begin( ), knotVector4.end( ), expected4.begin( ), eps ) );
}

TEST_CASE( "computeControlPoints_test" )
{
    auto xyzValues = CoordinateList<2> { { 0.0,   0.0   }, 
                                         { 15.0,  20.0  }, 
                                         { 171.0, 85.0  }, 
                                         { 307.0, 340.0 }, 
                                         { 907.0, 515.0 } };

    auto d = 5.0 + 13.0 + 17.0 + 25.0;
    auto tvalues = interpolation::centripetralLocalCoordinates( xyzValues );

    // Compute and check knot vectors
    auto knotVector1 = interpolation::averagedKnotVector( tvalues, 1 );
    auto knotVector3 = interpolation::averagedKnotVector( tvalues, 3 );
    auto knotVector4 = interpolation::averagedKnotVector( tvalues, 4 );
    
    auto expectedKnotVector1 = std::array { 0.0, 0.0, 
                                            5.0 / d, 
                                            ( 5.0 + 13.0 ) / d, 
                                            ( 5.0 + 13.0 + 17.0 ) / d, 
                                            1.0, 1.0 };
    
    auto expectedKnotVector3 = std::array { 0.0, 0.0, 0.0, 0.0,
                                            ( 3 * 5.0 + 2 * 13.0 + 17.0 ) / 3.0 / d,
                                            1.0, 1.0, 1.0, 1.0 };

    auto expectedKnotVector4 = std::array { 0.0, 0.0, 0.0, 0.0, 0.0,
                                            1.0, 1.0, 1.0, 1.0, 1.0 };
    
    REQUIRE( knotVector1.size( ) == expectedKnotVector1.size( ) );
    REQUIRE( knotVector3.size( ) == expectedKnotVector3.size( ) );
    REQUIRE( knotVector4.size( ) == expectedKnotVector4.size( ) );

    REQUIRE( utilities::floatingPointEqual( knotVector1.begin( ), 
        knotVector1.end( ), expectedKnotVector1.begin( ), 1e-10 ) );

    REQUIRE( utilities::floatingPointEqual( knotVector3.begin( ),
        knotVector3.end( ), expectedKnotVector3.begin( ), 1e-10 ) );

    REQUIRE( utilities::floatingPointEqual( knotVector4.begin( ),
        knotVector4.end( ), expectedKnotVector4.begin( ), 1e-10 ) );

    // Compute and check control points
    auto controlPoints1 = interpolation::computeControlPoints( xyzValues, tvalues, knotVector1 );
    auto controlPoints3 = interpolation::computeControlPoints( xyzValues, tvalues, knotVector3 );
    auto controlPoints4 = interpolation::computeControlPoints( xyzValues, tvalues, knotVector4 );
   
    REQUIRE( controlPoints1.size( ) == xyzValues.size( ) );
    REQUIRE( controlPoints3.size( ) == xyzValues.size( ) );
    REQUIRE( controlPoints4.size( ) == xyzValues.size( ) );

    auto expectedControlPoints1 = xyzValues;

    auto expectedControlPoints3 = CoordinateList<2> { {   0.0,       0.0    },
                                                      { -12.5687,   31.9598 },
                                                      { 383.886,    30.3872 },
                                                      { 236.859,   672.775  },
                                                      { 907.0,     515.0    } };
    
    auto expectedControlPoints4 = CoordinateList<2> { {    0.0,            0.0          },
                                                      {  -38.5422077922,  80.2976190476 },
                                                      {  718.2705627706, -71.8650793651 },
                                                      { -139.3798701299, 883.5119047619 },
                                                      {  907.0,          515.0          } };

    for( size_t ipoint = 0; ipoint < xyzValues.size( ); ++ipoint )
    {
        CHECK( spatial::distance( controlPoints1[ipoint], expectedControlPoints1[ipoint] ) < 1e-10);
        CHECK( spatial::distance( controlPoints3[ipoint], expectedControlPoints3[ipoint] ) < 5e-4 );
        CHECK( spatial::distance( controlPoints4[ipoint], expectedControlPoints4[ipoint] ) < 1e-10 );
    }

} // computeControlPoints_test

TEST_CASE( "openKnotVector_test" )
{
    auto target = std::vector { 23.0, 32.0, 45.0 };
    auto x = std::array { 2.0, 3.0, 5.0, 5.5 };

    polynomial::openKnotVector( x, 5, 3, target );

    auto expected = std::vector
    {
        23.0, 32.0, 45.0,
        2.0, 2.0, 2.0, 2.0, 2.0, 2.0,
        3.0, 3.0,
        5.0, 5.0,
        5.5, 5.5, 5.5, 5.5, 5.5, 5.5
    };

    CHECK( target == expected );
}

//TEST_CASE( "makeBSplineWithDerivative_test" )
//{
//    std::vector<double> coordinates{ 100.0, 200.0, 300.0, 500.0, 1000.0 };
//    std::vector<double> values{ 0.03, 0.03, 0.03, 0.05, 0.11 };
//
//    auto interpolant = interpolation::makeBSplineInterpolation( coordinates, values );
//
//    std::cout << "[";
//    for (double T = 0.0; T <= 1500.0; T += 1.0 )
//    {
//        std::cout << interpolant(T)[0] << ", ";
//    }
//    std::cout << "]" << std::endl;
//
//} // makeBSplineWithDerivative


} // mlhp
