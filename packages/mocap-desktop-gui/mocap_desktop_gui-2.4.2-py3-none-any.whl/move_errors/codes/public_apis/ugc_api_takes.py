"""Error codes for ugc_api_takes service."""
from enum import Enum

from move_errors.codes.base import BaseErrorCode
from move_errors.utils.codes import (
    get_default_error_code,
    get_default_error_code404,
    get_default_pydantic_error_code,
)


class UgcApiTakesErrorCodes(BaseErrorCode, Enum):
    """Error codes for ugc_api_takes service."""

    MV_010_020_0001 = (
        {
            "suggestions": [
                "Please verify that the volume you provided has finished processing.",
                "{0} {1}".format(
                    "Please use getVolume query to verify the volume state",
                    "before trying this query again.",
                ),
                "Please check the data field to see the current state of the volume.",
            ],
        },
        "MV_010_020_0001",
        True,
        "The provided volume needs to be on a completed state.",
    )
    """Describes an error when volume is not on a final state."""

    MV_010_020_0002 = (
        {
            "suggestions": [
                "{0} {1}".format(
                    "Please make sure that you're using the same device_labels",
                    "that were used in volume creation.",
                ),
                "{0} {1}".format(
                    "getVolume query can be used to verify the device labels",
                    "used in the volume creation.",
                ),
                "Please see the data key for more info on the device labels used.",
            ],
        },
        "MV_010_020_0002",
        True,
        "Wrong device labels provided.",
    )
    """Describes an error when wrong device labels are provided."""

    MV_010_020_0404 = get_default_error_code404("MV_010_020_0404")
    """Describes an error code when a resource is not found."""

    MV_010_020_0998 = get_default_pydantic_error_code("MV_010_020_0998")
    """Describes an error code when a pydantic error occurs."""

    MV_010_020_0999 = get_default_error_code("MV_010_020_0999")
    """Describes an error code when an unknown error occurs."""
