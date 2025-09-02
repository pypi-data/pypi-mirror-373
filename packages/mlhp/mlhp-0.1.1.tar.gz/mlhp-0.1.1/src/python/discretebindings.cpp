// This file is part of the mlhp project. License: See LICENSE

#include "pybind11/pybind11.h"
#include "pybind11/functional.h"
#include "pybind11/stl.h"

#include "mlhp/core.hpp"

#include "src/python/pymlhpcore.hpp"

#include <sstream>
#include <iomanip>

namespace mlhp::bindings
{

template<size_t D>
void defineGrid( pybind11::module& m )
{
    auto overloadMeshMembers = []<typename Type, typename...Args>( pybind11::class_<Type, Args...>& pybindclass, std::string type )
    {
        auto str = [=]( const Type& mesh )
        {
            std::ostringstream os;

            os << type << "<" << D << "> (address: " << &mesh << ")\n";
            os << "    ncells       : " << mesh.ncells( ) << std::endl;
            os << "    memory usage : " << utilities::memoryUsageString( mesh.memoryUsage( ) ) << std::endl;

            return os.str( );
        };

        pybindclass.def( "__str__", str );
    };

    auto __str__ = []( const HierarchicalGridSharedPtr<D>& grid )
    { 
        std::ostringstream os;

        print( *grid, os );

        return os.str( );
    };

    auto refineF1 = []( AbsHierarchicalGrid<D>& self,
                        const RefinementFunctionWrapper<D>& refinement )
    { 
        self.refine( refinement );
    };  

    
    // https://pybind11.readthedocs.io/en/stable/advanced/classes.html#overriding-virtuals
    //class PyAbsMesh : public AbsMesh<D>
    //{
    //    using AbsMesh::AbsMesh;

    //    CellIndex ncells( ) const override
    //    {
    //        PYBIND11_OVERRIDE_PURE( CellIndex, AbsMesh<D>, ncells, 0 );
    //    }
    //};

    auto absMesh = pybind11::class_<AbsMesh<D>, MeshSharedPtr<D>>
        ( m, add<D>( "AbsMesh" ).c_str( ) );
            
    auto neighbours = []( const AbsMesh<D>& mesh, CellIndex icell, size_t iface )
    {
        auto target = std::vector<MeshCellFace> { };

        mesh.neighbours( icell, iface, target );

        return target;
    };

    auto mapF1 = pybind11::overload_cast<const AbsMesh<D>&, CellIndex, std::array<double, D>>( &mesh::map<D> );

    auto mapF2 = []( const AbsMesh<D>& mesh, const std::vector<CellIndex>& indices, const CoordinateList<D>& rst )
    {
        return mesh::map<D>( mesh, indices, rst );
    };

    auto mapBackwardsF1 = []( const AbsMesh<D>& mesh, std::array<double, D> xyz, double epsilon )
    {
        auto result = BackwardMapVector<D> { };
        
        mesh.createBackwardMapping( )->map( xyz, result, epsilon );

        return result;
    };

    auto mapBackwardsF2 = []( const AbsMesh<D>& mesh, std::vector<std::array<double, D>> xyz, double epsilon )
    {
        auto result = mesh::mapBackwardMultiple<D>( mesh, xyz, epsilon );
        auto nested = std::vector<BackwardMapVector<D>>( xyz.size( ) );

        for( size_t i = 0; i < xyz.size( ); ++i )
        {
            auto span = utilities::linearizedSpan( result, i );

            nested[i] = std::vector( span.begin( ), span.end( ) );
        }

        return nested;
    };


    absMesh.def( "ncells", []( const AbsMesh<D>& mesh ) { return mesh.ncells( ); } );
    absMesh.def( "nfaces", []( const AbsMesh<D>& mesh, CellIndex icell ) { return mesh.nfaces( icell ); }, pybind11::arg( "icell" ) );
    absMesh.def_property_readonly( "ndim", []( const AbsMesh<D>& ) { return D; } );
    absMesh.def( "cellType", &AbsMesh<D>::cellType, pybind11::arg( "icell" ) );
    absMesh.def( "memoryUsage", []( const AbsMesh<D>& mesh ) { return mesh.memoryUsage( ); } );
    absMesh.def( "neighbours", neighbours, pybind11::arg( "icell" ), pybind11::arg( "iface" ) );
    absMesh.def( "shallowClone", &AbsMesh<D>::clone );
    absMesh.def( "map", mapF1, pybind11::arg( "icell" ), pybind11::arg( "rst" ) );
    absMesh.def( "map", mapF2, pybind11::arg( "icell" ), pybind11::arg( "rst" ) );
    absMesh.def( "mapBackwards", mapBackwardsF1, pybind11::arg( "xyz" ), pybind11::kw_only( ), pybind11::arg( "epsilon" ) = 1e-10 );
    absMesh.def( "mapBackwards", mapBackwardsF2, pybind11::arg( "xyz" ), pybind11::kw_only( ), pybind11::arg( "epsilon" ) = 1e-10 );

    if constexpr ( D <= 3 )
    {
        auto writeVtuF = pybind11::overload_cast<const AbsMesh<D>&, const std::string&>( &writeVtu<D> );
    
        absMesh.def( "writeVtu", writeVtuF, pybind11::arg( "filename" ) = "mesh.vtu" );
        absMesh.def( "skeletonMesh", &createSkeletonMesh<D>, "Create simplex mesh of all mesh faces." );
    }

    overloadMeshMembers( absMesh, "AbsMesh" ); 

    auto absGrid = pybind11::class_<AbsGrid<D>, AbsMesh<D>, GridSharedPtr<D>>
        ( m, add<D>( "AbsGrid" ).c_str( ) );
    
    overloadMeshMembers( absGrid, "AbsGrid" );
    
    auto cartesianGrid = pybind11::class_<CartesianGrid<D>, AbsGrid<D>, CartesianGridSharedPtr<D>>
        ( m, add<D>( "CartesianGrid" ).c_str( ) );
    
    cartesianGrid.def( "boundingBox", []( const CartesianGrid<D>& grid ) { return grid.boundingBox( ); } );
    cartesianGrid.def( "shape", pybind11::overload_cast<size_t>( &CartesianGrid<D>::ncells, pybind11::const_ ), pybind11::arg( "axis" ) );
    cartesianGrid.def( "coordinates", &CartesianGrid<D>::coordinates );
    
    overloadMeshMembers( cartesianGrid, "CartesianGrid" );
    
    m.def( "makeGrid", &makeCartesianGrid<D>,
           pybind11::arg( "ncells" ),
           pybind11::arg( "lengths" ) = array::make<D>( 1.0 ),
           pybind11::arg( "origin" ) = array::make<D>( 0.0 ) );

    m.def( "gridsplit", &mesh::gridsplit<D>, pybind11::arg( "lengths" ), pybind11::arg( "targetNumber" ) );

    auto makeGridF = []( CoordinateGrid<D>&& grid ) 
    { 
        return std::make_shared<CartesianGrid<D>>( std::move( grid ) ); 
    };

    m.def( "makeGrid", makeGridF, pybind11::arg( "ticks" ) );
    
    auto leafRefinementLevelsF = []( const AbsHierarchicalGrid<D>& grid, bool fullHierarchy )
    {
        return mesh::refinementLevels( grid, fullHierarchy );
    };

    auto refineF2 = pybind11::overload_cast<const std::vector<CellIndex>&>( &AbsHierarchicalGrid<D>::refine );

    pybind11::class_<AbsHierarchicalGrid<D>, AbsMesh<D>, HierarchicalGridSharedPtr<D>>
        ( m, add<D>( "AbsHierarchicalGrid" ).c_str( ) )
        .def( "nleaves", &AbsHierarchicalGrid<D>::nleaves )
        .def( "refine", refineF1, pybind11::arg( "strategy" ) )
        .def( "refine", refineF2, pybind11::arg( "leafIndices" ) )
        .def( "baseGrid", &AbsHierarchicalGrid<D>::baseGridPtr )
        .def( "refinementLevels", leafRefinementLevelsF, pybind11::arg( "fullHierarchy" ) = false )
        .def( "__str__", __str__ );

    auto refinedGrid = pybind11::class_<RefinedGrid<D>, AbsHierarchicalGrid<D>, 
        std::shared_ptr<RefinedGrid<D>>> ( m, add<D>( "RefinedGrid" ).c_str( ) );

    refinedGrid.def( pybind11::init<std::shared_ptr<AbsGrid<D>>>( ) );
    
    using FactoryType = HierarchicalGridSharedPtr<D>( std::array<size_t, D>,
                                                      std::array<double, D>, 
                                                      std::array<double, D> );

    m.def( "makeRefinedGrid", static_cast<FactoryType*>( makeRefinedGrid<D> ),
           pybind11::arg( "ncells" ),
           pybind11::arg( "lengths" ) = array::make<D>( 1.0 ),
           pybind11::arg( "origin" ) = array::make<D>( 0.0 ) );
    
    m.def( "makeRefinedGrid", []( GridSharedPtr<D> grid ) { return makeRefinedGrid<D>( grid ); },
        pybind11::arg( "grid" ) );

    auto makeRefinedGridA = []( const AbsHierarchicalGrid<D>& grid,
                                const std::vector<int>& relativeDepth,
                                size_t maxdepth ) 
    { 
        return makeRefinedGrid( grid, relativeDepth, maxdepth );
    };

    m.def( "makeRefinedGrid", makeRefinedGridA, pybind11::arg( "grid" ), 
        pybind11::arg( "relativeDepth" ), pybind11::arg( "maxdepth" ) = NoValue<size_t> );
    
    pybind11::class_<AbsFilteredMesh<D>, AbsMesh<D>, std::shared_ptr<
        AbsFilteredMesh<D>>>( m, add<D>( "AbsFilteredMesh" ).c_str( ) );

    auto filteredGrid = pybind11::class_<FilteredGrid<D>, AbsGrid<D>, AbsFilteredMesh<D>, 
        std::shared_ptr<FilteredGrid<D>>>( m, add<D>( "FilteredGrid" ).c_str( ) );

    filteredGrid.def( pybind11::init<std::shared_ptr<AbsGrid<D>>, 
        std::vector<bool>>( ), pybind11::arg( "grid" ), pybind11::arg( "mask" ) );

    overloadMeshMembers( filteredGrid, "FilteredGrid" );

    auto asfieldF = []( const std::shared_ptr<ImplicitFunctionWrapper<D>>& f, double value0, double value1 ) 
    { 
        auto s = [=]( std::array<double, D> xyz )
        {
            return f->get( )( xyz ) ? value1 : value0;
        };

        return ScalarFunctionWrapper<D> { std::function { std::move( s ) } };
    };

    auto implicitWrapper = pybind11::class_<ImplicitFunctionWrapper<D>, 
        std::shared_ptr<ImplicitFunctionWrapper<D>>>( m, add<D>( "ImplicitFunction" ).c_str( ) );
    
    implicitWrapper.def( "__call__", &ImplicitFunctionWrapper<D>::call );
    implicitWrapper.def( "asfield", asfieldF, pybind11::arg( "value0" ) = 0.0, pybind11::arg( "value1" ) = 1.0 );

    defineVectorization( implicitWrapper );

    pybind11::class_<RefinementFunctionWrapper<D>>( m, add<D>( "RefinementFunction" ).c_str( ) )
        .def( "__call__", &RefinementFunctionWrapper<D>::call );
    
    auto cutstateF = []( const AbsGrid<D>& grid,
                         const ImplicitFunctionWrapper<D>& domain,
                         size_t nseedpoints )
    {
        return mesh::cutstate( grid, domain.get( ), nseedpoints );
    };

    m.def( "cutstate", cutstateF, pybind11::arg( "grid" ),
        pybind11::arg( "domain" ), pybind11::arg( "nseedpoints" ) = 4 );

    auto filteredGridF1 = []( std::shared_ptr<AbsGrid<D>> grid,
                            const ImplicitFunctionWrapper<D>& function,
                            size_t nseedpoints )
    { 
        auto mask = mesh::cutstate( *grid, function.get( ), nseedpoints );

        return std::make_shared<FilteredGrid<D>>( grid, std::move( mask ) );
    };

    m.def( "makeFilteredGrid", filteredGridF1, pybind11::arg( "grid" ),
        pybind11::kw_only( ), pybind11::arg( "domain" ), pybind11::arg( "nseedpoints" ) = 4 );
    
    auto filteredGridF2 = []( std::shared_ptr<AbsGrid<D>> grid,
                              const std::vector<std::int8_t>& cutstate,
                              bool removeCutCells )
    { 
        return std::make_shared<FilteredGrid<D>>( grid, cutstate, removeCutCells );
    };
    
    auto filteredGridF3 = []( std::shared_ptr<AbsGrid<D>> grid,
                              const std::vector<bool>& mask )
    { 
        return std::make_shared<FilteredGrid<D>>( grid, mask );
    };

    m.def( "makeFilteredGrid", filteredGridF2, pybind11::arg( "grid" ),
        pybind11::kw_only( ), pybind11::arg( "cutstate" ), pybind11::arg( "removeCutCells" ) = false );

    m.def( "makeFilteredGrid", filteredGridF3, pybind11::arg( "grid" ), 
        pybind11::kw_only( ), pybind11::arg( "mask" ) );

    auto transformation = pybind11::class_<spatial::HomogeneousTransformation<D>>( m,
        add<D>( "HomogeneousTransformation" ).c_str( ) );

    auto transformationVectorCallF = []( const spatial::HomogeneousTransformation<D>& t,
                                         std::vector<std::array<double, D>> xyz )
    {
        for( auto& x : xyz )
        {
            x = t( x );
        }

        return xyz;
    };

    transformation.def( "__call__", &spatial::HomogeneousTransformation<D>::operator(), pybind11::arg( "xyz" ) );
    transformation.def( "__call__", transformationVectorCallF, pybind11::arg( "xyz" ) );

    auto transformationMatrixF = []( const spatial::HomogeneousTransformation<D>& t )
    {
        auto matrix = std::array<std::array<double, D + 1>, D + 1> { };

        for( size_t i = 0; i < D; ++i )
        {
            for( size_t j = 0; j < D + 1; ++j )
            {
                matrix[i][j] = t.matrix[i * (D + 1) + j];
            }
        }

        return matrix;
    };

    auto concatenateF = []( const std::vector<spatial::HomogeneousTransformation<D>>& transformations )
    {
        auto n = transformations.size( );
        auto result = n ? transformations.back( ) : spatial::scale( array::make<D>( 1.0 ) );

        for( size_t i = 1; i < n; ++i )
        {
            auto tmp = spatial::HomogeneousTransformationMatrix<D> { };

            linalg::mmproduct( result.matrix.data( ), transformations[n - i - 1].matrix.data( ), tmp.data( ), D + 1 );

            result.matrix = tmp;
        }

        return result;
    };

    transformation.def( "matrix", transformationMatrixF );
    transformation.def( "invert", &spatial::HomogeneousTransformation<D>::invert );

    m.def( "translation", &spatial::translate<D> );
    m.def( "scaling", &spatial::scale<D> );
    m.def( "concatenate", concatenateF, pybind11::arg( "transformations" ) );

    if constexpr ( D == 2 ) m.def( "rotation", []( double phi ) 
        { return spatial::rotate( phi ); }, pybind11::arg( "phi" ) );

    if constexpr ( D == 3 ) m.def( "rotation", []( std::array<double, 3> normal, double phi ) 
        { return spatial::rotate( normal, phi ); }, pybind11::arg( "normal" ), pybind11::arg( "phi" ) );

    m.def( "implicitSphere", []( std::array<double, D> center, double radius )
        { return ImplicitFunctionWrapper<D>{ implicit::sphere( center, radius ) }; },
        pybind11::arg( "center" ), pybind11::arg( "radius" ) );

    m.def( "implicitCube", []( std::array<double, D> x1, std::array<double, D> x2 )
        { return ImplicitFunctionWrapper<D>{ implicit::cube( x1, x2 ) }; },
        pybind11::arg( "corner1" ), pybind11::arg( "corner2" ) );
    
    m.def( "implicitEllipsoid", []( std::array<double, D> origin, std::array<double, D> radii )
        { return ImplicitFunctionWrapper<D>{ implicit::ellipsoid( origin, radii ) }; },
        pybind11::arg( "origin" ), pybind11::arg( "radii" ) );
    
    m.def( "implicitThreshold", []( const ScalarFunctionWrapper<D>& function, 
                                    double threshold, double sign ) -> ImplicitFunctionWrapper<D>
        { return implicit::threshold( function.get( ), threshold, sign ); },
        pybind11::arg( "function" ), pybind11::arg( "threshold" ) = 0.0, pybind11::arg( "sign" ) = true );

    m.def( "implicitHalfspace", []( std::array<double, D> origin, 
                                    std::array<double, D> outwardNormal ) -> ImplicitFunctionWrapper<D>
        { return implicit::halfspace( origin, outwardNormal ); },
        pybind11::arg( "origin" ), pybind11::arg( "outwardNormal" ) );
    
    m.def( "implicitTransformation", []( const ImplicitFunctionWrapper<D>& function,
                                         const spatial::HomogeneousTransformation<D>& t )
        { return ImplicitFunctionWrapper<D> { implicit::transform( function.get( ), t ) }; },
        pybind11::arg( "function" ), pybind11::arg( "transformation" ) );

    auto implicitF = []( std::vector<ImplicitFunctionWrapper<D>>&& wrappers, auto&& op, bool initial )
    {
        if( !wrappers.empty( ) )
        {
            auto functions = utilities::convertVector<ImplicitFunction<D>>( std::move( wrappers ) );

            auto function = [=, functions = std::move(functions)]( std::array<double, D> xyz )
            {
                auto value = functions.front( )( xyz );

                for( size_t ifunction = 1; ifunction < functions.size( ); ++ifunction )
                {
                    value = op( value, functions[ifunction]( xyz ) );
                }

                return value;
            };

            return ImplicitFunctionWrapper<D> { std::function { function } };
        }
        else
        {
            return ImplicitFunctionWrapper<D> { ImplicitFunction<D> { 
                utilities::returnValue( initial ) } };
        }
    };

    auto implicitUnionF = [=]( std::vector<ImplicitFunctionWrapper<D>>&& functions )
    {
        return implicitF( std::move( functions ), []( bool v1, bool v2 ){ return v1 || v2; }, false );
    };

    auto implicitIntersectionF = [=]( std::vector<ImplicitFunctionWrapper<D>>&& functions )
    {
        return implicitF( std::move( functions ), []( bool v1, bool v2 ){ return v1 && v2; }, true );
    };

    auto implicitSubtractionF = [=]( std::vector<ImplicitFunctionWrapper<D>>&& functions )
    {
        return implicitF( std::move( functions ), []( bool v1, bool v2 ){ return v1 && !v2; }, true );
    };
    
    m.def( "implicitUnion", implicitUnionF, pybind11::arg( "functions" ) );
    m.def( "implicitIntersection", implicitIntersectionF, pybind11::arg( "functions" ) );
    m.def( "implicitSubtraction", implicitSubtractionF, pybind11::arg( "functions" ) );

    m.def( "invert", []( const ImplicitFunctionWrapper<D>& function )
        { return ImplicitFunctionWrapper<D>{ implicit::invert<D>( function ) }; },
        pybind11::arg( "function" ) );
          
    m.def( "extrude", []( const ImplicitFunctionWrapper<D>& function, double minValue, double maxValue, size_t axis )
        { return ImplicitFunctionWrapper<D + 1>{ implicit::extrude<D>( function, minValue, maxValue, axis ) }; },
        pybind11::arg( "function" ), pybind11::arg( "minValue" ), pybind11::arg( "maxValue" ), pybind11::arg( "axis" ) = D );

    m.def( "refineTowardsBoundary", []( const ImplicitFunctionWrapper<D>& function,
                                        size_t maxDepth,
                                        size_t nseedpoints )
    {
        return RefinementFunctionWrapper<D>{ refineTowardsDomainBoundary<D>( 
            function, maxDepth, nseedpoints ) };
    }, pybind11::arg( "function" ), pybind11::arg( "maxDepth" ), 
       pybind11::arg( "nseedpoints" ) = 7 );

    m.def( "refineInsideDomain", []( const ImplicitFunctionWrapper<D>& function,
                                     size_t maxDepth,
                                     size_t nseedpoints )
    {
        return RefinementFunctionWrapper<D>{ refineInsideDomain<D>(
            function, maxDepth, nseedpoints ) };
    }, pybind11::arg( "function" ), pybind11::arg( "maxDepth" ), 
       pybind11::arg( "nseedpoints" ) = 7 );

    auto refineWithLevelFunctionF = []( const ScalarFunctionWrapper<D>& function,
                                        size_t nseedpoints )
    {
        auto levelFunction = [=]( std::array<double, D> xyz )
        {
            auto level = std::round( function.get( )( xyz ) );

            MLHP_CHECK( level >= 0.0 && level < NoValue<RefinementLevel>, 
                        "Refinement level function values must be in [0, " + std::to_string(
                        static_cast<int>( NoValue<RefinementLevel> ) - 1 ) + "]." );

            return static_cast<RefinementLevel>( level );
        };

        return RefinementFunctionWrapper<D>{ refineWithLevelFunction<D>( levelFunction, nseedpoints ) };
    };
    
    m.def( "refineWithLevelFunction", refineWithLevelFunctionF, 
           pybind11::arg( "function" ), pybind11::arg( "nseedpoints" ) = 7 );

    auto refinementOrF = []( std::vector<RefinementFunctionWrapper<D>>&& wrappers )
    {
        auto refinements = utilities::convertVector<RefinementFunction<D>>( std::move( wrappers ) );

        return RefinementFunctionWrapper<D> { [refinements = std::move( refinements )] 
            (const MeshMapping<D>& mapping, RefinementLevel level )
        { 
            bool value = false;

            for( auto& refinement : refinements )
            {
                value = value ? true : refinement( mapping, level );
            }

            return value;
        } };
    };

    m.def( "refinementOr", refinementOrF, pybind11::arg( "refinements" ) );

    auto refineAdaptivelyF = []( const AbsHierarchicalGrid<D>& grid,
                                 const std::vector<int>& relativeDepth,
                                 size_t maxdepth )
    { 
         return RefinementFunctionWrapper<D> { mesh::refineAdaptively( grid, relativeDepth, maxdepth ) };
    };

    m.def( "refineAdaptively", refineAdaptivelyF, pybind11::arg( "grid" ), 
           pybind11::arg( "relativeDepth" ), pybind11::arg("maxdepth" ) = NoValue<size_t> );
}

template<size_t D>
void defineMesh( pybind11::module& m )
{
    auto printMesh = []( const UnstructuredMesh<D>& mesh )
    { 
        std::ostringstream os;

        print( mesh, os );

        return os.str( );
    };

    pybind11::class_<UnstructuredMesh<D>, AbsMesh<D>, std::shared_ptr<UnstructuredMesh<D>>>
        ( m, add<D>( "UnstructuredMesh" ).c_str( ) ) 
        .def( "__str__", printMesh );

    m.def( "makeUnstructuredMesh", []( CoordinateList<D>&& vertices,
                                       std::vector<size_t>&& connectivity,
                                       std::vector<size_t>&& offsets,
                                       bool filterVertices,
                                       bool reorderVertices )
        { return std::make_shared<UnstructuredMesh<D>>( std::move( vertices ),
            std::move( connectivity ), std::move( offsets ), filterVertices, reorderVertices ); },
        pybind11::arg( "vertices" ), pybind11::arg( "cells" ), pybind11::arg( "offsets" ), 
           pybind11::arg( "filter" ) = true, pybind11::arg( "reorder" ) = true );
    
    auto kdtreeC = pybind11::class_<KdTree<D>, std::shared_ptr<KdTree<D>>, 
        AbsMesh<D>>( m, add<D>( "KdTree" ).c_str( ) );

    auto kdtreeStr = []( const KdTree<D>& tree ) 
    { 
        auto sstream = std::stringstream { };

        print( tree, sstream );

        return sstream.str( );
    };

    auto kdtreePrintFullF = []( const KdTree<D>& t )
    {
        auto sstream = std::stringstream { };

        printFull( t, sstream );

        auto str = sstream.str( );

        if( !str.empty( ) )
        {
            pybind11::print( str.substr( 0, str.size( ) - 1 ) );
        }
    };

    kdtreeC.def( "__str__", kdtreeStr );
    kdtreeC.def( "nfull", &KdTree<D>::nfull );
    kdtreeC.def( "nleaves", &KdTree<D>::nleaves );
    kdtreeC.def( "maxdepth", &KdTree<D>::maxdepth );
    kdtreeC.def( "printFull", kdtreePrintFullF );
    kdtreeC.def( "boundingBox", []( const KdTree<D>& t ) { return t.boundingBox( ); } );
    
    if constexpr ( D <= 3 )
    {
        auto kdtreeWriteVtu = []( const KdTree<D>& tree, std::string filename, bool pvtu )
        {
            auto writer = pvtu ? PVtuOutput { filename }.operator mlhp::MeshWriter( ) : 
                                 VtuOutput { filename }.operator mlhp::MeshWriter( );

            auto topologies = static_cast<mlhp::PostprocessTopologies>( utilities::binaryPow<int>( D ) );
            auto grid = cellmesh::grid<D>( array::makeSizes<D>( 1 ), topologies );

            writeOutput( tree, grid, makeKdTreeInfoProcessor<D>( ), writer );
        };

        auto buildKdTreeF = []( const SimplexMesh<D, D - 1>& simplexMesh,
                                std::optional<spatial::BoundingBox<D>> bounds,
                                size_t maxdepth, double KT, double KL, 
                                double emptyCellBias, bool clip )
        {
            auto objectProvider = kdtree::makeObjectProvider<D, D - 1>( simplexMesh, clip );

            return buildKdTree<D>( objectProvider, bounds ? *bounds : simplexMesh.boundingBox( ), 
                { .maxdepth = maxdepth, .KT = KT, .KL = KL, .emptyCellBias = emptyCellBias } );
        };
        
        m.def( "buildKdTree", buildKdTreeF, pybind11::arg( "simplexMesh" ), pybind11::kw_only( ),
               pybind11::arg( "bounds" ) = std::nullopt,
               pybind11::arg( "maxdepth" ) = kdtree::Parameters { }.maxdepth,
               pybind11::arg( "KT" ) = kdtree::Parameters { }.KT,
               pybind11::arg( "KL" ) = kdtree::Parameters { }.KL,
               pybind11::arg( "emptyCellBias" ) = kdtree::Parameters { }.emptyCellBias,
               pybind11::arg( "clipSimplices" ) = true );

        kdtreeC.def( "writeVtu", kdtreeWriteVtu, pybind11::arg( "filename" ) =
            "kdtree", pybind11::arg( "pvtu" ) = false );
    }
}

void defineBasisSingle( pybind11::module& m )
{
    pybind11::class_<AnsatzTemplateVector>( m, "AnsatzTemplateVector" );

    pybind11::class_<PolynomialDegreeTuple>( m, "PolynomialDegreeTuple" )
        .def( pybind11::init<size_t>( ) )
        .def( pybind11::init<const std::vector<size_t>&>( ) );

    pybind11::class_<UniformGrading>( m, "UniformGrading", 
        "Same polynomial degrees everywhere." )
        .def( pybind11::init<PolynomialDegreeTuple>( ),
              pybind11::arg( "uniformDegrees" ) );

    pybind11::class_<LinearGrading>( m, "LinearGrading",
        "Set degrees on finest elements. Increment degrees by one per level coarser." )
        .def( pybind11::init<PolynomialDegreeTuple>( ),
              pybind11::arg( "fineDegrees" ) );

    pybind11::class_<InterpolatedGrading>( m, "InterpolatedGrading",
        "Interpolate between degrees on root elements and finest elements." )
        .def( pybind11::init<PolynomialDegreeTuple, 
                             PolynomialDegreeTuple>( ),
              pybind11::arg( "rootDegrees" ), pybind11::arg( "fineDegrees" ) );
}

template<size_t D, GradingConcept Grading>
void defineBasisFactoryWithGrading( pybind11::module& m )
{
    using FactoryType = MultilevelHpBasisSharedPtr<D>( 
        const HierarchicalGridSharedPtr<D>&, const Grading&, size_t );
    
    m.def( "makeHpTensorSpace", static_cast<FactoryType*>( makeHpBasis<TensorSpace> ),
           "Create tensor space multi-level hp basis with custom polynomial grading.",
           pybind11::arg( "grid" ), pybind11::arg( "grading" ), pybind11::arg( "nfields" ) = 1 );

    m.def( "makeHpTrunkSpace", static_cast<FactoryType*>( makeHpBasis<TrunkSpace> ),
           "Create trunk space multi-level hp basis with custom polynomial grading.",
           pybind11::arg( "grid" ), pybind11::arg( "grading" ), pybind11::arg( "nfields" ) = 1 );

    auto ptr1 = &makeHpBasisFactory<TensorSpace, D, Grading>;
    auto ptr2 = &makeHpBasisFactory<TrunkSpace, D, Grading>;

    m.def( add<D>( "makeHpTensorSpaceFactory" ).c_str( ), ptr1, "Create factory that creates tensor "
           "space hp bases with custom polynomial degree distribution.", pybind11::arg( "degrees" ) );

    m.def( add<D>( "makeHpTrunkSpaceFactory" ).c_str( ), ptr2, "Create factory that creates trunk "
           "space hp bases with custom polynomial degree distribution.", pybind11::arg( "degrees" ) );
}

template<size_t D>
void defineBasis( pybind11::module& m )
{
    auto overloadBasisMembers = []<typename Type, typename...Args>( pybind11::class_<Type, Args...>& pybindclass, 
                                                                    std::string type, bool doStr = true )
    {
        if( doStr )
        {
            auto str = [=]( const Type& basis )
            {
                std::ostringstream os;

                os << type << "<" << D << "> (address: "  << &basis << ")\n";
                os << "    number of elements         : " << basis.nelements( ) << std::endl;
                os << "    number of field components : " << basis.nfields( ) << std::endl;
                os << "    number of dofs             : " << basis.ndof( ) << std::endl;
                os << "    maximum polynomial degree  : " << basis::maxdegree( basis ) << std::endl;
                os << "    heap memory usage          : " << utilities::memoryUsageString( basis.memoryUsage( ) ) << std::endl;

                return os.str( );
            };

            pybindclass.def( "__str__", str );
        }
    };

    auto absBasis = pybind11::class_<AbsBasis<D>, std::shared_ptr<AbsBasis<D>>>( m, add<D>( "AbsBasis" ).c_str( ) );
    
    absBasis.def( "nelements", &AbsBasis<D>::nelements );
    absBasis.def( "ndof", &AbsBasis<D>::ndof );
    absBasis.def_property_readonly( "ndim", []( const AbsBasis<D>& ){ return D; } );
    absBasis.def( "nfields", &AbsBasis<D>::nfields );
    absBasis.def( "mesh", &AbsBasis<D>::meshPtr );
    absBasis.def( "locationMap", &basis::locationMap<D>, pybind11::arg( "icell" ) );
    absBasis.def( "locationMaps", &basis::locationMapVector<D> );
    absBasis.def( "maxdegree", basis::maxdegree<D> );
    absBasis.def( "memoryUsage", &AbsBasis<D>::memoryUsage );

    overloadBasisMembers( absBasis, "AbsBasis" );

    using MlhpBasis = MultilevelHpBasis<D>;
    using MlhpBasisBinding = pybind11::class_<MlhpBasis, AbsBasis<D>, std::shared_ptr<MlhpBasis>>;

    auto defBasisPrint = []<typename Basis, typename... Args>( pybind11::class_<Basis, Args...>& b )
    {
        auto str = []( const Basis& basis )
        {
            std::ostringstream os;

            print( basis, os );

            return os.str( );
        };

        b.def( "__str__", std::move( str ) );
    };

    auto mlhpBasis = MlhpBasisBinding( m, add<D>( "MultilevelHpBasis" ).c_str( ) );
         
    defBasisPrint( mlhpBasis );
    
    overloadBasisMembers( mlhpBasis, "MultilevelHpBasis", false );

    pybind11::implicitly_convertible<size_t, PolynomialDegreeTuple>( );
    pybind11::implicitly_convertible<std::vector<size_t>, PolynomialDegreeTuple>( );

    using FactoryType1 = MultilevelHpBasisSharedPtr<D>( const HierarchicalGridSharedPtr<D>&,
                                                        const PolynomialDegreeTuple&, size_t );
    
    m.def( "makeHpTensorSpace", static_cast<FactoryType1*>( makeHpBasis<TensorSpace> ),
           "Create tensor space multi-level hp basis with uniform polynomial degree distribution.",
           pybind11::arg( "grid" ),  pybind11::arg( "degree" ) = 1, pybind11::arg( "nfields" ) = 1 );

    m.def( "makeHpTrunkSpace", static_cast<FactoryType1*>( makeHpBasis<TrunkSpace> ),
           "Create trunk space multi-level hp basis with uniform polynomial degree distribution.",
           pybind11::arg( "grid" ),  pybind11::arg( "degree" ) = 1, pybind11::arg( "nfields" ) = 1 );

    m.def( "makeHpTensorSpaceFactory", []( std::array<size_t, D> degrees )
           { return makeHpBasisFactory<TensorSpace, D>( degrees ); },
           "Create factory that creates tensor space hp bases with uniform polynomial degree distribution.",
           pybind11::arg( "degrees" ) );

    m.def( "makeHpTrunkSpaceFactory", []( std::array<size_t, D> degrees )
           { return makeHpBasisFactory<TrunkSpace, D>( degrees ); },
           "Create factory that creates trunk space hp bases with uniform polynomial degree distribution.",
           pybind11::arg( "degrees" ) );

    using FactoryType2 = MultilevelHpBasisFactory<D>( const PolynomialDegreeTuple& );

    auto ptr1 = static_cast<FactoryType2*>( makeHpBasisFactory<TensorSpace, D> );
    auto ptr2 = static_cast<FactoryType2*>( makeHpBasisFactory<TrunkSpace, D> );

    m.def( add<D>( "makeHpTensorSpaceFactory" ).c_str( ), ptr1, "Create factory that creates tensor "
           "space hp bases with custom polynomial degree distribution.", pybind11::arg( "degrees" ) );

    m.def( add<D>( "makeHpTrunkSpaceFactory" ).c_str( ), ptr2, "Create factory that creates trunk "
           "space hp bases with custom polynomial degree distribution.", pybind11::arg( "degrees" ) );

    defineBasisFactoryWithGrading<D, UniformGrading>( m );
    defineBasisFactoryWithGrading<D, LinearGrading>( m );
    defineBasisFactoryWithGrading<D, InterpolatedGrading>( m );

    auto count = []( std::array<size_t, D> degrees )
    {
        BooleanMask<D> mask;

        TrunkSpace::initialMaskProvider<D>( )( mask, degrees );

        return std::accumulate( mask.begin( ), mask.end( ), std::uint64_t { 0 } );
    };

    m.def( "countTrunkSpaceDofs", count, "Number element dofs using trunk space.", pybind11::arg( "degrees" ) );

    m.def( "additiveSchwarzPreconditioner", []( const linalg::UnsymmetricSparseMatrix& matrix,
                                                const AbsBasis<D>& basis,
                                                const DofIndexVector& dirichletDofs )
           { return makeAdditiveSchwarzPreconditioner( matrix, basis, dirichletDofs ); },
           pybind11::arg( "matrix" ), pybind11::arg( "basis" ), 
           pybind11::arg( "dirichletDofs" ) = DofIndexVector { } );

    auto bsplineBasis = pybind11::class_<BSplineBasis<D>, AbsBasis<D>, 
        std::shared_ptr<BSplineBasis<D>>>( m, add<D>( "BSplineBasis" ).c_str( ) );
      
    defBasisPrint( bsplineBasis );
    
    using BSplineArg = std::variant<size_t, std::array<size_t, D>, std::vector<std::array<size_t, D>>>;

    auto makeBSplineBasisF = []( std::shared_ptr<const CartesianGrid<D>> grid,
                                 BSplineArg degree,
                                 std::optional<BSplineArg> continuity,
                                 size_t nfields )
    {
        auto convertArg = [&]( auto& arg ) -> std::vector<std::array<size_t, D>>
        {
            if( arg.index( ) == 2 )
            {
                return std::get<2>( arg );
            }
            if( arg.index( ) == 1 )
            {
                return std::vector<std::array<size_t, D>>( nfields, std::get<1>( arg ) );
            }
            else//( std::holds_alternative<0>( arg ) )
            {
                return std::vector<std::array<size_t, D>>( nfields, array::make<D>( std::get<0>( arg ) ) );
            }
        };

        auto degrees = convertArg( degree );
        auto continuities = std::vector<std::array<size_t, D>> { };

        if( !continuity )
        {
            for( auto& p : degrees )
            {
                MLHP_CHECK( array::minElement( p ) > 0, "Zero polynomial degree." );

                continuities.push_back( array::subtract( p, size_t{ 1 } ) );
            }
        }
        else
        {
            continuities = convertArg( *continuity );
        }

        return std::make_shared<BSplineBasis<D>>( grid, degrees, continuities );
    };

    m.def( "makeBSplineBasis", makeBSplineBasisF, pybind11::arg( "grid" ), pybind11::arg( "degree" ), 
           pybind11::arg( "continuity" ) = std::nullopt, pybind11::arg( "nfields" ) = 1 );

    auto unstructuredBasis = pybind11::class_<UnstructuredBasis<D>, AbsBasis<D>, 
        std::shared_ptr<UnstructuredBasis<D>>> ( m, add<D>( "UnstructuredBasis" ).c_str( ) );

    defBasisPrint( unstructuredBasis );
   
    overloadBasisMembers( unstructuredBasis, "UnstructuredBasis" );

    m.def( "makeUnstructuredBasis", []( const std::shared_ptr<UnstructuredMesh<D>>& mesh,
                                        size_t nfields )
        { return std::make_shared<UnstructuredBasis<D>>( mesh, nfields ); },
        pybind11::arg( "mesh" ), pybind11::arg( "nfields" ) = 1 );

    pybind11::class_<ElementFilterBasis<D>, std::shared_ptr<ElementFilterBasis<D>>, AbsBasis<D>>
        elementFilterBasis( m, add<D>( "ElementFilterBasis" ).c_str( ) );

    auto makeFilteredBasisF = []( const std::shared_ptr<const AbsBasis<D>>& basis,
                                  const std::shared_ptr<const AbsFilteredMesh<D>>& filteredMesh )
    {
        return std::make_shared<ElementFilterBasis<D>>( basis, filteredMesh );
    };

    m.def( "makeFilteredBasis", makeFilteredBasisF, pybind11::arg( "basis" ), pybind11::arg( "filteredMesh" ) );

    overloadBasisMembers( elementFilterBasis, "ElementFilterBasis" );

    pybind11::class_<DummyBasis<D>, std::shared_ptr<DummyBasis<D>>, AbsBasis<D>> 
        dummyBasis( m, add<D>( "DummyBasis" ).c_str( ) );

    overloadBasisMembers( dummyBasis, "DummyBasis" );

    auto makeDummyBasisF = []( std::shared_ptr<const AbsMesh<D>> mesh, size_t nfields )
    { 
        return std::make_shared<DummyBasis<D>>( mesh, nfields );
    };

    m.def( "makeDummyBasis", makeDummyBasisF, pybind11::arg( "mesh" ), pybind11::arg( "nfields" ) = 1 );

    auto scalarEvaluatorF1 = []( BasisConstSharedPtr<D> basis, const DoubleVector& dofs, size_t ifield, size_t diffOrder, size_t icomponent )
    {
        return ScalarFunctionWrapper<D> { basis::scalarEvaluator<D>( std::move( basis ), dofs.getShared( ), ifield, diffOrder, icomponent ) };
    };

    m.def( "scalarEvaluator", scalarEvaluatorF1, pybind11::arg( "basis" ),
        pybind11::arg( "dofs" ), pybind11::kw_only( ), pybind11::arg( "ifield" ) = 0, 
        pybind11::arg( "difforder" ) = 0, pybind11::arg( "icomponent" ) = 0 );

    pybind11::class_<basis::EvaluatorComponent<D>>( m, add<D>( "_EvaluatorComponent" ).c_str( ) );

    auto evaluatorComponentF = []( size_t ifield, std::array<size_t, D> diffIndices, double outside )
    { 
        return basis::EvaluatorComponent<D> { .ifield = ifield, .defaultValue = outside, .diffIndices = diffIndices };
    };

    m.def( "evaluatorComponent", evaluatorComponentF, pybind11::kw_only( ), 
        pybind11::arg( "ifield" ), pybind11::arg( "diff" ), pybind11::arg( "outside" ) );

    auto vectorEvaluatorF1 = []( BasisConstSharedPtr<D> basis, const DoubleVector& dofs, size_t difforder )
    {
        return basis::vectorEvaluator<D>( std::move( basis ), dofs.getShared( ), difforder );
    };

    auto vectorEvaluatorF2 = []( BasisConstSharedPtr<D> basis, 
                                 const DoubleVector& dofs, 
                                 std::vector<basis::EvaluatorComponent<D>>&& components )
    {
        return basis::vectorEvaluator<D>( std::move( basis ), dofs.getShared( ), std::move( components ) );
    };

    m.def( "vectorEvaluator", vectorEvaluatorF1, pybind11::arg( "basis" ), 
           pybind11::arg( "dofs" ), pybind11::kw_only( ), pybind11::arg( "difforder" ) = 0 );
    
    m.def( "vectorEvaluator", vectorEvaluatorF2, pybind11::arg( "basis" ), 
           pybind11::arg( "dofs" ), pybind11::kw_only( ), pybind11::arg( "components" ) );

    auto findSupportElementsF = []( const AbsBasis<D>& basis, 
                                    const std::vector<DofIndex>& dofIndices, 
                                    bool linearizeLists ) ->
        std::variant<LinearizedVectors<CellIndex>, std::vector<std::vector<CellIndex>>>
    {
        auto supports = basis::findSupportElements<D>( basis, dofIndices );
        auto result = std::vector<std::vector<CellIndex>> { };

        if( linearizeLists )
        {
            return supports;
        }

        for( size_t i = 0; i < dofIndices.size( ); ++i )
        {
            auto view = utilities::linearizedSpan( supports, i );

            result.emplace_back( view.begin( ), view.end( ) );
        }

        return result;
    };

    m.def( "findSupportElements", findSupportElementsF, pybind11::arg( "basis" ), pybind11::arg( "dofIndices" ),
       pybind11::kw_only( ), pybind11::arg( "linearizeLists" ) = false );

    m.def( "findSupportedDofs", &basis::findSupportedDofs<D>, pybind11::arg( "basis" ),
        pybind11::arg( "cellIndices" ), pybind11::arg( "dirichletIndices" ) = std::vector<CellIndex> { }, 
        pybind11::kw_only( ), pybind11::arg( "exclusive" ) = false, pybind11::arg( "invert" ) = false );
}

template<size_t D>
void definePartitioners( pybind11::module& m )
{
    pybind11::class_<AbsQuadrature<D>, std::shared_ptr<AbsQuadrature<D>>> absQuadrature( m, 
        add<D>( "AbsQuadrature" ).c_str( ) );

    pybind11::class_<EvaluateQuadraturePartition<D>, std::shared_ptr<EvaluateQuadraturePartition<D>>>
        qudraturePartition( m, add<D>( "QuadraturePartition" ).c_str( ) );

    qudraturePartition.def_readwrite( "rst", &EvaluateQuadraturePartition<D>::rst );
    qudraturePartition.def_readwrite( "xyz", &EvaluateQuadraturePartition<D>::xyz );
    qudraturePartition.def_readwrite( "weights", &EvaluateQuadraturePartition<D>::weights );
    qudraturePartition.def_readwrite( "isgrid", &EvaluateQuadraturePartition<D>::isgrid );
    qudraturePartition.def_readwrite( "icell", &EvaluateQuadraturePartition<D>::icell );

    auto evaluateF = pybind11::overload_cast<const AbsQuadrature<D>&, const AbsMesh<D>&, 
        CellIndex, std::array<size_t, D>>( &evaluateQuadrature<D> );

    absQuadrature.def( "evaluate", evaluateF, pybind11::arg( "mesh" ), 
        pybind11::arg( "icell" ), pybind11::arg( "orders" ) );

    pybind11::class_<StandardQuadrature<D>, AbsQuadrature<D>, std::shared_ptr<
        StandardQuadrature<D>>>(m, add<D>("StandardQuadrature").c_str( ));

    pybind11::class_<GridQuadrature<D>, AbsQuadrature<D>, std::shared_ptr<
        GridQuadrature<D>>>( m, add<D>( "GridQuadrature" ).c_str( ) );

    pybind11::class_<SpaceTreeQuadrature<D>, AbsQuadrature<D>, std::shared_ptr<
        SpaceTreeQuadrature<D>>>( m, add<D>( "SpaceTreeQuadrature" ).c_str( ) );

    pybind11::class_<MomentFittingQuadrature<D>, AbsQuadrature<D>, std::shared_ptr<
        MomentFittingQuadrature<D>>>( m, add<D>( "MomentFittingQuadrature" ).c_str( ) );

    pybind11::class_<MeshProjectionQuadrature<D>, AbsQuadrature<D>, std::shared_ptr<
        MeshProjectionQuadrature<D>>>( m, add<D>( "MeshProjectionQuadrature" ).c_str( ) );

    pybind11::class_<CellmeshQuadrature<D>, AbsQuadrature<D>, std::shared_ptr<
        CellmeshQuadrature<D>>>( m, add<D>( "CellmeshQuadrature" ).c_str( ) );

    auto gridQuadratureF1 = []( std::array<size_t, D> nsubcells, const ScalarFunctionWrapper<D>& weight )
    { 
        return std::make_shared<GridQuadrature<D>>( nsubcells, weight.get( ) );
    };

    m.def( "gridQuadrature", gridQuadratureF1, pybind11::arg( "nsubcells" ) = array::makeSizes<D>( 1 ),
           pybind11::arg( "weight" ) = ScalarFunctionWrapper<D> { spatial::constantFunction<D>( 1.0 ) } );
    
    auto gridQuadratureF2 = []( std::shared_ptr<const AbsHierarchicalGrid<D>> grid, 
                                std::array<size_t, D> rootsubcells,
                                const ScalarFunctionWrapper<D>& weight,
                                std::optional<std::array<size_t, D>> maxsubcells )
    { 
        return maxsubcells ? std::make_shared<GridQuadrature<D>>( std::move( grid ), rootsubcells, *maxsubcells, weight.get( ) ) :
                             std::make_shared<GridQuadrature<D>>( std::move( grid ), rootsubcells, weight.get( ) );
    };

    m.def( "gridQuadrature", gridQuadratureF2, pybind11::arg( "grid" ), pybind11::arg( "rootsubcells" ) =
           array::makeSizes<D>( 1 ), pybind11::arg( "maxsubcells" ) = std::nullopt, 
           pybind11::arg( "weight" ) = ScalarFunctionWrapper<D> { spatial::constantFunction<D>( 1.0 ) } );
    
    m.def( "spaceTreeQuadrature", []( const ImplicitFunctionWrapper<D>& function, size_t depth, double epsilon, size_t nseedpoints )
           { return std::make_shared<SpaceTreeQuadrature<D>>( function, epsilon, depth, nseedpoints ); },
           pybind11::arg( "function" ), pybind11::arg( "depth" ), 
           pybind11::arg( "epsilon" ) = 1.0, pybind11::arg( "nseedpoints" ) = 5 );
    
    m.def( "momentFittingQuadrature", []( const ImplicitFunctionWrapper<D>& function, size_t depth,
                                          double epsilon, size_t nseedpoints, QuadratureOrderDeterminorWrapper<D> cutOrders )
           { return std::make_shared<MomentFittingQuadrature<D>>( function, epsilon, depth, nseedpoints, cutOrders.get( ) ); },
           pybind11::arg( "function" ), pybind11::arg( "depth" ), pybind11::arg( "epsilon" ) = 1.0, pybind11::kw_only( ),
           pybind11::arg( "nseedpoints" ) = 5, pybind11::arg( "cutOrders" ) = 
               QuadratureOrderDeterminorWrapper<D> { relativeQuadratureOrder<D>( 0, 2.0 ) } );

    auto meshProjectionQuadratureF = []( std::shared_ptr<const AbsHierarchicalGrid<D>> grid,
                                         std::shared_ptr<const AbsQuadrature<D>> quadrature,
                                         size_t maxdepth )
    { 
        return std::make_shared<MeshProjectionQuadrature<D>>( std::move( grid ), std::move( quadrature ), maxdepth );
    };

    m.def( "meshProjectionQuadrature", meshProjectionQuadratureF,
           pybind11::arg( "grid" ), pybind11::arg( "quadrature" ) = StandardQuadrature<D> { },
           pybind11::arg( "maxdepth" ) = NoValue<size_t> );

    m.def( "cellMeshQuadrature", []( const CellMeshCreatorWrapper<D>& meshCreator,
                                     const ScalarFunctionWrapper<D>& weight )
           { return std::make_shared<CellmeshQuadrature<D>>( meshCreator.get( ), weight.get( ) ); },
           pybind11::arg( "meshCreator" ), pybind11::arg( "weight" ) = 
           ScalarFunctionWrapper<D> { spatial::constantFunction<D>( 1.0 ) } );
    
    pybind11::class_<CachedQuadrature<D>, AbsQuadrature<D>, std::shared_ptr<
        CachedQuadrature<D>>>( m, add<D>( "CachedQuadrature" ).c_str( ) );

    auto cachedQuadratureF = []( const AbsMesh<D>& mesh, size_t degree, const AbsQuadrature<D>& partitioner )
    {
        return CachedQuadrature<D>( mesh, std::vector<std::array<size_t, D>>( 
            mesh.ncells( ), array::make<D>( degree ) ), partitioner );
    };

    m.def( "cachedQuadrature", cachedQuadratureF, pybind11::arg( "mesh" ), 
        pybind11::arg( "polynomialDegree" ), pybind11::arg( "partitioner" ) );
}

template<size_t D>
using SharedQuadrature = std::shared_ptr<AbsQuadrature<D>>;

void definePartitionersSingle( pybind11::module& m )
{
    using QuadratureVariant = DimensionVariant<SharedQuadrature>;
        
    auto standardQuadratureF = []( size_t ndim )
    { 
        auto create = [&]<size_t D>( ) -> QuadratureVariant {
            return std::make_shared<StandardQuadrature<D>>( ); };

        return dispatchDimension( create, ndim );
    };

    m.def( "standardQuadrature", standardQuadratureF, pybind11::arg( "ndim" ) );
}

void defineFunctionWrappersSingle( pybind11::module& m )
{
    defineFunctionWrapper<RealFunction, RealFunctionTag>( m, "RealFunction", true );
    defineFunctionWrapper<RealFunctionWithDerivative, RealFunctionTag>( m, "RealFunctionWithDerivative", true );
   
    auto parseExtrapolate = []( std::string&& extrapolate ) -> interpolation::Extrapolate
    {
        for( char&c : extrapolate ) c = std::tolower( c );

        if( extrapolate == "default" ) return interpolation::Extrapolate::Default;
        if( extrapolate == "constant" ) return interpolation::Extrapolate::Constant;
        if( extrapolate == "linear" ) return interpolation::Extrapolate::Linear;

        MLHP_THROW( "Invalid extrapolation string \"" + extrapolate + 
            "\". Available"" are default, constant, and linear." );
    };
    
    auto constantInterpolationF = [=]( const std::vector<double>& positions,
                                       const std::vector<double>& values )
    {
        return RealFunctionWithDerivativeWrapper { 
            interpolation::makeConstantInterpolation( positions, values ) };
    };
    
    auto linearInterpolationF = [=]( const std::vector<double>& positions,
                                     const std::vector<double>& values,
                                     std::string extrapolate )
    {
        return RealFunctionWithDerivativeWrapper { interpolation::makeLinearInterpolation( 
            positions, values, parseExtrapolate( std::move( extrapolate ) ) ) };
    };
    
    auto splineInterpolationF = [=]( const std::vector<double>& positions,
                                     const std::vector<double>& values,
                                     size_t degree,
                                     std::string extrapolate )
    {
        return RealFunctionWithDerivativeWrapper { interpolation::makeBSplineInterpolation( 
            positions, values, degree, parseExtrapolate( std::move( extrapolate ) ) ) };
    };
    
    auto hermiteInterpolationF = [=]( const std::vector<double>& positions,
                                      const std::vector<double>& values,
                                      const std::vector<double>& derivatives,
                                      std::string extrapolate )
    {
        return RealFunctionWithDerivativeWrapper { interpolation::makeCubicHermiteSpline( 
            positions, values, derivatives, parseExtrapolate( std::move( extrapolate ) ) ) };
    };
    
    m.def( "constantInterpolation", constantInterpolationF,
        pybind11::arg( "positions" ), pybind11::arg( "values" ) );

    m.def( "linearInterpolation", linearInterpolationF, pybind11::arg( "positions" ), 
        pybind11::arg( "values" ), pybind11::arg( "extrapolate" ) = "linear" );

    m.def( "splineInterpolation", splineInterpolationF, pybind11::arg( "positions" ), 
        pybind11::arg( "values" ), pybind11::arg( "degree" ) = 3,
        pybind11::arg( "extrapolate" ) = "linear" );
    
    m.def( "hermiteInterpolation", hermiteInterpolationF, pybind11::arg( "positions" ), 
        pybind11::arg( "values" ), pybind11::arg( "derivatives" ), 
        pybind11::arg( "extrapolate" ) = "linear" );

    auto scaleFunctionF = []( const RealFunctionWithDerivativeWrapper& interpolation, double scaling )
    {
        return RealFunctionWithDerivativeWrapper { [=, f = interpolation.get( )]( double x )
        {
            return f( x ) * scaling;
        } };
    };

    m.def( "scaleFunction", scaleFunctionF, pybind11::arg( "function" ), pybind11::arg( "scaling" ) );
}

template<size_t D>
void defineIntegrands( pybind11::module& m )
{
    if constexpr( D == 1 )
    {
        pybind11::enum_<AssemblyType>( m, "AssemblyType" )
            .value( "Scalar", AssemblyType::Scalar )
            .value( "Vector", AssemblyType::Vector )
            .value( "UnsymmetricMatrix", AssemblyType::UnsymmetricMatrix )
            .value( "SymmetricMatrix", AssemblyType::SymmetricMatrix );
    }

    auto maxdiff1 = []( const DomainIntegrand<D>& I ) { return static_cast<int>( I.maxdiff ); };
    auto maxdiff2 = []( DomainIntegrand<D>& I, int maxdiff ) { I.maxdiff = static_cast<DiffOrders>( maxdiff ); };

    pybind11::class_<DomainIntegrand<D>>( m, add<D>( "DomainIntegrand" ).c_str( ) )
        .def_readwrite( "types", &DomainIntegrand<D>::types, "Assembly target types." )
        .def_property( "maxdiff", maxdiff1, maxdiff2, "Highest shape function derivative." );

    pybind11::class_<KinematicEquation<D>, std::shared_ptr<KinematicEquation<D>>>( m, add<D>( "KinematicEquation" ).c_str( ) )
        .def_readonly( "nfields", &KinematicEquation<D>::nfields )
        .def_readonly( "ncomponents", &KinematicEquation<D>::ncomponents )
        .def_readwrite( "largestrain", &KinematicEquation<D>::largestrain )
        .def_readwrite( "name", &KinematicEquation<D>::name );

    pybind11::class_<ConstitutiveEquation<D>, std::shared_ptr<ConstitutiveEquation<D>>>( m, add<D>( "ConstitutiveEquation" ).c_str( ) )
        .def_readonly( "ncomponents", &ConstitutiveEquation<D>::ncomponents )
        .def_readwrite( "symmetric", &ConstitutiveEquation<D>::symmetric )
        .def_readwrite( "incremental", &ConstitutiveEquation<D>::incremental )
        .def_readwrite( "name", &ConstitutiveEquation<D>::name );

    m.def( "poissonIntegrand", []( const ScalarFunctionWrapper<D>& kappa,
                                   const ScalarFunctionWrapper<D>& source )
        { return makePoissonIntegrand<D>( kappa, source ); }, 
        pybind11::arg( "conductivity" ), pybind11::arg( "source" ) );

    auto makeL2DomainIntegrandF1 = []( std::optional<ScalarFunctionWrapper<D>> rhs,
                                       std::optional<ScalarFunctionWrapper<D>> mass,
                                       std::optional<std::reference_wrapper<DoubleVector>> dofs,
                                       size_t ifield )
    {
        return makeL2DomainIntegrand<D>
        ( 
            mass ? std::optional { mass->get( ) } : std::nullopt,
            rhs ? std::optional { rhs->get( ) } : std::nullopt,
            dofs ? dofs->get( ).getShared( ) : nullptr, 
            ifield 
        );
    };

    m.def( "l2DomainIntegrand", makeL2DomainIntegrandF1, pybind11::arg( "rhs" ) = std::nullopt,
        pybind11::arg( "mass" ) = ScalarFunctionWrapper<D> { spatial::constantFunction<D>( 1.0 ) },
        pybind11::arg( "dofs" ) = std::nullopt, pybind11::arg( "ifield" ) = 0 );

    auto makeL2DomainIntegrandF2 = []( std::optional<spatial::VectorFunction<D>> rhs,
                                       std::optional<spatial::VectorFunction<D>> mass,
                                       std::optional<std::reference_wrapper<DoubleVector>> dofs )
    {
        return makeL2DomainIntegrand<D>( mass, rhs, dofs ? dofs->get( ).getShared( ) : nullptr );
    };

    m.def( "l2DomainIntegrand", makeL2DomainIntegrandF2, pybind11::arg( "rhs" ) = std::nullopt, 
           pybind11::arg( "mass" ) = std::nullopt, pybind11::arg( "dofs" ) = std::nullopt );

    m.def( "functionIntegrand", []( const ScalarFunctionWrapper<D>& function )
        { return makeFunctionIntegrand<D>( function ); }, pybind11::arg( "function" ) );
    
    m.def( "functionIntegrand", pybind11::overload_cast<const spatial::VectorFunction<D>&>( 
        &makeFunctionIntegrand<D> ), pybind11::arg( "function" ) );

    m.def( "l2ErrorIntegrand", []( const DoubleVector& dofs,
                                   const ScalarFunctionWrapper<D>& solution )
        { return makeL2ErrorIntegrand<D>( dofs.getShared( ), solution ); }, 
           pybind11::arg( "dofs" ), pybind11::arg( "solution" ) );

    m.def( "energyErrorIntegrand", []( const DoubleVector& dofs,
                                       const spatial::VectorFunction<D>& derivatives )
        { return makeEnergyErrorIntegrand<D>( dofs.getShared( ), derivatives ); },
           pybind11::arg( "dofs" ), pybind11::arg( "derivatives" ) );

    m.def( "staticDomainIntegrand", []( std::shared_ptr<const KinematicEquation<D>> kinematics,
                                        std::shared_ptr<const ConstitutiveEquation<D>> constitutive,
                                        const spatial::VectorFunction<D>& rhs )
        { return makeStaticDomainIntegrand<D>( kinematics, constitutive, rhs ); },
        pybind11::arg( "kinematics" ), pybind11::arg( "constitutive" ),
        pybind11::arg( "source") = spatial::VectorFunction<D> { spatial::constantFunction<D>( array::make<D>( 0.0 ) ) } );

    m.def( "staticDomainIntegrand", []( std::shared_ptr<const KinematicEquation<D>> kinematics,
                                        std::shared_ptr<const ConstitutiveEquation<D>> constitutive,
                                        const DoubleVector& dofs,
                                        const spatial::VectorFunction<D>& rhs,
                                        bool computeTangent )
        { return makeStaticDomainIntegrand<D>( kinematics, constitutive, dofs.getShared( ), rhs, computeTangent ); },
        pybind11::arg( "kinematics" ), pybind11::arg( "constitutive" ), pybind11::arg( "dofs" ),
        pybind11::arg( "source") = spatial::VectorFunction<D> { spatial::constantFunction<D>( array::make<D>( 0.0 ) ) },
        pybind11::arg( "computeTangent" ) = true );

    auto internalEnergyIntegrandF = []( const DoubleVector& dofs, 
                                        std::shared_ptr<const KinematicEquation<D>> kinematics,
                                        std::shared_ptr<const ConstitutiveEquation<D>> constitutive )
    {
        return makeInternalEnergyIntegrand<D>( dofs.getShared( ), kinematics, constitutive );
    };

    m.def( "internalEnergyIntegrand", internalEnergyIntegrandF, pybind11::arg( "dofs" ), 
        pybind11::arg( "kinematics" ), pybind11::arg( "constitutive" ) );

    if constexpr( D == 3 )
    {
        m.def( "isotropicElasticMaterial", []( const ScalarFunctionWrapper<3>& E,
                                               const ScalarFunctionWrapper<3>& nu )
            { return makeIsotropicElasticMaterial( E, nu ); } );
    }

    if constexpr( D == 2 )
    {
        m.def( "planeStressMaterial", []( const ScalarFunctionWrapper<D>& E,
                                          const ScalarFunctionWrapper<D>& nu )
            { return makePlaneStressMaterial( E, nu ); } );

        m.def( "planeStrainMaterial", []( const ScalarFunctionWrapper<D>& E,
                                          const ScalarFunctionWrapper<D>& nu )
            { return makePlaneStrainMaterial( E, nu ); } );
    }

    pybind11::class_<BasisProjectionIntegrand<D>>( m, add<D>( "BasisProjectionIntegrand" ).c_str( ) );

    m.def( "transientPoissonIntegrand", []( const ScalarFunctionWrapper<D + 1>& capacity,
                                            const ScalarFunctionWrapper<D + 1>& diffusivity,
                                            const ScalarFunctionWrapper<D + 1>& source,
                                            const DoubleVector& dofs,
                                            std::array<double, 2> timeStep,
                                            double theta )
        { return makeTransientPoissonIntegrand<D>( capacity, diffusivity, source, dofs.getShared( ), timeStep, theta ); } ); 

}

void defineIntegrandsSingle( pybind11::module& m )
{
    using BasisProjectionVariant = DimensionVariant<BasisProjectionIntegrand>;

    auto l2BasisProjectionIntegrandD = []( size_t ndim, const DoubleVector& dofs )
    { 
        auto create = [&]<size_t D>( ) -> BasisProjectionVariant {
            return makeL2BasisProjectionIntegrand<D>( dofs.getShared( ) ); };

        return dispatchDimension( create, ndim );
    };

    m.def( "l2BasisProjectionIntegrand", l2BasisProjectionIntegrandD,
        pybind11::arg( "ndim" ), pybind11::arg( "dofs" ) );
    
    using KinematicsVariant = DimensionVariant<KinematicEquation>;

    auto smallStrainKinematicsF = []( size_t ndim )
    { 
        auto create = [&]<size_t D>( ) -> KinematicsVariant {
            return makeSmallStrainKinematics<D>( ); };

        return dispatchDimension( create, ndim );
    };

    m.def( "smallStrainKinematics", smallStrainKinematicsF, pybind11::arg( "ndim" ) );
}

std::array<DoubleVector, 2> splitF( const DoubleVector& dofVector,
                                    const std::vector<DofIndex>& indices )
{
    auto& dofs = dofVector.get( );

    if( dofs.empty( ) )
    {
        MLHP_CHECK( indices.empty( ), "Empty dof vector with non-empty index vector." );

        return { };
    }

    if( indices.empty( ) )
    {
        return { DoubleVector { }, DoubleVector { dofs } };
    }

    auto max = std::max_element( indices.begin( ), indices.end( ) );

    MLHP_CHECK( *max < dofs.size( ), "Index " + std::to_string( *max ) + " at position " + 
        std::to_string( std::distance( indices.begin( ), max ) ) + " exceeds vector size of " + 
        std::to_string( dofs.size( ) ) + "." );

    auto mask = algorithm::indexMask( indices, dofs.size( ) );
    auto size0 = static_cast<size_t>( std::count( mask.begin( ), mask.end( ), size_t { 0 } ) );
    auto values0 = std::vector<double>( size0 );
    auto values1 = std::vector<double>( dofs.size( ) - size0 );

    size_t count0 = 0, count1 = 0;

    for( size_t idof = 0; idof < dofs.size( ); ++idof )
    {
        if( !mask[idof] )
        {
            values0[count0++] = dofs[idof];
        }
        else
        {
            values1[count1++] = dofs[idof];
        }
    }

    return { std::move( values1 ), std::move( values0 ) };
}

void bindLinalg( pybind11::module& m )
{
    auto absSparseMatrix = pybind11::class_<linalg::AbsSparseMatrix, 
        std::shared_ptr<linalg::AbsSparseMatrix>>( m, "AbsSparseMatrix" );

    auto view1d = []<typename T>( T* ptr, size_t size ) 
    { 
        return pybind11::memoryview::from_buffer( ptr, sizeof( T ), 
            pybind11::format_descriptor<T>::value, { size }, { sizeof( T ) } );
    };

    auto indptr_buffer = [=]( linalg::AbsSparseMatrix& M ) { return view1d( M.indptr( ), M.size1( ) + 1 ); };
    auto indices_buffer = [=]( linalg::AbsSparseMatrix& M ) { return view1d( M.indices( ), M.nnz( ) ); };
    auto data_buffer = [=]( linalg::AbsSparseMatrix& M ) { return view1d( M.data( ), M.nnz( ) ); };

    auto indptr_address = []( linalg::AbsSparseMatrix& M ) { return reinterpret_cast<std::uintptr_t>( M.indptr( ) ); };
    auto indices_address = []( linalg::AbsSparseMatrix& M ) { return reinterpret_cast<std::uintptr_t>( M.indices( ) ); };
    auto data_address = []( linalg::AbsSparseMatrix& M ) { return reinterpret_cast<std::uintptr_t>( M.data( ) ); };

    auto indptr_array = []( const linalg::AbsSparseMatrix& M ) { return pybind11::array( static_cast<pybind11::ssize_t>( M.size1( ) + 1 ), M.indptr( ), pybind11::none( ) ); };
    auto indices_array = []( const linalg::AbsSparseMatrix& M ) { return pybind11::array( static_cast<pybind11::ssize_t>( M.nnz( ) ), M.indices( ), pybind11::none( ) ); };
    auto data_array = []( const linalg::AbsSparseMatrix& M ) { return pybind11::array( static_cast<pybind11::ssize_t>( M.nnz( ) ), M.data( ), pybind11::none( ) ); };
    
    auto indptr_list = []( const linalg::AbsSparseMatrix& M ){ return std::vector( M.indptr( ), M.indptr( ) + M.size1( ) + 1 ); };
    auto indices_list = []( const linalg::AbsSparseMatrix& M ){ return std::vector( M.indices( ), M.indices( ) + M.nnz( ) ); };
    auto data_list = []( const linalg::AbsSparseMatrix& M ){ return std::vector( M.data( ), M.data( ) + M.nnz( ) ); };
    
    auto shape = []( const linalg::AbsSparseMatrix& M ) { return std::array { M.size1( ), M.size2( ) }; };

    auto multiply = []( const linalg::AbsSparseMatrix& M, const DoubleVector& rhs )
    { 
        auto result = std::vector( M.size1( ), 0.0 );
            
        M.multiply( rhs.get( ).data( ), result.data( ) );

        return DoubleVector { std::move( result ) };
    };

    auto todense = []( const linalg::AbsSparseMatrix& M )
    {
        auto result = linalg::todense( M );

        auto pyshape = { static_cast<pybind11::ssize_t>( M.size1( ) ),
                         static_cast<pybind11::ssize_t>( M.size2( ) ) };

        auto pystrides = { static_cast<pybind11::ssize_t>( sizeof( double ) * M.size2( ) ),
                           static_cast<pybind11::ssize_t>( sizeof( double ) ) };

        return pybind11::array_t<double>( std::move( pyshape ), std::move( pystrides ), result.data( ) );
    };

    auto csrData = [=]( const linalg::AbsSparseMatrix& M )
    { 
        return std::tuple { std::tuple { data_array( M ), indices_array( M ), indptr_array( M ) }, shape( M ) };
    };

    auto getitem = []( const linalg::AbsSparseMatrix& M, std::array<size_t, 2> ij )
    { 
        MLHP_CHECK( ij[0] < M.size1( ), "Index 0 out of bounds." );
        MLHP_CHECK( ij[1] < M.size2( ), "Index 1 out of bounds." );

        return M( ij[0], ij[1] ); 
    };

    auto setitem = []( linalg::AbsSparseMatrix& M, std::array<size_t, 2> ij, double value )
    {
        MLHP_CHECK( ij[0] < M.size1( ), "Index 0 out of bounds." );
        MLHP_CHECK( ij[1] < M.size2( ), "Index 1 out of bounds." );

        auto ptr = M.find( ij[0], ij[1] );

        MLHP_CHECK( ptr != nullptr, "Matrix entry not in sparsity pattern." );

        *ptr = value;
    };

    absSparseMatrix.def( "memoryUsage", &linalg::AbsSparseMatrix::memoryUsage );
    absSparseMatrix.def( "__call__", &linalg::AbsSparseMatrix::operator() );
    absSparseMatrix.def( "__mul__", multiply );
    absSparseMatrix.def( "todense", todense );
    absSparseMatrix.def( "__getitem__", getitem );
    absSparseMatrix.def( "__setitem__", setitem );
    absSparseMatrix.def( "indptr_list", indptr_list );
    absSparseMatrix.def( "indices_list", indices_list );
    absSparseMatrix.def( "data_list", data_list );
    absSparseMatrix.def_property_readonly( "nnz", &linalg::AbsSparseMatrix::nnz );
    absSparseMatrix.def_property_readonly( "indptr_array", indptr_array );
    absSparseMatrix.def_property_readonly( "indices_array", indices_array );
    absSparseMatrix.def_property_readonly( "data_array", data_array );
    absSparseMatrix.def_property_readonly( "csr_arrays", csrData );
    absSparseMatrix.def_property_readonly( "indptr_buffer", indptr_buffer );
    absSparseMatrix.def_property_readonly( "indptr_address", indptr_address );
    absSparseMatrix.def_property_readonly( "indices_buffer", indices_buffer );
    absSparseMatrix.def_property_readonly( "indices_address", indices_address );
    absSparseMatrix.def_property_readonly( "data_buffer", data_buffer );
    absSparseMatrix.def_property_readonly( "data_address", data_address );
    absSparseMatrix.def_property_readonly( "shape", shape );
    absSparseMatrix.def_property_readonly( "symmetricHalf", &linalg::AbsSparseMatrix::symmetricHalf );

    [[maybe_unused]]
    pybind11::class_<linalg::SymmetricSparseMatrix,
        std::shared_ptr<linalg::SymmetricSparseMatrix>>
        symmetricSparse( m, "SymmetricSparseMatrix", absSparseMatrix );

    [[maybe_unused]]
    pybind11::class_<linalg::UnsymmetricSparseMatrix,
        std::shared_ptr<linalg::UnsymmetricSparseMatrix>>
        unsymmetricSparse( m, "UnsymmetricSparseMatrix", absSparseMatrix );
    
    auto matrixStr = []<typename Matrix>( ) { return []( const Matrix& matrix )
    { 
        std::stringstream sstream;

        linalg::print( matrix, sstream );

        return sstream.str( );
    }; };
    
    symmetricSparse.def( "__str__", matrixStr.template operator()<linalg::SymmetricSparseMatrix>( ) );
    symmetricSparse.def( "copy", []( const linalg::SymmetricSparseMatrix M ) { return M; } );
    unsymmetricSparse.def( "__str__", matrixStr.template operator()<linalg::UnsymmetricSparseMatrix>( ) );
    unsymmetricSparse.def( "copy", []( const linalg::UnsymmetricSparseMatrix M ) { return M; } );

    auto extractBlockF = []( const linalg::UnsymmetricSparseMatrix& M,
                             const std::vector<DofIndex>& rowIndices, 
                             const std::vector<DofIndex>& columnIndices )
    { 
        return linalg::extractBlock( M, std::span { rowIndices }, std::span { columnIndices } );
    };

    auto extractBlocksF = []( const linalg::UnsymmetricSparseMatrix& M,
                              const std::vector<DofIndex>& indices0,
                              const std::vector<DofIndex>& indices1 )
    {
        auto sharedBlock = [&]( auto& i0, auto& i1 ) 
        { 
            return std::make_shared<linalg::UnsymmetricSparseMatrix>( 
                linalg::extractBlock( M, std::span { i0 }, std::span { i1 } ) );
        };

        return std::array { std::array { sharedBlock( indices0, indices0 ), sharedBlock( indices0, indices1 ) }, 
                            std::array { sharedBlock( indices1, indices0 ), sharedBlock( indices1, indices1 ) } };
    };

    unsymmetricSparse.def( "extractBlock", extractBlockF, pybind11::arg( "rowIndices" ), pybind11::arg( "columnIndices" ) );
    unsymmetricSparse.def( "extractBlocks", extractBlocksF, pybind11::arg( "indices0" ), pybind11::arg( "indices1" ) );

    using MatrixVariant = std::variant<linalg::UnsymmetricSparseMatrix, linalg::SymmetricSparseMatrix>;

    auto allocateSparseMatrixF = []( std::array<size_t, 2> sizes, size_t nentries, bool symmetric ) -> MatrixVariant
    {
        if( symmetric ) 
        {
            return allocateMatrix<linalg::SymmetricSparseMatrix>( sizes[0], sizes[1], nentries );
        }
        else
        {
            return allocateMatrix<linalg::UnsymmetricSparseMatrix>( sizes[0], sizes[1], nentries );
        }
    };
 
    auto linearOperator = defineFunctionWrapper<linalg::LinearOperator>( m, "LinearOperator" );

    auto callLinearOperatorF1 = []( const LinearOperatorWrapper& self, const DoubleVector& vector )
    { 
        auto result = DoubleVector( vector.size( ), 0.0 );

        self.get( )( vector.get( ).data( ), result.get( ).data( ), vector.size( ) );

        return result;
    };
    
    auto callLinearOperatorF2 = []( const LinearOperatorWrapper& self, std::vector<double> vector )
    { 
        auto result = vector;

        self.get( )( vector.data( ), result.data( ), vector.size( ) );

        return result;
    };
    
    auto callLinearOperatorF3 = []( const LinearOperatorWrapper& self, const pybind11::array_t<double>& vector )
    { 
        auto result = vector;

        self.get( )( vector.data( ), const_cast<double*>( result.data( ) ), static_cast<std::uint64_t>( vector.size( ) ) );

        return result;
    };
    
    auto callLinearOperatorF4 = []( const LinearOperatorWrapper& self, std::uint64_t vector, std::uint64_t target, std::uint64_t n )
    { 
        self.get( )( reinterpret_cast<const double*>( vector ), reinterpret_cast<double*>( target ), n );
    };

    linearOperator->def( "__call__", callLinearOperatorF1, pybind11::arg( "operand" ) );
    linearOperator->def( "__call__", callLinearOperatorF2, pybind11::arg( "operand" ) );
    linearOperator->def( "call_array", callLinearOperatorF3, pybind11::arg( "operand" ) );

    linearOperator->def( "__call__", callLinearOperatorF4, pybind11::arg( "vector_address" ), 
        pybind11::arg( "target_address" ), pybind11::arg( "n" ) );

    auto linearOperatorF1 = []( const std::shared_ptr<const linalg::AbsSparseMatrix>& matrix )
    { 
        return LinearOperatorWrapper { linalg::makeDefaultMultiply( matrix ) };
    };

    auto linearOperatorF2 = []( std::function<std::variant<std::shared_ptr<DoubleVector>, 
        std::vector<double>>( const DoubleVector& vector )> function )
    {
        return LinearOperatorWrapper { [function = std::move( function )] ( const double* vector, 
                                                                            double* target, 
                                                                            std::uint64_t n )
        {
            thread_local auto tmp = DoubleVector( size_t { 0 }, 0.0 );

            tmp.get( ).resize( n );

            std::copy( vector, vector + n, tmp.get( ).begin( ) );

            auto output = function( tmp );

            std::vector<double>* ptr =  nullptr;

            if( std::holds_alternative<std::vector<double>>( output ) )
            {
                ptr = &std::get<std::vector<double>>( output );
            }
            else
            {
                ptr = &std::get<std::shared_ptr<DoubleVector>>( output )->get( );
                
                MLHP_CHECK( ptr, "Linear operator did not return a value." );
            }
            
            MLHP_CHECK( ptr->size( ) == n, "Length of linear operator output inconsistent with input." );

            std::copy( ptr->begin( ), ptr->end( ), target);
        } };
    };

    auto linearOperatorF3 = []( std::function<void( pybind11::array_t<const double> vector,
                                                    pybind11::array_t<double> target )> function )
    {
        return LinearOperatorWrapper { [function = std::move( function )] ( const double* vector, double* target, std::uint64_t n )
        {
            function( pybind11::array_t<const double>( static_cast<pybind11::ssize_t>( n ), vector, pybind11::none( ) ),
                      pybind11::array_t<double>( static_cast<pybind11::ssize_t>( n ), target, pybind11::none( ) ));
        } };
    };
    
    auto linearOperatorF4 = []( std::function<void( std::uint64_t vector, std::uint64_t target, std::uint64_t size )> function )
    {
        return LinearOperatorWrapper { [function = std::move( function )] ( const double* vector, double* target, std::uint64_t n )
        {
            function( reinterpret_cast<std::uint64_t>( vector ), reinterpret_cast<std::uint64_t>( target ), n );
        } };
    };
    
    auto linearOperatorF5 = [=]( std::function<void( pybind11::memoryview vector, pybind11::memoryview target )> function )
    {
        return LinearOperatorWrapper { [=, function = std::move( function )] ( const double* vector, double* target, std::uint64_t n )
        {
            function( view1d( vector, static_cast<size_t> ( n ) ), view1d( target, static_cast<size_t> ( n ) ) );
        } };
    };

    m.def( "linearOperator", linearOperatorF1, pybind11::arg( "matrix" ), "Sparse matrix-vector product." );
    m.def( "linearOperator", linearOperatorF2, pybind11::arg( "function" ), "Linear operator from python function using list." );
    m.def( "linearOperator_array", linearOperatorF3, pybind11::arg( "function" ), "Linear operator from python function using numpy arrays." );
    m.def( "linearOperator_buffer", linearOperatorF5, pybind11::arg( "function" ), "Linear operator from python function using buffers." );

    m.def( "linearOperator_address", linearOperatorF4, pybind11::arg( "function" ), "Linear operator from python function "
           "using vector address, target address, and size (all parameters are 64 bit unsigned integers)." );

    m.def( "allocateSparseMatrix", allocateSparseMatrixF, pybind11::arg( "shape" ), 
        pybind11::arg( "nentries" ), pybind11::arg( "symmetric" ) = false );

    auto doubleVectorWrapper = pybind11::class_<DoubleVector, std::shared_ptr<DoubleVector>>( m, "DoubleVector" );
    auto floatVectorWrapper = pybind11::class_<FloatVector, std::shared_ptr<FloatVector>>( m, "FloatVector" );

    VectorWrapper<double>::bindMembers( doubleVectorWrapper );
    VectorWrapper<float>::bindMembers( floatVectorWrapper );

    [[maybe_unused]]
    pybind11::class_<ScalarDouble> scalarDouble( m, "ScalarDouble" );
    
    scalarDouble.def( pybind11::init<>( ) );
    scalarDouble.def( pybind11::init<double>( ) );
    scalarDouble.def( "get", []( const ScalarDouble& value ) { return value.get( ); } );
    
    auto internalCGF = []( const LinearOperatorWrapper& A,
                           const DoubleVector& b,
                           DoubleVector& x0,
                           double rtol, double atol, size_t maxiter,
                           const LinearOperatorWrapper& M,
                           std::optional<std::shared_ptr<DoubleVector>> tmp )
    {
        return linalg::cg( A, b.get( ), x0.get( ), rtol, atol, maxiter, M, tmp ? ( *tmp )->getShared( ) : nullptr );
    };
    
    auto internalBiCGStabF = []( const LinearOperatorWrapper& A,
                                 const DoubleVector& b,
                                 DoubleVector& x0,
                                 double rtol, double atol, size_t maxiter, 
                                 const LinearOperatorWrapper& M,
                                 std::optional<std::shared_ptr<DoubleVector>> tmp )
    {
        return linalg::bicgstab( A, b.get( ), x0.get( ), rtol, atol, maxiter, M, tmp ? ( *tmp )->getShared( ) : nullptr );
    };

    auto defineInternalIterativeSolve = [&]( const auto& name, auto&& def )
    {
        m.def( name, def, pybind11::arg( "A" ), pybind11::arg( "b" ), pybind11::arg( "x0" ),
            pybind11::arg( "rtol" ), pybind11::arg( "atol" ), pybind11::arg( "maxiter" ), 
            pybind11::arg( "M" ), pybind11::arg( "tmp" ) );
    };

    defineInternalIterativeSolve( "internalCG", internalCGF );
    defineInternalIterativeSolve( "internalBiCGStab", internalBiCGStabF );

    m.def( "noPreconditioner", []( ){ return LinearOperatorWrapper { linalg::makeNoPreconditioner( ) }; } );

    auto diagonalPreconditionerF = []( const linalg::AbsSparseMatrix& matrix,
                                       std::optional<std::shared_ptr<DoubleVector>> tmp )
    { 
        return LinearOperatorWrapper { linalg::makeDiagonalPreconditioner( matrix, tmp ? ( *tmp )->getShared( ) : nullptr ) };
    };

    m.def( "diagonalPreconditioner", diagonalPreconditionerF, pybind11::arg( "matrix" ),
           pybind11::arg( "target" ) = std::nullopt );
    
    auto fillParallel = []( std::span<double> data, double value )
    {
        auto nint = static_cast<std::int64_t>( data.size( ) );

        #pragma omp parallel for schedule(static)
        for( std::int64_t ii = 0; ii < nint; ++ii )
        {
            data[static_cast<size_t>( ii )] = value;
        }
    };

    m.def( "fill", [fillParallel]( linalg::AbsSparseMatrix& matrix, double value )
           { fillParallel( std::span { matrix.data( ), matrix.nnz( ) }, value ); },
           pybind11::arg( "matrix" ), pybind11::arg( "value" ) = 0.0 );

    m.def( "fill", [fillParallel]( DoubleVector& vector, double value )
           { fillParallel( vector.get( ), value ); },
           pybind11::arg( "vector" ), pybind11::arg( "value" ) = 0.0 );
    
    auto copyF1 = []( const DoubleVector& vectorWrapper, double scaling, double offset ) -> DoubleVector
    { 
        auto nint = static_cast<std::int64_t>( vectorWrapper.size( ) );
        auto& source = vectorWrapper.get( );
        auto vector = std::vector<double>( vectorWrapper.size( ) );

        #pragma omp parallel for schedule(static)
        for( std::int64_t ii = 0; ii < nint; ++ii )
        {
            auto i = static_cast<size_t>( ii );

            vector[i] = scaling * source[i] + offset;
        }

        return DoubleVector( std::move( vector ) );
    };

    auto copyF2 = []( const DoubleVector& sourceWrapper, DoubleVector& targetWrapper, double scaling, double offset )
    { 
        MLHP_CHECK( sourceWrapper.size( ) == targetWrapper.size( ), "Inconsistent sizes in add." );

        auto nint = static_cast<std::int64_t>( sourceWrapper.size( ) );
        auto& source = sourceWrapper.get( );
        auto& target = targetWrapper.get( );

        #pragma omp parallel for schedule(static)
        for( std::int64_t ii = 0; ii < nint; ++ii )
        {
            auto i = static_cast<size_t>( ii );

            target[i] = scaling * source[i] + offset;
        }
    };

    m.def( "copy", copyF1, pybind11::arg( "vector" ), pybind11::arg( 
        "scaling" ) = 1.0, pybind11::arg( "offset" ) = 0.0 );
    
    m.def( "copy", copyF2, pybind11::arg( "source" ), pybind11::arg( "target" ), 
        pybind11::arg( "scaling" ) = 1.0, pybind11::arg( "offset" ) = 0.0 );

    auto normF = []( const DoubleVector& vector )
    {
        auto result = 0.0;
        auto nint = static_cast<std::int64_t>( vector.size( ) );

        auto& v = vector.get( );

        #pragma omp parallel for schedule(static) reduction(+:result)
        for( std::int64_t ii = 0; ii < nint; ++ii )
        {
            result += v[static_cast<size_t>( ii )] * v[static_cast<size_t>( ii )];
        }

        return std::sqrt( result );
    };

    m.def( "norm", normF, pybind11::arg( "vector" ) );
    
    m.def( "split", splitF, pybind11::arg( "vector" ), pybind11::arg( "indices" ) );
    
    auto addF = []( const DoubleVector& vector1, 
                    const DoubleVector& vector2,
                    double factor,
                    std::optional<std::shared_ptr<DoubleVector>> out ) -> std::optional<std::shared_ptr<DoubleVector>>
    { 
        if( !out )
        {
            auto result = std::make_shared<DoubleVector>( vector1.size( ) );

            out = std::optional { std::move( result ) };
        }

        MLHP_CHECK( vector1.get( ).size( ) == vector2.get( ).size( ),
                    "Inconsistent vector sizes in add." );
        MLHP_CHECK( vector1.get( ).size( ) == ( *out )->get( ).size( ),
                    "Inconsistent vector sizes in add." );

        auto& v1 = vector1.get( );
        auto& v2 = vector2.get( );
        auto& t = ( *out )->get( );

        auto nint = static_cast<std::int64_t>( v1.size( ) );

        #pragma omp parallel for schedule(static)
        for( std::int64_t ii = 0; ii < nint; ++ii )
        {
            auto i = static_cast<size_t>( ii );

            t[i] = v1[i] + factor * v2[i];
        }

        return out;
    };

    m.def( "add", addF, pybind11::arg( "vector1" ), pybind11::arg( "vector2" ), pybind11::arg(
           "factor" ) = 1.0, pybind11::kw_only( ), pybind11::arg( "out" ) = std::nullopt );
    
    m.def( "inflateDofs", []( const DoubleVector& interiorDofs,
                              const DofIndicesValuesPair& dirichletDofs ) -> DoubleVector
        { return DoubleVector { boundary::inflate( interiorDofs.get( ), dirichletDofs ) }; }, 
        pybind11::arg( "interiorDofs" ), 
        pybind11::arg( "dirichletDofs" ) );
}

template<size_t D>
void defineBoundaryCondition( pybind11::module& m )
{
    QuadratureOrderDeterminorWrapper<D> defaultDeterminor { relativeQuadratureOrder<D>( 1 ) };
    
    m.def( "integrateDirichletDofs", [=]( const spatial::VectorFunction<D>& function,
                                          const AbsBasis<D>& basis, std::vector<size_t> faces,
                                          const QuadratureOrderDeterminorWrapper<D>& orderDeterminor )
        { return boundary::boundaryDofs<D>( function, basis, faces, orderDeterminor ); },
        pybind11::arg( "boundaryFunctions" ), pybind11::arg( "basis" ), pybind11::arg( "faces" ), 
        pybind11::arg( "orderDeterminor" ) = defaultDeterminor );

    m.def( "integrateDirichletDofs", [=]( const ScalarFunctionWrapper<D>& function,
                                          const AbsBasis<D>& basis, std::vector<size_t> faces,
                                          const QuadratureOrderDeterminorWrapper<D>& orderDeterminor,
                                          size_t fieldComponent )
        { return boundary::boundaryDofs<D>( function, basis, faces, orderDeterminor, fieldComponent ); }, 
        pybind11::arg( "boundaryFunctions" ), pybind11::arg( "basis" ), pybind11::arg( "faces" ),
        pybind11::arg( "orderDeterminor" ) = defaultDeterminor, pybind11::arg( "ifield" ) = 0 );
}

void definePostprocessingSingle( pybind11::module& m )
{
    pybind11::enum_<PostprocessTopologies>( m, "PostprocessTopologies" )
        .value( "Nothing", PostprocessTopologies::None )
        .value( "Corners", PostprocessTopologies::Corners )
        .value( "Edges", PostprocessTopologies::Edges )
        .value( "Faces", PostprocessTopologies::Faces )
        .value( "Volumes", PostprocessTopologies::Volumes )
        .def( "__or__", []( PostprocessTopologies a,
                            PostprocessTopologies b )
                            { return a | b; } );

    pybind11::class_<OutputMeshPartition, std::shared_ptr<OutputMeshPartition>>( m, "CellMeshPartition" )
        .def( pybind11::init<CellIndex, std::vector<double>, std::vector<std::int64_t>, 
              std::vector<std::int64_t>, std::vector<std::int8_t>>( ), 
              pybind11::arg( "index" ) = 0, pybind11::arg( "points" ) = std::vector<double> { }, 
              pybind11::arg( "connectivity" ) = std::vector<std::int64_t> { },
              pybind11::arg( "offsets" ) = std::vector<std::int64_t> { 0 }, 
              pybind11::arg( "types" ) = std::vector<std::int8_t> { } )
        .def( "index", []( const OutputMeshPartition& o ){ return o.index; } )
        .def( "points", []( const OutputMeshPartition& o ){ return o.points; } )
        .def( "connectivity", []( const OutputMeshPartition& o ){ return o.connectivity; } )
        .def( "offsets", []( const OutputMeshPartition& o ){ return o.offsets; } )
        .def( "types", []( const OutputMeshPartition& o ){ return o.types; } );

    pybind11::class_<MeshWriter, std::shared_ptr<MeshWriter>>( m, "MeshWriter" );

    auto convertOutput = []<typename T>( ) { return []( T& out )
    {
        return std::make_shared<MeshWriter>( out.operator mlhp::MeshWriter( ) );
    }; };

    pybind11::class_<VtuOutput>( m, "VtuOutput" )
        .def( pybind11::init( []( std::string filename, std::string writemode )
            { return VtuOutput { .filename = filename, .mode = writemode }; } ), 
            pybind11::arg( "filename" ) = "output.vtu",
            pybind11::arg( "writemode" ) = "RawBinaryCompressed" )
        .def( "meshWriter", convertOutput.template operator()<VtuOutput>() );

    pybind11::class_<PVtuOutput>( m, "PVtuOutput" )
        .def( pybind11::init( []( std::string filename, std::string writemode, size_t maxpartitions )
            { return PVtuOutput { .filename = filename, .mode = writemode, .maxpartitions = maxpartitions }; } ),
            pybind11::arg( "filename" ) = "output.vtu",
            pybind11::arg( "writemode" ) = "RawBinaryCompressed",
            pybind11::arg( "maxpartitions" ) = 2 * parallel::getMaxNumberOfThreads( ) )
        .def( "meshWriter", convertOutput.template operator()<PVtuOutput>() );
    
    pybind11::class_<DataAccumulator, std::shared_ptr<DataAccumulator>>( m, "DataAccumulator" )
        .def( pybind11::init<>( ) )
        .def( "mesh", []( const DataAccumulator& d ){ return *d.mesh; } )
        .def( "data", []( const DataAccumulator& d ){ return *d.data; } )
        .def( "meshWriter", convertOutput.template operator()<DataAccumulator>() );
}

template<size_t D>
using ElementProcessorSharedPtr = std::shared_ptr<ElementProcessor<D>>;

template<size_t D>
using CellProcessorSharedPtr = std::shared_ptr<CellProcessor<D>>;

template<size_t D>
void definePostprocessingDimensions( pybind11::module& m )
{
    pybind11::class_<ElementProcessor<D>, std::shared_ptr<ElementProcessor<D>>>
        ( m, add<D>( "ElementProcessor" ).c_str( ) );

    pybind11::class_<CellProcessor<D>, std::shared_ptr<CellProcessor<D>>>
        ( m, add<D>( "CellProcessor" ).c_str( ) );

    m.def( "functionProcessor", []( const ScalarFunctionWrapper<D>& function,
                                    const std::string& name )
           { return std::make_shared<CellProcessor<D>>(
                   makeFunctionProcessor<D>( function.get( ), name ) ); },
           pybind11::arg( "function" ), pybind11::arg( "name" ) );

    m.def( "functionProcessor", []( const ImplicitFunctionWrapper<D>& function,
                                    const std::string& name )
           { return std::make_shared<CellProcessor<D>>(
                   makeFunctionProcessor<D>( function.get( ), name ) ); },
           pybind11::arg( "function" ), pybind11::arg( "name" ) = "Domain" );
     
    auto defDerivativeProcessor = [&]( const std::string& functionName,
                                       const std::string& fieldName,
                                       auto&& create )
    {
        auto gradientProcessorF = [=]( std::array<std::shared_ptr<DoubleVector>, D> gradient,
                                       std::shared_ptr<const KinematicEquation<D>> kinematics,
                                       std::shared_ptr<const ConstitutiveEquation<D>> constitutive,
                                       const std::string& name )
        {
            auto gradientSpan = std::array<std::span<const double>, D> { };

            for( size_t axis = 0; axis < D; ++axis )
            {
                gradientSpan[axis] = gradient[axis]->get( );
            }

            return create( gradientSpan, std::move( kinematics ), std::move( constitutive ), name );
        };

        auto solutionProcessorF = [=]( const DoubleVector& solution,
                                       std::shared_ptr<const KinematicEquation<D>> kinematics,
                                       std::shared_ptr<const ConstitutiveEquation<D>> constitutive,
                                       const std::string& name )
        {
            return create( solution.getShared( ), std::move( kinematics ), std::move( constitutive ), name );
        };

        m.def( functionName.c_str( ), gradientProcessorF, pybind11::arg( "gradient" ),
            pybind11::arg( "kinematics" ), pybind11::arg( "constitutive" ), 
            pybind11::arg( "name" ) = fieldName );

        m.def( functionName.c_str( ), solutionProcessorF, pybind11::arg( "solution" ),
            pybind11::arg( "kinematics" ), pybind11::arg( "constitutive" ), 
            pybind11::arg( "name" ) = fieldName );
    };

    auto stressF = []( auto&&... args ) { return makeStressProcessor<D>( std::forward<decltype( args )>( args )... ); };
    auto vonMisesF = []( auto&&... args ) { return makeVonMisesProcessor<D>( std::forward<decltype( args )>( args )... ); };
    auto strainF = []( auto&&... args ) { return makeStrainProcessor<D>( std::forward<decltype( args )>( args )... ); };
    auto strainEnergyF = []( auto&&... args ) { return makeStrainEnergyProcessor<D>( std::forward<decltype( args )>( args )... ); };

    defDerivativeProcessor( "stressProcessor", "Stress", stressF );
    defDerivativeProcessor( "vonMisesProcessor", "VonMisesStress", vonMisesF );
    defDerivativeProcessor( "strainProcessor", "Strain", strainF );
    defDerivativeProcessor( "strainEnergyProcessor", "StrainEnergyDensity", strainEnergyF );

    if constexpr( D <= 3 )
    {
        defineFunctionWrapper<CellMeshCreator<D>>( m, add<D>( "CellMeshCreator" ).c_str( ) );

        auto defaultMesh = wrapFunction( cellmesh::grid<D>( array::makeSizes<D>( 1 ) ) );
        auto defaultResolution = ResolutionDeterminorWrapper<D> { uniformResolution( array::makeSizes<D>( 1 ) ) };

        m.def( "internalBasisOutput", []( const AbsBasis<D>& basis,
                                          const CellMeshCreatorWrapper<D>& cellmesh,
                                          std::shared_ptr<MeshWriter> writer,
                                          std::vector<ElementProcessor<D>>&& processors )
        {
            writeOutput( basis, cellmesh.get( ), mergeProcessors( std::move( processors ) ), *writer );
        },
        pybind11::arg( "basis" ), pybind11::arg( "cellmesh" ) = defaultMesh,
        pybind11::arg( "output" ), pybind11::arg( "processors" ) = std::vector<ElementProcessor<D>>{ } );

        m.def( "internalMeshOutput", []( const AbsMesh<D>& mesh,
                                         const CellMeshCreatorWrapper<D>& cellmesh,
                                         const MeshWriter& writer,
                                         std::vector<CellProcessor<D>>&& processors )
        {
            writeOutput( mesh, cellmesh.get( ), mergeProcessors( std::move( processors ) ), writer );
        },
        pybind11::arg( "mesh" ), pybind11::arg( "cellmesh" ) = defaultMesh,
        pybind11::arg( "output" ), pybind11::arg( "processors" ) = std::vector<CellProcessor<D>>{ } );

        m.def( "convertToElementProcessor", []( CellProcessor<D> processor ) { return
            convertToElementProcessor<D>( std::move( processor ) ); }, pybind11::arg( "elementProcessor" ) );
        
        defineFunctionWrapper<ResolutionDeterminor<D>>( m, add<D>( "ResolutionDeterminor" ).c_str( ) );

        auto instantiateResoluton = [&]<typename Resolution>( )
        {
            auto createGridOnCellsF = []( Resolution resolution,
                                          PostprocessTopologies topologies )
            {
                return CellMeshCreatorWrapper<D> { cellmesh::grid<D>( resolution, topologies ) };
            };

            m.def( "gridCellMesh", createGridOnCellsF, pybind11::arg( "resolution" ), 
                   pybind11::arg( "topologies" ) = defaultOutputTopologies[D] );

            if constexpr ( D <= 3 )
            {   
                auto createMarchingCubesBoundaryF = []( const ImplicitFunctionWrapper<D>& function,
                                                        Resolution resolution,
                                                        bool recoverMeshBoundaries,
                                                        size_t niterations )
                {
                    return CellMeshCreatorWrapper<D> { cellmesh::boundary<D>( 
                        function, resolution, recoverMeshBoundaries, niterations ) };
                };
        
                auto createMarchingCubesVolumeF = []( const ImplicitFunctionWrapper<D>& function,
                                                      Resolution resolution,
                                                      bool coarsen,
                                                      bool meshBothSides,
                                                      size_t niterations )
                {
                    return CellMeshCreatorWrapper<D> { cellmesh::domain<D>( function.get( ), 
                            resolution, coarsen, meshBothSides, niterations ) };
                };

                m.def( "boundaryCellMesh", createMarchingCubesBoundaryF, pybind11::arg( "function" ),
                        pybind11::arg( "resolution" ) = defaultResolution, pybind11::kw_only( ), 
                        pybind11::arg( "recoverMeshBoundaries" ) = true,
                        pybind11::arg( "niterations" ) = marching::bisectionDefault );
                m.def( "domainCellMesh", createMarchingCubesVolumeF, 
                        pybind11::arg( "function" ), pybind11::arg( "resolution" ) = defaultResolution, pybind11::kw_only( ),
                        pybind11::arg( "coarsen" ) = false, pybind11::arg( "meshBothSides" ) = false,
                        pybind11::arg( "niterations" ) = marching::bisectionDefault );
            }
        };

        instantiateResoluton.template operator()<std::array<size_t, D>>( );
        instantiateResoluton.template operator()<ResolutionDeterminorWrapper<D>>( );

        auto degreeOffsetResolutionF = []( BasisConstSharedPtr<D> basis, size_t offset, bool exceptLinear )
        {
            return ResolutionDeterminorWrapper<D> { degreeOffsetResolution<D>( *basis, offset, exceptLinear ) };
        };

        m.def( "degreeOffsetResolution", degreeOffsetResolutionF, pybind11::arg("basis"),
            pybind11::arg( "offset" ) = 2, pybind11::arg( "exceptLinear" ) = true );

        auto quadraturePointCellMeshF1 = []( const AbsQuadrature<D>& quadrature, const AbsBasis<D>& basis,
                                             const QuadratureOrderDeterminorWrapper<D>& determinor )
        {
            return CellMeshCreatorWrapper<D> { cellmesh::quadraturePoints( quadrature, basis, determinor.get( ) ) };
        };
        
        auto quadraturePointCellMeshF2 = []( const AbsQuadratureOnMesh<D>& quadrature,
                                             const AbsBasis<D>& basis )
        {
            return CellMeshCreatorWrapper<D> { cellmesh::quadraturePoints( quadrature, basis ) };
        };

        m.def( "quadraturePointCellMesh", quadraturePointCellMeshF1, pybind11::arg( "quadrature" ), 
               pybind11::arg( "basis" ), pybind11::arg( "orderDeterminor" ) = 
               QuadratureOrderDeterminorWrapper<D> { relativeQuadratureOrder<D>( ) } );

        m.def( "quadraturePointCellMesh", quadraturePointCellMeshF2, pybind11::arg( "quadrature" ), pybind11::arg( "basis" ) );
    }
}

void definePostprocessingSingle2( pybind11::module& m )
{
    auto solutionProcessorF = []( size_t ndim, const DoubleVector& dofs, const std::string& name )
    { 
        auto create = [&]<size_t D>( ) -> DimensionVariant<ElementProcessorSharedPtr>
        { 
            return utilities::moveShared( makeSolutionProcessor<D>( dofs.getShared( ), name ) );
        };

        return dispatchDimension( create, ndim );
    };
    
    m.def( "solutionProcessor", solutionProcessorF, pybind11::arg( "ndim" ), 
        pybind11::arg( "dofs" ), pybind11::arg( "solutionName" ) = "Solution" );

    auto kdtreeProcessorF = []( size_t ndim )
    { 
        auto create = [&]<size_t D>( ) -> DimensionVariant<CellProcessorSharedPtr>
        { 
            return utilities::moveShared( makeKdTreeInfoProcessor<D>( ) );
        };

        return dispatchDimension( create, ndim );
    };
    
    m.def( "kdTreeInfoProcessor", kdtreeProcessorF, pybind11::arg( "ndim" ) );

    auto customCellMeshF = []( size_t ndim, std::vector<OutputMeshPartition>&& partitions )
    { 
        auto create = [&]<size_t D>( ) -> DimensionVariant<CellMeshCreatorWrapper>
        { 
            return CellMeshCreatorWrapper<D> { cellmesh::custom<D>( std::move( partitions ) ) };
        };

        return dispatchDimension( create, ndim );
    };

    m.def( "customCellMesh", customCellMeshF, pybind11::arg( "ndim" ), pybind11::arg( "partitions" ) );

    auto cellDataProcessorF = []( size_t ndim, const DoubleVector& data, const std::string& name )
    { 
        using CellProcessorVariant = DimensionVariant<CellProcessorSharedPtr>;

        auto create = [&]<size_t D>( ) -> CellProcessorVariant
        { 
            return std::make_shared<CellProcessor<D>>( makeCellDataProcessor<D>( data.getShared( ), name ) );
        };

        return dispatchDimension( create, ndim );
    };

    m.def( "cellDataProcessor", cellDataProcessorF, pybind11::arg( "ndim" ), 
        pybind11::arg( "data" ), pybind11::arg( "name" ) = "CellData" );
}

void defineConfig( pybind11::module& m )
{
    struct Config { };

    auto conf = pybind11::class_<Config>( m, "config" );

    conf.def_property_readonly_static( "commitId",        []( pybind11::object ) { return std::string { config::commitId        }; } );
    conf.def_property_readonly_static( "osName",          []( pybind11::object ) { return std::string { config::osName          }; } );
    conf.def_property_readonly_static( "osVersion",       []( pybind11::object ) { return std::string { config::osVersion       }; } );
    conf.def_property_readonly_static( "architecture",    []( pybind11::object ) { return std::string { config::architecture    }; } );
    conf.def_property_readonly_static( "compilerId",      []( pybind11::object ) { return std::string { config::compilerId      }; } );
    conf.def_property_readonly_static( "compilerVersion", []( pybind11::object ) { return std::string { config::compilerVersion }; } );
    conf.def_property_readonly_static( "compileDate",     []( pybind11::object ) { return std::string { __DATE__                }; } );
    conf.def_property_readonly_static( "compileTime",     []( pybind11::object ) { return std::string { __TIME__                }; } );
    conf.def_property_readonly_static( "threading",       []( pybind11::object ) { return std::string { config::threading       }; } );
    conf.def_property_readonly_static( "maxdim",          []( pybind11::object ) { return config::maxdim; } );
    conf.def_property_readonly_static( "cellIndexSize",   []( pybind11::object ) { return CHAR_BIT * sizeof( CellIndex ); } );
    conf.def_property_readonly_static( "dofIndexSize",    []( pybind11::object ) { return CHAR_BIT * sizeof( DofIndex ); } );
    conf.def_property_readonly_static( "simdAlignment",   []( pybind11::object ) { return config::simdAlignment; } );
    conf.def_property_readonly_static( "debugChecks",     []( pybind11::object ) { return config::debugChecks; } );

    auto getNumThreads = []( pybind11::object ) { return parallel::getMaxNumberOfThreads( ); };
    auto setNumThreads = []( pybind11::object, size_t nthreads ) { parallel::setNumberOfThreads( nthreads ); };

    conf.def_property_static( "numThreads", getNumThreads, setNumThreads, "Wraps calls to omp_set_num_threads and omp_get_max_threads." );

    auto str = []( pybind11::object )
    { 
        auto sstream = std::ostringstream { };
        auto debugChecks = config::debugChecks ? std::string { "On" } : std::string { "Off" };

        sstream << "MLHP python bindings\n";
        sstream << "    Commit ID         : " << config::commitId                   << "\n";
        sstream << "    OS name           : " << config::osName                     << "\n";
        sstream << "    OS version        : " << config::osVersion                  << "\n";
        sstream << "    Architecture      : " << config::architecture               << "\n";
        sstream << "    Compiler ID       : " << config::compilerId                 << "\n";
        sstream << "    Compiler version  : " << config::compilerVersion            << "\n";
        sstream << "    Compilation date  : " << __DATE__                           << "\n";
        sstream << "    Compilation time  : " << __TIME__                           << "\n";
        sstream << "    Highest dimension : " << config::maxdim                     << "\n";
        sstream << "    Cell index size   : " << CHAR_BIT * sizeof( CellIndex )     << "\n";
        sstream << "    Dof index size    : " << CHAR_BIT * sizeof( DofIndex )      << "\n";
        sstream << "    SIMD alignment    : " << config::simdAlignment              << "\n";
        sstream << "    Debug checks      : " << debugChecks                        << "\n";
        sstream << "    Multi-threading   : " << config::threading                  << "\n";
        sstream << "    Number of threads : " << parallel::getMaxNumberOfThreads( ) << "\n";

        return sstream.str( );
    };

    auto call = [=]( pybind11::object obj )
    {
        pybind11::print( str( obj ) );
    };

    conf.def( "__str__", str );
    conf.def( "__call__", call );

    static constexpr Config obj;

    m.attr( "config" ) = &obj;
}

void defineDimensionIndendent( pybind11::module& m )
{    
    pybind11::enum_<CellType>( m, "CellType" )
        .value( "NCube", CellType::NCube )
        .value( "Simplex", CellType::Simplex );
    
    m.def( "combineDirichletDofs", &boundary::combine, pybind11::arg( "boundaryDofs" ) );

    defineFunctionWrappersSingle( m );
    defineBasisSingle( m );
    definePostprocessingSingle( m );
    defineConfig( m );
}

template<size_t D>
void defineDimension( pybind11::module& m )
{
    defineGrid<D>( m );
    defineMesh<D>( m );
    defineBasis<D>( m );
    definePartitioners<D>( m );
    defineIntegrands<D>( m );
    defineBoundaryCondition<D>( m );
    definePostprocessingDimensions<D>( m );
}

template<size_t... D>
void defineDimensions( pybind11::module& m, std::index_sequence<D...>&& )
{
    [[maybe_unused]] std::initializer_list<int> tmp { ( defineDimension<D + 1>( m ), 0 )... };
}

void bindDiscretization( pybind11::module& m )
{
    defineDimensionIndendent( m );

    defineDimensions( m, std::make_index_sequence<config::maxdim>( ) );

    defineIntegrandsSingle( m );
    definePartitionersSingle( m );
    definePostprocessingSingle2( m );
    
    bindLinalg( m );
}

} // mlhp::bindings

