from typing import Any, Awaitable
from tapo import ApiClient, GenericDeviceHandler
from .AsyncDeviceState import AsyncDeviceState


class TapoState(AsyncDeviceState):
    """
    Class to represent the state of a generic Tapo device.
    """


    def __init__(self, ipv4: str, **kwargs) -> None:
        """
        Constructor.
        Initializes the Tapo device with its IP address,
        and creates a Tapo API client.

        Args:
            ipv4 (str): The Tapo device's IPv4 address.
            kwargs (dict): device-specific additional parameters,
                           including the TP-Link account credentials.
        """
        # Superclass constructor
        super().__init__(ipv4)

        # Tapo device connector
        self.client = ApiClient(
            kwargs.get("username", ""),
            kwargs.get("password", "")
        )
        self.device: GenericDeviceHandler = None
    

    async def _async_get_state(self) -> Awaitable[Any]:
        """
        Asynchronously get the status of the generic Tapo device.

        Returns:
            Awaitable[Any]: async function which returns the Tapo device's status.
        """
        if self.device is None:
            self.device = await self.client.generic_device(self.ipv4)

        info = await self.device.get_device_info()
        return info
    

    async def _async_close(self) -> None:
        """
        Asynchronously close the connection to the Tapo device.
        Simply sets the device and client to None.
        """
        self.device = None
        self.client = None
