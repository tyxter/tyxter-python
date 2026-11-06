from __future__ import annotations

from typing import TYPE_CHECKING, cast

from tyxter.types import (
    GroupResponse,
    InboundSandboxMessageRequest,
    MessageResponse,
    PaymentResponse,
    SandboxGroupParticipantRequest,
    SandboxLLMFailureRequest,
    SandboxLLMFailureResponse,
    SandboxPaymentStatusRequest,
    SandboxQuickstartResponse,
    SandboxTemplateStatusRequest,
    TemplateResponse,
)

from ._base import Resource, path_id

if TYPE_CHECKING:
    from tyxter.client import Tyxter


class SandboxInboundMessagesResource(Resource):
    def create(
        self,
        payload: InboundSandboxMessageRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return cast(
            MessageResponse,
            self._request(
                "POST",
                "/v1/sandbox/inbound-messages",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )


class SandboxTemplatesResource(Resource):
    def set_status(
        self,
        template_id: str,
        payload: SandboxTemplateStatusRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> TemplateResponse:
        return cast(
            TemplateResponse,
            self._request(
                "POST",
                f"/v1/sandbox/templates/{path_id('template_id', template_id)}/status",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )


class SandboxPaymentsResource(Resource):
    def set_status(
        self,
        payment_id: str,
        payload: SandboxPaymentStatusRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> PaymentResponse:
        return cast(
            PaymentResponse,
            self._request(
                "POST",
                f"/v1/sandbox/payments/{path_id('payment_id', payment_id)}/status",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )


class SandboxGroupsResource(Resource):
    def simulate_participant(
        self,
        group_id: str,
        payload: SandboxGroupParticipantRequest,
        *,
        idempotency_key: str | None = None,
    ) -> GroupResponse:
        return cast(
            GroupResponse,
            self._request(
                "POST",
                f"/v1/sandbox/groups/{path_id('group_id', group_id)}/participants",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )


class SandboxLLMResource(Resource):
    def set_failure(
        self,
        payload: SandboxLLMFailureRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> SandboxLLMFailureResponse:
        return cast(
            SandboxLLMFailureResponse,
            self._request(
                "POST",
                "/v1/sandbox/llm/failure",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )


class SandboxResource(Resource):
    def __init__(self, client: Tyxter) -> None:
        super().__init__(client)
        self.inbound_messages = SandboxInboundMessagesResource(self._client)
        self.templates = SandboxTemplatesResource(self._client)
        self.payments = SandboxPaymentsResource(self._client)
        self.groups = SandboxGroupsResource(self._client)
        self.llm = SandboxLLMResource(self._client)

    def quickstart(self) -> SandboxQuickstartResponse:
        return cast(
            SandboxQuickstartResponse,
            self._request("GET", "/v1/sandbox/quickstart"),
        )
