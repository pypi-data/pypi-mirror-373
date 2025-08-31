from typing import List

from bluer_options.terminal import show_usage, xtra


def help_lock(
    tokens: List[str],
    mono: bool,
) -> str:
    args = [
        "[--lock <lock-name>]",
        "[--timeout <10>]",
        "[--verbose 0]",
    ]

    return show_usage(
        [
            "@lock",
            "lock",
            "[.|<object-name>]",
        ]
        + args,
        "lock <object-name>.",
        mono=mono,
    )


def help_unlock(
    tokens: List[str],
    mono: bool,
) -> str:
    args = [
        "[--lock <lock-name>]",
        "[--verbose 0]",
    ]

    return show_usage(
        [
            "@lock",
            "unlock",
            "[.|<object-name>]",
        ]
        + args,
        "unlock <object-name>.",
        mono=mono,
    )


help_functions = {
    "lock": help_lock,
    "unlock": help_unlock,
}
