from typing import List

from bluer_options.terminal import show_usage


def help_input(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@sbc",
            "hat",
            "input",
        ],
        "read hat inputs.",
        mono=mono,
    )


def help_output(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@sbc",
            "hat",
            "output",
            "<10101010>",
        ],
        "activate hat outputs.",
        mono=mono,
    )


def help_validate(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@sbc",
            "hat",
            "validate",
        ],
        "validate hat.",
        mono=mono,
    )


help_functions = {
    "input": help_input,
    "output": help_output,
    "validate": help_validate,
}
