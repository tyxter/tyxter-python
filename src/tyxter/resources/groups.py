from __future__ import annotations

from typing import cast

from tyxter.types import (
    CreateGroupEligibilityCheckRequest,
    CreateGroupRequest,
    GroupEligibilityResponse,
    GroupResponse,
    GroupStatus,
    ListGroupsResponse,
)

from ._base import Resource, path_id


class GroupsResource(Resource):
    """WhatsApp Business groups. Never personal WhatsApp groups.

    Every write is accepted asynchronously; none of these calls reaches Meta.
    """

    def retrieve_eligibility(self, *, phone_number_id: str) -> GroupEligibilityResponse:
        return cast(
            GroupEligibilityResponse,
            self._request(
                "GET",
                "/v1/groups/eligibility",
                params={"phone_number_id": phone_number_id},
            ),
        )

    def create_eligibility_check(
        self,
        payload: CreateGroupEligibilityCheckRequest,
        *,
        idempotency_key: str | None = None,
    ) -> GroupEligibilityResponse:
        return cast(
            GroupEligibilityResponse,
            self._request(
                "POST",
                "/v1/groups/eligibility-checks",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def create(
        self,
        payload: CreateGroupRequest,
        *,
        idempotency_key: str | None = None,
    ) -> GroupResponse:
        return cast(
            GroupResponse,
            self._request(
                "POST",
                "/v1/groups",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        phone_number_id: str | None = None,
        status: GroupStatus | None = None,
    ) -> ListGroupsResponse:
        return cast(
            ListGroupsResponse,
            self._request(
                "GET",
                "/v1/groups",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "phone_number_id": phone_number_id,
                    "status": status,
                },
            ),
        )

    def retrieve(self, group_id: str) -> GroupResponse:
        # The id is percent-encoded into one path segment, so a pasted personal
        # invite link reaches the API's 422 personal_whatsapp_group_not_supported.
        return cast(
            GroupResponse,
            self._request("GET", f"/v1/groups/{path_id('group_id', group_id)}"),
        )

    def delete(self, group_id: str, *, idempotency_key: str | None = None) -> GroupResponse:
        return cast(
            GroupResponse,
            self._request(
                "DELETE",
                f"/v1/groups/{path_id('group_id', group_id)}",
                idempotency_key=idempotency_key,
            ),
        )

    def reset_invite_link(
        self, group_id: str, *, idempotency_key: str | None = None
    ) -> GroupResponse:
        return cast(
            GroupResponse,
            self._request(
                "POST",
                f"/v1/groups/{path_id('group_id', group_id)}/invite-link/reset",
                idempotency_key=idempotency_key,
            ),
        )
