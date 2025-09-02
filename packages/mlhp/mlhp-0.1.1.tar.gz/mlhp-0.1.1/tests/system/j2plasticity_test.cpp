// This file is part of the mlhp project. License: See LICENSE

#include "external/catch2/catch.hpp"
#include "mlhp/core.hpp"
#include <iomanip>

namespace mlhp
{

template<size_t D>
auto makeQuadraturePointIndexFinder( size_t quadratureOrder )
{
    auto points = gaussLegendrePoints( quadratureOrder )[0];
    auto strides = nd::stridesFor( array::make<D>( quadratureOrder ) );

    auto find1D = [=]( double r )
    {
        auto index = utilities::findInterval( points, r );
        auto local = utilities::mapToLocal0( points[index], points[index + 1], r );

        return local < 0.5 ? index : index + 1;
    };

    return [=]( std::array<double, D> rst )
    {
        auto index = size_t { 0 };

        for( size_t axis = 0; axis < D; ++axis )
        {
            index += strides[axis] * find1D( rst[axis] );
        }

        return index;
    };
}

struct HistoryVariables
{
    std::array<double, 6> stress = { };
    std::array<double, 6> backStress = { };
    double effectivePlasticStrain;
};

template<size_t D>
using HistoryAccessor = std::function<HistoryVariables&( CellIndex, std::array<double, D> )>;

template<size_t D>
auto makeHistory( CellIndex nelements, size_t quadratureOrder )
{
    auto indexFinder = makeQuadraturePointIndexFinder<D>( quadratureOrder );
    auto history = LinearizedVectors<HistoryVariables> { };
    auto generator = [=, n = size_t { 0 }] ( ) mutable { 
        return n = n + utilities::integerPow( quadratureOrder, 3 ); };

    std::get<0>( history ).resize( nelements + 1 );
    std::generate( std::get<0>( history ).begin( ), std::get<0>( history ).end( ), generator );
    std::get<1>( history ).resize( std::get<0>( history ).back( ) );

    return std::function { [=, history = std::move( history )]( CellIndex icell, 
                                                std::array<double, D> rst) mutable -> HistoryVariables&
    {
        return std::get<1>( history )[std::get<0>(history)[icell] + indexFinder( rst )];
    } };
}

// https://mae.ufl.edu/nkim/egm6352/Chap4.pdf
// https://www.youtube.com/watch?v=XO4FdwEwjG0&list=PL6f9zUtPSkfhAQyJ4GP1O-u4JKokNq4cU&index=1
// https://csm.mech.utah.edu/content/wp-content/uploads/2011/10/9tutorialOnJ2Plasticity.pdf
// Plasticity: returns 1) Stress increment for given strain increment 2) Consistant tangent
// Yield function f(Sigma, SigmaY) always zero when yielding
// Deviatoric projection: https://youtu.be/22f3ske1-e4?feature=shared&t=2295
// Return mapping: https://youtu.be/8ogBBoWptVQ?feature=shared&t=2952
// https://gitlab.lrz.de/cie_sam/adhocpp/-/blob/master/libraries/mathmodel/packages/material/src/materialFunctions.cpp?ref_type=heads#L1182

template<size_t D, size_t N>
struct NonlinearMaterial
{
    using Evaluate = std::array<double, N>( const BasisFunctionEvaluation<D>& shapes,
                                            std::array<double, N> totalStrainIncrement,
                                            std::span<double, N * N> tangentStiffness );

    static constexpr size_t ndim = D;
    static constexpr size_t ncomponents = N;
    
    bool symmetric = false;

