// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/algorithm.hpp"

namespace mlhp
{

TEST_CASE( "backwardIndexMap_test" )
{
    std::vector<bool> mask  { false,  true, false,  true,  true, false,  true, false };
    DofIndexVector map      { NoDof,     0, NoDof,     1,     2, NoDof,     3, NoDof };
    DofIndexVector splitMap {      0,    0,     1,     1,     2,     2,     3,     3 };

    DofIndexVector result;

    REQUIRE_NOTHROW( result = algorithm::backwardIndexMap<DofIndex>( mask ) );

    REQUIRE( result.size( ) == map.size( ) );

    CHECK( std::equal( result.begin( ), result.end( ), map.begin( ) ) );

    REQUIRE_NOTHROW( result = algorithm::splitBackwardIndexMap<DofIndex>( mask ) );

    REQUIRE( result.size( ) == map.size( ) );

    CHECK( std::equal( result.begin( ), result.end( ), splitMap.begin( ) ) );

} // backwardIndexMap_test

TEST_CASE( "forwardIndexMap_test" )
{
    std::vector<bool> mask { false, true, false, true, true, false, true, false };
    DofIndexVector map { 1, 3, 4, 6 };
    DofIndexVector result;

    REQUIRE_NOTHROW( result = algorithm::forwardIndexMap<DofIndex>( mask ) );

    REQUIRE( result.size( ) == map.size( ) );

    CHECK( std::equal( result.begin( ), result.end( ), map.begin( ) ) );

} // forwardIndexMap_test

TEST_CASE( "invertIndices_test" )
{
    auto indices = std::vector<size_t> { 4, 3, 6 };

    auto expected = std::vector<size_t> 
    { 
        NoValue<size_t>, 
        NoValue<size_t>, 
        NoValue<size_t>, 
        1, 
        0, 
        NoValue<size_t>, 
        2 
    };

    CHECK( algorithm::invertIndices( indices ) == expected );

    expected.push_back( NoValue<size_t> );

    CHECK( algorithm::invertIndices( indices, size_t { 8 } ) == expected );

    CHECK_NOTHROW( algorithm::invertIndices( std::vector<size_t> { } ) );
    CHECK_NOTHROW( algorithm::invertIndices( std::vector<size_t> { } ), 4 );

} // removeMissingDofs

TEST_CASE( "invertRepeatedIndices_test" )
{
    auto indices = std::vector<size_t> { 4, 4, 3, 6, 6 };

    auto expectedOffsets = std::vector<size_t> 
    { 
        0, 0, 0, 0, 1, 3, 3, 5
    };

    auto expectedInverted = std::vector<size_t>
    { 
        2, 0, 1, 3, 4 
    };

    auto [offsets1, inverted1] = algorithm::invertRepeatedIndices( indices );
    
    CHECK( offsets1 == expectedOffsets );
    CHECK( inverted1 == expectedInverted );

    expectedOffsets.push_back( 5 );

    auto [offsets2, inverted2] = algorithm::invertRepeatedIndices( indices, size_t { 8 } );

    CHECK( offsets2 == expectedOffsets );
    CHECK( inverted2 == expectedInverted );

    CHECK_NOTHROW( algorithm::invertRepeatedIndices( std::vector<size_t> { } ) );
    CHECK_NOTHROW( algorithm::invertRepeatedIndices( std::vector<size_t> { } ), 4 );

} // removeMissingDofs

TEST_CASE( "computeNumberOfDofs1_test" )
{
    DofIndexVector locationMaps
    {
        0, 2, 5, 3, // 0
        2, 3, 8, 4, // 1
        7, 3, 1, 6  // 1
    };

    DofIndex n1, n2;

    REQUIRE_NOTHROW( n1 = algorithm::computeNumberOfDofs( locationMaps ) );
    REQUIRE_NOTHROW( n2 = algorithm::computeNumberOfDofs( { } ) );

    CHECK( n1 == 9 );
    CHECK( n2 == 0 );
}

} // namespace mlhp
