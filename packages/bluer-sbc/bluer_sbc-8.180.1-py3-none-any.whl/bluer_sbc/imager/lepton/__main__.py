import argparse
import os

from blueness import module

from bluer_sbc import NAME
from bluer_sbc.imager.lepton import instance as lepton
from bluer_sbc.hardware import hardware
from bluer_sbc.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    default="",
    help="capture|preview",
)
parser.add_argument(
    "--filename",
    default="",
    type=str,
)
parser.add_argument(
    "--output_path",
    type=str,
    default="",
)
args = parser.parse_args()

success = False
if args.task == "capture":
    success, _, _ = lepton.capture(
        filename=os.path.join(args.output_path, "camera.jpg"),
    )
elif args.task == "preview":
    success = True

    hardware.sign_images = False
    try:
        while not hardware.pressed("qe"):
            _, image = lepton.capture()
            hardware.update_screen(image)
    finally:
        pass
else:
    logger.error(f"-{NAME}: {args.task}: command not found.")

if not success:
    logger.error(f"-{NAME}: {args.task}: failed.")
