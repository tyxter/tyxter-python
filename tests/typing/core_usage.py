from __future__ import annotations

from typing import Literal

from typing_extensions import assert_type

from tyxter import Tyxter, TyxterAPIError
from tyxter.types import (
    AgenticPlatformDefaultStatus,
    CreateApiKeyRequest,
    CreateApiKeyResponse,
    CreateMessageRequest,
    CreateProjectRequest,
    CreateTemplateRequest,
    CreateWebhookEndpointResponse,
    CreditHardBlockEngagedWebhookEnvelope,
    CreditHardBlockTrigger,
    CreditToppedUpWebhookData,
    CreditToppedUpWebhookEnvelope,
    DisplayNameWarningCode,
    DuplicateTemplateRequest,
    ErrorDiscoveryPointer,
    EstimatedExternalMetaCost,
    EstimatedExternalMetaCostSummary,
    FlowRejectionCode,
    FlowResponse,
    GroupMessageReceivedWebhookEnvelope,
    GroupParticipantJoinedWebhookData,
    GroupParticipantRemovalInitiator,
    GroupParticipantWebhookEnvelope,
    GroupWebhookEnvelope,
    GroupWebhookStatus,
    InboundMessageMediaConsumed,
    InboundMessageMediaDescriptor,
    InboundMessageMediaFailed,
    InboundMessageMediaFailure,
    InboundUnknownDescriptor,
    InboundUnsupportedDescriptor,
    InstagramMediaMessageInput,
    LedgerEntryPaymentFee,
    LedgerEntryResponse,
    ListMediaAssetsResponse,
    ListMessagesResponse,
    ListPhoneRenewalsResponse,
    ListProjectsResponse,
    ListPublicFeedbackReportsResponse,
    MediaAssetDownloadResponse,
    MediaAssetResponse,
    MediaDownloadHint,
    MediaMessagePayload,
    MessageBatchPacingResponse,
    MessageBatchResponse,
    MessageContext,
    MessageDetailResponse,
    MessageMediaTranscribedWebhookData,
    MessageMediaTranscribedWebhookEnvelope,
    MessageMediaTranscribedWebhookTranscript,
    MessageMediaTranscriptionFailedWebhookData,
    MessageMediaTranscriptionFailedWebhookEnvelope,
    MessageMediaTranscriptionFailedWebhookTranscript,
    MessageMediaTranscriptionWebhookEnvelope,
    MessageMediaTranscriptResponse,
    MessageReactionReceivedWebhookEnvelope,
    MessageReadSenderIdentity,
    MessageResponse,
    MessageSummaryResponse,
    MetaConnectionMutationResponse,
    MetaDiagnosticsFailure,
    MetaDiagnosticsPhoneFacts,
    MetaDiagnosticsResponse,
    NativePixOrderDetailsMessagePayload,
    PaymentFeeCompletionState,
    PaymentResponse,
    PaymentWebhookEnvelope,
    PhoneLessInboundSenderIdentity,
    PhoneMessagingTier,
    PhoneNumberMutationResponse,
    PhoneNumberNameReviewResponse,
    PhoneNumberOrderPreviewCharge,
    PhoneNumberOrderResponse,
    PhoneNumberPendingNameReviewResponse,
    PhoneNumberReadResponse,
    PhoneNumberRentalApprovalOrder,
    PhoneNumberResponse,
    PhoneRenewalResponse,
    PhoneRenewalSummaryState,
    ProjectResponse,
    ProviderConnectionDisableScheduledWebhookData,
    ProviderConnectionDisableScheduledWebhookEnvelope,
    ProviderConnectionOperationErrorCode,
    ProviderConnectionPolicyWarningWebhookData,
    ProviderConnectionPolicyWarningWebhookEnvelope,
    ProviderConnectionResponse,
    ProviderConnectionSendBlockCode,
    ProviderConnectionSendCapability,
    ProviderConnectionWabaSendCapability,
    ProviderCredentialSetupSessionCompletedOpenAISttResult,
    ProviderCredentialSetupSessionResponse,
    ProviderCredentialSetupSessionResult,
    ProviderCredentialSetupSttProvider,
    PublicFeedbackReportResponse,
    PurchaseBillingPackageRequest,
    RequestMessageMediaTranscription,
    RotateWebhookSigningSecretResponse,
    SandboxDefaultTemplate,
    SendMediaMessageInput,
    ServiceWindowRequiredDetails,
    ServiceWindowRequiredReason,
    TemplateGenerationRequest,
    TemplateGenerationResponse,
    TemplateParameterFormat,
    TemplateResponse,
    TestWebhookEndpointResponse,
    TopupPaymentMethodKind,
    TopupResponse,
    TypingIndicatorResponse,
    TyxterErrorBody,
    TyxterWireErrorBody,
    UpdateTemplateRequest,
    WebhookEndpointResponse,
    WebhookListenSessionConflictDetails,
    WhatsAppGroupRecipientIdentity,
)


