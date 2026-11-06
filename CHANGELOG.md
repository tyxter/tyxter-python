# Changelog

All notable changes to the Tyxter Python SDK are documented here. The format is
based on Keep a Changelog, and versions follow Python packaging version rules.

**Version line.** This package tracks the canonical JavaScript SDK version,
published on npm as [`tyxter`](https://www.npmjs.com/package/tyxter) (formerly
[`@tyxter/sdk-js`](https://www.npmjs.com/package/@tyxter/sdk-js)), for API
and functional parity. That is why this package goes `0.1.0a0` → `0.8.0` rather
than incrementing from its own history: it is adopting the canonical line, not
claiming four releases of its own. Explicitly identified forward-compatible
additions may follow a later canonical manifest and are kept distinct from the
published JavaScript tag in these notes.

## [Unreleased]

No unreleased changes.

## [0.12.0] - 2026-11-06

This Python release ports canonical `tyxter` 0.12.0, published on npm from Tyxter Messaging tag
`sdk-js-v0.12.0` (`a9142f6b52726629474fdc5c8afe21ff4687fb13`); the canonical package was published
as `@tyxter/sdk-js` through 0.10.0. It ports the canonical diff from `sdk-js-v0.8.0`
(`58524926a1fa9498bcfe3abb9d7aa8fd39be1e85`) through `sdk-js-v0.9.0`, `sdk-js-v0.10.0`,
`sdk-js-v0.11.0`, `sdk-js-v0.11.1` and `sdk-js-v0.12.0`, and closes the older gaps listed under
Added and Fixed. `conformance/` now records the tag commit; its route and query snapshots are
byte-identical to the previous `e253e046739889d2bd2d32c4798e3864ba9f9290` copies.

Python conventions and the deliberate differences from canonical:

- Fields the canonical SDK added to an already-published response type are `NotRequired` here,
  even where the canonical type requires them, so existing response constructors keep
  type-checking; current API reads include them. Brand-new types mirror canonical exactly.
- `PhoneNumberReadResponse.renewal` stays `NotRequired`, although reads always include it, and
  `PhoneNumberMutationResponse` keeps the inherited optional `renewal`, although mutation
  responses never carry it. A TypedDict subclass can neither make an inherited key required nor
  drop it, and a sibling type would break `PhoneNumberResponse` annotations on these methods.
- `MessageReactionReceivedWebhookData` is not a structural subtype of `MessageWebhookData`, which
  canonical extends: its sender requires `profile_name`, and TypedDict values are invariant.
- `TyxterAPIError.next_allowed_at` is `None` both when the details omit it and when the API sent
  `null`, where canonical keeps `undefined` and `null` apart; `raw_body["details"]` tells the
  two apart.
- Deprecations are type-checker signals only (PEP 702 `@deprecated(..., category=None)`),
  matching canonical JSDoc `@deprecated`; nothing warns at runtime.
- Canonical inline shapes get exported names. The canonical runtime suffix on the User-Agent is
  not ported: the API classifies Python SDK requests only when the header is exactly
  `tyxter-python/<version>`.

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
- `PurchaseBillingPackageRequest`: package purchases are card-only, so `payment_method` is
  optional and accepts only `"card"` (the default); the optional `payment_method_id` selects a
  saved card. The API already refused `"pix"`.
- `SaveBillingPaymentMethodRequest` (`stripe_payment_method_id`, optional `set_default`) and
  `UpdateAutoTopupConfigRequest` (`enabled`, `threshold_brl`, `amount_brl`, optional nullable
  `payment_method_id`) are typed with their exact API fields instead of any JSON object. Runtime
  requests are unchanged; a type checker now rejects other keys.

### Changed

- `provider_connections.exchange_meta_oauth()` now answers `202` with the connection carrying a
  queued `operation` of kind `meta_oauth_exchange`, instead of a `201` `connected` connection.
  Tyxter sends the single-use code to Meta at most once and completes Embedded Signup after the
  response; poll `retrieve()` until `operation["state"]` is `"succeeded"` or `"failed"`.
  Code-exchange and Embedded Signup refusals (`meta_oauth_exchange_failed`, `meta_waba_missing`,
  `meta_payment_method_required`, `meta_identity_enforced` and the other onboarding codes) no
  longer raise: they arrive in `operation["error_code"]`. Refusals that need no Meta call still
  raise `TyxterAPIError`. Display-name `warnings` now come only for a `display_name` the request
  supplied.
- `provider_connections.complete_meta_registration()` now answers `202` with the still-`pending`
  connection carrying a queued `operation` of kind `meta_registration_completion`, instead of a
  `200` `connected` connection. Onboarding and credential refusals arrive in
  `operation["error_code"]` and the connection stays `pending`; refusals that need no Meta call
  still raise. Both methods now return `MetaConnectionMutationResponse`, a subtype of
  `ProviderConnectionResponse` with optional display-name `warnings`.
- `meta_signup_sessions.retrieve()` can report `processing` for up to about 16 minutes past
  `expires_at`, instead of about 10: a hosted completion claimed before `expires_at` finishes in
  a Tyxter worker. `meta_signup_sessions.create()` answers `meta_signup_session_pending` ahead of
  `meta_signup_connection_exists` when both apply, and a pending connection with no credential
  and no queued operation no longer blocks it.
- WhatsApp Business groups are no longer labelled beta. From the next groups eligibility check,
  Meta's documented `official_business_account.oba_status` decides the Official Business Account
  fact before the undocumented `is_official_business_account` boolean: `APPROVED` counts as OBA,
  and `NOT_STARTED`, `PENDING` and `REJECTED` answer `not_eligible` with
  `not_official_business_account`, so new `groups.create()` requests for such numbers refuse with
  `group_phone_number_not_eligible`.
- `phone_numbers.list()` and `retrieve()` return `PhoneNumberReadResponse`, and `provision()` and
  `connect()` return `PhoneNumberMutationResponse`; both subtype `PhoneNumberResponse`.
  `renewal` reports renewal policy v2 facts for the number's current UTC month; the retired
  `cycle_id`, warning, grace, `release_requested_at` and `provider_evidence_observed_at` fields
  are always `None`.
- A production `phone_numbers.provision()` creates a rental order and raises `TyxterAPIError`
  409 `phone_number_rental_approval_required`, whose `rental_order` holds the order to approve.
- Automatic top-up `enabled` can turn `False` without a write of yours, when an automatic top-up
  fails. Saving or defaulting that card, or `update_auto_topup()` with `enabled: True`, turns it
  back on without charging.
- The remaining messaging allowance estimate compares usage with a cap reduced by the configured
  safety margin and the sending phone's quality ratio; linked phones can report different
  values. No field changed.

### Deprecated

- `whatsapp_channels.publish_text()` / `publish_media()` and the `whatsapp_channel_text()` /
  `whatsapp_channel_media()` builders are marked deprecated for type checkers. WhatsApp Channel
  publishing is unsupported and the API rejects these payloads with `invalid_message_request`;
  the methods, builders, `WhatsAppChannelsResource` and the `whatsapp_channels` attribute remain
  so existing imports and error handling keep working.
- `billing.list_phone_renewals()` and `billing.retrieve_phone_renewal()` are marked deprecated
  for type checkers. They keep returning cycles recorded by the retired prepaid renewal design;
  no new cycle is recorded. Read `renewal` on phone-number reads instead. No removal date is
  set.

### Added

- WhatsApp Business groups: `groups.retrieve_eligibility()`,
  `groups.create_eligibility_check()`, `groups.create()`, `groups.list()`, `groups.retrieve()`,
  `groups.delete()`, `groups.reset_invite_link()`, and
  `sandbox.groups.simulate_participant()`, with `GroupResponse`, `GroupEligibilityResponse`,
  `ListGroupsResponse` and their request types. The six teaching-only personal-invite routes under
  `/v1/groups/<invite host>/*` have no SDK method, as their manifest rows state.
- WhatsApp Business group messages: `"whatsapp_group"` on `MessageIdentityType` and the
  exported `WhatsAppGroupRecipientIdentity`, so `messages.create()` and the `messages.send_*`
  helpers can send to an active group from the number that hosts it.
  `sandbox.inbound_messages.create()` accepts `group_id`.
- Replies and reactions: optional `reply_to` (`MessageReplyTo`) on `CreateMessageRequest`, the
  `messages.send_*` inputs, every `whatsapp.send_*` input and the `whatsapp_*` builders; a
  `"reaction"` message (`ReactionMessagePayload`) for `messages.create()`; and a `"reaction"`
  sandbox inbound type.
- Message reads: `MessageReadSender` and `profile_name` on read senders, `context`
  (`MessageContext`), and `animated` on inbound sticker media.
- Webhook contracts: `profile_name` on `message.*` senders (`MessageWebhookSender`);
  `GroupMessageReceivedWebhookEnvelope`, `MessageReactionReceivedWebhookEnvelope`,
  `GroupWebhookEnvelope` (six lifecycle events), `GroupParticipantWebhookEnvelope` (with
  `GroupParticipantWebhookData`), `CreditHardBlockEngagedWebhookEnvelope` and
  `CreditHardBlockLiftedWebhookEnvelope`, with their data types. The merchant `payment.*` envelopes
  (`PaymentWebhookEnvelope` and its seven members), present in the canonical SDK since
  `sdk-js-v0.3.0` but never ported, are added too.
- Typed `TyxterAPIError` views: `retryable` (the `False` stop hint), `raw_body`
  (`TyxterWireErrorBody`), `details` (the listen-session conflict), `guard_reason` and
  `next_allowed_at` (recipient-guard refusals), `rental_order` and `service_window`, with
  `TyxterWireErrorResponse`, `CreditBalanceExhaustedDetails`, `RecipientGuardDetails`,
  `ServiceWindowRequiredDetails`, `PhoneNumberRentalApprovalRequiredDetails` and
  `WebhookListenSessionConflictDetails`. `TyxterErrorBody` gains `retryable` and the
  listen-session `details`.
- Meta diagnostics: `phone_numbers.request_meta_diagnostics()` and
  `phone_numbers.get_meta_diagnostics()`, with `MetaDiagnosticsResponse` and its section,
  capability and check types. A capability `value` of `"unknown"` stays distinct from `False`.
  Answers include the live `display_name` and `account_review` checks, `can_use_flows: False`
  with `medium_message_quality` for a YELLOW quality rating, and the Official Business Account
  object in `phone.facts.official_business_account`.
- Provider connections: optional `operation` (`ProviderConnectionOperation`, with
  `ProviderConnectionOperationKind` and `ProviderConnectionOperationErrorCode`),
  `MetaConnectionChannel`, `channels.agentic_payments.platform_default`
  (`AgenticPlatformDefaultStatus`) on `status()`, and the `ApiKey*` / `DashboardBff*` Salvy
  request aliases.
- Customer-owned Salvy numbers: `provider_connections.register_salvy()`, `rotate_salvy()`,
  `refresh_salvy_discovery()` and `list_salvy_numbers()`; `phone_numbers.import_salvy()`,
  `complete_salvy_registration()` and `convert_to_byon()`; and `billing.list_phone_management()`.
  The writes require a caller-supplied idempotency key. `ProviderName` and
  `ProviderCredentialSetupTarget` gain `"salvy"`, `ProviderConnectionChannel` gains
  `"phone_numbers"`, `ProviderConnectionResponse` gains optional `salvy`, and
  `PhoneNumberResponse` gains optional `salvy_management`.
- Phone numbers: rental orders (`phone_numbers.create_order()`, `retrieve_order()`,
  `CreatePhoneNumberOrderRequest`, `PhoneNumberOrderResponse`), `renewal`
  (`PhoneRenewalSummary`), and advisory display-name `warnings` (`DisplayNameWarning`,
  `DisplayNameWarningCode`).
- Billing and payments: `held_brl` and `production_blocked` on `billing.balance()`; typed
  `LedgerEntryResponse` rows with `hold` / `release` entries, the `payment_fee_hold` source and
  `payment_fee`; `salvy_byok_enabled` on plans; `fees` (`PaymentFees`) on payment and agentic
  payment responses; the newer `PhoneRenewalResponse` date fields; and `payments.cancel()`, with
  optional `idempotency_key` and `trace_id`.
- Flows: `rejection_code` (`FlowRejectionCode`) and `rejection_details`
  (`FlowRejectionDetails`).
- Webhook endpoints: `probation`, `held_event_count`, `oldest_held_event_at` and
  `disabled_detail.probation_retrip`; delivery attempts gain `failure_class`.
- Message batches: `recipient_guard_skipped_count`, and `guard_reason` / `next_allowed_at` on
  failure-export rows.
- `"syncing"` on `ProjectProfileMetaSyncStatus`, and transcription `prompt` / `keywords` hints on
  `RequestMessageMediaTranscription`.
- `messages.list(created_after=...)`.
- Optional `idempotency_key` on `ai_agents.update()`, `api_keys.rename()`, `automations.update()`,
  `automation_runs.cancel()`, `llm_routes.update()`, `messages.request_transcription()`,
  `messages.typing()`, `sandbox.templates.set_status()`, `templates.estimate_cost()` and
  `webhook_events.create_listen_session()`, whose routes now honor `Idempotency-Key`. A keyed
  `request_transcription()` response, and its replay, carries `text: None`.

### Fixed

- `messages.send_*`, `whatsapp.send_*` and the `whatsapp_*` builders silently dropped a
  `reply_to` key, so the message went out without its quote; they now send it.
- The `messages.send_*` inputs accept every `MessageRecipient`, including a structured phone
  recipient, instead of only `MessageIdentity`.
- Response fields canonical has had since `sdk-js-v0.4.0` and Python never typed:
  `estimated_external_meta_cost` on usage records, summaries and summary buckets
  (`EstimatedExternalMetaCost`, `EstimatedExternalMetaCostSummary`), and `templates` and
  `capabilities.send_template_messages` on `sandbox.quickstart()`. They are `NotRequired`.
- `CreateAudienceRequest.contact_ids` is optional, as the API allows and canonical has since
  `sdk-js-v0.1.0`.
- `MetaSignupSessionResponse` types the `"failed"` status and the optional `error`
  (`MetaSignupFailure`: `code` `meta_signup_session_expired`, `reason`, `message` and a `feedback`
  pointer) that `meta_signup_sessions.retrieve()` returns when a hosted signup handoff fails. Start a
  new session rather than exchanging a late code.
- `MetaOnboardingConfigResponse` types `login_options.extras.version` as `"v4"`, the Embedded
  Signup version the API returns; it was `"v3"`.
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
