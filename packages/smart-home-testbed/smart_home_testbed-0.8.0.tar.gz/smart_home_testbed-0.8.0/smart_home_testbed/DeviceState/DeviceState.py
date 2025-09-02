from typing import Any


class DeviceState:
    """
    Abstract class which represent a device state.
    """

    def __init__(self, ipv4: str, **kwargs) -> None:
        """
        Constructor.
        Initialize the device with its IP address.

        Args:
            ipv4 (str): The device's IPv4 address.
            kwargs (dict): device-specific additional parameters.
        """
        self.ipv4 = ipv4

        # Set the device-specific parameters
        for key, value in kwargs.items():
            setattr(self, key, value)


    def get_state(self) -> Any:
        """
        Get the state of the device.

        Returns:
            Any: current state of the device.
        """
        raise NotImplementedError


    def is_event_successful(self, previous_state: Any) -> bool:
        """
        Check if an event was successful,
        i.e. if the device is still reachable
        and its state has changed compared to the previous state.

        Args:
            previous_state (Any): The state of the device before the event.
        Returns:
            bool: True if the event was successful, False otherwise.
        """
        try:
            state = self.get_state()
        except Exception:
            return False
        else:
            return state != previous_state
