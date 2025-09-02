from ....DeviceState import CameraScreenshotState
from ....DeviceControl import CameraErrorControl


class DLinkCamera(CameraScreenshotState, CameraErrorControl):
    """
    DLink camera (DCS-8000LH).
    """

    ### Class attributes
    # Android package
    android_package = "com.dlink.mydlinkunified"
    # SSIM threshold below which images are considered different
    SSIM_DIFF_THRESHOLD = 0.9
    ## Screen coordinates
    # Stream event
    x_start = 637
    y_start = 1479
    x_stop = 76
    y_stop = 1648
    # Error message
    x_error = 540
    y_error = 1333
