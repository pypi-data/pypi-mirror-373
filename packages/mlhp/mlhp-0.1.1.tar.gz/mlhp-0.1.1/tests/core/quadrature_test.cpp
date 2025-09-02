// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/quadrature.hpp"

#include "mlhp/core/spatial.hpp" /////////////////////////////////////////////// REMOVE
#include "mlhp/core/postprocessing.hpp" /////////////////////////////////////////////// REMOVE

namespace mlhp
{
namespace
{

auto makePolynomial( size_t order, std::array<double, 2> bounds )
{
    auto coefficients = std::vector<double> { };
    auto integral = 0.0;

    for( size_t i = 0; i < order + 1; ++i )
    {
        coefficients.push_back( std::sin( 0.85 * i ) + 2.21 );

        auto value0 = std::pow( bounds[0], i + 1);
        auto value1 = std::pow( bounds[1], i + 1);

        integral += coefficients[i] / ( i + 1.0 ) * ( value1 - value0 );
    }

    auto evaluate = [=]( double r )
    {
        double value = 0.0;

        for( size_t i = 0; i < order + 1; ++i )
        {
            value += coefficients[i] * std::pow( r, i );
        }

        return value;
    };

    return std::pair { evaluate, integral };
}

template<size_t D>
auto determineAccuracy( const CoordinateList<D>& rst,
                        const std::vector<double>& weights,
                        std::array<double, 2> bounds )
{
    auto accuracy = std::array<size_t, D> { };

    for( size_t axis = 0; axis < D; ++axis )
    {
        bool equal = true;

        while( equal )
        {
            auto [evaluate, expected] = makePolynomial( accuracy[axis], bounds );
            auto computed = 0.0;
            
            for( size_t i = 0; i < rst.size( ); ++i )
            {
                computed += evaluate( rst[i][axis] ) * weights[i];
            }

            expected *= utilities::integerPow( bounds[1] - bounds[0], D - 1 );
            equal = std::abs( computed - expected ) < 1e-12;
            accuracy[axis] += equal ? size_t { 1 } : size_t { 0 };
        }

        REQUIRE( accuracy[axis] > 0 );

        accuracy[axis] -= 1;
    }

    return accuracy;
}

} // namespace

TEST_CASE( "computeGaussLegendrePoints_test" )
{
    std::vector<double> coordinates[] =
    {
        { },                                                                                    // dummy
        {  0.0 },                                                                               // order 1
        { -0.5773502691896257, 0.5773502691896257 },                                            // order 2
        { -0.7745966692414834, 0.0000000000000000, 0.7745966692414834 },                        // order 3
        { -0.8611363115940526, -0.3399810435848563, 0.3399810435848563, 0.8611363115940526 },   // order 4
        { -0.9061798459386640, -0.5384693101056831, 0.0000000000000000, 0.5384693101056831,     // order 5
           0.9061798459386640 },
        { -0.932469514203152, -0.6612093864662645, -0.23861918608319693, 0.23861918608319693,   // order 6
           0.6612093864662645, 0.932469514203152 },
        { -0.9491079123427585, -0.7415311855993945, -0.4058451513773972, 0.0,                   // order 7
           0.4058451513773972,  0.7415311855993945, 0.9491079123427585 },
        { -0.9602898564975362 , -0.7966664774136267 , -0.525532409916329, -0.18343464249564978, // order 8 
           0.18343464249564978,  0.525532409916329, 0.7966664774136267, 0.9602898564975362 },   
        { -0.9681602395076261, -0.8360311073266358, -0.6133714327005904, -0.3242534234038089,   // order 9
           0.0, 0.3242534234038089, 0.6133714327005904, 0.8360311073266358, 
           0.9681602395076261 },
        { -0.9739065285171717, -0.8650633666889845, -0.6794095682990244, -0.4333953941292472,   // order 10
          -0.14887433898163122, 0.14887433898163122, 0.4333953941292472,  0.6794095682990244,  
           0.8650633666889845, 0.9739065285171717 },
        { -0.978228658146057, -0.8870625997680953, -0.7301520055740494, -0.5190961292068118,    // order 11
          -0.26954315595234496,  0.0, 0.26954315595234496, 0.5190961292068118,
           0.7301520055740494, 0.8870625997680953, 0.978228658146057 },
        { -0.9815606342467192, -0.9041172563704748, -0.7699026741943047, -0.5873179542866175,   // order 12
          -0.3678314989981802, -0.1252334085114689, 0.1252334085114689, 0.3678314989981802, 
           0.5873179542866175, 0.7699026741943047, 0.9041172563704748, 0.9815606342467192 }
    };

    std::vector<double> weights[] =
    {
        { },                                                                                    // dummy
        { 2.0 },                                                                                // order 1
        { 1.0000000000000000, 1.0000000000000000 },                                             // order 2
        { 0.5555555555555556, 0.8888888888888888, 0.5555555555555556 },                         // order 3
        { 0.3478548451374538, 0.6521451548625461, 0.6521451548625461, 0.3478548451374538 },     // order 4
        { 0.2369268850561891, 0.4786286704993665, 0.5688888888888889, 0.4786286704993665,       // order 5
          0.2369268850561891 },
        { 0.17132449237916975, 0.36076157304813894, 0.46791393457269137, 0.46791393457269137,   // order 6
          0.36076157304813894, 0.17132449237916975 },
        { 0.12948496616887065, 0.2797053914892766 , 0.3818300505051183, 0.41795918367346896,    // order 7
          0.3818300505051183 , 0.2797053914892766, 0.12948496616887065 },
        { 0.10122853629037669,  0.22238103445337434,  0.31370664587788705, 0.36268378337836177, // order 8
          0.36268378337836177,  0.31370664587788705, 0.22238103445337434, 0.10122853629037669 },
        { 0.08127438836157472, 0.18064816069485712, 0.26061069640293566, 0.3123470770400028,    // order 9
          0.33023935500125967, 0.3123470770400028, 0.26061069640293566, 0.18064816069485712, 
          0.08127438836157472 },
        { 0.06667134430868807, 0.14945134915058036, 0.219086362515982, 0.2692667193099965,      // order 10
          0.295524224714753, 0.295524224714753, 0.2692667193099965, 0.219086362515982,
          0.14945134915058036,  0.06667134430868807 },
        { 0.055668567116173164, 0.1255803694649047, 0.18629021092773443, 0.23319376459199068,   // order 11
          0.26280454451024676, 0.2729250867779009, 0.26280454451024676, 0.23319376459199068, 
          0.18629021092773443, 0.1255803694649047, 0.055668567116173164 },
        { 0.04717533638651202, 0.10693932599531888, 0.1600783285433461, 0.20316742672306565,    // order 12
          0.23349253653835464, 0.2491470458134027, 0.2491470458134027, 0.23349253653835464, 
          0.20316742672306565, 0.1600783285433461 , 0.10693932599531888, 0.04717533638651202 }
    };
    
    double tolerance = 1e-13;

    std::array<std::vector<double>, 2> points;

    size_t orders[] = { 0, 10, 1, 5, 2, 12, 3, 0, 4, 8, 6, 7, 9, 11 };

    for( size_t order : orders )
    {
        REQUIRE_NOTHROW( points = gaussLegendrePoints( order ) );
            
        size_t size = coordinates[order].size( );

        REQUIRE( points[0].size() == size );
        REQUIRE( points[1].size() == size );

        for( size_t i = 0; i < size; ++i )
        {
            if( std::abs( coordinates[order][i] ) > tolerance )
            { 
                CHECK( points[0][i] == Approx( coordinates[order][i] ).epsilon( tolerance ) );
            }
            else
            {
                CHECK( points[0][i] == Approx( coordinates[order][i] ).margin( tolerance ) );
            }

            CHECK( points[1][i] == Approx( weights[order][i] ).epsilon( tolerance ) );

        } // for i
    } // for each order

} // computeGaussLegendrePoints_test

TEST_CASE( "triangleQuadrature_test" )
{
    for( size_t order = 1; order <= 8; ++order )
    {
        auto rst = CoordinateList<2> { };
        auto weights = std::vector<double> { };
        auto cache = QuadraturePointCache { };

        simplexQuadrature<2>( { order, order }, rst, weights, cache );
        
        REQUIRE( rst.size( ) == order * order );
        REQUIRE( weights.size( ) == order * order );
        
        // Copy rotated triangle to form square domain
        for( size_t i = 0; i < order * order; ++i )
        {
            rst.push_back( { 1.0 - rst[i][0], 1.0 - rst[i][1] } );
            weights.push_back( weights[i] );
        }
            
        // writePoints( rst, "triangle_quadrature_" + std::to_string( order ) + ".vtu", weights );

        auto accuracy = determineAccuracy( rst, weights, { 0.0, 1.0 } );

        CHECK( accuracy[0] == 2 * order - 1 );
        CHECK( accuracy[1] == 2 * order - 1 );
    }

} // triangleQuadrature_test

TEST_CASE( "tensorProductQuadrature_test" )
{
    for( size_t order = 1; order <= 8; ++order )
    {
        auto weights = std::vector<double> { };
        auto cache = QuadraturePointCache { };
        auto grid = CoordinateGrid<2>{ };

        tensorProductQuadrature( std::array{ order, order }, grid, weights, cache );

        auto rst = spatial::tensorProduct( grid );
            
        REQUIRE( rst.size( ) == order * order );
        REQUIRE( weights.size( ) == order * order );
        
        auto path = testing::outputPath( "core/tensorproduct_quadrature_" + std::to_string( order ) + ".vtu" );

        writeVtu<2>( rst, path, weights );

        auto accuracy = determineAccuracy( rst, weights, { -1.0, 1.0 } );

        CHECK( accuracy[0] == 2 * order - 1 );
        CHECK( accuracy[1] == 2 * order - 1 );
    }

} // tensorProductQuadrature_test

TEST_CASE( "gaussLobatto_test" )
{
    std::vector<double> coordinates[] =
    {
        { -1.0, 1.0 },                                                                    // n = 2
        { -1.0, 0.0, 1.0 },                                                               // n = 3
        { -1.0, -1.0 / std::sqrt( 5.0 ), 1.0 / std::sqrt( 5.0 ), 1.0 },                   // n = 4
        { -1.0, -std::sqrt( 3.0 / 7.0 ), 0.0, std::sqrt( 3.0 / 7.0 ), 1.0 },              // n = 5
        { -1.0, -std::sqrt( ( 7 - 2 * std::sqrt( 7 ) ) / 21 ), -std::sqrt( ( 7 + 2 *      // n = 6
           std::sqrt( 7 ) ) / 21 ), std::sqrt( ( 7 + 2 * std::sqrt( 7 ) ) / 21 ),
           std::sqrt( ( 7 - 2 * std::sqrt( 7 ) ) / 21 ), 1.0 }
    };

    std::vector<double> weights[] =                                                       
    {                                                                                     
        { 1.0, 1.0 },                                                                     // n = 2
        { 1.0 / 3.0, 4.0 / 3.0, 1.0 / 3.0 },                                              // n = 3
        { 1.0 / 6.0, 5.0 / 6.0, 5.0 / 6.0, 1.0 / 6.0 },                                   // n = 4
        { 1.0 / 10.0, 49.0 / 90.0, 32.0 / 45.0, 49.0 / 90.0, 1.0 / 10.0 },                // n = 5
        { 1.0 / 15.0, ( 14.0 - std::sqrt( 7 ) ) / 30.0, ( 14.0 + std::sqrt( 7 ) ) / 30.0, // n = 6
          ( 14.0 + std::sqrt( 7 ) ) / 30.0,( 14.0 - std::sqrt( 7 ) ) / 30.0, 1.0 / 15.0 }
    };

    std::array<std::vector<double>, 2> points;

    for( size_t n = 2; n <= 5; ++n )
    {
        REQUIRE_NOTHROW( points = gaussLobattoPoints( n ) );
            
        REQUIRE( points[0].size() == n );
        REQUIRE( points[1].size() == n );

        auto tolerance = 1e-13;

        for( size_t i = 0; i < n; ++i )
        {
            if( std::abs( coordinates[n - 2][i] ) > tolerance )
            { 
                CHECK( points[0][i] == Approx( coordinates[n - 2][i] ).epsilon( tolerance ) );
            }
            else
            {
                CHECK( points[0][i] == Approx( coordinates[n - 2][i] ).margin( tolerance ) );
            }

            CHECK( points[1][i] == Approx( weights[n - 2][i] ).epsilon( tolerance ) );

        } // for i
    } // for each n
} // gaussLobatto_test


} // namespace mlhp
