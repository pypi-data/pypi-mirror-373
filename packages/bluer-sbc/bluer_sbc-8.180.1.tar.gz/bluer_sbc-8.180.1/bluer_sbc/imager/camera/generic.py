import cv2
from typing import Tuple, List, Union
import numpy as np

from blueness import module
from bluer_options import string
from bluer_options import host
from bluer_options.timer import Timer
from bluer_options.logger import crash_report
from bluer_objects import file, objects

from bluer_sbc import env
from bluer_sbc.hardware import hardware
from bluer_sbc.imager.classes import Imager
from bluer_sbc.logger import logger


class Camera(Imager):
    def __init__(self):
        self.device = None
        self.resolution = []

    def capture(
        self,
        close_after: bool = True,
        log: bool = True,
        open_before: bool = True,
        filename: str = "",
        object_name: str = "",
    ) -> Tuple[bool, np.ndarray]:
        success = False
        image = np.ones((1, 1, 3), dtype=np.uint8) * 127

        if open_before:
            if not self.open():
                return success, image

        if self.device is None:
            return success, image

        success, image = self.capture_function()
        if not success:
            logger.warning("capture failed.")
        elif log:
            logger.info(
                "{}.capture(): {}".format(
                    self.__class__.__name__,
                    string.pretty_shape_of_matrix(image),
                )
            )

        if close_after:
            self.close()

        if success and filename:
            success = file.save_image(
                filename=objects.path_of(
                    object_name=object_name,
                    filename=filename,
                ),
                image=image,
                log=log,
            )

        return success, image

    def capture_function(self) -> Tuple[bool, np.ndarray]:
        success = False
        image = np.ones((1, 1, 3), dtype=np.uint8) * 127

        try:
            success, image = self.device.read()

            if success:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        except Exception as e:
            crash_report(e)

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
        logger.error(f"{self.__class__.__name__}.capture_video(): not implemented.")
        return False

    def close(self, log: bool = True) -> bool:
        if self.device is None:
            logger.warning(
                "{}.close(): device is {}, failed.".format(
                    self.__class__.__name__,
                    self.device,
                )
            )
            return False

        try:
            self.close_function()
        except Exception as e:
            crash_report(e)
            return False

        self.device = None

        if log:
            logger.info(f"{self.__class__.__name__}.close().")

        return True

    def close_function(self):
        self.device.release()

    def get_resolution(self) -> List[int]:
        try:
            resolution = self.get_resolution_function()
        except Exception as e:
            crash_report(e)
            return []

        return resolution

    def get_resolution_function(self) -> Tuple[int, int]:
        return [
            int(self.device.get(const))
            for const in [cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FRAME_WIDTH]
        ]

    def open(
        self,
        log: bool = True,
        resolution: Union[List[int], None] = None,
    ) -> bool:
        try:
            self.open_function(resolution=resolution)

            self.resolution = self.get_resolution()

            if log:
                logger.info(
                    "{}.open({})".format(
                        self.__class__.__name__,
                        string.pretty_shape(self.resolution),
                    )
                )

            return True
        except Exception as e:
            crash_report(e)
            return False

    def open_function(
        self,
        resolution=Union[List[int], None],
    ):
        self.device = cv2.VideoCapture(0)

        # https://stackoverflow.com/a/31464688
        self.device.set(cv2.CAP_PROP_FRAME_WIDTH, env.BLUER_SBC_CAMERA_WIDTH)
        self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, env.BLUER_SBC_CAMERA_HEIGHT)

    def preview(
        self,
        length: float = -1,
    ) -> bool:
        logger.info(
            "{}.preview{} ... | press q or e to quit ...".format(
                self.__class__.__name__,
                "[{}]".format("" if length == -1 else string.pretty_duration(length)),
            )
        )

        hardware.sign_images = False
        timer = Timer(length, "preview")
        try:
            self.open(
                log=True,
                resolution=(320, 240),
            )

            while not hardware.pressed("qe"):
                _, image = self.capture(
                    close_after=False,
                    log=False,
                    open_before=False,
                )
                hardware.update_screen(image, None, [])

                if timer.tick(wait=True):
                    logger.info(
                        "{} is up, quitting.".format(string.pretty_duration(length))
                    )
                    break

        except KeyboardInterrupt:
            logger.info("Ctrl+C, stopping.")

        finally:
            self.close(log=True)

        return True
