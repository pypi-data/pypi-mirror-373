// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/algorithm.hpp"
#include "mlhp/core/basisevaluation.hpp"
#include "mlhp/core/postprocessing.hpp"
#include "mlhp/core/mesh.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/utilities.hpp"
#include "mlhp/core/partitioning.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/triangulation.hpp"
#include "mlhp/core/postprocessing_impl.hpp"
#include "mlhp/core/integrands.hpp"

#include <functional>
#include <vector>
#include <filesystem>

namespace mlhp
{

#define MLHP_CHECK_SIZES(size1, size2, str1, str2, loc)                                                       \
    MLHP_CHECK( size1 == size2,                                                                               \
                std::string { str1 } + " size (" + std::to_string( size1 ) + ") is inconsistent with " +      \
                std::string { str2 } + " (" + std::to_string( size2 ) + ") in " + std::string { loc } + "." )

template<size_t D>
ElementProcessor<D> makeSolutionProcessor( memory::vptr<const std::vector<double>> solution,
                                           const std::string& name )
{
    auto evaluate = [=]( auto& shapes, auto&, auto &locationMap, auto target )
    {
        evaluateSolutions( shapes, locationMap, *solution, target );
    };

    auto ndof = solution->size( );
    auto diff = DiffOrders::Shapes;

    auto outputData = [=]( auto& basis ) -> Output
    {
        MLHP_CHECK_SIZES( ndof, basis.ndof( ), "Dof vector", "the number of basis dofs", "solution processor" );

        return { .name = name, .type = Output::Type::PointData, .ncomponents = basis.nfields( ) };
    };

    return detail::makeElementPointProcessor<D>( std::move( evaluate ), std::move( outputData ), diff );
}

namespace
{

template<size_t D>
auto makeStressStrainProcessor( memory::vptr<const std::vector<double>> solution, 
                                auto&& kinematics, auto&& constitutive, auto&& name, 
                                size_t nresults, auto&& function )
{
    struct ThisCache
    {
        const LocationMap* locationMap;

        memory::AlignedVector<double> tmp;

        typename KinematicEquation<D>::AnyCache kinematicsCache;
        typename ConstitutiveEquation<D>::AnyCache constitutiveCache;
    };

    auto ndof = solution->size( );

    auto outputData = [=] ( auto& basis ) -> OutputVector
    {
        MLHP_CHECK_SIZES( ndof, basis.ndof( ), "Dof vector", "the number of basis dofs", "von Mises processor" );

        return { Output { .name = name, .type = Output::Type::PointData, .ncomponents = nresults } };
    };

    auto initialize = [=]( auto& basis )
    {
        auto cache = ThisCache { };

        cache.kinematicsCache = kinematics->create( basis );
        cache.constitutiveCache = constitutive->create( basis, *kinematics );

        return typename ElementProcessor<D>::Cache { std::move( cache ) };
    };
    
    auto evaluateCell = [=]( auto& anyCache, auto, auto& locationMap, auto& mapping )
    {
        auto& cache = utilities::cast<ThisCache>( anyCache );

        cache.locationMap = &locationMap;

        constitutive->prepare( cache.constitutiveCache, mapping, locationMap );
    };

    auto evaluatePoint = [=]( auto& anyCache, auto targets, const auto& shapes )
    {
        auto& cache = utilities::cast<ThisCache>( anyCache );

        auto ncomponents = constitutive->ncomponents;

        cache.tmp.resize( 2 * ncomponents );

        std::fill( cache.tmp.begin( ), cache.tmp.end( ), 0.0 );

        auto gradient = std::array<double, D * D> { };
        auto strain = std::span<double> ( cache.tmp.begin( ), ncomponents );
        auto stress = std::span<double>( strain.data( ) + strain.size( ), ncomponents );

        evaluateSolutions( shapes, *cache.locationMap, *solution, gradient, 1 );

        kinematics->evaluate( cache.kinematicsCache, shapes, gradient, 
            std::span { strain }, std::span<double> { } );

        constitutive->evaluate( cache.constitutiveCache, shapes, std::span { strain }, 
            std::span { stress }, std::span<double> { } );
        
        function( strain, stress, targets[0] );
    };

    return ElementProcessor<D>
    { 
        .outputData = std::move( outputData ), 
        .initialize = std::move( initialize ),
        .evaluateCell = std::move( evaluateCell ),
        .evaluatePoint = std::move( evaluatePoint ),
        .diffOrder = DiffOrders::FirstDerivatives
    };
}

template<size_t D>
auto makeStressStrainProcessor( std::array<std::span<const double>, D>& gradientDofs,
                                auto&& kinematics, auto&& constitutive,
                                auto&& name, size_t nresults, auto&& function )
{
    struct ThisCache
    {
        const LocationMap* locationMap;

        memory::AlignedVector<double> tmp;

        typename KinematicEquation<D>::AnyCache kinematicsCache;
        typename ConstitutiveEquation<D>::AnyCache constitutiveCache;
    };

    auto ndof = gradientDofs[0].size( );

    for( size_t axis = 1; axis < D; ++axis )
    {
        MLHP_CHECK_SIZES( ndof, gradientDofs[axis].size( ), "Gradient component (axis = " +
            std::to_string( axis ) + ")", "the first component", "mechanical processor." );
    }

    auto outputData = [=] ( auto& basis ) -> OutputVector
    {
        MLHP_CHECK_SIZES( ndof, basis.ndof( ), "Gradient dof vector", 
            "the number of basis dofs", "mechanical processor" );

        return { Output { .name = name, .type = Output::Type::PointData, .ncomponents = nresults } };
    };

    auto initialize = [=]( auto& basis ) 
    {
        auto cache = ThisCache { };

        checkConsistency( basis, kinematics );
        checkConsistency( kinematics, constitutive );

        cache.kinematicsCache = kinematics->create( basis );
        cache.constitutiveCache = constitutive->create( basis, *kinematics );

        return typename ElementProcessor<D>::Cache { std::move( cache ) };
    };
    
    auto evaluateCell = [=]( auto& anyCache, auto, auto& locationMap, auto& mapping )
    {
        auto& cache = utilities::cast<ThisCache>( anyCache );

        cache.locationMap = &locationMap;

        constitutive->prepare( cache.constitutiveCache, mapping, locationMap );
    };

    auto evaluatePoint = [=]( auto& anyCache, auto targets, const auto& shapes )
    {
        auto& cache = utilities::cast<ThisCache>( anyCache );

        auto ncomponents = constitutive->ncomponents;

        cache.tmp.resize( 2 * ncomponents );

        std::fill( cache.tmp.begin( ), cache.tmp.end( ), 0.0 );

        auto gradient = std::array<double, D * D> { };
        auto strain = std::span<double> ( cache.tmp.begin( ), ncomponents );
        auto stress = std::span<double>( strain.data( ) + strain.size( ), ncomponents );

        for( size_t axis = 0; axis < D; ++axis )
        {
            auto di = evaluateSolutions<D>( shapes, *cache.locationMap, gradientDofs[axis] );

            for( size_t ifield = 0; ifield < D; ++ifield )
            {
                gradient[ifield * D + axis] = di[ifield];
            }
        }

        kinematics->evaluate( cache.kinematicsCache, shapes, gradient, 
            std::span { strain }, std::span<double> { } );

        constitutive->evaluate( cache.constitutiveCache, shapes, 
            std::span { strain }, std::span { stress }, std::span<double> { } );
        
        function( strain, stress, targets[0] );
    };

    return ElementProcessor<D>
    { 
        .outputData = std::move( outputData ), 
        .initialize = std::move( initialize ),
        .evaluateCell = std::move( evaluateCell ),
        .evaluatePoint = std::move( evaluatePoint ),
        .diffOrder = DiffOrders::Shapes
    };
}

template<size_t D>
auto evaluateJ2( const auto& tensorSpan ) -> double
{
    constexpr size_t ncomponents = ( D * ( D + 1 ) ) / 2;

    MLHP_CHECK( tensorSpan.size( ) == ncomponents, "Inconsistent number of components." );

    auto tensor = std::array<double, ncomponents> { };

    std::copy( tensorSpan.begin( ), tensorSpan.end( ), tensor.begin( ) );

    if constexpr ( D == 1 ) 
    {
        return tensor[0];
    }
    else if constexpr ( D == 2 )
    {
        auto [S11, S22, S12] = tensor;

        return std::sqrt( S11 * S11 - S11 * S22 +
            S22 * S22 + 3 * S12 * S12 );
    }
    else if constexpr ( D == 3 )
    {
        auto [S11, S22, S33, S12, S23, S13] = tensor;

        auto D1 = ( S11 - S22 ) * ( S11 - S22 );
        auto D2 = ( S22 - S33 ) * ( S22 - S33 );
        auto D3 = ( S33 - S11 ) * ( S33 - S11 );
        auto S = S12 * S12 + S23 * S23 + S13 * S13;

        return std::sqrt( 0.5 * ( D1 + D2 + D3 ) + 3.0 * S );
    }
    else
    {
        MLHP_NOT_IMPLEMENTED;
    }
}

} // namespace

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeVonMisesProcessor( memory::vptr<const std::vector<double>> solution,
                                           memory::vptr<const KinematicEquation<D>> kinematics,
                                           memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                           const std::string& name )
{
    auto evaluate = []( auto&&, auto&& stress, auto&& target )
    {
        target[0] = evaluateJ2<D>( stress );
    };

    return makeStressStrainProcessor<D>( solution, kinematics, constitutive, name, 1, evaluate );
}

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeStressProcessor( memory::vptr<const std::vector<double>> solution,
                                         memory::vptr<const KinematicEquation<D>> kinematics,
                                         memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                         const std::string& name )
{
    auto ncomponents = constitutive->ncomponents;

    auto evaluate = [=]( auto&&, auto&& stress, auto&& target )
    {
        MLHP_CHECK_DBG( stress.size( ) == ncomponents, "Inconsistent number of stress components." );

        std::copy( stress.begin( ), stress.end( ), target.begin( ) );
    };

    return makeStressStrainProcessor<D>( solution, kinematics, constitutive, name, ncomponents, evaluate );
}

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeStrainProcessor( memory::vptr<const std::vector<double>> solution,
                                         memory::vptr<const KinematicEquation<D>> kinematics,
                                         memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                         const std::string& name )
{
    auto ncomponents = constitutive->ncomponents;

    auto evaluate = [=]( auto&& strain, auto&&, auto&& target )
    {
        MLHP_CHECK_DBG( strain.size( ) == ncomponents, "Inconsistent number of strain components." );

        std::copy( strain.begin( ), strain.end( ), target.begin( ) );
    };

    return makeStressStrainProcessor<D>( solution, kinematics, constitutive, name, ncomponents, evaluate );
}

template<size_t D>
ElementProcessor<D> makeStrainEnergyProcessor( memory::vptr<const std::vector<double>> solution,
                                               memory::vptr<const KinematicEquation<D>> kinematics,
                                               memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                               const std::string& name )
{
    auto evaluate = []( auto&& strain, auto&& stress, auto&& target )
    {
        target[0] = 0.5 * spatial::dot( strain, stress );
    };

    return makeStressStrainProcessor<D>( solution, kinematics, constitutive, name, 1, evaluate );
}

template<size_t D>
ElementProcessor<D> makeStressProcessor( std::array<std::span<const double>, D> gradient,
                                         memory::vptr<const KinematicEquation<D>> kinematics,
                                         memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                         const std::string& name )
{
    auto evaluate = []( auto&&, auto&& stress, auto&& target )
    {
        std::copy( stress.begin( ), stress.end( ), target.begin( ) );
    };

    return makeStressStrainProcessor<D>( gradient, kinematics, 
        constitutive, name, ( D * ( D + 1 ) ) / 2, evaluate );
}

template<size_t D>
ElementProcessor<D> makeVonMisesProcessor( std::array<std::span<const double>, D> gradient,
                                           memory::vptr<const KinematicEquation<D>> kinematics,
                                           memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                           const std::string& name )
{
    auto evaluate = []( auto&&, auto&& stress, auto&& target )
    {
        target[0] = evaluateJ2<D>( stress );
    };

    return makeStressStrainProcessor<D>( gradient, kinematics, constitutive, name, 1, evaluate );
}

template<size_t D>
ElementProcessor<D> makeStrainProcessor( std::array<std::span<const double>, D> gradient,
                                         memory::vptr<const KinematicEquation<D>> kinematics,
                                         memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                         const std::string& name )
{
    auto evaluate = []( auto&& strain, auto&&, auto&& target )
    {
        std::copy( strain.begin( ), strain.end( ), target.begin( ) );
    };

    return makeStressStrainProcessor<D>( gradient, kinematics, 
        constitutive, name, ( D * ( D + 1 ) ) / 2, evaluate );
}

template<size_t D>
ElementProcessor<D> makeStrainEnergyProcessor( std::array<std::span<const double>, D> gradient,
                                               memory::vptr<const KinematicEquation<D>> kinematics,
                                               memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                               const std::string& name )
{
    auto evaluate = []( auto&& strain, auto&& stress, auto&& target )
    {
        target[0] = 0.5 * spatial::dot( strain, stress );
    };

    return makeStressStrainProcessor<D>( gradient, kinematics, constitutive, name, 1, evaluate );
}

template<size_t D>
ElementProcessor<D> makeShapeFunctionProcessor( const DofIndexVector& indices,
                                                size_t diffOrder,
                                                size_t diffComponent,
                                                const std::string& name )
{
    auto nfunctions = indices.size( );
    auto diff = static_cast<DiffOrders>( diffOrder );

    auto evaluate = [=]( auto& shapes, auto&, auto &locationMap, auto target )
    {
        MLHP_CHECK( diffOrder <= shapes.maxdifforder( ), "Invalid diff order." );
        MLHP_CHECK( diffComponent < shapes.ncomponents( diffOrder ), "Invalid number of components.");

        for( size_t ifunction = 0; ifunction < nfunctions; ++ifunction )
        {
            auto result = std::find( locationMap.begin( ), locationMap.end( ), indices[ifunction] );

            if( result != locationMap.end( ) )
            {
                auto localIndex = static_cast<size_t>( std::distance( locationMap.begin( ), result ) );
                
                for( size_t ifield = 0; ifield < shapes.nfields( ); ++ifield )
                {
                    auto ndoffield = shapes.ndof( ifield );

                    if( localIndex < ndoffield )
                    {
                        target[ifunction] = *( shapes.get( ifield, diffOrder ) +
                            diffComponent * shapes.ndofpadded( ifield ) + localIndex );

                        break;
                    }

                    localIndex -= ndoffield;
                }
            }
        }
    };

    auto outputData = [=]( const AbsBasis<D>& basis ) -> Output
    {
        for( size_t i = 0; i < indices.size( ); ++i )
        {
            MLHP_CHECK( indices[i] < basis.ndof( ), "Invalid dof index " + std::to_string( i ) + " for basis "
                "with " + std::to_string( static_cast<std::uint64_t>( basis.ndof( ) ) ) + " number of dofs." );
        }

        return { .name = name, 
                 .type = Output::Type::PointData, 
                 .ncomponents = nfunctions };
    };

    return detail::makeElementPointProcessor<D>( std::move( evaluate ), std::move( outputData ), diff );
}

template<size_t D> MLHP_EXPORT
CellProcessor<D> makeRefinementLevelProcessor( const AbsHierarchicalGrid<D>& grid,
                                               const std::string& name )
{
    auto evaluate = [=, &grid]( auto cellIndex, auto&, auto result ) 
    { 
        result[0] = grid.refinementLevel( grid.fullIndex( cellIndex ) ); 
    };
        
    auto outputData = [=]( const AbsMesh<D>& ) { return std::pair { name, size_t { 1 } }; };

    return detail::makeCellCellProcessor<D>( std::move( evaluate ), std::move( outputData ) );
}

template<size_t D> 
CellProcessor<D> makeCellDataProcessor( memory::vptr<const std::vector<double>> data,
                                        const std::string& name )
{
    auto evaluate = [=]( auto cellIndex, auto&, auto result ) 
    { 
        result[0] = ( *data )[cellIndex]; 
    };
    
    auto ncells = data->size( );

    auto outputData = [=]( const AbsMesh<D>& mesh )
    {
        MLHP_CHECK( mesh.ncells( ) == ncells, "Inconsistent cell data vector size "
            "in cell data processor (" + std::to_string( std::uint64_t { mesh.ncells( ) } ) + 
            " mesh cells vs. " + std::to_string( ncells )  + " data values)." );

        return std::pair { name, size_t { 1 } };
    };

    return detail::makeCellCellProcessor<D>( std::move( evaluate ), std::move( outputData ) );
}

template<size_t D>
CellProcessor<D> makeKdTreeInfoProcessor( )
{
    auto treePtr = std::make_shared<const KdTree<D>*>( nullptr );

    auto evaluate = [=]( auto&, auto targets, auto cellIndex, auto& )
    { 
        auto& tree = **treePtr;
        auto fullIndex = tree.fullIndex( cellIndex );
        auto depth = 0.0;

        for( auto i = fullIndex; i != NoCell; i = tree.parent( i ) )
        {
            depth += 1.0;
        }

        targets[0][0] = tree.stateFull( fullIndex );
        targets[1][0] = static_cast<double>( tree.itemsFull( fullIndex ).size( ) );
        targets[2][0] = depth;
        targets[3][0] = static_cast<double>( cellIndex );
    };

    auto output = [=]( auto& mesh ) -> OutputVector
    {
        *treePtr = dynamic_cast<const KdTree<D>*>( &mesh );

        MLHP_CHECK( ( *treePtr ) != nullptr, "Dynamic cast failed. KdTree info "
            "processor must be used with an instance of KdTree<D>." );

        return 
        { 
            Output { .name = "CutState", .type = Output::Type::CellData, .ncomponents = size_t { 1 } },
            Output { .name = "ItemCount", .type = Output::Type::CellData, .ncomponents = size_t { 1 } },
            Output { .name = "TreeDepth", .type = Output::Type::CellData, .ncomponents = size_t { 1 } },
            Output { .name = "LeafIndex", .type = Output::Type::CellData, .ncomponents = size_t { 1 } }
        };
    };

    return CellProcessor<D> { .outputData = output, .evaluateCell = std::move( evaluate ) };
}

namespace 
{
 
template<typename Processor> 
Processor mergeProcessors( std::vector<Processor>&& processors )
{
    auto nprocessors = processors.size( );

    if( nprocessors == 1 )
    {
        return processors.front( );
    }
    
    auto sharedProcessors = std::make_shared<std::vector<Processor>>( std::move( processors ) );
    auto mergedProcessor = Processor { };

    if( nprocessors > 0 )
    {
        mergedProcessor.outputData = [=]( auto& mesh )
        {
            auto merged = std::vector<Output>{ };

            for( size_t iprocessor = 0; iprocessor < nprocessors; ++iprocessor )
            {
                auto outputs = sharedProcessors->at( iprocessor ).outputData( mesh );

                merged.insert( merged.end( ), outputs.begin( ), outputs.end( ) );
            }

            return merged;
        };

        struct Cache
        {
            std::vector<OutputVector> outputs;
            std::vector<typename Processor::Cache> caches;
        };

        mergedProcessor.initialize = [=]( auto& mesh ) -> typename Processor::Cache
        { 
            auto cache = Cache { .outputs = std::vector<OutputVector>( nprocessors ), 
                                 .caches = std::vector<typename Processor::Cache>( nprocessors ) };

            for( size_t iprocessor = 0; iprocessor < nprocessors; ++iprocessor )
            {
                cache.outputs[iprocessor] = sharedProcessors->at( iprocessor ).outputData( mesh );
                cache.caches[iprocessor] = sharedProcessors->at( iprocessor ).initialize( mesh );
            }

            return cache;
        };

        auto makeEvaluate = [&]( auto&& processorEvaluate )
        {
            return [=]<typename... Args>( auto& anyCache, auto targets, Args&&... args )
            {
                auto& cache = utilities::cast<Cache>( anyCache );
                auto offset = size_t { 0 };

                for( size_t iprocessor = 0; iprocessor < nprocessors; ++iprocessor )
                {
                    auto& processor = sharedProcessors->at( iprocessor );
                    auto noutputs = cache.outputs[iprocessor].size( );
                    auto processorTargets = targets.subspan( offset, noutputs );

                    processorEvaluate( processor )( cache.caches[iprocessor], 
                        processorTargets, std::forward<Args>( args )... );
            
                    offset += noutputs;
                }
            };
        };

        mergedProcessor.evaluateCell = makeEvaluate( []( auto& obj ) -> auto& { return obj.evaluateCell; } );
        mergedProcessor.evaluatePoint = makeEvaluate( []( auto& obj ) -> auto& { return obj.evaluatePoint; } );
    }

    return mergedProcessor;
}

} // namespace 

template<size_t D> 
CellProcessor<D> mergeProcessors( std::vector<CellProcessor<D>>&& processors )
{
    return mergeProcessors<CellProcessor<D>>( std::move( processors ) );
}

template<size_t D>
ElementProcessor<D> mergeProcessors( std::vector<ElementProcessor<D>>&& processors )
{
    auto maxdiff = -1;

    for( auto& processor : processors )
    {
        maxdiff = std::max( maxdiff, static_cast<int>( processor.diffOrder ) );
    }

    auto processor = mergeProcessors<ElementProcessor<D>>( std::move( processors ) );

    processor.diffOrder = static_cast<DiffOrders>( maxdiff );

    return processor;
}


template<size_t D>
ElementProcessor<D> convertToElementProcessor( CellProcessor<D>&& processor_ )
{
    auto processor = std::make_shared<CellProcessor<D>>( std::move( processor_ ) );

    return ElementProcessor<D>
    {
        .outputData = [=]( const AbsBasis<D>& basis )
        {
            return processor->outputData( basis.mesh( ) );
        },
        .initialize = [=]( const AbsBasis<D>& basis ) -> typename ElementProcessor<D>::Cache
        {
            return processor->initialize( basis.mesh( ) );
        },
        .evaluateCell = [=]( auto& anyCache, auto targets, auto&, auto& mapping )
        { 
            auto& cache = utilities::cast<typename CellProcessor<D>::Cache>( anyCache );

            processor->evaluateCell( cache, targets, mapping.icell, mapping );
        },
        .evaluatePoint = [=]( auto& anyCache, auto targets, auto& shapes )
        { 
            auto& cache = utilities::cast<typename CellProcessor<D>::Cache>( anyCache );

            processor->evaluatePoint( cache, targets, shapes.rst( ), shapes.xyz( ) );
        },
        .diffOrder = DiffOrders::NoShapes
    };
}

template<size_t D>
CellProcessor<D> convertToCellProcessor( ElementProcessor<D>&& processor_,
                                         const AbsBasis<D>& basis )
{
    using ElementProcessorCache = typename ElementProcessor<D>::Cache;

    struct Cache
    {
        ElementProcessorCache pcache;
        BasisEvaluationCache<D> bcache;
        std::vector<DofIndex> locationMap;
        BasisFunctionEvaluation<D> shapes;
    };

    auto processor = std::make_shared<ElementProcessor<D>>( std::move( processor_ ) );

    return CellProcessor<D>
    {
        .outputData = [=, &basis]( const AbsMesh<D>& mesh )
        {
            MLHP_CHECK( &basis.mesh( ) == &mesh, "Inconsistent mesh addresses." );

            return processor->outputData( basis );
        },
        .initialize = [=, &basis]( auto& ) -> typename CellProcessor<D>::Cache
        {
            auto cache = Cache { };
            
            cache.pcache = processor->initialize( basis );
            cache.bcache = basis.createEvaluationCache( );
            
            return { std::move( cache ) };
        },
        .evaluateCell = [=, &basis]( auto& anyCache, auto targets, auto cellIndex, auto& )
        {
            auto& cache = utilities::cast<Cache>( anyCache );
            auto maxdiff = std::max( static_cast<int>( processor->diffOrder ), 0 );

            utilities::resize0( cache.locationMap );

            basis.locationMap( cellIndex, cache.locationMap );
            basis.prepareEvaluation( cellIndex, static_cast<size_t>( 
                maxdiff ), cache.shapes, cache.bcache );

            processor->evaluateCell( cache.pcache, targets, 
                cache.locationMap, basis.mapping( cache.bcache ) );
        },
        .evaluatePoint = [=, &basis]( auto& anyCache, auto targets, auto rst, auto )
        {
            auto& cache = utilities::cast<Cache>( anyCache );

            basis.evaluateSinglePoint( rst, cache.shapes, cache.bcache );

            processor->evaluatePoint( cache.pcache, targets, cache.shapes );
        },
    };
}


namespace detail
{

template<size_t D>
void createPostprocessingGrid( CoordinateGrid<D>& rst,
                               std::array<size_t, D> resolution )
{
    if( array::minElement( resolution ) == 0 || array::maxElement( resolution ) >= NoValue<size_t> / 2 )
    {
        return;
    }

    for( size_t axis = 0; axis < D; ++axis )
    {
        rst[axis].resize( resolution[axis] + 1 );

        for( size_t iPoint = 0; iPoint < resolution[axis] + 1; ++iPoint )
        {
            rst[axis][iPoint] = ( 2.0 * iPoint ) / resolution[axis] - 1.0;
        }
    }
}

template<size_t D>
void createPostprocessingGrid( CoordinateGrid<D>& rst,
                               CoordinateList<D>& xyz,
                               const auto& mapping,
                               std::array<size_t, D> numberOfCells )
{
    createPostprocessingGrid( rst, numberOfCells );

    auto npoints = array::add<size_t>( numberOfCells, 1 );

    xyz.resize( array::product( npoints ) );

    // Point coordinates
    nd::executeWithIndex( npoints, [&]( std::array<size_t, D> ijk, size_t index )
    {
        xyz[index] = mapping( array::extract( rst, ijk ) );
    } );
}

constexpr bool operator&( PostprocessTopologies a, PostprocessTopologies b )
{
    return static_cast<int>( a ) & static_cast<int>( b );
}

template<size_t D>
void appendPointData( std::vector<double>& points,
                      const CoordinateList<D>& xyz )
{
    for( auto point : xyz )
    {
        std::array<double, 3> paddedPoint { };

        auto end = D <= 3 ? point.end( ) : point.begin( ) + 3;

        std::copy( point.begin( ), end, paddedPoint.begin( ) );

        points.insert( points.end( ), paddedPoint.begin( ), paddedPoint.end( ) );
    }
}

template<size_t D>
void appendVtuPostprocessingGrid( std::array<size_t, D> resolution,
                                  PostprocessTopologies topologies,
                                  std::vector<vtu11::VtkIndexType>& connectivity,
                                  std::vector<vtu11::VtkIndexType>& offsets,
                                  std::vector<vtu11::VtkCellType>& types )
{
    if( array::minElement( resolution ) == 0 || array::maxElement( resolution ) >= NoValue<size_t> / 2 )
    {
        return;
    }

    constexpr auto ordering = vtuOrdering<D>( );

    auto pointOffset = size_t { 0 };
    auto ncells = resolution;
    auto npoints = array::add<size_t>( ncells, 1 );

    static constexpr size_t pointsPerCell = utilities::integerPow( 2, D );

    auto pointStrides = nd::stridesFor( npoints );

    size_t offset = 0;

    if( !offsets.empty( ) )
    {
        offset = static_cast<size_t>( offsets.back( ) );
    }

    auto appendConnectivity = [&]( auto index )
    {
        connectivity.push_back( static_cast<vtu11::VtkIndexType>( index + pointOffset ) );
    };

    auto appendOffsets = [&]( auto index )
    {
        offsets.push_back( static_cast<vtu11::VtkIndexType>( index ) );
    };

    // 2^D corners if enabled
    if( topologies & PostprocessTopologies::Corners )
    {
        nd::execute( array::makeSizes<D>( 2 ), [&]( std::array<size_t, D> corner )
        {
            auto index = array::multiply( corner, ncells );

            appendConnectivity( nd::linearIndex( pointStrides, index ) );
            appendOffsets( ++offset );
            types.push_back( cubicTypes[0] );
        } );
    }

    // edges in 1D, faces in 2D, volumes in 3D
    if( ( D == 1 && topologies & PostprocessTopologies::Edges   ) ||
        ( D == 2 && topologies & PostprocessTopologies::Faces   ) ||
        ( D == 3 && topologies & PostprocessTopologies::Volumes ) )
    {
        nd::execute( ncells, [&]( std::array<size_t, D> ijk )
        {
            std::array<size_t, pointsPerCell> cell;

            nd::executeWithIndex( array::makeSizes<D>( 2 ), [&]( std::array<size_t, D> corner, size_t index2 )
            {
                auto sum = array::add( ijk, corner );

                cell[ordering[index2]] = nd::linearIndex( pointStrides, sum ) + pointOffset;
            } );

            connectivity.insert( connectivity.end( ), cell.begin( ), cell.end( ) );
            appendOffsets( offset + pointsPerCell );
            types.push_back( cubicTypes[D] );

            offset += pointsPerCell;
        } );
    }

    auto size1 = connectivity.size( );

    // edges in 2D
    if constexpr ( D == 2 ) if( topologies & PostprocessTopologies::Edges )
    {
        for( size_t i = 0; i < ncells[1]; ++i )
        {
            appendConnectivity( i + 0 );
            appendConnectivity( i + 1 );
            appendConnectivity( i + 0 + npoints[1] * ncells[0] );
            appendConnectivity( i + 1 + npoints[1] * ncells[0] );
        }

        for( size_t i = 0; i < ncells[0]; ++i )
        {
            appendConnectivity( ( i + 0 ) * npoints[1] );
            appendConnectivity( ( i + 1 ) * npoints[1] );
            appendConnectivity( ( i + 0 ) * npoints[1] + ncells[1] );
            appendConnectivity( ( i + 1 ) * npoints[1] + ncells[1] );
        }
    }

    // edges in 3D
    if constexpr ( D == 3 ) if( topologies & PostprocessTopologies::Edges )
    {
        for( size_t i = 0; i < ncells[2]; ++i )
        {
            appendConnectivity( i + 0 );
            appendConnectivity( i + 1 );
            appendConnectivity( i + 0 + npoints[2] * ncells[1] );
            appendConnectivity( i + 1 + npoints[2] * ncells[1] );
            appendConnectivity( i + 0 + npoints[2] * npoints[1] * ncells[0] );
            appendConnectivity( i + 1 + npoints[2] * npoints[1] * ncells[0] );
            appendConnectivity( i + 0 + npoints[2] * npoints[1] * ncells[0] + npoints[2] * ncells[1] );
            appendConnectivity( i + 1 + npoints[2] * npoints[1] * ncells[0] + npoints[2] * ncells[1] );
        }

        for( size_t i = 0; i < ncells[1]; ++i )
        {
            appendConnectivity( ( i + 0 ) * npoints[2] );
            appendConnectivity( ( i + 1 ) * npoints[2] );
            appendConnectivity( ( i + 0 ) * npoints[2] + ncells[2] );
            appendConnectivity( ( i + 1 ) * npoints[2] + ncells[2] );
            appendConnectivity( ( i + 0 ) * npoints[2] + npoints[2] * npoints[1] * ncells[0] );
            appendConnectivity( ( i + 1 ) * npoints[2] + npoints[2] * npoints[1] * ncells[0] );
            appendConnectivity( ( i + 0 ) * npoints[2] + ncells[2] + npoints[2] * npoints[1] * ncells[0] );
            appendConnectivity( ( i + 1 ) * npoints[2] + ncells[2] + npoints[2] * npoints[1] * ncells[0] );
        }

        for( size_t i = 0; i < ncells[0]; ++i )
        {
            appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] );
            appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] );
            appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + ncells[2] );
            appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + ncells[2] );
            appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + ncells[1] * npoints[2] );
            appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + ncells[1] * npoints[2] );
            appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + ncells[1] * npoints[2] + ncells[2] );
            appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + ncells[1] * npoints[2] + ncells[2] );
        }
    }

    size_t nlines = ( connectivity.size( ) - size1 ) / 2;

    for( size_t i = 0; i < nlines; ++i )
    {
        appendOffsets( offset + 2 * ( i + 1 ) );
        types.push_back( cubicTypes[1] );
    }

    offset += 2 * nlines;

    auto size2 = connectivity.size( );


    if constexpr( D == 3 ) if( topologies & PostprocessTopologies::Faces )
    {
        for( size_t j = 0; j < ncells[1]; ++j )
        {
            for( size_t k = 0; k < ncells[2]; ++k )
            {
                appendConnectivity( ( j + 0 ) * npoints[2] + k + 0 );
                appendConnectivity( ( j + 0 ) * npoints[2] + k + 1 );
                appendConnectivity( ( j + 1 ) * npoints[2] + k + 1 );
                appendConnectivity( ( j + 1 ) * npoints[2] + k + 0 );

                appendConnectivity( ( j + 0 ) * npoints[2] + k + 0 + npoints[2] * npoints[1] * ncells[0] );
                appendConnectivity( ( j + 0 ) * npoints[2] + k + 1 + npoints[2] * npoints[1] * ncells[0] );
                appendConnectivity( ( j + 1 ) * npoints[2] + k + 1 + npoints[2] * npoints[1] * ncells[0] );
                appendConnectivity( ( j + 1 ) * npoints[2] + k + 0 + npoints[2] * npoints[1] * ncells[0] );
            }
        }

        for( size_t i = 0; i < ncells[0]; ++i )
        {
            for( size_t k = 0; k < ncells[2]; ++k )
            {
                appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + k + 0 );
                appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + k + 1 );
                appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + k + 1 );
                appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + k + 0 );

                appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + k + 0 + npoints[2] * ncells[1] );
                appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + k + 1 + npoints[2] * ncells[1] );
                appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + k + 1 + npoints[2] * ncells[1] );
                appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + k + 0 + npoints[2] * ncells[1] );
            }
        }

        for( size_t i = 0; i < ncells[0]; ++i )
        {
            for( size_t j = 0; j < ncells[1]; ++j )
            {
                appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + ( j + 0 ) * npoints[2] );
                appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + ( j + 1 ) * npoints[2] );
                appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + ( j + 1 ) * npoints[2] );
                appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + ( j + 0 ) * npoints[2] );

                appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + ( j + 0 ) * npoints[2] + ncells[2] );
                appendConnectivity( ( i + 0 ) * npoints[2] * npoints[1] + ( j + 1 ) * npoints[2] + ncells[2] );
                appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + ( j + 1 ) * npoints[2] + ncells[2] );
                appendConnectivity( ( i + 1 ) * npoints[2] * npoints[1] + ( j + 0 ) * npoints[2] + ncells[2] );
            }
        }
    }

    size_t nfaces = ( connectivity.size( ) - size2 ) / 4;

    for( size_t i = 0; i < nfaces; ++i )
    {
        appendOffsets( offset + 4 * ( i + 1 ) );
        types.push_back( cubicTypes[2] );
    }

    offset += 4 * nfaces;
}

