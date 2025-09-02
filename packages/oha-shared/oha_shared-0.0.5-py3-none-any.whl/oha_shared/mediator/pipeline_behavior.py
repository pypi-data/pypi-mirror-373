import abc
from typing import TypeVar, Callable
from oha_shared.mediator.request import Request

TResponse = TypeVar("TResponse")


class PipelineBehavior(abc.ABC):
    @abc.abstractmethod
    async def handle(
        self, request: Request[TResponse], next_call: Callable[[], TResponse]
    ) -> TResponse:
        raise NotImplementedError("Subclasses must implement this method")
