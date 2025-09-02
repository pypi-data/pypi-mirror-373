import asyncio
import warnings
from functools import wraps
from json import JSONDecodeError
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar, cast

import httpx
from httpx import HTTPStatusError, Response
from loguru import logger
from tenacity import (
    RetryError,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

# Configure warnings to only show once
warnings.filterwarnings("once", category=DeprecationWarning)


def raise_for_status_with_detail(response: Response) -> None:
    """Raises HTTPStatusError with detailed error message from response if status code is non-2XX.
    Falls back to standard error message if no detail is found.
    """
    try:
        response.raise_for_status()
    except HTTPStatusError as e:
        try:
            error_detail = response.json().get("detail", str(e))
            raise HTTPStatusError(message=error_detail, request=response.request, response=response) from e
        except (ValueError, JSONDecodeError):
            raise e


T = TypeVar("T")
P = ParamSpec("P")
F = TypeVar("F", bound=Callable[..., Any])


def run_async(async_func: Callable[P, Awaitable[T]]) -> Callable[P, T]:
    """Utility function to run an async function in a synchronous context."""

    @wraps(async_func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        loop = asyncio.get_event_loop()
        return cast(T, loop.run_until_complete(async_func(*args, **kwargs)))

    return sync_wrapper


def retry_predicate(exception: Exception) -> bool:
    """Retry if the exception is an unavailability error (503) or TimeoutError."""
    if isinstance(exception, httpx.HTTPStatusError) and exception.response.status_code == 503:
        logger.warning(f"Retrying due to 503 error: {exception}")
        return True
    elif isinstance(exception, httpx.ReadTimeout):
        logger.warning(f"Retrying due to read timeout: {exception}")
        return True
    elif isinstance(exception, httpx.ConnectTimeout):
        logger.warning(f"Retrying due to connect timeout: {exception}")
        return True
    else:
        return False


retry_request = retry(
    stop=stop_after_attempt(3),
    # Waits 3-6s, then 6-12s, then 12-25s between attempts
    wait=wait_exponential(multiplier=3, min=3, max=25),
    retry=retry_if_exception(retry_predicate),
    retry_error_cls=RetryError,  # raise RetryError after the last retry
)


def deprecated(
    since: str | None = None,
    removal_version: str | None = None,
    alternative: str | None = None,
    extra_message: str | None = None,
) -> Callable[[F], F]:
    """Decorator to mark functions as deprecated.

    Args:
        since (str | None): Version when the deprecation was introduced
        removal_version (str | None): Version when the function will be removed
        alternative (str | None): Alternative function or method to use
        extra_message (str | None): Additional message to include in the deprecation warning
    Returns:
        Callable: Decorated function that issues a deprecation warning

    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            message = f"{func.__name__} is deprecated"
            if since:
                message += f" since version {since}."
            else:
                message += "."
            if removal_version:
                message += f" It will be removed in version {removal_version}."
            else:
                message += " It will be removed in a future version."
            if alternative:
                message += f" Use {alternative} instead."
            if extra_message:
                message += f" {extra_message}"

            warnings.warn(
                message,
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator
