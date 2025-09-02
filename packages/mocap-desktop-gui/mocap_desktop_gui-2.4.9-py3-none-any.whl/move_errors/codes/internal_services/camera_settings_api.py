"""Error codes for camera_settings_api."""
from enum import Enum

from move_errors.codes.base import BaseErrorCode
from move_errors.utils.codes import (
    get_default_bad_request_error_code,
    get_default_error_code,
    get_default_error_code404,
)


class CameraSettingsApiErrorCodes(BaseErrorCode, Enum):
    """Error codes for camera_settings_api."""

    MV_070_080_0404 = get_default_error_code404("MV_070_080_0404")
    """Describes an error code when a resource is not found."""

    MV_070_080_0400 = get_default_bad_request_error_code("MV_070_080_0400")
    """Describes an error code when a pydantic error occurs."""

    MV_070_080_0999 = get_default_error_code("MV_070_080_0999")
    """Describes an error code when an unknown error occurs."""
