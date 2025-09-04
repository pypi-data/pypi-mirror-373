# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import asyncio
import traceback
from abc import ABC, abstractmethod
from typing import Any, final

from loguru import logger

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class AsyncioWorker(ABC):

    def __init__(self, *args, **kwargs) -> None:
        """
        Warns the user that the background worker will not be created if the worker is inactive.
        """

        if not self.active:
            logger.warning(
                f"{self.__class__.__name__} has been made inactive. Its background task will not be created during "
                f"operation."
            )

    @property
    @abstractmethod
    def active(self) -> bool:
        """
        :return: Whether the worker should be activated during operation.
        """

        raise NotImplementedError

    @abstractmethod
    async def _work(
        self,
        previous_result: Any,
    ) -> Any:
        """
        :param previous_result: Previous result of call to this method.
        :return: Result to convey to this method on the next call.

        Method which defines the work that should be done by the worker each iteration.
        """

        raise NotImplementedError

    @abstractmethod
    def _handle_unexpected_exception(self, exception: Exception, error_traceback: str) -> None:
        """
        :param exception: Exception that occurred and was not handled elsewhere.
        :param error_traceback: Traceback of the exception.
        """

        raise NotImplementedError

    @final
    async def worker(self) -> None:
        """
        Asynchronous worker task that operates in the background of regular operation.
        """

        result = None

        while True:
            try:
                result = await self._work(previous_result=result)

            except asyncio.CancelledError:
                logger.info(f"Background task of {self.__class__.__name__} has been ordered to stop. Exiting.")
                break

            except Exception as e:
                logger.exception(e)
                logger.error(f"Unhandled {e.__class__.__name__} in {self.__class__.__name__} worker!")
                error_traceback = traceback.format_exc()

                self._handle_unexpected_exception(exception=e, error_traceback=error_traceback)
