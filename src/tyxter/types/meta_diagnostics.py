from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment
from .groups import GroupEligibilityReason

MetaDiagnosticsSandboxScenario: TypeAlias = Literal[
    "not_cloud_api",
    "whatsapp_business_app_number",
    "not_official_business_account",
    "missing_messaging_permission",
    "business_not_verified",
    "message_quality_medium",
    "message_quality_low",
    "meta_send_refused",
    "meta_send_blocked",
    "token_invalid",
    "token_expired",
    "token_scopes_missing",
    "token_waba_access_missing",
    "webhook_subscription_missing",
    "health_errors",
    "connection_suspended",
    "connection_pending",
    "connection_disconnected",
    "connection_reonboarding_required",
    "connection_reauthentication_required",
    "stored_send_blocked",
    "meta_payment_method_required",
    "meta_waba_inactive",
    "meta_messaging_permission_missing",
    "connection_link_mismatch",
    "registration_pin",
    "credential_access",
    "connection_access",
    "automatic_registration_unavailable",
    "registration_support_required",
    "display_name_pending",
    "display_name_declined",
    "display_name_expired",
    "display_name_missing",
    "account_review_pending",
    "account_review_deferred",
    "account_review_rejected",
]


class CreateMetaDiagnosticsCheckRequest(TypedDict, total=False):
    # Sandbox only; a production key is refused when it sends this field.
    sandbox_scenario: MetaDiagnosticsSandboxScenario


MetaDiagnosticsFailureCode: TypeAlias = Literal[
    "no_meta_connection",
    "connection_requires_reconnect",
    "meta_credentials_unreadable",
    "meta_app_not_configured",
    "no_meta_phone_number_id",
    "graph_refused",
    "graph_unavailable",
]


class MetaDiagnosticsFailure(TypedDict):
    code: MetaDiagnosticsFailureCode
    http_status: NotRequired[int]
    error_code: NotRequired[int]
    error_subcode: NotRequired[int]
    fbtrace_id: NotRequired[str]


class MetaDiagnosticsSectionReadFailed(TypedDict):
    """A section whose read failed. No facts are invented for it."""

    status: Literal["read_failed"]
    failure: MetaDiagnosticsFailure


class MetaDiagnosticsOfficialBusinessAccount(TypedDict, total=False):
    oba_status: str
    status_message: str


class MetaDiagnosticsThroughput(TypedDict):
    level: str


class MetaDiagnosticsPhoneFacts(TypedDict, total=False):
    platform_type: str
    is_on_biz_app: bool
    is_official_business_account: bool
    official_business_account: MetaDiagnosticsOfficialBusinessAccount
    status: str
    account_mode: str
    code_verification_status: str
    name_status: str
    quality_rating: str
    messaging_limit_tier: str
    throughput: MetaDiagnosticsThroughput


class MetaDiagnosticsPhoneSectionOk(TypedDict):
    status: Literal["ok"]
    facts: MetaDiagnosticsPhoneFacts
    # Fact names absent from this successful read; absence is not a failed read.
    missing_fields: list[str]


MetaDiagnosticsPhoneSection: TypeAlias = (
    MetaDiagnosticsPhoneSectionOk | MetaDiagnosticsSectionReadFailed
)


class MetaDiagnosticsWabaFacts(TypedDict, total=False):
    account_review_status: str
    business_verification_status: str
    ownership_type: str


class MetaDiagnosticsWabaSectionOk(TypedDict):
    status: Literal["ok"]
    facts: MetaDiagnosticsWabaFacts
    missing_fields: list[str]


MetaDiagnosticsWabaSection: TypeAlias = (
    MetaDiagnosticsWabaSectionOk | MetaDiagnosticsSectionReadFailed
)


class MetaDiagnosticsGranularScope(TypedDict):
    scope: str
    target_ids: NotRequired[list[str]]


class MetaDiagnosticsDebugTokenFacts(TypedDict, total=False):
    is_valid: bool
    # Unix seconds; 0 means the token never expires.
    expires_at: float
    scopes: list[str]
    granular_scopes: list[MetaDiagnosticsGranularScope]
    has_whatsapp_business_messaging: bool
    has_whatsapp_business_management: bool
    messaging_targets_waba: bool
    management_targets_waba: bool


class MetaDiagnosticsDebugTokenSectionOk(TypedDict):
    status: Literal["ok"]
    facts: MetaDiagnosticsDebugTokenFacts
    missing_fields: list[str]


MetaDiagnosticsDebugTokenSection: TypeAlias = (
    MetaDiagnosticsDebugTokenSectionOk | MetaDiagnosticsSectionReadFailed
)


class MetaDiagnosticsSubscribedAppsFacts(TypedDict):
    tyxter_app_subscribed: NotRequired[bool]
    other_app_ids: NotRequired[list[str]]
    override_callback_uri_present: bool


class MetaDiagnosticsSubscribedAppsSectionOk(TypedDict):
    status: Literal["ok"]
    facts: MetaDiagnosticsSubscribedAppsFacts
    missing_fields: list[str]


MetaDiagnosticsSubscribedAppsSection: TypeAlias = (
    MetaDiagnosticsSubscribedAppsSectionOk | MetaDiagnosticsSectionReadFailed
)


class MetaDiagnosticsHealthError(TypedDict, total=False):
    """A Meta health error. The API preserves any additional fields Meta sends."""

    error_code: float
    error_description: str
    possible_solution: str


class MetaDiagnosticsHealthEntity(TypedDict, total=False):
    """A Meta health entity. The API preserves any additional fields Meta sends."""

    entity_type: str
    id: str
    can_send_message: str
    errors: list[MetaDiagnosticsHealthError]


