// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/integrands.hpp"
#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/dense.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/spatial.hpp"

#include <array>

namespace mlhp
{
namespace
{

template<bool computeLhs, bool computeRhs, size_t D>
void computeL2ElementSystem( double mass, double rhs,
                             const BasisFunctionEvaluation<D>& shapes,
                             AlignedDoubleVectors& targets,
                             double weightDetJ, size_t ifield )
{
    MLHP_CHECK( ifield < shapes.nfields( ), "Field index out of bounds." );

    auto NI = shapes.noalias( ifield, 0 );
    auto ndofI = shapes.ndof( ifield );
    auto offset = fieldOffset( shapes, ifield );

    if constexpr( computeLhs )
    {
        auto massValue = mass * weightDetJ;
        auto expr1 = [&]( size_t i, size_t j ) { return NI[i] * NI[j] * massValue; };

        linalg::elementLhs<linalg::SymmetricDenseMatrix>( targets[0].data( ), 
            shapes.ndof( ),offset, ndofI, offset, ndofI, expr1 );
    }
    
    if constexpr( computeRhs )
    {
        auto expr2 = [&]( size_t i ) { return NI[i] * rhs * weightDetJ; };

        linalg::elementRhs( targets[computeLhs].data( ) + offset, ndofI, 0, expr2 );
    }
}

auto symmetricTargets( bool computeTangent, bool computeRhs )
{
    auto types = AssemblyTypeVector { };

    if( computeTangent )
    {
        types.push_back( AssemblyType::SymmetricMatrix );
    }

    if( computeRhs )
    {
        types.push_back( AssemblyType::Vector );
    }

    return types;
}

using DoubleVectorCache = utilities::ThreadLocalContainer<std::vector<double>>;

template<size_t L, size_t G>
auto evaluateVectorFunction( const spatial::VectorFunction<L, G>& f,
                             const BasisFunctionEvaluation<L>& shapes,
                             auto& tmp, size_t offset )
{
    MLHP_CHECK( f.odim == shapes.nfields( ), "Inconsistent number of fields.");

    auto value = std::span( utilities::begin( tmp, offset ), f.odim );

    f( shapes.xyz( ), value );

    return value;
}

template<bool computeLhs, bool computeRhs, size_t D>
void computeL2ElementSystem( std::span<double> massValue,
                             std::span<double> rhsValue,
                             const BasisFunctionEvaluation<D>& shapes,
                             AlignedDoubleVectors& targets,
                             double weightDetJ )
{
    auto offset = size_t { 0 };
    auto ndofall = shapes.ndof( );
    auto nfields = shapes.nfields( );

    for( size_t ifield = 0; ifield < nfields; ++ifield )
    {
        auto NI = shapes.noalias( ifield, 0 );
        auto ndofI = shapes.ndof( ifield );

        if( computeLhs )
        {
            auto expr1 = [&]( size_t i, size_t j ) { return NI[i] * NI[j] * massValue[ifield] * weightDetJ; };

            linalg::elementLhs<linalg::SymmetricDenseMatrix>( targets[0].data( ), ndofall,
                offset, ndofI, offset, ndofI, expr1 );
        }

        if( computeRhs )
        {
            auto expr2 = [&]( size_t i ) { return NI[i] * rhsValue[ifield] * weightDetJ; };

            linalg::elementRhs( targets[computeLhs].data( ) + offset, ndofI, 0, expr2 );
        }

        offset += ndofI;
    }
}

} // namespace

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2DomainIntegrand( std::optional<spatial::ScalarFunction<D>> mass,
                                          std::optional<spatial::ScalarFunction<D>> rhs,
                                          memory::vptr<const std::vector<double>> dofs,
                                          size_t ifield )
{
    MLHP_CHECK( dofs.get( ) == nullptr || ( mass != std::nullopt && rhs != std::nullopt ),
        "L2 integrand needs mass and rhs when dofs are given." );

    auto create = [&]<bool M, bool R, bool N>( )
    {
        return std::function { [=]( const BasisFunctionEvaluation<D>& shapes,
                                    const LocationMap& locationMap, 
                                    AlignedDoubleVectors& targets, 
                                    AlignedDoubleVector&,
                                    double weightDetJ )
        {
            auto massValue = M || ( R && N ) ? ( *mass )( shapes.xyz( ) ) : 1.0;
            auto rhsValue = R ? ( *rhs )( shapes.xyz( ) ) : 0.0;

            if constexpr( R && N )
            {
                rhsValue -= massValue * evaluateSolution( shapes, locationMap, *dofs );
            }

            computeL2ElementSystem<M, R>( massValue, rhsValue, shapes, targets, weightDetJ, ifield );
        } };
    };

    auto evaluate = std::function<typename DomainIntegrand<D>::Evaluate2> { };

    if(  mass &&  rhs &&  dofs ) evaluate = create.template operator()<true, true, true>( );
    if(  mass &&  rhs && !dofs ) evaluate = create.template operator()<true, true, false>( );
    if(  mass && !rhs &&  dofs ) evaluate = create.template operator()<true, false, true>( );
    if(  mass && !rhs && !dofs ) evaluate = create.template operator()<true, false, false>( );
    if( !mass &&  rhs &&  dofs ) evaluate = create.template operator()<false, true, true>( );
    if( !mass &&  rhs && !dofs ) evaluate = create.template operator()<false, true, false>( );
    if( !mass && !rhs &&  dofs ) evaluate = create.template operator()<false, false, true>( );
    if( !mass && !rhs && !dofs ) evaluate = create.template operator()<false, false, false>( );

    return DomainIntegrand<D>( symmetricTargets( mass != std::nullopt, 
        rhs != std::nullopt ), DiffOrders::Shapes, evaluate );
}

template<size_t D>
DomainIntegrand<D> makeL2DomainIntegrand( const spatial::ScalarFunction<D>& mass,
                                          const spatial::ScalarFunction<D>& rhs,
                                          size_t ifield )
{
    return makeL2DomainIntegrand<D>( mass, rhs, nullptr, ifield );
}

template<size_t D>
DomainIntegrand<D> makeL2DomainIntegrand( const spatial::ScalarFunction<D>& rhs,
                                          size_t ifield )
{
    return makeL2DomainIntegrand<D>( spatial::constantFunction<D>( 1.0 ), std::optional { rhs }, nullptr, ifield );
}

template<size_t D>
DomainIntegrand<D> makeL2DomainIntegrand( std::optional<spatial::VectorFunction<D>> mass,
                                          std::optional<spatial::VectorFunction<D>> rhs,
                                          memory::vptr<const std::vector<double>> dofs )
{
    if( !mass && !rhs )
    {
        return DomainIntegrand<D>( AssemblyTypeVector { }, DiffOrders::NoShapes, 
            std::function<typename DomainIntegrand<D>::Evaluate1> { utilities::doNothing( ) } );
    }

    MLHP_CHECK( !mass || !rhs || mass->odim == rhs->odim, "Inconsistent vector function dimensions." );

    auto nfields = mass ? mass->odim : rhs->odim;

    auto create = [&]<bool M, bool R, bool N>( )
    {
        return std::function { [=]( const BasisFunctionEvaluation<D>& shapes,
                                    const LocationMap& locationMap, 
                                    AlignedDoubleVectors& targets, 
                                    AlignedDoubleVector& tmp,
                                    double weightDetJ )
        {
            MLHP_CHECK( shapes.nfields( ) == nfields, "Inconsistent number of fields." );

            tmp.resize( 3 * nfields );

            auto massValue = std::span( tmp.data( ), nfields );
            auto rhsValue = std::span( tmp.data( ) + nfields, nfields );
                       
            if constexpr ( M || ( R && N ) )
            {
                ( *mass )( shapes.xyz( ), massValue );
            }

            if constexpr ( R )
            {
                ( *rhs )( shapes.xyz( ), rhsValue );
            }

            if constexpr ( R && N )
            {
                auto solution = std::span( tmp.data( ) + 2 * nfields, nfields );

                evaluateSolutions<D>( shapes, locationMap, *dofs, solution );

                for( size_t axis = 0; axis < nfields; ++axis )
                {
                    rhsValue[axis] -= massValue[axis] * solution[axis];
                }
            }

            computeL2ElementSystem<M, R>( massValue, rhsValue, shapes, targets, weightDetJ );
        } };
    };

    auto evaluate = std::function<typename DomainIntegrand<D>::Evaluate2> { };

    if(  mass &&  rhs &&  dofs ) evaluate = create.template operator()<true, true, true>( );
    if(  mass &&  rhs && !dofs ) evaluate = create.template operator()<true, true, false>( );
    if(  mass && !rhs &&  dofs ) evaluate = create.template operator()<true, false, true>( );
    if(  mass && !rhs && !dofs ) evaluate = create.template operator()<true, false, false>( );
    if( !mass &&  rhs &&  dofs ) evaluate = create.template operator()<false, true, true>( );
    if( !mass &&  rhs && !dofs ) evaluate = create.template operator()<false, true, false>( );
    if( !mass && !rhs &&  dofs ) evaluate = create.template operator()<false, false, true>( );
    if( !mass && !rhs && !dofs ) evaluate = create.template operator()<false, false, false>( );

    return DomainIntegrand<D>( symmetricTargets( mass != std::nullopt, 
        rhs != std::nullopt ), DiffOrders::Shapes, evaluate );
}

template<size_t D>
DomainIntegrand<D> makeL2DomainIntegrand( const spatial::VectorFunction<D>& rhs )
{
    auto mass = spatial::constantFunction<D>( std::vector<double>( rhs.odim, 1.0 ) );

    return makeL2DomainIntegrand<D>( mass, rhs );
}

template<size_t D>
DomainIntegrand<D> makePoissonIntegrand( const spatial::ScalarFunction<D>& conductivity,
                                         const spatial::ScalarFunction<D>& source )
{
    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes,
                         AlignedDoubleVectors& targets,
                         double weightDetJ )
    {
        double factor1 = conductivity( shapes.xyz( ) ) * weightDetJ;
        double factor2 = source( shapes.xyz( ) ) * weightDetJ;

        auto tmp = shapes.sizes( );
        auto ndof = std::get<0>( tmp );
        auto nblocks = std::get<1>( tmp );
        auto ndofpadded = std::get<2>( tmp );

        auto N = shapes.noalias( 0, 0 );
        auto dN = shapes.noalias( 0, 1 );

        linalg::symmetricElementLhs( targets[0].data( ), ndof, nblocks, [=]( size_t i, size_t j )
        { 
            double value = 0.0;

            for( size_t axis = 0; axis < D; ++axis )
            {
                value += dN[axis * ndofpadded + i] * dN[axis * ndofpadded + j] * factor1;
            }

            return value;
        } );

        linalg::elementRhs( targets[1].data( ), ndof, nblocks, [&]( size_t i )
        { 
            return N[i] * factor2;
        } );
    };

