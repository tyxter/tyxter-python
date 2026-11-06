from __future__ import annotations

from typing import cast

from tyxter.types import (
    AIAgentCompletionRequest,
    AIAgentCompletionResponse,
    AIAgentResponse,
    CreateAIAgentRequest,
    DeleteAIAgentResponse,
    ListAIAgentPromptVersionsResponse,
    ListAIAgentResponseLogsResponse,
    ListAIAgentsResponse,
    UpdateAIAgentRequest,
)

from ._base import Resource, path_id


class AIAgentsResource(Resource):
    def create(
        self, payload: CreateAIAgentRequest, *, idempotency_key: str | None = None
    ) -> AIAgentResponse:
        return cast(
            AIAgentResponse,
            self._request("POST", "/v1/ai-agents", json=payload, idempotency_key=idempotency_key),
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        include_archived: bool | None = None,
    ) -> ListAIAgentsResponse:
        return cast(
            ListAIAgentsResponse,
            self._request(
                "GET",
                "/v1/ai-agents",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "include_archived": include_archived,
                },
            ),
        )

    def retrieve(self, agent_id: str) -> AIAgentResponse:
        return cast(
            AIAgentResponse,
            self._request("GET", f"/v1/ai-agents/{path_id('agent_id', agent_id)}"),
        )

    def update(
        self,
        agent_id: str,
        payload: UpdateAIAgentRequest,
        *,
        idempotency_key: str | None = None,
    ) -> AIAgentResponse:
        return cast(
            AIAgentResponse,
            self._request(
                "PATCH",
                f"/v1/ai-agents/{path_id('agent_id', agent_id)}",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def delete(self, agent_id: str) -> DeleteAIAgentResponse:
        return cast(
            DeleteAIAgentResponse,
            self._request("DELETE", f"/v1/ai-agents/{path_id('agent_id', agent_id)}"),
        )

    def complete(
        self,
        agent_id: str,
        payload: AIAgentCompletionRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> AIAgentCompletionResponse:
        return cast(
            AIAgentCompletionResponse,
            self._request(
                "POST",
                f"/v1/ai-agents/{path_id('agent_id', agent_id)}/completions",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def list_prompt_versions(
        self,
        agent_id: str,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
    ) -> ListAIAgentPromptVersionsResponse:
        return cast(
            ListAIAgentPromptVersionsResponse,
            self._request(
                "GET",
                f"/v1/ai-agents/{path_id('agent_id', agent_id)}/prompt-versions",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def list_response_logs(
        self,
        agent_id: str,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
    ) -> ListAIAgentResponseLogsResponse:
        return cast(
            ListAIAgentResponseLogsResponse,
            self._request(
                "GET",
                f"/v1/ai-agents/{path_id('agent_id', agent_id)}/response-logs",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )
