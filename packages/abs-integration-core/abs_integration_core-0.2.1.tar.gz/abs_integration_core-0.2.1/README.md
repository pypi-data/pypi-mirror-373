# Integration Core

A core library for building and managing OAuth-based third-party integrations in FastAPI applications.

## Overview

`abs-integration-core` provides a set of reusable components to simplify the implementation of OAuth-based integrations with third-party services. It includes models, schemas, repositories, and a base service class that can be extended for specific integration providers.

## Features

- **Integration Model**: SQLAlchemy model for storing OAuth tokens and integration metadata
- **Standard Schemas**: Pydantic models for integration data validation and serialization
- **Repository Layer**: Data access layer for CRUD operations on integration records
- **Base Service**: Abstract base class for implementing integration services for different providers
- **Token Verification**: Automatic handling of token expiration and refresh

## Installation

```bash
pip install abs-integration-core
```

## Dependencies

This package depends on:

- `fastapi`: For API routing and endpoint handling
- `sqlalchemy`: For database ORM functionality
- `pydantic`: For data validation
- `abs-exception-core`: For standardized exception handling
- `abs-repository-core`: For base repository pattern implementation
- `abs-auth-rbac-core`: For authentication and base models

## Usage

### Models

The core model represents an OAuth integration with a third-party provider:

```python
from abs_integration_core.models import Integration

# The Integration model includes:
# - provider_name: String(255)
# - access_token: Text
# - refresh_token: Text  
# - expires_at: DateTime
```

### Schemas

Various Pydantic schemas are available for request/response handling:

```python
from abs_integration_core import (
    TokenData,
    IsConnectedResponse,
    CreateIntegration,
    UpdateIntegration,
    ResponseSchema
)

# TokenData includes:
# - access_token: str
# - refresh_token: str
# - expires_at: datetime

# Example: Create a standard API response
response = ResponseSchema(
    status=200,
    message="Integration created successfully",
    data=IsConnectedResponse(provider="sharepoint", connected=True)
)
```

### Repository

The `IntegrationRepository` provides data access methods:

```python
from abs_integration_core import IntegrationRepository

# Initialize repository with a database session factory
repo = IntegrationRepository(db_session)

# Available methods:
# - create_integration(integration_data)
# - update_integration(integration_id, update_data)
# - get_by_provider(provider_name)
# - get_all()
# - delete_by_provider(provider_name)
# - refresh_token(provider_name, token_data)
```

### Base Service

Extend the `IntegrationBaseService` to implement provider-specific integration services:

```python
from abs_integration_core import IntegrationBaseService

class SharepointIntegrationService(IntegrationBaseService):
    def __init__(self, provider_name, integration_repository, encryption):
        super().__init__(provider_name, integration_repository, encryption)
    
    def get_auth_url(self, state=None):
        # Implementation for generating OAuth URL
        
    async def get_token_data(self, code):
        # Implementation for exchanging code for tokens
        
    async def handle_oauth_callback(self, code):
        # Implementation for processing OAuth callback
        
    async def refresh_token(self):
        # Implementation for refreshing tokens
```

## Implementing a New Integration

To implement a new integration provider:

1. Create a new service class that extends `IntegrationBaseService`
2. Implement the required abstract methods:
   - `get_auth_url()`
   - `get_token_data(code)`
   - `handle_oauth_callback(code)`
   - `refresh_token()`
3. Register your service in your FastAPI application
4. Create API routes to initiate auth flow, handle callbacks, etc.

## Example: Creating API Routes

```python
from fastapi import APIRouter, Depends
from abs_integration_core import ResponseSchema, IsConnectedResponse

router = APIRouter(prefix="/integration", tags=["integration"])

@router.get("/{provider_name}/connect")
async def integration_connect(
    service: IntegrationBaseService = Depends(get_integration_service)
):
    auth_data = service.get_auth_url()
    return RedirectResponse(url=auth_data["auth_url"])

@router.get("/{provider_name}/callback")
async def integration_callback(
    code: str,
    service: IntegrationBaseService = Depends(get_integration_service)
):
    token_data = await service.handle_oauth_callback(code)
    return ResponseSchema(
        data=IsConnectedResponse(
            provider=service.provider_name,
            connected=True
        ),
        message=f"Integration connected successfully"
    )
```

## License

MIT 