// This file is part of the mlhp project. License: See LICENSE

#include "external/catch2/catch.hpp"
#include "mlhp/core.hpp"

namespace mlhp
{

// Manufactured solution defined later
spatial::VectorFunction<3, 3> elasticSolution ( );
spatial::VectorFunction<3, 3> elasticSource( double E, double nu );
spatial::VectorFunction<3, 6> elasticStress( double E, double nu  );
spatial::VectorFunction<3, 3> elasticTraction( double E, double nu, size_t axis, size_t side );

auto computeElasticProblem( const AbsBasis<3>& basis, double E, double nu, std::string name )
{
    static constexpr size_t D = 3;

    auto degree = basis::maxdegree( basis );
    auto& mesh = basis.mesh( );

    // Physics 
    auto constantE = spatial::constantFunction<D>( E );
    auto constantNu = spatial::constantFunction<D>( nu );

    auto kinematics = makeSmallStrainKinematics<D>( );
    auto constitutive = makeIsotropicElasticMaterial( constantE, constantNu );

    auto bodyForce = elasticSource( E, nu );
    auto integrand = makeStaticDomainIntegrand<D>( kinematics, constitutive, bodyForce );

    // Prepare dirichlet boundary conditions
    auto analyticalSolution = elasticSolution( );
    
    auto dirichetFaces = std::vector
    {
        boundary::boundaryDofs<D>( analyticalSolution, basis, { boundary::right } ),
        boundary::boundaryDofs<D>( analyticalSolution, basis, { boundary::front } ),
        boundary::boundaryDofs<D>( analyticalSolution, basis, { boundary::top } ),
    };

    auto dirichlet = boundary::combine( std::move( dirichetFaces ) );

    // Allocate matrix and assemble domain integral
    auto K = allocateMatrix<linalg::SymmetricSparseMatrix>( basis, dirichlet.first );
    auto F = std::vector<double>( K.size1( ), 0.0 );

    integrateOnDomain<D>( basis, integrand, { K, F }, dirichlet );
    
    // Neumann boundary conditions
    auto integrandBack = makeNeumannIntegrand<D>( elasticTraction( E, nu, 1, 1 ) );
    auto integrandBottom = makeNeumannIntegrand<D>( elasticTraction( E, nu, 2, 0 ) );

    auto quadratureBack = boundary::QuadratureOnMeshFaces<D>( mesh, { boundary::back } );
    auto quadratureBottom = boundary::QuadratureOnMeshFaces<D>( mesh, { boundary::bottom } );

    integrateOnSurface<D>( basis, integrandBack, quadratureBack, { F }, dirichlet );
    integrateOnSurface<D>( basis, integrandBottom, quadratureBottom, { F }, dirichlet );

    // Solve
    auto maxiter = std::max( K.size1( ), DofIndex { 2000 } );
    auto reducedDofs = linalg::makeCGSolver( 1e-12, 0.0, maxiter )( K, F );
    auto dofs = boundary::inflate( reducedDofs, dirichlet );

    // Write .vtu file
    auto processors = std::tuple 
    {
        makeSolutionProcessor<D>( dofs, "Numerical" ),
        makeFunctionProcessor<D>( analyticalSolution, "Analytical" ),
        makeFunctionProcessor<D>( bodyForce, "Source" ),
        makeVonMisesProcessor<D>( dofs, kinematics, constitutive )
    };
    
    auto postmesh = cellmesh::grid( array::make<D>( degree ) );
    auto output = VtuOutput { "outputs/systemtests/elasticity_" + name };

    writeOutput( basis, postmesh, std::move( processors ), output );

    // Integrate energy
    auto energyIntegrand = makeInternalEnergyIntegrand<D>( dofs, kinematics, constitutive );
    auto internalEnergy = double { 0.0 };

    integrateOnDomain<D>( basis, energyIntegrand, { internalEnergy }, dirichlet );

    // Integrate reaction forces on Dirichlet faces
    auto reactionIntegrand = makeReactionForceIntegrand<D>( kinematics, constitutive, dofs );
    auto reactionForces = std::vector<std::array<double, D>> { };

    for( auto face : { boundary::right, boundary::front, boundary::top } )
    {
        reactionForces.emplace_back( std::array<double, D> { } );

        auto targetVector = AssemblyTargetVector( reactionForces.back( ).begin( ), reactionForces.back( ).end( ) );
        auto faceQuadrature = boundary::QuadratureOnMeshFaces<D>( mesh, { face } );

        integrateOnSurface( basis, reactionIntegrand, faceQuadrature, targetVector );
    }

    return std::tuple { internalEnergy, reactionForces };
}

// Exact solution for right, front, and top face reaction forces
std::array<double, 3> reactionForce( double E, double nu, size_t iface );

// To test unstructured mesh
UnstructuredMesh<3> meshUnitCube( bool quads );

TEST_CASE( "elasticity_test" )
{
    static constexpr size_t D = 3;
    
    auto E = 2.3;
    auto nu = 0.3;

    // Square energy
    auto expectedEnergy = 10.0 * E * ( 96975178.0 * nu - 64469539.0 ) / 
        ( 21.0 * ( 2.0 * nu * nu + nu - 1.0 ) ) / ( 8000.0 * 8000.0 );
    
    SECTION( "multiple elements" )
    {
        auto mesh = makeRefinedGrid<D>( { 4, 2, 3 }, { 5.0, 3.0, 4.0 } );
        auto basis = makeHpBasis<TrunkSpace>( mesh, 5, D );
        
        auto [energy, reaction] = computeElasticProblem( *basis, E, nu, "multiple" );

        CHECK( energy == Approx( expectedEnergy ).epsilon( 1e-11 ) );

        CHECK( spatial::distance( reaction[0], reactionForce( E, nu, boundary::right ) ) < 1e-9 );
        CHECK( spatial::distance( reaction[1], reactionForce( E, nu, boundary::front ) ) < 1e-9 );
        CHECK( spatial::distance( reaction[2], reactionForce( E, nu, boundary::top ) ) < 1e-9 );
    }
    
    SECTION( "single element" )
    {
        auto mesh = makeRefinedGrid<D>( { 1, 1, 1 }, { 5.0, 3.0, 4.0 } );
        auto basis = makeHpBasis<TensorSpace>( mesh, 4, D );
        
        auto [energy, reaction] = computeElasticProblem( *basis, E, nu, "single" );

        CHECK( energy == Approx( expectedEnergy ).epsilon( 1e-12 ) );

        CHECK( spatial::distance( reaction[0], reactionForce( E, nu, boundary::right ) ) < 1e-10 );
        CHECK( spatial::distance( reaction[1], reactionForce( E, nu, boundary::front ) ) < 1e-10 );
        CHECK( spatial::distance( reaction[2], reactionForce( E, nu, boundary::top ) ) < 1e-10 );
    }

    SECTION( "unstructured quad mesh" )
    {
        auto mesh = std::make_shared<UnstructuredMesh<D>>( meshUnitCube( true ) );
        auto basis = UnstructuredBasis<D>( mesh, D );

        //print( *mesh, std::cout );
        //print( basis, std::cout );

        auto [energy, reaction] = computeElasticProblem( basis, E, nu, "unstructured_quads" );

        //std::cout << energy << " vs. " << expectedEnergy << std::endl;
        //std::cout << std::scientific << std::setprecision(12) << energy<< std::endl;

        // Check consistency with previous versions
        CHECK( energy == Approx( 1.164722869049 ).epsilon( 1e-8 ) );

        CHECK( spatial::distance<3>( reaction[0], std::array { -0.294558218402282, -1.92975920936874, 1.11333964703361 } ) < 1e-10 );
        CHECK( spatial::distance<3>( reaction[1], std::array { 1.26741456343562, -1.26250436035523, 0.255307747230697 } ) < 1e-10 );
        CHECK( spatial::distance<3>( reaction[2], std::array { -0.14389367797082, 0.986955736786777, -5.33803497318163 } ) < 1e-10 );
    }
    
    SECTION( "unstructured tet mesh" )
    {
        auto mesh = std::make_shared<UnstructuredMesh<D>>( meshUnitCube( false ) );
        auto basis = UnstructuredBasis<D>( mesh, D );

        //print( *mesh, std::cout );
        //print( basis, std::cout );

        auto [energy, reaction] = computeElasticProblem( basis, E, nu, "unstructured_tets" );

        //std::cout << energy << " vs. " << expectedEnergy << std::endl;
        //std::cout << std::scientific << std::setprecision(12) << energy<< std::endl;

        // Check consistency with previous versions
        CHECK( energy == Approx( 1.1730924543 ).epsilon( 1e-8 ) );

        CHECK( spatial::distance<3>( reaction[0], std::array { -0.299646025400525, -1.89001890327191, 1.11576730063222 } ) < 1e-10 );
        CHECK( spatial::distance<3>( reaction[1], std::array { 1.18400255318392, -1.16315336006594, 0.293238801169052 } ) < 1e-10 );
        CHECK( spatial::distance<3>( reaction[2], std::array { -0.203574439530525, 0.962261141032476, -5.66733826900833 } ) < 1e-10 );
    }

    SECTION( "bsplines" )
    {
        auto mesh = makeCartesianGrid<D>( { 3, 1, 2 }, { 5.0, 3.0, 4.0 } );
        auto basis = makeBSplineBasis<D>( mesh, { 4, 5, 4 }, { 3, 3, 0 }, D );

        auto [energy, reaction] = computeElasticProblem( *basis, E, nu, "bsplines" );

        CHECK( energy == Approx( expectedEnergy ).epsilon( 1e-10 ) );

        CHECK( spatial::distance( reaction[0], reactionForce( E, nu, boundary::right ) ) < 1e-10 );
        CHECK( spatial::distance( reaction[1], reactionForce( E, nu, boundary::front ) ) < 1e-10 );
        CHECK( spatial::distance( reaction[2], reactionForce( E, nu, boundary::top ) ) < 1e-10 );
    }
}

//! Python sympy script for analytical solution (scale by 1/8000)
/*
 * import sympy
 * 
 * x = sympy.symarray('x', 3)
 * E, nu = sympy.symbols('E nu')
 * 
 * # Manufactured solution
 * u = [x[0] * x[0] * ( x[0] - 8 ) * ( 5 * x[1] * x[2] - 2 * ( x[1] - 4 ) * ( x[2] - 5 ) ),
 *      2 * x[0] * x[0] * x[1] * ( -x[0] + 3 * ( x[0] - 7 ) * ( x[2] - 4 ) ) + 108 * x[2] * ( x[2] - 6 ),
 *      2 * x[0] * x[0] * ( -x[2] * x[2] * ( x[0] - 6 ) * ( x[1] - 4 ) + 75 ) + 57 * x[1] * ( x[1] - 2 )]
 *      
 * # Deformation gradient     
 * du = sympy.Matrix([[sympy.diff(ui, xi) for xi in x] for ui in u])
 * 
 * # Engineering strain in Voigt notation
 * strain = sympy.Matrix([[du[0, 0], 
 *                         du[1, 1], 
 *                         du[2, 2], 
 *                         du[1, 2] + du[2, 1], 
 *                         du[0, 2] + du[2, 0], 
 *                         du[0, 1] + du[1, 0]]]).T
 * 
 * # Material matrix: only mu on lower diagonal due to engineering strain
 * la = nu * E / ((1 + nu)*(1 - 2 * nu))
 * mu = E / (2 * (1 + nu))
 * 
 * C = sympy.Matrix([[2 * mu + la,          la,          la,     0,      0,     0],
 *                   [         la, 2 * mu + la,          la,     0,      0,     0],
 *                   [         la,          la, 2 * mu + la,     0,      0,     0],
 *                   [          0,           0,           0,    mu,      0,     0],
 *                   [          0,           0,           0,     0,     mu,     0],
 *                   [          0,           0,           0,     0,      0,    mu]])
 * 
 * # Material times strain gives stress
 * stress = C @ strain
 * 
 * S = sympy.Matrix([[stress[0], stress[5], stress[4]],
 *                   [stress[5], stress[1], stress[3]],
 *                   [stress[4], stress[3], stress[2]]])
 *      
 * # Divergence of stress gives force vector
 * force = [sympy.diff(S[0, 0], x[0]) + sympy.diff(S[1, 0], x[1]) + sympy.diff(S[2, 0], x[2]),
 *          sympy.diff(S[0, 1], x[0]) + sympy.diff(S[1, 1], x[1]) + sympy.diff(S[2, 1], x[2]),
 *          sympy.diff(S[0, 2], x[0]) + sympy.diff(S[1, 2], x[1]) + sympy.diff(S[2, 2], x[2])]
 * 
 * energy = sympy.integrate(stress[0] * strain[0] + stress[1] * strain[1] + stress[2] * strain[2] + 
 *                          stress[3] * strain[3] + stress[4] * strain[4] + stress[5] * strain[5], 
 *                          (x[0], 0, 5), (x[1], 0, 3), (x[2], 0, 4)) / 2
 * 
 * # right, front and top faces
 * right = sympy.integrate(S[:, 0].subs(x[0], 5), (x[1], 0, 3), (x[2], 0, 4))
 * front = sympy.integrate(-S[:, 1].subs(x[1], 0), (x[0], 0, 5), (x[2], 0, 4))
 * top = sympy.integrate(S[:, 2].subs(x[2], 4), (x[0], 0, 5), (x[1], 0, 3))
 * 
 * for i, s in enumerate(stress[:, 0]):
 *     print(f"stress[{i}] = {sympy.simplify(s)}")
 * 
 * for i, f in enumerate(force):
 *     print(f"force[{i}] = {sympy.simplify(-f)}")
 *     
 * print(f"energy = {sympy.simplify(energy)}")
 * 
 * print(f"right reaction: {[sympy.simplify(row) for row in right]}")
 * print(f"front reaction: {[sympy.simplify(row) for row in front]}")
 * print(f"top reaction: {[sympy.simplify(row) for row in top]}")
 */

// Manufactured solution with homogeneous Neumann on left face
spatial::VectorFunction<3, 3> elasticSolution( )
{
    return [=] ( std::array<double, 3> xyz ) noexcept
    {
        auto [x, y, z] = xyz;

        auto u = x * x * ( x - 8 ) * ( 5 * y * z - 2 * ( y - 4 ) * ( z - 5 ) );
        auto v = 2 * x * x * y * ( -x + 3 * ( x - 7 ) * ( z - 4 ) ) + 108 * z * ( z - 6 );
        auto w = 2 * x * x * ( -z * z * ( x - 6 ) * ( y - 4 ) + 75 ) + 57 * y * ( y - 2 );
        
        return std::array { u / 8000.0, v / 8000.0, w / 8000.0 - 1.0 / 4.0 };
    };
}

// Corresponding volume force
spatial::VectorFunction<3, 3> elasticSource( double E, double nu )
{
    return [=]( std::array<double, 3> xyz ) noexcept
    {
        auto [x, y, z] = xyz;

        auto fx = ( 2 * nu * x * ( -2 * x * z * ( y - 4 ) + x * ( 3 * z - 13 ) - 
            2 * x - 4 * z * ( x - 6 ) * ( y - 4 ) + 6 * ( x - 7 ) * ( z - 4 ) ) + 
            x * ( 2 * nu - 1 ) * (-x * ( 3 * z - 13 ) + 2 * x + 6 * z * ( x - 4 ) * 
                ( y - 4 ) - 6 * ( x - 7 ) * ( z - 4 ) ) + 2 * ( 1 - nu ) * ( 3 * x - 8 ) * 
            ( 5 * y * z - 2 * ( y - 4 ) * ( z - 5 ) ) ) / ( ( nu + 1 ) * ( 2 * nu - 1 ) );
        auto fy = ( -72 * nu * x * y * z + 312 * nu * x * y + 168 * nu * y * z - 
            672 * nu * y - 432 * nu - 4 * x * x * x * z + 33 * x * x * z + 30 * x * x + 
            36 * x * y * z - 156 * x * y - 48 * x * z - 160 * x - 84 * y * z + 
            336 * y + 216) / ( 2 * ( 2 * nu * nu + nu - 1 ) );
        auto fz = ( 2 * nu * x * ( 6 * x * ( x - 7 ) + ( 3 * x - 16 ) * ( 3 * y + 8 ) ) - 
            8 * x * x * ( 1 - nu ) * ( x - 6 ) * ( y - 4 ) + ( 2 * nu - 1 ) * ( -6 * x * x * 
                ( x - 7 ) - x * x * ( 3 * y + 8 ) + 8 * x * z * z * ( y - 4 ) - 2 * x * 
                ( x - 8 ) * ( 3 * y + 8 ) + 4 * z * z * ( x - 6 ) * ( y - 4 ) - 414 ) ) / 
            ( 2 * ( nu + 1 ) * ( 2 * nu - 1 ) );
        
        return std::array { E * fx / 8000.0, E * fy / 8000.0, E * fz / 8000.0 };
    };
}

// Corresponding stress tensor
spatial::VectorFunction<3, 6> elasticStress( double E, double nu  )
{
    return [=]( std::array<double, 3> xyz ) noexcept
    {
        auto S = std::array<double, 6> { };
        auto [x, y, z] = xyz;

        S[0] = x * ( 2 * nu * x * ( x + 2 * z * ( x - 6 ) * ( y - 4 ) - 3 * ( x - 7 ) *  
            ( z - 4 ) ) - ( 1 - nu ) * ( 3 * x - 16 ) * ( 5 * y * z - 2 * ( y - 4 ) * 
            ( z - 5 ) ) ) / ( ( nu + 1 ) * ( 2 * nu - 1 ) );
        S[1] = x * ( nu * ( 4 * x * z * ( x - 6 ) * ( y - 4 ) - ( 3 * x - 16 ) * 
            ( 5 * y * z - 2 * ( y - 4 ) * ( z - 5 ) ) ) + 2 * x * ( 1 - nu ) * 
            ( x - 3 * ( x - 7 ) * ( z - 4 ) ) ) / ( ( nu + 1 ) * ( 2 * nu - 1 ) );
        S[2] = x * ( nu * (2 * x * ( x - 3 * ( x - 7 ) * ( z - 4 ) ) - ( 3 * x - 16 ) * 
            ( 5 * y * z - 2 * ( y - 4 ) * ( z - 5 ) ) ) + 4 * x * z * ( 1 - nu ) * 
            ( x - 6 ) * ( y - 4 ) ) / ( ( nu + 1 ) * ( 2 * nu - 1 ) );
        S[3] = ( 3 * x * x * y * ( x - 7 ) + x * x * z * z * ( 6 - x ) + 57 * y + 
            108 * z - 381 ) / ( nu + 1 );
        S[4] = -x * ( 2 * x * z * z * ( y - 4 ) - x * ( x - 8 ) * ( 3 * y + 8 ) + 
            4 * z * z * ( x - 6 ) * ( y - 4 ) - 300 ) / ( 2 * nu + 2 );
        S[5] = x * ( 2 * x * y * ( 3 * z - 13 ) + x * ( x - 8 ) * ( 3 * z + 10 ) - 
            4 * y * ( x - 3 * ( x - 7 ) * ( z - 4 ) ) ) / ( 2 * ( nu + 1 ) );

        auto transform = [=]( auto value ) { return E * value / 8000.0; };

        std::transform( S.begin( ), S.end( ), S.begin( ), transform );

        return S;
    };
}

spatial::VectorFunction<3, 3> elasticTraction( double E, double nu, size_t axis, size_t side )
{
    auto stress = elasticStress( E, nu );

    return [=]( std::array<double, 3> xyz ) noexcept
    {
        auto S = stress( xyz );
        auto normal = array::makeAndSet<double, 3>( 0.0, axis, side ? 1.0 : -1.0 );

        auto stressTensor = std::array { S[0], S[5], S[4], 
                                         S[5], S[1], S[3],
                                         S[4], S[3], S[2] };

        return linalg::mvproduct<3, 3>( stressTensor, normal );
    };
}

std::array<double, 3> reactionForce( double E, double nu, size_t iface )
{
    if( iface == boundary::right )
    {
        return std::array {  1800 * E * nu / ( ( nu + 1 ) * ( 2 * nu - 1 ) ), 
                            -9090 * E / ( nu + 1 ), 
                             5775 * E / ( nu + 1 ) } / 8000;
    }
    else if( iface == boundary::front )
    {
        return std::array {  17000 * E / ( 3 * ( nu + 1 ) ), 
                             150 * E * ( 35 - 67 * nu ) / ( 2 * nu * nu + nu - 1 ), 
                             1300 * E / ( nu + 1 ) } / 8000;
    }
    else if( iface == boundary::top )
    {
        return std::array { -11125 * E / ( 16 * nu + 16 ), 
                             37755 * E / ( 8 * ( nu + 1 ) ), 
                             1875 * E * ( 12 - 5 * nu ) / ( 2 * ( 2 * nu * nu + nu - 1 ) ) } / 8000;
    }
    
    MLHP_THROW( "Invalid face index." );
}

UnstructuredMesh<3> meshUnitCube( bool quads )
{
    static constexpr size_t D = 3;

    auto nelements = std::array<size_t, D> { 14, 10, 12 };
    auto nvertices = array::add<size_t>( nelements, 1 );

    auto vertices = CoordinateList<D> { };
    auto connectivity = std::vector<size_t> { };
    auto offsets = std::vector<size_t> { 0 };

    auto xyzGenerator = spatial::makeGridPointGenerator( nvertices );

    nd::execute( nvertices, [&]( auto ijk )
    {
        auto xyz = xyzGenerator( ijk );

        auto d = 0.08 * std::sin( xyz[0] * 2.0 * std::numbers::pi ) *
                        std::sin( xyz[1] * 2.0 * std::numbers::pi ) *
                        std::sin( xyz[2] * 2.0 * std::numbers::pi );

        vertices.push_back( { 5.0 * ( xyz[0] + d ), 
                              3.0 * ( xyz[1] + d ), 
                              4.0 * ( xyz[2] + d ) } );
    } );
    
    auto engine1 = std::mt19937 { 0 };
    auto random1 = std::uniform_int_distribution<size_t> { }; 

    auto shuffle = [&]( auto& indices, size_t n )
    {
        for( size_t i = 0; i < n; ++i )
        {
            auto i0 = random1( engine1 ) % n;
            auto i1 = random1( engine1 ) % n;

            std::swap( indices[indices.size( ) - i0 - 1], 
                       indices[indices.size( ) - i1 - 1] );
        }
    };

    nd::execute( nelements, [&]( auto ijk )
    {
        auto indices = std::array 
        { 
            ( ijk[0] + 0 ) * nvertices[1] * nvertices[2] + ( ijk[1] + 0 ) * nvertices[2] + ijk[2] + 0, 
            ( ijk[0] + 0 ) * nvertices[1] * nvertices[2] + ( ijk[1] + 0 ) * nvertices[2] + ijk[2] + 1,
            ( ijk[0] + 0 ) * nvertices[1] * nvertices[2] + ( ijk[1] + 1 ) * nvertices[2] + ijk[2] + 0, 
            ( ijk[0] + 0 ) * nvertices[1] * nvertices[2] + ( ijk[1] + 1 ) * nvertices[2] + ijk[2] + 1, 
            ( ijk[0] + 1 ) * nvertices[1] * nvertices[2] + ( ijk[1] + 0 ) * nvertices[2] + ijk[2] + 0, 
            ( ijk[0] + 1 ) * nvertices[1] * nvertices[2] + ( ijk[1] + 0 ) * nvertices[2] + ijk[2] + 1,
            ( ijk[0] + 1 ) * nvertices[1] * nvertices[2] + ( ijk[1] + 1 ) * nvertices[2] + ijk[2] + 0, 
            ( ijk[0] + 1 ) * nvertices[1] * nvertices[2] + ( ijk[1] + 1 ) * nvertices[2] + ijk[2] + 1,
        };
        
        if( quads )
        {
            for( size_t i = 0; i < 8; ++i )
            {
                connectivity.push_back( indices[i] );
            }

            offsets.push_back( connectivity.size( ) );
        }
        else
        {
            constexpr auto tets = spatial::simplexSubdivisionIndices<D>( );

            for( auto tet : tets )
            {
                for( size_t i = 0; i < 4; ++i )
                {
                    connectivity.push_back( indices[tet[i]] );
                }

                shuffle( connectivity, 4 );

                offsets.push_back( connectivity.size( ) );
            }
        }
    } );

    return UnstructuredMesh<D> ( std::move( vertices ), 
        std::move( connectivity ), std::move( offsets ) );
}

} // namespace mlhp
