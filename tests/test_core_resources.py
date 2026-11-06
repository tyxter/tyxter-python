from __future__ import annotations

import json
from collections.abc import Callable
from typing import cast

import httpx
import pytest

from tyxter import Tyxter


def make_client() -> tuple[Tyxter, list[httpx.Request]]:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    return (
        Tyxter(
            api_key="tx_sandbox_test",
            base_url="https://api.test",
            transport=httpx.MockTransport(handler),
        ),
        seen,
    )


def body(request: httpx.Request) -> dict[str, object]:
    return cast(dict[str, object], json.loads(request.read()))


def test_account_resource_uses_both_public_identity_routes() -> None:
    client, seen = make_client()

    client.account.retrieve()
    client.account.me()

    assert [(request.method, request.url.path) for request in seen] == [
        ("GET", "/v1/account"),
        ("GET", "/v1/me"),
    ]


# Canonical deprecates WhatsApp Channel helpers for type checkers only; no runtime warning.
@pytest.mark.filterwarnings("error::DeprecationWarning")
def test_channel_resources_build_canonical_message_requests() -> None:
    client, seen = make_client()

    client.whatsapp.send_text(
        {
            "from": "pn_123",
            "to": "+15555550100",
            "body": "hello",
            "preview_url": True,
        },
        idempotency_key="idem_wa",
        trace_id="trc_wa",
    )
    client.instagram.send_text({"account_id": "ig_123", "user_id": "igsid_456", "body": "hello"})
    client.whatsapp_channels.publish_media(
        {"channel_id": "channel_123", "media": {"kind": "image", "link": "https://x/y"}}
    )

    assert body(seen[0]) == {
        "channel": "whatsapp",
        "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
        "recipient": {"type": "phone_e164", "id": "+15555550100"},
        "message": {"type": "text", "text": {"body": "hello", "preview_url": True}},
    }
    assert seen[0].headers["idempotency-key"] == "idem_wa"
    assert seen[0].headers["tyxter-trace-id"] == "trc_wa"
    assert body(seen[1]) == {
        "channel": "instagram",
        "sender": {"type": "instagram_account", "id": "ig_123"},
        "recipient": {"type": "instagram_user", "id": "igsid_456"},
        "message": {"type": "text", "text": {"body": "hello"}},
    }
    assert body(seen[2]) == {
        "channel": "whatsapp_channel",
        "sender": {"type": "whatsapp_channel", "id": "channel_123"},
        "recipient": {"type": "whatsapp_channel_audience", "id": "followers"},
        "message": {"type": "media", "media": {"kind": "image", "link": "https://x/y"}},
    }


def test_channel_media_resources_preserve_voice_intent_and_instagram_omission() -> None:
    client, seen = make_client()

    client.whatsapp.send_media(
        {
            "from": "pn_123",
            "to": "+15555550100",
            "media": {
                "kind": "audio",
                "link": "https://cdn.example.test/voice-note.ogg",
                "voice": True,
            },
        }
    )
    client.messages.send_media(
        {
            "channel": "whatsapp",
            "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
            "recipient": {"type": "phone_e164", "id": "+15555550100"},
            "media": {
                "kind": "audio",
                "link": "https://cdn.example.test/ordinary-audio.ogg",
                "voice": False,
            },
        }
    )
    client.instagram.send_media(
        {
            "account_id": "ig_123",
            "user_id": "igsid_456",
            "media": {"kind": "image", "link": "https://cdn.example.test/photo.jpg"},
        }
    )
    client.messages.create(
        {
            "channel": "instagram",
            "sender": {"type": "instagram_account", "id": "ig_123"},
            "recipient": {"type": "instagram_user", "id": "igsid_456"},
            "message": {
                "type": "media",
                "media": {"kind": "image", "link": "https://cdn.example.test/photo.jpg"},
            },
        }
    )
    client.messages.send_media(
        {
            "channel": "instagram",
            "sender": {"type": "instagram_account", "id": "ig_123"},
            "recipient": {"type": "instagram_user", "id": "igsid_456"},
            "media": {"kind": "image", "link": "https://cdn.example.test/photo.jpg"},
        }
    )

    assert body(seen[0])["message"] == {
        "type": "media",
        "media": {
            "kind": "audio",
            "link": "https://cdn.example.test/voice-note.ogg",
            "voice": True,
        },
    }
    assert body(seen[1])["message"] == {
        "type": "media",
        "media": {
            "kind": "audio",
            "link": "https://cdn.example.test/ordinary-audio.ogg",
            "voice": False,
        },
    }
    assert body(seen[2])["message"] == {
        "type": "media",
        "media": {"kind": "image", "link": "https://cdn.example.test/photo.jpg"},
    }
    assert body(seen[3])["message"] == {
        "type": "media",
        "media": {"kind": "image", "link": "https://cdn.example.test/photo.jpg"},
    }
    assert body(seen[4])["message"] == {
        "type": "media",
        "media": {"kind": "image", "link": "https://cdn.example.test/photo.jpg"},
    }


