import time
from .SmartThingsControl import SmartThingsControl
from .PlugControl import PlugControl


class SmartThingsPlugControl(SmartThingsControl, PlugControl):
    """
    Abstract class to control a generic plug through SmartThings.
    """

    def start_app(self) -> None:
        """
        Start the SmartThings app on the phone,
        and open the device controls.

        Raises:
            IndexError: If no adb device is found.
        """
        phone = self.get_phone()
        # Start SmartThings app
        phone.shell(f"monkey -p {SmartThingsControl.android_package} -c android.intent.category.LAUNCHER 1")
        time.sleep(10)
        # Open "Devices" tab
        phone.shell(f"input tap {SmartThingsControl.devices_x} {SmartThingsControl.devices_y}")
        # Do NOT open the device controls
