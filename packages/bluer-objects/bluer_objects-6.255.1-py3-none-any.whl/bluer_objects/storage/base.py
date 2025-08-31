import os
import glob
from typing import Tuple, List

from bluer_objects import objects
from bluer_objects.storage.policies import DownloadPolicy
from bluer_objects.logger import logger


class StorageInterface:
    def clear(
        self,
        do_dryrun: bool = True,
    ) -> bool:
        return True

    def download(
        self,
        object_name: str,
        filename: str = "",
        log: bool = True,
        policy: DownloadPolicy = DownloadPolicy.NONE,
    ) -> bool:
        if log:
            logger.info(
                "{}.download {}{}{}".format(
                    self.__class__.__name__,
                    object_name,
                    f"/{filename}" if filename else "",
                    (
                        ""
                        if policy == DownloadPolicy.NONE
                        else " - policy:{}".format(policy.name.lower())
                    ),
                )
            )

        return True

    def ls(
        self,
        object_name: str,
        where: str = "local",
    ) -> Tuple[bool, List[str]]:
        if where == "local":
            object_path = objects.object_path(
                object_name=object_name,
            )

            return True, sorted(
                [
                    os.path.relpath(filename, start=object_path)
                    for filename in glob.glob(
                        os.path.join(
                            object_path,
                            "**",
                            "*",
                        ),
                        recursive=True,
                    )
                    if os.path.isfile(filename)
                ]
            )

        if where == "cloud":
            logger.error("not implemented")
            return False, []

        logger.error(f"Unknown 'where': {where}")
        return False, []

    def upload(
        self,
        object_name: str,
        filename: str = "",
        public: bool = False,
        zip: bool = False,
        log: bool = True,
    ) -> bool:
        if log:
            logger.info(
                "{}.upload {}{}{}".format(
                    self.__class__.__name__,
                    object_name,
                    ".tar.gz" if zip else f"/{filename}" if filename else "",
                    " [public]" if public else "",
                )
            )

        return True