def core_usage(client: Tyxter) -> None:
    request: CreateMessageRequest = {
        "channel": "whatsapp",
        "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
        "recipient": {"type": "phone_e164", "id": "+15555550100"},
        "message": {"type": "text", "text": {"body": "hello"}},
    }

    assert_type(client.messages.create(request), MessageResponse)
    assert_type(client.messages.list(status="sent"), ListMessagesResponse)
    assert_type(
        client.messages.list(direction="inbound", include="payload"),
        ListMessagesResponse,
    )
    assert_type(client.messages.retrieve("msg_123"), MessageDetailResponse)
    assert_type(client.messages.cancel("msg_123"), MessageDetailResponse)

    transcription: RequestMessageMediaTranscription = {"language": "pt"}
    assert_type(
        client.messages.request_transcription("msg_123", transcription),
        MessageMediaTranscriptResponse,
    )
    assert_type(
        client.messages.retrieve_transcription("msg_123"),
        MessageMediaTranscriptResponse,
    )
    assert_type(client.messages.typing("msg_123"), TypingIndicatorResponse)
    assert_type(client.media.list(source="inbound_provider"), ListMediaAssetsResponse)
    assert_type(client.media.create_download_url("mda_123"), MediaAssetDownloadResponse)
    assert_type(
        client.provider_credential_setup_sessions.create({"target": "openai.stt"}),
        ProviderCredentialSetupSessionResponse,
    )
    setup_result = client.provider_credential_setup_sessions.create_result({"target": "openai.stt"})
    assert_type(
        setup_result,
        ProviderCredentialSetupSessionResult,
    )
    retrieved_setup_result = client.provider_credential_setup_sessions.retrieve_result("pcs_123")
    assert_type(retrieved_setup_result, ProviderCredentialSetupSessionResult)
    provider_credential_setup_result_narrowing(setup_result)
    provider_credential_setup_result_narrowing(retrieved_setup_result)

    order_details: NativePixOrderDetailsMessagePayload = {
        "type": "order_details",
        "body": {"text": "Review your order"},
        "action": {
            "name": "review_and_pay",
            "parameters": {
                "reference_id": "order_123",
                "type": "physical-goods",
                "payment_type": "br",
                "payment_settings": (
                    {
                        "type": "pix_dynamic_code",
                        "pix_dynamic_code": {
                            "code": "000201010212",
                            "merchant_name": "Tyxter Store",
                            "key": "merchant@example.com",
                            "key_type": "EMAIL",
                        },
                    },
                ),
                "currency": "BRL",
                "total_amount": {"value": 12990, "offset": 100},
            },
        },
    }
    client.whatsapp.send_interactive(
        {
            "from": "pn_123",
            "to": {"country_calling_code": "55", "national_number": "11999999999"},
            "interactive": order_details,
        }
    )


def a1_resource_usage(client: Tyxter) -> None:
    project: CreateProjectRequest = {"name": "Demo", "slug": "demo"}
    assert_type(client.projects.create(project), ProjectResponse)
    assert_type(client.projects.list(limit=10, starting_after="prj_1"), ListProjectsResponse)
    assert_type(client.projects.retrieve("prj_123"), ProjectResponse)

    assert_type(
        client.feedback.list(after="fbr_1", limit=10),
        ListPublicFeedbackReportsResponse,
    )
    assert_type(client.feedback.get("fbr_123"), PublicFeedbackReportResponse)
    assert_type(
        client.webhook_endpoints.test("whe_123", idempotency_key="idem_webhook_test"),
        TestWebhookEndpointResponse,
    )
    assert_type(
        client.billing.list_phone_renewals(status="funding_required"),
        ListPhoneRenewalsResponse,
    )
    assert_type(client.billing.retrieve_phone_renewal("phr_123"), PhoneRenewalResponse)

    api_key: CreateApiKeyRequest = {
        "name": "Project agent",
        "environment": "sandbox",
        "project_id": "prj_123",
        "scopes": ["messages:write"],
    }
    assert_type(client.api_keys.create(api_key), CreateApiKeyResponse)


def a1_response_shapes(
    batch: MessageBatchResponse,
    message: MessageSummaryResponse,
    media: InboundMessageMediaDescriptor,
    phone_number: PhoneNumberResponse,
    provider_connection: ProviderConnectionResponse,
) -> None:
    assert_type(batch["pacing"], MessageBatchPacingResponse | None)
    assert_type(message["status_reason"], str | None)
    assert_type(message["media"], InboundMessageMediaDescriptor | None)
    assert_type(message["redacted_at"], str | None)
    assert_type(media["asset_id"], str)
    if media["status"] == "failed":
        assert_type(media, InboundMessageMediaFailed)
        assert_type(media["failure"], InboundMessageMediaFailure)
    assert_type(phone_number["remaining_messaging_allowance_estimate"], int | None)
    if "display_phone_number" in provider_connection:
        assert_type(provider_connection["display_phone_number"], str | None)
    if "suspension_reason" in provider_connection:
        assert_type(provider_connection["suspension_reason"], str | None)