    return DomainIntegrand<D>( symmetricTargets( true, true ), DiffOrders::FirstDerivatives, evaluate);
}

template<size_t D>
DomainIntegrand<D> makeAdvectionDiffusionIntegrand( const spatial::VectorFunction<D, D>& velocity,
                                                    const spatial::ScalarFunction<D>& diffusivity,
                                                    const spatial::ScalarFunction<D>& source )
{
    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes,
                         AlignedDoubleVectors& targets, double weight )
    {
        auto ndof = shapes.ndof( );
        auto nblocks = shapes.nblocks( );
        auto ndofpadded = shapes.ndofpadded( );
        
        auto N = shapes.noalias( 0, 0 );
        auto dN = shapes.noalias( 0, 1 );

        auto a = velocity( shapes.xyz( ) );
        auto k = diffusivity( shapes.xyz( ) );
        auto f = source( shapes.xyz( ) );
        
        linalg::unsymmetricElementLhs( targets[0].data( ), ndof, nblocks, 
                                       [&]( size_t i, size_t j )
        {
            double value = 0.0;
            
            for( size_t axis = 0; axis < D; ++axis )
            {
                value += N[i] * a[axis] * dN[axis * ndofpadded + j];

            } // axis
                    
            for( size_t axis = 0; axis < D; ++axis )
            {
                value += dN[axis * ndofpadded + i] * k * dN[axis * ndofpadded + j];
        
            } // component
        
            return value * weight;
        } );
        
        linalg::elementRhs( targets[1].data( ), ndof, nblocks, [&]( size_t i )
        {
            return N[i] * f * weight;
        } );
    };

    auto types = std::vector { AssemblyType::UnsymmetricMatrix, AssemblyType::Vector };

    return DomainIntegrand<D>( types, DiffOrders::FirstDerivatives, evaluate );
}

template<size_t D>
DomainIntegrand<D> makeFunctionIntegrand( const spatial::ScalarFunction<D>& function )
{
    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes, const LocationMap&,
                         AlignedDoubleVectors& targets, AlignedDoubleVector&, double weightDetJ )
    {
        targets[0][0] += function( shapes.xyz( ) ) * weightDetJ;
    };

    return DomainIntegrand<D>( std::vector( 1, AssemblyType::Scalar ), DiffOrders::NoShapes, evaluate );
}

template<size_t D>
DomainIntegrand<D> makeFunctionIntegrand( const spatial::VectorFunction<D>& function )
{
    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes, const LocationMap&,
                         AlignedDoubleVectors& targets, AlignedDoubleVector& tmp, double weightDetJ )
    {
        tmp.resize( function.odim );
        
        auto result = std::span( tmp.data( ), function.odim );

        function( shapes.xyz( ), result );

        for( size_t i = 0; i < function.odim; ++i )
        {
            targets[i][0] += result[i] * weightDetJ;
        }
    };

    return DomainIntegrand<D>( std::vector( function.odim, AssemblyType::Scalar ), DiffOrders::NoShapes, evaluate );
}

template<size_t D>
DomainIntegrand<D> makeL2ErrorIntegrand( memory::vptr<const std::vector<double>> solutionDofs,
                                         const spatial::ScalarFunction<D>& solutionFunction )
{
    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& locationMap,
                         AlignedDoubleVectors& targets,
                         AlignedDoubleVector&,
                         double weightDetJ )
    {
        double analytical = solutionFunction( shapes.xyz( ) );
        double numerical = evaluateSolution( shapes, locationMap, *solutionDofs );

        targets[0][0] += numerical * numerical * weightDetJ;
        targets[1][0] += analytical * analytical * weightDetJ;
        targets[2][0] += utilities::integerPow( numerical - analytical, 2 ) * weightDetJ;
    };

    return DomainIntegrand<D>( std::vector( 3, AssemblyType::Scalar ), DiffOrders::Shapes, evaluate );
}

template<size_t D>
DomainIntegrand<D> makeEnergyErrorIntegrand( memory::vptr<const std::vector<double>> solutionDofs,
                                             const spatial::VectorFunction<D, D>& analyticalDerivatives )
{
    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& locationMap,
                         AlignedDoubleVectors& targets,
                         AlignedDoubleVector&, 
                         double weightDetJ )
    {
        auto du = evaluateGradient( shapes, locationMap, *solutionDofs );
        auto analytical = analyticalDerivatives( shapes.xyz( ) );

        for( size_t axis = 0; axis < D; ++axis )
        {
            targets[0][0] += 0.5 * weightDetJ * utilities::integerPow( du[axis], 2 );
            targets[1][0] += 0.5 * weightDetJ * utilities::integerPow( analytical[axis], 2 );
            targets[2][0] += 0.5 * weightDetJ * utilities::integerPow( du[axis] - analytical[axis], 2 );
        }
    };

    auto types = std::vector( 3, AssemblyType::Scalar );

    return DomainIntegrand<D>( types, DiffOrders::FirstDerivatives, evaluate );
}

namespace
{
    
template<size_t D>
auto isvoigt( size_t ncomponents )
{
    return ncomponents == VoigtIndices<D>::size;
}

}

template<size_t D>
void checkConsistency( const memory::vptr<const KinematicEquation<D>>& kinematics,
                       const memory::vptr<const ConstitutiveEquation<D>>& constitutive )
{
    MLHP_CHECK( kinematics.get( ) != nullptr, "Kinematic equation is a null pointer." );
    MLHP_CHECK( constitutive.get( ) != nullptr, "Constitutive equation is a null pointer." );
    MLHP_CHECK( kinematics->ncomponents != 0, "Kinematics has zero components." );
    MLHP_CHECK( constitutive->ncomponents != 0, "Material has zero components." );

    if( kinematics->ncomponents != constitutive->ncomponents )
    {
        MLHP_THROW( "The number of components differs between KinematicEquation (n = " + 
            std::to_string( kinematics->ncomponents ) + ") and ConstitutiveEquation (n = " + 
            std::to_string( constitutive->ncomponents ) + ")." );
    }

    if( kinematics->largestrain && kinematics->ncomponents != D * D && !isvoigt<D>( kinematics->ncomponents ) )
    {
        MLHP_THROW( "Large strain kinematic requires " + std::to_string( D * D ) + " components or " +
            std::to_string( ( D * ( D + 1 ) ) / 2 ) + " components in Voigt notation." );
    }
}

template<size_t D>
void checkConsistency( const AbsBasis<D>& basis, const memory::vptr<const KinematicEquation<D>>& kinematics )
{
    MLHP_CHECK( kinematics->nfields == basis.nfields( ), "Number of solution field "
        "components inconsistent between kinematics (n = " + std::to_string( kinematics->nfields ) + 
        ") and basis (n = " + std::to_string( basis.nfields( ) ) + ")." );
}

