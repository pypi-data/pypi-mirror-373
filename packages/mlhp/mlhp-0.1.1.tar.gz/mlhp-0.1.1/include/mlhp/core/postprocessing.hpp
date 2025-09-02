// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_POSTPROCESSING_HPP
#define MLHP_CORE_POSTPROCESSING_HPP

#include "mlhp/core/mesh.hpp"
#include "mlhp/core/basis.hpp"
#include "mlhp/core/utilities.hpp"
#include "mlhp/core/triangulation.hpp"
#include "mlhp/core/parallel.hpp"

#include <functional>
#include <vector>
#include <span>

namespace mlhp
{

//! Postprocess dofs
template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeSolutionProcessor( memory::vptr<const std::vector<double>> solution,
                                           const std::string& name = "Solution" );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeVonMisesProcessor( memory::vptr<const std::vector<double>> solution,
                                           memory::vptr<const KinematicEquation<D>> kinematics,
                                           memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                           const std::string& name = "VonMisesStress" );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeStressProcessor( memory::vptr<const std::vector<double>> solution,
                                         memory::vptr<const KinematicEquation<D>> kinematics,
                                         memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                         const std::string& name = "Stress" );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeStrainProcessor( memory::vptr<const std::vector<double>> solution,
                                         memory::vptr<const KinematicEquation<D>> kinematics,
                                         memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                         const std::string& name = "Strain" );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeStrainEnergyProcessor( memory::vptr<const std::vector<double>> solution,
                                               memory::vptr<const KinematicEquation<D>> kinematics,
                                               memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                               const std::string& name = "StrainEnergyDensity" );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeStressProcessor( std::array<std::span<const double>, D> gradient,
                                         memory::vptr<const KinematicEquation<D>> kinematics,
                                         memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                         const std::string& name = "Stress" );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeVonMisesProcessor( std::array<std::span<const double>, D> gradient,
                                           memory::vptr<const KinematicEquation<D>> kinematics,
                                           memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                           const std::string& name = "VonMisesStress" );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeStrainProcessor( std::array<std::span<const double>, D> gradient,
                                         memory::vptr<const KinematicEquation<D>> kinematics,
                                         memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                         const std::string& name = "Strain" );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeStrainEnergyProcessor( std::array<std::span<const double>, D> gradient,
                                               memory::vptr<const KinematicEquation<D>> kinematics,
                                               memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                               const std::string& name = "StrainEnergyDensity" );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> makeShapeFunctionProcessor( const DofIndexVector& indices,
                                                size_t diffOrder = 0,
                                                size_t diffComponent = 0,
                                                const std::string& name = "Basis");

template<size_t D> MLHP_EXPORT
CellProcessor<D> makeRefinementLevelProcessor( const AbsHierarchicalGrid<D>& grid,
                                               const std::string& name = "RefinementLevel" );

template<size_t D> MLHP_EXPORT
CellProcessor<D> makeCellDataProcessor( memory::vptr<const std::vector<double>> data,
                                        const std::string& name = "CellData" );

//! Outputs KdTree leaf cell info. Must be used with an instance of KdTree<D>.
template<size_t D> MLHP_EXPORT
CellProcessor<D> makeKdTreeInfoProcessor( );

//! Scalar return type convertible to double
template<size_t D, spatial::ConvertibleToScalarFunction Function> inline
auto makeFunctionProcessor( Function&& function, 
                            const std::string& name = "Function" );

//! Array return type with elements that are convertible to double
template<size_t D> inline
auto makeFunctionProcessor( const spatial::VectorFunction<D>& function, 
                            const std::string& name = "Function" );

//! Must be used with an instance of KdTree<D>
template<size_t D>  MLHP_EXPORT
CellProcessor<D> makeKdTreeInfoProcessor( );

struct MeshWriter;
struct OutputMeshPartition;

struct Output
{
    enum class Type { CellData, PointData };

    std::string name;
    Type type;
    size_t ncomponents;
};

struct DataAccumulator
{ 
    MLHP_EXPORT operator MeshWriter( );

