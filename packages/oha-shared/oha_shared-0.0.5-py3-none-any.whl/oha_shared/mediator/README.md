from tests.basic_test import pipeline_behaviors

# Mediator Pattern Implementation

A Python implementation of the Mediator pattern using the `wireup` dependency injection container. This package provides a clean way to decouple request senders from request handlers through a central mediator.

## Features

- Type-safe request/response handling using Python generics
- Dependency injection powered by `wireup` IOC container
- Async/await support
- Decorator-based handler registration
- Pipeline behaviors for cross-cutting concerns (logging, validation, etc.)
- Scoped container support for web frameworks

## Quick Start

### 1. Define Request and Response Classes

```python
from mediator.core.request import Request


class CreateOrderResponse:
    def __init__(self, order_id: str):
        self.order_id = order_id


class CreateOrderCommand(Request[CreateOrderResponse]):
    def __init__(self, price: float):
        self.price = price
```

### 2. Create Request Handler

```python
from mediator.core.decorators import request_handler
from mediator.core.request_handler import RequestHandler


@request_handler(CreateOrderCommand)
class CreateOrderHandler(RequestHandler[CreateOrderCommand, CreateOrderResponse]):
    async def handle(self, request: CreateOrderCommand) -> CreateOrderResponse:
        # Your business logic here
        order_id = f"order_{hash(request.price)}"
        return CreateOrderResponse(order_id=order_id)
```

### 3. Initialize Mediator

```python
import asyncio
import wireup
import mediator.core
from mediator import init_mediator
from mediator.core.mediator import Mediator

# Create wireup container with your service modules
container = wireup.create_async_container(
    service_modules=[
        mediator.core,  # Register mediator services
        your_handlers_module,  # Module containing your handlers
        pipeline_behaviors_module,  # Module containing your pipeline behaviors (if any)
    ]
)

# Initialize mediator with container
init_mediator(container.enter_scope)


# Get mediator instance and send requests
async def main():
    scope = container.enter_scope()
    mediator_instance = await scope.get(Mediator)

    request = CreateOrderCommand(price=100.0)
    response = await mediator_instance.send(request)
    print(f"Order created: {response.order_id}")


asyncio.run(main())
```

### 4. Pipeline Behaviors (Optional)

Pipeline behaviors allow you to implement cross-cutting concerns that execute before and after request handling:

```python
from mediator.core.pipeline_behavior import PipelineBehavior
from mediator.core.decorators import pipeline_behavior

@pipeline_behavior()
class LoggingPipelineBehavior(PipelineBehavior):
    async def handle(self, request, next_call):
        print(f"Handling request: {type(request).__name__}")
        response = await next_call()
        print(f"Request handled with response: {response}")
        return response

@pipeline_behavior()
class ValidationPipelineBehavior(PipelineBehavior):
    async def handle(self, request, next_call):
        # Add validation logic here
        print(f"Validating request: {type(request).__name__}")
        return await next_call()
```

To register pipeline behaviors with the mediator, pass them during initialization:

```python
# Register behaviors when initializing mediator
pipeline_behaviors = [LoggingPipelineBehavior, ValidationPipelineBehavior]
init_mediator(container.enter_scope, pipeline_behaviors=pipeline_behaviors)
```

### 5. Web Framework Integration

For FastAPI applications:

```python
# Use wireup's FastAPI integration for scoped containers
init_mediator(wireup.integration.fastapi.get_request_container)
```

## Architecture

### Core Components

- **`Mediator`**: Central dispatcher that routes requests to handlers
- **`Request[TResponse]`**: Generic base class for all requests
- **`RequestHandler[TRequest, TResponse]`**: Generic base class for handlers
- **`PipelineBehavior`**: Base class for implementing cross-cutting concerns
- **`@request_handler`**: Decorator for registering handlers with the container
- **`@pipeline_behavior`**: Decorator for registering pipeline behaviors

### How It Works

1. Requests implement `Request[ResponseType]` 
2. Handlers implement `RequestHandler[RequestType, ResponseType]` and use `@request_handler(RequestType)`
3. Pipeline behaviors implement `PipelineBehavior` and use `@pipeline_behavior()` for cross-cutting concerns
4. The mediator uses the wireup container to resolve handlers and behaviors based on request type
5. Pipeline behaviors execute in a chain before and after the actual handler
6. Handlers are registered with qualified names to avoid conflicts

## Dependencies

This package is built on top of the `wireup`[https://github.com/maldoinc/wireup] IOC container, which provides:
- Dependency injection
- Service lifetime management
- Scoped containers for web applications
- Integration with popular web frameworks
