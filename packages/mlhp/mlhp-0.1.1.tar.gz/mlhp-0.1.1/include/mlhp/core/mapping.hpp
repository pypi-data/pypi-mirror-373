// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_MAPPING_HPP
#define MLHP_CORE_MAPPING_HPP

#include <array>

#include "mlhp/core/spatial.hpp"
#include "mlhp/core/topologycore.hpp"
#include "mlhp/core/forwarddeclare.hpp"

namespace mlhp
{
namespace map
{

enum Evaluate : int
{
    None   = 0, // Do not evaluate
    Coords = 1, // Map coordinates
    DetJ   = 2, // Evaluate Jacobian determinant
    J      = 4, // Evaluate Jacobian matrix
};

constexpr Evaluate operator|( Evaluate a, Evaluate b )
{
    return static_cast<Evaluate>( static_cast<int>( a ) | static_cast<int>( b ) );
}

constexpr bool operator&( Evaluate a, Evaluate b )
{
    return static_cast<int>( a ) & static_cast<int>( b );
}

template<size_t G, size_t L = G>
struct Result
{
    map::Evaluate evaluate = map::None;

    std::array<double, L> rst    = { }; // local coordinates
    std::array<double, G> xyz    = { }; // global coordinates
    std::array<double, G * L> J  = { }; // Jacobian matrix
    double detJ = 0.0;                  // Jacobian matrix determinant
};

} // namespace map

template<size_t G, size_t L>
class AbsMapping : utilities::DefaultVirtualDestructor
{
public:
    map::Type type = map::Type::NCube; // Reference coordinate system type
    static constexpr size_t gdim = G; 
    static constexpr size_t ldim = L; 
                      
    explicit AbsMapping( map::Type type_ = map::Type::NCube ) :
        type { type_ }
    { }

    std::array<double, G> map( std::array<double, L> rst ) const
    {
        return map( rst, map::Coords ).xyz;
    }
        
    double detJ( std::array<double, L> rst ) const
    {
        return map( rst, map::DetJ ).detJ;
    }

    JacobianMatrix<G, L> J( std::array<double, L> rst ) const
    {
        return map( rst, map::J ).J;
    }

    map::Result<G, L> map( std::array<double, L> rst, map::Evaluate evaluate ) const
    {
        auto result = map::Result<G, L> { evaluate, rst };

        mapInternal( result );

        return result;
    }
     
    map::Result<G, L> operator()( std::array<double, L> rst, map::Evaluate evaluate ) const
    {
        return map( rst, evaluate );
    }

    std::array<double, G> operator()( std::array<double, L> rst ) const
    {
        return map( rst, map::Coords ).xyz;
    }
    
    void map( map::Result<G, L>& result ) const
    {
        mapInternal( result );
    }

private:
    virtual void mapInternal( map::Result<G, L>& result ) const = 0;
};

namespace map
{

template<size_t G, size_t L> inline
auto withJ( const AbsMapping<G, L>& mapping, std::array<double, L> rst )
{ 
    auto result = mapping( rst, map::Coords | map::J );

    return std::pair { result.xyz, result.J };
}

template<size_t G, size_t L> inline
auto withDetJ( const AbsMapping<G, L>& mapping, std::array<double, L> rst ) 
{ 
    auto result = mapping( rst, map::Coords | map::DetJ );

    return std::pair { result.xyz, result.detJ };
}

template<size_t G, size_t L> inline
auto withJDetJ( const AbsMapping<G, L>& mapping, std::array<double, L> rst ) 
{ 
    auto result = mapping( rst, map::Coords | map::J | map::DetJ );

    return std::tuple { result.xyz, result.J, result.detJ };
}

} // namespace map

namespace topology
{

template<size_t D> constexpr
size_t nfaces( CellType type )
{
    if( type == CellType::NCube ) return 2 * D;
    if( type == CellType::Simplex ) return D + 1;
    
    MLHP_THROW( "Not implemented for given cell type." );
}

template<size_t D> constexpr
size_t nvertices( CellType type )
{
    if( type == CellType::NCube ) return utilities::binaryPow<size_t>( D );
    if( type == CellType::Simplex ) return D + 1;
    
    MLHP_THROW( "Not implemented for given cell type." );
}

template<size_t D> constexpr
auto facetype( CellType type, [[maybe_unused]] size_t iface )
{
    MLHP_CHECK( type == CellType::NCube || 
                type == CellType::Simplex, 
                "Not implemented for given cell type." );

    return type;
}

template<size_t D> constexpr
auto isinside( CellType type, std::array<double, D> rst, double epsilon = 1e-10 )
{
    if( type == CellType::NCube ) 
    {
        return array::minElement( rst ) > -1.0 - epsilon &&
               array::maxElement( rst ) <  1.0 + epsilon;
    }

    if( type == CellType::Simplex )
    {
        return array::minElement( rst ) > -epsilon &&
               array::sum( rst ) < 1.0 + epsilon;
    }

    MLHP_THROW( "Not implemented for given cell type." );
}

} // namespace topology

//! Mapping of one cell from a mesh
template<size_t G, size_t L>
struct MeshMapping final : public AbsMapping<G, L>
{
      