    std::function<Evaluate> evaluate;
};

auto makeJ2Plasticity( const spatial::ScalarFunction<3>& youngsModulus,
                       const spatial::ScalarFunction<3>& poissonRatio,
                       double sigma0,
                       const HistoryAccessor<3>& historyAccessor0,
                       const HistoryAccessor<3>& historyAccessor1 )
{
    // Hardening coefficient
    double H = 0.5; 
    
    // beta = 0.0 -> isotropic hardening
    // beta = 1.0 -> kinematic hardening
    double beta = 0.0; 

    auto material = ConstitutiveEquation<3> { };

    material.evaluate = [=, &historyAccessor0, &historyAccessor1] ( 
        typename ConstitutiveEquation<3>::AnyCache&,
        const BasisFunctionEvaluation<3>& shapes,
        std::span<const double> totalStrainIncrement,
        std::span<double> stress,
        std::span<double> tangentStiffness )
    {
        auto& history0 = historyAccessor0( shapes.elementIndex( ), shapes.rst( ) );
        auto& history1 = historyAccessor1( shapes.elementIndex( ), shapes.rst( ) );

        // Linear elastic parameters
        auto nu = poissonRatio( shapes.xyz( ) );
        auto tmp1 = ( 1.0 - 2.0 * nu );
        auto tmp2 = youngsModulus( shapes.xyz( ) ) / ( ( 1.0 + nu ) * tmp1 );

        auto lambda = nu * tmp2;
        auto mu = 0.5 * tmp1 * tmp2;

        // Elastic tangent stiffness
        auto tangent = std::array<double, 6 * 6> { };
        auto D = linalg::adapter( tangent, 6 );
        auto diagonal = lambda + 2.0 * mu;

        D( 0, 0 ) = diagonal; D( 0, 1 ) = lambda;   D( 0, 2 ) = lambda;
        D( 1, 0 ) = lambda;   D( 1, 1 ) = diagonal; D( 1, 2 ) = lambda;
        D( 2, 0 ) = lambda;   D( 2, 1 ) = lambda;   D( 2, 2 ) = diagonal;
        D( 3, 3 ) = mu; D( 4, 4 ) = mu; D( 5, 5 ) = mu;

        // Trial stress
        auto sigmaTrialIncrement = std::array<double, 6> { };

        linalg::mmproduct( tangent.data( ), totalStrainIncrement.data( ), 
            sigmaTrialIncrement.data( ), 6, 6, 1 );

        auto sigmaTrial = history0.stress + sigmaTrialIncrement;
        auto sigmaTrialTrace = sigmaTrial[0] + sigmaTrial[1] + sigmaTrial[2];
        auto unitTensor = std::array<double, 6> { 1.0, 1.0, 1.0, 0.0, 0.0, 0.0 };

        // Shifted stress
        auto etaTrial = sigmaTrial - history0.backStress - 1.0 / 3.0 * sigmaTrialTrace * unitTensor;

        auto etaTrialNorm = std::sqrt( etaTrial[0] * etaTrial[0] +
                                       etaTrial[1] * etaTrial[1] + 
                                       etaTrial[2] * etaTrial[2] +
                               2.0 * ( etaTrial[3] * etaTrial[3] + 
                                       etaTrial[4] * etaTrial[4] + 
                                       etaTrial[5] * etaTrial[5] ) );

        // Yield function
        auto Hn = H;
        auto ep = history0.effectivePlasticStrain;

        auto f = etaTrialNorm - std::sqrt( 2.0 / 3.0 ) * ( sigma0 + ( 1.0 - beta ) * Hn * ep );
        
        // If elastic
        if( f < 0.0 )
        {
            if( !tangentStiffness.empty( ) )
            {
                std::copy( tangent.begin( ), tangent.end( ), tangentStiffness.begin( ) );
            }

            history1.stress = sigmaTrial;
            history1.backStress = history0.backStress;
            history1.effectivePlasticStrain = history0.effectivePlasticStrain;

            std::copy( history1.stress.begin( ), history1.stress.end( ), stress.begin( ) );
        }
        else
        {
            // Consistency parameter: flow amount
            auto deltaLambda = f / ( 2.0 * mu + 2.0 / 3.0 * H );

            // Unit deviatoric vector: flow direction
            auto N = etaTrial / etaTrialNorm;

            // Update history variables
            history1.stress = sigmaTrial - 2.0 * mu * deltaLambda * N;
            history1.backStress = history0.backStress + ( 2.0 / 3.0 ) * beta * H * deltaLambda * N;
            history1.effectivePlasticStrain = history0.effectivePlasticStrain + std::sqrt( 2.0 / 3.0 ) * deltaLambda;

            // Consistent / algorithmic tangent stiffness
            if( !tangentStiffness.empty( ) )
            {
                // Tangent stiffness
                auto c1 = 4.0 * mu * mu / ( 2.0 * mu + 2.0 / 3.0 * H );

                // Algorithmic contribution 
                auto c2 = 4.0 * mu * mu * deltaLambda / etaTrialNorm;

                auto Dalg = linalg::adapter( tangentStiffness, 6 );

                // Elastic with plastic correction
                for( size_t i = 0; i < 6; i++ )
                {
                    for( size_t j = 0; j < 6; j++ )
                    {
                        Dalg( i, j ) = D( i, j ) - ( c1 - c2 ) * N[i] * N[j];
                    }
                }
            
                // Deviatoric projection
                for( size_t i = 0; i < 3; ++i )
                {
                    for( size_t j = 0; j < 3; ++j )
                    {
                        Dalg( i, j ) -= -1.0 / 3.0 * c2;
                    }
                
                    Dalg( i + 0, i + 0 ) -= c2;
                    Dalg( i + 3, i + 3 ) -= c2 / 2.0;
                }
            }
        }

        std::copy( history1.stress.begin( ), history1.stress.end( ), stress.begin( ) );
    };

    material.ncomponents = 6;
    material.symmetric = true;
    material.incremental = true;
    material.name = "J2PlasticMaterial";

    return material;
}

ElementProcessor<3> postprocessPlasicity( const HistoryAccessor<3>& historyAccessor )
{
    auto evaluate = [&historyAccessor]( auto& shapes, auto&, auto&, auto target )
    {
        auto history = historyAccessor( shapes.elementIndex( ), shapes.rst( ) );

        auto [S11, S22, S33, S12, S23, S13] = history.stress;

        auto D1 = ( S11 - S22 ) * ( S11 - S22 );
        auto D2 = ( S22 - S33 ) * ( S22 - S33 );
        auto D3 = ( S33 - S11 ) * ( S33 - S11 );
        auto S = S12 * S12 + S23 * S23 + S13 * S13;

        target[0] = std::sqrt( 0.5 * ( D1 + D2 + D3 ) + 3.0 * S );
        target[1] = history.effectivePlasticStrain;
    };

    auto outputData = []( const AbsBasis<3>& ) -> Output
    {
        return { .name = "J2AndPlasticStrain",
                 .type = Output::Type::PointData, 
                 .ncomponents = 2 };
    };

    return detail::makeElementPointProcessor<3>( std::move( 
        evaluate ), std::move( outputData ), DiffOrders::NoShapes );
}

auto computeJ2Plasticity( const AbsBasis<3>& basis, double E, double nu, std::string name )
{
    static constexpr size_t D = 3;

    auto degree = basis::maxdegree( basis );
    auto& mesh = basis.mesh( );

    auto quadratureOffset = 1;

    auto nsteps = size_t { 5 };
    auto dofs0 = std::vector<double>( basis.ndof( ), 0.0 );
    
    auto history0 = makeHistory<3>( basis.nelements( ), degree + static_cast<size_t>( quadratureOffset ) );

    for( size_t istep = 1; istep <= nsteps; ++istep )
    {
        std::cout << "Load step " << istep << " / " << nsteps << ": || F || = " << std::flush;
        
        // Prepare dirichlet boundary conditions
        auto zeroScalarFunction = spatial::constantFunction<D>( 0.0 );
        auto zeroVectorFunction = spatial::constantFunction<D>( std::array { 0.0, 0.0, 0.0 } );
    
        auto dirichletFaces = std::vector
        {
            boundary::boundaryDofs<D>( zeroVectorFunction, basis, { boundary::left   } ),
            //boundary::boundaryDofs( zeroScalarFunction, basis, { boundary::front  }, 1 ),
            //boundary::boundaryDofs( zeroScalarFunction, basis, { boundary::back   }, 1 ),
            //boundary::boundaryDofs( zeroScalarFunction, basis, { boundary::bottom }, 2 ),
            //boundary::boundaryDofs( zeroScalarFunction, basis, { boundary::top    }, 2 ),
        };
        
        auto useForce = false;
        auto forceFunction = spatial::constantFunction<D>( array::make<D>( 0.0 ) );

        if( useForce )
        { 
            forceFunction = spatial::constantFunction<D>( std::array { istep * 1.0 / nsteps, 0.0, 0.0 } );
        }
        else
        {
            auto constraint = spatial::constantFunction<D>( istep * 3.0 / nsteps );

            dirichletFaces.push_back( boundary::boundaryDofs( constraint, basis, { boundary::right }, 1 ) );
            dirichletFaces.push_back( boundary::boundaryDofs( constraint, basis, { boundary::right }, 2 ) );
        }

        auto dirichlet = boundary::combine( std::move( dirichletFaces ) );

        // Physics 
        auto constantE = spatial::constantFunction<D>( E );
        auto constantNu = spatial::constantFunction<D>( nu );
        auto constantSy = 0.5;//2.0;

        auto kinematics = makeSmallStrainKinematics<D>( );
        auto constitutive = makeIsotropicElasticMaterial( constantE, constantNu );
        //auto constitutive = makeElastoplasticity( constantE, constantNu, constantSy );
        auto bodyForce = spatial::constantFunction<D>( std::array { 0.0, 0.0, 0.0 } );

        auto history1 = makeHistory<3>( basis.nelements( ), degree + static_cast<size_t>( quadratureOffset ) );

        // Neumann boundary conditions
        auto neumannIntegrand = makeNeumannIntegrand<D>( forceFunction );
        auto neumannQuadrature = boundary::QuadratureOnMeshFaces<D>( mesh, { boundary::right } );

        // Allocate matrix and assemble domain integral
        auto K = allocateMatrix<linalg::SymmetricSparseMatrix>( basis, dirichlet.first );
        auto F = std::vector<double>( K.size1( ), 0.0 );
        auto dofs = std::vector<double>( basis.ndof( ), 0.0 );

        auto norm0 = 0.0;

        // Newton-Raphson iterations
        for( size_t i = 0; i < 40; ++i )
        {
            std::fill( K.data( ), K.data( ) + K.nnz( ), 0.0 );
            std::fill( F.begin( ), F.end( ), 0.0 );
                    
            auto dirichletIncrement = dirichlet;

            for( size_t idof = 0; idof < dirichlet.first.size( ); ++idof )
            {
                dirichletIncrement.second[idof] = dirichlet.second[idof] - dofs[dirichlet.first[idof]];
            }

            auto dofIncrement = dofs;

            for( size_t idof = 0; idof < dofs0.size(); ++idof )
            {
                dofIncrement[idof] -= dofs0[idof];
            }

            auto material = makeJ2Plasticity( constantE, constantNu, constantSy, history0, history1 );
            auto integrand = makeStaticDomainIntegrand<D>( kinematics, material, dofIncrement, bodyForce );

            integrateOnDomain<D>( basis, integrand, { K, F }, dirichletIncrement, relativeQuadratureOrder<D>( quadratureOffset ) );

            if( useForce )
            {
                integrateOnSurface<D>( basis, neumannIntegrand, neumannQuadrature, { F }, dirichletIncrement );
            }

            auto norm1 = std::sqrt( std::inner_product( F.begin( ), F.end( ), F.begin( ), 0.0 ) );

            norm0 = i == 0 ? norm1 : norm0;

            std::cout << std::scientific << std::setprecision( 2 ) << norm1 << " " << std::flush;

            auto dx = boundary::inflate( linalg::makeCGSolver( )( K, F ), dirichletIncrement );

            std::transform( dofs.begin( ), dofs.end( ), dx.begin( ), dofs.begin( ), std::plus<double> { } );

            if( norm1 / norm0 <= 1e-6 ) break;
            if( ( i + 1 ) % 6 == 0 ) std::cout << "\n                ";
        }

        std::cout << std::endl;

        // Write .vtu file
        auto processors = std::tuple 
        {
            makeSolutionProcessor<D>( dofs, "Numerical" ),
            makeFunctionProcessor<D>( bodyForce, "Source" ),
            postprocessPlasicity( history1 ),
            //makeVonMisesProcessor<D>( dofs, kinematics, constitutive )
        };
    
        auto postmesh = cellmesh::grid( array::make<D>( degree ) );
        auto output = PVtuOutput { "outputs/systemtests/j2plasticity_" 
            + name + "_step_" + std::to_string( istep ) };

        writeOutput( basis, postmesh, std::move( processors ), output );

        // Integrate energy
        auto energyIntegrand = makeInternalEnergyIntegrand<D>( dofs, kinematics, constitutive );
        auto internalEnergy = double { 0.0 };

        integrateOnDomain<D>( basis, energyIntegrand, { internalEnergy }, dirichlet );

        dofs0 = dofs;
        history0 = std::move( history1 );
    }

    //return internalEnergy;
}

// To test unstructured mesh
UnstructuredMesh<3> meshUnitCube( bool quads );

TEST_CASE( "j2plasticity_test" )
{
    static constexpr size_t D = 3;
    
    auto E = 2.3;
    auto nu = 0.3;

    //// Square energy
    //auto expectedEnergy = 10.0 * E * ( 96975178.0 * nu - 64469539.0 ) / 
    //    ( 21.0 * ( 2.0 * nu * nu + nu - 1.0 ) ) / ( 8000.0 * 8000.0 );
    
    SECTION( "multiple elements" )
    {
        auto mesh = makeRefinedGrid<D>( { 40 / 2, 20 / 2, 20 / 2 }, { 8.0, 3.0, 3.0 } );
        auto basis = makeHpBasis<TrunkSpace>( mesh, 1, D );
        
        //auto energy = 
        computeJ2Plasticity( *basis, E, nu, "multiple" );

        //CHECK( energy == Approx( expectedEnergy ).epsilon( 1e-12 ) );
    }
    
    //SECTION( "single element" )
    //{
    //    auto mesh = makeRefinedGrid<D>( { 1, 1, 1 }, { 5.0, 3.0, 4.0 } );
    //    auto basis = makeHpBasis<TensorSpace>( mesh, 4, D );
    //    
    //    auto energy = computeElasticProblem( *basis, E, nu, "single" );

    //    CHECK( energy == Approx( expectedEnergy ).epsilon( 1e-12 ) );
    //}

    //SECTION( "unstructured quad mesh" )
    //{
    //    auto mesh = std::make_shared<UnstructuredMesh<D>>( meshUnitCube( true ) );
    //    auto basis = UnstructuredBasis<D>( mesh, D );

    //    //print( *mesh, std::cout );
    //    //print( basis, std::cout );

    //    auto energy = computeElasticProblem( basis, E, nu, "unstructured_quads" );

    //    //std::cout << energy << " vs. " << expectedEnergy << std::endl;
    //    //std::cout << std::scientific << std::setprecision(12) << energy<< std::endl;

    //    // Check consistency with previous versions
    //    CHECK( energy == Approx( 1.164722869049 ).epsilon( 1e-8 ) );
    //}
    //
    //SECTION( "unstructured tet mesh" )
    //{
    //    auto mesh = std::make_shared<UnstructuredMesh<D>>( meshUnitCube( false ) );
    //    auto basis = UnstructuredBasis<D>( mesh, D );

    //    //print( *mesh, std::cout );
    //    //print( basis, std::cout );

    //    auto energy = computeElasticProblem( basis, E, nu, "unstructured_tets" );

    //    //std::cout << energy << " vs. " << expectedEnergy << std::endl;
    //    //std::cout << std::scientific << std::setprecision(12) << energy<< std::endl;

    //    // Check consistency with previous versions
    //    CHECK( energy == Approx( 1.173093446568 ).epsilon( 1e-8 ) );
    //}
}

} // namespace mlhp
