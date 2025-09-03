import json
import urllib.parse
from abc import ABC
from typing import Dict, Optional, List

import httpx
from abs_exception_core.exceptions import BadRequestError
from abs_utils.logger import setup_logger
from fastapi import Request
from abs_exception_core.exceptions import InternalServerError

from abs_integration_core.schema import (
    ListResourcesResponse,
    ResourceItem,
    PaginationInfo
)

logger = setup_logger(__name__)


class DocuSignIntegrationBaseService(ABC):
    async def get_user_email(self, access_token: str) -> Optional[str]:
        """
        Get user email from DocuSign's userinfo endpoint.
        
        Args:
            access_token: The access token for the user
            
        Returns:
            User email if successful, None otherwise
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://account-d.docusign.com/oauth/userinfo",
                    headers=headers
                )
                response.raise_for_status()
                
                user_info = response.json()
                return user_info.get("email")
                
        except Exception as e:
            logger.error(f"Failed to get user email from DocuSign: {str(e)}")
            return None

    def get_auth_url(self, state: Optional[Dict] = None) -> Dict[str, str]:
        """
        Generate an authentication URL for DocuSign OAuth flow.

        Args:
            state: Optional state dictionary to include in the OAuth flow

        Returns:
            A dictionary containing the auth URL and other necessary information
        """
        state_param = ""
        if state:
            try:
                # Convert state dict to JSON and URL encode it
                state_json = json.dumps(state)
                state_param = urllib.parse.quote(state_json)
            except Exception as e:
                raise InternalServerError(f"Error encoding state: {e}")

        params = {
            "response_type": "code",
            "scope": self.scopes,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_url,
            "state": state_param,
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())

        return {"auth_url": f"{self.docusign_auth_url}?{query_string}"}

    async def subscribe(self, user_id: int, integration_uuid: str, target_url: str, event_types: List[str], *args, **kwargs) -> Dict:
        """
        Subscribe to DocuSign webhook events.

        Args:
            user_id: The user ID
            integration_uuid: The integration UUID to use for authentication
            target_url: Target URL for webhook notifications

        Returns:
            Dictionary containing subscription details
        """
        token_data = await self.get_integration_tokens(user_id, integration_uuid)
        account_id = await self.get_account_id(user_id, integration_uuid)
        return await self.create_webhook_subscription(
            token_data.access_token, account_id, target_url, event_types
        )

    async def create_webhook_subscription(
        self,
        access_token: str,
        account_id: str,
        target_url: str,
        event_types: List[str],
    ) -> Dict:
        """
        Create a webhook subscription for DocuSign events.

        Args:
            access_token: The access token for DocuSign API
            account_id: The DocuSign account ID

        Returns:
            Dictionary containing subscription details
        """
        try:
            # Validate that all change_type elements are valid DocuSign events
            if event_types:
                invalid_events = [event for event in event_types if event not in self.events]
                if invalid_events:
                    error_detail = f"Invalid event types: {', '.join(invalid_events)}. Valid events are: {', '.join(self.events)}"
                    raise BadRequestError(detail=error_detail)

            name = f"GovAssist Webhook for {target_url}"
            webhook_config = {
                "configurationType": "custom",
                "urlToPublishTo": target_url,
                "name": name,
                "allowEnvelopePublish": "true",
                "enableLog": "true",
                "requiresAcknowledgement": "true",
                "signMessageWithX509Certificate": "false",
                "deliveryMode": "SIM",
                "events": event_types,
                "eventData": {"version": "restv2.1"},
                "allUsers": "true",
            }

            async with httpx.AsyncClient() as client:
                list_url = f"{self.docusign_api_url}/accounts/{account_id}/connect"
                response = await client.get(
                    list_url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    existing_configs_data = response.json()
                    configurations = existing_configs_data.get("configurations", [])

                    config_to_delete_id = None
                    for config in configurations:
                        if config.get("name") == name:
                            config_to_delete_id = config.get("connectId")
                            break

                    if config_to_delete_id:
                        delete_url = f"{self.docusign_api_url}/accounts/{account_id}/connect/{config_to_delete_id}"
                        await client.delete(
                            delete_url,
                            headers={"Authorization": f"Bearer {access_token}"},
                        )

                        try:
                            await self.subscription_service.remove_by_uuid(
                                f"docusign_{config_to_delete_id}"
                            )
                        except Exception as e:
                            if "not found" in str(e):
                                logger.info(
                                    f"Subscription with id {config_to_delete_id} not found"
                                )
                            else:
                                logger.error(f"Error deleting subscription: {str(e)}")
                                raise e

                    create_url = (
                        f"{self.docusign_api_url}/accounts/{account_id}/connect"
                    )
                    response = await client.post(
                        create_url,
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json",
                        },
                        json=webhook_config,
                    )

                    if response.status_code not in (200, 201):
                        error_body_text = response.text
                        error_detail = f"Failed to create webhook configuration. Status: {response.status_code}. Body: {error_body_text}"
                        raise BadRequestError(detail=error_detail)

                    response_data = response.json()
                    subscription_id = response_data.get("connectId")

                    return {
                        "id": f"docusign_{subscription_id}",
                        "resourceType": "envelope",
                        "siteId": "envelope",
                        "resourceId": "envelope",
                        "changeType": "created, updated, deleted",
                    }

                else:
                    error_detail = f"Failed to list configurations: {response.text}"
                    logger.error(f"[DocuSign] Error: {error_detail}")
                    raise BadRequestError(detail=error_detail)

        except Exception as e:
            error_detail = f"Error processing webhook subscription: {str(e)}"
            logger.error(f"[DocuSign] Error: {error_detail}")
            raise BadRequestError(detail=error_detail)

    async def get_account_id(self, user_id: int, integration_uuid: str) -> str:
        """
        Get the DocuSign account ID for the authenticated user.
        This is required for making API calls to DocuSign.

        Returns:
            str: The DocuSign account ID

        Raises:
            BadRequestError: If unable to get account ID
        """
        try:
            token_data = await self.get_integration_tokens(user_id, integration_uuid)
            user_info_url = "https://account-d.docusign.com/oauth/userinfo"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    user_info_url,
                    headers={"Authorization": f"Bearer {token_data.access_token}"},
                )

                response.raise_for_status()
                user_info = response.json()

            accounts = user_info.get("accounts", [])
            account_id = accounts[0].get("account_id")
            return account_id

        except httpx.HTTPStatusError as http_err:
            logger.error(
                f"[DocuSign get_account_id] Error (HTTPStatusError): {str(http_err)}"
            )
            raise BadRequestError(detail=str(http_err))

        except Exception as e:
            logger.error(f"[DocuSign get_account_id] Error (Exception): {str(e)}")
            raise BadRequestError(detail=str(e))

    async def list_resources(self, user_id: int, integration_uuid: str, *args, **kwargs) -> ListResourcesResponse:
        """
        List all resources for the DocuSign account.

        Args:
            user_id: The user ID
            integration_uuid: The integration UUID to use for authentication

        Returns:
            ListResourcesResponse containing list of event types and their details
        """
        # Convert event strings to ResourceItem objects
        resources = [
            ResourceItem(
                id=event,
                name=event.replace("-", " ").title(),
                type="event",
                size=0,
                description=f"DocuSign webhook event: {event}",
                can_subscribe=True,
                has_children=False
            )
            for event in self.events
        ]

        return ListResourcesResponse(
            resources=resources,
            total_count=len(resources),
            current_path="",
            pagination=PaginationInfo(has_next_page=False, next_page_token=None)
        )

    async def list_subscriptions(
        self, user_id: int, integration_uuid: str, page: int = 1, page_size: int = 10, *args, **kwargs
    ) -> Dict:
        """
        List all webhook subscriptions for the DocuSign account using direct API calls.

        Args:
            user_id: The user ID
            integration_uuid: The integration UUID to use for authentication
            page: Page number for pagination
            page_size: Number of items per page

        Returns:
            Dictionary containing list of subscriptions and their details
        """
        return await self.subscription_service.list_subscriptions(
            find={
                "filters":{
                    "operator": "and",
                    "conditions": [
                        {
                            "field": "integration_id",
                            "operator": "eq",
                            "value": integration_uuid
                        },
                        {
                            "field": "user_id",
                            "operator": "eq",
                            "value": user_id
                        }
                    ],
                    "page": page,
                    "page_size": page_size
                }
            }
        )

    async def delete_subscription(self, subscription_id: str, user_id: int) -> Dict:
        """
        Delete a webhook subscription.

        Args:
            subscription_id: The ID of the subscription to delete

        Returns:
            Dictionary containing deletion status
        """
        try:
            subscription = await self.subscription_service.get_by_user_and_uuid(
                user_id, subscription_id, self.provider_name
            )
            account_id = await self.get_account_id(subscription["user_id"], subscription["integration_id"])
            token_data = await self.get_integration_tokens(subscription["user_id"], subscription["integration_id"])

            if not token_data or not token_data.access_token:
                raise ValueError(
                    "Failed to retrieve valid access token for delete_subscription"
                )

            access_token = token_data.access_token

            subscription_id = subscription_id.replace("docusign_", "")
            delete_url = f"{self.docusign_api_url}/accounts/{account_id}/connect/{subscription_id}"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.delete(delete_url, headers=headers)
                response.raise_for_status()

        except httpx.HTTPStatusError as http_err:
            logger.error(
                f"[DocuSign delete_subscription] Error (HTTPStatusError): {str(http_err)}"
            )
            raise BadRequestError(detail=str(http_err))
