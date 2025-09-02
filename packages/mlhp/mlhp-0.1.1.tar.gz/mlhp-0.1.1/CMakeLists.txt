# This file is part of the mlhp project. License: See LICENSE

cmake_minimum_required( VERSION 3.12 )

project( mlhp LANGUAGES CXX )

# Find out if mlhp is the root CMake project or not
get_directory_property( hasParent PARENT_DIRECTORY)
string( COMPARE EQUAL "${hasParent}" "" MLHP_IS_ROOT )

# ------------------- set project variables -----------------------

option( BUILD_SHARED_LIBS "Build shared library" ON )
option( MLHP_DEBUG_CHECKS "Enable debug checks with (hopefully) minor performance penalty." ON )
option( MLHP_ALL_OPTIMIZATIONS "Compile with all optimizations, including platform specific ones" ON )

option( MLHP_PYTHON "Enable pybind11 based python interface" ${MLHP_IS_ROOT} )
option( MLHP_TEST_PYTHON "Enable C++ unit and system tests." ${MLHP_IS_ROOT} )
option( MLHP_TEST_CPP "Enable C++ unit and system tests." ${MLHP_IS_ROOT} )
option( MLHP_EXAMPLES "Enable example drivers." OFF )

set( MLHP_MULTITHREADING OMP CACHE STRING "Select multi-threading implementation." )
set_property( CACHE MLHP_MULTITHREADING PROPERTY STRINGS OMP OFF )

set( MLHP_DIMENSIONS 3 CACHE STRING "Highest dimension to instantiate." )

set( MLHP_BUILD_ARCHIVE_DIR ${CMAKE_BINARY_DIR}/lib CACHE PATH "Build directory for static libs." )
set( MLHP_BUILD_LIBRARY_DIR ${CMAKE_BINARY_DIR}/lib CACHE PATH "Build directory for dynamic libs." )
set( MLHP_BUILD_BINARY_DIR ${CMAKE_BINARY_DIR}/bin CACHE PATH "Build directory for binaries." )

set( MLHP_SIMD_ALIGNMENT 32 CACHE STRING "Simd over-alignment 32 or 64, depending on cache line size of the CPU." )
set( MLHP_INDEX_SIZE_CELLS 32 CACHE STRING "Unsigned integer size used to index mesh cells." )
set( MLHP_INDEX_SIZE_DOFS 64 CACHE STRING "Unsigned integer size used to index degrees of freedom and sparse indices." )

mark_as_advanced( MLHP_BUILD_ARCHIVE_DIR MLHP_BUILD_LIBRARY_DIR MLHP_BUILD_BINARY_DIR
                  MLHP_INDEX_SIZE_CELLS MLHP_INDEX_SIZE_DOFS )

set( MLHP_OUTPUT_DIRS ARCHIVE_OUTPUT_DIRECTORY ${MLHP_BUILD_ARCHIVE_DIR}
                      LIBRARY_OUTPUT_DIRECTORY ${MLHP_BUILD_LIBRARY_DIR}
                      RUNTIME_OUTPUT_DIRECTORY ${MLHP_BUILD_BINARY_DIR} )
       
# Changes the default install path to build/install, assuming build is the project directory
if ( CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT )
    set( CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_BINARY_DIR}/install" CACHE PATH "default install path" FORCE )
endif( )

# Set dimension to 3 if lower
if( ${MLHP_DIMENSIONS} LESS 3 )
    message(WARNING "MLHP_DIMENSION must be at least 3.")

    set( MLHP_DIMENSIONS 3 CACHE STRING "Highest dimension to instantiate." FORCE ) 
endif( ${MLHP_DIMENSIONS} LESS 3 )

# Set up build types with Release as default
include(tools/cmake/ConfigureBuildType.cmake)

# ---------------------------- Core -------------------------------

# Provides interface target vtu11::vtu11
add_subdirectory(external/vtu11)

# Create mlhp_public_compile_flags and mlhp_private_compile_flags interface targets
include(tools/cmake/ConfigureCompiler.cmake)

# To automatically configure a library export header into build tree
include(GenerateExportHeader)

# Sets MLHP_CORE_SOURCES and MLHP_CORE_INCLUDES
include( src/core/files.cmake )

