from typing import Tuple, List
import numpy as np

from blueness import module

from bluer_sbc import NAME

NAME = module.name(__file__, NAME)


class Imager:
    def capture(self) -> Tuple[bool, np.ndarray]:
        return True, np.zeros(())


class TemplateImager(Imager):
    def capture(self) -> Tuple[bool, np.ndarray]:
        success, image = super().capture()

        # TODO: capture the image here

        return success, image

    def signature(self) -> List[str]:
        return [self.__class__.__name__]
