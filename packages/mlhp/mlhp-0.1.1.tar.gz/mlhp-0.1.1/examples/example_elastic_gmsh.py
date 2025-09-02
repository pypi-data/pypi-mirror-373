import mlhp 
import sys 
import numpy 
import gmshparser

assert(len(sys.argv) == 2)

print("1. Reading mesh", flush=True)

mesh = gmshparser.parse(sys.argv[1])

vertices = numpy.array([node.get_coordinates() for entity in mesh.get_node_entities() for node in entity.get_nodes()])
cells = [element.get_connectivity() for entity in mesh.get_element_entities() for element in entity.get_elements()]
types = numpy.array([entity.get_element_type() for entity in mesh.get_element_entities() for element in entity.get_elements()])

# Mesh is 3D
if numpy.any(types == 4) or numpy.any(types == 5):
    vertices = [vertex[:3] for vertex in vertices]
    # https://gmsh.info/dev/doc/texinfo/gmsh.pdf page 362/372
    hexes = [[cell[0], cell[1], cell[3], cell[2], cell[4], cell[5], cell[7], cell[6]]\
        for type, cell in zip(types, cells) if type == 5]
    cells = hexes + [cell for type, cell in zip(types, cells) if type == 4]
    
# Mesh is 2D
elif numpy.any(types == 2) or numpy.any(types == 3):
    vertices = [vertex[:2] for vertex in vertices]
    quads = [[cell[0], cell[1], cell[3], cell[2]] for type, cell in zip(types, cells) if type == 3]
    cells = quads + [cell for type, cell in zip(types, cells) if type == 2]
else:
    RuntimeError("Did not find 2- or 3D cubic or simplex elements")
    
offsets = numpy.cumsum([0] + [len(cell) for cell in cells])
cells = numpy.array([id for cell in cells for id in cell]) - 1

print("2. Setting up mesh and basis", flush=True)

mesh = mlhp.makeUnstructuredMesh(vertices, cells, offsets)

ndim = mesh.ndim
nfields = ndim

basis = mlhp.makeUnstructuredBasis(mesh, nfields)

print(mesh)
print(basis)

print("3. Computing dirichlet boundary conditions", flush=True)

dirichlet = mlhp.integrateDirichletDofs(mlhp.vectorField(ndim, [0.0] * nfields), basis, [0])

print("4. Setting up physics", flush=True)

E = mlhp.scalarField(ndim, 200 * 1e9)
nu = mlhp.scalarField(ndim, 0.3)
rhs = mlhp.vectorField(ndim, [0.0] * (ndim - 1) + [-1.0])

if ndim == 3:
    constitutive = mlhp.isotropicElasticMaterial(E, nu)
if ndim == 2:
    constitutive = mlhp.planeStressMaterial(E, nu)

kinematics = mlhp.smallStrainKinematics(ndim) 
integrand = mlhp.staticDomainIntegrand(kinematics, constitutive, rhs)

print("5. Allocating linear system", flush=True)

matrix = mlhp.allocateSparseMatrix(basis, dirichlet[0])
vector = mlhp.allocateRhsVector(matrix)

print("6. Integrating linear system", flush=True)

mlhp.integrateOnDomain(basis, integrand, [matrix, vector], 
    dirichletDofs=dirichlet)

print("7. Solving linear system", flush=True)

P = mlhp.diagonalPreconditioner(matrix)

interiorDofs, norms = mlhp.cg(matrix, vector, M=P, maxiter=5000, residualNorms=True)

allDofs = mlhp.inflateDofs(interiorDofs, dirichlet)

print("8. Postprocessing solution", flush=True)

processors = [mlhp.solutionProcessor(ndim, allDofs, "Displacement"),
              mlhp.vonMisesProcessor(allDofs, kinematics, constitutive)]

postmesh = mlhp.gridCellMesh([1] * ndim)
output = mlhp.PVtuOutput(filename="outputs/example_gmsh")
            
mlhp.basisOutput(basis, postmesh, output, processors)
