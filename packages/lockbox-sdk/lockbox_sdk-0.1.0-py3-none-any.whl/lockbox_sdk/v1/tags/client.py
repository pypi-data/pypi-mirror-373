from __future__ import annotations

from datetime import datetime
from typing import Any

from httpx import Response, Timeout
from pydantic import TypeAdapter

from lockbox_sdk.client import AsyncBaseClient, BaseClient
from lockbox_sdk.dto import PaginatedResponseDTO
from lockbox_sdk.v1.tags.api import TagsApi
from lockbox_sdk.v1.tags.dto import (
    CreateTagRequestDTO,
    CreateTagResponseDTO,
    GetTagResponseDTO,
)


class AsyncTagsClient(AsyncBaseClient):
    async def create_tag_request(
        self,
        payload: CreateTagRequestDTO,
        namespace: str,
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
            request=TagsApi.create_tag_request(
                payload=payload,
                namespace=namespace,
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

    async def create_tag(
        self,
        payload: CreateTagRequestDTO,
        namespace: str,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> CreateTagResponseDTO:
        """
        Create a new tag in a given namespace.

        :param payload: The request payload for creating a tag.
        :type payload: CreateTagRequestDTO
        :param namespace: The namespace in which to create the tag.
        :type namespace: str
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
        return TypeAdapter(CreateTagResponseDTO).validate_python(
            (await self.create_tag_request(
                payload=payload,
                namespace=namespace,
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

    async def find_tags_request(
        self,
        namespace: str,
        page: int = 1,
        per_page: int = 10,
        names: list[str] | None = None,
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
            request=TagsApi.find_tags_request(
                namespace=namespace,
                base_url=self._base_url,
                page=page,
                per_page=per_page,
                names=names,
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

    async def find_tags(
        self,
        namespace: str,
        page: int = 1,
        per_page: int = 10,
        names: list[str] | None = None,
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
    ) -> PaginatedResponseDTO[GetTagResponseDTO]:
        """
        Find tags in a namespace.

        :param namespace: The namespace to search within.
        :type namespace: str
        :param page: The page number to retrieve.
        :type page: int
        :param per_page: The number of items to retrieve per page.
        :type per_page: int
        :param names: A list of tag names to filter the results.
        :type names: list[str] | None
        :param created_before: Only include tags created before this date.
        :type created_before: datetime | None
        :param created_after: Only include tags created after this date.
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
        return TypeAdapter(PaginatedResponseDTO[GetTagResponseDTO]).validate_python(
            (await self.find_tags_request(
                namespace=namespace,
                page=page,
                per_page=per_page,
                names=names,
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

    async def get_tag_request(
        self,
        namespace: str,
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
            request=TagsApi.get_tag_request(
                namespace=namespace,
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

    async def get_tag(
        self,
        namespace: str,
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
    ) -> GetTagResponseDTO:
        """
        Get a tag by its name in a namespace.

        :param namespace: The name of the namespace.
        :type namespace: str
        :param name: The name of the tag.
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
        return TypeAdapter(GetTagResponseDTO).validate_python(
            (await self.get_tag_request(
                namespace=namespace,
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

    async def delete_tag_request(
        self,
        namespace: str,
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
            request=TagsApi.delete_tag_request(
                namespace=namespace,
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

    async def delete_tag(
        self,
        namespace: str,
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
        Delete a tag by its name in a namespace.

        :param namespace: The name of the namespace.
        :type namespace: str
        :param name: The name of the tag.
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
        await self.delete_tag_request(
            namespace=namespace,
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


class TagsClient(BaseClient):
    def create_tag_request(
        self,
        payload: CreateTagRequestDTO,
        namespace: str,
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
            request=TagsApi.create_tag_request(
                payload=payload,
                namespace=namespace,
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

    def create_tag(
        self,
        payload: CreateTagRequestDTO,
        namespace: str,
        *,
        tenant_id: str | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> CreateTagResponseDTO:
        """
        Create a new tag in a given namespace.

        :param payload: The request payload for creating a tag.
        :type payload: CreateTagRequestDTO
        :param namespace: The namespace in which to create the tag.
        :type namespace: str
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
        return TypeAdapter(CreateTagResponseDTO).validate_python(
            self.create_tag_request(
                payload=payload,
                namespace=namespace,
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

    def find_tags_request(
        self,
        namespace: str,
        page: int = 1,
        per_page: int = 10,
        names: list[str] | None = None,
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
            request=TagsApi.find_tags_request(
                namespace=namespace,
                base_url=self._base_url,
                page=page,
                per_page=per_page,
                names=names,
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

    def find_tags(
        self,
        namespace: str,
        page: int = 1,
        per_page: int = 10,
        names: list[str] | None = None,
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
    ) -> PaginatedResponseDTO[GetTagResponseDTO]:
        """
        Find tags in a namespace.

        :param namespace: The namespace to search within.
        :type namespace: str
        :param page: The page number to retrieve.
        :type page: int
        :param per_page: The number of items to retrieve per page.
        :type per_page: int
        :param names: A list of tag names to filter the results.
        :type names: list[str] | None
        :param created_before: Only include tags created before this date.
        :type created_before: datetime | None
        :param created_after: Only include tags created after this date.
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
        return TypeAdapter(PaginatedResponseDTO[GetTagResponseDTO]).validate_python(
            self.find_tags_request(
                namespace=namespace,
                page=page,
                per_page=per_page,
                names=names,
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

    def get_tag_request(
        self,
        namespace: str,
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
            request=TagsApi.get_tag_request(
                namespace=namespace,
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

    def get_tag(
        self,
        namespace: str,
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
    ) -> GetTagResponseDTO:
        """
        Get a tag by its name in a namespace.

        :param namespace: The name of the namespace.
        :type namespace: str
        :param name: The name of the tag.
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
        return TypeAdapter(GetTagResponseDTO).validate_python(
            self.get_tag_request(
                namespace=namespace,
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

    def delete_tag_request(
        self,
        namespace: str,
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
            request=TagsApi.delete_tag_request(
                namespace=namespace,
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

    def delete_tag(
        self,
        namespace: str,
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
        Delete a tag by its name in a namespace.

        :param namespace: The name of the namespace.
        :type namespace: str
        :param name: The name of the tag.
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
        self.delete_tag_request(
            namespace=namespace,
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
