from typing import List

from bluer_options.terminal import show_usage, xtra


def help_capture(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@sbc",
            "lepton",
            "capture",
        ],
        "lepton.capture.",
        mono=mono,
    )


def help_preview(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@sbc",
            "lepton",
            "preview",
        ],
        "lepton.preview.",
        mono=mono,
    )


help_functions = {
    "capture": help_capture,
    "preview": help_preview,
}
