from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, cast

from .types import (
    ErrorFeedbackPointer,
    PhoneNumberRentalApprovalOrder,
    ServiceWindowRequiredDetails,
    TyxterErrorType,
    TyxterWireErrorBody,
    WebhookListenSessionConflictDetails,
)

_SUPPORTED_ERROR_TYPES = {
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
}


_SERVICE_WINDOW_REASONS = {"no_inbound", "window_expired", "recipient_ambiguous"}


class TyxterError(Exception):
    """Base exception for all Tyxter SDK errors."""


class TyxterAPIError(TyxterError):
    """Error returned by the Tyxter API.

    ``body`` is the whole parsed response. ``raw_body`` is its complete ``error`` object, typed
    as ``TyxterWireErrorBody``, or ``None`` when the response was not a Tyxter error envelope.
    The remaining attributes are typed views of that object:

    - ``retryable`` is ``False`` when the API sent the stop hint, for example on
      ``402 credit_balance_exhausted``: stop automatic retries. ``None`` is not permission to
      retry.
    - ``details`` is the listen-session recovery view: set only when ``error.details`` carries
      ``active_session``.
    - ``guard_reason`` and ``next_allowed_at`` come from recipient-guard refusals.
      ``next_allowed_at`` is ``None`` both when the details omit it and when the API sent
      ``null`` (recovery needs engagement, consent or an earlier pending send to resolve); read
      ``raw_body["details"]`` to tell the two apart.
    - ``rental_order`` is the order a ``phone_number_rental_approval_required`` refusal created.
    - ``service_window`` is the evidence of a ``service_window_required`` refusal, when the
      server supplied a well-formed variant.
    """

    def __init__(
        self,
        *,
        status_code: int,
        type: TyxterErrorType | Literal["api_error"],
        code: str,
        message: str,
        param: str | None = None,
        request_id: str | None = None,
        trace_id: str | None = None,
        retry_after_ms: int | None = None,
        feedback: ErrorFeedbackPointer | None = None,
        body: object = None,
        retryable: Literal[False] | None = None,
        details: WebhookListenSessionConflictDetails | None = None,
        guard_reason: str | None = None,
        next_allowed_at: str | None = None,
        rental_order: PhoneNumberRentalApprovalOrder | None = None,
        service_window: ServiceWindowRequiredDetails | None = None,
        raw_body: TyxterWireErrorBody | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.type = type
        self.code = code
        self.message = message
        self.param = param
        self.request_id = request_id
        self.trace_id = trace_id
        self.retry_after_ms = retry_after_ms
        self.feedback = feedback
        self.body = body
        self.retryable = retryable
        self.details = details
        self.guard_reason = guard_reason
        self.next_allowed_at = next_allowed_at
        self.rental_order = rental_order
        self.service_window = service_window
        self.raw_body = raw_body


class TyxterConnectionError(TyxterError):
    """Network-level failure before the Tyxter API returned a response."""


class TyxterMediaUploadError(TyxterError):
    """A capability-URL media upload returned a non-success response."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"Media upload failed with HTTP {status_code}.")
        self.status_code = status_code


def parse_api_error(status_code: int, body: object) -> TyxterAPIError:
    if isinstance(body, Mapping) and isinstance(body.get("error"), Mapping):
        error = cast(Mapping[object, object], body["error"])
        message = _string_value(error.get("message")) or f"Tyxter API request failed: {status_code}"
        code = _string_value(error.get("code")) or f"http_{status_code}"
        raw_details = error.get("details")
        details = (
            cast(Mapping[object, object], raw_details) if isinstance(raw_details, Mapping) else None
        )
        return TyxterAPIError(
            status_code=status_code,
            type=_error_type(error.get("type")),
            code=code,
            message=message,
            param=_string_value(error.get("param")),
            request_id=_string_value(error.get("request_id")),
            trace_id=_string_value(error.get("trace_id")),
            retry_after_ms=_int_value(error.get("retry_after_ms")),
            feedback=_feedback_value(error.get("feedback")),
            body=body,
            retryable=False if error.get("retryable") is False else None,
            details=_listen_session_details(details),
            guard_reason=_string_value(details.get("guard_reason")) if details else None,
            next_allowed_at=_string_value(details.get("next_allowed_at")) if details else None,
            rental_order=_rental_order(code, details),
            service_window=_service_window(code, details),
            raw_body=cast(TyxterWireErrorBody, error),
        )

    return TyxterAPIError(
        status_code=status_code,
        type="api_error",
        code=f"http_{status_code}",
        message=f"Tyxter API request failed: {status_code}",
        body=body,
    )


def _string_value(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _int_value(value: object) -> int | None:
    if isinstance(value, int):
        return value
    return None


def _error_type(value: object) -> TyxterErrorType | Literal["api_error"]:
    if isinstance(value, str) and value in _SUPPORTED_ERROR_TYPES:
        return cast(TyxterErrorType, value)
    return "api_error"


def _listen_session_details(
    details: Mapping[object, object] | None,
) -> WebhookListenSessionConflictDetails | None:
    if details is None or not isinstance(details.get("active_session"), Mapping):
        return None
    return cast(WebhookListenSessionConflictDetails, details)


def _rental_order(
    code: str, details: Mapping[object, object] | None
) -> PhoneNumberRentalApprovalOrder | None:
    if code != "phone_number_rental_approval_required" or details is None:
        return None
    order = details.get("order")
    if not isinstance(order, Mapping):
        return None
    return cast(PhoneNumberRentalApprovalOrder, order)


def _service_window(
    code: str, details: Mapping[object, object] | None
) -> ServiceWindowRequiredDetails | None:
    if code != "service_window_required" or details is None:
        return None
    if "reason" not in details or "last_inbound_at" not in details:
        return None
    last_inbound_at = details["last_inbound_at"]
    if details["reason"] not in _SERVICE_WINDOW_REASONS:
        return None
    if last_inbound_at is not None and not isinstance(last_inbound_at, str):
        return None
    return cast(ServiceWindowRequiredDetails, details)


def _feedback_value(value: object) -> ErrorFeedbackPointer | None:
    if not isinstance(value, Mapping):
        return None
    if value.get("endpoint") != "/v1/feedback" or value.get("method") != "POST":
        return None
    return {"endpoint": "/v1/feedback", "method": "POST"}
