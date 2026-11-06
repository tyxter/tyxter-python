from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, Required, TypedDict

from .common import JSONObject
from .messages import MediaMessagePayload, MessageChannel, ReactionMessagePayload


class SandboxInboundUnsupportedInput(TypedDict):
    provider_type: NotRequired[str]


class SandboxInboundUnknownInput(TypedDict):
    provider_type: NotRequired[str]


InboundSandboxMessageRequest = TypedDict(
    "InboundSandboxMessageRequest",
    {
        "from": Required[str],
        "to": Required[str],
        "type": Required[
            Literal["text", "media", "interactive", "flow", "reaction", "unsupported", "unknown"]
        ],
        # Tyxter group id: `to` names its host phone number and `from` the participant.
        "group_id": NotRequired[str],
        "channel": NotRequired[MessageChannel],
        "reaction": NotRequired[ReactionMessagePayload],
        "text": NotRequired[dict[Literal["body"], str]],
        "media": NotRequired[MediaMessagePayload],
        "interactive": NotRequired[JSONObject],
        "flow": NotRequired[JSONObject],
        "unsupported": NotRequired[SandboxInboundUnsupportedInput],
        "unknown": NotRequired[SandboxInboundUnknownInput],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)


class SandboxTemplateStatusRequest(TypedDict):
    status: Literal["rejected", "paused", "disabled"]
    rejection_reason: NotRequired[str]


class SandboxEnvironment(TypedDict):
    id: str
    kind: Literal["sandbox"]
    project_id: str


class SandboxAPIKey(TypedDict):
    id: str
    key_prefix: str | None
    scopes: list[str]
    can_create_api_keys: Literal[False]
    api_key_creation: Literal["dashboard_or_api_keys_endpoint"]


class SandboxSender(TypedDict):
    default_sender_id: str | None
    phone_number: str | None
    display_name: str | None
    status: str | None
    outbound_messages_require_sender: Literal[True]
    inbound_simulation_requires_sender: Literal[False]


class SandboxSigningHeaders(TypedDict):
    id: Literal["tyxter-webhook-id"]
    timestamp: Literal["tyxter-webhook-timestamp"]
    signature: Literal["tyxter-webhook-signature"]


class SandboxWebhooks(TypedDict):
    active_endpoint_count: int
    listen_endpoint: Literal["/v1/webhook-events/listen"]
    retrieve_listen_event_endpoint: Literal["/v1/webhook-events/listen/:outbox_event_id"]
    inbound_event_type: Literal["message.received"]
    supported_listen_event_types: list[str]
    signing_headers: SandboxSigningHeaders


class SandboxCapabilities(TypedDict):
    simulate_inbound: bool
    listen_for_webhooks: bool
    send_outbound_messages: bool
    send_template_messages: NotRequired[bool]


class SandboxDefaultTemplate(TypedDict):
    name: str
    language: str


class SandboxTemplates(TypedDict):
    approved_template_count: int
    default_template: SandboxDefaultTemplate | None


class SandboxQuickstartResponse(TypedDict):
    object: Literal["sandbox_quickstart"]
    environment: SandboxEnvironment
    api_key: SandboxAPIKey
    sender: SandboxSender
    webhooks: SandboxWebhooks
    templates: NotRequired[SandboxTemplates]
    capabilities: SandboxCapabilities
    missing_scopes: list[str]


SandboxLLMFailureKind: TypeAlias = Literal[
    "provider_down",
    "auth_failed",
    "timeout",
    "cost_cap_reached",
]


class SandboxLLMFailureRequest(TypedDict):
    failure: SandboxLLMFailureKind
    ttl_seconds: NotRequired[int]


class SandboxLLMFailureResponse(TypedDict):
    armed: Literal[True]
    failure: SandboxLLMFailureKind
    expires_at: str | None
