from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from httpx import Request

from lockbox_sdk.utils import build_accept_header, build_url, rfc3339_datetime
from lockbox_sdk.v1.api_keys.dto import (
    CreateApiKeyRequestDTO,
    CreateApiKeyResponseDTO,
    GetApiKeyResponseDTO,
    IntrospectApiKeyRequestDTO,
    IntrospectApiKeyResponseDTO,
    SetApiKeyExpirationRequestDTO,
    SetApiKeyMetadataRequestDTO,
)


class ApiKeysApi:
    @staticmethod
    def create_api_key_request(
        payload: CreateApiKeyRequestDTO,
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
            url=build_url(base_url, "/v1/api_keys", query=http_query),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                "Content-Type": payload.__content_type__,
                "Accept": build_accept_header([(CreateApiKeyResponseDTO.__content_type__, 1.0)]),
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
            content=payload.to_request_body(),
        )

    @staticmethod
    def find_api_keys_request(
        base_url: str,
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
        user_agent: str | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Request:
        return Request(
            method="GET",
            url=build_url(base_url, "/v1/api_keys", query={
                **(
                    http_query
                    if isinstance(http_query, dict)
                    else dict(http_query or {})
                ),
                "page": page,
                "per_page": per_page,
                **({"include_ids": include_ids} if include_ids else {}),
                **({"exclude_ids": exclude_ids} if exclude_ids else {}),
                **({"namespaces": namespaces} if namespaces else {}),
                **({"tags": tags} if tags else {}),
                **({"short_keys": short_keys} if short_keys else {}),
                **({"owners": owners} if owners else {}),
                **({"revoked": revoked} if revoked else {}),
                **({"metadata": metadata} if metadata else {}),
                **({"created_before": rfc3339_datetime(created_before)} if created_before else {}),
                **({"created_after": rfc3339_datetime(created_after)} if created_after else {}),
            }),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                "Accept": build_accept_header([(GetApiKeyResponseDTO.__content_type__, 1.0)]),
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
        )

    @staticmethod
    def introspect_api_key_request(
        payload: IntrospectApiKeyRequestDTO,
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
            url=build_url(base_url, "/v1/api_keys/introspect", query=http_query),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                "Content-Type": payload.__content_type__,
                "Accept": build_accept_header([
                    (IntrospectApiKeyResponseDTO.__content_type__, 1.0)
                ]),
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
            content=payload.to_request_body(),
        )

    @staticmethod
    def get_api_key_request(
        id: UUID,
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
            url=build_url(base_url, f"/v1/api_keys/{id}", query=http_query),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                "Accept": build_accept_header([(GetApiKeyResponseDTO.__content_type__, 1.0)]),
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
        )

    @staticmethod
    def delete_api_key_request(
        id: UUID,
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
            url=build_url(base_url, f"/v1/api_keys/{id}", query=http_query),
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

    @staticmethod
    def revoke_api_key_request(
        id: UUID,
        base_url: str,
        *,
        tenant_id: str | None = None,
        user_agent: str | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Request:
        return Request(
            method="PUT",
            url=build_url(base_url, f"/v1/api_keys/{id}/revoke", query=http_query),
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

    @staticmethod
    def rotate_api_key_request(
        id: UUID,
        base_url: str,
        *,
        tenant_id: str | None = None,
        user_agent: str | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Request:
        return Request(
            method="PUT",
            url=build_url(base_url, f"/v1/api_keys/{id}/rotate", query=http_query),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                "Accept": build_accept_header([(CreateApiKeyResponseDTO.__content_type__, 1.0)]),
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
        )

    @staticmethod
    def set_api_key_expiration(
        id: UUID,
        payload: SetApiKeyExpirationRequestDTO,
        base_url: str,
        *,
        tenant_id: str | None = None,
        user_agent: str | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Request:
        return Request(
            method="PUT",
            url=build_url(base_url, f"/v1/api_keys/{id}/expiration", query=http_query),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                "Content-Type": payload.__content_type__,
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
            content=payload.to_request_body(),
        )

    @staticmethod
    def set_api_key_metadata(
        id: UUID,
        payload: SetApiKeyMetadataRequestDTO,
        base_url: str,
        *,
        tenant_id: str | None = None,
        user_agent: str | None = None,
        http_query: dict[str, Any] | None = None,
        http_headers: dict[str, Any] | None = None,
        http_extensions: dict[str, Any] | None = None,
    ) -> Request:
        return Request(
            method="PUT",
            url=build_url(base_url, f"/v1/api_keys/{id}/metadata", query=http_query),
            headers={
                **(
                    http_headers
                    if isinstance(http_headers, dict)
                    else dict(http_headers or {})
                ),
                "Content-Type": payload.__content_type__,
                **({"User-Agent": user_agent} if user_agent else {}),
                **({"X-Tenant-Id": tenant_id} if tenant_id else {}),
            },
            extensions=http_extensions,
            content=payload.to_request_body(),
        )
