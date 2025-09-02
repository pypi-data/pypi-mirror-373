from __future__ import annotations

from datetime import datetime
from typing import Annotated, ClassVar, Generic, TypeAlias, TypeVar

from pydantic import BaseModel, PlainSerializer

from lockbox_sdk.utils import rfc3339_datetime


T = TypeVar("T")


Rfc3339Datetime: TypeAlias = Annotated[
    datetime,
    PlainSerializer(
        rfc3339_datetime,
        return_type=str,
        when_used="json"
    ),
]


class BaseSchema(BaseModel):
    __content_type__: ClassVar[str] = "application/json"

    def to_request_body(self, **kwargs) -> bytes:
        return self.model_dump_json(exclude_unset=True, **kwargs).encode()


class PaginatedResponseDTO(BaseSchema, Generic[T]):
    items: list[T]
    count: int
    next_page: int | None = None
    previous_page: int | None = None

