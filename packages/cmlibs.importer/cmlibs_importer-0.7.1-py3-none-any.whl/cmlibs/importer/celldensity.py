import csv
import os.path

from cmlibs.utils.zinc.field import create_field_finite_element, find_or_create_field_group
from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field
from cmlibs.zinc.status import OK as ZINC_OK

from cmlibs.importer.base import valid
from cmlibs.importer.errors import ImporterImportInvalidInputs, ImporterImportUnknownParameter, ImporterImportCellDensityError
from cmlibs.utils.zinc.general import ChangeManager


def import_data_into_region(region, inputs):
    if type(inputs) == list and len(inputs) == 1:
        inputs = inputs[0]

    if not valid(inputs, parameters("input")):
        raise ImporterImportInvalidInputs(f"Invalid input given to importer: {identifier()}")

    cell_density_data = {}

    with open(inputs) as f:
        csv_reader = csv.reader(f)
        first_row = True
        try:
            for row in csv_reader:
                if first_row:
                    first_row = False
                    # Remove Cell type column
                    row.pop(0)
                    cell_density_data["group_names"] = row[:]
                    cell_density_data["cell_types"] = []
                    cell_density_data["cell_densities"] = []
                else:
                    cell_density_data["cell_types"].append(row.pop(0))
                    cell_density_data["cell_densities"].append([float(r) for r in row])
        except UnicodeDecodeError:
            raise ImporterImportCellDensityError("Cell density file is not valid.")

    if len(cell_density_data["group_names"]) == 0:
        raise ImporterImportCellDensityError("Cell density file is not valid.")

    # Transpose the cell densities.
    transposed_tuples = list(zip(*cell_density_data["cell_densities"]))
    cell_density_data["cell_densities"] = [list(sublist) for sublist in transposed_tuples]

    field_module = region.getFieldmodule()

    with ChangeManager(field_module):
        data_points = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        data_template = data_points.createNodetemplate()
        # cell_type_fields = []
        for cell_type in cell_density_data["cell_types"]:
            field = create_field_finite_element(field_module, cell_type, 1, type_coordinate=False, managed=True, component_names=["density"])
            data_template.defineField(field)

        for group_index, group_name in enumerate(cell_density_data["group_names"]):
            group_field = find_or_create_field_group(field_module, group_name)
            data_points_group = group_field.getOrCreateNodesetGroup(data_points)

            field_cache = field_module.createFieldcache()
            node = data_points.createNode(-1, data_template)
            data_points_group.addNode(node)
            field_cache.setNode(node)

            cell_densities = cell_density_data["cell_densities"][group_index]
            for cell_index, cell_type in enumerate(cell_density_data["cell_types"]):
                field = field_module.findFieldByName(cell_type)
                field.assignReal(field_cache, cell_densities[cell_index])


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


def _setup_nodes(field_module):
    cell_density_field = create_field_finite_element(field_module, "cell_density", 1, type_coordinate=False)
    data_points = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)

    data_template = data_points.createNodetemplate()
    data_template.defineField(cell_density_field)


def identifier():
    return "CellDensity"


def parameters(parameter_name=None):
    importer_parameters = {
        "version": "0.1.0",
        "id": identifier(),
        "title": "Cell Density",
        "description":
            "Cell density importer is for data stored in a comma separated file."
            " The first column is the cell type, the second column indicates the region the density values"
            " apply to and the density values for the corresponding cell type given in column one.",
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
