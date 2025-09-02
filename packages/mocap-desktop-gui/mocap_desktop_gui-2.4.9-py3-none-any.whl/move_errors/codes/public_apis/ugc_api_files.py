"""Error codes for ugc_api_files service."""
from enum import Enum

from move_errors.codes.base import BaseErrorCode
from move_errors.utils.codes import (
    get_default_error_code,
    get_default_error_code404,
    get_default_pydantic_error_code,
)


class UgcApiFilesErrorCodes(BaseErrorCode, Enum):
    """Error codes for ugc_api_files service."""

    MV_010_010_0001 = (
        {
            "suggestions": [
                "Please verify that you've provided a file with a valid extension.",
            ],
        },
        "MV_010_010_0001",
        True,
        "Invalid file type",
    )
    """Describes an error code when an invalid file type is provided."""
    MV_010_010_0002 = (
        {
            "suggestions": [
                "Please verify that the file exists.",
                "Please verify that you have access to this file.",
                "Please verify that the file is > 0 bytes",
            ],
        },
        "MV_010_010_0002",
        True,
        "File not found",
    )
    """Describes an error code where the file could not be found."""

    MV_010_010_0404 = get_default_error_code404("MV_010_010_0404")
    """Describes an error code when a resource is not found."""

    MV_010_010_0998 = get_default_pydantic_error_code("MV_010_010_0998")
    """Describes an error code when a pydantic error occurs."""

    MV_010_010_0999 = get_default_error_code("MV_010_010_0999")
    """Describes an error code when an unknown error occurs."""
