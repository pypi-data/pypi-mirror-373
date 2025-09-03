from datetime import UTC, datetime, timedelta
from typing import Callable, Dict, List, Optional, Protocol

import httpx
from fastapi import HTTPException

from abs_integration_core.schema import Integration, SafeIntegration, Subscription, TokenData
from abs_integration_core.schema.common_schema import ListResourcesResponse
from abs_exception_core.exceptions import NotFoundError
from abs_utils.logger import setup_logger

logger = setup_logger(__name__)

class IntegrationServiceProtocol(Protocol):
    """Protocol defining the interface for integration services"""

    def get_auth_url(self, state: Optional[Dict] = None) -> Dict[str, str]:
        """
        Generate an authentication URL for OAuth flow.

        Args:
            state: Optional state dictionary to include in the OAuth flow

        Returns:
            A dictionary containing the auth URL and other necessary information
        """
        ...

    async def get_user_email(self, access_token: str) -> Optional[str]:
        """
        Get user email from the provider's userinfo endpoint.

        Args:
            access_token: The access token for the user

        Returns:
            User email if successful, None otherwise
        """
        ...

    async def handle_oauth_callback(self, code: str, user_id: int) -> TokenData:
        """
        Handle the OAuth callback and store tokens.

        Args:
            code: The authorization code from OAuth callback

        Returns:
            TokenData object
        """
        ...

    async def get_query_by_user_id(self, user_id: int):
        """Get the integration query by user_id"""
        ...

    async def get_all_integrations(
        self, find: Dict
    ) -> List[Integration]:
        """
        Get all integrations.

        Returns:
            List of TokenData objects
        """
        ...
    
    async def get_all_integrations_by_provider(
        self
    ) -> List[Integration]:
        """
        Get all integrations.

        Returns:
            List of TokenData objects
        """
        ...

    async def refresh_token(
        self, token_url: str, refresh_data: Dict, user_id: int, integration_uuid: str
    ) -> Optional[TokenData]:
        """
        Refresh the access token using the refresh token.

        Returns:
            Updated TokenData if successful, None otherwise
        """
        ...

    async def get_integration(self, user_id: int) -> Optional[TokenData]:
        """
        Get integration data.

        Returns:
            TokenData if integration exists, None otherwise
        """
        ...

    async def delete_integration(self, user_id: int, integration_uuid: str) -> bool:
        """
        Delete an integration.

        Returns:
            True if deleted, False otherwise
        """
        ...

    async def get_resource_subscription_method(self, resource_type: str) -> Callable:
        """
        Get the subscription method for a resource type.
        """
        ...

    async def subscribe(
        self,
        user_id: int,
        integration_uuid: str,
        target_url: str,
        site_id: str,
        resource_id: str,
        event_types: List[str] = ["created", "updated", "deleted"],
        expiration_days: int = 3,
    ) -> Dict:
        """
        Subscribe to a resource.
        """
        ...

    async def create_subscription(
        self,
        resource: str,
        change_type: str = "created,updated,deleted",
        expiration_days: int = 3,
    ) -> Dict:
        """
        Create a subscription for a resource.
        """
        ...

    async def delete_subscription(self, subscription_id: str, user_id: int) -> None:
        """
        Delete a subscription.
        """
        ...

    async def list_subscriptions(
        self, user_id: int, integration_uuid: str, page: int = 1, page_size: int = 10
    ) -> List[Subscription]:
        """
        List all subscriptions.
        """
        ...

    async def get_resource_path(
        self, resource_type: str, site_id: str, resource_id: str
    ) -> str:
        """
        Get the resource path for a SharePoint resource.
        """
        ...

    async def list_resources(self, user_id: int, integration_uuid: str, *args, **kwargs) -> ListResourcesResponse:
        """
        List all resources.
        """
        ...

    async def get_query_by_user_and_uuid(self, user_id: int, integration_uuid: str):
        """Get the integration query by user and UUID"""
        ...


