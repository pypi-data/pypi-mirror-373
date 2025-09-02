# This file is part of the mlhp project. License: See LICENSE

import mlhp
import unittest

def makeRefinement(position0, position1, time):
    sourcePosition = [(x1 - x0) * time + x0 for x0, x1 in zip(position0, position1)]
    
    refinement1Radii = [0.096, 0.048, 0.048]
    refinement2Radii = [0.052, 0.016, 0.016]

    center1 = [sourcePosition[0] - 0.6 * refinement1Radii[0]] + sourcePosition[1:]
    center2 = [sourcePosition[0] - 0.3 * refinement2Radii[0]] + sourcePosition[1:]
    
    domain1 = mlhp.implicitEllipsoid(center1, refinement1Radii)
    domain2 = mlhp.implicitEllipsoid(center2, refinement2Radii)
    
    refinement1 = mlhp.refineInsideDomain(domain1, 1)
    refinement2 = mlhp.refineInsideDomain(domain2, 2)
    
    return mlhp.refinementOr([refinement1, refinement2])
    
class LinearHeatTest (unittest.TestCase):
    def test_3D(self):
        
        D = 3
        theta = 0.5
        nsteps = 24
        
        lengths = [1.0, 0.4, 0.1]
        nelements = [10, 4, 1]
        degrees = [2, 2, 2]
        resolution = [2, 2, 2]
        
        duration = 1.0
        
        capacity = 1.0
        conductivity = 0.008
        sourceSigma = 0.02
        
        position0 = [0.2, lengths[1] / 2.0, lengths[2]]
        position1 = [0.8, lengths[1] / 2.0, lengths[2]]
        
        analytical = mlhp.makeAmLinearSolution(position0, position1, duration, 
            capacity, conductivity, sourceSigma, duration / 10.0, 0.0)
        
        initial = mlhp.scalarField(D, 0.0)
        
        dirichletSide = [i for i in range(2 * D - 1)]
        
        # Time integration
        grid0 = mlhp.makeRefinedGrid(nelements, lengths)
        grid0.refine(makeRefinement(position0, position1, 0.0))
        
        basis0 = mlhp.makeHpTrunkSpace(grid0, mlhp.LinearGrading(degrees))

        dofs0 = mlhp.projectOnto(basis0, initial)
        
        processors = [mlhp.solutionProcessor(D, dofs0, "Temperature"),
                      mlhp.functionProcessor(mlhp.sliceLast(analytical.solution, 0.0), "Analytical"),
                      mlhp.functionProcessor(mlhp.sliceLast(analytical.source, 0.0), "Source")]
                           
        postmesh = mlhp.gridCellMesh(resolution)
        output = mlhp.VtuOutput(f'outputs/linear_heat_{0}')
        
        mlhp.basisOutput(basis0, postmesh, output, processors)        
        
        dt = duration / nsteps
        ndof = 0
        integrals = [0.0, 0.0, 0.0]
        
        for istep in range(nsteps):
            time0, time1 = istep * dt, (istep + 1) * dt
            
            grid1 = mlhp.makeRefinedGrid(nelements, lengths)
            grid1.refine(makeRefinement(position0, position1, time1))
            
            basis1 = mlhp.makeHpTrunkSpace(grid1, mlhp.LinearGrading(degrees))

            print("Time step " + str(istep + 1) + " / " + str(nsteps) +
                  " (" + str(basis1.ndof()) + " number of unknowns)", flush=True)
               
            dirichlet = mlhp.integrateDirichletDofs(mlhp.sliceLast(
                analytical.solution, time1), basis1, dirichletSide)

            matrix = mlhp.allocateSparseMatrix(basis1, dirichlet[0])
            vector = mlhp.allocateRhsVector(matrix)
            
            integrand = mlhp.transientPoissonIntegrand(mlhp.scalarField(D + 1, capacity),
                mlhp.scalarField(D + 1, conductivity), analytical.source, dofs0, [time0, time1], theta)
                         
            mlhp.integrateOnDomain(basis0, basis1, integrand, [matrix, vector], dirichletDofs=dirichlet)
            
            dofs1 = mlhp.inflateDofs(mlhp.makeCGSolver()(matrix, vector), dirichlet)
            
            # Error integration (excluding initial condition         
            l2ErrorIntegrand = mlhp.l2ErrorIntegrand(dofs1, mlhp.sliceLast(analytical.solution, time1))
            l2Integrals = mlhp.makeScalars(3)
            
            mlhp.integrateOnDomain(basis1, l2ErrorIntegrand, l2Integrals)
            
            factor = dt if istep + 1 < nsteps else dt / 2.0
            
            integrals = [E + factor * Ec.get() for E, Ec in zip(integrals, l2Integrals)]
                     
            # Vtu postprocessing
            processors = [mlhp.solutionProcessor(D, dofs1, "Temperature"),
                          mlhp.functionProcessor(mlhp.sliceLast(analytical.solution, time1), "Analytical"),
                          mlhp.functionProcessor(mlhp.sliceLast(analytical.source, time1), "Source")]
            
            cellmesh = mlhp.gridCellMesh(resolution)
            output = mlhp.VtuOutput(f'outputs/linear_heat_{istep + 1}')
                
            mlhp.basisOutput(basis1, cellmesh, output, processors)             
            
            ndof += basis1.ndof()
            dofs0 = dofs1
            basis0 = basis1
        
        self.assertEqual(ndof, 33436)
        self.assertAlmostEqual(integrals[0], 2.7342053949**2, delta=1e-8)
        self.assertAlmostEqual(integrals[1], 2.7532175961**2, delta=1e-8)
        self.assertAlmostEqual(integrals[2], 0.0644606778**2, delta=1e-7)
        self.assertAlmostEqual(integrals[2] / integrals[1], 0.0234128526**2, delta=1e-7)
        