    std::shared_ptr<OutputMeshPartition> mesh;
    std::shared_ptr<std::vector<std::vector<double>>> data;
};

// TODO: implement through DataAccumulator
struct VtuOutput
{
    std::string filename = "output.vtu";
    std::string mode = "RawBinaryCompressed";

    MLHP_EXPORT operator MeshWriter( ) const;
};

struct PVtuOutput
{
    std::string filename = "output";
    std::string mode = "RawBinaryCompressed";

    size_t maxpartitions = 2 * parallel::getMaxNumberOfThreads( );

    MLHP_EXPORT MLHP_PURE
    operator MeshWriter( ) const;
};

// Generic mesh / basis output
template<size_t D> MLHP_EXPORT
void writeOutput( const AbsMesh<D>& mesh,
                  const CellMeshCreator<D>& meshCreator,
                  const CellProcessor<D>& processor,
                  const MeshWriter& writer );

template<size_t D> MLHP_EXPORT
void writeOutput( const AbsBasis<D>& basis,
                  const CellMeshCreator<D>& meshCreator,
                  const ElementProcessor<D>& processor,        
                  const MeshWriter& writer );

// Pass postprocessors as tuple
template<size_t D, typename... Processors>
void writeOutput( const AbsMesh<D>& mesh,
                  const CellMeshCreator<D>& meshCreator,
                  const std::tuple<Processors...>& processors,
                  const MeshWriter& writer );

template<size_t D, typename... Processors>
void writeOutput( const AbsBasis<D>& basis,
                  const CellMeshCreator<D>& meshCreator,
                  const std::tuple<Processors...>& processors,
                  const MeshWriter& writer );

//! Postprocess integration points
template<size_t D> MLHP_EXPORT
void writeOutput( const AbsBasis<D>& basis,
                  const AbsQuadrature<D>& quadrature,
                  const QuadratureOrderDeterminor<D>& determinor,
                  const std::string& filename );

template<size_t G, size_t L> MLHP_EXPORT
void writeVtu( const SimplexMesh<G, L>& simplexMesh,
               const std::string& filename = "simplices.vtu",
               std::span<const double> pointData = { } );

template<size_t D> MLHP_EXPORT
void writeVtu( std::span<const std::array<double, D>> points,
               const std::string& filename,
               std::span<const double> pointData = { } );

MLHP_EXPORT
void writeVtu( const std::string& filename,
               const std::vector<double>& points,
               const std::vector<std::int64_t>& connectivity,
               const std::vector<std::int64_t>& offsets,
               const std::vector<std::int8_t>& types,
               const std::vector<double>& pointData = { } );

MLHP_EXPORT
void writeStl( const Triangulation<3>& triangulation,
               const std::string& filename,
               const std::string& solidName = "Boundary" );

template<size_t D> MLHP_EXPORT
void writeVtu( const AbsMesh<D>& mesh,
               const std::string& filename = "mesh.vtu" );

enum class PostprocessTopologies
{
    None    = 0,
    Corners = 1,
    Edges   = 2,
    Faces   = 4,
    Volumes = 8
};

constexpr PostprocessTopologies operator|( PostprocessTopologies a, PostprocessTopologies b )
{
    return static_cast<PostprocessTopologies>( static_cast<int>( a ) | static_cast<int>( b ) );
}

constexpr PostprocessTopologies defaultOutputTopologies[] =
{
    PostprocessTopologies::None,
    PostprocessTopologies::Edges   | PostprocessTopologies::Corners,
    PostprocessTopologies::Faces   | PostprocessTopologies::Edges,
    PostprocessTopologies::Volumes | PostprocessTopologies::Edges
};

//! Postprocess on range of mappings
template<size_t D> MLHP_EXPORT
void writeOutput( const MappingRange<D>& mappings,
                  const std::string& filename,
                  std::array<size_t, D> numberOfSubdivisions = array::make<size_t, D>( 1 ),
                  PostprocessTopologies topologies = defaultOutputTopologies[D] );

// Postprocessing resolution on each element
template<size_t D> MLHP_EXPORT
ResolutionDeterminor<D> uniformResolution( std::array<size_t, D> resolution );

template<size_t D>
using PerLevelResolution = std::function<std::array<size_t, D>( RefinementLevel level )>;

template<size_t D> MLHP_EXPORT
ResolutionDeterminor<D> perLevelResolution( const PerLevelResolution<D>& resolution );

template<size_t D> MLHP_EXPORT
ResolutionDeterminor<D> degreeOffsetResolution( const AbsBasis<D>& basis,
                                                size_t offset = 1,
                                                bool exceptLinear = true );

namespace cellmesh
{

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> grid( const ResolutionDeterminor<D>& resolutionDeterminor,
                         PostprocessTopologies topologies = defaultOutputTopologies[D] );

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> grid( std::array<size_t, D> resolution = array::makeSizes<D>( 1 ),
                         PostprocessTopologies topologies = defaultOutputTopologies[D] );

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> custom( std::vector<OutputMeshPartition>&& partitions );

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> boundary( const ImplicitFunction<D>& function,
                             std::array<size_t, D> resolution = array::makeSizes<D>( 1 ),
                             bool recoverMeshBoundaries = true,
                             size_t niterations = marching::bisectionDefault );

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> boundary( const ImplicitFunction<D>& function,
                             const ResolutionDeterminor<D>& determinor,
                             bool recoverMeshBoundaries = true,
                             size_t niterations = marching::bisectionDefault );

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> domain( const ImplicitFunction<D>& function,
                           std::array<size_t, D> resolution = array::makeSizes<D>( 1 ),
                           bool coarsen = false,
                           bool meshBothSides = false,
                           size_t niterations = marching::bisectionDefault );

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> domain( const ImplicitFunction<D>& function,
                           const ResolutionDeterminor<D>& determior,
                           bool coarsen = false,
                           bool meshBothSides = false,
                           size_t niterations = marching::bisectionDefault );

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> localSimplices( memory::vptr<const SimplexMesh<D, D - 1>> simplexMesh,
                                   memory::vptr<const SimplexCellAssociation<D>> celldata );

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> quadraturePoints( const AbsQuadrature<D>& quadrature,
                                     const AbsBasis<D>& basis,
                                     const QuadratureOrderDeterminor<D>& determinor );

template<size_t D> MLHP_EXPORT
CellMeshCreator<D> quadraturePoints( const AbsQuadratureOnMesh<D>& quadrature,
                                     const AbsBasis<D>& basis );

} // namespace cellmesh

using OutputVector = std::vector<Output>;

template<size_t D>
struct ElementProcessor
{
    using Cache = utilities::Cache<ElementProcessor>;
    using Targets = std::span<std::span<double>>;
    
