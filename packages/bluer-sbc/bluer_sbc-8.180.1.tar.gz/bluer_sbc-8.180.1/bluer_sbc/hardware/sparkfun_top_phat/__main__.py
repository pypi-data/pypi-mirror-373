import argparse
import time

from blueness import module

from bluer_sbc import NAME
from bluer_sbc.hardware.sparkfun_top_phat.classes import Sparkfun_Top_phat
from bluer_sbc.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    default="",
    help="validate_leds",
)
args = parser.parse_args()

hardware = Sparkfun_Top_phat()

success = False
if args.task == "validate_leds":
    logger.info("loop started (Ctrl+C to stop)")
    offset = 0
    # https://stackoverflow.com/a/18994932/10917551
    try:
        while True:
            for index in range(hardware.pixel_count):
                hardware.pixels[index] = tuple(
                    int(thing * hardware.intensity)
                    for thing in hardware.colormap[
                        (index + offset) % hardware.pixel_count
                    ][:3]
                )

            offset += 1

            hardware.pixels.show()
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Ctrl+C, stopping.")
    finally:
        hardware.release()
    success = True
else:
    logger.error(f"-{NAME}: {args.task}: command not found.")

if not success:
    logger.error(f"-{NAME}: {args.task}: failed.")
