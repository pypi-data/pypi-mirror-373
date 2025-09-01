import cv2

from bluer_sbc.hardware.screen import Screen


class Unicorn_16x16(Screen):
    def __init__(self):
        super().__init__()
        self.size = (16, 16)
        self.animated = True

    def release(self):
        super().release()

        import unicornhathd

        unicornhathd.off()

    def update_screen(self, image, session, header):
        import unicornhathd

        image = cv2.rotate(
            cv2.resize(
                image,
                self.size,
            ),
            cv2.ROTATE_90_CLOCKWISE,
        )

        super().update_screen(image, session, header)

        for x in range(0, 16):
            for y in range(0, 16):
                unicornhathd.set_pixel(
                    x,
                    y,
                    image[x, y, 0],
                    image[x, y, 1],
                    image[x, y, 2],
                )

        unicornhathd.show()

        return self
