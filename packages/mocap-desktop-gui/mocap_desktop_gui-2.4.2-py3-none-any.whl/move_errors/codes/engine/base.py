"""Base class for engine ops error codes."""
from typing import Any

from move_errors.codes.base import BaseErrorCode
from move_errors.codes.engine.enums import OperationNames


class BaseEngineOpsErrorCode(BaseErrorCode):
    """Base class for engine ops error codes."""

    @classmethod
    def operation_name(cls) -> OperationNames:  # pragma: no cover
        """Return the engine operation name.

        Raises:
            NotImplementedError: If the operation name is not implemented.
        """
        raise NotImplementedError

    @classmethod
    def default_error_code(cls) -> Any:  # pragma: no cover
        """Return the default error code.

        This allows a consistent interface between all ops error code classes.

        Raises:
            NotImplementedError: If the error code is not implemented.
        """
        raise NotImplementedError
