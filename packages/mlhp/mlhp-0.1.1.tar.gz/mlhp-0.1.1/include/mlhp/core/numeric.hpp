// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_NUMERIC_HPP
#define MLHP_CORE_NUMERIC_HPP

#include "mlhp/core/alias.hpp"
#include "mlhp/core/coreexport.hpp"

#include <vector>
#include <functional>

namespace mlhp
{

using JacobianAndResidualFunction = std::function<void( const std::vector<double>& x,
                                                        linalg::UnsymmetricSparseMatrix& df,
                                                        std::vector<double>& f,
                                                        const DofIndicesValuesPair& )>;

MLHP_EXPORT
std::vector<double> newtonRaphson( const JacobianAndResidualFunction& evaluate,
                                   const LocationMapRange& locationMaps,
                                   const DofIndicesValuesPair& boundaryDofs,
                                   const linalg::SparseSolver& linearSolve,
                                   size_t maximumNumberOfIterations = 20,
                                   double tolerance = 1e-8 );

//class DoubleNewtonRaphson
//{
//public:
//    using Evaluate = std::function<void( double x, double& f, double& df )>;
//
//    DoubleNewtonRaphson( size_t maxNumberOfIterations, double tolerance ) :
//        maxit_( maxNumberOfIterations ), tolerance_( tolerance )
//    { }
//
//    double solve( const Evaluate& evaluate,
//                  double initial = 0.0 )
//    {
//        auto x = initial;
//        auto f = initial;
//
//        double df = 0.0;
//
//        for( size_t i = 0; i < maxit_; ++i )
//        {
//            std::cout << "iteration " << i << " with value " << x << std::endl;
//
//            evaluate( x, f, df );
//
//            x -= f /  df;
//
//            if( std::abs( f ) <= tolerance_ )
//            {
//                return x;
//            }
//        }
//
//        throw std::runtime_error( "Newton-Raphson iterations did not converge!" );
//    }
//
//private:
//    size_t maxit_;
//    double tolerance_;
//
//};

// returns (argmin, min f)
MLHP_EXPORT
std::tuple<double, double> lineSearch( const RealFunction& f,
                                       size_t nsteps );

MLHP_EXPORT
std::tuple<double, double> lineSearch( const RealFunction& f,
                                       size_t nsteps,
                                       double norm0 );    

} // mlhp

#endif // MLHP_CORE_NUMERIC_HPP
