from __future__ import annotations

from httpx import AsyncClient, Client

from lockbox_sdk.v1.api_keys.client import ApiKeysClient, AsyncApiKeysClient
from lockbox_sdk.v1.namespaces.client import AsyncNamespacesClient, NamespacesClient
from lockbox_sdk.v1.tags.client import AsyncTagsClient, TagsClient


class AsyncV1Client:
    def __init__(
        self,
        client: AsyncClient,
        base_url: str,
        user_agent: str | None = None,
    ) -> None:
        self._api_keys = AsyncApiKeysClient(
            client=client,
            base_url=base_url,
            user_agent=user_agent
        )
        self._namespaces = AsyncNamespacesClient(
            client=client,
            base_url=base_url,
            user_agent=user_agent
        )
        self._tags = AsyncTagsClient(
            client=client,
            base_url=base_url,
            user_agent=user_agent
        )

    @property
    def api_keys(self) -> AsyncApiKeysClient:
        """
        The API keys client for managing API keys.
        """
        return self._api_keys

    @property
    def namespaces(self) -> AsyncNamespacesClient:
        """
        The namespaces client for managing namespaces.
        """
        return self._namespaces

    @property
    def tags(self) -> AsyncTagsClient:
        """
        The tags client for managing tags.
        """
        return self._tags


class V1Client:
    def __init__(
        self,
        client: Client,
        base_url: str,
        user_agent: str | None = None,
    ) -> None:
        self._api_keys = ApiKeysClient(
            client=client,
            base_url=base_url,
            user_agent=user_agent
        )
        self._namespaces = NamespacesClient(
            client=client,
            base_url=base_url,
            user_agent=user_agent
        )
        self._tags = TagsClient(
            client=client,
            base_url=base_url,
            user_agent=user_agent
        )

    @property
    def api_keys(self) -> ApiKeysClient:
        """
        The API keys client for managing API keys.
        """
        return self._api_keys

    @property
    def namespaces(self) -> NamespacesClient:
        """
        The namespaces client for managing namespaces.
        """
        return self._namespaces

    @property
    def tags(self) -> TagsClient:
        """
        The tags client for managing tags.
        """
        return self._tags
