import time
from .DeviceControl import DeviceControl


class TapoControl(DeviceControl):
    """
    Abstract class to control a generic device through the Tapo app.
    """

    # Android package name
    android_package = "com.tplink.iot"


    def start_app(self) -> None:
        """
        Start the device's app on the phone.

        Raises:
            IndexError: If no adb device is found.
        """
        phone = self.get_phone()
        # Start Tapo app
        phone.shell(f"monkey -p {TapoControl.android_package} -c android.intent.category.LAUNCHER 1")
        time.sleep(10)
        # Open device controls
        phone.shell(f"input tap {self.device_x} {self.device_y}")
