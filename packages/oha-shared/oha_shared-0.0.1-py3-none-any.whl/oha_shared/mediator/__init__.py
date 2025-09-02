from typing import Callable, Optional
from wireup.ioc.container.async_container import ScopedAsyncContainer
from oha_shared.mediator.pipeline_behavior import PipelineBehavior
from oha_shared.mediator.mediator_config import MediatorConfig


def init_mediator(scoped_container_provider: Callable[[], ScopedAsyncContainer],
                  pipeline_behaviors: Optional[list[type[PipelineBehavior]]] = None,):
    if scoped_container_provider is None:
        raise ValueError("scoped_container_provider cannot be None")

    MediatorConfig.scoped_container_provider = scoped_container_provider

    if pipeline_behaviors:
        MediatorConfig.pipeline_behaviors = set(pipeline_behaviors)
