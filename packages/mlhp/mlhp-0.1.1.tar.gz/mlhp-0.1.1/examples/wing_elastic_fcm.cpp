// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core.hpp"

int main( )
{
    using namespace mlhp;

    auto time = utilities::tic( );

    static constexpr size_t D = 3;

    // Domain
    auto domain = implicit::ellipsoid<3>( { 0.0, 2.0, 0.4 }, { 20.0, 2.0, 0.4 } );

    // Discretization
    auto nelements = std::array<size_t, 3>{ 20, 4, 1 };
    auto lengths = std::array<double, 3>{ 20.0, 4.0, 0.8 };

    auto degrees = array::makeSizes<D>( 2 );
    auto resolution = array::add<size_t>( degrees, 3 );

    auto penaltyFCM = 1e-5;

    auto refinementDepth = size_t { 2 };
    auto integrationSpaceTreeDepth = size_t { 3 };

    // Create and refine grid
    auto refinementStrategy = refineTowardsDomainBoundary( domain, refinementDepth );
    
    auto grid = makeRefinedGrid( nelements, lengths );

    grid->refine( refinementStrategy );

    print( *grid, std::cout );

    auto nfields = size_t { D };

    // Create mlhp basis on refined grid
    auto basis = makeHpBasis<TrunkSpace>( grid, UniformGrading { degrees }, nfields );

    print( *basis, std::cout );

    // Set up boundary conditions
    auto boundaryFunctions = spatial::constantFunction<D>( array::make<D>( 0.0 ) );
    auto boundaryDofs = boundary::boundaryDofs<D>( boundaryFunctions, *basis, { boundary::left } );
    
    // Allocate sparse matrix
    auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( *basis, boundaryDofs.first );
    auto rhs = std::vector<double>( matrix.size1( ), 0.0 );

    linalg::print( matrix, std::cout );

    // Perform domain integral
    MomentFittingQuadrature<D> partitioner( domain, penaltyFCM, integrationSpaceTreeDepth );
    //SpaceTreeQuadrature<D> partitioner( domain, penaltyFCM, integrationSpaceTreeDepth );

    // Constant volume force in z-direction
    auto E = spatial::constantFunction<D>( 2.0e5 );
    auto nu = spatial::constantFunction<D>( 0.2 );
    auto force = spatial::constantFunction<D>( std::array { 0.0, 0.0, 1.0 } );

    auto kinematics = makeSmallStrainKinematics<D>( );
    auto material = makeIsotropicElasticMaterial( E, nu );
    auto integrand = makeStaticDomainIntegrand<D>( kinematics, material, force );

    integrateOnDomain( *basis, integrand, { matrix, rhs }, partitioner, boundaryDofs );

    time = utilities::toc( time, "Preprocessing and assembly took: " );

    // Solve system
    auto preconditioner = makeAdditiveSchwarzPreconditioner( matrix, *basis, boundaryDofs.first );
    auto multiplyM = makeDefaultMultiply( matrix );
  
    //auto multiplyP = linalg::makeDiagonalPreconditioner( matrix );
    auto multiplyP = makeDefaultMultiply( preconditioner );

    std::vector<double> interiorSolution( matrix.size1( ), 0.0 );

    linalg::cg( multiplyM, rhs, interiorSolution, 1e-6, 0.0, matrix.size1( ), multiplyP );

    auto solution = boundary::inflate( interiorSolution, boundaryDofs );

    time = utilities::toc( time, "Solving took:                    " );

    auto processors = std::tuple
    {
        makeFunctionProcessor<D>( domain, "Domain" ),
        makeSolutionProcessor<D>( solution, "Displacement" ),
        makeVonMisesProcessor<D>( solution, kinematics, material )
    };

    //auto postmesh = createGridOnCells( resolution );
    auto postmesh = cellmesh::domain( domain, resolution );
    auto writer = VtuOutput { "outputs/wing" };

    // Postprocess solution
    writeOutput( *basis, postmesh, std::move( processors ), writer );

    utilities::toc( time, "Postprocessing took:             " );

    auto difference = std::abs( linalg::norm( solution ) - 35.13060947858399 );

    MLHP_CHECK( difference < 5e-7, "Backward consistency check failed." );
}
