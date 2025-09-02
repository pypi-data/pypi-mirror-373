# This file is part of the mlhp project. License: See LICENSE

import mlhp
import scipy
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import matplotlib.collections as col

origin, lengths = [0.0, 0.0], [12.0, 8.0]

outline = [[origin[0], origin[0] + lengths[0], origin[0] + lengths[0], origin[0], origin[0]],
           [origin[1], origin[1], origin[1] + lengths[1], origin[1] + lengths[1], origin[0]]]

def compute(vertices):
    D = 2
    p = 1
    resolution = p + 1
    constrain = True
    projectStress = True
    eigenpair = 0 if constrain else 2
    nelements = mlhp.gridsplit(lengths, targetNumber=1000)
    
    # Setup boundaries and preprocess
    lines = [(i, i + 1) for i in range(len(vertices) - 1)] + [(len(vertices) - 1, 0)]
    boundary = mlhp.lineSegments(vertices, lines)
    
    domain = mlhp.rayIntersectionDomain(boundary)
    domainQuadrature = mlhp.spaceTreeQuadrature(function=domain, depth=p + 2, epsilon=0.0)
    
    baseGrid = mlhp.makeGrid(nelements, lengths=lengths, origin=origin)
    filteredGrid = mlhp.makeFilteredGrid(baseGrid, domain=domain)
    refinedGrid = mlhp.makeRefinedGrid(filteredGrid)
    
    basis = mlhp.makeHpTrunkSpace(refinedGrid, degree=p, nfields=D)
    
    # Allocate matrices and vectors
    K = mlhp.allocateSparseMatrix(basis)
    M = K.copy()
    F = mlhp.allocateRhsVector(K)
    
    # Assemble domain integral
    E = mlhp.scalarField(D, 1.0)
    nu = mlhp.scalarField(D, 0.3)
    rhs = mlhp.vectorField(D, [0.0] * D)
    
    kinematics = mlhp.smallStrainKinematics(D) 
    constitutive = mlhp.planeStressMaterial(E, nu)
    stiffnessIntegrand = mlhp.staticDomainIntegrand(kinematics, constitutive, rhs)
    massIntegrand = mlhp.l2DomainIntegrand(mass=mlhp.scalarField(D, 1.0), rhs=None)
    
    domainQuadrature = mlhp.spaceTreeQuadrature(function=domain, depth=p + 2, epsilon=1e-6)
    
    mlhp.integrateOnDomain(basis, stiffnessIntegrand, [K, F], quadrature=domainQuadrature)
    mlhp.integrateOnDomain(basis, massIntegrand, [M], quadrature=domainQuadrature)
    
    # Assemble boundary integral
    intersected, celldata = mlhp.intersectWithMesh(boundary, refinedGrid)
    lineQuadrature = mlhp.simplexQuadrature(intersected, celldata)
    penaltyIntegrand = mlhp.l2BoundaryIntegrand(lhs=mlhp.vectorField(D, [1e4] * D), rhs=mlhp.vectorField(D, [0.0] * D))
    
    if constrain:
        mlhp.integrateOnSurface(basis, penaltyIntegrand, [K, F], lineQuadrature)
    
    # Solve eigenvalue problem
    scipyM = scipy.sparse.csr_matrix(*M.csr_arrays)
    scipyK = scipy.sparse.csr_matrix(*K.csr_arrays)
    eigenvalues, eigenvectors = scipy.sparse.linalg.eigsh(scipyK, M=scipyM, k=eigenpair + 1, sigma=0.0)
    
    # Evaluate postprocessing and store result
    result = mlhp.DataAccumulator()
    cellmesh = mlhp.domainCellMesh(domain, [resolution]*D)
    dofs = mlhp.DoubleVector(eigenvectors.T[eigenpair])
    dofs = dofs if not projectStress else mlhp.projectGradient(basis, dofs, domainQuadrature)
    processors = [mlhp.vonMisesProcessor(dofs, kinematics, constitutive)]
    mlhp.basisOutput(basis, cellmesh=cellmesh, processors=processors, output=result)
    
    # Plot result
    plt.cla()
    plt.plot(*outline, '--', color='gray')
    plt.tricontourf(result.triangulation(mpl=True), result.data()[0], levels=20, cmap='turbo')
    refinedGrid.plot(show=False)
    plt.title("Von Mises stress in first nonzero eigenmode.")
    plt.xlabel("x")
    plt.ylabel("y")
    
    # Plot boundary segments (change boundary to intersected to see the quadrature supports)
    for ((x0, y0), (x1, y1)) in boundary.lineCollection(mpl=False):
        plt.plot((x0, x1), (y0, y1), 'x-r')
    
    ## Plot boundary quadrature points (change lineQuadrature to domainQuadrature for domain quadrature points)
    #if constrain:
    #    partitions = [p for i in range(refinedGrid.ncells()) for p in lineQuadrature.evaluate(refinedGrid, i, [1, 1])]
    #    plt.plot([xyz[0] for p in partitions for xyz in p.xyz], [xyz[1] for p in partitions for xyz in p.xyz], 'bx')

fig = plt.figure(figsize=(12, 8))
plt.plot(*outline, '--', color='gray')
plt.title("Pick domain corners (close with right click)")
plt.xlabel("x")
plt.ylabel("y")

vertices = []
while True:
    points = plt.ginput(1, timeout=1e5, mouse_stop=plt.MouseButton.RIGHT)
    if len(points):
        vertices.append((float(points[0][0]), float(points[0][1])))
        print(f"New vertex: {vertices[-1]}")
        if len(vertices) > 2:
            plt.plot([v[0] for v in vertices], [v[1] for v in vertices], '-rx')
            compute(vertices)
        fig.canvas.draw()
    else:
        break
