// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core.hpp"
#include <iomanip>

using namespace mlhp;

template<size_t D>
class AbsRefinedGridFunction : public utilities::DefaultVirtualDestructor
{
        HierarchicalGridSharedPtr<D> grid_;
        size_t ncomponents_;

    public:
        AbsRefinedGridFunction( const HierarchicalGridSharedPtr<D>& grid, size_t ncomponents ) :
            grid_ { grid }, ncomponents_ { ncomponents }
        { }
        
    const AbsHierarchicalGrid<D>& grid( ) const { return *grid_; };
    const HierarchicalGridSharedPtr<D> gridPtr( ) const { return grid_; }
    
    auto ncomponents( ) const
    {
        return ncomponents_;
    }

    template<size_t N>
    std::array<double, N> evaluate( const AbsHierarchicalGrid<D>& otherGrid,
                                    CellIndex otherCell, 
                                    std::array<double, D> otherRst,
                                    std::array<double, D> xyz ) const
    {
        auto [historyCell, historyRst] = mesh::mapToOtherGrid( otherGrid, this->grid( ), otherCell, otherRst );

        return this->evaluate<N>( historyCell, historyRst, xyz );
    }

    void evaluate( const AbsHierarchicalGrid<D>& otherGrid,
                   std::span<double> target,
                   CellIndex otherCell,
                   std::array<double, D> otherRst,
                   std::array<double, D> xyz ) const
    {
        auto [historyCell, historyRst] = mesh::mapToOtherGrid( otherGrid, this->grid( ), otherCell, otherRst );

        evaluateInternal( historyCell, target, historyRst, xyz );
    }

    template<size_t N>
    std::array<double, N> evaluate( CellIndex historyCell,
                                    std::array<double, D> rst,
                                    std::array<double, D> xyz ) const
    {
        MLHP_CHECK( N == ncomponents( ), "Inconsistent number of components." );

        auto target = std::array<double, N> { };

        evaluate( historyCell, target, rst, xyz );

        return target;
    }
    
    void evaluate( CellIndex historyCell,
                   std::span<double> target,
                   std::array<double, D> rst,
                   std::array<double, D> xyz ) const
    {
        evaluateInternal( historyCell, target, rst, xyz );
    }

private:
    virtual void evaluateInternal( CellIndex historyCell,
                                   std::span<double> target,
                                   std::array<double, D> rst, 
                                   std::array<double, D> xyz ) const = 0;
};

template<size_t D>
using SharedRefinedGridFunction = std::shared_ptr<AbsRefinedGridFunction<D>>;

template<size_t D>
class GaussPointInterpolation : public AbsRefinedGridFunction<D>
{
public:
    GaussPointInterpolation( std::shared_ptr<AbsHierarchicalGrid<D>> grid,
                             size_t ncomponents,
                             size_t quadratureOrder ) :
        AbsRefinedGridFunction<D>( grid, ncomponents ),
        quadratureOrder_ { quadratureOrder },
        points_ { gaussLegendrePoints( quadratureOrder )[0] }
    { 
        auto generator = [this, n = size_t { 0 }]( ) mutable
        {
            auto n0 = n;
            n += this->ncomponents( ) * utilities::integerPow( quadratureOrder_, D );
            return n0;
        };

        offsets_.resize( this->grid( ).ncells( ) + 1 );
        std::generate( offsets_.begin( ), offsets_.end( ), generator );
        data_.resize( offsets_.back( ) );
    }

    GaussPointInterpolation( const AbsRefinedGridFunction<D>& oldHistory,
                             const HierarchicalGridSharedPtr<D>& newGrid,
                             size_t quadratureOrder ) :
        GaussPointInterpolation( newGrid, oldHistory.ncomponents( ), quadratureOrder )
    {
        auto orders = array::makeSizes<D>( quadratureOrder );
        auto points = gaussLegendrePoints( quadratureOrder )[0];

        #pragma omp parallel
        {
            auto ncells = static_cast<std::int64_t>( newGrid->ncells( ) );
            auto mapping = newGrid->createMapping( );

            #pragma omp for
            for( std::int64_t ii = 0; ii < ncells; ++ii )
            {
                auto icell = static_cast<CellIndex>( ii );

                newGrid->prepareMapping( icell, mapping );

                nd::executeWithIndex( orders, [&]( std::array<size_t, D> ijk, size_t gaussPointIndex )
                {
                    auto newRst = std::array<double, D> { };

                    for( size_t axis = 0; axis < D; ++axis )
                    {
                        newRst[axis] = points[ijk[axis]];
                    }
                                      
                    auto [oldIndex, oldRst] = mesh::mapToOtherGrid( *newGrid, oldHistory.grid( ), icell, newRst );
                    auto itbegin = utilities::begin( data_, offsets_[icell] + gaussPointIndex * this->ncomponents( ) );
                    auto targetSpan = std::span( itbegin, oldHistory.ncomponents( ) );

                    oldHistory.evaluate( oldIndex, targetSpan, oldRst, mapping( newRst ) );
                } );
            }
        }
    }

    void evaluateInternal( CellIndex icell, 
                           std::span<double> target, 
                           std::array<double, D> rst, 
                           std::array<double, D> ) const override
    {
        auto strides = nd::stridesFor( array::make<D>( quadratureOrder_ ) );
        auto index = size_t { 0 };

        for( size_t axis = 0; axis < D; ++axis )
        {
            auto index1D = utilities::findInterval( points_, rst[axis] );
            auto local = utilities::mapToLocal0( points_[index1D], points_[index1D + 1], rst[axis] );

            index += strides[axis] * ( local < 0.5 ? index1D : index1D + 1 );
        }

        auto begin = utilities::begin( data_, offsets_[icell] + index * this->ncomponents( ) );

        std::copy_n( begin, this->ncomponents( ), target.begin( ) );
    }

private:
    size_t quadratureOrder_;
    std::vector<double> points_;
    std::vector<size_t> offsets_;
    std::vector<double> data_;
};

