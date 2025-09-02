// This file is part of the mlhp project. License: See LICENSE

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "src/python/pymlhpcore.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/triangulation.hpp"
#include "mlhp/core/postprocessing.hpp"
#include "mlhp/core/implicit.hpp"

namespace mlhp::bindings
{

template<size_t D>
using DynamicVectorFunction = spatial::VectorFunction<D, std::dynamic_extent>;

using ScalarFunctionWrapperVariant = DimensionVariantPlus1<ScalarFunctionWrapper>;
using VectorFunctionWrapperVariant = DimensionVariantPlus1<DynamicVectorFunction>;

namespace parser
{

// Define expressions
struct Constant
{
    double value;

    static std::optional<Constant> create( const std::vector<std::string>& expression, auto&, size_t )
    {
        return expression[0] == "Constant" ? std::optional<Constant> { Constant { std::stod( expression[1] ) } } : std::nullopt;
    }
};

struct Input
{
    size_t index;

    static std::optional<Input> create( const std::vector<std::string>& expression, auto&, size_t ndim )
    {
        if( expression[0] == "Input" )
        {
            auto index = std::stoi( expression[1] );
            auto intdim = static_cast<int>( ndim );

            MLHP_CHECK( index >= 0 && index < intdim, "Invalid input variable index " + std::to_string( index )
                + ". Must be at least 0 and smaller than ndim (" + std::to_string( ndim ) + ")." );

            return Input { static_cast<size_t>( index ) };
        }

        return std::nullopt;
    }
};

struct UnaryOp
{
    long index;
    std::function<double(double)> op;

    static std::optional<UnaryOp> create( const std::vector<std::string>& expr, auto&, size_t )
    {
        if( ( expr[0] == "Call" || expr[0] == "UnaryOp" ) && expr.size( ) == 3 )
        {
            using StdPair = std::pair<const char*, double(*)(double)>;

            auto stdfunctions = std::array
            {
                StdPair { "abs"   , std::abs    }, StdPair { "exp"   , std::exp    }, StdPair { "exp2"  , std::exp2  },
                StdPair { "expm1" , std::expm1  }, StdPair { "log"   , std::log    }, StdPair { "log10" , std::log10 },
                StdPair { "log2"  , std::log2   }, StdPair { "log1p" , std::log1p  }, StdPair { "sqrt"  , std::sqrt  },
                StdPair { "qbrt"  , std::cbrt   }, StdPair { "sin"   , std::sin    }, StdPair { "cos"   , std::cos   },
                StdPair { "tan"   , std::tan    }, StdPair { "asin"  , std::asin   }, StdPair { "acos"  , std::acos  },
                StdPair { "atan"  , std::atan   }, StdPair { "sinh"  , std::sinh   }, StdPair { "cosh"  , std::cosh  },
                StdPair { "tanh"  , std::tanh   }, StdPair { "asing" , std::asinh  }, StdPair { "acosh" , std::acosh },
                StdPair { "atanh" , std::atanh  }, StdPair { "erf"   , std::erf    }, StdPair { "erfc"  , std::erfc  },
                StdPair { "tgamma", std::tgamma }, StdPair { "lgamma", std::lgamma }, StdPair { "ceil"  , std::ceil  },
                StdPair { "floor" , std::floor  }, StdPair { "trunc" , std::trunc  }, StdPair { "round" , std::round },
            };
            
            auto id = std::stol( expr[2] );
            
            for( auto [name, ptr] : stdfunctions )
            {
                if( expr[1] == name ) return UnaryOp { id, ptr };
            }

            if( expr[1] == "sign"   ) return UnaryOp { id, []( double x ) noexcept { return x >= 0.0 ? 1.0 : 0.0; } };
            if( expr[1] == "UAdd"   ) return UnaryOp { id, []( double x ) noexcept { return +x; } };
            if( expr[1] == "USub"   ) return UnaryOp { id, []( double x ) noexcept { return -x; } };
            if( expr[1] == "Not"    ) return UnaryOp { id, []( double x ) noexcept { return x == 0.0; } };
            if( expr[1] == "Invert" ) return UnaryOp { id, []( double x ) noexcept { return x - 1.0; } };
        }

        return std::nullopt;
    }
};

struct BinaryOp
{
    long left, right;
    std::function<double(double, double)> op;

    static std::optional<BinaryOp> create( const std::vector<std::string>& expr, auto&, size_t )
    {
        if( ( expr[0] == "BinOp" || expr[0] == "Call" || expr[0] == "Compare" || expr[0] == "BoolOp" ) && expr.size( ) == 4 )
        {
            using StdPair = std::pair<const char*, double(*)(double, double)>;
            using CustomPair = std::pair<const char*, decltype( op )>;

            auto stdfunctions = std::array
            {
                StdPair { "pow" , std::pow }, StdPair { "Pow" , std::pow }, StdPair { "hypot" , std::hypot }, 
                StdPair { "atan2" , std::atan2 }, StdPair { "mod" , std::fmod }, StdPair { "remainder" , std::remainder },
            };
                      
            auto customfunctions = std::array 
            {
                CustomPair { "Add",   []( double l, double r ) noexcept { return l + r; } },
                CustomPair { "Sub",   []( double l, double r ) noexcept { return l - r; } },
                CustomPair { "Mult",  []( double l, double r ) noexcept { return l * r; } },
                CustomPair { "Div",   []( double l, double r ) noexcept { return l / r; } },
                CustomPair { "Eq",    []( double l, double r ) noexcept { return l == r; } },
                CustomPair { "NotEq", []( double l, double r ) noexcept { return l != r; } },
                CustomPair { "Lt",    []( double l, double r ) noexcept { return l < r; } },
                CustomPair { "LtE",   []( double l, double r ) noexcept { return l <= r; } },
                CustomPair { "Gt",    []( double l, double r ) noexcept { return l > r; } },
                CustomPair { "GtE",   []( double l, double r ) noexcept { return l >= r; } },
                CustomPair { "And",   []( double l, double r ) noexcept { return l && r; } },
                CustomPair { "Or",    []( double l, double r ) noexcept { return l || r; } },
                CustomPair { "Mod",   []( double l, double r ) noexcept { return std::fmod( l, r ); } },
                CustomPair { "max",   []( double l, double r ) { return std::max( l, r ); } },
                CustomPair { "min",   []( double l, double r ) noexcept { return std::min( l, r ); } }
            };
  
            auto id1 = std::stol( expr[2] );
            auto id2 = std::stol( expr[3] );
                        
            for( auto [name, ptr] : stdfunctions )
            {
                if( expr[1] == name ) return BinaryOp { id1, id2, ptr };
            }   

            for( auto [name, fn] : customfunctions )
            {
                if( expr[1] == name ) return BinaryOp { id1, id2, fn };
            }
        }

        return std::nullopt;
    }
};

struct Op3
{
    std::array<long, 3> ids;
    std::function<double(double, double, double)> op;

    static std::optional<Op3> create( const std::vector<std::string>& expr, auto&, size_t )
    {
        if( ( expr[0] == "Op3" || expr[0] == "Call" ) && expr.size( ) == 5 )
        {
            using CustomPair = std::pair<const char*, decltype( op )>;
      
            auto customfunctions = std::array 
            {
                CustomPair { "select", []( double cond, double v1, double v2 ) noexcept { return cond > 0.0 ? v1 : v2; } },
                CustomPair { "lerp", []( double a, double b, double t ) noexcept { return a + t * ( b - a ); } },
            };
  
            auto ids = std::array { std::stol( expr[2] ), std::stol( expr[3] ), std::stol( expr[4] ) };
                     
            for( auto [name, fn] : customfunctions )
            {
                if( expr[1] == name ) return Op3 { ids, fn };
            }
        }

        return std::nullopt;
    }
};

template<size_t D>
struct ScalarFieldEval
{
    std::array<long, D> operands;
    spatial::ScalarFunction<D> function;

    static std::optional<ScalarFieldEval<D>> create( const std::vector<std::string>& expr, 
                                                     const std::vector<ScalarFunctionWrapperVariant>& functions,
                                                     size_t )
    {
        if( expr[0] == "Call" && expr.size( ) > 1 && expr[1].size( ) >= 2 && expr[1][0] == 'f' )
        {
            MLHP_CHECK( expr.size( ) == D + 2, "Unexpected number of strings in scalar field expression." );
            MLHP_CHECK( expr[1].size( ) >= 2, "Invalid scalar field identifier \"" + expr[1] + "\" (must be f<list index>)." );
            
            auto functionIndex = 0;
            auto operands = std::array<long, D> { };
            
            try
            {
                functionIndex = std::stoi( expr[1].substr( 1 ) );
            }
            catch( const std::invalid_argument& )
            {
                MLHP_THROW( "Invalid scalar field identifier \"" + expr[1] + "\" (must be f<list index>)." );
            }

            for( size_t axis = 0; axis < D; ++axis )
            {
                operands[axis] = std::stoi( expr[axis + 2] );
            }

            MLHP_CHECK( functionIndex >= 0 && functionIndex < static_cast<int>( functions.size( ) ), "Function index " + std::to_string(
                functionIndex ) + " exceeds the number of fields given (" + std::to_string( functions.size( ) ) + ")." );

            auto& function = functions[static_cast<size_t>( functionIndex )];

            MLHP_CHECK( std::holds_alternative<ScalarFunctionWrapper<D>>( function ), "Invalid dimension of scalar "
                "field at index " + std::to_string( functionIndex ) + " ( must be " + std::to_string( D ) + " )" );

            return ScalarFieldEval<D> { operands, std::get<ScalarFunctionWrapper<D>>( function ).get( ) };
        }

        return std::nullopt;
    }
};

template<size_t D>
using Expression = std::variant<Constant, Input, UnaryOp, BinaryOp, Op3, ScalarFieldEval<D>>;

// Parse input
template<size_t D>
Expression<D> create( const std::vector<std::string>& expression, 
                      const std::vector<ScalarFunctionWrapperVariant>& functions )
{
    MLHP_CHECK( !expression.empty( ), "Empty expression." );

    // Iterate over variant types
    auto iterate = [&]<size_t I = 0>( auto&& self ) -> Expression<D>
    {
        // If index is within variant size
        if constexpr( I < std::variant_size_v<Expression<D>> )
        {
            // Call create and return if successful, otherwise move to next index
            if( auto result = std::variant_alternative_t<I, Expression<D>>::create( expression, functions, D ); result )
            {
                return *result;
            }

            return self.template operator()<I + 1>( self );
        }

        auto message = std::string { "Unknown expression [" };

        for( auto& subexpr : expression )
        {
            message += "\"" + subexpr + "\", ";
        }

        message.erase( message.end( ) - 2, message.end( ) );

        MLHP_THROW( message + "]." );
    };

    return iterate( iterate );
}

// Dispatch during runtime using overload resolution
template<size_t D>
struct DispatchExpression 
{
    double call( long index ) const { return std::visit( *this, tree[static_cast<size_t>( index )] ); };

