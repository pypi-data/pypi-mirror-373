import time
import math
import random
from ....DeviceState import HueState
from ....DeviceControl import LightControl


class HueLightEssentials(HueState, LightControl):
    """
    Philips Hue light bulb,
    controlled by the Hue Essentials app.
    """

    ### Class variables
    # Android package
    android_package = "com.superthomaslab.hueessentials"
    ## Screen coordinates
    # Zone button
    x_zone = 540
    y_zone = 582
    # Lamp button
    x_lamp = 896
    y_lamp = 2036
    # Toggle button
    x = 950
    y = 679
    # Brightness
    x_left_gauge = 100
    x_right_gauge = 1000
    y_brightness = 388
    # Color
    x_color_center = 540
    y_color_center = 1382
    y_color_top    = 900


    def start_app(self, open_lamp_control: bool = False) -> None:
        """
        Start the Hue Essentials app on the phone,
        and open the light control screen.

        Args:
            open_lamp_control (bool): Whether to additionally open the lamp control screen after having opened the app.
                                      Optional, default is False.
        Raises:
            IndexError: If no adb device is found.
        """
        phone = self.get_phone()
        # Open app
        phone.shell(f"monkey -p {self.android_package} -c android.intent.category.LAUNCHER 1")
        time.sleep(10)
        # Open zone controls
        phone.shell(f"input tap {self.x_zone} {self.y_zone}")
        # If needed, open lamp controls
        if open_lamp_control:
            time.sleep(3)
            phone.shell(f"input tap {self.x_lamp} {self.y_lamp}")
    

    def do_set_color(self) -> None:
        """
        Randomly set the color of the Philips Hue light
        through the Hue Essentials app.
        """
        # Compute color wheel's radius
        radius = self.y_color_center - self.y_color_top
        # Generate random position on the color wheel
        distance  = random.randint(0, radius)
        angle_deg = random.randint(0, 360)
        angle_rad = angle_deg * math.pi / 180
        x = self.x_color_center + distance * math.cos(angle_rad)
        y = self.y_color_center + distance * math.sin(angle_rad)
        # Set the color
        self.get_phone().shell(f"input tap {x} {y}")