def a4_template_authoring_usage(client: Tyxter) -> None:
    positional_format: TemplateParameterFormat = "POSITIONAL"
    named_format: TemplateParameterFormat = "NAMED"
    assert_type(positional_format, TemplateParameterFormat)
    assert_type(named_format, TemplateParameterFormat)

    create: CreateTemplateRequest = {
        "name": "order_tracking",
        "language": "en_US",
        "category": "utility",
        "parameter_format": named_format,
        "components": [{"type": "BODY", "text": "Hi {{customer_name}}"}],
    }
    generate: TemplateGenerationRequest = {
        "description": "Tell a customer their order is ready",
        "language": "en_US",
        "category": "utility",
        "parameter_format": named_format,
    }
    update: UpdateTemplateRequest = {"parameter_format": positional_format}
    duplicate: DuplicateTemplateRequest = {"parameter_format": named_format}

    generated = client.templates.generate(generate)
    created = client.templates.create(create)
    updated = client.templates.update("tpl_123", update)
    duplicated = client.templates.duplicate("tpl_123", duplicate)
    assert_type(generated, TemplateGenerationResponse)
    assert_type(created, TemplateResponse)
    assert_type(updated, TemplateResponse)
    assert_type(duplicated, TemplateResponse)
    if "parameter_format" in generated:
        assert_type(generated["parameter_format"], TemplateParameterFormat)
    if "parameter_format" in created:
        assert_type(created["parameter_format"], TemplateParameterFormat)

    legacy_template = TemplateResponse(
        id="tpl_123",
        object="template",
        name="order_tracking",
        language="en_US",
        category="utility",
        status="draft",
        environment="sandbox",
        components=[],
        provider_template_id=None,
        rejection_reason=None,
        provider_quality="unknown",
        authoring_signals=[],
        submitted_at=None,
        approved_at=None,
        created_at="2026-08-26T12:00:00Z",
        updated_at="2026-08-26T12:00:00Z",
    )
    legacy_generation = TemplateGenerationResponse(
        object="template_generation",
        name="order_tracking",
        language="en_US",
        category="utility",
        components=[],
        authoring_signals=[],
    )
    assert_type(legacy_template, TemplateResponse)
    assert_type(legacy_generation, TemplateGenerationResponse)


def a5_phone_name_review_usage(client: Tyxter) -> None:
    tier: PhoneMessagingTier = "tier_2k"
    pending: PhoneNumberPendingNameReviewResponse = {
        "requested_name": None,
        "status": "META_FUTURE_PENDING",
        "observed_at": "2026-09-01T10:00:00Z",
    }
    review: PhoneNumberNameReviewResponse = {
        "requested_name": "Tyxter Support",
        "decision": "META_FUTURE_DECISION",
        "reason": None,
        "reviewed_at": "2026-09-01T11:00:00Z",
    }
    assert_type(tier, PhoneMessagingTier)
    assert_type(pending["status"], str | None)
    assert_type(review["decision"], str)
    assert_type(review["reason"], str | None)

    phone = client.phone_numbers.retrieve("pn_123")
    assert_type(phone, PhoneNumberResponse)
    if "verified_name" in phone:
        assert_type(phone["verified_name"], str | None)
    if "pending_name_review" in phone:
        assert_type(phone["pending_name_review"], PhoneNumberPendingNameReviewResponse | None)
    if "name_review" in phone:
        assert_type(phone["name_review"], PhoneNumberNameReviewResponse | None)

    legacy_phone = PhoneNumberResponse(
        id="pn_123",
        object="phone_number",
        source="byon",
        status="active",
        environment="sandbox",
        display_name="Tyxter Support",
        ddd="11",
        phone="+5511999999999",
        provider_number_id=None,
        meta_phone_number_id="meta_123",
        waba_id="waba_123",
        quality_rating="unknown",
        messaging_tier="tier_1k",
        messaging_limit_tier=None,
        meta_throughput_tier=None,
        meta_quality_rating=None,
        meta_health_synced_at=None,
        current_24h_unique_recipients=0,
        remaining_messaging_allowance_estimate=None,
        verification_code=None,
        verification_code_received_at=None,
        monthly_fee_brl=None,
        error_code=None,
        error_message=None,
        created_at="2026-08-26T12:00:00Z",
        updated_at="2026-08-26T12:00:00Z",
        activated_at="2026-08-26T12:05:00Z",
        released_at=None,
        recent_messages=[],
    )
    assert_type(legacy_phone, PhoneNumberResponse)


