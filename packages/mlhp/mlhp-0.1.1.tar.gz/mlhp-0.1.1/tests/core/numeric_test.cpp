// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/numeric.hpp"

namespace mlhp
{

//TEST_CASE( "NewtonRaphson_test" )
//{
//    DoubleNewtonRaphson solve( 10, 1e-12 );
//
//    auto evaluate = [=]( const double& x, double& f, double& df )
//    {
//        f = ( x - 3.0 ) * ( x - 3.0 ) - 1.0;
//        df = 2.0 * ( x - 3.0 );
//    };
//
//    double result = solve.solve( evaluate, 0.0 );
//
//    std::cout << "result = " << result << std::endl;
//}

//TEST_CASE( "VectorRaphson_test" )
//{
//    VectorNewtonRaphson solve( 10, 1e-12 );
//
//    auto evaluate = [=]( const std::vector<double>& x, std::vector<double>& f, CompressedSparseRowMatrix& df )
//    {
//        f = ( x - 3.0 ) * ( x - 3.0 ) - 1.0;
//        df = 2.0 * ( x - 3.0 );
//    };
//
//    double result = solve.solve( evaluate, 0.0 );
//
//    std::cout << "result = " << result << std::endl;
//}

} // namespace mlhp
