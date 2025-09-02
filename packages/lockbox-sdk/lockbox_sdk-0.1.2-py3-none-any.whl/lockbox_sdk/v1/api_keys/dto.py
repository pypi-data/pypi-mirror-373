from __future__ import annotations

from uuid import UUID

from lockbox_sdk.dto import BaseSchema, Rfc3339Datetime


class CreateApiKeyRequestDTO(BaseSchema):
    owner: str
    scope: str | None = None
    tag: str | None = None
    expires_at: Rfc3339Datetime | None = None
    metadata: dict[str, str] | None = None


class CreateApiKeyResponseDTO(BaseSchema):
    id: UUID
    namespace: str
    key: str
    created_at: Rfc3339Datetime
    owner: str
    scope: str | None = None
    tag: str | None = None
    expires_at: Rfc3339Datetime | None = None
    metadata: dict[str, str] = {}


class GetApiKeyResponseDTO(BaseSchema):
    id: UUID
    namespace: str
    short_key: str
    created_at: Rfc3339Datetime
    owner: str
    scope: str | None = None
    tag: str | None = None
    revoked: bool = False
    revoked_at: Rfc3339Datetime | None = None
    expires_at: Rfc3339Datetime | None = None
    last_used_at: Rfc3339Datetime | None = None
    metadata: dict[str, str] = {}


class IntrospectApiKeyRequestDTO(BaseSchema):
    token: str
    scope: str | None = None
    tags: list[str | None] | None = None


class IntrospectApiKeyResponseDTO(BaseSchema):
    valid: bool
    key: GetApiKeyResponseDTO | None = None


class SetApiKeyExpirationRequestDTO(BaseSchema):
    expires_at: Rfc3339Datetime


class SetApiKeyMetadataRequestDTO(BaseSchema):
    metadata: dict[str, str]
