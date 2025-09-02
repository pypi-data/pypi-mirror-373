from wireup import service
from oha_shared.mediator.utils import create_service_qualifier


def request_handler(command_type):
    return service(
        lifetime="transient", qualifier=create_service_qualifier(command_type)
    )


def pipeline_behavior():
    return service(lifetime="transient")
