import json
import secrets
import urllib.parse
from abc import ABC
from typing import Dict, Optional, List
from datetime import datetime, timedelta, timezone, UTC

import httpx
from abs_exception_core.exceptions import InternalServerError
from abs_utils.logger import setup_logger



logger = setup_logger(__name__)


class OutlookIntegrationBaseService(ABC):
    async def get_user_email(self, access_token: str) -> Optional[str]:
        """
        Get user email from Microsoft Graph's me endpoint.
        
        Args:
            access_token: The access token for the user
            
        Returns:
            User email if successful, None otherwise
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.graph_api_url}/me",
                    headers=headers
                )
                response.raise_for_status()
                
                user_info = response.json()
                return user_info.get("mail") or user_info.get("userPrincipalName")
                
        except Exception as e:
            logger.error(f"Failed to get user email from Microsoft Graph: {str(e)}")
            return None

    def get_auth_url(self, state: Optional[Dict] = None) -> Dict[str, str]:
        """
        Generate an authentication URL for Microsoft Outlook OAuth flow.
        Returns both the auth URL and the state for verification.

        Args:
            state: Optional state dictionary to include in the OAuth flow
        """
        # Generate CSRF token
        csrf_token = secrets.token_urlsafe(16)

        # Prepare state parameter
        state_param = csrf_token
        if state:
            try:
                # Convert state dict to JSON and URL encode it
                state_json = json.dumps(state)
                state_param = urllib.parse.quote(state_json)
            except Exception as e:
                raise InternalServerError(f"Error encoding state: {e}")

        auth_url = (
            f"{self.authority}/oauth2/v2.0/authorize?"
            f"client_id={self.client_id}&"
            f"response_type=code&"
            f"redirect_uri={self.redirect_url}&"
            f"scope={self.scopes}&"
            f"state={state_param}&"
            f"prompt=select_account"
        )

        return {"auth_url": auth_url, "state": state_param}
    
    async def subscribe(
        self,
        user_id: int,
        integration_uuid: str,
        target_url: str,
        event_types: Optional[List[str]] = None,
        expiration_days: int = 3,
        *args,
        **kwargs,
    ) -> Dict:
        """
        Subscribe to Outlook resource changes.

        Args:
            user_id: The user ID
            integration_uuid: The integration UUID to use for authentication
            target_url: Target URL for webhook notifications
            resource_type: Type of resource to subscribe to (messages, events, contacts)
            event_types: Types of events to subscribe to (created, updated, deleted)
            expiration_days: Number of days until subscription expires (max 6)

        Returns:
            Dictionary containing subscription details
        """
        if event_types is None:
            event_types = ["created", "updated", "deleted"]
        
        subscription = await self.create_subscription(
            user_id=user_id,
            integration_uuid=integration_uuid,
            resource="/me/messages",
            target_url=target_url,
            event_types=event_types,
            expiration_days=min(expiration_days, 6),  # Outlook max is ~6.99 days (10070 minutes)
        )

        return subscription

    async def create_subscription(
        self,
        user_id: int,
        integration_uuid: str,
        resource: str,
        target_url: str,
        event_types: List[str],
        expiration_days: int = 6,
        *args,
        **kwargs
    ) -> Dict:
        """
        Create a subscription for the specified resource.

        Args:
            user_id: The user ID for authentication
            integration_uuid: The integration UUID to use for authentication
            resource: The resource path (e.g., "/me/messages")
            target_url: Target URL for webhook notifications
            event_types: Types of events (created, updated, deleted)
            expiration_days: Number of days until subscription expires (max 6)

        Returns:
            Dictionary containing subscription details
        """
        try:
            # Get valid access token
            token_data = await self.get_integration_tokens(user_id, integration_uuid)
            
            # Check account type for subscription support
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"{self.graph_api_url}/me",
                    headers={"Authorization": f"Bearer {token_data.access_token}"},
                )
                user_info = user_response.json()
                
                # Check if it's a personal account
                upn = user_info.get('userPrincipalName', '')
                is_personal = any(domain in upn.lower() for domain in ['outlook.com', 'hotmail.com', 'live.com', 'gmail.com'])
                
                if is_personal:
                    raise InternalServerError("Personal Microsoft accounts do not support webhook subscriptions. Please use a Work/School account (Office 365/Microsoft 365).")

            # Calculate expiration time (max 10070 minutes for Outlook)
            max_minutes = 10070  # Microsoft Graph API limit
            expiration_minutes = min(expiration_days * 24 * 60, max_minutes)
            expiration = datetime.now(UTC) + timedelta(minutes=expiration_minutes)

            client_state = secrets.token_urlsafe(16)
            subscription_data = {
                "changeType": ",".join(event_types),
                "notificationUrl": target_url,
                "resource": resource,
                "expirationDateTime": expiration.isoformat(),
                "clientState": client_state,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.graph_api_url}/subscriptions",
                    headers={"Authorization": f"Bearer {token_data.access_token}"},
                    json=subscription_data,
                )

                if response.status_code != 201:
                    error_detail = response.json()
                    
                    # Provide user-friendly error messages
                    if response.status_code == 401:
                        raise InternalServerError("Unauthorized: Your account may be a personal Microsoft account (not supported) or missing required permissions. Please use a Work/School account with proper permissions.")
                    elif response.status_code == 403:
                        raise InternalServerError("Forbidden: Your account lacks necessary permissions or licenses for webhook subscriptions. Please contact your administrator.")
                    elif response.status_code == 404:
                        raise InternalServerError("Not Found: Your mailbox is either inactive, soft-deleted, or hosted on-premise. Please ensure you have an active Microsoft 365 mailbox.")
                    else:
                        raise InternalServerError(f"Failed to create subscription: {error_detail.get('error', {}).get('message', 'Unknown error')}")
                
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating subscription: {e}")
            raise InternalServerError(f"Failed to create subscription: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating subscription: {e}")
            raise InternalServerError(f"Subscription creation failed: {str(e)}")

    async def renew_subscription(
        self,
        subscription_id: str,
        user_id: int,
        expiration_days: int = 6,
        *args,
        **kwargs
    ) -> Dict:
        """
        Renew a subscription by extending its expiration time.

        Args:
            subscription_id: The subscription ID to renew
            user_id: The user ID for authentication
            expiration_days: Number of days to extend (max 6)

        Returns:
            Dictionary containing updated subscription details
        """
        try:
            # Get existing subscription details
            subscription = await self.subscription_service.get_by_user_and_uuid(
                user_id, subscription_id, self.provider_name
            )
            token_data = await self.get_integration_tokens(user_id, subscription["integration_id"])

            # Check account type for subscription support
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"{self.graph_api_url}/me",
                    headers={"Authorization": f"Bearer {token_data.access_token}"},
                )
                user_info = user_response.json()
                
                # Check if it's a personal account
                upn = user_info.get('userPrincipalName', '')
                is_personal = any(domain in upn.lower() for domain in ['outlook.com', 'hotmail.com', 'live.com', 'gmail.com'])
                
                if is_personal:
                    raise InternalServerError("Personal Microsoft accounts do not support webhook subscriptions. Please use a Work/School account (Office 365/Microsoft 365).")

            # Calculate new expiration time (max 10070 minutes for Outlook)
            max_minutes = 10070  # Microsoft Graph API limit
            expiration_minutes = min(expiration_days * 24 * 60, max_minutes)
            new_expiration = datetime.now(UTC) + timedelta(minutes=expiration_minutes)

            # Update subscription with new expiration time
            update_data = {
                "expirationDateTime": new_expiration.isoformat()
            }

            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.graph_api_url}/subscriptions/{subscription_id}",
                    headers={"Authorization": f"Bearer {token_data.access_token}"},
                    json=update_data,
                )

                if response.status_code != 200:
                    error_detail = response.json()
                    
                    # Provide user-friendly error messages
                    if response.status_code == 401:
                        raise InternalServerError("Unauthorized: Your account may be a personal Microsoft account (not supported) or missing required permissions. Please use a Work/School account with proper permissions.")
                    elif response.status_code == 403:
                        raise InternalServerError("Forbidden: Your account lacks necessary permissions or licenses for webhook subscriptions. Please contact your administrator.")
                    elif response.status_code == 404:
                        raise InternalServerError("Not Found: The subscription may have expired or been deleted. Please create a new subscription.")
                    else:
                        raise InternalServerError(f"Failed to renew subscription: {error_detail.get('error', {}).get('message', 'Unknown error')}")
                
                response.raise_for_status()

                await self.subscription_service.update(
                    subscription["_id"],
                    {"expiration_time": response.json().get("expirationDateTime")}
                )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error renewing subscription: {e}")
            raise InternalServerError(f"Failed to renew subscription: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error renewing subscription: {e}")
            raise InternalServerError(f"Subscription renewal failed: {str(e)}")

    async def delete_subscription(
        self,
        subscription_id: str,
        user_id: int,
        *args,
        **kwargs
    ) -> bool:
        """
        Delete a subscription by its ID.

        Args:
            subscription_id: The subscription ID to delete
            user_id: The user ID for authentication

        Returns:
            True if deletion was successful
        """
        try:
            subscription = await self.subscription_service.get_by_user_and_uuid(
                user_id, subscription_id, self.provider_name
            )
            token_data = await self.get_integration_tokens(user_id, subscription["integration_id"])

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.graph_api_url}/subscriptions/{subscription_id}",
                    headers={"Authorization": f"Bearer {token_data.access_token}"},
                )
                
                if response.status_code == 204:
                    logger.info(f"Successfully deleted subscription: {subscription_id}")
                    return True
                else:
                    logger.error(f"Failed to delete subscription: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting subscription {subscription_id}: {str(e)}")
            return False