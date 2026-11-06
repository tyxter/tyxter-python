from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

PhoneNumberSource: TypeAlias = Literal["salvy", "byon"]
PhoneNumberStatus: TypeAlias = Literal[
    "requested",
    "provisioning",
    "provisioned",
    "verifying",
    "active",
    "failed",
    "release_requested",
    "released",
    "disconnected",
]
PhoneQualityRating: TypeAlias = Literal["green", "yellow", "red", "unknown"]
PhoneMessagingTier: TypeAlias = Literal[
    "tier_50", "tier_250", "tier_1k", "tier_2k", "tier_10k", "tier_100k", "unlimited", "unknown"
]
MetaThroughputTier: TypeAlias = Literal["1", "2", "3", "4", "unlimited"]


class ProvisionPhoneNumberRequest(TypedDict):
    ddd: str
    display_name: NotRequired[str]


class ConnectPhoneNumberRequest(TypedDict):
    phone: str
    meta_phone_number_id: str
    display_name: NotRequired[str]


class TransferPhoneNumberRequest(TypedDict):
    source_project_id: str
    source_environment_id: str
    target_project_id: str
    target_environment_id: str
    confirm_phone_number_id: str
    reason: NotRequired[str]


class ImportSalvyPhoneNumberRequest(TypedDict):
    provider_connection_id: str
    provider_number_id: str
    meta_phone_number_id: NotRequired[str]
    display_name: NotRequired[str]
    continuation_terms_version: Literal["salvy_byok_v1"]


class CompleteSalvyPhoneRegistrationRequest(TypedDict):
    meta_phone_number_id: str


class CreatePhoneNumberOrderRequest(TypedDict):
    ddd: str
    display_name: NotRequired[str]
    # Why the number is needed, shown to the owner or admin who approves the order.
    purpose: NotRequired[str]


PhoneNumberOrderStatus: TypeAlias = Literal[
    "awaiting_approval",
    "approved",
    "declined",
    "expired",
    "provisioning",
    "fulfilled",
    "failed",
]
PhoneNumberOrderFailureCode: TypeAlias = Literal[
    "phone_number_order_declined",
    "phone_number_order_expired",
    "phone_number_order_terms_changed",
]


class PhoneNumberOrderPreviewCharge(TypedDict):
    period_start: str
    period_end: str
    # The earliest instant the balance moves for this charge.
    charged_from: str
    amount_brl: str


class PhoneNumberOrderPreviewActivation(TypedDict):
    amount_brl: str
    period_start: str
    period_end: str


class PhoneNumberOrderPreviewFree(TypedDict):
    status: Literal["free"]


class PhoneNumberOrderPreviewForecast(TypedDict):
    status: Literal["forecast"]
    computed_at: str
    activation: PhoneNumberOrderPreviewActivation
    charges: list[PhoneNumberOrderPreviewCharge]


PhoneNumberOrderPreview: TypeAlias = PhoneNumberOrderPreviewFree | PhoneNumberOrderPreviewForecast


class PhoneNumberOrderFailure(TypedDict):
    code: PhoneNumberOrderFailureCode
    message: str


class PhoneNumberOrderResponse(TypedDict):
    object: Literal["phone_number_order"]
    id: str
    status: PhoneNumberOrderStatus
    project_id: str
    environment_id: str
    ddd: str
    display_name: str | None
    purpose: str | None
    preview: PhoneNumberOrderPreview
    terms_version: str
    # The dashboard page where an owner or admin approves or declines the order;
    # None unless the order awaits approval. No API key can approve an order.
    approval_url: str | None
    expires_at: str
    # The phone number the approval started; None before approval.
    phone_number_id: str | None
    failure: PhoneNumberOrderFailure | None
    created_at: str
    approved_at: str | None
    declined_at: str | None


class SalvyPhoneManagementResponse(TypedDict):
    provider_connection_id: str
    provider_number_id: str
    state: Literal["enabled", "suspended"]
    coverage: Literal["plan", "prepaid", "none"]
    covered_until: str | None
    next_charge_at: str | None
    next_charge_brl: str | None
    # None while enabled. An open string: treat an unfamiliar value as not serving.
    suspension_reason: str | None
    provider_status: str | None
    synced_at: str | None


PhoneNumberRecentMessageResponse = TypedDict(
    "PhoneNumberRecentMessageResponse",
    {
        "id": str,
        "object": Literal["message"],
        "direction": str,
        "type": str,
        "status": str,
        "from": str | None,
        "to": str | None,
        "template_name": str | None,
        "created_at": str,
    },
)


class PhoneNumberNameReviewResponse(TypedDict):
    requested_name: str | None
    decision: str
    reason: str | None
    reviewed_at: str


class PhoneNumberPendingNameReviewResponse(TypedDict):
    requested_name: str | None
    status: str | None
    observed_at: str


class PhoneNumberResponse(TypedDict):
    id: str
    object: Literal["phone_number"]
    source: PhoneNumberSource
    status: PhoneNumberStatus
    environment: Environment
    display_name: str | None
    ddd: str | None
    phone: str | None
    provider_number_id: str | None
    meta_phone_number_id: str | None
    waba_id: str | None
    # Optional management of a customer-owned Salvy number. None means ordinary
    # BYON or a Tyxter-provisioned rental; it never changes `source`.
    salvy_management: NotRequired[SalvyPhoneManagementResponse | None]
    quality_rating: PhoneQualityRating
    messaging_tier: PhoneMessagingTier
    messaging_limit_tier: str | None
    meta_throughput_tier: MetaThroughputTier | None
    meta_quality_rating: str | None
    verified_name: NotRequired[str | None]
    pending_name_review: NotRequired[PhoneNumberPendingNameReviewResponse | None]
    name_review: NotRequired[PhoneNumberNameReviewResponse | None]
    # When the Meta-reported health above was last read from Meta. ``None``
    # means it has never been read yet; an older timestamp means those fields
    # are as of that moment, since a failed refresh leaves both the values and
    # this marker untouched.
    meta_health_synced_at: str | None
    current_24h_unique_recipients: int
    remaining_messaging_allowance_estimate: int | None
    verification_code: str | None
    verification_code_received_at: str | None
    monthly_fee_brl: str | None
    error_code: str | None
    error_message: str | None
    created_at: str
    updated_at: str
    activated_at: str | None
    released_at: str | None
    recent_messages: list[PhoneNumberRecentMessageResponse]


class ListPhoneNumbersResponse(TypedDict):
    object: Literal["list"]
    data: list[PhoneNumberResponse]
    has_more: bool
    next_cursor: str | None


class AvailableRegionResponse(TypedDict):
    ddd: str
    country: Literal["BR"]
    monthly_fee_brl: str
    state: str | None
    region_label: str | None


class ListAvailableRegionsResponse(TypedDict):
    object: Literal["list"]
    data: list[AvailableRegionResponse]
