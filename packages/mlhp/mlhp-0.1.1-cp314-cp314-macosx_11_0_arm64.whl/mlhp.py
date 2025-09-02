# This file is part of the mlhp project. License: See LICENSE

import os, sys, ast
from functools import reduce

try:
    # mlhp.py script folder
    path = os.path.abspath( os.path.dirname(sys.argv[0]) );
    
    # Try to open path/mlhpPythonPath containing the python module path. This
    # file is written as post build command after compiling pymlhpcore.
    with open( os.path.join( path, 'mlhpPythonPath' ), 'r') as f:
        sys.path.append( os.path.normpath( f.read( ).splitlines( )[0] ) )
   
except IOError: 
    pass

from pymlhpcore import *
from pymlhpcore import _scalarFieldFromTree, _vectorFieldFromTree, _vectorFieldFromAddress, _scalarFieldFromAddress, _domainIntegrandFromAddress

def triangulation(vertices, triangles):
    result = simplexMesh(vertices, triangles)
    if type(result) != SimplexMesh3D:
        raise ValueError("Invalid input")
    return result
    
def lineSegments(vertices, segments):
    result = simplexMesh(vertices, segments)
    if type(result) != SimplexMesh2D:
        raise ValueError("Invalid input")
    return result
    
dataAccumulator = DataAccumulator

def _iterativeSolve(internalSolve, A, b, x0, *, rtol, atol, maxiter, M, residualNorms, tmp):
    maxiter_ = len(b) if maxiter is None else maxiter
    
    mA = linearOperator(A) if isinstance(A, AbsSparseMatrix) else A
    mM = noPreconditioner() if M is None else (linearOperator(M) if isinstance(M, AbsSparseMatrix) else M)
    
    solution = DoubleVector(len(b), 0.0) if x0 is None else copy(vector=x0)
    norms = internalSolve(mA, b, x0=solution, rtol=rtol, atol=atol, maxiter=maxiter_, M=mM, tmp=tmp);
    
    return [solution, norms] if residualNorms else solution
    
def cg(A, b, x0=None, *, rtol=1e-10, atol=0.0, maxiter=None, M=None, residualNorms=False, tmp=None):
    return _iterativeSolve(internalCG, A, b, x0, rtol=rtol, atol=atol, maxiter=maxiter, M=M, residualNorms=residualNorms, tmp=tmp)

def bicgstab(A, b, x0=None, *, rtol=1e-10, atol=0.0, maxiter=None, M=None, residualNorms=False, tmp=None):
    return _iterativeSolve(internalBiCGStab, A, b, x0, rtol=rtol, atol=atol, maxiter=maxiter, M=M, residualNorms=residualNorms, tmp=tmp)

def _makeSolve(solver, *, rtol, atol, maxiter, tmp):
    def solve(A, b):
        return solver(A, b, rtol=solve.rtol, atol=solve.atol, maxiter=solve.maxiter, M=diagonalPreconditioner(A), tmp=solve.tmp)
    solve.rtol = rtol
    solve.atol = atol
    solve.maxiter = maxiter
    solve.tmp = tmp
    return solve
    
def makeCGSolver(*, rtol=1e-10, atol=0.0, maxiter=None, tmp=None):
    return _makeSolve(cg, rtol=rtol, atol=atol, maxiter=maxiter, tmp=tmp)

def makeBiCGStabSolver(*, rtol=1e-10, atol=0.0, maxiter=None, tmp=None):
    return _makeSolve(bicgstab, rtol=rtol, atol=atol, maxiter=maxiter, tmp=tmp)

def makeScalars(n, value=0.0):
    return [ScalarDouble(value) for _ in range(n)]
    
def basisOutput(basis, cellmesh=None, output=VtuOutput("output.vtu"), processors=[]):
    kwargs = {'basis': basis, 'output' : output if isinstance(output, MeshWriter) else output.meshWriter()}
    
    if cellmesh is not None:
        kwargs['cellmesh'] = cellmesh
    if len(processors) > 0:
        convert = lambda p : type(p).__name__[:-2] != 'ElementProcessor'
        kwargs['processors'] = [(convertToElementProcessor(p) if convert(p) else p) for p in processors]
            
    internalBasisOutput(**kwargs)
 
