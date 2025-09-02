from __future__ import annotations

from datetime import datetime
from typing import Any

from httpx import Request

from lockbox_sdk.utils import build_accept_header, build_url, rfc3339_datetime
from lockbox_sdk.v1.tags.dto import (
    CreateTagRequestDTO,
    CreateTagResponseDTO,
    GetTagResponseDTO,
)


class TagsApi:
    @staticmethod
    def create_tag_request(
        payload: CreateTagRequestDTO,
        namespace: str,
        base_url: str,
        *,
        tenant_id: str | None = None,
        user_agent: str | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Request:
        return Request(
            method="POST",
            url=build_url(base_url, f"/v1/namespaces/{namespace}/tags", query=http_query),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                "Content-Type": payload.__content_type__,
                "Accept": build_accept_header([(CreateTagResponseDTO.__content_type__, 1.0)]),
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
            content=payload.to_request_body(),
        )

    @staticmethod
    def find_tags_request(
        namespace: str,
        base_url: str,
        page: int = 1,
        per_page: int = 10,
        names: list[str] | None = None,
        created_before: datetime | None = None,
        created_after: datetime | None = None,
        *,
        tenant_id: str | None = None,
        user_agent: str | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Request:
        return Request(
            method="GET",
            url=build_url(base_url, f"/v1/namespaces/{namespace}/tags", query={
                **(
                    http_query
                    if isinstance(http_query, dict)
                    else dict(http_query or {})
                ),
                "page": page,
                "per_page": per_page,
                **({"names": names} if names else {}),
                **({"created_before": rfc3339_datetime(created_before)} if created_before else {}),
                **({"created_after": rfc3339_datetime(created_after)} if created_after else {}),
            }),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                "Accept": build_accept_header([(GetTagResponseDTO.__content_type__, 1.0)]),
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
        )

    @staticmethod
    def get_tag_request(
        namespace: str,
        name: str,
        base_url: str,
        *,
        tenant_id: str | None = None,
        user_agent: str | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Request:
        return Request(
            method="GET",
            url=build_url(base_url, f"/v1/namespaces/{namespace}/tags/{name}", query=http_query),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                "Accept": build_accept_header([(GetTagResponseDTO.__content_type__, 1.0)]),
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
        )

    @staticmethod
    def delete_tag_request(
        namespace: str,
        name: str,
        base_url: str,
        *,
        tenant_id: str | None = None,
        user_agent: str | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Request:
        return Request(
            method="DELETE",
            url=build_url(base_url, f"/v1/namespaces/{namespace}/tags/{name}", query=http_query),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
        )
