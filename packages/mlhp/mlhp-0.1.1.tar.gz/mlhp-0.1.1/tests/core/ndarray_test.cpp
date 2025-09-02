// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/ndarray.hpp"

#include <numeric>

namespace mlhp
{

TEST_CASE( "TopologyMask_test")
{
    constexpr TopologyMask<4> mask4( true );

    static_assert( mask4.ndim( ) == 4 );

    static_assert( mask4.size( ) == 3 * 3 * 3 * 3 );

    static_assert( mask4.shape( ).size( ) == 4 );
    static_assert( mask4.strides( ).size( ) == 4 );

    static_assert( mask4.shape( )[0] == 3 );
    static_assert( mask4.shape( )[1] == 3 );
    static_assert( mask4.shape( )[2] == 3 );
    static_assert( mask4.shape( )[3] == 3 );

    static_assert( mask4.strides( )[0] == 27);
    static_assert( mask4.strides( )[1] == 9);
    static_assert( mask4.strides( )[2] == 3);

    static_assert( mask4( 0ul, 0ul, 0ul, 0ul ) == true );
    static_assert( mask4( 1ul, 0ul, 2ul, 1ul ) == true );
    static_assert( mask4( 2ul, 2ul, 2ul, 2ul ) == true );

    CHECK( mask4( 0, 1, 2, 1 ) == true );
}

TEST_CASE( "StaticArray_test" )
{
    constexpr nd::StaticArray<double, 3, 2> fixedArray1( 3.0 );

    static_assert( fixedArray1.ndim( ) == 2 );
    static_assert( fixedArray1.size( ) == 6 );
    static_assert( fixedArray1.strides( ).size( ) == 2 );
    static_assert( fixedArray1.strides( )[0] == 2 );
    static_assert( fixedArray1.shape( ).size( ) == 2 );
    static_assert( fixedArray1.shape( )[0] == 3 );
    static_assert( fixedArray1.shape( )[1] == 2 );
    static_assert( fixedArray1( 0ul, 0ul ) == 3.0 );
    static_assert( fixedArray1( 0ul, 1ul ) == 3.0 );
    static_assert( fixedArray1( 1ul, 0ul ) == 3.0 );
    static_assert( fixedArray1( 1ul, 1ul ) == 3.0 );
    static_assert( fixedArray1( 2ul, 0ul ) == 3.0 );
    static_assert( fixedArray1( 2ul, 1ul ) == 3.0 );

    static_assert( sizeof( fixedArray1 ) == sizeof( double ) * 6 );

    nd::StaticArray<double, 3, 2, 5> fixedArray2;

    std::iota( fixedArray2.begin( ), fixedArray2.end( ), 0 );

    CHECK( fixedArray2.ndim( ) == 3 );
    CHECK( fixedArray2.size( ) == 30 );
    REQUIRE( fixedArray2.shape( ).size( ) == 3 );
    CHECK( fixedArray2.shape( )[0] == 3 );
    CHECK( fixedArray2.shape( )[1] == 2 );
    CHECK( fixedArray2.shape( )[2] == 5 );

    REQUIRE( fixedArray2.strides( ).size( ) == 3 );
    REQUIRE( fixedArray2.strides( )[0] == 10 );
    REQUIRE( fixedArray2.strides( )[1] == 5 );

    size_t linearIndex = 0;

    const auto& constRef = fixedArray2;

    for( size_t i = 0; i < 3; ++i )
    {
        for( size_t j = 0; j < 2; ++j )
        {
            for( size_t k = 0; k < 5; ++k )
            {
                CHECK( fixedArray2( i, j, k ) == linearIndex );
                CHECK( fixedArray2[std::array{ i, j, k }] == linearIndex );
                CHECK( fixedArray2[linearIndex] == linearIndex );

                CHECK( constRef( i, j, k ) == linearIndex );
                CHECK( constRef[std::array{ i, j, k }] == linearIndex );
                CHECK( constRef[linearIndex] == linearIndex );

                ++linearIndex;
            }
        }
    }

} // fixedView_test

TEST_CASE( "CellDataArray_test" )
{
    CellDataArray<double, 3, 2> cells( 5 );

    size_t index = 0;
    for( size_t i = 0; i < 5; ++i )
    {
        std::iota( cells[i].begin( ), cells[i].end( ), static_cast<double>( index ) );

        index += 6;
    }

    double linearIndex = 0;
    for( size_t i = 0; i < 5; ++i )
    {
        for( size_t j = 0; j < 3; ++j )
        {
            for( size_t k = 0; k < 2; ++k )
            {
                CHECK( cells[i]( j, k ) == linearIndex );
                CHECK( cells[i]( j, k ) == linearIndex );

                ++linearIndex;
            }
        }
    }

} // CellDataArray_test

TEST_CASE( "DynamicArray_test" )
{
    nd::DynamicArray<double, 3> dynamicArray( { 2, 4, 3 } );

    REQUIRE( dynamicArray.size( ) == 2 * 4 * 3 );
    REQUIRE( dynamicArray.ndim( ) == 3 );

    REQUIRE( dynamicArray.shape( ).size( ) == 3 );

    REQUIRE( dynamicArray.shape( )[0] == 2 );
    REQUIRE( dynamicArray.shape( )[1] == 4 );
    REQUIRE( dynamicArray.shape( )[2] == 3 );

    REQUIRE( dynamicArray.strides( ).size( ) == 3 );

    REQUIRE( dynamicArray.strides( )[0] == 12 );
    REQUIRE( dynamicArray.strides( )[1] == 3 );
    REQUIRE( dynamicArray.strides( )[2] == 1 );

    std::iota( dynamicArray.begin( ), dynamicArray.end( ), 0 );

    size_t index = 0;

    for( size_t i = 0; i < 2; ++i )
    {
        for( size_t j = 0; j < 4; ++j )
        {
            for( size_t k = 0; k < 3; ++k )
            {
                CHECK( dynamicArray( i, j, k ) == static_cast<double>( index ) );
                CHECK( dynamicArray[{ i, j, k }] == static_cast<double>( index ) );
                CHECK( dynamicArray[index] == static_cast<double>( index ) );

                ++index;
            }
        }
    }
}

TEST_CASE( "nonzero_test" )
{
    BooleanMask<2> mask( { 4, 3 }, { false, true,  true,
                                      true,  true,  false,
                                      false, true,  false,
                                      true,  false, true  } );

    std::vector<std::array<size_t, 2>> indices( 10 );

    nd::nonzero( mask, indices );

    REQUIRE( indices.size( ) == 7 );
    CHECK( indices.capacity( ) == 10 );

    std::vector<std::array<size_t, 2>> expected
    {
        std::array<size_t, 2>{ 0, 1 },
        std::array<size_t, 2>{ 0, 2 },
        std::array<size_t, 2>{ 1, 0 },
        std::array<size_t, 2>{ 1, 1 },
        std::array<size_t, 2>{ 2, 1 },
        std::array<size_t, 2>{ 3, 0 },
        std::array<size_t, 2>{ 3, 2 }
    };

    for( size_t i = 0; i < 7; ++i )
    {
        for( size_t j = 0; j < 2; ++j )
        {
            CHECK( indices[i][j] == expected[i][j] );
        }
    }
}

TEST_CASE( "ndexecute_test" )
{
    std::array<size_t, 3> testLimits { 4, 2, 5 };

    std::array<std::array<size_t, 3>, 40> expectedIndices;

    size_t index = 0;

    for( size_t i = 0; i < 4; ++i )
    {
        for( size_t j = 0; j < 2; ++j )
        {
            for( size_t k = 0; k < 5; ++k )
            {
                expectedIndices[index++] = { i, j, k };
            }
        }
    }
    
    index = 0;

    nd::execute( testLimits, [&]( std::array<size_t, 3> indices )
    {
        for( size_t axis = 0; axis < 3; ++axis )
        {
            CHECK( indices[axis] == expectedIndices[index][axis] );
        }

        ++index;
    } );

    CHECK( index == 40 );

    index = 0;

    nd::executeWithIndex( testLimits, [&]( std::array<size_t, 3> indices, size_t linearIndex )
    {
        for( size_t axis = 0; axis < 3; ++axis )
        {
            CHECK( indices[axis] == expectedIndices[index][axis] );
        }

        CHECK( index++ == linearIndex );
    } );

    CHECK( index == 40 );

    auto result = std::vector<std::array<size_t, 3>> { };

    nd::executeTriangularBoundary<3>( size_t { 6 }, [&]( auto ijk )
    { 
        result.push_back( ijk );
    } );

    auto expected = std::vector<std::array<size_t, 3>>
    { 
        { 0, 0, 0 }, { 0, 0, 1 }, { 0, 0, 2 }, { 0, 0, 3 }, { 0, 0, 4 }, { 0, 0, 5 },
        { 0, 1, 0 }, { 0, 1, 1 }, { 0, 1, 2 }, { 0, 1, 3 }, { 0, 1, 4 },
        { 0, 2, 0 }, { 0, 2, 1 }, { 0, 2, 2 }, { 0, 2, 3 },
        { 0, 3, 0 }, { 0, 3, 1 }, { 0, 3, 2 },
        { 0, 4, 0 }, { 0, 4, 1 },
        { 0, 5, 0 },

        { 1, 0, 0 }, { 1, 0, 1 }, { 1, 0, 2 }, { 1, 0, 3 }, { 1, 0, 4 },
        { 1, 1, 0 },                           { 1, 1, 3 },
        { 1, 2, 0 },              { 1, 2, 2 },
        { 1, 3, 0 }, { 1, 3, 1 },
        { 1, 4, 0 },

        { 2, 0, 0 }, { 2, 0, 1 }, { 2, 0, 2 }, { 2, 0, 3 },
        { 2, 1, 0 },              { 2, 1, 2 },
        { 2, 2, 0 }, { 2, 2, 1 },
        { 2, 3, 0 },

        { 3, 0, 0 }, { 3, 0, 1 }, { 3, 0, 2 },
        { 3, 1, 0 }, { 3, 1, 1 },
        { 3, 2, 0 },

        { 4, 0, 0 }, { 4, 0, 1 },
        { 4, 1, 0 },

        { 5, 0, 0 }
    };

    CHECK( result == expected );

    result.clear( );

    nd::executeBoundary( std::array<size_t, 3> { 5, 4, 6 }, [&]( auto ijk )
    { 
        result.push_back( ijk );
    } );

    expected =
    {
        { 0, 0, 0 }, { 0, 0, 1 }, { 0, 0, 2 }, { 0, 0, 3 }, { 0, 0, 4 }, { 0, 0, 5 },
        { 0, 1, 0 }, { 0, 1, 1 }, { 0, 1, 2 }, { 0, 1, 3 }, { 0, 1, 4 }, { 0, 1, 5 },
        { 0, 2, 0 }, { 0, 2, 1 }, { 0, 2, 2 }, { 0, 2, 3 }, { 0, 2, 4 }, { 0, 2, 5 },
        { 0, 3, 0 }, { 0, 3, 1 }, { 0, 3, 2 }, { 0, 3, 3 }, { 0, 3, 4 }, { 0, 3, 5 },

        { 1, 0, 0 }, { 1, 0, 1 }, { 1, 0, 2 }, { 1, 0, 3 }, { 1, 0, 4 }, { 1, 0, 5 },
        { 1, 1, 0 },                                                     { 1, 1, 5 },
        { 1, 2, 0 },                                                     { 1, 2, 5 },
        { 1, 3, 0 }, { 1, 3, 1 }, { 1, 3, 2 }, { 1, 3, 3 }, { 1, 3, 4 }, { 1, 3, 5 },

        { 2, 0, 0 }, { 2, 0, 1 }, { 2, 0, 2 }, { 2, 0, 3 }, { 2, 0, 4 }, { 2, 0, 5 },
        { 2, 1, 0 },                                                     { 2, 1, 5 },
        { 2, 2, 0 },                                                     { 2, 2, 5 },
        { 2, 3, 0 }, { 2, 3, 1 }, { 2, 3, 2 }, { 2, 3, 3 }, { 2, 3, 4 }, { 2, 3, 5 },

        { 3, 0, 0 }, { 3, 0, 1 }, { 3, 0, 2 }, { 3, 0, 3 }, { 3, 0, 4 }, { 3, 0, 5 },
        { 3, 1, 0 },                                                     { 3, 1, 5 },
        { 3, 2, 0 },                                                     { 3, 2, 5 },
        { 3, 3, 0 }, { 3, 3, 1 }, { 3, 3, 2 }, { 3, 3, 3 }, { 3, 3, 4 }, { 3, 3, 5 },

        { 4, 0, 0 }, { 4, 0, 1 }, { 4, 0, 2 }, { 4, 0, 3 }, { 4, 0, 4 }, { 4, 0, 5 },
        { 4, 1, 0 }, { 4, 1, 1 }, { 4, 1, 2 }, { 4, 1, 3 }, { 4, 1, 4 }, { 4, 1, 5 },
        { 4, 2, 0 }, { 4, 2, 1 }, { 4, 2, 2 }, { 4, 2, 3 }, { 4, 2, 4 }, { 4, 2, 5 },
        { 4, 3, 0 }, { 4, 3, 1 }, { 4, 3, 2 }, { 4, 3, 3 }, { 4, 3, 4 }, { 4, 3, 5 },
    };

    CHECK( result == expected );
}

static_assert( nd::binaryUnravel<size_t, 4>( 13ul ) == std::array<size_t, 4> { 1, 1, 0, 1 } );
static_assert( nd::binaryUnravel<size_t, 4>(  6ul ) == std::array<size_t, 4> { 0, 1, 1, 0 } );
static_assert( nd::binaryUnravel<size_t, 4>(  9ul ) == std::array<size_t, 4> { 1, 0, 0, 1 } );
static_assert( nd::binaryUnravel<size_t, 4>( 10ul ) == std::array<size_t, 4> { 1, 0, 1, 0 } );

static_assert( nd::binaryUnravel<size_t, 3>(  0ul ) == std::array<size_t, 3> { 0, 0, 0 } );
static_assert( nd::binaryUnravel<size_t, 3>(  2ul ) == std::array<size_t, 3> { 0, 1, 0 } );
static_assert( nd::binaryUnravel<size_t, 3>(  5ul ) == std::array<size_t, 3> { 1, 0, 1 } );
static_assert( nd::binaryUnravel<size_t, 3>(  7ul ) == std::array<size_t, 3> { 1, 1, 1 } );

static_assert( nd::binaryRavel<size_t>( std::array<size_t, 4>{ 1, 1, 0, 1 } ) == 13 );
static_assert( nd::binaryRavel<size_t>( std::array<size_t, 4>{ 0, 1, 1, 0 } ) == 6 );
static_assert( nd::binaryRavel<size_t>( std::array<size_t, 4>{ 1, 0, 1, 0 } ) == 10 );
static_assert( nd::binaryRavel<size_t>( std::array<size_t, 3>{ 1, 0, 1 } ) == 5 );
static_assert( nd::binaryRavel<size_t>( std::array<size_t, 3>{ 1, 1, 0 } ) == 6 );
static_assert( nd::binaryRavel<size_t>( std::array<size_t, 3>{ 0, 0, 0 } ) == 0 );
static_assert( nd::binaryRavel<size_t>( std::array<size_t, 3>{ 1, 1, 1 } ) == 7 );

} // namespace mlhp
