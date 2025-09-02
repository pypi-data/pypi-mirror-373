// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/utilities.hpp"

#include <iomanip>
#include <sstream>

namespace mlhp::utilities
{

std::string roundNumberString( double result )
{
    std::ostringstream stream;

    std::fixed( stream );

    stream << std::setprecision( 1 + int { result < 10.0 } ) << result;

    return stream.str( );
}

std::string thousandSeparator( std::uint64_t integer )
{
    auto str = std::string { std::to_string( integer % 1000 ) };

    integer /= 1000;

    while( integer != 0 )
    {
        str = std::to_string( integer ) + "," + std::string( 
            3 - (  str.size( ) % 4 ), '0' ) + str;

        integer /= 1000;
    }

    return str;
}

std::string memoryUsageString( size_t bytes )
{
    constexpr std::array<const char*, 5> units = { "bytes", "kB", "MB", "GB", "TB" };
    double result = static_cast<double>( bytes );

    size_t i = 0;
    while( result >= 1000.0 && i++ < 4 )
    {
        result /= 1000;
    }

    return roundNumberString( result ) + " " + units[i];
}

} // namespace mlhp::utilities

MLHP_EXPORT bool MLHP_DISABLE_EXCEPTION_LOGS = false;


