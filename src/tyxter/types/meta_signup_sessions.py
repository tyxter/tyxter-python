from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

MetaSignupSessionStatus: TypeAlias = Literal[
    "pending", "processing", "completed", "expired", "failed"
]


class CreateMetaSignupSessionRequest(TypedDict):
    return_url: str
    end_customer_ref: NotRequired[str]


class MetaSignupFailureFeedback(TypedDict):
    endpoint: Literal["/v1/feedback"]
    method: Literal["POST"]


class MetaSignupFailure(TypedDict):
    """A terminal browser-handoff failure. Start a new session; do not exchange a late code."""

    code: Literal["meta_signup_session_expired"]
    reason: Literal["meta_signup_callback_lost", "popup_no_return"]
    message: str
    feedback: MetaSignupFailureFeedback


class MetaSignupSessionResponse(TypedDict):
    id: str
    object: Literal["meta_signup_session"]
    status: MetaSignupSessionStatus
    error: NotRequired[MetaSignupFailure]
    url: str | None
    return_url: str
    end_customer_ref: str | None
    project_id: str
    environment_id: str
    environment: Environment
    expires_at: str
    completed_at: str | None
    provider_connection_id: str | None
    created_at: str
    updated_at: str