def a6_provider_availability_usage(
    connection: ProviderConnectionResponse,
    flow: FlowResponse,
) -> None:
    capability: ProviderConnectionSendCapability = "blocked"
    block_code: ProviderConnectionSendBlockCode = 141006
    waba_capability = ProviderConnectionWabaSendCapability(
        waba_id="waba_123",
        send_capability=capability,
        send_block_codes=[block_code, 141011],
        observed_at="2026-09-01T10:06:00Z",
    )
    policy_data = ProviderConnectionPolicyWarningWebhookData(
        provider_connection_id="pc_123",
        provider="meta",
        display_name="Tyxter Support",
        violation_type="META_FUTURE_VIOLATION",
        observed_at="2026-09-01T10:05:00Z",
    )
    policy_warning = ProviderConnectionPolicyWarningWebhookEnvelope(
        id="evt_policy_warning",
        type="provider_connection.policy_warning",
        created_at="2026-09-01T10:05:00Z",
        environment="sandbox",
        trace_id="trc_policy_warning",
        data=policy_data,
    )
    disable_data = ProviderConnectionDisableScheduledWebhookData(
        provider_connection_id="pc_123",
        provider="meta",
        display_name="Tyxter Support",
        waba_ban_date=None,
        observed_at="2026-09-01T10:07:00Z",
    )
    disable_scheduled = ProviderConnectionDisableScheduledWebhookEnvelope(
        id="evt_disable_scheduled",
        type="provider_connection.disable_scheduled",
        created_at="2026-09-01T10:07:00Z",
        environment="sandbox",
        trace_id="trc_disable_scheduled",
        data=disable_data,
    )
    assert_type(waba_capability["send_capability"], ProviderConnectionSendCapability)
    assert_type(waba_capability["send_block_codes"], list[ProviderConnectionSendBlockCode])
    assert_type(policy_warning["data"]["violation_type"], str | None)
    assert_type(disable_scheduled["data"]["waba_ban_date"], str | None)

    if "last_policy_warning_type" in connection:
        assert_type(connection["last_policy_warning_type"], str | None)
    if "send_capability" in connection:
        assert_type(connection["send_capability"], ProviderConnectionSendCapability | None)
    if "send_block_codes" in connection:
        assert_type(connection["send_block_codes"], list[ProviderConnectionSendBlockCode] | None)
    if "waba_send_capabilities" in connection:
        assert_type(
            connection["waba_send_capabilities"], list[ProviderConnectionWabaSendCapability]
        )
    if "provider_missing_since" in flow:
        assert_type(flow["provider_missing_since"], str | None)


def a7_credit_provider_access(event: CreditToppedUpWebhookData) -> None:
    if "provider" in event:
        assert_type(event["provider"], Literal["stripe", "abacate_pay", "manual", "promotion"])


def a7_promotional_credit_usage(client: Tyxter) -> None:
    manual_payment_method: TopupPaymentMethodKind = "manual"
    promotion_payment_method: TopupPaymentMethodKind = "promotion"
    purchase_request: PurchaseBillingPackageRequest = {
        "package_code": "pkg_10k",
        "payment_method": "card",
    }
    promotion_topup = TopupResponse(
        id="topup_promotion_123",
        object="credit_topup",
        kind="cash",
        status="succeeded",
        amount_brl="25.00",
        payment_method=promotion_payment_method,
        package_code=None,
        quota_messages=None,
        quota_remaining=None,
        stripe_payment_intent_id=None,
        stripe_client_secret=None,
        provider="promotion",
        abacate_charge_id=None,
        pix_copy_paste=None,
        pix_qr_code_base64=None,
        pix_expires_at=None,
        created_at="2026-09-01T10:00:00Z",
        completed_at="2026-09-01T10:00:00Z",
    )
    historical_data = CreditToppedUpWebhookData(
        topup_id="topup_manual_123",
        amount_brl="25.00",
        payment_method=manual_payment_method,
        balance_brl="125.00",
    )
    promotion_data = CreditToppedUpWebhookData(
        topup_id="topup_promotion_123",
        amount_brl="25.00",
        payment_method=promotion_payment_method,
        provider="promotion",
        balance_brl="125.00",
    )
    historical_event = CreditToppedUpWebhookEnvelope(
        id="evt_credit_historical",
        type="credit.topped_up",
        created_at="2026-09-01T10:00:00Z",
        environment="sandbox",
        trace_id="trc_credit_historical",
        data=historical_data,
    )
    promotion_event = CreditToppedUpWebhookEnvelope(
        id="evt_credit_promotion",
        type="credit.topped_up",
        created_at="2026-09-01T10:00:00Z",
        environment="production",
        trace_id="trc_credit_promotion",
        data=promotion_data,
    )
    assert_type(client.billing.purchase_package(purchase_request), TopupResponse)
    assert_type(promotion_topup["payment_method"], TopupPaymentMethodKind)
    assert_type(promotion_event["data"]["payment_method"], TopupPaymentMethodKind)
    assert_type(historical_event["data"]["balance_brl"], str)
    a7_credit_provider_access(historical_event["data"])
    a7_credit_provider_access(promotion_event["data"])


def a2_message_media_contract_usage(client: Tyxter) -> None:
    whatsapp_media: MediaMessagePayload = {
        "kind": "audio",
        "link": "https://cdn.example.test/voice-note.ogg",
        "voice": True,
    }
    instagram_media: InstagramMediaMessageInput = {
        "account_id": "ig_123",
        "user_id": "igsid_456",
        "media": {"kind": "image", "link": "https://cdn.example.test/photo.jpg"},
    }
    outbound_request: CreateMessageRequest = {
        "channel": "whatsapp",
        "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
        "recipient": {"type": "phone_e164", "id": "+15555550100"},
        "message": {"type": "media", "media": whatsapp_media},
    }
    instagram_create: CreateMessageRequest = {
        "channel": "instagram",
        "sender": {"type": "instagram_account", "id": "ig_123"},
        "recipient": {"type": "instagram_user", "id": "igsid_456"},
        "message": {
            "type": "media",
            "media": {"kind": "image", "link": "https://cdn.example.test/photo.jpg"},
        },
    }
    instagram_send: SendMediaMessageInput = {
        "channel": "instagram",
        "sender": {"type": "instagram_account", "id": "ig_123"},
        "recipient": {"type": "instagram_user", "id": "igsid_456"},
        "media": {"kind": "image", "link": "https://cdn.example.test/photo.jpg"},
    }

    assert_type(client.messages.create(outbound_request), MessageResponse)
    assert_type(client.messages.create(instagram_create), MessageResponse)
    assert_type(client.messages.send_media(instagram_send), MessageResponse)
    assert_type(client.instagram.send_media(instagram_media), MessageResponse)


