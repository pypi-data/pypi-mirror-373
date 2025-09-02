import csv
import os.path

from mbfxml2ex.app import read_xml
from mbfxml2ex.exceptions import MBFXMLFormat
from mbfxml2ex.zinc import load

from cmlibs.utils.zinc.field import create_field_finite_element
from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field
from cmlibs.zinc.status import OK as ZINC_OK

from cmlibs.importer.base import valid
from cmlibs.importer.errors import ImporterImportMBFXMLError, ImporterImportGeneFileError, ImporterImportInvalidInputs, ImporterImportUnknownParameter
from cmlibs.utils.zinc.general import ChangeManager


def import_data_into_region(region, inputs):
    if not valid(inputs, parameters("inputs")):
        raise ImporterImportInvalidInputs(f"Invalid inputs given to importer: {identifier()}")

    marker_file = inputs[0]
    gene_data_file = inputs[1]

    try:
        contents = read_xml(marker_file)
    except MBFXMLFormat:
        raise ImporterImportMBFXMLError("Marker file is not a valid MBF XML file.")

    field_module = region.getFieldmodule()

    with ChangeManager(field_module):
        load(region, contents, None)

        with open(gene_data_file) as f:
            csv_reader = csv.DictReader(f)

            try:
                for row in csv_reader:
                    gene = row[""]
                    del row[""]

                    gene_field = create_field_finite_element(field_module, gene, 1, type_coordinate=False)
                    data_points = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
                    data_template = data_points.createNodetemplate()
                    data_template.defineField(gene_field)

                    point_iter = data_points.createNodeiterator()
                    data_point = point_iter.next()
                    while data_point.isValid():
                        field_cache = field_module.createFieldcache()
                        field_cache.setNode(data_point)
                        marker = field_module.findFieldByName("marker_name")
                        cell_name = marker.evaluateString(field_cache)

                        try:
                            gene_expression_value = float(row[cell_name])
                            data_point.merge(data_template)
                            gene_field.assignReal(field_cache, gene_expression_value)
                        except ValueError:
                            pass

                        data_point = point_iter.next()
            except UnicodeDecodeError:
                raise ImporterImportGeneFileError("Gene CSV file not valid.")


def import_data(inputs, output_directory):
    output = None
    context = Context("Gene")
    region = context.getDefaultRegion()

    import_data_into_region(region, inputs)

    # Inputs has already been validated by this point so it is safe to use.
    filename_parts = os.path.splitext(os.path.basename(inputs[0]))
    output_exf = os.path.join(output_directory, filename_parts[0] + ".exf")
    result = region.writeFile(output_exf)
    if result == ZINC_OK:
        output = output_exf

    return output


def identifier():
    return "RAGPData"


def parameters(parameter_name=None):
    importer_parameters = {
        "version": "0.1.0",
        "id": identifier(),
        "title": "RAGP Neuron Gene Sampling",
        "description":
            "Right Atrial Ganglionated Plexus (RAGP) neuron gene sampling importer is for gene data spread across two files."
            " The first file is an MBF XML file containing the marker coordinates and marker name."
            " The second file is a comma separated value file containing the gene name, marker name, value matrix.",
        "inputs": [
            {
                "mimetype": "application/vnd.mbfbioscience.metadata+xml",
            },
            {
                "mimetype": "text/x.vnd.sparc.gene-v-sample+csv",
            }
        ],
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
