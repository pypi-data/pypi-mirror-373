from typing import Any, Awaitable
import threading
import asyncio
from .DeviceState import DeviceState


class AsyncDeviceState(DeviceState):
    """
    Asynchronous querying of a device's state.
    """


    def __init__(self, ipv4: str) -> None:
        """
        Constructor.
        Initialize the device with its IP address and start the asyncio event loop.

        Args:
            ipv4 (str): The device's IPv4 address.
        """
        # Device's IPv4 address
        self.ipv4 = ipv4

        # asyncio event loop
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()


    def _start_loop(self):
        """
        Start the asyncio event loop, and run it forever.
        """
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()


    def _async_get_state(self) -> Awaitable[Any]:
        """
        Asynchronously get the state of the device.
        This method is abstract and should be implemented in subclasses.

        Returns:
            Awaitable[Any]: async coroutine which returns the current state of the device.
        """
        raise NotImplementedError("This method should be implemented in subclasses.")


    def get_state(self) -> Any:
        """
        Get the device's state.

        Returns:
            Any: current state of the device.
        """
        return asyncio.run_coroutine_threadsafe(self._async_get_state(), self.loop).result()
    

    async def _async_close(self) -> None:
        """
        Asynchronously close the connection to the device.
        This method is abstract and should be implemented in subclasses.
        """
        raise NotImplementedError("This method should be implemented in subclasses.")


    def close(self) -> None:
        """
        Close the connection to the device.
        """
        asyncio.run_coroutine_threadsafe(self._async_close(), self.loop).result()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
