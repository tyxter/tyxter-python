from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, Required, TypedDict

from .common import Environment, JSONObject
from .messages import TemplateHeaderMedia, VariableValue

MessageBatchStatus: TypeAlias = Literal[
    "pending", "enqueuing", "sending", "paused", "completed", "failed", "cancelled"
]


class BatchRecipient(TypedDict):
    to: str
    variables: NotRequired[dict[str, VariableValue]]


class BatchAudience(TypedDict):
    contact_ids: list[str]


class BatchTemplate(TypedDict):
    name: str
    language: str
    header_media: NotRequired[TemplateHeaderMedia]


class MessageBatchPacingResponse(TypedDict):
    deferred_recipient_count: int
    estimated_windows: int


CreateMessageBatchRequest = TypedDict(
    "CreateMessageBatchRequest",
    {
        "channel": Required[Literal["whatsapp"]],
        "from": Required[str],
        "template": Required[BatchTemplate],
        "recipients": NotRequired[list[BatchRecipient]],
        "audience": NotRequired[BatchAudience],
        "audience_id": NotRequired[str],
        "name": NotRequired[str],
        "scheduled_for": NotRequired[str],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)


class MessageBatchResponse(TypedDict):
    id: str
    object: Literal["message_batch"]
    status: MessageBatchStatus
    environment: Environment
    name: str | None
    template_name: str | None
    recipient_count: int
    pacing: MessageBatchPacingResponse | None
    # Recipients the recipient guard skipped. Included in `failed_count`; the failure export
    # gives each one's guard reason.
    recipient_guard_skipped_count: NotRequired[int]
    enqueued_count: int
    sent_count: int
    failed_count: int
    error_message: str | None
    trace_id: str
    scheduled_for: str | None
    started_at: str | None
    completed_at: str | None
    created_at: str
    updated_at: str


class ListMessageBatchesResponse(TypedDict):
    object: Literal["list"]
    data: list[MessageBatchResponse]
    has_more: bool
    next_cursor: str | None


class MessageBatchFailureExportRow(TypedDict):
    message_id: str
    to: str | None
    status: str
    error_code: str | None
    error_message: str | None
    guard_reason: NotRequired[str]
    next_allowed_at: NotRequired[str | None]
    created_at: str
    updated_at: str


class MessageBatchFailureExportResponse(TypedDict):
    object: Literal["message_batch_failure_export"]
    batch_id: str
    generated_at: str
    rows: list[MessageBatchFailureExportRow]
