from typing import Awaitable
from kasa import Device
from .AsyncDeviceState import AsyncDeviceState


class TpLinkPlugState(AsyncDeviceState):
    """
    Class to represent the state of a TP-Link plug.
    """

    def __init__(self, ipv4: str, **kwargs) -> None:
        """
        Constructor.

        Args:
            ipv4 (str): IPv4 address of the TP-Link plug.
            kwargs (dict): device-specific additional parameters.
        """
        # Superclass constructor
        super().__init__(ipv4)

        # TP-Link connector
        self.device_tplink: Device = None


    async def _async_get_state(self) -> Awaitable[bool]:
        """
        Asynchronously get the state of the TP-Link plug.

        Returns:
            bool: True if the plug is on, False otherwise.
        """
        if self.device_tplink is None:
            self.device_tplink = await Device.connect(host=self.ipv4)

        await self.device_tplink.update()
        return self.device_tplink.is_on
    

    async def _async_close(self) -> None:
        """
        Asynchronously close the connection to the TP-Link plug.
        """
        if self.device_tplink is not None:
            await self.device_tplink.disconnect()
            self.device_tplink = None
