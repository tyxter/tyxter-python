from __future__ import annotations

from typing import cast

from tyxter.types import (
    CreatePaymentRequest,
    ListPaymentsResponse,
    PaymentResponse,
    PaymentStatus,
    RequestPaymentApprovalRequest,
)

from ._base import Resource, path_id


class PaymentsResource(Resource):
    def create(
        self,
        payload: CreatePaymentRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> PaymentResponse:
        return cast(
            PaymentResponse,
            self._request(
                "POST",
                "/v1/payments",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: PaymentStatus | None = None,
    ) -> ListPaymentsResponse:
        return cast(
            ListPaymentsResponse,
            self._request(
                "GET",
                "/v1/payments",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "status": status,
                },
            ),
        )

    def retrieve(self, payment_id: str) -> PaymentResponse:
        return cast(
            PaymentResponse,
            self._request("GET", f"/v1/payments/{path_id('payment_id', payment_id)}"),
        )

    def cancel(
        self,
        payment_id: str,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> PaymentResponse:
        return cast(
            PaymentResponse,
            self._request(
                "POST",
                f"/v1/payments/{path_id('payment_id', payment_id)}/cancel",
                json={},
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def request_approval(
        self,
        payment_id: str,
        payload: RequestPaymentApprovalRequest | None = None,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> PaymentResponse:
        return cast(
            PaymentResponse,
            self._request(
                "POST",
                f"/v1/payments/{path_id('payment_id', payment_id)}/request-approval",
                json=payload or {},
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )
