// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/arrayfunctions.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/memory.hpp"
#include "mlhp/core/dense.hpp"

namespace mlhp
{

TEST_CASE( "array_binaryOperations_test" )
{
    auto arr1 = std::array { 6, 4 };
    auto arr2 = std::array { 3, 2 };

    CHECK( array::add( arr1, arr2 ) == std::array { 9, 6 } );
    CHECK( array::add( arr1, 2 ) == std::array { 8, 6 } );
    CHECK( array::add( 2, arr1 ) == std::array { 8, 6 } );
    CHECK( array::subtract( arr1, arr2 ) == std::array { 3, 2 } );
    CHECK( array::subtract( arr1, 2 ) == std::array { 4, 2 } );
    CHECK( array::subtract( 2, arr1 ) == std::array { -4, -2 } );
    CHECK( array::multiply( arr1, arr2 ) == std::array { 18, 8 } );
    CHECK( array::multiply( arr1, 2 ) == std::array { 12, 8 } );
    CHECK( array::multiply( 2, arr1 ) == std::array { 12, 8 } );
    CHECK( array::divide( arr1, arr2 ) == std::array { 2, 2 } );
    CHECK( array::divide( arr1, 2 ) == std::array { 3, 2 } );
    CHECK( array::divide( 4, arr1 ) == std::array { 0, 1 } );
}

TEST_CASE( "array_minmax_test" )
{
    auto arr1 = std::array { 3, 2 };
    auto arr2 = std::array { 2, 4 };

    CHECK( array::maxElement( arr1 ) == 3 );
    CHECK( array::maxElement( arr2 ) == 4 );

    CHECK( array::minElement( arr1 ) == 2 );
    CHECK( array::minElement( arr2 ) == 2 );

    CHECK( array::maxArray( arr1, arr2 ) == std::array { 3, 4 } );
    CHECK( array::minArray( arr1, arr2 ) == std::array { 2, 2 } );

    CHECK( array::maxArray( arr2, 3 ) == std::array { 3, 4 } );
    CHECK( array::maxArray( arr2, 4 ) == std::array { 4, 4 } );
    CHECK( array::maxArray( arr2, 5 ) == std::array { 5, 5 } );

    CHECK( array::minArray( arr2, 1 ) == std::array { 1, 1 } );
    CHECK( array::minArray( arr2, 2 ) == std::array { 2, 2 } );
    CHECK( array::minArray( arr2, 3 ) == std::array { 2, 3 } );
}

TEST_CASE( "array_extract_elementSizes_test" )
{
    auto vectors = std::array
    {
        std::vector<int> { 2, 4, 3, 6 },
        std::vector<int> { 8, 7 },
        std::vector<int> { 12, 11, 19, 15, 13 }
    };

    auto sizes = array::elementSizes( vectors );

    CHECK( sizes[0] == 4 );
    CHECK( sizes[1] == 2 );
    CHECK( sizes[2] == 5 );
    
    auto values = array::extract( vectors, std::array<size_t, 3>{ 2, 0, 4 } );

    CHECK( values[0] == 3 );
    CHECK( values[1] == 8 );
    CHECK( values[2] == 13 );
}

TEST_CASE( "array_slice_insert_test" )
{
    auto arr = std::array { 0, 4, 3 };

    std::array<int, 2> sliced = array::slice( arr, 1 );

    CHECK( sliced[0] == 0 );
    CHECK( sliced[1] == 3 );

    std::array<int, 3> inserted = array::insert( sliced, 1, 4 );

    CHECK( inserted[0] == 0 );
    CHECK( inserted[1] == 4 );
    CHECK( inserted[2] == 3 );
}

TEST_CASE( "array_make_test" )
{
    auto result = array::make<2>( -3 );

    CHECK( result[0] == -3 );
    CHECK( result[1] == -3 );
}

TEST_CASE( "array_numeric_test" )
{
    std::array<int, 2> arr1 { 2, -3 };

    CHECK( array::product( arr1 ) == -6 );
    CHECK( array::sum( arr1 ) == -1 );

    std::array<double, 2> v1 { 3.0, 4.0 };
    std::array<double, 2> v2 { 7.0, 7.0 };

    CHECK( spatial::normSquared( v1 ) == Approx( 25.0 ).epsilon( 1e-12 ) );
    CHECK( spatial::norm( v1 ) == Approx( 5.0 ).epsilon( 1e-12 ) );

    CHECK( spatial::distanceSquared( v1, v2 ) == Approx( 25.0 ).epsilon( 1e-12 ) );
    CHECK( spatial::distance( v1, v2 ) == Approx( 5.0 ).epsilon( 1e-12 ) );
}

TEST_CASE( "array_misc_test" )
{
    CHECK( array::range<double, 4>( ) == std::array { 0.0, 1.0, 2.0, 3.0 } );
    CHECK( array::range<double, 3>( 2.5 ) == std::array { 2.5, 3.5, 4.5 } );
    CHECK( array::range<double, 2>( 10.0, -1.0 ) == std::array { 10.0, 9.0 } );
    CHECK( array::range<int, 2>( ) == std::array { 0, 1 } );
    CHECK( array::range<int, 1>( 4 ) == std::array { 4 } );
    CHECK( array::range<int, 5>( -3, 2 ) == std::array { -3, -1, 1, 3, 5 } );

    CHECK( array::reverse<int, 3>( { 3, 5, -1 } ) == std::array { -1, 5, 3 } );
    CHECK( array::reverse<int, 4>( { 7, 4, 9, 2 } ) == std::array { 2, 9, 4, 7 } );
}

TEST_CASE( "convert_test" )
{
    std::array<int, 2> arr { -1, 2 };

    auto converted = array::convert<size_t>( arr );

    CHECK( converted[0] == std::numeric_limits<size_t>::max( ) );
    CHECK( converted[1] == 2 );
}

TEST_CASE( "vectorMemory_test" )
{
    std::vector<double> v1;

    CHECK( utilities::vectorInternalMemory( v1 ) == 0 );

    std::vector<std::vector<int>> v2 { { 1, 2, 1 }, { 0 }, { 2, 3 }, { 5, 4, 5, 6 } };

    size_t expectedSize2 = v2.capacity( ) * sizeof( std::vector<int> ) + 10 * sizeof( int );

    CHECK( utilities::vectorInternalMemory( v2 ) == expectedSize2 );
    CHECK( utilities::vectorInternalMemory( v1, v2 ) == expectedSize2 );

    std::vector<decltype( v2 )> v3 { v2, v2, v2, v2 };

    size_t expectedSize3 = 4 * ( expectedSize2 + sizeof( v2 ) );

    CHECK( utilities::vectorInternalMemory( v3 ) == expectedSize3 );
    CHECK( utilities::vectorInternalMemory( v1, v2, v3 ) == expectedSize2 + expectedSize3 );

    using VectorOfMatrices = std::vector<std::array<std::array<double, 2>, 3>>;

    std::vector<VectorOfMatrices> v4( 4, VectorOfMatrices( 5 ) );

    size_t expectedSize4 = 4 * ( sizeof( VectorOfMatrices ) + 5 * 2 * 3 * sizeof( double ) );

    CHECK( utilities::vectorInternalMemory( v4 ) == expectedSize4 );
    CHECK( utilities::vectorInternalMemory( v1, v2, v3, v4 ) == expectedSize2 + expectedSize3 + expectedSize4 );

    // This is probably implementation defined and can not be tested like this
    CHECK( utilities::vectorInternalMemory( std::vector<bool>( 0, false ) ) == 0 );
    CHECK( utilities::vectorInternalMemory( std::vector<bool>( 64, false ) ) == 8 );
    CHECK( utilities::vectorInternalMemory( std::vector<bool>( 65, false ) ) > 8 );
    CHECK( utilities::vectorInternalMemory( std::vector<bool>( 65, false ) ) <= 16 );
}

TEST_CASE( "dofPadding_test" )
{
    constexpr size_t simdSize = mlhp::config::simdAlignment / sizeof( double );

    CHECK( memory::paddedLength<double>( 0 ) == 0 );

    for( size_t j = 0; j < 3; ++j )
    {
        for( size_t i = 1; i <= simdSize; ++i )
        {
            CHECK( memory::paddedLength<double>( i + j * simdSize ) == ( j + 1 ) * simdSize );
        }
    }

    size_t nblocks8 = 0;
    size_t nblocks2 = 0;

    for( size_t iRow = 0; iRow < 23; ++iRow )
    {
        CHECK( linalg::symmetricNumberOfBlocks( iRow ) == nblocks8 );
        CHECK( linalg::symmetricNumberOfBlocks<std::uint16_t>( iRow ) == nblocks2 );

        size_t offset8 = nblocks8 * memory::simdVectorSize<double>( ) + iRow;
        size_t offset2 = nblocks2 * memory::simdVectorSize<std::uint16_t>( ) + iRow;

        CHECK( linalg::symmetricDenseOffset( iRow, iRow ) == offset8 );
        CHECK( linalg::symmetricDenseOffset<std::uint16_t>( iRow, iRow ) == offset2 );

        nblocks8 += memory::paddedNumberOfBlocks<double>( iRow + 1 );
        nblocks2 += memory::paddedNumberOfBlocks<std::uint16_t>( iRow + 1 );
    }
}

TEST_CASE( "chunk_test" )
{
    std::vector<std::array<size_t, 3>> expected1
    {
        { 0, 0, 0 }, { 1, 1, 0 }, { 2, 1, 0 }, { 3, 1, 0 }, { 3, 1, 1 }, { 3, 1, 2 }, 
        { 3, 2, 0 }, { 3, 2, 1 }, { 3, 2, 2 }, { 3, 3, 0 }
    };

    for( size_t i = 0; i < expected1.size( ); ++i )
    {
        CHECK( utilities::divideIntoChunks<size_t>( i, 3 ) == expected1[i] );
    }

    std::vector<std::array<size_t, 3>> expected2
    {
        { 0, 0, 0 }, { 1, 1, 0 }, { 1, 2, 0 }, { 1, 3, 0 }, { 1, 4, 0 }, { 1, 5, 0 },
        { 2, 3, 0 }, { 2, 3, 1 }, { 2, 4, 0 }, { 3, 3, 0 }, { 3, 3, 1 }, { 3, 3, 2 },
        { 4, 3, 0 }, { 4, 3, 1 }, { 4, 3, 2 }, { 4, 3, 3 }, { 4, 4, 0 }, { 4, 4, 1 },
        { 4, 4, 2 }, { 4, 4, 3 }, { 4, 5, 0 }, { 4, 5, 1 }, { 4, 5, 2 }, { 4, 5, 3 },
        { 4, 6, 0 }, { 4, 6, 1 }, { 4, 6, 2 }, { 4, 6, 3 }, { 4, 7, 0 }
    };

    for( size_t i = 0; i < expected2.size( ); ++i )
    {
        CHECK( utilities::divideIntoChunks<size_t>( i, 4, 3 ) == expected2[i] );
    }

    std::vector<std::array<size_t, 3>> expected3
    {
        { 0,  0, 0 }, { 1,  1, 0 }, { 1,  2, 0 }, { 1,  3, 0 }, { 1,  4, 0 }, { 1,  5, 0 },
        { 1,  6, 0 }, { 1,  7, 0 }, { 1,  8, 0 }, { 1,  9, 0 }, { 1, 10, 0 }, { 1, 11, 0 },
        { 1, 12, 0 }, { 1, 13, 0 }, { 2,  7, 0 }, { 2,  7, 1 }, { 2,  8, 0 }, { 2,  8, 1 },
        { 2,  9, 0 }, { 2,  9, 1 }, { 2, 10, 0 }, { 3,  7, 0 }, { 3,  7, 1 }, { 3,  7, 2 },
        { 3,  8, 0 }, { 3,  8, 1 }, { 3,  8, 2 }, { 3,  9, 0 }, { 4,  7, 0 }, { 4,  7, 1 }, 
        { 4,  7, 2 }, { 4,  7, 3 }, { 4,  8, 0 }, { 4,  8, 1 }, { 4,  8, 2 }, { 5,  7, 0 }, 
        { 5,  7, 1 }, { 5,  7, 2 }, { 5,  7, 3 }, { 5,  7, 4 }, { 5,  8, 0 }, { 5,  8, 1 }, 
        { 5,  8, 2 }, { 5,  8, 3 }, { 5,  8, 4 }, { 5,  9, 0 }, { 5,  9, 1 }, { 5,  9, 2 }, 
        { 5,  9, 3 }, { 5,  9, 4 }, { 5, 10, 0 }, { 5, 10, 1 }, { 5, 10, 2 }, { 5, 10, 3 }, 
        { 5, 10, 4 }, { 5, 11, 0 }
    };

    for( size_t i = 0; i < expected3.size( ); ++i )
    {
        CHECK( utilities::divideIntoChunks<size_t>( i, 5, 7 ) == expected3[i] );
    }

    CHECK( utilities::chunkRange( 0, { 3, 2, 0 } ) == std::array { 0, 2 } );
    CHECK( utilities::chunkRange( 1, { 3, 2, 0 } ) == std::array { 2, 4 } );
    CHECK( utilities::chunkRange( 2, { 3, 2, 0 } ) == std::array { 4, 6 } );

    CHECK( utilities::chunkRange( 0, { 3, 2, 1 } ) == std::array { 0, 3 } );
    CHECK( utilities::chunkRange( 1, { 3, 2, 1 } ) == std::array { 3, 5 } );
    CHECK( utilities::chunkRange( 2, { 3, 2, 1 } ) == std::array { 5, 7 } );
                                                                 
    CHECK( utilities::chunkRange( 0, { 3, 2, 2 } ) == std::array { 0, 3 } );
    CHECK( utilities::chunkRange( 1, { 3, 2, 2 } ) == std::array { 3, 6 } );
    CHECK( utilities::chunkRange( 2, { 3, 2, 2 } ) == std::array { 6, 8 } );
    
    std::vector<std::array<size_t, 2>> expected4 
    {
        { 0, 2 }, { 2, 4 }, { 4, 5 }, { 5, 6 }, { 6, 7 } 
    };

    for( size_t i = 0; i < expected4.size( ); ++i )
    {
        CHECK( utilities::chunkRange( i, { 5, 1, 2 } ) == expected4[i] );
    }
}

TEST_CASE( "findInterval_test" )
{
    auto positions = std::vector { 3.0, 4.0, 4.2 };

    CHECK( utilities::findInterval( positions, 2.9 ) == 0 );
    CHECK( utilities::findInterval( positions, 3.0 ) == 0 );
    CHECK( utilities::findInterval( positions, 3.5 ) == 0 );
    CHECK( utilities::findInterval( positions, 4.1 ) == 1 );
    CHECK( utilities::findInterval( positions, 4.2 ) == 1 );
    CHECK( utilities::findInterval( positions, 4.3 ) == 1 );
}

namespace detail
{

static bool is_aligned( const void* MLHP_RESTRICT pointer, size_t byte_count )
{
    return reinterpret_cast<uintptr_t>( pointer ) % byte_count == 0;
}

} // namespace detail

TEST_CASE( "memoryAlignment" )
{
    double test = 1.0;

    // Test is_aligned function
    REQUIRE( detail::is_aligned( &test, alignof( double ) ) == true );
    REQUIRE( detail::is_aligned( reinterpret_cast<char*>( &test ) + alignof( double ) / 2, alignof( double ) ) == false );

    memory::AlignedVector<double> v1( 1, 0.0 );
    memory::AlignedVector<double> v2( 2, 0.0 );
    memory::AlignedVector<double> v3( 3, 0.0 );

    CHECK( detail::is_aligned( v1.data( ), mlhp::config::simdAlignment ) );
    CHECK( detail::is_aligned( v2.data( ), mlhp::config::simdAlignment ) );
    CHECK( detail::is_aligned( v3.data( ), mlhp::config::simdAlignment ) );
}

TEST_CASE( "divideCeil_test" )
{
    CHECK( utilities::divideCeil( 0, 1 ) == 0 );
    CHECK( utilities::divideCeil( -2, 2 ) == -1 );
    CHECK( utilities::divideCeil( 5, 1 ) == 5 );
    CHECK( utilities::divideCeil( 5, 2 ) == 3 );
    CHECK( utilities::divideCeil( 5, 3 ) == 2 );
    CHECK( utilities::divideCeil( 5, 4 ) == 2 );
    CHECK( utilities::divideCeil( 5, 5 ) == 1 );

    for( int i = 5; i < 20; ++i )
    {
        CHECK( utilities::divideCeil( 5, i ) == 1 );
    }
}

} // namespace mlhp
