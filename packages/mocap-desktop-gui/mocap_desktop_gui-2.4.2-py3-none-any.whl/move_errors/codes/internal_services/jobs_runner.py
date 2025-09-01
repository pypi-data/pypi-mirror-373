"""Error codes for jobs runner."""
from enum import Enum

from move_errors.codes.base import BaseErrorCode
from move_errors.utils.codes import (
    get_default_bad_request_error_code,
    get_default_error_code,
)


class JobsRunnerErrorCodes(BaseErrorCode, Enum):
    """Error codes for jobs_runner."""

    MV_070_060_0998 = get_default_bad_request_error_code("MV_070_060_0998")
    """Describes an error code when a pydantic error occurs."""

    MV_070_060_0001 = (
        {
            "suggestions": [
                "Upgrade your plan now to continue",
            ],
        },
        "MV_070_060_0001",
        True,
        "You do not have enough credits to process this video",
    )
    MV_070_060_0002 = (
        {
            "suggestions": [
                "Verify that the source file(s) are a valid mp4, avi or mov format.",
                "Verify that the source file(s) are not corrupt.",
                "Verify that the source file(s) are at least 2 seconds long.",
            ],
        },
        "MV_070_060_0002",
        True,
        "{0}".format(
            "We were unable to analyse your source video file(s)",
        ),
    )

    MV_070_060_0999 = get_default_error_code("MV_070_060_0999")
    """Describes an error code when an unknown error occurs."""
