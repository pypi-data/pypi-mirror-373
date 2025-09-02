import unittest
import sys

pattern = "*_test.py"

if len(sys.argv) > 1:
    pattern = sys.argv[1]

loader = unittest.TestLoader( )
suite = loader.discover('systemtests', pattern=pattern)
runner = unittest.TextTestRunner( )
result = runner.run(suite)
exit(not result.wasSuccessful())