std::function<void( )> offsetPoints( const std::vector<double>& pointData,
                                     std::vector<vtu11::VtkIndexType>& connectivity )
{
    auto pointOffset = static_cast<vtu11::VtkIndexType>( pointData.size( ) / 3 );
    auto cellBegin = connectivity.size( );

    return [&, pointOffset, cellBegin]( ) noexcept
    {
        for( size_t ipoint = cellBegin; ipoint < connectivity.size( ); ++ipoint )
        {
            connectivity[ipoint] += pointOffset;
        }
    };
}
} // namespace detail

namespace
{

template<size_t D, typename Derived>
struct OutputEvaluator
{
    OutputEvaluator( const OutputVector& outputs_ ) :
        outputs { outputs_ }, data ( outputs_.size( ) ), spans_( outputs_.size( ) )
    { }
    
    void evaluate( CellIndex cellIndex,
                   const CoordinateGrid<D>& rst,
                   CoordinateList<D>& xyzList,
                   size_t ncells,
                   bool isGrid )
    {
        auto derived = static_cast<Derived*>( this );
        auto shape = array::elementSizes( rst );
        auto npoints = isGrid ? array::product( shape ) : rst[0].size( );

        // Resize data arrays
        for( size_t ioutput = 0; ioutput < outputs.size( ); ++ioutput )
        {
            auto ncomponents = outputs[ioutput].ncomponents;
            auto size = data[ioutput].size( );
            auto nvalues = outputs[ioutput].type == Output::Type::PointData ? npoints : ncells;

            auto newsize = size + ncomponents * nvalues; 

            if( newsize > data[ioutput].capacity( ) )
            {
                data[ioutput].reserve( 2 * newsize );
            }

            data[ioutput].resize( newsize, 0.0 );
            spans_[ioutput] = std::span( data[ioutput].data( ) + size, ncomponents );
        }

        xyzList.resize( npoints );

        derived->evaluateCell( cellIndex, spans_, rst, isGrid );

        auto evaluate = [&]( size_t index, auto&& ijk, auto&& rstPoint )
        {
            xyzList[index] = derived->evaluatePoint( rstPoint, spans_, ijk, isGrid );

            // Increment spans by the number of components
            for( size_t ioutput = 0; ioutput < outputs.size( ); ++ioutput )
            {
                if( outputs[ioutput].type == Output::Type::PointData )
                {
                    spans_[ioutput] = std::span( spans_[ioutput].data( ) + 
                        outputs[ioutput].ncomponents, outputs[ioutput].ncomponents );
                }
            }
        };

        if( isGrid )
        {
            nd::executeWithIndex( shape, [&]( std::array<size_t, D> ijk, size_t index )
            { 
                evaluate( index, ijk, array::extract( rst, ijk ) );
            } );
        }
        else
        {
            for( size_t axis = 1; axis < D; ++axis )
            {
                MLHP_CHECK( rst[axis].size( ) == rst[0].size( ), "Inconsistent coordinate vector sizes." );
            }

            for( size_t index = 0; index < rst[0].size( ); ++index )
            {
                auto ijk = array::make<D>( index );

                evaluate( index, ijk, array::extract( rst, ijk ) );
            }
        }

        // Copy cell values to other cells
        for( size_t ioutput = 0; ioutput < outputs.size( ); ++ioutput )
        {
            if( outputs[ioutput].type == Output::Type::CellData )
            {
                for( size_t icell = 1; icell < ncells; ++icell )
                {
                    auto cellspan = std::span { spans_[ioutput].data( ) + icell *
                        outputs[ioutput].ncomponents, outputs[ioutput].ncomponents };

                    std::copy( spans_[ioutput].begin( ), spans_[ioutput].end( ), cellspan.begin( ) );
                }
            }
        }
    }

