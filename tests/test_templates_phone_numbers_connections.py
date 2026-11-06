from __future__ import annotations

import json
from typing import cast

import httpx

from tyxter import Tyxter
from tyxter.types import (
    PhoneNumberResponse,
    ProviderConnectionResponse,
    ProviderCredentialSetupSessionResponse,
    TemplateResponse,
)


def body(request: httpx.Request) -> dict[str, object]:
    return cast(dict[str, object], json.loads(request.read()))


def make_client(seen: list[httpx.Request]) -> Tyxter:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    return Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )


def template_response(parameter_format: str) -> dict[str, object]:
    return {
        "id": "tpl_123",
        "object": "template",
        "name": "order_tracking",
        "language": "en_US",
        "category": "utility",
        "parameter_format": parameter_format,
        "status": "draft",
        "environment": "sandbox",
        "components": [],
        "provider_template_id": None,
        "rejection_reason": None,
        "provider_quality": "unknown",
        "authoring_signals": [],
        "submitted_at": None,
        "approved_at": None,
        "created_at": "2026-08-26T12:00:00Z",
        "updated_at": "2026-08-26T12:00:00Z",
    }


def make_template_client(seen: list[httpx.Request]) -> Tyxter:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        request_body = body(request) if request.content else {}
        parameter_format = request_body.get("parameter_format", "POSITIONAL")
        assert isinstance(parameter_format, str)
        if request.url.path.endswith("/templates/generate"):
            return httpx.Response(
                200,
                json={
                    "object": "template_generation",
                    "name": "order_tracking",
                    "language": "en_US",
                    "category": "utility",
                    "parameter_format": parameter_format,
                    "components": [],
                    "authoring_signals": [],
                },
            )
        return httpx.Response(200, json=template_response(parameter_format))

    return Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )


def phone_response(**overrides: object) -> dict[str, object]:
    return {
        "id": "pn_123",
        "object": "phone_number",
        "source": "byon",
        "status": "active",
        "environment": "sandbox",
        "display_name": "Tyxter Support",
        "ddd": "11",
        "phone": "+5511999999999",
        "provider_number_id": None,
        "meta_phone_number_id": "meta_123",
        "waba_id": "waba_123",
        "quality_rating": "unknown",
        "messaging_tier": "tier_2k",
        "messaging_limit_tier": "META_FUTURE_LIMIT",
        "meta_throughput_tier": None,
        "meta_quality_rating": None,
        "meta_health_synced_at": "2026-09-01T10:00:00Z",
        "current_24h_unique_recipients": 12,
        "remaining_messaging_allowance_estimate": None,
        "verification_code": None,
        "verification_code_received_at": None,
        "monthly_fee_brl": None,
        "error_code": None,
        "error_message": None,
        "created_at": "2026-08-26T12:00:00Z",
        "updated_at": "2026-09-01T10:00:00Z",
        "activated_at": "2026-08-26T12:05:00Z",
        "released_at": None,
        "recent_messages": [],
        **overrides,
    }


def provider_connection_response(**overrides: object) -> dict[str, object]:
    return {
        "id": "pc_123",
        "object": "provider_connection",
        "provider": "meta",
        "channel": "whatsapp",
        "status": "connected",
        "display_name": "Tyxter Support",
        "environment": "sandbox",
        "waba_id": "waba_123",
        "phone_number_id": "meta_phone_123",
        "ig_business_account_id": None,
        "page_id": None,
        "provider_account_id": "account_123",
        "payment_receiver": None,
        "payment_capabilities": None,
        "agentic_capabilities": None,
        "default_participant_id": None,
        "agent_id": None,
        "agentic_api_base_url": None,
        "webhook_secret_configured": True,
        "token_source": "manual",
        "token_expires_at": None,
        "token_refreshed_at": None,
        "token_rotated_at": None,
        "created_at": "2026-09-01T10:00:00Z",
        "updated_at": "2026-09-01T10:00:00Z",
        "disconnected_at": None,
        **overrides,
    }


