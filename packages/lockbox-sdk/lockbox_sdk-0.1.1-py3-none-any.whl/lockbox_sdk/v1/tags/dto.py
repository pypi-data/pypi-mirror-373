from __future__ import annotations

from lockbox_sdk.dto import BaseSchema, Rfc3339Datetime


class CreateTagRequestDTO(BaseSchema):
    name: str


class CreateTagResponseDTO(BaseSchema):
    namespace: str
    name: str
    created_at: Rfc3339Datetime


class GetTagResponseDTO(BaseSchema):
    namespace: str
    name: str
    created_at: Rfc3339Datetime
