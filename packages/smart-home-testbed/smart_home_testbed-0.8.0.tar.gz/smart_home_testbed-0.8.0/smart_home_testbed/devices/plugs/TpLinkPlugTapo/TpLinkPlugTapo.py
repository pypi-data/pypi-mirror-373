from ....DeviceState import TpLinkPlugState
from ....DeviceControl import TapoPlugControl


class TpLinkPlugTapo(TpLinkPlugState, TapoPlugControl):
    """
    TP-Link HS110 plug,
    controlled through the Tapo app.
    """
    
    # Screen coordinates for device controls
    device_x = 799
    device_y = 654
