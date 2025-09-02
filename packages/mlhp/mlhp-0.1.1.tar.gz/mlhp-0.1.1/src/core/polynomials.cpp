// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/polynomials.hpp"
#include "mlhp/core/utilities.hpp"
#include "mlhp/core/ndarray.hpp"
#include "mlhp/core/compilermacros.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/dense.hpp"

#include <limits>
#include <vector>

namespace mlhp::polynomial
{
namespace detail 
{

// Constexpr version of the square root (Taken from http://stackoverflow.com/a/34134071)
// Return value:
//   - For a finite and non-negative value of "x", returns an approximation for the square root of "x"
//   - Otherwise, returns NaN
double constexpr sqrtNewtonRaphson( double x, double curr, double prev )
{
  return curr == prev ? curr : sqrtNewtonRaphson( x, 0.5 * ( curr + x / curr ), curr );
}

double constexpr compileTimeSquareRoot( double x )
{
  return x >= 0.0 && x < std::numeric_limits<double>::max( ) ? sqrtNewtonRaphson( x, x, 0.0 ) : 1.0;
}

} // namespace detail

constexpr double computePreFactorForIntegratedLegendre( int j )
{
    return 1.0 / detail::compileTimeSquareRoot( 4 * j - 2 );
}

constexpr double computeOneOverJ( int j )
{
    return j > 0 ? 1.0 / j : 0.0;
}

constexpr double computeTwoJminusOne( int j )
{
    return 2.0 * j - 1;
}

constexpr double computeJminusOne( int j )
{
    return j - 1;
}

template<typename Function, size_t... Indices>
constexpr decltype( auto ) computeInternal( std::index_sequence<Indices...> sequence, Function function )
{
    return std::array<double, sequence.size( )> { function( Indices ) ... };
}

template<size_t N, typename Function>
constexpr decltype( auto ) compute( Function function )
{
    return computeInternal( std::make_index_sequence<N>( ), function );
}

constexpr auto factors = compute<config::maxdegree>( computePreFactorForIntegratedLegendre );
constexpr auto oneOverJ = compute<config::maxdegree>( computeOneOverJ );
constexpr auto twoJminusOne = compute<config::maxdegree>( computeTwoJminusOne );
constexpr auto JminusOne = compute<config::maxdegree>( computeJminusOne );

template<size_t MaxDiffOrder> 
void integratedLegendre( size_t ansatzOrder,
                         double coordinate,
                         std::array<double*, MaxDiffOrder + 1> target )
{
    MLHP_EXPECTS( ansatzOrder > 0 );

    std::array<double* MLHP_RESTRICT, MaxDiffOrder + 1> N;

    for( size_t diffOrder = 0; diffOrder <= MaxDiffOrder; ++diffOrder )
    {
        N[diffOrder] = target[diffOrder];
    }

    // The three last Legendre shape functions (and derivatives)
    std::array<std::array<double, 3>, MaxDiffOrder + 1> L; 

    L[0] = { 1.0, coordinate, 0.0 };
    
    N[0][0] = 0.5 * ( 1.0 - coordinate );
    N[0][1] = 0.5 * ( 1.0 + coordinate );

    if constexpr ( MaxDiffOrder > 0 )
    {
        L[1] = { 0, 1, 0.0 };

        N[1][0] = -0.5;
        N[1][1] =  0.5;
    }

    if constexpr ( MaxDiffOrder > 1 )
    {
        L[2] = { 0, 0, 0.0 };

        N[2][0] = 0.0;
        N[2][1] = 0.0;
    }

    for ( size_t j = 2; j <= ansatzOrder; ++j )
    {
        // Compute the next Legendre function
        L[0][2] = oneOverJ[j] * ( twoJminusOne[j] * coordinate * 
            L[0][1] - JminusOne[j] * L[0][0] );

        for( size_t D = 1; D <= MaxDiffOrder; ++D )
        {
            L[D][2] = oneOverJ[j] * ( twoJminusOne[j] * ( D * L[D - 1][1] + 
                coordinate * L[D][1] ) - JminusOne[j] * L[D][0] );
        }

        // Compute integrated Legendre function and move Legendre functions
        for( size_t D = 0; D <= MaxDiffOrder; ++D )
        {
            N[D][j] = factors[j] * ( L[D][2] - L[D][0] );

            L[D][0] = L[D][1];
            L[D][1] = L[D][2];
        }
    } // for j

} // integratedLegendre

template<size_t MaxDiffOrder>
void integratedLegendre( size_t ansatzOrder,
                         double coordinate,
                         double* target )
{
    std::array<double*, MaxDiffOrder + 1> targets { target };

    if constexpr( MaxDiffOrder != 0 )
    {
        for( size_t diffOrder = 1; diffOrder <= MaxDiffOrder; ++diffOrder )
        {
            targets[diffOrder] = targets[diffOrder - 1] + ansatzOrder + 1;
        }
    }

    integratedLegendre<MaxDiffOrder>( ansatzOrder, coordinate, targets );
}

/*
 * #define MAKE_LOOKUP_TABLE_EXPR( functionName, N, expr )    \
 *     []<size_t... I>( std::index_sequence<I...> ) constexpr \
 *     {                                                      \
 *         return std::array { &functionName<expr>... };      \
 *     } ( std::make_index_sequence<N>( ) )
 * 
 * #define MAKE_LOOKUP_TABLE( functionName, N )               \
 *     MAKE_LOOKUP_TABLE_EXPR( functionName, N, I )
 */

void integratedLegendre( size_t ansatzOrder,
                         size_t maxDiffOrder,
                         double coordinate,
                         double* target )
{
    if( maxDiffOrder == 0 ) integratedLegendre<0>( ansatzOrder, coordinate, target );
    else if( maxDiffOrder == 1 ) integratedLegendre<1>( ansatzOrder, coordinate, target );
    else if( maxDiffOrder == 2 ) integratedLegendre<2>( ansatzOrder, coordinate, target );
    else MLHP_THROW( "Invalid diff order" );
}

PolynomialBasis makeIntegratedLegendreBasis( )
{
    using EvaluationType = void( size_t, size_t, double, double* );

    return static_cast<std::add_pointer_t<EvaluationType>>( &integratedLegendre );
}

void bspline( std::span<const double> U,
              size_t degree, 
              size_t maxdiff, 
              size_t ispan,
              double x,
              std::span<double> target,
              std::span<double> tmp )
{
    auto pPlus1 = degree + 1;

    MLHP_CHECK( target.size( ) == ( maxdiff + 1 ) * pPlus1, "Wrong target size." );
    MLHP_CHECK( tmp.size( ) >= ( pPlus1 + 4 ) * pPlus1, "Too small tmp storage size." );
    MLHP_CHECK( ispan + 1 >= degree, "Invalid span index" );

    std::fill( tmp.begin( ), tmp.end( ), 0.0 );

    if( maxdiff > degree )
    {
        std::fill( utilities::begin( target, maxdiff *
            ( degree + 1 ) ), target.end( ), 0.0 );

        maxdiff = degree;
    }

    auto tmpSpan = std::span { tmp };

    auto N = linalg::adapter( target, pPlus1 );
    auto ndu = linalg::adapter( tmpSpan, pPlus1 );

    auto left = tmpSpan.subspan( ( degree + 1 ) * pPlus1, pPlus1 );
    auto right = tmpSpan.subspan( ( degree + 2 ) * pPlus1, pPlus1 );

    auto a = std::array 
    { 
        tmpSpan.subspan( ( degree + 3 ) * pPlus1, pPlus1 ), 
        tmpSpan.subspan( ( degree + 4 ) * pPlus1, pPlus1 ) 
    };

    ndu( 0, 0 ) = 1;

    for( size_t j = 1; j <= degree; ++j )
    {
        left[j] = x - U[ispan + 1 - j];
        right[j] = U[ispan + j] - x;

        double saved = 0.0;

        for( size_t r = 0; r <= j - 1; ++r )
        {
            ndu( j, r ) = right[r + 1] + left[j - r];
    
            double temp = ndu( r, j - 1 ) / ndu( j, r );
    
            ndu( r, j ) = saved + right[r + 1] * temp;
    
            saved = left[j - r] * temp;
        }
    
        ndu( j, j ) = saved;
    }

    for( size_t i = 0; i < degree + 1; ++i )
    {
        N( 0, i ) = ndu( i, degree );
    }
    
    for( size_t r = 0; r <= degree; ++r )
    {
        size_t s1 = 0, s2 = 1;

        a[0][0] = 1;
    
        for( size_t k = 1; k <= maxdiff; ++k )
        {
            auto d = 0.0;
            auto rk = r - k; 
            auto pk = degree - k;
    
            if( r >= k )
            {
                a[s2][0] = a[s1][0] / ndu( pk + 1, rk );
    
                d = a[s2][0] * ndu( rk, pk );
            }

            auto j1 = r >= k ? size_t { 1 } : k - r;
            auto j2 = r + k <= degree + 1 ? k - 1 : degree - r;

            for( size_t j = j1; j <= j2; ++j )
            {
                a[s2][j] = (a[s2][j] - a[s1][j - 1]) / ndu( pk + 1, rk + j );
    
                d = d + a[s2][j] * ndu( rk + j, pk );    
            }
    
            if( r <= pk )
            {
                a[s2][k] = -a[s1][k - 1] / ndu( pk + 1, r );
    
                d = d + a[s2][k] * ndu( r, pk );
            }
    
            N( k, r ) = d;
    
            std::swap( s1, s2 );    
        }
    }
    
    auto r = static_cast<double>( degree );
    
    for( size_t k = 1; k <= maxdiff; ++k )
    {
        for( size_t i = 0; i < degree + 1; ++i )
        {
            N( k, i ) *= r;
        }
    
        r = r * ( degree - k );
    }
}

namespace
{

template<size_t Maxdegree>
void bsplineForward( std::span<const double> U, size_t degree, 
                     size_t maxdiff, size_t ispan, double x,
                     std::span<double> target )
{
    auto tmp = std::array<double, ( Maxdegree + 5 ) * ( Maxdegree + 1 )> { };

    bspline( U, degree, maxdiff, ispan, x, target, tmp );
}

} // namespace

void bspline( std::span<const double> U,
              size_t degree, 
              size_t maxdiff, 
              size_t ispan,
              double x,
              std::span<double> target )
{
    MLHP_CHECK( std::abs( U[ispan + 1] - U[ispan] ) > std::abs( U.back( ) - U.front( ) ) * 1e-12,
                "In B-Spline evaluation: ispan refers to collapsed knot span." )

    if( degree > 12 )
    {
        auto tmp = std::vector<double>( ( degree + 5 ) * ( degree + 1 ), 0.0 );

        bspline( U, degree, maxdiff, ispan, x, target, tmp );
    }
    else if( degree == 1 ) bsplineForward<1>( U, degree, maxdiff, ispan, x, target );
    else if( degree == 2 ) bsplineForward<2>( U, degree, maxdiff, ispan, x, target );
    else if( degree == 3 ) bsplineForward<3>( U, degree, maxdiff, ispan, x, target );
    else if( degree == 4 ) bsplineForward<4>( U, degree, maxdiff, ispan, x, target );
    else if( degree <= 6 ) bsplineForward<6>( U, degree, maxdiff, ispan, x, target );
    else if( degree <= 8 ) bsplineForward<8>( U, degree, maxdiff, ispan, x, target );
    else if( degree <= 10 ) bsplineForward<10>( U, degree, maxdiff, ispan, x, target );
    else if( degree <= 12 ) bsplineForward<12>( U, degree, maxdiff, ispan, x, target );
}

size_t findKnotSpan( std::span<const double> U, size_t npoints, size_t degree, double x )
{
    if( x <= U[degree] ) return degree;
    if( x >= U[npoints + 1] ) return npoints - 1;
    
    auto bounds = std::array { degree, npoints + 1 };
    auto index = std::midpoint( bounds[0], bounds[1] );
    
    while( x < U[index] || x >= U[index + 1] )
    {
        bounds[x < U[index] ? 1 : 0] = index;
        index = std::midpoint( bounds[0], bounds[1] );
    }
    return index;
}

MLHP_EXPORT
void openKnotVector( std::span<double> x,
                     size_t degree,
                     size_t continuity,
                     std::vector<double>& target )
{
    MLHP_CHECK( degree > continuity, "Continuity must be smaller than the polynomial degree." );
    MLHP_CHECK( x.size( ) >= 2, "Position vector must have at least two coordinates." );

    auto multiplicity = degree - continuity;
    auto nknots = ( x.size( ) - 2 ) * multiplicity + 2 * ( degree + 1 );
    auto size0 = utilities::increaseSizes( nknots, target )[0];

    for( size_t i = 0; i < degree + 1; ++i )
    {
        target[size0 + i] = x.front( );
        target[size0 + nknots - 1 - i] = x.back( );
    }

    for( size_t i = 0; i < x.size( ) - 2; ++i )
    {
        for( size_t j = 0; j < multiplicity; ++j )
        {
            target[size0 + degree + 1 + multiplicity * i + j] = x[i + 1];
        }
    }
}

namespace
{

bool skipCurrent( size_t index, const auto& indices )
{
    for( size_t i = 0; i < indices.size( ); ++i )
    {
        if( index == indices[i] )
        {
            return true;
        }
    }

    return false;
}

// https://en.wikipedia.org/wiki/Lagrange_polynomial#Derivatives
template<size_t Diff>
double singleLagrangeRecursive( auto&& points, size_t p, size_t j, double x, auto&& exclude )
{
    double xj = points(j);

    if constexpr( Diff == 0 )
    {
        auto value = 1.0;
    
        for( size_t m = 0; m <= p; ++m )
        {
            if( !skipCurrent( m, exclude ) )
            {
                auto xm = points(m);

                value *= ( x - xm ) / ( xj - xm );
            }
        }

        return value;
    }
    else
    {
        auto value = 0.0;

        for( size_t i = 0; i <= p; ++i )
        {
            if( !skipCurrent( i, exclude ) )
            {
                value += singleLagrangeRecursive<Diff - 1>( points, p, j, x,
                    array::append( exclude, i) ) / ( xj - points(i) );
            }

        } // for i

        return value;
    }
}

double singleLagrange( auto&& points, size_t p, size_t j, double x, size_t diff )
{
    if( diff == 0 ) return singleLagrangeRecursive<0>( points, p, j, x, std::array { j } );
    if( diff == 1 ) return singleLagrangeRecursive<1>( points, p, j, x, std::array { j } );
    if( diff == 2 ) return singleLagrangeRecursive<2>( points, p, j, x, std::array { j } );

    MLHP_THROW( "Diff orders >2 not implemented for lagrange shape functions." );
}

} // namespace

double lagrange( std::span<const double> points, size_t i, double x, size_t diff )
{
    MLHP_CHECK( !points.empty( ), "No lagrange interpolation points given." );

    return singleLagrange( [=]( auto j ) { return points[j]; }, points.size( ) - 1, i, x, diff );
}

void lagrange( size_t ansatzOrder,
               size_t numberOfEvaluationCoordinate,
               const double* lagrangePoints,
               const double* evaluationCoordinates,
               double* target )
{
    const double* MLHP_RESTRICT r = evaluationCoordinates;
    const double* MLHP_RESTRICT p = lagrangePoints;
    double* MLHP_RESTRICT N = target;
    
    std::fill( N, N + ( ansatzOrder + 1 ) * numberOfEvaluationCoordinate, 1.0 );

    for( size_t i = 0; i <= ansatzOrder; ++i )
    {
        for( size_t j = 0; j <= ansatzOrder; ++j )
        {
            if( i != j )
            {
                for( size_t k = 0; k < numberOfEvaluationCoordinate; ++k )
                {
                    N[i * numberOfEvaluationCoordinate + k] *= ( r[k] - p[j] ) / ( p[i] - p[j] );
                }
            }
        } // for j
    } // for i
}

PolynomialBasis makeEquallySpacedLagrangeBasis( bool reorder )
{
    return [=]( size_t polynomialDegree,
                size_t maxDiffOrder,
                double coordinate,
                double* targetMemory )
    {
        MLHP_CHECK( maxDiffOrder <= 2, "Invalid diff order." );
        MLHP_CHECK( polynomialDegree != 0, "Zero polynomial degree.");

        auto points = [=]( size_t k )
        {
            k = reorder ? ( k == 1 ? polynomialDegree : std::max( k, size_t { 1 } ) - 1 ) : k;

            return ( 2.0 * k ) / polynomialDegree - 1.0;
        };

        for( size_t diff = 0; diff <= maxDiffOrder; ++diff )
        {
            for( size_t j = 0; j <= polynomialDegree; ++j )
            {
                targetMemory[( polynomialDegree + 1 ) * diff + j] = 
                    singleLagrange( points, polynomialDegree, j, coordinate, diff );
            }
        }
    };
}

std::array<double, 4> cubicHermite( double t )
{
    auto t2 = t * t;
    auto t3 = t2 * t;
    auto tmp1 = 2.0 * t3 - 3.0 * t2;
    auto tmp2 = t3 - t2;

    return { tmp1 + 1.0, tmp2 - t2 + t, -tmp1, tmp2 };
}

std::array<double, 4> cubicHermiteDerivatives( double t )
{
    auto t2 = t * t;
    auto tmp1 = 6.0 * t2 - 6.0 * t;
    auto tmp2 = 3.0 * t2 - 2.0 * t;

    return { tmp1, tmp2 - 2.0 * t + 1.0, -tmp1, tmp2 };
}

std::array<double, 3> linearTriangle( std::array<double, 2> rs )
{
    return { 1.0 - rs[0] - rs[1], rs[0], rs[1] };
}

namespace
{

template<size_t D> MLHP_PURE
std::array<double, D> deBoorRecursive( std::span<const double> knotVector,
                                       const CoordinateList<D>& controlPoints,
                                       size_t degree, size_t ispan, double x,
                                       size_t level )
{
    if( level == degree )
    {
        return controlPoints[ispan];
    }

    double t = ( x - knotVector[ispan] ) / ( knotVector[ispan + level + 1] - knotVector[ispan] );

    auto P1 = deBoorRecursive( knotVector, controlPoints, degree, ispan - 1, x, level + 1 );
    auto P2 = deBoorRecursive( knotVector, controlPoints, degree, ispan, x, level + 1 );

    return spatial::interpolate( P1, P2, t );
}

} // namespace

template<size_t D>
std::array<double, D> deBoor( std::span<const double> knotVector,
                              const CoordinateList<D>& controlPoints,
                              size_t degree, size_t ispan, double x )
{
    return deBoorRecursive( knotVector, controlPoints, degree, ispan, x, 0 );
}

template MLHP_EXPORT void integratedLegendre<0>( size_t, double, std::array<double*, 1> );
template MLHP_EXPORT void integratedLegendre<1>( size_t, double, std::array<double*, 2> );
template MLHP_EXPORT void integratedLegendre<2>( size_t, double, std::array<double*, 3> );
template MLHP_EXPORT void integratedLegendre<0>( size_t, double, double* );
template MLHP_EXPORT void integratedLegendre<1>( size_t, double, double* );
template MLHP_EXPORT void integratedLegendre<2>( size_t, double, double* );


#define MLHP_INSTANTIATE_DIM( D )                                              \
                                                                               \
    template MLHP_EXPORT                                                       \
    std::array<double, D> deBoor( std::span<const double> knotVector,          \
                                  const CoordinateList<D>& controlPoints,      \
                                  size_t degree, size_t ispan, double x );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM

} // namespace mlhp::polynomial


