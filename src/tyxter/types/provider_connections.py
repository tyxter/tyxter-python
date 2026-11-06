from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, Required, TypedDict

from .common import Environment
from .display_names import DisplayNameWarning

ProviderName: TypeAlias = Literal["meta", "iniciador", "abacate_pay", "salvy"]
ProviderConnectionStatus: TypeAlias = Literal["pending", "connected", "suspended", "disconnected"]
ProviderConnectionSendCapability: TypeAlias = Literal["available", "blocked"]
ProviderConnectionSendBlockCode: TypeAlias = Literal[141006, 141008, 141011]
ProviderTokenSource: TypeAlias = Literal["manual", "embedded_signup"]
ProviderConnectionChannel: TypeAlias = Literal[
    "whatsapp", "instagram", "payments", "agentic_payments", "phone_numbers"
]
MetaConnectionChannel: TypeAlias = Literal["whatsapp", "instagram"]
ProviderReadinessStatus: TypeAlias = Literal[
    "missing", "connected", "pending", "suspended", "disconnected", "selection_required"
]
ProviderCredentialSetupTarget: TypeAlias = Literal[
    "meta.whatsapp",
    "salvy",
    "abacate_pay.payments",
    "iniciador.payments",
    "iniciador.agentic_payments",
    "openai.tts",
    "elevenlabs.tts",
    "xai.tts",
    "openai.stt",
]
ProviderCredentialSetupSessionStatus: TypeAlias = Literal[
    "pending", "completed", "denied", "expired"
]
ProviderCredentialSetupTtsProvider: TypeAlias = Literal["openai", "elevenlabs", "xai"]
ProviderCredentialSetupSttProvider: TypeAlias = Literal["openai"]


class PaymentReceiverProfile(TypedDict, total=False):
    name: str
    tax_id: str
    bank_name: str
    ispb: str
    issuer: str
    account_number: str
    account_type: Literal["CACC", "SLRY", "SVGS", "TRAN"]


class PaymentProviderCapabilities(TypedDict):
    hosted_payment_link: bool
    fixed_receiver: bool
    webhook_hmac: bool
    dynamic_receiver: bool


class AgenticPaymentProviderCapabilities(TypedDict):
    mcp_tools: bool
    reusable_authorizations: bool
    hosted_authorization: bool
    hosted_payment_confirmation: bool
    polling: bool


class ExchangeMetaOAuthCodeRequest(TypedDict, total=False):
    code: Required[str]
    waba_id: NotRequired[str]
    phone_number_id: NotRequired[str]
    display_name: NotRequired[str]
    business_id: NotRequired[str]
    signup_session_id: NotRequired[str]


SalvyConnectionOperationErrorCode: TypeAlias = Literal[
    "salvy_credentials_invalid",
    "salvy_provider_unavailable",
    "salvy_connection_unavailable",
]


class SalvyConnectionOperation(TypedDict):
    state: Literal["queued", "succeeded", "failed"]
    error_code: SalvyConnectionOperationErrorCode | None


class SalvyConnectionInfo(TypedDict):
    sync_mode: Literal["polling"]
    credential_hint: str | None
    discovered_at: str | None
    operation: SalvyConnectionOperation | None


class RegisterSalvyConnectionRequest(TypedDict):
    api_key: str
    display_name: NotRequired[str]
    continuation_terms_version: Literal["salvy_byok_v1"]


ApiKeyRegisterSalvyConnectionRequest: TypeAlias = RegisterSalvyConnectionRequest
DashboardBffRegisterSalvyConnectionRequest: TypeAlias = RegisterSalvyConnectionRequest


class RotateSalvyConnectionRequest(TypedDict):
    api_key: str


ApiKeyRotateSalvyConnectionRequest: TypeAlias = RotateSalvyConnectionRequest
DashboardBffRotateSalvyConnectionRequest: TypeAlias = RotateSalvyConnectionRequest

# The worker operation behind an asynchronous connect: a Meta Embedded Signup OAuth code
# exchange (`exchange_meta_oauth`), a Meta complete-registration
# (`complete_meta_registration`), a Meta registration made internally, a legacy Meta token
# rotation, or an Iniciador agentic registration made in the dashboard.
ProviderConnectionOperationKind: TypeAlias = Literal[
    "meta_registration",
    "meta_token_rotation",
    "meta_oauth_exchange",
    "meta_registration_completion",
    "iniciador_agentic_registration",
]
# Why a provider-connection operation failed: the stable code the same route answered
# synchronously before its provider call moved to a worker. `meta_validation_failed` also
# covers a registration, rotation or complete-registration the worker could not finish in time,
# `meta_oauth_exchange_unavailable` an OAuth code exchange, and `agentic_provider_unavailable`
# an agentic registration; a retry can succeed.
ProviderConnectionOperationErrorCode: TypeAlias = Literal[
    "whatsapp_credentials_invalid",
    "instagram_credentials_invalid",
    "missing_whatsapp_scopes",
    "meta_token_foreign_app",
    "meta_phone_number_not_accessible",
    "meta_instagram_page_not_accessible",
    "meta_waba_phone_mismatch",
    "meta_instagram_account_mismatch",
    "meta_validation_failed",
    "meta_identity_enforced",
    "meta_phone_number_already_connected",
    "meta_signup_connection_exists",
    "provider_connection_policy_suspended",
    "missing_meta_app_credentials",
    "invalid_provider_connection_request",
    "invalid_environment",
    "meta_oauth_exchange_failed",
    "meta_oauth_exchange_unavailable",
    "meta_waba_missing",
    "meta_phone_number_missing",
    "meta_connection_reauthorization_required",
    "meta_messaging_permission_missing",
    "meta_payment_method_required",
    "meta_phone_pin_mismatch",
    "meta_phone_platform_unsupported",
    "meta_phone_registration_forbidden",
    "agentic_provider_unauthorized",
    "agentic_provider_unavailable",
    "unsafe_iniciador_agentic_api_base_url",
]


class ProviderConnectionOperation(TypedDict):
    kind: ProviderConnectionOperationKind
    # `queued` until the worker finishes; poll `retrieve` until `succeeded` or `failed`.
    state: Literal["queued", "succeeded", "failed"]
    # Set only when `state` is `failed`.
    error_code: ProviderConnectionOperationErrorCode | None
    updated_at: str


class SalvyNumberResponse(TypedDict):
    provider_number_id: str
    phone: str
    provider_status: str
    imported_phone_number_id: str | None


class ListSalvyNumbersResponse(TypedDict):
    object: Literal["list"]
    data: list[SalvyNumberResponse]
    has_more: bool
    next_cursor: str | None


class ProviderConnectionRestriction(TypedDict):
    restriction_type: str
    expiration: str | None
    remediation: str | None


class ProviderConnectionWabaSendCapability(TypedDict):
    waba_id: str
    send_capability: ProviderConnectionSendCapability
    send_block_codes: list[ProviderConnectionSendBlockCode]
    observed_at: str


