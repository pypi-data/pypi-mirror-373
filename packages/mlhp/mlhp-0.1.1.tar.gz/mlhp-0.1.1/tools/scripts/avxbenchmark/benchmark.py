#!/usr/bin/python

import os
import subprocess
import re

raise ValueError("MLHP_ENABLE_OMP changed to MLHP_MULTITHREADING=OMP")

# (polynomial degree, number of elements, refinement level)
configurations = [(1, 140, 0), (2, 65, 0), (3, 34, 0), (5, 12, 0), (8, 4, 0), (3, 8, 3)]

#flags = ("-march=native -mprefer-vector-width=512", )
flags = ("-march=native -mno-avx512f -mno-avx", "-march=native -mno-avx512f", "-march=native -mprefer-vector-width=512")

#alignments = (64, ) 
alignments = (8, 32, 64)

compileCores = 20

runTimes = 2

numberOfIterations = 50

logFile = "./performance_benchmark"

tmpdir = "tmp_mlhp_benchmark"
source = tmpdir + "/source"
build = tmpdir + "/build"

keywords = ["grid", "basis", "allocation", "shapes", "matrix", "scatter", "assembly", "total"]

if not os.path.exists( tmpdir ):
    os.makedirs( tmpdir )

os.system( "rm -rf " + tmpdir + "/*" )
os.system( "git clone --recursive https://gitlab.com/phmkopp/mlhp.git " + source )
os.system( "cd " + source + "&& git checkout refactorSpatialFunctions && cd -" )

os.system( "mkdir " + build )

def readFile( filename ):
    with open( filename, 'r') as content_file:
        code = content_file.read()
    return code

def writeFile( filename, content ):
    with open( filename, "w" ) as text_file:
        text_file.write( content )

def placeFile( polynomialDegree, numberOfElements, refinementLevel, MatrixType ):
    code = readFile( "benchmark.cpp.in" )
    code = code.replace( '__polynomialDegree__', str( polynomialDegree ) )
    code = code.replace( '__numberOfElements__', str( numberOfElements ) )
    code = code.replace( '__refinementLevel__', str( refinementLevel ) )
    code = code.replace( '__MatrixType__', MatrixType )

    writeFile( os.path.join( source, "tests", "system", "files.cmake" ), "set( MLHP_SYSTEM_TEST_SOURCES benchmark.cpp )" )
    writeFile( os.path.join( source, "tests", "system", "benchmark.cpp" ), code )


def cmakeConfigure( flags, alignment ):
    allFlags = "-Ofast -Wno-unused-parameter -Wno-unused-variable -Wno-unused-local-typedefs" + " " + flags
    arguments = "-DMLHP_ALL_OPTIMIZATIONS=OFF "\
                "-DMLHP_DEBUG_CHECKS=OFF "     \
                "-DMLHP_ENABLE_OMP=OFF "

    arguments += "-DMLHP_SIMD_ALIGNMENT=" + str( alignment ) + " "
    arguments += "-DCMAKE_CXX_FLAGS=\"" + allFlags + "\""

    os.system("cd " + build + " && cmake " + arguments + " ../source"  )

def compileAndRun( ):
    os.system("cd " + build + " && make -j" + str( compileCores ) + " system_testrunner > /dev/null" )

    times = [0.0 for _ in keywords]

    for _ in range( runTimes ):
        os.system(build + "/bin/system_testrunner > " + tmpdir + "/current_benchmark_output.txt" )

        content = readFile( tmpdir + "/current_benchmark_output.txt" )

        for iTime, name in enumerate( keywords ):
            times[iTime] += float( re.search( r"" + name + ": (.*)", content ).group(1) )

    return [time / float( runTimes ) for time in times]

def replaceInFile( filename, old, new ):
    content = readFile( filename )
    content = content.replace( old, new )
    writeFile( filename, content )

writeFile( logFile + "_log.txt", "" )
def log( stuff ):
    print( stuff )
    with open( logFile + "_log.txt","a") as f:
        f.write( stuff + "\n" )

# Inject timing couts into assembly.cpp
def insertLines( filename, lines ):
    with open( filename, "r" ) as file:
        content = file.readlines( )

    for index, (number, line) in enumerate( lines ):
        content.insert( number + index, line + "\n" )

    with open( filename, "w" ) as file:
        for line in content:
            file.write( line );

