from blueness import module

from bluer_sbc import NAME
from bluer_sbc import env
from bluer_sbc.logger import logger

NAME = module.name(__file__, NAME)


imager_name = env.BLUER_SBC_SESSION_IMAGER
if imager_name == "lepton":
    from bluer_sbc.imager.lepton import instance as imager
else:
    from bluer_sbc.imager.camera import instance as imager

logger.info(f"{NAME}: {imager_name}: {imager.__class__.__name__}")
