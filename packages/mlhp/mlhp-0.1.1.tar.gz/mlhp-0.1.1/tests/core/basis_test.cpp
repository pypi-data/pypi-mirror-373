// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"
#include "tests/core/singleBaseCell_2D.hpp"

#include "mlhp/core/polynomials.hpp"
#include "mlhp/core/derivativeHelper.hpp"
#include "mlhp/core/multilevelhpcore.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/algorithm.hpp"
#include "mlhp/core/refinement.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/postprocessing.hpp" // REMOVE

#include <array>
#include <vector>
#include <type_traits>
#include <numeric>

namespace mlhp
{

TEST_CASE( "homogeneous_p34_test" )
{
    std::array<size_t, 2> p { 3, 4 };

    std::vector<std::array<size_t, 2>> polynomialDegrees( singlebasecell2d::numberOfElements, p );

    LinearizedTensorProductIndices<2> computedIndices;
    
    std::function initialMaskProvider = initializeTensorSpaceMasks<2>;

    REQUIRE_NOTHROW( computedIndices = constructTensorProductIndices( singlebasecell2d::neighbours( ),
            singlebasecell2d::isLeaf, singlebasecell2d::levels, polynomialDegrees, initialMaskProvider ) );

    CHECK( computedIndices == singlebasecell2d::homogeneousTensorProductIndices34 );
}

TEST_CASE( "locationmaps_test" )
{
    DofIndexVector locationMaps;

    auto [entries, indices] = singlebasecell2d::homogeneousTensorProductIndices34;

    REQUIRE_NOTHROW( locationMaps = generateLocationMaps( entries, indices,
        singlebasecell2d::neighbours( ), singlebasecell2d::levels ) );
    
    std::vector<double> expectedData
    {
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 1, 6, 11,
        16, 5, 6, 7, 8, 9, 6, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
        35, 20, 24, 28, 32, 24, 25, 26, 27, 36, 24, 36, 37, 38, 39, 40, 41, 42, 43, 44,
        45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 42, 56, 47, 52, 41, 42, 43, 44, 45,
        42, 56, 57, 58, 59, 36, 56, 60, 61, 62, 63, 64, 65, 36, 37, 38, 39, 40, 60, 66,
        67, 68, 69, 64, 70, 71, 72, 73, 65, 74, 75, 76, 77, 56, 60, 61, 62, 63, 57, 78,
        79, 80, 81, 58, 82, 83, 84, 85, 59, 86, 87, 88, 89, 60, 66, 67, 68, 69, 78, 90,
        91, 92, 93, 82, 94, 95, 96, 97, 86, 98, 99, 100, 101, 102, 103, 104, 105, 106,
        107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 102, 118, 119, 120, 121,
        106, 122, 123, 124, 125, 110, 126, 127, 128, 129, 114, 130, 131, 132, 133, 106,
        107, 108, 109, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 106,
        122, 123, 124, 125, 134, 146, 147, 148, 149, 138, 150, 151, 152, 153, 142, 154,
        155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 158,
        170, 171, 172, 173, 162, 174, 175, 176, 177, 166, 178, 179, 180, 181, 158, 159,
        160, 161, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 158, 170,
        171, 172, 173, 182, 194, 195, 196, 186, 197, 198, 199, 200, 190, 201, 202, 203,
        204, 134, 135, 136, 137, 170, 205, 206, 207, 208, 174, 209, 210, 211, 212, 178,
        213, 214, 215, 216, 134, 146, 147, 148, 149, 205, 217, 218, 219, 220, 209, 221,
        222, 223, 224, 213, 225, 226, 227, 228, 170, 205, 206, 207, 208, 197, 229, 230,
        231, 232, 201, 233, 234, 235, 236, 205, 217, 218, 219, 220, 229, 237, 238, 239,
        240, 233, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254,
        255, 256, 245, 257, 258, 259, 260, 249, 261, 262, 263, 264, 253, 265, 266, 267,
        268, 245, 246, 247, 248, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279,
        280, 245, 257, 258, 259, 260, 269, 281, 282, 283, 273, 284, 285, 286, 287, 277,
        288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303,
        304, 305, 306, 293, 307, 308, 309, 310, 298, 311, 312, 313, 314, 303, 315, 316,
        317, 318, 292, 293, 294, 295, 296, 319, 320, 321, 322, 323, 324, 325, 326, 327,
        328, 329, 330, 331, 332, 333, 293, 307, 308, 309, 310, 320, 334, 335, 336, 337,
        325, 338, 339, 340, 341, 330, 342, 343, 344, 345, 269, 270, 271, 272, 307, 346,
        347, 348, 349, 311, 350, 351, 352, 353, 315, 354, 355, 356, 357, 269, 281, 282,
        283, 346, 358, 359, 360, 350, 361, 362, 363, 354, 364, 365, 366, 307, 346, 347,
        348, 349, 334, 367, 368, 369, 370, 338, 371, 372, 373, 374, 342, 375, 376, 377,
        378, 346, 358, 359, 360, 367, 379, 380, 381, 371, 382, 383, 384, 375, 385, 386,
        387, 182, 183, 184, 185, 257, 388, 389, 390, 391, 261, 392, 393, 394, 395, 265,
        396, 397, 398, 399, 182, 194, 195, 196, 388, 400, 401, 402, 392, 403, 404, 405,
        396, 406, 407, 408, 257, 388, 389, 390, 391, 284, 409, 410, 411, 412, 288, 413,
        414, 415, 416, 388, 400, 401, 402, 409, 417, 418, 419, 413, 420, 421, 422
    };

    std::vector<DofIndex> expectedIndices
    {
        0, 0, 20, 24, 29, 30, 46, 50, 55, 61, 76, 80, 85, 90, 98, 118, 138, 158, 
        174, 194, 210, 230, 242, 257, 273, 292, 311, 331, 346, 361, 373, 388, 
        404, 423, 438, 453, 473, 493, 512, 528, 548, 564, 583, 599, 614, 626
    };

    CHECK( indices.size( ) == expectedIndices.size( ) );
    CHECK( locationMaps.size( ) == expectedData.size( ) );

    CHECK( std::equal( indices.begin( ), indices.end( ), expectedIndices.begin( ) ) );
    CHECK( std::equal( locationMaps.begin( ), locationMaps.end( ), expectedData.begin( ) ) );
}

TEST_CASE( "DerivativesHelper_test" )
{
    // diff order 0
    static_assert( diff::indices<1, 0>( ).size( ) == 1 );
    static_assert( diff::indices<2, 0>( ).size( ) == 1 );
    static_assert( diff::indices<3, 0>( ).size( ) == 1 );
    static_assert( diff::indices<4, 0>( ).size( ) == 1 );

    static_assert( diff::indices<1, 0>( ) == std::array<std::array<size_t, 1>, 1>{ 0 } );
    static_assert( diff::indices<2, 0>( ) == std::array<std::array<size_t, 2>, 1>{ 0, 0 } );
    static_assert( diff::indices<3, 0>( ) == std::array<std::array<size_t, 3>, 1>{ 0, 0, 0 } );
    static_assert( diff::indices<4, 0>( ) == std::array<std::array<size_t, 4>, 1>{ 0, 0, 0, 0 } );
   
    // diff order 1
    static_assert( diff::indices<1, 1>( ).size( ) == 1 );
    static_assert( diff::indices<2, 1>( ).size( ) == 2 );
    static_assert( diff::indices<3, 1>( ).size( ) == 3 );
    static_assert( diff::indices<4, 1>( ).size( ) == 4 );

    static_assert( diff::indices<1, 1>( ) == std::array<std::array<size_t, 1>, 1>{ 1 } );

    static_assert( diff::indices<2, 1>( ) == std::array<std::array<size_t, 2>, 2>{ 1, 0,
                                                                                   0, 1 } );

    static_assert( diff::indices<3, 1>( ) == std::array<std::array<size_t, 3>, 3>{ 1, 0, 0,
                                                                                   0, 1, 0, 
                                                                                   0, 0, 1 } );

    static_assert( diff::indices<4, 1>( ) == std::array<std::array<size_t, 4>, 4>{ 1, 0, 0, 0,
                                                                                   0, 1, 0, 0, 
                                                                                   0, 0, 1, 0, 
                                                                                   0, 0, 0, 1 } );
    
    // diff order 2
    static_assert( diff::indices<1, 2>( ).size( ) == 1 );
    static_assert( diff::indices<2, 2>( ).size( ) == 3 );
    static_assert( diff::indices<3, 2>( ).size( ) == 6 );
    static_assert( diff::indices<4, 2>( ).size( ) == 10 );

    static_assert( diff::indices<1, 2>( ) == std::array<std::array<size_t, 1>, 1>{ 2 } );

    static_assert( diff::indices<2, 2>( ) == std::array<std::array<size_t, 2>, 3>{ 2, 0,
                                                                                   1, 1, 
                                                                                   0, 2 } );

    static_assert( diff::indices<3, 2>( ) == std::array<std::array<size_t, 3>, 6>{ 2, 0, 0,
                                                                                   1, 1, 0, 
                                                                                   1, 0, 1, 
                                                                                   0, 2, 0, 
                                                                                   0, 1, 1, 
                                                                                   0, 0, 2 } );

    static_assert( diff::indices<4, 2>( ) == std::array<std::array<size_t, 4>, 10>{ 2, 0, 0, 0,
                                                                                    1, 1, 0, 0, 
                                                                                    1, 0, 1, 0, 
                                                                                    1, 0, 0, 1, 
                                                                                    0, 2, 0, 0, 
                                                                                    0, 1, 1, 0, 
                                                                                    0, 1, 0, 1, 
                                                                                    0, 0, 2, 0, 
                                                                                    0, 0, 1, 1, 
                                                                                    0, 0, 0, 2 } );

    static_assert( diff::allNComponents<3, 0>( ) == 1 );
    static_assert( diff::allNComponents<3, 1>( ) == 1 + 3 );
    static_assert( diff::allNComponents<3, 2>( ) == 1 + 3 + 6 );

    constexpr auto allindices0 = diff::allIndices<3, 0>( );
    constexpr auto allindices1 = diff::allIndices<3, 1>( );
    constexpr auto allindices2 = diff::allIndices<3, 2>( );

    constexpr auto indices0 = diff::indices<3, 0>( );
    constexpr auto indices1 = diff::indices<3, 1>( );
    constexpr auto indices2 = diff::indices<3, 2>( );

    static_assert( allindices0 == indices0 );

    static_assert( allindices1[0] == indices0[0] );
    static_assert( allindices1[1] == indices1[0] );
    static_assert( allindices1[2] == indices1[1] );
    static_assert( allindices1[3] == indices1[2] );

    static_assert( allindices2[0] == indices0[0] );
    static_assert( allindices2[1] == indices1[0] );
    static_assert( allindices2[2] == indices1[1] );
    static_assert( allindices2[3] == indices1[2] );
    static_assert( allindices2[4] == indices2[0] );
    static_assert( allindices2[5] == indices2[1] );
    static_assert( allindices2[6] == indices2[2] );
    static_assert( allindices2[7] == indices2[3] );
    static_assert( allindices2[8] == indices2[4] );
    static_assert( allindices2[9] == indices2[5] );
}

namespace evaluategridtest
{
    
auto makeTestBasis( const BooleanMask<2>& mask )
{
    auto maskProvider = [=]( BooleanMask<2>& uninitializedMask, std::array<size_t, 2> )
    {
        uninitializedMask = mask;
    };

    auto grid = makeRefinedGrid<2>( { 1, 1 }, { 2.0, 2.0 }, { -1.0, -1.0 } );

    std::vector<size_t> degrees { mask.shape( )[0] - 1, mask.shape( )[1] - 1,
                                  mask.shape( )[0] - 1, mask.shape( )[1] - 1 };

    AnsatzTemplateVector ansatzTemplates( { 1, 2, 2 }, degrees  );

    return MultilevelHpBasis<2>( grid, ansatzTemplates, maskProvider );
}

} // evaluategridtest

TEST_CASE( "evaluategridtest_test" )
{
    constexpr std::array<size_t, 2> shape { 3, 4};

    // Force one element with this tensor product mask
    BooleanMask<2> mask( shape, std::vector<bool>{ true,  false, true, false,
                                                   false, false, true, true,
                                                   false, true,  true, false } );

    auto basis = evaluategridtest::makeTestBasis( mask );

    CoordinateGrid<2> rs 
    {
        std::vector<double>{ -1.0, -0.1234 },
        std::vector<double>{ -0.232, 0.1234, 0.6212 }
    };
    
    nd::StaticArray<double, 3, shape[0], shape[1]> Nr, Ns;

    for( size_t i = 0; i < rs[0].size( ); ++i )
    {
        polynomial::integratedLegendre<2>( shape[0] - 1, rs[0][i],
            { &Nr( 0, i, 0 ),& Nr( 1, i, 0 ),& Nr( 2, i, 0 ) } );
    }

    for( size_t i = 0; i < rs[1].size( ); ++i )
    {
        polynomial::integratedLegendre<2>( shape[1] - 1, rs[1][i],
            { &Ns( 0, i, 0 ),& Ns( 1, i, 0 ),& Ns( 2, i, 0 ) } );
    }

    BasisFunctionEvaluation<2> shapes;

    auto cache = basis.createEvaluationCache( );

    auto maxdegrees = basis.prepareEvaluation( 0, 2, shapes, cache );

    CHECK( maxdegrees == std::array<size_t, 2>{ 2, 3 } );

    size_t headerMemory = ( 2 * 2 + 2 * 3 + 1 ) * sizeof( size_t );
    size_t dataMemory = 2 * ( 1 + 2 + 3 ) * memory::paddedLength<double>( 6 ) * sizeof( double );

    REQUIRE( shapes.maxdifforder( ) == 2 );
    REQUIRE( shapes.memoryUsage( ) == headerMemory + dataMemory );

    basis.prepareGridEvaluation( rs, cache );

    for( size_t iCoordinate = 0; iCoordinate < rs[0].size( ); ++iCoordinate )
    {
        for( size_t jCoordinate = 0; jCoordinate < rs[1].size( ); ++jCoordinate )
        {
            REQUIRE_NOTHROW( basis.evaluateGridPoint( { iCoordinate, jCoordinate }, shapes, cache ) );

            for( size_t ifield : { 0ul, 1ul } )
            {
                size_t activeIndex = 0;

                for( size_t iBasis = 0; iBasis < shape[0]; ++iBasis )
                {
                    for( size_t jBasis = 0; jBasis < shape[1]; ++jBasis )
                    {
                        if( mask( iBasis, jBasis ) )
                        {
                            auto computed = [&]( size_t diffOrder, size_t component )
                            {
                                auto N = shapes.get( ifield, diffOrder );
                                auto ndofpadded = shapes.ndofpadded( ifield );

                                return N[ndofpadded * component + activeIndex];
                            };

                            auto expected = [&]( size_t diffOrderR, size_t diffOrderS )
                            {
                                return Nr( diffOrderR, iCoordinate, iBasis ) * Ns( diffOrderS, jCoordinate, jBasis );
                            };

                            // shapes
                            CHECK( computed( 0, 0 ) == expected( 0, 0 ) );

                            // first derivatives
                            CHECK( computed( 1, 0 ) == expected( 1, 0 ) );
                            CHECK( computed( 1, 1 ) == expected( 0, 1 ) );

                            // second derivatives
                            CHECK( computed( 2, 0 ) == expected( 2, 0 ) );
                            CHECK( computed( 2, 1 ) == expected( 1, 1 ) );
                            CHECK( computed( 2, 2 ) == expected( 0, 2 ) );

                            activeIndex += 1;
                        }

                    } // jBasis
                } // iBasis
            } // ifield
        } // jCoordinate
    } // iCoordinate
}

TEST_CASE( "constructTensorProductMasks_inhomogeneousDegrees" )
{
    const auto& degrees = singlebasecell2d::inhomogeneousDegrees;
    const auto& neighbours = singlebasecell2d::neighbours( );
    const auto& levels = singlebasecell2d::levels;
    const auto& leafMask = singlebasecell2d::isLeaf;

    LinearizedTensorProductIndices<2> indices;

    std::function initialMaskProvider = &initializeTensorSpaceMasks<2>;

    REQUIRE_NOTHROW( indices = constructTensorProductIndices(
        neighbours, leafMask, levels, degrees, initialMaskProvider ) );

    CHECK( indices == singlebasecell2d::inhomogeneousTensorProductIndices );
}

TEST_CASE( "ThisShouldWork_test" )
{
    std::function path = []( double t ) noexcept { return std::array<double, 1>{ 0.6 * t + 0.3 }; };

    auto refinementStrategy = refineInsideDomain( implicit::revolveSphereAroundPath( path, 0.03 ), 2 );

    // Create grid
    auto grid = makeRefinedGrid<2>( { 2, 2 }, { 1.0, 1.0 } );

    grid->refine( refinementStrategy );

    // Create multilevel hp data structure
    auto basis = makeHpBasis<TensorSpace>( grid, 1 );

    // Do checks
    CHECK( grid->nleaves( ) == 34 );
    CHECK( grid->nfull( ) == 44 );
    CHECK( grid->fullIndex( 0 ) == 1 );

    std::vector<CellIndex> fullIndices 
    { 
         1,  4,  5,  8, 10, 11, 16, 17, 18, 19, 20, 21,
        22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
        34, 35, 36, 37, 38, 39, 40, 41, 42, 43
    };

    for( CellIndex i = 0; i < grid->nleaves( ); ++i )
    {
        CHECK( grid->fullIndex( i ) == fullIndices[i] );
    }

    TensorProductIndicesVector<2> target;

    auto checkEqual = [&]( CellIndex index, const TensorProductIndicesVector<2>& expected )
    { 
        basis->tensorProductIndices( index, 0, target );

        REQUIRE( target.size( ) == expected.size( ) );

        for( size_t i = 0; i < expected.size( ); ++i )
        {
            CHECK( target[i][0] == expected[i][0] );
            CHECK( target[i][1] == expected[i][1] );
        }
    };

    checkEqual( 0, { { 0, 1 }, { 1, 1 } } );
    checkEqual( 1, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 2, { { 0, 1 } } );
    checkEqual( 3, { { 0, 0 }, { 0, 1 } } );
    checkEqual( 4, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 5, { { 0, 0 }, { 1, 0 } } );
    checkEqual( 6, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 7, { { 0, 0 }, { 1, 0 } } );
    checkEqual( 8, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 9, { { 0, 0 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 10, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 11, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 12, { { 1, 0 } } );
    checkEqual( 13, { } );
    checkEqual( 14, { { 0, 0 }, { 1, 0 } } );
    checkEqual( 15, { } );
    checkEqual( 16, { { 1, 0 }, { 1, 1 } } );
    checkEqual( 17, { { 1, 0 }, { 1, 1 } } );
    checkEqual( 18, { { 0, 0 }, { 0, 1 } } );
    checkEqual( 19, { { 0, 0 }, { 0, 1 } } );
    checkEqual( 20, { { 1, 0 }, { 1, 1 } } );
    checkEqual( 21, { { 1, 0 } } );
    checkEqual( 22, { { 0, 0 }, { 0, 1 }, { 1, 1 } } );
    checkEqual( 23, { { 0, 0 }, { 1, 0 } } );
    checkEqual( 24, { { 0, 1 }, { 1, 1 } } );
    checkEqual( 25, { { 0, 0 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 26, { { 0, 1 } } );
    checkEqual( 27, { { 0, 0 }, { 0, 1 } } );
    checkEqual( 28, { { 1, 0 }, { 1, 1 } } );
    checkEqual( 29, { { 1, 0 }, { 1, 1 } } );
    checkEqual( 30, { { 0, 0 }, { 0, 1 }, { 1, 1 } } );
    checkEqual( 31, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 32, { { 1, 0 }, { 1, 1 } } );
    checkEqual( 33, { { 1, 0 }, { 1, 1 } } );
    checkEqual( 34, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 35, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 36, { { 0, 1 }, { 1, 1 } } );
    checkEqual( 37, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 38, { { 0, 1 }, { 1, 1 } } );
    checkEqual( 39, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 40, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 41, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 42, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );
    checkEqual( 43, { { 0, 0 }, { 0, 1 }, { 1, 0 }, { 1, 1 } } );

    std::vector<DofIndex> expectedNDof 
    { 
        4, 6, 4, 5, 5, 5, 8, 8, 8, 8, 6, 5, 
        7, 6, 6, 7, 5, 6, 5, 5, 6, 7, 4, 4, 
        6, 6, 6, 8, 6, 8, 6, 6, 6, 6 
    };

    LocationMap locationMap;

    for( CellIndex i = 0; i < expectedNDof.size( ); ++i )
    {
        locationMap.resize( 0 );

        basis->locationMap( i, locationMap );

        CHECK( locationMap.size( ) == expectedNDof[i] );
    }
}

TEST_CASE( "TensorSpace_2D_test" )
{
    BooleanMask<2> mask;

    std::array<size_t, 2> degrees { 2, 3 };

    CHECK_NOTHROW( initializeTensorSpaceMasks<2>( mask, degrees ) );

    CHECK( mask.shape( )[0] == 3 );
    CHECK( mask.shape( )[1] == 4 );

    CHECK( std::accumulate( mask.begin( ), mask.end( ), size_t( 0 ) ) == 3 * 4 );

    degrees[1] = 0;

    MLHP_DISABLE_EXCEPTION_LOGS = true;

    CHECK_THROWS( initializeTensorSpaceMasks<2>( mask, degrees ) );
}

TEST_CASE( "TensorSpace_4D_test" )
{
    if constexpr( mlhp::config::maxdim >= 4 )
    {
        BooleanMask<4> mask;

        std::array<size_t, 4> degrees { 3, 1, 4, 2 };

        CHECK_NOTHROW( initializeTensorSpaceMasks<4>( mask, degrees ) );

        CHECK( mask.shape( )[0] == 4 );
        CHECK( mask.shape( )[1] == 2 );
        CHECK( mask.shape( )[2] == 5 );
        CHECK( mask.shape( )[3] == 3 );

        CHECK( std::accumulate( mask.begin( ), mask.end( ), size_t( 0 ) ) == 4 * 5 * 2 * 3 );
    }
}

TEST_CASE( "TruncSpace_1D_test" )
{
    BooleanMask<1> mask;

    std::array<size_t, 1> degrees { 2 };
    
    CHECK_NOTHROW( initializeTrunkSpaceMasks<1>( mask, degrees ) );

    CHECK( mask.shape( )[0] == 3 );

    degrees[0] = 0;

    CHECK_THROWS( initializeTrunkSpaceMasks<1>( mask, degrees ) );
}

TEST_CASE( "TruncSpace_2D_test" )
{
    BooleanMask<2> mask1, mask2;

    std::array<size_t, 2> degrees1 { 4, 6 };
    std::array<size_t, 2> degrees2 { 6, 4 };

    REQUIRE_NOTHROW( initializeTrunkSpaceMasks<2>( mask1, degrees1 ) );
    REQUIRE_NOTHROW( initializeTrunkSpaceMasks<2>( mask2, degrees2 ) );

    REQUIRE( mask1.shape( ) == std::array<size_t, 2>{ 5, 7 } );
    REQUIRE( mask2.shape( ) == std::array<size_t, 2>{ 7, 5 } );

    std::vector<bool> data { true,  true,  true,  true,  true,  true,  true,
                             true,  true,  true,  true,  true,  true,  true,
                             true,  true,  true,  true,  true, false, false,
                             true,  true,  true,  true, false, false, false,
                             true,  true,  true, false, false, false, false };

    auto expected = [&]( size_t i, size_t j ) { return data[i * 7 + j]; };
    
    for( size_t i = 0; i < 5; ++i )
    {
        for( size_t j = 0; j < 7; ++j )
        {
            CHECK( mask1( i, j ) == expected( i, j ) );
            CHECK( mask2( j, i ) == expected( i, j ) );
        }
    }
}

TEST_CASE( "TruncSpace_3D_test" )
{
    size_t ordering[6][3] = { { 0, 1, 2 }, { 0, 2, 1 }, { 1, 0, 2 }, { 1, 2, 0 }, { 2, 0, 1 }, { 2, 1, 0 } };

    auto reorder = [&]( std::array<size_t, 3> arr, size_t index )
    { 
        return std::array<size_t, 3>{ arr[ordering[index][0]],
                                      arr[ordering[index][1]], 
                                      arr[ordering[index][2]] }; 
    };

    std::array<size_t, 3> orders { 3, 4, 5 };
    
    BooleanMask<3> masks[6];

    for( size_t i = 0; i < 6; ++i )
    {
        auto reordered = reorder( orders, i );

        REQUIRE_NOTHROW( initializeTrunkSpaceMasks<3>( masks[i], reordered ) );

        REQUIRE( masks[i].shape( ) == array::add<size_t, 3>( reordered, 1 ) );
    }

    std::vector<bool> data { true,  true,  true,  true,  true,  true,
                             true,  true,  true,  true,  true,  true,
                             true,  true,  true,  true, false, false,
                             true,  true,  true, false, false, false,
                             true,  true, false, false, false, false,

                             true,  true,  true,  true,  true,  true,
                             true,  true,  true,  true,  true,  true,
                             true,  true,  true,  true, false, false,
                             true,  true,  true, false, false, false,
                             true,  true, false, false, false, false,

                             true,  true,  true,  true, false, false,
                             true,  true,  true,  true, false, false,
                             true,  true, false, false, false, false,
                             true,  true, false, false, false, false,
                            false, false, false, false, false, false,

                             true,  true,  true, false, false, false,
                             true,  true,  true, false, false, false,
                             true,  true, false, false, false, false,
                            false, false, false, false, false, false,
                            false, false, false, false, false, false };

    auto access = [&]( std::array<size_t, 3> ijk ) { return data[( ijk[0] * 5 + ijk[1] ) * 6 + ijk[2]]; };

    nd::execute( array::add<size_t>( orders, 1 ), [&]( std::array<size_t, 3> ijk )
    {
        for( size_t i = 0; i < 6; ++i )
        {
            CHECK( masks[i][reorder( ijk, i )] == access( ijk ) );
        }
    } );
}

TEST_CASE( "compressedTensorProduct2D_test" )
{
    /* Tensor product mask:
     *       ---------------------
     * Ns5  |  0   0   0   0   0  |
     * Ns4  |  0   0   1   1   0  |
     * Ns3  |  1   0   1   1   1  |
     * Ns2  |  0   0   0   0   0  |
     * Ns1  |  0   0   1   1   1  | 
     * Ns0  |  1   0   0   1   1  |
     *       ---------------------
     *        Nr0 Nr1 Nr2 Nr3 Nr4
     */

    std::vector<std::array<PolynomialDegree, 2>> indices
    {
        {{ 0, 0 }}, {{ 0, 3 }},
        {{ 2, 1 }}, {{ 2, 3 }}, {{ 2, 4 }},
        {{ 3, 0 }}, {{ 3, 1 }}, {{ 3, 3 }}, {{ 3, 4 }},
        {{ 4, 0 }}, {{ 4, 1 }}, {{ 4, 3 }}
    };

    std::vector<PolynomialDegree> compressed
    {
        4,                      // 3 blocks r
            0, 2,   0, 3,       //     r index 0, 2 entries s: [0, 3]
            2, 3,   1, 3, 4,    //     r index 2, 3 entries s: [1, 3, 4]
            3, 4,   0, 1, 3, 4, //     r index 3, 4 entries s: [0, 1, 3, 4]
            4, 3,   0, 1, 3     //     r index 4, 3 entries s: [0, 1, 3]
    };

    double Nr[] = {  5.4, -4.1,  0.7,  2.3,  1.8 };
    double Ns[] = { -2.7,  3.2, -0.3,  6.7,  4.4, -3.3 };
    
    std::vector<double> expectedShapes
    {
        Nr[0] * Ns[0], Nr[0] * Ns[3],
        Nr[2] * Ns[1], Nr[2] * Ns[3], Nr[2] * Ns[4],
        Nr[3] * Ns[0], Nr[3] * Ns[1], Nr[3] * Ns[3], Nr[3] * Ns[4],
        Nr[4] * Ns[0], Nr[4] * Ns[1], Nr[4] * Ns[3]
    };

    std::array<const double*, 2> bases1D = { Nr, Ns };

    std::vector<double> shapesTarget( expectedShapes.size( ), 0.0 );
    std::vector<PolynomialDegree> compressTarget( 10, 6 );

    CHECK_NOTHROW( compressIndices( indices.data( ), indices.data( ) + indices.size( ), compressTarget ) );

    REQUIRE( compressTarget.size( ) == compressed.size( ) + 10 );

    CHECK( std::equal( compressed.begin( ), compressed.end( ), compressTarget.begin( ) + 10 ) );

    CHECK_NOTHROW( compressedTensorProduct( compressed.data( ), bases1D, 2.0, shapesTarget.data( ) ) );

    for( size_t i = 0; i < expectedShapes.size( ); ++i )
    {
        CHECK( shapesTarget[i] == Approx( 2.0 * expectedShapes[i] ).epsilon( 1e-12 ) );
    }
}

TEST_CASE( "compressedTensorProduct3D_test" )
{
    /* Tensor product mask:
     * 
     *  t  s       __________  
     *  | /       |1  1  0  0|
     *  |/___ r   |1  1  0  1|
     *          / |0  0  0 /0|
     *            |1__1__0__1|
     *        /_________ /    
     *       |1  1  0  0|  /
     *       |1  1  0  0|  
     *     / |1  1  0 /0|/ 
     *       |0__0__0__0|
     *   /_________ /  
     *  |0  0  0  1|  /
     *  |0  1  0  1|  
     *  |1  1  0  0|/
     *  |0__0__0__1|
     * 
     */

    std::vector<std::array<PolynomialDegree, 3>> indices
    {

        {{ 0, 0, 1 }},                               // Column (0, 0, i)
        {{ 0, 1, 1 }}, {{ 0, 1, 2 }}, {{ 0, 1, 3 }}, // Column (0, 1, i)
        {{ 0, 2, 0 }}, {{ 0, 2, 2 }}, {{ 0, 2, 3 }}, // Column (0, 2, i)
        {{ 1, 0, 1 }}, {{ 1, 0, 2 }},                // Column (1, 0, i)
        {{ 1, 1, 1 }}, {{ 1, 1, 2 }}, {{ 1, 1, 3 }}, // Column (1, 1, i)
        {{ 1, 2, 0 }}, {{ 1, 2, 2 }}, {{ 1, 2, 3 }}, // Column (1, 2, i)
        {{ 3, 0, 0 }}, {{ 3, 0, 2 }}, {{ 3, 0, 3 }}, // Column (3, 0, i)
        {{ 3, 2, 0 }}, {{ 3, 2, 2 }}                 // Column (3, 2, i)
    };

    std::vector<PolynomialDegree> compressed
    {
        3,                       // 3 blocks r
            0, 3,                //     r index 0, 3 blocks s
                0, 1,   1,       //         s index 0, 1 entry   t, t indices [1]
                1, 3,   1, 2, 3, //         s index 1, 3 entries t, t indices [1, 2, 3]
                2, 3,   0, 2, 3, //         s index 2, 3 entries t, t indices [0, 2, 3]
            1, 3,                //     r index 1, 3 blocks s
                0, 2,   1, 2,    //         s index 0, 2 entries t, t indices [1, 2]
                1, 3,   1, 2, 3, //         s index 1, 3 entries t, t indices [1, 2, 3]
                2, 3,   0, 2, 3, //         s index 2, 3 entries t, t indices [0, 2, 3]
            3, 2,                //     r index 3, 2 blocks s
                0, 3,   0, 2, 3, //         s index 0, 3 entries t, t indices [0, 2, 3]
                2, 2,   0, 2     //         s index 2, 2 entries t, t indices [0, 2]
    };

    double Nr[] = { -4.1,  0.3,  2.3,  1.8 };
    double Ns[] = {  6.7,  4.4, -3.3 };
    double Nt[] = {  5.4, -2.7,  3.2, -0.3 };

    std::vector<double> expectedShapes
    {
        Nr[0] * Ns[0] * Nt[1],
        Nr[0] * Ns[1] * Nt[1], Nr[0] * Ns[1] * Nt[2], Nr[0] * Ns[1] * Nt[3],
        Nr[0] * Ns[2] * Nt[0], Nr[0] * Ns[2] * Nt[2], Nr[0] * Ns[2] * Nt[3],
        Nr[1] * Ns[0] * Nt[1], Nr[1] * Ns[0] * Nt[2],
        Nr[1] * Ns[1] * Nt[1], Nr[1] * Ns[1] * Nt[2], Nr[1] * Ns[1] * Nt[3],
        Nr[1] * Ns[2] * Nt[0], Nr[1] * Ns[2] * Nt[2], Nr[1] * Ns[2] * Nt[3],
        Nr[3] * Ns[0] * Nt[0], Nr[3] * Ns[0] * Nt[2], Nr[3] * Ns[0] * Nt[3],
        Nr[3] * Ns[2] * Nt[0], Nr[3] * Ns[2] * Nt[2]
    };

    std::array<const double*, 3> bases1D = { Nr, Ns, Nt };

    std::vector<double> target( expectedShapes.size( ), 0.0 );
    std::vector<PolynomialDegree> compressTarget( 13, 2 );

    CHECK_NOTHROW( compressIndices( indices.data( ), indices.data( ) + indices.size( ), compressTarget ) );

    REQUIRE( compressTarget.size( ) == compressed.size( ) + 13 );

    CHECK( std::equal( compressed.begin( ), compressed.end( ), compressTarget.begin( ) + 13 ) );

    CHECK_NOTHROW( compressedTensorProduct( compressed.data( ), bases1D, 0.4, target.data( ) ) );

    for( size_t i = 0; i < expectedShapes.size( ); ++i )
    {
        CHECK( target[i] == Approx( 0.4 * expectedShapes[i] ).epsilon( 1e-12 ) );
    }
}

TEST_CASE( "BasisFunctionEvaluation_test" )
{
    BasisFunctionEvaluation<3> shapes;

    shapes.initialize( 5, 3, 2 );

    shapes.addDofs( 0, 5 );
    shapes.addDofs( 1, 4 );
    shapes.addDofs( 2, 6 );
    shapes.addDofs( 0, 9 );
    shapes.addDofs( 1, 8 );
    shapes.addDofs( 2, 7 );

    shapes.allocate( );

    REQUIRE( shapes.elementIndex( ) == 5 );
    REQUIRE( shapes.maxdifforder( ) == 2 );
    REQUIRE( shapes.nfields( ) == 3 );
    REQUIRE( shapes.ndof( ) == 14 + 12 + 13 );

    REQUIRE( shapes.ndof( 0 ) == 14 );
    REQUIRE( shapes.ndof( 1 ) == 12 );
    REQUIRE( shapes.ndof( 2 ) == 13 );

    auto padded0 = memory::paddedLength<double>( 14 );
    auto padded1 = memory::paddedLength<double>( 12 );
    auto padded2 = memory::paddedLength<double>( 13 );

    REQUIRE( shapes.ndofpadded( 0 ) == padded0 );
    REQUIRE( shapes.ndofpadded( 1 ) == padded1 );
    REQUIRE( shapes.ndofpadded( 2 ) == padded2 );

    auto paddedLengths = padded0 + padded1 + padded2;

    size_t infosize = 3 + 3 + 3 * 3 + 1;
    size_t datasize = ( 1 + 3 + 6 ) * paddedLengths;

    auto expectedCapacity = sizeof( size_t ) * infosize + sizeof( double ) * datasize;

    REQUIRE( shapes.memoryUsage( ) == expectedCapacity );

    auto begin0 = shapes.get( 0, 0 );

    auto unsignedDistance = []( auto ptr1, auto ptr2 )
    {
        auto d = std::distance( ptr1, ptr2 );

        CHECK( d >= 0 );

        return static_cast<size_t>( d );
    };

    CHECK( unsignedDistance( begin0, shapes.get( 0, 1 ) ) == 1 * padded0 );
    CHECK( unsignedDistance( begin0, shapes.get( 0, 2 ) ) == 4 * padded0 );

    auto begin1 = shapes.get( 1, 0 );

    CHECK( unsignedDistance( begin0, begin1 ) == 10 * padded0 );

    CHECK( unsignedDistance( begin1, shapes.get( 1, 1 ) ) == 1 * padded1 );
    CHECK( unsignedDistance( begin1, shapes.get( 1, 2 ) ) == 4 * padded1 );

    auto begin2 = shapes.get( 2, 0 );

    CHECK( unsignedDistance( begin1, begin2 ) == 10 * padded1 );

    CHECK( unsignedDistance( begin2, shapes.get( 2, 1 ) ) == 1 * padded2 );
    CHECK( unsignedDistance( begin2, shapes.get( 2, 2 ) ) == 4 * padded2 );
}

namespace basisevaluation
{

/*
 *  ---------------------------------------
 * |    |    |    |    |         |         |
 * |----|----|----|----|         |         |
 * |    |    |    |    |         |         |
 * |---------|---------|---------|---------|
 * |         | 11 |    |    |    |         |
 * |         |----|----|----|----|         |
 * |         |    |    |    |    |         |
 * |-------------------|---------|---------|
 * |                   |    |    |    |    |
 * |                   |----|----|----|----|
 * |                   |    |    |    |    |
 * |                   |---------|---------|
 * |                   |         |    |    |
 * |                   |         |----|----|
 * |                   |         |    |    |
 *  ---------------------------------------
 */

auto tensorProduct( std::array<size_t, 2> diff,
                    std::array<double, 2> rs,
                    std::array<size_t, 2> degrees )
{
    std::vector<double> Nr( ( degrees[0] + 1 ) * ( diff[0] + 1 ) );
    std::vector<double> Ns( ( degrees[1] + 1 ) * ( diff[1] + 1 ) );

    polynomial::integratedLegendre( degrees[0], diff[0], rs[0], Nr.data( ) );
    polynomial::integratedLegendre( degrees[1], diff[1], rs[1], Ns.data( ) );

    std::vector<std::vector<double>> matrix( Nr.size( ) );

    size_t offset0 = ( degrees[0] + 1 ) * diff[0];
    size_t offset1 = ( degrees[1] + 1 ) * diff[1];

    for( size_t i = 0; i <= degrees[0]; ++i )
    {
        matrix[i].resize( Ns.size( ) );

        for( size_t j = 0; j <= degrees[1]; ++j )
        {
            matrix[i][j] = Nr[i + offset0] * Ns[j + offset1];
        }
    }

    return matrix;
}

auto expectedShapes( std::array<size_t, 2> diff,
                     std::array<double, 2> rs )
{
    std::vector<double> field0( 11 );
    std::vector<double> field1( 12 );

    size_t diffOrder = diff[0] + diff[1];

    // Level 3: field 1 (1, 2), field 2 (2, 1)
    auto tp3 = tensorProduct( diff, rs, { 2, 2 } );

    double factor3 = std::pow( 2.0 / 10.0 * 8.0, diffOrder );

    field0[0] = tp3[1][0] * factor3;
    field0[1] = tp3[1][1] * factor3;
    field0[2] = tp3[1][2] * factor3;

    field1[0] = tp3[1][0] * factor3;
    field1[1] = tp3[1][1] * factor3;
    field1[2] = tp3[2][0] * factor3;
    field1[3] = tp3[2][1] * factor3;

    // Level 2: field 1 (2, 3), field 2 (3, 2)
    rs = { 0.5 * ( rs[0] - 1.0 ), 0.5 * ( rs[1] + 1.0 ) };

    auto tp2 = tensorProduct( diff, rs, { 3, 3 } );

    double factor2 = std::pow( 2.0 / 10.0 * 4.0, diffOrder );

    field0[3] = tp2[0][1] * factor2;
    field0[4] = tp2[0][2] * factor2;
    field0[5] = tp2[0][3] * factor2;
    field0[6] = tp2[1][1] * factor2;

    field1[4] = tp2[0][1] * factor2;
    field1[5] = tp2[0][2] * factor2;
    field1[6] = tp2[1][1] * factor2;

    // Level 1: field 1 (3, 4), field 2 (4, 3)
    rs = { 0.5 * ( rs[0] + 1.0 ), 0.5 * ( rs[1] - 1.0 ) };

    auto tp1 = tensorProduct( diff, rs, { 4, 4 } );

    double factor1 = std::pow( 2.0 / 10.0 * 2.0, diffOrder );

    field0[7] = tp1[0][0] * factor1;
    field0[8] = tp1[1][0] * factor1;
    field0[9] = tp1[2][0] * factor1;
    field0[10] = tp1[3][0] * factor1;

    field1[7] = tp1[0][0] * factor1;
    field1[8] = tp1[1][0] * factor1;
    field1[9] = tp1[2][0] * factor1;
    field1[10] = tp1[3][0] * factor1;
    field1[11] = tp1[4][0] * factor1;

    return std::make_tuple( field0, field1 );
}

auto constructPolynomialDegrees( const AbsHierarchicalGrid<2>& grid )
{
    size_t nfields = 2;

    AnsatzTemplateVector degrees( { grid.nleaves( ), nfields, 2 } );

    for( CellIndex ielement = 0; ielement < grid.nleaves( ); ++ielement )
    {
        auto level = grid.refinementLevel( grid.fullIndex( ielement ) );

        size_t increment = 3 - level;

        // Field 0
        degrees( ielement, 0, 0 ) = 1 + increment;
        degrees( ielement, 0, 1 ) = 2 + increment;

        // Field 1
        degrees( ielement, 1, 0 ) = 2 + increment;
        degrees( ielement, 1, 1 ) = 1 + increment;
    }

    return degrees;
}

} // namespace basisevaluation

TEST_CASE( "MultilevelHpEvaluation2D_test" )
{
    auto refinedGrid = makeRefinedGrid<2>( { 1, 1 }, { 10.0, 10.0 } );

    auto circle = implicit::sphere<2>( { 0.0, 0.0 }, 8.0 );

    refinedGrid->refine( refineTowardsDomainBoundary( circle, 3 ) );

    auto degrees = basisevaluation::constructPolynomialDegrees( *refinedGrid );

    auto basis = MultilevelHpBasis<2>( refinedGrid, degrees, initializeTrunkSpaceMasks<2> );

    auto testEqual = []( const auto& expected,
                         const double* begin,
                         const double* end )
    {
        CHECK( memory::paddedLength<double>( expected.size( ) ) ==
               static_cast<size_t>( std::distance( begin, end ) ) );

        for( size_t i = 0; i < expected.size( ); ++i )
        {
            CHECK( expected[i] == Approx( begin[i] ).epsilon( 1e-12 ) );
        }
    };

    auto cache1 = basis.createEvaluationCache( );
    auto cache2 = basis.createEvaluationCache( );

    BasisFunctionEvaluation<2> shapes1, shapes2;

    CoordinateGrid<2> rst { { { -0.5, 0.5 }, { -0.2, 0.0, 0.4 } } };

    CellIndex element = 11;

    // Test evaluation up to orders 0, 1 and 2
    for( size_t maxdifforder = 0; maxdifforder <= 2; ++maxdifforder )
    {
        auto maxdegrees1 = basis.prepareEvaluation( element, maxdifforder, shapes1, cache1 );
        auto maxdegrees2 = basis.prepareEvaluation( element, maxdifforder, shapes2, cache2 );

        auto maxdegrees3 = basis.maxdegrees( element );

        CHECK( maxdegrees1 == std::array<size_t, 2> { 4, 3 } );
        CHECK( maxdegrees2 == std::array<size_t, 2> { 4, 3 } );
        CHECK( maxdegrees3 == std::array<size_t, 2> { 4, 3 } );
        
        basis.prepareGridEvaluation( rst, cache1 );

        // Loop over evaluation coordinates in r and s
        for( size_t i = 0; i < rst[0].size( ); ++i )
        {
            for( size_t j = 0; j < rst[1].size( ); ++j )
            {
                std::array<double, 2> coordinates = { rst[0][i], rst[1][j] };

                basis.evaluateGridPoint( { i, j }, shapes1, cache1 );
                basis.evaluateSinglePoint( coordinates, shapes2, cache2 );

                for( const auto& shapesPtr : { &shapes1, &shapes2 } )
                {
                    const auto& shapes = *shapesPtr;
                
                    auto [field0, field1] = basisevaluation::expectedShapes( { 0, 0 }, coordinates );

                    testEqual( field0, shapes.get( 0, 0 ), shapes.get( 0, 1 ) );

                    testEqual( field1, shapes.get( 1, 0 ), shapes.get( 1, 1 ) );

                    if( maxdifforder >= 1 )
                    {
                        auto [field0D0, field1D0] = basisevaluation::expectedShapes( { 1, 0 }, coordinates );
                        auto [field0D1, field1D1] = basisevaluation::expectedShapes( { 0, 1 }, coordinates );

                        auto midpoint0 = std::midpoint( shapes.get( 0, 1 ), shapes.get( 0, 2 ) );
                        auto midpoint1 = std::midpoint( shapes.get( 1, 1 ), shapes.get( 1, 2 ) );

                        testEqual( field0D0, shapes.get( 0, 1 ), midpoint0 );
                        testEqual( field0D1, midpoint0, shapes.get( 0, 2 ) );

                        testEqual( field1D0, shapes.get( 1, 1 ), midpoint1 );
                        testEqual( field1D1, midpoint1, shapes.get( 1, 2 ) );
                    }

                    if( maxdifforder >= 2 )
                    {
                        auto [field0D0, field1D0] = basisevaluation::expectedShapes( { 2, 0 }, coordinates );
                        auto [field0D1, field1D1] = basisevaluation::expectedShapes( { 1, 1 }, coordinates );
                        auto [field0D2, field1D2] = basisevaluation::expectedShapes( { 0, 2 }, coordinates );

                        auto size0 = std::distance( shapes.get( 0, 2 ), shapes.get( 0, 3 ) );
                        auto size1 = std::distance( shapes.get( 1, 2 ), shapes.get( 1, 3 ) );

                        auto onethird0 = shapes.get( 0, 2 ) + size0 / 3;
                        auto twothird0 = onethird0 + size0 / 3;

                        auto onethird1 = shapes.get( 1, 2 ) + size1 / 3;
                        auto twothird1 = onethird1 + size1 / 3;

                        testEqual( field0D0, shapes.get( 0, 2 ), onethird0 );
                        testEqual( field0D1, onethird0, twothird0 );
                        testEqual( field0D2, twothird0, shapes.get( 0, 3 ) );

                        testEqual( field1D0, shapes.get( 1, 2 ), onethird1 );
                        testEqual( field1D1, onethird1, twothird1 );
                        testEqual( field1D2, twothird1, shapes.get( 1, 3 ) );
                    } 

                } // for shapes1 and shapes2

            } // for i grid point
        } // for j grid point
    } // for maxdifforder
}

TEST_CASE( "ElementFilterBasis_test" )
{
    /*   __________ __________ __________ __________
     *  | /  /  /  |          |          | /  /  /  |
     *  |/  /  /  /| 7  14 15 | 14 20 21 |/  /  /  /|
     *  |  /  /  / | 6  12 13 | 12 18 19 |  /  /  / |
     *  |_/__/__/__|__________|__________|_/__/__/__|
     *  | /  /  /  |          |          |          |
     *  |/  /  /  /| 6  12 13 | 12 18 19 | 18 24 25 |
     *  |  /  /  / | 3  9  11 | 9  16 17 | 16 22 23 |
     *  |_/__/__/__|__________|__________|__________|
     *  |          |          | /  /  /  | /  /  /  |
     *  | 1  3  5  | 3  9  11 |/  /  /  /|/  /  /  /|
     *  | 0  2  4  | 2  8  10 |  /  /  / |  /  /  / |
     *  |__________|__________|_/__/__/__|_/__/__/__|
     * 
     *  Numbering is sometimes a bit weird because of the influence
     *  of removed elements (e.g. left two elements influence left
     *  edge dofs in the second column of elements).
     */

    CellIndexVector filteredCells = { 1, 2, 6, 9, 11 };

    auto unfilteredGrid = makeRefinedGrid<2>( { 4, 3 }, { 4.0, 3.0 } );
    auto filteredGrid = std::make_shared<FilteredMesh<2>>( unfilteredGrid, filteredCells );
    
    auto degrees = std::array<size_t, 2> { 2, 1 };

    auto unfilteredBasis = makeHpBasis<TensorSpace>( unfilteredGrid, degrees, 2 );
    auto filteredBasis = std::make_shared<ElementFilterBasis<2>>( unfilteredBasis, filteredGrid );

    std::vector<LocationMap> expectedLocationMaps
    {
        { 0, 1, 2, 3, 4, 5 }, { 2, 3, 8, 9, 10, 11 },
        { 3, 6, 9, 12, 11, 13 }, { 6, 7, 12, 14, 13, 15 },
        { 9, 12, 16, 18, 17, 19 }, { 12, 14, 18, 20, 19, 21 },
        { 16, 18, 22, 24, 23, 25 }
    };

    LocationMap locationMap;

    REQUIRE( filteredBasis->nelements( ) == 7 );
    REQUIRE( filteredBasis->ndof( ) == 2 * 26 );
    CHECK( filteredBasis->nfields( ) == 2 );

    CHECK( &filteredBasis->mesh( ) == filteredGrid.get( ) );

    for( CellIndex icell = 0; icell < 7; ++icell )
    {
        locationMap.resize( 0 );

        filteredBasis->locationMap( icell, locationMap );

        auto& expected = expectedLocationMaps[icell];

        auto offsetted = []( auto dof1, auto dof2 ){ return dof1 + 26 == dof2; };

        CHECK( std::equal( expected.begin( ), expected.end( ), 
                           locationMap.begin( ) ) );

        CHECK( std::equal( expected.begin( ), expected.end( ),
                           locationMap.begin( ) + 6, offsetted ) );

    } // icell

    // Check basis function evaluation
    auto cache1 = filteredBasis->createEvaluationCache( );
    auto cache2 = unfilteredBasis->createEvaluationCache( );

    auto shapes1 = BasisFunctionEvaluation<2> { };
    auto shapes2 = BasisFunctionEvaluation<2> { };

    CHECK( filteredBasis->prepareEvaluation( 2, 0, shapes1, cache1 ) == degrees );
    CHECK( unfilteredBasis->prepareEvaluation( 4, 0, shapes2, cache2 ) == degrees );

    filteredBasis->evaluateSinglePoint( { 0.2, -0.6 }, shapes1, cache1 );
    unfilteredBasis->evaluateSinglePoint( { 0.2, -0.6 }, shapes2, cache2 );

    CHECK( std::equal( shapes1.get( 0, 0 ), shapes1.get( 2, 0 ), 
                       shapes2.get( 0, 0 ), shapes2.get( 2, 0 ) ) );

    CHECK( shapes1.rst( ) == shapes2.rst( ) );
    CHECK( shapes1.xyz( ) == shapes2.xyz( ) );
    CHECK( shapes1.elementIndex( ) == 2 );
    CHECK( shapes1.maxdifforder( ) == 0 );
    CHECK( shapes1.nfields( ) == 2 );

    auto& mapping1 = filteredBasis->mapping( cache1 );
    auto& mapping2 = unfilteredBasis->mapping( cache2 );

    CHECK( mapping1.icell == 2 );
    CHECK( mapping1.mesh == filteredGrid.get( ) );

    CHECK( mapping1( { -0.9, 0.3 } ) == mapping2( { -0.9, 0.3 } ) );

} // ElementFilterBasis_test

TEST_CASE( "faceDofs_test" )
{
    auto grid = makeRefinedGrid<2>( { 1, 1 }, { 1.0, 1.0 } );
    auto circle = implicit::sphere<2>( { }, 0.8 );

    grid->refine( refineTowardsDomainBoundary( circle, 3, 6 ) );

    auto templates = basis::createAnsatzTemplates( singlebasecell2d::inhomogeneousDegrees, 2 );
    auto basis = MultilevelHpBasis<2>( grid, templates, &initializeTensorSpaceMasks<2> );

    auto expected = singlebasecell2d::elementFaceDofs( );

    REQUIRE( basis.nelements( ) == expected.size( ) );

    std::vector<size_t> target0, target1, target2;

    for( CellIndex ielement = 0; ielement < basis.nelements( ); ++ielement )
    {
        for( size_t iedge = 0; iedge < 4; ++iedge )
        {
            target0.resize( 0 );
            target1.resize( 0 );
            target2.resize( 0 );

            auto offset0 = basis.faceDofs( ielement, iedge, 0, target0 );
            auto offset1 = basis.faceDofs( ielement, iedge, 1, target1 );
            auto offset2 = basis::faceDofsWithoutOffset( basis, ielement, iedge, 1, target2 );

            CHECK( offset0 == 0 );
            CHECK( offset1 == basis.ndofelement( ielement, 0 ) );
            CHECK( offset2 == basis.ndofelement( ielement, 0 ) );

            for( auto& entry : target1 )
            {
                entry -= offset1;
            }

            CHECK( target0 == expected[ielement][iedge] );
            CHECK( target1 == expected[ielement][iedge] );
            CHECK( target2 == expected[ielement][iedge] );
        }
    }
}

TEST_CASE( "findSupportingElements_test" )
{
    auto grid = makeRefinedGrid<2>( { 3, 3 }, { 1.0, 1.0 } );
    
    REQUIRE( grid->ncells( ) == 9 );

    grid->refine( refineCellIndices<2>( { { 0, 1, 5, 7 }, { 11, 14, 16 } } ) );
    
    REQUIRE( grid->ncells( ) == 30 );

    auto basis = makeHpBasis<TensorSpace>( grid, 1 );

    // Single element and dof
    {
        auto locationMap = basis::locationMap( *basis, 0 );

        auto [offsets, elements] = basis::findSupportElements( *basis, { locationMap[1] } );
        
        auto expectedOffsets = std::vector<size_t> { 0, 1 };
        auto expectedElements = std::vector<CellIndex> { 0 };

        CHECK( offsets == expectedOffsets );
        CHECK( elements == expectedElements );
    }

    // Multiple
    {
        auto dofIndices = std::vector
        {
            basis::locationMap( *basis, 1 )[1],
            basis::locationMap( *basis, 2 )[3],
            basis::locationMap( *basis, 12 )[0],
            basis::locationMap( *basis, 17 )[1],
            basis::locationMap( *basis, 24 )[1],
            basis::locationMap( *basis, 24 )[2],
            basis::locationMap( *basis, 3 )[3],
        };

        auto expectedElements = std::vector<CellIndex>
        {
            1,  2,  5,  6,  7,  8,  9,  10, 11, 18, 19, 20, 21,
            2,  4,  12, 13, 14, 15, 16, 17, 22, 23, 24, 25, 26, 27, 28, 29,
            12, 13, 22, 23, 24, 25, 26, 27, 28, 29,
            16, 17,
            24, 25, 26, 27,
            12, 13, 22, 23, 24, 25, 26, 27, 28, 29,
            3,  14, 15, 16, 17
        };

        auto expectedOffsets = std::vector<size_t>
        {
            0, 13, 29, 39, 41, 45, 55, 60
        };

        auto [offsets, elements] = basis::findSupportElements( *basis, dofIndices );

        CHECK( offsets == expectedOffsets );
        CHECK( elements == expectedElements );

        CHECK_NOTHROW( basis::findSupportElements( *basis, { } ) );
    }
}

TEST_CASE( "UnstructuredBasis2D_test" )
{
    static constexpr size_t D = 2;

    /*                     
     *  8 ---        0 --- 6
     *     |        / \   / \ _  
     *     |       /   \ /      \ 
     *  5 ---     4-----3         1
     *     |     /      |     _ / 
     *     |    /       | _ /    
     *  2 ---  2--------5
     *       
     *         |--|--|--|--|-------|
     *         1  2  3  4  5       8
     */
    
    auto vertices = CoordinateList<D>
    {
        { 3.0, 8.0 }, { 8.0, 5.0 }, { 1.0, 2.0 }, { 4.0, 5.0 },
        { 2.0, 5.0 }, { 4.0, 2.0 }, { 5.0, 8.0 }
    };

    auto connectivity = std::vector<size_t>
    {
        2, 4, 5, 3, 3, 6, 0, 4, 3, 0, 5, 1, 3, 6
    };

    auto offsets = std::vector<size_t>
    {
        0, 4, 7, 10, 14
    };

    auto mesh = std::make_shared<UnstructuredMesh<D>> ( std::move( 
        vertices ), std::move( connectivity ), std::move( offsets ) );

    auto basis = std::make_shared<UnstructuredBasis<D>>( mesh, 2 );
    
    CHECK( basis->nelements( ) == 4 );
    CHECK( basis->ndof( ) == 14 );
    CHECK( basis->nfields( ) == 2 );
    CHECK( basis->memoryUsage( ) == 0 );
    CHECK( &basis->mesh( ) == mesh.get( ) );

    auto ndofelement = std::array<size_t, 4> { 4, 3, 3, 4 };
    auto nfaces = std::array<size_t, 4> { 4, 3, 3, 4 };

    auto cellTypes = std::array
    { 
        CellType::NCube, 
        CellType::Simplex, 
        CellType::Simplex, 
        CellType::NCube 
    };

    auto locationMaps = std::vector<LocationMap>
    {
        { 4, 8, 10, 6, 5, 9, 11, 7 },
        { 6, 12, 0, 7, 13, 1 },
        { 8, 6, 0, 9, 7, 1 },
        { 10, 2, 6, 12, 11, 3, 7, 13 },
    };

    auto faceDofs0 = std::vector<std::vector<std::vector<size_t>>>
    {
        { { 0, 1 }, { 2, 3 }, { 0, 2 }, { 1, 3 } },
        { { 0, 2 }, { 0, 1 }, { 1, 2 } },
        { { 0, 2 }, { 0, 1 }, { 1, 2 } },
        { { 0, 1 }, { 2, 3 }, { 0, 2 }, { 1, 3 } }
    };
    
    auto faceDofs1 = std::vector<std::vector<std::vector<size_t>>>
    {
        { { 4, 5 }, { 6, 7 }, { 4, 6 }, { 5, 7 } },
        { { 3, 5 }, { 3, 4 }, { 4, 5 } },
        { { 3, 5 }, { 3, 4 }, { 4, 5 } },
        { { 4, 5 }, { 6, 7 }, { 4, 6 }, { 5, 7 } }
    };

    for( CellIndex ielement = 0; ielement < 4; ++ielement )
    {
        CHECK( basis->ndofelement( ielement, 0 ) == ndofelement[ielement] );
        CHECK( basis->ndofelement( ielement, 1 ) == ndofelement[ielement] );
        CHECK( basis->ndofelement( ielement ) == 2 * ndofelement[ielement] );
        CHECK( basis->maxdegrees( ielement ) == std::array<size_t, D> { 1, 1 } );

        auto locationMap = LocationMap { };

        basis->locationMap( ielement, locationMap );
        
        CHECK( locationMap == locationMaps[ielement] );
        REQUIRE( basis->mesh( ).nfaces( ielement ) == nfaces[ielement] );
        REQUIRE( basis->mesh( ).cellType( ielement ) == cellTypes[ielement] );

        for( size_t iface = 0; iface < nfaces[ielement]; ++iface )
        {
            auto faceDofs = std::vector<size_t> { };

            CHECK( basis->faceDofs( ielement, iface, 0, faceDofs ) == 0 );
            CHECK( faceDofs == faceDofs0[ielement][iface] );

            faceDofs.resize( 0 );
                        
            CHECK( basis->faceDofs( ielement, iface, 1, faceDofs ) == ndofelement[ielement] );
            CHECK( faceDofs == faceDofs1[ielement][iface] );
        }
    }

    auto cache = basis->createEvaluationCache( );
    auto shapes = BasisFunctionEvaluation<D> { };

    // Element 0
    basis->prepareEvaluation( 0, 1, shapes, cache );
    basis->evaluateSinglePoint( { 0.3, -0.4 }, shapes, cache );

    CHECK( spatial::distance<2>( shapes.rst( ), { 0.3, -0.4 } ) < 1e-8 );
    CHECK( spatial::distance<2>( shapes.xyz( ), { 3.055, 2.9 } ) < 1e-8 );

    CHECK( shapes.maxdifforder( ) == 1 );
    CHECK( shapes.elementIndex( ) == 0 );
    CHECK( shapes.nfields( ) == 2 );
    CHECK( shapes.ndof( 0 ) == 4 );
    CHECK( shapes.ndof( 1 ) == 4 );

    auto N = std::array { 0.35 * 0.7, 0.35 * 0.3, 0.65 * 0.7, 0.65 * 0.3 };

    auto dNdx = std::array { -42.0 / 162.0, -18.0 / 162.0,  42.0 / 162.0,  18.0 / 162.0 };
    auto dNdy = std::array { -14.0 / 162.0,  21.0 / 162.0, -40.0 / 162.0,  33.0 / 162.0 };

    for( size_t i = 0; i < 4; ++i )
    {
        CHECK( shapes.get( 0, 0 )[i] == Approx( N[i] ).epsilon( 1e-8 ) );
        CHECK( shapes.get( 1, 0 )[i] == Approx( N[i] ).epsilon( 1e-8 ) );

        CHECK( shapes.get( 0, 1 )[i] == Approx( dNdx[i] ).epsilon( 1e-8 ) );
        CHECK( shapes.get( 1, 1 )[i] == Approx( dNdx[i] ).epsilon( 1e-8 ) );

        auto n = shapes.ndofpadded( 0 );

        CHECK( shapes.get( 0, 1 )[i + n] == Approx( dNdy[i] ).epsilon( 1e-8 ) );
        CHECK( shapes.get( 1, 1 )[i + n] == Approx( dNdy[i] ).epsilon( 1e-8 ) );
    }

    // Element 3
    basis->prepareEvaluation( 3, 1, shapes, cache );
    basis->evaluateSinglePoint( { -0.9, 0.5 }, shapes, cache );
    
    CHECK( shapes.maxdifforder( ) == 1 );
    CHECK( shapes.elementIndex( ) == 3 );
    CHECK( shapes.nfields( ) == 2 );
    CHECK( shapes.ndof( 0 ) == 4 );
    CHECK( shapes.ndof( 1 ) == 4 );

    N = { 0.2375, 0.7125, 0.0125, 0.0375 };

    dNdx = { -0.1147540984,  0.278688524590, -0.049180327869, -0.114754098361 };
    dNdy = { -0.1693989071, -0.040983606557,  0.046448087432,  0.163934426230 };

    for( size_t i = 0; i < 4; ++i )
    {
        CHECK( shapes.get( 0, 0 )[i] == Approx( N[i] ).epsilon( 1e-8 ) );
        CHECK( shapes.get( 1, 0 )[i] == Approx( N[i] ).epsilon( 1e-8 ) );

        CHECK( shapes.get( 0, 1 )[i] == Approx( dNdx[i] ).epsilon( 1e-8 ) );
        CHECK( shapes.get( 1, 1 )[i] == Approx( dNdx[i] ).epsilon( 1e-8 ) );
        
        auto n = shapes.ndofpadded( 0 );
        
        CHECK( shapes.get( 0, 1 )[i + n] == Approx( dNdy[i] ).epsilon( 1e-8 ) );
        CHECK( shapes.get( 1, 1 )[i + n] == Approx( dNdy[i] ).epsilon( 1e-8 ) );
    }
}

TEST_CASE( "FieldFilterBasis_test" )
{
    auto degrees = AnsatzTemplateVector { { 4, 3, 2 } };

    for( size_t icell = 0; icell < 4; ++icell )
    {
        for( size_t axis = 0; axis < 2; ++axis )
        {
            degrees( icell, 0, axis ) = 2;
            degrees( icell, 1, axis ) = 1;
            degrees( icell, 2, axis ) = 3;
        }
    }

    auto grid = makeRefinedGrid<2>( { 2, 2 }, { 3.0, 2.0 }, { 2.0, 1.0 } );
    auto basis = std::make_shared<MultilevelHpBasis<2>>( grid, degrees, &initializeTensorSpaceMasks<2> );

    auto filtered0 = std::make_shared<FieldFilterBasis<2>>( basis, 0 );
    auto filtered1 = std::make_shared<FieldFilterBasis<2>>( basis, 1 );
    auto filtered2 = std::make_shared<FieldFilterBasis<2>>( basis, 2 );
    
    // Test general functions
    auto checkAll = [&]( auto& filtered )
    { 
        CHECK( &filtered->mesh( ) == grid.get( ) );
        CHECK( filtered->meshPtr( ) == grid );
        CHECK( filtered->maxdegrees( 2 ) == basis->maxdegrees( 2 ) );
        CHECK( filtered->nelements( ) == basis->nelements( ) );
        CHECK( filtered->nfields( ) == 1 );
        CHECK( filtered->memoryUsage( ) == sizeof( DofIndex ) * basis->ndof( ) );
    };

    checkAll( filtered0 );
    checkAll( filtered1 );
    checkAll( filtered2 );

    CHECK( basis->ndof( ) == 25 + 9 + 49 );

    CHECK( filtered0->ndof( ) == 25 );
    CHECK( filtered1->ndof( ) == 9 );
    CHECK( filtered2->ndof( ) == 49 );
        
    CHECK( filtered0->ndofelement( 1 ) == 9 );
    CHECK( filtered1->ndofelement( 1 ) == 4 );
    CHECK( filtered2->ndofelement( 1 ) == 16 );

    CHECK( filtered0->ndofelement( 1, 0 ) == 9 );
    CHECK( filtered1->ndofelement( 1, 0 ) == 4 );
    CHECK( filtered2->ndofelement( 1, 0 ) == 16 );

    // Check locationMap and faceDofs
    auto map = basis::locationMap( *basis, 1 );

    CHECK( basis::locationMap( *filtered0, 1 ) == LocationMap { 1, 9, 10, 4, 11, 12, 7, 13, 14 } );
    CHECK( basis::locationMap( *filtered1, 2 ) == LocationMap { 2, 3, 6, 7 } );
    CHECK( basis::locationMap( *filtered2, 3 ) == LocationMap { 5, 19, 20, 21, 29, 40, 41, 42, 33, 43, 44, 45, 37, 46, 47, 48 } );

    auto faceDofs = []( auto& basis_, CellIndex ielement, size_t iface )
    {
        auto localDofs = std::vector<size_t> { };

        auto offset = basis_->faceDofs( ielement, iface, 0, localDofs );

        CHECK( offset == 0 );

        return localDofs;
    };

    CHECK( faceDofs( filtered0, 3, 0 ) == std::vector<size_t> { 0, 1, 2 } );
    CHECK( faceDofs( filtered0, 1, 2 ) == std::vector<size_t> { 0, 3, 6 } );

    CHECK( faceDofs( filtered1, 1, 3 ) == std::vector<size_t> { 1, 3 } );
    CHECK( faceDofs( filtered1, 2, 2 ) == std::vector<size_t> { 0, 2 } );

    CHECK( faceDofs( filtered2, 2, 1 ) == std::vector<size_t> { 4, 5, 6, 7 } );
    CHECK( faceDofs( filtered2, 0, 3 ) == std::vector<size_t> { 1, 5, 9, 13 } );

    // Test shape function extraction
    auto checkFieldShapes = [&]( auto& filtered, size_t ifield, DofIndex ndof )
    { 
        auto cache = basis->createEvaluationCache( );
        auto cache1 = filtered->createEvaluationCache( );
        auto shapes = BasisFunctionEvaluation<2> { };
        auto shapes1 = BasisFunctionEvaluation<2> { };

        auto rstGrid = CoordinateGrid<2> { std::vector { -0.2, 0.4, 0.9 }, 
                                           std::vector { 0.3, 0.5, 0.7, 0.8 } };

        basis->prepareEvaluation( 2, 1, shapes, cache );
        basis->prepareGridEvaluation( rstGrid, cache );
        basis->evaluateGridPoint( { 2, 1 }, shapes, cache );

        filtered->prepareEvaluation( 2, 1, shapes1, cache1 );
        filtered->prepareGridEvaluation( rstGrid, cache1 );
        filtered->evaluateGridPoint( { 2, 1 }, shapes1, cache1 );

        CHECK( spatial::distance( shapes1.rst( ), shapes.rst( ) ) < 1e-10 );
        CHECK( spatial::distance( shapes1.xyz( ), shapes.xyz( ) ) < 1e-10 );
        CHECK( shapes1.elementIndex( ) == 2 );
        CHECK( shapes1.nfields( ) == 1 );
        CHECK( shapes1.ndof( ) == ndof );
        CHECK( shapes1.maxdifforder( ) == 1 );

        auto checkEqual = [&]( )
        {
            auto ncomponents = std::array { diff::ncomponents<2, 0>( ), diff::ncomponents<2, 1>( ) };

            for( size_t idiff = 0; idiff < 2; ++idiff )
            {
                for( size_t icomp = 0; icomp < ncomponents[idiff]; ++icomp )
                {
                    auto N = shapes.noalias( ifield, idiff );
                    auto N1 = shapes1.noalias( 0, idiff );

                    CHECK( utilities::floatingPointEqual( N, N + ndof, N1, 0.0 ) );
                }
            }
        };

        checkEqual( );

        basis->evaluateSinglePoint( { -0.14, -0.65 }, shapes, cache );
        filtered->evaluateSinglePoint( { -0.14, -0.65 }, shapes1, cache1 );

        checkEqual( );
    };

    checkFieldShapes( filtered0, 0, 9 );
    checkFieldShapes( filtered1, 1, 4 );
    checkFieldShapes( filtered2, 2, 16 );

    // Test index maps
    auto mask0 = std::vector<DofIndex>( 83, NoDof );
    auto mask1 = std::vector<DofIndex>( 83, NoDof );
    auto mask2 = std::vector<DofIndex>( 83, NoDof );

    std::iota( mask0.begin( ), mask0.begin( ) + 25, DofIndex { 0 } );
    std::iota( mask1.begin( ) + 25, mask1.begin( ) + 34, DofIndex { 0 } );
    std::iota( mask2.begin( ) + 34, mask2.end( ), DofIndex { 0 } );

    CHECK( filtered0->dofIndexMap( ) == mask0 );
    CHECK( filtered1->dofIndexMap( ) == mask1 );
    CHECK( filtered2->dofIndexMap( ) == mask2 );

    mask0 = std::vector<DofIndex>( 25 );
    mask1 = std::vector<DofIndex>( 9 );
    mask2 = std::vector<DofIndex>( 49 );

    std::iota( mask0.begin( ), mask0.end( ), DofIndex { 0 } );
    std::iota( mask1.begin( ), mask1.end( ), DofIndex { 25 } );
    std::iota( mask2.begin( ), mask2.end( ), DofIndex { 34 } );

    CHECK( filtered0->dofIndexMap( true ) == mask0 );
    CHECK( filtered1->dofIndexMap( true ) == mask1 );
    CHECK( filtered2->dofIndexMap( true ) == mask2 );

    // Test derivative projection
    auto f0 = []( std::array<double, 2> xy ) noexcept { return xy[0] * ( 2.0 - xy[1] ) + 4.0; };
    auto f1 = []( std::array<double, 2> xy ) noexcept { return 2.0 * xy[0] - xy[1] + 1.0; };
    auto f2 = []( std::array<double, 2> xy ) noexcept { return ( xy[0] + 1.0 ) * xy[0] * ( 2.0  + xy[1] ); };

    auto solver = linalg::makeCGSolver( 1e-14 );

    auto dofs = utilities::linearizeVectors<double>( { projectOnto<2>( *filtered0, f0, solver ),
        projectOnto<2>( *filtered1, f1, solver ), projectOnto<2>( *filtered2, f2, solver ) } );

    auto [dx, dy] = projectGradient( *basis, dofs, StandardQuadrature<2> { }, linalg::makeCGSolver( 1e-14 ) );

    auto fdx = basis::vectorEvaluator<2>( basis, dx );
    auto fdy = basis::vectorEvaluator<2>( basis, dy );

    auto expectedX = []( double x, double y ) { return std::array { 2.0 - y, 2.0, ( 2.0 * x + 1.0 ) * ( y + 2.0 ) }; };
    auto expectedY = []( double x, double   ) { return std::array { -x, -1.0, x * ( x + 1.0 ) }; };

    auto testCoordinates = CoordinateList<2>
    {
        { 2.3, 1.7 }, { 4.2, 1.2 }, { 3.9, 2.9 }, { 3.3, 1.7 }, 
        { 2.5, 2.5 }, { 2.0, 1.0 }, { 5.0, 3.0 }, { 5.0, 1.0 }
    };

    for( const auto& xyz : testCoordinates )
    {
        CHECK( spatial::distance( fdx.call<3>( xyz ), expectedX( xyz[0], xyz[1] ) ) < 1e-10 );
        CHECK( spatial::distance( fdy.call<3>( xyz ), expectedY( xyz[0], xyz[1] ) ) < 1e-10 );
    }
    
    //writeOutput( *basis, cellmesh::createGrid<2>( array::makeSizes<2>( 20 ) ), 
    //    std::tuple { makeSolutionProcessor<2>( dofs ) }, VtuOutput { "outputs/f" } );
    //writeOutput( *basis, cellmesh::createGrid<2>( array::makeSizes<2>( 20 ) ), 
    //    std::tuple { makeSolutionProcessor<2>( dx ) }, VtuOutput { "outputs/f_x" } );
    //writeOutput( *basis, cellmesh::createGrid<2>( array::makeSizes<2>( 20 ) ), 
    //    std::tuple { makeSolutionProcessor<2>( dy ) }, VtuOutput { "outputs/f_y" } );
}

TEST_CASE( "dofsSupportedOnElements_test" )
{
    /*
     *   Dof indices:                                    Element indices:
     * 
     *  15---19---17---33---31---47---45---61---59      
     *  |         |         |         |         |        _______ _______ _______ _______
     *  16   20   18   34   32   48   46   62   60      |       |       |       |       |
     *  |         |         |         |         |       |   2   |   5   |   8   |   11  |
     *  9----13---11---29---27---43---41---57---55      |_______|_______|_______|_______|
     *  |         |         |         |         |       |       |       |       |       |
     *  10   14   12   30   28   44   42   58   56      |   1   |   4   |   7   |   10  |
     *  |         |         |         |         |       |_______|_______|_______|_______|
     *  1----7----4----25---22---39---36---53---50      |       |       |       |       |
     *  |         |         |         |         |       |   0   |   3   |   6   |   9   |
     *  2    8    5    26   23   40   37   54   51      |_______|_______|_______|_______|
     *  |         |         |         |         |
     *  0----6----3----24---21---38---35---52---49
     */

    auto mesh = makeRefinedGrid<2>( { 4, 3 }, { 3.0, 4.0 } );
    auto basis = makeHpBasis<TensorSpace>( mesh, 2 );

    auto dofs = basis::findSupportedDofs( *basis, { 4, 8 } );

    CHECK( dofs == std::vector<DofIndex> { 4, 11, 12, 22, 25, 
        27, 28, 29, 30, 31, 32, 41, 43, 45, 46, 47, 48 } );

    dofs = basis::findSupportedDofs( *basis, { 4, 8 }, { }, true );

    CHECK( dofs == std::vector<DofIndex> { 30, 47, 48 } );

    dofs = basis::findSupportedDofs( *basis, { 0, 1, 2,
        3, 5, 6, 7, 9, 10, 11 }, { }, false, true );

    CHECK( dofs == std::vector<DofIndex> { 30, 47, 48 } );

    dofs = basis::findSupportedDofs( *basis, { 4, 8, 7 },
        { 17, 33, 31, 47, 45, 61 } );

    CHECK( dofs == std::vector<DofIndex> { 4, 11, 12, 21, 24,
        26, 27, 28, 29, 30, 33, 36, 38, 39, 40, 41, 42, 43 } );

    dofs = basis::findSupportedDofs( *basis, { 4, 8, 7 },
        { 17, 33, 31, 47, 45, 61 }, true );
    
    CHECK( dofs == std::vector<DofIndex> { 27, 29, 40, 41, 43 } );
    
    dofs = basis::findSupportedDofs( *basis, { 0, 1, 2, 3, 5,
        6, 9, 10, 11 }, { 17, 33, 31, 47, 45, 61 }, true, true );
        
    CHECK( dofs == std::vector<DofIndex> { 4, 11, 12, 21, 24,
        26, 27, 28, 29, 30, 33, 36, 38, 39, 40, 41, 42, 43 } );
}

TEST_CASE( "BSplineBasis_test" )
{
    auto degrees = std::vector<std::array<size_t, 2>> { { 2, 3 }, { 3, 1 }, { 1, 2 } };
    auto continuities = std::vector<std::array<size_t, 2>> { { 1, 1 }, { 2, 0 }, { 0, 0 } };

    auto mesh = makeCartesianGrid<2>( { 2, 3 }, { 4.0, 3.0 }, { 6.0, 5.0 } );
    auto basis = BSplineBasis<2>( mesh, degrees, continuities );

    CHECK( basis.ndof( ) == 73 );
    CHECK( basis.ndofelement( 3, 0 ) == 3 * 4 );
    CHECK( basis.ndofelement( 0, 1 ) == 4 * 2 );
    CHECK( basis.ndofelement( 1, 2 ) == 2 * 3 );
    CHECK( basis.ndofelement( 2 ) == 3 * 4 + 4 * 2 + 2 * 3 );
    CHECK( basis.nelements( ) == 6 );
    CHECK( basis.maxdegrees( 4 ) == std::array<size_t, 2>{ 3, 3 } );
    CHECK( basis.nfields( ) == 3 );
    CHECK( &basis.mesh( ) == mesh.get( ) );
    CHECK( basis.meshPtr( ).get( ) == mesh.get( ) );
    
    auto cache = basis.createEvaluationCache( );
    auto shapes = BasisFunctionEvaluation<2> { };
    auto rstGrid = std::array { std::vector { -0.2, 0.6 }, std::vector { -0.5, 0.0, 0.5 } };

    basis.prepareEvaluation( 1, /* 2 */ 1, shapes, cache );

    CHECK( shapes.elementIndex( ) == 1 );
    CHECK( shapes.maxdifforder( ) == /* 2 */ 1 );
    CHECK( shapes.nfields( ) == 3 );
    CHECK( shapes.ndof( 0 ) == 3 * 4 );
    CHECK( shapes.ndof( 1 ) == 4 * 2 );
    CHECK( shapes.ndof( 2 ) == 2 * 3 );
    CHECK( shapes.ndof( ) == 3 * 4 + 4 * 2 + 2 * 3 );

    basis.prepareGridEvaluation( rstGrid, cache );
    basis.evaluateGridPoint( { 1, 2 }, shapes, cache );

    CHECK( shapes.rst( ) == std::array{ 0.6, 0.5 } );
    CHECK( shapes.xyz( ) == mesh::map( *mesh, 1, std::array{ 0.6, 0.5 } ) );
    CHECK( basis.ndofelement( 3 ) == basis::locationMap( basis, 2 ).size( ) );

    auto f = spatial::VectorFunction<2, 3>( [=]( std::array<double, 2> xy )
    {
        auto [x, y] = xy;

        if( !spatial::insideBoundingBox<2>( mesh->boundingBox( ), xy ) )
        {
            return std::array { 0.0, 0.0, 0.0 };
        }

        return std::array 
        { 
            ( x - 6.0 ) * ( 10.0 - x ) * ( y - 5.0 ) * std::pow( 8.0 - y, 2 ), 
            ( x - 5.0 ) * ( 11.0 - x ) * ( x - 8.0 ) + ( y - 3.0 ),
            std::abs( x - 8.0 ) + std::abs( y - 6.0 ) * std::abs( y - 7.0 )
        };
    } );

    auto df = spatial::VectorFunction<2, 6>( [=]( std::array<double, 2> xy )
    {
        auto [x, y] = xy;

        if( !spatial::insideBoundingBox<2>( mesh->boundingBox( ), xy ) )
        {
            return array::make<6>( 0.0 );
        }

        return std::array
        {
            ( 16.0 - 2.0 * x ) * ( y - 5.0 ) * std::pow( 8.0 - y, 2 ),
            ( x - 6.0 ) * ( 10.0 - x ) * 3.0 * ( y * y - 14.0 * y + 48.0 ),
            -3.0 * ( x * x - 16.0 * x + 61.0 ),
            1.0,
            x < 8.0 ? -1.0 : 1.0,
            2.0 * ( y - 6.5 ) * ( std::abs( y - 6.5 ) > 0.5 ? 1.0 : -1.0 )
        };
    } );

    auto dofs = projectOnto<2>( basis, f );
    auto u = basis::vectorEvaluator<2>( basis, dofs, 0 );
    auto du = basis::vectorEvaluator<2>( basis, dofs, 1 );

    // Make sure f is defined properly and just zero
    CHECK( spatial::distance<3>( f.call<3>( { 8.4, 7.2 } ), { 5.40672, 7.736, 0.64 } ) < 1e-12 );

    auto xsamples = utilities::linspace( 6.0 - 2.0 / 3.0, 10.0 + 2.0 / 3.0, 9 );
    auto ysamples = utilities::linspace( 5.0 - 1.0 / 3.0, 8.0 + 1.0 / 3.0, 12 );

    auto equal0 = true;
    auto equal1 = true;

    for( auto x : xsamples )
    {
        for( auto y : ysamples )
        {
            auto xy0 = std::array { x, y };
            auto xy1 = std::array { x + 1e-8, y + 1e-8 }; // To prevent ambiguous derivatives on element interfaces

            equal0 = equal0 && spatial::distance( u.call<3>( xy0 ), f.call<3>( xy0 ) ) < 1e-10;
            equal1 = equal1 && spatial::distance( du.call<6>( xy1 ), df.call<6>( xy1 ) ) < 1e-10;
        }
    }

    CHECK( equal0 );
    CHECK( equal1 );

    //auto cellMesh = cellmesh::grid<2>( array::makeSizes<2>( 100 ) );
    //auto processors = std::tuple { makeSolutionProcessor<2>( dofs ), makeFunctionProcessor<2>( f, "F" ), makeFunctionProcessor<2>( df, "dF" ) };

    //writeOutput( basis, cellMesh, processors, VtuOutput { testing::outputPath( "core/bsplinebasis.vtu" ) } );
    
    // =============
    
    //for( size_t idof = 0; idof < basis.ndof( ); ++idof )
    //{
    //    auto processors = std::tuple
    //    {
    //        makeShapeFunctionProcessor<2>( { idof }, 0, 0, "shapes" ),
    //        //makeShapeFunctionProcessor<2>( { idof }, 2, 0, "diff20" ),
    //        //makeShapeFunctionProcessor<2>( { idof }, 2, 1, "diff11" ),
    //        //makeShapeFunctionProcessor<2>( { idof }, 2, 2, "diff02" ),
    //        makeShapeFunctionProcessor<2>( { idof }, 1, 0, "diff0" ),
    //        makeShapeFunctionProcessor<2>( { idof }, 1, 1, "diff1" )
    //    };

    //    auto cellMesh = cellmesh::grid<2>( array::makeSizes<2>( 100 ) );

    //    writeOutput( basis, cellMesh, processors, VtuOutput{ "outputs/shapes_" +
    //        std::to_string( idof ) + ".vtu" } );
    //}
}

} // namespace mlhp