class ProviderConnectionResponse(TypedDict):
    id: str
    object: Literal["provider_connection"]
    provider: ProviderName
    channel: ProviderConnectionChannel
    status: ProviderConnectionStatus
    display_name: str
    environment: Environment
    waba_id: str | None
    phone_number_id: str | None
    display_phone_number: NotRequired[str | None]
    ig_business_account_id: str | None
    page_id: str | None
    provider_account_id: str | None
    # Customer-owned Salvy discovery state; None for every non-Salvy connection.
    salvy: NotRequired[SalvyConnectionInfo | None]
    # The worker operation behind an asynchronous connect, token rotation or
    # complete-registration. `exchange_meta_oauth` and `complete_meta_registration` answer with
    # it `queued`; poll `retrieve` until it is `succeeded` (the connection is `connected`) or
    # `failed` (`error_code` says why). None when the connection never ran one, or when a later
    # credential write replaced a queued one; a newer registration, code exchange, rotation or
    # complete-registration replaces a queued one, so `kind` can change while you poll. Absent
    # from older API images.
    operation: NotRequired[ProviderConnectionOperation | None]
    payment_receiver: PaymentReceiverProfile | None
    payment_capabilities: PaymentProviderCapabilities | None
    agentic_capabilities: AgenticPaymentProviderCapabilities | None
    default_participant_id: str | None
    agent_id: str | None
    agentic_api_base_url: str | None
    webhook_secret_configured: bool
    suspension_reason: NotRequired[str | None]
    last_policy_warning_type: NotRequired[str | None]
    last_policy_warning_at: NotRequired[str | None]
    send_capability: NotRequired[ProviderConnectionSendCapability | None]
    send_block_codes: NotRequired[list[ProviderConnectionSendBlockCode] | None]
    send_capability_observed_at: NotRequired[str | None]
    waba_send_capabilities: NotRequired[list[ProviderConnectionWabaSendCapability]]
    waba_ban_date: NotRequired[str | None]
    waba_ban_state: NotRequired[str | None]
    account_review_status: NotRequired[str | None]
    restrictions: NotRequired[list[ProviderConnectionRestriction] | None]
    credential_last_four: NotRequired[str | None]
    token_source: ProviderTokenSource | None
    token_expires_at: str | None
    token_refreshed_at: str | None
    token_rotated_at: str | None
    created_at: str
    updated_at: str
    disconnected_at: str | None


class MetaConnectionMutationResponse(ProviderConnectionResponse):
    """The `202` connection returned by `exchange_meta_oauth()` and `complete_meta_registration()`.

    `warnings` carries advisory display-name suggestions only for a `display_name` the request
    supplied; it may be absent on older cached idempotency responses.
    """

    warnings: NotRequired[list[DisplayNameWarning]]


class DeleteProviderConnectionResponse(TypedDict):
    id: str
    object: Literal["provider_connection"]
    status: Literal["disconnected"]


class ListProviderConnectionsResponse(TypedDict):
    object: Literal["list"]
    data: list[ProviderConnectionResponse]
    has_more: bool
    next_cursor: str | None


class MessagingChannelReadiness(TypedDict):
    ready: bool
    status: ProviderReadinessStatus
    connection_id: str | None
    reason: str | None


class PaymentsChannelReadiness(TypedDict):
    ready: bool
    status: ProviderReadinessStatus
    active_connection_id: str | None
    active_mode: Literal["sandbox_default", "iniciador", "abacate_pay"] | None
    reason: str | None


class AgenticPlatformDefaultStatus(TypedDict):
    """Managed agentic-payments app availability, not connected readiness.

    `configured` reports managed app configuration, `active` stored-row ownership and `kyc`
    production KYC eligibility. A disconnected slot can recover on first agentic use.
    """

    configured: bool
    active: bool
    kyc: Literal["approved", "pending", "required"] | None


class AgenticPaymentsChannelReadiness(MessagingChannelReadiness):
    platform_default: NotRequired[AgenticPlatformDefaultStatus]


class ProviderConnectionChannels(TypedDict):
    whatsapp: MessagingChannelReadiness
    instagram: MessagingChannelReadiness
    payments: PaymentsChannelReadiness
    agentic_payments: AgenticPaymentsChannelReadiness


class ProviderConnectionStatusResponse(TypedDict):
    object: Literal["provider_connection_status"]
    environment: Environment
    channels: ProviderConnectionChannels


class MetaOnboardingExtras(TypedDict):
    version: Literal["v4"]
    sessionInfoVersion: Literal["3"]


class MetaOnboardingLoginOptions(TypedDict):
    config_id: str
    response_type: Literal["code"]
    override_default_response_type: Literal[True]
    extras: MetaOnboardingExtras


class MetaOnboardingConfigResponse(TypedDict):
    object: Literal["meta_onboarding_config"]
    mode: Literal["embedded_signup"]
    app_id: str
    config_id: str
    graph_api_version: str
    sdk_url: str
    allowed_message_origins: list[str]
    message_type: Literal["WA_EMBEDDED_SIGNUP"]
    login_options: MetaOnboardingLoginOptions
    completion_endpoint: Literal["/v1/provider-connections/meta/oauth"]


class CreateProviderCredentialSetupSessionRequest(TypedDict):
    target: ProviderCredentialSetupTarget


class ProviderCredentialSetupSessionResponse(TypedDict):
    object: Literal["provider_credential_setup_session"]
    request_id: str
    target: ProviderCredentialSetupTarget
    status: ProviderCredentialSetupSessionStatus
    project_id: str
    project_slug: str
    environment_id: str
    environment: Environment
    setup_url: str
    poll_url: str
    expires_at: str
    completed_at: str | None
    denied_at: str | None
    completed_provider_connection_id: str | None
    completed_tts_provider: ProviderCredentialSetupTtsProvider | None
    completed_stt_provider: NotRequired[ProviderCredentialSetupSttProvider | None]
    created_at: str
    updated_at: str


class _ProviderCredentialSetupSessionResultBase(TypedDict):
    object: Literal["provider_credential_setup_session"]
    request_id: str
    project_id: str
    project_slug: str
    environment_id: str
    environment: Environment
    setup_url: str
    poll_url: str
    expires_at: str
    completed_at: str | None
    denied_at: str | None
    created_at: str
    updated_at: str


class ProviderCredentialSetupSessionIncompleteResult(_ProviderCredentialSetupSessionResultBase):
    target: ProviderCredentialSetupTarget
    status: Literal["pending", "denied", "expired"]
    completed_provider_connection_id: None
    completed_tts_provider: None
    completed_stt_provider: None


class ProviderCredentialSetupSessionCompletedConnectionResult(
    _ProviderCredentialSetupSessionResultBase
):
    target: Literal[
        "meta.whatsapp",
        "salvy",
        "abacate_pay.payments",
        "iniciador.payments",
        "iniciador.agentic_payments",
    ]
    status: Literal["completed"]
    completed_provider_connection_id: str
    completed_tts_provider: None
    completed_stt_provider: None


class _ProviderCredentialSetupSessionCompletedTtsResult(_ProviderCredentialSetupSessionResultBase):
    status: Literal["completed"]
    completed_provider_connection_id: None
    completed_stt_provider: None


class ProviderCredentialSetupSessionCompletedOpenAITtsResult(
    _ProviderCredentialSetupSessionCompletedTtsResult
):
    target: Literal["openai.tts"]
    completed_tts_provider: Literal["openai"]


class ProviderCredentialSetupSessionCompletedElevenLabsTtsResult(
    _ProviderCredentialSetupSessionCompletedTtsResult
):
    target: Literal["elevenlabs.tts"]
    completed_tts_provider: Literal["elevenlabs"]


class ProviderCredentialSetupSessionCompletedXaiTtsResult(
    _ProviderCredentialSetupSessionCompletedTtsResult
):
    target: Literal["xai.tts"]
    completed_tts_provider: Literal["xai"]


class ProviderCredentialSetupSessionCompletedOpenAISttResult(
    _ProviderCredentialSetupSessionResultBase
):
    target: Literal["openai.stt"]
    status: Literal["completed"]
    completed_provider_connection_id: None
    completed_tts_provider: None
    completed_stt_provider: ProviderCredentialSetupSttProvider


ProviderCredentialSetupSessionResult: TypeAlias = (
    ProviderCredentialSetupSessionIncompleteResult
    | ProviderCredentialSetupSessionCompletedConnectionResult
    | ProviderCredentialSetupSessionCompletedOpenAITtsResult
    | ProviderCredentialSetupSessionCompletedElevenLabsTtsResult
    | ProviderCredentialSetupSessionCompletedXaiTtsResult
    | ProviderCredentialSetupSessionCompletedOpenAISttResult
)
