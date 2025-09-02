"""Error codes for ugc_api_files service."""
from enum import Enum

from move_errors.codes.base import BaseErrorCode
from move_errors.codes.constants import SUGGESTIONS
from move_errors.utils.codes import get_default_error_code, get_default_error_code404


class MovePlatformBackendErrorCodes(BaseErrorCode, Enum):
    """Error codes for move_platform_backend service."""

    MV_000_030_0001 = (
        {
            SUGGESTIONS: [
                "{0} {1}".format(
                    "Please verify that you've provided",
                    "a valid file_id of a existing file.",
                ),
            ],
        },
        "MV_000_030_0001",
        True,
        "Invalid file_id provided",
    )
    """Describes an error code when an invalid file_id is provided."""

    MV_000_030_0002 = (
        {
            SUGGESTIONS: [
                "{0} {1}".format(
                    "Please verify that you've provided",
                    "a valid file format, only webm is supported currently.",
                ),
            ],
        },
        "MV_000_030_0002",
        True,
        "Invalid format provided, only webm is supported currently.",
    )
    """Describes an error code when an invalid format is provided."""

    MV_000_030_0003 = (
        {
            SUGGESTIONS: [
                "Please verify that you are requesting a file belonging to you.",
            ],
        },
        "MV_000_030_0003",
        True,
        "File not found in move_ugc_api",
    )
    """Describes an error code when the file is not found in move_ugc_api."""

    MV_000_030_0004 = (
        {
            SUGGESTIONS: [
                "Please verify that you've requested a existing file.",
            ],
        },
        "MV_000_030_0004",
        True,
        "We couldn't find this file",
    )
    """Describes an error code when the file is not found in move_ugc_api."""

    MV_000_030_0005 = (
        {
            SUGGESTIONS: [
                "{0} {1}".format(
                    "Please verify that you've provided",
                    "a valid file_id of a existing file.",
                ),
            ],
        },
        "MV_000_030_0005",
        True,
        "Something went wrong while trying to access this file.",
    )

    MV_000_030_0006 = (
        {
            SUGGESTIONS: [
                "Unauthorized.",
            ],
        },
        "MV_000_030_0006",
        True,
        "Unauthorized.",
    )

    MV_000_030_0999 = get_default_error_code("MV_000_030_0999")
    """Describes an error code when an unknown error occurs."""

    MV_000_030_0404 = get_default_error_code404("MV_000_030_0404")
    """Describes an error code when a resource is not found."""
