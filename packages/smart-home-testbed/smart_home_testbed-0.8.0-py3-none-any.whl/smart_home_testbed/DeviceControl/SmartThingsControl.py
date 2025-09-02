import time
from .DeviceControl import DeviceControl


class SmartThingsControl(DeviceControl):
    """
    Abstract class to control a generic device through SmartThings.
    """

    ## Class variables
    # Android package name
    android_package = "com.samsung.android.oneconnect"
    # Devices tab button screen coordinates
    devices_x = 335
    devices_y = 2230


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
        time.sleep(5)
        # Open device controls
        phone.shell(f"input tap {self.device_x} {self.device_y}")