    void reset( CellIndex icell_ )
    {
        this->icell = icell_;
        this->type = mapping->type;
    }

    void reset( AbsMapping<G, L>& mapping_, 
                CellIndex icell_ )
    {
        this->mapping = &mapping_;
        reset( icell_ );
    }

    void reset( const AbsMesh<L>& mesh_, 
                AbsMapping<G, L>& mapping_, 
                CellIndex icell_ )
    {
        this->mesh = &mesh_;
        reset( mapping_, icell_ );
    }
      
    void mapInternal( map::Result<G, L>& result ) const override
    {
        mapping->map(result);
    }

    const AbsMesh<L>* mesh = nullptr;
    memory::vptr<AbsMapping<G, L>> mapping = nullptr;
    utilities::Cache<MeshMapping> cache;
    CellIndex icell = NoCell;
};

template<size_t D>
struct CartesianMapping final : public AbsMapping<D, D>
{
public:
    // Identity mapping
    explicit CartesianMapping( ) noexcept : 
        center_ { array::make<D>( 0.0 ) }, 
        halflengths_ { array::make<D>( 1.0 ) }
    { }

    // Bounding box / two corners
    CartesianMapping( spatial::BoundingBox<D> bounds )
    {
        resetBounds( bounds );
    }

    auto resetBounds( spatial::BoundingBox<D> bounds )
    {
        center_ = 0.5 * ( bounds[1] + bounds[0] );
        halflengths_ = 0.5 * ( bounds[1] - bounds[0] );

        return *this;
    }

    auto resetCenterHalflengths( std::array<double, D> center,
                                 std::array<double, D> halflengths )
    {
        center_ = center;
        halflengths_ = halflengths;

	    return *this;
    }

    double mapGrid( CoordinateGrid<D>& rst ) const
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            utilities::scaleVector( rst[axis], halflengths_[axis], center_[axis] );
        }

        return array::product( halflengths_ );
    }

    auto center( ) const { return center_; }
    auto halflengths( ) const { return halflengths_; }

private:
    void mapInternal( map::Result<D>& result ) const override
    {
        if( result.evaluate & map::Coords )
        {
            for( size_t axis = 0; axis < D; ++axis )
            {
                result.xyz[axis] = result.rst[axis] * halflengths_[axis] + center_[axis];
            }
        }
        if( result.evaluate & map::DetJ )
        {
            result.detJ = array::product( halflengths_ );
        }
        if( result.evaluate & map::J )
        {
            for( size_t axis1 = 0; axis1 < D; ++axis1 )
            {
                for( size_t axis2 = 0; axis2 < D; ++axis2 )
                {
                    result.J[axis1 * D + axis2] = axis1 == axis2 ? halflengths_[axis1] : 0.0;
                }
            }
        }
    }

    std::array<double, D> center_, halflengths_;
};

template<size_t D>
struct NCubeMapping final : public AbsMapping<D, D>
{
    static constexpr size_t nvertices = utilities::binaryPow<size_t>( D );

    using VertexArray = std::array<std::array<double, D>, nvertices>;

    VertexArray vertices = { };

    explicit NCubeMapping( ) = default;

    NCubeMapping( const VertexArray& vertices_ ) :
        vertices { vertices_ }
    { }

    void mapInternal( map::Result<D>& result ) const override
    {
        if( result.evaluate & map::Coords )
        {
            result.xyz = { };
            
            auto N = spatial::multilinearShapeFunctions( result.rst );

            for( size_t i = 0; i < N.size( ); ++i )
            {
                result.xyz = result.xyz + N[i] * vertices[i];
            }
        }
        if( result.evaluate & map::J || result.evaluate & map::DetJ )
        {
            result.J = spatial::multilinearJacobian<D, D>( vertices, result.rst );
        }
        if( result.evaluate & map::DetJ )
        {
            result.detJ = spatial::computeDeterminant<D, D>( result.J );
        }
    }
};

