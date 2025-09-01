import random

from bluer_sbc import fullname
from bluer_sbc.logger import logger


class Hardware:
    def __init__(self):
        logger.info(f"{self.__class__.__name__}.init().")

        self.key_buffer = []
        self.animated = False

    def animate(self):
        if self.buffer is None:
            return self
        if not self.animated:
            return self

        y = random.randint(0, self.buffer.shape[0] - 1)
        x = random.randint(0, self.buffer.shape[1] - 1)

        self.buffer[y, x] = 255 - self.buffer[y, x]

        self.animated = False
        self.update_screen(self.buffer, None, [], [])
        self.animated = True

    def clock(self):
        return self

    def pressed(self, keys):
        output = bool([key for key in keys if key in self.key_buffer])

        self.key_buffer = [key for key in self.key_buffer if key not in keys]

        return output

    def pulse(self, pin=None, frequency=None):
        """
        pulse pin.
        :param pin: "data" / "incoming" / "loop" / "outputs"
        :param frequency: frequency
        :return: self
        """
        return self

    def release(self):
        logger.info(f"{self.__class__.__name__}.release()")

    def signature(self):
        return [
            fullname(),
            f"hardware:{self.__class__.__name__}",
        ]

    def update_screen(self, image, session, header):
        return self
