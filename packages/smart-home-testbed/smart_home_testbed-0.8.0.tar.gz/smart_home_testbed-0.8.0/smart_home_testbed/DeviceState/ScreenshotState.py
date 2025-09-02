import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from .DeviceState import DeviceState


class ScreenshotState(DeviceState):
    """
    Device state using app screenshot.
    """

    # SSIM threshold below which images are considered different
    SSIM_DIFF_THRESHOLD = 0.95


    def get_state(self) -> np.ndarray:
        """
        Get the state of the device,
        by taking a screenshot of its app.

        Returns:
            numpy.ndarray: The screenshot as a numpy array.
        """
        return self.screenshot()
    

    def is_event_successful(self, previous_state: np.ndarray) -> bool:
        """
        Check if an event was successful,
        i.e. if the current state has changed compared to the given previous state.
        This method uses the SSIM metric to compare the screenshots.

        Args:
            previous_state (numpy.ndarray): app screenshot, as a numpy array, which represents the previous state.
        Returns:
            bool: True if the event was successful, False otherwise.
        """
        current_state = self.get_state()

        # Load images, and convert to grayscale
        gray_previous  = cv2.cvtColor(previous_state, cv2.COLOR_BGR2GRAY)
        gray_current   = cv2.cvtColor(current_state, cv2.COLOR_BGR2GRAY)

        # Compute SSIM
        score = ssim(gray_previous, gray_current, full=False)
        return score < self.SSIM_DIFF_THRESHOLD
