import os
from typing import List

from bluer_options.help.functions import get_help
from bluer_objects import file, README

from bluer_sbc import NAME, VERSION, ICON, REPO_NAME
from bluer_sbc.designs.cheshmak import items as cheshmak_items
from bluer_sbc.designs.cheshmak import marquee as cheshmak_marquee
from bluer_sbc.designs.blue_bracket import items as blue_bracket_items
from bluer_sbc.designs.bluer_swallow import items as bluer_swallow_items
from bluer_sbc.designs.bluer_swallow import marquee as bluer_swallow_marquee
from bluer_sbc.designs.bryce import items as bryce_items
from bluer_sbc.designs.bryce import marquee as bryce_marquee
from bluer_sbc.help.functions import help_functions


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            cols=readme.get("cols", 3),
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
        )
        for readme in [
            {
                "items": cheshmak_marquee
                + bluer_swallow_marquee
                + bryce_marquee
                + blue_bracket_items,
                "path": "..",
            },
            {
                "items": cheshmak_items,
                "path": "./docs/cheshmak.md",
            },
            {
                "items": bluer_swallow_items,
                "path": "./docs/bluer-swallow.md",
            },
            {
                "items": bryce_items,
                "path": "./docs/bryce.md",
            },
        ]
        + [
            {"path": f"./docs/aliases/{item}.md"}
            for item in [
                "camera",
                "hardware",
                "rpi",
            ]
        ]
    )
