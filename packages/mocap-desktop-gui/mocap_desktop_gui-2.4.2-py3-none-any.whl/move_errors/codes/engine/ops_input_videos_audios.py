"""Operation error codes."""
from enum import Enum
from typing import Any

from move_errors.codes.engine.base import BaseEngineOpsErrorCode
from move_errors.codes.engine.enums import OperationNames


class OpsInputVideosAudiosOperationErrorCodes(BaseEngineOpsErrorCode, Enum):
    """Operation error codes."""

    MV_060_130_0999 = (
        {
            "suggestions": [
                "Please make sure the camera settings are correct and the original metadata is included with the source videos",  # noqa: E501
            ],
        },
        "MV_060_130_0999",
        True,
        "There has been an issue with the camera settings",
    )
    """Describes an error code when an unknown error occurs."""

    @classmethod
    def operation_name(cls) -> OperationNames:
        """Operation name.

        Returns:
            The operation name for this ops error class
        """
        return OperationNames.OPS_INPUT_VIDEOS_AUDIOS

    @classmethod
    def default_error_code(cls) -> Any:
        """Return the default error code for this class.

        Returns:
            The default error code.
        """
        return cls.MV_060_130_0999
