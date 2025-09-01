from typing import List

from bluer_options.terminal import show_usage, xtra


def help_validate(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@sbc",
            "unicorn_16x16",
            "validate",
        ],
        "validate unicorn_16x16.",
        mono=mono,
    )


help_functions = {
    "validate": help_validate,
}
