import csv
import os.path
import shlex

from cmlibs.utils.zinc.field import create_field_finite_element, find_or_create_field_group
from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field
from cmlibs.zinc.status import OK as ZINC_OK

from cmlibs.importer.base import valid
from cmlibs.importer.errors import ImporterImportInvalidInputs, ImporterImportUnknownParameter, ImporterImportXYZError
from cmlibs.utils.zinc.general import ChangeManager


def identifier():
    return "XYZ"


def import_data_into_region(region, inputs):
    if isinstance(inputs, list) and len(inputs) == 1:
        inputs = inputs[0]

    if not valid(inputs, parameters("input")):
        raise ImporterImportInvalidInputs(f"Invalid input given to importer: {identifier()}")

    field_module = region.getFieldmodule()
    component_names = ["X", "Y", "Z"]

    with ChangeManager(field_module):
        data_points = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        data_template = data_points.createNodetemplate()

        datapoint_field = create_field_finite_element(field_module, "coordinates", 3, type_coordinate=True, managed=True,
                                                      component_names=component_names)
        data_template.defineField(datapoint_field)

        points_by_group, legend = _read_input_file(inputs)
        for group_id, points in points_by_group.items():
            if group_id is None:
                group_name = "Ungrouped"
            else:
                group_name = legend.get(group_id, f"Group {group_id}")

            group_field = find_or_create_field_group(field_module, group_name)
            data_points_group = group_field.getOrCreateNodesetGroup(data_points)

            for point in points:
                node = data_points.createNode(-1, data_template)
                _add_data_point(field_module, datapoint_field, node, list(point))
                data_points_group.addNode(node)


def import_data(inputs, output_directory):
    output = None
    context = Context(identifier())
    region = context.getDefaultRegion()

    import_data_into_region(region, inputs)

    # Inputs has already been validated by this point so it is safe to use.
    filename_parts = os.path.splitext(os.path.basename(inputs))
    output_exf = os.path.join(output_directory, filename_parts[0] + ".exf")
    result = region.writeFile(output_exf)
    if result == ZINC_OK:
        output = output_exf

    return output


def parameters(parameter_name=None):
    importer_parameters = {
        "version": "0.1.0",
        "id": identifier(),
        "title": "XYZ List of Points",
        "description":
            """
            XYZ importer is for importing XYZ data stored in space separated columns.
            The first column is the X coordinate, the second column is the Y coordinate, the
            third column is the Z coordinate.
            The '#' character can be used to indicate a comment, any text after the '#' will be ignored.
            The XYZ data can have an additional column to define the group the point belongs to, in which case the
            fourth column is a natural number.
            The group natural number can be defined in the legend section of the file.
            The legend section has only two columns, the first column is the group natural number
            and anything after the group number is the group name.
            """,
        "input": {
            "mimetype": "text/plain",
        },
        "output": {
            "mimetype": "text/x.vnd.abi.exf+plain",
        }
    }

    if parameter_name is not None:
        if parameter_name in importer_parameters:
            return importer_parameters[parameter_name]
        else:
            raise ImporterImportUnknownParameter(f"Importer '{identifier()}' does not have parameter: {parameter_name}")

    return importer_parameters


def _add_data_point(field_module, datapoint_field, node, row):
    field_cache = field_module.createFieldcache()
    field_cache.setNode(node)
    datapoint_field.assignReal(field_cache, row)


def _read_input_file(inputs):
    points_by_group = {}
    legend = {}

    with open(inputs) as f:
        try:
            lines = f.readlines()
        except UnicodeDecodeError:
            raise ImporterImportXYZError("Point cloud data file is not valid.")
        for line in lines:
            split_line = line.split('#', 1)
            line = split_line[0].strip()
            if not line:
                continue  # Skip empty lines and comments.

            parts = shlex.split(line)
            if _is_legend_line(parts):  # Legend entry
                group_number = int(parts[0])
                group_name = ' '.join(parts[1:])
                legend[group_number] = group_name
            elif len(parts) == 3 or len(parts) == 4:  # Point data
                try:
                    x, y, z = map(float, parts[:3])
                    group_number = int(parts[3]) if len(parts) == 4 else None
                    if group_number not in points_by_group:
                        points_by_group[group_number] = []
                    points_by_group[group_number].append((x, y, z))
                except ValueError:
                    raise ImporterImportXYZError(f"Invalid point data: {parts}")

    return points_by_group, legend


def _is_legend_line(parts):
    """
    Check if the line is a legend entry.
    A legend entry has at least two parts: a group number and a group name.
    """
    return len(parts) == 2 and parts[0].isdigit() and int(parts[0]) > 0 and ' '.join(parts[1:]).strip()
