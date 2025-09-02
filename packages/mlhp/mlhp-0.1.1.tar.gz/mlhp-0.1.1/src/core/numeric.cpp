// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/numeric.hpp"
#include "mlhp/core/sparse.hpp"
#include "mlhp/core/assembly.hpp"
#include "mlhp/core/boundary.hpp"

#include <iostream>

namespace mlhp
{

std::vector<double> newtonRaphson( const JacobianAndResidualFunction& evaluate,
                                   const LocationMapRange& locationMaps,
                                   const DofIndicesValuesPair& boundaryDofs,
                                   const linalg::SparseSolver& linearSolve,
                                   size_t maximumNumberOfIterations,
                                   double tolerance )
{
    auto df = allocateMatrix<linalg::UnsymmetricSparseMatrix>( locationMaps, boundaryDofs.first );

    size_t size = df.size1( );

    std::vector<double> x( size, 0.0 );
    std::vector<double> f( size, 0.0 );
    std::vector<double> dx( size, 0.0 );

    auto zeroBoundaryDofs = boundaryDofs;

    std::fill( zeroBoundaryDofs.second.begin( ), zeroBoundaryDofs.second.end( ), 0.0 );

    for( size_t i = 0; i < maximumNumberOfIterations; ++i )
    {
        std::fill( f.begin( ), f.end( ), 0.0 );
        std::fill( df.data( ), df.data( ) + df.nnz( ), 0.0 );

        evaluate( boundary::inflate( x, boundaryDofs ), df, f, zeroBoundaryDofs );

        double residualNorm = std::sqrt( std::inner_product( f.begin( ), f.end( ), f.begin( ), 0.0 ) );

        std::cout << "iteration " << i << ": | F | = " << residualNorm << std::endl;

        dx = linearSolve( df, f );

        std::transform( x.begin( ), x.end( ), dx.begin( ), x.begin( ), std::minus<double>( ) );

        if( residualNorm <= tolerance )
        {
            return boundary::inflate( x, boundaryDofs );
        }
    }

    std::cout << "Newton-Raphson iterations did not converge!" << std::endl;

    return boundary::inflate( x, boundaryDofs );

//    throw std::runtime_error( "Newton-Raphson iterations did not converge!" );
}

std::tuple<double, double> lineSearch( const RealFunction& f,
                                       size_t nsteps, 
                                       double norm0 )
{
    // Where to choose points in the middle
    double alpha = 0.5;

    // Initialize scaling factors and function evaluations
    double beta[3] = { 0.0, 0.0, 1.0 };
    double eval[3] = { norm0, 0.0, f( 1.0 ) };

    // If minimum is > 1.0 return 1.0
    if( eval[2] < eval[0] && f( 1.0 + 0.001 ) <= eval[2] )
    {
        return { 1.0, eval[2] };
    }

    for( size_t i = 0; i + 3 < nsteps; ++i )
    {
        // Determine new middle point and evaluate function
        beta[1] = ( 1.0 - alpha ) * beta[0] + alpha * beta[2];
        eval[1] = f( beta[1] );
       
        size_t interval = std::min( eval[0], eval[1] ) < std::min( eval[1], eval[2] ) ? 0 : 1;

        // Expand interval with smaller two values to [0, 2] 
        beta[0] = beta[interval];
        beta[2] = beta[interval + 1];
        eval[0] = eval[interval];
        eval[2] = eval[interval + 1];
    }

    // Minimum is either at 0 or 2
    return eval[0] < eval[2] ? std::tuple { beta[0], eval[0] } : std::tuple { beta[2], eval[2] };
}

std::tuple<double, double> lineSearch( const RealFunction& f,
                                       size_t nsteps )
{
    MLHP_CHECK( nsteps > 1, "" );

    return lineSearch( f, nsteps - 1, f( 0.0 ) );
}

} // mlhp

