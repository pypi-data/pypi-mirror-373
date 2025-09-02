from cmlibs.importer.errors import ImporterImportUnknownParameter

try:
    from cmlibs.importer.trimesh import base_import_data, base_import_data_into_region
except ImportError:
    base_import_data = None
    base_import_data_into_region = None


if base_import_data_into_region is not None:
    def import_data_into_region(region, inputs):
        base_import_data_into_region(region, inputs, identifier, parameters)

if base_import_data is not None:
    def import_data(inputs, output_directory):
        return base_import_data(inputs, output_directory, identifier, parameters)


def identifier():
    return "SVG"


def parameters(parameter_name=None):
    importer_parameters = {
        "version": "0.1.0",
        "id": identifier(),
        "title": "SVG",
        "description":
            "SVG image file format.",
        "input": {
            "mimetype": "image/svg+xml",
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


