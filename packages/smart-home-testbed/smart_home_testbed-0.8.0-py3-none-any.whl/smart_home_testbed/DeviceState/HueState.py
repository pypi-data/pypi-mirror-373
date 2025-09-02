from typing import Awaitable
from enum import Enum
import contextlib
import asyncio
import threading
from aiohue import HueBridgeV2, create_app_key
from .LightState import LightState


class HueState(LightState):
    """
    Class to represent the state of a Philips Hue light bulb.
    """


    class StateKeys(Enum):
        """
        Enum for the keys in the dictionary representing the state of the Philips Hue device.
        """
        IS_ON      = "is_on"
        BRIGHTNESS = "brightness"
        COLOR_X    = "color_x"
        COLOR_Y    = "color_y"

    
    @staticmethod
    async def _get_app_key(bridge_ip: str) -> Awaitable[str]:
        """
        Asynchronously get the app key for the Philips Hue bridge.

        Args:
            bridge_ip (str): IP address of the Philips Hue bridge.
        Returns:
            Awaitable[str]: async function which returns the app key.
        """
        input("Press the link button on the bridge and press enter to continue...")
        return await create_app_key(bridge_ip, "authentication_example")
    

    @classmethod
    def get_app_key(cls, bridge_ip: str) -> str:
        """
        Get the app key for the Philips Hue bridge.

        Args:
            bridge_ip (str): IP address of the Philips Hue bridge.
        Returns:
            str: app key.
        """
        with contextlib.suppress(KeyboardInterrupt):
            asyncio.run(cls._get_app_key(bridge_ip))

    
    def __init__(self, ipv4: str, **kwargs) -> None:
        """
        Constructor.

        Args:
            ipv4 (str): IPv4 address of the Philips Hue bridge.
            kwargs (dict): device-specific additional parameters,
                           including Philips Hue app key.
        """
        # Device's IPv4 address
        self.ipv4 = ipv4

        # App key for the Philips Hue bridge
        self.appkey = kwargs.get("appkey", "")

        # Hue bridge instance
        self.hue_bridge: HueBridgeV2 = None

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

    
    async def _async_get_state(self) -> Awaitable[dict]:
        """
        Get the state of the Philips Hue light asynchronously.

        Returns:
            Awaitable[dict]: async function which returns the status of the Philips Hue light.
        """
        if self.hue_bridge is None:
            self.hue_bridge = HueBridgeV2(self.ipv4, self.appkey)
            await self.hue_bridge.initialize()

        light = next(l for l in self.hue_bridge.lights.items)
        return {
            self.StateKeys.IS_ON: light.is_on,
            self.StateKeys.BRIGHTNESS: light.brightness,
            self.StateKeys.COLOR_X: light.color.xy.x,
            self.StateKeys.COLOR_Y: light.color.xy.y
        }
        
    
    def get_state(self) -> dict:
        """
        Get the state of the Philips Hue light.

        Returns:
            dict: The status of the Philips Hue light.
        """
        return asyncio.run_coroutine_threadsafe(self._async_get_state(), self.loop).result()
    

    async def _async_close(self) -> None:
        """
        Close the Philips Hue bridge connection asynchronously.
        """
        if self.hue_bridge is not None:
            await self.hue_bridge.close()
            self.hue_bridge = None
    

    def close(self) -> None:
        """
        Stop the Philips Hue light.
        """
        asyncio.run_coroutine_threadsafe(self._async_close(), self.loop).result()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