namespace mlhp::interpolation
{
namespace
{

template<size_t D>
auto distanceLocalCoordinates( const CoordinateList<D>& xyz )
{
    auto coordinates = std::vector<double>( xyz.size( ), 0.0 );

    for( size_t ipoint = 1; ipoint < xyz.size( ); ++ipoint )
    {
        coordinates[ipoint] = spatial::distance( xyz[ipoint], xyz[ipoint - 1] );
    }
    
    return coordinates;
}

auto sumAndScaleLocalCoordinates( std::vector<double> coordinates )
{
    auto scale = 1.0 / std::accumulate( coordinates.begin( ) + 1, coordinates.end( ), 0.0 );

    for( size_t i = 1; i < coordinates.size( ); ++i )
    {
        coordinates[i] = coordinates[i - 1] + scale * coordinates[i];
    }
    
    return coordinates;
}

} // namespace

template<size_t D>
std::vector<double> equidistantLocalCoordinates( const CoordinateList<D>& xyz )
{
    return sumAndScaleLocalCoordinates( distanceLocalCoordinates( xyz ) );
}

template<size_t D>
std::vector<double> centripetralLocalCoordinates( const CoordinateList<D>& xyz )
{
    auto coordinates = distanceLocalCoordinates( xyz );

    for( size_t ipoint = 1; ipoint < xyz.size( ); ++ipoint )
    {
        coordinates[ipoint] = std::sqrt( coordinates[ipoint] );
    }

    return sumAndScaleLocalCoordinates( coordinates );
}

std::vector<double> averagedKnotVector( const std::vector<double>& localCoordinates,
                                        size_t degree )
{
    auto npoints = localCoordinates.size( );
    auto nknots = npoints + degree + 1;
    auto ninner = npoints - degree - 1;

    MLHP_CHECK( npoints > degree, "Invalid polynomial degree." );

    auto knotVector = std::vector<double>( nknots, 0.0 );

    for( size_t iknot = 0; iknot < ninner; ++iknot )
    {
        auto sum = std::accumulate( localCoordinates.data( ) + iknot + 1,
                                    localCoordinates.data( ) + iknot + degree + 1, 0.0 );

        knotVector[iknot + degree + 1] = sum / degree;
    }

    std::fill( knotVector.data( ) + ninner + degree + 1, 
               knotVector.data( ) + ninner + 2 * ( degree + 1 ), 1.0 );

    return knotVector;
}

template<size_t D>
CoordinateList<D> computeControlPoints( const CoordinateList<D>& xyzValues,
                                        std::span<const double> tvalues,
                                        std::span<const double> knotVector )
{
    auto npoints = xyzValues.size( );

    MLHP_CHECK( tvalues.size( ) == npoints, "Inconsistent sizes." );
    MLHP_CHECK( knotVector.size( ) > npoints + 1, "Knot vector too small." );

    auto degree = knotVector.size( ) - npoints - 1;

    auto M = std::vector<double>( npoints * npoints, 0.0 );
    auto N = std::vector<double>( degree + 1, 0.0 );

    auto Matrix = linalg::adapter( M, npoints );

    for( size_t ipoint = 0; ipoint < npoints; ++ipoint )
    {
        auto ispan = polynomial::findKnotSpan( knotVector, npoints, degree, tvalues[ipoint] );
        
        polynomial::bspline( knotVector, degree, 0, ispan, tvalues[ipoint], N );

        for( size_t ispline = 0; ispline < degree + 1; ++ispline )
        {
            Matrix( ipoint, ispan - degree + ispline ) = N[ispline];
        }
    } 

    auto permutation = std::vector<size_t>( npoints, 0 );
    auto luResult = linalg::luFactor( M, permutation );

    MLHP_CHECK( luResult != -1, "Interpolation matrix is singular." );

    auto controlPoints = CoordinateList<D>( npoints );

    auto xip = std::vector<double>( npoints, 0.0 );
    auto xcp = std::vector<double>( npoints, 0.0 );

    // First x, then y coordinates
    for( size_t axis = 0; axis < D; ++axis )
    {
        for( size_t ipoint = 0; ipoint < npoints; ++ipoint )
        {
            xip[ipoint] = xyzValues[ipoint][axis];
        }

        linalg::luSubstitute( M, permutation, xip, xcp );

        for( size_t ipoint = 0; ipoint < npoints; ++ipoint )
        {
            controlPoints[ipoint][axis] = xcp[ipoint];
        }
    }

    return controlPoints;
}

namespace
{

auto extrapolateInterpolation( auto&& interpolate, 
                               std::array<double, 2> bounds, 
                               Extrapolate extrapolate )
{
    return [=, interpolate = std::move( interpolate )]( double x ) -> std::array<double, 2>
    {
        if( extrapolate == Extrapolate::Default )
        {
            return interpolate( x );
        }

        auto xc = 0.0;

        if( x < bounds[0] )
        {
            xc = bounds[0];
        }
        else if( x > bounds[1] )
        {
            xc = bounds[1];
        }
        else
        {
            return interpolate( x );
        }

        auto result = interpolate( xc );
        
        if( extrapolate == Extrapolate::Linear )
        {
            return { result[0] + ( x - xc ) * result[1], result[1] };
        }

        // Extrapolate::Constant
        return { result[0], 0.0 };
    };
}

auto computeInverseLengths( const std::vector<double>& positions )
{
    auto J = std::vector<double>( positions.size( ) - 1 );

    for( size_t i = 0; i + 1 < positions.size( ); ++i )
    {
        J[i] = 1.0 / ( positions[i + 1] - positions[i] );
    }

    return J;
}

} // namespace

RealFunctionWithDerivative makeConstantInterpolation( const std::vector<double>& positions,
                                                      const std::vector<double>& values )
{    
    MLHP_CHECK( !positions.empty( ), "No interpolation points given." );
    MLHP_CHECK( positions.size( ) == values.size( ), "Inconsistent number of position and data values." );

    if( values.size( ) == 1 )
    {
        return [v = values[0]]( double ) noexcept { return std::array { v, 0.0 }; };
    }
    
    return [=]( double x ) -> std::array<double, 2>
    {
        auto i = utilities::findInterval( positions, x );
        auto left = x < 0.5 * ( positions[i] + positions[i + 1] );

        return { left ? values[i] : values[i + 1], 0.0 };
    };
}

RealFunctionWithDerivative makeCubicHermiteSpline( const std::vector<double>& positions,
                                                   const std::vector<double>& values,
                                                   const std::vector<double>& derivatives,
                                                   Extrapolate extrapolate )
{
    if( positions.size( ) < 2 ) return makeLinearInterpolation( positions, values, extrapolate );

    MLHP_CHECK( positions.size( ) == values.size( ), "Inconsistent number of position and data values." );
    MLHP_CHECK( positions.size( ) == derivatives.size( ), "Inconsistent number of position and derivative values." );
    
    auto J = computeInverseLengths( positions );
    auto bounds = std::array { positions.front( ), positions.back( ) };

    auto interpolate = [=]( double x ) -> std::array<double, 2>
    {
        auto i = utilities::findInterval( positions, x );

        auto invJ = positions[i + 1] - positions[i];
        auto t = ( x - positions[i] ) * J[i];

        auto [H0, H1, H2, H3] = polynomial::cubicHermite( t );
        auto [D0, D1, D2, D3] = polynomial::cubicHermiteDerivatives( t );

        auto f = H0 * values[i] + H1 * derivatives[i] * invJ + H2 * values[i + 1] + H3 * derivatives[i + 1] * invJ;
        auto d = D0 * values[i] + D1 * derivatives[i] * invJ + D2 * values[i + 1] + D3 * derivatives[i + 1] * invJ;

        return { f, d * J[i] };
    };

    return extrapolateInterpolation( std::move( interpolate ), bounds, extrapolate );
}

RealFunctionWithDerivative makeLinearInterpolation( const std::vector<double>& positions,
                                                    const std::vector<double>& values,
                                                    Extrapolate extrapolate )
{
    if( positions.size( ) <= 1 )
    {
        return makeConstantInterpolation( positions, values );
    }

    MLHP_CHECK( positions.size( ) == values.size( ), "Inconsistent number of position and data values." );

    auto J = computeInverseLengths( positions );
    auto bounds = std::array { positions.front( ), positions.back( ) };

    auto interpolate = [=]( double x ) MLHP_PURE -> std::array<double, 2>
    {
        auto i = utilities::findInterval( positions, x );
        auto t = ( x - positions[i] ) * J[i];

        auto f = ( 1.0 - t ) * values[i] + t * values[i + 1];
        auto df = ( values[i + 1] - values[i] ) * J[i];

        return { f, df };
    };
    
    return extrapolateInterpolation( std::move( interpolate ), bounds, extrapolate );
}

RealFunctionWithDerivative makeBSplineInterpolation( const std::vector<double>& positions,
                                                     const std::vector<double>& values,
                                                     size_t degree,
                                                     Extrapolate extrapolate )
{
    if( positions.size( ) < 2 )
    {
        return makeLinearInterpolation( positions, values, extrapolate );
    }

    MLHP_CHECK( positions.size( ) == values.size( ), "Inconsistent number of position and data values." );

    auto npoints = positions.size( );

    degree = std::min( npoints - 1, degree );

    auto xList = CoordinateList<1>( npoints );
    auto yList = CoordinateList<1>( npoints );

    for( size_t ipoint = 0; ipoint < npoints; ++ipoint )
    {
        xList[ipoint][0] = positions[ipoint];
        yList[ipoint][0] = values[ipoint];
    }

    auto local = equidistantLocalCoordinates( xList );
    auto knotVector = averagedKnotVector( local, degree );
    auto control = computeControlPoints( yList, local, knotVector );
    
    auto bounds = std::array { positions.front( ), positions.back( ) };
    auto invJ = 1.0 / ( bounds[1] - bounds[0] );

    auto interpolate = [=]( double x ) -> std::array<double, 2>
    {
        auto t = invJ * ( x - bounds[0] );

        auto N = std::vector<double>( 2 * ( degree + 1 ), 0.0 );
        auto ispan = polynomial::findKnotSpan( knotVector, npoints, degree, t );

        polynomial::bspline( knotVector, degree, 1, ispan, t, N );
        
        auto f = std::array<double, 2> { };

        for( size_t i = 0; i < degree + 1; ++i )
        {
            f[0] += control[ispan - degree + i][0] * N[i];
            f[1] += control[ispan - degree + i][0] * N[i + degree + 1] * invJ;
        }

        return f;
    };

    return extrapolateInterpolation( std::move( interpolate ), bounds, extrapolate );
}

template<size_t D> MLHP_EXPORT
spatial::ParameterFunction<D> makeBSpline( const CoordinateList<D>& controlPoints,
                                           std::span<const double> knotVector )
{
    auto npoints = controlPoints.size( );

    MLHP_CHECK( knotVector.size( ) > npoints + 1, "Invalid knot vector." );
    
    auto knotVector_ = knotVector;
    auto degree = knotVector.size( ) - npoints - 1;

    return [=]( double t )
    {
        auto ispan = polynomial::findKnotSpan( knotVector_, npoints, degree, t );

        return polynomial::deBoor( knotVector_, controlPoints, degree, ispan, t );
    };
}

#define MLHP_INSTANTIATE_DIM( D )                                                      \
                                                                                       \
    template MLHP_EXPORT                                                               \
    std::vector<double> equidistantLocalCoordinates(const CoordinateList<D>& xyz);     \
                                                                                       \
    template  MLHP_EXPORT                                                              \
    std::vector<double> centripetralLocalCoordinates(const CoordinateList<D>& xyz);    \
                                                                                       \
    template MLHP_EXPORT                                                               \
    CoordinateList<D> computeControlPoints( const CoordinateList<D>& xyzValues,        \
                                            std::span<const double> tvalues,           \
                                            std::span<const double> knotVector );      \
                                                                                       \
    template MLHP_EXPORT                                                               \
    spatial::ParameterFunction<D> makeBSpline( const CoordinateList<D>& controlPoints, \
                                               std::span<const double> knotVector );

    MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM


} // mlhp::intepolation

