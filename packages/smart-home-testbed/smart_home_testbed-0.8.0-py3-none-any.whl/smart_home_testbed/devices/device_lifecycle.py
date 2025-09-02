from typing import Any
import importlib


def init_device(name: str, ipv4: str, **kwargs) -> Any:
    """
    Factory method to create a device object.

    Args:
        name (str): The name of the device.
        ipv4 (str): The device's IPv4 address.
        kwargs (dict): device-specific additional parameters.
    Returns:
        Any: The device object.
    """
    package_parts = importlib.import_module(__name__).__name__.split(".")
    package_name = f"{package_parts[0]}.{package_parts[1]}"
    package = importlib.import_module(package_name)
    cls = getattr(package, name)
    return cls(ipv4, **kwargs)


def close_device(device: Any) -> None:
    """
    Close the device connector.

    Args:
        device (Any): The device object.
    """
    try:
        device.close()
    except AttributeError:
        # If the device does not have a stop method, we can ignore it
        pass
