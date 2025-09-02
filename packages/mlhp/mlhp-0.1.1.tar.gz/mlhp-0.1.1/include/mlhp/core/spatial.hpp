// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_SPATIAL_HPP
#define MLHP_CORE_SPATIAL_HPP

#include "mlhp/core/alias.hpp"
#include "mlhp/core/coreexport.hpp"

namespace mlhp::spatial
{

// ========= General functions =========

template<size_t D> constexpr
auto dot( std::array<double, D> v1, 
          std::array<double, D> v2 );

template<typename T1, size_t D1, typename T2, size_t D2>
auto dot( std::span<T1, D1> v1,
          std::span<T2, D2> v2 );

template<size_t N>
auto norm( const std::array<double, N>& arr );

template<size_t D>
auto normalize( std::array<double, D> v );

template<size_t D>
auto normalizeChecked( std::array<double, D> v,
                       std::array<double, D> zero = array::make<D>( 0.0 ),
                       double tolerance = 100 * std::numeric_limits<double>::min( ) );

template<size_t N>
auto distance( const std::array<double, N>& arr1,
               const std::array<double, N>& arr2 );

template<size_t D>
auto invert( std::array<double, D> v );

template<size_t N>
constexpr auto normSquared( const std::array<double, N>& arr );

template<size_t N>
constexpr auto distanceSquared( const std::array<double, N>& arr1,
                                const std::array<double, N>& arr2 );

//! Compute factor = dot( v, u ) / dot( u, u ), such that u - factor * u 
//! is the orthogonal projection of v onto u
template<typename T1, size_t D1, typename T2, size_t D2>
double projectionFactor( std::span<T1, D1> u,
                         std::span<T2, D2> v );

template<size_t D>
double projectionFactor( std::array<double, D> u,
                         std::array<double, D> v );

//! Make v orthogonal to u, i.e. remove the projection of v onto u from v: 
//! p = v - dot( v, u ) / dot( u, u ) * u = v - projectionFactor( u, v ) * u
//! As a result, dot( p, u ) = 0, while dot( p, v ) is generally != 0. This 
//! function is the fundamental building block of the Gram-Schmidt process:
//! https://en.wikipedia.org/wiki/Gram%E2%80%93Schmidt_process#The_Gram%E2%80%93Schmidt_process
template<size_t D>
std::array<double, D> orthogonalize( std::array<double, D> u,
                                     std::array<double, D> v );

template<typename T1, size_t D1, typename T2, size_t D2, size_t D3>
void orthogonalize( std::span<T1, D1> u,
                    std::span<T2, D2> v,
                    std::span<double, D3> target );

//! Compute t * v1 + ( 1 - t ) * v2
template<size_t N>
auto interpolate( std::array<double, N> v1,
                  std::array<double, N> v2,
                  double t );

//! Cross product
constexpr 
std::array<double, 3> cross( std::array<double, 3> v1,
                             std::array<double, 3> v2 );

constexpr 
double cross( std::array<double, 2> v1,
              std::array<double, 2> v2 );

template<size_t N> 
constexpr auto standardBasisVector( size_t axis );

//! Returns { point, coordinate }
template<size_t D> 
constexpr auto projectOntoLine( std::array<double, D> line0,
                                std::array<double, D> line1,
                                std::array<double, D> point );

//! Returns { point, coordinate } with coordinate constrained to [0, 1]
template<size_t D>
constexpr auto closestPointOnSegment( std::array<double, D> line0,
                                      std::array<double, D> line1,
                                      std::array<double, D> point );

//! Find itersection point between a semi-infinite ray and a finie line segment
MLHP_EXPORT MLHP_PURE
std::optional<double> segmentRayIntersection( std::array<double, 2> v1,
                                              std::array<double, 2> v2,
                                              std::array<double, 2> rayOrigin,
                                              std::array<double, 2> rayAxis,
                                              double epsilon = 1e-10 );

//! Target size must be two times polygon size. Returns span in target.
//! Side == false --> left side, Side == true --> right side
template<size_t D> MLHP_EXPORT
CoordinateSpan<D> clipPolygon( CoordinateConstSpan<D> polygon,
                               CoordinateSpan<D> target,
                               size_t axis, 
                               double position, 
                               bool side,
                               bool closePolygon = true );

//! Target size must be three times polygon size. Returns span in target. 
template<size_t D> MLHP_EXPORT
CoordinateSpan<D> clipPolygon( CoordinateConstSpan<D> polygon, 
                               CoordinateSpan<D> target,
                               const BoundingBox<D>& bounds,
                               bool closePolygon = true );

//auto clipLine( const std::array<double, D> rayOrigin,
//               const std::array<double, D> rayDirection,
//               const BoundingBox<D>& bounds );
//
//template<size_t D> 
//auto clipRay( const std::array<double, D> rayOrigin,
//              const std::array<double, D> rayDirection,
//              const BoundingBox<D>& bounds );

//! Finds some orthonormal vectors n1 and n2 that span the plane defined by normal
MLHP_EXPORT MLHP_PURE
std::array<std::array<double, 3>, 2> findPlaneVectors( std::array<double, 3> normal );

template<size_t D>
using MultilinearShapes = std::array<double, utilities::binaryPow<size_t>( D )>;

template<size_t L, size_t G>
using MultilinearCornersSpan = std::span<const std::array<double, G>, utilities::binaryPow<size_t>( L )>;

//! Evaluate linear/bilinear/trilinear/... interpolation on [-1, 1]^D
template<size_t D> MLHP_EXPORT MLHP_PURE
MultilinearShapes<D> multilinearShapeFunctions( std::array<double, D> rst, 
                                                std::array<size_t, D> diff = { } );


template<size_t L, size_t G> MLHP_EXPORT MLHP_PURE
JacobianMatrix<G, L> multilinearJacobian( MultilinearCornersSpan<L, G> corners, 
                                          std::array<double, L> rst );

template<size_t D> MLHP_EXPORT MLHP_PURE
std::array<double, D + 1> simplexShapeFunctions( std::array<double, D> rst, 
                                                 std::array<size_t, D> diff = { } );

//! Compute Jacobian matrix of composed mapping outer o inner as matrix product outer * inner
template<size_t G, size_t I, size_t L>
JacobianMatrix<G, L> concatenateJacobians( const JacobianMatrix<I, L>& inner,
                                           const JacobianMatrix<G, I>& outer );

template<size_t G, size_t L = G>
double computeDeterminant( const JacobianMatrix<G, L>& matrix );

template<size_t D>
bool isDiagonal( const JacobianMatrix<D, D>& matrix, double eps = 0.0 );

/*! Map local normal vector using a Jacobian matrix such that the global vector
 * is again normal to the mapped plane the local normal vector represents. 
 * 
 * Reference coordinates (r, s)    |  Global coordiantes (x, y)
 *                                 |  ____________________                normal computed by mapPlaneNormal 
 * |\            / local normal n  |    \ ___             \          _ /  (orthogonal to global face)
 * |   \      /    (orthogonal to  |          \ ___         \    _ / 
 * |      \/          local face)  |                \ ___     \/_________ transformed normal J * n     
 * |         \                     |                      \ ___ \         (not orthogonal to global face)  
 * |____________\                  |                            \ \
 *                                 |                           
 */
template<size_t D> MLHP_EXPORT
std::array<double, D> mapPlaneNormal( const JacobianMatrix<D, D>& jacobian,
                                      std::array<double, D> normal );

// ========= Triangles =========

template<size_t D>
constexpr auto triangleCentroid( std::array<double, D> vertex0,
                                 std::array<double, D> vertex1,
                                 std::array<double, D> vertex2 );

template<size_t D>
auto triangleCross( std::array<double, D> vertex0,
                    std::array<double, D> vertex1,
                    std::array<double, D> vertex2 );

template<size_t D>
auto triangleNormal( std::array<double, D> vertex0,
                     std::array<double, D> vertex1,
                     std::array<double, D> vertex2 );

template<size_t D>
auto triangleArea( std::array<double, D> vertex0,
                   std::array<double, D> vertex1,
                   std::array<double, D> vertex2 );

template<size_t D>
auto triangleArea( std::span<const std::array<double, D>> vertices );

double tetrahedronVolume( const std::array<double, 3>& vertex0,
                          const std::array<double, 3>& vertex1,
                          const std::array<double, 3>& vertex2,
                          const std::array<double, 3>& vertex3 );

MLHP_EXPORT MLHP_PURE
std::optional<double> triangleRayIntersection( const std::array<double, 3>& vertex0,
                                               const std::array<double, 3>& vertex1,
                                               const std::array<double, 3>& vertex2,
                                               const std::array<double, 3>& rayOrigin,
                                               const std::array<double, 3>& rayAxis,
                                               double epsilon = 1e-12 );

//! Target size must be at least 3. Returns span in target.
//! Side == false --> left side, Side == true --> right side
template<size_t D>
CoordinateSpan<D> clipTriangle( const std::array<double, D>& vertex0,
                                const std::array<double, D>& vertex1,
                                const std::array<double, D>& vertex2,
                                size_t axis, double position, bool side,
                                CoordinateSpan<D> targetPolygon );

//! Returns subspan in targetPolygon.
template<size_t D>
CoordinateSpan<D> clipTriangle( const std::array<double, D>& vertex0,
                                const std::array<double, D>& vertex1,
                                const std::array<double, D>& vertex2,
                                const BoundingBox<D>& bounds,
                                std::span<std::array<double, D>, 9> targetPolygon );

template<size_t D>
BoundingBox<D> triangleClippedBoundingBox( const std::array<double, D>& vertex0,
                                           const std::array<double, D>& vertex1,
                                           const std::array<double, D>& vertex2,
                                           size_t axis, double position, bool side );

template<size_t D>
BoundingBox<D> triangleClippedBoundingBox( const std::array<double, D>& vertex0,
                                           const std::array<double, D>& vertex1,
                                           const std::array<double, D>& vertex2,
                                           const spatial::BoundingBox<D>& bounds );

//! Overwrite two vertices with vertices clipped to bounding box. Returns false if no intersection.
template<size_t D>
bool clipLineSegment( std::array<double, D>& vertex0,
                      std::array<double, D>& vertex1,
                      const BoundingBox<D>& bounds );

template<size_t D>
BoundingBox<D> lineSegmentClippedBoundingBox( std::array<double, D> vertex0,
                                              std::array<double, D> vertex1,
                                              const spatial::BoundingBox<D>& bounds );

//! Points leftward: t = v1 - v0; d = (t[1], -t[0]); n = d / ||d||
std::array<double, 2> lineSegmentNormal( std::array<double, 2> v0,
                                         std::array<double, 2> v1 );

template<size_t G, size_t L>
std::span<std::array<double, G>> clipSimplex( std::span<std::array<double, G>, 3 * ( L + 1 )> vertices,
                                              const BoundingBox<G>& bounds );

template<size_t G, size_t L>
BoundingBox<G> simplexClippedBoundingBox( std::span<const std::array<double, G>, L + 1> vertices,
                                          const BoundingBox<G>& bounds );

//! Array of simplices that subdivide an n cube (like 6 tetrahedra subdivide a cube)
template<size_t D> requires ( D <= 3 )
constexpr auto simplexSubdivisionIndices( );

template<size_t G>
std::array<double, G> simplexNormal( std::span<const std::array<double, G>, G> vertices );

template<size_t G> requires ( G <= 3 && G > 1 )
std::array<double, G> measureWeightedSimplexNormal( std::span<const std::array<double, G>, G> vertices );

template<size_t G, size_t L>
double simplexMeasure( std::span<const std::array<double, G>, L + 1> vertices );

//! Implemented for D = 1, D = 2, and D = 3
template<size_t D> requires ( D <= 3 && D > 0 ) MLHP_EXPORT MLHP_PURE
std::optional<double> simplexRayIntersection( std::span<const std::array<double, D>, D> vertices,
                                              const std::array<double, D>& rayOrigin,
                                              const std::array<double, D>& rayDirection );

// ========= Axis aligned bounding boxes =========

//! Initialize with numeric_limits
template<size_t D> constexpr
BoundingBox<D> makeFullBoundingBox( );

template<size_t D> constexpr
BoundingBox<D> makeEmptyBoundingBox( );

template<size_t D> constexpr
BoundingBox<D> boundingBoxOr( const BoundingBox<D>& bounds1,
                              const BoundingBox<D>& bounds2 );

template<size_t D> constexpr
BoundingBox<D> boundingBoxOr( const BoundingBox<D>& bounds,
                              std::array<double, D> xyz );

template<size_t D> constexpr
BoundingBox<D> boundingBoxAnd( const BoundingBox<D>& bounds1,
                               const BoundingBox<D>& bounds2 );

template<size_t D> constexpr
BoundingBox<D> extendBoundingBox( const BoundingBox<D>& bounds,
                                  double relative = 1e-10,
                                  double absolute = 0.0 );

template<size_t D> constexpr
BoundingBox<D> boundingBoxAt( const std::array<double, D>& xyz, 
                              double width );

template<size_t D> constexpr
BoundingBox<D> boundingBoxAt( const std::array<double, D>& xyz,
                              const std::array<double, D>& lengths );

template<size_t D> constexpr
bool insideBoundingBox( const BoundingBox<D>& bounds, 
                        std::array<double, D> xyz );

template<size_t D> constexpr MLHP_PURE
bool boundingBoxIsValid( const BoundingBox<D>& bounds, double epsilon = 0.0 );

template<size_t D> constexpr
double boundingBoxVolume( const BoundingBox<D>& bounds );

template<size_t D> MLHP_EXPORT
BoundingBox<D> boundingBox( CoordinateConstSpan<D> coordinates );

template<size_t D>
BoundingBox<D> boundingBox( const std::array<double, D>& vertex0,
                            const std::array<double, D>& vertex1,
                            const std::array<double, D>& vertex2 );

template<size_t D> constexpr
bool boundingBoxIntersectsOther( const BoundingBox<D>& bounds0, 
                                 const BoundingBox<D>& bounds1 );

//! Local line coordinates of intersection points
using OptionalTBounds = std::optional<std::array<double, 2>>;

template<size_t D>
OptionalTBounds boundingBoxIntersectsRay( const spatial::BoundingBox<D>& bounds,
                                          const std::array<double, D>& rayOrigin,
                                          const std::array<double, D>& rayDirection );

//! Same as boundingBoxIntersectsRay but directly give 1 / rayDirection (computed componentwise)
template<size_t D>
OptionalTBounds boundingBoxIntersectsInvRay( const spatial::BoundingBox<D>& bounds,
                                             const std::array<double, D>& rayOrigin,
                                             const std::array<double, D>& invDirection );

// ========= Spatial function objects =========

namespace detail
{

template<typename T>
struct IsVectorFunction { static constexpr bool value = false; };

template<size_t L, size_t G>
struct IsVectorFunction<spatial::VectorFunction<L, G>> { static constexpr bool value = true; };

template<typename T>
concept NotAVectorFunction = !IsVectorFunction<std::remove_const_t<std::remove_reference_t<std::decay_t<T>>>>::value;

} // namespace detail

template<size_t L, size_t G>
struct VectorFunction
{
    using Type = void( std::array<double, L> xyz, std::span<double, G> out );

