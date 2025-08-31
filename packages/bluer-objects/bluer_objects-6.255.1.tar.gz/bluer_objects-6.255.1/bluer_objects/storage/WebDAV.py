from typing import List, Tuple
from webdav3.client import Client

from bluer_objects.storage.base import StorageInterface
from bluer_objects import env, file, path
from bluer_objects import objects
from bluer_objects.storage.policies import DownloadPolicy
from bluer_objects.logger import logger


# https://chatgpt.com/c/67e06812-4af0-8005-b2ab-5f9a1eabbbe3
# https://pypi.org/project/webdavclient3/


# ❗️ fails on .txt, .json, .yaml, ... other files with 'content-length',
# see WebDAV.ipynb for details (set BLUER_OBJECTS_STORAGE_INTERFACE=webdav).
class WebDAVInterface(StorageInterface):
    name = "webdav"

    def __init__(self):
        super().__init__()

        config = {
            "webdav_hostname": env.WEBDAV_HOSTNAME,
            "webdav_login": env.WEBDAV_LOGIN,
            "webdav_password": env.WEBDAV_PASSWORD,
        }

        self.client = Client(config)

    def mkdir(
        self,
        path: str,
        log: bool = True,
    ) -> bool:
        try:
            if self.client.check(path):
                return True

            self.client.mkdir(path)
        except Exception as e:
            logger.error(e)
            return False

        if log:
            logger.info(
                "{}.mkdir: {}".format(
                    self.__class__.__name__,
                    path,
                )
            )

        return True

    def download(
        self,
        object_name: str,
        filename: str = "",
        log: bool = True,
        policy: DownloadPolicy = DownloadPolicy.NONE,
    ) -> bool:
        local_path = objects.path_of(
            object_name=object_name,
            filename=filename,
            create=True,
        )

        if filename:
            if not path.create(file.path(local_path)):
                return False

        try:
            self.client.download_sync(
                remote_path=f"{object_name}/{filename}",
                local_path=local_path,
            )
        except Exception as e:
            logger.error(e)
            return False

        return super().download(
            object_name=object_name,
            filename=filename,
            log=log,
            policy=policy,
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

        if filename:
            remote_dir = "/".join([object_name] + filename.split("/")[:-1])
            if not self.mkdir(
                path=remote_dir,
                log=log,
            ):
                return False

        try:
            self.client.upload_sync(
                remote_path=f"{object_name}/{filename}",
                local_path=objects.path_of(
                    object_name=object_name,
                    filename=filename,
                ),
            )
        except Exception as e:
            logger.error(e)
            return False

        return super().upload(
            object_name=object_name,
            filename=filename,
            public=public,
            zip=zip,
            log=log,
        )