def test_templates_cover_all_routes_and_only_generate_is_idempotent() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.templates.create(
        {
            "name": "order_ready",
            "language": "en_US",
            "category": "utility",
            "components": [{"type": "BODY", "text": "Ready"}],
        }
    )
    client.templates.generate(
        {
            "description": "Tell a customer their order is ready",
            "language": "en_US",
            "category": "utility",
        },
        idempotency_key="idem_generate",
    )
    client.templates.list(limit=10, starting_after="tpl_1")
    client.templates.retrieve("tpl/2")
    client.templates.update("tpl/2", {"language": "pt_BR"})
    client.templates.submit("tpl/2")
    client.templates.duplicate("tpl/2")
    client.templates.analytics("tpl/2")
    client.templates.estimate_cost("tpl/2", {"recipients": 20})
    client.templates.delete("tpl/2")

    assert body(seen[0])["name"] == "order_ready"
    assert seen[1].headers["idempotency-key"] == "idem_generate"
    assert str(seen[2].url) == ("https://api.test/v1/templates?limit=10&starting_after=tpl_1")
    assert all("idempotency-key" not in request.headers for request in seen[2:])
    assert str(seen[3].url) == "https://api.test/v1/templates/tpl%2F2"
    assert body(seen[4]) == {"language": "pt_BR"}
    assert not seen[5].content
    assert body(seen[6]) == {}
    assert seen[7].url.path.endswith("/analytics")
    assert body(seen[8]) == {"recipients": 20}
    assert seen[9].method == "DELETE"


def test_template_parameter_formats_are_forwarded_and_returned() -> None:
    seen: list[httpx.Request] = []
    client = make_template_client(seen)

    generated = client.templates.generate(
        {
            "description": "Tell a customer their order is ready",
            "language": "en_US",
            "category": "utility",
            "parameter_format": "NAMED",
        }
    )
    created = client.templates.create(
        {
            "name": "order_tracking",
            "language": "en_US",
            "category": "utility",
            "parameter_format": "NAMED",
            "components": [{"type": "BODY", "text": "Hi {{customer_name}}"}],
        }
    )
    updated = client.templates.update("tpl_123", {"parameter_format": "POSITIONAL"})
    duplicated = client.templates.duplicate("tpl_123", {"parameter_format": "NAMED"})

    assert generated["parameter_format"] == "NAMED"
    assert created["parameter_format"] == "NAMED"
    assert updated["parameter_format"] == "POSITIONAL"
    assert duplicated["parameter_format"] == "NAMED"
    assert [body(request) for request in seen] == [
        {
            "description": "Tell a customer their order is ready",
            "language": "en_US",
            "category": "utility",
            "parameter_format": "NAMED",
        },
        {
            "name": "order_tracking",
            "language": "en_US",
            "category": "utility",
            "parameter_format": "NAMED",
            "components": [{"type": "BODY", "text": "Hi {{customer_name}}"}],
        },
        {"parameter_format": "POSITIONAL"},
        {"parameter_format": "NAMED"},
    ]


def test_template_parameter_format_omission_preserves_existing_payloads() -> None:
    seen: list[httpx.Request] = []
    client = make_template_client(seen)

    client.templates.generate(
        {
            "description": "Tell a customer their order is ready",
            "language": "en_US",
            "category": "utility",
        }
    )
    client.templates.create(
        {
            "name": "order_tracking",
            "language": "en_US",
            "category": "utility",
            "components": [{"type": "BODY", "text": "Ready"}],
        }
    )
    client.templates.update("tpl_123", {})
    client.templates.duplicate("tpl_123")

    assert [body(request) for request in seen] == [
        {
            "description": "Tell a customer their order is ready",
            "language": "en_US",
            "category": "utility",
        },
        {
            "name": "order_tracking",
            "language": "en_US",
            "category": "utility",
            "components": [{"type": "BODY", "text": "Ready"}],
        },
        {},
        {},
    ]