    static constexpr size_t extent = G;
    
    size_t odim;
    std::function<Type> function;

    //! Construct dynamic extent from expression with result span (only option)
    template<detail::NotAVectorFunction Function>
    VectorFunction( size_t odim_, Function&& f )
        requires ( G == std::dynamic_extent && std::is_invocable_v<Function, std::array<double, L>, std::span<double, G>> ) : 
        odim { odim_ }, function { std::forward<Function>( f ) }
    { }

    //! Construct static extent from expression with result span (option 1)
    template<detail::NotAVectorFunction Function>
    VectorFunction( Function&& f )
        requires ( G != std::dynamic_extent && std::is_invocable_v<Function, std::array<double, L>, std::span<double, G>> ) :
        odim { G }, function { std::forward<Function>( f ) }
    { }

    //! Construct static extent from expression returning an std::array (option 2)
    template<detail::NotAVectorFunction Function>
    VectorFunction( Function&& f )
        requires ( G != std::dynamic_extent && std::is_invocable_v<Function, std::array<double, L>> ) :
        odim { G }
    { 
        function  = [f = std::forward<Function>( f )]( std::array<double, L> xyz, std::span<double, G> out ) 
        {  
            auto result = f( xyz );

            std::copy( result.begin( ), result.end( ), out.begin( ) );
        };
    }

