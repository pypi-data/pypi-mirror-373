"""Util methods for move-error codes."""
import os
from typing import Any

from move_errors.codes.messages import (
    UNKNOWN_ERROR_MESSAGE,
    UNKNOWN_ERROR_SUGGESTION_MESSAGE,
)

SUGGESTIONS_LITERAL = "suggestions"


def get_default_error_code(code: str) -> tuple[dict[str, Any], str, bool, str]:
    """Get the default error code.

    Args:
        code: The error code.

    Returns:
        The default error code tuple.
    """
    return (
        {
            "suggestions": [
                UNKNOWN_ERROR_SUGGESTION_MESSAGE,
            ],
        },
        code,
        True,
        UNKNOWN_ERROR_MESSAGE,
    )


def get_default_pydantic_error_code(code: str) -> tuple[dict[str, Any], str, bool, str]:
    """Get the default error code for pydantic errors.

    Args:
        code: The error code.

    Returns:
        The default error code tuple.
    """
    return (
        {
            SUGGESTIONS_LITERAL: [
                "Please verify that you've provided the correct data.",
                "Please refer to the data key for invalid data related to this error.",
                "{0} {1}.".format(
                    "Please check the api documentation for the correct data format at",
                    "https://move-ai.github.io/move-ugc-api/schema/",
                ),
            ],
        },
        code,
        True,
        # This message will most likely be overridden by the pydantic error message
        "Data validation failed.",
    )


def get_default_error_code404(code: str) -> tuple[dict[str, Any], str, bool, str]:
    """Get the default error code for not found errors.

    Args:
        code: The error code.

    Returns:
        The default error code tuple.
    """
    service: str = os.getenv("SERVICE_NAME", "Move.ai")
    return (
        {
            SUGGESTIONS_LITERAL: [
                "Please verify that the resource you're requesting exists.",
            ],
        },
        code,
        True,
        # This message will most likely be overridden by the pydantic error message
        f"Resource not found in {service}.",
    )


def get_default_bad_request_error_code(
    code: str,
) -> tuple[dict[str, Any], str, bool, str]:
    """Get the default error code for bad requests.

    This is typically used for internal bad requests.

    Args:
        code: The error code.

    Returns:
        The default error code tuple.
    """
    return (
        {
            SUGGESTIONS_LITERAL: [
                "Please verify that you've provided the correct data.",
            ],
        },
        code,
        # By default, don't display this error to the user, as it's an internal error
        # This can be overridden on api by api basis.
        False,
        "Bad request.",
    )
