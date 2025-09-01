from typing import List

from bluer_options.terminal import show_usage
from bluer_ai.help.generic import help_functions as generic_help_functions

from bluer_sbc.help.adafruit_rgb_matrix import (
    help_functions as help_adafruit_rgb_matrix,
)
from bluer_sbc.help.camera import help_functions as help_camera
from bluer_sbc.help.grove import help_functions as help_grove
from bluer_sbc.help.hat import help_functions as help_hat
from bluer_sbc.help.lepton import help_functions as help_lepton
from bluer_sbc.help.rpi import help_functions as help_rpi
from bluer_sbc.help.scroll_phat_hd import help_functions as help_scroll_phat_hd
from bluer_sbc.help.sparkfun_top_phat import help_functions as help_sparkfun_top_phat
from bluer_sbc.help.unicorn_16x16 import help_functions as help_unicorn_16x16
from bluer_sbc import ALIAS


help_functions = generic_help_functions(plugin_name=ALIAS)

help_functions.update(
    {
        "adafruit_rgb_matrix": help_adafruit_rgb_matrix,
        "camera": help_camera,
        "grove": help_grove,
        "hat": help_hat,
        "lepton": help_lepton,
        "rpi": help_rpi,
        "scroll_phat_hd": help_scroll_phat_hd,
        "sparkfun_top_phat": help_sparkfun_top_phat,
        "unicorn_16x16": help_unicorn_16x16,
    }
)
