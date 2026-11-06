from __future__ import annotations

from typing import Literal

from typing_extensions import NotRequired, TypedDict

from .contacts import ContactStatus, ContactTagRef


class AudienceContactRef(TypedDict):
    id: str
    phone: str
    status: ContactStatus
    tags: NotRequired[list[ContactTagRef]]


class CreateAudienceRequest(TypedDict):
    name: str
    contact_ids: NotRequired[list[str]]
    description: NotRequired[str | None]


class UpdateAudienceRequest(TypedDict, total=False):
    name: str
    description: str | None
    contact_ids: list[str]


class AudienceResponse(TypedDict):
    id: str
    object: Literal["audience"]
    name: str
    description: str | None
    contact_count: int
    contacts: NotRequired[list[AudienceContactRef]]
    trace_id: str
    created_at: str
    updated_at: str


class ListAudiencesResponse(TypedDict):
    object: Literal["list"]
    data: list[AudienceResponse]
    has_more: bool
    next_cursor: str | None
