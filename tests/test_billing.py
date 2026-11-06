from __future__ import annotations

import json
from typing import cast

import httpx
import pytest

from tyxter import Tyxter


def body(request: httpx.Request) -> dict[str, object]:
    return cast(dict[str, object], json.loads(request.read()))


def test_billing_covers_manifest_routes_and_headers() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    client.billing.balance()
    client.billing.list_plans()
    client.billing.current_plan()
    client.billing.subscribe_plan({"plan_offering_id": "growth"}, idempotency_key="idem_subscribe")
    client.billing.change_plan({"plan_offering_id": "scale"}, idempotency_key="idem_change")
    client.billing.cancel_plan(idempotency_key="idem_cancel")
    client.billing.list_packages(limit=10, status="succeeded")
    client.billing.purchase_package(
        {"package_code": "pkg_10k", "payment_method": "card", "payment_method_id": "pm_card_1"},
        idempotency_key="idem_purchase",
    )
    client.billing.list_payment_methods()
    client.billing.save_payment_method(
        {"stripe_payment_method_id": "pm_1", "set_default": True}, idempotency_key="idem_save"
    )
    client.billing.create_payment_method_setup_intent(idempotency_key="idem_setup")
    client.billing.set_default_payment_method("pm/1", idempotency_key="idem_default")
    client.billing.delete_payment_method("pm/1", idempotency_key="idem_delete")
    client.billing.retrieve_auto_topup()
    client.billing.update_auto_topup(
        {"enabled": True, "threshold_brl": "10.0000", "amount_brl": "50.0000"},
        idempotency_key="idem_auto",
    )
    client.billing.list_ledger(environment="sandbox", source_type="usage")
    client.billing.list_invoices(project_id="prj_1")
    client.billing.download_invoice("inv/1")
    client.rate_cards.list(limit=5, currency="brl")
    client.rate_cards.retrieve_current()

    assert body(seen[3]) == {"plan_offering_id": "growth"}
    assert not seen[5].content
    assert seen[6].url.query.decode() == "limit=10&status=succeeded"
    assert not seen[10].content
    assert str(seen[11].url).endswith("/payment-methods/pm%2F1/default")
    assert str(seen[12].url).endswith("/payment-methods/pm%2F1")
    assert seen[15].url.query.decode() == "environment=sandbox&source_type=usage"
    assert seen[16].url.query.decode() == "project_id=prj_1"
    assert str(seen[17].url).endswith("/invoices/inv%2F1/download")
    assert seen[18].url.query.decode() == "limit=5&currency=brl"
    expected_idempotency = {
        3: "idem_subscribe",
        4: "idem_change",
        5: "idem_cancel",
        7: "idem_purchase",
        9: "idem_save",
        10: "idem_setup",
        11: "idem_default",
        12: "idem_delete",
        14: "idem_auto",
    }
    assert {
        index: request.headers["idempotency-key"]
        for index, request in enumerate(seen)
        if "idempotency-key" in request.headers
    } == expected_idempotency


def test_purchase_package_preserves_promotion_response_without_promotion_request() -> None:
    seen: list[httpx.Request] = []
    promotion_response = {
        "id": "topup_promotion_123",
        "object": "credit_topup",
        "kind": "cash",
        "status": "succeeded",
        "amount_brl": "25.00",
        "payment_method": "promotion",
        "package_code": None,
        "quota_messages": None,
        "quota_remaining": None,
        "stripe_payment_intent_id": None,
        "stripe_client_secret": None,
        "provider": "promotion",
        "abacate_charge_id": None,
        "pix_copy_paste": None,
        "pix_qr_code_base64": None,
        "pix_expires_at": None,
        "created_at": "2026-09-01T10:00:00Z",
        "completed_at": "2026-09-01T10:00:00Z",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=promotion_response)

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    topup = client.billing.purchase_package(
        {"package_code": "pkg_10k", "payment_method": "card"},
        idempotency_key="idem_promotion_response",
    )

    assert topup == promotion_response
    assert len(seen) == 1
    assert seen[0].method == "POST"
    assert str(seen[0].url) == "https://api.test/v1/billing/packages/purchase"
    assert seen[0].headers["idempotency-key"] == "idem_promotion_response"
    assert body(seen[0]) == {"package_code": "pkg_10k", "payment_method": "card"}


# Canonical deprecates these reads for type checkers only; they must not warn at runtime.
@pytest.mark.filterwarnings("error::DeprecationWarning")
def test_phone_renewals_use_exact_query_and_encoded_cycle_paths() -> None:
    seen: list[httpx.Request] = []
    renewal = {
        "id": "phr_1",
        "object": "phone_renewal",
        "status": "funding_required",
        "actionable_state": "at_risk",
        "recommended_action": "add_credit_or_enable_auto_topup",
        "phone_number_id": "pn_1",
        "display_name": "Support",
        "phone": "+5511999999999",
        "period_start": "2026-09-01T00:00:00Z",
        "period_end": "2026-10-01T00:00:00Z",
        "amount_brl": "49.00",
        "currency": "brl",
        "upcoming_notice_at": None,
        "funding_scheduled_at": None,
        "funding_attempted_at": None,
        "next_funding_attempt_at": None,
        "funded_at": None,
        "release_cutoff_at": None,
        "release_requested_at": None,
        "renewed_at": None,
        "released_at": None,
        "cancelled_at": None,
        "terminal_at": None,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path == "/v1/billing/phone-renewals":
            return httpx.Response(
                200,
                json={"object": "list", "data": [renewal], "has_more": False, "next_cursor": None},
            )
        return httpx.Response(200, json=renewal)

    client = Tyxter(
        api_key="tx_sandbox_test",
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )

    listed = client.billing.list_phone_renewals(
        limit=5, starting_after="phr_0", status="funding_required"
    )
    retrieved = client.billing.retrieve_phone_renewal("phr/1")

    assert listed["data"][0]["recommended_action"] == "add_credit_or_enable_auto_topup"
    assert retrieved["actionable_state"] == "at_risk"
    assert str(seen[0].url) == (
        "https://api.test/v1/billing/phone-renewals?limit=5&starting_after=phr_0&status=funding_required"
    )
    assert str(seen[1].url) == "https://api.test/v1/billing/phone-renewals/phr%2F1"
    assert all("idempotency-key" not in request.headers for request in seen)
    assert all("tyxter-trace-id" not in request.headers for request in seen)
