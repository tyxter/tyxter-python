from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

TyxterErrorType: TypeAlias = Literal[
    "authentication_error",
    "authorization_error",
    "payment_required",
    "validation_error",
    "idempotency_conflict",
    "rate_limited",
    "not_found",
    "conflict",
    "provider_error",
    "internal_error",
    "service_unavailable",
]


class ErrorFeedbackPointer(TypedDict):
    """Pointer to the feedback endpoint on errors the API marks as reportable.

    Many errors carry it, for example an unhandled ``internal_error``, the payment-fee and
    merchant-cancellation refusals, and ``phone_number_rental_approval_required``; this list is
    not complete. Treat the pointer's presence, not the error code, as the signal that a failure
    can be reported.
    """

    endpoint: Literal["/v1/feedback"]
    method: Literal["POST"]


class ErrorDiscoveryPointer(TypedDict):
    openapi: str
    well_known: str


class WebhookListenSessionActiveSession(TypedDict):
    id: str
    expires_at: str
    created_at: str


class WebhookListenSessionConflictDetails(TypedDict):
    """Bounded recovery metadata for an active production listen-session conflict."""

    active_session: WebhookListenSessionActiveSession


class PhoneNumberRentalApprovalOrder(TypedDict):
    id: str
    approval_url: str
    expires_at: str


class PhoneNumberRentalApprovalRequiredDetails(TypedDict):
    """Recovery metadata for ``phone_number_rental_approval_required``.

    ``order`` is the production rental order the request created: its id, the dashboard page
    where an organization owner or admin approves or declines it, and when it expires.
    """

    order: PhoneNumberRentalApprovalOrder


ServiceWindowRequiredReason: TypeAlias = Literal[
    "no_inbound", "window_expired", "recipient_ambiguous"
]


class ServiceWindowRequiredDetails(TypedDict):
    """Bounded evidence for a ``service_window_required`` refusal."""

    reason: ServiceWindowRequiredReason
    last_inbound_at: str | None


class CreditBalanceExhaustedReachableRoute(TypedDict):
    method: str
    path: str


class CreditBalanceExhaustedDetails(TypedDict):
    """Details of a ``402 credit_balance_exhausted`` refusal.

    ``top_up_url`` is the organization's billing page; ``reachable_routes`` lists each public
    route that still answers while credit is exhausted.
    """

    top_up_url: str
    reachable_routes: list[CreditBalanceExhaustedReachableRoute]


class RecipientGuardDetails(TypedDict):
    """Recipient-guard refusal metadata, such as ``recipient_duplicate_message``.

    ``next_allowed_at`` is the cooldown timestamp, or ``None`` while recovery needs engagement,
    consent or the resolution of an earlier pending send.
    """

    next_allowed_at: str | None
    guard_reason: NotRequired[str]


TyxterWireErrorDetails: TypeAlias = (
    CreditBalanceExhaustedDetails
    | WebhookListenSessionConflictDetails
    | PhoneNumberRentalApprovalRequiredDetails
    | ServiceWindowRequiredDetails
    | RecipientGuardDetails
)


class _TyxterErrorBodyFields(TypedDict):
    type: TyxterErrorType
    code: str
    message: str
    param: NotRequired[str]
    retry_after_ms: NotRequired[int]
    # ``False`` is a stop hint: do not retry automatically. Absence is not permission to retry.
    retryable: NotRequired[Literal[False]]
    request_id: NotRequired[str]
    trace_id: NotRequired[str]
    feedback: NotRequired[ErrorFeedbackPointer]
    discovery: NotRequired[ErrorDiscoveryPointer]


class TyxterErrorBody(_TyxterErrorBodyFields):
    """The existing error-body view; ``details`` is the listen-session recovery view."""

    details: NotRequired[WebhookListenSessionConflictDetails]


class TyxterWireErrorBody(_TyxterErrorBodyFields):
    """The complete ``error`` object of an API error response, including every details family."""

    details: NotRequired[TyxterWireErrorDetails]


class TyxterErrorResponse(TypedDict):
    error: TyxterErrorBody


class TyxterWireErrorResponse(TypedDict):
    error: TyxterWireErrorBody
