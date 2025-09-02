from ....DeviceState import TapoPlugState
from ....DeviceControl import SmartThingsPlugControl


class TapoPlugSmartThings(TapoPlugState, SmartThingsPlugControl):
    """
    Tapo P110 plug,
    controlled by the SmartThings app.
    """

    ## Class attributes
    # Screen coordinates to open the device controls
    device_x = 799
    device_y = 776
    # Toggle coordinates from the "Devices" tab
    x = 972
    y = 679
