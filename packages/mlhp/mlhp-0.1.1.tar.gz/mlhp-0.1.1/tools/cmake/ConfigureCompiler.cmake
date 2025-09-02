include(CheckCXXCompilerFlag)

add_library( mlhp_public_compile_flags INTERFACE )
add_library( mlhp_private_compile_flags INTERFACE )

target_compile_features( mlhp_public_compile_flags INTERFACE cxx_std_20 )

add_library( mlhp_optimization_flags INTERFACE )

if( CMAKE_CXX_COMPILER_ID STREQUAL "GNU" )

    # Hidden visibility
    target_compile_options( mlhp_private_compile_flags INTERFACE -fvisibility=hidden )

    # Compiler warnings
    target_compile_options( mlhp_private_compile_flags INTERFACE -fPIC -pedantic -Wall -Wextra -Wcast-align
        -Wsuggest-attribute=pure -Wimport -Wsuggest-final-methods -Wsuggest-attribute=format 
        -Wsuggest-attribute=malloc -Wformat-y2k -Wpacked  
        -Wswitch-enum -Wwrite-strings -Wformat-nonliteral -Wformat-security -Wcast-qual -Wsuggest-override 
        -Wsuggest-final-types -Wdisabled-optimization -Wformat=2 -Winit-self -Wlogical-op -Wmissing-include-dirs 
        -Wnoexcept -Wold-style-cast -Woverloaded-virtual -Wredundant-decls -Wshadow -Wsign-conversion -Wsign-promo 
        -Wstrict-null-sentinel -Wundef )

    if( CMAKE_CXX_COMPILER_VERSION LESS 14 )
        target_compile_options( mlhp_private_compile_flags INTERFACE -Wno-missing-field-initializers )
    endif( CMAKE_CXX_COMPILER_VERSION LESS 14 )
   
    target_compile_options( mlhp_private_compile_flags INTERFACE -Wno-attributes -Wno-restrict -Wno-unknown-pragmas )
 
    # Mostly from: https://stackoverflow.com/questions/5088460/flags-to-enable-thorough-and-verbose-g-warnings
    # Removed: -Wsuggest-attribute=noreturn -Wpadded  -Wsuggest-attribute=cold -Wswitch-default 

    target_compile_options( mlhp_optimization_flags INTERFACE -Ofast -march=native )
    
    set( MLHP_AVX512_FLAG -mprefer-vector-width=512 )

elseif( CMAKE_CXX_COMPILER_ID MATCHES "Clang" )

    # Hidden visibility
    target_compile_options( mlhp_private_compile_flags INTERFACE -fvisibility=hidden -fPIC )
    
    # Warnings / errors (enable later: -Wconversion -Wfloat-equal)
    target_compile_options( mlhp_private_compile_flags INTERFACE -Wall -Wextra -Wpedantic -Wshadow -Wunreachable-code 
        -Wuninitialized -Wold-style-cast -Wno-missing-braces -Wno-instantiation-after-specialization )

    # Same optimization flags as gcc
    target_compile_options( mlhp_optimization_flags INTERFACE -O3 -ffast-math -march=native )
    
    set( MLHP_AVX512_FLAG -mprefer-vector-width=512 )

elseif( CMAKE_CXX_COMPILER_ID STREQUAL "MSVC" )

    # Remove inconsistent dll interface warning
    target_compile_options( mlhp_public_compile_flags INTERFACE /wd4251 )

    # Warning levels
    target_compile_options( mlhp_private_compile_flags INTERFACE /W3 )

    # Optimizations 
    # These make it worse: /Gy /Ob2 /Oi /Ot /Oy /GL /GS-
    target_compile_options( mlhp_optimization_flags INTERFACE  /fp:fast /fp:except- )
    
    set( MLHP_AVX512_FLAG /arch:AVX2 )

    ## For when clang is used with msvc
    #target_compile_options( mlhp_private_compile_flags INTERFACE -Wno-missing-braces -Wno-instantiation-after-specialization )

else()
    message(WARNING "Unknown compiler")
    
endif( CMAKE_CXX_COMPILER_ID STREQUAL "GNU" )

if( ${MLHP_ALL_OPTIMIZATIONS} )

    message( STATUS "Enabling optimizations for native architecture." )

    if( DEFINED MLHP_AVX512_FLAG )
        CHECK_CXX_COMPILER_FLAG( ${MLHP_AVX512_FLAG} MLHP_COMPILER_SUPPORTS_AXV512_OPTION )

        if( ${MLHP_COMPILER_SUPPORTS_AXV512_OPTION} )
            target_compile_options( mlhp_optimization_flags INTERFACE ${MLHP_AVX512_FLAG} )
        endif( ${MLHP_COMPILER_SUPPORTS_AXV512_OPTION} )
    endif( DEFINED MLHP_AVX512_FLAG )
    
    target_link_libraries( mlhp_public_compile_flags INTERFACE mlhp_optimization_flags )
    
endif( ${MLHP_ALL_OPTIMIZATIONS} )

# Enable omp if option is ON
if( ${MLHP_MULTITHREADING} STREQUAL "OMP" )
    find_package(OpenMP COMPONENTS CXX)

    if( OPENMP_FOUND )
        message( STATUS "Enabling OpenMP multi-threading." )
        set( MLHP_MULTITHREADING_OMP ON )
        target_link_libraries( mlhp_public_compile_flags INTERFACE OpenMP::OpenMP_CXX )
    else( OPENMP_FOUND )
        message( STATUS "Did not find OpenMP - disabling multi-threading." )
        set( MLHP_MULTITHREADING OFF CACHE STRING "Select multi-threading implementation." FORCE )
    endif( OPENMP_FOUND )
    
endif( ${MLHP_MULTITHREADING} STREQUAL "OMP" )
