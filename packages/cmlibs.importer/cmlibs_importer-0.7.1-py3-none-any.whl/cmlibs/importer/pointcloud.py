import csv
import os.path

from cmlibs.utils.zinc.field import create_field_finite_element
from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field
from cmlibs.zinc.status import OK as ZINC_OK

from cmlibs.importer.base import valid
from cmlibs.importer.errors import ImporterImportInvalidInputs, ImporterImportUnknownParameter, ImporterImportPointCloudError
from cmlibs.utils.zinc.general import ChangeManager


def import_data_into_region(region, inputs):
    if isinstance(inputs, list) and len(inputs) == 1:
        inputs = inputs[0]

    if not valid(inputs, parameters("input")):
        raise ImporterImportInvalidInputs(f"Invalid input given to importer: {identifier()}")

    field_module = region.getFieldmodule()

    datapoint_field = None
    with ChangeManager(field_module):
        data_points = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        data_template = data_points.createNodetemplate()

        with open(inputs) as f:
            csv_reader = csv.reader(f)
            first_row = True
            try:
                for row in csv_reader:
                    if first_row:
                        first_row = False
                        if len(row) == 3:
                            try:
                                component_names = ["X", "Y", "Z"]
                                values = [float(r) for r in row]
                            except ValueError:
                                component_names = row
                                values = None
                        else:
                            raise ImporterImportPointCloudError("Point cloud data is invalid, expect three dimensional data.")

                        datapoint_field = create_field_finite_element(field_module, "coordinates", 3, type_coordinate=True, managed=True, component_names=component_names)
                        data_template.defineField(datapoint_field)
                        if values is not None:
                            node = data_points.createNode(-1, data_template)
                            _add_data_point(field_module, datapoint_field, node, values)
                    else:
                        if len(row) == 3:
                            try:
                                values = [float(r) for r in row]
                            except ValueError:
                                raise ImporterImportPointCloudError(f"Point cloud data has invalid row {row}.")
                            node = data_points.createNode(-1, data_template)
                            _add_data_point(field_module, datapoint_field, node, values)
                        else:
                            raise ImporterImportPointCloudError("Point cloud data is invalid, expect three dimensional data.")
            except UnicodeDecodeError:
                raise ImporterImportPointCloudError("Point cloud data file is not valid.")


def _add_data_point(field_module, datapoint_field, node, row):
    field_cache = field_module.createFieldcache()
    field_cache.setNode(node)
    datapoint_field.assignReal(field_cache, row)


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


def identifier():
    return "PointCloud"


def parameters(parameter_name=None):
    importer_parameters = {
        "version": "0.1.0",
        "id": identifier(),
        "title": "Point Cloud",
        "description":
            "Point cloud importer is for importing XYZ data stored in a comma separated file."
            " The first column is the X coordinate, the second column is the Y coordinate, the"
            " third column is the Z coordinate. The first row is an optional header row.",
        "input": {
            "mimetype": "text/csv",
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
