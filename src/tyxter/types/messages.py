from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, Required, TypedDict

from .common import Environment, JSONObject, JSONValue

MessageChannel: TypeAlias = Literal["whatsapp", "instagram", "whatsapp_channel"]
MessageDirection: TypeAlias = Literal["inbound", "outbound"]
MessageIdentityType: TypeAlias = Literal[
    "whatsapp_phone_number",
    "phone_e164",
    "instagram_account",
    "instagram_user",
    "whatsapp_channel",
    "whatsapp_channel_audience",
    "whatsapp_group",
]
MessageKind: TypeAlias = Literal["text", "template", "media", "interactive", "flow", "reaction"]
MediaKind: TypeAlias = Literal["image", "document", "audio", "video", "sticker"]
VariableValue: TypeAlias = str | int | bool


class MessageIdentity(TypedDict):
    type: MessageIdentityType
    id: str


class PhoneLessInboundSenderIdentity(TypedDict):
    """Output-only fallback for a phone-less inbound WhatsApp sender on message reads."""

    type: Literal["phone_e164"]
    id: Literal[""]
    # Always None for a phone-less sender; current reads include it.
    profile_name: NotRequired[str | None]


class MessageReadSender(MessageIdentity):
    """A message read's sender, with the captured inbound WhatsApp profile name.

    ``profile_name`` is captured inbound profile evidence, not a verified identity or business
    display name. It is ``None`` on the default payload-less list, outbound and non-WhatsApp
    messages, phone-less rows, malformed captures and redacted rows. Recipients and request
    identities never carry it. Current reads always include it; it is ``NotRequired`` so
    existing response constructors keep type-checking.
    """

    profile_name: NotRequired[str | None]


MessageReadSenderIdentity: TypeAlias = MessageReadSender | PhoneLessInboundSenderIdentity


class StructuredPhoneRecipient(TypedDict):
    type: Literal["phone_e164"]
    country_calling_code: str
    national_number: str


class WhatsAppGroupRecipientIdentity(TypedDict):
    """An active WhatsApp Business group, addressed by its Tyxter group id.

    Send from the phone number that hosts the group.
    """

    type: Literal["whatsapp_group"]
    id: str


class MessageReplyTo(TypedDict):
    """Quote a Tyxter message in the same environment and conversation."""

    message_id: str


class ReactionMessagePayload(TypedDict):
    # Tyxter inbound WhatsApp message ID in this conversation.
    message_id: str
    # One emoji; an empty string removes the reaction.
    emoji: str


class StructuredPhoneInput(TypedDict):
    country_calling_code: str
    national_number: str


MessageRecipient: TypeAlias = (
    MessageIdentity | StructuredPhoneRecipient | WhatsAppGroupRecipientIdentity
)


class TextMessagePayload(TypedDict):
    body: str
    preview_url: NotRequired[bool]


class TemplateHeaderMedia(TypedDict):
    kind: Literal["image", "document", "video"]
    asset_id: str


class TemplateMessagePayload(TypedDict):
    name: str
    language: str
    variables: NotRequired[dict[str, VariableValue]]
    components: NotRequired[list[JSONObject]]
    header_media: NotRequired[TemplateHeaderMedia]


class TTSMediaSource(TypedDict):
    type: Literal["tts"]
    provider: Literal["openai", "elevenlabs", "xai"]
    text: str
    voice: str
    language: str
    model: NotRequired[str]
    instructions: NotRequired[str]


class InlineMediaPayload(TypedDict):
    filename: str
    mime_type: str
    base64: str


class MediaMessagePayload(TypedDict):
    kind: MediaKind
    id: NotRequired[str]
    link: NotRequired[str]
    asset_id: NotRequired[str]
    inline: NotRequired[InlineMediaPayload]
    source: NotRequired[TTSMediaSource]
    caption: NotRequired[str]
    filename: NotRequired[str]
    mime_type: NotRequired[str]
    voice: NotRequired[bool]


class InstagramMediaMessagePayload(TypedDict):
    kind: Literal["image", "document", "audio", "video"]
    id: NotRequired[str]
    link: NotRequired[str]
    asset_id: NotRequired[str]
    inline: NotRequired[InlineMediaPayload]
    source: NotRequired[TTSMediaSource]
    caption: NotRequired[str]
    filename: NotRequired[str]
    mime_type: NotRequired[str]


class InteractiveMessagePayload(TypedDict):
    type: Literal["button", "list"]
    body: JSONObject
    action: JSONObject
    header: NotRequired[JSONObject]
    footer: NotRequired[JSONObject]


class OrderDetailsAmount(TypedDict):
    value: int
    offset: Literal[100]


class OrderDetailsTax(TypedDict):
    value: int
    offset: Literal[100]
    description: NotRequired[str]


class OrderDetailsExpiration(TypedDict):
    timestamp: str
    description: str


class OrderDetailsItem(TypedDict):
    retailer_id: str
    name: str
    amount: OrderDetailsAmount
    quantity: int
    sale_amount: NotRequired[OrderDetailsAmount]


class OrderDetailsShipping(TypedDict):
    value: int
    offset: Literal[100]
    description: NotRequired[str]


class OrderDetailsDiscount(TypedDict):
    value: int
    offset: Literal[100]
    description: NotRequired[str]
    discount_program_name: NotRequired[str]


class NativePixOrder(TypedDict):
    status: Literal["pending"]
    tax: OrderDetailsTax
    items: list[OrderDetailsItem]
    subtotal: OrderDetailsAmount
    catalog_id: NotRequired[str]
    expiration: NotRequired[OrderDetailsExpiration]
    shipping: NotRequired[OrderDetailsShipping]
    discount: NotRequired[OrderDetailsDiscount]


class NativePixDynamicCode(TypedDict):
    code: str
    merchant_name: str
    key: str
    key_type: Literal["CPF", "CNPJ", "EMAIL", "PHONE", "EVP"]


class NativePixPaymentSetting(TypedDict):
    type: Literal["pix_dynamic_code"]
    pix_dynamic_code: NativePixDynamicCode


class NativePixText(TypedDict):
    text: str


class NativePixImageHeader(TypedDict):
    type: Literal["image"]
    link: str


class NativePixOrderDetailsParameters(TypedDict):
    reference_id: str
    type: Literal["digital-goods", "physical-goods"]
    payment_type: Literal["br"]
    payment_settings: tuple[NativePixPaymentSetting]
    currency: Literal["BRL"]
    total_amount: OrderDetailsAmount
    order: NotRequired[NativePixOrder]


class NativePixOrderDetailsAction(TypedDict):
    name: Literal["review_and_pay"]
    parameters: NativePixOrderDetailsParameters


class NativePixOrderDetailsMessagePayload(TypedDict):
    type: Literal["order_details"]
    body: NativePixText
    action: NativePixOrderDetailsAction
    header: NotRequired[NativePixImageHeader]
    footer: NotRequired[NativePixText]


InteractivePayload: TypeAlias = InteractiveMessagePayload | NativePixOrderDetailsMessagePayload


class FlowMessagePayload(TypedDict):
    type: Literal["flow"]
    body: JSONObject
    action: JSONObject
    header: NotRequired[JSONObject]
    footer: NotRequired[JSONObject]


class OutboundMessage(TypedDict):
    type: MessageKind
    text: NotRequired[TextMessagePayload]
    template: NotRequired[TemplateMessagePayload]
    media: NotRequired[MediaMessagePayload | InstagramMediaMessagePayload]
    interactive: NotRequired[InteractivePayload]
    flow: NotRequired[FlowMessagePayload]
    # WhatsApp only.
    reaction: NotRequired[ReactionMessagePayload]


class CreateMessageRequest(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageRecipient
    message: OutboundMessage
    # WhatsApp only.
    reply_to: NotRequired[MessageReplyTo]
    metadata: NotRequired[JSONObject]


class SendTextMessageInput(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageRecipient
    text: TextMessagePayload
    # WhatsApp only.
    reply_to: NotRequired[MessageReplyTo]
    metadata: NotRequired[JSONObject]


class SendTemplateMessageInput(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageRecipient
    template: TemplateMessagePayload
    # WhatsApp only.
    reply_to: NotRequired[MessageReplyTo]
    metadata: NotRequired[JSONObject]


class SendMediaMessageInput(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageRecipient
    media: MediaMessagePayload
    # WhatsApp only.
    reply_to: NotRequired[MessageReplyTo]
    metadata: NotRequired[JSONObject]


class SendInteractiveMessageInput(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageRecipient
    interactive: InteractivePayload
    # WhatsApp only.
    reply_to: NotRequired[MessageReplyTo]
    metadata: NotRequired[JSONObject]


class SendFlowMessageInput(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageRecipient
    flow: FlowMessagePayload
    # WhatsApp only.
    reply_to: NotRequired[MessageReplyTo]
    metadata: NotRequired[JSONObject]


class MessageResponse(TypedDict):
    id: str
    object: Literal["message"]
    status: str
    status_reason: str | None
    channel: MessageChannel
    environment: Environment
    template_id: str | None
    template_version_id: str | None
    template_version: int | None
    created_at: str
    trace_id: str


class MessageEventResponse(TypedDict):
    id: str
    type: str
    status: str | None
    payload: JSONValue | None
    created_at: str


class MessageProviderError(TypedDict):
    message: str | None
    type: str | None
    code: int | str | None
    error_subcode: int | str | None
    error_data: JSONValue | None
    fbtrace_id: str | None
    error_user_title: str | None
    error_user_msg: str | None


class InboundMessageMediaFailure(TypedDict):
    code: str
    message: str


class MediaDownloadHint(TypedDict):
    method: Literal["GET"]
    path: str


class _InboundMessageMediaBase(TypedDict):
    asset_id: str
    kind: MediaKind
    mime_type: str
    byte_length: int
    filename: str | None
    provider_media_id: NotRequired[str]
    voice: NotRequired[bool]
    # Sticker only: True when animated, False when static; omitted when Meta sent no signal.
    animated: NotRequired[bool]


class InboundMessageMediaConsumed(_InboundMessageMediaBase):
    status: Literal["consumed"]
    download: NotRequired[MediaDownloadHint]


class InboundMessageMediaFailed(_InboundMessageMediaBase):
    status: Literal["failed"]
    failure: InboundMessageMediaFailure


class InboundMessageMediaExpired(_InboundMessageMediaBase):
    status: Literal["expired"]


class InboundMessageMediaDeleted(_InboundMessageMediaBase):
    status: Literal["deleted"]


InboundMessageMediaDescriptor: TypeAlias = (
    InboundMessageMediaConsumed
    | InboundMessageMediaFailed
    | InboundMessageMediaExpired
    | InboundMessageMediaDeleted
)


class InboundUnsupportedReason(TypedDict):
    code: int
    message: str


class InboundUnsupportedDescriptor(TypedDict):
    provider_type: str | None
    reason: InboundUnsupportedReason | None


class InboundUnknownDescriptor(TypedDict):
    provider_type: str | None


class MessageContextReplyTo(TypedDict):
    message_id: str | None
    provider_message_id: str


class MessageContext(TypedDict):
    reply_to: MessageContextReplyTo | None
    forwarded: bool
    frequently_forwarded: bool


class MessageSummaryResponse(TypedDict):
    id: str
    object: Literal["message"]
    channel: MessageChannel
    direction: MessageDirection
    type: str
    status: str
    status_reason: str | None
    environment: Environment
    sender: MessageReadSenderIdentity
    recipient: MessageIdentity
    provider: str | None
    provider_message_id: str | None
    template_name: str | None
    template_id: str | None
    template_version_id: str | None
    template_version: int | None
    media: InboundMessageMediaDescriptor | None
    unsupported: NotRequired[InboundUnsupportedDescriptor | None]
    unknown: NotRequired[InboundUnknownDescriptor | None]
    payload: JSONValue | None
    metadata: JSONValue | None
    # Quote (`reply_to`) and forwarding facts.
    context: NotRequired[MessageContext | None]
    error_code: str | None
    error_message: str | None
    provider_error: MessageProviderError | None
    trace_id: str
    created_at: str
    updated_at: str
    redacted_at: str | None
    # Delivery-confirmation timeout stamp. Non-null once the provider accepted the
    # send but no delivery status ever arrived inside the platform's confirmation
    # window; the message is "sent" and stays "sent". Not a status: it clears the
    # moment any status lands, and the message can still be delivered or fail.
    # Always None in sandbox, where statuses are delivered synchronously.
    delivery_unconfirmed_at: str | None


class MessageDetailResponse(MessageSummaryResponse):
    events: list[MessageEventResponse]


class RequestMessageMediaTranscription(TypedDict):
    # Advisory context, trimmed; at most 1024 UTF-16 code units. An empty string clears it, and
    # a retry that omits it inherits the previous value.
    prompt: NotRequired[str]
    # At most 50 trimmed terms of 1-128 UTF-16 code units, without line separators or angle
    # brackets. Order, case and duplicates are kept. An empty list clears them, and a retry
    # that omits them inherits the previous value.
    keywords: NotRequired[list[str]]
    language: NotRequired[str]


MessageMediaTranscriptStatus: TypeAlias = Literal["pending", "succeeded", "failed"]


class MessageMediaTranscriptResponse(TypedDict):
    id: str
    object: Literal["message_media_transcript"]
    message_id: str
    media_asset_id: str
    status: MessageMediaTranscriptStatus
    provider: str | None
    model: str | None
    language: str | None
    text: str | None
    duration_seconds: int | None
    error_code: str | None
    error_message: str | None
    trace_id: str
    created_at: str
    completed_at: str | None


class TypingIndicatorResponse(TypedDict):
    object: Literal["typing_indicator"]
    message_id: str
    status: Literal["accepted"]


class ListMessagesResponse(TypedDict):
    object: Literal["list"]
    data: list[MessageSummaryResponse]
    has_more: bool
    next_cursor: str | None


WhatsAppTextMessageInput = TypedDict(
    "WhatsAppTextMessageInput",
    {
        "from": Required[str],
        "to": Required[str | StructuredPhoneInput],
        "body": Required[str],
        "preview_url": NotRequired[bool],
        "reply_to": NotRequired[MessageReplyTo],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppMediaMessageInput = TypedDict(
    "WhatsAppMediaMessageInput",
    {
        "from": Required[str],
        "to": Required[str | StructuredPhoneInput],
        "media": Required[MediaMessagePayload],
        "reply_to": NotRequired[MessageReplyTo],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppTTSMessageInput = TypedDict(
    "WhatsAppTTSMessageInput",
    {
        "from": Required[str],
        "to": Required[str | StructuredPhoneInput],
        "tts": Required[TTSMediaSource],
        "reply_to": NotRequired[MessageReplyTo],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppTemplateMessageInput = TypedDict(
    "WhatsAppTemplateMessageInput",
    {
        "from": Required[str],
        "to": Required[str | StructuredPhoneInput],
        "name": Required[str],
        "language": Required[str],
        "variables": NotRequired[dict[str, VariableValue]],
        "components": NotRequired[list[JSONObject]],
        "header_media": NotRequired[TemplateHeaderMedia],
        "reply_to": NotRequired[MessageReplyTo],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppInteractiveMessageInput = TypedDict(
    "WhatsAppInteractiveMessageInput",
    {
        "from": Required[str],
        "to": Required[str | StructuredPhoneInput],
        "interactive": Required[InteractivePayload],
        "reply_to": NotRequired[MessageReplyTo],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppFlowMessageInput = TypedDict(
    "WhatsAppFlowMessageInput",
    {
        "from": Required[str],
        "to": Required[str | StructuredPhoneInput],
        "flow": Required[FlowMessagePayload],
        "reply_to": NotRequired[MessageReplyTo],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)


class InstagramTextMessageInput(TypedDict):
    account_id: str
    user_id: str
    body: str
    preview_url: NotRequired[bool]
    metadata: NotRequired[JSONObject]


class InstagramMediaMessageInput(TypedDict):
    account_id: str
    user_id: str
    media: InstagramMediaMessagePayload
    metadata: NotRequired[JSONObject]


class WhatsAppChannelTextMessageInput(TypedDict):
    channel_id: str
    body: str
    preview_url: NotRequired[bool]
    metadata: NotRequired[JSONObject]


class WhatsAppChannelMediaMessageInput(TypedDict):
    channel_id: str
    media: MediaMessagePayload
    metadata: NotRequired[JSONObject]
