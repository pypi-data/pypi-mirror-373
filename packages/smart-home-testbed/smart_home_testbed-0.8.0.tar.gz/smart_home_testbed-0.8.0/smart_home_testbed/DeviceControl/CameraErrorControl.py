from .CameraControl import CameraControl


class CameraErrorControl(CameraControl):
    """
    Class to control a camera which displays error messages
    when connection issues occur.
    """

    def start_stream(self) -> None:
        """
        Dismiss the potential error message,
        then start the camera's video stream.
        Overwrites the method from the parent class CameraControl.
        """
        phone = self.get_phone()
        phone.shell(f"input tap {self.x_error} {self.y_error}")
        phone.shell(f"input tap {self.x_start} {self.y_start}")
