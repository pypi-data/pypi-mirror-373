from abs_integration_core.repository import SubscriptionsRepository
from abs_repository_core.services.base_service import BaseService
from abs_integration_core.schema import Subscription
from abs_repository_core.schemas import FilterSchema, FindBase
from typing import List, Dict
from abs_exception_core.exceptions import NotFoundError


class SubscriptionService(BaseService):
    def __init__(self, subscription_repository: SubscriptionsRepository):
        super().__init__(subscription_repository)

    async def create(self, schema: Subscription) -> Subscription:
        subscription = super().add(schema)
        return subscription

    async def remove_by_uuid(self, uuid: str) -> Subscription:
        id = self.get_by_attr("uuid", uuid).id
        return super().remove_by_id(id)

    async def list_subscriptions(self, find: Dict) -> List[Subscription]:
        return await super().get_list(FindBase(**find))
    
    async def get_user_id_by_subscription_id(self, subscription_id: str) -> int:
        """
        Get the user ID by subscription ID.
        """
        list_filter = FilterSchema(
            operator="AND",
            conditions=[
                {
                    "field": "target_url",
                    "operator": "like",
                    "value": f"/{subscription_id}"
                }
            ]
        )

        result = super().get_list(
            schema=FindBase(
                filters=list_filter,
                page=1,
                page_size=1
            )
        )

        if result.founds:
            return result.founds[0].user_id
        else:
            raise NotFoundError("Subscription not found")

    async def get_by_user_and_uuid(self, user_id: int, uuid: str, provider_name: str) -> Subscription:
        """
        Get a subscription by user ID and UUID.
        """
        list_filter = FilterSchema(
            operator="AND",
            conditions=[
                {
                    "field": "user_id",
                    "operator": "eq",
                    "value": user_id
                },
                {
                    "field": "uuid",
                    "operator": "eq",
                    "value": uuid
                },
                {
                    "field": "provider_name",
                    "operator": "eq",
                    "value": provider_name
                }
            ]
        )

        result = super().get_list(
            schema=FindBase(
                filters=list_filter,
                page=1,
                page_size=1
            )
        )

        if result.founds:
            return result.founds[0]
        else:
            raise NotFoundError("Subscription not found")