def test_template_copy_code_authoring_and_direct_send_shapes_stay_distinct() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.templates.create(
        {
            "name": "winter_coupon",
            "language": "en_US",
            "category": "marketing",
            "components": [
                {"type": "BODY", "text": "Use this coupon at checkout."},
                {"type": "BUTTONS", "buttons": [{"type": "COPY_CODE", "example": "WINTER25"}]},
            ],
        }
    )
    client.whatsapp.send_template(
        {
            "from": "pn_123",
            "to": "+15555550100",
            "name": "order_tracking",
            "language": "en_US",
            "variables": {"1": "Ana"},
        }
    )
    client.whatsapp.send_template(
        {
            "from": "pn_123",
            "to": "+15555550100",
            "name": "winter_coupon",
            "language": "en_US",
            "components": [
                {
                    "type": "button",
                    "sub_type": "copy_code",
                    "index": 0,
                    "parameters": [{"type": "coupon_code", "coupon_code": "WINTER25"}],
                }
            ],
        }
    )

    assert body(seen[0]) == {
        "name": "winter_coupon",
        "language": "en_US",
        "category": "marketing",
        "components": [
            {"type": "BODY", "text": "Use this coupon at checkout."},
            {"type": "BUTTONS", "buttons": [{"type": "COPY_CODE", "example": "WINTER25"}]},
        ],
    }
    assert body(seen[1]) == {
        "channel": "whatsapp",
        "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
        "recipient": {"type": "phone_e164", "id": "+15555550100"},
        "message": {
            "type": "template",
            "template": {
                "name": "order_tracking",
                "language": "en_US",
                "variables": {"1": "Ana"},
            },
        },
    }
    assert body(seen[2]) == {
        "channel": "whatsapp",
        "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
        "recipient": {"type": "phone_e164", "id": "+15555550100"},
        "message": {
            "type": "template",
            "template": {
                "name": "winter_coupon",
                "language": "en_US",
                "components": [
                    {
                        "type": "button",
                        "sub_type": "copy_code",
                        "index": 0,
                        "parameters": [{"type": "coupon_code", "coupon_code": "WINTER25"}],
                    }
                ],
            },
        },
    }


def test_template_response_remains_callable_without_additive_parameter_format() -> None:
    legacy_response = TemplateResponse(
        id="tpl_123",
        object="template",
        name="order_tracking",
        language="en_US",
        category="utility",
        status="draft",
        environment="sandbox",
        components=[],
        provider_template_id=None,
        rejection_reason=None,
        provider_quality="unknown",
        authoring_signals=[],
        submitted_at=None,
        approved_at=None,
        created_at="2026-08-26T12:00:00Z",
        updated_at="2026-08-26T12:00:00Z",
    )

    assert "parameter_format" not in legacy_response


def test_phone_numbers_cover_lifecycle_and_escape_ids() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.phone_numbers.list(limit=10, status="active")
    client.phone_numbers.list_available_regions()
    client.phone_numbers.provision({"ddd": "11"}, idempotency_key="idem_provision")
    client.phone_numbers.connect(
        {"phone": "+5511999999999", "meta_phone_number_id": "meta_1"},
        idempotency_key="idem_connect",
    )
    client.phone_numbers.retrieve("pn/1")
    client.phone_numbers.release("pn/1", idempotency_key="idem_release")
    client.phone_numbers.transfer(
        "pn/1",
        {
            "source_project_id": "prj_a",
            "source_environment_id": "env_a",
            "target_project_id": "prj_b",
            "target_environment_id": "env_b",
            "confirm_phone_number_id": "pn/1",
        },
        idempotency_key="idem_transfer",
    )
    client.phone_numbers.disconnect("pn/1")

    assert seen[0].url.query.decode() == "limit=10&status=active"
    assert seen[1].url.path == "/v1/phone-numbers/available-regions"
    assert [seen[index].headers["idempotency-key"] for index in (2, 3, 5, 6)] == [
        "idem_provision",
        "idem_connect",
        "idem_release",
        "idem_transfer",
    ]
    assert str(seen[4].url) == "https://api.test/v1/phone-numbers/pn%2F1"
    assert not seen[5].content
    assert seen[7].method == "DELETE"


