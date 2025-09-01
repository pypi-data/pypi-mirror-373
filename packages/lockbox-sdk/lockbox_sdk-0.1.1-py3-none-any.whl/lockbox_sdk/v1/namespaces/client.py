from __future__ import annotations

from datetime import datetime
from typing import Any

from httpx import Response, Timeout
from pydantic import TypeAdapter

from lockbox_sdk.client import AsyncBaseClient, BaseClient
from lockbox_sdk.dto import PaginatedResponseDTO
from lockbox_sdk.v1.namespaces.api import NamespacesApi
from lockbox_sdk.v1.namespaces.dto import (
    CreateNamespaceRequestDTO,
    CreateNamespaceResponseDTO,
    GetNamespaceResponseDTO,
)


class AsyncNamespacesClient(AsyncBaseClient):
    async def create_namespace_request(
        self,
        payload: CreateNamespaceRequestDTO,
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
            request=NamespacesApi.create_namespace_request(
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

    async def create_namespace(
        self,
        payload: CreateNamespaceRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> CreateNamespaceResponseDTO:
        """
        Create a new namespace.

        :param payload: The request payload for creating a namespace.
        :type payload: CreateNamespaceRequestDTO
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
        return TypeAdapter(CreateNamespaceResponseDTO).validate_python(
            (await self.create_namespace_request(
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

    async def find_namespaces_request(
        self,
        page: int = 1,
        per_page: int = 10,
        names: list[str] | None = None,
        is_default: bool | None = None,
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
            request=NamespacesApi.find_namespaces_request(
                base_url=self._base_url,
                page=page,
                per_page=per_page,
                names=names,
                is_default=is_default,
                created_before=created_before,
                created_after=created_after,
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

    async def find_namespaces(
        self,
        page: int = 1,
        per_page: int = 10,
        names: list[str] | None = None,
        is_default: bool | None = None,
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
    ) -> PaginatedResponseDTO[GetNamespaceResponseDTO]:
        """
        Find namespaces.

        :param page: The page number to retrieve.
        :type page: int
        :param per_page: The number of items to retrieve per page.
        :type per_page: int
        :param names: A list of namespace names to filter the results.
        :type names: list[str] | None
        :param is_default: Whether to include only default namespaces.
        :type is_default: bool | None
        :param created_before: Only include namespaces created before this date.
        :type created_before: datetime | None
        :param created_after: Only include namespaces created after this date.
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
        return TypeAdapter(PaginatedResponseDTO[GetNamespaceResponseDTO]).validate_python(
            (await self.find_namespaces_request(
                page=page,
                per_page=per_page,
                names=names,
                is_default=is_default,
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

    async def get_namespace_request(
        self,
        name: str,
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
            request=NamespacesApi.get_namespace_request(
                name=name,
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

    async def get_namespace(
        self,
        name: str,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> GetNamespaceResponseDTO:
        """
        Get a namespace by its name.

        :param name: The name of the namespace.
        :type name: str
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
        return TypeAdapter(GetNamespaceResponseDTO).validate_python(
            (await self.get_namespace_request(
                name=name,
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

    async def delete_namespace_request(
        self,
        name: str,
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
            request=NamespacesApi.delete_namespace_request(
                name=name,
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

    async def delete_namespace(
        self,
        name: str,
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
        Delete a namespace by its name.

        :param name: The name of the namespace.
        :type name: str
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
        await self.delete_namespace_request(
            name=name,
            tenant_id=tenant_id,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
            http_query=http_query,
            http_headers=http_headers,
            http_extensions=http_extensions,
        )


class NamespacesClient(BaseClient):
    def create_namespace_request(
        self,
        payload: CreateNamespaceRequestDTO,
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
            request=NamespacesApi.create_namespace_request(
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

    def create_namespace(
        self,
        payload: CreateNamespaceRequestDTO,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> CreateNamespaceResponseDTO:
        """
        Create a new namespace.

        :param payload: The request payload for creating a namespace.
        :type payload: CreateNamespaceRequestDTO
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
        return TypeAdapter(CreateNamespaceResponseDTO).validate_python(
            self.create_namespace_request(
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

    def find_namespaces_request(
        self,
        page: int = 1,
        per_page: int = 10,
        names: list[str] | None = None,
        is_default: bool | None = None,
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
            request=NamespacesApi.find_namespaces_request(
                base_url=self._base_url,
                page=page,
                per_page=per_page,
                names=names,
                is_default=is_default,
                created_before=created_before,
                created_after=created_after,
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

    def find_namespaces(
        self,
        page: int = 1,
        per_page: int = 10,
        names: list[str] | None = None,
        is_default: bool | None = None,
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
    ) -> PaginatedResponseDTO[GetNamespaceResponseDTO]:
        """
        Find namespaces.

        :param page: The page number to retrieve.
        :type page: int
        :param per_page: The number of items to retrieve per page.
        :type per_page: int
        :param names: A list of namespace names to filter the results.
        :type names: list[str] | None
        :param is_default: Whether to include only default namespaces.
        :type is_default: bool | None
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
        return TypeAdapter(PaginatedResponseDTO[GetNamespaceResponseDTO]).validate_python(
            self.find_namespaces_request(
                page=page,
                per_page=per_page,
                names=names,
                is_default=is_default,
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

    def get_namespace_request(
        self,
        name: str,
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
            request=NamespacesApi.get_namespace_request(
                name=name,
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

    def get_namespace(
        self,
        name: str,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> GetNamespaceResponseDTO:
        """
        Get a namespace by its name.

        :param name: The name of the namespace.
        :type name: str
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
        return TypeAdapter(GetNamespaceResponseDTO).validate_python(
            self.get_namespace_request(
                name=name,
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

    def delete_namespace_request(
        self,
        name: str,
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
            request=NamespacesApi.delete_namespace_request(
                name=name,
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

    def delete_namespace(
        self,
        name: str,
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
        Delete a namespace by its name.

        :param name: The name of the namespace.
        :type name: str
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
        self.delete_namespace_request(
            name=name,
            tenant_id=tenant_id,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            timeout=timeout,
            http_query=http_query,
            http_headers=http_headers,
            http_extensions=http_extensions,
        )