def a2_response_shapes(
    message: MessageSummaryResponse,
    media: InboundMessageMediaDescriptor,
    media_asset: MediaAssetResponse,
) -> None:
    phone_less: PhoneLessInboundSenderIdentity = {"type": "phone_e164", "id": ""}

    assert_type(phone_less, PhoneLessInboundSenderIdentity)
    assert_type(message["sender"], MessageReadSenderIdentity)
    if "unsupported" in message:
        assert_type(message["unsupported"], InboundUnsupportedDescriptor | None)
    if "unknown" in message:
        assert_type(message["unknown"], InboundUnknownDescriptor | None)
    if "download" in media_asset:
        assert_type(media_asset["download"], MediaDownloadHint | None)
    if media["status"] == "consumed" and "download" in media:
        assert_type(media, InboundMessageMediaConsumed)
        assert_type(media["download"], MediaDownloadHint)
    if media["status"] == "failed":
        assert_type(media, InboundMessageMediaFailed)
        assert_type(media["failure"], InboundMessageMediaFailure)


def a2_response_shape_fixtures() -> None:
    phone_less: PhoneLessInboundSenderIdentity = {"type": "phone_e164", "id": ""}
    consumed: InboundMessageMediaConsumed = {
        "asset_id": "mda_consumed",
        "kind": "audio",
        "mime_type": "audio/ogg",
        "byte_length": 12,
        "filename": None,
        "status": "consumed",
        "download": {"method": "GET", "path": "/v1/media/mda_consumed/download"},
    }
    failed: InboundMessageMediaFailed = {
        "asset_id": "mda_failed",
        "kind": "audio",
        "mime_type": "audio/ogg",
        "byte_length": 12,
        "filename": None,
        "status": "failed",
        "failure": {"code": "media_fetch_failed", "message": "Provider fetch failed."},
    }
    unsupported: InboundUnsupportedDescriptor = {
        "provider_type": "video_note",
        "reason": {"code": 131051, "message": "Message type is not supported."},
    }
    unknown: InboundUnknownDescriptor = {"provider_type": "location"}
    message: MessageSummaryResponse = {
        "id": "msg_unsupported",
        "object": "message",
        "channel": "whatsapp",
        "direction": "inbound",
        "type": "unsupported",
        "status": "received",
        "status_reason": None,
        "environment": "sandbox",
        "sender": phone_less,
        "recipient": {"type": "whatsapp_phone_number", "id": "pn_123"},
        "provider": "meta",
        "provider_message_id": "wamid_123",
        "template_name": None,
        "template_id": None,
        "template_version_id": None,
        "template_version": None,
        "media": None,
        "unsupported": unsupported,
        "unknown": None,
        "payload": None,
        "metadata": None,
        "error_code": None,
        "error_message": None,
        "provider_error": None,
        "trace_id": "trc_123",
        "created_at": "2026-08-10T12:00:00Z",
        "updated_at": "2026-08-10T12:00:00Z",
        "redacted_at": None,
        "delivery_unconfirmed_at": None,
    }
    media_asset: MediaAssetResponse = {
        "id": "mda_consumed",
        "object": "media_asset",
        "source": "inbound_provider",
        "provider": "meta",
        "provider_media_id": "media_123",
        "kind": "audio",
        "lifecycle": "single_use",
        "filename": None,
        "mime_type": "audio/ogg",
        "byte_length": 12,
        "status": "consumed",
        "download": {"method": "GET", "path": "/v1/media/mda_consumed/download"},
        "expires_at": None,
        "upload_expires_at": "2026-08-10T12:00:00Z",
        "completed_at": "2026-08-10T12:00:00Z",
        "consumed_at": "2026-08-10T12:00:00Z",
        "consumed_by_message_id": "msg_123",
        "deleted_at": None,
        "failure_code": None,
        "failure_message": None,
        "trace_id": "trc_123",
        "created_at": "2026-08-10T12:00:00Z",
        "updated_at": "2026-08-10T12:00:00Z",
    }

    assert_type(failed["failure"], InboundMessageMediaFailure)
    assert_type(unknown["provider_type"], str | None)
    if "download" in consumed:
        assert_type(consumed["download"], MediaDownloadHint)
    a2_response_shapes(message, consumed, media_asset)