def test_sandbox_resource_covers_quickstart_and_deterministic_controls() -> None:
    client, seen = make_client()

    client.sandbox.quickstart()
    client.sandbox.inbound_messages.create(
        {"from": "+15555550100", "to": "pn_123", "type": "text", "text": {"body": "hi"}},
        idempotency_key="idem_inbound",
        trace_id="trc_inbound",
    )
    client.sandbox.inbound_messages.create(
        {
            "from": "+15555550100",
            "to": "pn_123",
            "type": "unsupported",
            "unsupported": {"provider_type": "video_note"},
        }
    )
    client.sandbox.inbound_messages.create(
        {"from": "+15555550100", "to": "pn_123", "type": "unknown"}
    )
    client.sandbox.templates.set_status(
        "tmpl/123",
        {"status": "rejected", "rejection_reason": "fixture"},
        trace_id="trc_template",
    )
    client.sandbox.payments.set_status(
        "pay/123",
        {"status": "paid", "provider_event_id": "provider_evt_1"},
        idempotency_key="idem_payment",
        trace_id="trc_payment",
    )
    client.sandbox.llm.set_failure(
        {"failure": "provider_down", "ttl_seconds": 60},
        idempotency_key="idem_llm",
        trace_id="trc_llm",
    )

    assert [(request.method, request.url.path) for request in seen] == [
        ("GET", "/v1/sandbox/quickstart"),
        ("POST", "/v1/sandbox/inbound-messages"),
        ("POST", "/v1/sandbox/inbound-messages"),
        ("POST", "/v1/sandbox/inbound-messages"),
        ("POST", "/v1/sandbox/templates/tmpl/123/status"),
        ("POST", "/v1/sandbox/payments/pay/123/status"),
        ("POST", "/v1/sandbox/llm/failure"),
    ]
    assert body(seen[2]) == {
        "from": "+15555550100",
        "to": "pn_123",
        "type": "unsupported",
        "unsupported": {"provider_type": "video_note"},
    }
    assert body(seen[3]) == {"from": "+15555550100", "to": "pn_123", "type": "unknown"}
    assert str(seen[4].url) == "https://api.test/v1/sandbox/templates/tmpl%2F123/status"
    assert str(seen[5].url) == "https://api.test/v1/sandbox/payments/pay%2F123/status"
    assert seen[1].headers["idempotency-key"] == "idem_inbound"
    assert seen[1].headers["tyxter-trace-id"] == "trc_inbound"
    assert seen[4].headers["tyxter-trace-id"] == "trc_template"
    assert seen[5].headers["idempotency-key"] == "idem_payment"
    assert seen[5].headers["tyxter-trace-id"] == "trc_payment"
    assert body(seen[6]) == {"failure": "provider_down", "ttl_seconds": 60}
    assert seen[6].headers["idempotency-key"] == "idem_llm"
    assert seen[6].headers["tyxter-trace-id"] == "trc_llm"


