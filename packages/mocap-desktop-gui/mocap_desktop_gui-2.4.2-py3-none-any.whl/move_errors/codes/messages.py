"""Messages to be used for error codes."""

from move_errors.settings import MoveErrorSettings


def get_default_message() -> str:
    """Return default message.

    Returns:
        str: Default message.
    """
    settings = MoveErrorSettings()
    return f"Something went wrong in the {settings.service}. Please try again later."


# Constant for the unknown error message
UNKNOWN_ERROR_MESSAGE = "An unknown error occurred"
CONTACT_SUPPORT_MESSAGE = "Please contact support@move.ai."
# Constant for the unknown error message suggestion.
UNKNOWN_ERROR_SUGGESTION_MESSAGE = (
    f"This is an unknown error. {CONTACT_SUPPORT_MESSAGE}"
)
