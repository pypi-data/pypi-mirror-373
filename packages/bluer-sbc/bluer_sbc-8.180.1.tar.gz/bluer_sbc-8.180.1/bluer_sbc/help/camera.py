from typing import List

from bluer_options.terminal import show_usage


def help_capture_image(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@camera",
            "capture",
            "image",
        ],
        "capture an image.",
        mono=mono,
    )


def help_capture_video(
    tokens: List[str],
    mono: bool,
) -> str:
    args = [
        "[--length 10]",
        "[--preview 1]",
    ]

    return show_usage(
        [
            "@camera",
            "capture",
            "video",
        ]
        + args,
        "capture a video",
        mono=mono,
    )


def help_preview(
    tokens: List[str],
    mono: bool,
) -> str:
    args = [
        "[--length 10]",
    ]

    return show_usage(
        [
            "@camera",
            "preview",
            "[-]",
        ]
        + args,
        "preview.",
        mono=mono,
    )


help_functions = {
    "capture": {
        "image": help_capture_image,
        "video": help_capture_video,
    },
    "preview": help_preview,
}
