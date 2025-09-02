import abc
from typing import TypeVar, Generic

TResponse = TypeVar("TResponse")


class Request(abc.ABC, Generic[TResponse]):
    pass
