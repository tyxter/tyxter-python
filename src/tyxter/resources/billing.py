from __future__ import annotations

from typing import cast

from typing_extensions import deprecated

from tyxter.types import (
    AutoTopupConfigResponse,
    BillingPackageStatus,
    BillingPaymentMethodResponse,
    BillingPaymentMethodSetupIntentResponse,
    ChangePlanRequest,
    CreditBalanceResponse,
    CurrentPlanResponse,
    Environment,
    InvoiceDownloadResponse,
    ListBillingPackagesResponse,
    ListBillingPaymentMethodsResponse,
    ListInvoicesResponse,
    ListLedgerEntriesResponse,
    ListPhoneManagementResponse,
    ListPhoneRenewalsResponse,
    ListPlansResponse,
    PhoneRenewalResponse,
    PhoneRenewalStatus,
    PurchaseBillingPackageRequest,
    SaveBillingPaymentMethodRequest,
    SubscribePlanRequest,
    SubscribePlanResponse,
    TopupResponse,
    UpdateAutoTopupConfigRequest,
)

from ._base import Resource, path_id

_PHONE_RENEWALS_DEPRECATION = (
    "Phone renewal history is retired: no new cycle is recorded. Read `renewal` on "
    "phone_numbers.list() or phone_numbers.retrieve() for each number's current month."
)


class BillingResource(Resource):
    def balance(self) -> CreditBalanceResponse:
        return cast(CreditBalanceResponse, self._request("GET", "/v1/billing/balance"))

    def list_plans(self) -> ListPlansResponse:
        return cast(ListPlansResponse, self._request("GET", "/v1/billing/plans"))

    def current_plan(self) -> CurrentPlanResponse:
        return cast(CurrentPlanResponse, self._request("GET", "/v1/billing/plan"))

    def subscribe_plan(
        self, payload: SubscribePlanRequest, *, idempotency_key: str | None = None
    ) -> SubscribePlanResponse:
        return cast(
            SubscribePlanResponse,
            self._request(
                "POST",
                "/v1/billing/plan/subscribe",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def change_plan(
        self, payload: ChangePlanRequest, *, idempotency_key: str | None = None
    ) -> CurrentPlanResponse:
        return cast(
            CurrentPlanResponse,
            self._request(
                "POST",
                "/v1/billing/plan/change",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def cancel_plan(self, *, idempotency_key: str | None = None) -> CurrentPlanResponse:
        return cast(
            CurrentPlanResponse,
            self._request("POST", "/v1/billing/plan/cancel", idempotency_key=idempotency_key),
        )

    def list_packages(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: BillingPackageStatus | None = None,
    ) -> ListBillingPackagesResponse:
        return cast(
            ListBillingPackagesResponse,
            self._request(
                "GET",
                "/v1/billing/packages",
                params={"limit": limit, "starting_after": starting_after, "status": status},
            ),
        )

    def purchase_package(
        self,
        payload: PurchaseBillingPackageRequest,
        *,
        idempotency_key: str | None = None,
    ) -> TopupResponse:
        return cast(
            TopupResponse,
            self._request(
                "POST",
                "/v1/billing/packages/purchase",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list_payment_methods(self) -> ListBillingPaymentMethodsResponse:
        return cast(
            ListBillingPaymentMethodsResponse,
            self._request("GET", "/v1/billing/payment-methods"),
        )

    def save_payment_method(
        self,
        payload: SaveBillingPaymentMethodRequest,
        *,
        idempotency_key: str | None = None,
    ) -> BillingPaymentMethodResponse:
        return cast(
            BillingPaymentMethodResponse,
            self._request(
                "POST",
                "/v1/billing/payment-methods",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def create_payment_method_setup_intent(
        self, *, idempotency_key: str | None = None
    ) -> BillingPaymentMethodSetupIntentResponse:
        return cast(
            BillingPaymentMethodSetupIntentResponse,
            self._request(
                "POST",
                "/v1/billing/payment-methods/setup-intent",
                idempotency_key=idempotency_key,
            ),
        )

    def set_default_payment_method(
        self, payment_method_id: str, *, idempotency_key: str | None = None
    ) -> BillingPaymentMethodResponse:
        return cast(
            BillingPaymentMethodResponse,
            self._request(
                "POST",
                "/v1/billing/payment-methods/"
                f"{path_id('payment_method_id', payment_method_id)}/default",
                idempotency_key=idempotency_key,
            ),
        )

    def delete_payment_method(
        self, payment_method_id: str, *, idempotency_key: str | None = None
    ) -> BillingPaymentMethodResponse:
        return cast(
            BillingPaymentMethodResponse,
            self._request(
                "DELETE",
                f"/v1/billing/payment-methods/{path_id('payment_method_id', payment_method_id)}",
                idempotency_key=idempotency_key,
            ),
        )

    def retrieve_auto_topup(self) -> AutoTopupConfigResponse:
        return cast(AutoTopupConfigResponse, self._request("GET", "/v1/billing/auto-topup"))

    def update_auto_topup(
        self,
        payload: UpdateAutoTopupConfigRequest,
        *,
        idempotency_key: str | None = None,
    ) -> AutoTopupConfigResponse:
        return cast(
            AutoTopupConfigResponse,
            self._request(
                "PUT",
                "/v1/billing/auto-topup",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list_ledger(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        environment: Environment | None = None,
        source_type: str | None = None,
    ) -> ListLedgerEntriesResponse:
        return cast(
            ListLedgerEntriesResponse,
            self._request(
                "GET",
                "/v1/billing/ledger",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "environment": environment,
                    "source_type": source_type,
                },
            ),
        )

    def list_invoices(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        project_id: str | None = None,
    ) -> ListInvoicesResponse:
        return cast(
            ListInvoicesResponse,
            self._request(
                "GET",
                "/v1/invoices",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "project_id": project_id,
                },
            ),
        )

    @deprecated(_PHONE_RENEWALS_DEPRECATION)
    def list_phone_renewals(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: PhoneRenewalStatus | None = None,
    ) -> ListPhoneRenewalsResponse:
        """Deprecated: list renewal cycles recorded by the retired prepaid renewal design.

        The route keeps answering, but no new cycle is recorded. Read ``renewal`` on
        ``phone_numbers.list()`` / ``phone_numbers.retrieve()`` instead. No removal date is set.
        """
        return cast(
            ListPhoneRenewalsResponse,
            self._request(
                "GET",
                "/v1/billing/phone-renewals",
                params={"limit": limit, "starting_after": starting_after, "status": status},
            ),
        )

    @deprecated(_PHONE_RENEWALS_DEPRECATION)
    def retrieve_phone_renewal(self, cycle_id: str) -> PhoneRenewalResponse:
        """Deprecated: read ``renewal`` on ``phone_numbers.retrieve()`` instead."""
        return cast(
            PhoneRenewalResponse,
            self._request(
                "GET",
                f"/v1/billing/phone-renewals/{path_id('cycle_id', cycle_id)}",
            ),
        )

    def list_phone_management(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
    ) -> ListPhoneManagementResponse:
        return cast(
            ListPhoneManagementResponse,
            self._request(
                "GET",
                "/v1/billing/phone-management",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def download_invoice(self, invoice_id: str) -> InvoiceDownloadResponse:
        return cast(
            InvoiceDownloadResponse,
            self._request("GET", f"/v1/invoices/{path_id('invoice_id', invoice_id)}/download"),
        )
