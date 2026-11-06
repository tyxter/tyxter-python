from __future__ import annotations

from typing import cast

from tyxter.types import (
    APIKeyResponse,
    CreateApiKeyRequest,
    CreateApiKeyResponse,
    ListApiKeysResponse,
    RenameApiKeyRequest,
    RotateApiKeyResponse,
)

from ._base import Resource, path_id


class ApiKeysResource(Resource):
    def create(
        self, payload: CreateApiKeyRequest, *, idempotency_key: str | None = None
    ) -> CreateApiKeyResponse:
        return cast(
            CreateApiKeyResponse,
            self._request(
                "POST",
                "/v1/api-keys",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list(
        self, *, limit: int | None = None, starting_after: str | None = None
    ) -> ListApiKeysResponse:
        return cast(
            ListApiKeysResponse,
            self._request(
                "GET",
                "/v1/api-keys",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def retrieve(self, api_key_id: str) -> APIKeyResponse:
        return cast(
            APIKeyResponse,
            self._request("GET", f"/v1/api-keys/{path_id('api_key_id', api_key_id)}"),
        )

    def rename(
        self,
        api_key_id: str,
        payload: RenameApiKeyRequest,
        *,
        idempotency_key: str | None = None,
    ) -> APIKeyResponse:
        return cast(
            APIKeyResponse,
            self._request(
                "PATCH",
                f"/v1/api-keys/{path_id('api_key_id', api_key_id)}",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def rotate(
        self, api_key_id: str, *, idempotency_key: str | None = None
    ) -> RotateApiKeyResponse:
        return cast(
            RotateApiKeyResponse,
            self._request(
                "POST",
                f"/v1/api-keys/{path_id('api_key_id', api_key_id)}/rotate",
                idempotency_key=idempotency_key,
            ),
        )

    def revoke(self, api_key_id: str) -> APIKeyResponse:
        return cast(
            APIKeyResponse,
            self._request("DELETE", f"/v1/api-keys/{path_id('api_key_id', api_key_id)}"),
        )
