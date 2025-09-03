from __future__ import annotations


class ExcelValidationError(Exception):
    """Base error for excel parser"""


class NoExistingOMEROUser(ExcelValidationError):
    def __init__(self, entered_user_login):
        message = f"User {entered_user_login} does not exist in OMERO"
        super().__init__(message)


class UserNotInOMEROGroup(ExcelValidationError):
    def __init__(self, entered_user_login, entered_group_name):
        message = f"""
User {entered_user_login} does belong to OMERO group {entered_group_name}"""
        super().__init__(message)


class MissingExcelSheetError(ExcelValidationError):
    def __init__(self, sheet_name, file_path):
        message = f"Sheet {sheet_name} does not exist in {file_path} Excel file"
        super().__init__(message)


class ManifestValidationError(Exception):
    """Base error for manifest parser"""


class InvalidManifestError(ManifestValidationError):
    def __init__(self, manifest_file):
        message = f"Manifest {manifest_file} is invalid"
        super().__init__(message)
