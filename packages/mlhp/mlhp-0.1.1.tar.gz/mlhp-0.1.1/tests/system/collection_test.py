# This file is part of the mlhp project. License: See LICENSE

import mlhp
import unittest
import math
import random

class CollectionTest(unittest.TestCase):
    def test_integrateScalarFunction2D(self):
        D = 2
        radius = 0.8
        order = 2

        domain = mlhp.implicitSphere([0.0] * D, radius)
        mesh = mlhp.makeGrid([axis + 3 for axis in range(D)], [2] * D, [-1] * D)
        basis = mlhp.makeDummyBasis(mesh)
        target = mlhp.ScalarDouble()

        quadratureOrder = mlhp.relativeQuadratureOrder(D, order)
        quadratureScheme = mlhp.momentFittingQuadrature(domain, depth=5, epsilon=0.0)
        #quadratureScheme = mlhp.spaceTreeQuadrature(domain, depth=5, epsilon=0.0)
        
        integrand = mlhp.functionIntegrand(mlhp.scalarField(D, 1.0))
        
        mlhp.integrateOnDomain(basis, integrand, [target], quadrature=quadratureScheme, orderDeterminor=quadratureOrder)

        expected = math.pi**(D / 2) / math.gamma(D / 2 + 1) * radius**D
        error = abs(expected - target.get()) / expected
        
        #print(error)
        
        self.assertAlmostEqual(error, 0.0007483838265199594, places=6)
        
    def test_integrateVectorFunction3D(self):
        D = 3
        radius = 0.83
        order = 2

        domain = mlhp.implicitSphere([0.0] * D, radius)
        
        r = "((x**2 + y**2 + z**2)**(1/2))"
        
        f0 = f"-2 * {r}**3 + 3 * {r}**2 + 1"
        f1 = f"4 * (1 - {r}**2)"
        
        function = mlhp.vectorField(D, f"[{f0}, {f1}]")
        
        mesh = mlhp.makeGrid([6 - axis for axis in range(D)], [2] * D, [-1] * D)
        basis = mlhp.makeDummyBasis(mesh)
        targets = [mlhp.ScalarDouble() for _ in range(2)]

        #meshcreator = mlhp.domainCellMesh(function=domain, resolution=[4] * D, coarsen=True, meshBothSides=False)
        #quadratureScheme = mlhp.cellMeshQuadrature(meshcreator)
        #quadratureScheme = mlhp.momentFittingQuadrature(domain, depth=3, epsilon=0.0)
        quadratureScheme = mlhp.spaceTreeQuadrature(domain, depth=4, epsilon=0.0)
        
        quadratureOrder = mlhp.relativeQuadratureOrder(D, order)
        integrand = mlhp.functionIntegrand(function)
        
        mlhp.integrateOnDomain(basis, integrand, targets, quadrature=quadratureScheme, orderDeterminor=quadratureOrder)
        
        result = [target.get() for target in targets]
        
        expected0 = 4 * math.pi * (-2/6 * radius**6 + 3/5 * radius**5 + 1/3 * radius**3)
        expected1 = 16 * math.pi * (radius**3 / 3 - radius**5 / 5)
        
        error0 = abs(expected0 - targets[0].get()) / expected0
        error1 = abs(expected1 - targets[1].get()) / expected1
        
        #print(error0, error1)
        
        self.assertAlmostEqual(error0, 3.404156148046146e-05, places=6)
        self.assertAlmostEqual(error1, 5.345606556139261e-06, places=6)
        
        # Integral in spherical coordinates:
        # int_rho(0, 2*pi) int_phi(0, pi) int_r(0, R)  f * r**2 * sin(phi) * dr * dphi * drho
        #
        # f = f1: int_rho(0, 2*pi) int_phi(0, pi) int_r(0, R) (-2 * r**3 + 3 * r**2 + 1) * r**2 * sin(phi) * dr * dphi * drho =
        #         int_rho(0, 2*pi) int_phi(0, pi) (-2/6 * R**6 + 3/5 * R**5 + 1/3 * R**3) * [-cos(phi)](0, pi) * drho =
        #         int_rho(0, 2*pi) 2 * (-2/6 * R**6 + 3/5 * R**5 + 1/3 * R**3) * drho =
        #         4*pi * (-2/6 * R**6 + 3/5 * R**5 + 1/3 * R**3)
        #      
        # f = f2: int_rho(0, 2*pi) int_phi(0, pi) int_r(0, R) 4 * (1 - r**2) * r**2 * sin(phi) * dr * dphi * drho =
        #         int_rho(0, 2*pi) int_phi(0, pi) 4/3 * R**3 - 4/5 * R**5 * sin(phi) * dphi * drho =
        #         16 * pi * (R**3 / 3 - R**5 / 5)
        
        
    def test_integrateVolume(self):
        D = 3
        
        # Create domain by composing scalar fields for testing purposes
        sphere = mlhp.scalarField(D, f"x**2 + y**2 + z**2")
        
        sphere1 = mlhp.scalarField(D, f"f0(x - 1.0, y - 2.0, z + 0.1) < {0.5**2}", fields=[sphere]) 
        sphere2 = mlhp.scalarField(D, f"f0(x - 2.0, y - 1.0, z - 0.2) < {0.4**2}", fields=[sphere]) 
        sphere3 = mlhp.scalarField(D, f"f0(x - 1.5, y - 1.0, z - 1.5) < {0.6**2}", fields=[sphere]) 
        spheres = [sphere1, sphere2, sphere3]
        
        domain = mlhp.implicitFunction(D, "f0(x, y, z) + f1(x, y, z) + f2(x, y, z)", fields=spheres)
        
        expectedVolume = 4/3 * math.pi * (0.5**3 + 0.4**3 + 0.6**3)
        expectedArea = 4 * math.pi * (0.5**2 + 0.4**2 + 0.6**2)
        
        # Create mesh and triangulate domain
        mesh = mlhp.makeGrid([12, 11, 13], lengths=[1.9, 2.1, 2.7], origin=[0.5, 0.4, -0.6])
        basis = mlhp.makeDummyBasis(mesh)
        
        resolution = [7, 9, 8]
        triangles, celldata = mlhp.recoverDomainBoundary(mesh, domain, resolution)
        
        totalVolume = 1.9 * 2.1 * 2.7
        
        # Integrate volume of the entire domain first (inside + outside)
        meshcreator = mlhp.domainCellMesh(function=domain, 
            resolution=resolution, coarsen=True, meshBothSides=True)
        quadratureScheme = mlhp.cellMeshQuadrature(meshcreator)
        order = mlhp.absoluteQuadratureOrder([2]*D)
            
        integrand = mlhp.functionIntegrand(mlhp.scalarField(D, 1.0))
        computedVolume1 = mlhp.ScalarDouble(0.0)
        mlhp.integrateOnDomain(basis, integrand, [computedVolume1], quadrature=quadratureScheme, orderDeterminor=order)
        
        self.assertLess(abs(computedVolume1.get() - totalVolume) / totalVolume, 1e-13) 
        
        # Integrate volume through volume integral
        meshcreator = mlhp.domainCellMesh(function=domain, 
            resolution=resolution, coarsen=True, meshBothSides=False)
        quadratureScheme = mlhp.cellMeshQuadrature(meshcreator)
        order = mlhp.absoluteQuadratureOrder([2]*D)
            
        integrand = mlhp.functionIntegrand(mlhp.scalarField(D, 1.0))
        computedVolume2 = mlhp.ScalarDouble(0.0)
        mlhp.integrateOnDomain(basis, integrand, [computedVolume2], quadrature=quadratureScheme, orderDeterminor=order)
        
        self.assertAlmostEqual(computedVolume2.get(), expectedVolume, places=2)
        
        # Integrate area through scalar function surface integrand
        quadrature = mlhp.simplexQuadrature(triangles, celldata, order=order)
        integrand = mlhp.functionSurfaceIntegrand(mlhp.scalarField(3, 1.0))
        computedArea1 = mlhp.ScalarDouble(0.0)
        mlhp.integrateOnSurface(basis, integrand, [computedArea1], quadrature)
        
        self.assertAlmostEqual(computedArea1.get(), expectedArea, places=2)
        
        # Integrate area through vector function surface integrand
        quadrature = mlhp.simplexQuadrature(triangles, celldata)
        integrand = mlhp.functionSurfaceIntegrand(mlhp.vectorField(3, [2.0, 3.0]))
        computedArea2 = mlhp.makeScalars(2)
        mlhp.integrateOnSurface(basis, integrand, computedArea2, quadrature)
        
        self.assertAlmostEqual(computedArea2[0].get() / 2, expectedArea, places=2)
        self.assertAlmostEqual(computedArea2[1].get() / 3, expectedArea, places=2)
        
        # Integrate volume through dot product surface integrand (integrates dot(f, n))
        quadrature = mlhp.simplexQuadrature(triangles, celldata)
        integrand = mlhp.normalDotProductIntegrand(mlhp.vectorField(3, f"[x / {D}, y / {D}, z / {D}]"))
        computedVolume3 = mlhp.ScalarDouble(0.0)
        mlhp.integrateOnSurface(basis, integrand, [computedVolume3], quadrature)
        
        self.assertAlmostEqual(computedVolume3.get(), expectedVolume, places=2)
        self.assertLess(abs(computedVolume3.get() - computedVolume2.get()) / totalVolume, 1e-13)
        
        ## Write vtu files
        #postmesh1 = mlhp.associatedTrianglesCellMesh(triangles, celldata)
        #writer1 = mlhp.VtuOutput("outputs/collection_integratevolume_surface.vtu")
        #mlhp.writeMeshOutput(mesh, postmesh=postmesh1, writer=writer1)
        #
        #writer2 = mlhp.VtuOutput("outputs/collection_integratevolume_volume.vtu")
        #mlhp.writeMeshOutput(mesh, postmesh=meshcreator, writer=writer2)


    def test_integrateArea(self):
        D = 2
        
        # Create domain 
        circles = []
        random.seed(0)
        for i in range(10):
            for j in range(10):
                x = (i + 0.5 + 0.05 * random.random()) / 10.0
                y = (j + 0.5 + 0.05 * random.random()) / 10.0
                r = 0.04 + 0.03 * random.random()
                circles.append(mlhp.implicitSphere([x, y], r))
        union = mlhp.implicitUnion(circles)
        vertices = [((1 + math.cos(phi))/2, (1 + math.sin(phi))/2) for phi in [math.pi * (i/4 + 1/8) for i in range(8)]]
        segments = mlhp.lineSegments(vertices, list(zip(range(7), range(1, 8))) + [(len(vertices) - 1, 0)])
        domain = mlhp.implicitIntersection([mlhp.rayIntersectionDomain(segments), union])
       
        # Recover domain boundary
        resolution = [5, 3]
        expectedArea = 0.6479340628351379
        
        mesh = mlhp.makeRefinedGrid([13, 17])
        basis = mlhp.makeDummyBasis(mesh)
        
        segments, celldata = mlhp.recoverDomainBoundary(mesh, domain, resolution)
                
        # Integrate area through dot product boundary integrand 
        quadrature = mlhp.simplexQuadrature(segments, celldata)
        boundaryIntegrand = mlhp.normalDotProductIntegrand(mlhp.vectorField(2, f"[x / {D}, y / {D}]"))
        computedArea1 = mlhp.ScalarDouble(0.0)
        mlhp.integrateOnSurface(basis, boundaryIntegrand, [computedArea1], quadrature)
        
        self.assertAlmostEqual(computedArea1.get(), expectedArea, places=13)
        
        # Integrate area through area integral
        meshcreator2 = mlhp.domainCellMesh(function=domain, 
            resolution=resolution, coarsen=True, meshBothSides=False)
        quadratureScheme = mlhp.cellMeshQuadrature(meshcreator2)
        volumeOrder = mlhp.absoluteQuadratureOrder([2]*D)
            
        volumeIntegrand = mlhp.functionIntegrand(mlhp.scalarField(D, 1.0))
        computedArea2 = mlhp.ScalarDouble(0.0)
        mlhp.integrateOnDomain(basis, volumeIntegrand, [computedArea2], 
            quadrature=quadratureScheme, orderDeterminor=volumeOrder)
        
        self.assertAlmostEqual(computedArea2.get(), expectedArea, places=13)
        
        # Check if we recover the mesh area when we mesh both sides (inside and outside)
        meshcreator3 = mlhp.domainCellMesh(function=domain, 
            resolution=resolution, coarsen=True, meshBothSides=True)
        quadratureScheme = mlhp.cellMeshQuadrature(meshcreator3)
            
        computedArea3 = mlhp.ScalarDouble(0.0)
        mlhp.integrateOnDomain(basis, volumeIntegrand, [computedArea3], 
            quadrature=quadratureScheme, orderDeterminor=volumeOrder)
        
        self.assertLess(abs(computedArea3.get() - 1.0), 1e-13) 
        
        # import matplotlib.pyplot as plt
        # output = mlhp.dataAccumulator()
        # mlhp.meshOutput(mesh=mesh, cellmesh=meshcreator2, output=output)
        # plt.triplot(output.triangulation())
        # segments.plot(color="red")
