import argparse
import cv2
from datetime import datetime
import numpy as np
import os.path
import time


def capture(flip_v=True, device="/dev/spidev0.0"):
    from pylepton import Lepton

    with Lepton(device) as l:
        a, _ = l.capture()

    if flip_v:
        cv2.flip(a, 0, a)

    cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(a, 8, a)

    return np.uint8(a)


def capture_and_save(path):
    try:
        for _ in range(2):
            image = capture(False, "/dev/spidev0.0")
            time.sleep(1)

        cv2.imwrite(os.path.join(path, "image_raw.jpg"), image)

        cv2.imwrite(
            os.path.join(path, "image.jpg"),
            cv2.resize(image, (1280, 960), interpolation=cv2.INTER_NEAREST),
        )

        print(
            "lepton.capture_and_save({}) completed: {}.".format(
                path, "x".join([str(dim) for dim in image.shape])
            )
        )
    except Exception as e:
        print("lepton.capture_and_save() crashed: {}".format(e))
        return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "task",
        type=str,
        default="",
        help="capture",
    )
    parser.add_argument(
        "--output_path",
        default="",
    )
    args = parser.parse_args()

    success = False
    if args.task == "capture":
        success = capture_and_save(args.output_path)
    else:
        print("-lepton: {}: command not found.".format(args.task))

    if not success:
        print("-lepton: {}: failed.".format(args.task))