    std::vector<Output> outputs;
    std::vector<std::vector<double>> data;
    std::vector<std::span<double>> spans_;
};

template<size_t D>
struct CellOutputEvaluator : public OutputEvaluator<D, CellOutputEvaluator<D>>
{
    CellOutputEvaluator( const AbsMesh<D>& absMesh, 
                         const OutputVector& outputs_,
                         const CellProcessor<D>& processor_ ) :
        OutputEvaluator<D, CellOutputEvaluator<D>>( outputs_ ),
        mesh { &absMesh },
        mapping { absMesh.createMapping( ) },
        cache { processor_.initialize( absMesh ) },
        processor { &processor_ }
    { }

    auto& prepareMapping( CellIndex cellIndex )
    {
        mesh->prepareMapping( cellIndex, mapping );

        return mapping;
    }

    void evaluateCell( CellIndex cellIndex, auto& spans, auto&, auto )
    {
        processor->evaluateCell( cache, spans, cellIndex, mapping );
    }

    auto evaluatePoint( auto&& rst, auto&& spans, auto&&, auto&& )
    {
        auto xyz = mapping( rst );

        processor->evaluatePoint( cache, spans, rst, xyz );

        return xyz;
    }

    const AbsMesh<D>* mesh;
    MeshMapping<D> mapping;
    typename CellProcessor<D>::Cache cache;
    const CellProcessor<D>* processor;
};

template<size_t D>
struct BasisOutputEvaluator : public OutputEvaluator<D, BasisOutputEvaluator<D>>
{
    BasisOutputEvaluator( const AbsBasis<D>& basis_,
                          const OutputVector& outputs_,
                          const ElementProcessor<D>& processor_ ) :
        OutputEvaluator<D, BasisOutputEvaluator<D>>( outputs_ ),
        basis { &basis_ }, processor { &processor_ }, mapping { nullptr },
        processorCache { processor_.initialize( basis_ ) },
        basisCache { basis_.createEvaluationCache( ) }
    { }

