from ....DeviceState import ScreenshotState
from ....DeviceControl import TuyaControl, PlugControl


class TuyaPlug(ScreenshotState, TuyaControl, PlugControl):
    """
    Tuya generic plug.
    """

    ## Screen coordinates
    # Device controls screen coordinates
    device_x = 281
    device_y = 582
    # Toggle coordinates
    x = 540
    y = 1042
