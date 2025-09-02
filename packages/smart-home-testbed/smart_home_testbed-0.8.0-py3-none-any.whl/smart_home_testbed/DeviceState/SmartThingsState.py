from typing import List, Any, Awaitable
import asyncio
import aiohttp
from pysmartthings import SmartThings, Device
from .AsyncDeviceState import AsyncDeviceState


class SmartThingsState(AsyncDeviceState):
    """
    Abstract class which represents a generic SmartThings device's state.
    """


    @staticmethod
    async def _get_all_devices(token: str) -> Awaitable[List[Device]]:
        """
        Asynchronously get all the devices connected to SmartThings.

        Args:
            token (str): SmartThings API token.
        Returns:
            Awaitable[List]: async function which returns the list of all devices.
        """
        async with aiohttp.ClientSession() as session:
            api = SmartThings(session, token)
            devices = await api.get_devices()
            return devices
        
    
    @classmethod
    def get_all_devices(cls) -> List[Device]:
        """
        Get all the devices connected to SmartThings.

        Returns:
            List: list of all devices
        """
        return asyncio.run(cls._get_all_devices())
    

    @classmethod
    def print_all_devices(cls) -> None:
        """
        Print the label, name and id of all devices connected to SmartThings.
        """
        for device in cls.get_all_devices():
            print(device.label, device.name, device.device_id)

    
    def __init__(self, ipv4: str, **kwargs) -> None:
        """
        Constructor.

        Args:
            ipv4 (str): IPv4 address of the SmartThings device.
            kwargs (dict): device-specific additional parameters,
                           including SmartThings API token.
        """
        # Superclass constructor
        super().__init__(ipv4)

        # SmartThings instance
        self.id = kwargs.get("id", "")
        self.token = kwargs.get("token", "")
        self.http_session: aiohttp.ClientSession = None
        self.smartthings: SmartThings = None

    
    async def _async_get_state(self) -> Awaitable[Any]:
        """
        Asynchronously get the SmartThings device status.

        Returns:
            Awaitable[Any]: async function which returns the device status.
        """
        if self.http_session is None and self.smartthings is None:
            self.http_session = aiohttp.ClientSession()
            self.smartthings = SmartThings(session=self.http_session)
            self.smartthings.authenticate(self.token)
        
        status = await self.smartthings.get_device_status(self.id)
        return status
    

    async def _async_close(self) -> None:
        """
        Asynchronously close the SmartThings session.
        """
        if self.http_session is not None:
            await self.http_session.close()
            self.http_session = None
            self.smartthings  = None
