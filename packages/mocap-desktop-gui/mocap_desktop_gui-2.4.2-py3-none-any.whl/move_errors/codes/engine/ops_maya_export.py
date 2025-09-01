"""Operation error codes."""
from enum import Enum
from typing import Any

from move_errors.codes.engine.base import BaseEngineOpsErrorCode
from move_errors.codes.engine.enums import OperationNames
from move_errors.codes.messages import CONTACT_SUPPORT_MESSAGE


class OpsMayaExportOperationErrorCodes(BaseEngineOpsErrorCode, Enum):
    """Operation error codes."""

    MV_060_190_0999 = (
        {
            "suggestions": [
                CONTACT_SUPPORT_MESSAGE,
            ],
        },
        "MV_060_190_0999",
        True,
        "The engine was unable to generate a MAYA export",
    )
    """Describes an error code when an unknown error occurs."""

    @classmethod
    def operation_name(cls) -> OperationNames:
        """Operation name.

        Returns:
            The operation name for this ops error class
        """
        return OperationNames.OPS_MAYA_EXPORT

    @classmethod
    def default_error_code(cls) -> Any:
        """Return the default error code for this class.

        Returns:
            The default error code.
        """
        return cls.MV_060_190_0999
