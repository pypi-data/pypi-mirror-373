import abc
from typing import TypeVar
from wireup import abstract, service
from oha_shared.mediator.pipeline_behavior import PipelineBehavior
from oha_shared.mediator.mediator_config import MediatorConfig
from oha_shared.mediator.request import Request
from oha_shared.mediator.request_handler import RequestHandlerBase
from oha_shared.mediator.utils import create_service_qualifier

TResponse = TypeVar("TResponse")


@abstract
class Mediator(abc.ABC):
    @abc.abstractmethod
    async def send(self, request: Request[TResponse]) -> TResponse:
        raise NotImplementedError("Subclasses must implement this method")


@service(lifetime="singleton")
class DefaultMediator(Mediator):
    def __init__(self):
        pass

    @staticmethod
    async def __get_pipeline_behavior_chain():
        registered_behaviors = MediatorConfig.pipeline_behaviors

        if not registered_behaviors:
            return []

        behaviors: list[PipelineBehavior] = []
        container = MediatorConfig.scoped_container_provider()

        for registered_behavior in registered_behaviors:
            instance = await container.get(registered_behavior)
            behaviors.append(instance)

        return behaviors

    @staticmethod
    def __build_pipeline_chain(
        behaviors: list[PipelineBehavior],
        request: Request[TResponse],
        handler: RequestHandlerBase,
    ):
        """
        Builds the pipeline chain by creating nested lambda functions.
        Each behavior gets a next_call that points to the next behavior or final handler.
        """

        # Start with the final handler call
        def final_handler():
            return handler.handle(request)

        # Build the chain backwards - start with the final handler and wrap each behavior
        next_call = final_handler

        # Iterate through behaviors in reverse order
        for behavior in reversed(behaviors):
            # Capture the current next_call and behavior in the closure
            current_next = next_call
            current_behavior = behavior

            # Create a new next_call that invokes the current behavior
            def create_behavior_call(behavior, next_func):
                def behavior_call():
                    return behavior.handle(request, next_func)

                return behavior_call

            next_call = create_behavior_call(current_behavior, current_next)

        return next_call

    async def send(self, request: Request[TResponse]) -> TResponse:
        container = MediatorConfig.scoped_container_provider()
        qualifier = create_service_qualifier(type(request))
        handler = await container.get(RequestHandlerBase, qualifier=qualifier)

        if handler is None:
            raise ValueError(
                f"No handler found for request type: {type(request).__name__}"
            )

        # Get the pipeline behaviors
        behaviors = await self.__get_pipeline_behavior_chain()

        # If no behaviors, just call the handler directly
        if not behaviors:
            return await handler.handle(request)

        # Build and execute the pipeline chain
        pipeline_chain = self.__build_pipeline_chain(behaviors, request, handler)
        return await pipeline_chain()
