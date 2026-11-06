from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .billing import ThroughputTier
from .common import Environment

ProjectDefaultLanguage: TypeAlias = Literal["pt_BR", "en_US", "es_ES"]
ProjectProfileVertical: TypeAlias = Literal[
    "UNDEFINED",
    "OTHER",
    "AUTO",
    "BEAUTY",
    "APPAREL",
    "EDU",
    "ENTERTAIN",
    "EVENT_PLAN",
    "FINANCE",
    "GROCERY",
    "GOVT",
    "HOTEL",
    "HEALTH",
    "NONPROFIT",
    "PROF_SERVICES",
    "RETAIL",
    "TRAVEL",
    "RESTAURANT",
]
# `syncing`: a requested sync is queued or running in a Tyxter worker; the other fields keep
# the last result.
ProjectProfileMetaSyncStatus: TypeAlias = Literal["not_synced", "syncing", "synced", "failed"]


class EnvironmentResponse(TypedDict):
    id: str
    object: Literal["environment"]
    kind: Environment
    name: str
    throughput_tier: ThroughputTier
    created_at: str
    updated_at: str


class CreateProjectRequest(TypedDict):
    name: str
    slug: NotRequired[str]


class ProjectProfileMetaSyncResponse(TypedDict):
    status: ProjectProfileMetaSyncStatus
    synced_at: str | None
    phone_number_id: str | None
    profile_picture_url: str | None
    error_code: str | None
    error_message: str | None


class ProjectProfileResponse(TypedDict):
    about: str | None
    description: str | None
    address: str | None
    email: str | None
    websites: list[str]
    vertical: ProjectProfileVertical | None
    profile_image_url: str | None
    profile_image_mime_type: str | None
    profile_image_size_bytes: int | None
    profile_image_uploaded_at: str | None
    meta_sync: ProjectProfileMetaSyncResponse


class ProjectResponse(TypedDict):
    id: str
    object: Literal["project"]
    name: str
    slug: str
    default_language: ProjectDefaultLanguage
    profile: ProjectProfileResponse
    archived_at: str | None
    created_at: str
    updated_at: str
    environments: list[EnvironmentResponse]


class ListProjectsResponse(TypedDict):
    object: Literal["list"]
    data: list[ProjectResponse]
    has_more: bool
    next_cursor: str | None
