from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

ThroughputTier: TypeAlias = Literal["starter", "growth", "scale"]
SubscriptionBillingRail: TypeAlias = Literal["stripe_card", "pix_annual"]
BillingPackageStatus: TypeAlias = Literal["pending", "succeeded", "failed", "refunded", "expired"]
PhoneRenewalStatus: TypeAlias = Literal[
    "scheduled",
    "funding_required",
    "funded",
    "renewed",
    "release_requested",
    "released",
    "cancelled",
]
PhoneRenewalActionableState: TypeAlias = Literal[
    "upcoming",
    "at_risk",
    "funded",
    "renewed",
    "release_pending",
    "released",
    "cancelled",
]
PhoneRenewalRecommendedAction: TypeAlias = Literal[
    "none", "add_credit_or_enable_auto_topup", "monitor_release"
]


class CreditBalanceResponse(TypedDict):
    object: Literal["credit_balance"]
    # Production API-key and MCP credit policy, independent of the selected environment.
    # Recovering access does not clear other sending gates. Current reads always include it.
    production_blocked: NotRequired[bool]
    organization_id: str
    balance_brl: str
    # Credit held by outstanding production reservations, already deducted from
    # `balance_brl`. A hold is not spend; sandbox holds are not counted. Current reads always
    # include it.
    held_brl: NotRequired[str]
    currency: Literal["brl"]
    updated_at: str


class PlanOfferingResponse(TypedDict):
    object: Literal["plan_offering"]
    id: str
    display_name: str
    monthly_fee_brl: str
    annual_pix_fee_brl: str
    platform_fee_multiplier: str
    net_transport_rate_brl: str
    throughput_tier: ThroughputTier
    max_phones: int | None
    salvy_byok_enabled: NotRequired[bool]


class ListPlansResponse(TypedDict):
    object: Literal["list"]
    data: list[PlanOfferingResponse]


class CurrentPlanResponse(TypedDict):
    object: Literal["subscription"]
    status: Literal["active", "past_due", "canceled", "none"]
    plan_offering_id: str | None
    display_name: str | None
    billing_rail: SubscriptionBillingRail | None
    throughput_tier: ThroughputTier
    max_phones: int | None
    platform_fee_multiplier: str
    net_transport_rate_brl: str
    monthly_fee_brl: str | None
    current_period_end: str | None
    cancel_at_period_end: bool
    # A plan entitlement, not evidence that Salvy BYOK admission is available at runtime.
    salvy_byok_enabled: NotRequired[bool]


class SubscribePlanRequest(TypedDict):
    plan_offering_id: str
    rail: NotRequired[SubscriptionBillingRail]


class ChangePlanRequest(TypedDict):
    plan_offering_id: str


class SubscribePixCheckout(TypedDict):
    charge_id: str
    amount_brl: str
    copy_paste: str | None
    qr_code_base64: str | None
    expires_at: str | None


class SubscribePlanResponse(TypedDict):
    object: Literal["subscription_checkout"]
    subscription: CurrentPlanResponse
    pix: SubscribePixCheckout | None


class PlanPackageOfferingResponse(TypedDict):
    id: str
    object: Literal["plan_package_offering"]
    code: str
    name: str
    throughput_tier: ThroughputTier
    price_brl: str
    quota_messages: int
    active: bool
    created_at: str
    updated_at: str


class BillingPackageResponse(TypedDict):
    id: str
    object: Literal["billing_package"]
    status: BillingPackageStatus
    package_code: str
    throughput_tier: ThroughputTier
    amount_brl: str
    quota_messages: int
    quota_remaining: int
    payment_method: Literal["pix", "card"]
    stripe_payment_intent_id: str | None
    created_at: str
    completed_at: str | None


class ListBillingPackagesResponse(TypedDict):
    object: Literal["list"]
    data: list[BillingPackageResponse]
    has_more: bool
    next_cursor: str | None
    available_packages: list[PlanPackageOfferingResponse]


class PurchaseBillingPackageRequest(TypedDict):
    package_code: str
    # Package purchases are card-only; `card` is the default.
    payment_method: NotRequired[Literal["card"]]
    # Saved-card selector.
    payment_method_id: NotRequired[str]


TopupPaymentMethodKind: TypeAlias = Literal["pix", "card", "x402", "manual", "promotion"]


