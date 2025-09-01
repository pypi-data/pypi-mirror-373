"""MoveError exception structure."""
from typing import Any, TypeVar

from move_errors.codes.base import BaseErrorCode
from move_errors.codes.messages import get_default_message

ErrorCodes = TypeVar("ErrorCodes", bound=BaseErrorCode)


class MoveError(Exception):
    """Base Exception for Move Services."""

    default_message: str = get_default_message()

    def __init__(  # noqa: WPS211
        self,
        code: ErrorCodes,
        info: dict[str, Any] | None = None,  # noqa: WPS110
        message: str | None = None,
        is_display: bool | None = None,
        data: dict[str, Any] | None = None,  # noqa: WPS110
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the MoveError class.

        Args:
            code (ErrorCodes):
                The error code.
            info (dict[str, Any], optional):
                Error information. Defaults to None.
            message (str):
                Error message. Defaults to get_default_message().
            is_display (bool):
                Whether to display the message to the user. Defaults to False.
            data (dict[str, Any], optional):
                Additional data. Defaults to None.
            args (Any):
                Additional arguments.
            kwargs (Any):
                Additional keyword arguments.
        """
        self.code = code
        self.info = info or self.code.info  # noqa: WPS110
        self.message = message or self.code.message or self.default_message
        self.is_display = self.code.is_display
        self.data = data or {}  # noqa: WPS110

        # Overwrite is_display if provided instead of using the value from error code
        if is_display is not None:
            self.is_display = is_display

        if not self.is_display:
            self.message = self.default_message

        super().__init__(
            self.message,
            self.code.code,
            self.info,
            self.is_display,
            self.data,
            *args,
            **kwargs,
        )
