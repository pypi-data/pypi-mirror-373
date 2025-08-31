from typing import List

from bluer_options.terminal import show_usage


def help_is_accessible(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@web",
            "is_accessible",
            "<url>",
        ],
        "is <url> accessible?",
        mono=mono,
    )


def help_where_am_i(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@web",
            "where_am_i",
        ],
        "where am I?",
        mono=mono,
    )


help_functions = {
    "is_accessible": help_is_accessible,
    "where_am_i": help_where_am_i,
}
