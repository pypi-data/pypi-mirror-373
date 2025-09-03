import json
import urllib.parse
import uuid
from abc import ABC
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import httpx
from abs_utils.logger import setup_logger
from abs_exception_core.exceptions import InternalServerError

from abs_integration_core.schema import (
    ListResourcesResponse,
    ResourceItem,
    PaginationInfo,
    NavigationPath,
    Subscription
)

logger = setup_logger(__name__)


class GoogleIntegrationBaseService(ABC):
    def _convert_expiration_to_datetime(self, expiration_ms: str) -> Optional[datetime]:
        """
        Convert Google Drive expiration timestamp from milliseconds to datetime.
        
        Args:
            expiration_ms: Expiration timestamp in milliseconds (as string)
            
        Returns:
            Timezone-aware datetime object or None if conversion fails
        """
        if not expiration_ms:
            return None
        
        try:
            expiration_seconds = int(expiration_ms) / 1000
            return datetime.fromtimestamp(expiration_seconds, tz=timezone.utc)
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to convert expiration timestamp {expiration_ms}: {str(e)}")
            return None

    async def get_user_email(self, access_token: str) -> Optional[str]:
        """
        Get user email from Google's userinfo endpoint.
        
        Args:
            access_token: The access token for the user
            
        Returns:
            User email if successful, None otherwise
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers=headers
                )
                response.raise_for_status()
                
                user_info = response.json()

                return user_info.get("email")
                
        except Exception as e:
            logger.error(f"Failed to get user email from Google: {str(e)}")
            return None

    def get_auth_url(self, state: Optional[Dict] = None) -> Dict[str, str]:
        """
        Generate an authentication URL for OAuth flow.

        Args:
            state: Optional state dictionary to include in the OAuth flow

        Returns:
            A dictionary containing the auth URL and other necessary information
        """
        if state:
            try:
                # Convert state dict to JSON and URL encode it
                state_json = json.dumps(state)
                state_param = urllib.parse.quote(state_json)
            except Exception as e:
                raise InternalServerError(f"Error encoding state: {e}")

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_url,
            "response_type": "code",
            "scope": self.scopes,
            "access_type": "offline",
            "prompt": "consent",
            "state": state_param,
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())

        return {"auth_url": f"{self.google_auth_url}?{query_string}"}

    async def get_subscription_by_resource_id(
        self, resource_id: Optional[str] = None, user_id: int = None
    ) -> Optional[str]:
        """
        Get the site and channel ID for a Google Drive resource.
        """
        subscriptions_db = await self.subscription_service.list_subscriptions(
            find={
                "filters":{
                    "operator": "and",
                    "conditions": [
                        {
                            "field": "site_id",
                            "operator": "eq",
                            "value": resource_id
                        },
                        {
                            "field": "user_id",
                            "operator": "eq",
                            "value": user_id
                        }
                    ],
                    "page": 1,
                    "page_size": 1
                }
            }
        )

        subscriptions = subscriptions_db.get("founds", [])
        for sub in subscriptions:
            if sub.get("site_id") == resource_id:
                return sub.get("uuid")

        return None

    async def subscribe(
        self,
        user_id: int,
        integration_uuid: str,
        resource_id: str,
        target_url: str,
        expiration_days: int = 3,
        *args,
        **kwargs,
    ) -> Dict:
        """
        Subscribe to a Google Drive resource.

        Args:
            user_id: The user ID
            integration_uuid: The integration UUID to use for authentication
            resource_id: Google Drive file/folder ID
            target_url: Target URL for webhook notifications
            expiration_days: Number of days until subscription expires

        Returns:
            Dictionary containing subscription details
        """
        if not resource_id:
            raise ValueError("Resource ID is required")

        subscription_id = await self.get_subscription_by_resource_id(
            resource_id, user_id
        )
        subscription_deleted = False

        if subscription_id:
            subscription_deleted = await self.delete_subscription(
                subscription_id, user_id, target_url
            )

        subscription_data = await self.create_subscription(
            user_id=user_id,
            integration_uuid=integration_uuid,
            resource=resource_id,
            target_url=target_url,
            expiration_days=expiration_days,
        )

        if subscription_deleted:
            logger.info(f"Removing old subscription from database: {subscription_id}")
            await self.subscription_service.remove_by_uuid(subscription_id)
        subscription_data["siteId"] = resource_id

        return subscription_data

    async def create_subscription(
        self,
        user_id: int,
        integration_uuid: str,
        resource: str,
        target_url: str,
        expiration_days: int = 3,
    ) -> Dict:
        """
        Create a subscription for a Google Drive resource.

        Args:
            integration_uuid: The integration UUID to use for authentication
            resource: Resource ID to watch
            target_url: Target URL for webhook notifications
            expiration_days: Number of days until subscription expires

        Returns:
            Dictionary containing subscription details
        """
        token_data = await self.get_integration_tokens(user_id, integration_uuid)
        expiration_time = datetime.utcnow() + timedelta(
            days=expiration_days
        )
        expiration_ms = int(expiration_time.timestamp() * 1000)

        new_channel_id = str(uuid.uuid4())

        headers = {
            "Authorization": f"Bearer {token_data.access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            watch_request = {
                "id": new_channel_id,
                "type": "web_hook",
                "address": target_url,
                "expiration": expiration_ms,
                "resourceId": resource,
            }

            response = await client.post(
                f"{self.drive_api_url}/files/{resource}/watch",
                headers=headers,
                json=watch_request,
            )

            if response.status_code != 200:
                raise Exception(f"Failed to create subscription: {response.text}")

            response_data = response.json()
            
            # Convert expiration from milliseconds to datetime
            expiration_ms = response_data.get("expiration")
            expires_at = self._convert_expiration_to_datetime(expiration_ms)
            if expires_at:
                response_data["expires_at"] = expires_at.isoformat()
            
            return response_data

    async def renew_subscription(
        self,
        subscription_id: str,
        expiration_days: int = 3,
        *args,
        **kwargs,
    ) -> None:
        """
        Renew a Google Drive subscription.

        Args:
            subscription_id: ID of the subscription to renew
            expiration_days: Number of days until new expiration

        Returns:
            Dictionary containing updated subscription details
        """
        existing_subscription = await self.subscription_service.get_by_attr(
            "uuid", subscription_id
        )

        subscription = await self.subscribe(
            resource_id=existing_subscription["site_id"],
            expiration_days=expiration_days,
            target_url=existing_subscription["target_url"],
            user_id=existing_subscription["user_id"],
            integration_uuid=existing_subscription["integration_id"]
        )
        
        await self.subscription_service.create(
            Subscription(
                uuid=subscription["id"],
                target_url=existing_subscription["target_url"],
                site_id=subscription.get("siteId", None),
                resource_id=subscription.get("resourceId", None),
                target_path=existing_subscription["target_path"],
                event_types=existing_subscription["event_types"],
                provider_name=self.provider_name.lower(),
                user_id=existing_subscription["user_id"],
                integration_id=existing_subscription["integration_id"],
                expires_at=subscription.get("expires_at", None)
            )
        )


    async def delete_subscription(
        self,
        subscription_id: str,
        user_id: int,
        target_url: Optional[str] = None,
    ) -> bool:
        """
        Delete a Google Drive subscription.

        Args:
            subscription_id: ID of the subscription to delete
        """
        subscription = await self.subscription_service.get_by_user_and_uuid(
            user_id, subscription_id, self.provider_name
        )
        if target_url:
            if target_url != subscription["target_url"]:
                return False

        site_id = subscription["site_id"]

        token_data = await self.get_integration_tokens(subscription["user_id"], subscription["integration_id"])
        headers = {
            "Authorization": f"Bearer {token_data.access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                stop_request = {"id": subscription_id, "resourceId": subscription["resource_id"]}

                logger.info(f"Attempting to stop channel: {subscription_id}")
                response = await client.post(
                    f"{self.drive_api_url}/channels/stop",
                    headers=headers,
                    json=stop_request,
                )

                if response.status_code == 204:
                    logger.info("Successfully stopped existing subscription")
                else:
                    logger.error(
                        f"Unexpected response when stopping subscription: {response.status_code}"
                    )
                    if response.content:
                        logger.error(response.json())

            except Exception as e:
                logger.error(f"Error stopping existing subscription: {str(e)}")

        return True

    async def get_folder_by_path(self, user_id: int, integration_uuid: str, folder_path: str) -> Optional[str]:
        """
        Get folder ID by path. Google Drive doesn't have native path support,
        so we need to traverse the folder structure.

        Args:
            user_id: The user ID
            folder_path: The folder path (e.g., "Documents/Work/Projects")

        Returns:
            Folder ID if found, None otherwise
        """
        if not folder_path:
            return None

        token_data = await self.get_integration_tokens(user_id, integration_uuid)
        headers = {"Authorization": f"Bearer {token_data.access_token}"}

        # Split path into parts
        path_parts = [part.strip() for part in folder_path.split("/") if part.strip()]
        current_parent_id = "root"  # Start from root

        for folder_name in path_parts:
            # Search for folder with this name in current parent
            params = {
                "q": f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{current_parent_id}' in parents and trashed=false",
                "fields": "files(id,name)",
                "pageSize": 1,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.drive_api_url}/files", headers=headers, params=params
                )
                if response.status_code != 200:
                    logger.error(
                        f"Failed to search for folder {folder_name}: {response.text}"
                    )
                    return None

                data = response.json()
                files = data.get("files", [])

                if not files:
                    logger.warning(
                        f"Folder '{folder_name}' not found in parent '{current_parent_id}'"
                    )
                    return None

                current_parent_id = files[0]["id"]

        return current_parent_id

    async def list_resources(
        self,
        user_id: int,
        integration_uuid: str,
        page_token: Optional[str] = None,
        folder_path: Optional[str] = None,
        page_size: int = 40,
        *args,
        **kwargs,
    ) -> ListResourcesResponse:
        """
        List Google Drive resources with folder navigation and pagination support.

        Args:
            user_id: The user ID
            integration_uuid: The integration UUID to use for authentication
            page_token: Optional token for fetching the next page of results
            folder_path: Optional folder path to navigate to
            page_size: Optional page size for pagination

        Returns:
            ListResourcesResponse containing files list, navigation info, and pagination
        """
        token_data = await self.get_integration_tokens(user_id, integration_uuid)
        headers = {"Authorization": f"Bearer {token_data.access_token}"}

        # Determine the parent folder ID
        parent_id = "root"
        if folder_path:
            parent_id = await self.get_folder_by_path_with_uuid(integration_uuid, folder_path)
            if not parent_id:
                return ListResourcesResponse(
                    resources=[],
                    total_count=0,
                    current_path=folder_path,
                    pagination=PaginationInfo(has_next_page=False, next_page_token=None)
                )

        # Build query parameters
        params = {
            "fields": "nextPageToken, files(id,name,mimeType,webViewLink,createdTime,modifiedTime,size,parents)",
            "pageSize": page_size,
            "orderBy": "folder,name",
            "q": f"'{parent_id}' in parents and trashed=false",
        }

        if page_token:
            params["pageToken"] = page_token

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.drive_api_url}/files", headers=headers, params=params
            )
            if response.status_code != 200:
                raise Exception(f"Failed to list resources: {response.text}")

            data = response.json()
            files = data.get("files", [])

            # Process files using list comprehension for better performance
            resources = [
                ResourceItem(
                    id=file.get("id"),
                    name=file.get("name"),
                    type="folder" if file.get("mimeType") == "application/vnd.google-apps.folder" else "file",
                    size=file.get("size", 0),
                    web_url=file.get("webViewLink"),
                    created_date_time=file.get("createdTime"),
                    last_modified_date_time=file.get("modifiedTime"),
                    mime_type=file.get("mimeType"),
                    can_subscribe=file.get("mimeType") == "application/vnd.google-apps.folder",
                    has_children=file.get("mimeType") == "application/vnd.google-apps.folder",
                    navigation_path=NavigationPath(
                        folder_path=f"{folder_path}/{file['name']}" if folder_path else file["name"]
                    ) if file.get("mimeType") == "application/vnd.google-apps.folder" else None
                )
                for file in files
            ]

            return ListResourcesResponse(
                resources=resources,
                total_count=len(resources),
                current_path=folder_path or "",
                pagination=PaginationInfo(
                    has_next_page=bool(data.get("nextPageToken")),
                    next_page_token=data.get("nextPageToken")
                )
            )

    async def list_subscriptions(
        self, user_id: int, integration_uuid: str, page: int = 1, page_size: int = 10
    ) -> List[Dict]:
        """
        List all active Google Drive subscriptions from the database and validate them.

        Returns:
            List of subscription details including:
            - id: The subscription ID
            - resourceId: The resource ID being watched
            - resourceName: Name of the resource
            - resourceType: Type of resource (file, folder, drive)
            - expiration: When the subscription expires
            - address: The webhook URL
            - status: Whether the subscription is still valid
        """
        subscriptions_db = await self.subscription_service.list_subscriptions(
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

        if not subscriptions_db:
            return []

        return subscriptions_db
