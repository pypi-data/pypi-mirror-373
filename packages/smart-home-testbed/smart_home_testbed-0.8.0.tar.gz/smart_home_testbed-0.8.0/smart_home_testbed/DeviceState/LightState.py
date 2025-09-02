from enum import Enum
from .DeviceState import DeviceState


class LightState(DeviceState):
    """
    Abstract class for the state of a light device.
    """

    class StateKeys(Enum):
        """
        Enum for the keys in the dictionary representing the state of a light device.
        """
        IS_ON      = "is_on"
        BRIGHTNESS = "brightness"
        HUE        = "hue"
        SATURATION = "saturation"


    def is_off(self) -> bool:
        """
        Check if the light is on.
        
        Returns:
            bool: True if the light is on, False otherwise.
        """
        return not self.get_state()[self.StateKeys.IS_ON]
