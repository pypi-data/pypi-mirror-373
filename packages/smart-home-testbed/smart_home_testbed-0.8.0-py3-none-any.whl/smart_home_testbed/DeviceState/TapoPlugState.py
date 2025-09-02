from typing import Awaitable
from tapo import PlugEnergyMonitoringHandler
from .TapoState import TapoState


class TapoPlugState(TapoState):
    """
    Class to represent the state of a Tapo plug.
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
        # Superclass (TapoState) constructor
        super().__init__(ipv4, **kwargs)

        # Tapo plug connector
        self.device: PlugEnergyMonitoringHandler = None


    async def _async_get_state(self) -> Awaitable[bool]:
        """
        Asynchronously get the state of the Tapo plug.

        Returns:
            Awaitable[bool]: async function which returns True if the plug is on, False otherwise.
        """
        if self.device is None:
            # Create a Tapo plug device handler
            self.device = await self.client.p110(self.ipv4)

        info = await self.device.get_device_info()
        return info.device_on