//! Returns generator for splitting the given cell mapping into an equidistant grid of smaller cells
template<size_t D> inline
auto makeCartesianMappingSplitter( const CartesianMapping<D>& mapping,
                                   std::array<size_t, D> times )
{
    MLHP_CHECK( array::product( times ) > 0, "Division by zero in makeCartesianMappingSplitter." );

    auto halflengths = mapping.halflengths( );
    auto center = mapping.center( ) - halflengths;

    halflengths = array::divide( halflengths, array::convert<double>( times ) );
    center = center + halflengths;

    return [=]( std::array<size_t, D> ijk )
    {
        auto subcell = CartesianMapping<D> { };
        auto offset = 2.0 * array::multiply( array::convert<double>( ijk ), halflengths );

        return subcell.resetCenterHalflengths( center + offset, halflengths );
    };
}

template<size_t D>
auto concatenateCartesianMappings( const CartesianMapping<D>& globalMapping,
                                   const CartesianMapping<D>& localMapping )
{
    auto result = CartesianMapping<D> { };
    auto newCenter = globalMapping.map( localMapping.center( ) );
    auto newHalflengths = globalMapping.halflengths( ) * localMapping.halflengths( );
                  
    return result.resetCenterHalflengths( newCenter, newHalflengths );
}

/*!  For example: 3D triangles -> G = 3, L = 2
 *                  
 *     A
 *     |           
 *   1 X                (0, 0) --> v0
 *     | \              (1, 0) --> v1
 *     |   \            (0, 1) --> v2  
 *   s |     \              
 *     |       \        (1/2, 1/2) --> (v1 + v2)/2  
 *     |         \
 *   0 O --------  X --->
 *     0     r     1    
 */ 
template<size_t G, size_t L = G>
class SimplexMapping final : public AbsMapping<G, L>
{
public:
    static constexpr size_t nvertices = L + 1;

    explicit SimplexMapping( ) = default;

    template<typename... Vertices>
    SimplexMapping( std::array<double, G> origin, Vertices&&... vertices ) :
        SimplexMapping( std::array { origin, std::forward<Vertices>( vertices )... } )
    { }

    SimplexMapping( const CoordinateArray<G, L + 1>& vertices ) :
        AbsMapping<G, L>( map::Type::Simplex ), origin_ { vertices[0] }, detJ_ { 1.0 }
    { 
        if constexpr ( L > 0 && G > 0 )
        {
            for( size_t iglobal = 0; iglobal < G; ++iglobal )
            {
                for( size_t ilocal = 0; ilocal < L; ++ilocal )
                {
                    axes_[L * iglobal + ilocal] = vertices[ilocal + 1][iglobal] - origin_[iglobal];
                }
            }

            detJ_ = spatial::computeDeterminant<G, L>( axes_ );
        }
    }

private:
    void mapInternal( map::Result<G, L>& result ) const override
    {
        if( result.evaluate & map::Coords ) result.xyz = origin_ + linalg::mvproduct<G, L>( axes_, result.rst );
        if( result.evaluate & map::DetJ ) result.detJ = detJ_;
        if( result.evaluate & map::J ) result.J = axes_;
    }

    std::array<double, G> origin_;
    std::array<double, G * L> axes_;
    double detJ_;
};

template<size_t G>
using TriangleMapping = SimplexMapping<G, 2>;


