from abs_repository_core.repository import BaseRepository
from abs_integration_core.models import Integration
from typing import Callable, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from abs_integration_core.schema import CreateIntegration
from abs_integration_core.schema import TokenData
from abs_exception_core.exceptions import NotFoundError
from abs_repository_core.schemas import FilterSchema, FindBase


class IntegrationRepository(BaseRepository):
    def __init__(self, db: Callable[..., Session]):
        self.db = db
        super().__init__(db, Integration)
    
    def create_integration(self, integration_data: CreateIntegration) -> Integration:
        """
        Create a new integration record.
        
        Args:
            integration_data: Integration data including provider_name, access_token, etc.
            
        Returns:
            The created integration object
            
        Raises:
            DuplicatedError: If integration with same provider already exists
        """
        new_integration = Integration(
            provider_name=integration_data.provider_name,
            access_token=integration_data.access_token,
            refresh_token=integration_data.refresh_token,
            expires_at=integration_data.expires_at,
            user_id=integration_data.user_id,
            email=integration_data.email
        )

        existing_integration = self.get_by_provider_user_email(
            provider_name=integration_data.provider_name,
            user_id=integration_data.user_id,
            email=integration_data.email
        )
        if existing_integration:
            integration_id = existing_integration.get("id","")
            return self.update(integration_id, new_integration)
        else:
            return super().create(new_integration)
    
    def refresh_token(
        self,
        integration_id: int, 
        token_data: TokenData
    ) -> Integration:
        """
        Update token information for a specific integration.
        
        Args:
            provider_name: The integration provider name
            token_data: The data to update
            
        Returns:
            The updated integration object
            
        Raises:
            NotFoundError: If integration doesn't exist
        """
        integration_data = super().update(integration_id, token_data)

        return integration_data

    async def get_by_user_and_uuid(self, user_id: int, uuid: str, provider_name: str) -> Optional[Integration]:
        """
        Get integration by UUID.
        
        Args:
            uuid: The integration UUID
            
        Returns:
            The integration object if found, None otherwise
        """
        conditions = [
            {"field": "uuid", "operator": "eq", "value": uuid},
            {"field": "user_id", "operator": "eq", "value": user_id},
            {"field": "provider_name", "operator": "eq", "value": provider_name}
        ]
        
        find_query = FilterSchema(operator="AND", conditions=conditions)
        result = await super().read_by_options(find=FindBase(filters=find_query, page=1, page_size=1))
        
        if result.founds > 0:
            return result.founds[0]
        return None
    
    async def get_by_provider_user_email(
        self,
        provider_name: str,
        user_id: int,
        email: str
    ) -> Optional[Integration]:
        """
        Get integration by provider name, user ID, and email.
        
        Args:
            provider_name: The integration provider name
            user_id: The user ID
            email: The user email
            
        Returns:
            The integration object if found, None otherwise
        """
        conditions = [
            {"field": "provider_name", "operator": "eq", "value": provider_name},
            {"field": "user_id", "operator": "eq", "value": user_id},
            {"field": "email", "operator": "eq", "value": email}
        ]
        
        find_query = FilterSchema(operator="AND", conditions=conditions)
        result = await super().read_by_options(find=FindBase(filters=find_query, page=1, page_size=1))
        
        if result.founds > 0:
            return result.founds[0]
        return None
