"""Error codes for run_manager."""
from enum import Enum

from move_errors.codes.base import BaseErrorCode
from move_errors.utils.codes import (
    get_default_bad_request_error_code,
    get_default_error_code,
)


class RunManagerErrorCodes(BaseErrorCode, Enum):
    """Error codes for run_manager."""

    MV_070_030_0998 = get_default_bad_request_error_code("MV_070_030_0998")
    """Describes an error code when a pydantic error occurs."""

    MV_070_030_0999 = get_default_error_code("MV_070_030_0999")
    """Describes an error code when an unknown error occurs."""
