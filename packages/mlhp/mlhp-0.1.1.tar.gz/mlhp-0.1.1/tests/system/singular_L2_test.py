# This file is part of the mlhp project. License: See LICENSE

import mlhp
import unittest

def compute(D, refinementDepth):

    analytical = mlhp.makeSingularSolution(D).solution

    # Domain and discretization
    nelements = [4] * D
    lengths = [1.0] * D

    sphere = mlhp.implicitSphere([0.0] * D, 0.0)
    strategy = mlhp.refineTowardsBoundary(sphere, refinementDepth)

    grid = mlhp.makeRefinedGrid(nelements, lengths)
    grid.refine(strategy)

    basis = mlhp.makeHpTrunkSpace(grid, mlhp.LinearGrading(1))

    # Compute indices and values for dirichlet boundary condition
    dofs = mlhp.projectOnto(basis, analytical)
    
    # Vtk Postprocessing
    processors = [mlhp.solutionProcessor(D, dofs),
                  mlhp.functionProcessor(analytical, "Analytical")]

    cellmesh = mlhp.gridCellMesh([refinementDepth + 1] * D)
    output = mlhp.VtuOutput(f'outputs/singular_L2_{D}D_{refinementDepth}')
            
    mlhp.basisOutput(basis, cellmesh, output, processors)
        
    # Error computation
    l2ErrorIntegrand = mlhp.l2ErrorIntegrand(dofs, analytical)
    l2Integrals = mlhp.makeScalars(3)
    
    mlhp.integrateOnDomain(basis, l2ErrorIntegrand, l2Integrals)
                               
    # Return number of dofs and || u_fe - u_ex ||^2 
    return [ len(dofs), l2Integrals[2].get() ]
    
class SingularL2Test (unittest.TestCase):
    
    def computeStudy(self, D, expected, tol):
        expectedNDofs, expectedL2 = expected
        
        for iStudy, expectedNDof in enumerate(expectedNDofs):
            computedNDof, computedL2 = compute(D, iStudy)
            
            self.assertEqual(computedNDof, expectedNDof)
            self.assertAlmostEqual(computedL2, expectedL2[iStudy], delta=tol)
        
    def test_1D(self):
    
        expectedNDof = [5, 9, 14, 20, 27]
        l2 = [3.08705e-06, 6.21486e-07, 1.25989e-07, 2.55838e-08, 5.19513e-09]

        self.computeStudy(1, [expectedNDof, l2], 1e-10)
             
    def test_2D(self):
    
        expectedNDof = [25, 66, 113, 181, 273]
        l2 = [1.42219e-06, 1.2541e-06, 1.67571e-07, 2.11436e-08, 2.68362e-09]

        self.computeStudy(2, [expectedNDof, l2], 1e-10)
             
    def test_3D(self):
    
        expectedNDof = [125, 429, 754, 1337]
        l2 = [7.35596e-07, 2.28911e-07, 1.66542e-08, 1.27925e-09]

        self.computeStudy(3, [expectedNDof, l2], 1e-10)
     
