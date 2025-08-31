from typing import List

from bluer_options.terminal import show_usage


def help_select_target(
    tokens: List[str],
    mono: bool,
) -> str:
    args = [
        "[--host <hostname>]",
        "[--loop 0]",
    ]

    return show_usage(
        [
            "@swallow",
            "select_target",
        ]
        + args,
        "select swallow target.",
        mono=mono,
    )
