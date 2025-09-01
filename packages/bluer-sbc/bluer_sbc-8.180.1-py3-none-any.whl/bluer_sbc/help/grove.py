from typing import List

from bluer_options.terminal import show_usage


def help_info(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "grove",
            "info",
        ],
        "show grove info.",
        mono=mono,
    )


def help_validate(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "adc | button"

    return show_usage(
        [
            "grove",
            "validate",
            f"[{options}]",
        ],
        "validate grove.",
        mono=mono,
    )


def help_validate_oled_128x64(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "animate | buttons | image | shapes | stats"

    return show_usage(
        [
            "grove",
            "validate",
            "oled_128x64",
            f"[{options}]",
        ],
        "validate grove oled_128x64.",
        mono=mono,
    )


help_functions = {
    "info": help_info,
    "validate": help_validate,
    "validate_oled_128x64": help_validate_oled_128x64,
}
