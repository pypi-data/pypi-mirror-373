import base64
import json
import secrets
import urllib.parse
from abc import ABC
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional, Literal

import httpx
from abs_exception_core.exceptions import InternalServerError
from abs_utils.logger import setup_logger
from fastapi import HTTPException
import asyncio
import time

from abs_integration_core.schema import (
    Subscription,
    ListResourcesResponse,
    ResourceItem,
    PaginationInfo,
    NavigationPath
)

logger = setup_logger(__name__)


class SharepointIntegrationBaseService(ABC):
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
        Generate an authentication URL for Microsoft SharePoint OAuth flow.
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
        site_id: str,
        resource_id: str,
        expiration_days: int = 3,
        *args,
        **kwargs,
    ) -> Subscription:
        """
        Subscribe to a resource.

        Args:
            user_id: The user ID
            integration_uuid: The integration UUID to use for authentication
            target_url: Target URL for webhook notifications
            site_id: SharePoint site ID
            resource_id: SharePoint resource ID
            expiration_days: Number of days until subscription expires
        """
        if not resource_id:
            raise ValueError("Resource ID is required")
        if not site_id:
            raise ValueError("Site ID is required")

        subscription = await self.create_subscription(
            user_id=user_id,
            integration_uuid=integration_uuid,
            resource=f"/sites/{site_id}/lists/{resource_id}",
            expiration_days=expiration_days,
            target_url=target_url,
        )

        return subscription

    async def create_subscription(
        self,
        user_id: int,
        integration_uuid: str,
        resource: str,
        target_url: str,
        expiration_days: int = 3,
    ) -> Dict:
        """
        Create a subscription for SharePoint list or folder changes.

        Args:
            user_id: The user ID
            integration_uuid: The integration UUID to use for authentication
            resource: The resource path (e.g., "/sites/{site-id}/lists/{list-id}")
            target_url: Target URL for webhook notifications
            expiration_days: Number of days until subscription expires (max 3)

        Returns:
            Dict containing subscription details
        """
        # Get valid access token
        token_data = await self.get_integration_tokens(user_id, integration_uuid)

        # Calculate expiration time (max 3 days from now)
        expiration = datetime.now(UTC) + timedelta(days=min(expiration_days, 3))

        client_state = secrets.token_urlsafe(16)
        subscription_data = {
            "changeType": "updated",
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
            if response.status_code >= 400:
                logger.error(f"Graph API error: {response.text}")
            response = response.raise_for_status()

            response_data = response.json()
            response_data["expires_at"] = expiration.isoformat()
            
            return response_data

    async def renew_subscription(
        self,
        user_id: int,
        integration_uuid: str,
        subscription_id: str,
        expiration_days: int = 3,
        *args,
        **kwargs,
    ) -> None:
        """
        Renew an existing subscription.

        Args:
            subscription_id: The ID of the subscription to renew
            expiration_days: Number of days until subscription expires (max 3)

        Returns:
            Dict containing updated subscription details
        """
        subscription = await self.subscription_service.get_by_user_and_uuid(
            user_id, subscription_id, self.provider_name
        )
        token_data = await self.get_integration_tokens(user_id, integration_uuid)
        expiration = datetime.now(UTC) + timedelta(days=min(expiration_days, 3))

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.graph_api_url}/subscriptions/{subscription_id}",
                headers={"Authorization": f"Bearer {token_data.access_token}"},
                json={"expirationDateTime": expiration.isoformat()},
            )
            response.raise_for_status()

            await self.subscription_service.update(subscription["_id"], {"expires_at": expiration})

    async def delete_subscription(self, subscription_id: str, user_id: int) -> None:
        """
        Delete a subscription.

        Args:
            subscription_id: The ID of the subscription to delete
        """
        subscription = await self.subscription_service.get_by_user_and_uuid(
            user_id, subscription_id, self.provider_name
        )
        token_data = await self.get_integration_tokens(user_id, subscription["integration_id"])

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.graph_api_url}/subscriptions/{subscription_id}",
                    headers={"Authorization": f"Bearer {token_data.access_token}"},
                )
                response.raise_for_status()

        except Exception as e:
            logger.error(f"Error deleting subscription: {str(e)}")

            if "Client error" in str(e):
                if "404 Not Found" in str(e):
                    logger.info(f"Subscription with id {subscription_id} not found")
            else:
                raise e

    async def list_subscriptions(
        self, user_id: int, integration_uuid: str, page: int = 1, page_size: int = 10, *args, **kwargs
    ) -> Dict:
        """
        List all webhook subscriptions for the DocuSign account using direct API calls.

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

    async def get_sites(
        self, user_id: int, integration_uuid: str, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all SharePoint sites or search for specific sites.

        Args:
            search: Optional search term to filter sites

        Returns:
            List of site information
        """
        token_data = await self.get_integration_tokens(user_id, integration_uuid)
        if search:
            url = f"{self.graph_api_url}/sites?search={search}"
        else:
            # Use a default keyword to return all sites (e.g., 'sharepoint')
            url = f"{self.graph_api_url}/sites?search=sharepoint"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, headers={"Authorization": f"Bearer {token_data.access_token}"}
            )
            response.raise_for_status()
            return response.json().get("value", [])

    async def get_site_drives(self, user_id: int, integration_uuid: str, site_id: str) -> List[Dict[str, Any]]:
        """
        Get all drives in a SharePoint site.

        Args:
            site_id: The ID of the SharePoint site

        Returns:
            List of drive information
        """
        token_data = await self.get_integration_tokens(user_id, integration_uuid)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.graph_api_url}/sites/{site_id}/drives",
                headers={"Authorization": f"Bearer {token_data.access_token}"},
            )
            response.raise_for_status()
            return response.json().get("value", [])

    async def get_site_lists(self, user_id: int, integration_uuid: str, site_id: str) -> List[Dict[str, Any]]:
        """
        Get all lists in a SharePoint site.

        Args:
            site_id: The ID of the SharePoint site

        Returns:
            List of list information
        """
        token_data = await self.get_integration_tokens(user_id, integration_uuid)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.graph_api_url}/sites/{site_id}/lists",
                headers={"Authorization": f"Bearer {token_data.access_token}"},
            )
            response.raise_for_status()
            return response.json().get("value", [])

    async def get_drive_items(
        self,
        user_id: int,
        integration_uuid: str,
        site_id: str,
        drive_id: str,
        folder_path: Optional[str] = None,
        page_token: Optional[str] = None,
        page_size: int = 40,
        type_filter: Optional[Literal["folder"]] = None,
    ) -> Dict[str, Any]:
        """
        Get items (files and folders) in a SharePoint drive or specific folder with pagination.

        Args:
            user_id: The ID of the user
            site_id: The ID of the SharePoint site
            drive_id: The ID of the drive
            folder_path: Optional path to a specific folder (e.g., "/Documents/SubFolder")
            page_token: Optional pagination token for next page
            page_size: Number of items per page (default: 40)
            type_filter: Optional filter to return only files or folders (uses folder property filtering)

        Returns:
            Dictionary containing items and pagination metadata
        """
        token_data = await self.get_integration_tokens(user_id, integration_uuid)

        # Build the URL based on whether we're browsing root or a specific folder
        if folder_path:
            # Remove leading slash if present and encode the path
            folder_path = folder_path.lstrip("/")
            encoded_path = urllib.parse.quote(folder_path)
            url = f"{self.graph_api_url}/sites/{site_id}/drives/{drive_id}/root:/{encoded_path}:/children"
        else:
            url = (
                f"{self.graph_api_url}/sites/{site_id}/drives/{drive_id}/root/children"
            )

        # Add pagination parameters
        params = {"$top": page_size, "$orderby": "name"}

        # Add type filtering if specified
        if type_filter:
            if type_filter == "folder":
                params["$filter"] = "folder ne null"

        if page_token:
            # Use $skiptoken for Graph API pagination
            params["$skiptoken"] = page_token

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token_data.access_token}"},
                params=params,
            )
            response.raise_for_status()

            response_data = response.json()
            items = response_data.get("value", [])
            next_link = response_data.get("@odata.nextLink")

            # Process items to add useful metadata
            processed_items = []
            for item in items:
                processed_item = {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "type": "folder" if item.get("folder") else "file",
                    "size": item.get("size", 0),
                    "web_url": item.get("webUrl"),
                    "created_date_time": item.get("createdDateTime"),
                    "last_modified_date_time": item.get("lastModifiedDateTime"),
                    "parent_reference": item.get("parentReference", {}),
                }

                # Add folder-specific metadata
                if item.get("folder"):
                    processed_item["child_count"] = item.get("folder", {}).get(
                        "childCount", 0
                    )
                    processed_item["can_subscribe"] = (
                        True  # Folders can be subscribed to via drive subscription
                    )

                # Add file-specific metadata
                elif item.get("file"):
                    processed_item["mime_type"] = item.get("file", {}).get("mimeType")
                    processed_item["can_subscribe"] = (
                        False  # Individual files cannot be subscribed to
                    )

                processed_items.append(processed_item)

            # Generate next page token
            next_page_token = None
            if next_link:
                # Extract skiptoken from the @odata.nextLink URL
                try:
                    parsed_url = urllib.parse.urlparse(next_link)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    next_page_token = query_params.get("$skiptoken", [None])[0]
                except Exception as e:
                    logger.error(f"Failed to extract skiptoken from next link: {e}")
                    next_page_token = None

            return {
                "items": processed_items,
                "next_page_token": next_page_token,
                "has_next_page": next_page_token is not None,
                "total_count": len(processed_items),
            }

    async def list_resources(
        self,
        user_id: int,
        integration_uuid: str,
        site_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        folder_path: Optional[str] = None,
        type: Literal["folder"] = None,
        page_token: Optional[str] = None,
        page_size: int = 40,
    ) -> ListResourcesResponse:
        """
        List available SharePoint resources with dynamic browsing functionality and pagination.

        Navigation levels:
        1. No parameters: List all sites and their drives/lists
        2. site_id only: List drives in the site
        3. site_id + resource_id: List items in the list (with pagination, 40 items per page)
        4. site_id + resource_id + folder_path: List items in the specific folder (with pagination, 40 items per page)

        Args:
            user_id: The ID of the user
            integration_uuid: The integration UUID to use for authentication
            site_id: Optional site ID to browse
            resource_id: Optional resource ID (list_id) to browse
            folder_path: Optional folder path to browse
            page_token: Optional base64-encoded pagination token containing navigation state and Microsoft Graph skiptoken
            page_size: Optional page size for pagination

        Returns:
            ListResourcesResponse containing resources, navigation metadata, and pagination info
        """
        try:
            # Handle pagination token if provided
            current_page_token = None
            if page_token:
                logger.info(f"Processing pagination token: {page_token}")
                try:
                    # Decode the page token to get navigation state and pagination info
                    decoded_token = base64.b64decode(page_token).decode("utf-8")
                    token_data = json.loads(decoded_token)

                    # Extract navigation state from token
                    site_id = token_data.get("site_id", site_id)
                    resource_id = token_data.get("resource_id", resource_id)
                    folder_path = token_data.get("folder_path", folder_path)
                    type = token_data.get("type", type)
                    current_page_token = token_data.get("page_token")

                    logger.info(
                        f"Decoded navigation state: site_id={site_id}, resource_id={resource_id}, folder_path={folder_path}, type={type}, page_token={current_page_token}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to decode page token: {e}, using default navigation"
                    )

            # Level 1: No parameters - List all sites and their drives/lists
            if not site_id:
                logger.info("Listing all SharePoint sites and their drives/lists")
                sites = await self.get_sites(user_id, integration_uuid)

                resources = []
                for site in sites:
                    try:
                        site_id = site["id"].split(",")[1]
                        
                        resources.append(ResourceItem(
                            id=site_id,
                            name=site.get("name", "Unknown Site"),
                            type="site",
                            web_url=site.get("webUrl"),
                            description=site.get("description", ""),
                            navigation_path=NavigationPath(site_id=site_id)
                        ))

                    except Exception as e:
                        logger.error(
                            f"Error getting drives/lists for site {site.get('name', 'Unknown')}: {e}"
                        )

                return ListResourcesResponse(
                    resources=resources,
                    total_count=len(resources),
                    pagination=PaginationInfo(has_next_page=False, next_page_token=None)
                )

            # Level 2: site_id only - List drives in the site
            elif site_id and not resource_id:
                drives, lists = await asyncio.gather(
                    self.get_site_drives(user_id, integration_uuid, site_id),
                    self.get_site_lists(user_id, integration_uuid, site_id)
                )

                # Create a mapping of drive names to list IDs using dictionary comprehension
                lists_by_name = {
                    **{list_item.get("name", "").lower(): list_item["id"] for list_item in lists},
                    **{list_item.get("displayName", "").lower(): list_item["id"] 
                       for list_item in lists if list_item.get("displayName", "").lower() != list_item.get("name", "").lower()}
                }

                # Create drive resources using list comprehension
                resources = [
                    ResourceItem(
                        id=drive["id"],
                        name=drive.get("name", "Unknown Drive"),
                        type="drive",
                        web_url=drive.get("webUrl"),
                        description=drive.get("description", ""),
                        navigation_path=NavigationPath(
                            site_id=site_id,
                            resource_id=lists_by_name.get(drive.get('name', '').lower())
                        )
                    )
                    for drive in drives
                ]

                return ListResourcesResponse(
                    resources=resources,
                    total_count=len(resources),
                    pagination=PaginationInfo(has_next_page=False, next_page_token=None)
                )

            # Level 3 & 4: site_id + resource_id - List items in drive/folder
            elif site_id and resource_id:
                # Find the corresponding drive_id from the resource_id (list_id)
                drives, lists = await asyncio.gather(
                    self.get_site_drives(user_id, integration_uuid, site_id),
                    self.get_site_lists(user_id, integration_uuid, site_id)
                )
                
                # Find matching list and drive using generators and next()
                matching_list = next((list_item for list_item in lists if list_item["id"] == resource_id), None)
                if not matching_list:
                    return ListResourcesResponse(
                        resources=[],
                        total_count=0,
                        pagination=PaginationInfo(has_next_page=False, next_page_token=None)
                    )

                list_name = matching_list.get("displayName", matching_list.get("name", "")).lower()
                matching_drive = next((drive for drive in drives if drive.get("name", "").lower() == list_name), None)
                
                if not matching_drive:
                    return ListResourcesResponse(
                        resources=[],
                        total_count=0,
                        pagination=PaginationInfo(has_next_page=False, next_page_token=None)
                    )

                drive_id = matching_drive["id"]

                items_result = await self.get_drive_items(
                    user_id,
                    integration_uuid,
                    site_id=site_id,
                    drive_id=drive_id,
                    folder_path=folder_path,
                    page_token=current_page_token,
                    page_size=page_size,
                    type_filter=type,
                )

                items = items_result["items"]
                next_page_token = items_result["next_page_token"]
                has_next_page = items_result["has_next_page"]

                # Process items using list comprehension (filtering now done at API level)
                resources = [
                    ResourceItem(
                        id=item["id"],
                        name=item["name"],
                        type=item["type"],
                        size=item.get("size", 0),
                        web_url=item.get("web_url"),
                        created_date_time=item.get("created_date_time"),
                        last_modified_date_time=item.get("last_modified_date_time"),
                        mime_type=item.get("mime_type"),
                        can_subscribe=item.get("can_subscribe", item["type"] == "folder"),
                        has_children=item.get("child_count", 0) > 0 if item["type"] == "folder" else False,
                        navigation_path=NavigationPath(
                            site_id=site_id,
                            resource_id=resource_id,
                            folder_path=f"{folder_path}/{item['name']}" if folder_path else item["name"]
                        ) if item["type"] == "folder" else None
                    )
                    for item in items
                ]

                # Generate next page token for pagination
                next_page_token_encoded = None
                if has_next_page and next_page_token:
                    # Encode navigation state and pagination info
                    token_data = {
                        "site_id": site_id,
                        "resource_id": resource_id,
                        "folder_path": folder_path,
                        "type": type,
                        "page_token": next_page_token,
                    }
                    next_page_token_encoded = base64.b64encode(
                        json.dumps(token_data).encode("utf-8")
                    ).decode("utf-8")

                return ListResourcesResponse(
                    resources=resources,
                    total_count=len(resources),
                    current_path=folder_path or "",
                    pagination=PaginationInfo(
                        has_next_page=has_next_page,
                        next_page_token=next_page_token_encoded
                    )
                )

            else:
                raise ValueError("Invalid parameter combination")

        except Exception as e:
            logger.error(f"Error listing SharePoint resources: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to list SharePoint resources: {str(e)}"
            )
    
    async def post_batch(self, user_id: int, integration_uuid: str, requests_list: List[Dict]):
        token_data = await self.get_integration_tokens(user_id, integration_uuid)
        url = "https://graph.microsoft.com/v1.0/$batch"
        headers = {"Authorization": f"Bearer {token_data.access_token}", "Content-Type": "application/json"}

        def chunks(seq, n=20):
            for i in range(0, len(seq), n):
                yield seq[i:i+n]

        output = []
        for chunk in chunks(requests_list, 20):
            payload = {"requests": chunk}
            while True:
                async with httpx.AsyncClient() as client:
                    res = await client.post(url, headers=headers, json=payload)
                    if res.status_code == 429:
                        delay = int(res.headers.get("Retry-After", "3"))
                        time.sleep(delay)
                        continue
                res.raise_for_status()
                res_json = res.json()
                output.extend(res_json.get("responses", []))
                break
        return output

    def build_steps(self, item_ids:List[str]=None, drive_id:str=None,site_id:str=None):
        """
        paths: list of folder paths ("/" for root, "/Reports", "/Reports/2025")
        item_ids: list of specific driveItem IDs
        drive_id: use for SharePoint libraries (/drives/{drive-id}); else defaults to /me/drive
        """
        base = f"/sites/{site_id}/drives/{drive_id}"
        select = "id,name,webUrl,size,parentReference,file,createdDateTime,lastModifiedDateTime"
        steps, i = [], 1

        for iid in (item_ids or []):
            url = f"{base}/items/{iid}"
            steps.append({"id": str(i), "method": "GET", "url": url})
            i += 1

        return steps
