# Tyxter Python SDK

Typed, synchronous Python client for the Tyxter Messaging API. The package uses
`httpx`, supports Python 3.10–3.13, and tracks the canonical public launch
manifest.

The SDK is alpha software. Additive response fields are compatible and are
tolerated at runtime. Removing or renaming a public method, field, or stable
`error.code` requires a deprecation cycle.

The `0.12.0` source line is the release candidate for canonical `tyxter` 0.12.0,
which npm publishes. PyPI serves `0.8.0` until the repository's Trusted
Publishing workflow publishes this version. Editing the version or these docs
alone does not publish another package, create a tag, or change PyPI state.

## Install

Install the published SDK with `pip install tyxter`, or pin the published
release with `pip install tyxter==0.8.0`; neither includes the 0.12.0 candidate
documented in this checkout. To evaluate the current repository source instead,
install a checkout; doing so does not publish it:

```bash
git clone https://github.com/tyxter/tyxter-python.git
cd tyxter-python
git checkout main
uv sync --locked --extra dev
uv run python -c "import tyxter; print(tyxter.__version__)"
```

For routine development checks in that environment:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
```

## First message

```python
import os

from tyxter import Tyxter

with Tyxter(api_key=os.environ["TYXTER_API_KEY"]) as client:
    account = client.account.retrieve()
    sender_id = client.sandbox.quickstart()["sender"]["default_sender_id"]
    if sender_id is None:
        raise RuntimeError("sandbox sender is not configured")

    # A customer inbound opens WhatsApp's 24-hour free-form service window.
    client.sandbox.inbound_messages.create(
        {
            "from": "+15555550100",
            "to": sender_id,
            "type": "text",
            "text": {"body": "ping"},
        },
        idempotency_key="idem_python_open_window_001",
    )
    message = client.whatsapp.send_text(
        {
            "from": sender_id,
            "to": "+15555550100",
            "body": "Hello from Tyxter Python.",
        },
        idempotency_key="idem_python_first_message_001",
    )
    detail = client.messages.retrieve(message["id"])

