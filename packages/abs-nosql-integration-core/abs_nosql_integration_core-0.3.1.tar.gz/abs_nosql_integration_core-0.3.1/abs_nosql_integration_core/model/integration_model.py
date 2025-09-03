from abs_nosql_repository_core.document.base_document import BaseDraftDocument
from pydantic import Field, EmailStr
from datetime import datetime


class IntegrationDocument(BaseDraftDocument):
    provider_name: str = Field(..., description="The name of the provider")
    access_token: str = Field(..., description="The access token")
    refresh_token: str = Field(..., description="The refresh token")
    expires_at: datetime = Field(..., description="The expiration date of the access token")

    user_id: int = Field(..., description="The user id")
    email: EmailStr = Field(..., description="The email associated with the integration")
    is_active: bool = Field(True, description="Whether the integration is active and working")

    class Settings:
        name = "integrations"
