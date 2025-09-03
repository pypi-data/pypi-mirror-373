from typing import (
    Type,
    runtime_checkable,
    Dict,
    Any,
    Protocol,
)


def create_dynamic_protocol(name: str, *interfaces: Type) -> Type:
    """
    Dynamically create a Protocol that includes methods and attributes
    from multiple interfaces.
    """
    # Collect methods and attributes from all interfaces
    namespace: Dict[str, Any] = {}
    for interface in interfaces:
        for attr_name in dir(interface):
            if attr_name.startswith('_'):
                continue
            attr = getattr(interface, attr_name)
            if callable(attr) or isinstance(attr, property):
                # Only add methods and properties to the protocol
                namespace[attr_name] = attr

    # Create a dynamic Protocol class
    dynamic_protocol = type(
        name,
        (Protocol,),    # type: ignore
        namespace
    )
    return runtime_checkable(dynamic_protocol)
