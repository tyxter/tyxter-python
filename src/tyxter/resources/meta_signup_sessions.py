from __future__ import annotations

from typing import cast

from tyxter.types import CreateMetaSignupSessionRequest, MetaSignupSessionResponse

from ._base import Resource, path_id, required_idempotency_key


class MetaSignupSessionsResource(Resource):
    def create(
        self,
        payload: CreateMetaSignupSessionRequest,
        *,
        idempotency_key: str,
    ) -> MetaSignupSessionResponse:
        return cast(
            MetaSignupSessionResponse,
            self._request(
                "POST",
                "/v1/meta-signup-sessions",
                json=payload,
                idempotency_key=required_idempotency_key(idempotency_key),
            ),
        )

    def retrieve(self, session_id: str) -> MetaSignupSessionResponse:
        return cast(
            MetaSignupSessionResponse,
            self._request(
                "GET",
                f"/v1/meta-signup-sessions/{path_id('session_id', session_id)}",
            ),
        )