    //! Copy construct dynamic extent from static extent
    template<size_t D> requires ( D != std::dynamic_extent && G == std::dynamic_extent ) 
    VectorFunction( VectorFunction<L, D> f ) : odim { D }
    {
        function = [f = std::move( f )]( std::array<double, L> xyz, std::span<double> out ) 
        {   
            MLHP_CHECK( out.size( ) == D, "Inconsistent number of vector components." );

            auto result = f( xyz );

            std::copy( result.begin( ), result.end( ), out.begin( ) );

            // Maybe this works: out = result;
        };
    }

    //! Copy construct static extent from dynamic extent
    template<size_t D> requires ( D == std::dynamic_extent && G != std::dynamic_extent ) 
    VectorFunction( VectorFunction<L, D> f ) : odim { G }
    {
        MLHP_CHECK( f.odim == G, "Inconsistent number of vector components." );

        function = [f = std::move( f )]( std::array<double, L> xyz, std::span<double, G> out ) { f( xyz, out ); };
    }

    //! Construct from ScalarFunction
    VectorFunction( const ScalarFunction<L>& f ) 
        requires ( G == 1 || G == std::dynamic_extent ) : odim { 1 }
    {
        function = [=]( std::array<double, L> xyz, std::span<double, G> out ) { out[0] = f( xyz ); };
    }

