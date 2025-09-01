import argparse

from blueness import module
from bluer_options import string
from bluer_objects.env import abcli_object_name

from bluer_sbc import NAME
from bluer_sbc.imager.camera import instance as camera
from bluer_sbc.logger import logger

NAME = module.name(__file__, NAME)


parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="capture | capture_video | preview",
)
parser.add_argument(
    "--object_name",
    type=str,
    default=abcli_object_name,
)
parser.add_argument(
    "--filename",
    type=str,
    default="",
)
parser.add_argument(
    "--length",
    type=int,
    default=0,
)
parser.add_argument(
    "--output_path",
    type=str,
    default="",
)
parser.add_argument(
    "--preview",
    type=int,
    default=1,
    help="0 | 1",
)
args = parser.parse_args()

success = False
if args.task == "capture":
    success, image = camera.capture(
        filename=args.filename if args.filename else f"{string.timestamp()}.png",
        object_name=args.object_name,
    )
elif args.task == "capture_video":
    success = camera.capture_video(
        filename=args.filename if args.filename else f"{string.timestamp()}.h264",
        object_name=args.object_name,
        length=args.length if args.length else 10,
        preview=args.preview,
        resolution=(728, 600),
    )
elif args.task == "preview":
    success = camera.preview(length=args.length if args.length else -1)

else:
    logger.error(f"-{NAME}: {args.task}: command not found.")

if not success:
    logger.error(f"-{NAME}: {args.task}: failed.")
