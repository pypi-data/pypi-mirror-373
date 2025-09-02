import time
from ....DeviceState import TapoLightState
from ....DeviceControl import TapoControl, LightControl


class TapoLight(TapoLightState, TapoControl, LightControl):
    """
    Tapo L530E light.
    """

    ## Class variables
    # Device controls coordinates
    device_x = 799
    device_y = 994
    # Toggle coordinates
    x = 940
    y = 824
    # Brightness and color gauges
    x_left_gauge = 200
    x_right_gauge = 900
    # Brightness
    y_brightness = 1503
    # Color
    x_color_tab = 302
    y_color_tab = 1697
    y_color = 1939


    def do_set_color(self) -> None:
        """
        Ensure the "Color" tab is selected,
        then randomly set the color of the light. 
        """
        self.get_phone().shell(f"input tap {self.x_color_tab} {self.y_color_tab}")
        time.sleep(2)  # Wait for the color gauge to appear
        self._set_light_attr(self.y_color)
