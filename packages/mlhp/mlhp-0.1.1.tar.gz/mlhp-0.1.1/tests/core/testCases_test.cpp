// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/basis.hpp"
#include "mlhp/core/multilevelhpcore.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/refinement.hpp"

#include <numeric>

namespace mlhp
{
namespace testcases
{
    struct Expected
    {
        size_t nleaves, ncells;

        std::vector<CellIndex> neighbours;
        std::vector<bool> leafMask;
        std::vector<RefinementLevel> levels;
        std::vector<LocalPosition> positions;

        std::vector<DofIndex> locationMapIndex;
        std::vector<DofIndex> locationMaps, locationMapLengths;
        std::vector<PolynomialDegree> tensorProductIndices;

        Expected( const std::string& path,
                  size_t D,
                  size_t numberOfCells ) :
            ncells( numberOfCells ),
            neighbours( testing::readData<CellIndex>( path + "neighbours.txt", numberOfCells* D * 2 ) ),
            leafMask( testing::readData<bool>( path + "leafMask.txt", numberOfCells ) ),
            levels( testing::readData<RefinementLevel>( path + "levels.txt", numberOfCells ) ),
            positions( testing::readData<LocalPosition>( path + "positionsInParent.txt", numberOfCells* D ) )
        {
            nleaves = std::accumulate( leafMask.begin( ), leafMask.end( ), size_t { 0 } );

            locationMapIndex.resize( nleaves + 1 );
            locationMapIndex[0] = 0;

            locationMapLengths = testing::readData<DofIndex>( path + "locationMapLengths.txt", nleaves );

            std::partial_sum( locationMapLengths.begin( ), locationMapLengths.end( ), locationMapIndex.begin( ) + 1 );

            locationMaps = testing::readData<DofIndex>( path + "locationMaps.txt", locationMapIndex.back( ) );
            tensorProductIndices = testing::readData<PolynomialDegree>( path + "tensorProductIndices.txt" );
        }
    };

    template<size_t D>
    void compareGrid( const AbsHierarchicalGrid<D>& grid, const Expected& expected )
    {
        CHECK( grid.nfull( ) == expected.ncells );

        NCubeNeighboursVector<D> neighbours;
        std::vector<RefinementLevel> levels;
        std::vector<PositionInParent<D>> positions;
        std::vector<bool> leafMask;

        REQUIRE_NOTHROW( neighbours = mesh::hierarchicalNeighbours( grid ) );
        REQUIRE_NOTHROW( levels = mesh::refinementLevels( grid, true ) );
        REQUIRE_NOTHROW( positions = mesh::positionsInParent( grid ) );
        REQUIRE_NOTHROW( leafMask = mesh::leafMask( grid ) );

        REQUIRE( levels.size( ) == expected.ncells );
        REQUIRE( neighbours.size( ) == expected.ncells );
        REQUIRE( positions.size( ) == expected.ncells );
        REQUIRE( leafMask.size( ) == expected.ncells );

        CHECK( std::equal( levels.begin( ), levels.end( ), expected.levels.begin( ) ) );
        CHECK( std::equal( leafMask.begin( ), leafMask.end( ), expected.leafMask.begin( ) ) );

        for( size_t iCell = 0; iCell < expected.ncells; ++iCell )
        {
            CHECK( std::equal( neighbours[iCell].begin( ), neighbours[iCell].end( ),
                               expected.neighbours.begin( ) + static_cast<std::ptrdiff_t>( iCell * D * 2 ) ) );

            CHECK( std::equal( positions[iCell].begin( ), positions[iCell].end( ),
                               expected.positions.begin( ) + static_cast<std::ptrdiff_t>( iCell * D ) ) );

        } // for iCell
    } // compareGrid

    template<size_t D>
    void compareMlhpBasis( const MultilevelHpBasis<D>& basis, const Expected& expected )
    {
        REQUIRE( basis.nelements( ) == expected.nleaves );

        TensorProductIndicesVector<D> indices;
        std::vector<PolynomialDegree> computedIndices;

        for( CellIndex iCell = 0; iCell < expected.ncells; ++iCell )
        {
            REQUIRE_NOTHROW( basis.tensorProductIndices( iCell, 0, indices ) );

            for( auto tuple : indices )
            {
                computedIndices.insert( computedIndices.end( ), tuple.begin( ), tuple.end( ) );
            }
        } // for iCell

        REQUIRE( computedIndices.size( ) == expected.tensorProductIndices.size( ) );
        CHECK( std::equal( computedIndices.begin( ), computedIndices.end( ), expected.tensorProductIndices.begin( ) ) );

        size_t locationMapErrors = 0;

        LocationMap locationMap;

        for( CellIndex iLeaf = 0; iLeaf < expected.nleaves; ++iLeaf )
        {
            locationMap.resize( 0 );

            basis.locationMap( iLeaf, locationMap );

            REQUIRE( locationMap.size( ) == static_cast<size_t>( expected.locationMapLengths[iLeaf] ) );

            locationMapErrors += !std::equal( locationMap.begin( ), locationMap.end( ),
                expected.locationMaps.begin( ) + static_cast<std::ptrdiff_t>( expected.locationMapIndex[iLeaf] ) );

        } // for iLeaf

        CHECK( locationMapErrors == 0 );
    }

} // namespace testcases

TEST_CASE( "halfCircle2D_test" )
{
    std::array<size_t, 2> numberOfBaseElements = { 4, 3 };
    std::array<double, 2> lengths = { 1.0, 1.0 };
    std::array<size_t, 2> p { 3, 5 };

    size_t numberOfSeedPoints = 6;
    size_t refinementDepth = 4;

    testcases::Expected expected( "core/HalfCircle2D/", 2, 260 );

    // Topology
    auto circle = implicit::sphere<2>( { 1.0, 0.5 }, 0.3 );

    auto refinementStrategy = refineTowardsDomainBoundary( circle, refinementDepth, numberOfSeedPoints );

    auto grid = makeRefinedGrid( numberOfBaseElements, lengths );

    grid->refine( refinementStrategy );

    testcases::compareGrid( *grid, expected );

    // Mlhp Basis
    auto basis = makeHpBasis<TensorSpace>( grid, p );

    testcases::compareMlhpBasis( *basis, expected );
}

TEST_CASE( "ficheraCorner3D_test" )
{
    std::array<size_t, 3> numberOfBaseElements = { 2, 3, 2 };
    std::array<double, 3> lengths = { 1.0, 1.0, 1.0 };
    std::array<size_t, 3> p { 4, 2, 3 };

    size_t numberOfSeedPoints = 6;
    size_t refinementDepth = 3;

    testcases::Expected expected( "core/FicheraCorner3D/", 3, 460 );

    // Topology
    auto circle = implicit::sphere<3>( { 0.0, 0.0, 0.0 }, 0.46 );

    auto refinementStrategy = refineTowardsDomainBoundary( circle, refinementDepth, numberOfSeedPoints );

    auto grid = makeRefinedGrid( numberOfBaseElements, lengths );

    grid->refine( refinementStrategy );

    testcases::compareGrid( *grid, expected );

    // Mlhp Basis
    auto basis = makeHpBasis<TensorSpace>( grid, p );

    testcases::compareMlhpBasis( *basis, expected );
}

} // mlhp
