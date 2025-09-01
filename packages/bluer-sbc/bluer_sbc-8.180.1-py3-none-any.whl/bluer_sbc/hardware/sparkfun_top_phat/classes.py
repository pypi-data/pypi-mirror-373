import cv2
import time
from matplotlib import cm

from blueness import module

from bluer_sbc import NAME
from bluer_sbc.hardware.screen import Screen
from bluer_sbc.logger import logger

NAME = module.name(__file__, NAME)


class Sparkfun_Top_phat(Screen):
    def __init__(self):
        super(Sparkfun_Top_phat, self).__init__()
        self.size = (7, 17)
        self.animated = False

        import board
        import neopixel

        # https://learn.sparkfun.com/tutorials/sparkfun-top-phat-hookup-guide/ws2812b-leds
        self.pixel_count = 6
        self.pixels = neopixel.NeoPixel(
            board.D12,
            self.pixel_count,
            auto_write=False,
        )

        self.intensity = 48

        # https://matplotlib.org/stable/tutorials/colors/colormaps.html
        self.colormap = cm.get_cmap("copper", self.pixel_count)(range(self.pixel_count))

        self.pulse_cycle = 0

        # https://github.com/sparkfun/Top_pHAT_Button_Py/blob/main/examples/top_phat_button_ex1.py
        import top_phat_button

        self.buttons = top_phat_button.ToppHATButton()
        logger.info(f"{NAME}.connection status: {self.buttons.is_connected()}")

        self.buttons.pressed_interrupt_enable = False
        self.buttons.clicked_interrupt_enable = False

    def clock(self):
        super().clock()

        self.buttons.button_pressed  # These functions must be called to update button variables to their latest setting
        self.buttons.button_clicked  # These functions must be called to update button variables to their latest setting

        if self.buttons.a_clicked == True:
            logger.info(f"{NAME}: a clicked: update.")
            self.key_buffer += ["u"]

        if self.buttons.b_clicked == True:
            logger.info(f"{NAME}: b clicked: shutdown.")
            self.key_buffer += ["s"]

        if self.buttons.center_clicked == True:
            logger.info(f"{NAME}: center clicked.")
            self.key_buffer += [" "]

        if self.buttons.up_clicked == True:
            logger.info(f"{NAME}: up clicked.")
            self.intensity = min(255, 2 * self.intensity)

        if self.buttons.down_clicked == True:
            logger.info(f"{NAME}: down clicked.")
            self.intensity = max(1, self.intensity // 2)

        return self

    def pulse(self, pin=None, frequency=None):
        super().pulse(pin, frequency)

        for index in range(self.pixel_count):
            self.pixels[index] = tuple(
                int(thing * self.intensity)
                for thing in self.colormap[
                    (index + int(self.pulse_cycle / 10)) % self.pixel_count
                ][:3]
            )

        self.pixels.show()

        self.pulse_cycle += 1

        return self

    def release(self):
        super().release()
        for index in range(self.pixel_count):
            self.pixels[index] = 3 * (0,)
            self.pixels.show()
            time.sleep(0.1)

    def update_screen(self, image, session, header):
        image = cv2.resize(image, self.size)

        super().update_screen(image, session, header)

        return self