    //! Evaluate with target span
    void operator()( std::array<double, L> xyz, std::span<double, G> out ) const
    {
        if constexpr( G == std::dynamic_extent )
        {
            MLHP_CHECK( out.size( ) == odim, "Inconsistent number of vector components." );
        }

        function( xyz, out );
    }

    //! Evaluate with known size returning result array instead
    template<size_t D>
    std::array<double, D> call( std::array<double, L> xyz ) const
        requires( G == std::dynamic_extent || G == D )
    {
        if constexpr ( G == std::dynamic_extent ) 
        {
            MLHP_CHECK( D == odim, "Inconsistent output sizes." );
        }

        auto out = std::array<double, D> { };

        function( xyz, out );

        return out;
    }

    std::array<double, G> operator()( std::array<double, L> xyz ) const 
        requires ( G != std::dynamic_extent )
    {
        return call<G>( xyz );
    }
};

template<size_t D, typename... Args>
auto constantFunction( double value );

template<size_t I, size_t O>
auto constantFunction( std::array<double, O> value );

template<size_t I>
auto constantFunction( std::vector<double> value );

//! Create piecewise constant spatial function from voxel data (row-major/C-style ordering).
//! Instantiated for types double and float
template<size_t D, typename T>
ScalarFunction<D> voxelFunction( const std::vector<T>& data,
                                 std::array<size_t, D> nvoxels,
                                 std::array<double, D> lengths,
                                 std::array<double, D> origin,
                                 std::optional<T> outside = std::nullopt );

//! Same as above with shared pointer to vector
template<size_t D, typename T> MLHP_EXPORT
ScalarFunction<D> voxelFunction( const std::shared_ptr<const std::vector<T>>& data,
                                 std::array<size_t, D> nvoxels,
                                 std::array<double, D> lengths,
                                 std::array<double, D> origin,
                                 std::optional<T> outside = std::nullopt );

//! Binds given spatial coordinate to a given value
template<size_t D, typename ReturnType, typename... Args>
auto slice( const std::function<ReturnType( std::array<double, D>, Args...)>& function, size_t axis, double value );

template<size_t L, size_t G>
auto slice( const VectorFunction<L, G>& function, size_t axis, double value );

//! Binds last spatial coordinate to a given value
template<size_t D, typename ReturnType, typename... Args>
auto sliceLast( const std::function<ReturnType( std::array<double, D>, Args...)>& function, double value );

template<size_t L, size_t G>
auto sliceLast( const VectorFunction<L, G>& function, double value );

//! Peels last spatial coordinate into separate double parameter
template<size_t D>
auto peelLast( const ScalarFunction<D>& function );

template<size_t I, size_t O> requires ( O != std::dynamic_extent )
ScalarFunction<I> extractComponent( const VectorFunction<I, O>& function, size_t icomponent );

template<size_t D> MLHP_EXPORT
ScalarFunction<D> extractComponent( const VectorFunction<D>& function, size_t icomponent );

//! Adds N dimensions
template<size_t N, size_t D>
auto expandDimension( const ScalarFunction<D>& function,
                      std::array<size_t, N> positions );

//! Adds one dimension
template<size_t D>
auto expandDimension( const ScalarFunction<D>& function,
                      size_t index = D );

//! Activates function only if mask( xyz ) == true. If alpha is nonzero,
//! the function will be scaled by alpha when mask is false
template<size_t D> MLHP_EXPORT
ScalarFunction<D> mask( const ScalarFunction<D>& function,
                        const ImplicitFunction<D>& mask,
                        double alpha = 0.0 );

//! Same as above but with constant value instead of function
template<size_t D> MLHP_EXPORT
ScalarFunction<D> mask( double value,
                        const ImplicitFunction<D>& mask,
                        double alpha = 0.0 );

template<size_t D>
using SelectScalarFieldInputPair = std::pair<ImplicitFunction<D>, ScalarFunction<D>>;

template<size_t D> MLHP_EXPORT
ScalarFunction<D> selectField( std::vector<SelectScalarFieldInputPair<D>> domains,
                               std::optional<double> defaultValue = std::nullopt );

template<size_t D> MLHP_EXPORT
ScalarFunction<D> selectField( const std::vector<std::pair<ImplicitFunction<D>, double>>& domains,
                               std::optional<double> defaultValue = std::nullopt );

//! Gauss bell with value at center equals scaling
template<size_t D>
auto centerNormalizedGaussBell( std::array<double, D> center,
                                double sigma,
                                double scaling = 1.0 );

//! Gauss bell with integral over [-inf, inf]^D equals scaling
template<size_t D>
auto integralNormalizedGaussBell( std::array<double, D> center,
                                  double sigma,
                                  double scaling = 1.0 );

template<size_t D>
auto revolveAroundPath( const ScalarFunction<D>& function,
                        const ParameterFunction<D>& path,
                        const RealFunction& scaling );

// ========= Coordinate generators =========

template<size_t D>
auto makeGridPointGenerator( std::array<size_t, D> npoints,
                             std::array<double, D> lengths = array::make<D>( 1.0 ),
                             std::array<double, D> origin = array::make<D>( 0.0 ) );

template<size_t D>
auto makeRstGenerator( std::array<size_t, D> npoints, 
                       double scaling = 1.0 );

template<size_t D> MLHP_EXPORT
void cartesianTickVectors( std::array<size_t, D> ncells,
                           std::array<double, D> lengths,
                           std::array<double, D> origin,
                           CoordinateGrid<D>& target );

//! Equidistant points in the local coordinates for the given cell type
template<size_t D> MLHP_EXPORT
void distributeSeedPoints( CellType type, 
                           size_t nseedpoints, 
                           CoordinateList<D>& rst );

template<size_t D> MLHP_EXPORT
CoordinateGrid<D> cartesianTickVectors( std::array<size_t, D> ncells,
                                        std::array<double, D> lengths = array::make<D>( 1.0 ),
                                        std::array<double, D> origin = array::make<D>( 0.0 ) );

template<size_t D> MLHP_EXPORT
CoordinateList<D> tensorProduct( const CoordinateGrid<D>& grid );

template<size_t D> MLHP_EXPORT
void tensorProduct( const CoordinateGrid<D>& grid, 
                    CoordinateList<D>& target );

template<size_t D> MLHP_EXPORT
std::optional<std::uint64_t> findVoxel( std::array<size_t, D> nvoxels, 
                                        std::array<double, D> lengths,
                                        std::array<double, D> origin,
                                        std::array<double, D> xyz );

//! Evently distributes points on sphere (approximately)
MLHP_EXPORT
void fibonacciSphere( CoordinateSpan<3> target );

MLHP_EXPORT
CoordinateList<3> fibonacciSphere( size_t n );

// ========= Homogeneous transformations =========

// Provides translate, scale, rotate, invert and operator(). 
// When suitable allows method chaining. Definition can be   
// found in _impl.hpp. Created using functions below.                                 
template<size_t D> 
struct HomogeneousTransformation;

//! Create homogeneous translation
template<size_t D> MLHP_EXPORT MLHP_PURE
HomogeneousTransformation<D> translate( std::array<double, D> vector );

//! Create homogeneous scaling
template<size_t D> MLHP_EXPORT
HomogeneousTransformation<D> scale( std::array<double, D> factors );

//! Create homogeneous rotation: 2D overload
MLHP_EXPORT
HomogeneousTransformation<2> rotate( double phi );

//! Create homogeneous rotation: 3D overload
MLHP_EXPORT
HomogeneousTransformation<3> rotate( std::array<double, 3> normal, double phi );

//! Create homogeneous rotation: Generic implementation
template<size_t D> MLHP_EXPORT
HomogeneousTransformation<D> rotate( std::array<double, D> v1,
                                     std::array<double, D> v2,
                                     double phi );

template<size_t D, typename... HomogeneousTransformations>
HomogeneousTransformation<D> concatenate( const HomogeneousTransformation<D>& transformation1,
                                          const HomogeneousTransformation<D>& transformation2,
                                          HomogeneousTransformations&&... transformations );

// Determine if and what spatial function an arbitrary object can be converted to
template<typename T> struct InspectFunctionImpl { static constexpr auto type = 0; };

template<utilities::DoubleCastable Result, size_t I>
struct InspectFunctionImpl<std::function<Result( std::array<double, I> )>>
{
    static constexpr auto type = 1;
    static constexpr auto idim = I;
};

template<utilities::DoubleCastable Result, size_t O, size_t I>
struct InspectFunctionImpl<std::function<std::array<Result, O>( std::array<double, I> )>>
{
    static constexpr auto type = 2;
    static constexpr auto idim = I;
    static constexpr auto odim = O;
};

template<typename Function>
using InspectFunction = InspectFunctionImpl<decltype( std::function { std::declval<Function>( ) })>;

template<typename Function> concept ConvertibleToScalarFunction = InspectFunction<Function>::type == 1;
template<typename Function> concept ConvertibleToVectorFunction = InspectFunction<Function>::type == 2;

template<size_t D> MLHP_EXPORT
std::string to_string( std::array<double, D> coords );

} // namespace mlhp::spatial

