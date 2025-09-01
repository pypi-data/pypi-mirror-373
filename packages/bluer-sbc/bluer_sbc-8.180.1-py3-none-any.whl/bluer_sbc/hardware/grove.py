from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from bluer_options import string

from bluer_sbc.hardware.screen import Screen
from bluer_sbc.logger import logger

BUTTON = 24

RST = None  # on the PiOLED this pin isnt used


class Grove(Screen):
    def __init__(self):
        super(Grove, self).__init__()

        from grove.grove_button import GroveButton

        # https://wiki.seeedstudio.com/Grove-OLED_Display_0.96inch/
        self.size = (64, 128)

        self.button = GroveButton(BUTTON)
        self.button.on_press = lambda t: grove_button_on_press(self, t)
        self.button.on_release = lambda t: grove_button_on_release(self, t)

        import Adafruit_SSD1306

        # https://github.com/IcingTomato/Seeed_Python_SSD1315/blob/master/examples/stats.py
        self.display = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

        self.display.begin()
        self.display.clear()
        self.display.display()

        self.image = Image.new(
            "1",
            (self.display.width, self.display.height),
        )

        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle(
            (0, 0, self.display.width, self.display.height),
            outline=0,
            fill=0,
        )

        self.padding = -2
        self.top = self.padding
        self.bottom = self.display.height - self.padding

        self.font = ImageFont.load_default()

        self.line_count = 8
        self.line_length = 21

    def update_screen(self, image, session, header):
        super().update_screen(image, session, header)

        signature = (" | ".join(session.signature())).split(" | ")

        self.draw.rectangle(
            (0, 0, self.display.width, self.display.height),
            outline=0,
            fill=0,
        )

        for row in range(min(len(signature), self.line_count)):
            self.draw.text(
                (0, self.top + 8 * row),
                signature[row],
                font=self.font,
                fill=255,
            )

        self.display.image(self.image)
        self.display.display()

        return self


def grove_button_on_press(screen: Screen, t):
    logger.info("grove.button: pressed.")


def grove_button_on_release(screen: Screen, t):
    logger.info(f"grove.button: released after {string.pretty_duration(t)}.")

    if t > 60:
        logger.info("long press, ignored.")
        return

    if t > 5:
        key = "s"
    elif t > 3:
        key = "u"
    else:
        key = " "

    screen.key_buffer.append(key)
    logger.info(f"{screen.__class__.__name__}: '{key}'")
