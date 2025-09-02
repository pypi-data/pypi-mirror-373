"""Error codes for ugc_api_clients service."""
from enum import Enum

from move_errors.codes.base import BaseErrorCode
from move_errors.utils.codes import (
    get_default_error_code,
    get_default_error_code404,
    get_default_pydantic_error_code,
)


class UgcApiClientsErrorCodes(BaseErrorCode, Enum):
    """Error codes for ugc_api_clients service."""

    MV_010_040_0404 = get_default_error_code404("MV_010_040_0404")
    """Describes an error code when a resource is not found."""

    MV_010_040_0998 = get_default_pydantic_error_code("MV_010_040_0998")
    """Describes an error code when a pydantic error occurs."""

    MV_010_040_0999 = get_default_error_code("MV_010_040_0999")
    """Describes an error code when an unknown error occurs."""
