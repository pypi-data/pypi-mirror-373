from __future__ import annotations

from lockbox_sdk.dto import BaseSchema, Rfc3339Datetime


class CreateNamespaceRequestDTO(BaseSchema):
    name: str


class CreateNamespaceResponseDTO(BaseSchema):
    name: str
    created_at: Rfc3339Datetime
    is_default: bool = False


class GetNamespaceResponseDTO(BaseSchema):
    name: str
    created_at: Rfc3339Datetime
    is_default: bool = False
