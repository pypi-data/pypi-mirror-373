// This file is part of the mlhp project. License: See LICENSE

#include "external/catch2/catch.hpp"

#include "mlhp/core/spatial.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/integrands.hpp"
#include "mlhp/core/refinement.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/boundary.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/postprocessing.hpp"

namespace mlhp
{

template<size_t D>
auto makeRefinement( std::array<double, D> current )
{
    std::array<double, 3> refinement1Radii { 0.096, 0.048, 0.048 };
    std::array<double, 3> refinement2Radii { 0.052, 0.016, 0.016 };

    auto center1 = array::setEntry( current, 0, current[0] - 0.6 * refinement1Radii[0] );
    auto center2 = array::setEntry( current, 0, current[0] - 0.3 * refinement2Radii[0] );

    auto domain1 = implicit::ellipsoid( center1, refinement1Radii );
    auto domain2 = implicit::ellipsoid( center2, refinement2Radii );

    auto refinement1 = refineInsideDomain( domain1, 1 );
    auto refinement2 = refineInsideDomain( domain2, 2 );

    return refinementOr( refinement1, refinement2 );
}

TEST_CASE( "linear_heat_3D" )
{
    static constexpr size_t D = 3;

    double theta = 0.5;
    size_t nsteps = 24;

    auto lengths = std::array<double, 3> { 1.0, 0.4, 0.1 };
    auto nelements = std::array<size_t, 3> { 10, 4, 1 };
    auto degrees = array::make<D>( size_t { 2 } );
    auto resolution = array::add<size_t>( degrees, 0 );

    using AnsatzSpace = TrunkSpace;

    double duration = 1.0;

    double diffusivity = 0.008;
    double sigma = 0.02;

    std::function path = [=]( double t ) noexcept
    {
        return std::array<double, 3> { 0.6 * t + 0.2, lengths[1] / 2.0, lengths[2] };
    };

    std::function intensity = []( double t ) noexcept
    {
        return std::min( t / 0.05, 1.0 );
    };

    auto capacityFunction = spatial::constantFunction<D + 1>( 1.0 );
    auto diffusivityFunction = spatial::constantFunction<D + 1>( diffusivity );

    auto boundaries = boundary::allFaces( D );

    boundaries.pop_back( );

    auto source = solution::amLinearHeatSource<D>( path, intensity, sigma );
    auto solution = solution::amLinearHeatSolution( path, intensity, 1.0, diffusivity, sigma, duration / 10.0, 0.0 );

    // Initial discretization
    auto grid0 = makeRefinedGrid( nelements, lengths );
    auto grid1 = grid0;

    auto basis0 = makeHpBasis<AnsatzSpace>( grid0, LinearGrading { degrees }  );
    auto dofs0 = projectOnto( *basis0, spatial::constantFunction<D>( 0.0 ) );

     // Postprocess initial condition
     auto processors = std::tuple
     {
         makeSolutionProcessor<D>( dofs0 ),
         makeRefinementLevelProcessor<D>( *grid0 ),
         makeFunctionProcessor<D>( spatial::sliceLast( solution, 0.0 ), "Analytical" ),
         makeFunctionProcessor<D>( spatial::sliceLast( source, 0.0 ), "Source" ),
     };
     
     auto filename = "outputs/systemtests/linear_heat_cpp_";
     auto writer = VtuOutput { filename + std::to_string( 0 ) };
     auto postmesh = cellmesh::grid( resolution );

     writeOutput( *basis0, postmesh, std::move( processors ), writer );
     
     auto ndof = size_t { 0 };
     auto dt = duration / nsteps;
     auto integrals = std::array { 0.0, 0.0, 0.0 };

    // Time stepping
    for( size_t iTimeStep = 0; iTimeStep < nsteps; ++iTimeStep )
    {
        double time0 = iTimeStep * dt;
        double time1 = ( iTimeStep + 1 ) * dt;

        // Create discetisation for t^{i+1}
        grid1 = makeRefinedGrid( nelements, lengths );
        grid1->refine( makeRefinement( path( time1 ) ) );
            
        auto basis1 = makeHpBasis<AnsatzSpace>( grid1, LinearGrading { degrees } );

        std::cout << "Time step " << iTimeStep + 1 << " / " << nsteps;
        std::cout << " (" << basis1->ndof( ) << " number of unknowns)" << std::endl;
                
        auto dirichletDofs = boundary::boundaryDofs<D>( spatial::sliceLast( 
            solution, time1 ), *basis1, boundaries );

        auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( *basis1, dirichletDofs.first );
        auto vector = std::vector<double>( matrix.size1( ), 0.0 );

        auto integrand = makeTransientPoissonIntegrand<D>( capacityFunction, 
            diffusivityFunction, source, dofs0, { time0, time1 }, theta );

        integrateOnDomain<D>( *basis0, *basis1, integrand, { matrix, vector }, dirichletDofs );

        auto dofs1 = boundary::inflate( linalg::makeCGSolver( )( matrix, vector ), dirichletDofs );

        // Integrate L2 error
        auto l2Integrand = makeL2ErrorIntegrand( dofs1, spatial::sliceLast( solution, time1 ) );
        auto l2Integrals = ErrorIntegrals { };

        integrateOnDomain( *basis1, l2Integrand, l2Integrals );

        double factor = iTimeStep + 1 == nsteps ? dt / 2.0 : dt;

        integrals[0] += factor * l2Integrals.analyticalSquared;
        integrals[1] += factor * l2Integrals.numericalSquared;
        integrals[2] += factor * l2Integrals.differenceSquared;
        ndof += basis1->ndof( );

         // Postprocess vtu file with 6 sub-cells per element
        processors =
        {
            makeSolutionProcessor<D>( dofs1 ),
            makeRefinementLevelProcessor<D>( *grid1 ),
            makeFunctionProcessor<D>( spatial::sliceLast( solution, time1 ), "Analytical" ),
            makeFunctionProcessor<D>( spatial::sliceLast( source, time1 ), "Source" ),
        };
        
        writer = VtuOutput { filename + std::to_string( iTimeStep + 1 ) };

        writeOutput( *basis1, postmesh, std::move( processors ), writer );
             
        // Move discretization for next step
        dofs0 = std::move( dofs1 );
        grid0 = std::move( grid1 );
        basis0 = std::move( basis1 );
    }

    CHECK( ndof == 33436 );
    CHECK( std::sqrt( integrals[0] ) == Approx( 2.734205394711 ).epsilon( 1e-9 ) );
    CHECK( std::sqrt( integrals[1] ) == Approx( 2.753217596062 ).epsilon( 1e-9 ) );
    CHECK( std::sqrt( integrals[2] ) == Approx( 6.446093860799e-02 ).epsilon( 1e-7 ) );
    CHECK( std::sqrt( integrals[2] / integrals[1] ) == Approx( 2.341294734575e-02 ).epsilon( 1e-7 ) );
}

} // namespace mlhp::transient
