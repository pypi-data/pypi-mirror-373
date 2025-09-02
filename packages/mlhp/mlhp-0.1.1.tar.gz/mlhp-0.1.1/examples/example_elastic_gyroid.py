import mlhp, math

D = 3

print("1. Setting up mesh and basis", flush=True)

degree = 3
treedepth = 1
alpha = 1e-4

# Parse implicit function string (alternatively: use numba, see end of file)
Lx, Ly, Lz, t, pi = 1, 1, 1, 0.2, math.pi
term1 = f"cos(2*{pi}*x/{Lx}) * sin(2*{pi}*y/{Ly})"
term2 = f"cos(2*{pi}*y/{Ly}) * sin(2*{pi}*z/{Lz})"
term3 = f"cos(2*{pi}*z/{Lz}) * sin(2*{pi}*x/{Lx})"

domain = mlhp.implicitFunction(3, f"abs({term1} + {term2} + {term3}) < {t}")

grid = mlhp.makeGrid(ncells=[20] * D, lengths=[1.9] * D, origin=[-0.45] * D)
print(grid)

grid = mlhp.makeRefinedGrid(mlhp.makeFilteredGrid(grid, domain=domain, nseedpoints=degree + 2))
basis = mlhp.makeHpTrunkSpace(grid, degree=degree, nfields=D)

print(grid)
print(basis)

print("2. Computing dirichlet boundary conditions", flush=True)

left = mlhp.integrateDirichletDofs(mlhp.vectorField(D, [0.0] * D), basis, [0])
right = mlhp.integrateDirichletDofs(mlhp.scalarField(D, 1e-3), basis, [1], ifield=0)

dirichlet=mlhp.combineDirichletDofs([left, right])

print("3. Setting up physics", flush=True)

E = mlhp.scalarField(D, 200 * 1e9)
nu = mlhp.scalarField(D, 0.3)
rhs = mlhp.vectorField(D, [0.0, 0.0, 0])

kinematics = mlhp.smallStrainKinematics(D) 
constitutive = mlhp.isotropicElasticMaterial(E, nu)
integrand = mlhp.staticDomainIntegrand(kinematics, constitutive, rhs)

print("4. Allocating linear system", flush=True)

matrix = mlhp.allocateSparseMatrix(basis, dirichlet[0])
vector = mlhp.allocateRhsVector(matrix)

print(matrix)

print("5. Integrating linear system", flush=True)

#quadrature = mlhp.spaceTreeQuadrature(domain, depth=treedepth, epsilon=alpha)
quadrature = mlhp.momentFittingQuadrature(domain, depth=treedepth, epsilon=alpha)

# To extract quadrature points with integration order 3 (plot uses matplotlib and assumes D = 2):
# partitions = [quadrature.evaluate(mesh, icell, [3, 3]) for icell in range(mesh.ncells())]
# coordinates = [xyz for cell in partitions for partition in cell for xyz in partition.xyz]
# plt.plot([c[0] for c in coordinates], [c[1] for c in coordinates], 'x')

mlhp.integrateOnDomain(basis, integrand, [matrix, vector], 
    dirichletDofs=dirichlet, quadrature=quadrature)

print("6. Solving linear system", flush=True)

P = mlhp.additiveSchwarzPreconditioner(matrix, basis, dirichlet[0])
#P = mlhp.diagonalPreconditioner(matrix)

interiorDofs, norms = mlhp.cg(matrix, vector, M=P, maxiter=10000, residualNorms=True)

del matrix, P

allDofs = mlhp.inflateDofs(interiorDofs, dirichlet)

print("7. Postprocessing solution", flush=True)

processors = [mlhp.solutionProcessor(D, allDofs, "Displacement"),
              mlhp.vonMisesProcessor(allDofs, kinematics, constitutive),
              mlhp.functionProcessor(domain)]

gridmesh = mlhp.gridCellMesh(mlhp.degreeOffsetResolution(basis), mlhp.PostprocessTopologies.Volumes)
surfmesh = mlhp.boundaryCellMesh(domain, [degree + 2]*D)

gridoutput = mlhp.PVtuOutput(filename="outputs/gyroid_mesh")
surfoutput = mlhp.PVtuOutput(filename="outputs/gyroid_surf")
            
mlhp.basisOutput(basis, gridmesh, gridoutput, processors)
mlhp.basisOutput(basis, surfmesh, surfoutput, processors)

assert(abs(mlhp.norm(allDofs) - 0.05371560158) < 1e-10)

# # Alternatively: use numba to pass compiled implicit function
# from numba import cfunc, types, carray
# 
# Lx, Ly, Lz, t = 1, 1, 1, 0.2
# 
# @cfunc(types.float64(types.CPointer(types.double), types.int64))
# def gyroid(xyz, ndim): 
#     x, y, z = carray(xyz, ndim)[0], carray(xyz, ndim)[1], carray(xyz, ndim)[2]
#     
#     term1 = math.cos(2 * math.pi * x / Lx) * math.sin(2 * math.pi * y / Ly)
#     term2 = math.cos(2 * math.pi * y / Ly) * math.sin(2 * math.pi * z / Lz)
#     term3 = math.cos(2 * math.pi * z / Lz) * math.sin(2 * math.pi * x / Lx)
#     
#     return abs(term1 + term2 + term3) < t
# 
# domain = mlhp.implicitFunction(3, gyroid)
