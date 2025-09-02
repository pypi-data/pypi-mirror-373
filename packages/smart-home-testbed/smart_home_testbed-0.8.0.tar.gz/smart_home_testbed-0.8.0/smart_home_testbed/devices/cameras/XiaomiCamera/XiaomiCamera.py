import time
from ....DeviceState import CameraScreenshotState
from ....DeviceControl import CameraControl


class XiaomiCamera(CameraScreenshotState, CameraControl):
    """
    Xiaomi camera (Chuangmi IPC019).
    """

    ### Class variables
    # Android package name
    android_package = "com.xiaomi.smarthome"
    # SSIM threshold below which images are considered different
    SSIM_DIFF_THRESHOLD = 0.9
    ## Screen coordinates
    # Zone button
    x_zone = 475
    y_zone = 364
    # Stream event
    x_start = 950
    y_start = 509
    x_stop  = 86
    y_stop  = 218
    

    def start_app(self) -> None:
        """
        Start the Mi Home app on the phone,
        then switch to the zone control screen,
        then to the camera's stream.

        Raises:
            IndexError: If no adb device is found.
        """
        # Start the Mi Home app
        phone = self.get_phone()
        phone.shell(f"monkey -p {XiaomiCamera.android_package} -c android.intent.category.LAUNCHER 1")
        time.sleep(10)
        # Switch to the camera control screen
        phone.shell(f"input tap {self.x_zone} {self.y_zone}")
