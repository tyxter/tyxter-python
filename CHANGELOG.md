# Changelog

All notable changes to the Tyxter Python SDK are documented here. The format is
based on Keep a Changelog, and versions follow Python packaging version rules.

**Version line.** This package tracks the canonical
[`@tyxter/sdk-js`](https://www.npmjs.com/package/@tyxter/sdk-js) version for API
and functional parity. That is why this package goes `0.1.0a0` → `0.8.0` rather
than incrementing from its own history: it is adopting the canonical line, not
claiming four releases of its own. Explicitly identified forward-compatible
additions may follow a later canonical manifest and are kept distinct from the
published JavaScript tag in these notes.

## [Unreleased]

This section brings the SDK back in line with the canonical public-API manifest synced from
Tyxter Messaging `e253e046739889d2bd2d32c4798e3864ba9f9290`, against which
`tests/test_route_conformance.py` had failed. Request and response types follow the canonical
contracts at Messaging `e7a008dc00ab2184a1c76b3f8aa6c1086f8ee0c7`, whose route and query snapshots
are byte-identical to the vendored copies. These entries do not claim parity with a published
`sdk-js` release.

### Removed (breaking)

- `provider_connections.register_meta()` and `provider_connections.rotate_token()`, their
  `RegisterMetaConnectionRequest` and `RotateProviderConnectionTokenRequest` types, and
  `MetaOnboardingConfigResponse.manual_credentials_endpoint`. They called
  `POST /v1/provider-connections/meta` and `POST /v1/provider-connections/{connection_id}/rotate`,
  routes the API has removed, so every call already failed. No deprecated shim is kept, because a
  shim could only call a dead route. Connect a Meta account through Embedded Signup with
  `exchange_meta_oauth()` or a hosted `meta_signup_sessions` session, and replace an existing
  connection's credential by sending a fresh Embedded Signup code to `exchange_meta_oauth()`.

### Changed (breaking)

- `meta_signup_sessions.create()` requires a caller-supplied, nonblank `idempotency_key` and
  rejects a blank one before any request. The API now requires `Idempotency-Key` on
  `POST /v1/meta-signup-sessions` so the one-time launch URL replays deterministically, and
  refuses a request without one.

### Added

- Beta WhatsApp Business groups: `groups.retrieve_eligibility()`,
  `groups.create_eligibility_check()`, `groups.create()`, `groups.list()`, `groups.retrieve()`,
  `groups.delete()`, `groups.reset_invite_link()`, and
  `sandbox.groups.simulate_participant()`, with `GroupResponse`, `GroupEligibilityResponse`,
  `ListGroupsResponse` and their request types. The six teaching-only personal-invite routes under
  `/v1/groups/<invite host>/*` have no SDK method, as their manifest rows state.
- Meta diagnostics: `phone_numbers.request_meta_diagnostics()` and
  `phone_numbers.get_meta_diagnostics()`, with `MetaDiagnosticsResponse` and its section,
  capability and check types. A capability `value` of `"unknown"` stays distinct from `False`.
- Phone number rental orders: `phone_numbers.create_order()` and `phone_numbers.retrieve_order()`,
  with `CreatePhoneNumberOrderRequest` and `PhoneNumberOrderResponse`.
- Customer-owned Salvy numbers: `provider_connections.register_salvy()`, `rotate_salvy()`,
  `refresh_salvy_discovery()` and `list_salvy_numbers()`; `phone_numbers.import_salvy()`,
  `complete_salvy_registration()` and `convert_to_byon()`; and `billing.list_phone_management()`.
  The writes require a caller-supplied idempotency key. `ProviderName` and
  `ProviderCredentialSetupTarget` gain `"salvy"`, `ProviderConnectionChannel` gains
  `"phone_numbers"`, `ProviderConnectionResponse` gains optional `salvy`, and
  `PhoneNumberResponse` gains optional `salvy_management`.
- `payments.cancel()`, with optional `idempotency_key` and `trace_id`.
- `messages.list(created_after=...)`.
- Optional `idempotency_key` on `ai_agents.update()`, `api_keys.rename()`, `automations.update()`,
  `automation_runs.cancel()`, `llm_routes.update()`, `messages.request_transcription()`,
  `messages.typing()`, `sandbox.templates.set_status()`, `templates.estimate_cost()` and
  `webhook_events.create_listen_session()`, whose routes now honor `Idempotency-Key`.

### Fixed

- Package metadata: the Homepage URL pointed at `docs.tyxter.com`, which does not resolve; it now
  points at `https://tyxter.com/docs`. The Repository and Changelog URLs point at
  `tyxter/tyxter-python`.

## [0.8.0] - 2026-09-03

This Python release ports published `sdk-js-v0.8.0`
(`58524926a1fa9498bcfe3abb9d7aa8fd39be1e85`). The `sdk-js-v0.7.0` tag was never published, so
npm 0.8.0 was the first artifact to carry both the 0.7 and 0.8 surfaces. These entries describe
API functionality and exact wire request, response, and webhook contracts while preserving
compatible Python call sites; they do not claim identical language-specific type construction.

### Added

- Project management, public feedback report reads, webhook endpoint test receipts, and optional
  project-scoped API-key creation.
- Read-only `billing.list_phone_renewals()` and `billing.retrieve_phone_renewal()` from post-tag
  source commit `ed49c514b74a59de3b238d4ebc157f20482b6171`. These forward-compatible methods ship
  in Python 0.8.0 but are not attributed to the published `sdk-js-v0.8.0` tag.
- WhatsApp voice-note payloads, truthful unsupported/unknown inbound-message reads, phone-less
  inbound senders, media download hints, and media response fields without widening Instagram voice
  inputs or outbound identity requirements.
- Bounded transcription recovery with a required caller-supplied idempotency key, retry delay and
  API-discovery error details, `openai.stt` provider setup results, and typed transcription
  success/failure webhook contracts.
- Template authoring `parameter_format` response/request fields and standalone marketing
  `COPY_CODE` authoring, preserving the separate send-time variable and batch contracts.
- Phone-number `tier_2k`, nullable pending/durable Meta name-review observations, and public
  provider availability, WABA, and flow reconciliation observations without Python-side policy
  enforcement.
- Typed provider policy-warning and scheduled-disable webhook contracts with unchanged raw-body
  signature verification.
- Published contract and README truth for top-up and `credit.topped_up` response/event variants:
  `manual` and `promotion` payment/provider values, including intentionally omitted historical
  webhook providers. Promotion was not an item in the canonical changelog.

## [0.6.0] - 2026-08-10

This dated catch-up entry records the source version aligned to the published
JavaScript 0.5.0/0.6.0 surface. It does **not** claim that a Python 0.6.0
artifact has been published to PyPI.

### Added

- Message observability and capacity fields from the JavaScript 0.5.0 surface:
  `status_reason` on message responses, batch pacing forecasts, phone-number
  allowance estimates, and `messages.typing()` for an eligible inbound WhatsApp
  message.
- JavaScript 0.6.0's inbound-media and transcription surface: typed inbound
  media descriptors on message reads/lists, `media.list(source=...)`,
  `media.create_download_url()`, and request/retrieve transcription methods for
  inbound WhatsApp audio.
- Typed native WhatsApp `order_details` messages with Brazil Pix dynamic-code
  settings, structured phone recipients, and current provider-connection
  eligibility/restriction fields.

At the historical published-JavaScript 0.5/0.6 parity checkpoint, both SDK
sources exposed **170 of 172** manifest routes. The shared exemptions are
`PUT` and `GET /v1/media/blobs/:token`: their signed capability token is the
sole authority, so neither SDK wraps them in a bearer-authenticated method.

## [0.4.0] - 2026-08-03

First published release, and the point at which this package adopts the
canonical version line.

Verified at parity with `@tyxter/sdk-js` 0.4.0: both cover an identical **166 of
168** manifest routes, no route is covered by one SDK and missing from the
other, and neither invents a route the manifest does not define. The two
uncovered routes are the capability-token media blob `GET`/`PUT` endpoints,
exempt in both SDKs because the signed URL is the sole authority and neither
wraps it in a bearer-auth method.

### Changed

- The SDK now develops in its own repository,
  [`tyxter-dev/tyxter-python`](https://github.com/tyxter-dev/tyxter-python),
  instead of living under `sdks/python` in the Tyxter Messaging monorepo. The
  published package name (`tyxter`), its import path, and its public API are
  unchanged — this move affects contributors, not consumers.
- The canonical public-API manifest is vendored under `conformance/` and kept
  current by an automated sync PR from the Tyxter Messaging repo. The route,
  header, and query-parameter conformance gates are unchanged in strength.
- Release tags are `v<version>`, not `sdk-python-v<version>`.
- The client User-Agent assertion derives from `__version__` instead of a
  hardcoded literal, so a version bump is no longer a test failure.

### Added

- Typed synchronous `Tyxter` client for Python 3.10–3.13.
- Full public launch-manifest resource coverage, including channel-native
  message helpers, media capability uploads, webhook event listening, billing,
  automations, LLM routes, and agentic payments.
- Unauthenticated `TyxterBootstrap` client for agent API-key device approval.
- Typed stable API errors and cross-language webhook signature verification.
- Route, distribution, strict typing, and multi-version CI conformance gates.
- Query-parameter conformance gate: every method's query surface is locked to
  the Zod-derived `public-api-query-params.json` snapshot, so a contract query
  schema gaining a field fails the suite until the SDK exposes it.
- `messages.list()` server-side `direction` filter and typed
  `include="payload"` expansion.
- `data_retention` policy resource, `sandbox.llm.set_failure()` failure
  injection, and `provider_connections.complete_meta_registration()`.
- Typed `meta_signup_sessions.create()` / `.retrieve()` coverage and a parity
  gate between the typed and runtime error-type allowlists.

## [0.1.0a0] - 2026-07-14

Never published to PyPI — an in-tree marker from when the package lived in the
monorepo, kept here for history.

### Added

- Initial in-tree alpha package scaffold.
