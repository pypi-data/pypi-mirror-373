import csv
import os.path

from cmlibs.utils.zinc.field import create_field_finite_element, create_field_coordinates, find_or_create_field_group, find_or_create_field_stored_string
from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field
from cmlibs.zinc.status import OK as ZINC_OK

from cmlibs.importer.base import valid
from cmlibs.importer.errors import ImporterImportInvalidInputs, ImporterImportUnknownParameter, ImporterImportColonHRMError
from cmlibs.utils.zinc.general import ChangeManager


def import_data_into_region(region, inputs):
    if type(inputs) == list and len(inputs) == 1:
        inputs = inputs[0]

    if not valid(inputs, parameters("input")):
        raise ImporterImportInvalidInputs(f"Invalid input given to importer: {identifier()}")

    manometry_data = inputs
    field_module = region.getFieldmodule()

    # Determine times for time keeper.
    with open(manometry_data) as f:
        csv_reader = csv.reader(f, delimiter='\t')

        times = []
        try:
            for row in csv_reader:
                times.append(float(row[0]))
        except UnicodeDecodeError:
            raise ImporterImportColonHRMError("Colon HRM file is not valid.")
        except ValueError:
            raise ImporterImportColonHRMError("Colon HRM file is not valid.")

    with ChangeManager(field_module):
        with open(manometry_data) as f:
            csv_reader = csv.reader(f, delimiter='\t')
            first_row = True
            for row in csv_reader:
                time = float(row.pop(0))
                stimulation = float(row.pop(0))
                values = row[:]
                if first_row:
                    _setup_nodes(field_module, times, len(values))
                    first_row = False

                pressure_field = field_module.findFieldByName("pressure")
                stimulation_field = field_module.findFieldByName("stimulation")

                data_points = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
                for index, value in enumerate(values):
                    data_point = data_points.findNodeByIdentifier(index + 1)
                    field_cache = field_module.createFieldcache()
                    field_cache.setNode(data_point)
                    field_cache.setTime(time)
                    pressure_field.assignReal(field_cache, float(value))
                    stimulation_field.assignReal(field_cache, stimulation)


def import_data(inputs, output_directory):
    output = None
    context = Context("HRM")
    region = context.getDefaultRegion()

    import_data_into_region(region, inputs)

    # Inputs has already been validated by this point so it is safe to use.
    filename_parts = os.path.splitext(os.path.basename(inputs))
    output_exf = os.path.join(output_directory, filename_parts[0] + ".exf")
    result = region.writeFile(output_exf)
    if result == ZINC_OK:
        output = output_exf

    return output


def _setup_nodes(field_module, times, num_sensors):
    coordinate_field = create_field_coordinates(field_module)
    name_field = find_or_create_field_stored_string(field_module, "marker_name")
    pressure_field = create_field_finite_element(field_module, "pressure", 1, type_coordinate=False)
    stimulation_field = create_field_finite_element(field_module, "stimulation", 1, type_coordinate=False)
    data_points = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)

    data_template = data_points.createNodetemplate()
    data_template.defineField(coordinate_field)
    data_template.defineField(name_field)
    data_template.defineField(pressure_field)
    data_template.defineField(stimulation_field)

    group_field = find_or_create_field_group(field_module, "marker")
    nodeset_group = group_field.getOrCreateNodesetGroup(data_points)

    time_sequence = field_module.getMatchingTimesequence(times)

    data_template.setTimesequence(pressure_field, time_sequence)
    data_template.setTimesequence(stimulation_field, time_sequence)

    field_cache = field_module.createFieldcache()
    for index in range(num_sensors):
        pos = [index / (num_sensors - 1), 0.0, 0.0]
        node = data_points.createNode(-1, data_template)
        nodeset_group.addNode(node)
        field_cache.setNode(node)
        coordinate_field.assignReal(field_cache, pos)
        name_field.assignString(field_cache, f"Sensor {index + 1}")


def identifier():
    return "ColonHRM"


def parameters(parameter_name=None):
    importer_parameters = {
        "version": "0.1.0",
        "id": identifier(),
        "title": "Colon High Resolution Manometry",
        "description":
            "Colon high resolution manometry importer is for data listed in a tab separated values file."
            " The first column is time, the second column indicates if the stimulation has been applied, and"
            " any remaining columns are the values recorded from the sensors.",
        "input": {
            "mimetype": "text/tab-separated-values",
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
