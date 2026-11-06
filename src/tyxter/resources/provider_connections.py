from __future__ import annotations

from typing import cast

from tyxter.types import (
    CreateProviderCredentialSetupSessionRequest,
    DeleteProviderConnectionResponse,
    ExchangeMetaOAuthCodeRequest,
    ListProviderConnectionsResponse,
    ListSalvyNumbersResponse,
    MetaConnectionMutationResponse,
    MetaOnboardingConfigResponse,
    ProviderConnectionResponse,
    ProviderConnectionStatusResponse,
    ProviderCredentialSetupSessionResponse,
    ProviderCredentialSetupSessionResult,
    RegisterSalvyConnectionRequest,
    RotateSalvyConnectionRequest,
)

from ._base import Resource, path_id, required_idempotency_key


class ProviderCredentialSetupSessionsResource(Resource):
    def create(
        self,
        payload: CreateProviderCredentialSetupSessionRequest,
        *,
        idempotency_key: str | None = None,
    ) -> ProviderCredentialSetupSessionResponse:
        return cast(
            ProviderCredentialSetupSessionResponse,
            self._request(
                "POST",
                "/v1/provider-credential-setup-sessions",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def create_result(
        self,
        payload: CreateProviderCredentialSetupSessionRequest,
        *,
        idempotency_key: str | None = None,
    ) -> ProviderCredentialSetupSessionResult:
        return cast(
            ProviderCredentialSetupSessionResult,
            self.create(payload, idempotency_key=idempotency_key),
        )

    def retrieve(self, request_id: str) -> ProviderCredentialSetupSessionResponse:
        return cast(
            ProviderCredentialSetupSessionResponse,
            self._request(
                "GET",
                f"/v1/provider-credential-setup-sessions/{path_id('request_id', request_id)}",
            ),
        )

    def retrieve_result(self, request_id: str) -> ProviderCredentialSetupSessionResult:
        return cast(ProviderCredentialSetupSessionResult, self.retrieve(request_id))


class ProviderConnectionsResource(Resource):
    def list(
        self, *, limit: int | None = None, starting_after: str | None = None
    ) -> ListProviderConnectionsResponse:
        return cast(
            ListProviderConnectionsResponse,
            self._request(
                "GET",
                "/v1/provider-connections",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def status(self) -> ProviderConnectionStatusResponse:
        return cast(
            ProviderConnectionStatusResponse,
            self._request("GET", "/v1/provider-connections/status"),
        )

    def meta_onboarding(self) -> MetaOnboardingConfigResponse:
        return cast(
            MetaOnboardingConfigResponse,
            self._request("GET", "/v1/provider-connections/meta/onboarding"),
        )

    def exchange_meta_oauth(
        self,
        payload: ExchangeMetaOAuthCodeRequest,
        *,
        idempotency_key: str | None = None,
    ) -> MetaConnectionMutationResponse:
        """Accept a Facebook JS SDK OAuth code; the API answers ``202``.

        The response is the connection with its ``operation`` (``kind``
        ``"meta_oauth_exchange"``) ``queued``. Tyxter sends the single-use code to Meta at most
        once and completes Embedded Signup after the response. Sending the same code again
        while its exchange is queued returns that exchange's connection; a different code
        replaces it. Poll ``retrieve(connection["id"])`` until ``operation["state"]`` is
        ``"succeeded"`` (the connection is ``connected``) or ``"failed"``
        (``operation["error_code"]`` is the stable code, such as ``meta_oauth_exchange_failed``
        or ``meta_payment_method_required``; ``meta_oauth_exchange_unavailable`` means a new
        signup is needed), or until ``operation`` is ``None``. Refusals that need no Meta call
        still raise ``TyxterAPIError``. Reusing the idempotency key returns the stored ``202``
        body. ``warnings`` covers only a ``display_name`` the request supplied.
        """
        return cast(
            MetaConnectionMutationResponse,
            self._request(
                "POST",
                "/v1/provider-connections/meta/oauth",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def complete_meta_registration(
        self,
        connection_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> MetaConnectionMutationResponse:
        """Finish a Meta connection left ``pending`` after its access token was brokered.

        The API answers ``202`` with the still-``pending`` connection and its ``operation``
        (``kind`` ``"meta_registration_completion"``) ``queued``; Tyxter re-runs the remaining
        provider steps from the stored credentials afterwards. Poll
        ``retrieve(connection_id)`` until ``operation["state"]`` is ``"succeeded"`` or
        ``"failed"`` (the connection stays ``pending`` and can be completed again once the
        cause is fixed), until ``operation["kind"]`` changes (a newer credential operation
        replaced it), or until ``operation`` is ``None``. Calling it again while a completion is
        queued returns that one. Refusals that need no Meta call still raise
        ``TyxterAPIError``. Reusing the idempotency key returns the stored ``202`` body.
        """
        return cast(
            MetaConnectionMutationResponse,
            self._request(
                "POST",
                f"/v1/provider-connections/{path_id('connection_id', connection_id)}"
                "/meta/complete-registration",
                idempotency_key=idempotency_key,
            ),
        )

    def retrieve(self, connection_id: str) -> ProviderConnectionResponse:
        """Read one connection, including the ``operation`` of an asynchronous connect."""
        return cast(
            ProviderConnectionResponse,
            self._request(
                "GET",
                f"/v1/provider-connections/{path_id('connection_id', connection_id)}",
            ),
        )

    def register_salvy(
        self,
        payload: RegisterSalvyConnectionRequest,
        *,
        idempotency_key: str,
    ) -> ProviderConnectionResponse:
        return cast(
            ProviderConnectionResponse,
            self._request(
                "POST",
                "/v1/provider-connections/salvy",
                json=payload,
                idempotency_key=required_idempotency_key(idempotency_key),
            ),
        )

    def rotate_salvy(
        self,
        connection_id: str,
        payload: RotateSalvyConnectionRequest,
        *,
        idempotency_key: str,
    ) -> ProviderConnectionResponse:
        return cast(
            ProviderConnectionResponse,
            self._request(
                "POST",
                f"/v1/provider-connections/{path_id('connection_id', connection_id)}/salvy/rotate",
                json=payload,
                idempotency_key=required_idempotency_key(idempotency_key),
            ),
        )

    def refresh_salvy_discovery(
        self,
        connection_id: str,
        *,
        idempotency_key: str,
    ) -> ProviderConnectionResponse:
        return cast(
            ProviderConnectionResponse,
            self._request(
                "POST",
                f"/v1/provider-connections/{path_id('connection_id', connection_id)}"
                "/salvy/discovery",
                json={},
                idempotency_key=required_idempotency_key(idempotency_key),
            ),
        )

    def list_salvy_numbers(
        self,
        connection_id: str,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
    ) -> ListSalvyNumbersResponse:
        return cast(
            ListSalvyNumbersResponse,
            self._request(
                "GET",
                f"/v1/provider-connections/{path_id('connection_id', connection_id)}/salvy/numbers",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def delete(self, connection_id: str) -> DeleteProviderConnectionResponse:
        return cast(
            DeleteProviderConnectionResponse,
            self._request(
                "DELETE",
                f"/v1/provider-connections/{path_id('connection_id', connection_id)}",
            ),
        )
