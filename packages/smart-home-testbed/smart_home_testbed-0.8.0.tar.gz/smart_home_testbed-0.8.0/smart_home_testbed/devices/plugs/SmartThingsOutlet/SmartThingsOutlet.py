from typing import Awaitable
from pysmartthings import Capability, Attribute
from ....DeviceState import SmartThingsState
from ....DeviceControl import SmartThingsPlugControl


class SmartThingsOutlet(SmartThingsState, SmartThingsPlugControl):
    """
    SmartThings Outlet.
    """

    ## Class attributes
    # Screen to open the device controls from the "Devices" tab
    device_x = 281
    device_y = 1115
    # Toggle coordinates from the "Devices" tab
    x = 454
    y = 1018
    # States boolean values
    states = {
        "on":  True,
        "off": False
    }


    async def _async_get_state(self) -> Awaitable[bool]:
        """
        Asynchronously get the state of the plug.

        Returns:
            Awaitable[bool]: async function which returns True if the plug is on, False otherwise.
        """
        status = await super()._async_get_state()
        state = status["main"][Capability.SWITCH][Attribute.SWITCH].value
        return SmartThingsOutlet.states[state]