print(account["environment"]["kind"], detail["status"], message["trace_id"])
```

Set `base_url="http://localhost:3001"` when using the local stack.

## Native Pix order details

WhatsApp interactive sends accept the existing button/list payloads and the typed
native `order_details` Pix variant. A recipient can remain an E.164 string or use
the structured calling-code form; the SDK sends the latter unchanged as the public
API's `country_calling_code` and `national_number` fields.

```python
client.whatsapp.send_interactive(
    {
        "from": sender_id,
        "to": {"country_calling_code": "55", "national_number": "11999999999"},
        "interactive": {
            "type": "order_details",
            "header": {"type": "image", "link": "https://cdn.example.test/order.png"},
            "body": {"text": "Review and pay"},
            "footer": {"text": "Tyxter Store"},
            "action": {
                "name": "review_and_pay",
                "parameters": {
                    "reference_id": "order_123",
                    "type": "physical-goods",
                    "payment_type": "br",
                    "payment_settings": (
                        {
                            "type": "pix_dynamic_code",
                            "pix_dynamic_code": {
                                "code": "000201010212",
                                "merchant_name": "Tyxter Store",
                                "key": "merchant@example.com",
                                "key_type": "EMAIL",
                            },
                        },
                    ),
                    "currency": "BRL",
                    "total_amount": {"value": 12990, "offset": 100},
                },
            },
        },
    }
)
```

Native Pix order details are for a Brazil WABA eligible for Meta's Payments API.
The API accepts the request after its own checks, but Meta evaluates WABA and
message eligibility at provider-send time, so acceptance does not promise
delivery. This interactive message has no Tyxter `payment_id` resolution or
order-status update, and Meta does not reconcile settlement; confirm settlement
with the merchant or PSP.

## Inbound audio transcription and retries

Use `messages.request_transcription(message_id, {"language": "pt"})` to opt an
inbound WhatsApp-audio message into asynchronous transcription, then poll the
same receipt with `messages.retrieve_transcription(message_id)`. The typed
receipt exposes `pending`, `succeeded`, or `failed`, its text/error fields, and
its `trace_id`. A pending or succeeded request replays its receipt only when the
language is omitted or matches; a failed receipt returns
`transcription_retry_required`.

Requesting transcription never buys a second attempt. Start one bounded manual
retry only with `messages.retry_transcription()`. Its caller-supplied, nonblank
idempotency key is trimmed before sending; reuse that same key to replay the
accepted retry without opening another generation. A retry always reuses the
original source; it cannot replace media that has expired or is structurally
unavailable. If the API returns `transcription_retry_rate_limited`, wait its
`retry_after_ms` value and replay the same logical retry command with the same
key. Use a fresh key only for a distinct retry command.

Both `request_transcription()` and `retry_transcription()` accept optional
advisory `prompt` and `keywords`. The server trims the prompt and rejects one
longer than 1024 UTF-16 code units; `keywords` allows at most 50 trimmed terms of
1–128 UTF-16 code units each, without CR, LF, U+2028, U+2029 or angle brackets,
and keeps order, case and duplicates. Invalid hints return
`invalid_transcription_request`; a request whose hints differ from the newest
generation returns `transcription_hints_conflict`. A retry inherits omitted
hints, and an empty prompt or keyword list clears that field. Hints never appear
in transcript responses or webhooks. A keyed `request_transcription()` response,
and its replay, carries `text: None`; read the text with
`retrieve_transcription()`.

Subscribe to both terminal events: `message.media_transcribed` and
`message.media_transcription_failed`. The success event carries the transcript's
speech, provider, model, and duration; the failure event is failure-safe and
carries its stable `error_code` without those success-only fields.

```python
client.messages.retry_transcription(
    "msg_123",
    {"language": "pt"},
    idempotency_key="transcription-retry-msg_123-1",
    trace_id="trc_transcription_retry",
)
```

## Inbound media, typing, and message observability

Inbound message reads and lists expose a typed `media` descriptor with the
Tyxter `mda_*` asset ID. Use `client.media.list(source="inbound_provider")` to
find imported provider media and `client.media.create_download_url(asset_id)`
to mint a fresh, short-lived `download_url`; do not assume a previous capability
URL remains valid. A consumed inbound descriptor also has a `download` hint
(`{"method": "GET", "path": ...}`); treat it as the API's current download
affordance rather than a durable provider URL. Failed media carries `failure`,
while expired and deleted media carry neither a download nor a failure.

For WhatsApp OGG/Opus mono audio, `client.whatsapp.send_media(...)` accepts
`"voice": True` to request a native voice note; omit it or pass `False` for
ordinary audio. Instagram media has a separate input shape: ordinary image,
document, audio, and video sends remain valid, but it deliberately has no
`voice` field. An inbound WhatsApp sender can be phone-less, represented on
reads only as `{"type": "phone_e164", "id": ""}`; do not reuse it as an
outbound recipient. `type == "unsupported"` means the provider withheld the
content and supplies an `unsupported` descriptor when available, whereas
`type == "unknown"` means content arrived but has no typed projection yet—read
its raw `payload` through `retrieve()` or `list(include="payload")` instead of
treating it as a refusal. A default list row may have `payload` set to `None`.

For a WhatsApp typing indicator, pass the Tyxter message ID from
`message.received.data.message_id`. The webhook envelope's top-level `id` is the
event ID and `data.provider_message_id` is Meta's reference, so neither targets
`client.messages.typing()`. The indicator response is an `accepted` receipt.

Message accepts and reads expose `trace_id` for correlation. `retrieve()` also
returns the message event timeline, while message rows expose `status_reason`,
terminal error details, provider error information, and
`delivery_unconfirmed_at` when provider acceptance has not yet been followed by
a delivery status. An accepted send is not a delivery guarantee.

The complete deterministic example at
`examples/sandbox_send_and_verify.py` sends a sandbox message, retrieves it,
polls the public webhook-listen API, and verifies the returned raw-body
signature preview without using dashboard or internal routes.

```bash
TYXTER_API_KEY=tx_sandbox_... \
TYXTER_WEBHOOK_SECRET=... \
python examples/sandbox_send_and_verify.py
```

## Replies, reactions, and WhatsApp Business group messages

WhatsApp sends accept `reply_to={"message_id": ...}` on `messages.create()`, the
`messages.send_*` helpers, every `whatsapp.send_*` helper, and the `whatsapp_*`
builders in `tyxter.message_builders`. Use a Tyxter message ID in the same
environment and conversation. The helpers keep the quote alongside metadata,
idempotency keys and trace IDs.

`messages.create()` also sends a reaction to an inbound WhatsApp message; an
empty `emoji` removes it. Targets must be at most 30 days old and inside an open
24-hour service window. Normal outbound billing applies, and a reaction's status
stops at `sent`.

```python
client.messages.create(
    {
        "channel": "whatsapp",
        "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
        "recipient": {"type": "phone_e164", "id": "+5511999999999"},
        "message": {
            "type": "reaction",
            "reaction": {"message_id": "msg_inbound_123", "emoji": "👍"},
        },
    },
    idempotency_key="reaction-123",
)
```

To send to an active WhatsApp Business group, use
`{"type": "whatsapp_group", "id": "<Tyxter group id>"}` as the recipient and the
phone number that hosts the group as the sender. Participant replies arrive as
`group.message_received` (`GroupMessageReceivedWebhookEnvelope`). In sandbox,
`sandbox.inbound_messages.create()` accepts `group_id`, with the host phone in
`to` and the participant in `from`.

Message reads and `message.*` webhook senders carry `profile_name`: the captured
inbound WhatsApp profile name, not a verified identity or business display name.
It is `None` on the default payload-less list, outbound and non-WhatsApp
messages, phone-less rows and redacted rows. Already-stored webhook snapshots can
lack it. Reads also carry `context` (`reply_to`, `forwarded`,
`frequently_forwarded`), and an inbound sticker's `media.animated` is `True` or
`False` when Meta sent the signal and omitted otherwise. A
`message.reaction_received` event keeps the reacted message's snapshot and adds
`data["reaction"]` with `emoji`, `removed`, `from` (`None` when Meta withholds the
reacting phone) and `reacted_message_id`.

## Resources

The client exposes snake-case resource namespaces:

- `account`, `api_keys`, `ai_agents`, `agentic_payments`, `audiences`, and `projects`
- `automations`, `automation_runs`, and `automation_webhooks`
- `batches`, `billing`, `contacts`, `data_retention`, `feedback`, `fiscal`,
  `flows`, and `groups`
- `llm`, `llm_routes`, `media`, `messages`, `meta_signup_sessions`, and `payments`
- `phone_numbers`, `provider_connections`, and
  `provider_credential_setup_sessions`
- `rate_cards`, `sandbox`, `templates`, `usage`, `webhook_endpoints`, and
  `webhook_events`
- channel-native conveniences: `whatsapp` and `instagram`. `whatsapp_channels`
  and the `whatsapp_channel_*` builders are deprecated: WhatsApp Channel
  publishing is unsupported and the API rejects them with
  `invalid_message_request`. They are marked deprecated for type checkers (PEP 702)
  and do not warn at runtime; they remain so existing imports and error handling
  keep working.

Request and response dictionaries are `TypedDict` contracts exported from
`tyxter.types`. Write methods expose `idempotency_key` and `trace_id` only where
the canonical endpoint manifest supports those headers.

Provider credential setup keeps `create()` and `retrieve()` source-compatible
with `ProviderCredentialSetupSessionResponse`, including mutable status and
completion fields. Use `create_result()` or `retrieve_result()` when strict type
narrowing must distinguish provider-connection, TTS, and STT completion axes.

## Template authoring

Omit `parameter_format` on create or generation to select the compatible `"POSITIONAL"` default.
On update, omission retains the draft or rejected template's current format; on duplicate, it inherits
the source template's format. Set `"NAMED"` when BODY values are bound by their parameter names.
The approved template version, not a send request, determines how its variables are resolved.

```python
from time import sleep