// https://mae.ufl.edu/nkim/egm6352/Chap4.pdf
// https://www.youtube.com/watch?v=XO4FdwEwjG0&list=PL6f9zUtPSkfhAQyJ4GP1O-u4JKokNq4cU&index=1
// https://csm.mech.utah.edu/content/wp-content/uploads/2011/10/9tutorialOnJ2Plasticity.pdf
// Deviatoric projection: https://youtu.be/22f3ske1-e4?feature=shared&t=2295
// Return mapping: https://youtu.be/8ogBBoWptVQ?feature=shared&t=2952
// https://gitlab.lrz.de/cie_sam/adhocpp/-/blob/master/libraries/mathmodel/packages/material/src/materialFunctions.cpp?ref_type=heads#L1182
class J2PlasticityHelper
{
    std::array<double, 6> stress_ { }, flowDirection_ { }, backstress0_ { };
    std::array<double, 6 * 6> elasticTangent_ { };
    double yieldFunction_ = 0.0, deltaLambda_ = 0.0, etaTrialNorm_ = 0.0, mu_ = 0.0, ep0_ = 0.0;
    bool isinside_ = false;

    // Hardening coefficient
    double H = 0.0; // 2000 * 1e6;

    // beta = 0.0 -> isotropic hardening
    // beta = 1.0 -> kinematic hardening
    double beta = 0.5;

public:
    J2PlasticityHelper( const spatial::ScalarFunction<3>& youngsModulus,
                        const spatial::ScalarFunction<3>& poissonRatio,
                        double sigma0,
                        std::span<const double> history0,
                        std::array<double, 3> xyz,
                        std::span<const double> totalStrainIncrement,
                        const ImplicitFunction<3>& domain )
    {
        auto previousStress = std::array<double, 6> { };

        std::copy( history0.begin( ), history0.begin( ) + 6, previousStress.begin( ) );
        std::copy( history0.begin( ) + 6, history0.begin( ) + 12, backstress0_.begin( ) );
        ep0_ = history0[12];
        isinside_ = domain( xyz );

        // Linear elastic parameters
        auto nu = poissonRatio( xyz );
        auto tmp1 = ( 1.0 - 2.0 * nu );
        auto tmp2 = youngsModulus( xyz ) / ( ( 1.0 + nu ) * tmp1 );

        auto lambda = nu * tmp2;
        mu_ = 0.5 * tmp1 * tmp2;

        // Elastic tangent stiffness
        std::fill( elasticTangent_.begin( ), elasticTangent_.end( ), 0.0 );

        auto D = linalg::adapter( elasticTangent_, 6 );
        auto diagonal = lambda + 2.0 * mu_;

        D( 0, 0 ) = diagonal; D( 0, 1 ) = lambda;   D( 0, 2 ) = lambda;
        D( 1, 0 ) = lambda;   D( 1, 1 ) = diagonal; D( 1, 2 ) = lambda;
        D( 2, 0 ) = lambda;   D( 2, 1 ) = lambda;   D( 2, 2 ) = diagonal;
        D( 3, 3 ) = mu_; D( 4, 4 ) = mu_; D( 5, 5 ) = mu_;

        // Trial stress
        auto sigmaTrialIncrement = std::array<double, 6> { };

        linalg::mmproduct( elasticTangent_.data( ), totalStrainIncrement.data( ),
            sigmaTrialIncrement.data( ), 6, 6, 1 );

        auto sigmaTrial = previousStress + sigmaTrialIncrement;
        auto sigmaTrialTrace = sigmaTrial[0] + sigmaTrial[1] + sigmaTrial[2];
        auto unitTensor = std::array<double, 6> { 1.0, 1.0, 1.0, 0.0, 0.0, 0.0 };

        // Shifted stress
        auto etaTrial = sigmaTrial - backstress0_ - 1.0 / 3.0 * sigmaTrialTrace * unitTensor;

        etaTrialNorm_ = std::sqrt( etaTrial[0] * etaTrial[0] +
                                   etaTrial[1] * etaTrial[1] + 
                                   etaTrial[2] * etaTrial[2] +
                           2.0 * ( etaTrial[3] * etaTrial[3] + 
                                   etaTrial[4] * etaTrial[4] + 
                                   etaTrial[5] * etaTrial[5] ) );

        // Yield function
        yieldFunction_ = etaTrialNorm_ - std::sqrt( 2.0 / 3.0 ) * ( sigma0 + ( 1.0 - beta ) * H * ep0_ );
        
        if( !isinside_ )
        {
            yieldFunction_ = -1.0;
        }

        // If elastic
        if( yieldFunction_ < 0.0 )
        {
            stress_ = sigmaTrial;
        }
        else
        {
            // Consistency parameter: flow amount
            deltaLambda_ = yieldFunction_ / ( 2.0 * mu_ + 2.0 / 3.0 * H );

            // Unit deviatoric vector: flow direction
            flowDirection_ = etaTrial / etaTrialNorm_;

            // New stress
            stress_ = sigmaTrial - 2.0 * mu_ * deltaLambda_ * flowDirection_;
        }
    }

    auto stress( ) const
    {
        return stress_;
    }

    auto newHistory( std::span<double> target )
    {
        auto factor = isinside_;
        auto backstress1 = backstress0_ * factor;
        auto ep1 = ep0_ * factor;

        if( yieldFunction_ >= 0.0 )
        {
            backstress1 = backstress0_ + ( 2.0 / 3.0 ) * beta * H * deltaLambda_ * flowDirection_;
            ep1 = ep0_ + std::sqrt( 2.0 / 3.0 ) * deltaLambda_;
        }

        std::copy( stress_.begin( ), stress_.end( ), target.begin( ) );
        std::copy( backstress1.begin( ), backstress1.end( ), target.begin( ) + 6 );

        target[12] = ep1;
    }