cppCast = lambda var : "std::chrono::duration_cast<std::chrono::duration<double>>(" + var + " - t0).count( )"
cppPoint = lambda index : "auto t" + str( index ) + " = std::chrono::steady_clock::now( );"
cppCout = lambda text : "std::cout << " + text + " << std::endl;\n"

start = 234

cppCode = [ #( 14, "#include <iostream>"),
            ( start + 22, "auto t0 = std::chrono::steady_clock::now( );\n"\
                          "auto shapesTime  = t0;\n"\
                          "auto matrixTime  = t0;\n"\
                          "auto scatterTime = t0;"),
            ( start + 30, cppPoint(1) ),
            ( start + 31, cppPoint(2) ),
            ( start + 39, cppPoint(3) ),
            ( start + 40, cppPoint(4) ),
            ( start + 40, "shapesTime  += t4 - t3;\n" ),
            ( start + 43, cppPoint(5) ),
            ( start + 44, cppPoint(6) ),
            ( start + 45, cppPoint(7) ),
            ( start + 45, "shapesTime  += t6 - t5;\n"\
                          "matrixTime  += t7 - t6;\n"),
            ( start + 48, cppPoint(8) ),
            ( start + 49, cppPoint(9) ),
            ( start + 49, "shapesTime  += t2 - t1;\n"\
                          "scatterTime += t9 - t8;\n"),
            ( start + 50, cppCout( "\"shapes:  \" << " + cppCast( "shapesTime"  ) ) + \
                          cppCout( "\"matrix:  \" << " + cppCast( "matrixTime"  ) ) + \
                          cppCout( "\"scatter: \" << " + cppCast( "scatterTime" ) ) ) ]
                    
insertLines( source + "/src/core/assembly.cpp", cppCode )
 

# Start measurements
results = [ [ [ [ [ ] for _3 in range( 2 * len( flags ) ) ] for _2 in configurations ] for _1 in alignments ] for _ in keywords ]

def printResults( ):
    for iTiming, name in enumerate( keywords ):
        log( "-------------------- " + name + " time -----------------\n" )
        for iAlign, alignment in enumerate( alignments ):
            resultString = "alignment: " + str( alignment ) + "\n"
            for iConfig, conf in enumerate( configurations ):
                for iCompile, time in enumerate( results[iTiming][iAlign][iConfig] ):
                    resultString += str( sum( time ) / len( time ) ) + ", "
                resultString += "\n"
            log( resultString )

for iteration in range( numberOfIterations ):
    log("============================ iteration " + str( iteration ) + " =================================")
    for iAlign, alignment in enumerate( alignments ):
        for iFlag, flag in enumerate( flags ):
            log( "configuring with " + str( alignment ) + " byte alignement and compiler flags: " + flag )

            placeFile( *configurations[0], MatrixType="Symmetric" )

            cmakeConfigure( flag, alignment )

            for iConfig, config in enumerate( configurations ):
 
               for iSymm, symmetry in enumerate(("Unsymmetric", "Symmetric")):
                    placeFile( *config, MatrixType=symmetry )

                    if symmetry == "Symmetric":
                        replaceInFile( source + "/src/core/integrands.cpp", "linalg::unsymmetricElementLhs", "linalg::symmetricElementLhs" )
                        replaceInFile( source + "/src/core/integrands.cpp", "AssemblyType::UnsymmetricMatrix", "AssemblyType::SymmetricMatrix" )
                    else: 
                        replaceInFile( source + "/src/core/integrands.cpp", "linalg::symmetricElementLhs", "linalg::unsymmetricElementLhs" )
                        replaceInFile( source + "/src/core/integrands.cpp", "AssemblyType::SymmetricMatrix", "AssemblyType::UnsymmetricMatrix" )

                    time = compileAndRun( )
 
                    log( "p = " + str( config[0] ) + ", n = " + str( config[1] ) + ", r = " + str( config[2] ) + ", " + symmetry + ": " + str( time ) )
 
                    for i in range( len( keywords ) ):
                        results[i][iAlign][iConfig][iSymm * len(flags) + iFlag].append( time[i] )

    printResults( )
    writeFile( logFile + "_data.py", "data = " + str( results ) )

os.system( "rm -rf " + tmpdir )