named_template = client.templates.create(
    {
        "name": "order_tracking",
        "language": "en_US",
        "category": "utility",
        "parameter_format": "NAMED",
        "components": [
            {
                "type": "BODY",
                "text": "Hi {{customer_name}}, order {{order_id}} is ready.",
                "example": {
                    "body_text_named_params": [
                        {"param_name": "customer_name", "example": "Ana"},
                        {"param_name": "order_id", "example": "ORD-123"},
                    ]
                },
            }
        ],
    }
)

client.templates.submit(named_template["id"])
approved_template = client.templates.retrieve(named_template["id"])
while approved_template["status"] == "submitted":
    sleep(5)  # Use application-appropriate polling/backoff in production.
    approved_template = client.templates.retrieve(named_template["id"])
if approved_template["status"] != "approved":
    raise RuntimeError(f"Template was not approved: {approved_template['status']}")

client.whatsapp.send_template(
    {
        "from": "pn_123",
        "to": "+5511999999999",
        "name": named_template["name"],
        "language": named_template["language"],
        # No send-time parameter_format: the approved version selects NAMED.
        "variables": {"customer_name": "Ana", "order_id": "ORD-123"},
    }
)
```

Standalone `COPY_CODE` is a marketing coupon button, not an authentication OTP button with
`{"type": "OTP", "otp_type": "COPY_CODE"}`. Author it without a `text` field; the service
accepts one nonempty coupon example of at most 20 characters on a marketing template.

```python
from time import sleep

