from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, cast

import httpx

from ._version import __version__
from .errors import TyxterConnectionError, parse_api_error
from .resources import (
    AccountResource,
    AgentApiKeyDeviceAuthorizationsResource,
    AgenticPaymentsResource,
    AIAgentsResource,
    ApiKeysResource,
    AudiencesResource,
    AutomationRunsResource,
    AutomationsResource,
    AutomationWebhooksResource,
    BatchesResource,
    BillingResource,
    ContactsResource,
    DataRetentionResource,
    FeedbackResource,
    FiscalResource,
    FlowsResource,
    GroupsResource,
    InstagramMessagesResource,
    LLMResource,
    LLMRoutesResource,
    MediaResource,
    MessagesResource,
    MetaSignupSessionsResource,
    PaymentsResource,
    PhoneNumbersResource,
    ProjectsResource,
    ProviderConnectionsResource,
    ProviderCredentialSetupSessionsResource,
    RateCardsResource,
    SandboxResource,
    TemplatesResource,
    UsageResource,
    WebhookEndpointsResource,
    WebhookEventsResource,
    WhatsAppChannelsResource,
    WhatsAppMessagesResource,
)
from .types import QueryValue


class Tyxter:
    """Synchronous Tyxter API client.

    Resource surfaces are added incrementally in R5a. The core request layer is
    intentionally private so resources can keep a small public API.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.tyxter.com",
        timeout: float = 30.0,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        if not base_url:
            raise ValueError("base_url is required")
        if http_client is not None and transport is not None:
            raise ValueError("transport cannot be combined with http_client")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = http_client or httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
        )
        self._owns_client = http_client is None
        self.account = AccountResource(self)
        self.api_keys = ApiKeysResource(self)
        self.ai_agents = AIAgentsResource(self)
        self.agentic_payments = AgenticPaymentsResource(self)
        self.audiences = AudiencesResource(self)
        self.automations = AutomationsResource(self)
        self.automation_runs = AutomationRunsResource(self)
        self.automation_webhooks = AutomationWebhooksResource(self)
        self.messages = MessagesResource(self)
        self.whatsapp = WhatsAppMessagesResource(self.messages)
        self.instagram = InstagramMessagesResource(self.messages)
        # Deprecated: WhatsApp Channel publishing is unsupported and the API rejects its calls
        # with invalid_message_request. Kept so existing imports and error handling still work.
        self.whatsapp_channels = WhatsAppChannelsResource(self.messages)
        self.media = MediaResource(self)
        self.meta_signup_sessions = MetaSignupSessionsResource(self)
        self.payments = PaymentsResource(self)
        self.billing = BillingResource(self)
        self.phone_numbers = PhoneNumbersResource(self)
        self.projects = ProjectsResource(self)
        self.provider_connections = ProviderConnectionsResource(self)
        self.provider_credential_setup_sessions = ProviderCredentialSetupSessionsResource(self)
        self.rate_cards = RateCardsResource(self)
        self.batches = BatchesResource(self)
        self.contacts = ContactsResource(self)
        self.data_retention = DataRetentionResource(self)
        self.feedback = FeedbackResource(self)
        self.fiscal = FiscalResource(self)
        self.flows = FlowsResource(self)
        self.groups = GroupsResource(self)
        self.llm = LLMResource(self)
        self.llm_routes = LLMRoutesResource(self)
        self.webhook_endpoints = WebhookEndpointsResource(self)
        self.webhook_events = WebhookEventsResource(self)
        self.sandbox = SandboxResource(self)
        self.templates = TemplatesResource(self)
        self.usage = UsageResource(self)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Tyxter:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Mapping[str, object] | None = None,
        params: Mapping[str, QueryValue] | None = None,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> object:
        headers = self._headers(
            idempotency_key=idempotency_key,
            trace_id=trace_id,
            has_body=json is not None,
        )
        try:
            response = self._client.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                json=json,
                params=params,
            )
        except httpx.RequestError as exc:
            raise TyxterConnectionError(str(exc)) from exc

        body = self._parse_response(response)
        if response.is_error:
            raise parse_api_error(response.status_code, body)
        return body

    def _headers(
        self,
        *,
        idempotency_key: str | None,
        trace_id: str | None,
        has_body: bool,
    ) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"tyxter-python/{__version__}",
        }
        if has_body:
            headers["Content-Type"] = "application/json"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        if trace_id:
            headers["Tyxter-Trace-Id"] = trace_id
        return headers

    def _request_absolute(
        self,
        method: Literal["PUT"],
        url: str,
        *,
        content: bytes,
        headers: Mapping[str, str],
    ) -> httpx.Response:
        try:
            return self._client.request(method, url, content=content, headers=headers)
        except httpx.RequestError as exc:
            raise TyxterConnectionError(str(exc)) from exc

    def _parse_response(self, response: httpx.Response) -> object:
        if response.status_code == 204 or not response.content:
            return None

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type.lower():
            return response.text

        try:
            return cast(object, response.json())
        except ValueError:
            return response.text


class TyxterBootstrap:
    """Unauthenticated client for approving an agent API key by device flow."""

    def __init__(
        self,
        *,
        base_url: str = "https://api.tyxter.com",
        timeout: float = 30.0,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        if http_client is not None and transport is not None:
            raise ValueError("transport cannot be combined with http_client")
        self.base_url = base_url.rstrip("/")
        self._client = http_client or httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
        )
        self._owns_client = http_client is None
        self.agent_api_key_device_authorizations = AgentApiKeyDeviceAuthorizationsResource(self)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> TyxterBootstrap:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Mapping[str, object],
        trace_id: str | None,
    ) -> object:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"tyxter-python/{__version__}",
        }
        if trace_id:
            headers["Tyxter-Trace-Id"] = trace_id
        try:
            response = self._client.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                json=json,
            )
        except httpx.RequestError as exc:
            raise TyxterConnectionError(str(exc)) from exc

        if response.status_code == 204 or not response.content:
            body: object = None
        elif "application/json" in response.headers.get("content-type", "").lower():
            try:
                body = cast(object, response.json())
            except ValueError:
                body = response.text
        else:
            body = response.text
        if response.is_error:
            raise parse_api_error(response.status_code, body)
        return body
