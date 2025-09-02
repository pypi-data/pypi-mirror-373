// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/sparse.hpp"
#include "mlhp/core/boundary.hpp"
#include "mlhp/core/refinement.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/quadrature.hpp"
#include "mlhp/core/integrandtypes.hpp"
#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/multilevelhpcore.hpp"

#include "singleBaseCell_2D.hpp"

namespace mlhp
{

TEST_CASE( "inflate" )
{
    std::vector<double> reduced { 2.0, 3.0, 4.0 };

    std::vector<double> boundary { 5.0, 6.0 };
    std::vector<DofIndex> indices { 1, 3 };

    std::vector<double> inflated;

    REQUIRE_NOTHROW( inflated = boundary::inflate( reduced, { indices, boundary } ) );

    REQUIRE( inflated.size( ) == 5 );

    std::array<double, 5> expected { 2.0, 5.0, 3.0, 6.0, 4.0 };

    CHECK( std::equal( inflated.begin( ), inflated.end( ), expected.begin( ) ) );
}

TEST_CASE( "triangulateFaces_test" )
{
    auto grid = makeRefinedGrid<3>( { 2, 1, 3 }, { 2.0, 1.0, 3.0 }, { 3.0, 2.0, 4.0 } );

    auto sphere = implicit::sphere<3>( { 2.13, 2.02, 3.49 }, 2.17 );

    grid->refine( refineTowardsDomainBoundary( sphere, 3 ) );

    auto triangulation1 = boundary::triangulateFaces( *grid, { 1, 2, 4 } );
    auto triangulation2 = boundary::triangulateFaces( *grid, { 0, 3, 5 } );

    // For visualization:
    //writeTriangles( std::get<0>( sides1[0] ), "triangles1.vtu" );

    std::vector expectedTriangulations =
    {
        testing::readData<double>( "core/MeshBoundaryTriangulation/face0.txt" ),
        testing::readData<double>( "core/MeshBoundaryTriangulation/face1.txt" ),
        testing::readData<double>( "core/MeshBoundaryTriangulation/face2.txt" ),
        testing::readData<double>( "core/MeshBoundaryTriangulation/face3.txt" ),
        testing::readData<double>( "core/MeshBoundaryTriangulation/face4.txt" ),
        testing::readData<double>( "core/MeshBoundaryTriangulation/face5.txt" )
    };

    std::vector computedSides =
    { 
        triangulation2[0], triangulation1[0], triangulation1[1], 
        triangulation2[1], triangulation1[2], triangulation2[2] 
    };

    for( size_t i = 0; i < 6; ++i )
    {
        const auto& xyz = std::get<0>( computedSides[i] );

        REQUIRE( xyz.size( ) == expectedTriangulations[i].size( ) );

        // If the order changes either the files must be changed or some sorting has to be done
        CHECK( utilities::floatingPointEqual( xyz.begin( ), xyz.end( ),
               expectedTriangulations[i].begin( ), 1e-10 ) );
    }
}

TEST_CASE( "boundaryDofs_test" )
{
    // Create 2D grid, project onto top edge and compare
    // to projection onto 1D grid.

    auto grid1D = makeRefinedGrid<1>( { 1 }, { 1.0 } );
    auto grid2D = makeRefinedGrid<2>( { 1, 1 }, { 1.0, 1.0 } );

    auto interval = implicit::sphere<1>( { 1.0 }, 0.2 );
    auto circle = implicit::sphere<2>( { }, 0.8 );

    grid1D->refine( refineTowardsDomainBoundary( interval, 3, 6 ) );
    grid2D->refine( refineTowardsDomainBoundary( circle, 3, 6 ) );

    auto templates1D = basis::createAnsatzTemplates<1>( { { 3 }, { 4 }, { 2 }, { 3 } } );
    auto templates2D = basis::createAnsatzTemplates<2>( singlebasecell2d::inhomogeneousDegrees, 2 );

    auto basis1D = MultilevelHpBasis<1>( grid1D, templates1D, &initializeTensorSpaceMasks<1> );
    auto basis2D = MultilevelHpBasis<2>( grid2D, templates2D, &initializeTensorSpaceMasks<2> );

    auto f = []( double t ) noexcept { return t * t + 0.3 * t + 4.2; };

    auto f1D = [=]( std::array<double, 1> x ) noexcept { return f( x[0] ); };
    auto f2D = [=]( std::array<double, 2> x ) noexcept { return f( x[1] ); };

    auto dofs1D = projectOnto<1>( basis1D, f1D );

    auto [indices2D, dofs2D] = boundary::boundaryDofs<2>( f2D, basis2D, { boundary::left }, 1 );

    auto expectedIndices = DofIndexVector { 0, 1, 2, 3, 12, 13, 14, 15, 70, 71, 81, 82, 83, };

    for( auto& index : expectedIndices )
    {
        index += 252;
    }

    REQUIRE( dofs1D.size( ) == dofs2D.size( ) );

    CHECK( indices2D == expectedIndices );
    CHECK( utilities::floatingPointEqual( dofs1D.begin( ), dofs1D.end( ), dofs2D.begin( ), 1e-5 ) );
}

TEST_CASE( "QuadratureOnMeshFaces_test" )
{
    auto nelements = std::array<size_t, 3> { 3, 2, 3 };
    auto lengths = std::array<double, 3> { 3.0, 2.0, 3.0 };
    auto origin = std::array<double, 3> { 5.0, -1.0, 2.0 };

    auto mesh = makeRefinedGrid( nelements, lengths, origin );
    
    mesh->refine( refineCellIndices<3>( { { 7 } } ) );

    REQUIRE( mesh->ncells( ) == 25 );

    REQUIRE( mesh->refinementLevel( mesh->fullIndex( 16 ) ) == 0 );
    REQUIRE( mesh->refinementLevel( mesh->fullIndex( 17 ) ) == 1 );
    REQUIRE( mesh->refinementLevel( mesh->fullIndex( 24 ) ) == 1 );

    auto mapping = mesh->createMapping( );

    auto rst = CoordinateList<3> { };
    auto normals = CoordinateList<3> { };
    auto weights = std::vector<double>{ };

    SECTION( "empty" )
    {
        auto quadrature = boundary::QuadratureOnMeshFaces<3>( { }, absoluteQuadratureOrder( array::makeSizes<3>( 1 ) ) );
        auto cache = quadrature.initialize( );

        for( CellIndex icell = 0; icell < 25; ++icell )
        {
            mesh->prepareMapping( icell, mapping );
         
            utilities::resize0( rst, normals, weights );

            quadrature.distribute( mapping, { 6, 6, 6 }, rst, normals, weights, cache );

            CHECK( ( rst.empty( ) && normals.empty( ) && weights.empty( ) ) );
        }
    }

    SECTION( "cell faces" )
    {
        auto faces = std::vector 
        { 
            MeshCellFace { 5, boundary::face( 2, 1 ) },  // left back top
            MeshCellFace { 15, boundary::face( 0, 1 ) }, // right back bottom
            MeshCellFace { 22, boundary::face( 1, 0 ) }, // refined right front bottom of middle front
        };

        auto quadrature = boundary::QuadratureOnMeshFaces<3>( faces, absoluteQuadratureOrder( array::makeSizes<3>( 3 ) ) );
        auto cache = quadrature.initialize( );
        
        auto [r, w] = gaussLegendrePoints( 3 );

        for( CellIndex icell = 0; icell < 25; ++icell )
        {
            mesh->prepareMapping( icell, mapping );

            auto begin = rst.size( );

            quadrature.distribute( mapping, { 5, 1, 2 }, rst, normals, weights, cache );
            
            if( icell == 5 || icell == 15 || icell == 22 )
            {
                REQUIRE( rst.size( ) == begin + 9 );
                REQUIRE( normals.size( ) == begin + 9 );
                REQUIRE( weights.size( ) == begin + 9 );

                for( size_t i = 0; i < 3; ++i )
                {
                    for( size_t j = 0; j < 3; ++j )
                    {
                        auto index = begin + 3 * i + j;
                        
                        if( icell == 5 )
                        {
                            CHECK( weights[index] == 0.25 * w[i] * w[j] );
                            CHECK( spatial::distance( rst[index], std::array { r[i], r[j], 1.0 } ) < 1e-10 );
                            CHECK( spatial::distance( normals[index], std::array { 0.0, 0.0, 1.0 } ) < 1e-10 );
                        }
                        else if( icell == 15 )
                        {
                            CHECK( weights[index] == 0.25 * w[i] * w[j] );
                            CHECK( spatial::distance( rst[index], std::array { 1.0, r[i], r[j] } ) < 1e-10 );
                            CHECK( spatial::distance( normals[index], std::array { 1.0, 0.0, 0.0 } ) < 1e-10 );
                        }
                        else if( icell == 22 )
                        {
                            CHECK( weights[index] == 0.25 * 0.25 * w[i] * w[j] );
                            CHECK( spatial::distance( rst[index], std::array { r[i], -1.0, r[j] } ) < 1e-10 );
                            CHECK( spatial::distance( normals[index], std::array { 0.0, -1.0, 0.0 } ) < 1e-10 );
                        }

                    } // for j
                } // for i
            }
            else
            {
                CHECK( rst.size( ) == begin );
                CHECK( normals.size( ) == begin );
                CHECK( weights.size( ) == begin );
            }
        } // for icell

    } // cell faces

    SECTION( "integrate function" )
    {
        auto order = absoluteQuadratureOrder( array::makeSizes<3>( 5 ) );

        auto meshfaces = std::vector { boundary::right, boundary::front, boundary::top };
        auto quadrature = boundary::QuadratureOnMeshFaces<3>( *mesh, meshfaces, order );
        auto cache = quadrature.initialize( );

        auto function1 = []( double y, double z ) { return std::cos( y ) * std::sin( z ); };
        auto function2 = []( double x, double z ) { return std::cos( x ) + std::cos( z ); };
        auto function3 = []( double x, double y ) { return std::sin( x + y ) * std::cos( x - y ); };

        auto inInterval = []( double x0, double x1, double x ){ return x >= x0 - 1e-10 && x <= x1 + 1e-10; };

        auto function = [=]( std::array<double, 3> xyz ) 
        { 
            return ( inInterval(  8.0,  8.0, xyz[0] ) ? function1( xyz[1], xyz[2] ) : 0.0 ) + 
                   ( inInterval( -1.0, -1.0, xyz[1] ) ? function2( xyz[0], xyz[2] ) : 0.0 ) +
                   ( inInterval(  5.0,  5.0, xyz[2] ) ? function3( xyz[0], xyz[1] ) : 0.0 );
        };

        double value1 = 0.0, value2 = 0.0;

        for( CellIndex icell = 0; icell < 25; ++icell )
        {
            mesh->prepareMapping( icell, mapping );

            utilities::resize0( rst, normals, weights );

            quadrature.distribute( mapping, { 1, 2, 4 }, rst, normals, weights, cache );
            
            for( size_t ipoint = 0; ipoint < rst.size( ); ++ipoint )
            {
                value1 += weights[ipoint];
                value2 += function( mapping( rst[ipoint] ) ) * weights[ipoint];
            }
        }

        CHECK( value1 == Approx( 6.0 + 9.0 + 6.0 ).epsilon( 1e-10 ) );

        auto yz = 2.0 * std::sin( 1.0 ) * std::cos( 2.0 ) - 2.0 * std::sin( 1.0 ) * cos( 5.0 );
        auto xz = -3.0 * std::sin( 2.0 ) + 3.0 * std::sin( 8.0 );

        auto xy = std::cos( 4.0 ) * std::cos( 6.0 ) / 2.0 + std::sin( 7.0 ) * std::cos( 9.0 ) / 4.0 - 
                  std::sin( 4.0 ) * std::sin( 6.0 ) / 2.0 - std::sin( 9.0 ) * std::cos( 7.0 ) / 4.0 + 
                  std::sin( 6.0 ) * std::cos( 4.0 ) / 4.0 + std::sin( 7.0 ) * std::sin( 9.0 ) / 2.0 - 
                  std::sin( 4.0 ) * std::cos( 6.0 ) / 4.0 - std::cos( 7.0 ) * std::cos( 9.0 ) / 2.0;

        CHECK( value2 == Approx ( yz + xz + xy ).epsilon( 1e-10 ) );

        auto evaluate = [=]( typename SurfaceIntegrand<3>::Cache&,
                             const BasisFunctionEvaluation<3>& shapes, 
                             const LocationMap& /* locationMap */,
                             std::array<double, 3> /* normal */,
                             AlignedDoubleVectors& targets,
                             double weightDetJ )
        {
            targets[0][0] += function( shapes.xyz( ) ) * weightDetJ;
        };

        auto basis = makeHpBasis<TensorSpace>( mesh, 1 );
        auto integrand = makeSurfaceIntegrand<3>( { AssemblyType::Scalar }, DiffOrders::NoShapes, evaluate );
        auto value3 = 0.0;

        integrateOnSurface<3>( *basis, integrand, quadrature, { value3 } );
        
        CHECK( value3 == Approx ( yz + xz + xy ).epsilon( 1e-10 ) );

    } // integrate function
}

} // namespace mlhp
