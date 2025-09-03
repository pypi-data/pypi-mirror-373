from pydantic import Field
from typing import Optional, List
from abs_nosql_repository_core.document.base_document import BaseDraftDocument
from datetime import datetime


class Subscription(BaseDraftDocument):
    target_url: str = Field(..., description="The target URL to subscribe to")
    site_id: Optional[str] = Field(None, description="The ID of the site")
    resource_id: Optional[str] = Field(None, description="The ID of the resource")
    target_path: str = Field("", description="The target path to subscribe to")
    event_types: List[str] = Field(..., description="The types of events to subscribe to")
    provider_name: Optional[str] = Field(None, description="The name of the provider")
    expires_at: Optional[datetime] = Field(None, description="The expiration date of the subscription")

    user_id: Optional[int] = Field(None, description="The ID of the user")
    integration_id: Optional[str] = Field(None, description="The ID of the integration")

    class Settings:
        name = "subscriptions"
