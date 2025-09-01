from typing import List

from bluer_options.terminal import show_usage, xtra


def help_validate(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "button | leds"

    return show_usage(
        [
            "@sbc",
            "sparkfun_top_phat",
            "validate",
            f"[{options}]",
        ],
        "validate sparkfun_top_phat.",
        mono=mono,
    )


help_functions = {
    "validate": help_validate,
}
