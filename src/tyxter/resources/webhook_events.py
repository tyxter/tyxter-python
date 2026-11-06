from __future__ import annotations

from typing import Literal, cast

from tyxter.types import (
    BulkResendWebhookEventsRequest,
    BulkResendWebhookEventsResponse,
    CreateWebhookListenSessionRequest,
    ListenWebhookEventsResponse,
    ListWebhookEventsResponse,
    WebhookDeliveryAttempt,
    WebhookEventResponse,
    WebhookEventStatus,
    WebhookListenSessionResponse,
)

from ._base import Resource, path_id


class WebhookEventsResource(Resource):
    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        event_type: str | None = None,
        event_types: str | None = None,
        webhook_endpoint_id: str | None = None,
        status: WebhookEventStatus | None = None,
    ) -> ListWebhookEventsResponse:
        return cast(
            ListWebhookEventsResponse,
            self._request(
                "GET",
                "/v1/webhook-events",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "event_type": event_type,
                    "event_types": event_types,
                    "webhook_endpoint_id": webhook_endpoint_id,
                    "status": status,
                },
            ),
        )

    def listen(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        start_at: Literal["oldest", "tail"] | None = None,
        event_type: str | None = None,
        event_types: str | None = None,
        wait_ms: int | None = None,
        webhook_endpoint_id: str | None = None,
        listen_session_id: str | None = None,
    ) -> ListenWebhookEventsResponse:
        return cast(
            ListenWebhookEventsResponse,
            self._request(
                "GET",
                "/v1/webhook-events/listen",
                params={
                    "limit": limit,
                    "cursor": cursor,
                    "start_at": start_at,
                    "event_type": event_type,
                    "event_types": event_types,
                    "wait_ms": wait_ms,
                    "webhook_endpoint_id": webhook_endpoint_id,
                    "listen_session_id": listen_session_id,
                },
            ),
        )

    def create_listen_session(
        self,
        payload: CreateWebhookListenSessionRequest | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> WebhookListenSessionResponse:
        return cast(
            WebhookListenSessionResponse,
            self._request(
                "POST",
                "/v1/webhook-events/listen-sessions",
                json=payload or {},
                idempotency_key=idempotency_key,
            ),
        )

    def disable_listen_session(self, listen_session_id: str) -> WebhookListenSessionResponse:
        return cast(
            WebhookListenSessionResponse,
            self._request(
                "DELETE",
                "/v1/webhook-events/listen-sessions/"
                f"{path_id('listen_session_id', listen_session_id)}",
            ),
        )

    def retrieve_listen_event(
        self,
        outbox_event_id: str,
        *,
        webhook_endpoint_id: str | None = None,
        listen_session_id: str | None = None,
    ) -> WebhookEventResponse:
        return cast(
            WebhookEventResponse,
            self._request(
                "GET",
                f"/v1/webhook-events/listen/{path_id('outbox_event_id', outbox_event_id)}",
                params={
                    "webhook_endpoint_id": webhook_endpoint_id,
                    "listen_session_id": listen_session_id,
                },
            ),
        )

    def retrieve(self, webhook_event_id: str) -> WebhookEventResponse:
        return cast(
            WebhookEventResponse,
            self._request(
                "GET",
                f"/v1/webhook-events/{path_id('webhook_event_id', webhook_event_id)}",
            ),
        )

    def resend(
        self,
        webhook_event_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> WebhookDeliveryAttempt:
        return cast(
            WebhookDeliveryAttempt,
            self._request(
                "POST",
                f"/v1/webhook-events/{path_id('webhook_event_id', webhook_event_id)}/resend",
                idempotency_key=idempotency_key,
            ),
        )

    def bulk_resend(
        self,
        payload: BulkResendWebhookEventsRequest,
        *,
        idempotency_key: str | None = None,
    ) -> BulkResendWebhookEventsResponse:
        return cast(
            BulkResendWebhookEventsResponse,
            self._request(
                "POST",
                "/v1/webhook-events/bulk-resend",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )
