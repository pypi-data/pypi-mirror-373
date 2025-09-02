// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core.hpp"
#include <iomanip>

using namespace mlhp;

template<size_t D>
auto timeSteppingRefinement( std::array<double, D> current )
{
    // Refine based on distance to "laser":
    //     Outside outer radius (distance  > radius1):
    //         -> 0 levels
    //     Between outer and inner radius (radius2 < distance < radius1)
    //         -> interpolate between level1 and level2
    //     Inside inner radius (distance < radius2 ):
    //         -> level2
    auto refine = [=]( double radius1, double radius2, 
                       double level1, double level2 )
    {
        // Skewness in x-direction
        double scaleLeft = 2.2;
        double scaleRight = 1.6;

        return refineWithLevelFunction<D>( [=]( std::array<double, D> xyz )
        {
            auto dx = xyz - current;

            // Rescale in x
            dx[0] = dx[0] < 0 ? dx[0] / scaleLeft : dx[0] / scaleRight;

            // Compute and scale distance
            double d = std::min( ( spatial::norm( dx ) - radius1 ) / ( radius2 - radius1 ), 1.0 );

            return d >= 0.0 ? static_cast<RefinementLevel>( d * level2 + ( 1 - d ) * level1 ) : RefinementLevel { 0 };
        } );
    };

    // Add two refinements
    return refinementOr( refine( 0.1,   0.02,  0, 3 ),
                         refine( 0.015, 0.005, 3, 5 ) );
}

int main( )
{
    static constexpr size_t D = 3;

    // Physics setup
    double diffusivity = 0.01;
    double capacity = 1.0;
    double duration = 1.0;
    double sigma = 0.0021;
    double u0 = 25.0;

    std::array<double, D> lengths { 1.0, 0.4, 0.1 };

    std::function path = [=]( double t ) noexcept
    {
        double x = ( 0.6 * t / duration + 0.2 ) * lengths[0];

        return std::array<double, 3>{ x, lengths[1] / 2.0, lengths[2] };
    };

    double energy = 0.484;

    std::function intensity = [=]( double t ) noexcept
    {
        return 2.0 * energy * std::min( t / 0.05, 1.0 );
    };

    auto source = solution::amLinearHeatSource( path, intensity, sigma );

    auto solution = solution::amLinearHeatSolution(  path, intensity, 
        capacity, diffusivity, sigma, duration / 100, u0 );

    auto boundaries = boundary::allFaces( D );

    boundaries.pop_back( );

    auto capacityFunction = spatial::constantFunction<D + 1>( capacity );
    auto diffusivityFunction = spatial::constantFunction<D + 1>( diffusivity );

    // Discretization parameters
    size_t nsteps = 256;
    double theta = 0.5;

    auto nelements = std::array<size_t, 3> { 10, 4, 1 };
    auto degrees = std::vector<PolynomialDegree> { 2, 3, 4, 3, 3, 2 };
    auto grading = PerLevelGrading { degrees };

    using AnsatzSpace = TrunkSpace;

    // Initial discretization
    auto grid0 = makeRefinedGrid( nelements, lengths );
    auto grid1 = grid0;

    auto basis0 = makeHpBasis<AnsatzSpace>( grid0, grading );
    auto dofs0 = projectOnto( *basis0, spatial::constantFunction<D>( u0 ) );

    // Postprocess initial condition
    auto processors = std::tuple
    {
        makeSolutionProcessor<D>( dofs0 ),
        makeFunctionProcessor<D>( spatial::sliceLast( source, 0.0 ), "Source" )
    };
    
    auto resolution = array::makeSizes<D>( *std::max_element( degrees.begin( ), degrees.end( ) ) );
    auto postmesh = cellmesh::grid( resolution );
    auto filename = "outputs/travelling_heat_source_";
    auto writer = VtuOutput { filename + std::to_string( 0 ) };

    writeOutput( *basis0, postmesh, std::move( processors ), writer );

    size_t vtuInterval = 32;

    // Time stepping
    for( size_t iTimeStep = 0; iTimeStep < nsteps; ++iTimeStep )
    {
        double time0 = iTimeStep * duration / nsteps;
        double time1 = ( iTimeStep + 1 ) * duration / nsteps;

        // Create discetisation for t^{i+1}
        grid1 = makeRefinedGrid( nelements, lengths );
        grid1->refine( timeSteppingRefinement( path( time1 ) ) );
            
        auto basis1 = makeHpBasis<AnsatzSpace>( grid1, grading );

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

        if( ( iTimeStep + 1 ) % vtuInterval == 0 )
        {
             // Postprocess vtu file with 6 sub-cells per element
            processors =
            {
                makeSolutionProcessor<D>( dofs1 ),
                makeFunctionProcessor<D>( spatial::sliceLast( source, time1 ), "Source" ),
            };

            auto index = ( iTimeStep / vtuInterval ) + 1;
            auto writer = VtuOutput { filename + std::to_string( index ) };
            auto postmesh = cellmesh::grid( resolution );

            writeOutput( *basis1, postmesh, std::move( processors ), writer );
        }
            
        // Move discretization for next step
        dofs0 = std::move( dofs1 );
        grid0 = std::move( grid1 );
        basis0 = std::move( basis1 );
    }

    auto difference = std::abs( linalg::norm( dofs0 ) - 6606.646046763458 );

    MLHP_CHECK( basis0->ndof( ) == 2345, "First backward consistency check failed." );
    MLHP_CHECK( difference < 1e-6, "Second backward consistency check failed." );
}
