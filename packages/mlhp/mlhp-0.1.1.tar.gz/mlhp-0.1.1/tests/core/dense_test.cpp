// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/dense.hpp"
#include "mlhp/core/compilermacros.hpp"
#include "mlhp/core/memory.hpp"
#include "mlhp/core/spatial.hpp"

#include<array>

namespace mlhp
{
namespace linalg
{

TEST_CASE( "lu_test" )
{
    // -------------------- test lu ----------------------

    auto M = std::array
    {
        -6.57236887,  0.84564944, -1.02177673,  3.75118371,  2.67678544,
         9.64342431, -1.2257033,   4.58716922, -5.83018145, -7.51428046,
         5.68716742,  2.04974341,  0.10133382, -9.21934916,  9.65478781,
        -9.0823581,   6.64997405, -8.45984082, -9.00872702, -2.79864918,
        -8.70517483,  6.64140389, -9.14154383,  1.50739727,  5.46489685 
    };

    auto P = std::array<size_t, 5> { };

   auto luResult = luFactor( M, P );

    auto expectedLU = std::array 
    {  
        9.64342430e+00, -1.22570330e+00,  4.58716921e+00, -5.83018145e+00, -7.51428045e+00, // LU(0, j)
       -9.02705776e-01,  5.53495443e+00, -5.00067967e+00, -3.75554119e+00, -1.31828751e+00, // LU(1, j)
       -6.81538907e-01,  1.85818261e-03,  2.11384974e+00, -2.15333300e-01, -2.44203943e+00, // LU(2, j)
       -9.41818778e-01,  9.92886884e-01,  3.90543631e-01, -1.06867767e+01, -7.61310628e+00, // LU(3, j)
        5.89745637e-01,  5.00924916e-01, -4.68170311e-02,  3.65859817e-01,  1.74176656e+01, // LU(4, j)
    };

    size_t expectedP[] = { 1, 4, 0, 3, 2 };

    for( size_t i = 0; i < 5; ++i )
    {
        CHECK( P[i] == expectedP[i] );

        for( size_t j = 0; j < 5; ++j )
        {
            CHECK( M[i * 5 + j] == Approx( expectedLU[i * 5 + j] )
                   .epsilon( 1e-7 ).margin( 1e-7 ) );
        }
    }

    CHECK( luDeterminant( M, P, luResult ) == Approx( 21001.780993001175 ).epsilon( 1e-10 ) );

    // --------------- test substitution -----------------

    auto rhs = std::array { -5.73507895,  6.63643545,  3.95315262, -0.00832055,  0.47981328 };
    auto solution = std::array<double, 5> { };

    CHECK_NOTHROW( luSubstitute( expectedLU, expectedP, rhs, solution ) );

    double expectedSolution[] =
    {
        1.04182070e+00,  4.82824712e-01, -7.91224906e-01,  1.10071363e-01, -1.93329855e-01
    };

    for( size_t i = 0; i < 5; ++i )
    {
        CHECK( solution[i] == Approx( expectedSolution[i] ).epsilon( 1e-8 ) );
    }

    // ----------------- test inverse --------------------

    auto inverse = std::array<double, 25> { };

    CHECK_NOTHROW( luInvert( expectedLU, expectedP, inverse ) );

    double expectedInverse[] =
    {
        -1.47601385e-01,  2.57481231e-02, -4.20978210e-03, -5.96623725e-02,  8.45846450e-02,
         4.63548835e-01,  4.30408775e-01,  4.20831567e-02, -8.74995005e-02,  2.45605207e-01,
         4.88585129e-01,  2.65933738e-01,  6.21603209e-02, -3.22741026e-02, -1.00033493e-06,
         2.87857519e-02,  5.86061643e-02, -4.09001788e-02, -7.86098520e-02,  9.84851204e-02,
         1.08913134e-02, -5.33723617e-02,  5.74129749e-02, -2.10051005e-02, -7.92413881e-03
    };

    for( size_t i = 0; i < 5; ++i )
    {
        for( size_t j = 0; j < 5; ++j )
        {
            CHECK( inverse[i * 5 + j] == Approx( expectedInverse[i * 5 + j] )
                   .epsilon( 2e-9 ).margin( 2e-9 ) );
        }
    }
}

TEST_CASE( "lu_test2" )
{
    auto J = std::array { 0.0, 0.02, 0.02, 0.0 };
    auto P = std::array<size_t, 2> { };

    auto luResult = luFactor( J, P );

    CHECK( linalg::luDeterminant( J, P, luResult ) == Approx( -0.0004 ).epsilon( 1e-10 ) );

    auto r = std::array { 4.2, 7.4 };
    auto x = std::array<double, 2> { };

    luSubstitute( J, P, r, x );

    CHECK( x[0] == Approx( 370.0 ).epsilon( 1e-8 ) );
    CHECK( x[1] == Approx( 210.0 ).epsilon( 1e-8 ) );
}

TEST_CASE( "lu_test3" )
{
    auto A = std::array
    {
        40.0           , 0.0            , -4.3643578047199, 0.0            , 0.0            , -4.3643578047199,
        0.0            , 9.5238095238095,  0.0            , 0.0            , 0.0            ,  0.0,
       -4.3643578047199, 0.0            ,  4.4444444444444, 0.0            , 0.0            ,  0.4761904761905,
        0.0            , 0.0            ,  0.0            , 9.5238095238095, 0.0            ,  0.0,
        0.0            , 0.0            ,  0.0            , 0.0            , 2.2675736961451,  0.0,
       -4.3643578047199, 0.0            ,  0.4761904761905, 0.0            , 0.0            ,  4.4444444444444
    };

    auto p = std::array<size_t, 6> { };
    auto inv = std::array<double, 6 * 6> { };

    auto expectedInv = std::array<double, 6 * 6>
    {
        0.031          , 0.0            , 0.0274954541697 , 0.0            ,  0.0           , 0.02749545416970,
        0.0            , 0.105          , 0.0             , 0.0            ,  0.0           , 0.0,
        0.0274954541697, 0.0            , 0.252           , 0.0            ,  0.0           , 0.0,
        0.0            , 0.0            , 0.0             , 0.105          ,  0.0           , 0.0,
        0.0            , 0.0            , 0.0             , 0.0            ,  0.441         , 0.0,
        0.0274954541697, 0.0            , 0.0             , 0.0            ,  0.0           , 0.2520
    };

    auto luResult = linalg::luFactor( A, p );

    linalg::luInvert( A, p, inv );

    CHECK( linalg::luDeterminant( A, p, luResult ) == Approx( 129551.28413829784 ).epsilon( 1e-10 ) );
    CHECK( spatial::distance( inv, expectedInv ) < 1e-10 );
}

TEST_CASE( "lu_singular_test1" )
{
    auto A = std::vector
    {
         -2.990141306631388,  11.638867495117692,   3.066635636610189, // Row 0
         -6.062214763371493,   7.976688120394939,  -5.943737494309515, // _____
         -5.454481551080378,  10.356670965926167,   2.415489616086328, // Row 1
         -6.713248216317353,   7.638850188248097,  -2.927840213785585, // _____
         -7.923570519607564,  16.100289444870604,   1.463376344338631, // Row 2
        -10.55596992010815 ,   8.349311395473327,  -0.923483585253721, // _____
        -11.69439164919719 ,   7.425431549675658,   6.339771609165389, // Row 3
         -7.482533314473259,  16.16195285026443 ,  -5.715819240299324, // _____
         -6.187513720942986,   6.856562983735548,   3.853965150908406, // Row 4
         -5.091547368929338,  10.898722688342163,  -5.073361362963714, // _____
         -7.670169250568312,  14.012239988305618,  -1.482258580801285, // Row 5
         -9.709432787114622,   6.454818632606449,   2.933904622497696, // _____
    };

    auto p = std::array<size_t, 6> { };

    // Default dolerance large enough for luFactor to abort due to zero column
    auto LU = A;
    auto luResult = linalg::luFactor( LU, p );
    auto det = linalg::luDeterminant( LU, p, luResult );

    CHECK( std::abs( det ) < 1e-20 );

    // Explicit tolerance small enough for luFactor to finish normally
    LU = A;
    luResult = linalg::luFactor( LU, p, 1e-30 );
    det = linalg::luDeterminant( LU, p, luResult );

    CHECK( std::abs( det ) < 1e-20 );

    CHECK( p == std::array<size_t, 6> { 3, 2, 0, 5, 1, 4 } ); 

    // Check LU error || A[p, :] - L @ U || / || A ||
    auto L = LU, U = LU;

    for( size_t i = 0; i < 6; ++i )
    {
        for( size_t j = 0; j < 6; ++j )
        {
            if( j >= i )
            {
                L[i * 6 + j] = i == j;
            }
            else
            {
                U[i * 6 + j] = 0.0;
            }
        }
    }

    linalg::mmproduct( L.data( ), U.data( ), LU.data( ), 6 );

    auto anorm2 = 0.0;
    auto enorm2 = 0.0;

    for( size_t i = 0; i < 6; ++i )
    {
        for( size_t j = 0; j < 6; ++j )
        {
            anorm2 += std::pow( A[i * 6 + j], 2 );
            enorm2 += std::pow( A[p[i] * 6 + j] - LU[i * 6 + j], 2 );
        }
    }

    REQUIRE( enorm2 != 0.0 );

    CHECK( std::sqrt( enorm2 / anorm2 ) < 1e-14 );
}

TEST_CASE( "lu_singular_test2" )
{
    auto A = std::array { 1.0, 1.0, 1.0, 1.0 };
    auto p = std::array<size_t, 2> { };

    CHECK( linalg::luFactor( A, p ) == -1 );
    CHECK( linalg::luDeterminant( A, p, -1 ) == 0.0 );
}

TEST_CASE( "lu_negative_test" )
{

}

TEST_CASE( "elementLhs_test" )
{
    auto allsize = size_t { 13 };

    auto offset0 = size_t { 3 };
    auto size0 = size_t { 4 };
    
    auto offset1 = size_t { 5 };
    auto size1 = size_t { 3 };

    // Unsymmetric
    {
        auto target = memory::AlignedVector<double>( linalg::denseMatrixStorageSize<linalg::UnsymmetricDenseMatrix>( allsize ), 1.3 );
        auto expr = []( size_t i, size_t j ) { return i * 100.0 + j + 5.1; };

        linalg::elementLhs<linalg::UnsymmetricDenseMatrix>( target.data( ), allsize, offset0, size0, offset1, size1, expr );

        auto index = size_t { 0 };
        auto allpadded = memory::paddedLength<double>( allsize );

        for( size_t i = 0; i < allsize; ++i )
        {
            for( size_t j = 0; j < allpadded; ++j )
            {
                auto inblock = i >= offset0 && i < offset0 + size0 && j >= offset1 && j < offset1 + size1;
                auto expected = ( inblock ? ( i - offset0 ) * 100.0 + ( j - offset1 ) + 5.1 : 0.0 ) + 1.3;

                CHECK( target[index] == Approx( expected ) );

                index += 1;
            }
        }

        CHECK( index == target.size( ) );
    }

    // Symmetric
    {
        auto target = memory::AlignedVector<double>( linalg::denseMatrixStorageSize<linalg::SymmetricDenseMatrix>( allsize ), 1.3 );
        auto expr = []( size_t i, size_t j ) { return i + j + 5.1; };

        linalg::elementLhs<linalg::SymmetricDenseMatrix>( target.data( ), allsize, offset0, size0, offset1, size1, expr );

        auto index = size_t { 0 };

        for( size_t i = 0; i < allsize; ++i )
        {
            for( size_t j = 0; j < memory::paddedLength<double>( i + 1 ); ++j )
            {
                auto inblock = i >= offset0 && i < offset0 + size0 && j >= offset1 && j < offset1 + size1;
                auto expected = ( inblock ? ( i - offset0 ) + ( j - offset1 ) + 5.1 : 0.0 ) + 1.3;
                    
                CHECK( target[index] == Approx( expected ) );

                index += 1;
            }
        }

        CHECK( index == target.size( ) );
    }
}

TEST_CASE( "householder_test" )
{
    SECTION( "1" )
    {
        auto x = std::array { 4.0, -2.0, 9.0, 0.5 };
        auto v = x;

        auto [alpha, beta] = linalg::householderVector( v, v );
        auto r = x - beta * v * spatial::dot( x, v );

        auto expected = std::array { alpha, 0.0, 0.0, 0.0 };

        CHECK( std::abs( alpha ) == Approx( spatial::norm( x ) ).epsilon( 1e-14 ) );
        CHECK( spatial::distance( r, expected ) < 1e-14 );

        auto P = std::array<double, 16> { };

        linalg::householderMatrix( x, P );

        r = linalg::mvproduct<4, 4>( P, x );

        CHECK( spatial::distance( r, expected ) < 1e-14 );
    }

    SECTION( "2" )
    {
        auto x = std::array { 4.0, 0.0 };
        auto v = x;

        auto [alpha, beta] = linalg::householderVector( v, v );

        CHECK( spatial::distance( x - beta * v * spatial::dot( x, v ), { alpha, 0.0 } ) < 1e-10 );
        CHECK( std::abs( alpha ) == Approx( 4.0 ).epsilon( 1e-10 ) );

        x[0] = -0.1;

        std::tie( alpha, beta ) = linalg::householderVector( x, v );

        CHECK( spatial::distance( x - beta * v * spatial::dot( x, v ), { alpha, 0.0 } ) < 1e-10 );
        CHECK( std::abs( alpha ) == Approx( 0.1 ).epsilon( 1e-10 ) );
    }

    SECTION( "3" )
    {
        auto x = std::array { -1e-10, 5.0, -3.0 };
        auto v = x;

        auto [alpha, beta] = linalg::householderVector( v, v );

        CHECK( spatial::distance( x - beta * v * spatial::dot( x, v ), { alpha, 0.0 } ) < 1e-10 );
        CHECK( std::abs( alpha ) == Approx( spatial::norm( x ) ).epsilon( 1e-10 ) );

        auto u = v * std::sqrt( beta / 2.0 );

        CHECK( spatial::distance( x - 2.0 * u * spatial::dot( x, u ), { alpha, 0.0 } ) < 1e-10 );
    }
}

TEST_CASE( "qr_test" )
{
    auto M = std::array
    {
        0.18, -8.96, -0.65, -6.35,
       -3.97,  0.94, -6.15,  4.61,
       -9.05, -2.54,  4.74,  4.64,
       -9.49, -1.36,  7.41, -7.18,
       -2.77, -1.75, -9.13,  1.38,
       -6.06,  9.11, -5.52,  9.14
    };

    static constexpr auto m = size_t { 6 }, n = size_t { 4 };

    auto Q = std::array<double, m * m> { };
    auto R = std::array<double, m * n> { };

    linalg::qr( M, Q, R, { m, n }, false );

    // Test if R is triangular
    for( size_t i = 1; i < m; ++i )
    {
        for( size_t j = 0; j < std::min( i, n ); ++j )
        {
            CHECK( std::abs( R[i * n + j] ) < 1e-14 );
        }
    }

    // Check if columns of Q are orthonormal
    for( size_t icol = 0; icol < m; ++icol )
    {
        for( size_t jcol = 0; jcol <= icol; ++jcol )
        {
            auto dot = 0.0;

            for( size_t irow = 0; irow < m; ++irow )
            {
                dot += Q[irow * m + icol] * Q[irow * m + jcol];
            }

            CHECK( std::abs( dot - ( icol == jcol ) ) < 1e-12 );
        }
    }

    // Check if we get M back from QR
    auto recoveredM = std::array<double, m * n> { };

    linalg::mmproduct( Q.data( ), R.data( ), recoveredM.data( ), m, m, n );

    CHECK( spatial::distance( M, recoveredM ) < 1e-12 );

    // =========== Same again for reduced form ===========
    std::fill( Q.begin( ), Q.end( ), 0.0 );
    std::fill( R.begin( ), R.end( ), 0.0 );
    std::fill( recoveredM.begin( ), recoveredM.end( ), 0.0 );

    linalg::qr( M, Q, R, { m, n }, true );

    // Test if R is triangular
    for( size_t i = 1; i < n; ++i )
    {
        for( size_t j = 0; j < i; ++j )
        {
            CHECK( std::abs( R[i * n + j] ) < 1e-14 );
        }
    }

    // Check if columns of Q are orthonormal
    for( size_t icol = 0; icol < n; ++icol )
    {
        for( size_t jcol = 0; jcol <= icol; ++jcol )
        {
            auto dot = 0.0;

            for( size_t irow = 0; irow < m; ++irow )
            {
                dot += Q[irow * n + icol] * Q[irow * n + jcol];
            }

            CHECK( std::abs( dot - ( icol == jcol ) ) < 1e-12 );
        }
    }

    // Check if we get M back from QR
    linalg::mmproduct( Q.data( ), R.data( ), recoveredM.data( ), m, n, n );

    CHECK( spatial::distance( M, recoveredM ) < 1e-12 );
}

TEST_CASE( "norm_test" )
{
    auto data = std::array { 5.0, -2.0, 0.0, 3.2 };

    CHECK( linalg::norm( data ) == Approx( std::sqrt( 39.24 ) ).epsilon( 1e-10 ) );
}

TEST_CASE( "issymmetric_test" )
{
    auto data1 = std::array { 5.0, -2.0,  0.0, 
                              3.2,  0.7,  5.1,
                              9.1, -4.3,  3.7 };
                                          
    auto data2 = std::array { 5.0, -2.0,  0.0, 
                             -2.0,  0.7,  5.1,
                              0.0,  5.1,  3.7 };

    auto data3 = std::array { 0.0, 0.0,
                              0.0, 0.0 };

    auto data4 = std::array { 0.0, 1e-20,
                              1e-20, 0.0 };

    auto data5 = std::array { 0.0, -1e-20,
                              1e-20, 0.0 };

    CHECK( linalg::issymmetric( data1, 3 ) == false );
    CHECK( linalg::issymmetric( data2, 3 ) == true );
    CHECK( linalg::issymmetric( data3, 2 ) == true );
    CHECK( linalg::issymmetric( data4, 2 ) == true );
    CHECK( linalg::issymmetric( data5, 2 ) == false );
}

TEST_CASE( "hessenberg_form_test" )
{
    // https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.hessenberg.html

    static constexpr size_t n = 6;

    auto A = std::array
    {  
       -9.39,  2.51,  5.41, -0.23,  7.6 , -2.4 ,
        3.23, -5.47,  4.74,  7.04, -7.32, -4.57,
       -6.86,  6.09,  9.38,  5.83,  8.63,  4.99,
       -1.51,  9.02,  7.86, -4.62, -2.89,  1.67,
        4.33,  7.53, -4.21, -0.22,  2.33,  5.12,
       -1.95,  0.53,  3.58, -9.96, -9.08,  4.02,
    };

    auto Q = std::array<double, n * n> { };
    auto tmp = std::array<double, n> { };

    linalg::hessenberg( A, tmp, Q );

    auto expectedH = std::array
    {
        -9.39            ,  -0.98421102785897,  1.41785053586788, // Row 0
        -6.14455824113947,  -6.86273392750086,  3.36294745307650, // _____
        -9.07325740845040,   3.61246262329333, -3.46724841477661, // Row 1
        -6.59677816414984,  -5.40860018141443,  7.87219986230652, // _____
         0.0             , -12.85680085723422, -1.15708820687125, // Row 2
        -5.89120384831946,   3.08495431185226,  4.35144792556196, // _____
         0.0             ,   0.0             , 12.21708200631897, // Row 3
         0.51217144678394,   4.46861989599124, -8.61248011779762, // _____
         0.0             ,   0.0             ,  0.0             , // Row 4
        14.96274020275835,   1.37443213482733,  6.66008528133276, // _____
         0.0             ,   0.0             ,  0.0             , // Row 5
         0.0             ,   4.73480539308627,  1.29802200196665  // _____
    };

    auto expectedQ = std::array
    {
         1.0             ,   0.0             ,  0.0             , // Row 0
         0.0             ,   0.0             ,  0.0             , // _____
         0.0             ,  -0.35599122284261, -0.81667168706311, // Row 1
         0.00330949504086,  -0.44707092724501,  0.08021370246651, // _____
         0.0             ,   0.75606804603724, -0.00909111489433, // Row 2
        -0.25309875273312,  -0.53837399711828,  0.27271399300959, // _____
         0.0             ,   0.16642314132890, -0.24109252311440, // Row 3
        -0.62644135429132,   0.17763233135141, -0.70013978448655, // _____
         0.0             ,  -0.47722662381068,  0.32573200959968, // Row 4
        -0.71049774404572,  -0.15369056691080,  0.37111396200764, // _____
         0.0             ,   0.21491730171612, -0.41077702029199, // Row 5
        -0.19670855077275,   0.67461617957211,  0.53969579332760  // _____
    };

    CHECK( spatial::distance( A, expectedH ) < 1e-12 );
    CHECK( spatial::distance( Q, expectedQ ) < 1e-12 );
}

TEST_CASE( "givens_test" )
{
    CHECK( spatial::distance<3>( linalg::givensr( 2.0, 0.0 ), { 1.0, 0.0, 2.0 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( -2.0, 0.0 ), { -1.0, 0.0, 2.0 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( 0.0, 0.5 ), { 0.0, -1.0, 0.5 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( 0.0, -0.5 ), { 0.0, 1.0, 0.5 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( 4.0, 3.0 ), { 0.8, -0.6, 5.0 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( 3.0, 4.0 ), { 0.6, -0.8, 5.0 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( 4.0, -3.0 ), { 0.8, 0.6, 5.0 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( 3.0, -4.0 ), { 0.6, 0.8, 5.0 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( -4.0, 3.0 ), { -0.8, -0.6, 5.0 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( -3.0, 4.0 ), { -0.6, -0.8, 5.0 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( -4.0, -3.0 ), { -0.8, 0.6, 5.0 } ) < 1e-10 );
    CHECK( spatial::distance<3>( linalg::givensr( -3.0, -4.0 ), { -0.6, 0.8, 5.0 } ) < 1e-10 );
}

MLHP_PURE
auto sameEigenvector( std::span<const double> computed,
                      std::span<const double> expected,
                      double tolerance = 1e-10 )
{
    if( computed.size( ) != expected.size( ) )
    {
        return false;
    }

    if( computed.empty( ) )
    {
        return true;
    }

    auto pred = []( auto v1, auto v2 ) { return std::abs( v1 ) < std::abs( v2 ); } ;
    auto it2 = std::max_element( expected.begin( ), expected.end( ), pred );
    auto it1 = computed.begin( ) + std::distance( expected.begin( ), it2 );
    auto ratio = ( *it1 ) / ( *it2 );

    if( std::abs( std::abs( ratio ) - 1.0 ) > tolerance )
    {
        return false;
    }

    for( size_t i = 0; i < computed.size( ); ++i )
    {
        if( std::abs( computed[i] - ratio * expected[i] ) > tolerance )
        {
            return false;
        }
    }

    return true;
}

auto eigspans( std::span<const double> values, size_t size )
{
    return [=]( size_t i )
    {
        return values.subspan( size * i, size );
    };
}

TEST_CASE( "eigh2D_test" )
{
    auto A = std::array { 3.166822207070386419, 2.3999013387040122325,
                          2.3999013387040122325, 3.7525258034586794764 };

    auto [l1, l2] = eigh2D( A );
    auto [v1, v2] = eigh2Dv( A, { l1, l2 } );

    if( l1 > l2 )
    {
        std::swap( l1, l2 );
        std::swap( v1, v2 );
    }

    CHECK( l1 == Approx( 1.0419708367140892 ).epsilon( 1e-10 ) );
    CHECK( l2 == Approx( 5.877377173814977 ).epsilon( 1e-10 ) );

    CHECK( sameEigenvector( v1, std::array { -0.7487082552320004,  0.6628996519439829 } ) );
    CHECK( sameEigenvector( v2, std::array { -0.6628996519439829, -0.7487082552320004 } ) );
}

TEST_CASE( "eigh_test_1x1" )
{
    auto A = std::array { 7.0 };
    auto tmp = std::array { 3.0 };
    auto lambda = std::array { -2.0 };

    eigh( A, lambda, tmp );

    CHECK( lambda[0] == Approx( 7.0 ).epsilon( 1e-10 ) );
    CHECK( A[0] == Approx( 1.0 ).epsilon( 1e-10 ) );

    eigh( std::span<double> { }, std::span<double> { }, std::span<double> { } );
}

TEST_CASE( "eigh_test_2x2" )
{
    auto A = std::array { 3.166822207070386419, 2.3999013387040122325,
                          2.3999013387040122325, 3.7525258034586794764 };

    auto lambda = std::array<double, 2> { };
    auto tmp = std::array<double, 2> { };

    eigh( A, lambda, tmp );

    linalg::sorteig( lambda, A );

    auto eigv = eigspans( A, 2 );

    CHECK( lambda[0] == Approx( 1.0419708367140892 ).epsilon( 1e-10 ) );
    CHECK( lambda[1] == Approx( 5.877377173814977 ).epsilon( 1e-10 ) );

    CHECK( sameEigenvector( eigv( 0 ), std::array { -0.7487082552320004,  0.6628996519439829 } ) );
    CHECK( sameEigenvector( eigv( 1 ), std::array { -0.6628996519439829, -0.7487082552320004 } ) );
}

TEST_CASE( "eigh_test_3x3" )
{
    auto A = std::array { 4.0, 2.0, 1.0,
                          2.0, 5.0, 3.0,
                          1.0, 3.0, 8.0 };

    auto lambda = std::array<double, 3> { };
    auto tmp = std::array<double, 3> { };

    eigh( A, lambda, tmp );

    linalg::sorteig( lambda, A );

    auto eigv = eigspans( A, 3 );

    CHECK( lambda[0] == Approx( 2.1470277462656777 ).epsilon( 1e-10 ) );
    CHECK( lambda[1] == Approx( 4.419421156529432 ).epsilon( 1e-10 ) );
    CHECK( lambda[2] == Approx( 10.433551097204884 ).epsilon( 1e-10 ) );

    auto expectedVectors = std::array
    {
        std::array { 0.6393981541260892, -0.7230838083654667, 0.2613805780463474 },
        std::array { 0.7116431513878535, 0.42785397491318583, -0.5572297562350306 },
        std::array { 0.29109109499075075, 0.5423013758332903 , 0.788146681897733 },
    };

    CHECK( sameEigenvector( eigv( 0 ), expectedVectors[0] ) );
    CHECK( sameEigenvector( eigv( 1 ), expectedVectors[1] ) );
    CHECK( sameEigenvector( eigv( 2 ), expectedVectors[2] ) );
}

TEST_CASE( "eigh_test_4x4" )
{
    auto A = std::array
    {
        3.0, 2.0, 0.0, 0.0,
        2.0, 4.0, 1.0, 0.5,
        0.0, 1.0, 2.0, 0.0,
        0.0, 0.5, 0.0, 5.0
    };

    auto tmp = std::array<double, 4> { };
    auto lambda = std::array<double, 4> { };

    eigh( A, lambda, tmp );

    linalg::sorteig( lambda, A, true, false );

    auto eigv = eigspans( A, 4 );

    auto expectedValues = std::array
    {
        5.907311414745722, 4.8497289633736775, 2.2638999524580585, 0.9790596694225424
    };

    auto expectedVectors = std::array
    {
        std::array { 0.506808335423663, 0.7367248293327473, 0.18855032300533725, 0.4059933653205589 },
        std::array { 0.2957776221931002, 0.27355421724418694, 0.09599306487040013, -0.9102027356224011 },
        std::array { 0.5693359811937734, -0.2095441214120374, -0.7940286440382738, 0.038292481592602456 },
        std::array { 0.575775520383608, -0.5818039852512282, 0.5698707043164346, 0.07234675690495429 }
    };

    for( size_t i = 0; i < 4; ++i )
    {
        CHECK( lambda[i] == Approx( expectedValues[i] ).epsilon( 1e-10 ) );
        CHECK( sameEigenvector( eigv( i ), expectedVectors[i] ) );
    }
}

TEST_CASE( "eigh_test_6x6" )
{
    auto A = std::array
    {
        12.84,  9.27,  1.42, -1.34,  1.36, 15.11,
        9.27,  13.52,  5.76,  0.48,  5.49, 10.51,
        1.42,   5.76,  5.87,  2.51,  4.52,  2.75,
        -1.34,  0.48,  2.51,  1.7 ,  1.79,  0.0,
        1.36,   5.49,  4.52,  1.79,  4.12,  2.5,
        15.11, 10.51,  2.75,  0.0 ,  2.5 , 18.26
    };

    auto A1 = A, A2 = A;

    auto tmp = std::array<double, 6> { };
    auto lambda = std::array<double, 6> { };

    linalg::eigh( A1, lambda, tmp );
    linalg::sorteig( lambda, A1 );

    auto eigv = eigspans( A1, 6 );

    auto expectedValues = std::array 
    { 
        -0.4347534490118, 0.1158908569549,  0.3781762338777, 
         3.187234568459, 12.52530202276,   40.53814976696 
    };
        
    auto expectedVectors = std::array<std::array<double, 6>, 6>
    {
        std::array {  0.6533470179733, -0.0503140800289, -0.1656049391381, 
                      0.547730244343,   0.0815838723439, -0.4863299525987 },
        std::array {  0.3186161136565, -0.4181552209759,  0.1873310296664,
                     -0.5677312390249,  0.5903952292946, -0.1328600093125 },
        std::array { -0.2543651511998,  0.0522980701141, -0.686950044756 ,
                      0.1887029165317,  0.6194749923278,  0.2032359734399 },
        std::array { -0.0764014735967, -0.6395869839358,  0.3293860114103,
                      0.5180505198655,  0.0828645421129,  0.4487240653529 },
        std::array { -0.3426210737909,  0.3988985184701,  0.5706465757911,
                      0.2713712032812,  0.4775244708483, -0.3101311127014 },
        std::array { -0.5326287925991, -0.5016852382979, -0.1773388465398,
                     -0.006734824157 , -0.1616543419815, -0.6379591995876 }
    };

    for( size_t i = 0; i < 6; ++i )
    {
        CHECK( lambda[i] == Approx( expectedValues[i] ).epsilon( 1e-10 ) );
        CHECK( sameEigenvector( eigv( i ), expectedVectors[i], 1e-8 ) );
    }

    // Check sorted by absolute value
    eigh( A2, lambda, tmp );

    sorteig( lambda, true, true );

    auto absordering = std::array<size_t, 6> { 1, 2, 0, 3, 4, 5 };

    for( size_t i = 0; i < 6; ++i )
    {
        CHECK( lambda[i] == Approx( expectedValues[absordering[i]] ).epsilon( 1e-10 ) );
    }
}

TEST_CASE( "eig_test1" )
{
    auto A = std::array
    {
        4.0, 1.0, 0.0,
        2.0, 6.0, 2.0,
        1.0, 3.0, 7.0
    };

    auto lambda = std::array<double, 3> { };
    auto vectors = std::array<double, 9> { };
    auto tmp = std::array<double, 3> { };

    linalg::eig( A, lambda, tmp, vectors );
    linalg::sorteig( lambda, vectors );

    auto expectedVectors = std::array<std::array<double, 3>, 3>
    {
        std::array { 0.6666666666667, -0.6666666666667,  0.3333333333333 },
        std::array { 0.5163443299512, 0.3944519682862,  -0.7601290532814 },
        std::array { 0.1089474441437, 0.5704562235115, 0.8140701145918 }
    };

    auto eigv = eigspans( vectors, 3 );

    CHECK( spatial::distance<3>( lambda, { 3.0, 4.7639320225002, 9.2360679774998 } ) < 1e-10 );

    CHECK( sameEigenvector( eigv( 0 ), expectedVectors[0], 1e-10 ) );
    CHECK( sameEigenvector( eigv( 1 ), expectedVectors[1], 1e-10 ) );
    CHECK( sameEigenvector( eigv( 2 ), expectedVectors[2], 1e-10 ) );
}

TEST_CASE( "eig_test2" )
{
    auto data = std::vector
    {
        1.439, 1.642, 1.242, 1.66 , 0.718, 1.586,
        1.642, 3.16 , 2.148, 2.695, 1.348, 2.015,
        1.242, 2.148, 2.021, 1.696, 0.931, 1.482,
        1.66 , 2.695, 1.696, 2.73 , 1.189, 1.904,
        0.718, 1.348, 0.931, 1.189, 0.774, 0.762,
        1.586, 2.015, 1.482, 1.904, 0.762, 1.919
    };

    auto n = size_t { 6 };

    data.resize( 2 * n * n + 2 * n );

    auto D = std::span { data };

    auto A = D.subspan( 0 * n * n, n * n );
    auto Q = D.subspan( 1 * n * n, n * n );
    auto T = D.subspan( 2 * n * n, n );
    auto L = D.subspan( 2 * n * n + n, n );

    linalg::eig( A, L, T, Q );
    linalg::sorteig( L, Q );

    auto eigv = eigspans( Q, n );

    auto expectedLambda = std::array
    {
        0.0240003978875,  
        0.1331436082572,
        0.19802208396  ,  
        0.6287049774673,
        0.7889145796468,  
        10.2702143527813 
    };

    auto expectedVectors = std::vector
    {
        std::array {  0.6283357608343,  0.3634744176656, -0.0688325519739, 
                     -0.1505285143332, -0.3586358110404, -0.5630844701821 },
        std::array {  0.0757993860251,  0.4059713795803, -0.3900749765608, 
                     -0.6216633710747,  0.4728004524369,  0.2593792396096 },
        std::array { -0.4339132487102,  0.4878222602132, -0.1163625271891, 
                     -0.0583190939562, -0.6847106264948,  0.296612101145  },
        std::array {  0.1420338952295, -0.1690606914876,  0.7210206480704, 
                     -0.5862491474706, -0.1818032411044,  0.2337383127982 },
        std::array { -0.5273571928563,  0.3860957681007,  0.399010047945,  
                     -0.0669453504069,  0.3031792760506, -0.5632193864461 },
        std::array { -0.3359891085696, -0.5361451012117, -0.3879221074018, 
                     -0.4891880618594, -0.23246796183  , -0.394752928824  }
    };

    for( size_t i = 0; i < n; ++i )
    {
        CHECK( L[i] == Approx( expectedLambda[i] ).epsilon( 1e-10 ) );

        CHECK( sameEigenvector( eigv( i ), expectedVectors[i], 1e-10 ) );
    }
}

// The one from here https://people.inf.ethz.ch/arbenz/ewp/Lnotes/2010/chapter3.pdf
TEST_CASE( "eig_pdf_test" )
{
    auto data = std::vector
    {
         7.0,  3.0,  4.0, -11.0, -9.0, -2.0,
        -6.0,  4.0, -5.0,   7.0,  1.0, 12.0,
        -1.0, -9.0,  2.0,   2.0,  9.0,  1.0,
        -8.0,  0.0, -1.0,   5.0,  0.0,  8.0,
        -4.0,  3.0, -5.0,   7.0,  2.0, 10.0,
         6.0,  1.0,  4.0, -11.0, -7.0, -1.0
    };

    auto n = size_t { 6 };

    data.resize( 2 * n * n + 2 * n );

    auto D = std::span { data };

    auto A = D.subspan( 0 * n * n, n * n );
    auto Q = D.subspan( 1 * n * n, n * n );
    auto Re = D.subspan( 2 * n * n, n );
    auto Im = D.subspan( 2 * n * n + n, n );

    linalg::eig( A, Re, Im, Q );
    linalg::sorteig( Re, Q );

    //// These are wrong, need to extract complext eigenvalues. Also 
    //// these values aren't given to enough precision in the pdf.
    //auto expectedLambda = std::array
    //{
    //    -0.2583773936929, 2.258377393693, 3.0, 4.0, 5.0, 5.0
    //};

    //for( size_t i = 0; i < n; ++i )
    //{
    //    CHECK( L[i] == Approx( expectedLambda[i] ).epsilon( 1e-6 ) );
    //}
}

TEST_CASE( "eig_singular_test" )
{
    auto A = std::vector
    {
         -2.990141306631388,  11.638867495117692,   3.066635636610189, // Row 0
         -6.062214763371493,   7.976688120394939,  -5.943737494309515, // _____
         -5.454481551080378,  10.356670965926167,   2.415489616086328, // Row 1
         -6.713248216317353,   7.638850188248097,  -2.927840213785585, // _____
         -7.923570519607564,  16.100289444870604,   1.463376344338631, // Row 2
        -10.55596992010815 ,   8.349311395473327,  -0.923483585253721, // _____
        -11.69439164919719 ,   7.425431549675658,   6.339771609165389, // Row 3
         -7.482533314473259,  16.16195285026443 ,  -5.715819240299324, // _____
         -6.187513720942986,   6.856562983735548,   3.853965150908406, // Row 4
         -5.091547368929338,  10.898722688342163,  -5.073361362963714, // _____
         -7.670169250568312,  14.012239988305618,  -1.482258580801285, // Row 5
         -9.709432787114622,   6.454818632606449,   2.933904622497696, // _____
    };

    auto real = std::array<double, 6> { };
    auto imag = std::array<double, 6> { };
    auto V = std::array<double, 6 * 6> { };
    auto Acopy = A;

    linalg::eig( Acopy, real, imag, V );
    linalg::sorteig( real, V, false, false );

    auto expectedReal = std::array { 6.4, 5.3, 2.1, 1.38, 0.0, 0.0 };

    auto expectedV = std::array
    {
        std::array {  0.791550368169847,  0.369618860976383,  0.355039926784736,  
                      0.058315736766575,  0.325882058401455,  0.034303374568568 },
        std::array { -0.291258969793175, -0.33429459593675 , -0.657061792013609, 
                     -0.028434252987722, -0.036887679551644, -0.607878219278084 },
        std::array {  0.079150891890554,  0.302274526788914,  0.57589097203125 ,  
                      0.445564934521809,  0.16444280125537 ,  0.587490671704864 },
        std::array { -0.508738920458882, -0.163432378197442, -0.030524335227596, 
                     -0.319233672587984, -0.623205177562131, -0.472491272376236 },
        std::array {  0.253110484158827,  0.269135995768492,  0.528955208021496,  
                      0.449176387892272,  0.258490136163483,  0.561365040382599 },
        std::array { -0.461443896774513,  0.359068739825726, -0.106938290749525, 
                      0.789405206771131, -0.123594839356465, -0.090923634926045 },
    };

    auto eigv = eigspans( V, 6 );

    // Check all eigenvalues
    for( size_t i = 0; i < 6; ++i )
    {
        CHECK( real[i] == Approx( expectedReal[i] ).margin( 1e-12 ) );
        CHECK( imag[i] == Approx( 0.0 ).margin( 1e-12 ) );
    }
     
    // Check eigenvectors of non-zero eigenvalues
    for( size_t i = 0; i < 4; ++i )
    {
        CHECK( sameEigenvector( eigv( i ), expectedV[i], 1e-12 ) );
    }

    // Eigenvectors of zero eigenvalues
    for( size_t i = 4; i < 6; ++i )
    {
        CHECK( linalg::norm( eigv( 4 ) ) == Approx( 1.0 ).epsilon( 1e-12 ) );

        auto lambdaV = linalg::mvproduct<6, 6>( std::span { A }, eigv( 4 ).subspan<0, 6>( ) );

        CHECK( spatial::norm( lambdaV ) < 1e-12 );
    }

    // Check singular eigenvectors not linear dependent
    auto dot = 0.0;

    for( size_t j = 0; j < 6; ++j )
    {
        dot += eigv( 4 )[j] * eigv( 5 )[j];
    }

    CHECK( std::abs( dot ) > 1e-3 );
}

TEST_CASE( "generalized_eigh_test" )
{
    // From: 2 x 2 elements, [2.0, 3.0] lengths, p = 2, Dirichlet all sides, integrated Legendre polynomials
    auto M = std::vector
    { 
        0.6666666666667, -0.2041241452319, -0.2041241452319, 0.0625, -0.2041241452319, 0.0625, -0.2041241452319, 0.0625, 0.0625,
        -0.2041241452319, 0.2, 0.0625, -0.06123724356958, 0.0, 0.0, 0.0625, -0.06123724356958, 0.0,
        -0.2041241452319, 0.0625, 0.2, -0.06123724356958, 0.0625, -0.06123724356958, 0.0, 0.0, 0.0,
        0.0625, -0.06123724356958, -0.06123724356958, 0.06, 0.0, 0.0, 0.0, 0.0, 0.0,
        -0.2041241452319, 0.0, 0.0625, 0.0, 0.2, -0.06123724356958, 0.0625, 0.0, -0.06123724356958,
        0.0625, 0.0, -0.06123724356958, 0.0, -0.06123724356958, 0.06, 0.0, 0.0, 0.0,
        -0.2041241452319, 0.0625, 0.0, 0.0, 0.0625, 0.0, 0.2, -0.06123724356958, -0.06123724356958,
        0.0625, -0.06123724356958, 0.0, 0.0, 0.0, 0.0, -0.06123724356958, 0.06, 0.0,
        0.0625, 0.0, 0.0, 0.0, -0.06123724356958, 0.0, -0.06123724356958, 0.0, 0.06,
    };

    auto K = std::vector 
    { 
        2.888888888889, -0.6123724356958, -0.2721655269759, 0.0, -0.6123724356958, 0.0, -0.2721655269759, 0.0, 0.0,
        -0.6123724356958, 1.488888888889, 0.0, -0.2721655269759, 0.0, 0.0, 0.0, -0.2721655269759, 0.0,
        -0.2721655269759, 0.0, 2.266666666667, -0.6123724356958, 0.0, -0.6123724356958, 0.0, 0.0, 0.0,
        0.0, -0.2721655269759, -0.6123724356958, 0.8666666666667, 0.0, 0.0, 0.0, 0.0, 0.0,
        -0.6123724356958, 0.0, 0.0, 0.0, 1.488888888889, -0.2721655269759, 0.0, 0.0, -0.2721655269759,
        0.0, 0.0, -0.6123724356958, 0.0, -0.2721655269759, 0.8666666666667, 0.0, 0.0, 0.0,
        -0.2721655269759, 0.0, 0.0, 0.0, 0.0, 0.0, 2.266666666667, -0.6123724356958, -0.6123724356958,
        0.0, -0.2721655269759, 0.0, 0.0, 0.0, 0.0, -0.6123724356958, 0.8666666666667, 0.0,
        0.0, 0.0, 0.0, 0.0, -0.2721655269759, 0.0, -0.6123724356958, 0.0, 0.8666666666667,
    };

    auto lambda = std::vector<double>( 9 );
    auto tmp1 = std::vector<double>( 9 );
    auto tmp2 = std::vector<size_t>( 9 );
    auto modes = std::vector<double>( 9 * 9 );

    auto copyK = K, copyM = M;

    linalg::eig( copyK, copyM, lambda, tmp1, tmp2, modes );
    linalg::sorteig( lambda, modes, true );

    auto expectedLambda = std::array
    {
         3.5908335653955,  6.9304061435644, 11.1048718662755,
        14.4444444444444, 16.7884972402518, 24.3025355411319,
        33.2855768338223, 36.6251494119912, 46.4832405086786
    };

    //auto expectedModes = std::array
    //{
    //    std::array {  0.826434029238 , -0.2790574386234, -0.2790574386234,
    //                  0.0942277922932, -0.2790574386234,  0.0942277922932,
    //                 -0.2790574386234,  0.0942277922932,  0.0942277922932 },
    //    std::array {  0.0                ,  1.2988269315378e+00,                  0.0,
    //                 -4.3856775484452e-01, -1.2988269315378e+00,  4.3856775484452e-01,
    //                  0.0                , -4.3856775484452e-01,  4.3856775484452e-01 }
    //};
        
    for( size_t i = 0; i < 9; ++i )
    {
        CHECK( lambda[i] == Approx( expectedLambda[i] ).epsilon( 1e-10 ) );
    }

    auto eigv = eigspans( modes, 9 );

    for( size_t i = 0; i + 1 < 9; ++i )
    {
        auto vi = eigv( i );
        auto normI = std::sqrt( std::inner_product( vi.begin( ), vi.end( ), vi.begin( ), 0.0 ) );

        CHECK( normI == Approx( 1.0 ).epsilon( 1e-10 ) );

        // Check if vectors are orthogonal
        for( size_t j = i + 1; j < 9; ++j )
        {
            auto vj = eigv( j );

            auto normJ = std::sqrt( std::inner_product( vj.begin( ), vj.end( ), vj.begin( ), 0.0 ) );
            auto dot = std::inner_product( vi.begin( ), vi.end( ), vj.begin( ), 0.0 ) / ( normI * normJ );

            CHECK( std::abs( dot ) < 1e-10 );
        }

        // Check if they are eigenvectors
        auto Mv = linalg::mvproduct<9>( M, vi );
        auto Kv = linalg::mvproduct<9>( K, vi );

        CHECK( spatial::distance( Kv, lambda[i] * Mv ) < 1e-10 );
    }
}

TEST_CASE( "generalized_eig_test1" )
{
    //auto M = std::vector
    //{
    //    40.0           , 0.0            , -4.3643578047199, 0.0            , 0.0            , -4.3643578047199,
    //    0.0            , 9.5238095238095,  0.0            , 0.0            , 0.0            ,  0.0,
    //   -4.3643578047199, 0.0            ,  4.4444444444444, 0.0            , 0.0            ,  0.4761904761905,
    //    0.0            , 0.0            ,  0.0            , 9.5238095238095, 0.0            ,  0.0,
    //    0.0            , 0.0            ,  0.0            , 0.0            , 2.2675736961451,  0.0,
    //   -4.3643578047199, 0.0            ,  0.4761904761905, 0.0            , 0.0            ,  4.4444444444444
    //};

    //auto K = std::vector
    //{
    //    400.0003999999977      ,   9.26342336171615e-14, -43.64357804719833     ,  -2.111533170534585e-12,  8.326672684688674e-17,  -4.364358023917214e-05,
    //      9.26342336171615e-14 ,  95.23849523809456    ,   4.98212582300539e-14 ,   1.859623566247137e-15, -4.919398222114069e-13,  -9.853229343548264e-16,
    //    -43.64357804719833     ,  4.98212582300539e-14 ,  44.4448444444441      ,   2.236544283107378e-13,  4.996003610813204e-16,   2.333966353518235e-13,
    //     -2.111533170534585e-12,  1.859623566247137e-15,   2.236544283107378e-13, 400.0000952380924      ,  9.384160115644136e-14,  -2.7031155092061e-12,
    //      8.326672684688674e-17, -4.919398222114069e-13,   4.996003610813204e-16,   9.384160115644136e-14, 95.2381904761897      ,   1.110223024625157e-16,
    //     -4.364358023917214e-05, -9.853229343548264e-16,   2.333966353518235e-13,  -2.7031155092061e-12  ,  1.110223024625157e-16, 400.0000444444418
    //};

    //auto lambda = std::array<double, 6> { };
    //auto tmp1 = std::vector<double>( 6 * 6 );
    //auto tmp2 = std::array<size_t, 6> { };
    //auto modes = std::vector<double>( 6 * 6 );

    //linalg::eigh( K, M, lambda, tmp1, tmp2, modes );
}

} // namespace linalg
} // namespace mlhp