list( TRANSFORM MLHP_CORE_SOURCES PREPEND src/core/ )
list( TRANSFORM MLHP_CORE_INCLUDES PREPEND include/mlhp/core/ )

add_library( mlhpcore ${MLHP_CORE_SOURCES} ${MLHP_CORE_INCLUDES} include/mlhp/core.hpp )
add_library( mlhp::core ALIAS mlhpcore )

target_link_libraries( mlhpcore PRIVATE mlhp_private_compile_flags vtu11::vtu11
                                PUBLIC mlhp_public_compile_flags )

target_include_directories( mlhpcore PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include 
                                            ${CMAKE_CURRENT_BINARY_DIR}/include )   
# Not sure what this does: $<INSTALL_INTERFACE:include>

generate_export_header( mlhpcore EXPORT_MACRO_NAME MLHP_EXPORT EXPORT_FILE_NAME 
                        ${CMAKE_CURRENT_BINARY_DIR}/include/mlhp/core/coreexport.hpp )

# Set output directories
set_target_properties( mlhpcore PROPERTIES ${MLHP_OUTPUT_DIRS} )

# Python module links statically, so doesn't need to install the static library
if( NOT SKBUILD )
	install( TARGETS mlhpcore
			 EXPORT mlhpcore-targets
			 ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
			 LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
			 RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
			 INCLUDES DESTINATION ${LIBLEGACY_INCLUDE_DIRS} )
			 
	# install( DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/mlhp
	#          DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/ )
	#         
	# install( DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include/mlhp
	#          DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/ )
endif(NOT SKBUILD)

# ----------------------- Core testrunner -------------------------