coupon_template = client.templates.create(
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

client.templates.submit(coupon_template["id"])
approved_coupon = client.templates.retrieve(coupon_template["id"])
while approved_coupon["status"] == "submitted":
    sleep(5)  # Use application-appropriate polling/backoff in production.
    approved_coupon = client.templates.retrieve(coupon_template["id"])
if approved_coupon["status"] != "approved":
    raise RuntimeError(f"Template was not approved: {approved_coupon['status']}")

client.whatsapp.send_template(
    {
        "from": "pn_123",
        "to": "+5511999999999",
        "name": coupon_template["name"],
        "language": coupon_template["language"],
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
```

`client.batches.create` intentionally does not support this COPY_CODE send shape: its batch
contract has no per-recipient button-parameter source.

## Phone name-review reads

Phone reads expose three distinct name facts. `display_name` remains the customer-entered value;
`verified_name` is nullable Meta-verified display-name evidence; and `name_review` is nullable or
the latest durable review `{requested_name, decision, reason, reviewed_at}`. Its `decision` is an
open Meta string. `pending_name_review` is separately nullable or
`{requested_name, status, observed_at}`: `status` is nullable and, when present, an open Meta
string; `observed_at` shares the freshness fact in `meta_health_synced_at`. Neither a null status
nor a null pending or durable review block implies approval. SDK list and retrieve reads return
these API values; they do not trigger a live Meta fetch.

## Provider availability observations

Provider connection availability fields are advisory evidence, not SDK send enforcement. An absent
or null `send_capability` means there is no trusted observation: it is unknown and establishes
neither availability nor unavailability. A `blocked` value does not change the connection status or
block a client send. `send_block_codes`, `waba_send_capabilities`, and
`waba_ban_date` provide diagnostic Meta observations, including WABA-specific evidence and its
observed timestamp. Policy-warning strings remain open provider values. A flow's nullable
`provider_missing_since` is an observation: null means the provider resolves or has never been
checked, while a timestamp is the first reconciliation failure. Verify provider warning and
scheduled-disable webhook envelopes with the existing raw-body signature verifier.

## Asynchronous phone, diagnostics, and group operations

The API accepts these writes and a Tyxter worker completes them; the request
itself calls no provider. Read the resource again for the outcome.

- `phone_numbers.request_meta_diagnostics()` returns the stored answer with
  `check_accepted`; poll `get_meta_diagnostics()` until `check_pending` is false.
  A capability `value` is `True`, `False`, or `"unknown"`: `"unknown"` means
  required facts are missing, not that the capability is refused. A section
  whose `status` is `read_failed` carries a `failure` and no facts.
- `phone_numbers.create_order()` creates a rental order. In production it waits
  at `approval_url` for an organization owner or admin; no API key can approve
  it, and nothing is charged before approval. Poll `retrieve_order()`. A
  production `phone_numbers.provision()` rents nothing: it raises
  `TyxterAPIError` 409 `phone_number_rental_approval_required`, whose
  `rental_order` holds the order's `id`, `approval_url` and `expires_at`; hand the
  URL to an owner or admin and poll `retrieve_order()` rather than also calling
  `create_order()`.
- `provider_connections.exchange_meta_oauth()` and
  `complete_meta_registration()` answer `202` with the connection and its
  `operation` `queued` (`meta_oauth_exchange` or `meta_registration_completion`).
  Poll `provider_connections.retrieve()` until `operation["state"]` is
  `"succeeded"` or `"failed"`; on failure `operation["error_code"]` is the stable
  code, such as `meta_oauth_exchange_failed` or `meta_payment_method_required`.
  These Meta refusals no longer raise; refusals that need no Meta call still
  raise `TyxterAPIError`. Phone `provision()`/`connect()` and these two methods
  can return advisory display-name `warnings` with a stable `code`; they do not
  block submission or predict Meta approval.
- Salvy BYOK: `provider_connections.register_salvy()` returns a pending
  connection whose `salvy.operation` reports the worker's validation;
  `list_salvy_numbers()` reads the cached discovery snapshot, and
  `phone_numbers.import_salvy()` imports one number from it.
  `billing.list_phone_management()` reports management coverage and charges.
- `groups` manages WhatsApp Business groups created through Meta's Groups API,
  never personal WhatsApp groups. `groups.create()` returns a `pending` group,
  and a Tyxter worker resolves the create, as `active` or as `failed` with a
  `failure.code`. A create the worker cannot send fails without any Meta call.
  A production create Meta accepts stays `pending` until Meta reports the
  outcome, and stays `pending` if that outcome never arrives. In sandbox,
  `sandbox.groups.simulate_participant()` simulates members joining and leaving.
- `payments.cancel()` queues hosted-checkout cancellation and returns the current
  payment; poll `retrieve()` until the provider confirms a terminal status.
  Transparent Pix and unsupported providers answer
  `payment_cancellation_unsupported` and change nothing.

## Promotional credit reads and events

Top-up responses and `credit.topped_up` webhook events can report both `payment_method` and
`provider` as `"promotion"` for a separately granted campaign bonus. Historical webhook events may
omit `provider`, which the SDK never infers. There is no campaign, redemption, or promotion-creation
operation in this SDK. A response `kind` of `"cash"` can coexist with the promotional discriminants;
it does not establish cash settlement or a provider charge.

## Billing, fees, and phone rental reads

- `billing.balance()` returns `held_brl`, credit held by outstanding production
  holds and already deducted from `balance_brl` (a hold is not spend), and
  `production_blocked`, the production API-key credit policy.
- Usage reads keep Tyxter billing apart from what Meta bills directly:
  `usage.list_records()` rows carry nullable `estimated_external_meta_cost` with
  the event-time Meta reference rate when one is available, and `usage.retrieve()`
  and its buckets carry a separately marked aggregate with covered and
  missing-reference quantities. Each is an estimate (`is_estimate: True`).
- `billing.list_ledger()` rows are typed `LedgerEntryResponse`. `hold` and
  `release` entries are payment completion-fee holds and their return; only
  `debit` is spend. `payment_fee` names the payment and fee reservation.
- Payment responses carry `fees` (`PaymentFees`): `initiation` is charged once and
  `completion` is held until the outcome (`completion["state"]`). `simulated` is
  `True` in sandbox, where nothing leaves the balance, and `fees` is `None` for a
  payment charged none.
- Package purchases are card-only: `payment_method` accepts only `"card"` (the
  default), and `payment_method_id` selects a saved card.
- Automatic top-up `enabled` can change without a write of yours: a failed
  automatic top-up turns it `False`. `save_payment_method()` and
  `set_default_payment_method()` turn back on only a configuration a failure
  turned off, pointed at that card, and `update_auto_topup({"enabled": True, ...})`
  turns it on as well. None of these charges immediately.
- `phone_numbers.list()` and `retrieve()` return `PhoneNumberReadResponse` with
  `renewal` (`PhoneRenewalSummary`): the number's current UTC month, with the next
  charge in `next_renewal_at` and, on the free plan, the release instant in
  `release_cutoff_at`. It is `None` for BYON and sandbox numbers.
  `billing.list_phone_renewals()` and `retrieve_phone_renewal()` are deprecated
  for type checkers: they return cycles recorded by the retired prepaid design,
  and no new cycle is recorded.

## Pagination

List methods return cursor pages. Continue with `next_cursor` only when
`has_more` is true:

```python
cursor = None
while True:
    page = client.messages.list(limit=100, starting_after=cursor)
    for message in page["data"]:
        print(message["id"], message["status"])
    if not page["has_more"]:
        break
    cursor = page["next_cursor"]
```

## Idempotency and errors

Tyxter does not implicitly retry writes. Reuse one idempotency key for retries
of the same logical operation and choose your retry policy from the stable error
fields:

- **Unsupported** endpoints do not expose an idempotency-key argument because
  the manifest disallows that header.
- **Supported** endpoints accept an optional caller key and forward it when one
  is supplied.
- **Required** endpoints always send a key. `feedback.create()` generates one
  when omitted (and rejects an explicit blank key). Every other required
  endpoint takes a caller-supplied, nonblank key and rejects a blank one before
  any request: transcription retry, `meta_signup_sessions.create()`, the Salvy
  provider-connection writes (`register_salvy`, `rotate_salvy`,
  `refresh_salvy_discovery`), and `phone_numbers.import_salvy()`,
  `complete_salvy_registration()` and `convert_to_byon()`.

Flow creation, LLM route upsert/delete, AI Agent completion, and automation
webhook-secret rotation all accept the `idempotency_key` keyword argument.

```python
from tyxter import TyxterAPIError, TyxterConnectionError

try:
    message = client.messages.create(payload, idempotency_key="order_123_send_1")
except TyxterAPIError as error:
    print(error.status_code, error.code, error.request_id, error.trace_id)
    if error.retry_after_ms is not None:
        print("retry after", error.retry_after_ms, "ms")
except TyxterConnectionError as error:
    print("request did not receive an API response", error)
```

`TyxterAPIError.body` preserves the original response, and `raw_body` is its
complete `error` object typed as `TyxterWireErrorBody`. Errors the API marks as
reportable include `error.feedback`, which points to the public feedback
endpoint. A `route_not_found` response may instead include `error.discovery`,
whose `openapi` and `well_known` relative paths describe the API host; read it
from `raw_body` rather than expecting a separate exception attribute.

Typed views of `error.details`:

- `retryable` is `False` when the API sends the stop hint, for example on
  `402 credit_balance_exhausted`: stop automatic retries until credit recovers.
  `None` is not permission to retry. That refusal's `raw_body["details"]` is
  `CreditBalanceExhaustedDetails` (`top_up_url`, `reachable_routes`).
- `service_window` is `ServiceWindowRequiredDetails` (`reason` and nullable
  `last_inbound_at`) on `service_window_required`, when the server supplied it.
- `rental_order` is the order a `phone_number_rental_approval_required` refusal
  created.
- `next_allowed_at` and `guard_reason` come from recipient-guard refusals such as
  `recipient_duplicate_message`. `next_allowed_at` is `None` both when absent and
  while an earlier send is pending; `raw_body["details"]` tells them apart.
- `details` is the listen-session conflict view
  (`details["active_session"]`), set only on that conflict.

The SDK never narrows `raw_body["details"]` by itself; check `error.code` before
treating it as one variant:

```python
from typing import cast

from tyxter import TyxterAPIError
from tyxter.types import CreditBalanceExhaustedDetails

try:
    client.messages.list()
except TyxterAPIError as error:
    if error.retryable is False:
        print("pause automatic retries", error.trace_id)
    raw_details = error.raw_body.get("details") if error.raw_body is not None else None
    if error.code == "credit_balance_exhausted" and raw_details is not None:
        details = cast(CreditBalanceExhaustedDetails, raw_details)
        print(details["top_up_url"])
    raise
```

## Webhook verification

Tyxter signs the exact raw request body with
`HMAC-SHA256(secret, "{timestamp}.{raw_body}")`. Never parse and re-serialize
the body before verification.

```python
from tyxter import WebhookSignatureVerifier

verifier = WebhookSignatureVerifier(signing_secret)
if not verifier.verify(raw_body=raw_body_bytes, headers=request_headers):
    raise PermissionError("invalid Tyxter webhook signature")
```

FastAPI:

```python
from fastapi import HTTPException, Request

@app.post("/webhooks/tyxter")
async def tyxter_webhook(request: Request) -> dict[str, bool]:
    raw_body = await request.body()
    if not verifier.verify(raw_body=raw_body, headers=request.headers):
        raise HTTPException(status_code=400, detail="invalid signature")
    return {"received": True}
```

Django:

```python
from django.http import HttpRequest, JsonResponse

def tyxter_webhook(request: HttpRequest) -> JsonResponse:
    headers = {key: value for key, value in request.headers.items()}
    if not verifier.verify(raw_body=request.body, headers=headers):
        return JsonResponse({"error": "invalid signature"}, status=400)
    return JsonResponse({"received": True})
```

Header names are case-insensitive. The default replay tolerance is 300 seconds.

## Typed webhook events

After verifying the signature, parse the raw body and annotate it with the
matching envelope from `tyxter.types`:

- `PaymentWebhookEnvelope` for the seven merchant `payment.*` events; narrow on
  `event["type"]`.
- `GroupWebhookEnvelope` for the six WhatsApp Business group lifecycle outcomes,
  and `GroupParticipantWebhookEnvelope` for `group.participant_joined` /
  `group.participant_removed` (`initiated_by` on a removal only). Lifecycle data
  includes `invite_link`, which lets anyone who has it join the group: store
  payloads as secrets.
- `GroupMessageReceivedWebhookEnvelope` and
  `MessageReactionReceivedWebhookEnvelope` for group replies and reactions.
- `CreditHardBlockEngagedWebhookEnvelope` and
  `CreditHardBlockLiftedWebhookEnvelope` for wallet hard-block changes.

```python
import json

from tyxter.types import GroupParticipantWebhookEnvelope

event: GroupParticipantWebhookEnvelope = json.loads(raw_body_bytes)
if event["type"] == "group.participant_removed":
    print(event["data"]["initiated_by"])
print(event["data"]["participant"]["wa_id"], event["data"]["participant_count"])
```

Webhook endpoint reads add `held_event_count` and `oldest_held_event_at` for
pending held events, and `probation` after breaker recovery until the first
real delivery success; `disabled_detail["probation_retrip"]` marks a re-trip
during probation. Delivery attempts carry `failure_class`, which is `None` on
pending, successful, historical and unclassified attempts.

## Media capability URLs

`client.media.upload(...)` performs create → capability upload → complete. The
SDK deliberately does not attach the Tyxter bearer token to the returned upload
URL. Capability failures raise `TyxterMediaUploadError`.

## Client ownership and cleanup

Use the context manager when the SDK creates its own `httpx.Client`. If you pass
`http_client=`, the caller retains ownership and the SDK will not close it.

```python
import httpx

http_client = httpx.Client()
client = Tyxter(api_key="tx_sandbox_...", http_client=http_client)
client.close()       # does not close http_client
http_client.close()  # caller-owned cleanup
```

`TyxterBootstrap` is a separate unauthenticated client for agent API-key device
authorization. It never sends a bearer token.

## Broadcast example

`examples/broadcast_customer_list.py` validates a CSV of E.164 phone numbers and
sends an approved template through `client.batches.create`.

```bash
python examples/broadcast_customer_list.py \
  --customers examples/customers.csv \
  --from pn_123 \
  --template-name promo_april \
  --template-language en_US \
  --name "April promo" \
  --idempotency-key idem_april_promo_001
```

## Route conformance

`conformance/` holds a vendored copy of the canonical public-API manifest:

- `public-api-launch-endpoints.json` — every launch route, its scope, query
  schema, and whether it honors `Idempotency-Key` / `Trace-Id`.
- `public-api-query-params.json` — the Zod-derived query-parameter names.
- `SOURCE_COMMIT` — the Tyxter Messaging commit these copies were taken from.

`tests/test_route_conformance.py` pins this package's resource surface to that
manifest: a route in the manifest with no typed SDK method fails, an SDK method
that hits a route the manifest does not define fails, and a query parameter or
`Idempotency-Key` mode (`unsupported`, `supported`, or `required`) that drifts
from the contract fails.

The current manifest at `a9142f6b52726629474fdc5c8afe21ff4687fb13` classifies
all **206** rows: **198** have typed SDK routes, and **8** are reviewed
exemptions. `PUT` and `GET /v1/media/blobs/:token` are capability-token routes:
the signed token is their sole authority, so they are not bearer-authenticated
SDK routes. The other six are `GET` and `DELETE` under
`/v1/groups/{https://chat.whatsapp.com,http://chat.whatsapp.com,chat.whatsapp.com}/*`,
teaching-only refusals for a pasted personal WhatsApp invite link that the
manifest itself declares have no SDK method; `groups.retrieve()` and
`groups.delete()` percent-encode the id and reach the same `422`. The count is
source-conformance evidence, not a publication claim. That commit is the
`sdk-js-v0.12.0` release tag; the snapshots are byte-identical to the
`e253e046739889d2bd2d32c4798e3864ba9f9290` copies they replace.

**Do not hand-edit these files to make a test pass.** They are generated in the
Tyxter Messaging repo, where they are verified against the mounted `v1`
controllers, and are updated here only by the automated sync PR. Editing them
locally silences the gate instead of fixing the drift — if a sync PR turns the
suite red, the correct fix is to add or correct the SDK method.