namespace
{

template<size_t D>
DomainIntegrand<D> internalElasticDomainIntegrand( AssemblyTypeVector types, 
                                                   DiffOrders maxdiff, 
                                                   memory::vptr<const KinematicEquation<D>> kinematics,
                                                   memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                                   auto&& evaluateGaussPoint )
{
    using AnyCache = typename DomainIntegrand<D>::Cache;

    checkConsistency( kinematics, constitutive );

    struct ThisCache
    {
        const LocationMap* locationMap;

        memory::AlignedVector<double> tmp;

        typename KinematicEquation<D>::AnyCache kinematicsCache;
        typename ConstitutiveEquation<D>::AnyCache constitutiveCache;
    };

    // Create cache at beginning of omp parallel
    auto create = [=]( const AbsBasis<D>& basis ) -> AnyCache
    {
        checkConsistency( basis, kinematics );

        auto cache = ThisCache { };

        cache.kinematicsCache = kinematics->create( basis );
        cache.constitutiveCache = constitutive->create( basis, *kinematics );

        return AnyCache { std::move( cache ) };
    };

    // Prepare cache for the given element
    auto prepare = [=]( AnyCache& anyCache, 
                        const MeshMapping<D>& mapping, 
                        const LocationMap& locationMap )
    {
        auto& cache = utilities::cast<ThisCache>( anyCache );

        cache.locationMap = &locationMap;

        kinematics->prepare( cache.kinematicsCache, mapping, locationMap );
        constitutive->prepare( cache.constitutiveCache, mapping, locationMap );
    };

    // Evaluate at Gauss point
    auto evaluate = [evaluateGaussPoint = std::move( evaluateGaussPoint )] ( 
        AnyCache& anyCache,
        const BasisFunctionEvaluation<D>& shapes,
        AlignedDoubleVectors& targets, 
        double weightDetJ )
    {
        MLHP_CHECK( shapes.nfields( ) == D, "Invalid number of fields in elasticity integrand." );

        auto& cache = utilities::cast<ThisCache>( anyCache );

        evaluateGaussPoint( shapes, *cache.locationMap, targets, cache.tmp,
            cache.kinematicsCache, cache.constitutiveCache, weightDetJ );
    };

    return DomainIntegrand<D>( types, maxdiff, std::move( create ), 
        std::move( prepare ), std::move( evaluate ) );
}

template<size_t D>
SurfaceIntegrand<D> internalElasticSurfaceIntegrand( AssemblyTypeVector types, 
                                                     DiffOrders maxdiff, 
                                                     memory::vptr<const KinematicEquation<D>> kinematics,
                                                     memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                                     auto&& evaluateGaussPoint )
{
    using AnyCache = typename SurfaceIntegrand<D>::Cache;

    checkConsistency( kinematics, constitutive );

    struct ThisCache
    {
        memory::AlignedVector<double> tmp;

        typename KinematicEquation<D>::AnyCache kinematicsCache;
        typename ConstitutiveEquation<D>::AnyCache constitutiveCache;
    };
    
    // Create cache at beginning of omp parallel
    auto create = [=]( const AbsBasis<D>& basis ) -> AnyCache
    {
        checkConsistency( basis, kinematics );

        auto cache = ThisCache { };

        cache.kinematicsCache = kinematics->create( basis );
        cache.constitutiveCache = constitutive->create( basis, *kinematics );

        return AnyCache { std::move( cache ) };
    };

    // Prepare cache for the given element
    auto prepare = [=]( AnyCache& anyCache, 
                        const MeshMapping<D>& mapping, 
                        const LocationMap& locationMap )
    {
        auto& cache = utilities::cast<ThisCache>( anyCache );

        kinematics->prepare( cache.kinematicsCache, mapping, locationMap );
        constitutive->prepare( cache.constitutiveCache, mapping, locationMap );
    };

    auto evaluate = [=]( AnyCache& anyCache,
                         const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& locationMap,
                         std::array<double, D> normal,
                         AlignedDoubleVectors& targets,
                         double weightDetJ )
    {
        MLHP_CHECK( shapes.nfields( ) == D, "Invalid number of fields in elasticity integrand." );

        auto& cache = utilities::cast<ThisCache>( anyCache );

        evaluateGaussPoint( shapes, locationMap, normal, targets, cache.tmp,
            cache.kinematicsCache, cache.constitutiveCache, weightDetJ );
    };
    
    return SurfaceIntegrand<D> { create, prepare, evaluate, types, maxdiff };
}

} // namespace

template<size_t D>
DomainIntegrand<D> makeInternalEnergyIntegrand( memory::vptr<const std::vector<double>> solutionDofs,
                                                memory::vptr<const KinematicEquation<D>> kinematics,
                                                memory::vptr<const ConstitutiveEquation<D>> constitutive )
{
    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& locationMap,
                         AlignedDoubleVectors& targets,
                         AlignedDoubleVector& tmp,
                         auto& kinematicsCache,
                         auto& constitutiveCache,
                         double weightDetJ )
    { 
        tmp.resize( D * D + 2 * constitutive->ncomponents );

        std::fill( tmp.begin( ), tmp.end( ), 0.0 );

        auto gradient = std::span( tmp.data( ), D * D );
        auto strain = std::span( gradient.data( ) + gradient.size( ), constitutive->ncomponents );
        auto stress = std::span( strain.data( ) + strain.size( ), constitutive->ncomponents );

        evaluateSolutions( shapes, locationMap, *solutionDofs, gradient, 1 );

        kinematics->evaluate( kinematicsCache, shapes, gradient, strain, std::span<double> { } );
        constitutive->evaluate( constitutiveCache, shapes, strain, stress, std::span<double> { } );
        
        targets[0][0] += 0.5 * spatial::dot( strain, stress ) * weightDetJ;
    };

    return internalElasticDomainIntegrand<D>( { AssemblyType::Scalar }, 
        DiffOrders::FirstDerivatives, kinematics, constitutive, std::move( evaluate ) );
}

template<size_t D>
KinematicEquation<D> makeSmallStrainKinematics( )
{
    auto evaluate = []( typename KinematicEquation<D>::AnyCache&,
                        const BasisFunctionEvaluation<D>& shapes, 
                        std::span<const double> du,
                        std::span<double> strainEvaluation,
                        std::span<double> strainOperator )
    { 
        static constexpr size_t ncomponents = ( D * ( D + 1 ) ) / 2;

        // Prepare 
        auto B = memory::assumeAlignedNoalias( strainOperator.data( ) );
        auto offsets = fieldOffsets<D, D>( shapes );
        auto ndofpadded = shapes.ndofpadded( );

        MLHP_CHECK( strainOperator.empty( ) || strainOperator.size( ) == ncomponents * ndofpadded,
                    "Invalid strain operator size in small strain kinematrics" );
        
        MLHP_CHECK( strainEvaluation.empty( ) || strainEvaluation.size( ) == ncomponents,
                    "Invalid strain evaluation size in infinitesimal strain kinematrics" );
        
        // Now copy derivative components into the right spot
        auto evaluateComponent = [&]( size_t index, size_t iN, size_t iD )
        {
            if( !strainOperator.empty( ) )
            {
                auto dN = shapes.get( iN, 1 ) + iD * shapes.ndofpadded( iN );
                auto offset = index * ndofpadded + offsets[iN];

                std::copy_n( dN, shapes.ndof( iN ), B + offset );
            }

            if( !strainEvaluation.empty( ) )
            {
                strainEvaluation[index] += du[iN * D + iD];
            }
        };

        // Normal strain
        for( size_t index = 0; index < D; ++index )
        {
            // e_ii
            evaluateComponent( index, index, index ); // N_i,dxi
        }

        // Engineering shear strain
        for( auto index = D; index < VoigtIndices<D>::size; ++index )
        {
            auto [i, j] = VoigtIndices<D>::matrix[index];

            evaluateComponent( index, i, j ); // N_i,y +       
            evaluateComponent( index, j, i ); //       + N_j,x 
        }
    };

    return
    {
        .create = utilities::returnEmpty<typename KinematicEquation<D>::AnyCache>( ),
        .evaluate = evaluate,
        .nfields = D,
        .ncomponents = VoigtIndices<D>::size,
        .largestrain = false,
        .name = "SmallStrainKinematics"
    };
}

namespace
{

template<size_t D, size_t N>
auto makeLinearConstitutive( auto&& material, bool symmetric, std::string name )
{
    auto constitutive = ConstitutiveEquation<D> { };
    
    constitutive.evaluate = [=]( typename ConstitutiveEquation<D>::AnyCache&,
                                 const BasisFunctionEvaluation<D>& shapes,
                                 std::span<const double> strain,
                                 std::span<double> stress,
                                 std::span<double> tangent )
    { 
        auto C = std::array<double, N * N> { };

        material( shapes.xyz( ), C );

        if( !stress.empty( ) )
        {
            linalg::mmproduct( C.data( ), strain.data( ), stress.data( ), N, N, 1 );
        }

        if( !tangent.empty( ) )
        {
            std::copy( C.begin( ), C.end( ), tangent.begin( ) );
        }
    };

    constitutive.symmetric = symmetric;
    constitutive.ncomponents = N;
    constitutive.incremental = false;
    constitutive.name = name;

    return constitutive;
}

} // namespace

