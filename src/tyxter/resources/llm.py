from __future__ import annotations

from typing import cast

from tyxter.types import (
    DeleteLLMRouteResponse,
    ListLLMResponseLogsResponse,
    ListLLMRoutePromptVersionsResponse,
    LLMCompletionRequest,
    LLMCompletionResponse,
    LLMRouteResponse,
    UpdateLLMRouteRequest,
    UpsertLLMRouteRequest,
)

from ._base import Resource


class LLMRoutesResource(Resource):
    def upsert(
        self, payload: UpsertLLMRouteRequest, *, idempotency_key: str | None = None
    ) -> LLMRouteResponse:
        return cast(
            LLMRouteResponse,
            self._request("PUT", "/v1/llm-routes", json=payload, idempotency_key=idempotency_key),
        )

    def retrieve(self, *, phone_number_id: str | None = None) -> LLMRouteResponse:
        return cast(
            LLMRouteResponse,
            self._request("GET", "/v1/llm-routes", params={"phone_number_id": phone_number_id}),
        )

    def update(
        self,
        payload: UpdateLLMRouteRequest,
        *,
        phone_number_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> LLMRouteResponse:
        return cast(
            LLMRouteResponse,
            self._request(
                "PATCH",
                "/v1/llm-routes",
                json=payload,
                params={"phone_number_id": phone_number_id},
                idempotency_key=idempotency_key,
            ),
        )

    def list_prompt_versions(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        phone_number_id: str | None = None,
    ) -> ListLLMRoutePromptVersionsResponse:
        return cast(
            ListLLMRoutePromptVersionsResponse,
            self._request(
                "GET",
                "/v1/llm-routes/prompt-versions",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "phone_number_id": phone_number_id,
                },
            ),
        )

    def delete(
        self,
        *,
        phone_number_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> DeleteLLMRouteResponse:
        return cast(
            DeleteLLMRouteResponse,
            self._request(
                "DELETE",
                "/v1/llm-routes",
                params={"phone_number_id": phone_number_id},
                idempotency_key=idempotency_key,
            ),
        )


class LLMResource(Resource):
    def complete(
        self,
        payload: LLMCompletionRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> LLMCompletionResponse:
        return cast(
            LLMCompletionResponse,
            self._request(
                "POST",
                "/v1/llm/completions",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def list_responses(
        self, *, limit: int | None = None, starting_after: str | None = None
    ) -> ListLLMResponseLogsResponse:
        return cast(
            ListLLMResponseLogsResponse,
            self._request(
                "GET",
                "/v1/llm/responses",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )
