from typing import Dict, Optional, List
from abs_integration_core.schema import TokenData, Integration, UpdateIntegration, CreateIntegration
from abs_nosql_integration_core.repository import IntegrationRepository
from abs_exception_core.exceptions import NotFoundError
from abs_nosql_repository_core.service import BaseService
from abs_integration_core.utils.encryption import Encryption
from abs_integration_core.service.base_services import AbstractIntegrationBaseService
from datetime import datetime, timedelta, UTC
import httpx
from abs_nosql_repository_core.schema.base_schema import FilterSchema, ListFilter, FieldFilterSchema
from abs_utils.logger import setup_logger


logger = setup_logger(__name__)


class IntegrationBaseService(BaseService, AbstractIntegrationBaseService):
    """
    Base abstract class for all integration services.
    Any integration service should inherit from this class and implement its methods.
    """
    def __init__(
        self, 
        integration_repository: IntegrationRepository,
        encryption: Encryption,
        provider_name: Optional[str] = None
    ):
        self.provider_name = provider_name
        self.encryption = encryption
        super().__init__(integration_repository)

    async def handle_oauth_callback(self, code: str, user_id: int) -> TokenData:
        """
        Handle the OAuth callback and store tokens with email fetched from provider.
        
        Args:
            code: The authorization code from OAuth callback
            user_id: The user ID
            
        Returns:
            TokenData object
        """
        token_data = await self.get_integration_token_data(code)

        # Fetch user email from provider
        user_email = await self.get_user_email(token_data.access_token)

        # Check if integration already exists for this provider, user, and email
        existing_integration = None
        if user_email:
            existing_integration = await self.repository.get_by_provider_user_email(
                self.provider_name, user_id, user_email
            )
        
        if existing_integration:
            # Update existing integration with new encrypted tokens
            update_data = UpdateIntegration(
                access_token=self.encryption.encrypt_token(token_data.access_token),
                refresh_token=self.encryption.encrypt_token(token_data.refresh_token),
                expires_at=token_data.expires_at,
                email=user_email
            )
            await self.repository.update(
                existing_integration["_id"],
                update_data.model_dump(exclude_none=True)
            )
        else:
            # Create new integration with encrypted tokens and fetched email
            create_data = CreateIntegration(
                provider_name=self.provider_name,
                access_token=self.encryption.encrypt_token(token_data.access_token),
                refresh_token=self.encryption.encrypt_token(token_data.refresh_token),
                expires_at=token_data.expires_at,
                user_id=user_id,
                email=user_email
            )
            await self.repository.create_integration(create_data)
        
        # Return unencrypted token data to the caller
        return token_data

    async def refresh_token(self, token_url: str, refresh_data: Dict, user_id: int, integration_uuid: str) -> Optional[TokenData]:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            Updated TokenData if successful, None otherwise
        """
        # Get the current integration
        integration = await self.get_query_by_user_and_uuid(user_id, integration_uuid)
        
        # Decrypt the refresh token for use with the API
        decrypted_refresh_token = self.encryption.decrypt_token(integration["refresh_token"])
        
        # Use the refresh token to get a new access token
        refresh_data["refresh_token"] = decrypted_refresh_token

        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=refresh_data)
            token_response.raise_for_status()
            token = token_response.json()

        new_access_token = token.get("access_token")
        new_refresh_token = token.get("refresh_token", decrypted_refresh_token)
        expires_in = token.get("expires_in", 3600)
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
            
        # Update the integration in the database with encrypted tokens
        token_data = TokenData(
            access_token=self.encryption.encrypt_token(new_access_token),
            refresh_token=self.encryption.encrypt_token(new_refresh_token),
            expires_at=expires_at
        )
        await self.repository.refresh_token(
            integration_id=integration["_id"],
            token_data=token_data
        )
        
        # Return decrypted token data to the caller
        return TokenData(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_at=expires_at
        )

    async def get_query_by_user_id(self, user_id: int):
        find_query = FilterSchema(
            operator="and",
            conditions=[
                {"field": "user_id", "operator": "eq", "value": user_id},
                {"field": "provider_name", "operator": "eq", "value": self.provider_name}
            ]
        )
        query = await super().get_all(find=ListFilter(filters=find_query))
        if len(query["founds"]) > 0:
            return query["founds"][0]
        else:
            raise NotFoundError(detail="Integration not found")

    async def get_integration(self, user_id: int) -> Optional[TokenData]:
        """
        Get integration data.
        
        Returns:
            TokenData if integration exists, None otherwise
        """
        try:
            integration = await self.get_query_by_user_id(user_id)
            return integration
        except Exception:
            return None

    async def get_all_integrations_by_provider(
        self, page: int = 1, page_size: int = 10
    ) -> List[Integration]:
        """
        Get all integrations.

        Returns:
            List of TokenData objects
        """
        try:
            find_query = FilterSchema(
                operator="and",
                conditions=[
                    {"field": "provider_name", "operator": "eq", "value": self.provider_name}
                ]
            )
            query = await super().get_all(
                find=ListFilter(
                    filters=find_query,
                    page=page,
                    page_size=page_size
                )
            )
            return query
        except Exception:
            return []

    async def get_all_integrations(self, find: Dict) -> List[Integration]:
        """
        Get all integrations.
        
        Returns:
            List of TokenData objects
        """
        find = ListFilter(**find)
        find.field_filter = FieldFilterSchema(
            fields=["access_token", "refresh_token"],
            type="exclude"
        )

        return await super().get_all(find)

    async def delete_integration(self, user_id: int, integration_uuid: str) -> bool:
        """
        Delete an integration.
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            integration = await self.get_query_by_user_and_uuid(user_id, integration_uuid)
            await super().delete(integration["_id"])

            return True

        except NotFoundError:
            # If the integration doesn't exist, consider it "deleted"
            return True

        except Exception as e:
            logger.error(f"Error deleting integration: {str(e)}")
            return False

    async def get_query_by_user_and_uuid(self, user_id: int, integration_uuid: str):
        """Get the integration query by user and UUID"""
        integration = await self.repository.get_by_user_and_uuid(user_id, integration_uuid, self.provider_name)
        if not integration:
            raise NotFoundError("Integration not found")
        return integration
