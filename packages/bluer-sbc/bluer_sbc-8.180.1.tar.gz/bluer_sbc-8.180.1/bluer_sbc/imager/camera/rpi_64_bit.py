from typing import Tuple, Union, List
import numpy as np

from bluer_options.logger import crash_report

from bluer_sbc.imager.camera.generic import Camera
from bluer_sbc import env


class RPI_64_bit_Camera(Camera):
    def capture_function(self) -> Tuple[bool, np.ndarray]:
        success = False
        image = np.ones((1, 1, 3), dtype=np.uint8) * 127

        try:
            image = self.device.capture_array()
            success = True
        except Exception as e:
            crash_report(e)

        return success, image

    def close_function(self):
        self.device.stop()
        del self.device

    def get_resolution_function(self) -> Tuple[int, int]:
        width, height = self.device.stream_configuration("main")["size"]
        return [height, width]

    def open_function(
        self,
        resolution=Union[List[int], None],
    ):
        from picamera2 import Picamera2

        self.device = Picamera2()

        config = self.device.create_still_configuration(
            main={
                "size": (
                    env.BLUER_SBC_CAMERA_WIDTH,
                    env.BLUER_SBC_CAMERA_HEIGHT,
                )
            }
        )
        self.device.configure(config)

        self.device.start()
