import os
from typing import List

from bluer_ai.env import ABCLI_PATH_IGNORE
from bluer_objects import file

from bluer_sbc.logger import logger


def reply_to_bash(
    status: str,  # exit/reboot/seed/shutdown/update
    content: List[str] = [],
) -> bool:
    logger.info(f"session.reply_to_bash({status}).")

    return file.save_text(
        filename=os.path.join(
            ABCLI_PATH_IGNORE,
            f"session_reply_{status}",
        ),
        text=content,
    )
