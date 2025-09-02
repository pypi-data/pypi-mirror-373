import time
from .DeviceControl import DeviceControl


class CameraControl(DeviceControl):
    """
    Class to control a camera device.
    """

    # Stream event duration
    stream_duration = 10


    def stream(self) -> None:
        """
        Perform the `stream` event.
        """
        self.start_stream()
        time.sleep(self.stream_duration)
        self.stop_stream()


    def start_stream(self) -> None:
        """
        Start the camera's video stream.
        """
        self.get_phone().shell(f"input tap {self.x_start} {self.y_start}")

    
    def do_stop_stream(self) -> None:
        """
        Stop the camera's video stream.
        """
        self.get_phone().shell(f"input tap {self.x_stop} {self.y_stop}")

    
    def stop_stream(self) -> None:
        """
        Check if the stream was successful,
        then stop the stream.
        """
        # Check if stream was successful
        self._was_last_stream_successful = self.get_state()
        
        if self._was_last_stream_successful:
            self.do_stop_stream()
