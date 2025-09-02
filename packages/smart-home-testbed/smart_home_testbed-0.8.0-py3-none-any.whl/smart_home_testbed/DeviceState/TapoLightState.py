from typing import Awaitable
from .TapoState import TapoState
from .LightState import LightState


class TapoLightState(TapoState, LightState):
    """
    Class to represent the state of a Tapo light bulb.
    """


    async def _async_get_state(self) -> Awaitable[dict]:
        """
        Get the state of the light asynchronously.

        Returns:
            Awaitable[dict]: async function which returns the state of the light.
        """
        dev = await self.client.l530(self.ipv4)
        info = await dev.get_device_info()
        return {
            self.StateKeys.IS_ON:      info.device_on,
            self.StateKeys.BRIGHTNESS: info.brightness,
            self.StateKeys.HUE:        info.hue,
            self.StateKeys.SATURATION: info.saturation
        }
