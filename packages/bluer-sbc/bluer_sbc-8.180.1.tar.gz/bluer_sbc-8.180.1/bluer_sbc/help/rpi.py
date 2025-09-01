from typing import List

from bluer_options.terminal import show_usage, xtra


def help_fake_display(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun", mono=mono)

    return show_usage(
        [
            "@rpi",
            "fake_display",
            f"[{options}]",
        ],
        "fake the display on an rpi.",
        mono=mono,
    )


help_functions = {
    "fake_display": help_fake_display,
}
