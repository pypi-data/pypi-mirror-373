from typing import List

from bluer_options.terminal import show_usage, xtra

from bluer_objects.storage.policies import DownloadPolicy


def help_download(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "".join(
        [
            "filename=<filename>",
            xtra(
                ",policy={}".format(
                    "|".join(sorted([policy.name.lower() for policy in DownloadPolicy]))
                ),
                mono=mono,
            ),
        ]
    )

    open_options = "open,QGIS"

    return show_usage(
        [
            "@download",
            f"[{options}]",
            "[.|<object-name>]",
            f"[{open_options}]",
        ],
        "download <object-name>.",
        mono=mono,
    )
