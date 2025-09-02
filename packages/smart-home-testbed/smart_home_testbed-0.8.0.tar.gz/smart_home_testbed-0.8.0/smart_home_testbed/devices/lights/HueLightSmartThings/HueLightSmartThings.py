from ....DeviceState import HueState
from ....DeviceControl import SmartThingsLightControl


class HueLightSmartThings(HueState, SmartThingsLightControl):
    """
    Philips Hue light bulb,
    controlled by the SmartThings app.
    """

    ## Class variables
    # Screen coordinates to open the device controls
    device_x = 799
    device_y = 1139
