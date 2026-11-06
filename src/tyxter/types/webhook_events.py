from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import JSONValue

WebhookEventStatus: TypeAlias = Literal["pending", "delivered", "failed"]


class WebhookDeliveryAttempt(TypedDict):
    id: str
    status: Literal["pending", "succeeded", "failed"]
    attempt: int
    status_code: int | None
    # None on pending, successful, historical and unclassified attempts.
    failure_class: NotRequired[
        Literal["auth_rejected", "server_error", "unreachable", "timeout"] | None
    ]
    response_body_redacted: str | None
    error_message: str | None
    next_retry_at: str | None
    created_at: str


class WebhookSignatureHeaders(TypedDict):
    tyxter_webhook_id: str
    tyxter_webhook_timestamp: str
    tyxter_webhook_signature: str


class WebhookSignaturePreview(TypedDict):
    object: Literal["webhook_signature_preview"]
    mode: Literal["sandbox_listen", "production_listen"]
    algorithm: Literal["hmac-sha256"]
    signed_content: Literal["timestamp.raw_body"]
    webhook_endpoint_id: str
    webhook_id: str
    timestamp: str
    raw_body: str
    raw_body_base64: str
    signature: str
    headers: dict[str, str]


class WebhookEventResponse(TypedDict):
    id: str
    object: Literal["webhook_event"]
    endpoint_id: str | None
    type: str
    source_type: str
    source_id: str
    payload: JSONValue
    status: WebhookEventStatus
    trace_id: str
    created_at: str
    attempts: list[WebhookDeliveryAttempt]
    signature_preview: NotRequired[WebhookSignaturePreview]


class ListWebhookEventsResponse(TypedDict):
    object: Literal["list"]
    data: list[WebhookEventResponse]
    has_more: bool
    next_cursor: str | None


class ListenWebhookEventsResponse(TypedDict):
    object: Literal["webhook_event_listen"]
    data: list[WebhookEventResponse]
    has_more: bool
    next_cursor: str | None
    next_poll_after_ms: NotRequired[int]


class CreateWebhookListenSessionRequest(TypedDict):
    ttl_seconds: NotRequired[int]
    reason: NotRequired[str]


class WebhookListenSessionResponse(TypedDict):
    id: str
    object: Literal["webhook_listen_session"]
    environment: Literal["production"]
    status: Literal["active", "disabled", "expired"]
    expires_at: str
    disabled_at: str | None
    created_at: str
    trace_id: str
    poll_endpoint: Literal["/v1/webhook-events/listen"]
    retrieve_endpoint: Literal["/v1/webhook-events/listen/:outbox_event_id"]


class BulkResendWebhookEventsRequest(TypedDict):
    webhook_event_ids: NotRequired[list[str]]
    event_type: NotRequired[str]
    status: NotRequired[WebhookEventStatus]
    limit: NotRequired[int]


class BulkResendWebhookEventsResponse(TypedDict):
    object: Literal["webhook_bulk_resend"]
    requested: int
    enqueued: int
    skipped: int
    attempts: list[WebhookDeliveryAttempt]