namespace mlhp::solution
{

//! Gaussian bell travelling in space
template<size_t D> MLHP_EXPORT
spatial::ScalarFunction<D + 1> amLinearHeatSource( const spatial::ParameterFunction<D>& path,
                                                   const RealFunction& intensity,
                                                   double sigma );

template<size_t D> MLHP_EXPORT
spatial::ScalarFunction<D + 1> amLinearHeatSolution( const spatial::ParameterFunction<D>& path,
                                                     const RealFunction& intensity,
                                                     double capacity, double kappa,
                                                     double sigma, double dt,
                                                     double shift = 0.0 );

//! Standard ND Fichera cube / 1D singular example
template<size_t D> MLHP_EXPORT
spatial::ScalarFunction<D> singularSolution( );

template<size_t D> MLHP_EXPORT
spatial::VectorFunction<D, D> singularSolutionDerivatives( );

template<size_t D> MLHP_EXPORT
spatial::ScalarFunction<D> singularSolutionSource( );

} // namespace mlhp::solution

namespace mlhp
{

template<size_t D> constexpr auto operator+( std::array<double, D> arr1, std::array<double, D> arr2 );
template<size_t D> constexpr auto operator-( std::array<double, D> arr1, std::array<double, D> arr2 );
template<size_t D> constexpr auto operator*( std::array<double, D> arr1, std::array<double, D> arr2 );
template<size_t D> constexpr auto operator/( std::array<double, D> arr1, std::array<double, D> arr2 );

template<size_t D> constexpr auto operator+( std::array<double, D> arr, double value );
template<size_t D> constexpr auto operator-( std::array<double, D> arr, double value );
template<size_t D> constexpr auto operator*( std::array<double, D> arr, double value );
template<size_t D> constexpr auto operator/( std::array<double, D> arr, double value );

template<size_t D> constexpr auto operator+( double value, std::array<double, D> arr );
template<size_t D> constexpr auto operator-( double value, std::array<double, D> arr );
template<size_t D> constexpr auto operator*( double value, std::array<double, D> arr );
template<size_t D> constexpr auto operator/( double value, std::array<double, D> arr );

template<size_t D> std::ostream& operator<<( std::ostream& stream, std::array<double, D> coordinates );

} // namespace mlhp

#include "mlhp/core/spatial_impl.hpp"

#endif // MLHP_CORE_SPATIAL_HPP