    double operator()( const Constant& node ) const noexcept { return node.value; }    
    double operator()( const Input& node ) const noexcept { return xyz[node.index]; }    
    double operator()( const UnaryOp& node ) const noexcept { return node.op( call( node.index ) ); }    
    double operator()( const BinaryOp& node ) const noexcept { return node.op( call( node.left ), call( node.right ) ); }
    double operator()( const Op3& node ) const noexcept { return node.op( call( node.ids[0] ), call( node.ids[1] ), call( node.ids[2] ) ); }

    double operator()( const ScalarFieldEval<D>& node ) const noexcept
    {
        auto xyz2 = std::array<double, D> { };

        for( size_t axis = 0; axis < D; ++axis )
        {
            xyz2[axis] = call( node.operands[axis] );
        }

        return node.function( xyz2 );
    };

    const std::vector<Expression<D>>& tree;
    const std::array<double, D>& xyz;
};

template<size_t D>
auto createExpressionList( std::vector<std::vector<std::string>>&& tree,
                           const std::vector<ScalarFunctionWrapperVariant>& scalarFields )
{
    MLHP_CHECK( !tree.empty( ), "Empty tree." );

    auto nodes = std::vector<parser::Expression<D>> { };

    for( auto& node : tree )
    {
        nodes.push_back( parser::create<D>( node, scalarFields ) );
    }

    return nodes;
}

} // parser

// Should really be created by a lambda expression, but that crashes clang++-12 
struct VectorizedVectorFunction
{
	template <typename... Vectors>
	auto operator()()
    {
        return []( const spatial::VectorFunction<sizeof...( Vectors )>& f, const Vectors&... xyz )
        {
            auto size = vectorizationCheckSizes( xyz... );
            auto result = std::vector<double>( size * f.odim );
            
            [[maybe_unused]]
            auto chunksize = parallel::clampChunksize( size, 700 );
        
            #pragma omp parallel for schedule(dynamic, chunksize)
            for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( size ); ++ii )
            {
                auto i = static_cast<size_t>( ii );
                auto target = std::span { result }.subspan( i * f.odim, f.odim );
        
                f( std::array { xyz[i]... }, target );
            }
        
            return result;
        };
	}
};

template<size_t D>
void defineVectorFunctionWrapper( pybind11::module& m )
{
    auto wrapper = pybind11::class_<spatial::VectorFunction<D>>( m, add<D>( "VectorFunction" ).c_str( ) );

    auto callF1 = []( const spatial::VectorFunction<D>& function, std::array<double, D> xyz )
    {
        auto out = std::vector<double>( function.odim, 0.0 );

        function( xyz, out );

        return out;
    };
    
    wrapper.def( "__call__", callF1, pybind11::arg( "xyz" ) );
    wrapper.def_readonly( "odim", &spatial::VectorFunction<D>::odim );
    wrapper.def_property_readonly( "idim", []( const spatial::VectorFunction<D>& ) { return D; } );

    defineVectorization<double, D>( wrapper, VectorizedVectorFunction { } );
}

template<size_t D>
void defineFunctionWrappers( pybind11::module& m )
{
    auto s = defineFunctionWrapper<spatial::ScalarFunction<D>>( m, 
        add<D>( "ScalarFunction" ), true, pybind11::arg( "xyz" ) );
    
    defineFunctionWrapper<QuadratureOrderDeterminor<D>>( m, add<D>( "QuadratureOrderDeterminor" ), true );
    defineVectorFunctionWrapper<D>( m );

    defineVectorization( *s );

    auto implicitF1 = []( const ScalarFunctionWrapper<D>& f, double threshold ) 
    { 
        return ImplicitFunctionWrapper<D> { implicit::threshold( f.get( ), threshold ) };
    };

    s->def( "asimplicit", implicitF1, pybind11::arg( "threshold" ) = 0.5 );

    if constexpr( D == config::maxdim )
    {
        auto sm = defineFunctionWrapper<spatial::ScalarFunction<D + 1>>( m, add<D + 1>( "ScalarFunction" ), true );
        
        defineVectorFunctionWrapper<D + 1>( m );
        defineVectorization( *sm );
    }
}

template<size_t D>
void defineTriangulation( pybind11::module& m )
{    
    if constexpr( D <= 3 )
    {
        auto simplexMeshC = pybind11::class_<SimplexMesh<D, D - 1>,
            std::shared_ptr<SimplexMesh<D, D - 1>>>( m, add<D>( "SimplexMesh" ).c_str( ) );
    
        auto associationC = pybind11::class_<SimplexCellAssociation<D>,
            std::shared_ptr<SimplexCellAssociation<D>>>( m, add<D>( "SimplexCellAssociation" ).c_str( ) );

        auto triangulationStr = []( const SimplexMesh<D, D - 1>& simplexMesh )
        {
            auto sstream = std::stringstream { };
            auto memoryUsage = utilities::memoryUsageString( simplexMesh.memoryUsage( ) );

            sstream << "SimplexMesh<" << D << ", " << D - 1 << "> (address " << &simplexMesh << ")" << std::endl;
            sstream << "    number of vertices  : " << simplexMesh.nvertices( ) << std::endl;
            sstream << "    number of simplices : " << simplexMesh.ncells( ) << std::endl;
            sstream << "    heap memory usage   : " << memoryUsage << std::endl;

            return sstream.str( );
        };

        auto associationInit = []( std::vector<std::array<double, D>>&& rst, std::vector<size_t>&& offsets )
        {
            if( offsets.empty( ) ) 
            {
                offsets = { 0 };
            }

            return std::make_shared<SimplexCellAssociation<D>>( 
                SimplexCellAssociation<D> { std::move( rst ), std::move( offsets ) } );
        };
    
        auto associationStr = []( const SimplexCellAssociation<D>& association )
        {
            auto sstream = std::stringstream { };
            auto memoryUsage = utilities::memoryUsageString( association.memoryUsage( ) );

            sstream << "SimplexCellAssociation" << D << "D (address " << &association << ")" << std::endl;
            sstream << "    number of vertices   : " << association.rst.size( ) << std::endl;
            sstream << "    number of simplices  : " << association.offsets.back( ) << std::endl;
            sstream << "    number of mesh cells : " << association.offsets.size( ) - 1 << std::endl;
            sstream << "    heap memory usage    : " << memoryUsage << std::endl;

            return sstream.str( );
        };

        auto boundingBoxF = []( SimplexMesh<D, D - 1>& t, size_t itriangle )
        { 
            return t.boundingBox( itriangle );
        };

        auto transformF = []( SimplexMesh<D, D - 1>& tri, const spatial::HomogeneousTransformation<D>& transform )
        {
            for( auto& v : tri.vertices )
            {
                v = transform( v );
            }
        };

        auto normalsF = []( const SimplexMesh<D, D - 1>& simplexMesh )
        {
            auto result = CoordinateList<D>( simplexMesh.ncells( ) );
            
            for( size_t i = 0; i < result.size( ); ++i )
            {
                result[i] = simplexMesh.cellNormal( i );
            }

            return result;
        };

        simplexMeshC.def( "__str__", triangulationStr );
        simplexMeshC.def( "ncells", &SimplexMesh<D, D - 1>::ncells );
        simplexMeshC.def( "nvertices", &SimplexMesh<D, D - 1>::nvertices );
        simplexMeshC.def( "cellIndices", []( SimplexMesh<D, D - 1>& s, size_t i ) { return s.cells[i]; }, pybind11::arg( "icell" ) );
        simplexMeshC.def( "cellVertices", &SimplexMesh<D, D - 1>::cellVertices, pybind11::arg( "icell" ) );
        simplexMeshC.def( "cellNormal", &SimplexMesh<D, D - 1>::cellNormal, pybind11::arg( "icell" ) );
        simplexMeshC.def( "boundingBox", []( SimplexMesh<D, D - 1>& t ) { return t.boundingBox( ); } );
        simplexMeshC.def( "boundingBox", boundingBoxF, pybind11::arg( "itriangle" ) );
        simplexMeshC.def( "measure", &SimplexMesh<D, D - 1>::measure );
        simplexMeshC.def( "transform", transformF, pybind11::arg( "transformation" ) );
        simplexMeshC.def_readwrite( "vertices", &SimplexMesh<D, D - 1>::vertices );
        simplexMeshC.def_readwrite( "cells", &SimplexMesh<D, D - 1>::cells );
        simplexMeshC.def_property_readonly( "normals", normalsF );

        m.def( "simplexCellAssociation", associationInit, pybind11::arg( "rst" ), pybind11::arg( "offsets" ) );

        associationC.def( "__str__", associationStr );
        associationC.def_readwrite( "rst", &SimplexCellAssociation<D>::rst );
        associationC.def_readwrite( "offsets", &SimplexCellAssociation<D>::offsets );

        auto writeVtuF = []( const SimplexMesh<D, D - 1>& simplexMesh, 
                             const std::string& name, 
                             std::vector<double> pointData )
        {
            writeVtu( simplexMesh, name, pointData );
        };

        simplexMeshC.def( "writeVtu", writeVtuF, pybind11::arg( "filename" ) = "surfacemesh.vtu", 
            pybind11::kw_only( ), pybind11::arg( "pointData" ) = std::vector<double> { } );

        auto intersectF = []( const SimplexMesh<D, D - 1>& simplexMesh, 
                              const AbsMesh<D>& mesh,
                              std::shared_ptr<KdTree<D>>& tree )
        { 
            if( tree == nullptr )
            {
                tree = utilities::moveShared( buildKdTree( simplexMesh ) );
            }

            auto [intersected, celldata] = intersectWithMesh( simplexMesh, mesh, *tree );

            return std::pair { utilities::moveShared( intersected ), utilities::moveShared( celldata ) };
        };

        m.def( "intersectWithMesh", intersectF, pybind11::arg( "simplexMesh" ), 
            pybind11::arg( "mesh" ), pybind11::kw_only( ), pybind11::arg( "tree" ) = nullptr );

        auto implicitDomainF = []( std::shared_ptr<SimplexMesh<D, D - 1>> t,
                                   std::shared_ptr<KdTree<D>> tree, 
                                   CoordinateList<D> rays )
        {
            return ImplicitFunctionWrapper<D> { rayIntersectionDomain<D>( t, tree, rays ) };
        };

        m.def( "rayIntersectionDomain", implicitDomainF, pybind11::arg( "simplexMesh" ),
               pybind11::kw_only( ), pybind11::arg( "tree" ) = nullptr, 
               pybind11::arg( "rays" ) = CoordinateList<D> { } );

        simplexMeshC.def( "integrateNormalComponents", integrateNormalComponents<D>, pybind11::arg( "abs" ) = false );

        auto filterTriangulationF1 = []( const SimplexMesh<D, D - 1>& simplexMesh, 
                                         const ImplicitFunctionWrapper<D>& function, 
                                         size_t nseedpoints )
        { 
            return utilities::moveShared( filterSimplexMesh( simplexMesh, function.get( ), nseedpoints ) );
        };
    
        auto filterTriangulationF2 = []( const SimplexMesh<D, D - 1>& triangulation, 
                                         const ImplicitFunctionWrapper<D>& function, 
                                         const SimplexCellAssociation<D>& celldata,
                                         size_t nseedpoints )
        { 
            auto [filteredMesh, filteredCelldata] = filterSimplexMesh(
                triangulation, celldata, function.get( ), nseedpoints );

            return std::pair { utilities::moveShared( filteredMesh ), utilities::moveShared( filteredCelldata ) };
        };

        simplexMeshC.def( "filter", filterTriangulationF1, pybind11::arg( "function" ), 
            pybind11::kw_only( ), pybind11::arg( "nseedpoints" ) = 2 );

        simplexMeshC.def( "filter", filterTriangulationF2, pybind11::arg( "function" ),
            pybind11::arg( "celldata" ), pybind11::kw_only( ), pybind11::arg( "nseedpoints" ) = 2 );


        auto associatedTrianglesCellMeshF = []( std::shared_ptr<const SimplexMesh<D, D - 1>> simplexMesh,
                                                std::shared_ptr<const SimplexCellAssociation<D>> celldata )
        { 
             return CellMeshCreatorWrapper<D> { cellmesh::localSimplices<D>( simplexMesh, celldata ) };
        };

        m.def( "localSimplexCellMesh", associatedTrianglesCellMeshF, 
            pybind11::arg( "simplexMesh" ), pybind11::arg( "celldata" ) );

        auto recoverBoundaryF = []( const AbsMesh<D>& mesh,
                                    const ImplicitFunctionWrapper<D>& function,
                                    std::array<size_t, D> resolution,
                                    size_t niterations )
        {
            auto [intersected, celldata] = recoverDomainBoundary( mesh, function.get( ), resolution, niterations );

            return std::pair { utilities::moveShared( intersected ), utilities::moveShared( celldata ) };
        };

        m.def( "recoverDomainBoundary", recoverBoundaryF, pybind11::arg( "mesh" ), 
               pybind11::arg( "function" ), pybind11::arg( "resolution" ) = array::makeSizes<D>( 1 ), 
               pybind11::kw_only( ), pybind11::arg( "niterations" ) = marching::bisectionDefault );
    
        auto createSimplexMesh = []( CoordinateList<D>&& xyz, std::vector<std::array<size_t, D>>&& cells )
        {
            auto nvertices = xyz.size( );

            for( auto& icell : cells )
            {
                MLHP_CHECK( array::maxElement( icell ) < nvertices, "Vertex index out of bounds." );
            }

            auto simplexMesh = SimplexMesh<D, D - 1> { };

            simplexMesh.vertices = std::move( xyz );
            simplexMesh.cells = std::move( cells );

            return simplexMesh;
        };

        if constexpr ( D == 1 )
        {
            simplexMeshC.def_readwrite( "normals", &SimplexMesh<D, D - 1>::normals );
        
            auto simplexMeshInitF = [=]( CoordinateList<D>&& xyz, 
                                         std::vector<std::array<size_t, D>>&& cells,
                                         std::vector<std::array<double, D>> normals )
            {
                auto simplexMesh = createSimplexMesh( std::move( xyz ), std::move( cells ) );

                MLHP_CHECK( normals.size( ) == simplexMesh.cells.size( ), "Number of normals (" + 
                    std::to_string( normals.size( ) ) + ") differs from number of cells (" + 
                    std::to_string( simplexMesh.cells.size( ) ) + ")." );

                for( size_t i = 0; i < normals.size( ); ++i )
                {
                    MLHP_CHECK( std::abs( spatial::norm( normals[i] ) - 1.0 ) < 1e-10, "Invalid normal " + 
                        spatial::to_string( normals[i] ) + " at index " + std::to_string( i ) + "." );
                }

                simplexMesh.normals = std::move( normals );

                return utilities::moveShared( simplexMesh );
            };

            m.def( "simplexMesh", simplexMeshInitF,
                pybind11::arg( "vertices" ) = std::vector<std::array<double, D>> { },
                pybind11::arg( "cells" ) = std::vector<std::array<size_t, D>> { },
                pybind11::arg( "normals" ) = std::vector<std::array<double, D>> { } );
        }
        else
        {
            m.def( "simplexMesh", createSimplexMesh,
                pybind11::arg( "vertices" ) = std::vector<std::array<double, D>> { },
                pybind11::arg( "cells" ) = std::vector<std::array<size_t, D>> { } );
        }

        if constexpr( D == 2 )
        {
            simplexMeshC.def( "length", &SimplexMesh<D, D - 1>::measure );
        }

        if constexpr( D == 3 )
        {
            simplexMeshC.def( "area", &SimplexMesh<D, D - 1>::measure );

            auto readStlF = []( std::string filename, bool correctOrdering )
            {
                return createTriangulation<3>( readStl( filename, correctOrdering) );
            };

            m.def( "readStl", readStlF, pybind11::arg( "filename" ), pybind11::arg( "correctOrdering" ) = false );
        
            simplexMeshC.def( "writeStl", &writeStl, pybind11::arg( "filename" ) = "triangulation.stl", 
                pybind11::arg("solidname") = "Boundary");
        }
    }
}

