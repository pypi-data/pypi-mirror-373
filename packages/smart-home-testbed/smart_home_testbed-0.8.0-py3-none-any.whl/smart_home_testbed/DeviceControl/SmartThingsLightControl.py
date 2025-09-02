from .SmartThingsControl import SmartThingsControl
from .LightControl import LightControl


class SmartThingsLightControl(SmartThingsControl, LightControl):
    """
    Abstract class to control a generic light bulb through SmartThings.
    """

    ## Screen event coordinates
    # Toggle
    x = 961
    y = 436
    # Brightness and color gauges
    x_left_gauge  = 100
    x_right_gauge = 1000
    # Brightness
    y_brightness = 751
    # Color
    y_color = 1479
