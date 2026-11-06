from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment, JSONObject

FlowStatus: TypeAlias = Literal["draft", "validated", "published", "archived"]
FlowRejectionCode: TypeAlias = Literal[
    "meta_account_integrity",
    "meta_validation_errors",
    "meta_permission_denied",
    "provider_rejected",
    "provider_not_configured",
]


class FlowRejectionAccountHealthEntry(TypedDict):
    entity_type: str | None
    error_code: int
    description: str | None
    remediation: str | None


class FlowRejectionValidationError(TypedDict):
    message: str


class FlowRejectionDetails(TypedDict):
    provider_code: int | None
    provider_subcode: int | None
    diagnostics_status: Literal["not_requested", "available", "read_failed"]
    account_health: list[FlowRejectionAccountHealthEntry]
    validation_errors: list[FlowRejectionValidationError]


class CreateFlowRequest(TypedDict):
    name: str
    flow_json: JSONObject


class FlowResponse(TypedDict):
    id: str
    object: Literal["flow"]
    name: str
    status: FlowStatus
    environment: Environment
    flow_json: JSONObject
    provider_flow_id: str | None
    provider_missing_since: NotRequired[str | None]
    rejection_reason: str | None
    # Branch on the stable code; never parse `rejection_reason`. Historical records have None.
    rejection_code: NotRequired[FlowRejectionCode | None]
    rejection_details: NotRequired[FlowRejectionDetails | None]
    published_at: str | None
    created_at: str
    updated_at: str


class ListFlowsResponse(TypedDict):
    object: Literal["list"]
    data: list[FlowResponse]
    has_more: bool
    next_cursor: str | None
