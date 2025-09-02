// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_INTEGRANDTYPES_HPP
#define MLHP_CORE_INTEGRANDTYPES_HPP

#include "mlhp/core/alias.hpp"
#include "mlhp/core/memory.hpp"
#include "mlhp/core/utilities.hpp"

namespace mlhp
{

template<size_t D>
class DomainIntegrand
{
public:

    using Cache = utilities::Cache<DomainIntegrand>;

    // Generic constructor
    using Create = Cache( const AbsBasis<D>& basis );

    using Prepare = void( Cache& cache, 
                          const MeshMapping<D>& mapping,
                          const LocationMap& locationMap );
    
    using Evaluate = void( Cache& cache, const BasisFunctionEvaluation<D>& shapes,
                           AlignedDoubleVectors& targets, double weightDetJ );

    DomainIntegrand( AssemblyTypeVector types_, DiffOrders maxdiff_,
                     const std::function<Create>& create_, 
                     const std::function<Prepare>& prepare_, 
                     const std::function<Evaluate>& evaluate_ ) :
        createCache { create_ }, prepare { prepare_ }, evaluate { evaluate_ },
        types { types_ }, maxdiff { maxdiff_ }
    { }

    std::function<Create> createCache = utilities::returnEmpty<Cache>( );
    std::function<Prepare> prepare = utilities::doNothing( );
    std::function<Evaluate> evaluate = utilities::doNothing( );
    
    AssemblyTypeVector types;
    DiffOrders maxdiff;

    // Construct using simple evaluation function.
    using Evaluate1 = void( const BasisFunctionEvaluation<D>& shapes, 
                            AlignedDoubleVectors& targets, double weightDetJ );
    
    DomainIntegrand( AssemblyTypeVector types_, DiffOrders maxdiff_,
                     const std::function<Evaluate1>& evaluate_ ) :
        types { types_ }, maxdiff { maxdiff_ }
    { 
        evaluate = [=]( Cache&, const BasisFunctionEvaluation<D>& shapes,
                         AlignedDoubleVectors& targets, double weightDetJ )
        { 
            evaluate_( shapes, targets, weightDetJ );
        };
    }

    // Construct evaluator with also location map, element index and temporary storage. 
    using Evaluate2 = void( const BasisFunctionEvaluation<D>& shapes,
                            const LocationMap& locationMap, 
                            AlignedDoubleVectors& targets, 
                            AlignedDoubleVector& tmp,
                            double weightDetJ );

    DomainIntegrand( AssemblyTypeVector types_, DiffOrders maxdiff_,
                     const std::function<Evaluate2>& evaluate_ ) :
        types { types_ }, maxdiff { maxdiff_ }
    { 
        struct SimpleCache
        {
            const LocationMap* locationMap;
            memory::AlignedVector<double> tmp;
        };

        createCache = []( const AbsBasis<D>& ) 
        { 
            return SimpleCache { .locationMap = nullptr, .tmp = { } }; 
        };

        prepare = []( Cache& anyCache, const MeshMapping<D>&, const LocationMap& locationMap )
        {
            auto& cache = utilities::cast<SimpleCache>( anyCache );
            cache.locationMap = &locationMap;
        };

        evaluate = [=]( Cache& anyCache, const BasisFunctionEvaluation<D>& shapes,
                         AlignedDoubleVectors& targets, double weightDetJ )
        { 
            auto& cache = utilities::cast<SimpleCache>( anyCache );

            evaluate_( shapes, *cache.locationMap, targets, cache.tmp, weightDetJ );
        };
    }
};

template<size_t D>
class BasisProjectionIntegrand
{
public:
    using Evaluate = std::function<void( const LocationMap& locationMap0,
                                         const LocationMap& locationMap1,
                                         const BasisFunctionEvaluation<D>& shapes0,
                                         const BasisFunctionEvaluation<D>& shapes1,
                                         AlignedDoubleVectors& targets,
                                         double weightDetJ )>;

    BasisProjectionIntegrand( AssemblyTypeVector types,
                              DiffOrders diffOrder,
                              const Evaluate& evaluate ) :
        types_( types ), diffOrder_( diffOrder ), evaluate_( evaluate )
    { }

    void evaluate( const LocationMap& locationMap0,
                   const LocationMap& locationMap1,
                   const BasisFunctionEvaluation<D>& shapes0,
                   const BasisFunctionEvaluation<D>& shapes1,
                   AlignedDoubleVectors& targets,
                   double weightDetJ ) const
    {
        return evaluate_( locationMap0, locationMap1, 
            shapes0, shapes1, targets, weightDetJ );
    }

    DiffOrders diffOrder( ) const { return diffOrder_; }
    AssemblyTypeVector types( ) const { return types_; }

private:
    AssemblyTypeVector types_;
    DiffOrders diffOrder_;
    Evaluate evaluate_;
};

template<size_t D>
class SurfaceIntegrand
{
public:
    using Cache = utilities::Cache<SurfaceIntegrand>;

    struct DefaultCache
    {
        memory::AlignedVector<double> doubleVector;
    }; 

    using Create = Cache( const AbsBasis<D>& basis );

    using Prepare = void( Cache& cache,
                          const MeshMapping<D>& mapping,
                          const LocationMap& locationMap );

    using Evaluate = void( Cache& cache, 
                           const BasisFunctionEvaluation<D>& shapes,
                           const LocationMap& locationMap,
                           std::array<double, D> normal,
                           AlignedDoubleVectors& targets,
                           double weightDetJ );

    std::function<Create> createCache = utilities::returnValue( DefaultCache { } );
    std::function<Prepare> prepare = utilities::doNothing( );
    std::function<Evaluate> evaluate = utilities::doNothing( );

    AssemblyTypeVector types = { };
    DiffOrders maxdiff = DiffOrders::NoShapes;
};

template<size_t D> inline
auto makeSurfaceIntegrand( const AssemblyTypeVector& types,
                           DiffOrders maxdiff,
                           std::function<void( typename SurfaceIntegrand<D>::Cache&,
                                               const BasisFunctionEvaluation<D>& shapes,
                                               const LocationMap& locationMap,
                                               std::array<double, D> normal,
                                               AlignedDoubleVectors& targets,
                                               double weightDetJ )> evaluate )
{
    return SurfaceIntegrand<D>{ .evaluate = std::move( evaluate ), .types = types, .maxdiff = maxdiff };
}

} // mlhp

#endif // MLHP_CORE_INTEGRANDTYPES_HPP