    auto& prepareMapping( CellIndex elementIndex )
    {
        auto diff = std::max( static_cast<int>( processor->diffOrder ), 0 );

        basis->prepareEvaluation( elementIndex, static_cast<size_t>( diff ), shapes, basisCache );

        mapping = &basis->mapping( basisCache );

        return *mapping;
    }

    void evaluateCell( CellIndex elementIndex, auto& spans, auto& rst, auto isGrid )
    {
        utilities::resize0( locationMap );

        basis->locationMap( elementIndex, locationMap );

        if( isGrid ) basis->prepareGridEvaluation( rst, basisCache );

        processor->evaluateCell( processorCache, spans, locationMap, *mapping );
    }
    
    auto evaluatePoint( auto&& rst, auto&& spans, auto&& ijk, auto&& isGrid )
    {
        auto xyz = mapping->map( rst );

        if( isGrid ) basis->evaluateGridPoint( ijk, shapes, basisCache );
        else basis->evaluateSinglePoint( rst, shapes, basisCache );

        processor->evaluatePoint( processorCache, spans, shapes );

        return xyz;
    }

    const AbsBasis<D>* basis;
    const ElementProcessor<D>* processor;
    const MeshMapping<D>* mapping;
    typename ElementProcessor<D>::Cache processorCache;
    BasisEvaluationCache<D> basisCache;
    BasisFunctionEvaluation<D> shapes;
    LocationMap locationMap;
};

template<size_t D>
void writeOutput( const CellMeshCreator<D>& meshCreator,
                  const std::vector<Output>& outputs,
                  const MeshWriter& writer,
                  CellIndex ncells,
                  auto&& createEvaluator )
{
    static_assert( D <= 3 );

    auto maxpartitions = std::min( writer.maxpartitions, 5 * parallel::getMaxNumberOfThreads( ) );
    auto partitionData = utilities::divideIntoChunks( ncells, static_cast<CellIndex>( maxpartitions ) );
    auto writerData = writer.initialize( partitionData[0], outputs );

    #pragma omp parallel 
    {
        auto partition = OutputMeshPartition { };
        auto meshCreatorCache = std::any { };
        auto rstVectors = CoordinateGrid<D> { };
        auto xyzList = CoordinateList<D> { };

        #pragma omp for schedule( dynamic )
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( partitionData[0] ); ++ii )
        {
            partition.index = static_cast<CellIndex>( ii );

            utilities::resize0( partition.points, partition.connectivity, 
                partition.offsets, partition.types, xyzList );

            auto evaluator = createEvaluator( );
            auto [chunkBegin, chunkEnd] = utilities::chunkRange( partition.index, partitionData );

            for( auto icell = chunkBegin; icell < chunkEnd; ++icell )
            {
                utilities::resize0( rstVectors );

                auto& mapping = evaluator.prepareMapping( icell );

                auto offset = detail::offsetPoints( partition.points, partition.connectivity );
                auto begin = partition.offsets.size( );

                auto isGrid = meshCreator( mapping, rstVectors, partition.connectivity, 
                    partition.offsets, partition.types, meshCreatorCache );

                if( partition.offsets.size( ) != begin )
                {
                    evaluator.evaluate( icell, rstVectors, xyzList, partition.offsets.size( ) - begin, isGrid );
            
                    detail::appendPointData( partition.points, xyzList );

                    offset( );
                }
            }

            writer.writePartition( writerData, partition, evaluator.data );
        }
    }

    writer.finalize( writerData );
}

auto convertToVtu11Info( const std::vector<Output>& outputs )
{
    auto dataSetInfo = std::vector<vtu11::DataSetInfo> { };

    for( auto& [name, type, ncomponents] : outputs)
    {
        auto vtu11Type = ( type == Output::Type::PointData ) ? 
            vtu11::DataSetType::PointData : vtu11::DataSetType::CellData;

        dataSetInfo.push_back( { name, vtu11Type, ncomponents } );
    }

    return dataSetInfo;
}

auto createParentDirectoriesIfNeeded( const std::string& path )
{
    if( !path.empty( ) && !std::filesystem::exists( path ) )
    {
        vtu11fs::create_directories( path );
    }
}

} // namespace

