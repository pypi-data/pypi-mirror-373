from __future__ import annotations

from typing import Any

from httpx import AsyncClient, Client

from lockbox_sdk.v1.client import AsyncV1Client, V1Client


class AsyncLockboxSdk:
    def __init__(
        self,
        base_url: str,
        verify_ssl: bool = True,
        timeout: float | None = None,
        follow_redirects: bool = True,
        client: AsyncClient | None = None,
        **kwargs: Any,
    ) -> None:
        self._client = client or AsyncClient(
            base_url=base_url,
            verify=verify_ssl,
            timeout=timeout,
            follow_redirects=follow_redirects,
            **kwargs,
        )
        self._base_url = base_url
        self._v1 = AsyncV1Client(
            client=self._client,
            base_url=base_url
        )

    @property
    def client(self) -> AsyncClient:
        """
        The HTTP client used for making Api requests.
        """
        return self._client

    @property
    def base_url(self) -> str:
        """
        The base URL for the Api.
        """
        return self._base_url

    @property
    def v1(self) -> AsyncV1Client:
        """
        The v1 client for making Api requests.
        """
        return self._v1

    async def __aenter__(self) -> AsyncLockboxSdk:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()

    async def close(self) -> None:
        """
        Close the client connection.
        """
        await self._client.aclose()


class LockboxSdk:
    def __init__(
        self,
        base_url: str,
        verify_ssl: bool = True,
        timeout: float | None = None,
        follow_redirects: bool = True,
        client: Client | None = None,
        **kwargs: Any,
    ) -> None:
        self._client = client or Client(
            base_url=base_url,
            verify=verify_ssl,
            timeout=timeout,
            follow_redirects=follow_redirects,
            **kwargs,
        )
        self._base_url = base_url
        self._v1 = V1Client(
            client=self._client,
            base_url=base_url
        )

    @property
    def client(self) -> Client:
        """
        The HTTP client used for making Api requests.
        """
        return self._client

    @property
    def base_url(self) -> str:
        """
        The base URL for the Api.
        """
        return self._base_url

    @property
    def v1(self) -> V1Client:
        """
        The v1 client for making Api requests.
        """
        return self._v1

    def __enter__(self) -> LockboxSdk:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        """
        Close the client connection.
        """
        self._client.close()
