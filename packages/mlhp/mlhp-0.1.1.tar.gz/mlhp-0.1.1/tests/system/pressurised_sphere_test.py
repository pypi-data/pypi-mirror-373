# This file is part of the mlhp project. License: See LICENSE

import mlhp, math
import unittest

class PressurizedSphereTest(unittest.TestCase):
    def test_elastic(self):
    
        D = 3
        
        # inner, outer, and plastic radii
        a, b, c = 0.1, 0.2, 0.1 
        
        youngsModulus = 200 * 1e9
        sigmaY = 200 * 1e6
        P = 2 * sigmaY * math.log(c / a) + 2 * sigmaY / 3 * ( 1 - c**3 / b**3 )
        
        # Domain setup
        inner = mlhp.implicitSphere( [0.0, 0.0, 0.0], a )
        outer = mlhp.implicitSphere( [0.0, 0.0, 0.0], b )
        
        domain = mlhp.implicitSubtraction([outer, inner])
        
        origin, max = [0.0] * D, [1.2 * b] * D
        lengths = [m - o for o, m in zip(origin, max)]
        
        # Discrtization setup
        nelements = [20] * D
        polynomialDegree = 1
        alphaFCM = 1e-5
        
        grid = mlhp.makeGrid(nelements, lengths, origin)
        grid = mlhp.makeFilteredGrid(grid, domain=domain, nseedpoints=polynomialDegree + 2)
        grid = mlhp.makeRefinedGrid(grid)
        
        basis = mlhp.makeHpTrunkSpace(grid, degree=polynomialDegree, nfields=D)

        # Constrain normal displacement on three sides
        face0 = mlhp.integrateDirichletDofs(mlhp.scalarField(D, 0.0), basis, [0 * 2], ifield=0)
        face1 = mlhp.integrateDirichletDofs(mlhp.scalarField(D, 0.0), basis, [1 * 2], ifield=1)
        face2 = mlhp.integrateDirichletDofs(mlhp.scalarField(D, 0.0), basis, [2 * 2], ifield=2)
    
        dirichlet = mlhp.combineDirichletDofs([face0, face1, face2])

        # Allocate sparse linear system
        matrix = mlhp.allocateSparseMatrix(basis, dirichlet[0])
        vector = mlhp.allocateRhsVector(matrix)

        # Recover inner boundary and impose pressure
        resolution = [polynomialDegree + 3] * D
        triangulation, celldata = mlhp.recoverDomainBoundary(grid, inner, resolution)

        quadrature = mlhp.simplexQuadrature(triangulation, celldata)
        integrand = mlhp.normalNeumannIntegrand(mlhp.scalarField(D, -P))

        mlhp.integrateOnSurface(basis, integrand, [vector], quadrature, dirichletDofs=dirichlet)
        
        # Assemble domain contributions
        E = mlhp.scalarField(D, youngsModulus)
        nu = mlhp.scalarField(D, 0.3)
        rhs = mlhp.vectorField(D, [0.0, 0.0, 0.0])

        kinematics = mlhp.smallStrainKinematics(D) 
        constitutive = mlhp.isotropicElasticMaterial(E, nu)
        integrand = mlhp.staticDomainIntegrand(kinematics, constitutive, rhs)

        quadrature = mlhp.spaceTreeQuadrature(domain, depth=polynomialDegree + 1, epsilon=alphaFCM)

        mlhp.integrateOnDomain(basis, integrand, [matrix, vector], quadrature=quadrature, dirichletDofs=dirichlet)

        # Solve linear system
        P = mlhp.diagonalPreconditioner(matrix)

        interiorDofs = mlhp.cg(matrix, vector, rtol=1e-12, M=P, maxiter=2000)

        dofs = mlhp.inflateDofs(interiorDofs, dirichlet)
        
        # Postprocess solution
        #gradient = mlhp.projectGradient(basis, dofs, quadrature)

        processors = [mlhp.solutionProcessor(D, dofs, "Displacement"),
        #              mlhp.vonMisesProcessor(gradient, kinematics, constitutive, "ProjVonMises"),
                      mlhp.vonMisesProcessor(dofs, kinematics, constitutive)]
        surfmesh = mlhp.boundaryCellMesh(domain, [5]*D)
        output = mlhp.PVtuOutput(filename="outputs/pressurized_sphere_surface")

        mlhp.basisOutput(basis, surfmesh, output, processors)
        
        self.assertEqual(len(dofs), 9876)
        self.assertAlmostEqual(mlhp.norm(dofs), 0.0015142966728928131, delta=1e-7)
        