DataAccumulator::operator MeshWriter( )
{
    data = std::make_shared<std::vector<std::vector<double>>>( );
    mesh = std::make_shared<OutputMeshPartition>( );
    mesh->index = 0;

    auto allPartitions = mesh;
    auto allData = data;

    MeshWriter writer { .maxpartitions = NoValue<size_t> };

    writer.writePartition = [=]( MeshWriter::Cache&,
                                 const OutputMeshPartition& partition,
                                 const std::vector<std::vector<double>>& partitionData )
    {
        if( partition.points.empty( ) && partition.connectivity.empty( ) )
        {
            return;
        }

        // Append to cached data
        #pragma omp critical
        {
            auto append = []( auto& container, auto& additional, auto offset )
            {
                auto size = container.size( );
                auto diff = additional.size( );

                container.resize( size + diff );

                for( size_t i = 0; i < diff; ++i )
                {
                    using Type = std::decay_t<decltype(container[0])>;
                    
                    container[size + i] = additional[i] + static_cast<Type>( offset );
                }
            };
            
            auto& all = *allPartitions;

            append( all.offsets, partition.offsets, all.connectivity.size( ) );
            append( all.connectivity, partition.connectivity, all.points.size( ) / 3 );
            append( all.points, partition.points, 0.0 );
            append( all.types, partition.types, 0 );

            if( allData->size( ) < partitionData.size( ) )
            {
                allData->resize( partitionData.size( ) );
            }

            for( size_t i = 0; i < allData->size( ); ++i )
            {
                append( allData->at( i ), partitionData[i], 0.0 );
            }
        } // omp critical
    };

    return writer;
}

PVtuOutput::operator MeshWriter( ) const
{
    struct Cache
    {
        std::string path, name, mode;
        std::vector<vtu11::DataSetInfo> dataSetInfo;
    };

    MeshWriter writer { .maxpartitions = maxpartitions };

    writer.initialize = [thisCopy = *this]( auto npartitions, auto& outputs ) -> typename MeshWriter::Cache
    {
        auto cache = Cache { };
        auto path = std::filesystem::path { thisCopy.filename };
        auto extension = path.extension( ) != ".vtu" && path.extension( ) != ".pvtu";

        MLHP_CHECK( !path.stem( ).empty( ), "File name is missing." );

        cache.path = path.parent_path( ).string( );
        cache.name = path.stem( ).string( );
        cache.name += extension ? path.extension( ).string( ) : "";
        cache.mode = thisCopy.mode;
        cache.dataSetInfo = convertToVtu11Info( outputs );

        createParentDirectoriesIfNeeded( cache.path );

        vtu11::writePVtu( cache.path, cache.name, cache.dataSetInfo, npartitions );

        return cache;
    };

    writer.writePartition = []( MeshWriter::Cache& anyCache,
                                const OutputMeshPartition& partition,
                                const std::vector<std::vector<double>>& data )
    {
        auto& cache = utilities::cast<Cache>( anyCache );

        auto mesh = vtu11::Vtu11UnstructuredMesh { partition.points,
        partition.connectivity, partition.offsets, partition.types };

        vtu11::writePartition( cache.path, cache.name, mesh, 
            cache.dataSetInfo, data, partition.index, cache.mode );
    };

    return writer;
}

VtuOutput::operator MeshWriter( ) const
{
    struct Cache
    {
        std::string name, mode;
        std::vector<vtu11::DataSetInfo> dataSetInfo;
        OutputMeshPartition allPartitions;
        std::vector<std::vector<double>> allData;
        MeshWriter accumulator;
    };

    auto writer = MeshWriter { .maxpartitions = NoValue<size_t> };
    auto dataAccumulator = std::make_shared<DataAccumulator>( );

    writer.initialize = [thisCopy = *this]( auto, auto& outputs ) -> typename MeshWriter::Cache
    {
        auto cache = Cache { };
        auto path = std::filesystem::path { thisCopy.filename };
        auto extension = path.extension( ) != ".vtu" && path.extension( ) != ".pvtu";

        MLHP_CHECK( !path.stem( ).empty( ), "File name is missing." );

        cache.name = ( path.parent_path( ) / path.stem( ) ).string();
        cache.name = cache.name + ( extension ? path.extension( ).string( ) : "" ) + ".vtu";
        cache.dataSetInfo = convertToVtu11Info( outputs );
        cache.allData.resize( cache.dataSetInfo.size( ) );
        cache.mode = thisCopy.mode;

        createParentDirectoriesIfNeeded( path.parent_path( ).string( ) );

        return cache;
    };

    writer.writePartition = []( MeshWriter::Cache& anyCache,
                                const OutputMeshPartition& partition,
                                const std::vector<std::vector<double>>& data )
    {
        auto& cache = utilities::cast<Cache>( anyCache );

        // Append to cached data
        #pragma omp critical
        {
            auto append = []( auto& container, auto& additional, auto offset )
            {
                auto size = container.size( );
                auto diff = additional.size( );

                container.resize( size + diff );

                for( size_t i = 0; i < diff; ++i )
                {
                    using Type = std::decay_t<decltype(container[0])>;
                    
                    container[size + i] = additional[i] + static_cast<Type>( offset );
                }
            };
            
            auto& all = cache.allPartitions;

            append( all.offsets, partition.offsets, all.connectivity.size( ) );
            append( all.connectivity, partition.connectivity, all.points.size( ) / 3 );
            append( all.points, partition.points, 0.0 );
            append( all.types, partition.types, 0 );

            for( size_t i = 0; i < cache.allData.size( ); ++i )
            {
                append( cache.allData[i], data[i], 0.0 );
            }
        } // omp critical
    };

    writer.finalize = []( MeshWriter::Cache& anyCache )
    {
        #pragma omp barrier
        auto& cache = utilities::cast<Cache>( anyCache );
        auto& allMesh = cache.allPartitions;

        auto mesh = vtu11::Vtu11UnstructuredMesh { allMesh.points,
            allMesh.connectivity, allMesh.offsets, allMesh.types };

        vtu11::writeVtu( cache.name, mesh, cache.dataSetInfo, 
            cache.allData, cache.mode );
    };

    return writer;
}

template<size_t D>
void writeOutput( const AbsMesh<D>& mesh,
                  const CellMeshCreator<D>& meshCreator,
                  const CellProcessor<D>& processor,
                  const MeshWriter& writer )
{
    auto outputs = processor.outputData( mesh );
    auto evaluator = [&]( ) { return CellOutputEvaluator<D> { mesh, outputs, processor }; };
    
    writeOutput<D>( meshCreator, outputs, writer, mesh.ncells( ), evaluator );
}

template<size_t D>
void writeOutput( const AbsBasis<D>& basis,
                  const CellMeshCreator<D>& meshCreator,
                  const ElementProcessor<D>& processor,
                  const MeshWriter& writer)
{
    auto outputs = processor.outputData( basis );
    auto evaluator = [&]( ) { return BasisOutputEvaluator<D> { basis, outputs, processor }; };

    writeOutput<D>( meshCreator, outputs, writer, basis.nelements( ), evaluator );
}

template<size_t D>
void writeOutput( const AbsBasis<D>& basis,
                  const AbsQuadrature<D>& quadrature,
                  const QuadratureOrderDeterminor<D>& determinor,
                  const std::string& filename )
{
    std::vector<double> points;
    std::vector<vtu11::VtkIndexType> connectivity, offsets;
    std::vector<vtu11::VtkCellType> types;

    auto& mesh = basis.mesh( );
    auto quadratureCache = quadrature.initialize( );
    auto nelements = basis.nelements( );

    CoordinateGrid<D> rst;
    CoordinateList<D> xyz;

    std::vector<double> weights;

    vtu11::VtkIndexType pointIndex = 0;

    auto mapping = mesh.createMapping( );

    for( CellIndex iElement = 0; iElement < nelements; ++iElement )
    {
        mesh.prepareMapping( iElement, mapping );

        size_t numberOfIntegrationCells = quadrature.partition( mapping, quadratureCache );

        auto integrationOrders = determinor( iElement, basis.maxdegrees( iElement ) );

        for( size_t iIntegrationCell = 0; iIntegrationCell < numberOfIntegrationCells; ++iIntegrationCell )
        {
            quadrature.distribute( iIntegrationCell, integrationOrders, rst, xyz, weights, quadratureCache );

            for( size_t iPoint = 0; iPoint < xyz.size( ); ++iPoint )
            {
                for( size_t axis = 0; axis < D; ++axis )
                {
                    points.push_back( xyz[iPoint][axis] );
                }

                for( size_t axis = D; axis < 3; ++axis )
                {
                    points.push_back( 0.0 );
                }

                connectivity.push_back( pointIndex );
                offsets.push_back( pointIndex );
                types.push_back( 1 );

                pointIndex++;
            }

        } // for iIntegrationCell
    } // for iElement

    vtu11::Vtu11UnstructuredMesh vtu11Mesh { points, connectivity, offsets, types };
    vtu11::writeVtu( filename, vtu11Mesh, { }, { } );
}

template<size_t D>
void writeOutput( const MappingRange<D>& mappings,
                  const std::string& filename,
                  std::array<size_t, D> numberOfSubdivisions,
                  PostprocessTopologies topologies )
{
    static_assert( D <= 3 );
    
    std::vector<double> points;
    std::vector<vtu11::VtkIndexType> connectivity, offsets;
    std::vector<vtu11::VtkCellType> types;

    CoordinateGrid<D> rstVectors;
    CoordinateList<D> xyzList;

    vtu11::Vtu11UnstructuredMesh mesh { points, connectivity, offsets, types };

    auto size = mappings.size( );

    for( decltype( size ) i = 0; i < size; ++i )
    {
        auto map = [&]( auto rst ) { return mappings( i, rst ); };

        auto offset = detail::offsetPoints( points, connectivity );

        detail::createPostprocessingGrid( rstVectors, xyzList, map, numberOfSubdivisions );
        detail::appendVtuPostprocessingGrid( numberOfSubdivisions, topologies, connectivity, offsets, types );
        detail::appendPointData( points, xyzList );

        offset( );
    }

    vtu11::writeVtu( filename, mesh, { }, { } );
}

template<size_t G, size_t L>
void writeVtu( const SimplexMesh<G, L>& simplexMesh,
               const std::string& filename,
               std::span<const double> pointData )
{
    auto ncells = simplexMesh.ncells( );

    auto vertices = std::vector<double>( 3 * simplexMesh.vertices.size( ), 0.0 );
    auto connectivity = std::vector<vtu11::VtkIndexType>( ( L + 1 ) * ncells );
    auto offsets = std::vector<vtu11::VtkIndexType>( ncells );
    auto types = std::vector<vtu11::VtkCellType>( ncells, detail::simplexTypes[L] );
    auto pointDataVector = std::vector( pointData.begin( ), pointData.end( ) );

    for( size_t ivertex = 0; ivertex < simplexMesh.vertices.size( ); ++ivertex )
    {
        for( size_t axis = 0; axis < G; ++axis )
        {
            vertices[3 * ivertex + axis] = simplexMesh.vertices[ivertex][axis];
        }
    }

    for( size_t icell = 0; icell < simplexMesh.cells.size( ); ++icell )
    {
        for( size_t ivertex = 0; ivertex < L + 1; ++ivertex )
        {
            connectivity[( L + 1 ) * icell + ivertex] = static_cast<vtu11::VtkIndexType>( simplexMesh.cells[icell][ivertex] );
        }
    }

    std::generate( offsets.begin( ), offsets.end( ), [i = L + 1]( ) mutable 
        { auto tmp = i; i += L + 1; return tmp; } );

    auto info = std::vector<vtu11::DataSetInfo> { };
    auto data = std::vector<vtu11::DataSetData> { };

    if constexpr ( L + 1 == G )
    {
        auto normalData = std::vector<double>( ncells * G );

        for( size_t i = 0; i < ncells; ++i )
        {
            auto normal = simplexMesh.cellNormal( i );

            for( size_t axis = 0; axis < G; ++axis )
            {
                normalData[i * G + axis] = normal[axis];
            }
        }

        info.push_back( vtu11::DataSetInfo { "NormalVector", vtu11::DataSetType::CellData, G } );
        data.push_back( std::move( normalData ) );
    }

    if( auto ncomponents = pointData.size( ) / simplexMesh.nvertices( ) )
    {
        info.push_back( vtu11::DataSetInfo { "PointData", vtu11::DataSetType::PointData, ncomponents } );
        data.push_back( std::move( pointDataVector ) );
    }

    vtu11::Vtu11UnstructuredMesh mesh { vertices, connectivity, offsets, types };

    vtu11::writeVtu( filename, mesh, info, data );
}

