import time
from ....DeviceState import CameraScreenshotState
from ....DeviceControl import CameraControl, SmartThingsControl


class TapoCameraSmartThings(CameraScreenshotState, CameraControl, SmartThingsControl):
    """
    Tapo camera (C200),
    controlled through the SmartThings app.
    """

    ### Class attributes
    # SSIM threshold below which images are considered different
    SSIM_DIFF_THRESHOLD = 0.975
    ## Screen coordinates
    # Device controls button
    device_x = 281
    device_y = 1454
    # Expand stream
    x_expand = 864
    y_expand = 873
    # Toggle stream
    x_start = 540
    y_start = 1285


    def start_app(self) -> None:
        """
        Start the SmartThings app on the phone,
        and open the camera stream.

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
        time.sleep(15)
        # Expand stream to fullscreen
        phone.shell(f"input tap {self.x_expand} {self.y_expand}")
        phone.shell(f"input tap {self.x_expand} {self.y_expand}")
        time.sleep(3)
        # Pause stream
        phone.shell(f"input tap {self.x_start} {self.y_start}")
    

    def do_stop_stream(self) -> None:
        """
        Stop the camera's video stream.
        """
        phone = self.get_phone()
        phone.shell(f"input tap {self.x_start} {self.y_start}")
        phone.shell(f"input tap {self.x_start} {self.y_start}")
