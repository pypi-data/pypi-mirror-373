from typing import Callable
from wireup.ioc.container.async_container import ScopedAsyncContainer
from oha_shared.mediator.pipeline_behavior import PipelineBehavior


class MediatorConfig:
    scoped_container_provider: Callable[[], ScopedAsyncContainer] 
    pipeline_behaviors: set[type[PipelineBehavior]] = set()

    @classmethod
    def set_scoped_container_provider(cls, provider: Callable[[], ScopedAsyncContainer]):
        cls.scoped_container_provider = provider