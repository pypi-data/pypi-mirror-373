// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_DERIVATIVE_HELPER_HPP
#define MLHP_CORE_DERIVATIVE_HELPER_HPP

#include <array>
#include <cstddef>

namespace mlhp
{
namespace diff
{

// Array of arrays indicating which directions are differentiated.
// E.g. for derivativeIndices<3, 1>( ) we get
//
//     { { 1, 0, 0 },
//       { 0, 1, 0 },
//       { 0, 0, 1 } }
// 
// More examples in the test (basis_test.cpp)


// Returns number of index tuples for one diff order
template<size_t D, size_t diffOrder>
consteval size_t ncomponents( );

template<size_t D>
consteval std::array<size_t, 3> ncomponents( );

// Returns array of index tuples as described above
template<size_t D, size_t diffOrder>
consteval auto indices( );

// Returns total number of index tuples up to given diff order
template<size_t D, size_t diffOrder>
consteval size_t allNComponents( );

// Concatenates all index tuples up to given diff order
template<size_t D, size_t MaxDiff>
consteval auto allIndices( );

} // diff
} // mlhp

#include "mlhp/core/derivativeHelper_impl.hpp"

#endif // MLHP_CORE_DERIVATIVE_HELPER_HPP