def meshOutput(mesh, cellmesh=None, output=VtuOutput("output.vtu"), processors=[]):
    kwargs = {'mesh': mesh, 'output' : output if isinstance(output, MeshWriter) else output.meshWriter()}
    
    if cellmesh is not None:
        kwargs['cellmesh'] = cellmesh
    if len(processors) > 0:
        kwargs['processors'] = processors
            
    internalMeshOutput(**kwargs)
 
def _parseFunction(tree):
    tokens = []
    
    def _convert(node):
        id = _convert.index
        _convert.index += 1
        if isinstance(node, ast.AST):
            nodeType = node.__class__.__name__
            if nodeType == "Constant":
                tokens.append([id, nodeType, str(node.value)])
            elif nodeType == "BinOp":
                tokens.append([id, nodeType, node.op.__class__.__name__, _convert(node.left), _convert(node.right)])
            elif nodeType == "BoolOp" and len(node.values) == 2:
                tokens.append([id, nodeType, node.op.__class__.__name__, _convert(node.values[0]), _convert(node.values[1])])
            elif nodeType == "Compare" and len(node.comparators) == 1:
                tokens.append([id, nodeType, node.ops[0].__class__.__name__, _convert(node.left), _convert(node.comparators[0])])
            elif nodeType == "Call":
                tokens.append([id, nodeType, node.func.id] + [_convert(arg) for arg in node.args])
            elif nodeType == "Name" and node.id in {'x', 'y', 'z', 'r', 's', 't'}:
                tokens.append([id, "Input", str( { 'x' : 0, 'y' : 1, 'z' : 2, 'r' : 0, 's' : 1, 't' : 2 }[node.id] ) ])
            elif nodeType == "Subscript" and isinstance(node.slice, ast.Constant):
                tokens.append([id, "Input", str(node.slice.value)])
            elif nodeType == "UnaryOp":
                tokens.append([id, nodeType, node.op.__class__.__name__, _convert(node.operand)])
            elif nodeType == "IfExp":
                tokens.append([id, "Call", "select", _convert(node.test), _convert(node.body), _convert(node.orelse)])
            elif nodeType == "Num": # Legacy python 3.7
                tokens.append([id, "Constant", str(node.n)])
            elif nodeType == "Subscript" and node.slice.__class__.__name__ == "Index": # Legacy python 3.7
                tokens.append([id, "Input", str(node.slice.value.n)])
            else:
                raise(ValueError("Expression of type \"" + nodeType + "\" is not supported."))
        return str(id)
        
    _convert.index = 0
    _convert(tree)
    
    return [token[1:] for token in sorted(tokens, key=lambda token : token[0])]
    
def _parseScalarField(expr):
    if not isinstance(expr, str): raise ValueError("Expression must be a string")
    
    tree = ast.parse(expr).body
    
    if len(tree) != 1: raise ValueError("Expression string must contain one expression.")
    
    return _parseFunction(tree[0].value)
     
def _parseVectorField(expr):
    if not isinstance(expr, str): raise ValueError("Expression must be a string")
    
    expressionList = ast.parse(expr).body[0].value
    
    if not isinstance(expressionList, ast.List): 
        raise ValueError("Root expression is not a list.")
    
    return [_parseFunction(expr) for expr in expressionList.elts]
    
def scalarField(ndim, func=None, *, address=None, fields=[]):
    if address is not None:
        if func is not None: raise ValueError("Both function and address given.")
        return _scalarFieldFromAddress(ndim, address)
    if hasattr(func, "address"):
        return _scalarFieldFromAddress(ndim, func.address)
    if isinstance(func, (bool, int, float)):
        return _scalarFieldFromTree(ndim, _parseScalarField(str(float(func))), fields)
    if isinstance(func, str):
        return _scalarFieldFromTree(ndim, _parseScalarField(func), fields)
    raise ValueError("Invalid function input parameter.")
 
def vectorField(idim, func=None, odim=None, *, address=None, fields=[]):
    if (func is None) == (address is None): raise ValueError("Must specify either func or address.")
    
    if address is not None:
        if odim is None: raise ValueError("Passing address requires also specifying odim.")
        return _vectorFieldFromAddress(idim, odim, address)
    if hasattr(func, "address"):
        if odim is None: raise ValueError("Passing address requires also specifying odim.")
        return _vectorFieldFromAddress(idim, odim, func.address)
    if isinstance(func, (list, tuple)) and reduce(lambda a, b: a and b, [isinstance(v, (bool, int, float)) for v in func]):
        return _vectorFieldFromTree(idim, _parseVectorField(str([float(f) for f in func])), fields)
    if isinstance(func, str):
        return _vectorFieldFromTree(idim, _parseVectorField(func), fields)
    raise ValueError("Invalid function input parameter.")
  
def implicitFunction(ndim, func=None, address=None, fields=[]):
    return implicitThreshold(scalarField(ndim, func, address=address, fields=fields), 0.5)
 
def domainIntegrand(ndim, callback, types, maxdiff, tmpdofs=0):
    return _domainIntegrandFromAddress(ndim, callback.address, types, maxdiff, tmpdofs) 
    
# Convenience functions for plotting in 2D
def _triangulation(dataAccumulator: DataAccumulator, *, mpl=True):
    mesh = dataAccumulator.mesh()
    pointData = mesh.points()
    connectivity = mesh.connectivity()
    triangles = []
    for offset, type in zip(mesh.offsets(), mesh.types()):
        v = connectivity[offset - 3 if type == 5 else offset - 4:offset]
        if type == 5: triangles += [v]
        if type == 9: triangles += [[v[0], v[1], v[3]], [v[3], v[1], v[2]]]
        
    x, y = pointData[:-2:3], pointData[1:-1:3]
    
    if mpl:
        import matplotlib.tri as tri
        return tri.Triangulation(x, y, triangles)
    else:
        return x, y, triangles
    
def _lineCollection(simplexMesh2D: SimplexMesh2D, *, mpl=True, axis=None, color="black"):
    vertices = simplexMesh2D.vertices
    lines = [[vertices[id] for id in cell] for cell in simplexMesh2D.cells]
    
    if mpl or axis is not None:
        import matplotlib.collections as col
        collection = col.LineCollection(lines, colors=color)
        
    if axis is not None:
        import matplotlib.pyplot as plt
        # Since add_collection currently doesn't adjust the limits, we need to do it ourselves
        coords = [[v[i] for li in lines for v in li] for i in range(2)]
        bounds = [[f(c) for f in (min, max)] for c in coords]
        extend = 0.01 * max([x1 - x0 for x0, x1 in bounds])
        bounds = [(x0 - extend, x1 + extend) for x0, x1 in bounds]
        if len(axis.lines) != 0 or len(axis.collections) != 0:
            lims = (axis.get_xlim(), axis.get_ylim())
            bounds = [(min(x0, l0), max(x1, l1)) for (x0, x1), (l0, l1) in zip(bounds, lims)]
        axis.add_collection(collection)
        axis.set_xlim(bounds[0])
        axis.set_ylim(bounds[1])
        
    return collection if mpl else lines
   
def _plotMesh(absMesh2D: AbsMesh2D, *, axis=None, show=None, color="black"):
    import matplotlib.pyplot as plt
    
    pltAxis = plt.gca() if axis is None else axis
    meshEdges = absMesh2D.skeletonMesh().lineCollection(axis=pltAxis, color=color)
    
    if show or (axis is None and show is None): 
        plt.show()
        
def _plotSegments(lineSegments: SimplexMesh2D, *, axis=None, show=None, color="black"):
    import matplotlib.pyplot as plt
    
    pltAxis = plt.gca() if axis is None else axis
    lineSegments.lineCollection(axis=pltAxis, color=color)
    
    if show or (axis is None and show is None): 
        plt.show()

DataAccumulator.triangulation = _triangulation
SimplexMesh2D.lineCollection = _lineCollection
SimplexMesh2D.plot = _plotSegments
AbsMesh2D.plot = _plotMesh

#del os, sys, path