class AbstractIntegrationBaseService(IntegrationServiceProtocol):
    """
    Base abstract class for all integration services.
    Any integration service should inherit from this class and implement its methods.
    """

    def set_provider_data(self, provider_name: str, token_url: str, scopes: str):
        self.provider_name = provider_name
        self.token_url = token_url
        self.scopes = scopes

    async def renew_subscription(
        self,
        subscription_id: str,
        expiration_days: int = 3,
        *args,
        **kwargs
    ) -> None:
        """
        Renew a subscription.
        """
        ...

    async def refresh_integration_token(self, user_id: int, integration_uuid: str) -> TokenData:
        """
        Refresh the access token using the refresh token.

        Returns:
            Updated TokenData if successful, None otherwise
        """
        refresh_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "scope": self.scopes,
        }
        return await self.refresh_token(self.token_url, refresh_data, user_id, integration_uuid)

    async def get_integration_token_data(self, code: str) -> TokenData:
        """
        Exchange authorization code for token data.

        Args:
            code: The authorization code from OAuth callback

        Returns:
            TokenData object with access_token, refresh_token and expires_in
        """
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_url,
            "grant_type": "authorization_code",
            "scope": self.scopes,
        }

        return await self.get_token_data(self.token_url, token_data)

    async def get_token_data(self, token_url: str, token_data: Dict) -> TokenData:
        """
        Exchange authorization code for token data.

        Args:
            code: The authorization code from OAuth callback

        Returns:
            TokenData object with access_token, refresh_token and expires_in
        """
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            token = token_response.json()

        expires_in = token.get("expires_in", 3600)
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

        return TokenData(
            access_token=token.get("access_token"),
            refresh_token=token.get("refresh_token"),
            expires_at=expires_at,
        )

    async def _verify_access_token(
        self, token_data: TokenData, user_id: int, integration_uuid: str
    ) -> TokenData:
        """
        Verify the access token and refresh it if it's close to expiration.

        Args:
            token_data: The token data to verify

        Returns:
            TokenData object - either the original if valid or a refreshed one
        """
        current_time = datetime.now(UTC)
        buffer_minutes = 5
        expiration_buffer = current_time + timedelta(minutes=buffer_minutes)

        # Ensure token_data.expires_at is also timezone-aware
        if token_data.expires_at.tzinfo is None:
            token_data.expires_at = token_data.expires_at.replace(tzinfo=UTC)

        if token_data.expires_at <= expiration_buffer:
            return await self.refresh_integration_token(user_id, integration_uuid)

        return token_data

    async def get_integration_tokens(self, user_id: int, integration_uuid: str) -> TokenData:
        """
        Get the integration tokens.
        """
        result = await self.get_query_by_user_and_uuid(user_id, integration_uuid)

        access_token = (
            result.get("access_token")
            if isinstance(result, dict)
            else result.access_token
        )
        refresh_token = (
            result.get("refresh_token")
            if isinstance(result, dict)
            else result.refresh_token
        )
        expires_at = (
            result.get("expires_at") if isinstance(result, dict) else result.expires_at
        )

        tokens = TokenData(
            access_token=self.encryption.decrypt_token(access_token),
            refresh_token=self.encryption.decrypt_token(refresh_token),
            expires_at=expires_at,
        )

        return await self._verify_access_token(tokens, user_id, integration_uuid)

    async def update_integration_status(self, user_id: int, integration_uuid: str) -> SafeIntegration:
        """
        Update the `is_active` status of an integration by verifying the user's email via the provider.

        This method attempts to retrieve the integration and its tokens, then calls `get_user_email` to
        check if the access token is still valid. If the email is successfully retrieved, the integration
        is considered active. If the active status has changed, the integration record is updated accordingly.

        Args:
            user_id (int): The user ID associated with the integration.
            integration_uuid (str): The UUID of the integration to update.

        Returns:
            SafeIntegration: The integration object with the updated `is_active` status.

        Raises:
            HTTPException: If an error occurs during the update process.
        """
        try:
            integration = await self.get_query_by_user_and_uuid(user_id, integration_uuid)

            token_data = await self.get_integration_tokens(user_id, integration_uuid)
            email = await self.get_user_email(token_data.access_token)

            is_active = email is not None
            update_data = {"is_active": is_active}

            is_integration_active = integration.get("is_active") if isinstance(integration, dict) else integration.is_active
            if is_active != is_integration_active:
                await self.update(integration["_id"], update_data)

            if isinstance(integration, dict):
                integration["is_active"] = is_active
            else:
                integration.is_active = is_active

            return SafeIntegration(**integration).model_dump(exclude_none=True)

        except NotFoundError as e:
            raise e

        except Exception as e:
            logger.error(f"Error updating integration status: {e}")
            update_data = {"is_active": False}
            try:
                await self.update(integration["_id"], update_data)
                if isinstance(integration, dict):
                    integration["is_active"] = update_data["is_active"]
                else:
                    integration.is_active = update_data["is_active"]

                return SafeIntegration(**integration).model_dump(exclude_none=True)

            except:
                pass

            raise HTTPException(f"Internal server error {e}")
