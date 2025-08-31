import glob
import os
from typing import Tuple, List
from webdav3.client import Client
from tqdm import tqdm

from bluer_objects.storage.base import StorageInterface
from bluer_objects import env
from bluer_objects import objects
from bluer_objects.host import unzip
from bluer_objects.storage.policies import DownloadPolicy
from bluer_objects.logger import logger


# tars the objects to avoid 'content-length' - see WebDAVInterface.
class WebDAVzipInterface(StorageInterface):
    name = "webdav-zip"

    def __init__(self):
        super().__init__()

        config = {
            "webdav_hostname": env.WEBDAV_HOSTNAME,
            "webdav_login": env.WEBDAV_LOGIN,
            "webdav_password": env.WEBDAV_PASSWORD,
        }

        self.client = Client(config)

    def clear(
        self,
        do_dryrun: bool = True,
    ) -> bool:
        logger.info(
            "{}.clear({})".format(
                self.__class__.__name__,
                "dryrun" if do_dryrun else "",
            )
        )

        count: int = 0
        for thing in tqdm(self.client.list()):
            if not thing.endswith(".zip"):
                continue
            if not thing.startswith("test"):
                continue

            logger.info(thing)
            if do_dryrun:
                continue

            try:
                self.client.clean(remote_path=thing)
            except Exception as e:
                logger.error(e)
                return False

            count += 1

        logger.info(f"deleted {count} object(s).")

        return True

    def download(
        self,
        object_name: str,
        filename: str = "",
        log: bool = True,
        policy: DownloadPolicy = DownloadPolicy.NONE,
    ) -> bool:
        object_path = objects.object_path(
            object_name=object_name,
            create=True,
        )
        zip_filename = f"{object_path}.zip"

        try:
            if not self.client.check(remote_path=f"{object_name}.zip"):
                logger.warning(f"{object_name} doesn't exist.")
                return True
        except Exception as e:
            logger.error(e)
            return False

        try:
            self.client.download_sync(
                remote_path=f"{object_name}.zip",
                local_path=zip_filename,
            )
        except Exception as e:
            logger.error(e)
            return False

        if not unzip(
            zip_filename=zip_filename,
            output_folder=object_path,
            log=log,
        ):
            return False

        return super().download(
            object_name=object_name,
            log=log,
            policy=policy,
        )

    def ls(
        self,
        object_name: str,
        where: str = "local",
    ) -> Tuple[bool, List[str]]:
        if where == "cloud":
            try:
                if self.client.check(remote_path=f"{object_name}.zip"):
                    return True, [f"{object_name}.zip"]
            except Exception as e:
                logger.error(e)
                return False, []

            return True, []

        return super().ls(
            object_name=object_name,
            where=where,
        )

    def upload(
        self,
        object_name: str,
        filename: str = "",
        public: bool = False,
        zip: bool = False,
        log: bool = True,
    ) -> bool:
        if public or zip:
            logger.error("public/zip upload not supported.")
            return False

        object_path = objects.object_path(object_name=object_name)

        if not zip(
            zip_filename=f"../{object_name}.zip",
            input_folder=".",
            work_dir=object_path,
            log=log,
        ):
            return False

        zip_filename = f"{object_path}.zip"
        try:
            self.client.upload_sync(
                remote_path=f"{object_name}.zip",
                local_path=zip_filename,
            )
        except Exception as e:
            logger.error(e)
            return False

        return super().upload(
            object_name=object_name,
            public=public,
            zip=zip,
            log=log,
        )
