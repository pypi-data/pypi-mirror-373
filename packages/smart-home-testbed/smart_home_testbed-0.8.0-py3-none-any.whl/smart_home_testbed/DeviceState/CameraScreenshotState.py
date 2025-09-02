import cv2
from skimage.metrics import structural_similarity as ssim
from .CameraState import CameraState


class CameraScreenshotState(CameraState):
    """
    Abstract class for the state of a camera device,
    which uses screenshot-based event validation.
    """

    # SSIM threshold below which images are considered different
    SSIM_DIFF_THRESHOLD = 0.9
    # Default file name for streaming screenshot
    FILENAME_SCREENSHOT_STREAM = "stream.png"


    def __init__(self, ipv4: str, **kwargs) -> None:
        """
        Constructor.
        Initialize the camera device with its IP address.

        Args:
            ipv4 (str): The device's IPv4 address.
            kwargs (dict): device-specific additional parameters,
                           including the path to the streaming screenshot.
        """
        # Call parent constructor
        super().__init__(ipv4, **kwargs)

        # Compute gray array of streaming screenshot
        path_screenshot_stream = kwargs.get("path_screenshot_stream", CameraScreenshotState.FILENAME_SCREENSHOT_STREAM)
        stream_image = cv2.imread(path_screenshot_stream)
        self.gray_stream_image = cv2.cvtColor(stream_image, cv2.COLOR_BGR2GRAY)


    def get_state(self) -> bool:
        """
        Get the state of the camera device,
        i.e. if it is currently streaming,
        by taking a screenshot of its app.

        Returns:
            bool: True if the camera is currently streaming, False otherwise.
        """
        # Take screenshot and convert to grayscale
        screenshot_array = self.screenshot()
        gray_screenshot = cv2.cvtColor(screenshot_array, cv2.COLOR_BGR2GRAY)

        # Compute SSIM
        try:
            score = ssim(self.gray_stream_image, gray_screenshot, full=False)
            return score > self.SSIM_DIFF_THRESHOLD
        except ValueError:
            return False
