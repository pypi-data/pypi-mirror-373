# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from functools import lru_cache
from typing import Any, Iterable

from loguru import logger

# ======================================================================================================================
#
# EXCEPTIONS
#
# ======================================================================================================================


class CustomException(Exception):
    def __init__(self, *args: Iterable[Any]):
        logger.error(f"{type(self).__name__} raised.")

        self.message: Any = args[0] if args else None

    def __str__(self) -> str:
        if self.message:
            return type(self).__name__ + f": {self.message}"
        else:
            return type(self).__name__ + " raised."


class InvalidObservationSizeError(CustomException):
    pass


# ======================================================================================================================
#
# WARNINGS
#
# ======================================================================================================================


@lru_cache(maxsize=None)
def warn_once(message: str) -> None:
    """
    :param message: Message to log.
    """

    logger.warning(message)


def pydantic_field_deprecation_warning(old_name: str, new_name: str) -> None:
    """
    :param old_name: Name of the old field being deprecated.
    :param new_name: Name of the new field that is replacing the old one.
    """

    warn_once(
        f"The field name {old_name} is deprecated and will be removed in an upcoming release. Use {new_name} instead."
    )
