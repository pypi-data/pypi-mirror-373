from typing import List

from bluer_options.terminal import show_usage


def help_create_test_asset(
    tokens: List[str],
    mono: bool,
) -> str:
    args = [
        "[--depth 10]",
    ]

    return show_usage(
        [
            "@create_test_asset",
            "[.|<object-name>]",
        ]
        + args,
        "create test asset.",
        mono=mono,
    )
