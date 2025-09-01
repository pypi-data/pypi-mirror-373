"""Define Error Handlers."""
import httpx
from starlette.requests import Request
from starlette.responses import JSONResponse

from move_errors.exceptions import MoveError


def move_error_handler(
    request: Request,
    exc: MoveError,
) -> JSONResponse:
    """Exception Handler for Move Error.

    Args:
        request: Request object.
        exc: Exception object.

    Returns:
        JSONResponse: JSON response when MoveError is raised.
    """
    status_code = httpx.codes.BAD_REQUEST
    if isinstance(exc.data, dict) and exc.data.get("status_code"):
        status_code = exc.data["status_code"]
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code.code,
                "message": exc.message,
                "info": exc.info,
                "data": exc.data or {},
                "is_display": exc.is_display,
            },
        },
    )
