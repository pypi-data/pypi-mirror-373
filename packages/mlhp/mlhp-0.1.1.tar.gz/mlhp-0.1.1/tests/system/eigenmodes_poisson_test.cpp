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

TEST_CASE( "eigenmodes_poisson_test" )
{
    static constexpr size_t D = 2;

    auto nelements = array::makeSizes<D>( 3 );
    auto lengths = array::make<D>( 1.0 );
    auto degree = size_t { 4 };
    auto nsamples = array::makeSizes<D>( degree > 1 ? degree + 6 : degree );

    // Create uniform finite element mesh
    auto grid = makeRefinedGrid( nelements, lengths );
    auto basis = makeHpBasis<TrunkSpace>( grid, degree );

    //print( *basis, std::cout );

    //// Analytical solution / source
    //auto solution = solution::singularSolution<D>( );
    //auto solutionDerivatives = solution::singularSolutionDerivatives<D>( );
    //auto source = solution::singularSolutionSource<D>( );

    // Fix all four sides
    auto boundaryDofs = boundary::boundaryDofs<D>( spatial::constantFunction<D>( 0.0 ), *basis, boundary::allFaces( D ) );

    // Allocate sparse matrix
    auto sparseK = allocateMatrix<linalg::SymmetricSparseMatrix>( *basis, boundaryDofs.first );
    auto sparseM = allocateMatrix<linalg::SymmetricSparseMatrix>( *basis, boundaryDofs.first );
    auto vector = std::vector<double>( sparseK.size1( ), 0.0 );

    // Assemble global system
    auto kappa = spatial::constantFunction<D>( 1.0 );
    auto noRhs = std::optional<spatial::ScalarFunction<D>> { std::nullopt };

    auto integrandK = makePoissonIntegrand<D>( kappa, spatial::constantFunction<D>( 0.0 ) );
    auto integrandM = makeL2DomainIntegrand<D>( spatial::constantFunction<D>( 1.0 ), noRhs, nullptr );

    integrateOnDomain( *basis, integrandK, { sparseK, vector }, boundaryDofs );
    integrateOnDomain( *basis, integrandM, { sparseM }, boundaryDofs );

    auto K = linalg::todense( sparseK );
    auto M = linalg::todense( sparseM );

    auto ndof = sparseK.size2( );

    auto lambda = std::vector<double>( ndof );
    auto modes  = std::vector<double>( M.size( ) );
    auto imag = std::vector<double>( ndof );
    auto perm = std::vector<size_t>( ndof );

    linalg::eig( K, M, lambda, imag, perm, modes );
    linalg::sorteig( lambda, modes );

    auto nmodes = DofIndex { 16 };
    auto postmesh = cellmesh::grid( nsamples );

    for( size_t i = 0; i < std::min( nmodes, ndof ); ++i )
    {
        auto vi = std::span( modes ).subspan( i * ndof, ndof );
        auto dofs = utilities::moveShared( boundary::inflate( vi, boundaryDofs ) );

        auto processor = makeSolutionProcessor<D>( dofs, "Mode" );
        auto filename = "outputs/systemtests/eigenmodes_poisson_" + std::to_string( D ) + "D_" + std::to_string( i );

        writeOutput( *basis, postmesh, processor, VtuOutput { filename } );
    }

    CHECK( linalg::norm( imag ) < 1e-12 );

    // Check first 10 eigenvalues to make sure result are still the same
    CHECK( lambda[0] == Approx( 19.7393348606987 ).epsilon( 1e-10 ) );
    CHECK( lambda[1] == Approx( 49.3529159325756 ).epsilon( 1e-10 ) );
    CHECK( lambda[2] == Approx( 49.3529159325756 ).epsilon( 1e-10 ) );
    CHECK( lambda[3] == Approx( 79.0985758311807 ).epsilon( 1e-10 ) );
    CHECK( lambda[4] == Approx( 98.7170297692444 ).epsilon( 1e-10 ) );
    CHECK( lambda[5] == Approx( 98.7170297692447 ).epsilon( 1e-10 ) );
    CHECK( lambda[6] == Approx( 129.283951556864 ).epsilon( 1e-10 ) );
    CHECK( lambda[7] == Approx( 129.283951556864 ).epsilon( 1e-10 ) );
    CHECK( lambda[8] == Approx( 168.284984213955 ).epsilon( 1e-10 ) );
    CHECK( lambda[9] == Approx( 168.284984213955 ).epsilon( 1e-10 ) );
}

} // namespace mlhp