def test_phone_name_review_reads_preserve_future_meta_values() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path == "/v1/phone-numbers":
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        phone_response(
                            verified_name="Tyxter Verified",
                            pending_name_review={
                                "requested_name": "Tyxter Support",
                                "status": "META_FUTURE_PENDING",
                                "observed_at": "2026-09-01T10:00:00Z",
                            },
                            name_review=None,
                        )
                    ],
                    "has_more": False,
                    "next_cursor": None,
                },
            )
        return httpx.Response(
            200,
            json=phone_response(
                verified_name=None,
                pending_name_review=None,
                name_review={
                    "requested_name": None,
                    "decision": "META_FUTURE_DECISION",
                    "reason": None,
                    "reviewed_at": "2026-09-01T11:00:00Z",
                },
            ),
        )

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    listed = client.phone_numbers.list()
    retrieved = client.phone_numbers.retrieve("pn/123")

    assert listed["data"][0]["messaging_tier"] == "tier_2k"
    assert listed["data"][0]["verified_name"] == "Tyxter Verified"
    assert listed["data"][0]["pending_name_review"] == {
        "requested_name": "Tyxter Support",
        "status": "META_FUTURE_PENDING",
        "observed_at": "2026-09-01T10:00:00Z",
    }
    assert listed["data"][0]["name_review"] is None
    assert retrieved["verified_name"] is None
    assert retrieved["pending_name_review"] is None
    assert retrieved["name_review"] == {
        "requested_name": None,
        "decision": "META_FUTURE_DECISION",
        "reason": None,
        "reviewed_at": "2026-09-01T11:00:00Z",
    }
    assert [request.method for request in seen] == ["GET", "GET"]
    assert str(seen[0].url) == "https://api.test/v1/phone-numbers"
    assert str(seen[1].url) == "https://api.test/v1/phone-numbers/pn%2F123"


def test_phone_number_response_remains_callable_without_additive_review_fields() -> None:
    legacy_response = PhoneNumberResponse(
        id="pn_123",
        object="phone_number",
        source="byon",
        status="active",
        environment="sandbox",
        display_name="Tyxter Support",
        ddd="11",
        phone="+5511999999999",
        provider_number_id=None,
        meta_phone_number_id="meta_123",
        waba_id="waba_123",
        quality_rating="unknown",
        messaging_tier="tier_1k",
        messaging_limit_tier=None,
        meta_throughput_tier=None,
        meta_quality_rating=None,
        meta_health_synced_at=None,
        current_24h_unique_recipients=0,
        remaining_messaging_allowance_estimate=None,
        verification_code=None,
        verification_code_received_at=None,
        monthly_fee_brl=None,
        error_code=None,
        error_message=None,
        created_at="2026-08-26T12:00:00Z",
        updated_at="2026-08-26T12:00:00Z",
        activated_at="2026-08-26T12:05:00Z",
        released_at=None,
        recent_messages=[],
    )

    assert "verified_name" not in legacy_response
    assert "pending_name_review" not in legacy_response
    assert "name_review" not in legacy_response


def test_provider_connections_and_credential_setup_match_header_capabilities() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.provider_connections.list(limit=5, starting_after="pc_1")
    client.provider_connections.status()
    client.provider_connections.meta_onboarding()
    client.provider_connections.exchange_meta_oauth(
        {"code": "code", "signup_session_id": "signup_123"}
    )
    client.provider_connections.retrieve("pc/2")
    client.provider_connections.delete("pc/2")
    client.provider_credential_setup_sessions.create(
        {"target": "meta.whatsapp"}, idempotency_key="idem_setup"
    )
    client.provider_credential_setup_sessions.retrieve("req/1")
    client.provider_connections.complete_meta_registration("pc/2", idempotency_key="idem_complete")

    assert seen[0].url.query.decode() == "limit=5&starting_after=pc_1"
    assert seen[1].url.path.endswith("/status")
    assert seen[2].url.path.endswith("/meta/onboarding")
    assert body(seen[3]) == {"code": "code", "signup_session_id": "signup_123"}
    assert all("idempotency-key" not in request.headers for request in seen[:6])
    assert str(seen[4].url) == "https://api.test/v1/provider-connections/pc%2F2"
    assert seen[5].method == "DELETE"
    assert seen[6].headers["idempotency-key"] == "idem_setup"
    assert str(seen[7].url) == ("https://api.test/v1/provider-credential-setup-sessions/req%2F1")
    assert seen[8].method == "POST"
    assert str(seen[8].url) == (
        "https://api.test/v1/provider-connections/pc%2F2/meta/complete-registration"
    )
    assert seen[8].headers["idempotency-key"] == "idem_complete"


