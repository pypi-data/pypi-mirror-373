$ cat printMedians.py
#!/usr/bin/python

import numpy
import performance_benchmark_data

def printMatrix( M ):
    for row in M:
        string = str( row[0] )
        for entry in row[1:]:
            string += ", " + str( entry )
        print( string )
    print( "" )

def printResult( data, name ):
    print( "--- " + str( name ) + " time ---" )
    for iAlign in range( data.shape[0] ):
        printMatrix( numpy.median( data[iAlign], axis=-1 ) )

data = numpy.array( performance_benchmark_data.data )

print( str( data.shape[0] ) + " data sets." )
print( str( data.shape[1] ) + " alignments." )
print( str( data.shape[4] ) + " number of runs." )

printResult( data[0], "Grid" )
printResult( data[1], "Basis" )
printResult( data[2], "Allcoation" )
printResult( data[3], "Shapes" )
printResult( data[4], "Matrix" )
printResult( data[5], "Scatter" )
printResult( data[6], "Total assembly" )
printResult( data[7], "Total" )
