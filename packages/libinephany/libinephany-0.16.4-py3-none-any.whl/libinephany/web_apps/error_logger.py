# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import asyncio
import datetime
import os
import traceback as traceback_module
from types import TracebackType
from typing import Protocol, TypeAlias

from loguru import logger
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient as SlackAsyncClient

from libinephany.utils.asyncio_worker import AsyncioWorker
from libinephany.utils.error_severities import SEVERITY_EMOJIS, SEVERITY_LEVELS, ErrorSeverities

# ======================================================================================================================
#
# TYPE HINTS
#
# ======================================================================================================================

ExceptionEntry: TypeAlias = tuple[Exception, traceback_module.TracebackException, datetime.datetime]
ExceptionPackage: TypeAlias = tuple[Exception, str, datetime.datetime]


class ExceptionSeverityClassifier(Protocol):
    def __call__(self, *, exception: Exception, traceback: str, timestamp: datetime.datetime) -> ErrorSeverities:
        """
        :param exception: Exception to classify the severity of.
        :param traceback: Traceback associated with the given exception.
        :param timestamp: Time the exception occurred.
        :return: Severity of the exception.
        """

        ...


# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ErrorLogger(AsyncioWorker):

    SLACK_BOT_TOKEN = "SLACK_BOT_TOKEN"
    SLACK_BOT_CHANNEL_ID = "SLACK_BOT_CHANNEL_ID"

    ENCODING = "utf-8"
    CHANNEL_MENTION = "<!channel>"

    def __init__(
        self,
        service_name: str,
        minimum_severity: ErrorSeverities = ErrorSeverities.WARNING,
        error_classifier: ExceptionSeverityClassifier | None = None,
        max_time_accumulating_errors: float = 10.0,
        max_errors_in_queue: int = 5000,
    ) -> None:
        """
        :param service_name: Name of the service deployed on the cloud errors sent to this error logger should be sent
        to.
        :param minimum_severity: Minimum error severity that can be sent to Slack.
        :param error_classifier: Optional callable used to alter how errors severities are classified. If this is None
        all errors are given the 'WARNING' severity.
        :param max_time_accumulating_errors: Maximum amount of time to spend batching identical errors together.
        :param max_errors_in_queue: Maximum length of the error logging queue.
        """

        self._error_queue: asyncio.Queue = asyncio.Queue(maxsize=max_errors_in_queue)

        self._slack_client, self._channel_id = self._get_slack_client()

        self.service_name = service_name
        self.error_classifier = error_classifier if error_classifier is not None else default_error_classifier
        self.max_time_accumulating_errors = max_time_accumulating_errors
        self.minimum_severity = SEVERITY_LEVELS[minimum_severity]

        super().__init__()

    def __enter__(self) -> "ErrorLogger":
        """
        :return: This class instance.
        """

        return self

    def __exit__(
        self, exc_type: type[Exception] | None, exc_val: Exception | None, exc_tb: TracebackType | None
    ) -> bool | None:
        """
        :param exc_type: None or the type of exception that occurred.
        :param exc_val: None or the caught exception instance.
        :param exc_tb: None or the traceback of the exception.
        :return: Whether the error should propagate outwards.
        """

        if exc_val is not None:
            logger.error(f"{self.__class__.__name__} context manager caught an exception of type {exc_type.__name__}.")

            exception_strings = traceback_module.format_exception(exc_type, exc_val, exc_tb)
            formatted_exception = "".join(exception_strings)

            self.put(exception=exc_val, traceback=formatted_exception)

            return True

        return None

    @property
    def active(self) -> bool:
        """
        :return: Boolean indicating whether the worker background thread should be activated.
        """

        return self._slack_client is not None and self._channel_id is not None

    @staticmethod
    def _log_error_to_terminal(exception: Exception) -> None:
        """
        :param exception: Exception to log to the terminal.
        """

        try:
            logger.error(f"Server encountered {exception.__class__.__name__}. Logging traceback to terminal.")
            logger.exception(exception)
        except Exception as e:
            print(
                f"{e.__class__.__name__} occurred when attempting to log exception {exception.__class__.__name__} to "
                f"the terminal!"
            )

    @staticmethod
    def _get_slack_message(
        mention: str,
        notification_emoji: str,
        service_name: str,
        exception: Exception,
        frequency: int,
        frequency_time_window: float,
    ) -> str:
        """
        :param mention: Mention tag of the entire channel or a particular user ID.
        :param notification_emoji: Emoji to include in the message which indicates the error's severity.
        :param service_name: Name of the service the error comes from.
        :param exception: Exception that occurred.
        :param frequency: How frequently the exception occurred in the given time window.
        :param frequency_time_window: Time between the first and last instance of the exception.
        :return: Formatted Slack message string.
        """

        frequency_line = f"{frequency} in {frequency_time_window}s" if frequency > 1 else f"{frequency}"

        return (
            f"{mention}{notification_emoji} *{service_name} Error* {notification_emoji}\n"
            f"• *Service*: {service_name}\n"
            f"• *Error Type*: {exception.__class__.__name__}\n"
            f"• *Frequency*: {frequency_line}\n"
            f"• *Traceback*: "
        )

    def _get_traceback_file_name(self, exception: Exception, exception_timestamp: str) -> str:
        """
        :param exception: Exception being sent to Slack.
        :param exception_timestamp: Time the exception occurred.
        :return: Filename the exception should be stored in.
        """

        formatted_service_name = self.service_name.replace(" ", "_")

        return f"{formatted_service_name}__{exception.__class__.__name__}__{exception_timestamp}.txt"

    def _get_slack_client(self) -> tuple[SlackAsyncClient | None, str | None]:
        """
        :return: Tuple of:
            - None or the asynchronous Slack API client.
            - None or the ID of the channel the Slack bot should send messages to.
        """

        api_token = os.environ.get(self.SLACK_BOT_TOKEN, None)
        channel_id = os.environ.get(self.SLACK_BOT_CHANNEL_ID, None)

        if api_token is not None and channel_id is not None:
            return SlackAsyncClient(token=api_token), channel_id

        logger.warning(
            f"No errors will be sent to Slack. Missing either {self.SLACK_BOT_TOKEN} or {self.SLACK_BOT_CHANNEL_ID}."
        )
        return None, None

    def _handle_unexpected_exception(self, exception: Exception, error_traceback: str) -> None:
        """
        :param exception: Exception that occurred and was not handled elsewhere.
        :param error_traceback: Traceback of the exception.
        """

        pass

    async def _count_exception_frequency(
        self, exception: Exception, timestamp: datetime.datetime
    ) -> tuple[int, float, ExceptionPackage | None]:
        """
        :param exception: Exception to count the frequency of.
        :param timestamp: Time the exception occurred.
        :return: Tuple of:
            - How frequently the error occurred in the returned time window.
            - Time window which is the time in seconds between the first occurrence of the given error and the last
              occurrence.
            - None or a Tuple containing the next error to handle.
        """

        base_entry = (exception, traceback_module.TracebackException.from_exception(exception), timestamp)

        next_to_process, time_window = None, None
        start_time = datetime.datetime.now(datetime.timezone.utc)
        frequency = 1

        while True:
            try:
                next_exception, next_traceback, next_timestamp = await asyncio.wait_for(
                    self._error_queue.get(), timeout=self.max_time_accumulating_errors
                )
                next_entry = (
                    next_exception,
                    traceback_module.TracebackException.from_exception(next_exception),
                    next_timestamp,
                )

                exceptions_are_similar = _exceptions_are_similar(
                    original_exception_entry=base_entry,
                    next_exception_entry=next_entry,
                    start_time=start_time,
                    max_interval=self.max_time_accumulating_errors,
                )

                if not exceptions_are_similar:
                    next_to_process = (next_exception, next_traceback, next_timestamp)
                    break

                frequency += 1
                time_window = next_timestamp - timestamp

            except (asyncio.QueueEmpty, TimeoutError):
                break

        time_window = 0.0 if time_window is None else round(time_window.total_seconds(), 3)
        return frequency, time_window, next_to_process

    async def _send_error_to_slack(
        self,
        severity: ErrorSeverities,
        exception: Exception,
        traceback: str,
        exception_timestamp: datetime.datetime,
        frequency: int,
        frequency_time_window: float,
    ) -> None:
        """
        :param exception: Exception caught by the API middleware and transferred to the ErrorLogger.
        :param traceback: Traceback associated with the exception.
        :param exception_timestamp: Time the exception occurred.
        :param frequency: How many times the error occurred within a certain timeframe.
        :param frequency_time_window: Length of time between the first and last occurrence of this error.

        :todo: Handle rate limits and retries.
        """

        formatted_timestamp = exception_timestamp.isoformat()
        traceback_filename = self._get_traceback_file_name(exception=exception, exception_timestamp=formatted_timestamp)

        notification_emoji = SEVERITY_EMOJIS[severity]
        mention = "" if not ErrorSeverities.should_mention(severity=severity) else self.CHANNEL_MENTION

        self._log_error_to_terminal(exception=exception)

        try:
            await self._slack_client.files_upload_v2(
                channel=self._channel_id,
                filename=traceback_filename,
                content=traceback.encode(self.ENCODING),
                initial_comment=self._get_slack_message(
                    mention=mention,
                    notification_emoji=notification_emoji,
                    service_name=self.service_name,
                    exception=exception,
                    frequency=frequency,
                    frequency_time_window=frequency_time_window,
                ),
            )
        except SlackApiError as e:
            logger.exception(e)
            logger.error("Failed to send error to slack!")

    async def _work(
        self,
        previous_result: ExceptionPackage | None,
    ) -> ExceptionPackage | None:
        """
        :param previous_result: Previous result of call to this method.
        :return: Result to convey to this method on the next call.

        Asynchronous worker function which gathers errors and sends them to Slack.
        """

        next_exception: ExceptionPackage | None = None

        if next_exception is None:
            exception, traceback, exception_timestamp = await self._error_queue.get()
        else:
            exception, traceback, exception_timestamp = next_exception

        severity = self.error_classifier(exception=exception, traceback=traceback, timestamp=exception_timestamp)
        severity_level = SEVERITY_LEVELS[severity]

        if severity_level <= self.minimum_severity:
            frequency, frequency_window, next_exception = await self._count_exception_frequency(
                exception=exception, timestamp=exception_timestamp
            )

            await self._send_error_to_slack(
                severity=severity,
                exception=exception,
                traceback=traceback,
                exception_timestamp=exception_timestamp,
                frequency=frequency,
                frequency_time_window=frequency_window,
            )

        return next_exception

    def put(self, exception: Exception, traceback: str) -> None:
        """
        :param exception: Exception to add to the queue.
        :param traceback: Traceback of the exception to add to the queue.
        """

        if self.active:
            exception_timestamp = datetime.datetime.now(datetime.timezone.utc)

            try:
                self._error_queue.put_nowait((exception, traceback, exception_timestamp))

            except asyncio.QueueFull:
                logger.warning(f"{self.__class__.__name__} queue is full! Logging error to terminal.")
                self._log_error_to_terminal(exception=exception)

        else:
            self._log_error_to_terminal(exception=exception)


# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def _extract_last_frame(traceback: traceback_module.TracebackException) -> None | traceback_module.FrameSummary:
    """
    :param traceback: Traceback exception stack to extract the last frame from.
    :return: None or the last traceback frame.
    """

    return traceback.stack[-1] if traceback.stack else None


def _exceptions_are_similar(
    original_exception_entry: ExceptionEntry,
    next_exception_entry: ExceptionEntry,
    start_time: datetime.datetime,
    max_interval: float,
) -> bool:
    """
    :param original_exception_entry: Tuple of the original exception, it's traceback stack and the time it occurred at.
    :param next_exception_entry: Tuple of the new exception, it's traceback stack and the time it occurred at.
    :param start_time: Time this exception batch begun accumulating.
    :param max_interval: Maximum time between identical exceptions.
    :return: Whether the exceptions should be batched together in the Slack message.
    """

    original_exception, original_traceback, original_timestamp = original_exception_entry
    next_exception, next_traceback, next_timestamp = next_exception_entry

    original_last_frame = _extract_last_frame(traceback=original_traceback)
    next_last_frame = _extract_last_frame(traceback=next_traceback)

    if not original_last_frame or not next_last_frame:
        return False

    return (
        original_last_frame.filename == next_last_frame.filename
        and original_last_frame.lineno == next_last_frame.lineno
        and original_last_frame.name == next_last_frame.name
        and original_exception.__class__.__name__ == next_exception.__class__.__name__
        and abs((next_timestamp - start_time).total_seconds()) <= max_interval
    )


def default_error_classifier(*, exception: Exception, traceback: str, timestamp: datetime.datetime) -> ErrorSeverities:
    """
    :param exception: Exception to classify the severity of.
    :param traceback: Traceback associated with the given exception.
    :param timestamp: Time the exception occurred.
    :return: Severity of the exception.

    :note: This is a default placeholder function not intended for actual use in production.
    """

    logger.debug(
        f"Default error classifier received exception {exception.__class__.__name__} at {timestamp}. Giving"
        f" error severity level '{ErrorSeverities.WARNING.value}'."
    )
    logger.trace(traceback)

    return ErrorSeverities.WARNING
