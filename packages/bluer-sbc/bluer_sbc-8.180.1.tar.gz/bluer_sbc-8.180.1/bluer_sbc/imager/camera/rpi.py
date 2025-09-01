from typing import Tuple, Union, List
import numpy as np
from time import sleep

from bluer_options.logger import crash_report
from bluer_options import string
from bluer_objects import file, objects

from bluer_sbc.imager.camera.generic import Camera
from bluer_sbc.hardware import hardware
from bluer_sbc import env
from bluer_sbc.logger import logger


class RPI_Camera(Camera):
    def capture_function(self) -> Tuple[bool, np.ndarray]:
        success = False
        image = np.ones((1, 1, 3), dtype=np.uint8) * 127

        temp = file.auxiliary("camera", "png")
        try:
            self.device.capture(temp)
            success = True
        except Exception as e:
            crash_report(e)

        if success:
            success, image = file.load_image(temp)

        return success, image

    # https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/6
    def capture_video(
        self,
        filename: str,
        object_name: str,
        length: int = 10,  # in seconds
        preview: bool = True,
        pulse: bool = True,
        resolution=None,
    ) -> bool:
        if not self.open(resolution=resolution):
            return False

        full_filename = objects.path_of(
            object_name=object_name,
            filename=filename,
        )

        success = True
        try:
            if preview:
                self.device.start_preview()

            self.device.start_recording(full_filename)
            if pulse:
                for _ in range(int(10 * length)):
                    hardware.pulse("outputs")
                    sleep(0.1)
            else:
                sleep(length)
            self.device.stop_recording()

            if preview:
                self.device.stop_preview()
        except Exception as e:
            crash_report(e)
            success = False

        if not self.close():
            return False

        if success:
            logger.info(
                "{}.capture_video(): {} -{}-> {}".format(
                    self.__class__.__name__,
                    string.pretty_duration(length),
                    string.pretty_bytes(file.size(full_filename)),
                    filename,
                )
            )

        return success

    def close_function(self):
        self.device.close()

    def get_resolution_function(self) -> Tuple[int, int]:
        return [value for value in self.device.resolution]

    def open_function(
        self,
        resolution=Union[List[int], None],
    ):
        from picamera import PiCamera

        self.device = PiCamera()
        self.device.rotation = env.BLUER_SBC_CAMERA_ROTATION

        # https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/7
        self.device.resolution = (
            (
                (2592, 1944)
                if env.BLUER_SBC_CAMERA_HI_RES
                else (
                    env.BLUER_SBC_CAMERA_WIDTH,
                    env.BLUER_SBC_CAMERA_HEIGHT,
                )
            )
            if resolution is None
            else resolution
        )