ConstitutiveEquation<3> makeIsotropicElasticMaterial( const spatial::ScalarFunction<3>& youngsModulus,
                                                      const spatial::ScalarFunction<3>& poissonRatio )
{
    auto material = [=]( std::array<double, 3> xyz, std::span<double> target )
    {
        MLHP_CHECK( target.size( ) == 6 * 6, "Invalid matrix size in isotropic elastic material." );

        // Compute Lame parameters
        auto [lambda, mu] = ElasticConverter( youngsModulus( xyz ), poissonRatio( xyz ) ).lameParameters( );

        auto diagonal = lambda + 2.0 * mu;
        auto C = linalg::adapter( target, 6 );

        // Upper left block
        C( 0, 0 ) = diagonal; C( 0, 1 ) = lambda;   C( 0, 2 ) = lambda;
        C( 1, 0 ) = lambda;   C( 1, 1 ) = diagonal; C( 1, 2 ) = lambda;
        C( 2, 0 ) = lambda;   C( 2, 1 ) = lambda;   C( 2, 2 ) = diagonal;
        
        // Lower right diagonal: engineering strain -> mu instead of 2 * mu
        C( 3, 3 ) = mu; C( 4, 4 ) = mu; C( 5, 5 ) = mu;
    };
    
    return makeLinearConstitutive<3, 6>( std::move( material ), true, "IsotropicElasticMaterial" );
}

ConstitutiveEquation<2> makePlaneStressMaterial( const spatial::ScalarFunction<2>& youngsModulus,
                                                 const spatial::ScalarFunction<2>& poissonRatio )
{
    auto material = [=]( std::array<double, 2> xyz, std::span<double> target )
    {
        auto nu = poissonRatio( xyz );
        auto E = youngsModulus( xyz );
        auto tmp = E / ( 1.0 - nu * nu );
        auto C = linalg::adapter( target, 3 );

        C( 0, 0 ) = tmp;
        C( 1, 1 ) = tmp;
        C( 2, 2 ) = 0.5 * tmp * ( 1.0 - nu );
        C( 0, 1 ) = tmp * nu;
        C( 1, 0 ) = tmp * nu;
    };

    return makeLinearConstitutive<2, 3>( std::move( material ), true, "PlanStressMaterial" );
}

ConstitutiveEquation<2> makePlaneStrainMaterial( const spatial::ScalarFunction<2>& youngsModulus,
                                                 const spatial::ScalarFunction<2>& poissonRatio )
{
    auto material = [=]( std::array<double, 2> xyz, std::span<double> target )
    {
        auto nu = poissonRatio( xyz );
        auto E = youngsModulus( xyz );
        auto tmp = E / ( ( 1.0 + nu ) * ( 1.0 - 2.0 * nu ) );
        auto C = linalg::adapter( target, 3 );

        C( 0, 0 ) = tmp * ( 1.0 - nu );
        C( 1, 1 ) = tmp * ( 1.0 - nu );
        C( 2, 2 ) = 0.5 * tmp * ( 1.0 - 2.0 * nu );
        C( 0, 1 ) = tmp * nu;
        C( 1, 0 ) = tmp * nu;
    };

    return makeLinearConstitutive<2, 3>( std::move( material ), true, "PlaneStrainMaterial" );
}

namespace
{

//! Multiply B * CB with dynamic size passed as function argument 
//! if N == 0, or with static dimension if N > 0.
template<size_t N, typename MatrixTag>
void matrixMatrixProduct( const double* BPtr, const double* CBPtr, double* target,
                          size_t size, size_t ndof, size_t nblocks, size_t ndofpadded )
{
    auto B = memory::assumeAlignedNoalias( BPtr );
    auto CB = memory::assumeAlignedNoalias( CBPtr );

    linalg::elementLhs<MatrixTag>( target, ndof, nblocks, [&]( size_t i, size_t j )
    { 
        auto value = 0.0;

        if constexpr( N != 0 )
        {
            // Size known at compile time
            for( size_t axis = 0; axis < N; ++axis )
            {
                value += B[axis * ndofpadded + i] * CB[axis * ndofpadded + j];
            }
        }
        else
        {
            // Size only known at runtime
            for( size_t axis = 0; axis < size; ++axis )
            {
                value += B[axis * ndofpadded + i] * CB[axis * ndofpadded + j];
            }
        }

        return value;
    } );
}

// Call matrixMatrixProduct using function pointer table (static dimension if size is small)
template<typename MatrixTag>
auto dispatchedProduct( const double* B, const double* CB, double* target, 
                        size_t size, size_t ndof, size_t nblocks, size_t ndofpadded )
{
    // Instantiate matrixMatrixProduct for N = 0 .. 10 and store return function pointers in an array
    auto makeLookupTable = [=]<size_t... I>( std::index_sequence<I...> ) constexpr 
    {       
        return std::array { &matrixMatrixProduct<I, MatrixTag>... };
    };
    
    // Create function pointer table and index based on input size (dynamic size goes into index 0)
    static constexpr auto tableSize = size_t { 10 };
    static constexpr auto lookup = makeLookupTable( std::make_index_sequence<tableSize>( ) );
    
    lookup[size < tableSize ? size : size_t { 0 }]( B, CB, target, size, ndof, nblocks, ndofpadded );
}

auto dispatchedProduct( const double* B, const double* CB, double* target,
                        size_t size, size_t ndof, size_t nblocks, size_t ndofpadded,
                        bool symmetric )
{
    if( symmetric )
    {
        dispatchedProduct<linalg::SymmetricDenseMatrix>( B, CB, target, size, ndof, nblocks, ndofpadded );
    }
    else
    {
        dispatchedProduct<linalg::UnsymmetricDenseMatrix>( B, CB, target, size, ndof, nblocks, ndofpadded );
    }
}

} // namespace

template<size_t D>
DomainIntegrand<D> makeStaticDomainIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,
                                              memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                              const spatial::VectorFunction<D, D>& force )
{
    MLHP_CHECK( !kinematics->largestrain, "Linear version of domain integrand used with nonlinear kinematics." );

    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& /* locationMap */,
                         AlignedDoubleVectors& targets,
                         AlignedDoubleVector& tmp,
                         auto& kinematicsCache,
                         auto& constitutiveCache,
                         double weightDetJ )
    { 
        auto ndofpadded = shapes.ndofpadded( );
        auto ncomponents = constitutive->ncomponents;

        // Two matrices with (6, padded(N)) for stresses and strains
        tmp.resize( 2 * ncomponents * ndofpadded + ncomponents * ncomponents );        

        std::fill( tmp.begin( ), tmp.end( ), 0.0 );

        auto B = memory::assumeAlignedNoalias( tmp.data( ) );
        auto S = memory::assumeAlignedNoalias( B + ncomponents * ndofpadded );
        auto C = std::span( S + ncomponents * ndofpadded, ncomponents * ncomponents );

        auto strainOperator = std::span( B, ncomponents * ndofpadded );
        auto deformationGradient = std::span( S + ncomponents * ndofpadded, D * D );

        // Compute B matrix from shape function evaluation
        kinematics->evaluate( kinematicsCache, shapes, deformationGradient, std::span<double> { }, strainOperator );

        // Compute tangent stiffness
        constitutive->evaluate( constitutiveCache, shapes, std::span<double> { }, std::span<double> { }, C );

        std::transform( C.begin( ), C.end( ), C.begin( ), [=]( auto c ) { return c * weightDetJ; } );

        // Compute S = C * B
        linalg::mmproduct( C.data( ), B, S, ncomponents, ncomponents, ndofpadded );

        // Compute B^T * S
        dispatchedProduct( B, S, targets[0].data( ), ncomponents, shapes.ndof( ), 
            shapes.nblocks( ), ndofpadded, constitutive->symmetric );

        auto rhs = targets[1].data( );
        auto forceValues = force( shapes.xyz( ) ) * weightDetJ;

        // Compute right hand side for each field
        for( size_t ifield = 0; ifield < D; ++ifield )
        {
            auto N = shapes.noalias( ifield, 0 );
            auto size = shapes.ndof( ifield );

            linalg::elementRhs( rhs, size, shapes.nblocks( ifield ), [=]( size_t i )
            { 
                return N[i] * forceValues[ifield];
            } );

            rhs += size;
        }
    };

    auto types = std::vector { constitutive->symmetric ? AssemblyType::SymmetricMatrix :
        AssemblyType::UnsymmetricMatrix, AssemblyType::Vector };

    return internalElasticDomainIntegrand<D>( types, DiffOrders::FirstDerivatives,
        kinematics, constitutive, std::move( evaluate ) );
}

