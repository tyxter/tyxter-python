from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

UsageGroupBy: TypeAlias = Literal[
    "destination_country",
    "template_id",
    "meta_pass_through_fee",
    "tyxter_markup",
    "package_consumption",
]
ConversationCategory: TypeAlias = Literal["service", "utility", "marketing", "authentication"]


class EstimatedExternalMetaCostSummary(TypedDict):
    """An aggregate estimate of what Meta bills directly, kept apart from Tyxter billing.

    ``covered_quantity`` had a Meta reference rate; ``missing_reference_quantity`` did not.
    """

    amount_brl: str | None
    currency: Literal["brl"]
    covered_quantity: int
    missing_reference_quantity: int
    is_estimate: Literal[True]
    billing_party: Literal["meta"]
    billing_relationship: Literal["external"]


class EstimatedExternalMetaCost(TypedDict):
    """One usage record's estimate of what Meta bills directly, with its event-time rate."""

    amount_brl: str
    currency: Literal["brl"]
    quantity: int
    conversation_category: ConversationCategory
    meta_reference_meter_key: str
    unit_rate_brl: str
    rate_card_id: str
    rate_effective_from: str
    source_id: str
    is_estimate: Literal[True]
    billing_party: Literal["meta"]
    billing_relationship: Literal["external"]


class UsageSummaryBucket(TypedDict):
    meter_id: str
    environment: Environment
    group_key: str | None
    quantity: int
    cost_brl: str
    meta_pass_through_fee_brl: str
    tyxter_markup_brl: str
    package_messages_debited: int
    estimated_external_meta_cost: NotRequired[EstimatedExternalMetaCostSummary]


class UsageSummaryResponse(TypedDict):
    object: Literal["usage_summary"]
    currency: Literal["brl"]
    period_start: str
    period_end: str
    group_by: UsageGroupBy | None
    buckets: list[UsageSummaryBucket]
    total_cost_brl: str
    estimated_external_meta_cost: NotRequired[EstimatedExternalMetaCostSummary]


class UsageRecordTransport(TypedDict):
    list_rate_brl: str
    net_rate_brl: str
    plan_multiplier: str
    list_amount_brl: str
    discount_amount_brl: str
    net_amount_brl: str
    plan_offering_id: str | None
    meta_reference_meter_key: str | None
    meta_reference_rate_brl: str | None


class UsageRecordResponse(TypedDict):
    id: str
    object: Literal["usage_record"]
    meter_id: str
    conversation_category: ConversationCategory | None
    environment: Environment
    quantity: int
    cost_brl: str
    uncollected_brl: str
    currency: Literal["brl"]
    transport: UsageRecordTransport | None
    # None when no verified event-time Meta reference rate is available.
    estimated_external_meta_cost: NotRequired[EstimatedExternalMetaCost | None]
    message_id: str | None
    package_topup_id: str | None
    package_messages_debited: int
    trace_id: str
    recorded_at: str


class ListUsageRecordsResponse(TypedDict):
    object: Literal["list"]
    data: list[UsageRecordResponse]
    has_more: bool
    next_cursor: str | None
