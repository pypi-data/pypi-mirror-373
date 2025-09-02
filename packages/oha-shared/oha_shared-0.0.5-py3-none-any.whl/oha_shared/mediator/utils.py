def create_service_qualifier(service_cls: type) -> str:
    """
    Create a unique qualifier for a service class based on its module and class name.

    Args:
        service_cls (type): The service class to create a qualifier for.

    Returns:
        str: A unique qualifier string for the service class.
    """
    qualifier = f"{service_cls.__module__}.{service_cls.__name__}"
    return qualifier