template<size_t D> 
DomainIntegrand<D> makeStaticDomainIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,
                                              memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                              memory::vptr<const std::vector<double>> dofs,
                                              const spatial::VectorFunction<D, D>& force,
                                              bool integrateTangent )
{
    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& locationMap,
                         AlignedDoubleVectors& targets,
                         AlignedDoubleVector& tmp,
                         auto& kinematicsCache,
                         auto& constitutiveCache,
                         double weightDetJ )
    { 
        auto N = constitutive->ncomponents;
        auto sizes = shapes.sizes( );
        auto ndof = std::get<0>( sizes );
        auto nblocks = std::get<1>( sizes );
        auto ndofpadded = std::get<2>( sizes );
        
        tmp.resize( 2 * N * ndofpadded + D * D + 2 * N + N * N );       

        std::fill( tmp.begin( ), tmp.end( ), 0.0 );

        auto B = memory::assumeAlignedNoalias( tmp.data( ) );
        auto S = memory::assumeAlignedNoalias( B + N * ndofpadded );
        auto C = std::span<double> { S + N * ndofpadded, integrateTangent ? N * N : 0 };

        auto strainOperator = std::span( B, N * ndofpadded );
        auto gradient = std::span<double, D * D> { C.data( ) + C.size( ), D * D };
        auto strain = std::span<double> { gradient.data( ) + gradient.size( ), N };
        auto stress = std::span<double> { strain.data( ) + strain.size( ), N };

        evaluateSolutions( shapes, locationMap, *dofs, gradient, 1 );

        // Compute B matrix from shape function evaluation
        kinematics->evaluate( kinematicsCache, shapes, gradient, strain, strainOperator );
                    
        // Compute stress and tangent stiffness
        constitutive->evaluate( constitutiveCache, shapes, strain, stress, C );
        
        if( integrateTangent )
        {
            std::transform( C.begin( ), C.end( ), C.begin( ), [=]( auto c ) { return c * weightDetJ; } );

            // Compute S = C * B
            linalg::mmproduct( C.data( ), B, S, N, N, ndofpadded );

            // Compute B^T * S
            dispatchedProduct( B, S, targets[0].data( ), N, shapes.ndof( ),
                shapes.nblocks( ), ndofpadded, constitutive->symmetric );
        }

        auto rhs = targets[integrateTangent].data( );
        
        // Internal forces
        linalg::elementRhs( rhs, ndof, nblocks, [&]( size_t idof )
        { 
            double value = 0.0;
        
            for( size_t icomponent = 0; icomponent < N; ++icomponent)
            {
                value += B[icomponent * ndofpadded + idof] * stress[icomponent];
            }
            
            return -value * weightDetJ;
        } );
        
        auto forceValues = force( shapes.xyz( ) );

        // External forces
        for( size_t ifield = 0; ifield < D; ++ifield )
        {
            auto Ni = shapes.noalias( ifield, 0 );
            auto size = shapes.ndof( ifield );

            linalg::elementRhs( rhs, size, shapes.nblocks( ifield ), [=]( size_t j )
            { 
                return Ni[j] * forceValues[ifield] * weightDetJ;
            } );

            rhs += size;
        }
    };

    auto types = std::vector { AssemblyType::Vector };

    if( integrateTangent )
    {
        types.insert( types.begin( ), constitutive->symmetric ? 
            AssemblyType::SymmetricMatrix : AssemblyType::UnsymmetricMatrix );
    }

    return internalElasticDomainIntegrand<D>( types, DiffOrders::FirstDerivatives,
        kinematics, constitutive, std::move( evaluate ) );
}

template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNeumannIntegrand( const spatial::ScalarFunction<D>& rhs,
                                          size_t ifield )
{
    auto evaluate = [=]( typename SurfaceIntegrand<D>::Cache&,
                         const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap&, std::array<double, D>,
                         AlignedDoubleVectors& targets, double weightDetJ )
    { 
        MLHP_CHECK( ifield < shapes.nfields( ), "Invalid field component index." );
        MLHP_CHECK_DBG( shapes.ndofpadded( ) == targets[0].size( ), "Invalid target size." );

        auto value = rhs( shapes.xyz( ) ) * weightDetJ;
        auto target = memory::assumeAlignedNoalias( targets[0].data( ) ) + fieldOffset( shapes, ifield );
        auto N = shapes.noalias( ifield, 0 );
        auto ndof = shapes.ndof( ifield );
        auto nblocks = shapes.nblocks( ifield );

        linalg::elementRhs( target, ndof, nblocks, [&]( size_t idof )
        { 
            return N[idof] * value;
        } );
    };

    return makeSurfaceIntegrand<D>( { AssemblyType::Vector }, DiffOrders::Shapes, evaluate );
}

namespace
{

template<size_t D>
auto vectorNeumanIntegrand( auto&& vectorFunction )
{
    auto evaluate = [=] ( typename SurfaceIntegrand<D>::Cache& anyCache,
                          const BasisFunctionEvaluation<D>& shapes,
                          const LocationMap&, std::array<double, D> normal,
                          AlignedDoubleVectors& targets, double weightDetJ )
    { 
        MLHP_CHECK_DBG( shapes.ndofpadded( ) == targets[0].size( ), "Invalid target size." );

        auto& data = utilities::cast<typename SurfaceIntegrand<D>::DefaultCache>( anyCache ).doubleVector;
        auto value = vectorFunction( shapes.xyz( ), normal, data );
        auto target = memory::assumeAlignedNoalias( targets[0].data( ) );
        auto nfields = shapes.nfields( );

        for( size_t ifield = 0; ifield < nfields; ++ifield )
        {
            auto N = shapes.noalias( ifield, 0 );
            auto ndof = shapes.ndof( ifield );
            auto nblocks = shapes.nblocks( ifield );

            linalg::elementRhs( target, ndof, nblocks, [&]( size_t iDof )
            { 
                return N[iDof] * value[ifield] * weightDetJ;
            } );

            target += ndof;
        }
    };

    return makeSurfaceIntegrand<D>( { AssemblyType::Vector }, DiffOrders::Shapes, evaluate );
}

} // namespace

template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNeumannIntegrand( const spatial::VectorFunction<D>& rhs )
{
    auto cache = std::make_shared<DoubleVectorCache>( std::vector<double>( rhs.odim, 0.0 ) );

    auto function = [cache, rhs]( std::array<double, D> xyz, auto&&, auto&& data )
    {
        data.resize( rhs.odim );

        std::fill( data.begin( ), data.end( ), 0.0 );

        rhs( xyz, data );

        return std::span<double>( data );
    };

    return vectorNeumanIntegrand<D>( std::move( function ) );
}

template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNormalNeumannIntegrand( const spatial::ScalarFunction<D>& pressure )
{
    auto function = [pressure]( std::array<double, D> xyz, std::array<double, D>& normal, auto&& )
    {
        normal = normal * pressure(xyz);

        return std::span<double>( normal );
    };

    return vectorNeumanIntegrand<D>( std::move( function ) );
}

template<size_t D>
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::ScalarFunction<D>& mass,
                                             const spatial::ScalarFunction<D>& rhs,
                                             size_t ifield )
{
    auto evaluate = [=]( typename SurfaceIntegrand<D>::Cache&,
                         const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& /* locationMap */,
                         std::array<double, D> /* normal */,
                         AlignedDoubleVectors& targets,
                         double weightDetJ )
    {
        computeL2ElementSystem<true, true>( mass( shapes.xyz( ) ), 
            rhs( shapes.xyz( ) ), shapes, targets, weightDetJ, ifield );
    };

    return makeSurfaceIntegrand<D>( symmetricTargets( true, true ), DiffOrders::Shapes, evaluate );
}

template<size_t D>
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::ScalarFunction<D>& mass,
                                             const spatial::ScalarFunction<D>& rhs,
                                             memory::vptr<const std::vector<double>> dofs,
                                             size_t ifield,
                                             bool computeTangent )
{
    auto createEvaluate = [&]<bool tangent>( )
    {
        return std::function { [=] ( typename SurfaceIntegrand<D>::Cache&,
                                     const BasisFunctionEvaluation<D>& shapes,
                                     const LocationMap& locationMap,
                                     std::array<double, D> /* normal */,
                                     AlignedDoubleVectors& targets,
                                     double weightDetJ )
        {
            auto u = evaluateSolution( shapes, locationMap, *dofs, ifield );
            auto massValue = mass( shapes.xyz( ) );

            computeL2ElementSystem<tangent, true>( massValue, rhs( shapes.xyz( ) ) -
                massValue * u, shapes, targets, weightDetJ, ifield );
        } };
    };

    auto evaluate = computeTangent ? 
        createEvaluate.template operator()<true>( ) : 
        createEvaluate.template operator()<false>( );

    return makeSurfaceIntegrand<D>( symmetricTargets( computeTangent, true ), 
        DiffOrders::Shapes, std::move( evaluate ) );
}

template<size_t D>
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::VectorFunction<D>& mass,
                                             const spatial::VectorFunction<D>& rhs )
{
    auto evaluate = [=]( typename SurfaceIntegrand<D>::Cache& anyCache,
                         const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& /* locationMap */,
                         std::array<double, D> /* normal */,
                         AlignedDoubleVectors& targets,
                         double weightDetJ )
    {
        auto& data = utilities::cast<typename SurfaceIntegrand<D>::DefaultCache>( anyCache ).doubleVector;

        data.resize( 2 * mass.odim );

        std::fill( data.begin( ), data.end( ), 0.0 );

        auto massValue = evaluateVectorFunction( mass, shapes, data, 0 );
        auto rhsValue = evaluateVectorFunction( rhs, shapes, data, mass.odim );

        computeL2ElementSystem<true, true>( massValue, rhsValue, shapes, targets, weightDetJ );
    };

    return makeSurfaceIntegrand<D>( symmetricTargets( true, true ), DiffOrders::Shapes, evaluate );
}

