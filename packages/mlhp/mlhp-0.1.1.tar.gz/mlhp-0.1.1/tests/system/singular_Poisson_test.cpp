// This file is part of the mlhp project. License: See LICENSE

#include "external/catch2/catch.hpp"

#include "mlhp/core/basis.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/refinement.hpp"
#include "mlhp/core/postprocessing.hpp"
#include "mlhp/core/boundary.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/partitioning.hpp"
#include "mlhp/core/integrands.hpp"
#include "mlhp/core/spatial.hpp"

namespace mlhp
{

template<size_t D>
auto computeSingularPoisson( size_t refinementLevel )
{
    auto circle = implicit::sphere<D>( array::make<D>( 0.0 ), 1e-10 );

    auto nelements = array::makeSizes<D>( 2 );
    auto lengths = array::make<D>( 1.0 );
    auto nsamples = array::makeSizes<D>( 6 );

    auto determinor = relativeQuadratureOrder<D>( 6 );

    auto kappa = spatial::constantFunction<D>( 1.0 );

    // Make and refine grid
    auto refinementStrategy = refineTowardsDomainBoundary( circle, refinementLevel );
    
    auto grid = makeRefinedGrid( nelements, lengths );

    grid->refine( refinementStrategy );

    // Create multi-level hp basis on refined grid
    auto basis = makeHpBasis<TensorSpace>( grid, LinearGrading { 1 } );

    // Analytical solution / source
    auto solution = solution::singularSolution<D>( );
    auto solutionDerivatives = solution::singularSolutionDerivatives<D>( );
    auto source = solution::singularSolutionSource<D>( );

    // Boundary conditions
    std::vector<size_t> faces;

    for( size_t axis = 0; axis < D; ++axis )
    {
        faces.push_back( D > 1 ? boundary::face( axis, 1 ) : boundary::face( axis, 0 ) );
    }

    auto boundaryDofs = boundary::boundaryDofs<D>( solution, *basis, faces, determinor );

    // Allocate sparse matrix
    auto matrix = allocateMatrix<linalg::SymmetricSparseMatrix>( *basis, boundaryDofs.first );
    auto vector = std::vector<double>( matrix.size1( ), 0.0 );

    // Assemble global system
    auto integrand = makePoissonIntegrand<D>( kappa, source );

    integrateOnDomain( *basis, integrand, { matrix, vector }, determinor, boundaryDofs );

    // Solve global system
    auto interiorSolution = linalg::makeCGSolver( 1e-8 )( matrix, vector );
    auto fullSolution = boundary::inflate( interiorSolution, boundaryDofs );

    // Integrate errors
    auto errorIntegrand1 = makeL2ErrorIntegrand( fullSolution, solution );
    auto errorIntegrand2 = makeEnergyErrorIntegrand( fullSolution, solutionDerivatives );

    auto l2Integrals = ErrorIntegrals { };
    auto energyIntegrals = ErrorIntegrals { };

    integrateOnDomain( *basis, errorIntegrand1, l2Integrals, determinor );
    integrateOnDomain( *basis, errorIntegrand2, energyIntegrals, determinor );

    // Write .vtu file
    auto processors = std::tuple
    {
        makeSolutionProcessor<D>( fullSolution ),
        makeRefinementLevelProcessor<D>( *grid ),
        makeFunctionProcessor<D>( solution, "AnalyticalSolution" )
    };

    auto filename = "outputs/systemtests/singular_poisson_" + std::to_string( D ) + 
        "D_" + std::to_string( refinementLevel );

    auto postmesh = cellmesh::grid( nsamples );

    writeOutput( *basis, postmesh, std::move( processors ), VtuOutput { filename } );

    return std::make_tuple( interiorSolution.size( ), l2Integrals, energyIntegrals );
}

TEST_CASE( "singular_poisson_1D" )
{
    std::vector<size_t> expectedNDof
    {
        2, 4, 7, 11, 16, 22, 29, 37, 46, 56, 67, 79, 92, 106, 121
    };

    //  || u_fe ||^2           || u_ex ||^2           || u_fe - u_ex ||^2 
    std::vector<double> expectedL2
    {
        6.914607633604007e-02, 8.504902721615198e-02, 2.928890993910548e-03,
        8.016221094407519e-02, 8.504970932813005e-02, 5.991769268849056e-04,
        8.325721653547175e-02, 8.504986201631788e-02, 1.234260964142547e-04,
        8.421589511839145e-02, 8.504989528024202e-02, 2.577582230557335e-05,
        8.458731502250817e-02, 8.504990239475595e-02, 5.523493705326081e-06,
        8.477005741242361e-02, 8.504990389678072e-02, 1.239140593183687e-06,
        8.487473596150186e-02, 8.504990421092019e-02, 2.993528336282569e-07,
        8.493893221484800e-02, 8.504990427616553e-02, 8.017155387904352e-08,
        8.497931751152689e-02, 8.504990428964616e-02, 2.415225056271726e-08,
        8.500494668521676e-02, 8.504990429242062e-02, 8.101605075046017e-09,
        8.502125833216244e-02, 8.504990429298966e-02, 2.943593247441695e-09,
        8.503164944448841e-02, 8.504990429310642e-02, 1.125072252676386e-09,
        8.503827085192792e-02, 8.504990429313017e-02, 4.426260639785544e-10,
        8.504249048393167e-02, 8.504990429313491e-02, 1.768592022715152e-10,
        8.504517958907377e-02, 8.504990429313561e-02, 7.123769608005646e-11
    };

    //  || u_fe ||^2           || u_ex ||^2           || u_fe - u_ex ||^2 
    std::vector<double> expectedEnergy
    {
        9.608234165274407e-02, 1.621973751253788e-01, 7.138588991963273e-02,
        1.273406970667416e-01, 1.800777704229674e-01, 5.799254570646351e-02,
        1.529296586181907e-01, 1.951448011230133e-01, 4.710475518403806e-02,
        1.738357784860602e-01, 2.077294819275249e-01, 3.826095386808723e-02,
        1.908941027538204e-01, 2.181722042036728e-01, 3.107755154709163e-02,
        2.047990133041843e-01, 2.267950324172362e-01, 2.524281571891652e-02,
        2.161246935413616e-01, 2.338886119246855e-01, 2.050353755851414e-02,
        2.253440044262195e-01, 2.397075316549283e-01, 1.665404751568436e-02,
        2.328451573735017e-01, 2.444703791165997e-01, 1.352729000364527e-02,
        2.389461093428775e-01, 2.483622205594243e-01, 1.098757372166665e-02,
        2.439067985173679e-01, 2.515381675756399e-01, 8.924683085555669e-03,
        2.479394289520614e-01, 2.541272631934935e-01, 7.249095222962551e-03,
        2.512170449243342e-01, 2.562362687079875e-01, 5.888094966265872e-03,
        2.538806360670874e-01, 2.579531412480326e-01, 4.782619246322538e-03,
        2.560449981297001e-01, 2.593501144371697e-01, 3.884693943738992e-03
    };

    for( size_t level = 0; level < 15; ++level )
    {
        auto [ndof, l2, energy] = computeSingularPoisson<1>( level );

        CHECK( ndof == expectedNDof[level] );

        CHECK( l2.analyticalSquared == Approx( expectedL2[3 * level + 0] ).margin( 1e-13 ) );
        CHECK( l2.numericalSquared == Approx( expectedL2[3 * level + 1] ).margin( 1e-13 ) );
        CHECK( l2.differenceSquared == Approx( expectedL2[3 * level + 2] ).margin( 1e-13 ) );

        CHECK( energy.analyticalSquared == Approx( expectedEnergy[3 * level + 0] ).margin( 1e-13 ) );
        CHECK( energy.numericalSquared == Approx( expectedEnergy[3 * level + 1] ).margin( 1e-13 ) );
        CHECK( energy.differenceSquared == Approx( expectedEnergy[3 * level + 2] ).margin( 1e-13 ) );
    }

} // singular_poisson_1D

TEST_CASE( "singular_poisson_2D" )
{
    std::vector<size_t> expectedNDof { 4, 16, 43, 91, 166, 274, 421 };

    //  || u_fe ||^2           || u_ex ||^2           || u_fe - u_ex ||^2 
    std::vector<double> expectedL2
    {
        7.875379152102370e-01, 7.651952986264087e-01, 9.162106683616916e-04,
        7.774108026781820e-01, 7.651956917460384e-01, 2.322246674511380e-04,
        7.730958399119884e-01, 7.651957148749008e-01, 7.885640983979245e-05,
        7.702400856424169e-01, 7.651957163550016e-01, 3.063787337350217e-05,
        7.684451610349655e-01, 7.651957164562875e-01, 1.256160582035055e-05,
        7.673058990120096e-01, 7.651957164636090e-01, 5.287370116218303e-06,
        7.665755790617267e-01, 7.651957164641640e-01, 2.261875945470946e-06
    };

    //  || u_fe ||^2           || u_ex ||^2           || u_fe - u_ex ||^2 
    std::vector<double> expectedEnergy
    {
        1.669654637845138e-01, 2.198442959916174e-01, 1.873143442308777e-02,
        1.862415033400312e-01, 2.201506937176595e-01, 8.501155357769815e-03,
        1.986873320886977e-01, 2.202667114514623e-01, 4.219228408228769e-03,
        2.065170321763431e-01, 2.203121446495678e-01, 2.106762438067322e-03,
        2.114608775429283e-01, 2.203304126020373e-01, 1.050715787413467e-03,
        2.145999470662706e-01, 2.203379157632553e-01, 5.237300542356567e-04,
        2.166061329811668e-01, 2.203410519230486e-01, 2.609902773331898e-04
    };

    for( size_t level = 0; level < expectedNDof.size( ); ++level )
    {
        auto [ndof, l2, energy] = computeSingularPoisson<2>( level );

        CHECK( ndof == expectedNDof[level] );

        CHECK( l2.analyticalSquared == Approx( expectedL2[3 * level + 0] ).margin( 1e-11 ) );
        CHECK( l2.numericalSquared == Approx( expectedL2[3 * level + 1] ).margin( 1e-11 ) );
        CHECK( l2.differenceSquared == Approx( expectedL2[3 * level + 2] ).margin( 1e-11 ) );

        CHECK( energy.analyticalSquared == Approx( expectedEnergy[3 * level + 0] ).margin( 1e-11 ) );
        CHECK( energy.numericalSquared == Approx( expectedEnergy[3 * level + 1] ).margin( 1e-11 ) );
        CHECK( energy.differenceSquared == Approx( expectedEnergy[3 * level + 2] ).margin( 1e-11 ) );
    }

} // singular_poisson_2D

TEST_CASE( "singular_poisson_3D" )
{
    std::vector<size_t> expectedNDof { 8, 64, 253, 701 };

    //  || u_fe ||^2           || u_ex ||^2           || u_fe - u_ex ||^2 
    std::vector<double> expectedL2
    {
        9.659905837600349e-01, 9.605919492908129e-01, 1.483443528911890e-04,
        9.601987618239501e-01, 9.605919562820383e-01, 8.680396212303872e-06,
        9.605839083298555e-01, 9.605919564504448e-01, 4.895078783405369e-07,
        9.605896008391291e-01, 9.605919564549138e-01, 3.088918625986140e-08
    };

    //  || u_fe ||^2           || u_ex ||^2           || u_fe - u_ex ||^2 
    std::vector<double> expectedEnergy
    {
        1.440899916775600e-01, 1.487644364150273e-01, 8.377824612160365e-03,
        1.476197015559576e-01, 1.487563097859692e-01, 1.354094673977860e-03,
        1.484575745290196e-01, 1.487550737832889e-01, 3.203256377277012e-04,
        1.486812267663147e-01, 1.487548754943080e-01, 8.015058386866951e-05
    };

    for( size_t level = 0; level < expectedNDof.size( ); ++level )
    {
        auto [ndof, l2, energy] = computeSingularPoisson<3>( level );

        CHECK( ndof == expectedNDof[level] );

        CHECK( l2.analyticalSquared == Approx( expectedL2[3 * level + 0] ).margin( 1e-12 ) );
        CHECK( l2.numericalSquared == Approx( expectedL2[3 * level + 1] ).margin( 1e-12 ) );
        CHECK( l2.differenceSquared == Approx( expectedL2[3 * level + 2] ).margin( 1e-12 ) );

        CHECK( energy.analyticalSquared == Approx( expectedEnergy[3 * level + 0] ).margin( 1e-13 ) );
        CHECK( energy.numericalSquared == Approx( expectedEnergy[3 * level + 1] ).margin( 1e-13 ) );
        CHECK( energy.differenceSquared == Approx( expectedEnergy[3 * level + 2] ).margin( 1e-13 ) );
    }

} // singular_poisson_3D

} // namespace mlhp
