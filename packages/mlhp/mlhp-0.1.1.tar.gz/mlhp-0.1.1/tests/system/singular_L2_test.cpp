// This file is part of the mlhp project. License: See LICENSE

#include "external/catch2/catch.hpp"

#include "mlhp/core/implicit.hpp"
#include "mlhp/core/postprocessing.hpp"
#include "mlhp/core/integrands.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/refinement.hpp"
#include "mlhp/core/spatial.hpp"

namespace mlhp
{

template<size_t D>
auto computeSingularL2( size_t refinementLevel )
{
    auto circle = implicit::sphere<D>( array::make<D>( 0.0 ), 1e-10 );

    auto nelements = array::make<D>( size_t { 4 } );
    auto lengths = array::make<D>( 1.0 );
    auto nsamples = array::make<D>( size_t { 6 } );

    auto function = solution::singularSolution<D>( );

    // Create and refined grid
    auto refinementStrategy = refineTowardsDomainBoundary( circle, refinementLevel );
    
    auto grid = makeRefinedGrid( nelements, lengths );

    grid->refine( refinementStrategy );

    // Create multi-level hp basis on refined grid
    auto basis = makeHpBasis<TrunkSpace>( grid, LinearGrading { 1 } );

    // Project function onto space spanned by basis
    auto dofs = projectOnto( *basis, function );

    // Integrate error
    auto errorIntegrand1 = makeL2ErrorIntegrand( dofs, function );
    auto l2integrals = ErrorIntegrals { };

    integrateOnDomain( *basis, errorIntegrand1, l2integrals, relativeQuadratureOrder<D>( 1 ) );

    // Write .vtu file
    auto processors = std::tuple 
    {
        makeSolutionProcessor<D>( dofs ),
        makeFunctionProcessor<D>( function, "AnalyticalSolution" )
    };

    auto postmesh = cellmesh::grid( nsamples );
    auto file = "outputs/systemtests/singular_l2_" + std::to_string( D ) + "D_" + std::to_string( refinementLevel );

    writeOutput( *basis, postmesh, std::move( processors ), VtuOutput { file } );

    return std::make_pair( dofs.size( ), l2integrals.differenceSquared );
}

TEST_CASE( "singular_l2_1D" )
{
    // || u_ex - u_fe ||^2_L2
    std::vector<double> expectedL2
    {
        3.08705e-06,
        6.21486e-07,
        1.25989e-07,
        2.55838e-08,
        5.19513e-09
    };

    std::vector<size_t> expectedNDof { 5, 9, 14, 20, 27 };

    for( size_t refinementLevel = 0; refinementLevel < expectedNDof.size( ); ++refinementLevel )
    {
        auto [ndof, l2] = computeSingularL2<1>( refinementLevel );
        
        CHECK( ndof == expectedNDof[refinementLevel] );
        CHECK( l2 == Approx( expectedL2[refinementLevel] ).margin( 1e-12 ) );
    }

} // singular_l2_1D

TEST_CASE( "singular_l2_2D" )
{
    std::vector<size_t> expectedNDof { 25, 66, 113, 181, 273 };

    // || u_ex - u_fe ||^2_L2
    std::vector<double> expectedL2
    {
        1.42219e-06,
        1.2541e-06,
        1.67571e-07,
        2.11436e-08,
        2.68362e-09
    };

    for( size_t refinementLevel = 0; refinementLevel < expectedNDof.size( ); ++refinementLevel )
    {
        auto [ndof, l2] = computeSingularL2<2>( refinementLevel );

        CHECK( ndof == expectedNDof[refinementLevel] );
        CHECK( l2 == Approx( expectedL2[refinementLevel] ).margin( 1e-12 ) );
    }

} // singular_l2_2D

TEST_CASE( "singular_l2_3D" )
{
    std::vector<size_t> expectedNDof { 125, 429, 754, 1337 };

    // || u_ex - u_fe ||^2_L2
    std::vector<double> expectedL2
    {
        7.35596e-07,
        2.28911e-07,
        1.66542e-08,
        1.27925e-09
    };

    for( size_t refinementLevel = 0; refinementLevel < expectedL2.size( ); ++refinementLevel )
    {
        auto [ndof, l2] = computeSingularL2<3>( refinementLevel );

        CHECK( ndof == expectedNDof[refinementLevel] );
        CHECK( l2 == Approx( expectedL2[refinementLevel] ).margin( 1e-12 ) );
    }

} // singular_l2_3D

} // namespace mlhp
