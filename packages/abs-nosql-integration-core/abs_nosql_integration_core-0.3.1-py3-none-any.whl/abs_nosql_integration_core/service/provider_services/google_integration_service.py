from abs_integration_core.service.base_services import GoogleIntegrationBaseService

from abs_nosql_integration_core.repository import IntegrationRepository
from abs_nosql_integration_core.service.nosql_integration_service import (
    IntegrationBaseService,
)
from abs_nosql_integration_core.service.nosql_subscription_service import (
    SubscriptionService,
)
from abs_nosql_integration_core.utils import Encryption
from typing import Optional


class GoogleIntegrationService(GoogleIntegrationBaseService, IntegrationBaseService):
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

        self.scopes = "https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
        self.google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.drive_api_url = "https://www.googleapis.com/drive/v3"