def whole_branch_r1_legacy_response_constructors() -> None:
    consumed = InboundMessageMediaConsumed(
        asset_id="mda_legacy",
        kind="audio",
        mime_type="audio/ogg",
        byte_length=12,
        filename=None,
        status="consumed",
    )
    message = MessageSummaryResponse(
        id="msg_legacy",
        object="message",
        channel="whatsapp",
        direction="inbound",
        type="text",
        status="received",
        status_reason=None,
        environment="sandbox",
        sender={"type": "phone_e164", "id": ""},
        recipient={"type": "whatsapp_phone_number", "id": "pn_123"},
        provider="meta",
        provider_message_id="wamid_legacy",
        template_name=None,
        template_id=None,
        template_version_id=None,
        template_version=None,
        media=None,
        payload=None,
        metadata=None,
        error_code=None,
        error_message=None,
        provider_error=None,
        trace_id="trc_legacy",
        created_at="2026-08-10T12:00:00Z",
        updated_at="2026-08-10T12:00:00Z",
        redacted_at=None,
        delivery_unconfirmed_at=None,
    )
    media_asset = MediaAssetResponse(
        id="mda_legacy",
        object="media_asset",
        source="inbound_provider",
        provider="meta",
        provider_media_id="media_legacy",
        kind="audio",
        lifecycle="single_use",
        filename=None,
        mime_type="audio/ogg",
        byte_length=12,
        status="consumed",
        expires_at=None,
        upload_expires_at="2026-08-10T12:00:00Z",
        completed_at="2026-08-10T12:00:00Z",
        consumed_at="2026-08-10T12:00:00Z",
        consumed_by_message_id="msg_legacy",
        deleted_at=None,
        failure_code=None,
        failure_message=None,
        trace_id="trc_legacy",
        created_at="2026-08-10T12:00:00Z",
        updated_at="2026-08-10T12:00:00Z",
    )
    endpoint = WebhookEndpointResponse(
        id="whe_legacy",
        object="webhook_endpoint",
        url="https://example.test/webhooks",
        description=None,
        subscribed_events=["message.sent"],
        status="active",
        disabled_reason=None,
        last_failure_at=None,
        last_success_at=None,
        environment="sandbox",
        created_at="2026-08-10T12:00:00Z",
        updated_at="2026-08-10T12:00:00Z",
    )
    created = CreateWebhookEndpointResponse(
        id="whe_legacy",
        object="webhook_endpoint",
        url="https://example.test/webhooks",
        description=None,
        subscribed_events=["message.sent"],
        status="active",
        disabled_reason=None,
        last_failure_at=None,
        last_success_at=None,
        environment="sandbox",
        created_at="2026-08-10T12:00:00Z",
        updated_at="2026-08-10T12:00:00Z",
        signing_secret="whsec_legacy",
    )
    rotated = RotateWebhookSigningSecretResponse(
        id="whe_legacy",
        object="webhook_endpoint",
        url="https://example.test/webhooks",
        description=None,
        subscribed_events=["message.sent"],
        status="active",
        disabled_reason=None,
        last_failure_at=None,
        last_success_at=None,
        environment="sandbox",
        created_at="2026-08-10T12:00:00Z",
        updated_at="2026-08-10T12:00:00Z",
        signing_secret="whsec_rotated",
    )

    assert_type(consumed, InboundMessageMediaConsumed)
    assert_type(message, MessageSummaryResponse)
    assert_type(media_asset, MediaAssetResponse)
    assert_type(endpoint, WebhookEndpointResponse)
    assert_type(created, CreateWebhookEndpointResponse)
    assert_type(rotated, RotateWebhookSigningSecretResponse)


def a3_transcription_webhook_narrowing(event: MessageMediaTranscriptionWebhookEnvelope) -> None:
    if event["type"] == "message.media_transcribed":
        assert_type(event, MessageMediaTranscribedWebhookEnvelope)
        assert_type(event["data"], MessageMediaTranscribedWebhookData)
        assert_type(event["data"]["transcript"], MessageMediaTranscribedWebhookTranscript)
        assert_type(event["data"]["transcript"]["provider"], str)
        assert_type(event["data"]["transcript"]["duration_seconds"], int)
    else:
        assert_type(event, MessageMediaTranscriptionFailedWebhookEnvelope)
        assert_type(event["data"], MessageMediaTranscriptionFailedWebhookData)
        assert_type(event["data"]["transcript"], MessageMediaTranscriptionFailedWebhookTranscript)
        assert_type(event["data"]["transcript"]["error_code"], str)
        assert_type(event["data"]["transcript"]["error_message"], str | None)


