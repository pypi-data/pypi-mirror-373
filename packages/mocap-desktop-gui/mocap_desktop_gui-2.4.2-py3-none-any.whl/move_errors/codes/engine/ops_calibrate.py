"""Operation error codes."""
from enum import Enum
from typing import Any

from move_errors.codes.engine.base import BaseEngineOpsErrorCode
from move_errors.codes.engine.enums import OperationNames


class OpsCalibrateOperationErrorCodes(BaseEngineOpsErrorCode, Enum):
    """Operation error codes."""

    MV_060_020_0999 = (
        {
            "suggestions": [
                "Verify your camera settings and ensure that a single actor is "
                + "visible in a Y-pose throughout the videos.",
            ],
        },
        "MV_060_020_0999",
        True,
        "The system was unable to generate a calibration",
    )
    """Describes an error code when an unknown error occurs."""

    @classmethod
    def operation_name(cls) -> OperationNames:
        """Operation name.

        Returns:
            The operation name for this ops error class
        """
        return OperationNames.OPS_CALIBRATE

    @classmethod
    def default_error_code(cls) -> Any:
        """Return the default error code for this class.

        Returns:
            The default error code.
        """
        return cls.MV_060_020_0999