template<size_t D> 
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::VectorFunction<D>& mass,
                                             const spatial::VectorFunction<D>& rhs,
                                             memory::vptr<const std::vector<double>> dofs,
                                             bool computeTangent )
{
    auto create = [&]<bool M>( )
    {
        return std::function { [=] ( typename SurfaceIntegrand<D>::Cache& anyCache,
                                     const BasisFunctionEvaluation<D>& shapes,
                                     const LocationMap& locationMap,
                                     std::array<double, D> /* normal */,
                                     AlignedDoubleVectors& targets,
                                     double weightDetJ )
        {
            auto& data = utilities::cast<typename SurfaceIntegrand<D>::DefaultCache>( anyCache ).doubleVector;

            data.resize( 3 * mass.odim );

            std::fill( data.begin( ), data.end( ), 0.0 );

            auto massValue = evaluateVectorFunction( mass, shapes, data, 0 );
            auto rhsValue = evaluateVectorFunction( rhs, shapes, data, mass.odim );
            auto uValue = std::span( data.data( ) + mass.odim, shapes.nfields( ) );

            evaluateSolutions( shapes, locationMap, *dofs, uValue, 0 );

            for( size_t ifield = 0; ifield < uValue.size( ); ++ifield )
            {
                rhsValue[ifield] = rhsValue[ifield] - massValue[ifield] * uValue[ifield];
            }

            computeL2ElementSystem<M, true>( massValue, rhsValue, shapes, targets, weightDetJ );
        } };

    };

    auto evaluate = computeTangent ? create.template operator()<true>( ) : create.template operator()<false>( );

    return makeSurfaceIntegrand<D>( symmetricTargets( computeTangent, true ), DiffOrders::Shapes, evaluate );
}

namespace
{
    
template<size_t D>
auto internalNormalL2Integrand( const std::optional<spatial::ScalarFunction<D>>& mass,
                                auto&& rhs, bool computeVector )
{
    auto computeMatrix = mass != std::nullopt;

    auto evaluate = [=]( typename SurfaceIntegrand<D>::Cache& cache,
                         const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& locationMap,
                         std::array<double, D> normal,
                         AlignedDoubleVectors& targets,
                         double weightDetJ )
    {
        auto& tmp = utilities::cast<typename SurfaceIntegrand<D>::DefaultCache>( cache ).doubleVector;

        auto [ndof, nblocks, ndofpadded] = shapes.sizes( );
        auto nfields = shapes.nfields( );

        MLHP_CHECK( nfields == D, "Inconsistent number of fields" );

        tmp.resize( ndofpadded );

        auto N = memory::assumeAlignedNoalias( tmp.data( ) );
        auto offset = size_t { 0 };
    
        for( size_t ifield = 0; ifield < nfields; ++ifield )
        {
            auto ndofI = shapes.ndof( ifield );
            auto NI = shapes.noalias( ifield, 0 );

            for( size_t idof = 0; idof < ndofI; ++idof )
            {
                auto value = normal[ifield] * NI[idof];

                N[offset + idof] = value;
            }

            offset += ndofI;
        }
    
        if( computeVector )
        {
            auto value = rhs( shapes, locationMap, normal ) * weightDetJ;

            linalg::elementRhs( targets[computeMatrix].data( ), ndof, nblocks, [&]( size_t i )
            {
                return N[i] * value;
            } );
        }

        if( computeMatrix )
        {
            auto value = std::sqrt( ( *mass )( shapes.xyz( ) ) * weightDetJ );

            std::transform( N, N + ndofpadded, N, [=]( double v ) { return v * value; } );

            linalg::symmetricElementLhs( targets[0].data( ), ndof, nblocks, [&]( size_t i, size_t j )
            {
                return N[i] * N[j];
            } );
        }
    };

    return makeSurfaceIntegrand<D>( symmetricTargets( computeMatrix, computeVector ), DiffOrders::Shapes, evaluate );
}

} // namespace

template<size_t D>
SurfaceIntegrand<D> makeL2NormalIntegrand( const std::optional<spatial::ScalarFunction<D>>& mass,
                                           const std::optional<spatial::ScalarFunction<D>>& rhs )
{
    auto rhsCallback = [=]( auto& shapes, auto&, auto& ) { return ( *rhs )( shapes.xyz( ) ); };

    return internalNormalL2Integrand<D>( mass, std::move( rhsCallback ), rhs != std::nullopt );
}

template<size_t D>
SurfaceIntegrand<D> makeL2NormalIntegrand( const std::optional<spatial::ScalarFunction<D>>& mass,
                                           const std::optional<spatial::ScalarFunction<D>>& rhs,
                                           memory::vptr<const std::vector<double>> dofs )
{
    auto rhsCallback = [=]( auto& shapes, auto& locationMap, auto& normal ) 
    { 
        return spatial::dot( evaluateSolutions<D>( shapes, locationMap, *dofs ), normal ) - ( *rhs )( shapes.xyz( ) ); 
    };

    return internalNormalL2Integrand<D>( mass, std::move( rhsCallback ), rhs != std::nullopt );
}

namespace
{

template<size_t D>
auto internalNitscheIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,
                               memory::vptr<const ConstitutiveEquation<D>> constitutive,
                               const spatial::VectorFunction<D>& function,
                               double beta )
{
    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& /* locationMap */,
                         std::array<double, D> normal,
                         AlignedDoubleVectors& targets,
                         AlignedDoubleVector& tmp,
                         auto& kinematicsCache,
                         auto& constitutiveCache,
                         double weightDetJ )
    { 
        auto ncomponents = constitutive->ncomponents;
        auto ndof = shapes.ndof( );
        auto nblocks = shapes.nblocks( );
        auto ndofpadded = shapes.ndofpadded( );
        auto nfields = shapes.nfields( );

        MLHP_CHECK( nfields == D, "Number of fields not equal to number of dimensions." );

        tmp.resize( ( ncomponents + 2 * D ) * ndofpadded + ncomponents * ncomponents );

        std::fill( tmp.begin( ), tmp.end( ), 0.0 );

        auto Sn = std::span( tmp.data( ), D * ndofpadded );
        auto N = std::span( Sn.data( ) + D * ndofpadded, D * ndofpadded );

        auto strainOperator = std::span( N.data( ) + D * ndofpadded, ncomponents * ndofpadded );
        auto materialMatrix = std::span( strainOperator.data( ) + ncomponents * ndofpadded, ncomponents * ncomponents );

        kinematics->evaluate( kinematicsCache, shapes, std::span<double> { }, std::span<double> { }, strainOperator );
        constitutive->evaluate( constitutiveCache, shapes, std::span<double> { }, std::span<double> { }, materialMatrix );

        auto NPtr = memory::assumeAlignedNoalias( N.data( ) );
        auto BPtr = memory::assumeAlignedNoalias( Sn.data( ) );

        // Compute n^T * C * B
        for( size_t i = 0; i < ndofpadded; ++i )
        {
            auto S = std::array<double, D * D> { };

            // Compute row i of C * B: S_i = C_jk * B_ki
            for( size_t j = 0; j < ncomponents; ++j )
            {
                for( size_t k = 0; k < ncomponents; ++k )
                {
                    S[j] += materialMatrix[j * ncomponents + k] * strainOperator[k * ndofpadded + i];
                }
            }

            // Compute dot product with normal vector: Sn_ij = S_jk * n_k
            for( size_t j = 0; j < D; ++j )
            {
                Sn[j * ndofpadded + i] = 0.0;

                for( size_t k = 0; k < D; ++k )
                {
                    auto index = VoigtIndices<D>::matrix[j][k];

                    Sn[j * ndofpadded + i] += normal[k] * S[index];
                }
            }
        }

        auto fieldOffset = size_t { 0 };

        for( size_t ifield = 0; ifield < nfields; ++ifield )
        {
            auto ndofI = shapes.ndof( ifield );
            auto NI = shapes.noalias( ifield, 0 );

            for( size_t idof = 0; idof < ndofI; ++idof )
            {
                NPtr[ifield * ndofpadded + fieldOffset + idof] = NI[idof];
            }

            fieldOffset += ndofI;
        }

        auto lhs = [&]( size_t i, size_t j )
        { 
            auto value = 0.0;

            for( size_t axis = 0; axis < D; ++axis )
            {
                value += NPtr[axis * ndofpadded + i] * NPtr[axis * ndofpadded + j] * beta;
                value -= NPtr[axis * ndofpadded + i] * BPtr[axis * ndofpadded + j];
                value -= BPtr[axis * ndofpadded + i] * NPtr[axis * ndofpadded + j];
            }

            return value * weightDetJ;
        };

        auto fValue = function.template call<D>( shapes.xyz( ) );

        auto rhs = [&]( size_t i )
        {
            auto value = 0.0;

            for( size_t axis = 0; axis < D; ++axis )
            {
                value += ( NPtr[axis * ndofpadded + i] * beta + BPtr[axis * ndofpadded + i] ) * fValue[axis];
            }

            return value * weightDetJ;
        };

        if( constitutive->symmetric )
        {
            linalg::symmetricElementLhs( targets[0].data( ), ndof, nblocks, std::move( lhs ) );
        }
        else
        {
            linalg::unsymmetricElementLhs( targets[0].data( ), ndof, nblocks, std::move( lhs ) );
        }

        linalg::elementRhs( targets[1].data( ), ndof, nblocks, std::move( rhs ) );
    };

    auto types = std::vector { AssemblyType::Vector };
    auto integrateTangent = true;

    if( integrateTangent )
    {
        types.insert( types.begin( ), constitutive->symmetric ? 
            AssemblyType::SymmetricMatrix : AssemblyType::UnsymmetricMatrix );
    }

    return internalElasticSurfaceIntegrand<D>( types, DiffOrders::FirstDerivatives,
        kinematics, constitutive, std::move( evaluate ) );
}

} // namespace 

