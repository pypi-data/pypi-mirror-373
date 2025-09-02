// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/sparse.hpp"
#include "mlhp/core/alias.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/memory.hpp"

namespace mlhp
{
namespace linalg
{

TEST_CASE( "test_gmres" )
{
    std::array<double, 16> data
    {
        1.0,  0.0,  3.0,  2.0,
        5.0,  3.0,  0.0,  3.0,
        0.0, -1.0,  2.0, -4.0,
       -2.0,  3.0,  0.0,  1.0
    };

    std::array<double, 4> rhs = { 1.0, 2.0, -3.0, 4.0 };

    std::array<std::array<double, 4>, 5> solutions
    {
        std::array<double, 4>{  0.169867690994452, -0.494238156209987, 1.000000000000000, 1.332052923602219 },
        std::array<double, 4>{ -0.201903700542658, -0.435649481089105, 0.983534452943718, 1.734330904883811 },
        std::array<double, 4>{ -0.307090130586031, -0.231010163115204, 1.236038540690432, 1.628899042266033 },
        std::array<double, 4>{ -0.453608247422680,  0.835051546391753, 0.092783505154639, 0.587628865979381 },
        std::array<double, 4>{ -0.453608247422680,  0.835051546391753, 0.092783505154639, 0.587628865979381 } // same
    };

//    std::array<double, 5> errors { 1.914854215512676, 1.230388913573920, 1.160505055753951, 1.141898479325880, 0.000000000000000 };

    auto multiplyA = [&]( const double* vector, double* target, std::uint64_t ) noexcept -> void
    {
        for( size_t i = 0; i < 4; ++i )
        {
            target[i] = 0.0;

            for( size_t j = 0; j < 4; ++j )
            {
                target[i] += data[i * 4 + j] * vector[j];
            }
        }
    };

    std::vector<double> computedErrors;

    for( size_t i = 4; i < 5; ++i )
    {
        size_t numberOfIterations = i + 1;

        std::array<double, 4> u = { 1.0, 1.0, 1.0, 1.0 }; // initial and target

        REQUIRE_NOTHROW( computedErrors = gmres( multiplyA, &rhs[0], &u[0], 4, numberOfIterations, 1e-10 ) );

        REQUIRE( computedErrors.size( ) == i + 1 );

        for( size_t j = 0; j < 4; ++j )
        {
            CHECK( u[j] == Approx( solutions[i][j] ).epsilon( 1e-10 ) );
        }
    }
}

TEST_CASE( "test_cg" )
{
    std::array<double, 16> data
    {
       1.0,  25.0,   0.0,   4.0,
      25.0,   9.0,   1.0,   9.0,
       0.0,   1.0,   4.0, -12.0,
       4.0,   9.0, -12.0,   1.0
    };

    std::vector<double> rhs = { 1.0, 2.0, -3.0, 4.0 };
    std::vector<double> solution { 0.03221482177350403, 0.014471337041767379, -0.2991165201237083,  0.1515004380455779 };

    auto multiplyA = [&]( const double* vector, double* target, std::uint64_t ) noexcept -> void
    {
        for( size_t i = 0; i < 4; ++i )
        {
            target[i] = 0.0;

            for( size_t j = 0; j < 4; ++j )
            {
                target[i] += data[i * 4 + j] * vector[j];
            }
        }
    };

    auto preconditioner = [&]( const double* vector, double* target, std::uint64_t ) -> void
    {
        std::copy( vector, vector + 4, target );
    };

    auto target = std::vector<double>( 4, 0.0 );

    auto residualNorms = cg( multiplyA, rhs, target, 1e-12, 0.0, 10, preconditioner );

    double tolerance = 1e-10;

    REQUIRE( residualNorms.size( ) == 5 );

    CHECK( residualNorms[0] == Approx( 5.477225575051661 ).epsilon( tolerance ) );
    CHECK( residualNorms[1] == Approx( 2.876304105755805 ).epsilon( tolerance ) );
    CHECK( residualNorms[2] == Approx( 2.9582111690779533 ).epsilon( tolerance ) );
    CHECK( residualNorms[3] == Approx( 0.5697344255757155 ).epsilon( tolerance ) );
    CHECK( residualNorms[4] == Approx( 0.0 ).margin( tolerance ) );

    for( size_t i = 0; i < 4; ++i )
    {
        CHECK( target[i] == Approx( solution[i] ).epsilon( tolerance ) );
    }
}

TEST_CASE( "SymmetricSparseMatrix_test" )
{
    //  2.0 -0.5  0.0  0.0  0.8
    // -0.5  1.0  0.0  1.4  6.1
    //  0.0  0.0 -0.2  0.0 -4.9
    //  0.0  1.4  0.0  3.2  0.0
    //  0.8  6.1 -4.9  0.0  2.7

    linalg::SparseIndex indices[] { 0, 1, 4, 1, 3, 4, 2, 4, 3, 4 };
    linalg::SparsePtr indptr []   { 0,       3,       6,    8, 9, 10 };

    double data[] = { 2.0, -0.5, 0.8, 1.0, 1.4, 6.1, -0.2, -4.9, 3.2, 2.7 };

    SymmetricSparseMatrix matrix;

    matrix.claim( { indices, indptr, data }, 5, 5 );

    // Find
    CHECK( matrix.find( 2, 1 ) == nullptr );
    CHECK( matrix.find( 1, 2 ) == nullptr );

    REQUIRE( matrix.find( 1, 4 ) != nullptr );
    REQUIRE( matrix.find( 4, 1 ) != nullptr );

    CHECK( *matrix.find( 1, 4 ) == Approx( 6.1 ).epsilon( 1e-12 ) );
    CHECK( *matrix.find( 4, 1 ) == Approx( 6.1 ).epsilon( 1e-12 ) );

    // operator()
    CHECK( matrix( 3, 4 ) == 0.0 );
    CHECK( matrix( 4, 3 ) == 0.0 );

    CHECK( matrix( 2, 2 ) == Approx( -0.2 ).epsilon( 1e-12 ) );
    CHECK( matrix( 0, 4 ) == Approx(  0.8 ).epsilon( 1e-12 ) );
    CHECK( matrix( 4, 0 ) == Approx(  0.8 ).epsilon( 1e-12 ) );

    // Convert matrix
    auto converted1 = convertToUnsymmetric( matrix );
    auto converted2 = convertToSymmetric( converted1 );

    CHECK( converted1.size1( ) == 5 );
    CHECK( converted1.size2( ) == 5 );
    CHECK( converted2.size1( ) == 5 );
    CHECK( converted2.size2( ) == 5 );

    CHECK( converted1.nnz( ) == 15 );
    CHECK( converted2.nnz( ) == 10 );

    CHECK( std::equal( matrix.indices( ), matrix.indices( ) + 10, converted2.indices( ) ) );
    CHECK( std::equal( matrix.indptr( ), matrix.indptr( ) + 6, converted2.indptr( ) ) );
    CHECK( utilities::floatingPointEqual( matrix.data( ), matrix.data( ) + 10, converted2.data( ), 1e-12 ) );

    // Matrix vector multiplication
    std::vector<double> rhs { 4.3, 0.9, -3.8, 2.7, -5.1 };
    std::vector<double> result;

    REQUIRE_NOTHROW( result = matrix * rhs );

    std::vector<double> expectedResult = { 4.07, -28.58, 25.75, 9.9, 13.78 };

    REQUIRE( result.size( ) == 5 );

    CHECK( utilities::floatingPointEqual( result.begin( ), result.end( ), expectedResult.data( ), 1e-12 ) );

    matrix.release( );
}

TEST_CASE( "additiveSchwarzPreconditiner_test" )
{

    LocationMapVector locationMaps
    {
        { 3, 5, 2, 9 },
        { 2, 5, 1 },
        { 4, 7, 6, 8 },
        { 6, 3, 0, 2 },
        { 0, 7, 4, 9 }
    };

    std::vector<DofIndex> boundaryDofs = { 0, 4, 5 };

    auto matrix = allocateMatrix<UnsymmetricSparseMatrix>( locationMaps, boundaryDofs );

    CHECK( matrix.size1( ) == 7 );
    CHECK( matrix.size2( ) == 7 );
    CHECK( matrix.nnz( ) == 27 );

    double data[] =
    {
         0.64202513, -0.71780219,  0.73520574,  0.09422523,  0.64773527,  0.27863069,  
         0.09926103,  0.83820316, -0.15063977, -0.22692626, -0.25393631,  0.41522684, 
        -0.69547944,  0.6159814 ,  0.02996156, -0.99045522, -0.22174527,  0.02455323, 
        -0.13893814,  0.43454513, -0.10693943,  0.3213493 ,  0.00797774, -0.40185595,  
         0.10185092, -0.96199103,  0.4709358
    };

    std::copy( std::begin( data ), std::end( data ), matrix.data( ) );

    double expectedData[] =
    {
         0.16018508,  1.2202804,  -1.24986683,  1.7712951,   2.59201746,  0.18616924,
         0.7813684,   2.61182362, -0.33810382, -0.45193774, -0.55979437,  0.92256199,
        -0.59297582,  1.45431102, -3.3145493,   0.20974528,  0.17302143,  0.04518146,
         3.17605458, -1.01153099, -0.71418838, -2.09317093,  0.22652082, -0.12978111,
         1.41031782,  2.23931574,  2.96840753
    };

    auto generator = utilities::makeIndexRangeFunction( size_t { 5 }, std::function { 
        [&]( size_t index, std::vector<SparseIndex>& map )
    {
        map.resize( locationMaps[index].size( ) );

        std::copy( locationMaps[index].begin( ), 
                   locationMaps[index].end( ), map.begin( ) );
    } } );

    auto P = makeAdditiveSchwarzPreconditioner( matrix, generator, boundaryDofs, 10 );

    CHECK( P.size1( ) == 7 );
    CHECK( P.size2( ) == 7 );
    CHECK( P.nnz( ) == 27 );

    CHECK( std::equal( P.indices( ), P.indices( ) + P.nnz( ), matrix.indices( ) ) );
    CHECK( std::equal( P.indptr( ), P.indptr( ) + P.size1( ), matrix.indptr( ) ) );

    for( size_t i = 0; i < P.nnz( ); ++i )
    {
        CHECK( P.data( )[i] == Approx( expectedData[i] ).epsilon( 1e-7 ).margin( 1e-7 ) );
    }
}

TEST_CASE( "transpose_test" )
{
    auto indices = new linalg::SparseIndex[10] { 0, 1, 4, 1, 3, 4, 2, 4, 1, 4 };
    auto indptr = new linalg::SparsePtr[5]    { 0,       3,       6,    8,   10 };
    auto data = new double[10] { 2.0, -0.5, 0.8, 1.0, 1.4, 6.1, -0.2, -4.9, 0.6, 2.7 };

    UnsymmetricSparseMatrix matrix;

    matrix.claim( { indices, indptr, data }, 4, 5 );

    auto matrix1 = linalg::transpose( matrix );

    CHECK( matrix1.size1( ) == matrix.size2( ) );
    CHECK( matrix1.size2( ) == matrix.size1( ) );
    CHECK( matrix1.nnz( ) == matrix.nnz( ) );

    auto matrix2 = linalg::transpose( matrix1 );

    CHECK( matrix2.size1( ) == matrix.size1( ) );
    CHECK( matrix2.size2( ) == matrix.size2( ) );
    CHECK( matrix2.nnz( ) == matrix.nnz( ) );

    for( size_t i = 0; i <= matrix.size1( ); ++i )
    {
        CHECK( matrix2.indptr( )[i] == matrix.indptr( )[i] );
    }
    
    for( size_t i = 0; i < matrix.nnz( ); ++i )
    {
        CHECK( matrix2.indices( )[i] == matrix.indices( )[i] );
        CHECK( matrix2.data( )[i] == matrix.data( )[i] );
    }
}

TEST_CASE( "extractBlock_test" )
{
    //  2.0 -0.5  0.0  0.8
    // -0.5  1.0  0.0  6.1
    //  0.0  0.0 -0.2 -4.9
    //  0.0  1.4  0.0  0.0
    //  0.8  6.1 -4.9  2.7
    
    double data[] = 
    {  
         2.0, -0.5,        0.8, 
        -0.5,  1.0,        6.1,  // <----- 0
                    -0.2, -4.9,  // <----- 3
               1.4,              // <----- 2,4
         0.8,  6.1, -4.9,  2.7   // <----- 1
    };  
    //          A     A     A
    //          |     |     |
    //          1    2,2    0

    linalg::SparseIndex indices[] =
    { 
        0, 1,    3, // 0 -> 2
        0, 1,    3, // 3 -> 5
              2, 3, // 6 -> 7
           1,       // 8
        0, 1, 2, 3  // 9 -> 12
    };

    linalg::SparsePtr indptr[] =
    { 
        0, 3, 6, 8, 9, 13
    };

    UnsymmetricSparseMatrix matrix0;

    matrix0.claim( { indices, indptr, data }, 5, 5 );

    // Expected:
    //  6.1,  1.0,
    //  2.7,  6.1, -4.9, -4.9,
    //        1.4,
    // -4.9,       -0.2, -0.2,
    //        1.4,

    auto rowIndices = std::vector<DofIndex> { 1, 4, 3, 2, 3 };
    auto columnIndices = std::vector<DofIndex> { 3, 1, 2, 2 };

    auto matrix1 = linalg::extractBlock( matrix0, rowIndices, columnIndices );

    REQUIRE( matrix1.size1( ) == rowIndices.size( ) );
    REQUIRE( matrix1.size2( ) == columnIndices.size( ) );
    REQUIRE( matrix1.nnz( ) == 11 );

    auto indptr1 = std::vector( matrix1.indptr( ), matrix1.indptr( ) + matrix1.size1( ) + 1 );
    auto indices1 = std::vector( matrix1.indices( ), matrix1.indices( ) + matrix1.nnz( ) );
    auto expected1 = std::vector<double> { 6.1, 1.0, 2.7, 6.1, -4.9, -4.9, 1.4, -4.9, -0.2, -0.2, 1.4 };

    CHECK( indptr1 == std::vector<linalg::SparsePtr> { 0, 2, 6, 7, 10, 11 } );
    CHECK( indices1 == std::vector<linalg::SparseIndex> { 0, 1, 0, 1, 2, 3, 1, 0, 2, 3, 1 } );
    CHECK( std::equal( expected1.begin( ), expected1.end( ), matrix1.data( ) ) );

    matrix0.release( );
}

TEST_CASE( "test_bicgstab" )
{
    // [[ 5.12,  0.  , 17.72,  8.48, -0.78, 10.72,  5.56, 15.52],
    //  [17.4 ,  0.  , 15.88,  0.  ,  0.92,  0.  ,  0.  , 14.48],
    //  [11.8 ,  9.06,  9.58, 11.78, -0.98,  0.  ,  0.  ,  0.  ],
    //  [10.34,  0.  ,  0.  ,  0.  ,  9.32,  8.94,  4.26,  0.  ],
    //  [ 0.  , 14.82,  0.  , 11.86,  7.7 ,  0.  ,  0.5 ,  0.  ],
    //  [10.28,  0.  ,  0.  , 17.32,  0.  ,  1.3 ,  3.54,  5.52],
    //  [ 0.  , 10.52,  0.  , 12.6 ,  6.88, 17.8 , 18.08,  6.3 ],
    //  [ 0.  ,  0.  , 10.22,  4.02,  0.  ,  5.36,  5.94,  0.  ]]
    auto indices = std::vector<SparseIndex>
    {
        0,    2, 3, 4, 5, 6, 7, 
        0,    2,    4,       7, 
        0, 1, 2, 3, 4, 
        0,          4, 5, 6, 
           1,    3, 4,    6, 
        0,       3,    5, 6, 7, 
           1,    3, 4, 5, 6, 7, 
           2,    3,    5, 6
    };

    auto indptr = std::vector<SparsePtr>
    {
        0,  7, 11, 16, 20, 24, 29, 35, 39
    };

    auto data = std::vector<double>
    {
        5.12,        17.72,  8.48, -0.78, 10.72,  5.56, 15.52,
       17.4 ,        15.88,         0.92,               14.48,
       11.8 ,  9.06,  9.58, 11.78, -0.98,
       10.34,                       9.32,  8.94,  4.26,
              14.82,        11.86,  7.7 ,         0.5 ,
       10.28,               17.32,         1.3 ,  3.54,  5.52,
              10.52,        12.6 ,  6.88, 17.8 , 18.08,  6.3 ,
                     10.22,  4.02,         5.36,  5.94
    };

    auto matrix = UnsymmetricSparseMatrix { };
    auto A = linalg::makeDefaultMultiply( matrix );

    matrix.claim( { indices.data( ), indptr.data( ), data.data( ) }, 8, 8 );

    auto M = LinearOperator { [&]( const double* vector, double* target, std::uint64_t n )
    {  
        MLHP_CHECK( n == 8, "Invalid size." );

        for( size_t i = 0; i < n; ++i )
        {
            target[i] = vector[i] / ( matrix( i, i ) + 0.1 * ( i % 3 ) + 0.2 );
        }
    } };

    auto x0 = std::vector { 7.94, -0.6 , -8.08, -6.34, -2.64, -0.46, -1.76,  4.96 };
    auto b = std::vector { 2.28,  7.1 , -4.28, -6.2 ,  6.28,  3.22, -3.76,  0.56 };

    auto expected = std::vector
    {
        -0.52364501244353, -0.3728162915749 , 0.35340115278066, 0.25177603275128,  
         1.09671220504728, -1.58799425999318, 0.74877942769112, 0.66232304431748
    };

    auto expectedNorms = std::vector 
    { 
        243.60484423032312, 388.12861958197993, 288.4353226111492, 3016.602245418494, 244.89302874548517,
        713.1211336160162, 688.1486648490031, 380.165066546182, 5.763551615508594,
        0.02537377611911598, 0.0002717927128135421, 6.989675770825827e-05,
        1.0444421971523213e-05, 1.0720480444259219e-11,
    };

    auto solution = x0;
    auto norms = linalg::bicgstab( A, b, solution, 0.0, 4e-10, 15, M );

    auto check = [&]( bool checkNorms )
    {
        for( size_t i = 0; i < 8; ++i )
        {
            CHECK( solution[i] == Approx( expected[i] ).margin( 1e-9 ) );
        }

        if( checkNorms )
        {
            REQUIRE( norms.size( ) >= 9 );

            for( size_t i = 0; i < 9; ++i )
            {
                CHECK( norms[i] == Approx( expectedNorms[i] ).epsilon( 0.2 ) );
            }
        }
    };

    check( true );

    solution = x0;
    norms = linalg::bicgstab( A, b, solution, 3e-11, 0.0, 15, M );

    check( true );

    std::fill( solution.begin( ), solution.end( ), 0.0 );
    norms = linalg::bicgstab( A, b, solution, 0.0, 4e-10, 20, M );

    check( false );
    
    std::fill( b.begin( ), b.end( ), 0.0 );
    norms = linalg::bicgstab( A, b, solution, 0.0, 4e-10, 20, M );

    CHECK( linalg::norm( solution ) == 0.0 );

    matrix.release( );
}

} // namespace linalg
} // namespace mlhp
