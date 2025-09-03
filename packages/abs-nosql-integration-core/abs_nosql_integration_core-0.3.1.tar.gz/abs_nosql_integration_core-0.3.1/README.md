# NoSQL Integration Core

A comprehensive library for building OAuth-based integration services with NoSQL databases in FastAPI applications.

## Overview

NoSQL Integration Core extends the base Integration Core library to provide specialized support for NoSQL databases like MongoDB. It simplifies the process of managing OAuth tokens, API credentials, and integration state while leveraging the flexibility and scalability of NoSQL databases.

## Installation

```bash
# Using pip
pip install abs-nosql-integration-core

# Using Poetry
poetry add abs-nosql-integration-core
```

## Features

- Complete OAuth 2.0 flow management
- Secure token storage with encryption
- Automatic token refresh handling
- NoSQL database integration with Beanie ODM
- Asynchronous API with FastAPI compatibility
- Built-in MongoDB integration

## Architecture

The package follows a modular architecture:

- **Repository Layer**: Handles persistence with NoSQL databases
- **Service Layer**: Implements OAuth flows and business logic
- **Models**: Defines document models for NoSQL storage
- **Schemas**: Defines data models and validation

## Usage

### Basic Setup

```python
from abs_nosql_integration_core.service import IntegrationBaseService
from abs_nosql_integration_core.repository import IntegrationRepository
from abs_integration_core.utils.encryption import Encryption

# Create an integration service
class MyIntegrationService(IntegrationBaseService):
    def __init__(
        self,
        provider_name: str,
        integration_repository: IntegrationRepository,
        encryption: Encryption
    ):
        super().__init__(provider_name, integration_repository, encryption)
        # Additional provider-specific configuration
```

### Dependency Injection Setup

```python
from dependency_injector import containers, providers
from abs_nosql_integration_core.repository import IntegrationRepository
from abs_integration_core.utils.encryption import Encryption

class Container(containers.DeclarativeContainer):
    # MongoDB initialization
    mongodb_client = providers.Singleton(
        MongoClient, 
        connection_string=settings.MONGODB_CONNECTION_STRING
    )
    
    # Encryption service
    encryption = providers.Singleton(
        Encryption,
        secret_key=settings.ENCRYPTION_KEY
    )
    
    # Repository layer
    integration_repository = providers.Singleton(IntegrationRepository)
    
    # Service layer
    my_integration_service = providers.Singleton(
        MyIntegrationService,
        provider_name="my_provider",
        integration_repository=integration_repository,
        encryption=encryption
    )
```

### FastAPI Integration

```python
from fastapi import Depends, FastAPI, APIRouter
from dependency_injector.wiring import inject, Provide

router = APIRouter()

@router.get("/connect")
async def connect(
    service: IntegrationBaseService = Depends(get_integration_service),
):
    auth_url = service.get_auth_url()
    return {"auth_url": auth_url}

@router.get("/callback")
async def callback(
    code: str,
    service: IntegrationBaseService = Depends(get_integration_service),
):
    token_data = await service.handle_oauth_callback(code)
    return {"status": "connected"}
```

## Document Schema

The integration document model includes:

```python
class IntegrationDocument(BaseDraftDocument):
    provider_name: str  # Name of the integration provider
    access_token: str   # OAuth access token (encrypted)
    refresh_token: str  # OAuth refresh token (encrypted)
    expires_at: datetime  # Token expiration date
```

## Repository Methods

The `IntegrationRepository` class provides:

- `create_integration`: Create a new integration record
- `refresh_token`: Update access and refresh tokens
- `get_query_by_provider`: Find an integration by provider name
- `get_integration`: Get a single integration by provider
- `get_all_integrations`: Get all integrations
- `delete_integration`: Remove an integration

## Service Methods

The `IntegrationBaseService` class provides:

- `get_auth_url`: Generate OAuth authorization URL
- `handle_oauth_callback`: Process OAuth callback and store tokens
- `refresh_token`: Refresh expired access tokens
- `get_integration`: Get current integration details
- `delete_integration`: Remove integration and related tokens

## Exception Handling

The library uses a standard exception hierarchy:

- `NotFoundError`: Integration not found
- `BadRequestError`: Invalid request parameters
- `DuplicatedError`: Integration already exists
- `UnauthorizedError`: Authentication issues

## MongoDB Configuration

The package supports MongoDB through Beanie ODM:

```python
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from abs_nosql_integration_core.model import IntegrationDocument

async def init_mongodb():
    # Create Motor client
    client = AsyncIOMotorClient(MONGODB_URL)
    
    # Initialize Beanie with document models
    await init_beanie(
        database=client.db_name,
        document_models=[IntegrationDocument]
    )
```

## Best Practices

- Always encrypt sensitive tokens using the provided encryption utilities
- Use dependency injection for better testability
- Implement proper error handling for OAuth edge cases
- Consider rate limiting for API calls
- Implement proper logging for debugging
- Use async context managers for database operations

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License.
