# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import asyncio
import os
import traceback
from typing import Any, Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette import status

from libinephany.utils.asyncio_worker import AsyncioWorker
from libinephany.web_apps.error_logger import ErrorLogger

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

SCHEDULE_ENDPOINT = "/schedule"
SCHEMA_ENDPOINT = "/schema"

INTERNAL_SERVER_ERROR_RESPONSE_JSON = {"detail": "Internal Server Error"}

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def create_background_task(component: AsyncioWorker) -> asyncio.Task | None:
    """
    :param component: Component responsible for the given task.
    :return: None or the created task.
    """

    if component.active:
        logger.info(f"{component.__class__.__name__} is active. Creating background worker task.")
        return asyncio.create_task(component.worker())

    return None


def get_environment_variable(environment_variable: str) -> Any:
    """
    :param environment_variable: Name of the environment variable to get the value of.
    :return: Retrieved environment variable value.
    :raises: KeyError if the given environment variable has not been set.
    """

    value = os.environ.get(environment_variable, None)

    if value is None:
        raise KeyError(f"Environment variable {environment_variable} has not been set!")

    return value


async def gracefully_stop_background_task(component: AsyncioWorker, task: asyncio.Task | None) -> None:
    """
    :param component: Component responsible for the given task.
    :param task: None or the task to gracefully stop.
    """

    if task is not None:
        logger.info(f"Waiting for {component.__class__.__name__} task to finish...")
        task.cancel()

        try:
            await task

        except Exception as e:
            logger.exception(e)
            logger.error(f"Unhandled exception in {component.__class__.__name__}'s background task!")


# ======================================================================================================================
#
# WEB APP ROUTES
#
# ======================================================================================================================


def add_basic_app_routes_and_middleware(app: FastAPI):
    """
    :param app: Initialised web app to add routes to.
    """

    logger.info("Creating Web App Routes.")

    @app.get("/health")
    @app.get("/ping")
    async def health_check() -> dict[str, str]:
        logger.info("Health check called.")

        return {"status": "healthy"}

    @app.middleware("http")
    async def catch_errors(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.debug(
                f"Exception {e.__class__.__name__} caught by {ErrorLogger.__name__} middleware. Sending exception to "
                f"error logger."
            )

            exception_traceback = traceback.format_exc()
            app.state.error_logger.put(exception=e, traceback=exception_traceback)  # type: ignore

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=INTERNAL_SERVER_ERROR_RESPONSE_JSON,
            )

    return app
