from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from httpx import Response, Timeout
from pydantic import TypeAdapter

from lockbox_sdk.client import AsyncBaseClient, BaseClient
from lockbox_sdk.dto import PaginatedResponseDTO
from lockbox_sdk.v1.api_keys.api import ApiKeysApi
from lockbox_sdk.v1.api_keys.dto import (
    CreateApiKeyRequestDTO,
    CreateApiKeyResponseDTO,
    GetApiKeyResponseDTO,
    IntrospectApiKeyRequestDTO,
    IntrospectApiKeyResponseDTO,
    SetApiKeyExpirationRequestDTO,
    SetApiKeyMetadataRequestDTO,
)


class AsyncApiKeysClient(AsyncBaseClient):
    async def create_api_key_request(
        self,
        payload: CreateApiKeyRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return await self.send_request(
            request=ApiKeysApi.create_api_key_request(
                payload=payload,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    async def create_api_key(
        self,
        payload: CreateApiKeyRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> CreateApiKeyResponseDTO:
        """
        Create a new API key.

        :param payload: The request payload for creating an API key.
        :type payload: CreateApiKeyRequestDTO
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        return TypeAdapter(CreateApiKeyResponseDTO).validate_python(
            (await self.create_api_key_request(
                payload=payload,
                tenant_id=tenant_id,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                timeout=timeout,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions=http_extensions,
            )).json()
        )

    async def find_api_keys_request(
        self,
        page: int = 1,
        per_page: int = 10,
        include_ids: list[UUID] | None = None,
        exclude_ids: list[UUID] | None = None,
        namespaces: list[str] | None = None,
        tags: list[str] | None = None,
        short_keys: list[str] | None = None,
        owners: list[str] | None = None,
        revoked: bool | None = None,
        metadata: dict[str, Any] | None = None,
        created_before: datetime | None = None,
        created_after: datetime | None = None,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return await self.send_request(
            request=ApiKeysApi.find_api_keys_request(
                page=page,
                per_page=per_page,
                include_ids=include_ids,
                exclude_ids=exclude_ids,
                namespaces=namespaces,
                tags=tags,
                short_keys=short_keys,
                owners=owners,
                revoked=revoked,
                metadata=metadata,
                created_before=created_before,
                created_after=created_after,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    async def find_api_keys(
        self,
        page: int = 1,
        per_page: int = 10,
        include_ids: list[UUID] | None = None,
        exclude_ids: list[UUID] | None = None,
        namespaces: list[str] | None = None,
        tags: list[str] | None = None,
        short_keys: list[str] | None = None,
        owners: list[str] | None = None,
        revoked: bool | None = None,
        metadata: dict[str, Any] | None = None,
        created_before: datetime | None = None,
        created_after: datetime | None = None,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> PaginatedResponseDTO[GetApiKeyResponseDTO]:
        """
        Find API keys.

        :param page: The page number to retrieve.
        :type page: int
        :param per_page: The number of items to retrieve per page.
        :type per_page: int
        :param include_ids: A list of API key IDs to include in the response.
        :type include_ids: list[UUID] | None
        :param exclude_ids: A list of API key IDs to exclude from the response.
        :type exclude_ids: list[UUID] | None
        :param namespaces: A list of namespaces to filter the API keys.
        :type namespaces: list[str] | None
        :param tags: A list of tags to filter the API keys.
        :type tags: list[str] | None
        :param short_keys: A list of short keys to filter the API keys.
        :type short_keys: list[str] | None
        :param owners: A list of owners to filter the API keys.
        :type owners: list[str] | None
        :param revoked: Whether to include revoked API keys.
        :type revoked: bool | None
        :param metadata: Metadata to filter the API keys.
        :type metadata: dict[str, Any] | None
        :param created_before: Only include API keys created before this date.
        :type created_before: datetime | None
        :param created_after: Only include API keys created after this date.
        :type created_after: datetime | None
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        return TypeAdapter(PaginatedResponseDTO[GetApiKeyResponseDTO]).validate_python(
            (await self.find_api_keys_request(
                page=page,
                per_page=per_page,
                include_ids=include_ids,
                exclude_ids=exclude_ids,
                namespaces=namespaces,
                tags=tags,
                short_keys=short_keys,
                owners=owners,
                revoked=revoked,
                metadata=metadata,
                created_before=created_before,
                created_after=created_after,
                tenant_id=tenant_id,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                timeout=timeout,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions=http_extensions,
            )).json()
        )

    async def introspect_api_key_request(
        self,
        payload: IntrospectApiKeyRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return await self.send_request(
            request=ApiKeysApi.introspect_api_key_request(
                payload=payload,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    async def introspect_api_key(
        self,
        payload: IntrospectApiKeyRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> IntrospectApiKeyResponseDTO:
        """
        Introspect an API key.

        :param payload: The request payload for introspecting an API key.
        :type payload: IntrospectApiKeyRequestDTO
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        return TypeAdapter(IntrospectApiKeyResponseDTO).validate_python(
            (await self.introspect_api_key_request(
                payload=payload,
                tenant_id=tenant_id,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                timeout=timeout,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions=http_extensions,
            )).json()
        )

    async def get_api_key_request(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return await self.send_request(
            request=ApiKeysApi.get_api_key_request(
                id=id,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    async def get_api_key(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> GetApiKeyResponseDTO:
        """
        Get an API key by its ID.

        :param id: The ID of the API key.
        :type id: UUID
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        return TypeAdapter(GetApiKeyResponseDTO).validate_python(
            (await self.get_api_key_request(
                id=id,
                tenant_id=tenant_id,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                timeout=timeout,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions=http_extensions,
            )).json()
        )

    async def delete_api_key_request(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return await self.send_request(
            request=ApiKeysApi.delete_api_key_request(
                id=id,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    async def delete_api_key(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> None:
        """
        Delete an API key by its ID.

        :param id: The ID of the API key.
        :type id: UUID
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        await self.delete_api_key_request(
            id=id,
            tenant_id=tenant_id,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
            http_query=http_query,
            http_headers=http_headers,
            http_extensions=http_extensions,
        )

    async def revoke_api_key_request(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return await self.send_request(
            request=ApiKeysApi.revoke_api_key_request(
                id=id,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    async def revoke_api_key(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> None:
        """
        Revoke an API key by its ID.

        :param id: The ID of the API key.
        :type id: UUID
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        await self.revoke_api_key_request(
            id=id,
            tenant_id=tenant_id,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
            http_query=http_query,
            http_headers=http_headers,
            http_extensions=http_extensions,
        )

    async def rotate_api_key_request(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return await self.send_request(
            request=ApiKeysApi.rotate_api_key_request(
                id=id,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    async def rotate_api_key(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> CreateApiKeyResponseDTO:
        """
        Rotate an API key by its ID.

        :param id: The ID of the API key.
        :type id: UUID
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        return TypeAdapter(CreateApiKeyResponseDTO).validate_python(
            (await self.rotate_api_key_request(
                id=id,
                tenant_id=tenant_id,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                timeout=timeout,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions=http_extensions,
            )).json()
        )

    async def set_api_key_expiration_request(
        self,
        id: UUID,
        payload: SetApiKeyExpirationRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return await self.send_request(
            request=ApiKeysApi.set_api_key_expiration(
                id=id,
                payload=payload,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    async def set_api_key_expiration(
        self,
        id: UUID,
        payload: SetApiKeyExpirationRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> None:
        """
        Set the expiration date for an API key.

        :param id: The ID of the API key.
        :type id: UUID
        :param payload: The request payload for setting the API key expiration.
        :type payload: SetApiKeyExpirationRequestDTO
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        await self.set_api_key_expiration_request(
            id=id,
            payload=payload,
            tenant_id=tenant_id,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
            http_query=http_query,
            http_headers=http_headers,
            http_extensions=http_extensions,
        )

    async def set_api_key_metadata_request(
        self,
        id: UUID,
        payload: SetApiKeyMetadataRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return await self.send_request(
            request=ApiKeysApi.set_api_key_metadata(
                id=id,
                payload=payload,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    async def set_api_key_metadata(
        self,
        id: UUID,
        payload: SetApiKeyMetadataRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> None:
        """
        Set the metadata for an API key.

        :param id: The ID of the API key.
        :type id: UUID
        :param payload: The request payload for setting the API key metadata.
        :type payload: SetApiKeyMetadataRequestDTO
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        await self.set_api_key_metadata(
            id=id,
            payload=payload,
            tenant_id=tenant_id,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
            http_query=http_query,
            http_headers=http_headers,
            http_extensions=http_extensions,
        )


class ApiKeysClient(BaseClient):
    def create_api_key_request(
        self,
        payload: CreateApiKeyRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return self.send_request(
            request=ApiKeysApi.create_api_key_request(
                payload=payload,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    async def create_api_key(
        self,
        payload: CreateApiKeyRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> CreateApiKeyResponseDTO:
        """
        Create a new API key.

        :param payload: The request payload for creating an API key.
        :type payload: CreateApiKeyRequestDTO
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        return TypeAdapter(CreateApiKeyResponseDTO).validate_python(
            self.create_api_key_request(
                payload=payload,
                tenant_id=tenant_id,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                timeout=timeout,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions=http_extensions,
            ).json()
        )

    def find_api_keys_request(
        self,
        page: int = 1,
        per_page: int = 10,
        include_ids: list[UUID] | None = None,
        exclude_ids: list[UUID] | None = None,
        namespaces: list[str] | None = None,
        tags: list[str] | None = None,
        short_keys: list[str] | None = None,
        owners: list[str] | None = None,
        revoked: bool | None = None,
        metadata: dict[str, Any] | None = None,
        created_before: datetime | None = None,
        created_after: datetime | None = None,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return self.send_request(
            request=ApiKeysApi.find_api_keys_request(
                page=page,
                per_page=per_page,
                include_ids=include_ids,
                exclude_ids=exclude_ids,
                namespaces=namespaces,
                tags=tags,
                short_keys=short_keys,
                owners=owners,
                revoked=revoked,
                metadata=metadata,
                created_before=created_before,
                created_after=created_after,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    def find_api_keys(
        self,
        page: int = 1,
        per_page: int = 10,
        include_ids: list[UUID] | None = None,
        exclude_ids: list[UUID] | None = None,
        namespaces: list[str] | None = None,
        tags: list[str] | None = None,
        short_keys: list[str] | None = None,
        owners: list[str] | None = None,
        revoked: bool | None = None,
        metadata: dict[str, Any] | None = None,
        created_before: datetime | None = None,
        created_after: datetime | None = None,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> PaginatedResponseDTO[GetApiKeyResponseDTO]:
        """
        Find API keys.

        :param page: The page number to retrieve.
        :type page: int
        :param per_page: The number of items to retrieve per page.
        :type per_page: int
        :param include_ids: A list of API key IDs to include in the response.
        :type include_ids: list[UUID] | None
        :param exclude_ids: A list of API key IDs to exclude from the response.
        :type exclude_ids: list[UUID] | None
        :param namespaces: A list of namespaces to filter the API keys.
        :type namespaces: list[str] | None
        :param tags: A list of tags to filter the API keys.
        :type tags: list[str] | None
        :param short_keys: A list of short keys to filter the API keys.
        :type short_keys: list[str] | None
        :param owners: A list of owners to filter the API keys.
        :type owners: list[str] | None
        :param revoked: Whether to include revoked API keys.
        :type revoked: bool | None
        :param metadata: Metadata to filter the API keys.
        :type metadata: dict[str, Any] | None
        :param created_before: Only include API keys created before this date.
        :type created_before: datetime | None
        :param created_after: Only include API keys created after this date.
        :type created_after: datetime | None
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        return TypeAdapter(PaginatedResponseDTO[GetApiKeyResponseDTO]).validate_python(
            self.find_api_keys_request(
                page=page,
                per_page=per_page,
                include_ids=include_ids,
                exclude_ids=exclude_ids,
                namespaces=namespaces,
                tags=tags,
                short_keys=short_keys,
                owners=owners,
                revoked=revoked,
                metadata=metadata,
                created_before=created_before,
                created_after=created_after,
                tenant_id=tenant_id,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                timeout=timeout,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions=http_extensions,
            ).json()
        )

    def introspect_api_key_request(
        self,
        payload: IntrospectApiKeyRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return self.send_request(
            request=ApiKeysApi.introspect_api_key_request(
                payload=payload,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    def introspect_api_key(
        self,
        payload: IntrospectApiKeyRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> IntrospectApiKeyResponseDTO:
        """
        Introspect an API key.

        :param payload: The request payload for introspecting an API key.
        :type payload: IntrospectApiKeyRequestDTO
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        return TypeAdapter(IntrospectApiKeyResponseDTO).validate_python(
            self.introspect_api_key_request(
                payload=payload,
                tenant_id=tenant_id,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                timeout=timeout,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions=http_extensions,
            ).json()
        )

    def get_api_key_request(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return self.send_request(
            request=ApiKeysApi.get_api_key_request(
                id=id,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    def get_api_key(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> GetApiKeyResponseDTO:
        """
        Get an API key by its ID.

        :param id: The ID of the API key.
        :type id: UUID
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        return TypeAdapter(GetApiKeyResponseDTO).validate_python(
            self.get_api_key_request(
                id=id,
                tenant_id=tenant_id,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                timeout=timeout,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions=http_extensions,
            ).json()
        )

    def delete_api_key_request(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return self.send_request(
            request=ApiKeysApi.delete_api_key_request(
                id=id,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    def delete_api_key(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> None:
        """
        Delete an API key by its ID.

        :param id: The ID of the API key.
        :type id: UUID
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        self.delete_api_key_request(
            id=id,
            tenant_id=tenant_id,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
            http_query=http_query,
            http_headers=http_headers,
            http_extensions=http_extensions,
        )

    def revoke_api_key_request(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return self.send_request(
            request=ApiKeysApi.revoke_api_key_request(
                id=id,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    def revoke_api_key(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> None:
        """
        Revoke an API key by its ID.

        :param id: The ID of the API key.
        :type id: UUID
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        self.revoke_api_key_request(
            id=id,
            tenant_id=tenant_id,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
            http_query=http_query,
            http_headers=http_headers,
            http_extensions=http_extensions,
        )

    def rotate_api_key_request(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return self.send_request(
            request=ApiKeysApi.rotate_api_key_request(
                id=id,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    def rotate_api_key(
        self,
        id: UUID,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> CreateApiKeyResponseDTO:
        """
        Rotate an API key by its ID.

        :param id: The ID of the API key.
        :type id: UUID
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        return TypeAdapter(CreateApiKeyResponseDTO).validate_python(
            self.rotate_api_key_request(
                id=id,
                tenant_id=tenant_id,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                timeout=timeout,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions=http_extensions,
            ).json()
        )

    def set_api_key_expiration_request(
        self,
        id: UUID,
        payload: SetApiKeyExpirationRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return self.send_request(
            request=ApiKeysApi.set_api_key_expiration(
                id=id,
                payload=payload,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    def set_api_key_expiration(
        self,
        id: UUID,
        payload: SetApiKeyExpirationRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> None:
        """
        Set the expiration date for an API key.

        :param id: The ID of the API key.
        :type id: UUID
        :param payload: The request payload for setting the API key expiration.
        :type payload: SetApiKeyExpirationRequestDTO
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        self.set_api_key_expiration_request(
            id=id,
            payload=payload,
            tenant_id=tenant_id,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
            http_query=http_query,
            http_headers=http_headers,
            http_extensions=http_extensions,
        )

    def set_api_key_metadata_request(
        self,
        id: UUID,
        payload: SetApiKeyMetadataRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Response:
        return self.send_request(
            request=ApiKeysApi.set_api_key_metadata(
                id=id,
                payload=payload,
                base_url=self._base_url,
                tenant_id=tenant_id,
                user_agent=self._user_agent,
                http_query=http_query,
                http_headers=http_headers,
                http_extensions={
                    **(http_extensions or {}),
                    **({"timeout": Timeout(timeout).as_dict()} if timeout else {}),
                },
            ),
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    def set_api_key_metadata(
        self,
        id: UUID,
        payload: SetApiKeyMetadataRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> None:
        """
        Set the metadata for an API key.

        :param id: The ID of the API key.
        :type id: UUID
        :param payload: The request payload for setting the API key metadata.
        :type payload: SetApiKeyMetadataRequestDTO
        :param tenant_id: The ID of the tenant.
        :type tenant_id: str | None
        :param max_retries: The maximum number of retries for the request.
        :type max_retries: int
        :param base_delay: The base delay between retries.
        :type base_delay: float
        :param max_delay: The maximum delay between retries.
        :type max_delay: float
        :param timeout: The timeout for the request.
        :type timeout: float | None
        :param http_query: Additional query parameters for the request.
        :type http_query: dict[str, Any] | None
        :param http_headers: Additional headers for the request.
        :type http_headers: dict[str, Any] | None
        :param http_extensions: Additional extensions for the request.
        :type http_extensions: dict[str, Any] | None
        """
        self.set_api_key_metadata(
            id=id,
            payload=payload,
            tenant_id=tenant_id,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
            http_query=http_query,
            http_headers=http_headers,
            http_extensions=http_extensions,
        )
