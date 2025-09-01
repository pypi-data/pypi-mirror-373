from typing import Tuple
import numpy as np

from blueness import module
from bluer_options import string
from bluer_objects import file
from bluer_objects import path
from bluer_objects.env import abcli_path_git
from bluer_objects.host import shell

from bluer_sbc import NAME
from bluer_sbc.imager.classes import Imager
from bluer_sbc.logger import logger


NAME = module.name(__file__, NAME)


class Lepton(Imager):
    def capture(self) -> Tuple[bool, np.ndarray]:
        success, image = super().capture()

        temp_dir = path.auxiliary("lepton")
        success = shell(
            f"python python2.py capture --output_path {temp_dir}",
            work_dir=f"{abcli_path_git}/bluer-sbc/bluer_sbc/imager/lepton",
        )

        if success:
            success, image = file.load_image(f"{temp_dir}/image.jpg")

        if success:
            logger.info(f"{NAME}.capture(): {string.pretty_shape_of_matrix(image)}")

        return success, image
