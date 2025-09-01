"""Operation error codes."""
from enum import Enum
from typing import Any

from move_errors.codes.engine.base import BaseEngineOpsErrorCode
from move_errors.codes.engine.enums import OperationNames


class OpsSyncMultiviewVideosOperationErrorCodes(BaseEngineOpsErrorCode, Enum):
    """Operation error codes."""

    MV_060_350_0999 = (
        {
            "suggestions": [
                "Check the videos settings and the clap times provided",
            ],
        },
        "MV_060_350_0999",
        True,
        "The engine has been unable to synchronize the videos",
    )
    """Describes an error code when an unknown error occurs."""

    @classmethod
    def operation_name(cls) -> OperationNames:
        """Operation name.

        Returns:
            The operation name for this ops error class
        """
        return OperationNames.OPS_SYNC_MULTIVIEW_VIDEOS

    @classmethod
    def default_error_code(cls) -> Any:
        """Return the default error code for this class.

        Returns:
            The default error code.
        """
        return cls.MV_060_350_0999
