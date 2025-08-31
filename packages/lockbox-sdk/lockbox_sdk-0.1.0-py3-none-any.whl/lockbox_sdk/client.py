from __future__ import annotations

from httpx import AsyncClient, Client, Request, Response

from lockbox_sdk.error import to_api_error, to_api_error_async
from lockbox_sdk.utils import async_retry, calculate_delay, is_retryable_error, retry


class AsyncBaseClient:
    def __init__(
        self,
        client: AsyncClient,
        base_url: str,
        user_agent: str | None = None,
    ) -> None:
        self._client = client
        self._base_url = base_url
        self._user_agent = user_agent

    @to_api_error_async
    async def send_request(
        self,
        request: Request,
        *,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ) -> Response:
        async def inner() -> Response:
            response = await self._client.send(request)
            response.raise_for_status()
            return response

        return await async_retry(
            inner,
            should_retry=is_retryable_error,
            calculate_delay=calculate_delay(base_delay=base_delay, max_delay=max_delay),
            max_retries=max_retries,
        )


class BaseClient:
    def __init__(
        self,
        client: Client,
        base_url: str,
        user_agent: str | None = None,
    ) -> None:
        self._client = client
        self._base_url = base_url
        self._user_agent = user_agent

    @to_api_error
    def send_request(
        self,
        request: Request,
        *,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ) -> Response:
        def inner() -> Response:
            response = self._client.send(request)
            response.raise_for_status()
            return response

        return retry(
            inner,
            should_retry=is_retryable_error,
            calculate_delay=calculate_delay(base_delay=base_delay, max_delay=max_delay),
            max_retries=max_retries,
        )
