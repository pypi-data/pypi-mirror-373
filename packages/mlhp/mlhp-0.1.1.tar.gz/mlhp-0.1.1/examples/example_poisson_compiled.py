# This file is part of the mlhp project. License: See LICENSE
import mlhp
import numpy

from numba import cfunc, types, carray

targetTypes = [mlhp.AssemblyType.UnsymmetricMatrix, mlhp.AssemblyType.Vector]
ndim, nfields, ntargets = 3, 1, len(targetTypes)

print("Compiling...", flush=True)

# Use numba to compile element linear system callback into c function and pass function pointer to mlhp
@cfunc(types.float64(types.CPointer(types.float64)))
def rhs(xyzPtr):
    xyz = carray(xyzPtr, ndim)
    return numpy.sqrt(xyz[0] + xyz[1] + xyz[2])

@cfunc(types.float64(types.CPointer(types.float64)))
def conductivity(xyzPtr): return 1

@cfunc(types.void(types.CPointer(types.CPointer(types.float64)), # targets
                  types.CPointer(types.CPointer(types.float64)), # shapes
                  types.CPointer(types.CPointer(types.float64)), # mapping
                  types.CPointer(types.float64),                 # local coordinates
                  types.CPointer(types.float64),                 # history variables
                  types.CPointer(types.float64),                 # temporary storage
                  types.CPointer(types.int64),                   # location map
                  types.CPointer(types.int64),                   # total sizes
                  types.CPointer(types.int64),                   # field sizes
                  types.float64, types.float64, types.int64))    # det(J), weight, element index
def evaluate(targets_, shapes_, mapping_, rst_, history_, tmp_, locationMap_, sizes_, fieldSizes_, detJ, weight, ielement):
    ndof, ndofpadded = carray(sizes_, 2)
    xyz_ = carray(mapping_, 1)[0]
    
    Ke = carray(carray(targets_, ntargets)[0], (ndof, ndofpadded))
    Fe = carray(carray(targets_, ntargets)[1], ndofpadded)
    
    N = carray(carray(shapes_, nfields)[0], (4, ndofpadded))[0]
    B = carray(carray(shapes_, nfields)[0], (4, ndofpadded))[1:]
    
    k = conductivity(xyz_) * weight * detJ
    f = rhs(xyz_) * weight * detJ
    
    for idof in range(ndof):
        for jdof in range(ndof):
            for axis in range(ndim):
                Ke[idof, jdof] += B[axis, idof] * B[axis, jdof] * k
    
    for idof in range(ndof):
        Fe[idof] += N[idof] * f

print("Preprocessing...", flush=True)

integrand = mlhp.domainIntegrand(ndim, evaluate, types=targetTypes, maxdiff=1)

# Preprocess
mesh = mlhp.makeRefinedGrid([100, 100, 100])
basis = mlhp.makeHpTrunkSpace(mesh, degree=1, nfields=nfields)

dirichlet = mlhp.integrateDirichletDofs(mlhp.scalarField(ndim, 0.0), basis, [1, 3, 5])

print(mesh)
print(basis)

print("Assembling...", flush=True)

matrix = mlhp.allocateSparseMatrix(basis, dirichlet[0])
vector = mlhp.allocateRhsVector(matrix)

print(matrix, flush=True)

mlhp.integrateOnDomain(basis, integrand, [matrix, vector], dirichletDofs=dirichlet)

print("Solving...", flush=True)

dofs = mlhp.inflateDofs(mlhp.makeCGSolver()(matrix, vector), dirichlet)

print("Postprocessing...", flush=True)

processors = [mlhp.solutionProcessor(ndim, dofs, "Temperature" )]

sampling = mlhp.gridCellMesh(mlhp.degreeOffsetResolution(basis), mlhp.PostprocessTopologies.Volumes)
output = mlhp.PVtuOutput(filename="outputs/example_poisson_compiled")
            
mlhp.basisOutput(basis, sampling, output, processors)

# Backwards consistency check
assert(abs(mlhp.norm(dofs) - 104.83856802268146) < 1e-8)

print("Done.")

# # Alternatively: use cffi to directly compile C code
# import cffi
# ffibuilder = cffi.FFI()
# ffibuilder.cdef("""extern unsigned long long address;""")
# ffibuilder.set_source("_integrand_cffi",
#     """
#         #include "math.h"
#         
#         double rhs(double* xyz)
#         {
#             return sqrt(xyz[0] + xyz[1] + xyz[2]);
#         }
#         
#         double conductivity(double* xyz)
#         {
#             return 1.0;
#         }
#         
#         void integrand(double** targets,     double** shapes,     double** mapping, 
#                        double*  rst,         double*  history,    double*  tmp, 
#                        int64_t* locationMap, int64_t* totalSizes, int64_t* fieldSizes, 
#                        double   detJ,        double   weight,     int64_t  ielement)
#         {
#            int64_t ndof = totalSizes[0];
#            int64_t ndofpadded = totalSizes[1];
#            
#            double* N = shapes[0];
#            double* B = shapes[0] + ndofpadded;
#            
#            double k = conductivity(mapping[0]) * weight * detJ;
#            double f = rhs(mapping[0]) * weight * detJ;
#            
#            for(int64_t idof = 0; idof < ndof; ++idof)
#            {
#                for(int64_t jdof = 0; jdof < ndof; ++jdof)
#                {
#                    for(int64_t axis = 0; axis < 3; ++axis)
#                    {
#                        targets[0][idof * ndofpadded + jdof] += B[axis * ndofpadded + idof] * 
#                                                                B[axis * ndofpadded + jdof] * k;
#                    }
#                }
#                
#                targets[1][idof] += N[idof] * f;
#            }
#         }
#         
#         unsigned long long address = (unsigned long long)&integrand;
#     """)
# ffibuilder.compile()
# from _integrand_cffi import lib as evaluate
