from ....DeviceState import TpLinkPlugState
from ....DeviceControl import PlugControl


class TpLinkPlug(TpLinkPlugState, PlugControl):
    """
    TP-Link HS110 plug.
    """
    
    ## Class variables
    # Android package name
    android_package = "com.tplink.kasa_android"
    # Toggle coordinates
    x = 950
    y = 654