// E.g. in 2D: Moves quad nodes as follows:
// (-1, -1) -> (0, 0)
// ( 1, -1) -> (1, 0)
// (-1,  1) -> (0, 1)
// ( 1,  1) -> (1/2, 1/2)
template<size_t D>
class NCubeCollapsedToSimplex final : public AbsMapping<D, D>
{
    void mapInternal( map::Result<D>& result ) const override
    {
        /* 
         * # Symbolic computation of a collapsed n cube (scale each cube vertex v by 1 / sum(vi)):
         * import numpy, sympy
         * ndim = 3
         * r = sympy.symarray('r', ndim)
         * N = [numpy.product([(1 + (2*i - 1)*ri)/2 for i, ri in zip(ijk, r)]) for ijk in numpy.ndindex(*[2]*ndim)][1:]
         * P = [ijk / sympy.Integer(numpy.sum(ijk)) for ijk in [numpy.array(ijk) for ijk in numpy.ndindex(*[2]*ndim)][1:]]
         * x = [sympy.factor(numpy.sum([n * p[axis] for n, p in zip(N, P)])) for axis in range(ndim)]
         * J = sympy.Matrix([[sympy.factor(sympy.diff(xi, ri)) for xi in x] for ri in r])
         * #detJ = sympy.factor( J.det( ) )
         * #eval = lambda rst : [xi.subs({ rs : rn for rs, rn in zip(r, rst)}).evalf() for xi in x]
         */
        
        if constexpr( D > 4 ) MLHP_NOT_IMPLEMENTED;

        if( result.evaluate & map::Coords )
        {
            if constexpr( D == 1 )
            {
                result.xyz = { ( result.rst[0] + 1 ) / 2.0 };
            }
            if constexpr( D == 2 )
            {
                auto [r, s] = result.rst;

                result.xyz = { ( r + 1 ) * ( 3 - s ) / 8.0, ( 3 - r ) * ( s + 1 ) / 8.0 };
            }
            if constexpr( D == 3 )
            {
                auto [r, s, t] = result.rst;

                result.xyz = { ( r + 1 ) * ( s * t - 2 * s - 2 * t + 7 ) / 24.0,
                               ( s + 1 ) * ( r * t - 2 * r - 2 * t + 7 ) / 24.0,
                               ( t + 1 ) * ( r * s - 2 * r - 2 * s + 7 ) / 24.0 };
            }
            if constexpr( D == 4 )
            {
                auto [r, s, t, u] = result.rst;

                result.xyz =  
                { 
                    -( r + 1 ) * ( 3 * s * t * u - 5 * s * t - 5 * s * u + 11 * s - 5 * t * u + 11 * t + 11 * u - 45 ) / 192.0,
                    -( s + 1 ) * ( 3 * r * t * u - 5 * r * t - 5 * r * u + 11 * r - 5 * t * u + 11 * t + 11 * u - 45 ) / 192.0,
                    -( t + 1 ) * ( 3 * r * s * u - 5 * r * s - 5 * r * u + 11 * r - 5 * s * u + 11 * s + 11 * u - 45 ) / 192.0,
                    -( u + 1 ) * ( 3 * r * s * t - 5 * r * s - 5 * r * t + 11 * r - 5 * s * t + 11 * s + 11 * t - 45 ) / 192.0 
                };
            }
        }

        if( result.evaluate & map::J || result.evaluate & map::DetJ )
        {
            auto P = std::array<size_t, D> { };
            auto J = std::array<double, D * D> { };
        
            if constexpr( D == 1 )
            {
                J = { 1.0 / 2.0 };
            }
            if constexpr( D == 2 )
            {
                auto [r, s] = result.rst;
            
                J = { -( s - 3 ), -( s + 1 ), -( r + 1 ), -( r - 3 ) };
                
                std::transform( J.begin( ), J.end( ), J.begin( ), []( auto& j ) { return j / 8; } );
            }
            if constexpr( D == 3 )
            {
                auto [r, s, t] = result.rst;

                J = { ( s * t - 2 * s - 2 * t + 7 ), ( s + 1 ) * ( t - 2 ), ( s - 2 ) * ( t + 1 ),
                      ( r + 1 ) * ( t - 2 ), ( r * t - 2 * r - 2 * t + 7 ), ( r - 2 ) * ( t + 1 ),
                      ( r + 1 ) * ( s - 2 ), ( r - 2 ) * ( s + 1 ), ( r * s - 2 * r - 2 * s + 7 ) };
                
                std::transform( J.begin( ), J.end( ), J.begin( ), []( auto& j ) { return j / 24.0; } );
            }
            if constexpr( D == 4 )
            {
                auto [r, s, t, u] = result.rst;

                J = { -( 3 * s * t * u - 5 * s * t - 5 * s * u + 11 * s - 5 * t * u + 11 * t + 11 * u - 45 ), 
                      -( s + 1 ) * ( 3 * t * u - 5 * t - 5 * u + 11 ), -( t + 1 ) * ( 3 * s * u - 5 * s - 5 * u + 11 ), 
                      -( u + 1 ) * ( 3 * s * t - 5 * s - 5 * t + 11 ), -( r + 1 ) * ( 3 * t * u - 5 * t - 5 * u + 11 ), 
                      -( 3 * r * t * u - 5 * r * t - 5 * r * u + 11 * r - 5 * t * u + 11 * t + 11 * u - 45 ), 
                      -( t + 1 ) * ( 3 * r * u - 5 * r - 5 * u + 11 ), -( u + 1 ) * ( 3 * r * t - 5 * r - 5 * t + 11 ),
                      -( r + 1 ) * ( 3 * s * u - 5 * s - 5 * u + 11 ), -( s + 1 ) * ( 3 * r * u - 5 * r - 5 * u + 11 ), 
                      -( 3 * r * s * u - 5 * r * s - 5 * r * u + 11 * r - 5 * s * u + 11 * s + 11 * u - 45 ), 
                      -( u + 1 ) * ( 3 * r * s - 5 * r - 5 * s + 11 ), -( r + 1 ) * ( 3 * s * t - 5 * s - 5 * t + 11 ), 
                      -( s + 1 ) * ( 3 * r * t - 5 * r - 5 * t + 11 ), -( t + 1 ) * ( 3 * r * s - 5 * r - 5 * s + 11 ), 
                      -( 3 * r * s * t - 5 * r * s - 5 * r * t + 11 * r - 5 * s * t + 11 * s + 11 * t - 45 ) };

                std::transform( J.begin( ), J.end( ), J.begin( ), []( auto& j ) { return j / 192.0; } );
            }

            result.J = J;
            result.detJ = linalg::det( J, P );
        }
    }
};

