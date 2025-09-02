from .DeviceState import DeviceState


class CameraState(DeviceState):
    """
    Abstract class for the state of a camera device.
    """


    def __init__(self, ipv4: str, **kwargs) -> None:
        """
        Constructor.
        Initialize the camera device with its IP address.

        Args:
            ipv4 (str): The device's IPv4 address.
            kwargs (dict): device-specific additional parameters.
        """
        self.ipv4 = ipv4
        self._was_last_stream_successful = False


    def is_event_successful(self, _) -> bool:
        """
        Check if the last stream event was successful.

        Returns:
            bool: True if the event was successful, False otherwise.
        """
        return self._was_last_stream_successful
