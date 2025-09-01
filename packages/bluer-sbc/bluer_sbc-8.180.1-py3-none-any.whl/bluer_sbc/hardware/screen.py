import copy

from bluer_sbc.hardware.hardware import Hardware


class Screen(Hardware):
    def __init__(self):
        super().__init__()
        self.size = None

        self.buffer = None

    def update_screen(self, image, session, header):
        if self.animated:
            self.buffer = copy.deepcopy(image)

        return super().update_screen(image, session, header)