if( ${MLHP_TEST_CPP} )

    # Creates MLHP_CORE_TEST_SOURCES variable
    include( tests/core/files.cmake )
    include( tests/system/files.cmake )

    # Core unit tests
    list( TRANSFORM MLHP_CORE_TEST_SOURCES PREPEND tests/core/ )
    list( TRANSFORM MLHP_SYSTEM_TEST_SOURCES PREPEND tests/system/ )

    add_executable( mlhpcore_testrunner ${MLHP_CORE_TEST_SOURCES} )

    target_link_libraries( mlhpcore_testrunner PRIVATE mlhp::core mlhp_private_compile_flags )
    target_include_directories( mlhpcore_testrunner PRIVATE . )   
    set_target_properties( mlhpcore_testrunner PROPERTIES ${MLHP_OUTPUT_DIRS} )

    file( GLOB MLHP_CORE_TESTFILES tests/core/testfiles/* )
    file( COPY ${MLHP_CORE_TESTFILES} DESTINATION testfiles/core )

    install( DIRECTORY tests/core/testfiles/ DESTINATION testfiles/core )

    # System tests
    add_executable( system_testrunner ${MLHP_SYSTEM_TEST_SOURCES} )
                    
    target_link_libraries( system_testrunner PRIVATE mlhp::core mlhp_private_compile_flags )
    target_include_directories( system_testrunner PRIVATE . )  
    set_target_properties( system_testrunner PROPERTIES ${MLHP_OUTPUT_DIRS} )
  
    install( TARGETS mlhpcore_testrunner system_testrunner )

endif( ${MLHP_TEST_CPP} )

# --------------------------- Examples ----------------------------

include( tools/cmake/CreateExampleDriver.cmake )

CreateExampleCppDriver( fichera_corner "Poisson equation fichera corner benchmark." )
CreateExampleCppDriver( j2_pressurized_sphere_fcm "Immersed pressurized sphere with J2 plasticity." )
CreateExampleCppDriver( linear_elastic_fcm_stl "FCM example with stl geometry." )
CreateExampleCppDriver( travelling_heat_source "Linear heat equation with moving point-like source." )
CreateExampleCppDriver( waveequation_matrix_free "Immersed scalar wave equation." )
CreateExampleCppDriver( wing_elastic_fcm "FCM example with linear elasticity." )

CreateExamplePythonDriver( example_elastic_fcm "Placeholder fcm example." )
CreateExamplePythonDriver( example_elastic_fcm_csg "Compute with a csg geometry." )
CreateExamplePythonDriver( example_elastic_fcm_stl "Compute with an stl geometry." )
CreateExamplePythonDriver( example_elastic_gmsh "Compute with unstructured grid from gmsh file." )
CreateExamplePythonDriver( example_elastic_gyroid "Gyroid TPMS implicit geometry." )
CreateExamplePythonDriver( example_interactive_eigenmodes "Interactive eigenvalue analysis using a line segment boundary." )
CreateExamplePythonDriver( example_planestress_fcm_plate "Plate with a hole using FCM." )
CreateExamplePythonDriver( example_poisson_compiled "Define integrand with numba or cffi." )

# ----------------------- Python bindings -------------------------

if( ${MLHP_PYTHON} )

    add_subdirectory( external/pybind11 )

    # Creates MLHP_PYTHON_BINDING_SOURCES variable
    include( src/python/files.cmake )

    list( TRANSFORM MLHP_PYTHON_BINDING_SOURCES PREPEND src/python/ )

    pybind11_add_module( pymlhpcore ${MLHP_PYTHON_BINDING_SOURCES} )

    target_link_libraries( pymlhpcore PRIVATE mlhpcore mlhp_private_compile_flags )
    
    target_include_directories( pymlhpcore PRIVATE . )

    # Set output directories
    set_target_properties( pymlhpcore PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${MLHP_BUILD_BINARY_DIR} )

    # After building pymlhpcore write file bin/mlhpPath.py containing directory of python module
    add_custom_command( TARGET pymlhpcore POST_BUILD COMMAND ${CMAKE_COMMAND} -E echo 
      "$<TARGET_FILE_DIR:pymlhpcore>" > ${MLHP_BUILD_BINARY_DIR}/mlhpPythonPath )

    # Copy python sources
    file( COPY src/python/mlhp.py DESTINATION ${MLHP_BUILD_BINARY_DIR} )

	# Install differently when building with scikit-build-core
    if(SKBUILD)
	    install( FILES src/python/mlhp.py DESTINATION . )
	    install( TARGETS pymlhpcore LIBRARY DESTINATION . )
    else(SKBUILD)
	    install( FILES src/python/mlhp.py DESTINATION ${CMAKE_INSTALL_BINDIR} )
	    install( TARGETS pymlhpcore LIBRARY DESTINATION ${CMAKE_INSTALL_BINDIR} )
    endif(SKBUILD)

    if( ${MLHP_TEST_PYTHON} )

        # Creates MLHP_PYTHON_TESTS variable
        include( tests/system/files.cmake )

        list( TRANSFORM MLHP_PYTHON_TESTS PREPEND tests/system/ )
            
        file( COPY ${MLHP_PYTHON_TESTS} DESTINATION ${MLHP_BUILD_BINARY_DIR}/systemtests )
        file( COPY tests/system/run_systemtests.py DESTINATION ${MLHP_BUILD_BINARY_DIR} )
        
	    install( FILES ${MLHP_PYTHON_TESTS} DESTINATION ${CMAKE_INSTALL_BINDIR}/systemtests )
	    install( FILES tests/system/run_systemtests.py DESTINATION ${CMAKE_INSTALL_BINDIR} )

    endif( ${MLHP_TEST_PYTHON} )
endif( ${MLHP_PYTHON} )

# Configure x macro strings
set(MLHP_DIMENSIONS_XMACRO_LIST)
set(MLHP_POSTPROCESSING_DIMENSIONS_XMACRO_LIST)

foreach(DIM RANGE 1 ${MLHP_DIMENSIONS})
    set(MLHP_DIMENSIONS_XMACRO_LIST "${MLHP_DIMENSIONS_XMACRO_LIST} MLHP_INSTANTIATE_DIM(${DIM})")
endforeach(DIM)

foreach(DIM RANGE 1 3)
    set(MLHP_POSTPROCESSING_DIMENSIONS_XMACRO_LIST "${MLHP_POSTPROCESSING_DIMENSIONS_XMACRO_LIST} MLHP_INSTANTIATE_DIM(${DIM})")
endforeach(DIM)

# Configure configuration header to build tree
configure_file( src/core/config.hpp.in include/mlhp/core/config.hpp )
