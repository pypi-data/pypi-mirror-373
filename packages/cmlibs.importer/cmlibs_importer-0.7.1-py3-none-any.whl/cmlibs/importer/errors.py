
class ImporterImportError(Exception):
    pass


class ImporterImportInvalidInputs(ImporterImportError):
    pass


class ImporterImportUnknownParameter(ImporterImportError):
    pass


class ImporterImportMBFXMLError(ImporterImportError):
    pass


class ImporterImportFileNotFoundError(ImporterImportError):
    pass


class ImporterImportGeneFileError(ImporterImportError):
    pass


class ImporterImportColonHRMError(ImporterImportError):
    pass


class ImporterImportColonManometryError(ImporterImportError):
    pass


class ImporterImportCellDensityError(ImporterImportError):
    pass


class ImporterImportPointCloudError(ImporterImportError):
    pass


class ImporterImportXYZError(ImporterImportError):
    pass