template<size_t D>
SurfaceIntegrand<D> makeNitscheIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,
                                          memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                          const spatial::VectorFunction<D>& function,
                                          double beta )
{
    // Needs to be tested
    MLHP_NOT_IMPLEMENTED;

    return internalNitscheIntegrand<D>( kinematics, constitutive, function, beta );
}

template<size_t D>
SurfaceIntegrand<D> makeNitscheIntegrand( [[maybe_unused]] memory::vptr<const KinematicEquation<D>> kinematics,
                                          [[maybe_unused]] memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                          [[maybe_unused]] memory::vptr<const std::vector<double>> dofs,
                                          [[maybe_unused]] const spatial::VectorFunction<D>& function,
                                          [[maybe_unused]] double beta )
{
    MLHP_NOT_IMPLEMENTED;
}

template<size_t D>
void expandVoigtNotation( std::span<const double> reduced,
                          std::span<double> fullTensor )
{
    if( isvoigt<D>( reduced.size( ) ) )
    {
        for( size_t i = 0; i < D; ++i )
        {
            for( size_t j = 0; j < D; ++j )
            {
                fullTensor[i * D + j] = reduced[VoigtIndices<D>::vector[i][j]];
            }
        }
    }
    else if( reduced.size( ) == D * D )
    {
        std::copy( reduced.begin( ), reduced.end( ), fullTensor.begin( ) );
    }
    else
    {
        MLHP_THROW( "Constitutive components are neither ndim^2 nor in Voigt notation." );
    }
}

template<size_t D>
SurfaceIntegrand<D> makeReactionForceIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,
                                                memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                                memory::vptr<const std::vector<double>> dofs )
{
    if constexpr ( D > 3 )
    {
        MLHP_THROW( "Reaction force integrand is implemented only for dimensions 1, 2, and 3." );
    }

    auto evaluate = [=]( const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& locationMap,
                         std::array<double, D> normal,
                         AlignedDoubleVectors& targets,
                         AlignedDoubleVector& tmp,
                         auto& kinematicsCache,
                         auto& constitutiveCache,
                         double weightDetJ )
    { 
        auto ncomponents = constitutive->ncomponents;

        // Two matrices with (6, padded(N)) for stresses and strains
        tmp.resize( 2 * ncomponents + D * D );        

        std::fill( tmp.begin( ), tmp.end( ), 0.0 );

        auto deformationGradient = std::span( tmp.data( ), D * D );
        auto strain = std::span( deformationGradient.data( ) + D * D, ncomponents );
        auto stress = std::span( strain.data( ) + ncomponents, ncomponents );

        // Compute B matrix from shape function evaluation
        evaluateSolutions( shapes, locationMap, *dofs, deformationGradient, 1 );

        kinematics->evaluate( kinematicsCache, shapes, deformationGradient, strain, std::span<double> { } );
        constitutive->evaluate( constitutiveCache, shapes, strain, stress, std::span<double> { } );
    
        auto fullStressTensor = deformationGradient;

        expandVoigtNotation<D>( stress, fullStressTensor );

        for( size_t i = 0; i < D; ++i )
        {
            for( size_t j = 0; j < D; ++j )
            {
                targets[i][0] += fullStressTensor[i * D + j] * normal[j] * weightDetJ;
            }
        }
    };

    auto types = AssemblyTypeVector( D, AssemblyType::Scalar );

    return internalElasticSurfaceIntegrand<D>( types, DiffOrders::FirstDerivatives,
        kinematics, constitutive, std::move( evaluate ) );
}

template<size_t D>
SurfaceIntegrand<D> makeFunctionSurfaceIntegrand( const spatial::ScalarFunction<D>& function )
{
    auto evaluate = [=] ( typename SurfaceIntegrand<D>::Cache&,
                          const BasisFunctionEvaluation<D>& shapes,
                          const LocationMap&,
                          std::array<double, D>,
                          AlignedDoubleVectors& targets,
                          double weightDetJ )
    {
        targets[0][0] += function( shapes.xyz( ) ) * weightDetJ;
    };

    return makeSurfaceIntegrand<D>( std::vector { AssemblyType::Scalar }, DiffOrders::NoShapes, evaluate );
}

namespace
{

template<size_t D>
auto makeVectorSurfaceIntegrand( const spatial::VectorFunction<D>& function,
                                 size_t nvariables, auto&& callback )
{
    auto evaluate = [=] ( typename SurfaceIntegrand<D>::Cache& anyCache,
                          const BasisFunctionEvaluation<D>& shapes,
                          const LocationMap&,
                          std::array<double, D> normal,
                          AlignedDoubleVectors& targets,
                          double weightDetJ )
    {
        auto& data = utilities::cast<typename SurfaceIntegrand<D>::DefaultCache>( anyCache ).doubleVector;

        data.resize( function.odim );

        std::fill( data.begin( ), data.end( ), 0.0 );

        function( shapes.xyz( ), data );

        callback( data, normal, weightDetJ, targets );
    };

    auto types = AssemblyTypeVector( nvariables, AssemblyType::Scalar );

    return makeSurfaceIntegrand<D>( types, DiffOrders::NoShapes, evaluate );
}

} // namespace

template<size_t D>
SurfaceIntegrand<D> makeFunctionSurfaceIntegrand( const spatial::VectorFunction<D>& function )
{
    auto evaluate = []( auto& data, auto&, auto weightDetJ, auto& targets )
    { 
        for( size_t i = 0; i < data.size( ); ++i )
        {
            targets[i][0] += data[i] * weightDetJ;
        }
    };

    return makeVectorSurfaceIntegrand( function, function.odim, evaluate );
}

template<size_t D>
SurfaceIntegrand<D> makeNormalDotProductIntegrand( const spatial::VectorFunction<D>& function )
{
    auto evaluate = []( auto& data, auto& normal, auto weightDetJ, auto& targets )
    { 
        for( size_t i = 0; i < data.size( ); ++i )
        {
            targets[0][0] += data[i] * normal[i] * weightDetJ;
        }
    };

    return makeVectorSurfaceIntegrand( function, 1, evaluate );
}

template<size_t D>
BasisProjectionIntegrand<D> makeL2BasisProjectionIntegrand( memory::vptr<const std::vector<double>> oldDofs )
{
    auto evaluate = [=]( const LocationMap& locationMap0,
                         const LocationMap&,
                         const BasisFunctionEvaluation<D>& shapes0,
                         const BasisFunctionEvaluation<D>& shapes1,
                         AlignedDoubleVectors& targets,
                         double weightDetJ )
    { 
        auto nfields = shapes1.nfields( );
        auto size = shapes1.ndof( );
        auto offset = size_t { 0 };

        MLHP_CHECK( shapes0.nfields( ) == nfields, "Inconsistent number of fields." );

        for( size_t kfield = 0; kfield < nfields; ++kfield )
        {
            auto ndof = shapes1.ndof( kfield );
            auto nblocks = shapes1.nblocks( kfield );

            auto Nk = shapes1.noalias( kfield, 0 );
            auto uk = evaluateSolution( shapes0, locationMap0, *oldDofs, kfield );

            linalg::elementLhs<linalg::SymmetricDenseMatrix>( targets[0].data( ), 
                size, offset, ndof, offset, ndof, [&]( size_t i, size_t j )
            {
                return Nk[i] * Nk[j] * weightDetJ;
            } );

            linalg::elementRhs( targets[1].data( ) + offset, ndof, nblocks, [&]( size_t i )
            {
                return Nk[i] * uk * weightDetJ;

            } );

            offset += ndof;
        }
    };

    return BasisProjectionIntegrand<D>( symmetricTargets( true, true ), DiffOrders::Shapes, evaluate );
}

template<size_t D> MLHP_EXPORT
BasisProjectionIntegrand<D> makeTransientPoissonIntegrand( const spatial::ScalarFunction<D + 1>& capacity,
                                                           const spatial::ScalarFunction<D + 1>& diffusivity,
                                                           const spatial::ScalarFunction<D + 1>& source,
                                                           memory::vptr<const std::vector<double>> dofs0,
                                                           std::array<double, 2> timeStep,
                                                           double theta )
{
    auto evaluate = [=]( const LocationMap& locationMap0,
                         const LocationMap&,
                         const BasisFunctionEvaluation<D>& shapes0,
                         const BasisFunctionEvaluation<D>& shapes1,
                         AlignedDoubleVectors& targets,
                         double weightDetJ )
    { 
        auto tmp1 = shapes1.sizes( );

        auto ndof = std::get<0>( tmp1 );
        auto nblocks = std::get<1>( tmp1 );
        auto ndofpadded = std::get<2>( tmp1 );

        auto N = shapes1.noalias( 0, 0 );
        auto dN = shapes1.noalias( 0, 1 );

        auto u = evaluateSolution( shapes0, locationMap0, *dofs0 );
        auto du = evaluateGradient( shapes0, locationMap0, *dofs0 );

        auto xyz = shapes1.xyz( );

        auto xyzt0 = array::append( xyz, timeStep[0] );
        auto xyzt1 = array::append( xyz, timeStep[1] );

        double c = capacity( xyzt1 ) * weightDetJ / ( timeStep[1] - timeStep[0] );
        double k = diffusivity( xyzt1 ) * weightDetJ;

        double source0 = theta == 1.0 ? 0.0 : source( xyzt0 ) * weightDetJ;
        double source1 = theta == 0.0 ? 0.0 : source( xyzt1 ) * weightDetJ;

        linalg::symmetricElementLhs( targets[0].data( ), ndof, nblocks, [&]( size_t i, size_t j )
        {
            double value = N[i] * N[j] * c;

            for( size_t axis = 0; axis < D; ++axis )
            {
                value += dN[axis * ndofpadded + i] * dN[axis * ndofpadded + j] * theta * k;

            } // component

            return value;
        } );

        linalg::elementRhs( targets[1].data( ), ndof, nblocks, [&]( size_t i )
        {
            double value = N[i] * ( c * u + ( 1.0 - theta ) * source0 + theta * source1 );

            for( size_t axis = 0; axis < D; ++axis )
            {
                value -= dN[axis * ndofpadded + i] * ( 1.0 - theta ) * k * du[axis];
            }

            return value;
        } );
    };

    return BasisProjectionIntegrand<D>( symmetricTargets( true, true ), DiffOrders::FirstDerivatives, evaluate );
}

#define MLHP_INSTANTIATE_DIM( D )                                                                                 \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makePoissonIntegrand( const spatial::ScalarFunction<D>& kappa,                             \
                                             const spatial::ScalarFunction<D>& source );                          \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeAdvectionDiffusionIntegrand( const spatial::VectorFunction<D, D>& velocity,            \
                                                        const spatial::ScalarFunction<D>& diffusivity,            \
                                                        const spatial::ScalarFunction<D>& source );               \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeFunctionIntegrand( const spatial::ScalarFunction<D>& function );                       \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeFunctionIntegrand( const spatial::VectorFunction<D>& function );                       \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    KinematicEquation<D> makeSmallStrainKinematics( );                                                            \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    void expandVoigtNotation<D>( std::span<const double> reduced, std::span<double> fullTensor );                 \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    void checkConsistency( const memory::vptr<const KinematicEquation<D>>& kinematics,                            \
                           const memory::vptr<const ConstitutiveEquation<D>>& constitutive );                     \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    void checkConsistency( const AbsBasis<D>& basis,                                                              \
                           const memory::vptr<const KinematicEquation<D>>& kinematics );                          \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeStaticDomainIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,            \
                                                  memory::vptr<const ConstitutiveEquation<D>> constitutive,       \
                                                  const spatial::VectorFunction<D, D>& force );                   \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeStaticDomainIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,            \
                                                  memory::vptr<const ConstitutiveEquation<D>> constitutive,       \
                                                  memory::vptr<const std::vector<double>> dofs,                   \
                                                  const spatial::VectorFunction<D, D>& force,                     \
                                                  bool integrateTangent );                                        \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeL2DomainIntegrand( std::optional<spatial::ScalarFunction<D>> mass,                     \
                                              std::optional<spatial::ScalarFunction<D>> rhs,                      \
                                              memory::vptr<const std::vector<double>> dofs,                       \
                                              size_t ifield );                                                    \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeL2DomainIntegrand( const spatial::ScalarFunction<D>& rhs,                              \
                                              size_t ifield );                                                    \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeL2DomainIntegrand( const spatial::ScalarFunction<D>& mass,                             \
                                              const spatial::ScalarFunction<D>& rhs,                              \
                                              size_t ifield );                                                    \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeL2DomainIntegrand( const spatial::VectorFunction<D>& rhs );                            \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeL2DomainIntegrand( std::optional<spatial::VectorFunction<D>> mass,                     \
                                              std::optional<spatial::VectorFunction<D>> rhs,                      \
                                              memory::vptr<const std::vector<double>> dofs );                     \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeL2ErrorIntegrand( memory::vptr<const std::vector<double>> solutionDofs,                \
                                             const spatial::ScalarFunction<D>& solutionFunction );                \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeEnergyErrorIntegrand( memory::vptr<const std::vector<double>> solutionDofs,            \
                                                 const spatial::VectorFunction<D, D>&                             \
                                                     analyticalDerivatives );                                     \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    DomainIntegrand<D> makeInternalEnergyIntegrand( memory::vptr<const std::vector<double>> solutionDofs,         \
                                                    memory::vptr<const KinematicEquation<D>> kinematics,          \
                                                    memory::vptr<const ConstitutiveEquation<D>> constitutive );   \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    BasisProjectionIntegrand<D> makeL2BasisProjectionIntegrand( memory::vptr<const std::vector<double>> oldDofs );\
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    BasisProjectionIntegrand<D> makeTransientPoissonIntegrand( const spatial::ScalarFunction<D + 1>& capacity,    \
                                                               const spatial::ScalarFunction<D + 1>& diffusivity, \
                                                               const spatial::ScalarFunction<D + 1>& source,      \
                                                               memory::vptr<const std::vector<double>> dofs0,     \
                                                               std::array<double, 2> timeStep,                    \
                                                               double theta );                                    \
                                                                                                                  \
    template class SurfaceIntegrand<D>;                                                                           \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeNeumannIntegrand( const spatial::ScalarFunction<D>& rhs, size_t ifield );             \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeNeumannIntegrand( const spatial::VectorFunction<D>& rhs );                            \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeNormalNeumannIntegrand( const spatial::ScalarFunction<D>& pressure );                 \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::ScalarFunction<D>& mass,                          \
                                                 const spatial::ScalarFunction<D>& rhs,                           \
                                                 size_t ifield );                                                 \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::ScalarFunction<D>& mass,                          \
                                                 const spatial::ScalarFunction<D>& rhs,                           \
                                                 memory::vptr<const std::vector<double>> dofs,                    \
                                                 size_t ifield, bool computeTangent );                            \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::VectorFunction<D>& mass,                          \
                                                 const spatial::VectorFunction<D>& rhs );                         \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::VectorFunction<D>& mass,                          \
                                                 const spatial::VectorFunction<D>& rhs,                           \
                                                 memory::vptr<const std::vector<double>> dofs,                    \
                                                 bool computeTangent );                                           \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeL2NormalIntegrand( const std::optional<spatial::ScalarFunction<D>>& lhs,              \
                                               const std::optional<spatial::ScalarFunction<D>>& rhs );            \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeL2NormalIntegrand( const std::optional<spatial::ScalarFunction<D>>& lhs,              \
                                               const std::optional<spatial::ScalarFunction<D>>& rhs,              \
                                               memory::vptr<const std::vector<double>> dofs );                    \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeNitscheIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,                \
                                              memory::vptr<const ConstitutiveEquation<D>> constitutive,           \
                                              const spatial::VectorFunction<D>& function,                         \
                                              double beta );                                                      \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeNitscheIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,                \
                                              memory::vptr<const ConstitutiveEquation<D>> constitutive,           \
                                              memory::vptr<const std::vector<double>> dofs,                       \
                                              const spatial::VectorFunction<D>& function,                         \
                                              double beta );                                                      \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeReactionForceIntegrand( memory::vptr<const KinematicEquation<D>> kinematics,          \
                                                    memory::vptr<const ConstitutiveEquation<D>> constitutive,     \
                                                    memory::vptr<const std::vector<double>> dofs );               \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeFunctionSurfaceIntegrand( const spatial::ScalarFunction<D>& function );               \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeFunctionSurfaceIntegrand( const spatial::VectorFunction<D>& function );               \
                                                                                                                  \
    template MLHP_EXPORT                                                                                          \
    SurfaceIntegrand<D> makeNormalDotProductIntegrand( const spatial::VectorFunction<D>& function );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // mlhp