def a3_transcription_webhook_fixtures() -> None:
    success: MessageMediaTranscribedWebhookEnvelope = {
        "id": "evt_transcribed",
        "type": "message.media_transcribed",
        "created_at": "2026-08-25T12:00:00Z",
        "environment": "sandbox",
        "trace_id": "trc_transcribed",
        "data": {
            "message_id": "msg_123",
            "status": "delivered",
            "channel": "whatsapp",
            "sender": {"type": "phone_e164", "id": "+15555550100"},
            "recipient": {"type": "whatsapp_phone_number", "id": "pn_123"},
            "provider_message_id": "wamid_123",
            "metadata": None,
            "transcript": {
                "id": "mtr_123",
                "media_asset_id": "mda_123",
                "status": "succeeded",
                "provider": "openai",
                "model": "gpt-4o-transcribe",
                "language": "pt",
                "text": "olá",
                "duration_seconds": 4,
                "completed_at": "2026-08-25T12:00:04Z",
            },
        },
    }
    failure: MessageMediaTranscriptionFailedWebhookEnvelope = {
        "id": "evt_failed",
        "type": "message.media_transcription_failed",
        "created_at": "2026-08-25T12:00:00Z",
        "occurred_at": "2026-08-25T12:00:04Z",
        "environment": "production",
        "trace_id": "trc_failed",
        "data": {
            "message_id": "msg_456",
            "status": "failed",
            "channel": "instagram",
            "sender": {"type": "instagram_user", "id": "ig_1"},
            "recipient": {"type": "instagram_account", "id": "ig_business_1"},
            "provider_message_id": None,
            "metadata": None,
            "transcript": {
                "id": "mtr_456",
                "media_asset_id": "mda_456",
                "status": "failed",
                "error_code": "transcription_failed",
                "error_message": "Provider rejected the media.",
                "language": None,
                "completed_at": "2026-08-25T12:00:04Z",
            },
        },
    }

    a3_transcription_webhook_narrowing(success)
    a3_transcription_webhook_narrowing(failure)


def a3_error_discovery_shape(error: TyxterErrorBody) -> None:
    if "discovery" in error:
        assert_type(error["discovery"], ErrorDiscoveryPointer)


def a3_error_discovery_fixture() -> TyxterErrorBody:
    discovery = ErrorDiscoveryPointer(
        openapi="/openapi.json",
        well_known="/.well-known/tyxter.json",
    )
    error = TyxterErrorBody(
        type="not_found",
        code="route_not_found",
        message="No route matches GET /v1/does-not-exist.",
        discovery=discovery,
    )
    a3_error_discovery_shape(error)
    return error


def diagnostics_and_rental_order_usage(client: Tyxter) -> None:
    meta_diagnostics_and_order_narrowing(
        client.phone_numbers.request_meta_diagnostics(
            "pn_123", {"sandbox_scenario": "message_quality_medium"}
        ),
        client.phone_numbers.create_order({"ddd": "11", "purpose": "Support line"}),
    )
    meta_diagnostics_and_order_narrowing(
        client.phone_numbers.get_meta_diagnostics("pn_123"),
        client.phone_numbers.retrieve_order("ord_123"),
    )


def meta_diagnostics_and_order_narrowing(
    diagnostics: MetaDiagnosticsResponse, order: PhoneNumberOrderResponse
) -> None:
    phone = diagnostics["phone"]
    if phone is not None:
        if phone["status"] == "ok":
            assert_type(phone["facts"], MetaDiagnosticsPhoneFacts)
        else:
            assert_type(phone["failure"], MetaDiagnosticsFailure)
    # "unknown" stays distinct from False: a missing fact is not a refusal.
    can_send = diagnostics["capabilities"]["can_send"]["value"]
    if not isinstance(can_send, bool):
        assert_type(can_send, Literal["unknown"])
    preview = order["preview"]
    if preview["status"] == "forecast":
        assert_type(preview["charges"], list[PhoneNumberOrderPreviewCharge])


def provider_credential_setup_result_narrowing(
    result: ProviderCredentialSetupSessionResult,
) -> None:
    if result["status"] == "completed" and result["target"] == "openai.stt":
        assert_type(result, ProviderCredentialSetupSessionCompletedOpenAISttResult)
        assert_type(result["completed_stt_provider"], ProviderCredentialSetupSttProvider)
        assert_type(result["completed_tts_provider"], None)


def create(client: Tyxter) -> ProviderCredentialSetupSessionResponse:
    return client.provider_credential_setup_sessions.create({"target": "openai.tts"})


def mutate_legacy_provider_credential_setup_session(
    result: ProviderCredentialSetupSessionResponse,
) -> None:
    result["target"] = "openai.stt"
    result["status"] = "completed"
    result["completed_provider_connection_id"] = "pcn_123"
    result["completed_tts_provider"] = "openai"
    result["completed_stt_provider"] = "openai"


def parity_0_12_requests(client: Tyxter) -> None:
    group_reply: CreateMessageRequest = {
        "channel": "whatsapp",
        "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
        "recipient": {"type": "whatsapp_group", "id": "grp_123"},
        "message": {"type": "text", "text": {"body": "Welcome"}},
        "reply_to": {"message_id": "msg_inbound_123"},
    }
    reaction: CreateMessageRequest = {
        "channel": "whatsapp",
        "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
        "recipient": {"type": "phone_e164", "id": "+5511999999999"},
        "message": {
            "type": "reaction",
            "reaction": {"message_id": "msg_inbound_123", "emoji": ""},
        },
    }
    group: WhatsAppGroupRecipientIdentity = {"type": "whatsapp_group", "id": "grp_123"}
    assert_type(client.messages.create(group_reply), MessageResponse)
    assert_type(client.messages.create(reaction, idempotency_key="reaction-1"), MessageResponse)
    assert_type(
        client.messages.send_text(
            {
                "channel": "whatsapp",
                "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
                "recipient": group,
                "text": {"body": "hi"},
                "reply_to": {"message_id": "msg_inbound_123"},
            }
        ),
        MessageResponse,
    )
    assert_type(
        client.whatsapp.send_text(
            {
                "from": "pn_123",
                "to": "+5511999999999",
                "body": "hi",
                "reply_to": {"message_id": "m"},
            }
        ),
        MessageResponse,
    )
    client.sandbox.inbound_messages.create(
        {"from": "+5511988887777", "to": "+5511999999999", "type": "text", "group_id": "grp_123"}
    )
    client.messages.request_transcription(
        "msg_123", {"prompt": "Clinic appointment", "keywords": ["Tyxter", "Dr. Ada"]}
    )
    client.billing.purchase_package({"package_code": "pkg_10k", "payment_method_id": "pm_1"})
    client.billing.save_payment_method({"stripe_payment_method_id": "pm_1", "set_default": True})
    client.billing.update_auto_topup(
        {"enabled": True, "threshold_brl": "10.0000", "amount_brl": "50.0000"}
    )