template<size_t G, size_t L = G, size_t I = G>
struct ConcatenatedMapping final : public AbsMapping<G, L>
{
    memory::vptr<const AbsMapping<G, I>> globalMapping = nullptr;
    memory::vptr<const AbsMapping<I, L>> localMapping = nullptr;

    explicit ConcatenatedMapping( ) noexcept = default;

    ConcatenatedMapping( memory::vptr<const AbsMapping<G, I>> global,
                         memory::vptr<const AbsMapping<I, L>> local ):
        globalMapping { std::move( global ) }, localMapping { std::move( local ) }
    { }

private:
    void mapInternal( map::Result<G, L>& result ) const override
    {
        if constexpr ( G != I || G != L ) result.evaluate = result.evaluate | map::J;

        auto result0 = localMapping->map( result.rst, result.evaluate | map::Coords );
        auto result1 = globalMapping->map( result0.xyz, result.evaluate );
        
        if( result.evaluate & map::Coords )
        {
            result.xyz = result1.xyz;
        }
        if( result.evaluate & map::J )
        {
            result.J = spatial::concatenateJacobians<G, I, L>( result0.J, result1.J );
        }
        if( result.evaluate & map::DetJ )
        {
            if constexpr ( G != I || G != L ) 
            {
                result.detJ = spatial::computeDeterminant<G, L>( result.J );
            }
            else
            {
                result.detJ = result0.detJ * result1.detJ;
            }
        }
    }
};

template<size_t L>
class FaceMapping final : public AbsMapping<L, L - 1>
{
public:
    FaceMapping( CellType cellType, size_t iface )
    {
        reset( cellType, iface );
    }

    void resetNCube( size_t iface, std::array<double, L> center, std::array<double, L> halfwidth )
    {
        auto vertices = std::array<std::array<double, L>, L> { };
        auto [normal, side] = normalAxisAndSide( iface );

        std::fill( vertices.begin( ), vertices.end( ), center );

        this->normal_ = array::setEntry<double, L>( center, normal, 2.0 * side - 1.0 );

        for( size_t axis = 0; axis < L; ++axis )
        {
            vertices[axis + (axis < normal)][axis] += halfwidth[axis];
            vertices[axis][normal] = this->normal_[normal];
        }

        this->mapping_ = vertices;
        this->type = CellType::NCube;
    }

    void resetNSimplex( size_t iface )
    {
        auto vertices = std::array<std::array<double, L>, L> { };

        if( iface < L )
        {
            normal_ = array::setEntry<double, L>( { }, iface, -1.0 );
                            
            for( size_t axis = 0; axis + 1 < L; ++axis )
            {
                vertices[axis + 1] = array::setEntry<double, L>( { }, axis + ( axis >= iface ), 1.0 );
            }
        }
        else
        {
            normal_ = array::make<L>( 1.0 / std::sqrt( L ) );
                                            
            for( size_t axis = 0; axis < L; ++axis )
            {
                vertices[axis] = array::setEntry<double, L>( { }, axis, 1.0 );
            }
        }

        this->mapping_ = vertices;
        this->type = CellType::Simplex;
    }

    void reset( CellType cellType, size_t iface )
    {
        if( cellType == CellType::NCube )
        {
            resetNCube( iface, { }, array::make<L>( 1.0 ) );
        }
        else // CellType::Simplex
        {
            MLHP_CHECK( cellType == CellType::Simplex, "Face mapping not implemented" );

            resetNSimplex( iface );
        }
    }

    auto normal( ) const
    {
        return normal_;
    }

private:
    void mapInternal( map::Result<L, L - 1>& result ) const override
    {
        mapping_.map( result );
    }

    std::array<double, L> normal_;
    SimplexMapping<L, L - 1> mapping_;
};

} // mlhp

#endif // MLHP_CORE_MAPPING_HPP
