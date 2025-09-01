"""Base error code structure.

All error codes should inherit from this base class.
This ensures all error codes have all the necessary information such as:
1. error_info
2. message
3. error_type
4. is_display
"""
from dataclasses import dataclass, field
from typing import Any

from move_errors.codes.messages import get_default_message


@dataclass
class BaseErrorCode:
    """Base error code structure.

    We're using dataclass here instead of pydantic, due to native support of
    dataclasses in Enums. See the following link:
    https://docs.python.org/3/howto/enum.html#dataclass-support

    To create a new error code class, inherit from this class and provide
    the necessary information.

    Example:
    ```python
    from move_errors.codes.base import BaseErrorCode
    class EngineErrorCodes(BaseErrorCode, Enum):

        MV_010_010_0001 = (
            {"suggestions": ["Is there a human in the frame?"]},
            "MV_010_010_0001",
            True,
            "Failed to create a volume."
        )
    ```
    """

    info: dict[str, Any]  # noqa: WPS110
    """
    Error information - this can store information related to the error
    such as suggestions to resolve the error, etc.
    """

    code: str
    """
    The actual error code value. This should be unique accross error code classes.
    This should follow the company numbering policy.
    https://www.notion.so/moveai/SPIKE-Error-Code-Policies-4c07e5d750514f8788fa5a2b615bf3ee
    """

    is_display: bool
    """
    Whether to display the message associated with the code to the user.
    """

    message: str = field(default_factory=get_default_message)
    """
    Message associated to this error code.
    """
