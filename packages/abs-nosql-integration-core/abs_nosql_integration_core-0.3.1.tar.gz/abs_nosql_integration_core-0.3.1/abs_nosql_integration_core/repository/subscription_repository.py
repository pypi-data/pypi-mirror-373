from abs_nosql_integration_core.model import SubscriptionDocument
from abs_nosql_integration_core.schema.subscription_schema import Subscription as SubscriptionSchema
from abs_nosql_repository_core.repository.base_repository import BaseRepository
from abs_nosql_repository_core.schema import ListFilter
from typing import List


class SubscriptionsRepository(BaseRepository):
    def __init__(self):
        super().__init__(SubscriptionDocument)

    async def create(self, schema: SubscriptionSchema, collection_name: str = None) -> dict:
        subscription = SubscriptionSchema(
            **schema.model_dump()
        )
        return await super().create(subscription, collection_name)
