from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .billing import TopupPaymentMethodKind
from .common import Environment, JSONObject
from .messages import (
    InboundMessageMediaDescriptor,
    InboundUnknownDescriptor,
    InboundUnsupportedDescriptor,
    MessageContext,
    MessageProviderError,
)

WebhookEndpointStatus: TypeAlias = Literal["active", "disabled"]
WebhookEndpointDisabledDetailFailureClass: TypeAlias = Literal[
    "auth_rejected", "server_error", "unreachable", "timeout"
]


class WebhookEndpointDisabledDetail(TypedDict):
    last_status_code: int | None
    failure_class: WebhookEndpointDisabledDetailFailureClass
    # Present when three consecutive real delivery failures during probation re-tripped it.
    probation_retrip: NotRequired[Literal[True]]


class CreateWebhookEndpointRequest(TypedDict):
    url: str
    subscribed_events: list[str]
    description: NotRequired[str]


class UpdateWebhookEndpointRequest(TypedDict, total=False):
    url: str
    subscribed_events: list[str]
    description: str | None
    status: WebhookEndpointStatus


class WebhookEndpointResponse(TypedDict):
    id: str
    object: Literal["webhook_endpoint"]
    url: str
    description: str | None
    subscribed_events: list[str]
    status: WebhookEndpointStatus
    # True after breaker recovery until the first successful real delivery.
    probation: NotRequired[bool]
    # Number of pending events currently held for this endpoint.
    held_event_count: NotRequired[int]
    # Creation time of the oldest currently held event; None when none are held.
    oldest_held_event_at: NotRequired[str | None]
    disabled_reason: str | None
    disabled_detail: NotRequired[WebhookEndpointDisabledDetail | None]
    last_failure_at: str | None
    last_success_at: str | None
    environment: Environment
    created_at: str
    updated_at: str


class CreateWebhookEndpointResponse(WebhookEndpointResponse):
    signing_secret: str


class RotateWebhookSigningSecretResponse(WebhookEndpointResponse):
    signing_secret: str


class ListWebhookEndpointsResponse(TypedDict):
    object: Literal["list"]
    data: list[WebhookEndpointResponse]
    has_more: bool
    next_cursor: str | None


class TestWebhookEndpointResponse(TypedDict):
    object: Literal["webhook_test"]
    webhook_event_id: str
    webhook_endpoint_id: str
    status: Literal["pending"]


class DeleteWebhookEndpointResponse(TypedDict):
    id: str
    deleted: bool


MessageMediaTranscriptionWebhookEventType: TypeAlias = Literal[
    "message.media_transcribed", "message.media_transcription_failed"
]


class MessageWebhookIdentity(TypedDict):
    type: str
    id: str


class MessageWebhookSender(MessageWebhookIdentity):
    """A ``message.*`` webhook sender with the captured inbound WhatsApp profile name.

    ``profile_name`` is ``None`` for every sender except a resolved inbound WhatsApp sender with
    captured evidence, and after privacy cleanup. It is not a verified identity. Newly rendered
    events include it; already-stored webhook snapshots keep their original body and can lack
    it, so it is ``NotRequired``.
    """

    profile_name: NotRequired[str | None]


class MessageWebhookData(TypedDict):
    message_id: str
    status: str
    channel: Literal["whatsapp", "instagram"]
    sender: MessageWebhookSender
    recipient: MessageWebhookIdentity
    provider_message_id: str | None
    metadata: object | None


class MessageMediaTranscribedWebhookTranscript(TypedDict):
    id: str
    media_asset_id: str
    status: Literal["succeeded"]
    provider: str
    model: str
    language: str | None
    text: str | None
    duration_seconds: int
    completed_at: str


class MessageMediaTranscribedWebhookData(MessageWebhookData):
    transcript: MessageMediaTranscribedWebhookTranscript


class _WebhookEventEnvelope(TypedDict):
    id: str
    created_at: str
    occurred_at: NotRequired[str]
    environment: Environment
    trace_id: str


class CreditToppedUpWebhookData(TypedDict):
    topup_id: str
    amount_brl: str
    payment_method: TopupPaymentMethodKind
    provider: NotRequired[Literal["stripe", "abacate_pay", "manual", "promotion"]]
    balance_brl: str


class CreditToppedUpWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["credit.topped_up"]
    data: CreditToppedUpWebhookData


class CreditHardBlockLiftedWebhookData(TypedDict):
    organization_id: str
    # Four-decimal BRL amounts.
    balance_brl: str
    floor_brl: str
    top_up_url: str


CreditHardBlockTrigger: TypeAlias = Literal["usage", "phone_renewal", "reversal", "reconciliation"]


class CreditHardBlockEngagedWebhookData(CreditHardBlockLiftedWebhookData):
    trigger: CreditHardBlockTrigger


class CreditHardBlockEngagedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["credit.hard_block_engaged"]
    data: CreditHardBlockEngagedWebhookData


class CreditHardBlockLiftedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["credit.hard_block_lifted"]
    data: CreditHardBlockLiftedWebhookData


class MessageMediaTranscribedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["message.media_transcribed"]
    data: MessageMediaTranscribedWebhookData


class MessageMediaTranscriptionFailedWebhookTranscript(TypedDict):
    id: str
    media_asset_id: str
    status: Literal["failed"]
    error_code: str
    error_message: str | None
    language: str | None
    completed_at: str


class MessageMediaTranscriptionFailedWebhookData(MessageWebhookData):
    transcript: MessageMediaTranscriptionFailedWebhookTranscript


class MessageMediaTranscriptionFailedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["message.media_transcription_failed"]
    data: MessageMediaTranscriptionFailedWebhookData


MessageMediaTranscriptionWebhookTranscript: TypeAlias = (
    MessageMediaTranscribedWebhookTranscript | MessageMediaTranscriptionFailedWebhookTranscript
)
MessageMediaTranscriptionWebhookData: TypeAlias = (
    MessageMediaTranscribedWebhookData | MessageMediaTranscriptionFailedWebhookData
)
MessageMediaTranscriptionWebhookEnvelope: TypeAlias = (
    MessageMediaTranscribedWebhookEnvelope | MessageMediaTranscriptionFailedWebhookEnvelope
)


class ProviderConnectionPolicyWarningWebhookData(TypedDict):
    provider_connection_id: str
    provider: Literal["meta"]
    display_name: str
    violation_type: str | None
    observed_at: str


class ProviderConnectionPolicyWarningWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["provider_connection.policy_warning"]
    data: ProviderConnectionPolicyWarningWebhookData


class ProviderConnectionDisableScheduledWebhookData(TypedDict):
    provider_connection_id: str
    provider: Literal["meta"]
    display_name: str
    waba_ban_date: str | None
    observed_at: str


class ProviderConnectionDisableScheduledWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["provider_connection.disable_scheduled"]
    data: ProviderConnectionDisableScheduledWebhookData


class GroupMessageReceivedContentText(TypedDict):
    body: str


class GroupMessageReceivedContent(TypedDict):
    type: str
    text: NotRequired[GroupMessageReceivedContentText]
    media: NotRequired[InboundMessageMediaDescriptor]
    unsupported: NotRequired[InboundUnsupportedDescriptor]
    unknown: NotRequired[InboundUnknownDescriptor]
    interactive: NotRequired[JSONObject]
    context: NotRequired[MessageContext]


class GroupMessageReceivedRecipient(TypedDict):
    type: Literal["whatsapp_group"]
    id: str


class GroupMessageReceivedWebhookData(TypedDict):
    """A participant's message in a WhatsApp Business group (``group.message_received``)."""

    message_id: str
    status: str
    channel: Literal["whatsapp", "instagram"]
    sender: MessageWebhookSender
    recipient: GroupMessageReceivedRecipient
    provider_message_id: str | None
    metadata: object | None
    group_id: str
    phone_number_id: str
    content: NotRequired[GroupMessageReceivedContent]


class GroupMessageReceivedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["group.message_received"]
    data: GroupMessageReceivedWebhookData


# ``from`` is None when Meta withholds the reacting user's phone.
MessageReaction = TypedDict(
    "MessageReaction",
    {
        "emoji": str,
        "removed": bool,
        "from": str | None,
        "reacted_message_id": str,
    },
)


class MessageReactionReceivedWebhookData(MessageWebhookData):
    """``message.reaction_received``: the reacted message's snapshot plus the reaction."""

    reaction: MessageReaction


class MessageReactionReceivedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["message.reaction_received"]
    data: MessageReactionReceivedWebhookData


GroupWebhookStatus: TypeAlias = Literal["pending", "active", "failed", "deleting", "deleted"]
GroupWebhookEventType: TypeAlias = Literal[
    "group.created",
    "group.create_failed",
    "group.deleted",
    "group.delete_failed",
    "group.invite_link_reset",
    "group.invite_link_reset_failed",
]


class GroupWebhookFailure(TypedDict):
    code: str
    message: str
    provider: MessageProviderError | None


class GroupWebhookData(TypedDict):
    """Data of the six WhatsApp Business group lifecycle events.

    ``occurred_at`` is when Tyxter recorded the outcome. On the three ``*_failed`` events,
    ``failure`` is the failure of the operation that failed, stored with the event; every other
    field, and ``failure`` on the other three events, is the group as Tyxter reads it when it
    sends the event (or serves it on a listen read), so a delayed or replayed event can show a
    later state. ``invite_link`` lets anyone who has it join the group: store payloads as
    secrets.
    """

    group_id: str
    phone_number_id: str
    status: GroupWebhookStatus
    subject: str
    provider_group_id: str | None
    invite_link: str | None
    failure: GroupWebhookFailure | None
    occurred_at: str


class GroupWebhookEnvelope(_WebhookEventEnvelope):
    type: GroupWebhookEventType
    data: GroupWebhookData


class GroupWebhookParticipant(TypedDict):
    wa_id: str


GroupParticipantRemovalInitiator: TypeAlias = Literal["participant", "business"]


class _GroupParticipantWebhookDataFields(TypedDict):
    group_id: str
    phone_number_id: str
    participant: GroupWebhookParticipant
    participant_count: int
    occurred_at: str


class GroupParticipantWebhookData(_GroupParticipantWebhookDataFields):
    """Data of ``group.participant_joined`` and ``group.participant_removed``.

    The join or removal as Tyxter recorded it, never the group's later state.
    ``participant.wa_id`` is the participant's WhatsApp ID. ``occurred_at`` is Meta's time in
    whole seconds (sandbox: the simulation time); the same participant, action and second
    reported twice is one event. ``participant_count`` is Tyxter's count right after it applied
    the change. ``initiated_by`` is present exactly on a removal.
    """

    initiated_by: NotRequired[GroupParticipantRemovalInitiator]


class GroupParticipantJoinedWebhookData(_GroupParticipantWebhookDataFields):
    """``group.participant_joined`` data; it never carries ``initiated_by``."""


class GroupParticipantRemovedWebhookData(_GroupParticipantWebhookDataFields):
    initiated_by: GroupParticipantRemovalInitiator


class GroupParticipantJoinedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["group.participant_joined"]
    data: GroupParticipantJoinedWebhookData


class GroupParticipantRemovedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["group.participant_removed"]
    data: GroupParticipantRemovedWebhookData


GroupParticipantWebhookEnvelope: TypeAlias = (
    GroupParticipantJoinedWebhookEnvelope | GroupParticipantRemovedWebhookEnvelope
)


PaymentWebhookEventType: TypeAlias = Literal[
    "payment.created",
    "payment.approval_available",
    "payment.link_generated",
    "payment.paid",
    "payment.failed",
    "payment.expired",
    "payment.cancelled",
]
PaymentWebhookStatus: TypeAlias = Literal[
    "link_pending", "link_generated", "paid", "failed", "expired", "cancelled"
]
TerminalPaymentWebhookStatus: TypeAlias = Literal["paid", "failed", "expired", "cancelled"]


class _PaymentWebhookDataFields(TypedDict):
    id: str
    object: Literal["payment_request"]
    # Legacy alias of ``id``, retained for existing integrations.
    payment_request_id: str
    amount_brl: str | None
    currency: str
    description: str | None
    customer_name: str | None
    customer_phone: str | None
    customer_email: str | None
    external_reference: str | None
    metadata: object | None
    provider: str | None
    provider_payment_id: str | None
    provider_approval_id: str | None
    provider_event_id: NotRequired[str | None]
    provider_event_type: NotRequired[str]
    operation: NotRequired[str]
    error_code: NotRequired[str]
    error_message: NotRequired[str]
    sandbox_simulator: NotRequired[bool]
    sandbox_pay_page: NotRequired[bool]


class PaymentWebhookData(_PaymentWebhookDataFields):
    """Sanitized event-time snapshot shared by all merchant ``payment.*`` events."""

    status: PaymentWebhookStatus
    payment_link_url: str | None


class PaymentCreatedWebhookData(_PaymentWebhookDataFields):
    status: Literal["link_pending"]
    payment_link_url: None


class PaymentLinkGeneratedWebhookData(_PaymentWebhookDataFields):
    status: Literal["link_generated"]
    payment_link_url: str


class PaymentPaidWebhookData(_PaymentWebhookDataFields):
    status: Literal["paid"]
    payment_link_url: str | None


class PaymentFailedWebhookData(_PaymentWebhookDataFields):
    status: Literal["failed"]
    payment_link_url: str | None


class PaymentExpiredWebhookData(_PaymentWebhookDataFields):
    status: Literal["expired"]
    payment_link_url: str | None


class PaymentCancelledWebhookData(_PaymentWebhookDataFields):
    status: Literal["cancelled"]
    payment_link_url: str | None


class PaymentCreatedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["payment.created"]
    data: PaymentCreatedWebhookData


class PaymentApprovalAvailableWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["payment.approval_available"]
    data: PaymentLinkGeneratedWebhookData


class PaymentLinkGeneratedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["payment.link_generated"]
    data: PaymentLinkGeneratedWebhookData


class PaymentPaidWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["payment.paid"]
    data: PaymentPaidWebhookData


class PaymentFailedWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["payment.failed"]
    data: PaymentFailedWebhookData


class PaymentExpiredWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["payment.expired"]
    data: PaymentExpiredWebhookData


class PaymentCancelledWebhookEnvelope(_WebhookEventEnvelope):
    type: Literal["payment.cancelled"]
    data: PaymentCancelledWebhookData


PaymentWebhookEnvelope: TypeAlias = (
    PaymentCreatedWebhookEnvelope
    | PaymentApprovalAvailableWebhookEnvelope
    | PaymentLinkGeneratedWebhookEnvelope
    | PaymentPaidWebhookEnvelope
    | PaymentFailedWebhookEnvelope
    | PaymentExpiredWebhookEnvelope
    | PaymentCancelledWebhookEnvelope
)