#define MLHP_INSTANTIATE_SIMPLEXMESH( G, L )             \
    template MLHP_EXPORT                                 \
    void writeVtu( const SimplexMesh<G, L>& simplexMesh, \
                   const std::string& filename,          \
                   std::span<const double> pointData );  \

// Points
MLHP_INSTANTIATE_SIMPLEXMESH( 1, 0 )

// Line segments
MLHP_INSTANTIATE_SIMPLEXMESH( 1, 1 )
MLHP_INSTANTIATE_SIMPLEXMESH( 2, 1 )
MLHP_INSTANTIATE_SIMPLEXMESH( 3, 1 )

// Triangles
MLHP_INSTANTIATE_SIMPLEXMESH( 2, 2 )
MLHP_INSTANTIATE_SIMPLEXMESH( 3, 2 )

void writeStl( const Triangulation<3>& triangulation,
               const std::string& filename,
               const std::string& solidName )
{
    auto file = std::ofstream { filename };

    MLHP_CHECK( file.is_open( ), "Unable to open .stl file." );

    file << "solid " << solidName << "\n" << std::scientific;

    for( size_t itriangle = 0; itriangle < triangulation.cells.size( ); ++itriangle )
    {
        auto v0 = triangulation.vertices[triangulation.cells[itriangle][0]];
        auto v1 = triangulation.vertices[triangulation.cells[itriangle][1]];
        auto v2 = triangulation.vertices[triangulation.cells[itriangle][2]];

        auto normal = spatial::triangleNormal( v0, v1, v2 );
        
        file << " facet normal " << normal[0] << " " << normal[1] << " " << normal[2] << "\nouter loop\n";
        file << "  vertex " << v0[0] << " " << v0[1] << " " << v0[2] << "\n";
        file << "  vertex " << v1[0] << " " << v1[1] << " " << v1[2] << "\n";
        file << "  vertex " << v2[0] << " " << v2[1] << " " << v2[2] << "\n";
        file << " endloop\nendfacet\n";
    }

    file << "endsolid " << solidName << "\n";

    file.close( );
}

template<size_t D>
void writeVtu( const AbsMesh<D>& mesh, const std::string& filename )
{
    auto topologies = static_cast<PostprocessTopologies>( utilities::binaryPow<size_t>( D ) );
    auto provider = cellmesh::grid<D>( array::makeSizes<D>( 1 ), topologies );
    auto output = VtuOutput { filename };

    writeOutput( mesh, provider, CellProcessor<D> { }, output );
}

template<size_t D>
void writeVtu( std::span<const std::array<double, D>> points,
               const std::string& filename,
               std::span<const double> pointData )
{
    auto coordinates = std::vector<double>( points.size( ) * 3, 0.0 );
    auto connectivity = std::vector<vtu11::VtkIndexType>( points.size( ) );
    auto offsets = std::vector<vtu11::VtkIndexType>( points.size( ) );
    auto types = std::vector<vtu11::VtkCellType>( points.size( ), 1 );
    auto pointDataVector = std::vector( pointData.begin( ), pointData.end( ) );

    for( size_t i = 0; i < points.size( ); ++i )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            coordinates[3 * i + axis] = points[i][axis];
        }

        connectivity[i] = static_cast<vtu11::VtkIndexType>( i );
        offsets[i] = static_cast<vtu11::VtkIndexType>( i ) + 1;
    }

    writeVtu( filename, coordinates, connectivity, offsets, types, pointDataVector );
}

void writeVtu( const std::string& filename,
               const std::vector<double>& points,
               const std::vector<std::int64_t>& connectivity,
               const std::vector<std::int64_t>& offsets,
               const std::vector<std::int8_t>& types,
               const std::vector<double>& pointData )
{
    vtu11::Vtu11UnstructuredMesh mesh { points, connectivity, offsets, types };
        
    if( points.empty( ) )
    {
        return;
    }

    auto ncomponents = pointData.size( ) / ( points.size( ) / 3 );

    if( ncomponents )
    {
        vtu11::writeVtu( filename, mesh, { std::make_tuple( "PointData", vtu11::DataSetType::PointData, ncomponents ) }, { pointData }, "Ascii" );
    }
    else
    {
        vtu11::writeVtu( filename, mesh, { }, { }, "Ascii" );
    }
}