def test_webhook_events_resource_covers_listen_inspect_and_resend_routes() -> None:
    client, seen = make_client()

    client.webhook_events.list(
        limit=10,
        event_types="message.sent,message.failed",
        status="failed",
    )
    client.webhook_events.listen(
        cursor="cur_1",
        start_at="tail",
        wait_ms=1000,
        listen_session_id="lsn_1",
    )
    client.webhook_events.create_listen_session({"ttl_seconds": 60, "reason": "diagnostic"})
    client.webhook_events.disable_listen_session("lsn/1")
    client.webhook_events.retrieve_listen_event(
        "outbox/1", webhook_endpoint_id="whe_1", listen_session_id="lsn_1"
    )
    client.webhook_events.retrieve("evt/1")
    client.webhook_events.resend("evt/1")
    client.webhook_events.bulk_resend({"event_type": "message.failed", "limit": 25})

    assert seen[0].url.query.decode() == (
        "limit=10&event_types=message.sent%2Cmessage.failed&status=failed"
    )
    assert seen[1].url.query.decode() == (
        "cursor=cur_1&start_at=tail&wait_ms=1000&listen_session_id=lsn_1"
    )
    assert body(seen[2]) == {"ttl_seconds": 60, "reason": "diagnostic"}
    assert str(seen[3].url) == "https://api.test/v1/webhook-events/listen-sessions/lsn%2F1"
    assert str(seen[4].url) == (
        "https://api.test/v1/webhook-events/listen/outbox%2F1"
        "?webhook_endpoint_id=whe_1&listen_session_id=lsn_1"
    )
    assert str(seen[5].url) == "https://api.test/v1/webhook-events/evt%2F1"
    assert str(seen[6].url) == "https://api.test/v1/webhook-events/evt%2F1/resend"
    assert not seen[6].content
    assert body(seen[7]) == {"event_type": "message.failed", "limit": 25}


_REPLY_TO = {"message_id": "msg_inbound_123"}
_ROUTE = {"from": "pn_123", "to": "+15555550100", "reply_to": _REPLY_TO, "metadata": {"k": "v"}}
_SEND_ROUTE = {
    "channel": "whatsapp",
    "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
    "recipient": {"type": "whatsapp_group", "id": "grp_123"},
    "reply_to": _REPLY_TO,
    "metadata": {"k": "v"},
}
_TTS = {"type": "tts", "provider": "openai", "text": "oi", "voice": "alloy", "language": "pt"}
_FLOW = {"type": "flow", "body": {"text": "Book"}, "action": {"name": "flow"}}
_INTERACTIVE = {"type": "button", "body": {"text": "Pick"}, "action": {"buttons": []}}


@pytest.mark.parametrize(
    ("send", "message"),
    [
        pytest.param(
            lambda client: client.whatsapp.send_text({**_ROUTE, "body": "hi"}),
            {"type": "text", "text": {"body": "hi"}},
            id="whatsapp.send_text",
        ),
        pytest.param(
            lambda client: client.whatsapp.send_media(
                {**_ROUTE, "media": {"kind": "image", "link": "https://x/y"}}
            ),
            {"type": "media", "media": {"kind": "image", "link": "https://x/y"}},
            id="whatsapp.send_media",
        ),
        pytest.param(
            lambda client: client.whatsapp.send_audio_from_text({**_ROUTE, "tts": _TTS}),
            {"type": "media", "media": {"kind": "audio", "source": _TTS}},
            id="whatsapp.send_audio_from_text",
        ),
        pytest.param(
            lambda client: client.whatsapp.send_template(
                {**_ROUTE, "name": "promo", "language": "pt_BR"}
            ),
            {"type": "template", "template": {"name": "promo", "language": "pt_BR"}},
            id="whatsapp.send_template",
        ),
        pytest.param(
            lambda client: client.whatsapp.send_interactive(
                {**_ROUTE, "interactive": _INTERACTIVE}
            ),
            {"type": "interactive", "interactive": _INTERACTIVE},
            id="whatsapp.send_interactive",
        ),
        pytest.param(
            lambda client: client.whatsapp.send_flow({**_ROUTE, "flow": _FLOW}),
            {"type": "flow", "flow": _FLOW},
            id="whatsapp.send_flow",
        ),
        pytest.param(
            lambda client: client.messages.send_text({**_SEND_ROUTE, "text": {"body": "hi"}}),
            {"type": "text", "text": {"body": "hi"}},
            id="messages.send_text",
        ),
    ],
)
def test_whatsapp_send_helpers_keep_the_quoted_message(
    send: Callable[[Tyxter], object], message: dict[str, object]
) -> None:
    client, seen = make_client()

    send(client)

    sent = body(seen[0])
    assert sent["reply_to"] == _REPLY_TO
    assert sent["message"] == message
    assert sent["metadata"] == {"k": "v"}
