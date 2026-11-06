from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment, JSONObject

PaymentStatus: TypeAlias = Literal[
    "link_pending",
    "link_generated",
    "approval_requested",
    "approved",
    "paid",
    "failed",
    "expired",
    "cancelled",
]
MerchantPaymentProvider: TypeAlias = Literal["iniciador", "abacate_pay"]


class IniciadorProviderOptions(TypedDict, total=False):
    participant_id: str
    redirect_url: str
    redirect_on_error_url: str


class AbacatePayProviderOptions(TypedDict, total=False):
    charge_type: Literal["pix", "checkout"]
    create_customer: bool


class PaymentProviderOptions(TypedDict, total=False):
    iniciador: IniciadorProviderOptions
    abacate_pay: AbacatePayProviderOptions


class CreatePaymentRequest(TypedDict):
    amount_brl_centavos: int
    description: NotRequired[str]
    customer_name: NotRequired[str]
    customer_tax_id: NotRequired[str]
    customer_phone: NotRequired[str]
    customer_email: NotRequired[str]
    external_reference: NotRequired[str]
    metadata: NotRequired[JSONObject]
    provider_options: NotRequired[PaymentProviderOptions]


class RequestPaymentApprovalRequest(TypedDict):
    note: NotRequired[str]
    metadata: NotRequired[JSONObject]


class SandboxPaymentStatusRequest(TypedDict):
    status: Literal["paid", "failed", "expired", "cancelled"]
    provider_event_id: NotRequired[str]
    metadata: NotRequired[JSONObject]


PaymentFeeCompletionState: TypeAlias = Literal["held", "settled", "released", "unresolved"]


class PaymentFeeInitiation(TypedDict):
    # Matches `payment_fee.reservation_id` on the ledger's payment initiation debit.
    reservation_id: str
    amount_brl: str
    charged_at: str


class PaymentFeeCompletion(TypedDict):
    # Matches `payment_fee.reservation_id` on the ledger's hold, release and settlement.
    reservation_id: str
    # Fraction of the payment amount: "0.01" is 1%.
    rate: str
    amount_brl: str
    state: PaymentFeeCompletionState
    held_at: str
    settled_at: str | None
    released_at: str | None


class PaymentFees(TypedDict):
    """The payment-service fees of one accepted payment.

    The same object appears on `PaymentResponse` and `AgenticPaymentResponse`. Amounts are
    four-decimal strings, snapshotted at acceptance and never re-priced.
    """

    # True in sandbox: the amounts production would charge, with no balance movement.
    simulated: bool
    # Pricing version: the BRL rate card in force when the payment was accepted.
    rate_card_id: str
    initiation: PaymentFeeInitiation
    completion: PaymentFeeCompletion


class PaymentResponse(TypedDict):
    id: str
    object: Literal["payment_request"]
    status: PaymentStatus
    environment: Environment
    amount_brl: str
    currency: Literal["BRL"]
    description: str | None
    customer_name: str | None
    customer_tax_id: str | None
    customer_phone: str | None
    customer_email: str | None
    external_reference: str | None
    metadata: JSONObject | None
    payment_link_url: str | None
    pix_copy_paste: str | None
    pix_qr_code_base64: str | None
    provider: MerchantPaymentProvider
    provider_connection_id: str | None
    provider_payment_id: str | None
    provider_approval_id: str | None
    provider_metadata: JSONObject | None
    trace_id: str
    created_at: str
    updated_at: str
    link_generated_at: str | None
    approval_requested_at: str | None
    approved_at: str | None
    paid_at: str | None
    failed_at: str | None
    expired_at: str | None
    cancelled_at: str | None
    # None: no fee is owed. An Idempotency-Key replay returns its stored response, with `fees`
    # as at the original call; read the payment for the current state. Absent only on such a
    # replay stored before the field existed.
    fees: NotRequired[PaymentFees | None]


class ListPaymentsResponse(TypedDict):
    object: Literal["list"]
    data: list[PaymentResponse]
    has_more: bool
    next_cursor: str | None
