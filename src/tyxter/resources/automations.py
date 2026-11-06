from __future__ import annotations

from typing import cast

from tyxter.types import (
    AutomationResponse,
    AutomationRunResponse,
    AutomationRunStatus,
    AutomationStatus,
    AutomationVersionResponse,
    AutomationWebhookInput,
    AutomationWebhookSecretResponse,
    CreateAutomationRequest,
    CreateAutomationRunRequest,
    CreateAutomationVersionRequest,
    DeleteAutomationResponse,
    ListAutomationRunsResponse,
    ListAutomationsResponse,
    ListAutomationStepRunsResponse,
    ListAutomationVersionsResponse,
    PublishAutomationRequest,
    UpdateAutomationRequest,
)

from ._base import Resource, path_id


class AutomationsResource(Resource):
    def create(
        self, payload: CreateAutomationRequest, *, idempotency_key: str | None = None
    ) -> AutomationResponse:
        return cast(
            AutomationResponse,
            self._request("POST", "/v1/automations", json=payload, idempotency_key=idempotency_key),
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: AutomationStatus | None = None,
    ) -> ListAutomationsResponse:
        return cast(
            ListAutomationsResponse,
            self._request(
                "GET",
                "/v1/automations",
                params={"limit": limit, "starting_after": starting_after, "status": status},
            ),
        )

    def retrieve(self, automation_id: str) -> AutomationResponse:
        return cast(
            AutomationResponse,
            self._request("GET", f"/v1/automations/{path_id('automation_id', automation_id)}"),
        )

    def update(
        self,
        automation_id: str,
        payload: UpdateAutomationRequest,
        *,
        idempotency_key: str | None = None,
    ) -> AutomationResponse:
        return cast(
            AutomationResponse,
            self._request(
                "PATCH",
                f"/v1/automations/{path_id('automation_id', automation_id)}",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def delete(self, automation_id: str) -> DeleteAutomationResponse:
        return cast(
            DeleteAutomationResponse,
            self._request("DELETE", f"/v1/automations/{path_id('automation_id', automation_id)}"),
        )

    def create_version(
        self,
        automation_id: str,
        payload: CreateAutomationVersionRequest,
        *,
        idempotency_key: str | None = None,
    ) -> AutomationVersionResponse:
        return cast(
            AutomationVersionResponse,
            self._request(
                "POST",
                f"/v1/automations/{path_id('automation_id', automation_id)}/versions",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list_versions(
        self,
        automation_id: str,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
    ) -> ListAutomationVersionsResponse:
        return cast(
            ListAutomationVersionsResponse,
            self._request(
                "GET",
                f"/v1/automations/{path_id('automation_id', automation_id)}/versions",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def publish(
        self,
        automation_id: str,
        payload: PublishAutomationRequest,
        *,
        idempotency_key: str | None = None,
    ) -> AutomationResponse:
        return cast(
            AutomationResponse,
            self._request(
                "POST",
                f"/v1/automations/{path_id('automation_id', automation_id)}/publish",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def pause(
        self,
        automation_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> AutomationResponse:
        return cast(
            AutomationResponse,
            self._request(
                "POST",
                f"/v1/automations/{path_id('automation_id', automation_id)}/pause",
                idempotency_key=idempotency_key,
            ),
        )

    def resume(
        self,
        automation_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> AutomationResponse:
        return cast(
            AutomationResponse,
            self._request(
                "POST",
                f"/v1/automations/{path_id('automation_id', automation_id)}/resume",
                idempotency_key=idempotency_key,
            ),
        )

    def rotate_webhook_secret(
        self,
        automation_id: str,
        slug: str,
        *,
        idempotency_key: str | None = None,
    ) -> AutomationWebhookSecretResponse:
        return cast(
            AutomationWebhookSecretResponse,
            self._request(
                "POST",
                f"/v1/automations/{path_id('automation_id', automation_id)}"
                f"/webhook-triggers/{path_id('slug', slug)}/rotate-secret",
                idempotency_key=idempotency_key,
            ),
        )

    def create_run(
        self,
        automation_id: str,
        payload: CreateAutomationRunRequest | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> AutomationRunResponse:
        return cast(
            AutomationRunResponse,
            self._request(
                "POST",
                f"/v1/automations/{path_id('automation_id', automation_id)}/runs",
                json=payload or {},
                idempotency_key=idempotency_key,
            ),
        )

    def list_runs(
        self,
        automation_id: str,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: AutomationRunStatus | None = None,
    ) -> ListAutomationRunsResponse:
        return cast(
            ListAutomationRunsResponse,
            self._request(
                "GET",
                f"/v1/automations/{path_id('automation_id', automation_id)}/runs",
                params={"limit": limit, "starting_after": starting_after, "status": status},
            ),
        )


class AutomationRunsResource(Resource):
    def retrieve(self, run_id: str) -> AutomationRunResponse:
        return cast(
            AutomationRunResponse,
            self._request("GET", f"/v1/automation-runs/{path_id('run_id', run_id)}"),
        )

    def list_steps(
        self,
        run_id: str,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
    ) -> ListAutomationStepRunsResponse:
        return cast(
            ListAutomationStepRunsResponse,
            self._request(
                "GET",
                f"/v1/automation-runs/{path_id('run_id', run_id)}/steps",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def cancel(self, run_id: str, *, idempotency_key: str | None = None) -> AutomationRunResponse:
        return cast(
            AutomationRunResponse,
            self._request(
                "POST",
                f"/v1/automation-runs/{path_id('run_id', run_id)}/cancel",
                idempotency_key=idempotency_key,
            ),
        )


class AutomationWebhooksResource(Resource):
    def invoke(
        self,
        slug: str,
        payload: AutomationWebhookInput | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> AutomationRunResponse:
        return cast(
            AutomationRunResponse,
            self._request(
                "POST",
                f"/v1/automation-webhooks/{path_id('slug', slug)}",
                json=payload or {},
                idempotency_key=idempotency_key,
            ),
        )
