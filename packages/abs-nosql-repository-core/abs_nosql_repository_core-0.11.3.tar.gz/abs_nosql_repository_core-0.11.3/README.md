# abs-nosql-repository-core

Shared base repository and service utilities for Beanie (NoSQL)-backed FastAPI apps.

## Overview

This package provides reusable base classes and utilities to simplify building repository and service layers for MongoDB/Beanie-based FastAPI applications. It includes:

- **BaseRepository**: Generic CRUD and query logic for Beanie/MongoDB documents.
- **BaseCollectionRepository**: CRUD and schema management for MongoDB collections.
- **BaseService**: Service layer abstraction for business logic using repositories.
- **BaseCollectionService**: Service layer for collection-level operations.
- **BaseDocument**: Standard document model for Beanie.
- **BaseSchema**: Standard Pydantic schema for API/data validation.

## Installation

Add to your `pyproject.toml`:

```toml
[dependencies]
abs-nosql-repository-core = ">=0.9.7,<0.10.0"
```

Or install via pip :

```bash
pip install abs-nosql-repository-core
```

## Dependencies
- Python >=3.13
- fastapi
- beanie
- abs-exception-core
- abs-utils

## Usage

### 1. Define Your Document Model

```python
from beanie import Document
from abs_nosql_repository_core.document import BaseDocument

class MyEntity(BaseDocument):
    name: str
    description: str
```

### 2. Define Your Repository

```python
from abs_nosql_repository_core.repository import BaseRepository
from myapp.model import MyEntity

class MyEntityRepository(BaseRepository):
    def __init__(self):
        super().__init__(document=MyEntity)
```

Or for collection-level operations:

```python
from abs_nosql_repository_core.repository import BaseCollectionRepository
from motor.motor_asyncio import AsyncIOMotorDatabase

class MyCollectionRepository(BaseCollectionRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)
```

### 3. Define Your Service

```python
from abs_nosql_repository_core.service import BaseService
from myapp.repository import MyEntityRepository

class MyEntityService(BaseService):
    def __init__(self, repository: MyEntityRepository):
        super().__init__(repository)
```

Or for collection-level services:

```python
from abs_nosql_repository_core.service import BaseCollectionService
from myapp.repository import MyCollectionRepository

class MyCollectionService(BaseCollectionService):
    def __init__(self, repository: MyCollectionRepository):
        super().__init__(repository)
```

### 4. Use in Your FastAPI App

- Initialize your repositories and services in your dependency injection container or app startup.
- Use the service methods in your API endpoints.

### 5. Example: Entity Manager Service Integration

**Repository Example:**

```python
from abs_nosql_repository_core.repository import BaseRepository
from src.model import Entities

class EntityManageRepository(BaseRepository):
    def __init__(self):
        super().__init__(document=Entities)
    # Add custom methods as needed
```

**Service Example:**

```python
from abs_nosql_repository_core.service import BaseService
from src.repository.entity_manage_repository import EntityManageRepository

class EntityManageService(BaseService):
    def __init__(self, repository: EntityManageRepository):
        super().__init__(repository)
    # Add business logic methods as needed
```

**Usage in FastAPI Endpoint:**

```python
from fastapi import APIRouter, Depends
from src.service.entity_manage_service import EntityManageService

router = APIRouter()

@router.post("/entities/")
async def create_entity(entity_data: EntitySchema, service: EntityManageService = Depends()):
    return await service.create_entity(entity_data)
```

## API Reference

### Repository Layer
- `BaseRepository(document=None, db=None, ...)` — For document-based CRUD and queries.
- `BaseCollectionRepository(db)` — For collection-level operations (create, drop, add field, etc).

### Service Layer
- `BaseService(repository)` — Standard CRUD and query service.
- `BaseCollectionService(repository)` — Collection management service.

### Document & Schema
- `BaseDocument` — Extend for your Beanie models.
- `BaseSchema` — Extend for your Pydantic schemas.

### Common Methods
- `create`, `bulk_create`, `get_by_attr`, `get_all`, `update`, `delete`, `bulk_update`, `bulk_delete`, etc.

## Advanced Features
- Filtering, sorting, pagination, and aggregation via `ListFilter`, `FilterSchema`, etc.
- Reference fields and joins via `AggregationStage`.
- Embedding and event hooks (see source for details).

## Integrating Azure Service Bus and Socket.IO with Repositories

The `BaseRepository` supports integration with Azure Service Bus and Socket.IO for event-driven and real-time features. This allows you to emit events (such as record creation, update, or deletion) to external systems or clients.

### Why Integrate?
- **Azure Service Bus**: Enables asynchronous event processing, microservice communication, and integration with cloud workflows.
- **Socket.IO**: Enables real-time notifications to connected clients (e.g., web dashboards) when data changes.

### How to Use

#### 1. Initialize the Utilities

```python
from abs_utils.azure_service_bus.azure_service_bus import AzureServiceBus
from abs_utils.socket_io.server import SocketIOService

# Azure Service Bus
azure_service_bus = AzureServiceBus(
    connection_string="<your-azure-service-bus-connection-string>",
    queue_name="<your-queue-name>"
)

# Socket.IO
sio_service = SocketIOService(cors_origins="*")
```

#### 2. Inject into Your Repository

```python
from abs_nosql_repository_core.repository import BaseRepository
from myapp.model import MyEntity

class MyEntityRepository(BaseRepository):
    def __init__(self, sio_service=None, azure_service_bus=None):
        super().__init__(
            document=MyEntity,
            sio_service=sio_service,              # Optional: for real-time events
            azure_service_bus=azure_service_bus   # Optional: for async event bus
        )
```

#### 3. Event Emission in CRUD Operations

When you call `create`, `update`, or `delete` on your repository, events will be automatically sent to Azure Service Bus and/or broadcasted via Socket.IO if the respective services are provided.

- **Azure Service Bus**: Sends structured event payloads for downstream processing.
- **Socket.IO**: Emits events to rooms or clients for real-time updates.

#### 4. Example Usage in a Service

```python
from myapp.repository import MyEntityRepository
from abs_nosql_repository_core.service import BaseService

class MyEntityService(BaseService):
    def __init__(self, repository: MyEntityRepository):
        super().__init__(repository)

# Usage
service = MyEntityService(
    repository=MyEntityRepository(
        sio_service=sio_service,
        azure_service_bus=azure_service_bus
    )
)

# Create an entity (will emit events)
await service.create({"name": "Test Entity"})
```

#### 5. Dependency Injection Example (FastAPI)

If you use a DI container (e.g., `dependency_injector`):

```python
from dependency_injector import containers, providers
from abs_utils.azure_service_bus.azure_service_bus import AzureServiceBus
from abs_utils.socket_io.server import SocketIOService
from myapp.repository import MyEntityRepository

class Container(containers.DeclarativeContainer):
    azure_service_bus = providers.Singleton(
        AzureServiceBus,
        connection_string="<your-conn-str>",
        queue_name="<your-queue>"
    )
    sio_service = providers.Singleton(SocketIOService, cors_origins="*")
    my_entity_repository = providers.Factory(
        MyEntityRepository,
        sio_service=sio_service,
        azure_service_bus=azure_service_bus
    )
```

#### 6. Custom Event Handling

You can extend your repository to emit custom events or handle event payloads as needed by overriding methods or using the provided services directly.

---

## License
MIT
