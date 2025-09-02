"""Unknown operation error codes."""
from enum import Enum
from typing import Any

from move_errors.codes.engine.base import BaseEngineOpsErrorCode
from move_errors.codes.engine.enums import OperationNames
from move_errors.utils.codes import get_default_error_code


class OpsUnknownOperationErrorCodes(BaseEngineOpsErrorCode, Enum):
    """Unknown operation error codes.

    If the engine does not send us an operation name then this
    error code class should be used as a fallback to still give the
    user a consistent message.
    """

    MV_060_999_0999 = get_default_error_code("MV_060_999_0999")
    """Describes an error code when an unknown error occurs."""

    @classmethod
    def operation_name(cls) -> OperationNames:
        """Operation name.

        Returns:
            The operation name for this ops error class
        """
        return OperationNames.OPS_UNKNOWN

    @classmethod
    def default_error_code(cls) -> Any:
        """Return the default error code for this class.

        Returns:
            The default error code.
        """
        return cls.MV_060_999_0999
