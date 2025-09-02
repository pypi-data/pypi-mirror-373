# This file is part of the mlhp project. License: See LICENSE

import mlhp
import operator
import unittest

from functools import reduce 

def computeImmersedBeam():

    # Prepare cube vertices [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), ..., (1, 1, 1)]
    vertices = [(float(i), float(j), float(k)) for i in range(2) for j in range(2) for k in range(2)]

    faces = [mlhp.triangulation(vertices, [[0, 2, 1], [2, 3, 1]]), # left
             mlhp.triangulation(vertices, [[4, 6, 5], [6, 7, 5]]), # right
             mlhp.triangulation(vertices, [[0, 1, 4], [4, 1, 5]]), # front
             mlhp.triangulation(vertices, [[2, 3, 6], [6, 3, 7]]), # back
             mlhp.triangulation(vertices, [[0, 4, 2], [4, 6, 2]]), # bottom
             mlhp.triangulation(vertices, [[1, 5, 3], [5, 7, 3]])] # top

    # Transform computational domain to not be axis-aligned
    scale = mlhp.scaling([0.8, 0.9, 1.3])
    rotate = mlhp.rotation([3.0, 1.0, 2.0], 2.9)
    translate = mlhp.translation([-2.0, 3.2, 0.4])
    transformation = mlhp.concatenate([scale, rotate, translate])

    for i, face in enumerate(faces):
        face.transform(transformation)
        #face.writeVtu(f"outputs/beam_face_{i}.vtu")
        
    # Create mesh and finite element basis
    bounds = [t.boundingBox() for t in faces]

    bounds = [[min([b[0][axis] for b in bounds]) for axis in range(3)],
              [max([b[1][axis] for b in bounds]) for axis in range(3)]]

    lengths = [(1 + 2e-6) * (b - a) for a, b in zip(*bounds)]
    origin = [a - 1e-6 * (b - a) for a, b in zip(*bounds)]

    targetNElements = 100
    elementSize = (reduce(operator.mul, lengths) / targetNElements)**(1 / 3)
    nelements = [int(l / elementSize) + 1 for l in lengths]
    
    degree = 3
    epsilon = 1e-6
    
    mesh = mlhp.makeRefinedGrid(nelements, lengths, origin)
    basis = mlhp.makeHpTrunkSpace(mesh, degree=degree, nfields=3)

    #print(mesh)
    #print(basis)

    # Linear system allocation
    matrix = mlhp.allocateSparseMatrix(basis, symmetric=False)######################################3
    vector = mlhp.allocateRhsVector(matrix)

    #print(matrix, flush=True)

    # Domain quadrature
    E = mlhp.scalarField(3, 1.0)
    nu = mlhp.scalarField(3, 0.3)

    domain = mlhp.implicitTransformation(mlhp.implicitCube([0.0] * 3, [1.0] * 3), transformation)

    kinematics = mlhp.smallStrainKinematics(ndim=3)
    material = mlhp.isotropicElasticMaterial(E, nu)
    domainIntegrand = mlhp.staticDomainIntegrand(kinematics, material)
    
    #domainQuadrature = mlhp.spaceTreeQuadrature(domain, depth=degree + 2, epsilon=epsilon)
    domainQuadrature = mlhp.momentFittingQuadrature(domain, depth=3, epsilon=epsilon)

    mlhp.integrateOnDomain(basis, domainIntegrand, [matrix, vector], domainQuadrature)

    # Boundary quadrature
    surfaceQuadratures = [mlhp.simplexQuadrature(*mlhp.intersectWithMesh(face, mesh)) for face in faces]

    tractionFace, reactionFace = 5, 4

    # Fix all other faces
    for iface in [i for i in range(6) if i != tractionFace]:
        boundaryIntegrand0 = mlhp.l2NormalIntegrand(lhs=mlhp.scalarField(3, 1e6))
        mlhp.integrateOnSurface(basis, boundaryIntegrand0, [matrix], surfaceQuadratures[iface])
        
    # Impose traction right
    traction = faces[tractionFace].integrateNormalComponents()
    tractionNormSquared = reduce(operator.add, [x**2 for x in traction])
    traction = [x / tractionNormSquared for x in traction]

    boundaryIntegrand1 = mlhp.neumannIntegrand(mlhp.vectorField(3, traction))
    #boundaryIntegrand1 = mlhp.l2NormalIntegrand(rhs=mlhp.scalarField(3, tractionNormSquared**(1/2)))
    
    mlhp.integrateOnSurface(basis, boundaryIntegrand1, [vector], surfaceQuadratures[tractionFace])

    # Linear solution
    
    #import mklwrapper as mkl
    #solution = mkl.pardisoSolve(matrix, vector, symmetric=True)
    
    preconditioner = mlhp.additiveSchwarzPreconditioner(matrix, basis)
    
    solution, norms = mlhp.cg(matrix, vector, M=mlhp.linearOperator(preconditioner), residualNorms=True)
    
    #print(f"{len(norms) = }")

    # Reaction force computation method 1 (add entries of residual vector)
    one = mlhp.projectOnto(basis, mlhp.vectorField(3, [1] * basis.nfields()))
    res = mlhp.allocateRhsVector(matrix)

    support = []

    for ifield in range(3):
        supportIntegrand0 = mlhp.neumannIntegrand(mlhp.scalarField(3, 1.0), ifield)
        mlhp.integrateOnSurface(basis, supportIntegrand0, [res], surfaceQuadratures[reactionFace])
        support.append([i for i, r in enumerate(res) if r != 0.0])
        mlhp.fill(res, 0.0)

    residualIntegrand = mlhp.staticDomainIntegrand(kinematics, material, solution, computeTangent=False)

    mlhp.integrateOnDomain(basis, residualIntegrand, [res], domainQuadrature)

    reactionForce1 = [sum([res[i] * one[i] for i in ids]) for ids in support]

    # Reaction force computation method 2 (evaluate surface integral)
    reactionIntegrand = mlhp.reactionForceIntegrand(kinematics, material, solution)
    reactionForce2 = [mlhp.ScalarDouble(0.0) for _ in range(3)]
    
    mlhp.integrateOnSurface(basis, reactionIntegrand, reactionForce2, surfaceQuadratures[reactionFace])

    # Write output files
    postprocessors = [mlhp.solutionProcessor(3, solution), 
                      mlhp.functionProcessor(domain, "Domain"), 
                      mlhp.vonMisesProcessor(solution, kinematics, material)] 
                      
    cellmesh0 = mlhp.gridCellMesh([1, 1, 1], mlhp.PostprocessTopologies.Volumes)
    cellmesh1 = mlhp.boundaryCellMesh(resolution=[16] * 3, function=domain)

    mlhp.basisOutput(basis, cellmesh0, processors=postprocessors, output=mlhp.PVtuOutput("outputs/immersed_beam_mesh"))
    mlhp.basisOutput(basis, cellmesh1, processors=postprocessors, output=mlhp.PVtuOutput("outputs/immersed_beam_boundary"))

    return reactionForce1, [v.get() for v in reactionForce2]


class ImmersedBeamTest(unittest.TestCase):
    def test_beam(self):
        computedForce1, computedForce2 = computeImmersedBeam()
   
        #print(computedForce1, computedForce2)

        expectedForce1 = [0.9188900472824151, 0.051292405920671726, -0.3934466008426754]
        expectedForce2 = [0.9088664395517154, 0.0897414937122639, -0.40792079443694496]

        for expected1, computed1 in zip(expectedForce1, computedForce1):
            self.assertAlmostEqual(expected1, computed1, places=6)
    
        for expected2, computed2 in zip(expectedForce2, computedForce2):
            self.assertAlmostEqual(expected2, computed2)
    