class TopupResponse(TypedDict):
    id: str
    object: Literal["credit_topup"]
    kind: Literal["cash", "package", "x402"]
    status: BillingPackageStatus
    amount_brl: str
    payment_method: TopupPaymentMethodKind
    package_code: str | None
    quota_messages: int | None
    quota_remaining: int | None
    stripe_payment_intent_id: str | None
    stripe_client_secret: str | None
    provider: NotRequired[Literal["stripe", "abacate_pay", "manual", "promotion"]]
    abacate_charge_id: NotRequired[str | None]
    pix_copy_paste: NotRequired[str | None]
    pix_qr_code_base64: NotRequired[str | None]
    pix_expires_at: NotRequired[str | None]
    created_at: str
    completed_at: str | None


class BillingPaymentMethodSetupIntentResponse(TypedDict):
    object: Literal["billing_payment_method_setup_intent"]
    stripe_customer_id: str
    stripe_setup_intent_id: str
    stripe_client_secret: str | None


class BillingPaymentMethodResponse(TypedDict):
    id: str
    object: Literal["billing_payment_method"]
    type: Literal["card"]
    brand: str | None
    last4: str | None
    exp_month: int | None
    exp_year: int | None
    is_default: bool
    status: Literal["active", "deleted"]
    created_at: str
    updated_at: str


class ListBillingPaymentMethodsResponse(TypedDict):
    object: Literal["list"]
    data: list[BillingPaymentMethodResponse]
    has_more: bool
    next_cursor: str | None


class SaveBillingPaymentMethodRequest(TypedDict):
    stripe_payment_method_id: str
    set_default: NotRequired[bool]


class AutoTopupConfigResponse(TypedDict):
    object: Literal["auto_topup_config"]
    enabled: bool
    threshold_brl: str
    amount_brl: str
    payment_method_id: str | None
    last_triggered_at: str | None
    updated_at: str | None


class UpdateAutoTopupConfigRequest(TypedDict):
    enabled: bool
    threshold_brl: str
    amount_brl: str
    payment_method_id: NotRequired[str | None]


LedgerEntryType: TypeAlias = Literal["debit", "credit", "hold", "release"]
LedgerEntrySourceType: TypeAlias = Literal["usage", "credit_topup", "payment_fee_hold"]


class LedgerEntryPaymentFee(TypedDict):
    payment_object: Literal["payment_request", "agentic_payment"]
    payment_id: str
    reservation_id: str


class LedgerEntryResponse(TypedDict):
    id: str
    object: Literal["ledger_entry"]
    # `hold` and `release` are payment completion-fee holds and their return: never spend.
    # Only `debit` entries are spend.
    type: LedgerEntryType
    source_type: LedgerEntrySourceType
    source_id: str
    meter_id: str | None
    amount_brl: str
    uncollected_brl: str | None
    currency: Literal["brl"]
    environment: Environment | None
    recorded_at: str
    trace_id: str | None
    # The payment and fee reservation of a payment-fee entry; None otherwise.
    payment_fee: LedgerEntryPaymentFee | None


class ListLedgerEntriesResponse(TypedDict):
    object: Literal["list"]
    data: list[LedgerEntryResponse]
    has_more: bool
    next_cursor: str | None


class PhoneRenewalResponse(TypedDict):
    id: str
    object: Literal["phone_renewal"]
    status: PhoneRenewalStatus
    actionable_state: PhoneRenewalActionableState
    recommended_action: PhoneRenewalRecommendedAction
    phone_number_id: str
    display_name: str | None
    phone: str | None
    period_start: str
    period_end: str
    amount_brl: str
    currency: Literal["brl"]
    upcoming_notice_at: str | None
    funding_scheduled_at: str | None
    funding_attempted_at: str | None
    next_funding_attempt_at: str | None
    funded_at: str | None
    next_renewal_at: NotRequired[str | None]
    # The 48h/24h warning dates are always None.
    renewal_warning_48h_at: NotRequired[str | None]
    renewal_warning_24h_at: NotRequired[str | None]
    grace_selected_at: NotRequired[str | None]
    grace_ends_at: NotRequired[str | None]
    release_cutoff_at: str | None
    release_requested_at: str | None
    renewed_at: str | None
    released_at: str | None
    cancelled_at: str | None
    terminal_at: str | None


