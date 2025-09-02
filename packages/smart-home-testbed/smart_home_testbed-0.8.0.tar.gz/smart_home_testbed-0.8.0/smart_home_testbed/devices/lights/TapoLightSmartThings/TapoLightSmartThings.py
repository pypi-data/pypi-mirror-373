from ....DeviceState import TapoLightState
from ....DeviceControl import SmartThingsLightControl


class TapoLightSmartThings(TapoLightState, SmartThingsLightControl):
    """
    Tapo light bulb,
    controlled by the SmartThings app.
    """

    ## Class variables
    # Screen coordinates to open the device controls
    device_x = 799
    device_y = 1454