def test_provider_connection_availability_reads_preserve_advisory_observations() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path == "/v1/provider-connections":
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        provider_connection_response(
                            last_policy_warning_type="META_FUTURE_WARNING",
                            last_policy_warning_at="2026-09-01T10:05:00Z",
                            send_capability="blocked",
                            send_block_codes=[141006, 141011],
                            send_capability_observed_at="2026-09-01T10:06:00Z",
                            waba_send_capabilities=[
                                {
                                    "waba_id": "waba_123",
                                    "send_capability": "blocked",
                                    "send_block_codes": [141006, 141011],
                                    "observed_at": "2026-09-01T10:06:00Z",
                                }
                            ],
                            waba_ban_date=None,
                        )
                    ],
                    "has_more": False,
                    "next_cursor": None,
                },
            )
        return httpx.Response(
            200,
            json=provider_connection_response(
                last_policy_warning_type=None,
                last_policy_warning_at=None,
                send_capability="available",
                send_block_codes=[],
                send_capability_observed_at="2026-09-01T11:06:00Z",
                waba_send_capabilities=[
                    {
                        "waba_id": "waba_123",
                        "send_capability": "available",
                        "send_block_codes": [],
                        "observed_at": "2026-09-01T11:06:00Z",
                    }
                ],
                waba_ban_date="2026-09-10",
            ),
        )

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    blocked = client.provider_connections.list()
    available = client.provider_connections.retrieve("pc/123")

    blocked_connection = blocked["data"][0]
    assert blocked_connection["last_policy_warning_type"] == "META_FUTURE_WARNING"
    assert blocked_connection["last_policy_warning_at"] == "2026-09-01T10:05:00Z"
    assert blocked_connection["send_capability"] == "blocked"
    assert blocked_connection["send_block_codes"] == [141006, 141011]
    assert blocked_connection["send_capability_observed_at"] == "2026-09-01T10:06:00Z"
    assert blocked_connection["waba_send_capabilities"] == [
        {
            "waba_id": "waba_123",
            "send_capability": "blocked",
            "send_block_codes": [141006, 141011],
            "observed_at": "2026-09-01T10:06:00Z",
        }
    ]
    assert blocked_connection["waba_ban_date"] is None
    assert available["last_policy_warning_type"] is None
    assert available["last_policy_warning_at"] is None
    assert available["send_capability"] == "available"
    assert available["send_block_codes"] == []
    assert available["send_capability_observed_at"] == "2026-09-01T11:06:00Z"
    assert available["waba_ban_date"] == "2026-09-10"
    assert [request.method for request in seen] == ["GET", "GET"]
    assert str(seen[0].url) == "https://api.test/v1/provider-connections"
    assert str(seen[1].url) == "https://api.test/v1/provider-connections/pc%2F123"


