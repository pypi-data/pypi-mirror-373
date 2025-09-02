import abc
from typing import Generic, TypeVar
from wireup import abstract
from oha_shared.mediator.request import Request

TRequest = TypeVar("TRequest", bound=Request)
TResponse = TypeVar("TResponse")


@abstract
class RequestHandlerBase(abc.ABC):
    @abc.abstractmethod
    async def handle(self, request: Request) -> object:
        raise NotImplementedError("Subclasses must implement this method")


@abstract
class RequestHandler(RequestHandlerBase, Generic[TRequest, TResponse]):
    @abc.abstractmethod
    async def handle(self, request: Request[TResponse]) -> TResponse:
        raise NotImplementedError("Subclasses must implement this method")
