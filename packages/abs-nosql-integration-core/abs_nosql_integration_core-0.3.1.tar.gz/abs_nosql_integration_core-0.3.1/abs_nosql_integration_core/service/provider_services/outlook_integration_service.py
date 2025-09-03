from abs_integration_core.service.base_services import OutlookIntegrationBaseService

from abs_nosql_integration_core.repository import IntegrationRepository
from abs_nosql_integration_core.service.nosql_integration_service import (
    IntegrationBaseService,
)
from abs_nosql_integration_core.service.nosql_subscription_service import (
    SubscriptionService,
)
from abs_nosql_integration_core.utils import Encryption
from typing import Optional


class OutlookIntegrationService(
    OutlookIntegrationBaseService, IntegrationBaseService
):
    def __init__(
        self,
        provider_name: str,
        integration_repository: IntegrationRepository,
        subscription_service: SubscriptionService,
        encryption: Encryption,
        client_id: str,
        client_secret: str,
        tenant_id: str,
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
        self.tenant_id = tenant_id
        self.redirect_url = redirect_url

        # Microsoft Graph scopes for Outlook/Mail access
        self.scopes = "https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/User.Read offline_access"
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.token_url = f"{self.authority}/oauth2/v2.0/token"
        self.graph_api_url = "https://graph.microsoft.com/v1.0"