def parity_0_12_responses(client: Tyxter, payment: PaymentResponse) -> None:
    phone = client.phone_numbers.retrieve("pn_123")
    assert_type(phone, PhoneNumberReadResponse)
    assert_type(client.phone_numbers.list()["data"][0], PhoneNumberReadResponse)
    renewal = phone.get("renewal")
    if renewal is not None:
        assert_type(renewal["state"], PhoneRenewalSummaryState)
    provisioned = client.phone_numbers.provision({"ddd": "11"}, idempotency_key="idem")
    assert_type(provisioned, PhoneNumberMutationResponse)
    for warning in provisioned.get("warnings", []):
        assert_type(warning["code"], DisplayNameWarningCode)
    connection = client.provider_connections.exchange_meta_oauth({"code": "code_123"})
    assert_type(connection, MetaConnectionMutationResponse)
    operation = client.provider_connections.retrieve(connection["id"]).get("operation")
    if operation is not None and operation["state"] == "failed":
        assert_type(operation["error_code"], ProviderConnectionOperationErrorCode | None)
    status = client.provider_connections.status()
    assert_type(
        status["channels"]["agentic_payments"].get("platform_default"),
        AgenticPlatformDefaultStatus | None,
    )
    entry = client.billing.list_ledger()["data"][0]
    assert_type(entry, LedgerEntryResponse)
    assert_type(entry["payment_fee"], LedgerEntryPaymentFee | None)
    fees = payment.get("fees")
    if fees is not None:
        assert_type(fees["completion"]["state"], PaymentFeeCompletionState)
    flow = client.flows.retrieve("flw_123")
    assert_type(flow.get("rejection_code"), FlowRejectionCode | None)
    message = client.messages.retrieve("msg_123")
    context = message.get("context")
    if context is not None:
        assert_type(context, MessageContext)
    sender = message["sender"]
    assert_type(sender.get("profile_name"), str | None)


def parity_0_12_errors(error: TyxterAPIError) -> None:
    assert_type(error.retryable, Literal[False] | None)
    assert_type(error.raw_body, TyxterWireErrorBody | None)
    assert_type(error.details, WebhookListenSessionConflictDetails | None)
    assert_type(error.next_allowed_at, str | None)
    assert_type(error.rental_order, PhoneNumberRentalApprovalOrder | None)
    assert_type(error.service_window, ServiceWindowRequiredDetails | None)
    if error.service_window is not None:
        assert_type(error.service_window["reason"], ServiceWindowRequiredReason)


def parity_0_12_webhooks(
    participant: GroupParticipantWebhookEnvelope,
    payment: PaymentWebhookEnvelope,
    lifecycle: GroupWebhookEnvelope,
    group_message: GroupMessageReceivedWebhookEnvelope,
    reaction: MessageReactionReceivedWebhookEnvelope,
    hard_block: CreditHardBlockEngagedWebhookEnvelope,
) -> None:
    if participant["type"] == "group.participant_removed":
        assert_type(participant["data"]["initiated_by"], GroupParticipantRemovalInitiator)
    else:
        assert_type(participant["data"], GroupParticipantJoinedWebhookData)
    if payment["type"] == "payment.link_generated":
        assert_type(payment["data"]["payment_link_url"], str)
    elif payment["type"] == "payment.created":
        assert_type(payment["data"]["payment_link_url"], None)
    assert_type(lifecycle["data"]["status"], GroupWebhookStatus)
    assert_type(group_message["data"]["recipient"]["type"], Literal["whatsapp_group"])
    assert_type(reaction["data"]["reaction"]["from"], str | None)
    assert_type(hard_block["data"]["trigger"], CreditHardBlockTrigger)


def pre_0_8_usage_and_quickstart_reads(client: Tyxter) -> None:
    summary = client.usage.retrieve(period_start="2026-10-01", period_end="2026-11-01")
    estimate = summary.get("estimated_external_meta_cost")
    if estimate is not None:
        assert_type(estimate, EstimatedExternalMetaCostSummary)
    record = client.usage.list_records()["data"][0]
    record_estimate = record.get("estimated_external_meta_cost")
    if record_estimate is not None:
        assert_type(record_estimate, EstimatedExternalMetaCost)
    templates = client.sandbox.quickstart().get("templates")
    if templates is not None:
        assert_type(templates["default_template"], SandboxDefaultTemplate | None)
    client.audiences.create({"name": "VIP"})
