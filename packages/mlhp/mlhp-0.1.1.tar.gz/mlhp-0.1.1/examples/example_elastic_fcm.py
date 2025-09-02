import mlhp

D = 3

print("1. Setting up mesh and basis", flush=True)

refinementDepth = 0
polynomialDegree = 2
nelements = [10] * D
lengths = [1.0] * D

alphaFCM = 1e-3 # needs better preconditioning

domain = mlhp.invert(mlhp.implicitCube([0.0,0.101,0.101], [1.0, 0.899, 0.899]))

strategy = mlhp.refineTowardsBoundary(domain, refinementDepth)

grid = mlhp.makeRefinedGrid(nelements, lengths)
grid.refine(strategy)

basis = mlhp.makeHpTensorSpace(grid, polynomialDegree, nfields=D)

print("2. Computing dirichlet boundary conditions", flush=True)

dirichlet = mlhp.integrateDirichletDofs(mlhp.vectorField(D, [0.0] * D), basis, [0])

print("3. Setting up physics", flush=True)

E = mlhp.scalarField(D, 200 * 1e9)
nu = mlhp.scalarField(D, 0.3)
rhs = mlhp.vectorField(D, [0.0, 0.0, 78.5 * 1e3])

kinematics = mlhp.smallStrainKinematics(D) 
constitutive = mlhp.isotropicElasticMaterial(E, nu)
integrand = mlhp.staticDomainIntegrand(kinematics, constitutive, rhs)

print("4. Allocating linear system", flush=True)

matrix = mlhp.allocateSparseMatrix(basis, dirichlet[0])
vector = mlhp.allocateRhsVector(matrix)

print("5. Integrating linear system", flush=True)

quadrature = mlhp.momentFittingQuadrature(domain, 
    depth=polynomialDegree + 1, epsilon=alphaFCM)

mlhp.integrateOnDomain(basis, integrand, [matrix, vector], 
    dirichletDofs=dirichlet, quadrature=quadrature)

print("6. Solving linear system", flush=True)

P = mlhp.additiveSchwarzPreconditioner(matrix, basis, dirichlet[0])
#P = mlhp.diagonalPreconditioner(matrix)

interiorDofs, norms = mlhp.cg(matrix, vector, M=P, maxiter=1000, residualNorms=True)

allDofs = mlhp.inflateDofs(interiorDofs, dirichlet)

print("7. Postprocessing solution", flush=True)

processors = [mlhp.solutionProcessor(D, allDofs, "Displacement"),
              mlhp.functionProcessor(domain)]

postmesh = mlhp.gridCellMesh([polynomialDegree + 3] * D)
output = mlhp.PVtuOutput(filename="outputs/linear_elasticity")
            
mlhp.basisOutput(basis, postmesh, output, processors)

# Backwards consistency check
assert(abs(mlhp.norm(allDofs) - 4.5063430579355176e-05) < 1e-12)
