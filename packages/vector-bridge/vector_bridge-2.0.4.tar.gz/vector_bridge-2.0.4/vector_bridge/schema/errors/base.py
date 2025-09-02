from enum import Enum
from typing import Type


class BaseError(Exception):
    """Base class for general authentication or base-level errors."""


class IncorrectUsernameOrPassword(BaseError):
    """Raised when the username or password is incorrect."""


class BaseErrorDetail(str, Enum):
    INCORRECT_USERNAME_OR_PASSWORD = "Incorrect username or password"

    def to_exception(self) -> Type[BaseError]:
        """Return the exception class that corresponds to this Base error detail."""
        mapping = {
            BaseErrorDetail.INCORRECT_USERNAME_OR_PASSWORD: IncorrectUsernameOrPassword,
        }
        return mapping[self]


def raise_for_base_error_detail(detail: str) -> None:
    """
    Raises the corresponding BaseError based on the given error detail string.
    """
    try:
        detail_enum = BaseErrorDetail(detail)
    except ValueError:
        raise BaseError(f"Unknown base error: {detail}")
    raise detail_enum.to_exception()(detail)
