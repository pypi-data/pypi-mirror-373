import os.path

from mbfxml2ex.app import read_xml
from mbfxml2ex.exceptions import MBFXMLFormat
from mbfxml2ex.zinc import load

from cmlibs.zinc.context import Context
from cmlibs.zinc.status import OK as ZINC_OK

from cmlibs.importer.base import valid
from cmlibs.importer.errors import ImporterImportInvalidInputs, ImporterImportUnknownParameter, ImporterImportMBFXMLError
from cmlibs.utils.zinc.general import ChangeManager


def import_data_into_region(region, inputs):
    if not valid(inputs, parameters("input")):
        raise ImporterImportInvalidInputs(f"Invalid input given to importer: {identifier()}")

    xml_file = inputs

    try:
        contents = read_xml(xml_file)
    except MBFXMLFormat:
        raise ImporterImportMBFXMLError("Given file is not a valid MBF XML file.")

    field_module = region.getFieldmodule()

    with ChangeManager(field_module):
        load(region, contents, None)


def import_data(inputs, output_directory):
    context = Context(identifier())
    region = context.getDefaultRegion()

    import_data_into_region(region, inputs)

    # Inputs has already been validated by this point so it is safe to use.
    filename_parts = os.path.splitext(os.path.basename(inputs))
    output_exf = os.path.join(output_directory, filename_parts[0] + ".exf")
    result = region.writeFile(output_exf)

    output = None
    if result == ZINC_OK:
        output = output_exf

    return output


def identifier():
    return "MBFXML"


def parameters(parameter_name=None):
    importer_parameters = {
        "version": "0.1.0",
        "id": identifier(),
        "title": "MBF Bioscience XML",
        "description":
            "MBF Bioscience XML is a file format produced by several MBF software products."
            " The specification for the MBF XML data is available here: https://neuromorphological-file-specification.readthedocs.io/en/latest/NMF.html.",
        "input": {
            "mimetype": "application/vnd.mbfbioscience.metadata+xml",
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
