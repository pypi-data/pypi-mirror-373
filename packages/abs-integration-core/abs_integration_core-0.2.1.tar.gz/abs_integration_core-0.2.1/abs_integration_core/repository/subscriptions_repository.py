from abs_integration_core.models import Subscription
from abs_integration_core.schema import Subscription as SubscriptionSchema
from typing import Callable
from sqlalchemy.orm import Session
from abs_repository_core.repository import BaseRepository
from typing import List
from abs_repository_core.schemas.base_schema import FilterSchema, FindBase


class SubscriptionsRepository(BaseRepository):
    def __init__(self, db: Callable[..., Session]):
        super().__init__(db, Subscription)
        
    
    def create(self, schema: SubscriptionSchema) -> Subscription:
        subscription = Subscription(
            **schema.model_dump()
        )
        return super().create(subscription)
