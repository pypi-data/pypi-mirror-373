// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_TEST_HPP
#define MLHP_CORE_TEST_HPP

#include "external/catch2/catch.hpp"

#include <filesystem>
#include <fstream>

namespace mlhp
{
namespace testing
{

inline auto testfilePath( )
{
    for( auto parentDir : { ".", ".." } )
    {
        auto path = std::filesystem::path { parentDir } / "testfiles";
        
        if( std::filesystem::exists( path ) )
        {
            return std::filesystem::absolute( path );
        }
    }
    
    FAIL( "No \"testfiles\" folder found in working directory and its parent." );

    return std::filesystem::path { };
}

inline auto testfilePath( const std::string& relativePath )
{
    return ( testfilePath( ) / relativePath ).string( );
}

inline auto outputPath( )
{
    std::filesystem::path path( "outputs" );
        
    std::filesystem::create_directories( path );
   
    return path;
}

inline auto outputPath( const std::string& relativePath )
{
    auto path = outputPath( ) / relativePath;
    auto pathstring = path.string( );

    std::filesystem::create_directories( path.remove_filename( ) );

    return pathstring;
}

template<typename T> struct ReadDataTargetType { using type = T; };
template<> struct ReadDataTargetType<bool> { using type = char; };
template<> struct ReadDataTargetType<std::uint8_t> { using type = int; };

template<typename T>
inline auto readData( std::string relativePath, size_t expectedSize = std::numeric_limits<size_t>::max( ) )
{
    auto fullPath = testfilePath( relativePath );
    
    REQUIRE( std::filesystem::exists( fullPath ) );

    std::ifstream file( fullPath );
    std::vector<T> result;

    REQUIRE( file.is_open( ) );

    typename ReadDataTargetType<T>::type value;

    while( file >> value )
    {
        if constexpr( std::is_same_v<T, bool> )
        {
            result.push_back( value != '0' );
        }
        else if constexpr( std::is_same_v<T, std::uint8_t> )
        {
            result.push_back( static_cast<std::uint8_t>( value ) );
        }
        else
        {
            result.push_back( value );
        }
    }

    file.close( );

    if( expectedSize != std::numeric_limits<size_t>::max( ) )
    {
        CHECK( result.size( ) == expectedSize );
    }

    return result;
}

} // testing
} // mlhp

#endif // MLHP_CORE_TEST_HPP
