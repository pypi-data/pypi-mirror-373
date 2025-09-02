import os.path
from pointpare import PointPare

import numpy as np
try:
    import trimesh
except ImportError:
    pass

from cmlibs.zinc.context import Context
from cmlibs.zinc.element import Element, Elementbasis
from cmlibs.zinc.field import Field
from cmlibs.zinc.status import OK as ZINC_OK

from cmlibs.importer.base import valid
from cmlibs.importer.errors import ImporterImportInvalidInputs
from cmlibs.utils.zinc.field import findOrCreateFieldCoordinates
from cmlibs.utils.zinc.finiteelement import createTriangleElements, create_nodes
from cmlibs.utils.zinc.general import ChangeManager


def base_import_data_into_region(region, inputs, identifier_fcn, parameters_fcn):
    if not valid(inputs, parameters_fcn("input")):
        raise ImporterImportInvalidInputs(f"Invalid input given to importer: {identifier_fcn()}")

    input_file = inputs

    mesh = trimesh.load(input_file)

    field_module = region.getFieldmodule()
    with ChangeManager(field_module):
        coordinates = findOrCreateFieldCoordinates(field_module)
        node_set = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)

        if isinstance(mesh, trimesh.Trimesh):
            create_nodes(coordinates, mesh.vertices.tolist(), node_set=node_set)
            mesh2d = field_module.findMeshByDimension(2)
            # Trimesh triangles are zero-based, Zinc is 1-based
            triangles = mesh.faces + 1
            createTriangleElements(mesh2d, coordinates, triangles.tolist())
        elif isinstance(mesh, trimesh.points.PointCloud):
            create_nodes(coordinates, mesh.vertices.tolist(), node_set_name="datapoints")
        else:
            stacked = [trimesh.util.stack_lines(e.discrete(mesh.vertices))
                       for e in mesh.entities]
            lines = trimesh.util.vstack_empty(stacked)
            # stack zeros for 2D lines
            is_2d_line = False
            if trimesh.util.is_shape(mesh.vertices, (-1, 2)):
                is_2d_line = True
                lines = lines.reshape((-1, 2))
                lines = np.column_stack((lines, np.zeros(len(lines))))

            lines_as_list = lines.tolist()

            pp = PointPare()
            pp.add_points(lines_as_list)
            pp.pare_points()

            create_nodes(coordinates, pp.get_pared_points(), node_set=node_set)

            zinc_mesh = field_module.findMeshByDimension(1)
            linear_basis = field_module.createElementbasis(1, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
            element_template = zinc_mesh.createElementtemplate()
            element_template.setElementShapeType(Element.SHAPE_TYPE_LINE)
            element_template.setNumberOfNodes(2)
            eft = zinc_mesh.createElementfieldtemplate(linear_basis)
            element_template.defineField(coordinates, -1, eft)
            p_dict = {}
            for index, point in enumerate(lines_as_list):
                p_dict[hash(tuple(point))] = index

            with ChangeManager(field_module):
                line_count = 0
                for index, s in enumerate(stacked):
                    new_line = []
                    for p in s:
                        p_as_list = p.tolist()
                        if is_2d_line:
                            p_as_list.append(0.0)

                        index = p_dict[hash(tuple(p_as_list))]
                        # Node indexing is zero-based, Zinc is one-based
                        new_line.append(pp.get_pared_index(index) + 1)

                    line_index = 0
                    while line_index < len(new_line):
                        element = zinc_mesh.createElement(-1, element_template)
                        element.setNodesByIdentifier(eft, [new_line[line_index], new_line[line_index + 1]])
                        line_index += 2

                    line_count += 1


def base_import_data(inputs, output_directory, identifier_fcn, parameters_fcn):
    context = Context(identifier_fcn())
    region = context.getDefaultRegion()

    base_import_data_into_region(region, inputs, identifier_fcn, parameters_fcn)

    # Inputs has already been validated by this point so it is safe to use.
    filename_parts = os.path.splitext(os.path.basename(inputs))
    output_exf = os.path.join(output_directory, filename_parts[0] + ".exf")
    result = region.writeFile(output_exf)

    output = None
    if result == ZINC_OK:
        output = output_exf

    return output
