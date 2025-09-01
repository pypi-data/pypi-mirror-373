from blueness import module
from bluer_options import host

from bluer_sbc import NAME
from bluer_sbc.env import BLUER_SBC_HARDWARE_KIND
from bluer_sbc.hardware.hardware import Hardware as Hardware_Class
from bluer_sbc.logger import logger

NAME = module.name(__file__, NAME)


if host.is_mac():
    from bluer_sbc.hardware.display import Display as Hardware_Class
elif BLUER_SBC_HARDWARE_KIND == "adafruit_rgb_matrix":
    from bluer_sbc.hardware.adafruit_rgb_matrix import (
        Adafruit_Rgb_Matrix as Hardware_Class,
    )
elif BLUER_SBC_HARDWARE_KIND == "grove":
    from bluer_sbc.hardware.grove import Grove as Hardware_Class
elif BLUER_SBC_HARDWARE_KIND == "prototype_hat":
    if host.is_headless():
        from bluer_sbc.hardware.hat.prototype import Prototype_Hat as Hardware_Class
    else:
        from bluer_sbc.hardware.display import Display as Hardware_Class
elif BLUER_SBC_HARDWARE_KIND == "scroll_phat_hd":
    from bluer_sbc.hardware.scroll_phat_hd import Scroll_Phat_HD as Hardware_Class
elif BLUER_SBC_HARDWARE_KIND == "sparkfun-top-phat":
    from bluer_sbc.hardware.sparkfun_top_phat.classes import (
        Sparkfun_Top_phat as Hardware_Class,
    )
elif BLUER_SBC_HARDWARE_KIND == "unicorn_16x16":
    from bluer_sbc.hardware.unicorn_16x16 import Unicorn_16x16 as Hardware_Class

hardware = Hardware_Class()

logger.info(f"{NAME}: {BLUER_SBC_HARDWARE_KIND}: {hardware.__class__.__name__}")
