from __future__ import annotations

from typing import cast

from tyxter.types import (
    CompleteSalvyPhoneRegistrationRequest,
    ConnectPhoneNumberRequest,
    CreateMetaDiagnosticsCheckRequest,
    CreatePhoneNumberOrderRequest,
    ImportSalvyPhoneNumberRequest,
    ListAvailableRegionsResponse,
    ListPhoneNumbersResponse,
    MetaDiagnosticsResponse,
    PhoneNumberOrderResponse,
    PhoneNumberResponse,
    PhoneNumberStatus,
    ProvisionPhoneNumberRequest,
    TransferPhoneNumberRequest,
)

from ._base import Resource, path_id, required_idempotency_key


class PhoneNumbersResource(Resource):
    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: PhoneNumberStatus | None = None,
    ) -> ListPhoneNumbersResponse:
        return cast(
            ListPhoneNumbersResponse,
            self._request(
                "GET",
                "/v1/phone-numbers",
                params={"limit": limit, "starting_after": starting_after, "status": status},
            ),
        )

    def retrieve(self, phone_number_id: str) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "GET", f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}"
            ),
        )

    def request_meta_diagnostics(
        self,
        phone_number_id: str,
        payload: CreateMetaDiagnosticsCheckRequest | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> MetaDiagnosticsResponse:
        return cast(
            MetaDiagnosticsResponse,
            self._request(
                "POST",
                f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}/meta-diagnostics",
                json=payload or {},
                idempotency_key=idempotency_key,
            ),
        )

    def get_meta_diagnostics(self, phone_number_id: str) -> MetaDiagnosticsResponse:
        return cast(
            MetaDiagnosticsResponse,
            self._request(
                "GET",
                f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}/meta-diagnostics",
            ),
        )

    def provision(
        self,
        payload: ProvisionPhoneNumberRequest,
        *,
        idempotency_key: str | None = None,
    ) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                "/v1/phone-numbers/provision",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def create_order(
        self,
        payload: CreatePhoneNumberOrderRequest,
        *,
        idempotency_key: str | None = None,
    ) -> PhoneNumberOrderResponse:
        return cast(
            PhoneNumberOrderResponse,
            self._request(
                "POST",
                "/v1/phone-numbers/orders",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def retrieve_order(self, order_id: str) -> PhoneNumberOrderResponse:
        return cast(
            PhoneNumberOrderResponse,
            self._request("GET", f"/v1/phone-numbers/orders/{path_id('order_id', order_id)}"),
        )

    def connect(
        self,
        payload: ConnectPhoneNumberRequest,
        *,
        idempotency_key: str | None = None,
    ) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                "/v1/phone-numbers/connect",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def import_salvy(
        self,
        payload: ImportSalvyPhoneNumberRequest,
        *,
        idempotency_key: str,
    ) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                "/v1/phone-numbers/import-salvy",
                json=payload,
                idempotency_key=required_idempotency_key(idempotency_key),
            ),
        )

    def complete_salvy_registration(
        self,
        phone_number_id: str,
        payload: CompleteSalvyPhoneRegistrationRequest,
        *,
        idempotency_key: str,
    ) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}"
                "/salvy/complete-registration",
                json=payload,
                idempotency_key=required_idempotency_key(idempotency_key),
            ),
        )

    def convert_to_byon(self, phone_number_id: str, *, idempotency_key: str) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}/convert-to-byon",
                json={},
                idempotency_key=required_idempotency_key(idempotency_key),
            ),
        )

    def disconnect(self, phone_number_id: str) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "DELETE", f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}"
            ),
        )

    def release(
        self, phone_number_id: str, *, idempotency_key: str | None = None
    ) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}/release",
                idempotency_key=idempotency_key,
            ),
        )

    def transfer(
        self,
        phone_number_id: str,
        payload: TransferPhoneNumberRequest,
        *,
        idempotency_key: str | None = None,
    ) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}/transfer",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list_available_regions(self) -> ListAvailableRegionsResponse:
        return cast(
            ListAvailableRegionsResponse,
            self._request("GET", "/v1/phone-numbers/available-regions"),
        )