PhoneRenewalSummaryState: TypeAlias = Literal[
    "upcoming", "funded", "at_risk", "grace", "release_pending", "released", "unknown"
]
PhoneRenewalSummaryReasonCode: TypeAlias = Literal[
    "insufficient_credit",
    "grace_in_progress",
    "grace_exhausted",
    "release_committed",
    "provider_timing_unknown",
    "provider_state_unknown",
    "cycle_not_ready",
]


class PhoneRenewalSummary(TypedDict):
    """A rented number's current UTC month, read from `renewal` on phone-number reads.

    `state` `upcoming` means the month is paid or the number was not charged for it; `at_risk`
    means this month's rental charge left the balance below zero and it has not come back to
    zero or above. `next_renewal_at` is the monthly charge at 00:05 UTC on the 1st.
    `release_cutoff_at` is when a free-plan number is released if the month is still unpaid,
    and `automatic_release_enabled` is False while a paid plan keeps the numbers. `amount_brl`
    is this month's rental charge, with four decimals. `cycle_id`, the 48h/24h warning dates,
    the grace dates, `release_requested_at` and `provider_evidence_observed_at` are always None.
    """

    state: PhoneRenewalSummaryState
    reason_codes: list[PhoneRenewalSummaryReasonCode]
    cycle_id: str | None
    amount_brl: str | None
    currency: Literal["brl"] | None
    next_renewal_at: str | None
    release_cutoff_at: str | None
    renewal_warning_48h_at: str | None
    renewal_warning_24h_at: str | None
    grace_selected_at: str | None
    grace_ends_at: str | None
    automatic_release_enabled: bool
    release_requested_at: str | None
    recommended_action: PhoneRenewalRecommendedAction | None
    evaluated_at: str
    provider_evidence_observed_at: str | None


class ListPhoneRenewalsResponse(TypedDict):
    object: Literal["list"]
    data: list[PhoneRenewalResponse]
    has_more: bool
    next_cursor: str | None


class PhoneManagementCoverageResponse(TypedDict):
    state: Literal["plan", "prepaid", "none"]
    covered_until: str | None
    next_charge_at: str | None
    next_charge_brl: str | None


class PhoneManagementResponse(TypedDict):
    phone_number_id: str
    coverage: PhoneManagementCoverageResponse
    covered_until: str | None
    next_charge_at: str | None
    next_charge_brl: str | None
    # Charged `prepaid` coverage alone does not prove payment; read this field.
    current_month_payment_status: NotRequired[Literal["paid", "unpaid", "not_charged"] | None]
    disable_at: NotRequired[str | None]
    service_state: NotRequired[
        Literal["serving", "disabled_unpaid_month_end", "funding_required", "not_serving"] | None
    ]


class PhoneManagementSummary(TypedDict):
    retained_count: int
    monthly_total_brl: str
    next_charge_at: str | None
    # Exact total due at `next_charge_at`; None when no charge is scheduled.
    next_charge_brl: NotRequired[str | None]


class ListPhoneManagementResponse(TypedDict):
    object: Literal["list"]
    data: list[PhoneManagementResponse]
    has_more: bool
    next_cursor: str | None
    summary: PhoneManagementSummary


class InvoiceResponse(TypedDict):
    id: str
    object: Literal["invoice"]
    organization_id: str
    project_id: str
    period_start: str
    period_end: str
    currency: Literal["brl"]
    total_brl: str
    status: Literal["generating", "ready", "failed"]
    error_message: str | None
    created_at: str
    updated_at: str


class ListInvoicesResponse(TypedDict):
    object: Literal["list"]
    data: list[InvoiceResponse]
    has_more: bool
    next_cursor: str | None


class InvoiceDownloadResponse(TypedDict):
    object: Literal["invoice_download"]
    invoice_id: str
    url: str
    expires_at: str


class RateCardEntryResponse(TypedDict):
    id: str
    meter_id: str
    kind: Literal["billed", "meta_reference"]
    conversation_category: Literal["service", "utility", "marketing", "authentication"] | None
    unit_amount: str
    tier_up_to: int | None


class RateCardResponse(TypedDict):
    id: str
    object: Literal["rate_card"]
    name: str
    currency: Literal["brl"]
    effective_from: str
    effective_to: str | None
    entries: list[RateCardEntryResponse]


class ListRateCardsResponse(TypedDict):
    object: Literal["list"]
    data: list[RateCardResponse]
    has_more: bool
    next_cursor: str | None