    // 1. Ask what data is being written
    using OutputData = OutputVector( const AbsBasis<D>& basis );

    // 2. Initialize inside omp parallel, before element loop
    using Initialize = Cache( const AbsBasis<D>& basis );

    // 3. Evaluate element before looping over points
    using EvaluateCell = void( Cache& cache, Targets targets,
                               const DofIndexVector& locationMap,
                               const MeshMapping<D>& mapping );

    // 4. Evaluate inside loop over all points and loop over all elements
    using EvaluatePoint = void( Cache& cache, Targets targets,
                                const BasisFunctionEvaluation<D>& shapes );

    // Callback functions with types declared above
    std::function<OutputData> outputData = utilities::returnEmpty<OutputVector>( );
    std::function<Initialize> initialize = utilities::returnEmpty<Cache>( );
    std::function<EvaluateCell> evaluateCell = utilities::doNothing( );
    std::function<EvaluatePoint> evaluatePoint = utilities::doNothing( );

    // Highest derivative needed
    DiffOrders diffOrder;
};

template<size_t D>
struct CellProcessor
{
    using Cache = utilities::Cache<CellProcessor>;
    using Targets = std::span<std::span<double>>;
    
    // 1. Ask what data is being written
    using OutputData = OutputVector( const AbsMesh<D>& mesh );

    // 2. Initialize inside omp parallel, before cell loop
    using Initialize = Cache( const AbsMesh<D>& mesh );

    // 3. Evaluate cell before looping over points
    using EvaluateCell = void( Cache& cache, Targets targets,
                               CellIndex cellIndex,
                               const AbsMapping<D>& mapping );

    // 4. Evaluate inside loop over all points and loop over all cells
    using EvaluatePoint = void( Cache& cache, Targets targets,
                                std::array<double, D> rst,
                                std::array<double, D> xyz );

    // Callback functions with types declared above
    std::function<OutputData> outputData = utilities::returnEmpty<OutputVector>( );
    std::function<Initialize> initialize = utilities::returnEmpty<Cache>( );
    std::function<EvaluateCell> evaluateCell = utilities::doNothing( );
    std::function<EvaluatePoint> evaluatePoint = utilities::doNothing( );
};

template<size_t D> MLHP_EXPORT
CellProcessor<D> mergeProcessors( std::vector<CellProcessor<D>>&& processors );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> mergeProcessors( std::vector<ElementProcessor<D>>&& processors );

template<size_t D> MLHP_EXPORT
ElementProcessor<D> convertToElementProcessor( CellProcessor<D>&& processor );

template<size_t D> MLHP_EXPORT
CellProcessor<D> convertToCellProcessor( ElementProcessor<D>&& processor,
                                         const AbsBasis<D>& basis );

struct OutputMeshPartition
{
    CellIndex index;

    std::vector<double> points;
    std::vector<std::int64_t> connectivity;
    std::vector<std::int64_t> offsets;
    std::vector<std::int8_t> types;
};

struct MeshWriter
{
    using Cache = utilities::Cache<MeshWriter>;

    using Initialize = Cache( size_t npartitions, 
                              const std::vector<Output>& outputs );

    using WritePartition = void( Cache& anyCache,
                                 const OutputMeshPartition& partition,
                                 const std::vector<std::vector<double>>& data );

    using Finalize = void( Cache& anyCache );

    std::function<Initialize> initialize = utilities::returnEmpty<Cache>( );
    std::function<WritePartition> writePartition = utilities::doNothing( );
    std::function<Finalize> finalize = utilities::doNothing( );

