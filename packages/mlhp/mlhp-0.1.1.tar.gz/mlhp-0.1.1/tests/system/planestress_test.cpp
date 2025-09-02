// This file is part of the mlhp project. License: See LICENSE

#include "external/catch2/catch.hpp"
#include "mlhp/core.hpp"

namespace mlhp
{

// Manufactured solution defined later
spatial::VectorFunction<2, 2> planeStressSolution ( );
spatial::VectorFunction<2, 2> planeStressSource( double E, double nu );
spatial::VectorFunction<2, 3> planeStressStress( double E, double nu  );
spatial::VectorFunction<2, 2> planeStressBackTraction( double E, double nu  );
spatial::VectorFunction<2, 2> planeStressRightTraction( double E, double nu  );

auto computePlaneStress( const AbsBasis<2>& basis, double E, double nu, std::string name )
{
    static constexpr size_t D = 2;

    auto degree = basis::maxdegree( basis );
    auto& mesh = basis.mesh( );

    // Physics 
    auto constantE = spatial::constantFunction<D>( E );
    auto constantNu = spatial::constantFunction<D>( nu );

    auto kinematics = makeSmallStrainKinematics<D>( );
    auto constitutive = makePlaneStressMaterial( constantE, constantNu );

    auto bodyForce = planeStressSource( E, nu );
    auto integrand = makeStaticDomainIntegrand<D>( kinematics, constitutive, bodyForce );

    // Prepare dirichlet boundary conditions
    auto zero = spatial::constantFunction<D>( 0.0 );

    auto dirichetFaces = std::vector
    {
        boundary::boundaryDofs( zero, basis, { boundary::left  }, 0 ), // u_x(0, y) = 0
        boundary::boundaryDofs( zero, basis, { boundary::left  }, 1 ), // u_y(0, y) = 0
        boundary::boundaryDofs( zero, basis, { boundary::front }, 0 ), // u_x(x, 0) = 0
        boundary::boundaryDofs( zero, basis, { boundary::front }, 1 )  // u_y(x, 0) = 0
    };
    
    auto dirichlet = boundary::combine( std::move( dirichetFaces ) );

    // Allocate matrix and assemble domain integral
    auto K = allocateMatrix<linalg::SymmetricSparseMatrix>( basis, dirichlet.first );
    auto F = std::vector<double>( K.size1( ), 0.0 );

    integrateOnDomain<D>( basis, integrand, { K, F }, dirichlet );
    
    // Neumann boundary conditions
    auto integrandRight = makeNeumannIntegrand<D>( planeStressRightTraction( E, nu ) );
    auto integrandBack = makeNeumannIntegrand<D>( planeStressBackTraction( E, nu ) );

    auto quadratureBack = boundary::QuadratureOnMeshFaces<D>( mesh, { boundary::back } );
    auto quadratureRight = boundary::QuadratureOnMeshFaces<D>( mesh, { boundary::right } );

    integrateOnSurface<D>( basis, integrandBack, quadratureBack, { F }, dirichlet );
    integrateOnSurface<D>( basis, integrandRight, quadratureRight, { F }, dirichlet );

    // Solve
    auto maxiter = std::max( size_t { 2000 }, static_cast<size_t>( K.size1( ) ) );

    auto reducedDofs = linalg::makeCGSolver( 1e-12, 0.0, maxiter )( K, F );
    auto dofs = boundary::inflate( reducedDofs, dirichlet );

    // Write .vtu file
    auto processors = std::tuple 
    {
        makeSolutionProcessor<D>( dofs, "Numerical" ),
        makeFunctionProcessor<D>( planeStressSolution( ), "Analytical" ),
        makeFunctionProcessor<D>( bodyForce, "Source" ),
        makeVonMisesProcessor<D>( dofs, kinematics, constitutive )
    };
    
    auto postmesh = cellmesh::grid( array::make<D>( degree ) );//, PostprocessTopologies::Faces );
    auto output = VtuOutput { "outputs/systemtests/plane_stress_" + name };

    writeOutput( basis, postmesh, std::move( processors ), output );

    // Integrate energy
    auto energyIntegrand = makeInternalEnergyIntegrand<D>( dofs, kinematics, constitutive );
    auto internalEnergy = double { 0.0 };

    integrateOnDomain<D>( basis, energyIntegrand, { internalEnergy }, dirichlet );
    
    return internalEnergy;
}

// To test unstructured mesh
UnstructuredMesh<2> meshUnitSquare( );

auto expectedEnergySquared( double E, double nu )
{
    return  ( ( 117403.0 * nu - 1378393.0 ) * E ) /
        ( 390.0 * ( 6930.0 * nu * nu - 6930.0 ) );
}

TEST_CASE( "plane_stress_pfem" )
{
    static constexpr size_t D = 2;
    
    auto E = 2.3;
    auto nu = 0.3;

    auto expectedEnergy = expectedEnergySquared( E, nu );
    
    SECTION( "multiple elements" )
    {
        auto mesh = makeRefinedGrid<D>( { 5, 5 }, { 1.0, 1.0 } );
        auto basis = makeHpBasis<TrunkSpace>( mesh, 7, D );
        
        auto energy = computePlaneStress( *basis, E, nu, "multiple" );

        CHECK( energy == Approx( expectedEnergy ).epsilon( 1e-12 ) );
    }
    
    SECTION( "single element" )
    {
        auto mesh = makeRefinedGrid<D>( { 1, 1 }, { 1.0, 1.0 } );
        auto basis = makeHpBasis<TensorSpace>( mesh, 7, D );
        
        auto energy = computePlaneStress( *basis, E, nu, "single" );

        CHECK( energy == Approx( expectedEnergy ).epsilon( 1e-12 ) );
    }
}

TEST_CASE( "plane_stress_unstructured" )
{
    static constexpr size_t D = 2;

    auto mesh = std::make_shared<UnstructuredMesh<D>>( meshUnitSquare( ) );
    auto basis = UnstructuredBasis<D>( mesh, D );

    auto energy = computePlaneStress( basis, 2.3, 0.3, "unstructured" );

    CHECK( energy == Approx( 1.2445388078 ).epsilon( 1e-8 ) );
}

TEST_CASE( "plane_stress_bsplines" )
{
    static constexpr size_t D = 2;

    auto mesh = makeCartesianGrid<D>( { 3, 4 }, { 1.0, 1.0 } );
    auto basis = makeBSplineBasis<D>( mesh, { 7, 6 }, { 3, 5 }, D );

    auto energy = computePlaneStress( *basis, 2.3, 0.3, "bsplines" );

    auto expectedEnergy = expectedEnergySquared( 2.3, 0.3 );

    CHECK( energy == Approx( expectedEnergy ).epsilon( 1e-8 ) );
}

// Manufactured solution
spatial::VectorFunction<2, 2> planeStressSolution( )
{
    return [=] ( std::array<double, 2> xy ) 
    {
        return std::array { std::pow( xy[0], 2 ) * std::pow( xy[1], 3 ),
                            std::pow( xy[0], 5 ) * std::pow( xy[1], 7 ) };
    };
}

// Corresponding right hand side
spatial::VectorFunction<2, 2> planeStressSource( double E, double nu )
{
    return [=]( std::array<double, 2> xy ) noexcept
    {
        double fx = - ( ( 1.0 - nu ) * ( 35.0 * std::pow( xy[0], 4 ) * std::pow( xy[1], 6 ) + 6.0 * 
            std::pow( xy[0], 2 ) * xy[1] ) * E ) / ( 2.0 * ( 1.0 - nu * nu ) ) - ( 35.0 * nu * 
            std::pow( xy[0], 4 ) * std::pow( xy[1], 6 ) * E ) / ( 1.0 - nu * nu ) - 
            ( 2.0 * std::pow( xy[1], 3 ) * E ) / ( 1.0 - nu * nu );

        double fy = - ( ( 1.0 - nu ) * ( 20.0 * std::pow( xy[0], 3 ) * std::pow( xy[1], 7 ) + 6.0 * 
            std::pow( xy[1], 2 ) * xy[0] ) * E ) / ( 2.0 * ( 1.0 - nu * nu ) ) - ( 42.0 * 
            std::pow( xy[0], 5 ) * std::pow( xy[1], 5 ) * E ) / ( 1.0 - nu * nu ) - 
            ( 6.0 * nu * xy[0] * std::pow( xy[1], 2 ) * E ) / ( 1.0 - nu * nu );

        return std::array { fx, fy };
    };
}

// Corresponding stress tensor
spatial::VectorFunction<2, 3> planeStressStress( double E, double nu  )
{
    return [=]( std::array<double, 2> xy ) noexcept
    {
        auto S = std::array<double, 3> { };
        auto c = E / ( 1.0 - nu * nu );
        
        auto xy3 = xy[0] * std::pow( xy[1], 3 );
        auto x4y3 = std::pow( xy[0], 4 ) * std::pow( xy[1], 3 );
        auto x2y2 = std::pow( xy[0], 2 ) * std::pow( xy[1], 2 );
        auto x2y5 = std::pow( xy[0], 2 ) * std::pow( xy[1], 5 );
        
        S[0] = c * xy3 * ( 2.0 + 7.0 * nu * x4y3 );
        S[1] = c * xy3 * ( 2.0 * nu + 7.0 * x4y3 );
        S[2] = 0.5 * c * ( 1.0 - nu ) * x2y2 * ( 3.0 + 5.0 * x2y5 );
        
        return S;
    };
}

// Extract [s_xy, s_yy] of stress tensor
spatial::VectorFunction<2, 2> planeStressBackTraction( double E, double nu  )
{
    auto stress = planeStressStress( E, nu );

    return [=]( std::array<double, 2> xy )
    { 
        return std::array { stress( xy )[2], stress( xy )[1] };
    };
}

// Extract [s_xx, s_xy] of stress tensor
spatial::VectorFunction<2, 2> planeStressRightTraction( double E, double nu  )
{
    auto stress = planeStressStress( E, nu );

    return [=]( std::array<double, 2> xy )
    { 
        return std::array { stress( xy )[0], stress( xy )[2] };
    };
}

UnstructuredMesh<2> meshUnitSquare( )
{
    static constexpr size_t D = 2;

    auto nelements = array::makeSizes<D>( 16 );
    auto nvertices = array::add<size_t>( nelements, 1 );

    auto vertices = CoordinateList<D> { };
    auto connectivity = std::vector<size_t> { };
    auto offsets = std::vector<size_t> { 0 };

    auto xyzGenerator = spatial::makeGridPointGenerator( nvertices );

    nd::execute( nvertices, [&]( auto ijk )
    {
        auto xy = xyzGenerator(ijk);

        auto d = 0.08 * std::sin( xy[0] * 2.0 * std::numbers::pi ) *
                        std::sin( xy[1] * 2.0 * std::numbers::pi );

        vertices.push_back( { xy[0] + d, xy[1] + d } );
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
    
    auto engine2 = std::mt19937 { 0 };
    auto random2 = std::uniform_int_distribution { 0, 2 }; 

    nd::execute( nelements, [&]( auto ijk )
    {
        auto indices = std::array 
        { 
            ijk[0] * nvertices[1] + ijk[1], 
            ijk[0] * nvertices[1] + ijk[1] + 1,
            ( ijk[0] + 1 ) * nvertices[1] + ijk[1], 
            ( ijk[0] + 1 ) * nvertices[1] + ijk[1] + 1  
        };
        
        if( auto r = random2( engine2 ); r != 0 )
        {
            auto indices0 = std::array { indices[0], indices[1], indices[3] };
            auto indices1 = std::array { indices[0], indices[2], indices[3] };

            if( r == 1 )
            {
                indices0 = { indices[0], indices[1], indices[2] };
                indices1 = { indices[1], indices[2], indices[3] };
            }

            for( auto index : indices0 )
            {
                connectivity.push_back( index );
            }

            shuffle( connectivity, 3 );

            offsets.push_back( connectivity.size( ) );

            for( auto index : indices1 )
            {
                connectivity.push_back( index );
            }

            shuffle( connectivity, 3 );

            offsets.push_back( connectivity.size( ) );

        }
        else
        {
            for( size_t i = 0; i < 4; ++i )
            {
                connectivity.push_back( indices[i] );
            }

            offsets.push_back( connectivity.size( ) );
        }
    } );

    return UnstructuredMesh<D> ( std::move( vertices ), 
        std::move( connectivity ), std::move( offsets ) );
}

} // namespace mlhp
