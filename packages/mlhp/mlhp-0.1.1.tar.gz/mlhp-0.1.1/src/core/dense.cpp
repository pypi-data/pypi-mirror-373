// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/dense.hpp"
#include "mlhp/core/utilities.hpp"
#include <cmath>

namespace mlhp::linalg
{

void solve( std::span<double> M,
            std::span<size_t> p,
            std::span<const double> b,
            std::span<double> u )
{
    MLHP_CHECK( luFactor( M, p ) != -1, "Matrix is singular." );

    luSubstitute( M, p, b, u );
}

double det( std::span<double> M,
            std::span<size_t> p,
            std::optional<double> eps )
{
    return luDeterminant( M, p, luFactor( M, p, eps ) );
}

// See: https://en.wikipedia.org/wiki/LU_decomposition#C_code_example
int luFactor( std::span<double> M,
              std::span<size_t> p,
              std::optional<double> eps )
{
    auto size = p.size( );
    auto nswaps = 0;

    if( !eps )
    {
        eps = 20.0 * std::numeric_limits<double>::epsilon( ) * linalg::norm( M );
    }

    MLHP_CHECK( M.size( ) == size * size, "Inconsistent sizes." );

    std::iota( p.begin( ), p.end( ), size_t{ 0 } );

    for( size_t i = 0; i < size; ++i )
    {
        double* MLHP_RESTRICT rowI = M.data( ) + i * size;

        size_t pivot = i;

        // First find index of largest value in column below (i, i)
        for( size_t j = i + 1; j < size; ++j )
        {
            pivot = std::abs( M[pivot * size + i] ) >
                    std::abs( M[j * size + i] ) ? pivot : j;
        }

        // Matrix is singular
        if( std::abs( M[pivot * size + i] ) <= *eps )
        {
            return -1;
        }

        // Swap rows i and pivot
        if( i != pivot )
        {
            nswaps += 1;

            std::swap( p[i], p[pivot] );
            std::swap_ranges( rowI, rowI + size, M.data( ) + pivot * size );
        }

        // Then loop over all rows below and subtract row i accordingly
        for( size_t j = i + 1; j < size; ++j )
        {
            auto* MLHP_RESTRICT rowJ = M.data( ) + j * size;

            rowJ[i] /= rowI[i];

            for( size_t k = i + 1; k < size; ++k )
            {
                rowJ[k] -= rowJ[i] * rowI[k];

            } // for k
        } // for j
    } // for j

    return nswaps;
}

void luSubstitute( std::span<const double> LU, 
                   std::span<const size_t> p, 
                   std::span<const double> b, 
                   std::span<double> u )
{
    auto size = p.size( );

    MLHP_CHECK( LU.size( ) == size * size, "Inconsistent sizes." );
    MLHP_CHECK( b.size( ) == size, "Inconsistent sizes." );
    MLHP_CHECK( u.size( ) == size, "Inconsistent sizes." );

    // Initialize u from permuting b
    for( size_t i = 0; i < size; ++i )
    {
        u[i] = b[p[i]];
    }

    // Forward substitution
    for( size_t i = 1; i < size; ++i )
    {
        const double* MLHP_RESTRICT rowI = LU.data( ) + i * size;

        for( size_t j = 0; j < i; ++j )
        {
            u[i] -= rowI[j] * u[j];
        }
    }

    // Backward substitution
    for( size_t r = 0; r < size; ++r )
    {
        size_t i = size - 1 - r;

        const double* MLHP_RESTRICT rowI = LU.data( ) + i * size;

        for( size_t j = i + 1; j < size; ++j )
        {
            u[i] -= rowI[j] * u[j];
        }

        u[i] /= rowI[i];
    }
}

void luInvert( std::span<const double> LU,
               std::span<const size_t> p,
               std::span<double> I )
{
    auto size = p.size( );

    MLHP_CHECK( LU.size( ) == size * size, "Inconsistent sizes." );
    MLHP_CHECK( I.size( ) == size * size, "Inconsistent sizes." );

    // Initialize permuted identity matrix
    std::fill( I.begin( ), I.end( ), 0.0 );

    for( size_t i = 0; i < size; ++i )
    {
        I[i * size + p[i]] = 1.0;
    }

    // Forward substitution
    for( size_t i = 1; i < size; ++i )
    {
        const double* MLHP_RESTRICT luRowI = LU.data( ) + i * size;

        for( size_t j = 0; j < i; ++j )
        {
            double* MLHP_RESTRICT invRowI = I.data( ) + i * size;
            double* MLHP_RESTRICT invRowJ = I.data( ) + j * size;

            for( size_t k = 0; k < size; ++k )
            {
                invRowI[k] -= luRowI[j] * invRowJ[k];
            }

        }
    }

    // Backward substitution
    for( size_t r = 0; r < size; ++r )
    {
        size_t i = size - 1 - r;

        const double* MLHP_RESTRICT luRowI = LU.data( ) + i * size;

        for( size_t j = i + 1; j < size; ++j )
        {
            double* MLHP_RESTRICT invRowI = I.data( ) + i * size;
            double* MLHP_RESTRICT invRowJ = I.data( ) + j * size;

            for( size_t k = 0; k < size; ++k )
            {
                invRowI[k] -= luRowI[j] * invRowJ[k];
            }
        }

        for( size_t k = 0; k < size; ++k )
        {
            I[i * size + k] /= luRowI[i];
        }

    } // for r
}

double luDeterminant( std::span<const double> LU,
                      std::span<const size_t> p,
                      int luResult )
{
    if( luResult == -1 )
    {
        return 0.0;
    }

    auto size = p.size( );
    auto det = 1.0;

    MLHP_CHECK( LU.size( ) == size * size, "Inconsistent sizes." );

    for( size_t i = 0; i < size; ++i )
    {
        det *= LU[i * size + i];
    }

    return luResult % 2 ? -det : det;
}

// https://en.wikipedia.org/wiki/Givens_rotation#Stable_calculation
std::array<double, 3> givensr( double a, double b )
{
    auto sign = []( auto v ) { return v >= 0.0 ? 1.0 : -1.0; };
    auto c = 0.0, s = 0.0, r = 0.0;

    if( b == 0 )
    {
        c = sign( a );
        s = 0;
        r = std::abs( a );
    }
    else if( a == 0 )
    {
        c = 0;
        s = -sign( b );
        r = std::abs( b );
    }
    else if( std::abs( a ) > std::abs( b ) )
    {
        auto t = b / a;
        auto u = sign( a ) * std::sqrt( 1.0 + t * t );
        c = 1 / u;
        s = -c * t;
        r = a * u;
    }
    else
    {
        auto t = a / b;
        auto u = sign( b ) * std::sqrt( 1.0 + t * t );
        s = -1 / u;
        c = t / u;
        r = b * u;
    }

    return std::array { c, s, r };
}

std::array<double, 2> givens( double a, double b )
{
    auto result = givensr( a, b );

    return { result[0], result[1] };
}

void qr( std::span<const double> M,
         std::span<double> Q,
         std::span<double> R,
         std::array<size_t, 2> sizes,
         bool reduce )
{
    auto [m, n] = sizes;

    MLHP_CHECK( m >= n, "More columns than rows not allowed in QR decomposition." );
    MLHP_CHECK( M.size( ) == m * n, "Inconsistent sizes." );
    MLHP_CHECK( Q.size( ) == m * m, "Inconsistent sizes." );
    MLHP_CHECK( R.size( ) == n * m, "Inconsistent sizes." );

    //auto* MLHP_RESTRICT R = RPtr;
    //auto* MLHP_RESTRICT Q = QPtr;

    // Initialize Q with identity and R with A
    for( size_t i = 0; i < m; ++i )
    {
        for( size_t j = 0; j < m; ++j )
        {
            Q[i * m + j] = i == j;
        }

        for( size_t j = 0; j < n; ++j )
        {
            R[i * n + j] = M[i * n + j];
        }
    }

    // QR factorization with in place givens rotations
    for( size_t i = 1; i < m; ++i )
    {
        for( size_t j = 0; j < std::min( i, n ); ++j )
        {
            auto [c, s] = givens( R[j * n + j], R[i * n + j] );

            if( std::abs( s ) < std::numeric_limits<double>::epsilon( ) * std::abs( c ) )
            {
                continue;
            }

            for( size_t k = 0; k < n; ++k )
            {
                auto R_jk = R[j * n + k];

                R[j * n + k] = c * R_jk - s * R[i * n + k];
                R[i * n + k] = s * R_jk + c * R[i * n + k];
            }

            for( size_t k = 0; k < m; ++k )
            {
                auto Q_kj = Q[k * m + j];

                Q[k * m + j] = c * Q_kj - s * Q[k * m + i];
                Q[k * m + i] = s * Q_kj + c * Q[k * m + i];
            }
        }
    }

    if( reduce && m != n )
    {
        // Remove columns right of n
        for( size_t i = 1; i < m; ++i )
        {
            for( size_t j = 0; j < n; ++j )
            {
                Q[i * n + j] = Q[i * m + j];
            }
        }
    }
}

//// Algorithm 5.1.1 from Matrix Computations book (Gene H. Golub, Charles F. Van Loan)
//std::tuple<double, double> householderVector( std::span<const double> x, std::span<double> v )
//{
//    auto x0 = x[0];
//    auto S = std::inner_product( x.begin( ) + 1, x.end( ), x.begin( ) + 1, 0.0 );
//
//    v[0] = 1.0;
//
//    std::copy( x.begin( ) + 1, x.end( ), v.begin( ) + 1 );
//
//    if( S == 0.0 )
//    {
//        return { x0 >= 0.0 ? 0.0 : 2.0, std::abs( x0 ) };
//    }
//    else
//    {
//        auto u = std::sqrt( x0 * x0 + S );
//
//        if( x0 <= 0.0 )
//        {
//            v[0] = x0 - u;
//        }
//        else
//        {
//            v[0] = -S / ( x0 + u );
//        }
//
//        auto beta = 2 * v[0] * v[0] / ( S + v[0] * v[0] );
//        auto scaling = 1.0 / v[0];
//
//        for( auto& vi : v )
//        {
//            vi *= scaling;
//        }
//
//        return std::tuple { u, beta };
//    }
//}

// eq. 2.4 from https://www.math.kth.se/na/SF2524/matber15/qrmethod.pdf
// The one above is supposedly better, but didn't work with the test configuration. The
// reason probably being non-uniqueness of stuff like hessenberg. Seems to make a real 
// difference though.
std::tuple<double, double> householderVector( std::span<const double> x, std::span<double> v )
{
    MLHP_CHECK( x.size( ) == v.size( ), "Inconsistent size." );

    std::copy( x.begin( ), x.end( ), v.begin( ) );

    auto norm1 = std::inner_product( v.begin( ) + 1, v.end( ), v.begin( ) + 1, 0.0 );
    auto norm = std::sqrt( v[0] * v[0] + norm1 );
    auto alpha = ( v[0] < 0.0 ? norm : -norm );

    v[0] -= alpha;

    auto scaling = 1.0 / v[0];
    auto beta = 2.0 * v[0] * v[0] / ( v[0] * v[0] + norm1 );
    
    std::transform( v.begin( ), v.end( ), v.begin( ), [=]( auto e ) { return e * scaling; } );

    return { alpha, beta };
}

MLHP_EXPORT std::tuple<double, double> householderMatrix( std::span<const double> x, std::span<double> P )
{
    auto n = x.size( );
    
    MLHP_CHECK( n != 0.0, "Zero input dimension." );
    MLHP_CHECK( P.size( ) == n * n, "Inconsistent size." );

    auto v = P.subspan( ( n - 1 ) * n, n );
    auto [alpha, beta] = householderVector( x, v );

    for( size_t i = 0; i < n; ++i )
    {
        for( size_t j = 0; j < n; ++j )
        {
            P[i * n + j] = ( i == j ) - beta * v[i] * v[j];
        }
    }

    return { alpha, beta };
}

std::array<double, 2> eigh2D( std::array<double, 2 * 2> A )
{
    auto D = ( A[0] * A[3] - A[1] * A[2] );
    auto trA = A[0] + A[3];
    auto tmp = std::sqrt( std::max( trA * trA - 4 * D, 0.0 ) );

    return std::array { 0.5 * ( trA + tmp ), 0.5 * ( trA - tmp ) };
}

std::array<std::array<double, 2>, 2> eigh2Dv( std::array<double, 2 * 2> A,
                                              std::array<double, 2> lambdas )
{
    auto v1 = std::array<double, 2> { };
    auto v2 = std::array<double, 2> { };

    auto [a, b, c, d] = A;

    if( c != 0.0 )
    {
        v1 = { lambdas[0] - d, c };
        v2 = { lambdas[1] - d, c };
    }
    else if( b != 0.0 )
    {
        v1 = { b, lambdas[0] - a };
        v2 = { b, lambdas[1] - a };
    }
    else
    {
        v1 = { 1.0, 0.0 };
        v2 = { 0.0, 1.0 };
    }

    auto norm1 = std::sqrt( v1[0] * v1[0] + v1[1] * v1[1] );
    auto norm2 = std::sqrt( v2[0] * v2[0] + v2[1] * v2[1] );

    return std::array { std::array { v1[0] / norm1, v1[1] / norm1 },
                        std::array { v2[0] / norm2, v2[1] / norm2 } };
}

namespace
{

auto transpose( std::span<double> A, size_t n )
{
    if( !A.empty( ) )
    {
        for( size_t i = 0; i < n; ++i )
        {
            for( size_t j = i + 1; j < n; ++j )
            {
                std::swap( A[i * n + j], A[j * n + i] );
            }
        }

        for( size_t i = 0; i < n; ++i )
        {
            auto v = A.subspan( i * n, n );
            auto norm = linalg::norm( v );
            auto scaling = 1.0 / norm;

            MLHP_CHECK( norm > 1e-100, "Zero length eigenvector." );

            std::transform( v.begin( ), v.end( ), v.begin( ), [=]( auto vi ) { return vi * scaling; } );
        }
    }
}

template<typename T>
auto makeIntAdapter( std::span<T> vector )
{
    return [=]( int i ) -> T& 
    {
        return vector[static_cast<size_t>( i )];
    };
}

template<typename T>
auto makeIntAdapter( std::span<T> matrix, int size2 )
{
    return [=]( int i, int j ) -> T&
        {
            return matrix[static_cast<size_t>( i ) * static_cast<size_t>( size2 ) + static_cast<size_t>( j )];
        };
}

}

// Symmetric Householder reduction to tridiagonal form.
// From: https://math.nist.gov/javanumerics/jama/
void tred2( std::span<double> A, std::span<double> tmp1, std::span<double> tmp2 )
{
    auto n = static_cast<int>( tmp1.size( ) );

    MLHP_CHECK( A.size( ) == tmp1.size( ) * tmp1.size( ), "Inconsistent sizes." );
    MLHP_CHECK( tmp2.size( ) == tmp1.size( ), "Inconsistent sizes." );

    auto V = makeIntAdapter( A, n );
    auto d = makeIntAdapter( tmp1 );
    auto e = makeIntAdapter( tmp2 );

    //  This is derived from the Algol procedures tred2 by
    //  Bowdler, Martin, Reinsch, and Wilkinson, Handbook for
    //  Auto. Comp., Vol.ii-Linear Algebra, and the corresponding
    //  Fortran subroutine in EISPACK.

    for( int j = 0; j < n; j++ )
    {
        d( j ) = V( n - 1, j );
    }

    // Householder reduction to tridiagonal form.
    for( int i = n - 1; i > 0; i-- )
    {
        // Scale to avoid under/overflow.
        double scale = 0.0;
        double h = 0.0;

        for( int k = 0; k < i; k++ )
        {
            scale = scale + std::abs( d( k ) );
        }

        if( scale == 0.0 )
        {
            e( i ) = d( i - 1 );
            for( int j = 0; j < i; j++ )
            {
                d( j ) = V( i - 1, j );
                V( i, j ) = 0.0;
                V( j, i ) = 0.0;
            }
        }
        else
        {
            // Generate Householder vector.
            for( int k = 0; k < i; k++ )
            {
                d( k ) /= scale;
                h += d( k ) * d( k );
            }

            double f = d( i - 1 );
            double g = std::sqrt( h );

            if( f > 0 )
            {
                g = -g;
            }

            e( i ) = scale * g;
            h = h - f * g;
            d( i - 1 ) = f - g;

            for( int j = 0; j < i; j++ )
            {
                e( j ) = 0.0;
            }

            // Apply similarity transformation to remaining columns.
            for( int j = 0; j < i; j++ )
            {
                f = d( j );
                V( j, i ) = f;
                g = e( j ) + V(j, j) * f;
                for( int k = j + 1; k <= i - 1; k++ )
                {
                    g += V( k, j ) * d( k );
                    e( k ) += V( k, j ) * f;
                }
                e( j ) = g;
            }
            f = 0.0;
            for( int j = 0; j < i; j++ )
            {
                e( j ) /= h;
                f += e( j ) * d( j );
            }
            double hh = f / ( h + h );
            for( int j = 0; j < i; j++ )
            {
                e( j ) -= hh * d( j );
            }
            for( int j = 0; j < i; j++ )
            {
                f = d( j );
                g = e( j );
                for( int k = j; k <= i - 1; k++ )
                {
                    V( k, j ) -= ( f * e( k ) + g * d( k ) );
                }
                d( j ) = V( i - 1, j );
                V( i, j ) = 0.0;
            }
        }
        d( i ) = h;
    }

    // Accumulate transformations.
    for( int i = 0; i < n - 1; i++ )
    {
        V( n - 1, i ) = V( i, i );
        V( i, i ) = 1.0;

        double h = d( i + 1 );

        if( h != 0.0 )
        {
            for( int k = 0; k <= i; k++ )
            {
                d( k ) = V( k, i + 1 ) / h;
            }

            for( int j = 0; j <= i; j++ )
            {
                double g = 0.0;

                for( int k = 0; k <= i; k++ )
                {
                    g += V(k, i + 1 ) * V( k, j );
                }

                for( int k = 0; k <= i; k++ )
                {
                    V( k, j ) -= g * d( k );
                }
            }
        }

        for( int k = 0; k <= i; k++ )
        {
            V( k, i + 1 ) = 0.0;
        }
    }

    for( int j = 0; j < n; j++ )
    {
        d( j ) = V( n - 1, j );
        V( n - 1, j ) = 0.0;
    }

    V( n - 1, n - 1 ) = 1.0;
    e( 0 ) = 0.0;
}

// Symmetric tridiagonal QL algorithm.
// From: https://math.nist.gov/javanumerics/jama/
void tql2( std::span<double> A, std::span<double> lambda, std::span<double> tmp )
{
    MLHP_CHECK( A.size( ) == lambda.size( ) * lambda.size( ), "Inconsistent sizes." );
    MLHP_CHECK( A.size( ) == lambda.size( ) * lambda.size( ), "Inconsistent sizes." );

    auto n = static_cast<int>( lambda.size( ) );
    auto V = makeIntAdapter( A, n );
    auto d = makeIntAdapter( lambda );
    auto e = makeIntAdapter( tmp );

    //  This is derived from the Algol procedures tql2, by
    //  Bowdler, Martin, Reinsch, and Wilkinson, Handbook for
    //  Auto. Comp., Vol.ii-Linear Algebra, and the corresponding
    //  Fortran subroutine in EISPACK.

    for( int i = 1; i < n; i++ )
    {
        e( i - 1 ) = e( i );
    }

    e( n - 1 ) = 0.0;

    double f = 0.0;
    double tst1 = 0.0;
    double eps = std::pow( 2.0, -52.0 );

    for( int l = 0; l < n; l++ )
    {
        // Find small subdiagonal element
        tst1 = std::max( tst1, std::abs( d( l ) ) + std::abs( e( l ) ) );
        
        int m = l;

        while( m < n )
        {
            if( std::abs( e( m ) ) <= eps * tst1 )
            {
                break;
            }
            m++;
        }

        // If m == l, d( l ) is an eigenvalue,
        // otherwise, iterate.
        if( m > l )
        {
            int iter = 0;

            do
            {
                iter = iter + 1;  // (Could check iteration count here.)

                // Compute implicit shift
                double g = d( l );
                double p = ( d( l + 1 ) - g ) / ( 2.0 * e( l ) );
                double r = std::hypot( p, 1.0 );

                if( p < 0 )
                {
                    r = -r;
                }

                d( l ) = e( l ) / ( p + r );
                d( l + 1 ) = e( l ) * ( p + r );

                double dl1 = d( l + 1 );
                double h = g - d( l );
                
                for( int i = l + 2; i < n; i++ )
                {
                    d( i ) -= h;
                }
                
                f = f + h;

                // Implicit QL transformation.
                p = d( m );

                double c = 1.0;
                double c2 = c;
                double c3 = c;
                double el1 = e( l + 1 );
                double s = 0.0;
                double s2 = 0.0;
                
                for( int i = m - 1; i >= l; i-- )
                {
                    c3 = c2;
                    c2 = c;
                    s2 = s;
                    g = c * e( i );
                    h = c * p;
                    r = std::hypot( p, e( i ) );
                    e( i + 1 ) = s * r;
                    s = e( i ) / r;
                    c = p / r;
                    p = c * d( i ) - s * g;
                    d( i + 1 ) = h + s * ( c * g + s * d( i ) );

                    // Accumulate transformation.

                    for( int k = 0; k < n; k++ )
                    {
                        h = V( k, i + 1 );
                        V( k, i + 1 ) = s * V( k, i ) + c * h;
                        V( k, i ) = c * V( k, i ) - s * h;
                    }
                }
                p = -s * s2 * c3 * el1 * e( l ) / dl1;
                e( l ) = s * p;
                d( l ) = c * p;

                // Check for convergence.
            }
            while( std::abs( e( l ) ) > eps * tst1 );
        }

        d( l ) = d( l ) + f;
        e( l ) = 0.0;
    }

    // Sort eigenvalues and corresponding vectors.
    for( int i = 0; i < n - 1; i++ )
    {
        int k = i;
        double p = d( i );

        for( int j = i + 1; j < n; j++ )
        {
            if( d( j ) < p )
            {
                k = j;
                p = d( j );
            }
        }

        if( k != i )
        {
            d( k ) = d( i );
            d( i ) = p;

            for( int j = 0; j < n; j++ )
            {
                p = V( j, i );
                V( j, i ) = V( j, k );
                V( j, k ) = p;
            }
        }
    }
}

// Nonsymmetric reduction to Hessenberg form.
// From: https://math.nist.gov/javanumerics/jama/
void orthes( std::span<double> A, std::span<double> tmp, std::span<double> eigenvectors )
{
    auto n = static_cast<int>( tmp.size( ) );

    MLHP_CHECK( A.size( ) == tmp.size( ) * tmp.size( ), "Inconsistent matrix size." );

    auto H = makeIntAdapter( A, n );
    auto ort = makeIntAdapter( tmp );

    //  This is derived from the Algol procedures orthes and ortran,
    //  by Martin and Wilkinson, Handbook for Auto. Comp.,
    //  Vol.ii-Linear Algebra, and the corresponding
    //  Fortran subroutines in EISPACK.   
    int low = 0;
    int high = n - 1;

    for( int m = low + 1; m <= high - 1; m++ )
    {
        // Scale column.
        double scale = 0.0;

        for( int i = m; i <= high; i++ )
        {
            scale = scale + std::abs( H( i, m - 1 ) );
        }
        if( scale != 0.0 )
        {

            // Compute Householder transformation.
            double h = 0.0;

            for( int i = high; i >= m; i-- )
            {
                ort( i ) = H( i, m - 1 ) / scale;

                h += ort( i ) * ort( i );
            }

            double g = std::sqrt( h );

            if( ort( m ) > 0 )
            {
                g = -g;
            }

            h = h - ort( m ) * g;
            ort( m ) = ort( m ) - g;

            // Apply Householder similarity transformation
            // H = (I-u*u'/h)*H*(I-u*u')/h)
            for( int j = m; j < n; j++ )
            {
                double f = 0.0;

                for( int i = high; i >= m; i-- )
                {
                    f += ort( i ) * H( i, j );
                }

                f = f / h;

                for( int i = m; i <= high; i++ )
                {
                    H( i, j ) -= f * ort( i );
                }
            }

            for( int i = 0; i <= high; i++ )
            {
                double f = 0.0;

                for( int j = high; j >= m; j-- )
                {
                    f += ort( j ) * H( i, j );
                }

                f = f / h;

                for( int j = m; j <= high; j++ )
                {
                    H( i, j ) -= f * ort( j );
                }
            }

            ort( m ) = scale * ort( m );
            H( m, m - 1 ) = scale * g;
        }
    }

    if( !eigenvectors.empty( ) )
    {
        MLHP_CHECK( eigenvectors.size( ) == tmp.size( ) * tmp.size( ), "Inconsistent matrix size." );

        auto V = makeIntAdapter( eigenvectors, n );

        // Accumulate transformations (Algol's ortran).
        for( int i = 0; i < n; i++ )
        {
            for( int j = 0; j < n; j++ )
            {
                V( i, j ) = ( i == j ? 1.0 : 0.0 );
            }
        }

        for( int m = high - 1; m >= low + 1; m-- )
        {
            if( H( m, m - 1 ) != 0.0 )
            {
                for( int i = m + 1; i <= high; i++ )
                {
                    ort( i ) = H( i, m - 1 );
                }

                for( int j = m; j <= high; j++ )
                {
                    double g = 0.0;

                    for( int i = m; i <= high; i++ )
                    {
                        g += ort( i ) * V( i, j );
                    }

                    // Double division avoids possible underflow
                    g = ( g / ort( m ) ) / H( m, m - 1 );

                    for( int i = m; i <= high; i++ )
                    {
                        V( i, j ) += g * ort( i );
                    }
                }
            }
        }
    } // if not empty

    for( int i = 2; i < n; ++i )
    {
        for( int j = 0; j + 1 < i; ++j )
        {
            H( i, j ) = 0.0;
        }
    }
}

// From: https://math.nist.gov/javanumerics/jama/
auto cdiv( double xr, double xi, double yr, double yi )
{
    double cdivr, cdivi;
    double r, d;
    if( std::abs( yr ) > std::abs( yi ) )
    {
        r = yi / yr;
        d = yr + r * yi;
        cdivr = ( xr + r * xi ) / d;
        cdivi = ( xi - r * xr ) / d;
    }
    else
    {
        r = yr / yi;
        d = yi + r * yr;
        cdivr = ( r * xr + xi ) / d;
        cdivi = ( r * xi - xr ) / d;
    }

    return std::tuple { cdivr, cdivi };
}

// Nonsymmetric reduction from Hessenberg to real Schur form.
// From: https://math.nist.gov/javanumerics/jama/
void hqr2( std::span<double> H_, std::span<double> lambda0, std::span<double> lambda1, std::span<double> eigenvectors )
{
    auto n = static_cast<int>( lambda0.size( ) );
   
    MLHP_CHECK( H_.size( ) == lambda0.size( ) * lambda0.size( ), "Inconsistent matrix size." );
    MLHP_CHECK( lambda1.size( ) == lambda0.size( ), "Inconsistent matrix size." );

    auto H = makeIntAdapter( H_, n );
    auto V = makeIntAdapter( eigenvectors, n );
    auto d = makeIntAdapter( lambda0 );
    auto e = makeIntAdapter( lambda1 );

    //  This is derived from the Algol procedure hqr2,
    //  by Martin and Wilkinson, Handbook for Auto. Comp.,
    //  Vol.ii-Linear Algebra, and the corresponding
    //  Fortran subroutine in EISPACK.

    // Initialize

    int nn = n;
    n = nn - 1;
    int low = 0;
    int high = nn - 1;
    double eps = std::pow( 2.0, -52.0 );
    double exshift = 0.0;
    double p = 0, q = 0, r = 0, s = 0, z = 0, t, w, x, y;

    // Store roots isolated by balanc and compute matrix norm

    double norm = 0.0;
    for( int i = 0; i < nn; i++ )
    {
        if( i < low || i > high )
        {
            d( i ) = H( i, i );
            e( i ) = 0.0;
        }
        for( int j = std::max( i - 1, 0 ); j < nn; j++ )
        {
            norm = norm + std::abs( H( i, j ) );
        }
    }

    // Outer loop over eigenvalue index

    int iter = 0;
    while( n >= low )
    {

        // Look for single small sub-diagonal element

        int l = n;
        while( l > low )
        {
            s = std::abs( H( l - 1, l - 1 ) ) + std::abs( H( l, l ) );
            if( s == 0.0 )
            {
                s = norm;
            }
            if( std::abs( H( l, l - 1 ) ) < eps * s )
            {
                break;
            }
            l--;
        }

        // Check for convergence
        // One root found

        if( l == n )
        {
            H( n, n ) = H( n, n ) + exshift;
            d( n ) = H( n, n );
            e( n ) = 0.0;
            n--;
            iter = 0;

            // Two roots found

        }
        else if( l == n - 1 )
        {
            w = H( n, n - 1 ) * H( n - 1, n );
            p = ( H( n - 1, n - 1 ) - H( n, n ) ) / 2.0;
            q = p * p + w;
            z = std::sqrt( std::abs( q ) );
            H( n, n ) = H( n, n ) + exshift;
            H( n - 1, n - 1 ) = H( n - 1, n - 1 ) + exshift;
            x = H( n, n );

            // Real pair

            if( q >= 0 )
            {
                if( p >= 0 )
                {
                    z = p + z;
                }
                else
                {
                    z = p - z;
                }
                d( n - 1 ) = x + z;
                d( n ) = d( n - 1 );
                if( z != 0.0 )
                {
                    d( n ) = x - w / z;
                }
                e( n - 1 ) = 0.0;
                e( n ) = 0.0;
                x = H( n, n - 1 );
                s = std::abs( x ) + std::abs( z );
                p = x / s;
                q = z / s;
                r = std::sqrt( p * p + q * q );
                p = p / r;
                q = q / r;

                // Row modification

                for( int j = n - 1; j < nn; j++ )
                {
                    z = H( n - 1, j );
                    H( n - 1, j ) = q * z + p * H( n, j );
                    H( n, j ) = q * H( n, j ) - p * z;
                }

                // Column modification

                for( int i = 0; i <= n; i++ )
                {
                    z = H( i, n - 1 );
                    H( i, n - 1 ) = q * z + p * H( i, n );
                    H( i, n ) = q * H( i, n ) - p * z;
                }

                // Accumulate transformations

                for( int i = low; i <= high; i++ )
                {
                    z = V( i, n - 1 );
                    V( i, n - 1 ) = q * z + p * V( i, n );
                    V( i, n ) = q * V( i, n ) - p * z;
                }

                // Complex pair

            }
            else
            {
                d( n - 1 ) = x + p;
                d( n ) = x + p;
                e( n - 1 ) = z;
                e( n ) = -z;
            }
            n = n - 2;
            iter = 0;

            // No convergence yet

        }
        else
        {

            // Form shift

            x = H( n, n );
            y = 0.0;
            w = 0.0;
            if( l < n )
            {
                y = H( n - 1, n - 1 );
                w = H( n, n - 1 ) * H( n - 1, n );
            }

            // Wilkinson's original ad hoc shift

            if( iter == 10 )
            {
                exshift += x;
                for( int i = low; i <= n; i++ )
                {
                    H(i, i) -= x;
                }
                s = std::abs( H( n, n - 1 ) ) + std::abs( H( n - 1, n - 2 ) );
                x = y = 0.75 * s;
                w = -0.4375 * s * s;
            }

            // MATLAB's new ad hoc shift

            if( iter == 30 )
            {
                s = ( y - x ) / 2.0;
                s = s * s + w;
                if( s > 0 )
                {
                    s = std::sqrt( s );
                    if( y < x )
                    {
                        s = -s;
                    }
                    s = x - w / ( ( y - x ) / 2.0 + s );
                    for( int i = low; i <= n; i++ )
                    {
                        H(i, i) -= s;
                    }
                    exshift += s;
                    x = y = w = 0.964;
                }
            }

            iter = iter + 1;   // (Could check iteration count here.)

            // Look for two consecutive small sub-diagonal elements

            int m = n - 2;
            while( m >= l )
            {
                z = H( m, m );
                r = x - z;
                s = y - z;
                p = ( r * s - w ) / H( m + 1, m ) + H( m, m + 1 );
                q = H( m + 1, m + 1 ) - z - r - s;
                r = H( m + 2, m + 1 );
                s = std::abs( p ) + std::abs( q ) + std::abs( r );
                p = p / s;
                q = q / s;
                r = r / s;
                if( m == l )
                {
                    break;
                }
                if( std::abs( H( m, m - 1 ) ) * ( std::abs( q ) + std::abs( r ) ) <
                    eps * ( std::abs( p ) * ( std::abs( H( m - 1, m - 1 ) ) + std::abs( z ) +
                                              std::abs( H( m + 1, m + 1 ) ) ) ) )
                {
                    break;
                }
                m--;
            }

            for( int i = m + 2; i <= n; i++ )
            {
                H( i, i - 2 ) = 0.0;
                if( i > m + 2 )
                {
                    H( i, i - 3 ) = 0.0;
                }
            }

            // Double QR step involving rows l:n and columns m:n


            for( int k = m; k <= n - 1; k++ )
            {
                bool notlast = ( k != n - 1 );
                if( k != m )
                {
                    p = H( k, k - 1 );
                    q = H( k + 1, k - 1 );
                    r = ( notlast ? H( k + 2, k - 1 ) : 0.0 );
                    x = std::abs( p ) + std::abs( q ) + std::abs( r );
                    if( x == 0.0 )
                    {
                        continue;
                    }
                    p = p / x;
                    q = q / x;
                    r = r / x;
                }

                s = std::sqrt( p * p + q * q + r * r );
                if( p < 0 )
                {
                    s = -s;
                }
                if( s != 0 )
                {
                    if( k != m )
                    {
                        H( k, k - 1 ) = -s * x;
                    }
                    else if( l != m )
                    {
                        H( k, k - 1 ) = -H( k, k - 1 );
                    }
                    p = p + s;
                    x = p / s;
                    y = q / s;
                    z = r / s;
                    q = q / p;
                    r = r / p;

                    // Row modification

                    for( int j = k; j < nn; j++ )
                    {
                        p = H( k, j ) + q * H( k + 1, j );
                        if( notlast )
                        {
                            p = p + r * H( k + 2, j );
                            H( k + 2, j ) = H( k + 2, j ) - p * z;
                        }
                        H( k, j ) = H( k, j ) - p * x;
                        H( k + 1, j ) = H( k + 1, j ) - p * y;
                    }

                    // Column modification

                    for( int i = 0; i <= std::min( n, k + 3 ); i++ )
                    {
                        p = x * H( i, k ) + y * H( i, k + 1 );
                        if( notlast )
                        {
                            p = p + z * H( i, k + 2 );
                            H( i, k + 2 ) = H( i, k + 2 ) - p * r;
                        }
                        H( i, k ) = H( i, k ) - p;
                        H( i, k + 1 ) = H( i, k + 1 ) - p * q;
                    }

                    // Accumulate transformations

                    for( int i = low; i <= high; i++ )
                    {
                        p = x * V( i, k ) + y * V( i, k + 1 );
                        if( notlast )
                        {
                            p = p + z * V( i, k + 2 );
                            V( i, k + 2 ) = V( i, k + 2 ) - p * r;
                        }
                        V( i, k ) = V( i, k ) - p;
                        V( i, k + 1 ) = V( i, k + 1 ) - p * q;
                    }
                }  // (s != 0)
            }  // k loop
        }  // check convergence
    }  // while (n >= low)

    // Backsubstitute to find vectors of upper triangular form

    if( norm == 0.0 )
    {
        return;
    }

    for( n = nn - 1; n >= 0; n-- )
    {
        p = d( n );
        q = e( n );

        // Real vector

        if( q == 0 )
        {
            int l = n;
            H( n, n ) = 1.0;
            for( int i = n - 1; i >= 0; i-- )
            {
                w = H( i, i ) - p;
                r = 0.0;
                for( int j = l; j <= n; j++ )
                {
                    r = r + H( i, j ) * H( j, n );
                }
                if( e( i ) < 0.0 )
                {
                    z = w;
                    s = r;
                }
                else
                {
                    l = i;
                    if( e( i ) == 0.0 )
                    {
                        if( w != 0.0 )
                        {
                            H( i, n ) = -r / w;
                        }
                        else
                        {
                            H( i, n ) = -r / ( eps * norm );
                        }

                        // Solve real equations

                    }
                    else
                    {
                        x = H( i, i + 1 );
                        y = H( i + 1, i );
                        q = ( d( i ) - p ) * ( d( i ) - p ) + e( i ) * e( i );
                        t = ( x * s - z * r ) / q;
                        H( i, n ) = t;
                        if( std::abs( x ) > std::abs( z ) )
                        {
                            H( i + 1, n ) = ( -r - w * t ) / x;
                        }
                        else
                        {
                            H( i + 1, n ) = ( -s - y * t ) / z;
                        }
                    }

                    // Overflow control

                    t = std::abs( H( i, n ) );
                    if( ( eps * t ) * t > 1 )
                    {
                        for( int j = i; j <= n; j++ )
                        {
                            H( j, n ) = H( j, n ) / t;
                        }
                    }
                }
            }

            // Complex vector

        }
        else if( q < 0 )
        {
            int l = n - 1;
            double cdivr, cdivi;
            // Last vector component imaginary so matrix is triangular

            if( std::abs( H( n, n - 1 ) ) > std::abs( H( n - 1, n ) ) )
            {
                H( n - 1, n - 1 ) = q / H( n, n - 1 );
                H( n - 1, n ) = -( H( n, n ) - p ) / H( n, n - 1 );
            }
            else
            {
                std::tie( cdivr, cdivi ) = cdiv( 0.0, -H( n - 1, n ), H( n - 1, n - 1 ) - p, q );
                H( n - 1, n - 1 ) = cdivr;
                H( n - 1, n ) = cdivi;
            }
            H( n, n - 1 ) = 0.0;
            H( n, n ) = 1.0;
            for( int i = n - 2; i >= 0; i-- )
            {
                double ra, sa, vr, vi;
                ra = 0.0;
                sa = 0.0;
                for( int j = l; j <= n; j++ )
                {
                    ra = ra + H( i, j ) * H( j, n - 1 );
                    sa = sa + H( i, j ) * H( j, n );
                }
                w = H(i, i) - p;

                if( e( i ) < 0.0 )
                {
                    z = w;
                    r = ra;
                    s = sa;
                }
                else
                {
                    l = i;
                    if( e( i ) == 0 )
                    {
                        std::tie( cdivr, cdivi ) = cdiv( -ra, -sa, w, q );
                        H( i, n - 1 ) = cdivr;
                        H( i, n ) = cdivi;
                    }
                    else
                    {

                        // Solve complex equations

                        x = H( i, i + 1 );
                        y = H( i + 1, i );
                        vr = ( d( i ) - p ) * ( d( i ) - p ) + e( i ) * e( i ) - q * q;
                        vi = ( d( i ) - p ) * 2.0 * q;
                        if( vr == 0.0 && vi == 0.0 )
                        {
                            vr = eps * norm * ( std::abs( w ) + std::abs( q ) +
                                                std::abs( x ) + std::abs( y ) + std::abs( z ) );
                        }
                        std::tie( cdivr, cdivi ) = cdiv( x * r - z * ra + q * sa, x * s - z * sa - q * ra, vr, vi );
                        H( i, n - 1 ) = cdivr;
                        H( i, n ) = cdivi;
                        if( std::abs( x ) > ( std::abs( z ) + std::abs( q ) ) )
                        {
                            H( i + 1, n - 1 ) = ( -ra - w * H( i, n - 1 ) + q * H( i, n ) ) / x;
                            H( i + 1, n ) = ( -sa - w * H( i, n ) - q * H( i, n - 1 ) ) / x;
                        }
                        else
                        {
                            std::tie( cdivr, cdivi ) = cdiv( -r - y * H( i, n - 1 ), -s - y * H( i, n ), z, q );
                            H( i + 1, n - 1 ) = cdivr;
                            H( i + 1, n ) = cdivi;
                        }
                    }

                    // Overflow control

                    t = std::max( std::abs( H( i, n - 1 ) ), std::abs( H( i, n ) ) );
                    if( ( eps * t ) * t > 1 )
                    {
                        for( int j = i; j <= n; j++ )
                        {
                            H( j, n - 1 ) = H( j, n - 1 ) / t;
                            H( j, n ) = H( j, n ) / t;
                        }
                    }
                }
            }
        }
    }

    // Vectors of isolated roots

    for( int i = 0; i < nn; i++ )
    {
        if( i < low || i > high )
        {
            for( int j = i; j < nn; j++ )
            {
                V( i, j ) = H( i, j );
            }
        }
    }

    // Back transformation to get eigenvectors of original matrix

    for( int j = nn - 1; j >= low; j-- )
    {
        for( int i = low; i <= high; i++ )
        {
            z = 0.0;
            for( int k = low; k <= std::min( j, high ); k++ )
            {
                z = z + V( i, k ) * H( k, j );
            }
            V( i, j ) = z;
        }
    }
}

// Algorithm 2 of https://www.math.kth.se/na/SF2524/matber15/qrmethod.pdf
// https://people.inf.ethz.ch/arbenz/ewp/Lnotes/2010/chapter3.pdf
// https://chayanbhawal.github.io/files/SRG17_presentation.pdf
MLHP_EXPORT void hessenberg( std::span<double> A,
                             std::span<double> tmp,
                             std::span<double> V )
{
    return orthes( A, tmp, V );
    
    //auto* MLHP_RESTRICT A = APtr;
    //auto* MLHP_RESTRICT v = tmpPtr;
    //auto* MLHP_RESTRICT Q = QPtr;

    //// Initialize U to identity if not a nullptr
    //if( Q )
    //{
    //    identity( std::span( Q, n * n ), n );
    //}

    //for( size_t k = 0; k + 2 < n; ++k )
    //{
    //    // Extract subvector v[k + 1:n] = A[k + 1:n, k]
    //    for( size_t i = k + 1; i < n; ++i )
    //    {
    //        v[i] = A[i * n + k];
    //    }

    //    // Compute reflector in subspan v[k + 1:n]
    //    auto x = std::span( v + k + 1, n - k - 1 );
    //    auto [alpha, beta] = householderVector( x, x );
    //    auto scaling = std::sqrt( beta / 2.0 );

    //    for( auto& xi : x )
    //    {
    //        xi *= scaling;
    //    }

    //    // Compute vTa = v.T * A[k + 1:, k + 1:] in subspan
    //    auto* MLHP_RESTRICT vTA = tmpPtr + n;

    //    for( size_t i = k + 1; i < n; ++i )
    //    {
    //        vTA[i] = 0.0;

    //        for( size_t j = k + 1; j < n; ++j )
    //        {
    //            vTA[i] += v[j] * A[j * n + i];
    //        }
    //    }

    //    // Compute A[k + 1:, k + 1:] -= 2 * v * vTa
    //    for( size_t i = k + 1; i < n; ++i )
    //    {
    //        for( size_t j = k + 1; j < n; ++j )
    //        {
    //            A[i * n + j] -= 2.0 * v[i] * vTA[j];
    //        }
    //    }

    //    // Set A[k + 1, k] = alpha and A[k + 2:, k] = 0
    //    A[( k + 1 ) * n + k] = alpha;

    //    for( size_t i = k + 2; i < n; ++i )
    //    {
    //        A[i * n + k] = 0.0;
    //    }

    //    // Compute A[:, k + 1:] * v
    //    auto* MLHP_RESTRICT Av = tmpPtr + n;

    //    for( size_t i = 0; i < n; ++i )
    //    {
    //        Av[i] = 0.0;

    //        for( size_t j = k + 1; j < n; ++j )
    //        {
    //            Av[i] += A[i * n + j] * v[j];
    //        }
    //    }

    //    // Compute A[:, k + 1:] -= 2 * Av * v.T;
    //    for( size_t i = 0; i < n; ++i )
    //    {
    //        for( size_t j = k + 1; j < n; ++j )
    //        {
    //            A[i * n + j] -= 2.0 * Av[i] * v[j];
    //        }
    //    }

    //    if( Q )
    //    {
    //        // Compute Q[:, k + 1:] * v[k + 1:]
    //        auto* MLHP_RESTRICT Qv = tmpPtr + n;

    //        for( size_t i = 0; i < n; ++i )
    //        {
    //            Qv[i] = 0.0;

    //            for( size_t j = k + 1; j < n; ++j )
    //            {
    //                Qv[i] += Q[i * n + j] * v[j];
    //            }
    //        }

    //        // Compute Q[:, k + 1:] -= 2 * Qv * v.T
    //        for( size_t i = 0; i < n; ++i )
    //        {
    //            for( size_t j = k + 1; j < n; ++j )
    //            {
    //                Q[i * n + j] -= 2.0 * Qv[i] * v[j];
    //            }
    //        }
    //    }
    //}
}

//namespace
//{
//
//void multiplyEigenvectors( std::span<double> Q1, 
//                           std::span<double> Q2, 
//                           std::span<double> tmp )
//{
//    auto n = tmp.size( );
//
//    MLHP_CHECK( Q1.size( ) == n * n, "Inconsistent sizes." );
//    MLHP_CHECK( Q2.size( ) == n * n, "Inconsistent sizes." );
//
//    // To produce the same output as numpy / scipy we compute Q1 = Q1 @ Q2 here ...
//    for( size_t i = 0; i < n; ++i )
//    {
//        auto rowQ1 = Q1.subspan( i * n, n );
//        auto rowTmp = tmp;
//
//        std::copy( rowQ1.begin( ), rowQ1.end( ), rowTmp.begin( ) );
//        std::fill( rowQ1.begin( ), rowQ1.end( ), 0.0 );
//
//        for( size_t j = 0; j < n; ++j )
//        {
//            for( size_t k = 0; k < n; ++k )
//            {
//                rowQ1[j] += rowTmp[k] * Q2[k * n + j];
//            }
//        }
//    }
//
//    // ... since that yields non-contiguous eigenvalues, we compute Q1 = Q2.T * Q1.T instead
//    for( size_t i = 0; i < n; ++i )
//    {
//        for( size_t j = i + 1; j < n; ++j )
//        {
//            std::swap( Q1[i * n + j], Q1[j * n + i] );
//        }
//    }
//}
//
//}

// Algorithm 3.6 of https://people.inf.ethz.ch/arbenz/ewp/Lnotes/2010/chapter3.pdf
// https://www.math.kth.se/na/SF2524/matber15/qrmethod.pdf
void eigh( std::span<double> A,
           std::span<double> lambda,
           std::span<double> tmp )
{
    if( A.empty( ) && lambda.empty( ) && tmp.empty( ) )
    {
        return;
    }

    tred2( A, lambda, tmp );

    tql2( A, lambda, tmp );

    transpose( A, lambda.size( ) );

    return;

    //auto n = lambda.size( );
    //auto Q1 = eigenvectors;
    //auto Q2 = tmp.subspan( 0, eigenvectors.empty( ) ? 2 * n : n * n );
    //auto a = lambda;
    //auto b = A.subspan( 0, n );

    //MLHP_CHECK( A.size( ) == n * n, "Inconsistent span sizes." );
    //MLHP_CHECK( tmp.size( ) >= 2 * n, "Temporary storage too small." );
    //MLHP_CHECK( eigenvectors.empty( ) || tmp.size( ) >= n * n, "Temporary storage too small." );
    //MLHP_CHECK( Q1.empty( ) || Q1.size( ) == n * n, "Inconsistent eigenvector target memory size." );

    //if( n == 0 )
    //{
    //    return;
    //}

    //hessenberg( A.data( ), tmp.data( ), n, Q1.empty( ) ? nullptr : Q1.data( ) );

    //// Initialize eigenvectors to identity if we need to compute them
    //if( !eigenvectors.empty( ) )
    //{
    //    identity( Q2, n );
    //}

    //a[0] = A[0];

    //for( size_t i = 1; i < n; ++i )
    //{
    //    a[i] = A[i * n + i];
    //    b[i] = A[( i - 1 ) * n + i];
    //}

    //auto m = n - 1;

    //while( m > 0 )
    //{
    //    auto d = ( a[m - 1] - a[m] ) / 2.0;
    //    auto s = 0.0;

    //    if( d == 0.0 )
    //    {
    //        s = a[m] - std::abs( b[m] );
    //    }
    //    else
    //    {
    //        auto signd = d >= 0.0 ? 1.0 : -1.0;
    //        auto bm2 = b[m] * b[m];

    //        s = a[m] - bm2 / ( d + signd * std::sqrt( d * d + bm2 ) );
    //    }

    //    auto x = a[0] - s;
    //    auto y = b[1];

    //    for( size_t k = 0; k < m; ++k )
    //    {
    //        auto c = 0.0, s = 0.0;

    //        if( m > 1 )
    //        {
    //            auto g = givens( x, y );

    //            c = g[0];
    //            s = g[1];
    //        }
    //        else
    //        {
    //            auto A = std::array { a[0], b[1], b[1], a[1] };
    //            auto [l1, l2] = eigh2D( A );
    //            auto [v1, v2] = eigh2Dv( A, { l1, l2 } );

    //            c = v1[0];
    //            s = v2[0];
    //        }

    //        auto w = c * x - s * y;
    //        auto d = a[k] - a[k + 1];
    //        auto z = ( 2 * c * b[k + 1] + d * s ) * s;

    //        a[k] -= z;
    //        a[k + 1] += z;
    //        b[k + 1] = d * c * s + ( c * c - s * s ) * b[k + 1];
    //        x = b[k + 1];

    //        if( k > 0 )
    //        {
    //            b[k] = w;
    //        }

    //        if( k + 1 < m )
    //        {
    //            y = -s * b[k + 2];
    //            b[k + 2] *= c;
    //        }

    //        if( !eigenvectors.empty( ) )
    //        {
    //            // Q[:, k : k + 2] = Q[:, k : k + 2] @ [[c, -s], [s, c]]
    //            for( size_t i = 0; i < n; ++i )
    //            {
    //                auto Qnew = Q2.subspan( i * n + k, 2 );
    //                auto Qold = std::array { Qnew[0], Qnew[1] };

    //                Qnew[0] = c * Qold[0] - s * Qold[1];
    //                Qnew[1] = s * Qold[0] + c * Qold[1];
    //            }
    //        }
    //    }

    //    constexpr auto eps = 1e-12;

    //    if( std::abs( b[m] ) < eps * ( std::abs( a[m - 1] ) + std::abs( a[m] ) ) )
    //    {
    //        m -= 1;
    //    }
    //}

    //if( !eigenvectors.empty( ) )
    //{
    //    multiplyEigenvectors( Q1, Q2, A.subspan( 0, n ) );
    //}
}

MLHP_EXPORT void eig( std::span<double> A,
                      std::span<double> B,
                      std::span<double> real,
                      std::span<double> imag,
                      std::span<size_t> perm,
                      std::span<double> V )
{
    auto n = real.size( );

    MLHP_CHECK( A.size( ) == n * n, "Inconsistent input size." );
    MLHP_CHECK( B.size( ) == n * n, "Inconsistent input size." );
    MLHP_CHECK( imag.size( ) == n, "Inconsistent input size." );
    MLHP_CHECK( perm.size( ) == n, "Inconsistent input size." );

    auto Bnorm = linalg::norm( B );
    auto luResult = linalg::luFactor( B, perm, 1e-12 * Bnorm );

    MLHP_CHECK( luResult != -1, "B matrix is singular." );

    // For each column in A: extract, triangular solve, write back
    for( size_t j = 0; j < n; ++j )
    {
        auto colAOld = imag;
        auto colANew = real;

        for( size_t i = 0; i < n; ++i )
        {
            colAOld[i] = A[i * n + j];
        }

        linalg::luSubstitute( B, perm, colAOld, colANew );

        for( size_t i = 0; i < n; ++i )
        {
            A[i * n + j] = colANew[i];
        }
    }

    linalg::eig( A, real, imag.subspan( 0, real.size( ) ), V );
}

//namespace
//{
//
//template<std::integral Int1, std::integral Int2, std::integral Int3, size_t N>
//auto updateColumns( auto&& M, 
//                    std::span<const double> P, 
//                    Int1 rowBegin, Int2 rowEnd,
//                    std::array<Int3, N> columnIndices )
//{
//    for( auto irow = rowBegin; irow < rowEnd; ++irow )
//    {
//        auto oldValues = std::array<double, N> { };
//
//        for( size_t j = 0; j < N; ++j )
//        {
//            oldValues[j] = M( irow, columnIndices[j] );
//        }
//
//        auto newValues = linalg::mvproduct<N, N>( P, oldValues );
//
//        for( size_t j = 0; j < N; ++j )
//        {
//            M( irow, columnIndices[j] ) = newValues[j];
//        }
//    }
//}
//
//template<std::integral Int1, std::integral Int2, std::integral Int3, size_t N>
//auto updateRows( auto&& M, 
//                 std::span<const double> P, 
//                 std::array<Int1, N> rowIndices,
//                 Int2 columnBegin, Int3 columnEnd )
//{
//    for( auto jcolumn = columnBegin; jcolumn < columnEnd; ++jcolumn )
//    {
//        auto oldValues = std::array<double, N> { };
//
//        for( size_t i = 0; i < N; ++i )
//        {
//            oldValues[i] = M( rowIndices[i], jcolumn );
//        }
//
//        auto newValues = linalg::mvproduct<N, N>( P, oldValues );
//
//        for( size_t i = 0; i < N; ++i )
//        {
//            M( rowIndices[i], jcolumn ) = newValues[i];
//        }
//    }
//}
//
//}

// Algorithm 3.5 from https://people.inf.ethz.ch/arbenz/ewp/Lnotes/2010/chapter3.pdf
// https://math.nist.gov/javanumerics/jama/
void eig( std::span<double> A,
          std::span<double> real,
          std::span<double> imag,
          std::span<double> V )
{
    // Reduce to Hessenberg form.
    orthes( A, real, V );

    // Reduce Hessenberg to real Schur form.
    hqr2( A, real, imag, V );

    transpose( V, real.size( ) );

    //auto n = lambda.size( );
    //auto Q1 = eigenvectors;
    //auto Q2 = tmp.subspan( 0, eigenvectors.empty( ) ? 2 * n : n * n );

    //MLHP_CHECK( A.size( ) == n * n, "Inconsistent matrix size." );
    //MLHP_CHECK( tmp.size( ) >= 2 * n, "Temporary storage too small." );
    //MLHP_CHECK( eigenvectors.empty( ) || tmp.size( ) >= n * n, "Temporary storage too small." );
    //MLHP_CHECK( eigenvectors.empty( ) || eigenvectors.size( ) >= n * n, "Inconsistent eigenvector target memory size." );

    //if( n == 0 )
    //{
    //    return;
    //}

    //hessenberg( A.data( ), tmp.data( ), n, Q1.empty( ) ? nullptr : Q1.data( ) );
    //
    //// Initialize eigenvectors to identity if we need to compute them
    //if( !eigenvectors.empty( ) )
    //{
    //    identity( Q2, n );
    //}

    //auto H = [&]( auto i, auto j ) -> double& { return A[(i - 1) * n + (j - 1)]; };
    //auto Q = [&]( auto i, auto j ) -> double& { return Q2[(i - 1) * n + (j - 1)]; };
    //auto p = static_cast<int>( n );

    ////auto it = 0;

    //while( p > 2 )
    //{
    //    auto H_p_pm1 = H( p, p - 1 );
    //    auto H_pm1_pm2 = H( p - 1, p - 2 );

    //    auto q = p - 1;
    //    auto s = H( q, q ) + H( p, p );
    //    auto t = H( q, q ) * H( p, p ) - H( p, q ) * H( q, p );
    //    auto x = H( 1, 1 ) * H( 1, 1 ) + H( 1, 2 ) * H( 2, 1 ) - s * H( 1, 1 ) + t;
    //    auto y = H( 2, 1 ) * ( H( 1, 1 ) + H( 2, 2 ) - s );
    //    auto z = H( 2, 1 ) * H( 3, 2 );

    //    for( int k = 0; k + 3 <= p; ++k )
    //    {
    //        auto P = std::array<double, 9> { };

    //        {
    //            auto xyz = std::array { x, y, z };

    //            householderMatrix( xyz, P );
    //        }

    //        auto r = std::max( 1, k );

    //        updateRows( H, P, std::array { k + 1, k + 2, k + 3 }, r, n + 1 );

    //        r = std::min( k + 4, p );

    //        updateColumns( H, P, 1, r + 1, std::array { k + 1, k + 2, k + 3 } );

    //        if( !eigenvectors.empty( ) )
    //        {
    //            updateColumns( Q, P, 1, n + 1, std::array { k + 1, k + 2, k + 3 } );
    //        }

    //        x = H( k + 2, k + 1 );
    //        y = H( k + 3, k + 1 );

    //        if( k + 3 < p )
    //        {
    //            z = H( k + 4, k + 1 );
    //        }
    //    }

    //    //auto [gc, gs] = givens( x, y );
    //    //auto P = std::array { gc, gs, -gs, gc };
    //    //auto PT = std::array { gc, -gs, gs, gc };

    //    auto P = std::array<double, 4> { };
    //    {
    //        auto xy = std::array { x, y };

    //        householderMatrix( xy, P );
    //    }
    //    auto PT = P;

    //    updateRows( H, PT, std::array { q, p }, p - 2, n + 1 );
    //    updateColumns( H, P, 1, p + 1, std::array { p - 1, p } );

    //    if( !eigenvectors.empty( ) )
    //    {
    //        updateColumns( Q, P, 1, n + 1, std::array { p - 1, p } );
    //    }

    //    constexpr auto eps = 1e-15;

    //    //std::cout << ++it << "     " << p << "    " << H( p, p - 1 ) << "      " << H( p - 1, p - 2 ) << std::endl;

    //    if( std::abs( H( p, q ) ) < eps * ( std::abs( H( q, q ) ) + std::abs( H( p, p ) ) ) )
    //    {
    //        //std::cout << std::setprecision( 13 ) << "\nH(" << it << ") = \n" << std::endl;// << "--------------------------\n";
    //        //for( size_t i = 1; i <= n; ++i )
    //        //{
    //        //    for( size_t j = 1; j <= n; ++j )
    //        //    {
    //        //        std::cout << std::setw( 20 ) << H( i, j );
    //        //    }
    //        //    std::cout << std::endl;
    //        //}
    //        //std::cout << std::endl;

    //        H( p, q ) = 0.0;
    //        p -= 1;
    //        q = p - 1;
    //    }
    //    else if( std::abs( H( p - 1, q - 1 ) ) < eps * ( std::abs( H( q - 1, q - 1 ) ) + std::abs( H( q, q ) ) ) )
    //    {
    //        //std::cout << std::setprecision( 13 ) << "\nH(" << it << ") = \n" << std::endl;// << "--------------------------\n";
    //        //for( size_t i = 1; i <= n; ++i )
    //        //{
    //        //    for( size_t j = 1; j <= n; ++j )
    //        //    {
    //        //        std::cout << std::setw( 20 ) << H( i, j );
    //        //    }
    //        //    std::cout << std::endl;
    //        //}
    //        //std::cout << std::endl;

    //        H( p - 1, q - 1 ) = 0.0;
    //        p -= 2;
    //        q = p - 1;
    //    }
    //}

    //for( size_t i = 0; i < n; ++i )
    //{
    //    lambda[i] = H( i + 1, i + 1 );
    //}

    //if( !eigenvectors.empty( ) )
    //{
    //    multiplyEigenvectors( Q1, Q2, A.subspan( 0, n ) );
    //}
}

MLHP_EXPORT void sorteig( std::span<double> lambda,
                          std::span<double> eigenvectors,
                          bool abs,
                          bool ascending )
{
    auto n = lambda.size( );
    auto V = !eigenvectors.empty( );

    MLHP_CHECK( !V || eigenvectors.size( ) == n * n, "Inconsistent input data." );

    for( size_t i = 0; i + 1 < n; ++i )
    {
        for( size_t j = 0; j + i + 1 < n; ++j )
        {
            auto cmp = abs ? std::abs( lambda[j] ) > std::abs( 
                lambda[j + 1] ) : lambda[j] > lambda[j + 1];

            if( cmp == ascending )
            {
                std::swap( lambda[j], lambda[j + 1] );

                if( V )
                {
                    auto v0 = eigenvectors.subspan( j * n, n );
                    auto v1 = eigenvectors.subspan( ( j + 1 ) * n, n );
                    
                    std::ranges::swap_ranges( v0, v1 );
                }
            }
        }
    }
}

void sorteig( std::span<double> lambda, bool abs, bool ascending )
{
    sorteig( lambda, std::span<double> { }, abs, ascending );
}

double norm( std::span<const double> data )
{
    return std::sqrt( std::inner_product( data.begin( ), data.end( ), data.begin( ), 0.0 ) );
}

bool issymmetric( std::span<const double> M, size_t size, double tolerance )
{
    MLHP_CHECK( M.size( ) == size * size, "Inconsistent matrix size." );

    auto eps = tolerance * linalg::norm( M );

    for( size_t i = 0; i < size; ++i )
    {
        for( size_t j = 0; j < size; ++j )
        {
            if( std::abs( M[i * size + j] - M[j * size + i] ) > eps )
            {
                return false;
            }
        }
    }

    return true;
}

void identity( std::span<double> M, size_t size )
{
    MLHP_CHECK( M.size( ) == size * size, "Invalid size." );

    for( size_t i = 0; i < size; ++i )
    {
        for( size_t j = 0; j < size; ++j )
        {
            M[i * size + j] = i == j;
        }
    }
}

// See also blaze/math/dense/Inversion.h
double invertSmall2( const auto& S, auto& T )
{
    T( 0, 0 ) = S( 1, 1 );
    T( 1, 0 ) = -S( 1, 0 );
    T( 0, 1 ) = -S( 0, 1 );
    T( 1, 1 ) = S( 0, 0 );

    return S( 0, 0 ) * S( 1, 1 ) - S( 0, 1 ) * S( 1, 0 );
}

// See also blaze/math/dense/Inversion.h
double invertSmallUnsymmetric3( const auto& S, auto& T )
{
    T( 0, 0 ) = S( 1, 1 ) * S( 2, 2 ) - S( 1, 2 ) * S( 2, 1 );
    T( 1, 0 ) = S( 1, 2 ) * S( 2, 0 ) - S( 1, 0 ) * S( 2, 2 );
    T( 2, 0 ) = S( 1, 0 ) * S( 2, 1 ) - S( 1, 1 ) * S( 2, 0 );

    double det =( S( 0, 0 ) * T( 0, 0 ) + S( 0, 1 ) * T( 1, 0 ) + S( 0, 2 ) * T( 2, 0 ) );

    T( 0, 1 ) = S( 0, 2 ) * S( 2, 1 ) - S( 0, 1 ) * S( 2, 2 );
    T( 1, 1 ) = S( 0, 0 ) * S( 2, 2 ) - S( 0, 2 ) * S( 2, 0 );
    T( 2, 1 ) = S( 0, 1 ) * S( 2, 0 ) - S( 0, 0 ) * S( 2, 1 );
    T( 0, 2 ) = S( 0, 1 ) * S( 1, 2 ) - S( 0, 2 ) * S( 1, 1 );
    T( 1, 2 ) = S( 0, 2 ) * S( 1, 0 ) - S( 0, 0 ) * S( 1, 2 );
    T( 2, 2 ) = S( 0, 0 ) * S( 1, 1 ) - S( 0, 1 ) * S( 1, 0 );

    return det;
}

// See also blaze/math/dense/Inversion.h
double invertSmallUnsymmetric4( const auto& S, auto& T )
{
    double tmp1 = S( 2, 2 ) * S( 3, 3 ) - S( 2, 3 ) * S( 3, 2 );
    double tmp2 = S( 2, 1 ) * S( 3, 3 ) - S( 2, 3 ) * S( 3, 1 );
    double tmp3 = S( 2, 1 ) * S( 3, 2 ) - S( 2, 2 ) * S( 3, 1 );

    T( 0, 0 ) = S( 1, 1 ) * tmp1 - S( 1, 2 ) * tmp2 + S( 1, 3 ) * tmp3;
    T( 0, 1 ) = S( 0, 2 ) * tmp2 - S( 0, 1 ) * tmp1 - S( 0, 3 ) * tmp3;

    double tmp4 = S( 2, 0 ) * S( 3, 3 ) - S( 2, 3 ) * S( 3, 0 );
    double tmp5 = S( 2, 0 ) * S( 3, 2 ) - S( 2, 2 ) * S( 3, 0 );

    T( 1, 0 ) = S( 1, 2 ) * tmp4 - S( 1, 0 ) * tmp1 - S( 1, 3 ) * tmp5;
    T( 1, 1 ) = S( 0, 0 ) * tmp1 - S( 0, 2 ) * tmp4 + S( 0, 3 ) * tmp5;

    tmp1 = S( 2, 0 ) * S( 3, 1 ) - S( 2, 1 ) * S( 3, 0 );

    T( 2, 0 ) = S( 1, 0 ) * tmp2 - S( 1, 1 ) * tmp4 + S( 1, 3 ) * tmp1;
    T( 2, 1 ) = S( 0, 1 ) * tmp4 - S( 0, 0 ) * tmp2 - S( 0, 3 ) * tmp1;
    T( 3, 0 ) = S( 1, 1 ) * tmp5 - S( 1, 0 ) * tmp3 - S( 1, 2 ) * tmp1;
    T( 3, 1 ) = S( 0, 0 ) * tmp3 - S( 0, 1 ) * tmp5 + S( 0, 2 ) * tmp1;

    tmp1 = S( 0, 2 ) * S( 1, 3 ) - S( 0, 3 ) * S( 1, 2 );
    tmp2 = S( 0, 1 ) * S( 1, 3 ) - S( 0, 3 ) * S( 1, 1 );
    tmp3 = S( 0, 1 ) * S( 1, 2 ) - S( 0, 2 ) * S( 1, 1 );

    T( 0, 2 ) = S( 3, 1 ) * tmp1 - S( 3, 2 ) * tmp2 + S( 3, 3 ) * tmp3;
    T( 0, 3 ) = S( 2, 2 ) * tmp2 - S( 2, 1 ) * tmp1 - S( 2, 3 ) * tmp3;

    tmp4 = S( 0, 0 ) * S( 1, 3 ) - S( 0, 3 ) * S( 1, 0 );
    tmp5 = S( 0, 0 ) * S( 1, 2 ) - S( 0, 2 ) * S( 1, 0 );

    T( 1, 2 ) = S( 3, 2 ) * tmp4 - S( 3, 0 ) * tmp1 - S( 3, 3 ) * tmp5;
    T( 1, 3 ) = S( 2, 0 ) * tmp1 - S( 2, 2 ) * tmp4 + S( 2, 3 ) * tmp5;

    tmp1 = S( 0, 0 ) * S( 1, 1 ) - S( 0, 1 ) * S( 1, 0 );

    T( 2, 2 ) = S( 3, 0 ) * tmp2 - S( 3, 1 ) * tmp4 + S( 3, 3 ) * tmp1;
    T( 2, 3 ) = S( 2, 1 ) * tmp4 - S( 2, 0 ) * tmp2 - S( 2, 3 ) * tmp1;
    T( 3, 2 ) = S( 3, 1 ) * tmp5 - S( 3, 0 ) * tmp3 - S( 3, 2 ) * tmp1;
    T( 3, 3 ) = S( 2, 0 ) * tmp3 - S( 2, 1 ) * tmp5 + S( 2, 2 ) * tmp1;

    return S( 0, 0 ) * T( 0, 0 ) + S( 0, 1 ) * T( 1, 0 ) + 
           S( 0, 2 ) * T( 2, 0 ) + S( 0, 3 ) * T( 3, 0 );
}

// See also blaze/math/dense/Inversion.h
double invertSmallUnsymmetric5( const auto& S, auto& T )
{
    double tmp1 = S( 3, 3 ) * S( 4, 4 ) - S( 3, 4 ) * S( 4, 3 );
    double tmp2 = S( 3, 2 ) * S( 4, 4 ) - S( 3, 4 ) * S( 4, 2 );
    double tmp3 = S( 3, 2 ) * S( 4, 3 ) - S( 3, 3 ) * S( 4, 2 );
    double tmp4 = S( 3, 1 ) * S( 4, 4 ) - S( 3, 4 ) * S( 4, 1 );
    double tmp5 = S( 3, 1 ) * S( 4, 3 ) - S( 3, 3 ) * S( 4, 1 );
    double tmp6 = S( 3, 1 ) * S( 4, 2 ) - S( 3, 2 ) * S( 4, 1 );
    double tmp7 = S( 3, 0 ) * S( 4, 4 ) - S( 3, 4 ) * S( 4, 0 );
    double tmp8 = S( 3, 0 ) * S( 4, 3 ) - S( 3, 3 ) * S( 4, 0 );
    double tmp9 = S( 3, 0 ) * S( 4, 2 ) - S( 3, 2 ) * S( 4, 0 );
    double tmp10 = S( 3, 0 ) * S( 4, 1 ) - S( 3, 1 ) * S( 4, 0 );

    double tmp11 = S( 2, 2 ) * tmp1 - S( 2, 3 ) * tmp2 + S( 2, 4 ) * tmp3;
    double tmp12 = S( 2, 1 ) * tmp1 - S( 2, 3 ) * tmp4 + S( 2, 4 ) * tmp5;
    double tmp13 = S( 2, 1 ) * tmp2 - S( 2, 2 ) * tmp4 + S( 2, 4 ) * tmp6;
    double tmp14 = S( 2, 1 ) * tmp3 - S( 2, 2 ) * tmp5 + S( 2, 3 ) * tmp6;
    double tmp15 = S( 2, 0 ) * tmp1 - S( 2, 3 ) * tmp7 + S( 2, 4 ) * tmp8;
    double tmp16 = S( 2, 0 ) * tmp2 - S( 2, 2 ) * tmp7 + S( 2, 4 ) * tmp9;
    double tmp17 = S( 2, 0 ) * tmp3 - S( 2, 2 ) * tmp8 + S( 2, 3 ) * tmp9;

    T( 0, 0 ) = S( 1, 1 ) * tmp11 - S( 1, 2 ) * tmp12 + S( 1, 3 ) * tmp13 - S( 1, 4 ) * tmp14;
    T( 0, 1 ) = -S( 0, 1 ) * tmp11 + S( 0, 2 ) * tmp12 - S( 0, 3 ) * tmp13 + S( 0, 4 ) * tmp14;
    T( 1, 0 ) = -S( 1, 0 ) * tmp11 + S( 1, 2 ) * tmp15 - S( 1, 3 ) * tmp16 + S( 1, 4 ) * tmp17;
    T( 1, 1 ) = S( 0, 0 ) * tmp11 - S( 0, 2 ) * tmp15 + S( 0, 3 ) * tmp16 - S( 0, 4 ) * tmp17;

    double tmp18 = S( 2, 0 ) * tmp4 - S( 2, 1 ) * tmp7 + S( 2, 4 ) * tmp10;
    double tmp19 = S( 2, 0 ) * tmp5 - S( 2, 1 ) * tmp8 + S( 2, 3 ) * tmp10;
    double tmp20 = S( 2, 0 ) * tmp6 - S( 2, 1 ) * tmp9 + S( 2, 2 ) * tmp10;

    T( 2, 0 ) = S( 1, 0 ) * tmp12 - S( 1, 1 ) * tmp15 + S( 1, 3 ) * tmp18 - S( 1, 4 ) * tmp19;
    T( 2, 1 ) = -S( 0, 0 ) * tmp12 + S( 0, 1 ) * tmp15 - S( 0, 3 ) * tmp18 + S( 0, 4 ) * tmp19;
    T( 3, 0 ) = -S( 1, 0 ) * tmp13 + S( 1, 1 ) * tmp16 - S( 1, 2 ) * tmp18 + S( 1, 4 ) * tmp20;
    T( 3, 1 ) = S( 0, 0 ) * tmp13 - S( 0, 1 ) * tmp16 + S( 0, 2 ) * tmp18 - S( 0, 4 ) * tmp20;
    T( 4, 0 ) = S( 1, 0 ) * tmp14 - S( 1, 1 ) * tmp17 + S( 1, 2 ) * tmp19 - S( 1, 3 ) * tmp20;
    T( 4, 1 ) = -S( 0, 0 ) * tmp14 + S( 0, 1 ) * tmp17 - S( 0, 2 ) * tmp19 + S( 0, 3 ) * tmp20;

    tmp11 = S( 1, 2 ) * tmp1 - S( 1, 3 ) * tmp2 + S( 1, 4 ) * tmp3;
    tmp12 = S( 1, 1 ) * tmp1 - S( 1, 3 ) * tmp4 + S( 1, 4 ) * tmp5;
    tmp13 = S( 1, 1 ) * tmp2 - S( 1, 2 ) * tmp4 + S( 1, 4 ) * tmp6;
    tmp14 = S( 1, 1 ) * tmp3 - S( 1, 2 ) * tmp5 + S( 1, 3 ) * tmp6;
    tmp15 = S( 1, 0 ) * tmp1 - S( 1, 3 ) * tmp7 + S( 1, 4 ) * tmp8;
    tmp16 = S( 1, 0 ) * tmp2 - S( 1, 2 ) * tmp7 + S( 1, 4 ) * tmp9;
    tmp17 = S( 1, 0 ) * tmp3 - S( 1, 2 ) * tmp8 + S( 1, 3 ) * tmp9;
    tmp18 = S( 1, 0 ) * tmp4 - S( 1, 1 ) * tmp7 + S( 1, 4 ) * tmp10;
    tmp19 = S( 1, 0 ) * tmp5 - S( 1, 1 ) * tmp8 + S( 1, 3 ) * tmp10;

    T( 0, 2 ) = S( 0, 1 ) * tmp11 - S( 0, 2 ) * tmp12 + S( 0, 3 ) * tmp13 - S( 0, 4 ) * tmp14;
    T( 1, 2 ) = -S( 0, 0 ) * tmp11 + S( 0, 2 ) * tmp15 - S( 0, 3 ) * tmp16 + S( 0, 4 ) * tmp17;
    T( 2, 2 ) = S( 0, 0 ) * tmp12 - S( 0, 1 ) * tmp15 + S( 0, 3 ) * tmp18 - S( 0, 4 ) * tmp19;

    tmp1 = S( 0, 2 ) * S( 1, 3 ) - S( 0, 3 ) * S( 1, 2 );
    tmp2 = S( 0, 1 ) * S( 1, 3 ) - S( 0, 3 ) * S( 1, 1 );
    tmp3 = S( 0, 1 ) * S( 1, 2 ) - S( 0, 2 ) * S( 1, 1 );
    tmp4 = S( 0, 0 ) * S( 1, 3 ) - S( 0, 3 ) * S( 1, 0 );
    tmp5 = S( 0, 0 ) * S( 1, 2 ) - S( 0, 2 ) * S( 1, 0 );
    tmp6 = S( 0, 0 ) * S( 1, 1 ) - S( 0, 1 ) * S( 1, 0 );
    tmp7 = S( 0, 2 ) * S( 1, 4 ) - S( 0, 4 ) * S( 1, 2 );
    tmp8 = S( 0, 1 ) * S( 1, 4 ) - S( 0, 4 ) * S( 1, 1 );
    tmp9 = S( 0, 0 ) * S( 1, 4 ) - S( 0, 4 ) * S( 1, 0 );
    tmp10 = S( 0, 3 ) * S( 1, 4 ) - S( 0, 4 ) * S( 1, 3 );

    tmp11 = S( 2, 2 ) * tmp10 - S( 2, 3 ) * tmp7 + S( 2, 4 ) * tmp1;
    tmp12 = S( 2, 1 ) * tmp10 - S( 2, 3 ) * tmp8 + S( 2, 4 ) * tmp2;
    tmp13 = S( 2, 1 ) * tmp7 - S( 2, 2 ) * tmp8 + S( 2, 4 ) * tmp3;
    tmp14 = S( 2, 1 ) * tmp1 - S( 2, 2 ) * tmp2 + S( 2, 3 ) * tmp3;
    tmp15 = S( 2, 0 ) * tmp10 - S( 2, 3 ) * tmp9 + S( 2, 4 ) * tmp4;
    tmp16 = S( 2, 0 ) * tmp7 - S( 2, 2 ) * tmp9 + S( 2, 4 ) * tmp5;
    tmp17 = S( 2, 0 ) * tmp1 - S( 2, 2 ) * tmp4 + S( 2, 3 ) * tmp5;

    T( 0, 3 ) = S( 4, 1 ) * tmp11 - S( 4, 2 ) * tmp12 + S( 4, 3 ) * tmp13 - S( 4, 4 ) * tmp14;
    T( 0, 4 ) = -S( 3, 1 ) * tmp11 + S( 3, 2 ) * tmp12 - S( 3, 3 ) * tmp13 + S( 3, 4 ) * tmp14;
    T( 1, 3 ) = -S( 4, 0 ) * tmp11 + S( 4, 2 ) * tmp15 - S( 4, 3 ) * tmp16 + S( 4, 4 ) * tmp17;
    T( 1, 4 ) = S( 3, 0 ) * tmp11 - S( 3, 2 ) * tmp15 + S( 3, 3 ) * tmp16 - S( 3, 4 ) * tmp17;

    tmp18 = S( 2, 0 ) * tmp8 - S( 2, 1 ) * tmp9 + S( 2, 4 ) * tmp6;
    tmp19 = S( 2, 0 ) * tmp2 - S( 2, 1 ) * tmp4 + S( 2, 3 ) * tmp6;
    tmp20 = S( 2, 0 ) * tmp3 - S( 2, 1 ) * tmp5 + S( 2, 2 ) * tmp6;

    T( 2, 3 ) = S( 4, 0 ) * tmp12 - S( 4, 1 ) * tmp15 + S( 4, 3 ) * tmp18 - S( 4, 4 ) * tmp19;
    T( 2, 4 ) = -S( 3, 0 ) * tmp12 + S( 3, 1 ) * tmp15 - S( 3, 3 ) * tmp18 + S( 3, 4 ) * tmp19;
    T( 3, 3 ) = -S( 4, 0 ) * tmp13 + S( 4, 1 ) * tmp16 - S( 4, 2 ) * tmp18 + S( 4, 4 ) * tmp20;
    T( 3, 4 ) = S( 3, 0 ) * tmp13 - S( 3, 1 ) * tmp16 + S( 3, 2 ) * tmp18 - S( 3, 4 ) * tmp20;
    T( 4, 3 ) = S( 4, 0 ) * tmp14 - S( 4, 1 ) * tmp17 + S( 4, 2 ) * tmp19 - S( 4, 3 ) * tmp20;
    T( 4, 4 ) = -S( 3, 0 ) * tmp14 + S( 3, 1 ) * tmp17 - S( 3, 2 ) * tmp19 + S( 3, 3 ) * tmp20;

    tmp11 = S( 3, 1 ) * tmp7 - S( 3, 2 ) * tmp8 + S( 3, 4 ) * tmp3;
    tmp12 = S( 3, 0 ) * tmp7 - S( 3, 2 ) * tmp9 + S( 3, 4 ) * tmp5;
    tmp13 = S( 3, 0 ) * tmp8 - S( 3, 1 ) * tmp9 + S( 3, 4 ) * tmp6;
    tmp14 = S( 3, 0 ) * tmp3 - S( 3, 1 ) * tmp5 + S( 3, 2 ) * tmp6;

    tmp15 = S( 3, 1 ) * tmp1 - S( 3, 2 ) * tmp2 + S( 3, 3 ) * tmp3;
    tmp16 = S( 3, 0 ) * tmp1 - S( 3, 2 ) * tmp4 + S( 3, 3 ) * tmp5;
    tmp17 = S( 3, 0 ) * tmp2 - S( 3, 1 ) * tmp4 + S( 3, 3 ) * tmp6;

    T( 3, 2 ) = S( 4, 0 ) * tmp11 - S( 4, 1 ) * tmp12 + S( 4, 2 ) * tmp13 - S( 4, 4 ) * tmp14;
    T( 4, 2 ) = -S( 4, 0 ) * tmp15 + S( 4, 1 ) * tmp16 - S( 4, 2 ) * tmp17 + S( 4, 3 ) * tmp14;

    return S( 0, 0 ) * T( 0, 0 ) + S( 0, 1 ) * T( 1, 0 ) + S( 0, 2 ) * 
        T( 2, 0 ) + S( 0, 3 ) * T( 3, 0 ) + S( 0, 4 ) * T( 4, 0 );
}

// See also blaze/math/dense/Inversion.h
double invertSmallUnsymmetric6( const auto& S, auto& T )
{
    double tmp1 = S( 4, 4 ) * S( 5, 5 ) - S( 4, 5 ) * S( 5, 4 );
    double tmp2 = S( 4, 3 ) * S( 5, 5 ) - S( 4, 5 ) * S( 5, 3 );
    double tmp3 = S( 4, 3 ) * S( 5, 4 ) - S( 4, 4 ) * S( 5, 3 );
    double tmp4 = S( 4, 2 ) * S( 5, 5 ) - S( 4, 5 ) * S( 5, 2 );
    double tmp5 = S( 4, 2 ) * S( 5, 4 ) - S( 4, 4 ) * S( 5, 2 );
    double tmp6 = S( 4, 2 ) * S( 5, 3 ) - S( 4, 3 ) * S( 5, 2 );
    double tmp7 = S( 4, 1 ) * S( 5, 5 ) - S( 4, 5 ) * S( 5, 1 );
    double tmp8 = S( 4, 1 ) * S( 5, 4 ) - S( 4, 4 ) * S( 5, 1 );
    double tmp9 = S( 4, 1 ) * S( 5, 3 ) - S( 4, 3 ) * S( 5, 1 );
    double tmp10 = S( 4, 1 ) * S( 5, 2 ) - S( 4, 2 ) * S( 5, 1 );
    double tmp11 = S( 4, 0 ) * S( 5, 5 ) - S( 4, 5 ) * S( 5, 0 );
    double tmp12 = S( 4, 0 ) * S( 5, 4 ) - S( 4, 4 ) * S( 5, 0 );
    double tmp13 = S( 4, 0 ) * S( 5, 3 ) - S( 4, 3 ) * S( 5, 0 );
    double tmp14 = S( 4, 0 ) * S( 5, 2 ) - S( 4, 2 ) * S( 5, 0 );
    double tmp15 = S( 4, 0 ) * S( 5, 1 ) - S( 4, 1 ) * S( 5, 0 );

    double tmp16 = S( 3, 3 ) * tmp1 - S( 3, 4 ) * tmp2 + S( 3, 5 ) * tmp3;
    double tmp17 = S( 3, 2 ) * tmp1 - S( 3, 4 ) * tmp4 + S( 3, 5 ) * tmp5;
    double tmp18 = S( 3, 2 ) * tmp2 - S( 3, 3 ) * tmp4 + S( 3, 5 ) * tmp6;
    double tmp19 = S( 3, 2 ) * tmp3 - S( 3, 3 ) * tmp5 + S( 3, 4 ) * tmp6;
    double tmp20 = S( 3, 1 ) * tmp1 - S( 3, 4 ) * tmp7 + S( 3, 5 ) * tmp8;
    double tmp21 = S( 3, 1 ) * tmp2 - S( 3, 3 ) * tmp7 + S( 3, 5 ) * tmp9;
    double tmp22 = S( 3, 1 ) * tmp3 - S( 3, 3 ) * tmp8 + S( 3, 4 ) * tmp9;
    double tmp23 = S( 3, 1 ) * tmp4 - S( 3, 2 ) * tmp7 + S( 3, 5 ) * tmp10;
    double tmp24 = S( 3, 1 ) * tmp5 - S( 3, 2 ) * tmp8 + S( 3, 4 ) * tmp10;
    double tmp25 = S( 3, 1 ) * tmp6 - S( 3, 2 ) * tmp9 + S( 3, 3 ) * tmp10;
    double tmp26 = S( 3, 0 ) * tmp1 - S( 3, 4 ) * tmp11 + S( 3, 5 ) * tmp12;
    double tmp27 = S( 3, 0 ) * tmp2 - S( 3, 3 ) * tmp11 + S( 3, 5 ) * tmp13;
    double tmp28 = S( 3, 0 ) * tmp3 - S( 3, 3 ) * tmp12 + S( 3, 4 ) * tmp13;
    double tmp29 = S( 3, 0 ) * tmp4 - S( 3, 2 ) * tmp11 + S( 3, 5 ) * tmp14;
    double tmp30 = S( 3, 0 ) * tmp5 - S( 3, 2 ) * tmp12 + S( 3, 4 ) * tmp14;
    double tmp31 = S( 3, 0 ) * tmp6 - S( 3, 2 ) * tmp13 + S( 3, 3 ) * tmp14;
    double tmp32 = S( 3, 0 ) * tmp7 - S( 3, 1 ) * tmp11 + S( 3, 5 ) * tmp15;
    double tmp33 = S( 3, 0 ) * tmp8 - S( 3, 1 ) * tmp12 + S( 3, 4 ) * tmp15;
    double tmp34 = S( 3, 0 ) * tmp9 - S( 3, 1 ) * tmp13 + S( 3, 3 ) * tmp15;
    double tmp35 = S( 3, 0 ) * tmp10 - S( 3, 1 ) * tmp14 + S( 3, 2 ) * tmp15;

    double tmp36 = S( 2, 2 ) * tmp16 - S( 2, 3 ) * tmp17 + S( 2, 4 ) * tmp18 - S( 2, 5 ) * tmp19;
    double tmp37 = S( 2, 1 ) * tmp16 - S( 2, 3 ) * tmp20 + S( 2, 4 ) * tmp21 - S( 2, 5 ) * tmp22;
    double tmp38 = S( 2, 1 ) * tmp17 - S( 2, 2 ) * tmp20 + S( 2, 4 ) * tmp23 - S( 2, 5 ) * tmp24;
    double tmp39 = S( 2, 1 ) * tmp18 - S( 2, 2 ) * tmp21 + S( 2, 3 ) * tmp23 - S( 2, 5 ) * tmp25;
    double tmp40 = S( 2, 1 ) * tmp19 - S( 2, 2 ) * tmp22 + S( 2, 3 ) * tmp24 - S( 2, 4 ) * tmp25;
    double tmp41 = S( 2, 0 ) * tmp16 - S( 2, 3 ) * tmp26 + S( 2, 4 ) * tmp27 - S( 2, 5 ) * tmp28;
    double tmp42 = S( 2, 0 ) * tmp17 - S( 2, 2 ) * tmp26 + S( 2, 4 ) * tmp29 - S( 2, 5 ) * tmp30;
    double tmp43 = S( 2, 0 ) * tmp18 - S( 2, 2 ) * tmp27 + S( 2, 3 ) * tmp29 - S( 2, 5 ) * tmp31;
    double tmp44 = S( 2, 0 ) * tmp19 - S( 2, 2 ) * tmp28 + S( 2, 3 ) * tmp30 - S( 2, 4 ) * tmp31;

    T( 0, 0 ) = S( 1, 1 ) * tmp36 - S( 1, 2 ) * tmp37 + S( 1, 3 ) * tmp38 - S( 1, 4 ) * tmp39 + S( 1, 5 ) * tmp40;
    T( 0, 1 ) = -S( 0, 1 ) * tmp36 + S( 0, 2 ) * tmp37 - S( 0, 3 ) * tmp38 + S( 0, 4 ) * tmp39 - S( 0, 5 ) * tmp40;
    T( 1, 0 ) = -S( 1, 0 ) * tmp36 + S( 1, 2 ) * tmp41 - S( 1, 3 ) * tmp42 + S( 1, 4 ) * tmp43 - S( 1, 5 ) * tmp44;
    T( 1, 1 ) = S( 0, 0 ) * tmp36 - S( 0, 2 ) * tmp41 + S( 0, 3 ) * tmp42 - S( 0, 4 ) * tmp43 + S( 0, 5 ) * tmp44;

    double tmp45 = S( 2, 0 ) * tmp20 - S( 2, 1 ) * tmp26 + S( 2, 4 ) * tmp32 - S( 2, 5 ) * tmp33;
    double tmp46 = S( 2, 0 ) * tmp21 - S( 2, 1 ) * tmp27 + S( 2, 3 ) * tmp32 - S( 2, 5 ) * tmp34;
    double tmp47 = S( 2, 0 ) * tmp22 - S( 2, 1 ) * tmp28 + S( 2, 3 ) * tmp33 - S( 2, 4 ) * tmp34;
    double tmp48 = S( 2, 0 ) * tmp23 - S( 2, 1 ) * tmp29 + S( 2, 2 ) * tmp32 - S( 2, 5 ) * tmp35;
    double tmp49 = S( 2, 0 ) * tmp24 - S( 2, 1 ) * tmp30 + S( 2, 2 ) * tmp33 - S( 2, 4 ) * tmp35;

    T( 2, 0 ) = S( 1, 0 ) * tmp37 - S( 1, 1 ) * tmp41 + S( 1, 3 ) * tmp45 - S( 1, 4 ) * tmp46 + S( 1, 5 ) * tmp47;
    T( 2, 1 ) = -S( 0, 0 ) * tmp37 + S( 0, 1 ) * tmp41 - S( 0, 3 ) * tmp45 + S( 0, 4 ) * tmp46 - S( 0, 5 ) * tmp47;
    T( 3, 0 ) = -S( 1, 0 ) * tmp38 + S( 1, 1 ) * tmp42 - S( 1, 2 ) * tmp45 + S( 1, 4 ) * tmp48 - S( 1, 5 ) * tmp49;
    T( 3, 1 ) = S( 0, 0 ) * tmp38 - S( 0, 1 ) * tmp42 + S( 0, 2 ) * tmp45 - S( 0, 4 ) * tmp48 + S( 0, 5 ) * tmp49;

    double tmp50 = S( 2, 0 ) * tmp25 - S( 2, 1 ) * tmp31 + S( 2, 2 ) * tmp34 - S( 2, 3 ) * tmp35;

    T( 4, 0 ) = S( 1, 0 ) * tmp39 - S( 1, 1 ) * tmp43 + S( 1, 2 ) * tmp46 - S( 1, 3 ) * tmp48 + S( 1, 5 ) * tmp50;
    T( 4, 1 ) = -S( 0, 0 ) * tmp39 + S( 0, 1 ) * tmp43 - S( 0, 2 ) * tmp46 + S( 0, 3 ) * tmp48 - S( 0, 5 ) * tmp50;
    T( 5, 0 ) = -S( 1, 0 ) * tmp40 + S( 1, 1 ) * tmp44 - S( 1, 2 ) * tmp47 + S( 1, 3 ) * tmp49 - S( 1, 4 ) * tmp50;
    T( 5, 1 ) = S( 0, 0 ) * tmp40 - S( 0, 1 ) * tmp44 + S( 0, 2 ) * tmp47 - S( 0, 3 ) * tmp49 + S( 0, 4 ) * tmp50;

    tmp36 = S( 1, 2 ) * tmp16 - S( 1, 3 ) * tmp17 + S( 1, 4 ) * tmp18 - S( 1, 5 ) * tmp19;
    tmp37 = S( 1, 1 ) * tmp16 - S( 1, 3 ) * tmp20 + S( 1, 4 ) * tmp21 - S( 1, 5 ) * tmp22;
    tmp38 = S( 1, 1 ) * tmp17 - S( 1, 2 ) * tmp20 + S( 1, 4 ) * tmp23 - S( 1, 5 ) * tmp24;
    tmp39 = S( 1, 1 ) * tmp18 - S( 1, 2 ) * tmp21 + S( 1, 3 ) * tmp23 - S( 1, 5 ) * tmp25;
    tmp40 = S( 1, 1 ) * tmp19 - S( 1, 2 ) * tmp22 + S( 1, 3 ) * tmp24 - S( 1, 4 ) * tmp25;
    tmp41 = S( 1, 0 ) * tmp16 - S( 1, 3 ) * tmp26 + S( 1, 4 ) * tmp27 - S( 1, 5 ) * tmp28;
    tmp42 = S( 1, 0 ) * tmp17 - S( 1, 2 ) * tmp26 + S( 1, 4 ) * tmp29 - S( 1, 5 ) * tmp30;
    tmp43 = S( 1, 0 ) * tmp18 - S( 1, 2 ) * tmp27 + S( 1, 3 ) * tmp29 - S( 1, 5 ) * tmp31;
    tmp44 = S( 1, 0 ) * tmp19 - S( 1, 2 ) * tmp28 + S( 1, 3 ) * tmp30 - S( 1, 4 ) * tmp31;
    tmp45 = S( 1, 0 ) * tmp20 - S( 1, 1 ) * tmp26 + S( 1, 4 ) * tmp32 - S( 1, 5 ) * tmp33;
    tmp46 = S( 1, 0 ) * tmp21 - S( 1, 1 ) * tmp27 + S( 1, 3 ) * tmp32 - S( 1, 5 ) * tmp34;
    tmp47 = S( 1, 0 ) * tmp22 - S( 1, 1 ) * tmp28 + S( 1, 3 ) * tmp33 - S( 1, 4 ) * tmp34;
    tmp48 = S( 1, 0 ) * tmp23 - S( 1, 1 ) * tmp29 + S( 1, 2 ) * tmp32 - S( 1, 5 ) * tmp35;
    tmp49 = S( 1, 0 ) * tmp24 - S( 1, 1 ) * tmp30 + S( 1, 2 ) * tmp33 - S( 1, 4 ) * tmp35;
    tmp50 = S( 1, 0 ) * tmp25 - S( 1, 1 ) * tmp31 + S( 1, 2 ) * tmp34 - S( 1, 3 ) * tmp35;

    T( 0, 2 ) = S( 0, 1 ) * tmp36 - S( 0, 2 ) * tmp37 + S( 0, 3 ) * tmp38 - S( 0, 4 ) * tmp39 + S( 0, 5 ) * tmp40;
    T( 1, 2 ) = -S( 0, 0 ) * tmp36 + S( 0, 2 ) * tmp41 - S( 0, 3 ) * tmp42 + S( 0, 4 ) * tmp43 - S( 0, 5 ) * tmp44;
    T( 2, 2 ) = S( 0, 0 ) * tmp37 - S( 0, 1 ) * tmp41 + S( 0, 3 ) * tmp45 - S( 0, 4 ) * tmp46 + S( 0, 5 ) * tmp47;
    T( 3, 2 ) = -S( 0, 0 ) * tmp38 + S( 0, 1 ) * tmp42 - S( 0, 2 ) * tmp45 + S( 0, 4 ) * tmp48 - S( 0, 5 ) * tmp49;
    T( 4, 2 ) = S( 0, 0 ) * tmp39 - S( 0, 1 ) * tmp43 + S( 0, 2 ) * tmp46 - S( 0, 3 ) * tmp48 + S( 0, 5 ) * tmp50;
    T( 5, 2 ) = -S( 0, 0 ) * tmp40 + S( 0, 1 ) * tmp44 - S( 0, 2 ) * tmp47 + S( 0, 3 ) * tmp49 - S( 0, 4 ) * tmp50;

    tmp1 = S( 0, 3 ) * S( 1, 4 ) - S( 0, 4 ) * S( 1, 3 );
    tmp2 = S( 0, 2 ) * S( 1, 4 ) - S( 0, 4 ) * S( 1, 2 );
    tmp3 = S( 0, 2 ) * S( 1, 3 ) - S( 0, 3 ) * S( 1, 2 );
    tmp4 = S( 0, 1 ) * S( 1, 4 ) - S( 0, 4 ) * S( 1, 1 );
    tmp5 = S( 0, 1 ) * S( 1, 3 ) - S( 0, 3 ) * S( 1, 1 );
    tmp6 = S( 0, 1 ) * S( 1, 2 ) - S( 0, 2 ) * S( 1, 1 );
    tmp7 = S( 0, 0 ) * S( 1, 4 ) - S( 0, 4 ) * S( 1, 0 );
    tmp8 = S( 0, 0 ) * S( 1, 3 ) - S( 0, 3 ) * S( 1, 0 );
    tmp9 = S( 0, 0 ) * S( 1, 2 ) - S( 0, 2 ) * S( 1, 0 );
    tmp10 = S( 0, 0 ) * S( 1, 1 ) - S( 0, 1 ) * S( 1, 0 );
    tmp11 = S( 0, 3 ) * S( 1, 5 ) - S( 0, 5 ) * S( 1, 3 );
    tmp12 = S( 0, 2 ) * S( 1, 5 ) - S( 0, 5 ) * S( 1, 2 );
    tmp13 = S( 0, 1 ) * S( 1, 5 ) - S( 0, 5 ) * S( 1, 1 );
    tmp14 = S( 0, 0 ) * S( 1, 5 ) - S( 0, 5 ) * S( 1, 0 );
    tmp15 = S( 0, 4 ) * S( 1, 5 ) - S( 0, 5 ) * S( 1, 4 );

    tmp16 = S( 2, 3 ) * tmp15 - S( 2, 4 ) * tmp11 + S( 2, 5 ) * tmp1;
    tmp17 = S( 2, 2 ) * tmp15 - S( 2, 4 ) * tmp12 + S( 2, 5 ) * tmp2;
    tmp18 = S( 2, 2 ) * tmp11 - S( 2, 3 ) * tmp12 + S( 2, 5 ) * tmp3;
    tmp19 = S( 2, 2 ) * tmp1 - S( 2, 3 ) * tmp2 + S( 2, 4 ) * tmp3;
    tmp20 = S( 2, 1 ) * tmp15 - S( 2, 4 ) * tmp13 + S( 2, 5 ) * tmp4;
    tmp21 = S( 2, 1 ) * tmp11 - S( 2, 3 ) * tmp13 + S( 2, 5 ) * tmp5;
    tmp22 = S( 2, 1 ) * tmp1 - S( 2, 3 ) * tmp4 + S( 2, 4 ) * tmp5;
    tmp23 = S( 2, 1 ) * tmp12 - S( 2, 2 ) * tmp13 + S( 2, 5 ) * tmp6;
    tmp24 = S( 2, 1 ) * tmp2 - S( 2, 2 ) * tmp4 + S( 2, 4 ) * tmp6;
    tmp25 = S( 2, 1 ) * tmp3 - S( 2, 2 ) * tmp5 + S( 2, 3 ) * tmp6;
    tmp26 = S( 2, 0 ) * tmp15 - S( 2, 4 ) * tmp14 + S( 2, 5 ) * tmp7;
    tmp27 = S( 2, 0 ) * tmp11 - S( 2, 3 ) * tmp14 + S( 2, 5 ) * tmp8;
    tmp28 = S( 2, 0 ) * tmp1 - S( 2, 3 ) * tmp7 + S( 2, 4 ) * tmp8;
    tmp29 = S( 2, 0 ) * tmp12 - S( 2, 2 ) * tmp14 + S( 2, 5 ) * tmp9;
    tmp30 = S( 2, 0 ) * tmp2 - S( 2, 2 ) * tmp7 + S( 2, 4 ) * tmp9;
    tmp31 = S( 2, 0 ) * tmp3 - S( 2, 2 ) * tmp8 + S( 2, 3 ) * tmp9;
    tmp32 = S( 2, 0 ) * tmp13 - S( 2, 1 ) * tmp14 + S( 2, 5 ) * tmp10;
    tmp33 = S( 2, 0 ) * tmp4 - S( 2, 1 ) * tmp7 + S( 2, 4 ) * tmp10;
    tmp34 = S( 2, 0 ) * tmp5 - S( 2, 1 ) * tmp8 + S( 2, 3 ) * tmp10;
    tmp35 = S( 2, 0 ) * tmp6 - S( 2, 1 ) * tmp9 + S( 2, 2 ) * tmp10;

    tmp36 = S( 3, 2 ) * tmp16 - S( 3, 3 ) * tmp17 + S( 3, 4 ) * tmp18 - S( 3, 5 ) * tmp19;
    tmp37 = S( 3, 1 ) * tmp16 - S( 3, 3 ) * tmp20 + S( 3, 4 ) * tmp21 - S( 3, 5 ) * tmp22;
    tmp38 = S( 3, 1 ) * tmp17 - S( 3, 2 ) * tmp20 + S( 3, 4 ) * tmp23 - S( 3, 5 ) * tmp24;
    tmp39 = S( 3, 1 ) * tmp18 - S( 3, 2 ) * tmp21 + S( 3, 3 ) * tmp23 - S( 3, 5 ) * tmp25;
    tmp40 = S( 3, 1 ) * tmp19 - S( 3, 2 ) * tmp22 + S( 3, 3 ) * tmp24 - S( 3, 4 ) * tmp25;
    tmp41 = S( 3, 0 ) * tmp16 - S( 3, 3 ) * tmp26 + S( 3, 4 ) * tmp27 - S( 3, 5 ) * tmp28;
    tmp42 = S( 3, 0 ) * tmp17 - S( 3, 2 ) * tmp26 + S( 3, 4 ) * tmp29 - S( 3, 5 ) * tmp30;
    tmp43 = S( 3, 0 ) * tmp18 - S( 3, 2 ) * tmp27 + S( 3, 3 ) * tmp29 - S( 3, 5 ) * tmp31;
    tmp44 = S( 3, 0 ) * tmp19 - S( 3, 2 ) * tmp28 + S( 3, 3 ) * tmp30 - S( 3, 4 ) * tmp31;

    T( 0, 4 ) = -S( 5, 1 ) * tmp36 + S( 5, 2 ) * tmp37 - S( 5, 3 ) * tmp38 + S( 5, 4 ) * tmp39 - S( 5, 5 ) * tmp40;
    T( 0, 5 ) = S( 4, 1 ) * tmp36 - S( 4, 2 ) * tmp37 + S( 4, 3 ) * tmp38 - S( 4, 4 ) * tmp39 + S( 4, 5 ) * tmp40;
    T( 1, 4 ) = S( 5, 0 ) * tmp36 - S( 5, 2 ) * tmp41 + S( 5, 3 ) * tmp42 - S( 5, 4 ) * tmp43 + S( 5, 5 ) * tmp44;
    T( 1, 5 ) = -S( 4, 0 ) * tmp36 + S( 4, 2 ) * tmp41 - S( 4, 3 ) * tmp42 + S( 4, 4 ) * tmp43 - S( 4, 5 ) * tmp44;

    tmp45 = S( 3, 0 ) * tmp20 - S( 3, 1 ) * tmp26 + S( 3, 4 ) * tmp32 - S( 3, 5 ) * tmp33;
    tmp46 = S( 3, 0 ) * tmp21 - S( 3, 1 ) * tmp27 + S( 3, 3 ) * tmp32 - S( 3, 5 ) * tmp34;
    tmp47 = S( 3, 0 ) * tmp22 - S( 3, 1 ) * tmp28 + S( 3, 3 ) * tmp33 - S( 3, 4 ) * tmp34;
    tmp48 = S( 3, 0 ) * tmp23 - S( 3, 1 ) * tmp29 + S( 3, 2 ) * tmp32 - S( 3, 5 ) * tmp35;
    tmp49 = S( 3, 0 ) * tmp24 - S( 3, 1 ) * tmp30 + S( 3, 2 ) * tmp33 - S( 3, 4 ) * tmp35;

    T( 2, 4 ) = -S( 5, 0 ) * tmp37 + S( 5, 1 ) * tmp41 - S( 5, 3 ) * tmp45 + S( 5, 4 ) * tmp46 - S( 5, 5 ) * tmp47;
    T( 2, 5 ) = S( 4, 0 ) * tmp37 - S( 4, 1 ) * tmp41 + S( 4, 3 ) * tmp45 - S( 4, 4 ) * tmp46 + S( 4, 5 ) * tmp47;
    T( 3, 4 ) = S( 5, 0 ) * tmp38 - S( 5, 1 ) * tmp42 + S( 5, 2 ) * tmp45 - S( 5, 4 ) * tmp48 + S( 5, 5 ) * tmp49;
    T( 3, 5 ) = -S( 4, 0 ) * tmp38 + S( 4, 1 ) * tmp42 - S( 4, 2 ) * tmp45 + S( 4, 4 ) * tmp48 - S( 4, 5 ) * tmp49;

    tmp50 = S( 3, 0 ) * tmp25 - S( 3, 1 ) * tmp31 + S( 3, 2 ) * tmp34 - S( 3, 3 ) * tmp35;

    T( 4, 4 ) = -S( 5, 0 ) * tmp39 + S( 5, 1 ) * tmp43 - S( 5, 2 ) * tmp46 + S( 5, 3 ) * tmp48 - S( 5, 5 ) * tmp50;
    T( 4, 5 ) = S( 4, 0 ) * tmp39 - S( 4, 1 ) * tmp43 + S( 4, 2 ) * tmp46 - S( 4, 3 ) * tmp48 + S( 4, 5 ) * tmp50;
    T( 5, 4 ) = S( 5, 0 ) * tmp40 - S( 5, 1 ) * tmp44 + S( 5, 2 ) * tmp47 - S( 5, 3 ) * tmp49 + S( 5, 4 ) * tmp50;
    T( 5, 5 ) = -S( 4, 0 ) * tmp40 + S( 4, 1 ) * tmp44 - S( 4, 2 ) * tmp47 + S( 4, 3 ) * tmp49 - S( 4, 4 ) * tmp50;

    tmp36 = S( 4, 2 ) * tmp16 - S( 4, 3 ) * tmp17 + S( 4, 4 ) * tmp18 - S( 4, 5 ) * tmp19;
    tmp37 = S( 4, 1 ) * tmp16 - S( 4, 3 ) * tmp20 + S( 4, 4 ) * tmp21 - S( 4, 5 ) * tmp22;
    tmp38 = S( 4, 1 ) * tmp17 - S( 4, 2 ) * tmp20 + S( 4, 4 ) * tmp23 - S( 4, 5 ) * tmp24;
    tmp39 = S( 4, 1 ) * tmp18 - S( 4, 2 ) * tmp21 + S( 4, 3 ) * tmp23 - S( 4, 5 ) * tmp25;
    tmp40 = S( 4, 1 ) * tmp19 - S( 4, 2 ) * tmp22 + S( 4, 3 ) * tmp24 - S( 4, 4 ) * tmp25;
    tmp41 = S( 4, 0 ) * tmp16 - S( 4, 3 ) * tmp26 + S( 4, 4 ) * tmp27 - S( 4, 5 ) * tmp28;
    tmp42 = S( 4, 0 ) * tmp17 - S( 4, 2 ) * tmp26 + S( 4, 4 ) * tmp29 - S( 4, 5 ) * tmp30;
    tmp43 = S( 4, 0 ) * tmp18 - S( 4, 2 ) * tmp27 + S( 4, 3 ) * tmp29 - S( 4, 5 ) * tmp31;
    tmp44 = S( 4, 0 ) * tmp19 - S( 4, 2 ) * tmp28 + S( 4, 3 ) * tmp30 - S( 4, 4 ) * tmp31;
    tmp45 = S( 4, 0 ) * tmp20 - S( 4, 1 ) * tmp26 + S( 4, 4 ) * tmp32 - S( 4, 5 ) * tmp33;
    tmp46 = S( 4, 0 ) * tmp21 - S( 4, 1 ) * tmp27 + S( 4, 3 ) * tmp32 - S( 4, 5 ) * tmp34;
    tmp47 = S( 4, 0 ) * tmp22 - S( 4, 1 ) * tmp28 + S( 4, 3 ) * tmp33 - S( 4, 4 ) * tmp34;
    tmp48 = S( 4, 0 ) * tmp23 - S( 4, 1 ) * tmp29 + S( 4, 2 ) * tmp32 - S( 4, 5 ) * tmp35;
    tmp49 = S( 4, 0 ) * tmp24 - S( 4, 1 ) * tmp30 + S( 4, 2 ) * tmp33 - S( 4, 4 ) * tmp35;
    tmp50 = S( 4, 0 ) * tmp25 - S( 4, 1 ) * tmp31 + S( 4, 2 ) * tmp34 - S( 4, 3 ) * tmp35;

    T( 0, 3 ) = S( 5, 1 ) * tmp36 - S( 5, 2 ) * tmp37 + S( 5, 3 ) * tmp38 - S( 5, 4 ) * tmp39 + S( 5, 5 ) * tmp40;
    T( 1, 3 ) = -S( 5, 0 ) * tmp36 + S( 5, 2 ) * tmp41 - S( 5, 3 ) * tmp42 + S( 5, 4 ) * tmp43 - S( 5, 5 ) * tmp44;
    T( 2, 3 ) = S( 5, 0 ) * tmp37 - S( 5, 1 ) * tmp41 + S( 5, 3 ) * tmp45 - S( 5, 4 ) * tmp46 + S( 5, 5 ) * tmp47;
    T( 3, 3 ) = -S( 5, 0 ) * tmp38 + S( 5, 1 ) * tmp42 - S( 5, 2 ) * tmp45 + S( 5, 4 ) * tmp48 - S( 5, 5 ) * tmp49;
    T( 4, 3 ) = S( 5, 0 ) * tmp39 - S( 5, 1 ) * tmp43 + S( 5, 2 ) * tmp46 - S( 5, 3 ) * tmp48 + S( 5, 5 ) * tmp50;
    T( 5, 3 ) = -S( 5, 0 ) * tmp40 + S( 5, 1 ) * tmp44 - S( 5, 2 ) * tmp47 + S( 5, 3 ) * tmp49 - S( 5, 4 ) * tmp50;

    return S( 0, 0 ) * T( 0, 0 ) + S( 0, 1 ) * T( 1, 0 ) + S( 0, 2 ) * T( 2, 0 ) +
        S( 0, 3 ) * T( 3, 0 ) + S( 0, 4 ) * T( 4, 0 ) + S( 0, 5 ) * T( 5, 0 );
}

void invert( std::span<double> source,
             std::span<size_t> p,
             std::span<double> target )
{
    auto size = p.size( );

    MLHP_CHECK( source.size( ) == size * size, "Inconsistent sizes." );
    MLHP_CHECK( target.size( ) == size * size, "Inconsistent sizes." );

    if( size == 0 )
    {
        return;
    }

    // Direct inverse computation for small matrices
    if( size <= 6 )
    {
        auto S = [=]( size_t i, size_t j ) -> double { return source[i * size + j]; };
        auto T = [=]( size_t i, size_t j ) -> double& { return target[i * size + j]; };

        double det = 0.0;

        if( size == 1 ) det = 1.0 / source[0];
        else if( size == 2 ) det = invertSmall2( S, T );
        else if( size == 3 ) det = invertSmallUnsymmetric3( S, T );
        else if( size == 4 ) det = invertSmallUnsymmetric4( S, T );
        else if( size == 5 ) det = invertSmallUnsymmetric5( S, T );
        else if( size == 6 ) det = invertSmallUnsymmetric6( S, T );

        //MLHP_CHECK( std::abs( det ) > 1e-12, "Matrix is singular." );

        double invDet = 1.0 / det;

        for( size_t i = 0; i < size * size; ++i )
        {
            target[i] *= invDet;
        }
    }
    else
    {
        MLHP_CHECK( linalg::luFactor( source, p ) != -1, "Matrix is singular." );

        linalg::luInvert( source, p, target );
    }
}

} // mlhp::linalg