    size_t maxpartitions;
};

namespace detail
{

template<size_t D> inline
ElementProcessor<D> makeElementPointProcessor( auto&& evaluateSimple, 
                                               auto&& outputSingle,
                                               DiffOrders diffOrder )
{
    using Cache = std::tuple<const std::vector<DofIndex>*, const MeshMapping<D>*>;

    auto evaluateCell = []( auto& anyCache, auto, 
                            auto& locationMap, auto& mapping )
    {
        auto& [cachedLocationMap, cachedMapping] = utilities::cast<Cache>( anyCache );

        cachedLocationMap = &locationMap;
        cachedMapping = &mapping;
    };

    auto initialize = []( auto& ) -> typename ElementProcessor<D>::Cache
    {
        return Cache { nullptr, nullptr };
    };

    auto evaluatePoint = [ evaluateSimple = std::move( evaluateSimple )]
                         ( auto& anyCache, auto targets, const auto& shapes )
    {
        const auto& [locationMap, mapping] = utilities::cast<Cache>( anyCache );

        evaluateSimple( shapes, *mapping, *locationMap, targets[0] );
    };

    auto outputData = [ outputSingle = std::move( outputSingle )]
                      ( auto& basis ) -> OutputVector
    {
        return { outputSingle( basis ) };
    };

    return 
    { 
        .outputData = std::move( outputData ), 
        .initialize = std::move( initialize ),
        .evaluateCell = std::move( evaluateCell ),
        .evaluatePoint = std::move( evaluatePoint ),
        .diffOrder = diffOrder
    };
}

template<size_t D> inline
CellProcessor<D> makeCellPointProcessor( auto&& evaluateSimple, 
                                         const std::string& name, 
                                         size_t ncomponents )
{
    auto evaluate = [ evaluateSimple = std::move( evaluateSimple )]
                    ( auto&, auto targets,  auto rst, auto xyz )
    {
        evaluateSimple( rst, xyz, targets[0] );
    };

    auto output = Output
    {
        .name = name,
        .type = Output::Type::PointData,
        .ncomponents = ncomponents
    };

    return CellProcessor<D>
    { 
        .outputData = utilities::returnValue( std::vector { output } ),
        .evaluatePoint = std::move( evaluate )
    };
}

template<size_t D> inline
CellProcessor<D> makeCellCellProcessor( auto&& evaluateSimple, 
                                        auto&& outputSimple )
{
    auto evaluate = [ evaluateSimple = std::move( evaluateSimple )]
                    ( auto&, auto targets, auto cellIndex, auto& mapping ) noexcept
    {
        evaluateSimple( cellIndex, mapping, targets[0] );
    };

    auto outputData = [ outputSimple = std::move( outputSimple )]
                      ( auto& mesh ) -> OutputVector
    {
        auto [name, ncomponents] = outputSimple( mesh );

        return { { .name = name, .type = Output::Type::CellData, .ncomponents = ncomponents } };
    };

    return CellProcessor<D> { .outputData = outputData, .evaluateCell = std::move( evaluate ) };
}

} // detail

template<size_t D, typename... Processors> inline
void writeOutput( const AbsMesh<D>& mesh,
                  const CellMeshCreator<D>& meshCreator,
                  const std::tuple<Processors...>& processors,
                  const MeshWriter& writer )
{
    auto copy = std::vector<CellProcessor<D>> { };

    auto recursive = [&]<size_t I = 0>( auto&& self )
    {
        using T = std::decay_t<decltype( std::get<I>( processors ) )>;

        copy.push_back( T { std::get<I>( processors ) } );

        if constexpr ( I + 1 < sizeof...( Processors ) ) 
        { 
            self.template operator()<I + 1>( self );
        }
    };

    recursive( recursive );

    writeOutput( mesh, meshCreator, mergeProcessors( std::move( copy ) ), writer );
}

template<size_t D, typename... Processors> inline
void writeOutput( const AbsBasis<D>& basis,
                  const CellMeshCreator<D>& meshCreator,
                  const std::tuple<Processors...>& processors,
                  const MeshWriter& writer )
{
    auto copy = std::vector<ElementProcessor<D>> { };

    auto recursive = [&]<size_t I = 0>( auto&& self )
    {
        using T = std::decay_t<decltype( std::get<I>( processors ) )>;

        if constexpr ( std::is_same_v<T, CellProcessor<D>> )
        {
            copy.push_back( convertToElementProcessor( T { std::get<I>( processors ) } ) );
        }
        else
        {
            copy.push_back( std::get<I>( processors ) );
        }

        if constexpr ( I + 1 < sizeof...( Processors ) ) 
        { 
            self.template operator()<I + 1>( self );
        }
    };

    recursive( recursive );
    
    writeOutput( basis, meshCreator, mergeProcessors( std::move( copy ) ), writer );
}

// Scalar return type convertible to double
template<size_t D, spatial::ConvertibleToScalarFunction Function> inline
auto makeFunctionProcessor( Function&& function, 
                            const std::string& name )
{
    auto evaluate = [=]( auto, auto xyz, auto result ) 
    { 
        result[0] = static_cast<double>( function( xyz ) ); 
    };

    return detail::makeCellPointProcessor<D>( std::move( evaluate ), name, 1 );
}

// Array return type with elements that are convertible to double
template<size_t D> inline
auto makeFunctionProcessor( const spatial::VectorFunction<D>& function, 
                            const std::string& name ) 
{
    return detail::makeCellPointProcessor<D>( [=]( auto, auto xyz, auto result ) 
        {  function( xyz, result ); }, name, function.odim );

    // static constexpr auto O = spatial::InspectFunction<Function>::odim;
    // 
    // auto evaluate = [=]( auto, auto xyz, auto result ) 
    // { 
    //     auto f = array::convert<double>( function( xyz ) ); 
    // 
    //     std::copy( f.begin( ), f.end( ), result.begin( ) );
    // };
    // 
    // return detail::makeCellPointProcessor<D>( std::move( evaluate ), name, O );
}

} // mlhp

#endif // MLHP_CORE_POSTPROCESSING_HPP
