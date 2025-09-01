"""Operation error codes."""
from enum import Enum
from typing import Any

from move_errors.codes.engine.base import BaseEngineOpsErrorCode
from move_errors.codes.engine.enums import OperationNames


class OpsOnlineBallTrackingOperationErrorCodes(BaseEngineOpsErrorCode, Enum):
    """Operation error codes."""

    MV_060_460_0999 = (
        {
            "suggestions": [
                "Check the ball is clearly visible in the videos",
            ],
        },
        "MV_060_460_0999",
        True,
        "No ball detected",
    )
    """Describes an error code when an unknown error occurs."""

    @classmethod
    def operation_name(cls) -> OperationNames:
        """Operation name.

        Returns:
            The operation name for this ops error class
        """
        return OperationNames.OPS_ONLINE_BALL_TRACKING

    @classmethod
    def default_error_code(cls) -> Any:
        """Return the default error code for this class.

        Returns:
            The default error code.
        """
        return cls.MV_060_460_0999
