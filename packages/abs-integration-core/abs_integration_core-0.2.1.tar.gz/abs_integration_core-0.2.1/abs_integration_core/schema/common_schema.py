from typing import Generic, Optional, TypeVar, Dict, List, Any
from pydantic import BaseModel, Field
from fastapi import status

T = TypeVar('T')


class ResponseSchema(BaseModel, Generic[T]):
    """
    Standard response schema for all API endpoints
    """
    status: int = status.HTTP_200_OK
    message: str = "Success"
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True


class NavigationPath(BaseModel):
    """
    Navigation path information for resources
    """
    site_id: Optional[str] = None
    resource_id: Optional[str] = None
    folder_path: Optional[str] = None

    class Config:
        extra = "allow"


class ResourceItem(BaseModel):
    """
    Common schema for resource items (files/folders) across different providers
    """
    id: str = Field(..., description="Unique identifier for the resource")
    name: str = Field(..., description="Name of the resource")
    type: str = Field(..., description="Type of resource (file/folder/drive)")
    size: int = Field(0, description="Size in bytes")
    web_url: Optional[str] = Field(None, description="Web URL to access the resource")
    created_date_time: Optional[str] = Field(None, description="Creation timestamp")
    last_modified_date_time: Optional[str] = Field(None, description="Last modification timestamp")
    mime_type: Optional[str] = Field(None, description="MIME type of the resource")
    can_subscribe: bool = Field(False, description="Whether the resource can be subscribed to")
    has_children: bool = Field(False, description="Whether the resource has children")
    navigation_path: Optional[NavigationPath] = Field(None, description="Navigation path for the resource")
    description: Optional[str] = Field(None, description="Description of the resource")

    class Config:
        extra = "allow"


class PaginationInfo(BaseModel):
    """
    Pagination information for list responses
    """
    has_next_page: bool = Field(False, description="Whether there are more pages available")
    next_page_token: Optional[str] = Field(None, description="Token for the next page")

    class Config:
        extra = "allow"


class ListResourcesResponse(BaseModel):
    """
    Standard response schema for list_resources endpoints across all providers
    """
    resources: List[ResourceItem] = Field(default_factory=list, description="List of resources")
    total_count: int = Field(0, description="Total number of resources in current response")
    current_path: str = Field("", description="Current path being browsed")
    pagination: PaginationInfo = Field(default_factory=PaginationInfo, description="Pagination information")

    class Config:
        extra = "allow"
