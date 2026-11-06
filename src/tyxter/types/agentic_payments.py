from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment, JSONObject
from .payments import PaymentFees

AgenticPixMethod: TypeAlias = Literal["PIX_DICT", "PIX_MANU", "PIX_QRCODE"]
AgenticAuthorizationStatus: TypeAlias = Literal["pending", "completed", "revoked", "rejected"]
AgenticPaymentStatus: TypeAlias = Literal[
    "authorization_link_pending",
    "authorization_required",
    "authorization_pending",
    "payment_link_pending",
    "payment_confirmation_required",
    "pending",
    "paid",
    "cancelled",
    "rejected",
    "expired",
    "error",
]


class AgenticPaymentNextAction(TypedDict):
    type: Literal["open_authorization_url", "open_payment_url"]
    url: str


class AgenticBusinessEntity(TypedDict):
    tax_id: str
    name: NotRequired[str]


class AgenticPaymentCreditor(TypedDict):
    name: str
    tax_id: str
    ispb: str
    number: str
    account_type: Literal["CACC", "SLRY", "SVGS", "TRAN"]
    issuer: NotRequired[str]


class CreateAgenticAuthorizationRequest(TypedDict):
    customer_tax_id: str
    agent_reason: str
    participant_id: NotRequired[str]
    participant_name: NotRequired[str]
    customer_name: NotRequired[str]
    business_entity: NotRequired[AgenticBusinessEntity]
    external_reference: NotRequired[str]
    metadata: NotRequired[JSONObject]
    redirect_url: NotRequired[str]
    redirect_on_error_url: NotRequired[str]


class CreateAgenticPaymentRequest(TypedDict):
    amount_brl_centavos: int
    method: AgenticPixMethod
    customer_tax_id: str
    agent_reason: str
    participant_id: NotRequired[str]
    participant_name: NotRequired[str]
    customer_name: NotRequired[str]
    business_entity: NotRequired[AgenticBusinessEntity]
    description: NotRequired[str]
    pix_key: NotRequired[str]
    qr_code: NotRequired[str]
    creditor: NotRequired[AgenticPaymentCreditor]
    external_reference: NotRequired[str]
    metadata: NotRequired[JSONObject]
    redirect_url: NotRequired[str]
    redirect_on_error_url: NotRequired[str]


class AgenticBankResponse(TypedDict):
    id: str
    object: Literal["agentic_bank"]
    participant_id: str
    name: str
    code: str | None
    ispb: str | None
    raw: JSONObject | None


class ListAgenticBanksResponse(TypedDict):
    object: Literal["list"]
    data: list[AgenticBankResponse]
    has_more: Literal[False]
    next_cursor: None


class AgenticAuthorizationResponse(TypedDict):
    id: str
    object: Literal["agentic_payment_authorization"]
    status: AgenticAuthorizationStatus
    environment: Environment
    provider_connection_id: str
    participant_id: str
    participant_name: str | None
    customer_name: str | None
    customer_tax_id: str
    business_tax_id: str | None
    business_name: str | None
    provider_authorization_id: str | None
    authorization_url: str | None
    upstream_status: str | None
    external_reference: str | None
    agent_reason: str
    metadata: JSONObject | None
    provider_metadata: JSONObject | None
    next_action: AgenticPaymentNextAction | None
    trace_id: str
    created_at: str
    updated_at: str
    completed_at: str | None
    revoked_at: str | None
    rejected_at: str | None


class AgenticPaymentResponse(TypedDict):
    id: str
    object: Literal["agentic_payment"]
    status: AgenticPaymentStatus
    environment: Environment
    provider_connection_id: str
    authorization_id: str | None
    amount_brl: str
    amount_brl_centavos: int
    currency: Literal["BRL"]
    method: AgenticPixMethod
    participant_id: str
    participant_name: str | None
    description: str | None
    customer_name: str | None
    customer_tax_id: str
    business_tax_id: str | None
    business_name: str | None
    agent_reason: str
    external_reference: str | None
    metadata: JSONObject | None
    payment_url: str | None
    provider: Literal["iniciador"]
    provider_payment_id: str | None
    provider_metadata: JSONObject | None
    next_action: AgenticPaymentNextAction | None
    trace_id: str
    created_at: str
    updated_at: str
    authorization_required_at: str | None
    payment_link_generated_at: str | None
    pending_at: str | None
    paid_at: str | None
    cancelled_at: str | None
    rejected_at: str | None
    expired_at: str | None
    error_at: str | None
    # None: no fee is owed. An Idempotency-Key replay (creation or cancel) returns its stored
    # response, with `fees` as at the original call; read the payment for the current state.
    # Absent only on such a replay stored before the field existed.
    fees: NotRequired[PaymentFees | None]


class ListAgenticAuthorizationsResponse(TypedDict):
    object: Literal["list"]
    data: list[AgenticAuthorizationResponse]
    has_more: bool
    next_cursor: str | None


class ListAgenticPaymentsResponse(TypedDict):
    object: Literal["list"]
    data: list[AgenticPaymentResponse]
    has_more: bool
    next_cursor: str | None
