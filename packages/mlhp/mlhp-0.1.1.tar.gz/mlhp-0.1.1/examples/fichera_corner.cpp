// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core.hpp"

int main( )
{
    using namespace mlhp;

    static constexpr size_t D = 2;

    // Analytical solution
    auto solution = solution::singularSolution<D>( );
    auto solutionDerivatives = solution::singularSolutionDerivatives<D>( );
    auto source = solution::singularSolutionSource<D>( );

    // Create and refine grid
    auto nelements = array::makeSizes<D>( 2 );
    auto lengths = array::make<D>( 1.0 );

    auto grid = makeRefinedGrid( nelements, lengths );

    size_t nlevels = 20;

    auto collapsedCircle = implicit::sphere<D>( array::make<D>( 0.0 ), 1e-10 );
    auto refinementStrategy = refineTowardsDomainBoundary( collapsedCircle, nlevels );

    grid->refine( refinementStrategy );

    print( *grid, std::cout );

    // Create multi-level hp basis on refined grid
    auto grading = UniformGrading { nlevels }; // fekernel::LinearGrading { 1 }

    using AnsatzSpace = TrunkSpace; // TensorSpace

    auto basis = makeHpBasis<AnsatzSpace>( grid, grading );

    print( *basis, std::cout );

    // Boundary conditions
    std::vector<size_t> faces;

    for( size_t axis = 0; axis < D; ++axis )
    {
        faces.push_back( boundary::face( axis, 1 ) );
    }

    auto boundaryDofs = boundary::boundaryDofs<D>( solution, *basis, faces );

    // Allocate sparse linear system
    auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( *basis, boundaryDofs.first );
    
    std::vector<double> F( matrix.size1( ), 0.0 );
    
    linalg::print( matrix, std::cout );

    // Integrate system
    auto conductivity = spatial::constantFunction<D>( 1.0 );

    auto integrand = makePoissonIntegrand( conductivity, source );

    integrateOnDomain( *basis, integrand, { matrix, F }, boundaryDofs );

    // Solve equation system
    auto interiorSolution = linalg::makeCGSolver( 1e-10 )( matrix, F );

    auto fullSolution = boundary::inflate( interiorSolution, boundaryDofs );

    // Write .vtu output
    if constexpr( D <= 3 )
    {
        auto nsamples = array::makeSizes<D>( 10 );

        auto numerical = makeSolutionProcessor<D>( fullSolution );
        auto analytical = makeFunctionProcessor<D>( solution, "AnalyticalSolution" );
        auto rhs = makeFunctionProcessor<D>( source, "Source" );
            
        auto path = "outputs/singular_" + std::to_string( D ) + "D_" + std::to_string( nlevels ) + ".vtu";
        auto postmesh = cellmesh::grid( nsamples );

        writeOutput( *basis, postmesh, std::tuple { numerical, analytical, rhs }, VtuOutput { path } );
    }
    
    // Integrate errors with p + 3 points
    //auto l2ErrorIntegrand = makeL2ErrorIntegrand( fullSolution, solution );
    auto energyErrorIntegrand = makeEnergyErrorIntegrand( fullSolution, solutionDerivatives );

    //auto l2Integrals = ErrorIntegrals { };
    auto energyIntegrals = ErrorIntegrals { };

    integrateOnDomain( *basis, energyErrorIntegrand, energyIntegrals, relativeQuadratureOrder<D>( 3 ) );

    double percent = energyIntegrals.relativeDifference( ) * 100.0;

    std::cout << "Number of internal dofs : " << interiorSolution.size( ) << std::endl;
    std::cout << "Energy error || u - u^h || / || u || * 100% : " << percent << std::endl;

    MLHP_CHECK( basis->ndof( ) == 12369, "First backward consistency check failed." );
    MLHP_CHECK( std::abs( percent - 9.995784079e-03 ) < 1e-10, "Second backward consistency check failed." );
}