namespace cellmesh
{

namespace
{

template<size_t D>
void simplexMesh( std::array<std::vector<double>, D>& pointData,
                  std::vector<std::int64_t>& connectivity,
                  std::vector<std::int64_t>& offsets,
                  std::vector<std::int8_t>& vtkTypes,
                  std::array<size_t, D> resolution,
                  [[maybe_unused]]PostprocessTopologies topologies )
{
    auto r = array::maxElement( resolution );
    auto ipoint = std::int64_t { 0 };

    nd::executeTriangular<D>( r, [&]( auto ijk )
    { 
        auto simplices = spatial::simplexSubdivisionIndices<D>( );

        for( auto simplex : simplices )
        {
            auto filter = false;

            for( auto flatIndex : simplex )
            {
                auto sum = size_t { 0 };

                for( size_t axis2 = 0; axis2 < D; ++axis2 )
                {
                    auto ii = ijk[axis2] + nd::binaryUnravel( flatIndex, D, axis2 );

                    sum += ii;

                    pointData[axis2].push_back( static_cast<double>( ii ) / r );
                }

                filter = filter || sum > r;

                connectivity.push_back( ipoint );
                ipoint += 1;
            }

            if( filter )
            {
                for( size_t ivertex = 0; ivertex < D + 1; ++ivertex )
                {
                    connectivity.pop_back( );

                    for( size_t axis2 = 0; axis2 < D; ++axis2 )
                    {
                        pointData[axis2].pop_back( );
                    }
                    ipoint -= 1;
                }
            }
            else
            {
                offsets.push_back( static_cast<std::int64_t>( connectivity.size( ) ) );
                vtkTypes.push_back( D == 3 ? 10 : (D == 2 ? 5 : 3) );
            }
        }
    } );
}

} // namespace

template<size_t D> 
CellMeshCreator<D> grid( const ResolutionDeterminor<D>& resolutionDeterminor,
                         PostprocessTopologies topologies )
{
    return [=]( const MeshMapping<D>& mapping,
                std::array<std::vector<double>, D>& pointData,
                std::vector<std::int64_t>& connectivity,
                std::vector<std::int64_t>& offsets,
                std::vector<std::int8_t>& vtkTypes,
                std::any& /* anyCache */ ) -> bool
    {
        auto resolution = resolutionDeterminor( mapping );

        if( mapping.type == map::Type::Simplex )
        {
            simplexMesh( pointData, connectivity, offsets, vtkTypes, resolution, topologies );
            
            //offsets.push_back( connectivity.size() );
            //vtkTypes.push_back( 5 );
            return false;
        }
        else
        {
            detail::createPostprocessingGrid( pointData, resolution );
            detail::appendVtuPostprocessingGrid( resolution, topologies, connectivity, offsets, vtkTypes );
        }

        return true;
    };
}

template<size_t D>
CellMeshCreator<D> grid( std::array<size_t, D> resolution,
                         PostprocessTopologies topologies )
{
    return grid<D>( uniformResolution<D>( resolution ), topologies );
}

template<size_t D>
CellMeshCreator<D> custom( std::vector<OutputMeshPartition>&& partitions )
{
    auto cellIndices = std::vector<CellIndex>( partitions.size( ) );

    std::transform( partitions.begin( ), partitions.end( ), 
        cellIndices.begin( ), []( auto& v ) { return v.index; } );

    auto map = utilities::moveShared( algorithm::invertRepeatedIndices( cellIndices ) );

    return [=]( const MeshMapping<D>& mapping,
                std::array<std::vector<double>, D>& pointData,
                std::vector<std::int64_t>& connectivity,
                std::vector<std::int64_t>& offsets,
                std::vector<std::int8_t>& vtkTypes,
                std::any& /* anyCache */ ) -> bool
    {
        auto& [poffsets, pindices] = *map;

        if( mapping.icell + 1 < poffsets.size( ) )
        {
            auto npartitions = poffsets[mapping.icell + 1] - poffsets[mapping.icell];

            for( size_t ipartition = 0; ipartition < npartitions; ++ipartition )
            {
                auto& partition = partitions[pindices[poffsets[mapping.icell] + ipartition]];

                MLHP_CHECK( !partition.offsets.empty( ) && partition.offsets.back( ) == static_cast<std::int64_t>( 
                    partition.connectivity.size( ) ), "Invalid offsets array in partition." );

                MLHP_CHECK( partition.types.size( ) + 1 == partition.offsets.size( ), 
                    "Invalid types array in partition." )

                auto pointOffset = static_cast<std::int64_t>( pointData.front( ).size( ) );
                auto cellOffset = static_cast<std::int64_t>( connectivity.size( ) );

                for( auto pointId : partition.connectivity )
                {
                    connectivity.push_back( pointId + pointOffset );
                }

                for( auto cellId : partition.offsets )
                {
                    offsets.push_back( cellId + cellOffset );
                }

                vtkTypes.insert( vtkTypes.end( ), partition.types.begin( ), partition.types.end( ) );

                for( size_t i = 0; i < partition.points.size( ) / D; ++i )
                {
                    for( size_t axis = 0; axis < D; ++axis )
                    {
                        pointData[axis].push_back( partition.points[i * D + axis] );
                    }
                }
            }
        }

        return false;
    };
}

namespace 
{

template<size_t D>
void appendMarchingCubesData( const std::vector<vtu11::VtkIndexType>& offsets,
                              const CoordinateList<D>& rstList,
                              std::vector<vtu11::VtkCellType>& types,
                              std::array<std::vector<double>, D>& pointData )
{
    auto begin = types.size( );

    types.resize( offsets.size( ) );

    static constexpr auto typeMap = std::array<vtu11::VtkCellType, 9>
    { 
        // 1  2  3  4                         8
        0, 1, 3, 5, D == 3 ? 10 : 9, 0, 0, 0, 12,
    };

    for( size_t icell = begin; icell < offsets.size( ); ++icell )
    {
        auto index0 = icell == 0 ? 0 : offsets[icell - 1];
        auto index1 = offsets[icell];

        types[icell] = typeMap[static_cast<size_t>( index1 - index0 )];
    }

    auto size = pointData[0].size( );
    
    for( size_t axis = 0; axis < D; ++axis )
    {
        pointData[axis].resize( size + rstList.size( ) );

        for( size_t ipoint = 0; ipoint < rstList.size( ); ++ipoint )
        {
            pointData[axis][size + ipoint] = rstList[ipoint][axis];
        }
    }
}

} // namespace

template<size_t D>
CellMeshCreator<D> domain( const ImplicitFunction<D>& function,
                           const ResolutionDeterminor<D>& determinor,
                           bool coarsen,
                           bool meshBothSides,
                           size_t niterations )
{        
    return [=]( const MeshMapping<D>& mapping,
                std::array<std::vector<double>, D>& pointData,
                std::vector<std::int64_t>& connectivity,
                std::vector<std::int64_t>& offsets,
                std::vector<std::int8_t>& vtkTypes,
                std::any& anyCache ) -> bool
    {        
        using Cache = std::tuple<CoordinateGrid<D>, CoordinateList<D>, std::vector<bool>, std::any>;

        if( !anyCache.has_value( ) )
        {
            anyCache = Cache { };
        }

        auto& [rst, rstList, values, otherCache] = std::any_cast<Cache&>( anyCache );

        auto resolution = determinor( mapping );

        // Evaluate implicit function on grid        
        marching::evaluateGrid( mapping, function, resolution, rst, values );

        auto count = std::accumulate( values.begin( ), values.end( ), size_t { 0 } );

        // Create grid if all are inside or return without doing anything if none are inside
        if( count == values.size( ) || ( meshBothSides && count == 0 ) )
        {
            if( coarsen )
            {
                resolution = array::makeSizes<D>( 1 );

                detail::createPostprocessingGrid( pointData, resolution );
            }
            else
            {
                pointData = rst;
            }
  
            auto topologies = static_cast<PostprocessTopologies>( utilities::binaryPow<int>( D ) );

            detail::appendVtuPostprocessingGrid( resolution, topologies, connectivity, offsets, vtkTypes );

            return true;
        }
        
        if( count == 0 )
        {
            for( size_t axis = 0; axis < D; ++axis )
            {
                pointData[axis].resize( 0 );
            }
        
            return true;
        }

        rstList.resize( 0 );

        cellLocalVolumeRecovery<D, std::int64_t>( mapping, function, values, rst, resolution,
            rstList, connectivity, offsets, meshBothSides, niterations, otherCache );

        appendMarchingCubesData( offsets, rstList, vtkTypes, pointData );

        return false;
    };
}

template<size_t D>
CellMeshCreator<D> domain( const ImplicitFunction<D>& function,
                           std::array<size_t, D> resolution,
                           bool coarsen,
                           bool meshBothSides,
                           size_t niterations )
{
    return domain( function, uniformResolution( resolution ), coarsen, meshBothSides, niterations );
}

namespace
{

template<size_t D>
void deactivateBoundarySides( const MeshMapping<D>& mapping,
                              std::array<size_t, D> resolution,
                              std::vector<MeshCellFace>& neighbours,
                              std::vector<bool>& evaluations )
{
    auto npoints = array::add<size_t, D>( resolution, 1 );

    for( size_t axis = 0; axis < D; ++axis )
    {
        for( size_t side = 0; side < 2; ++side )
        {
            MLHP_CHECK( mapping.mesh->nfaces( mapping.icell ) == 6, "Invalid cell type." );
            
            mapping.mesh->neighbours( mapping.icell, 2 * axis + side, utilities::resize0( neighbours ) );
                
            if( neighbours.empty( ) )
            {
                auto strides = nd::stridesFor( npoints );
            
                nd::execute( array::slice( npoints, axis ), [&]( std::array<size_t, D - 1> ij )
                {
                    auto ijk = array::insert( ij, axis, ( side ? npoints[axis] - 1 : size_t { 0 } ) );
            
                    evaluations[nd::linearIndex( strides, ijk )] = false;
                } );
            }
        }
    }
}

} // namespace

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> boundary( const ImplicitFunction<D>& function,
                             const ResolutionDeterminor<D>& determinor,
                             bool recoverMeshBoundaries,
                             size_t niterations )
{        
    return [=]( const MeshMapping<D>& mapping,
                std::array<std::vector<double>, D>& pointData,
                std::vector<std::int64_t>& connectivity,
                std::vector<std::int64_t>& offsets,
                std::vector<std::int8_t>& vtkTypes,
                std::any& anyCache ) -> bool
    {        
        using Cache = std::tuple<CoordinateGrid<D>, 
                                 CoordinateList<D>, 
                                 std::vector<bool>, 
                                 std::vector<MeshCellFace>, 
                                 std::any>;

        if( !anyCache.has_value( ) )
        {
            anyCache = Cache { };
        }

        auto& [rstGrid, rstList, evaluations, neighbours, otherCache] = std::any_cast<Cache&>( anyCache );

        auto resolution = determinor( mapping );

        marching::evaluateGrid( mapping, function, resolution, rstGrid, evaluations );
   
        if( recoverMeshBoundaries )
        {
            if constexpr ( D > 1 )
            {
                deactivateBoundarySides( mapping, resolution, neighbours, evaluations );
            }
        }

        auto count = std::accumulate( evaluations.begin( ), evaluations.end( ), size_t { 0 } );
        
        if( count == 0 || count == evaluations.size( ) )
        {
            return false;
        }

        rstList.resize( 0 );

        auto before = connectivity.size( );

        cellLocalBoundaryRecovery<D, std::int64_t>( mapping, function, evaluations, 
            rstGrid, resolution, rstList, connectivity, niterations, otherCache );

        auto ncells = ( connectivity.size( ) - before ) / D;
        auto size = offsets.size( );

        offsets.resize( size + ncells );

        for( size_t icell = 0; icell < ncells; ++icell )
        {
            offsets[size + icell] = static_cast<vtu11::VtkIndexType>( before + D * icell + D );
        }

        appendMarchingCubesData( offsets, rstList, vtkTypes, pointData );

        return false;
    };
}

template<size_t D>
CellMeshCreator<D> boundary( const ImplicitFunction<D>& function,
                             std::array<size_t, D> resolution,
                             bool recoverMeshBoundaries,
                             size_t niterations )
{
    return boundary( function, uniformResolution( resolution ), recoverMeshBoundaries, niterations );
}

template<size_t D>
CellMeshCreator<D> localSimplices( memory::vptr<const SimplexMesh<D, D - 1>> simplexMesh,
                                   memory::vptr<const SimplexCellAssociation<D>> celldata )
{
    if constexpr( D == 3 )
    {

    return [=]( const MeshMapping<D>& mapping,
                std::array<std::vector<double>, D>& localCoordinates,
                std::vector<std::int64_t>& connectivity,
                std::vector<std::int64_t>& offsets,
                std::vector<std::int8_t>& vtkTypes,
                std::any& ) -> bool
    { 
        auto begin = celldata->offsets[mapping.icell];
        auto end = celldata->offsets[mapping.icell + 1];

        for( size_t itriangle = begin; itriangle < end; ++itriangle )
        {
            auto [i0, i1, i2] = simplexMesh->cells[itriangle];

            connectivity.push_back( static_cast<std::int64_t>( localCoordinates[0].size( ) + 0 ) );
            connectivity.push_back( static_cast<std::int64_t>( localCoordinates[0].size( ) + 1 ) );
            connectivity.push_back( static_cast<std::int64_t>( localCoordinates[0].size( ) + 2 ) );
            
            for( size_t axis = 0; axis < D; ++axis )
            {
                localCoordinates[axis].push_back( celldata->rst[i0][axis] );
                localCoordinates[axis].push_back( celldata->rst[i1][axis] );
                localCoordinates[axis].push_back( celldata->rst[i2][axis] );
            }

            offsets.push_back( static_cast<int64_t>( connectivity.size( ) ) );
            vtkTypes.push_back( 5 );
        } 

        return false;
    };

    }
    else
    {
        MLHP_NOT_IMPLEMENTED;
    }
}

template<size_t D>
CellMeshCreator<D> quadraturePoints( const AbsQuadrature<D>& quadrature,
                                     const AbsBasis<D>& basis,
                                     const QuadratureOrderDeterminor<D>& determinor )
{
    struct Cache
    {
        QuadratureCache<D> quadratureCache;
        CoordinateGrid<D> rst;
        CoordinateList<D> xyz;
        std::vector<double> weights;
    };

    auto threadLocal = std::make_shared<utilities::ThreadLocalContainer<Cache>>( );
    auto nthreads = parallel::getMaxNumberOfThreads( );

    for( size_t ithread = 0; ithread < nthreads; ++ithread )
    {
        threadLocal->data[ithread].quadratureCache = quadrature.initialize( );
    }

    return [threadLocal, &quadrature, determinor, &basis]( const MeshMapping<D>& mapping,
                                                           std::array<std::vector<double>, D>& localCoordinates,
                                                           std::vector<std::int64_t>& connectivity,
                                                           std::vector<std::int64_t>& offsets,
                                                           std::vector<std::int8_t>& vtkTypes,
                                                           std::any& ) -> bool
    { 
        Cache& cache = threadLocal->get( );

        auto npartitions = quadrature.partition( mapping, cache.quadratureCache );
        auto orders = determinor( mapping.icell, basis.maxdegrees( mapping.icell ) );

        for( size_t ipartition = 0; ipartition < npartitions; ++ipartition )
        {
            utilities::resize0( cache.rst, cache.xyz, cache.weights );

            auto isgrid = quadrature.distribute( ipartition, orders, 
                cache.rst, cache.xyz, cache.weights, cache.quadratureCache );
            auto npoints = localCoordinates[0].size( );

            if( isgrid )
            {
                nd::execute( array::elementSizes( cache.rst ), [&]( std::array<size_t, D> ijk ) 
                { 
                    for( size_t axis = 0; axis < D; ++axis )
                    {
                        localCoordinates[axis].push_back( cache.rst[axis][ijk[axis]] );
                    }
                } );
            }
            else
            {
                for( size_t axis = 0; axis < D; ++axis )
                {
                    localCoordinates[axis].insert( localCoordinates[axis].end( ), 
                        cache.rst[axis].begin( ), cache.rst[axis].end( ) );
                }
            }

            for( size_t ipoint = npoints; ipoint < localCoordinates[0].size( ); ++ipoint )
            {
                connectivity.push_back( static_cast<std::int64_t>( ipoint ) );
            }

            offsets.push_back( static_cast<std::int64_t>( connectivity.size( ) ) );
            vtkTypes.push_back( 2 );
        }

        return false;
    };
}

template<size_t D>
CellMeshCreator<D> quadraturePoints( const AbsQuadratureOnMesh<D>& quadrature,
                                     const AbsBasis<D>& basis )
{
    struct Cache
    {
        CoordinateList<D> rst;
        CoordinateList<D> normals;
        std::vector<double> weights;
        typename AbsQuadratureOnMesh<D>::AnyCache quadratureCache;
    };

    auto threadLocal = std::make_shared<utilities::ThreadLocalContainer<Cache>>( );

    for( auto& cache : threadLocal->data )
    {
        cache.quadratureCache = quadrature.initialize( );
    }

    return [threadLocal, &quadrature, &basis]( const MeshMapping<D>& mapping,
                                               std::array<std::vector<double>, D>& localCoordinates,
                                               std::vector<std::int64_t>& connectivity,
                                               std::vector<std::int64_t>& offsets,
                                               std::vector<std::int8_t>& vtkTypes,
                                               std::any& ) -> bool
    { 
        Cache& cache = threadLocal->get( );

        utilities::resize0( cache.rst, cache.normals, cache.weights );

        quadrature.distribute( mapping, basis.maxdegrees( mapping.icell ), 
            cache.rst, cache.normals, cache.weights, cache.quadratureCache );
            
        for( size_t ipoint = 0; ipoint < cache.rst.size( ); ++ipoint )
        {
            connectivity.push_back( static_cast<std::int64_t>( localCoordinates[0].size( ) ) );

            for( size_t axis = 0; axis < D; ++axis )
            {
                localCoordinates[axis].push_back( cache.rst[ipoint][axis] );
            }
        }

        offsets.push_back( static_cast<std::int64_t>( connectivity.size( ) ) );
        vtkTypes.push_back( 2 );

        return false;
    };
}

} // namespace cellmesh

