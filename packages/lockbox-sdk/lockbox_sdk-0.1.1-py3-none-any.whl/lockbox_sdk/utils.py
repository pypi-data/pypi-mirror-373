from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence
from datetime import datetime
from typing import Awaitable, Callable, TypeVar
from urllib.parse import urlencode, urljoin

from httpx import ConnectError, ConnectTimeout

from lockbox_sdk.error import ApiError


R = TypeVar("R")


def compute_exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> float:
    """
    Compute the exponential backoff delay.

    :param attempt: The current retry attempt number.
    :type attempt: int
    :param base_delay: The base delay (in seconds) for the first retry.
    :type base_delay: float
    :param max_delay: The maximum delay (in seconds) for any retry.
    :type max_delay: float
    :return: The computed backoff delay.
    :rtype: float
    """
    return min(base_delay * (2 ** attempt), max_delay)


async def async_retry(
    func: Callable[..., Awaitable[R]],
    should_retry: Callable[[Exception], bool] = lambda _: True,
    calculate_delay: Callable[[int, Exception], float] = lambda attempt, _: (
        compute_exponential_backoff(attempt, base_delay=1.0, max_delay=60.0)
    ),
    max_retries: int = 3,
) -> R:
    """
    Retry an asynchronous function given callbacks for error handling and delay calculation.

    :param func: The asynchronous function to retry.
    :type func: Callable[..., Awaitable[R]]
    :param should_retry: A callback to determine if the function should be retried.
    :type should_retry: Callable[[Exception], bool]
    :param calculate_delay: A callback to calculate the delay before the next retry.
    :type calculate_delay: Callable[[int, Exception], float]
    :param max_retries: The maximum number of retry attempts.
    :type max_retries: int
    :return: The result of the successful function call.
    :rtype: R
    :raises RuntimeError: If the maximum number of retries is exceeded.
    """
    max_retries = max(max_retries, 0)
    retries = 0

    while retries < max_retries:
        try:
            return await func()
        except Exception as e:
            if retries == max_retries - 1 or not should_retry(e):
                raise

            retries += 1
            await asyncio.sleep(calculate_delay(retries, e))

    raise RuntimeError("max retries exceeded")


def retry(
    func: Callable[..., R],
    should_retry: Callable[[Exception], bool] = lambda _: True,
    calculate_delay: Callable[[int, Exception], float] = lambda attempt, _: (
        compute_exponential_backoff(attempt, base_delay=1.0, max_delay=60.0)
    ),
    max_retries: int = 3,
) -> R:
    """
    Retry a synchronous function given callbacks for error handling and delay calculation.

    :param func: The synchronous function to retry.
    :type func: Callable[..., R]
    :param should_retry: A callback to determine if the function should be retried.
    :type should_retry: Callable[[Exception], bool]
    :param calculate_delay: A callback to calculate the delay before the next retry.
    :type calculate_delay: Callable[[int, Exception], float]
    :param max_retries: The maximum number of retry attempts.
    :type max_retries: int
    :return: The result of the successful function call.
    :rtype: R
    :raises RuntimeError: If the maximum number of retries is exceeded.
    """
    max_retries = max(max_retries, 0)
    retries = 0

    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            if retries == max_retries - 1 or not should_retry(e):
                raise

            retries += 1
            time.sleep(calculate_delay(retries, e))

    raise RuntimeError("max retries exceeded")


def build_url(
    base_url: str,
    path: str | None = None,
    query: dict | None = None,
    params: dict | None = None,
) -> str:
    """
    Build a full URL given the base URL, path, query parameters, and path parameters.

    :param base_url: The base URL.
    :type base_url: str
    :param path: The path to append to the base URL.
    :type path: str | None
    :param query: Query parameters to include in the URL.
    :type query: dict | None
    :param params: Path parameters to include in the URL.
    :type params: dict | None
    :return: The full URL.
    :rtype: str
    """
    params = {k: str(v) for k, v in (params or {}).items()}
    url = urljoin(base_url, path.format(**params)) if path else base_url

    if query:
        query_parts = []

        for k, v in query.items():
            if v is None:
                continue

            if isinstance(v, dict):
                query_parts.extend([(f"{k}[{key}]", str(value)) for key, value in v.items()])
            elif isinstance(v, Sequence) and not isinstance(v, str):
                query_parts.extend([(f"{k}[]", str(item)) for item in v])
            else:
                query_parts.append((k, str(v)))

        url += "?" + urlencode(query_parts, doseq=True)

    return url


def build_accept_header(accepted_types: list[tuple[str, float]]) -> str:
    """
    Build a full Accept header given all of the accepted content type strings
    and their quality values.

    :return: The full Accept header.
    :rtype: str
    """
    return ", ".join(
        f"{content_type}{f'; q={quality}' if quality < 1.0 else ''}"
        for content_type, quality in accepted_types
    )


def is_retryable_error(error: Exception) -> bool:
    """
    Check if an error from a request is retryable.

    :param error: The error to check.
    :type error: Exception
    :return: True if the error is retryable, False otherwise.
    :rtype: bool
    """
    return (
        (isinstance(error, ApiError) and 500 <= error.response.status_code < 600)
        or isinstance(error, (ConnectError, ConnectTimeout, TimeoutError))
    )

def calculate_delay(
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> Callable[[int, Exception], float]:
    """
    Calculate the delay before the next retry attempt.

    :param base_delay: The base delay before the first retry.
    :type base_delay: float
    :param max_delay: The maximum delay between retries.
    :type max_delay: float
    :return: A function that calculates the delay for each retry attempt.
    :rtype: Callable[[int, Exception], float]
    """
    def inner(attempt: int, error: Exception) -> float:
        return (
            float(retry_after)
            if (
                isinstance(error, ApiError)
                and (retry_after := error.response.headers.get("retry-after")) is not None
            )
            else
            compute_exponential_backoff(
                attempt,
                base_delay=base_delay,
                max_delay=max_delay
            )
        )
    return inner


def rfc3339_datetime(dt: datetime) -> str:
    """
    Convert a datetime object to a string in RFC 3339 format.

    :param dt: The datetime object to convert.
    :type dt: datetime
    :return: The RFC 3339 formatted string.
    :rtype: str
    """
    if not isinstance(dt, datetime):
        raise TypeError("Expected a datetime object")

    return dt.isoformat().replace("+00:00", "Z")