    auto tangent( std::span<double> target ) const
    {
        // If elastic
        if( yieldFunction_ < 0.0 )
        {
            std::copy( elasticTangent_.begin( ), elasticTangent_.end( ), target.begin( ) );
        }
        else
        {
            // Tangent stiffness
            auto c1 = 4.0 * mu_ * mu_ / ( 2.0 * mu_ + 2.0 / 3.0 * H );

            // Algorithmic contribution 
            auto c2 = 4.0 * mu_ * mu_ * deltaLambda_ / etaTrialNorm_;

            auto D = linalg::adapter( elasticTangent_, 6 );
            auto Dalg = linalg::adapter( target, 6 );

            // Elastic with plastic correction
            for( size_t i = 0; i < 6; i++ )
            {
                for( size_t j = 0; j < 6; j++ )
                {
                    Dalg( i, j ) = D( i, j ) - ( c1 - c2 ) * flowDirection_[i] * flowDirection_[j];
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
};

auto makeJ2Material( const spatial::ScalarFunction<3>& youngsModulus,
                     const spatial::ScalarFunction<3>& poissonRatio,
                     double sigma0,
                     const SharedRefinedGridFunction<3>& history,
                     const ImplicitFunction<3>& domain )
{
    static constexpr size_t D = 3;
    static constexpr size_t ncomponents = ( D * ( D + 1 ) ) / 2;

    using AnyCache = typename ConstitutiveEquation<D>::AnyCache;

    struct ThisCache
    {
        const AbsHierarchicalGrid<D>* grid;
    };

    auto create = []( const AbsBasis<D>& basis, const KinematicEquation<D>& ) -> AnyCache
    { 
        auto grid = dynamic_cast<const AbsHierarchicalGrid<D>*>( &basis.mesh( ) );

        MLHP_CHECK( grid, "J2 plasticity needs to use a hierarchical grid to store history variables." );

        return ThisCache { .grid = grid };
    };

    auto evaluate = [=]( AnyCache& anyCache,
                         const BasisFunctionEvaluation<D>& shapes,
                         std::span<const double> strainIncrement,
                         std::span<double> stressTarget,
                         std::span<double> tangent )
    { 
        auto& cache = utilities::cast<ThisCache>( anyCache );
        
        auto j2data = history->template evaluate<13>( *cache.grid, shapes.elementIndex( ), shapes.rst( ), shapes.xyz( ) );
        auto j2plasticity = J2PlasticityHelper( youngsModulus, poissonRatio, sigma0, j2data, shapes.xyz( ), strainIncrement, domain );

        if( !tangent.empty( ) )
        {
            MLHP_CHECK( tangent.size( ) == ncomponents * ncomponents, "Tangent matrix target size (" + std::to_string( tangent.size( ) ) + 
                ") is not equal to the expected size (" + std::to_string( ncomponents ) + "^2)." );
            
            j2plasticity.tangent( tangent );
        }

        if( !stressTarget.empty( ) )
        {
            auto stress = j2plasticity.stress( );

            MLHP_CHECK_DBG( stressTarget.size( ) == ncomponents, "Inconsistent stress vector target size." );

            std::copy( stress.begin( ), stress.end( ), stressTarget.begin( ) );
        }
    };

    return ConstitutiveEquation<D>
    {
        .create = std::move( create ),
        .evaluate = std::move( evaluate ), 
        .ncomponents = ncomponents,
        .symmetric = true, 
        .incremental = true,
        .name = "J2Plasticity"
    };
}

template<size_t D>
using RefinedGridFunction = std::function<void( CellIndex historyCell,
                                                std::span<double> target,
                                                std::array<double, D> rst, 
                                                std::array<double, D> xyz )>;

template<size_t D> inline
auto makeRefinedGridFunction( const RefinedGridFunction<D>& function,
                              const HierarchicalGridSharedPtr<D>& grid,
                              size_t ncomponents )
{
    struct GridFunction : public AbsRefinedGridFunction<D>
    {
        RefinedGridFunction<D> function_;

        GridFunction( const HierarchicalGridSharedPtr<D>& g,
                      const RefinedGridFunction<D>& f,
                      size_t n ) :
            AbsRefinedGridFunction<D>( g, n ), function_ { f }
        { }

        void evaluateInternal( CellIndex historyCell,
                               std::span<double> target,
                               std::array<double, D> rst,
                               std::array<double, D> xyz ) const override
        {
            function_( historyCell, target, rst, xyz );
        }
    };

    return std::shared_ptr<AbsRefinedGridFunction<D>> { 
        std::make_shared<GridFunction>( grid, function, ncomponents ) };
};

template<size_t D>
using HistoryUpdateFunction = std::function<void( std::span<double> history,
                                                  std::span<double> strain0,
                                                  std::span<double> strain1,
                                                  std::array<double, D> xyz )>;

template<size_t D> inline
auto makeHistoryFunction( memory::vptr<const AbsRefinedGridFunction<D>> oldHistory,
                          memory::vptr<const MultilevelHpBasis<D>> basis0,
                          memory::vptr<const MultilevelHpBasis<D>> basis1,
                          memory::vptr<const std::vector<double>> dofs0,
                          memory::vptr<const std::vector<double>> dofs1,
                          memory::vptr<const KinematicEquation<D>> kinematics,
                          const HistoryUpdateFunction<D>& updateHistory )
{
    struct Cache
    {
        BasisFunctionEvaluation<D> shapes;
        BasisEvaluationCache<D> basisCache;
        std::vector<DofIndex> locationMap;
        std::vector<double> tmp;
        typename KinematicEquation<D>::AnyCache kinematicsCache;
    };

    auto container = std::make_shared<utilities::ThreadLocalContainer<std::tuple<Cache, Cache>>>( );

    for( size_t i = 0; i < container->data.size( ); ++i )
    {
        std::get<0>( container->data[i] ).basisCache = basis0->createEvaluationCache( );
        std::get<1>( container->data[i] ).basisCache = basis1->createEvaluationCache( );
        std::get<0>( container->data[i] ).kinematicsCache = kinematics->create( *basis0 );
        std::get<1>( container->data[i] ).kinematicsCache = kinematics->create( *basis1 );
        std::get<0>( container->data[i] ).tmp.resize( D * D + kinematics->ncomponents );
        std::get<1>( container->data[i] ).tmp.resize( D * D + kinematics->ncomponents );
    }

    auto update = [=]( CellIndex historyCell,
                       std::span<double> history0,
                       std::array<double, D> historyRst,
                       std::array<double, D> xyz ) mutable
    {
        auto& caches = container->get( );

        oldHistory->evaluate( historyCell, history0, historyRst, xyz );

        auto evaluateBasis = [&]( auto& basis, auto& cache, auto& dofs )
        {
            auto backward = mesh::mapToOtherGrid( oldHistory->grid( ), basis.hierarchicalGrid( ), historyCell, historyRst );
            
            basis.prepareEvaluation( backward.first, 1, cache.shapes, cache.basisCache );
            basis.locationMap( backward.first, utilities::resize0( cache.locationMap ) );
            basis.evaluateSinglePoint( backward.second, cache.shapes, cache.basisCache );

            std::fill( cache.tmp.begin( ), cache.tmp.end( ), 0.0 );

            auto gradient = std::span( cache.tmp.data( ), D * D );
            auto strain  = std::span( cache.tmp.data( ) + D * D, kinematics->ncomponents );

            evaluateSolutions( cache.shapes, cache.locationMap, dofs, gradient, 1 );

            kinematics->prepare( cache.kinematicsCache, basis.mapping( cache.basisCache ), cache.locationMap );
            kinematics->evaluate( cache.kinematicsCache, cache.shapes, gradient, strain, std::span<double> { } );

            return strain;
        };

        auto strain0 = evaluateBasis( *basis0, std::get<0>( caches ), *dofs0 );
        auto strain1 = evaluateBasis( *basis1, std::get<1>( caches ), *dofs1 );

        updateHistory( history0, strain0, strain1, xyz );
    };

    return makeRefinedGridFunction<D>( update, oldHistory->gridPtr( ), oldHistory->ncomponents( ) );
}

HistoryUpdateFunction<3> makeJ2Update( const ImplicitFunction<3>& domain,
                                       const spatial::ScalarFunction<3>& youngsModulus,
                                       const spatial::ScalarFunction<3>& poissonRatio,
                                       double sigma0 )
{
    static constexpr size_t D = 3;

    return [=]( std::span<double> history,
                std::span<double> strain0,
                std::span<double> strain1,
                std::array<double, D> xyz )
    { 
        for( size_t i = 0; i < strain1.size( ); ++i )
        {
            strain1[i] -= strain0[i];
        }

        J2PlasticityHelper( youngsModulus, poissonRatio, sigma0, 
            history, xyz, strain1, domain ).newHistory( history );
    };
}

template<typename T>
using SharedVector = std::shared_ptr<std::vector<T>>;

template<size_t D>
auto l2projectMechanicalHistory( const MultilevelHpBasis<D>& newBasis_,
                                 const AbsRefinedGridFunction<D>& oldHistory,
                                 const AbsQuadrature<D>& quadrature,
                                 const QuadratureOrderDeterminor<D>& determiner,
                                 const linalg::SparseSolver& solver,
                                 const spatial::ScalarFunction<D>& spatialWeight )
{
    auto ncomponents = size_t { oldHistory.ncomponents( ) };
    auto newBasis = makeHpBasis<TrunkSpace>( newBasis_.hierarchicalGridPtr( ), basis::maxdegree( newBasis_ ) );
    auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( *newBasis );
    auto vectors = std::vector<std::vector<double>>( ncomponents, std::vector<double>( newBasis->ndof( ), 0.0 ) );
    auto assemblyTypes = AssemblyTypeVector { AssemblyType::SymmetricMatrix };
    auto assemblyTargets = AssemblyTargetVector { matrix };

    for( size_t ivar = 0; ivar < ncomponents; ++ivar )
    {
        assemblyTypes.push_back( AssemblyType::Vector );
        assemblyTargets.push_back( vectors[ivar] );
    }

    auto evaluate = [&]( const BasisFunctionEvaluation<D>& shapes,
                         const LocationMap& /* locationMap */,
                         AlignedDoubleVectors& targets, 
                         AlignedDoubleVector& tmpHistory,
                         double weightDetJ )
    {
        auto ndofelement = shapes.ndof( );
        auto nblocks = shapes.nblocks( );
        auto N = shapes.noalias( 0, 0 );

        tmpHistory.resize( ncomponents );

        oldHistory.evaluate( newBasis->hierarchicalGrid( ), tmpHistory,
            shapes.elementIndex( ), shapes.rst( ), shapes.xyz( ) );

        weightDetJ *= spatialWeight( shapes.xyz( ) );
        
        linalg::symmetricElementLhs( targets[0].data( ), ndofelement, nblocks, [=]( size_t i, size_t j )
        {
            return N[i] * N[j] * weightDetJ;
        } );

        for( size_t icomponent = 0; icomponent < ncomponents; ++icomponent )
        {
            linalg::elementRhs( targets[icomponent + 1].data( ), ndofelement, nblocks, [&]( size_t i )
            {
                return N[i] * tmpHistory[icomponent] * weightDetJ;
            } );
        }
    };

    auto integrand = DomainIntegrand<D>( assemblyTypes, DiffOrders::Shapes, evaluate );
    auto result = std::vector<SharedVector<double>>( ncomponents );

    integrateOnDomain<D>( *newBasis, integrand, assemblyTargets, quadrature, determiner );

    for( size_t ivar = 0; ivar < ncomponents; ++ivar )
    {
        result[ivar] = std::make_shared<std::vector<double>>( solver( matrix, vectors[ivar] ) );
    }

    return result;
}

template<size_t D>
class BasisInterpolation : public AbsRefinedGridFunction<D>
{
public:
    BasisInterpolation( const MultilevelHpBasisSharedPtr<D>& basis,
                        std::vector<SharedVector<double>> projectedDofs ) :
        AbsRefinedGridFunction<D>( basis->hierarchicalGridPtr( ), projectedDofs.size( ) ),
        basis_ { basis }, projectedDofs_ { std::move( projectedDofs ) }
    { }

    void evaluateInternal( CellIndex historyCell,
                           std::span<double> target,
                           std::array<double, D> historyRst,
                           std::array<double, D> /* xyz */ ) const override
    {
        auto& cache = container.get( );

        if( !cache )
        {
            cache = std::make_shared<Cache>( );
            cache->basisCache = basis_->createEvaluationCache( );
        }

        basis_->prepareEvaluation( historyCell, 1, cache->shapes, cache->basisCache );
        basis_->locationMap( historyCell, utilities::resize0( cache->locationMap ) );
        basis_->evaluateSinglePoint( historyRst, cache->shapes, cache->basisCache );

        for( size_t icomponent = 0; icomponent < this->ncomponents( ); ++icomponent )
        {
            target[icomponent] = evaluateSolution( cache->shapes,
                cache->locationMap, *projectedDofs_[icomponent] );
        }
    }

private:
    struct Cache
    {
        BasisFunctionEvaluation<D> shapes;
        BasisEvaluationCache<D> basisCache;
        std::vector<DofIndex> locationMap;
    };

    mutable utilities::ThreadLocalContainer<std::shared_ptr<Cache>> container;

    std::vector<SharedVector<double>> projectedDofs_;
    std::shared_ptr<MultilevelHpBasis<D>> basis_;
};

template<size_t D> inline
auto makeInitialHistory( std::shared_ptr<AbsHierarchicalGrid<D>> grid,
                         const spatial::VectorFunction<D>& initializer )
{
    auto function = [=]( auto, auto target, auto, std::array<double, D> xyz )
    { 
        for( size_t i = 0; i < initializer.odim; ++i )
        {
            initializer( xyz, target );
        }
    };

    return std::shared_ptr<AbsRefinedGridFunction<D>>( 
        makeRefinedGridFunction<D>( function, grid, initializer.odim ) );
}

ElementProcessor<3> postprocessPlasicity( const AbsHierarchicalGrid<3>& grid,
                                          const AbsRefinedGridFunction<3>& history )
{
    static constexpr size_t D = 3;
    static constexpr size_t ncomponents = 13;

    MLHP_CHECK( history.ncomponents( ) == ncomponents, "Invalid number of history variables." );

    auto evaluatePoint = [&history, &grid]( auto& anyCache, auto targets, const auto& shapes )
    {
        auto data = history.template evaluate<ncomponents>( grid, 
            shapes.elementIndex( ), shapes.rst( ), shapes.xyz( ) );

        std::copy( data.begin( ), data.begin( ) + 6, targets[0].begin( ) );

        auto stressInDirection = [=]( auto direction )
        {     
            auto [S11, S22, S33, S12, S23, S13] = std::array { data[0], data[1], data[2], data[3], data[4], data[5] };

            auto S_dx = spatial::dot<3>( direction, { S11, S12, S13 } );
            auto S_dy = spatial::dot<3>( direction, { S12, S22, S23 } );
            auto S_dz = spatial::dot<3>( direction, { S13, S23, S33 } );

            return spatial::dot<3>( direction, { S_dx, S_dy, S_dz } );
        };
        
        auto [S11, S22, S33, S12, S23, S13] = std::array { data[0], data[1], data[2], data[3], data[4], data[5] };

        auto D1 = ( S11 - S22 ) * ( S11 - S22 );
        auto D2 = ( S22 - S33 ) * ( S22 - S33 );
        auto D3 = ( S33 - S11 ) * ( S33 - S11 );
        auto S = S12 * S12 + S23 * S23 + S13 * S13;

        targets[1][0] = data[12];
        targets[2][0] = std::sqrt( 0.5 * ( D1 + D2 + D3 ) + 3.0 * S );


        targets[3][0] = stressInDirection( spatial::normalize( shapes.xyz( ) ) );
        targets[4][0] = stressInDirection( spatial::findPlaneVectors( shapes.xyz( ) )[0] );
    };

    auto outputData = [=]( auto& /* basis */ )
    {
        return OutputVector
        {
            mlhp::Output {.name = "StressTensor", .type = Output::Type::PointData, .ncomponents = 6 },
            mlhp::Output {.name = "EffectivePlasticStrain", .type = Output::Type::PointData, .ncomponents = 1 },
            mlhp::Output {.name = "VonMisesStress", .type = Output::Type::PointData, .ncomponents = 1 },
            mlhp::Output {.name = "RadialStress", .type = Output::Type::PointData, .ncomponents = 1 },
            mlhp::Output {.name = "TangentialStress", .type = Output::Type::PointData, .ncomponents = 1 }
        };
    };

    return ElementProcessor<3>
    { 
        .outputData = std::move( outputData ), 
        .initialize = utilities::returnEmpty<typename ElementProcessor<D>::Cache>( ),
        .evaluateCell = utilities::doNothing( ),
        .evaluatePoint = std::move( evaluatePoint ),
        .diffOrder = DiffOrders::Shapes
    };
}

auto computeLoading( int istep, int nelastic, int nplastic, double a, double b, double c, double sigmaY )
{
    auto ielastic = istep > nelastic + nplastic ? 2 * nplastic + 2 * nelastic - istep : istep;
    auto iplastic = ielastic - nelastic;

    auto ci = std::max( iplastic, 0 ) / static_cast<double>( nplastic ) * ( c - a ) + a;
    auto Pi = 2 * sigmaY * std::log( ci / a ) + 2 * sigmaY / 3 * ( 1 - std::pow( ci, 3 ) / std::pow( b, 3 ) );

    if( iplastic < 0 )
    {
        Pi *= ielastic / static_cast<double>( nelastic );
    }

    return std::tuple { ielastic, iplastic, ci, Pi };
}

// Following in Hill - Theory of Plasticity from page 98
// Von Mises Stress is simply abs(S_tt - S_rr)!
auto makeAnalyticalStress( int istep, int nelastic, int nplastic, double a, double b, double c, double Y )
{
    auto [ielastic, iplastic, ci_, Pi_] = computeLoading( istep, nelastic, nplastic, a, b, c, Y );
    auto Pmax = std::get<3>( computeLoading( nelastic + nplastic, nelastic, nplastic, a, b, c, Y ) );

    auto ci = ci_;
    auto Pi = Pi_;

    spatial::VectorFunction<3, 2> expectedStress = [=]( std::array<double, 3> xyz ) -> std::array<double, 2>
    {
        auto r = spatial::norm( xyz );
        auto a3 = a * a * a;
        auto b3 = b * b * b;
        auto r3 = r * r * r;

        auto computeElastic = [=]( double P )
        {
            return std::array { -P * ( b3 / r3 - 1.0 ) / ( b3 / a3 - 1.0 ),
                                P * ( b3 / ( 2.0 * r3 ) + 1.0 ) / ( b3 / a3 - 1.0 ) };
        };

        auto computePlastic = [=]( double ci ) -> std::array<double, 2>
        {
            auto c3 = ci * ci * ci;

            if( r <= ci )
            {
                auto tmp = 2.0 * Y * std::log( ci / r ) + 2.0 * Y / 3.0 * ( 1.0 - c3 / b3 );

                return { -tmp, Y - tmp };
            }
            else
            {
                auto factor = 2.0 * Y * c3 / ( 3.0 * b3 );

                return { -factor * ( b3 / r3 - 1.0 ), factor * ( b3 / ( 2.0 * r3 ) + 1.0 ) };
            }
        };

        if( istep <= nelastic )
        {
            return computeElastic( Pi );
        }
        else if( istep < nelastic + nplastic + 1 )
        {
            return computePlastic( ci );
        }
        else
        {
            return computePlastic( c ) - computeElastic( Pmax - Pi );
        }
    };

    return expectedStress;
}

template<size_t D>
auto makeLineEvaluator( std::string filename, double a, double b, double c )
{
    struct WriteData
    {
        ~WriteData( )
        {
            if( data.empty( ) )
            {
                return;
            }

            auto file = std::ofstream( filename_ );

            if( !file.is_open( ) )
            {
                std::cout << "Error opening file." << std::endl;

                return;
            }
            
            file << std::scientific << std::setprecision( 18 );

            for( auto& vec : data )
            {
                for( auto& val : vec )
                {
                    file << val << " ";
                }
                file << "\n";
            }

            file.close( );
        }

        std::string filename_;
        std::vector<std::vector<double>> data;
    };

    auto writer = std::make_shared<WriteData>( WriteData { filename, { } } );

    return [=]( 
        std::shared_ptr<const AbsBasis<D>> basis,
        std::shared_ptr<const AbsRefinedGridFunction<D>> history,
        spatial::VectorFunction<3, 2> analyticalStress ) mutable
    {
        writer->data.emplace_back( );

        auto direction = spatial::normalize( std::array { 1.1, 0.8, 1.4 } );
        auto backwardMapping = history->grid( ).createBackwardMapping( );

        auto n = 200;

        for( int i = 0; i <= n; ++i )
        {
            auto xyz = ( i * ( b - a ) / n + a ) * direction;

            auto result = backwardMapping->map( xyz );
            auto h = history->template evaluate<13>( result->first, result->second, xyz );

            auto [S11, S22, S33, S12, S23, S13] = std::array { h[0], h[1], h[2], h[3], h[4], h[5] };
            auto D1 = ( S11 - S22 ) * ( S11 - S22 );
            auto D2 = ( S22 - S33 ) * ( S22 - S33 );
            auto D3 = ( S33 - S11 ) * ( S33 - S11 );
            auto S = S12 * S12 + S23 * S23 + S13 * S13;

            writer->data.back( ).push_back( std::sqrt( 0.5 * ( D1 + D2 + D3 ) + 3.0 * S ) );

            //auto [S_rr, S_tt] = analyticalStress( xyz );
            //writer->data.back( ).push_back( std::abs( S_rr - S_tt ) );
        }
    };
}

std::shared_ptr<AbsRefinedGridFunction<3>> selectHistory( 
    std::string type, auto j2update, auto closest, auto l2projection )
{
    if( type == "J2" ) return j2update;
    if( type == "CP" ) return closest;
    if( type == "L2" ) return l2projection;

    MLHP_THROW( "Invalid projection type string." );
}

// Paper from Ali: https://doi.org/10.1016/j.camwa.2018.10.027
void run( int coarsenHistory, std::string projectionType )
{
    std::cout << "==================== " << projectionType  << 
        ", " << coarsenHistory << " =====================" << std::endl;

    auto time = utilities::tic( );

    static constexpr size_t D = 3;
    static constexpr size_t nfields = D;

    // Setup benchmark parameters
    auto a = 0.102; // inner radius
    auto b = 0.203; // outer radius
    auto c = 0.149; // plastic radius

    auto E = 200 * 1e9;
    auto nu = 0.3;
    auto sigmaY = 200 * 1e6;
    
    // Study parameters
    auto nelements = array::makeSizes<D>( 10 );
    auto refinementDepth = size_t { 2 };
    auto polynomialDegree = size_t { 1 };
    auto quadratureOffset = 1;
    auto alphaFCM = 1e-6;
    auto treedepth = polynomialDegree + 2;
    //auto coarsenHistory = 1; // 0 -> no coarsening, 1 -> max one level per load step
    //auto projectionType = "CP";

    // Other setup
    auto min = array::make<D>( 0.0 );
    auto max = array::make<D>( 1.2 * b );

    auto inner = implicit::sphere<D>( min, a );
    auto outer = implicit::sphere<D>( min, b );
    auto domain = implicit::subtract( outer, inner );

    auto baseGrid = makeCartesianGrid( nelements, max - min, min );
    auto cutstate = mesh::cutstate( *baseGrid, domain, polynomialDegree + 2 );
    auto filteredGrid = std::make_shared<FilteredGrid<D>>( baseGrid, std::move( cutstate ) );

    auto mesh0 = makeRefinedGrid<D>( filteredGrid );
    auto basis0 = makeHpBasis<TrunkSpace>( mesh0, polynomialDegree, nfields );

    auto quadratureGrid0 = makeRefinedGrid<D>( filteredGrid );
    auto refineBoundary = refineTowardsDomainBoundary( domain, refinementDepth + treedepth, polynomialDegree + 2 );
    auto capRefinement0 = mesh::refineAdaptively( *mesh0, std::vector<int>( mesh0->ncells( ), static_cast<int>( treedepth ) ) );

    quadratureGrid0->refine( refinementAnd( refineBoundary, capRefinement0 ) );

    auto dofs0 = std::vector<double>( basis0->ndof( ), 0.0 );
    auto history0 = makeInitialHistory<D>( quadratureGrid0, spatial::constantFunction<D>( std::array<double, 13> { } ) );

    std::cout << "Initial state: " << basis0->nelements( ) << " elements, " << basis0->ndof( ) <<
        " dofs, " << history0->grid( ).ncells( ) << " history cells" << std::endl;

    auto nelastic = 2;
    auto nplastic = 5;
    auto ntotal = 2 * ( nelastic + nplastic ) + 1;

    auto filebase = std::string { "outputs/j2_pressurized_sphere_fcm_" };
    
    auto lineBaseName = filebase + "N" + std::to_string( nelements[0] ) + "_P" + std::to_string( polynomialDegree ) + 
        "_R" + std::to_string( refinementDepth ) + "_D" + std::to_string( treedepth ) + "_";
    auto lineExtension = projectionType + std::string { "_C" } + std::to_string( coarsenHistory ) + ".txt";
    //lineName = filebase + "Analytical.txt";

    auto evaluateLine1 = makeLineEvaluator<D>( lineBaseName + "PPCP_" + lineExtension, a, b, c );
    auto evaluateLine2 = makeLineEvaluator<D>( lineBaseName + "PPJ2_" + lineExtension, a, b, c );

    for( int istep = 0; istep < ntotal; ++istep )
    {
        auto [ielastic, iplastic, ci1_, Pi1] = computeLoading( istep, nelastic, nplastic, a, b, c, sigmaY );

        auto ci1 = ci1_;
        auto stepfilebase = std::string { filebase + std::to_string( istep ) };

        std::cout << "Load step " << istep << " / " << ntotal - 1 << ":\n" <<
            "    ielastic = " << ielastic << ", iplastic = " << iplastic << "\n"
            "    ci = " << std::fixed << std::setprecision( 3 ) << ci1 << ", Pi = " << Pi1 << std::endl;

        // Create new mesh, history, and basis
        std::function levelFunction = [&]( std::array<double, D> xyz )
        { 
             auto shape = std::exp( -std::pow( spatial::norm( xyz ) - ci1, 2 ) / ( 2 * std::pow( 0.02, 2 ) ) );

            return static_cast<RefinementLevel>( std::round( ( refinementDepth - 0.45 ) * shape ) );
        };

        auto mesh1 = makeRefinedGrid<D>( filteredGrid );

        mesh1->refine( refineWithLevelFunction<D>( levelFunction ) );

        auto quadratureGrid1 = makeRefinedGrid<D>( filteredGrid );

        auto capRefinement = mesh::refineAdaptively( *mesh1, std::vector<int>( mesh1->ncells( ), static_cast<int>( treedepth ) ) );
        auto refine1 = refinementAnd( refineBoundary, capRefinement );
        auto refine2 = mesh::refineAdaptively( *mesh1, std::vector<int>( mesh1->ncells( ), 0 ) );
        auto refine3 = mesh::refineAdaptively( history0->grid( ), std::vector<int>( history0->grid( ).ncells( ), -coarsenHistory ) );

        quadratureGrid1->refine( refinementOr( refine1, refine2, refine3 ) );

        auto quadratureMeshCreator = cellmesh::grid( array::makeSizes<D>( 1 ), PostprocessTopologies::Edges );

        writeOutput( *quadratureGrid1, quadratureMeshCreator, CellProcessor<D> { }, PVtuOutput { stepfilebase + "_quadrature" } );

        auto basis1 = makeHpBasis<TrunkSpace>( mesh1, polynomialDegree, nfields );
        auto determiner = relativeQuadratureOrder<D>( quadratureOffset );
        
        auto standardQuadrature = SpaceTreeQuadrature<D>( domain, alphaFCM, 0 );
        auto quadrature = MeshProjectionQuadrature<D>( *quadratureGrid1, standardQuadrature );

        auto domainMarchingCubes = cellmesh::domain( domain, array::makeSizes<D>( polynomialDegree + 3 ), true, true );
        auto marchingCubesQuadrature = CellmeshQuadrature<D>( domainMarchingCubes, spatial::mask( 1.0, domain, alphaFCM ) );

        std::cout << "    " << basis1->nelements( ) << " elements, " << basis1->ndof( ) << 
            " dofs, " << quadratureGrid1->ncells( ) << " quadrature cells" << std::endl;

        // Project old solution to new mesh using FCM
        auto projectionSolver = linalg::makeCGSolver( 1e-10, 0.0 );

        auto projectedDofs0 = std::vector<double> { };
        {
            auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( *basis1 );
            auto integrand = makeL2BasisProjectionIntegrand<D>( dofs0 );
            auto vector = std::vector<double>( matrix.size1( ), 0.0 );

            integrateOnDomain( *basis0, *basis1, integrand, { matrix, vector },
                               quadrature, determiner, { { }, { } } );

            projectedDofs0 = projectionSolver( matrix, vector );
        }

        // Extract triangulation of the three Dirichlet boundary surfaces
        auto boundaryResolution = array::makeSizes<D>( polynomialDegree + 3 );
        auto faceQuadrature = std::vector<SimplexQuadrature<D>> { };

        for( size_t axis = 0; axis < D; ++axis )
        {
            auto clipped = implicit::clip( domain, axis, 1e-10, false );
            auto [triangulation, celldata] = recoverDomainBoundary( *mesh1, clipped, boundaryResolution );
            auto sharedTriangulation = std::make_shared<Triangulation<D>>( std::move( triangulation ) );
            auto sharedCelldata = std::make_shared<SimplexCellAssociation<D>>( std::move( celldata ) );

            //writeStl( *sharedTriangulation, stepfilebase + "_face_" + std::to_string( axis ) + ".stl" );

            faceQuadrature.push_back( SimplexQuadrature<D>( sharedTriangulation, sharedCelldata ) );
        }

        // Extract inner sphere boundary
        auto [triangulation, celldata] = recoverDomainBoundary( *mesh1, inner, boundaryResolution );
        auto pressureQuadrature = SimplexQuadrature<D>( &triangulation, &celldata );

        // Allocate linear system
        auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( *basis1 );
        auto vector = std::vector<double>( matrix.size1( ), 0.0 );

        auto constantE = spatial::constantFunction<D>( E );
        auto constantNu = spatial::constantFunction<D>( nu );
        auto bodyForce = spatial::constantFunction<D>( array::make<nfields>( 0.0 ) );
        auto kinematics = makeSmallStrainKinematics<D>( );
        auto material = makeJ2Material( constantE, constantNu, sigmaY, history0, domain );

        auto dofs1 = projectedDofs0;
        auto norm0 = 0.0;

        std::cout << "    || F || = " << std::flush;

        // Newton-Raphson iterations
        for( size_t inewton = 0; inewton < 20; ++inewton )
        {
            std::fill( matrix.data( ), matrix.data( ) + matrix.nnz( ), 0.0 );
            std::fill( vector.begin( ), vector.end( ), 0.0 );

            auto dofIncrement = dofs1;

            for( size_t idof = 0; idof < projectedDofs0.size( ); ++idof )
            {
                dofIncrement[idof] -= projectedDofs0[idof];
            }

            // Assemble pressure integral on it
            auto pressureIntegrand = makeNormalNeumannIntegrand( spatial::constantFunction<D>( -Pi1 ) );

            integrateOnSurface( *basis1, pressureIntegrand, pressureQuadrature, { vector } );

            for( size_t axis = 0; axis < D; ++axis )
            {
                auto lhs = spatial::constantFunction<D>( 1e8 * E );
                auto rhs = spatial::constantFunction<D>( 1e8 * E * 0.0 );
                auto integrand = makeL2BoundaryIntegrand( lhs, rhs, dofs1, axis );

                integrateOnSurface( *basis1, integrand, faceQuadrature[axis], { matrix, vector } );
            }

            // Assemble domain contributions
            auto domainIntegrand = makeStaticDomainIntegrand<D>( kinematics, material, dofIncrement, bodyForce );

            if( projectionType == "J2" )
            {
                integrateOnDomain<D>( *basis1, domainIntegrand, { matrix, vector }, marchingCubesQuadrature, determiner );
            }
            else
            {
                integrateOnDomain<D>( *basis1, domainIntegrand, { matrix, vector }, quadrature, determiner );
            }

            auto norm1 = std::sqrt( std::inner_product( vector.begin( ), vector.end( ), vector.begin( ), 0.0 ) );

            norm0 = inewton == 0 ? norm1 : norm0;

            std::cout << std::scientific << std::setprecision( 2 ) << norm1 << " " << std::flush;

            // Solve
            auto dx = linalg::makeCGSolver( 1e-6, 1e-7 )( matrix, vector );

            std::transform( dofs1.begin( ), dofs1.end( ), dx.begin( ), dofs1.begin( ), std::plus<double> { } );

            if( norm1 <= std::max( norm0 * 1e-16, 3e-7 ) ) break;
            if( ( inewton + 1 ) % 6 == 0 ) std::cout << "\n              ";

        } // inewton

        std::cout << std::endl;

        auto returnMapping = makeJ2Update( domain, constantE, constantNu, sigmaY );

        auto history1J2 = makeHistoryFunction<D>( history0, basis0, basis1, utilities::copyShared( dofs0 ),
            utilities::copyShared( dofs1 ), kinematics, returnMapping );

        auto weight = [=]( std::array<double, 3> xyz ){ return 1.0; }; 
        auto history1CP = std::make_shared<GaussPointInterpolation<3>>( *history1J2, quadratureGrid1, polynomialDegree + quadratureOffset );
        auto history1L2 = std::shared_ptr<BasisInterpolation<3>> { };
        
        if( projectionType == "L2" )
        {
            auto projected = l2projectMechanicalHistory<D>( *basis1, *history1J2, quadrature, determiner, projectionSolver, weight );

            history1L2 = std::make_shared<BasisInterpolation<3>>( basis1, projected );
        }

        auto analyticalStress = makeAnalyticalStress( istep, nelastic, nplastic, a, b, c, sigmaY );
        
        std::function analyticalVonMises = [=]( std::array<double, D> xyz )
        {
            auto [S_rr, S_tt] = analyticalStress( xyz );
            return std::abs( S_tt - S_rr );
        };

        auto scaledInner = implicit::sphere<D>( min, ( 1.0 + 1e-4 ) * a );
        auto scaledOuter = implicit::sphere<D>( min, ( 1.0 - 1e-4 ) * b );
        auto scaledDomain = implicit::subtract( scaledOuter, scaledInner );

        auto processors = std::tuple
        {
            makeSolutionProcessor<D>( dofs1, "Displacement" ),
            postprocessPlasicity( *mesh1, *history1J2 ),
            makeFunctionProcessor<D>( domain, "Domain" ),
            makeFunctionProcessor<D>( spatial::extractComponent( analyticalStress, 0 ), "AnalyticalRadialStress" ),
            makeFunctionProcessor<D>( spatial::extractComponent( analyticalStress, 1 ), "AnalyticalTangentialStress" ),
            makeFunctionProcessor<D>( analyticalVonMises, "AnalyticalVonMisesStress" ),
            makeFunctionProcessor<D>( levelFunction, "LevelFunction" ),
        };

        //auto resolution = array::makeSizes<D>( polynomialDegree == 1 ? size_t { 1 } : polynomialDegree + 3 );
        auto resolution = array::makeSizes<D>( polynomialDegree + 3 );
        auto postmesh = cellmesh::domain( scaledDomain, resolution );

        writeOutput( *basis1, postmesh, processors, PVtuOutput { stepfilebase } );

        evaluateLine1( basis1, history1CP, analyticalStress );
        evaluateLine2( basis1, history1J2, analyticalStress );

        // Update state
        basis0 = std::move( basis1 );
        mesh0 = std::move( mesh1 );
        history0 = selectHistory( projectionType, history1J2, history1CP, history1L2 );
        dofs0 = std::move( dofs1 );

    } // istep
}

int main( )
{
    run( 0, "CP" );
    run( 1, "CP" );
    run( 0, "L2" );
    run( 1, "L2" );
    //run( 1, "J2" );
}
