from abs_integration_core.service.base_services import DocuSignIntegrationBaseService

from abs_nosql_integration_core.repository import IntegrationRepository
from abs_nosql_integration_core.service.nosql_integration_service import (
    IntegrationBaseService,
)
from abs_nosql_integration_core.service.nosql_subscription_service import (
    SubscriptionService,
)
from abs_nosql_integration_core.utils import Encryption
from typing import Optional


class DocusignIntegrationService(
    DocuSignIntegrationBaseService, IntegrationBaseService
):
    def __init__(
        self,
        provider_name: str,
        integration_repository: IntegrationRepository,
        subscription_service: SubscriptionService,
        encryption: Encryption,
        client_id: str,
        client_secret: str,
        redirect_url: Optional[str] = None,
    ):
        super().__init__(
            provider_name=provider_name,
            integration_repository=integration_repository,
            encryption=encryption,
        )

        self.subscription_service = subscription_service

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url

        self.scopes = "signature impersonation extended"
        self.docusign_base_oauth_url = "https://account-d.docusign.com/oauth"
        self.docusign_auth_url = f"{self.docusign_base_oauth_url}/auth"

        self.token_url = f"{self.docusign_base_oauth_url}/token"
        self.docusign_api_url = "https://demo.docusign.net/restapi/v2.1"

        self.events = [
            "envelope-sent",
            "envelope-resent",
            "envelope-delivered",
            "envelope-completed",
            "envelope-declined",
            "envelope-voided",
            "recipient-authenticationfailed",
            "recipient-autoresponded",
            "recipient-declined",
            "recipient-delivered",
            "recipient-completed",
            "recipient-sent",
            "recipient-resent",
            "template-created",
            "template-modified",
            "template-deleted",
            "envelope-corrected",
            "envelope-purge",
            "envelope-deleted",
            "envelope-discard",
            "identity-verification-completed",
            "identity-verification-pending",
            "recipient-reassign",
            "recipient-delegate",
            "recipient-finish-later",
            "click-agreed",
            "click-declined",
            "sms-opt-in",
            "sms-opt-out",
            "envelope-created",
            "envelope-removed",
        ]
