import time
from .DeviceControl import DeviceControl


class TuyaControl(DeviceControl):
    """
    Abstract class to control a generic device through the Tuya app.
    """

    # Metadata
    android_package = "com.tuya.smart"
    version = "3.3"


    def start_app(self) -> None:
        """
        Start the Tuya app on the phone.

        Raises:
            IndexError: If no adb device is found.
        """
        phone = self.get_phone()
        # Start Tapo app
        phone.shell(f"monkey -p {TuyaControl.android_package} -c android.intent.category.LAUNCHER 1")
        time.sleep(10)
        # Open device controls
        phone.shell(f"input tap {self.device_x} {self.device_y}")
