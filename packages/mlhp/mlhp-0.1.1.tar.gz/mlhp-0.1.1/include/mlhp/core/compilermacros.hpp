// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_COMPILERMACROS_HPP
#define MLHP_CORE_COMPILERMACROS_HPP

#include "mlhp/core/config.hpp"

#include <memory>

// Check if we are actually using g++, and not other compiles defining __gnuc__
#if defined(__GNUC__) && !defined(__llvm__) && !defined(__INTEL_COMPILER)

    //! Tells compiler to ignore possible aliasing
    #define MLHP_RESTRICT __restrict__
    
    #ifndef MLHP_DISABLE_PURE
        #define MLHP_PURE __attribute__((pure))
    #else
        #define MLHP_PURE
    #endif
    
    #define MLHP_MALLOC __attribute__((malloc))

// Visual studio compiler
#elif defined( _MSC_VER ) 

    #define MLHP_PURE 
    #define MLHP_MALLOC
    #define MLHP_RESTRICT __restrict
    
    // Prevents compilation problems with std::min and std::max
    #define NOMINMAX
    
    // // For other compilers:
    // #elif defined( __INTEL_COMPILER ) //  Intel icc / icpc compiler

// clang compiler
#elif defined( __clang__ ) 

    #define MLHP_PURE 
    #define MLHP_MALLOC
    
    #define MLHP_RESTRICT __restrict__ 
    
// Something else
#else

#define MLHP_PURE
#define MLHP_MALLOC
#define MLHP_RESTRICT

#endif

#endif // MLHP_CORE_COMPILERMACROS_HPP
