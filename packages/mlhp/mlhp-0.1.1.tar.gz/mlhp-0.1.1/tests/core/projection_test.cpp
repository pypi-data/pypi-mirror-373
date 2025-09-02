// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/partitioning.hpp"
#include "mlhp/core/mesh.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/refinement.hpp"

namespace mlhp
{
namespace meshintersectiontest
{

template<size_t D>
using MinMax = std::vector<std::array<std::array<double, D>, 2>>;

template<size_t D>
void checkCorrectIntersection( const HierarchicalGridSharedPtr<D>& thisMesh,
                               const HierarchicalGridSharedPtr<D>& otherMesh,
                               const MeshProjectionQuadrature<D>& partitioner,
                               std::vector<size_t> indices,
                               const MinMax<D>& local1,
                               const MinMax<D>& local2,
                               const MinMax<D>& globalMinMax )
{
    auto cache = partitioner.initialize( );
    auto mapping = thisMesh->createMapping( );

    REQUIRE( thisMesh->nleaves( ) + 1u == indices.size( ) );

    CoordinateGrid<D> thisRstGrid, otherRstGrid;
    CoordinateList<D> xyzList;
    std::vector<double> weights;

    bool correctThisLocal = true;
    bool correctOtherLocal = true;
    bool correctGlobal = true;
    bool correctWeight = true;
    bool correctOtherElement = true;

    double tolerance = 1e-12;
    double gauss = 1.0 / std::sqrt( 3 );

    auto integrationOrders = array::makeSizes<D>( 2 );
    auto backwardMapping = otherMesh->createBackwardMapping( );

    for( CellIndex iCell = 0; iCell < thisMesh->nleaves( ); ++iCell )
    {
        thisMesh->prepareMapping( iCell, mapping );

        size_t ncells = partitioner.partition( mapping, cache );

        REQUIRE( ncells == ( indices[iCell + 1] - indices[iCell] ) );

        for( size_t iPartition = 0; iPartition < ncells; ++iPartition )
        {
            auto otherElement = partitioner.distribute( iPartition, integrationOrders,
                thisRstGrid, otherRstGrid, xyzList, weights, cache );

            auto index = indices[iCell] + iPartition;

            auto [local1Min, local1Max] = local1[index];
            auto [local2Min, local2Max] = local2[index];
            auto [globalMin, globalMax] = globalMinMax[index];

            auto reverseMap = backwardMapping->map( array::multiply( array::add( globalMin, globalMax ), 0.5 ) );

            correctOtherElement = correctOtherElement && ( reverseMap && otherMesh->fullIndex( reverseMap->first ) == otherElement );

            double expectedDetJ = array::product( array::subtract( globalMax, globalMin ) ) / std::pow( 2.0, D );

            for( size_t axis = 0; axis < D; ++axis )
            {
                for( size_t end = 0; end < 2; ++end )
                {
                    double computedGaussLocal1 = thisRstGrid[axis][end];
                    double computedGaussLocal2 = otherRstGrid[axis][end];
                    double computedGaussGlobal = end == 0 ? xyzList.front( )[axis] : xyzList.back( )[axis];

                    double expected1 = utilities::mapToLocal1( local1Min[axis], local1Max[axis], computedGaussLocal1 );
                    double expected2 = utilities::mapToLocal1( local2Min[axis], local2Max[axis], computedGaussLocal2 );
                    double expected3 = utilities::mapToLocal1( globalMin[axis], globalMax[axis], computedGaussGlobal );

                    double sign = end == 0 ? -1.0 : 1.0;

                    auto checkEqual = [=]( double expected, bool& result )
                    {
                        result = result && std::abs( ( expected - sign * gauss ) / expected ) < tolerance;
                    };

                    checkEqual( expected1, correctThisLocal );
                    checkEqual( expected2, correctOtherLocal );
                    checkEqual( expected3, correctGlobal );

                    double computedWeight = ( end == 0 ? weights.front( ) : weights.back( ) );
                    
                    correctWeight = correctWeight && std::abs( ( computedWeight - expectedDetJ ) / expectedDetJ ) < tolerance;

                } // for end
            } // for axis
        } // for iPartition
    } // for iCell

    CHECK( correctThisLocal );
    CHECK( correctOtherLocal );
    CHECK( correctGlobal );
    CHECK( correctWeight );
    CHECK( correctOtherElement );
}

// Partition mesh 2 with respect to mesh 1 and point (1.6, 0.9)
auto solution2D_2( )
{
    std::vector<size_t> numberOfPartitions( 39, 1 );

    numberOfPartitions[2] = 28;
    numberOfPartitions[6] = 7;
    numberOfPartitions[15] = 7;

    std::vector<size_t> indices( numberOfPartitions.size( ) + 1, 0 );

    std::partial_sum( numberOfPartitions.begin( ), numberOfPartitions.end( ), indices.begin( ) + 1 );

    // Bottom left and top right corners in global coordinates
    MinMax<2> global( indices.back( ) );

    // iCell iPartition (xmin, ymin) (xmax, ymax)
    global[indices[0 ] + 0 ] = {{ { 1.0,  0.5   }, { 1.2,  0.9   } }};
    global[indices[1 ] + 0 ] = {{ { 1.0,  0.9   }, { 1.2,  1.5   } }};
    global[indices[2 ] + 0 ] = {{ { 1.2,  0.5   }, { 1.4,  0.6   } }}; // sub cell  0, partition 0
    global[indices[2 ] + 1 ] = {{ { 1.2,  0.6   }, { 1.4,  0.7   } }}; // sub cell  1, partition 0
    global[indices[2 ] + 2 ] = {{ { 1.4,  0.5   }, { 1.6,  0.6   } }}; // sub cell  2, partition 0
    global[indices[2 ] + 3 ] = {{ { 1.4,  0.6   }, { 1.6,  0.7   } }}; // sub cell  3, partition 0
    global[indices[2 ] + 4 ] = {{ { 1.2,  0.7   }, { 1.4,  0.8   } }}; // sub cell  4, partition 0
    global[indices[2 ] + 5 ] = {{ { 1.2,  0.8   }, { 1.4,  0.9   } }}; // sub cell  5, partition 0
    global[indices[2 ] + 6 ] = {{ { 1.4,  0.7   }, { 1.6,  0.8   } }}; // sub cell  6, partition 0
    global[indices[2 ] + 7 ] = {{ { 1.4,  0.8   }, { 1.5,  0.85  } }}; // sub cell  7, partition 0
    global[indices[2 ] + 8 ] = {{ { 1.4,  0.85  }, { 1.5,  0.9   } }}; // sub cell  7, partition 1
    global[indices[2 ] + 9 ] = {{ { 1.5,  0.8   }, { 1.6,  0.85  } }}; // sub cell  7, partition 2
    global[indices[2 ] + 10] = {{ { 1.5,  0.85  }, { 1.55, 0.875 } }}; // sub cell  7, partition 3
    global[indices[2 ] + 11] = {{ { 1.5,  0.875 }, { 1.55, 0.9   } }}; // sub cell  7, partition 4
    global[indices[2 ] + 12] = {{ { 1.55, 0.85  }, { 1.6,  0.875 } }}; // sub cell  7, partition 5
    global[indices[2 ] + 13] = {{ { 1.55, 0.875 }, { 1.6,  0.9   } }}; // sub cell  7, partition 6
    global[indices[2 ] + 14] = {{ { 1.6,  0.5   }, { 1.8,  0.6   } }}; // sub cell  8, partition 0
    global[indices[2 ] + 15] = {{ { 1.6,  0.6   }, { 1.8,  0.7   } }}; // sub cell  9, partition 0
    global[indices[2 ] + 16] = {{ { 1.8,  0.5   }, { 2.0,  0.6   } }}; // sub cell 10, partition 0
    global[indices[2 ] + 17] = {{ { 1.8,  0.6   }, { 2.0,  0.7   } }}; // sub cell 11, partition 0
    global[indices[2 ] + 18] = {{ { 1.6,  0.7   }, { 1.8,  0.8   } }}; // sub cell 12, partition 0
    global[indices[2 ] + 19] = {{ { 1.6,  0.8   }, { 1.7,  0.85  } }}; // sub cell 13, partition 0
    global[indices[2 ] + 24] = {{ { 1.7,  0.8   }, { 1.8,  0.85  } }}; // sub cell 13, partition 1
    global[indices[2 ] + 25] = {{ { 1.7,  0.85  }, { 1.8,  0.9   } }}; // sub cell 13, partition 2
    global[indices[2 ] + 20] = {{ { 1.6,  0.85  }, { 1.65, 0.875 } }}; // sub cell 13, partition 3
    global[indices[2 ] + 21] = {{ { 1.6,  0.875 }, { 1.65, 0.9   } }}; // sub cell 13, partition 4
    global[indices[2 ] + 22] = {{ { 1.65, 0.85  }, { 1.7,  0.875 } }}; // sub cell 13, partition 5
    global[indices[2 ] + 23] = {{ { 1.65, 0.875 }, { 1.7,  0.9   } }}; // sub cell 13, partition 6
    global[indices[2 ] + 26] = {{ { 1.8,  0.7   }, { 2.0,  0.8   } }}; // sub cell 14, partition 0
    global[indices[2 ] + 27] = {{ { 1.8,  0.8   }, { 2.0,  0.9   } }}; // sub cell 15, partition 0
    global[indices[3 ] + 0 ] = {{ { 1.0,  1.5   }, { 1.1,  1.65  } }};
    global[indices[4 ] + 0 ] = {{ { 1.0,  1.65  }, { 1.1,  1.8   } }};
    global[indices[5 ] + 0 ] = {{ { 1.1,  1.5   }, { 1.2,  1.65  } }};
    global[indices[6 ] + 0 ] = {{ { 1.2,  0.9   }, { 1.4,  1.05  } }}; // partition 0
    global[indices[6 ] + 1 ] = {{ { 1.2,  1.05  }, { 1.4,  1.2   } }}; // partition 1
    global[indices[6 ] + 6 ] = {{ { 1.4,  1.05  }, { 1.6,  1.2   } }}; // partition 2
    global[indices[6 ] + 2 ] = {{ { 1.4,  0.9   }, { 1.5,  0.975 } }}; // partition 3
    global[indices[6 ] + 3 ] = {{ { 1.4,  0.975 }, { 1.5,  1.05  } }}; // partition 4
    global[indices[6 ] + 4 ] = {{ { 1.5,  0.9   }, { 1.6,  0.975 } }}; // partition 5
    global[indices[6 ] + 5 ] = {{ { 1.5,  0.975 }, { 1.6,  1.05  } }}; // partition 6
    global[indices[7 ] + 0 ] = {{ { 1.1,  1.65  }, { 1.15, 1.725 } }};
    global[indices[8 ] + 0 ] = {{ { 1.1,  1.725 }, { 1.15, 1.8   } }};
    global[indices[9 ] + 0 ] = {{ { 1.15, 1.65  }, { 1.2,  1.725 } }};
    global[indices[10] + 0 ] = {{ { 1.15, 1.725 }, { 1.2,  1.8   } }};
    global[indices[11] + 0 ] = {{ { 1.2,  1.2   }, { 1.4,  1.35  } }};
    global[indices[12] + 0 ] = {{ { 1.2,  1.35  }, { 1.4,  1.5   } }};
    global[indices[13] + 0 ] = {{ { 1.4,  1.2   }, { 1.6,  1.35  } }};
    global[indices[14] + 0 ] = {{ { 1.4,  1.35  }, { 1.6,  1.5   } }};
    global[indices[15] + 4 ] = {{ { 1.6,  0.975 }, { 1.7,  1.05  } }}; // partition 0
    global[indices[15] + 5 ] = {{ { 1.7,  0.9   }, { 1.8,  0.975 } }}; // partition 1
    global[indices[15] + 6 ] = {{ { 1.7,  0.975 }, { 1.8,  1.05  } }}; // partition 2
    global[indices[15] + 0 ] = {{ { 1.6,  0.9   }, { 1.65, 0.9375} }}; // partition 3
    global[indices[15] + 1 ] = {{ { 1.6,  0.9375}, { 1.65, 0.975 } }}; // partition 4
    global[indices[15] + 2 ] = {{ { 1.65, 0.9   }, { 1.7,  0.9375} }}; // partition 5
    global[indices[15] + 3 ] = {{ { 1.65, 0.9375}, { 1.7,  0.975 } }}; // partition 6
    global[indices[16] + 0 ] = {{ { 1.6,  1.05  }, { 1.8,  1.2   } }};
    global[indices[17] + 0 ] = {{ { 1.8,  0.9   }, { 2.0,  1.05  } }};
    global[indices[18] + 0 ] = {{ { 1.8,  1.05  }, { 2.0,  1.2   } }};
    global[indices[19] + 0 ] = {{ { 1.6,  1.2   }, { 1.8,  1.35  } }};
    global[indices[20] + 0 ] = {{ { 1.6,  1.35  }, { 1.8,  1.5   } }};
    global[indices[21] + 0 ] = {{ { 1.8,  1.2   }, { 2.0,  1.35  } }};
    global[indices[22] + 0 ] = {{ { 1.8,  1.35  }, { 2.0,  1.5   } }};
    global[indices[23] + 0 ] = {{ { 1.2,  1.5   }, { 1.4,  1.575 } }};
    global[indices[24] + 0 ] = {{ { 1.2,  1.575 }, { 1.4,  1.65  } }};
    global[indices[25] + 0 ] = {{ { 1.4,  1.5   }, { 1.6,  1.575 } }};
    global[indices[26] + 0 ] = {{ { 1.4,  1.575 }, { 1.6,  1.65  } }};
    global[indices[27] + 0 ] = {{ { 1.2,  1.65  }, { 1.4,  1.725 } }};
    global[indices[28] + 0 ] = {{ { 1.2,  1.725 }, { 1.4,  1.8   } }};
    global[indices[29] + 0 ] = {{ { 1.4,  1.65  }, { 1.6,  1.725 } }};
    global[indices[30] + 0 ] = {{ { 1.4,  1.725 }, { 1.6,  1.8   } }};
    global[indices[31] + 0 ] = {{ { 1.6,  1.5   }, { 1.8,  1.575 } }};
    global[indices[32] + 0 ] = {{ { 1.6,  1.575 }, { 1.8,  1.65  } }};
    global[indices[33] + 0 ] = {{ { 1.8,  1.5   }, { 2.0,  1.575 } }};
    global[indices[34] + 0 ] = {{ { 1.8,  1.575 }, { 2.0,  1.65  } }};
    global[indices[35] + 0 ] = {{ { 1.6,  1.65  }, { 1.8,  1.725 } }};
    global[indices[36] + 0 ] = {{ { 1.6,  1.725 }, { 1.8,  1.8   } }};
    global[indices[37] + 0 ] = {{ { 1.8,  1.65  }, { 2.0,  1.725 } }};
    global[indices[38] + 0 ] = {{ { 1.8,  1.725 }, { 2.0,  1.8   } }};

    // Bottom left and top right corners in local coordinates
    std::array<std::array<double, 2>, 2> defaultLocalMinMax {{ { -1.0, -1.0 }, { 1.0, 1.0 } }};

    MinMax<2> thisLocal( global.size( ), defaultLocalMinMax );
    MinMax<2> otherLocal( global.size( ), defaultLocalMinMax );

    thisLocal[indices[2] + 0 ] = {{ { -1.0,  -1.0   }, { -0.5,  -0.5   } }}; // sub cell  0, partition 0
    thisLocal[indices[2] + 1 ] = {{ { -1.0,  -0.5   }, { -0.5,   0.0   } }}; // sub cell  1, partition 0
    thisLocal[indices[2] + 2 ] = {{ { -0.5,  -1.0   }, {  0.0,  -0.5   } }}; // sub cell  2, partition 0
    thisLocal[indices[2] + 3 ] = {{ { -0.5,  -0.5   }, {  0.0,   0.0   } }}; // sub cell  3, partition 0
    thisLocal[indices[2] + 4 ] = {{ { -1.0,   0.0   }, { -0.5,   0.5   } }}; // sub cell  4, partition 0
    thisLocal[indices[2] + 5 ] = {{ { -1.0,   0.5   }, { -0.5,   1.0   } }}; // sub cell  5, partition 0
    thisLocal[indices[2] + 6 ] = {{ { -0.5,   0.0   }, {  0.0,   0.5   } }}; // sub cell  6, partition 0
    thisLocal[indices[2] + 7 ] = {{ { -0.5,   0.5   }, { -0.25,  0.75  } }}; // sub cell  7, partition 0
    thisLocal[indices[2] + 8 ] = {{ { -0.5,   0.75  }, { -0.25,  1.0   } }}; // sub cell  7, partition 1
    thisLocal[indices[2] + 9 ] = {{ { -0.25,  0.5   }, {  0.0,   0.75  } }}; // sub cell  7, partition 2
    thisLocal[indices[2] + 10] = {{ { -0.25,  0.75  }, { -0.125, 0.875 } }}; // sub cell  7, partition 3
    thisLocal[indices[2] + 11] = {{ { -0.25,  0.875 }, { -0.125, 1.0   } }}; // sub cell  7, partition 4
    thisLocal[indices[2] + 12] = {{ { -0.125, 0.75  }, {  0.0,   0.875 } }}; // sub cell  7, partition 5
    thisLocal[indices[2] + 13] = {{ { -0.125, 0.875 }, {  0.0,   1.0   } }}; // sub cell  7, partition 6
    thisLocal[indices[2] + 14] = {{ {  0.0,  -1.0   }, {  0.5,  -0.5   } }}; // sub cell  8, partition 0
    thisLocal[indices[2] + 15] = {{ {  0.0,  -0.5   }, {  0.5,   0.0   } }}; // sub cell  9, partition 0
    thisLocal[indices[2] + 16] = {{ {  0.5,  -1.0   }, {  1.0,  -0.5   } }}; // sub cell 10, partition 0
    thisLocal[indices[2] + 17] = {{ {  0.5,  -0.5   }, {  1.0,   0.0   } }}; // sub cell 11, partition 0
    thisLocal[indices[2] + 18] = {{ {  0.0,   0.0   }, {  0.5,   0.5   } }}; // sub cell 12, partition 0
    thisLocal[indices[2] + 19] = {{ {  0.0,   0.5   }, {  0.25,  0.75  } }}; // sub cell 13, partition 0
    thisLocal[indices[2] + 24] = {{ {  0.25,  0.5   }, {  0.5,   0.75  } }}; // sub cell 13, partition 1
    thisLocal[indices[2] + 25] = {{ {  0.25,  0.75  }, {  0.5,   1.0   } }}; // sub cell 13, partition 2
    thisLocal[indices[2] + 20] = {{ {  0.0,   0.75  }, {  0.125, 0.875 } }}; // sub cell 13, partition 3
    thisLocal[indices[2] + 21] = {{ {  0.0,   0.875 }, {  0.125, 1.0   } }}; // sub cell 13, partition 4
    thisLocal[indices[2] + 22] = {{ {  0.125, 0.75  }, {  0.25,  0.875 } }}; // sub cell 13, partition 5
    thisLocal[indices[2] + 23] = {{ {  0.125, 0.875 }, {  0.25,  1.0   } }}; // sub cell 13, partition 6
    thisLocal[indices[2] + 26] = {{ {  0.5,   0.0   }, {  1.0,   0.5   } }}; // sub cell 14, partition 0
    thisLocal[indices[2] + 27] = {{ {  0.5,   0.5   }, {  1.0,   1.0   } }}; // sub cell 15, partition 0

    thisLocal[indices[6] + 0] = {{ { -1.0, -1.0 }, {  0.0,  0.0 } }}; // partition 0
    thisLocal[indices[6] + 1] = {{ { -1.0,  0.0 }, {  0.0,  1.0 } }}; // partition 1
    thisLocal[indices[6] + 6] = {{ {  0.0,  0.0 }, {  1.0,  1.0 } }}; // partition 2
    thisLocal[indices[6] + 2] = {{ {  0.0, -1.0 }, {  0.5, -0.5 } }}; // partition 3
    thisLocal[indices[6] + 3] = {{ {  0.0, -0.5 }, {  0.5,  0.0 } }}; // partition 4
    thisLocal[indices[6] + 4] = {{ {  0.5, -1.0 }, {  1.0, -0.5 } }}; // partition 5
    thisLocal[indices[6] + 5] = {{ {  0.5, -0.5 }, {  1.0,  0.0 } }}; // partition 6

    thisLocal[indices[15] + 4] = { { { -1.0,  0.0 }, {  0.0,  1.0 } } }; // partition 0
    thisLocal[indices[15] + 5] = { { {  0.0, -1.0 }, {  1.0,  0.0 } } }; // partition 1
    thisLocal[indices[15] + 6] = { { {  0.0,  0.0 }, {  1.0,  1.0 } } }; // partition 2
    thisLocal[indices[15] + 0] = { { { -1.0, -1.0 }, { -0.5, -0.5 } } }; // partition 3
    thisLocal[indices[15] + 1] = { { { -1.0, -0.5 }, { -0.5,  0.0 } } }; // partition 4
    thisLocal[indices[15] + 2] = { { { -0.5, -1.0 }, {  0.0, -0.5 } } }; // partition 5
    thisLocal[indices[15] + 3] = { { { -0.5, -0.5 }, {  0.0,  0.0 } } }; // partition 6
    
    otherLocal[indices[2 ] + 7 ] = {{ { -1.0, -1.0 }, {  0.0,  0.0 } }};
    otherLocal[indices[2 ] + 8 ] = {{ { -1.0,  0.0 }, {  0.0,  1.0 } }};
    otherLocal[indices[2 ] + 9 ] = {{ {  0.0, -1.0 }, {  1.0,  0.0 } }};
    otherLocal[indices[2 ] + 10] = {{ {  0.0,  0.0 }, {  0.5,  0.5 } }};
    otherLocal[indices[2 ] + 11] = {{ {  0.0,  0.5 }, {  0.5,  1.0 } }};
    otherLocal[indices[2 ] + 12] = {{ {  0.5,  0.0 }, {  1.0,  0.5 } }};
    otherLocal[indices[2 ] + 13] = {{ {  0.5,  0.5 }, {  1.0,  1.0 } }};
    
    otherLocal[indices[2 ] + 19] = {{ { -1.0, -1.0 }, {  0.0,  0.0 } }}; // partition 0 
    otherLocal[indices[2 ] + 24] = {{ {  0.0, -1.0 }, {  1.0,  0.0 } }}; // partition 1 
    otherLocal[indices[2 ] + 25] = {{ {  0.0,  0.0 }, {  1.0,  1.0 } }}; // partition 2 
    otherLocal[indices[2 ] + 20] = {{ { -1.0,  0.0 }, { -0.5,  0.5 } }}; // partition 3 
    otherLocal[indices[2 ] + 21] = {{ { -1.0,  0.5 }, { -0.5,  1.0 } }}; // partition 4 
    otherLocal[indices[2 ] + 22] = {{ { -0.5,  0.0 }, {  0.0,  0.5 } }}; // partition 5 
    otherLocal[indices[2 ] + 23] = {{ { -0.5,  0.5 }, {  0.0,  1.0 } }}; // partition 6 

    otherLocal[indices[3 ]] = {{ { -1.0, -1.0 }, {  0.0, 0.0 } }};
    otherLocal[indices[4 ]] = {{ { -1.0,  0.0 }, {  0.0, 1.0 } }};
    otherLocal[indices[5 ]] = {{ {  0.0, -1.0 }, {  1.0, 0.0 } }};

    otherLocal[indices[6] + 0] = {{ { -1.0, -1.0 }, {  0.0,  0.0 } }}; // partition 0
    otherLocal[indices[6] + 1] = {{ { -1.0,  0.0 }, {  0.0,  1.0 } }}; // partition 1
    otherLocal[indices[6] + 6] = {{ {  0.0,  0.0 }, {  1.0,  1.0 } }}; // partition 2
    otherLocal[indices[6] + 2] = {{ {  0.0, -1.0 }, {  0.5, -0.5 } }}; // partition 3
    otherLocal[indices[6] + 3] = {{ {  0.0, -0.5 }, {  0.5,  0.0 } }}; // partition 4
    otherLocal[indices[6] + 4] = {{ {  0.5, -1.0 }, {  1.0, -0.5 } }}; // partition 5
    otherLocal[indices[6] + 5] = {{ {  0.5, -0.5 }, {  1.0,  0.0 } }}; // partition 6

    otherLocal[indices[7 ]] = {{ {  0.0,  0.0 }, { 0.5,  0.5 } }};
    otherLocal[indices[8 ]] = {{ {  0.0,  0.5 }, { 0.5,  1.0 } }};
    otherLocal[indices[9 ]] = {{ {  0.5,  0.0 }, { 1.0,  0.5 } }};
    otherLocal[indices[10]] = {{ {  0.5,  0.5 }, { 1.0,  1.0 } }};

    otherLocal[indices[11]] = {{ { -1.0, -1.0 }, {  0.0, 0.0 } }};
    otherLocal[indices[12]] = {{ { -1.0,  0.0 }, {  0.0, 1.0 } }};
    otherLocal[indices[13]] = {{ {  0.0, -1.0 }, {  1.0, 0.0 } }};
    otherLocal[indices[14]] = {{ {  0.0,  0.0 }, {  1.0, 1.0 } }};

    otherLocal[indices[15] + 4] = {{ { -1.0,  0.0 }, {  0.0,  1.0 } }}; // partition 0
    otherLocal[indices[15] + 5] = {{ {  0.0, -1.0 }, {  1.0,  0.0 } }}; // partition 1
    otherLocal[indices[15] + 6] = {{ {  0.0,  0.0 }, {  1.0,  1.0 } }}; // partition 2
    otherLocal[indices[15] + 0] = {{ { -1.0, -1.0 }, { -0.5, -0.5 } }}; // partition 3
    otherLocal[indices[15] + 1] = {{ { -1.0, -0.5 }, { -0.5,  0.0 } }}; // partition 4
    otherLocal[indices[15] + 2] = {{ { -0.5, -1.0 }, {  0.0, -0.5 } }}; // partition 5
    otherLocal[indices[15] + 3] = {{ { -0.5, -0.5 }, {  0.0,  0.0 } }}; // partition 6
        
    otherLocal[indices[19]] = {{ { -1.0, -1.0 }, {  0.0, 0.0 } }};
    otherLocal[indices[20]] = {{ { -1.0,  0.0 }, {  0.0, 1.0 } }};
    otherLocal[indices[21]] = {{ {  0.0, -1.0 }, {  1.0, 0.0 } }};
    otherLocal[indices[22]] = {{ {  0.0,  0.0 }, {  1.0, 1.0 } }};
    
    otherLocal[indices[23]] = { { { -1.0, -1.0 }, { -0.5, -0.5 } } };
    otherLocal[indices[24]] = { { { -1.0, -0.5 }, { -0.5,  0.0 } } };
    otherLocal[indices[25]] = { { { -0.5, -1.0 }, {  0.0, -0.5 } } };
    otherLocal[indices[26]] = { { { -0.5, -0.5 }, {  0.0,  0.0 } } };
    otherLocal[indices[27]] = { { { -1.0,  0.0 }, { -0.5,  0.5 } } };
    otherLocal[indices[28]] = { { { -1.0,  0.5 }, { -0.5,  1.0 } } };
    otherLocal[indices[29]] = { { { -0.5,  0.0 }, {  0.0,  0.5 } } };
    otherLocal[indices[30]] = { { { -0.5,  0.5 }, {  0.0,  1.0 } } };
    otherLocal[indices[31]] = { { {  0.0, -1.0 }, {  0.5, -0.5 } } };
    otherLocal[indices[32]] = { { {  0.0, -0.5 }, {  0.5,  0.0 } } };
    otherLocal[indices[33]] = { { {  0.5, -1.0 }, {  1.0, -0.5 } } };
    otherLocal[indices[34]] = { { {  0.5, -0.5 }, {  1.0,  0.0 } } };
    otherLocal[indices[35]] = { { {  0.0,  0.0 }, {  0.5,  0.5 } } };
    otherLocal[indices[36]] = { { {  0.0,  0.5 }, {  0.5,  1.0 } } };
    otherLocal[indices[37]] = { { {  0.5,  0.0 }, {  1.0,  0.5 } } };
    otherLocal[indices[38]] = { { {  0.5,  0.5 }, {  1.0,  1.0 } } };

    return std::make_tuple( indices, thisLocal, otherLocal, global );

} // solution2D_2

// Partition mesh 1 with respect to mesh 2 and point (1.6, 0.9)
auto solution2D_1( )
{
    // Same partitioning, but different ordering
    auto [indices2, thisLocal2, otherLocal2, global2] = solution2D_2( );

    size_t totalNumberOfPartitions = thisLocal2.size( );

    MinMax<2> thisLocal( totalNumberOfPartitions );
    MinMax<2> otherLocal( totalNumberOfPartitions );
    MinMax<2> global( totalNumberOfPartitions );

    std::vector<size_t> indexMap
    {
         0,  1, 30, 31, 32, 40, 41, 42, 43, 62, 63, 64, 65, 66, 67, 68, 69,
        70, 71, 72, 73, 74, 75, 76, 77, 33, 34, 35, 36, 37, 38, 39, 44, 45,
        46, 47, 58, 59, 60, 61, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
        15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 48, 49,
        50, 51, 52, 53, 54, 55, 56, 57
    };

    std::vector<size_t> indices
    {
        0, 1, 2, 9, 25, 32, 36, 40, 41, 42, 43, 44, 45, 46, 47, 54, 55, 56,
        57, 58, 59, 66, 67, 68, 75, 76, 77, 78
    };

    for( size_t i = 0; i < indexMap.size( ); ++i )
    {
        otherLocal[i] = thisLocal2[indexMap[i]];
        thisLocal[i] = otherLocal2[indexMap[i]];
        global[i] = global2[indexMap[i]];
    }

    return std::make_tuple( indices, thisLocal, otherLocal, global );
}

} // namespace meshintersectiontest

TEST_CASE( "MeshProjectionQuadrature_test2D" )
{
    /*                    x (circle 2)
     * 1.8   -------------
     *      |   |         |
     * 1.5  |-------------|
     *      |   |         |
     *      |   |         |
     *      |   |         |
     * 0.9  |-------------|
     *      |   |         |
     *      |   |         |
     * 0.5   -------------x (circle 1)
     *
     *     1.0 1.2       2.0
     */

    CoordinateGrid<2> coordinates
    {{
        { 1.0, 1.2, 2.0 },
        { 0.5, 0.9, 1.5, 1.8 }
    }};

    auto mesh1 = makeRefinedGrid( coordinates );
    auto mesh2 = makeRefinedGrid( coordinates );

    auto circle1 = implicit::sphere<2>( { 2.0, 0.5 }, 0.55 );
    auto circle2 = implicit::sphere<2>( { 2.0, 2.0 }, 0.85 );

    auto embeddedCircle = implicit::sphere<2>( { 1.6, 0.9 }, 1e-8 );

    auto strategy1 = refineInsideDomain( circle1, 2, 4 );
    auto strategy2 = refineInsideDomain( circle2, 2, 4 );

    mesh1->refine( strategy1 );
    mesh2->refine( strategy2 );

    //postprocessing::postprocess( leafMappingRange( *mesh1 ), "mesh1.vtu" );
    //postprocessing::postprocess( leafMappingRange( *mesh2 ), "mesh2.vtu" );

    double alpha = 1.0;

    SpaceTreeQuadrature<2> spaceTree( embeddedCircle, alpha, 2 );

    MeshProjectionQuadrature<2> partitioner1( *mesh2, spaceTree );
    MeshProjectionQuadrature<2> partitioner2( *mesh1, spaceTree );

    auto [indices1, thisLocal1, otherLocal1, global1] = meshintersectiontest::solution2D_1( );
    auto [indices2, thisLocal2, otherLocal2, global2] = meshintersectiontest::solution2D_2( );

    meshintersectiontest::checkCorrectIntersection( mesh1, mesh2, partitioner1, indices1, thisLocal1, otherLocal1, global1 );
    meshintersectiontest::checkCorrectIntersection( mesh2, mesh1, partitioner2, indices2, thisLocal2, otherLocal2, global2 );

} // MeshProjectionQuadrature_test2D

namespace meshintersectiontest
{

auto solution3D( )
{
    std::string path = "core/MeshIntersectionPartitioner/";

    auto numberOfPartitions1 = testing::readData<size_t>( path + "indices1.dat" );
    auto numberOfPartitions2 = testing::readData<size_t>( path + "indices2.dat" );

    auto indexMap = testing::readData<size_t>( path + "indexMap.dat" );

    auto thisLocal1Data = testing::readData<double>( path + "thisLocal1.dat" );
    auto otherLocal1Data = testing::readData<double>( path + "otherLocal1.dat" );
    
    auto globalData = testing::readData<double>( path + "global.dat" );

    std::vector<size_t> indices1( numberOfPartitions1.size( ) + 1, 0 );
    std::vector<size_t> indices2( numberOfPartitions2.size( ) + 1, 0 );

    std::partial_sum( numberOfPartitions1.begin( ), numberOfPartitions1.end( ), indices1.begin( ) + 1 );
    std::partial_sum( numberOfPartitions2.begin( ), numberOfPartitions2.end( ), indices2.begin( ) + 1 );

    REQUIRE( ( !numberOfPartitions1.empty( ) && !numberOfPartitions2.empty( ) ) );
    REQUIRE( indices1.back( ) == indexMap.size( ) );
    REQUIRE( indices1.back( ) * 6 == globalData.size( ) );
    REQUIRE( indices2.back( ) * 6 == globalData.size( ) );
    REQUIRE( thisLocal1Data.size( ) == globalData.size( ) );
    REQUIRE( otherLocal1Data.size( ) == globalData.size( ) );

    MinMax<3> global1, thisLocal1, otherLocal1;

    for( size_t i = 0; i < globalData.size( ) / 6; ++i )
    {
        thisLocal1.emplace_back( );
        otherLocal1.emplace_back( );
        global1.emplace_back( );

        for( size_t axis = 0; axis < 3; ++axis )
        {
            for( size_t side = 0; side < 2; ++side )
            {
                thisLocal1.back( )[side][axis] = thisLocal1Data[6 * i + 3 * side + axis];
                otherLocal1.back( )[side][axis] = otherLocal1Data[6 * i + 3 * side + axis];
                global1.back( )[side][axis] = globalData[6 * i + 3 * side + axis];

            } // for side
        } // for axis
    } // for i

    MinMax<3> global2( global1.size( ) );
    MinMax<3> thisLocal2( thisLocal1.size( ) );
    MinMax<3> otherLocal2( otherLocal1.size( ) );

    for( size_t i = 0; i < thisLocal1.size( ); ++i )
    {
        thisLocal2[indexMap[i]] = otherLocal1[i];
        otherLocal2[indexMap[i]] = thisLocal1[i];
        global2[indexMap[i]] = global1[i];
    }
        
    return std::make_pair( std::make_tuple( indices1, thisLocal1, otherLocal1, global1 ), 
                           std::make_tuple( indices2, thisLocal2, otherLocal2, global2 ) );
}

} // namespace meshintersectiontest

TEST_CASE( "MeshProjectionQuadrature_test3D" )
{
    CoordinateGrid<3> coordinates
    {{
        {  0.3,  0.9,  2.1 },
        { -2.1, -1.7, -0.2, 0.2 },
        {  3.0,  4.2,  4.8 }
    }};

    auto mesh1 = makeRefinedGrid( coordinates );
    auto mesh2 = makeRefinedGrid( coordinates );

    auto sphere1 = implicit::sphere<3>( { 0.3, -2.1, 3.0 }, 1.8 );
    auto sphere2 = implicit::sphere<3>( { 2.1,  0.2, 4.8 }, 1.8 );

    auto embeddedSphere = implicit::sphere<3>( { 1.0, -1.0, 3.7 }, 0.3 );

    auto strategy1 = refineTowardsDomainBoundary( sphere1, 3, 4 );
    auto strategy2 = refineTowardsDomainBoundary( sphere2, 2, 4 );

    mesh1->refine( strategy1 );
    mesh2->refine( strategy2 );

    double alpha = 1.0;

    SpaceTreeQuadrature<3> spaceTree( embeddedSphere, alpha, 1 );

    MeshProjectionQuadrature<3> partitioner1( *mesh2, spaceTree );
    MeshProjectionQuadrature<3> partitioner2( *mesh1, spaceTree );

    auto [data1, data2] = meshintersectiontest::solution3D( );

    auto [indices1, thisLocal1, otherLocal1, global1] = data1;
    auto [indices2, thisLocal2, otherLocal2, global2] = data2;

    meshintersectiontest::checkCorrectIntersection( mesh1, mesh2, partitioner1, indices1, thisLocal1, otherLocal1, global1 );
    meshintersectiontest::checkCorrectIntersection( mesh2, mesh1, partitioner2, indices2, thisLocal2, otherLocal2, global2 );

} // MeshProjectionQuadrature_test3D

} // namespace mlhp
