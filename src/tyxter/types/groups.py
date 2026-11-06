from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment, JSONObject

# WhatsApp Business groups: business-owned groups on a Cloud API number, created
# through Meta's Groups API. Never personal WhatsApp groups.

# `unknown`, `not_checked` and `read_failed` stay distinct from `eligible` and
# `not_eligible`: a missing or failed read is never an answer.
GroupEligibilityStatus: TypeAlias = Literal[
    "eligible", "not_eligible", "unknown", "not_checked", "read_failed"
]
GroupEligibilityReason: TypeAlias = Literal[
    "not_cloud_api",
    "whatsapp_business_app_number",
    "not_official_business_account",
    "missing_messaging_permission",
]
GroupStatus: TypeAlias = Literal["pending", "active", "failed", "deleting", "deleted"]
GroupJoinApprovalMode: TypeAlias = Literal["auto_approve"]


class CreateGroupEligibilityCheckRequest(TypedDict):
    phone_number_id: str


class GroupEligibilityResponse(TypedDict):
    object: Literal["group_eligibility"]
    phone_number_id: str
    environment: Environment
    status: GroupEligibilityStatus
    # Non-empty only when status is not_eligible.
    reasons: list[GroupEligibilityReason]
    checked_at: str | None
    check_requested_at: str | None


class CreateGroupRequest(TypedDict):
    phone_number_id: str
    subject: str
    description: NotRequired[str | None]
    join_approval_mode: NotRequired[GroupJoinApprovalMode]


class GroupParticipant(TypedDict):
    wa_id: str
    joined_at: str


class GroupFailure(TypedDict):
    code: str
    message: str
    # Meta's error detail as Meta reported it; None when Tyxter sent no call.
    provider: JSONObject | None


class GroupResponse(TypedDict):
    id: str
    object: Literal["group"]
    status: GroupStatus
    environment: Environment
    phone_number_id: str
    subject: str
    description: str | None
    join_approval_mode: GroupJoinApprovalMode
    provider_group_id: str | None
    invite_link: str | None
    participants: list[GroupParticipant]
    participant_count: int
    failure: GroupFailure | None
    created_at: str
    updated_at: str
    deleted_at: str | None


class ListGroupsResponse(TypedDict):
    object: Literal["list"]
    data: list[GroupResponse]
    has_more: bool
    next_cursor: str | None


class SandboxGroupParticipantRequest(TypedDict):
    wa_id: str
    action: Literal["join", "remove"]