def test_provider_connection_response_remains_callable_without_availability_fields() -> None:
    legacy_response = ProviderConnectionResponse(
        id="pc_123",
        object="provider_connection",
        provider="meta",
        channel="whatsapp",
        status="connected",
        display_name="Tyxter Support",
        environment="sandbox",
        waba_id="waba_123",
        phone_number_id="meta_phone_123",
        ig_business_account_id=None,
        page_id=None,
        provider_account_id="account_123",
        payment_receiver=None,
        payment_capabilities=None,
        agentic_capabilities=None,
        default_participant_id=None,
        agent_id=None,
        agentic_api_base_url=None,
        webhook_secret_configured=True,
        token_source="manual",
        token_expires_at=None,
        token_refreshed_at=None,
        token_rotated_at=None,
        created_at="2026-09-01T10:00:00Z",
        updated_at="2026-09-01T10:00:00Z",
        disconnected_at=None,
    )

    assert "send_capability" not in legacy_response
    assert "waba_send_capabilities" not in legacy_response


def test_provider_credential_setup_stt_and_legacy_response_constructor_are_supported() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.provider_credential_setup_sessions.create({"target": "openai.stt"})
    legacy_response = ProviderCredentialSetupSessionResponse(
        object="provider_credential_setup_session",
        request_id="pcs_123",
        target="openai.tts",
        status="pending",
        project_id="prj_123",
        project_slug="demo",
        environment_id="env_123",
        environment="production",
        setup_url="https://setup.example.test/pcs_123",
        poll_url="https://api.example.test/v1/provider-credential-setup-sessions/pcs_123",
        expires_at="2026-08-10T12:00:00Z",
        completed_at=None,
        denied_at=None,
        completed_provider_connection_id=None,
        completed_tts_provider=None,
        created_at="2026-08-10T10:00:00Z",
        updated_at="2026-08-10T10:00:00Z",
    )

    assert body(seen[0]) == {"target": "openai.stt"}
    assert "completed_stt_provider" not in legacy_response


def test_provider_credential_setup_result_helpers_delegate_once_with_the_same_arguments() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.provider_credential_setup_sessions.create_result(
        {"target": "openai.stt"},
        idempotency_key="idem_stt_setup",
    )
    client.provider_credential_setup_sessions.retrieve_result("pcs/123")

    assert len(seen) == 2
    assert seen[0].method == "POST"
    assert seen[0].url.path == "/v1/provider-credential-setup-sessions"
    assert body(seen[0]) == {"target": "openai.stt"}
    assert seen[0].headers["idempotency-key"] == "idem_stt_setup"
    assert seen[1].method == "GET"
    assert str(seen[1].url) == ("https://api.test/v1/provider-credential-setup-sessions/pcs%2F123")


def test_meta_signup_sessions_cover_create_and_poll() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.meta_signup_sessions.create(
        {
            "return_url": "https://merchant.example/meta/callback",
            "end_customer_ref": "customer_123",
        },
        idempotency_key="idem_meta_signup",
    )
    client.meta_signup_sessions.retrieve("mss/123")

    assert seen[0].method == "POST"
    assert str(seen[0].url) == "https://api.test/v1/meta-signup-sessions"
    assert seen[0].headers["idempotency-key"] == "idem_meta_signup"
    assert body(seen[0]) == {
        "return_url": "https://merchant.example/meta/callback",
        "end_customer_ref": "customer_123",
    }
    assert seen[1].method == "GET"
    assert str(seen[1].url) == "https://api.test/v1/meta-signup-sessions/mss%2F123"


def test_audiences_cover_crud_without_stale_js_headers() -> None:
    seen: list[httpx.Request] = []
    client = make_client(seen)

    client.audiences.create({"name": "Customers", "contact_ids": ["ct_1"]})
    client.audiences.list(limit=5, starting_after="aud_1")
    client.audiences.retrieve("aud/2")
    client.audiences.update("aud/2", {"description": "Active customers"})
    client.audiences.delete("aud/2")

    assert body(seen[0]) == {"name": "Customers", "contact_ids": ["ct_1"]}
    assert str(seen[1].url) == ("https://api.test/v1/audiences?limit=5&starting_after=aud_1")
    assert str(seen[2].url) == "https://api.test/v1/audiences/aud%2F2"
    assert body(seen[3]) == {"description": "Active customers"}
    assert seen[4].method == "DELETE"
    assert all("idempotency-key" not in request.headers for request in seen)
    assert all("tyxter-trace-id" not in request.headers for request in seen)
