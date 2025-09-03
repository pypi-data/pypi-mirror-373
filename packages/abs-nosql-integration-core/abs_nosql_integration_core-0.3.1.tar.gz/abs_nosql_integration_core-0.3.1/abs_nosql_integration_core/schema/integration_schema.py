from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime
from abs_nosql_repository_core.document.base_document import BaseDocument


class Integration(BaseDocument):
    provider_name: Optional[str] = Field(None, description="The name of the provider")
    access_token: Optional[str] = Field(None, description="The access token")
    refresh_token: Optional[str] = Field(None, description="The refresh token")
    expires_at: Optional[datetime] = Field(None, description="The expiration date of the access token")

    user_id: Optional[int] = Field(None, description="The user id")
    email: Optional[EmailStr] = Field(None, description="The email associated with the integration")
    is_active: bool = Field(True, description="Whether the integration is active and working")

    class Settings:
        name = "integrations"