template<size_t D>
void defineSpatialDimension( pybind11::module& m )
{
    defineFunctionWrappers<D>( m );

    auto sliceLastF = []( const ScalarFunctionWrapper<D + 1>& function, double value )
    {
        return ScalarFunctionWrapper<D>{ spatial::sliceLast( 
            static_cast<spatial::ScalarFunction<D + 1>>( function ), value ) };
    };

    m.def( "sliceLast", sliceLastF, pybind11::arg( "function" ), pybind11::arg( "value" ) = 0.0 );

    auto expandDimensionF = []( const ScalarFunctionWrapper<D>& function, size_t index )
    {
        return ScalarFunctionWrapper<D + 1>{ spatial::expandDimension( function.get( ), index ) };
    };

    m.def( "expandDimension", expandDimensionF, pybind11::arg( "function" ), pybind11::arg( "index" ) = D );

    auto scalarFieldFromVoxelDataF1 = []( std::shared_ptr<DoubleVector> data, 
                                          std::array<size_t, D> nvoxels, 
                                          std::array<double, D> lengths, 
                                          std::array<double, D> origin,
                                          std::optional<double> outside )
    {
        return ScalarFunctionWrapper<D> { spatial::voxelFunction<D, double>(
            data->getShared( ), nvoxels, lengths, origin, outside ) };
    };
    
    auto scalarFieldFromVoxelDataF2 = []( std::shared_ptr<FloatVector> data, 
                                          std::array<size_t, D> nvoxels, 
                                          std::array<double, D> lengths, 
                                          std::array<double, D> origin,
                                          std::optional<float> outside )
    {
        return ScalarFunctionWrapper<D> { spatial::voxelFunction<D, float>(
            data->getShared( ), nvoxels, lengths, origin, outside ) };
    };

    auto wrapVoxelField = [&]( auto&& function )
    {
        m.def( "scalarFieldFromVoxelData", function, pybind11::arg( "data" ),
            pybind11::arg( "nvoxels" ), pybind11::arg( "lengths" ), 
            pybind11::arg( "origin" ) = array::make<D>( 0.0 ),
            pybind11::arg( "outside" ) = std::nullopt );
    };

    wrapVoxelField( scalarFieldFromVoxelDataF1 );
    wrapVoxelField( scalarFieldFromVoxelDataF2 );

    using ImplicitScalarPair = std::pair<ImplicitFunctionWrapper<D>, std::variant<double, ScalarFunctionWrapper<D>>>;

    auto selectScalarFieldF = []( const std::vector<ImplicitScalarPair>& input,
                                  std::optional<double> defaultValue )
    {
        auto functions = std::vector<spatial::SelectScalarFieldInputPair<D>>( );

        for( auto& [domain, variant] : input )
        {
            auto field = std::holds_alternative<double>( variant ) ? 
                spatial::constantFunction<D>( std::get<double>( variant ) ) : 
                std::get<ScalarFunctionWrapper<D>>( variant ).get( );

            functions.push_back( std::pair { domain, field } );
        }

        return ScalarFunctionWrapper<D> { spatial::selectField( functions, defaultValue ) };
    };

    m.def( "selectScalarField", selectScalarFieldF, pybind11::arg( "domains" ), pybind11::arg( "default" ) = std::nullopt );

    defineTriangulation<D>( m );
}

template<size_t... D>
void defineSpatialDimensions( pybind11::module& m, std::index_sequence<D...>&& )
{
    [[maybe_unused]] std::initializer_list<int> tmp { ( defineSpatialDimension<D + 1>( m ), 0 )... };
}

void bindSpatial( pybind11::module& m )
{
    defineSpatialDimensions( m, std::make_index_sequence<config::maxdim>( ) );
  
    // From syntax tree
    {
        using Tree = std::vector<std::vector<std::string>>;

        auto createScalar = []<size_t D>( 
            Tree&& tree, const std::vector<ScalarFunctionWrapperVariant>& scalarFields ) 
            -> ScalarFunctionWrapperVariant
        { 
            auto nodes = parser::createExpressionList<D>( std::move( tree ), scalarFields );

            auto impl = [nodes = std::move( nodes )]( std::array<double, D> xyz )
            {
                return parser::DispatchExpression<D> { nodes, xyz }.call( 0 );
            };

            return ScalarFunctionWrapper<D> { std::move( impl ) };
        };

        auto scalarFieldFromTree = [createScalar = std::move( createScalar )]( 
            size_t ndim, Tree tree, const std::vector<ScalarFunctionWrapperVariant>& scalarFields )
        {
            return dispatchDimension<config::maxdim + 1>( createScalar, ndim, std::move( tree ), scalarFields );
        };

        m.def( "_scalarFieldFromTree", scalarFieldFromTree, pybind11::arg( "ndim" ), 
            pybind11::arg( "tree" ), pybind11::arg( "scalarFields" ) );
                
        auto createVector = []<size_t D>( std::vector<Tree>&& tree,
                                          const std::vector<ScalarFunctionWrapperVariant>& scalarFields )
            -> VectorFunctionWrapperVariant
        { 
            auto nodes = std::vector<std::vector<parser::Expression<D>>> { };

            for( auto& field : tree )
            {
                nodes.push_back( parser::createExpressionList<D>( std::move( field ), scalarFields ) );
            }

            auto impl = [nodes = std::move( nodes )]( std::array<double, D> xyz, std::span<double> out )
            {
                for( size_t ifield = 0; ifield < nodes.size( ); ++ifield )
                {
                    out[ifield] = parser::DispatchExpression<D> { nodes[ifield], xyz }.call( 0 );
                }
            };

            return spatial::VectorFunction<D> { tree.size( ), std::move( impl ) };
        };

        auto vectorFieldFromTree = [createVector = std::move( createVector )]( 
            size_t idim, std::vector<Tree> tree, const std::vector<ScalarFunctionWrapperVariant>& scalarFields )
        {
            return dispatchDimension<config::maxdim + 1>( createVector, idim, std::move( tree ), scalarFields );
        };

        m.def( "_vectorFieldFromTree", vectorFieldFromTree, pybind11::arg( "idim" ), 
            pybind11::arg( "tree" ), pybind11::arg( "scalarFields" ) );
    }

    // From function pointer
    {
        auto createScalar = []<size_t D>( std::uint64_t address ) -> ScalarFunctionWrapperVariant
        { 
            return ScalarFunctionWrapper<D> { spatial::ScalarFunction<D> { [address]( std::array<double, D> xyz )
            { 
                return reinterpret_cast<double(*)( double*, std::int64_t )>( address ) ( xyz.data( ), static_cast<std::int64_t>( D ) ); 
            } } };
        };

        auto scalarFieldFromAddress = [createScalar = std::move( createScalar )]( size_t ndim, std::uint64_t address )
        {
            return dispatchDimension<config::maxdim + 1>( createScalar, ndim, address );
        };

        m.def( "_scalarFieldFromAddress", scalarFieldFromAddress,
            pybind11::arg( "ndim" ), pybind11::arg( "address" ) );

        auto createVector = []<size_t D>( size_t odim, std::uint64_t address ) -> VectorFunctionWrapperVariant
        { 
            return spatial::VectorFunction<D> { odim, [address]( std::array<double, D> xyz, std::span<double> out )
            { 
                auto function = reinterpret_cast<void( * )( double*, double*, std::int64_t, std::int64_t )>( address );

                return function( xyz.data( ), out.data( ), static_cast<std::int64_t>( D ), static_cast<std::int64_t>( out.size( ) ) );
            } };
        };
        
        auto vectorFieldFromAddress = [createVector = std::move( createVector )]( size_t idim, size_t odim, std::uint64_t address )
        {
            return dispatchDimension<config::maxdim + 1>( createVector, idim, odim, address );
        };
        
        m.def( "_vectorFieldFromAddress", vectorFieldFromAddress, pybind11::arg( "idim" ),
            pybind11::arg( "odim" ), pybind11::arg( "address" ) );
    }

    // Singular solution
    {
        struct SingularSolution 
        { 
            ScalarFunctionWrapperVariant solution;
            ScalarFunctionWrapperVariant source;
            VectorFunctionWrapperVariant derivatives;
        };

        auto makeSingularSolution = pybind11::class_<SingularSolution>( m, "makeSingularSolution" );

        auto init = []( size_t ndim )
        {
            auto create = []<size_t D>( )
            { 
                return SingularSolution
                {
                    .solution = solution::singularSolution<D>( ),
                    .source = solution::singularSolutionSource<D>( ),
                    .derivatives = spatial::VectorFunction<D> { solution::singularSolutionDerivatives<D>( ) }
                };
            };

            return dispatchDimension( create, ndim );
        };

        makeSingularSolution.def( pybind11::init( init ), pybind11::arg( "ndim" ) );
        makeSingularSolution.def_readonly( "solution", &SingularSolution::solution );
        makeSingularSolution.def_readonly( "source", &SingularSolution::source );
        makeSingularSolution.def_readonly( "derivatives", &SingularSolution::derivatives );
    }

    // AM Solution
    {
        struct AmLinearSolution
        {
            ScalarFunctionWrapperVariant solution;
            ScalarFunctionWrapperVariant source;
        };

        auto makeAMSolution = pybind11::class_<AmLinearSolution>( m, "makeAmLinearSolution" );

        makeAMSolution.def_readwrite( "solution", &AmLinearSolution::solution );
        makeAMSolution.def_readwrite( "source", &AmLinearSolution::source );

        auto registerConstructor = [&]<size_t D>( )
        {
            auto init = []( std::array<double, D> begin_, std::array<double, D> end, double duration,
                            double capacity, double kappa, double sigma, double dt, double shift )
            {
                auto begin = begin_;

                auto path = [=]( double t ) noexcept { return spatial::interpolate<D>( begin, end, t / duration ); };
                auto intensity = [=]( double t ) noexcept { return std::min( t / 0.05, 1.0 ); };

                return AmLinearSolution
                {
                    .solution = solution::amLinearHeatSolution<D>( path,
                        intensity, capacity, kappa, sigma, dt, shift ),
                    .source = solution::amLinearHeatSource<D>( path, intensity, sigma )
                };
            };

            makeAMSolution.def( pybind11::init( init ), pybind11::arg( "begin" ), pybind11::arg( "end" ), 
                pybind11::arg( "duration" ), pybind11::arg( "capacity" ), pybind11::arg( "kappa" ), 
                pybind11::arg( "sigma" ), pybind11::arg( "dt" ), pybind11::arg( "shift" ) );
        };
        
        registerConstructor.template operator()<1>( );
        registerConstructor.template operator()<2>( );
        registerConstructor.template operator()<3>( );
    }
}

} // mlhp::bindings
