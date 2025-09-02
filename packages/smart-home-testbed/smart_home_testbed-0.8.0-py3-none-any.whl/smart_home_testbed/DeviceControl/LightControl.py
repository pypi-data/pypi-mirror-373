import random
from .DeviceControl import DeviceControl


class LightControl(DeviceControl):
    """
    Class to control a light bulb device.
    """


    def toggle(self) -> None:
        """
        Perform the toggle event on the light.
        """
        self.get_phone().shell(f"input tap {self.x} {self.y}")


    def _set_light_attr(self, y: int) -> None:
        """
        Randomly set an attribute of the light
        (brightness or color).
        
        Args:
            y (int): The y-coordinate of the corresponding gauge.
        """
        x = random.randint(self.x_left_gauge, self.x_right_gauge)
        self.get_phone().shell(f"input tap {x} {y}")

    
    def do_set_brightness(self) -> None:
        """
        Randomly set the brightness of the light.
        """
        self._set_light_attr(self.y_brightness)

    
    def set_brightness(self) -> None:
        """
        Template method to randomly set the brightness of the light.
        The child class must implement the concrete method `is_off`,
        which checks if the light is off.
        """
        # If light is off, turn it on
        if self.is_off():
            self.toggle()
        
        self.do_set_brightness()
    

    def do_set_color(self) -> None:
        """
        Randomly set the color of the light.
        """
        self._set_light_attr(self.y_color)

    
    def set_color(self) -> None:
        """
        Template method to randomly set the color of the light.
        The child class must implement the concrete method `is_off`,
        which checks if the light is off.
        """
        # If light is off, turn it on
        if self.is_off():
            self.toggle()
        
        self.do_set_color()