class MetaDiagnosticsHealthFacts(TypedDict, total=False):
    can_send_message: str
    entities: list[MetaDiagnosticsHealthEntity]


class MetaDiagnosticsHealthSectionOk(TypedDict):
    status: Literal["ok"]
    facts: MetaDiagnosticsHealthFacts
    missing_fields: list[str]


MetaDiagnosticsHealthSection: TypeAlias = (
    MetaDiagnosticsHealthSectionOk | MetaDiagnosticsSectionReadFailed
)


class MetaDiagnosticsApp(TypedDict):
    debug_token: MetaDiagnosticsDebugTokenSection | None
    subscribed_apps: MetaDiagnosticsSubscribedAppsSection | None


MetaDiagnosticsCapabilityReason: TypeAlias = (
    GroupEligibilityReason
    | Literal[
        "business_not_verified",
        "low_message_quality",
        "medium_message_quality",
        "meta_send_blocked",
        "token_invalid",
        "connection_unavailable",
        "cannot_send",
    ]
)
MetaDiagnosticsMissingFact: TypeAlias = Literal[
    "phone.platform_type",
    "phone.is_on_biz_app",
    "phone.is_official_business_account",
    "phone.official_business_account.oba_status",
    "phone.quality_rating",
    "waba.business_verification_status",
    "app.debug_token.is_valid",
    "app.debug_token.has_whatsapp_business_messaging",
    "app.debug_token.messaging_targets_waba",
    "health_status.can_send_message",
    "send_permission",
]


class MetaDiagnosticsCapability(TypedDict):
    # True when the required facts pass, False when a reported fact disqualifies,
    # "unknown" when required facts are missing.
    value: bool | Literal["unknown"]
    reasons: list[MetaDiagnosticsCapabilityReason]
    missing: list[MetaDiagnosticsMissingFact]


class MetaDiagnosticsCapabilities(TypedDict):
    can_send: MetaDiagnosticsCapability
    can_create_groups: MetaDiagnosticsCapability
    can_use_flows: MetaDiagnosticsCapability


# Check keys name a family, not a unique check: several checks can share one.
# Meta health checks use an open `health_<entity_type>` key, hence `str`.
MetaDiagnosticsCheckKey: TypeAlias = (
    Literal[
        "token_valid",
        "token_expiry",
        "token_scopes",
        "token_waba_access",
        "webhook_subscription",
        "webhook_other_apps",
        "webhook_override",
        "message_quality",
        "display_name",
        "account_review",
        "send_permission",
        "connection_status",
        "connection_suspension",
        "connection_token_expiry",
        "connection_send_capability",
        "phone_health_freshness",
        "connection_link",
        "recent_send_errors",
        "last_inbound",
        "name_registration",
    ]
    | str
)
MetaDiagnosticsCheckVerdict: TypeAlias = Literal["ok", "warning", "blocker", "unknown"]
MetaDiagnosticsCheckCode: TypeAlias = Literal[
    "ok",
    "read_failed",
    "missing_fact",
    "token_invalid",
    "token_expired",
    "token_expiring",
    "token_scopes_missing",
    "token_waba_access_missing",
    "webhook_subscription_missing",
    "webhook_other_apps_present",
    "webhook_override_present",
    "health_errors",
    "message_quality_medium",
    "message_quality_low",
    "stored_fact_missing",
    "display_name_pending",
    "display_name_declined",
    "display_name_expired",
    "display_name_missing",
    "account_review_pending",
    "account_review_deferred",
    "account_review_rejected",
    "stored_read_failed",
    "connection_suspended",
    "connection_pending",
    "connection_disconnected",
    "connection_policy_suspended",
    "connection_reonboarding_required",
    "connection_suspension_unrecognized",
    "connection_reauthentication_required",
    "stored_send_blocked",
    "meta_send_refused",
    "meta_payment_method_required",
    "meta_waba_inactive",
    "meta_messaging_permission_missing",
    "phone_health_stale",
    "connection_link_mismatch",
    "recent_send_error",
    "registration_pin",
    "credential_access",
    "connection_access",
    "automatic_registration_unavailable",
    "registration_support_required",
    "registration_in_progress",
]


class MetaDiagnosticsCheck(TypedDict):
    key: MetaDiagnosticsCheckKey
    source: Literal["live", "stored"]
    # A blocker blocks the capability or check named by key/code, not
    # necessarily sending.
    verdict: MetaDiagnosticsCheckVerdict
    code: MetaDiagnosticsCheckCode
    remediation: str | None
    observed_at: str | None


class MetaDiagnosticsFeedback(TypedDict):
    endpoint: str
    method: Literal["POST"]


class MetaDiagnosticsResponse(TypedDict):
    object: Literal["meta_diagnostics"]
    phone_number_id: str
    environment: Environment
    # not_checked before any completed check; completed when a snapshot exists,
    # including one with failed section reads.
    status: Literal["not_checked", "completed"]
    # True when this request started a check, False when it coalesced with the
    # current window, None on reads.
    check_accepted: bool | None
    check_pending: bool
    check_requested_at: str | None
    next_check_available_at: str | None
    checked_at: str | None
    trace_id: str | None
    checked_trace_id: str | None
    feedback: MetaDiagnosticsFeedback | None
    phone: MetaDiagnosticsPhoneSection | None
    waba: MetaDiagnosticsWabaSection | None
    app: MetaDiagnosticsApp
    health_status: MetaDiagnosticsHealthSection | None
    capabilities: MetaDiagnosticsCapabilities
    checks: list[MetaDiagnosticsCheck]
