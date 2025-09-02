from .DeviceControl import DeviceControl


class PlugControl(DeviceControl):
    """
    Class to control a plug device.
    """


    def toggle(self) -> None:
        """
        Perform the toggle action on the plug.
        """
        self.get_phone().shell(f"input tap {self.x} {self.y}")
