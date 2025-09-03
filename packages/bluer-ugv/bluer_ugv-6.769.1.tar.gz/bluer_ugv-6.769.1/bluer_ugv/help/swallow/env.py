from typing import List

from bluer_options.terminal import show_usage, xtra


def help_cp(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@swallow",
            "env",
            "cp",
            "[<env-name>]",
        ],
        "cp swallow swallow-raspbian-<env-name>.",
        mono=mono,
    )


def help_list(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@swallow",
            "env",
            "list",
        ],
        "list swallow envs.",
        mono=mono,
    )


def help_set(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@swallow",
            "env",
            "set",
            "steering",
            "0 | 1",
        ],
        "set env.",
        {
            "steering: BLUER_SBC_SWALLOW_HAS_STEERING": "",
        },
        mono=mono,
    )


help_functions = {
    "cp": help_cp,
    "list": help_list,
    "set": help_set,
}
