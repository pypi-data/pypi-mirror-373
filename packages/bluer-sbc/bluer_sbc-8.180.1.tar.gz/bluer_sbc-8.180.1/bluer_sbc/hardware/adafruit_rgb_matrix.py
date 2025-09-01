import cv2
from PIL import Image

from bluer_sbc.hardware.screen import Screen


class Adafruit_Rgb_Matrix(Screen):
    def __init__(self):
        super(Adafruit_Rgb_Matrix, self).__init__()
        self.size = (32, 32)
        self.animated = True

        from rgbmatrix import RGBMatrix, RGBMatrixOptions

        options = RGBMatrixOptions()
        options.rows = 32
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = "adafruit-hat"  # adafruit-hat/regular

        self.matrix = RGBMatrix(options=options)

    def update_screen(self, image, session, header):
        image = cv2.resize(image, self.size)

        super().update_screen(image, session, header)

        self.matrix.SetImage(Image.fromarray(image).convert("RGB"))

        return self