template<size_t D>
ResolutionDeterminor<D> uniformResolution( std::array<size_t, D> resolution )
{
    return [=]( const MeshMapping<D>& ) noexcept { return resolution; };
}

template<size_t D>
ResolutionDeterminor<D> perLevelResolution( const PerLevelResolution<D>& resolution )
{
    return [=]( const MeshMapping<D>& mapping ) 
    { 
        auto& mesh = dynamic_cast<const AbsHierarchicalGrid<D>&>( *mapping.mesh );

        return resolution( mesh.refinementLevel( mapping.icell ) );
    };
}

template<size_t D> MLHP_EXPORT
ResolutionDeterminor<D> degreeOffsetResolution( const AbsBasis<D>& basis,
                                                size_t offset,
                                                bool exceptLinears )
{
    return [=, &basis]( const MeshMapping<D>& mapping )
    {
        auto degrees = basis.maxdegrees( mapping.icell );

        for( size_t axis = 0; axis < D; ++axis )
        {
            if( !exceptLinears || degrees[axis] > 1 )
            {
                degrees[axis] += offset;
            }
        }

        return degrees;
    };
}

// Instantiate for postprocessing dimensions
#define MLHP_INSTANTIATE_DIM( D )                                                           \
                                                                                            \
    template MLHP_EXPORT                                                                    \
    void writeOutput( const AbsMesh<D>& mesh,                                               \
                      const CellMeshCreator<D>& meshCreator,                                \
                      const CellProcessor<D>& processor,                                    \
                      const MeshWriter& writer );                                           \
                                                                                            \
    template MLHP_EXPORT                                                                    \
    void writeOutput( const AbsBasis<D>& basis,                                             \
                      const CellMeshCreator<D>& meshCreator,                                \
                      const ElementProcessor<D>& processor,                                 \
                      const MeshWriter& writer );                                           \
                                                                                            \
    template MLHP_EXPORT                                                                    \
    void writeOutput<D>( const AbsBasis<D>& basis,                                          \
                         const AbsQuadrature<D>& quadrature,                                \
                         const QuadratureOrderDeterminor<D>& determinor,                    \
                         const std::string& filename );                                     \
                                                                                            \
    template MLHP_EXPORT                                                                    \
    void writeOutput<D>( const MappingRange<D>& mappings,                                   \
                         const std::string& filename,                                       \
                         std::array<size_t, D> numberOfSubdivisions,                        \
                         PostprocessTopologies topologies );                                \
                                                                                            \
    namespace cellmesh                                                                      \
    {                                                                                       \
        template MLHP_EXPORT                                                                \
        CellMeshCreator<D> grid( std::array<size_t, D> resolution,                          \
                                       PostprocessTopologies topologies );                  \
                                                                                            \
        template MLHP_EXPORT                                                                \
        CellMeshCreator<D> grid( const ResolutionDeterminor<D>& resolution,                 \
                                       PostprocessTopologies topologies );                  \
                                                                                            \
        template MLHP_EXPORT                                                                \
        CellMeshCreator<D> quadraturePoints( const AbsQuadrature<D>& quadrature,            \
                                             const AbsBasis<D>& basis,                      \
                                             const QuadratureOrderDeterminor<D>& order );   \
                                                                                            \
        template MLHP_EXPORT                                                                \
        CellMeshCreator<D> quadraturePoints( const AbsQuadratureOnMesh<D>& quadrature,      \
                                             const AbsBasis<D>& basis );                    \
                                                                                            \
        template MLHP_EXPORT                                                                \
        CellMeshCreator<D> boundary( const ImplicitFunction<D>& function,                   \
                                     std::array<size_t, D> resolution,                      \
                                     bool recoverMeshBoundaries,                            \
                                     size_t niterations );                                  \
                                                                                            \
        template MLHP_EXPORT                                                                \
        CellMeshCreator<D> boundary( const ImplicitFunction<D>& function,                   \
                                     const ResolutionDeterminor<D>& determinor,             \
                                     bool recoverMeshBoundaries,                            \
                                     size_t niterations );                                  \
                                                                                            \
        template MLHP_EXPORT                                                                \
        CellMeshCreator<D> domain( const ImplicitFunction<D>& function,                     \
                                   std::array<size_t, D> resolution,                        \
                                   bool coarsen,                                            \
                                   bool meshBothSides,                                      \
                                   size_t niterations );                                    \
                                                                                            \
        template MLHP_EXPORT                                                                \
        CellMeshCreator<D> domain( const ImplicitFunction<D>& function,                     \
                                   const ResolutionDeterminor<D>& determior,                \
                                   bool coarsen,                                            \
                                   bool meshBothSides,                                      \
                                   size_t niterations );                                    \
                                                                                            \
        template MLHP_EXPORT                                                                \
        CellMeshCreator<D> localSimplices( memory::vptr<const SimplexMesh<D, D - 1>>,       \
                                           memory::vptr<const SimplexCellAssociation<D>> ); \
    }                                                                                       \
                                                                                            \
    template MLHP_EXPORT                                                                    \
    ResolutionDeterminor<D> uniformResolution( std::array<size_t, D> resolution );          \
                                                                                            \
    template MLHP_EXPORT                                                                    \
    ResolutionDeterminor<D> perLevelResolution( const PerLevelResolution<D>& resolution );  \
                                                                                            \
    template MLHP_EXPORT                                                                    \
    ResolutionDeterminor<D> degreeOffsetResolution( const AbsBasis<D>& basis,               \
                                                    size_t offset,                          \
                                                    bool exceptLinear );                    \
                                                                                            \
    template MLHP_EXPORT                                                                    \
    void writeVtu( const AbsMesh<D>& mesh,                                                  \
                   const std::string& filename );                                           \
                                                                                            \
    template MLHP_EXPORT                                                                    \
    void writeVtu( std::span<const std::array<double, D>> points,                           \
                   const std::string& filename,                                             \
                   std::span<const double> pointData );

MLHP_POSTPROCESSING_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

// Instantiate for all dimensions
#define MLHP_INSTANTIATE_DIM( D )                                                                  \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> makeSolutionProcessor( memory::vptr<const std::vector<double>> solution,   \
                                               const std::string& name );                          \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> makeVonMisesProcessor( memory::vptr<const std::vector<double>> solution,   \
                                               memory::vptr<const KinematicEquation<D>>,           \
                                               memory::vptr<const ConstitutiveEquation<D>>,        \
                                               const std::string& name );                          \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> makeStressProcessor( memory::vptr<const std::vector<double>> solution,     \
                                             memory::vptr<const KinematicEquation<D>>,             \
                                             memory::vptr<const ConstitutiveEquation<D>>,          \
                                             const std::string& name );                            \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> makeStrainProcessor( memory::vptr<const std::vector<double>> solution,     \
                                             memory::vptr<const KinematicEquation<D>>,             \
                                             memory::vptr<const ConstitutiveEquation<D>>,          \
                                             const std::string& name );                            \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> makeStrainEnergyProcessor( memory::vptr<const std::vector<double>>,        \
                                                   memory::vptr<const KinematicEquation<D>>,       \
                                                   memory::vptr<const ConstitutiveEquation<D>>,    \
                                                   const std::string& name );                      \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> makeStressProcessor( std::array<std::span<const double>, D> gradient,      \
                                             memory::vptr<const KinematicEquation<D>>,             \
                                             memory::vptr<const ConstitutiveEquation<D>>,          \
                                             const std::string& name );                            \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> makeVonMisesProcessor( std::array<std::span<const double>, D> gradient,    \
                                               memory::vptr<const KinematicEquation<D>> ,          \
                                               memory::vptr<const ConstitutiveEquation<D>>,        \
                                               const std::string& name );                          \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> makeStrainProcessor( std::array<std::span<const double>, D> gradient,      \
                                             memory::vptr<const KinematicEquation<D>> ,            \
                                             memory::vptr<const ConstitutiveEquation<D>>,          \
                                             const std::string& name );                            \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> makeStrainEnergyProcessor( std::array<std::span<const double>, D> gradient,\
                                                   memory::vptr<const KinematicEquation<D>>,       \
                                                   memory::vptr<const ConstitutiveEquation<D>>,    \
                                                   const std::string& name );                      \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> makeShapeFunctionProcessor( const DofIndexVector& indices,                 \
                                                    size_t diffOrder,                              \
                                                    size_t diffComponent,                          \
                                                    const std::string& name );                     \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    CellProcessor<D> makeRefinementLevelProcessor( const AbsHierarchicalGrid<D>& grid,             \
                                                   const std::string& name );                      \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    CellProcessor<D> makeCellDataProcessor( memory::vptr<const std::vector<double>> data,          \
                                            const std::string& name );                             \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    CellProcessor<D> makeKdTreeInfoProcessor( );                                                   \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    CellProcessor<D> mergeProcessors( std::vector<CellProcessor<D>>&& processors );                \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> mergeProcessors( std::vector<ElementProcessor<D>>&& processors );          \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    ElementProcessor<D> convertToElementProcessor( CellProcessor<D>&& processor );                 \
                                                                                                   \
    template MLHP_EXPORT                                                                           \
    CellProcessor<D> convertToCellProcessor( ElementProcessor<D>&& processor,                      \
                                             const AbsBasis<D>& basis );                           \
                                                                                                   \
    namespace cellmesh                                                                             \
    {                                                                                              \
        template MLHP_EXPORT                                                                       \
        CellMeshCreator<D> custom( std::vector<OutputMeshPartition>&& partitions );                \
    }
    
MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

namespace detail
{

// The functions that we need with D + 1 for space-time
#define INSTANTIATE_POSTPROCESSING_IMPL(D)                                            \
                                                                                      \
    template MLHP_EXPORT                                                              \
    void createPostprocessingGrid( CoordinateGrid<D>& rst,                            \
                                   std::array<size_t, D> numberOfCells );

// Instantiate detail:: with postprocessing dimensions
#define MLHP_INSTANTIATE_DIM( D )                                                     \
                                                                                      \
    template MLHP_EXPORT                                                              \
    void appendVtuPostprocessingGrid( std::array<size_t, D> resolution,               \
                                      PostprocessTopologies topologies,               \
                                      std::vector<vtu11::VtkIndexType>& connectivity, \
                                      std::vector<vtu11::VtkIndexType>& offsets,      \
                                      std::vector<vtu11::VtkCellType>& types );       \
                                                                                      \
    template MLHP_EXPORT                                                              \
    void appendPointData( std::vector<double>& points,                                \
                          const CoordinateList<D>& xyz );
    
MLHP_POSTPROCESSING_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

// Instantiate detail:: with postprocessing dimensions + 1 for space-time
#define MLHP_INSTANTIATE_DIM( D ) \
    INSTANTIATE_POSTPROCESSING_IMPL( D + 1 )
MLHP_INSTANTIATE_DIM( 0 ) MLHP_POSTPROCESSING_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // namespace detail
} // mlhp
