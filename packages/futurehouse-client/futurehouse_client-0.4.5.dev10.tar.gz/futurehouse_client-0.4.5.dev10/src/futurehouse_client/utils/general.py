import asyncio
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

from httpx import (
    CloseError,
    ConnectError,
    ConnectTimeout,
    HTTPStatusError,
    NetworkError,
    ReadError,
    ReadTimeout,
    RemoteProtocolError,
    codes,
)
from requests.exceptions import RequestException, Timeout
from tenacity import RetryCallState
from tqdm.asyncio import tqdm

T = TypeVar("T")

RETRYABLE_HTTP_STATUS_CODES = {
    codes.TOO_MANY_REQUESTS,
    codes.INTERNAL_SERVER_ERROR,
    codes.BAD_GATEWAY,
    codes.SERVICE_UNAVAILABLE,
    codes.GATEWAY_TIMEOUT,
}

_BASE_CONNECTION_ERRORS = (
    # From requests
    Timeout,
    ConnectionError,
    RequestException,
    # From httpx
    ConnectError,
    ConnectTimeout,
    ReadTimeout,
    ReadError,
    NetworkError,
    RemoteProtocolError,
    CloseError,
)


def create_retry_if_connection_error(
    *additional_exceptions,
) -> Callable[[RetryCallState], bool]:
    """Create a retry condition with base connection errors, HTTP status errors, plus additional exceptions."""

    def status_retries_with_exceptions(retry_state: RetryCallState) -> bool:
        if retry_state.outcome is not None and hasattr(
            retry_state.outcome, "exception"
        ):
            exception = retry_state.outcome.exception()
            # connection errors
            if isinstance(exception, _BASE_CONNECTION_ERRORS):
                return True
            # custom exceptions provided
            if additional_exceptions and isinstance(exception, additional_exceptions):
                return True
            # any http exceptions
            if isinstance(exception, HTTPStatusError):
                return exception.response.status_code in RETRYABLE_HTTP_STATUS_CODES
        return False

    return status_retries_with_exceptions


retry_if_connection_error = create_retry_if_connection_error()


async def gather_with_concurrency(
    n: int | asyncio.Semaphore, coros: Iterable[Awaitable[T]], progress: bool = False
) -> list[T]:
    """
    Run asyncio.gather with a concurrency limit.

    SEE: https://stackoverflow.com/a/61478547/2392535
    """
    semaphore = asyncio.Semaphore(n) if isinstance(n, int) else n

    async def sem_coro(coro: Awaitable[T]) -> T:
        async with semaphore:
            return await coro

    if progress:
        return await tqdm.gather(
            *(sem_coro(c) for c in coros), desc="Gathering", ncols=0
        )

    return await asyncio.gather(*(sem_coro(c) for c in coros))
