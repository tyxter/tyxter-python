from __future__ import annotations

from tyxter.types import (
    CreateMessageRequest,
    InstagramMediaMessageInput,
    InstagramTextMessageInput,
    JSONObject,
    MediaMessagePayload,
    MessageChannel,
    MessageIdentityType,
    MessageRecipient,
    MessageReplyTo,
    OutboundMessage,
    StructuredPhoneInput,
    TemplateMessagePayload,
    TextMessagePayload,
    WhatsAppChannelMediaMessageInput,
    WhatsAppChannelTextMessageInput,
    WhatsAppFlowMessageInput,
    WhatsAppInteractiveMessageInput,
    WhatsAppMediaMessageInput,
    WhatsAppTemplateMessageInput,
    WhatsAppTextMessageInput,
    WhatsAppTTSMessageInput,
)


def whatsapp_text(input: WhatsAppTextMessageInput) -> CreateMessageRequest:
    text: TextMessagePayload = {"body": input["body"]}
    if "preview_url" in input:
        text["preview_url"] = input["preview_url"]
    return _request(
        channel="whatsapp",
        sender_type="whatsapp_phone_number",
        sender_id=input["from"],
        recipient_type="phone_e164",
        recipient_id=input["to"],
        message={"type": "text", "text": text},
        metadata=input.get("metadata"),
        reply_to=input.get("reply_to"),
    )


def whatsapp_media(input: WhatsAppMediaMessageInput) -> CreateMessageRequest:
    return _request(
        channel="whatsapp",
        sender_type="whatsapp_phone_number",
        sender_id=input["from"],
        recipient_type="phone_e164",
        recipient_id=input["to"],
        message={"type": "media", "media": input["media"]},
        metadata=input.get("metadata"),
        reply_to=input.get("reply_to"),
    )


def whatsapp_audio_from_text(input: WhatsAppTTSMessageInput) -> CreateMessageRequest:
    media: MediaMessagePayload = {"kind": "audio", "source": input["tts"]}
    return _request(
        channel="whatsapp",
        sender_type="whatsapp_phone_number",
        sender_id=input["from"],
        recipient_type="phone_e164",
        recipient_id=input["to"],
        message={"type": "media", "media": media},
        metadata=input.get("metadata"),
        reply_to=input.get("reply_to"),
    )


def whatsapp_template(input: WhatsAppTemplateMessageInput) -> CreateMessageRequest:
    template: TemplateMessagePayload = {
        "name": input["name"],
        "language": input["language"],
    }
    if "variables" in input:
        template["variables"] = input["variables"]
    if "components" in input:
        template["components"] = input["components"]
    if "header_media" in input:
        template["header_media"] = input["header_media"]
    return _request(
        channel="whatsapp",
        sender_type="whatsapp_phone_number",
        sender_id=input["from"],
        recipient_type="phone_e164",
        recipient_id=input["to"],
        message={"type": "template", "template": template},
        metadata=input.get("metadata"),
        reply_to=input.get("reply_to"),
    )


def whatsapp_interactive(input: WhatsAppInteractiveMessageInput) -> CreateMessageRequest:
    return _request(
        channel="whatsapp",
        sender_type="whatsapp_phone_number",
        sender_id=input["from"],
        recipient_type="phone_e164",
        recipient_id=input["to"],
        message={"type": "interactive", "interactive": input["interactive"]},
        metadata=input.get("metadata"),
        reply_to=input.get("reply_to"),
    )


def whatsapp_flow(input: WhatsAppFlowMessageInput) -> CreateMessageRequest:
    return _request(
        channel="whatsapp",
        sender_type="whatsapp_phone_number",
        sender_id=input["from"],
        recipient_type="phone_e164",
        recipient_id=input["to"],
        message={"type": "flow", "flow": input["flow"]},
        metadata=input.get("metadata"),
        reply_to=input.get("reply_to"),
    )


def instagram_text(input: InstagramTextMessageInput) -> CreateMessageRequest:
    text: TextMessagePayload = {"body": input["body"]}
    if "preview_url" in input:
        text["preview_url"] = input["preview_url"]
    return _request(
        channel="instagram",
        sender_type="instagram_account",
        sender_id=input["account_id"],
        recipient_type="instagram_user",
        recipient_id=input["user_id"],
        message={"type": "text", "text": text},
        metadata=input.get("metadata"),
    )


def instagram_media(input: InstagramMediaMessageInput) -> CreateMessageRequest:
    return _request(
        channel="instagram",
        sender_type="instagram_account",
        sender_id=input["account_id"],
        recipient_type="instagram_user",
        recipient_id=input["user_id"],
        message={"type": "media", "media": input["media"]},
        metadata=input.get("metadata"),
    )


def whatsapp_channel_text(input: WhatsAppChannelTextMessageInput) -> CreateMessageRequest:
    text: TextMessagePayload = {"body": input["body"]}
    if "preview_url" in input:
        text["preview_url"] = input["preview_url"]
    return _request(
        channel="whatsapp_channel",
        sender_type="whatsapp_channel",
        sender_id=input["channel_id"],
        recipient_type="whatsapp_channel_audience",
        recipient_id="followers",
        message={"type": "text", "text": text},
        metadata=input.get("metadata"),
    )


def whatsapp_channel_media(input: WhatsAppChannelMediaMessageInput) -> CreateMessageRequest:
    return _request(
        channel="whatsapp_channel",
        sender_type="whatsapp_channel",
        sender_id=input["channel_id"],
        recipient_type="whatsapp_channel_audience",
        recipient_id="followers",
        message={"type": "media", "media": input["media"]},
        metadata=input.get("metadata"),
    )


def _request(
    *,
    channel: MessageChannel,
    sender_type: MessageIdentityType,
    sender_id: str,
    recipient_type: MessageIdentityType,
    recipient_id: str | StructuredPhoneInput,
    message: OutboundMessage,
    metadata: JSONObject | None,
    reply_to: MessageReplyTo | None = None,
) -> CreateMessageRequest:
    recipient: MessageRecipient
    if isinstance(recipient_id, str):
        recipient = {"type": recipient_type, "id": recipient_id}
    else:
        recipient = {
            "type": "phone_e164",
            "country_calling_code": recipient_id["country_calling_code"],
            "national_number": recipient_id["national_number"],
        }

    request: CreateMessageRequest = {
        "channel": channel,
        "sender": {"type": sender_type, "id": sender_id},
        "recipient": recipient,
        "message": message,
    }
    if reply_to is not None:
        request["reply_to"] = reply_to
    if metadata is not None:
        request["metadata"] = metadata
    return request
