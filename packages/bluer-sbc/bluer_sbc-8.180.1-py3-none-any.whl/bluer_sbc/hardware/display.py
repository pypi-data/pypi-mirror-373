import cv2
import numpy as np

from blueness import module
from bluer_options.logger import crash_report
from bluer_options.host import is_mac
from bluer_objects import file
from bluer_objects.graphics import add_signature
from bluer_objects.graphics.screen import get_size

from bluer_sbc import NAME
from bluer_sbc import env
from bluer_sbc.hardware.hat.prototype import Prototype_Hat
from bluer_sbc.host import signature
from bluer_sbc.logger import logger


NAME = module.name(__file__, NAME)


class Display(Prototype_Hat):
    def __init__(self):
        super().__init__()

        self.canvas = None
        self.canvas_size = (640, 480)

        self.title = " | ".join(signature())

        self.created = False

        self.sign_images = True
        self.interpolation = cv2.INTER_LINEAR

    def create(self):
        if self.created:
            return
        self.created = True

        logger.info(f"{NAME}.create()")

        if env.BLUER_SBC_DISPLAY_FULLSCREEN and not is_mac():
            # https://stackoverflow.com/a/34337534
            cv2.namedWindow(self.title, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(
                self.title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
            )

            screen_height, screen_width = get_size()
            self.canvas_size = (
                screen_width,
                screen_height,
            )
        else:
            cv2.namedWindow(self.title, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(
                self.title,
                self.canvas_size[0],
                self.canvas_size[1],
            )

    def save(self, filename: str = "") -> str:
        if self.canvas is None:
            return ""

        if not filename:
            filename = file.auxiliary("display", "jpg")

        return filename if file.save_image(filename, self.canvas) else ""

    def update_gui(self):
        try:
            if len(self.canvas.shape) == 2:
                self.canvas = np.stack(3 * [self.canvas], axis=2)

            cv2.imshow(
                self.title,
                cv2.cvtColor(
                    cv2.resize(
                        self.canvas,
                        dsize=self.canvas_size,
                        interpolation=self.interpolation,
                    ),
                    cv2.COLOR_BGR2RGB,
                ),
            )
        except Exception as e:
            crash_report(e)

    def update_screen(self, image, session, header):
        super().update_screen(image, session, header)

        self.canvas = np.copy(image)

        if self.sign_images:
            self.canvas = add_signature(
                self.canvas,
                header=header,
                footer=[" | ".join(signature())],
            )

        self.create()

        self.update_gui()

        key = cv2.waitKey(1)
        if key not in [-1, 255]:
            key = chr(key).lower()
            logger.info(f"{NAME}.update_screen(): key: '{key}'")
            self.key_buffer.append(key)

        return self
