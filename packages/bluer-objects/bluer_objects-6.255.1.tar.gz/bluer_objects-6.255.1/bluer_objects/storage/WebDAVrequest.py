import requests
from requests.auth import HTTPBasicAuth
import glob
from typing import Tuple, List
from xml.etree import ElementTree as ET
from tqdm import tqdm

from bluer_objects.storage.base import StorageInterface
from bluer_objects import env, file, path
from bluer_objects import objects
from bluer_objects.storage.policies import DownloadPolicy
from bluer_objects.logger import logger


# https://chatgpt.com/c/6824cf43-6738-8005-8733-54b6a77f20ee
class WebDAVRequestInterface(StorageInterface):
    name = "webdav-request"

    def clear(
        self,
        do_dryrun: bool = True,
        log: bool = True,
    ) -> bool:
        logger.info(
            "{}.clear({})".format(
                self.__class__.__name__,
                "dryrun" if do_dryrun else "",
            )
        )

        success, list_of_objects = self.list_raw(
            suffix="",
            recursive=False,
        )
        if not success:
            return False

        count: int = 0
        for thing in tqdm(list_of_objects):
            thing_name = thing.split(f"{env.WEBDAV_LOGIN}/", 1)[1]
            if not thing_name.startswith("test"):
                continue

            if not thing_name.endswith("/"):
                continue

            if not self.delete(
                object_name=thing_name.split("/", 1)[0],
                do_dryrun=do_dryrun,
                log=log,
            ):
                return False

            count += 1

        logger.info(f"deleted {count} object(s).")
        return True

    def delete(
        self,
        object_name: str,
        do_dryrun: bool = True,
        log: bool = True,
    ) -> bool:
        if log:
            logger.info(
                "{}.delete({}){}".format(
                    self.__class__.__name__,
                    object_name,
                    " dryrun" if do_dryrun else "",
                )
            )
        if do_dryrun:
            return True

        try:
            response = requests.request(
                method="DELETE",
                url=f"{env.WEBDAV_HOSTNAME}/{object_name}/",
                auth=HTTPBasicAuth(
                    env.WEBDAV_LOGIN,
                    env.WEBDAV_PASSWORD,
                ),
            )
        except Exception as e:
            logger.error(e)
            return False

        if response.status_code in [200, 204]:
            return True

        logger.error(f"failed to delete: {response.status_code} - {response.text}")
        return False

    def mkdir(
        self,
        path: str,
        log: bool = True,
    ) -> bool:
        url = f"{env.WEBDAV_HOSTNAME}/"
        for folder in path.split("/"):
            url = f"{url}{folder}/"

            try:
                response = requests.request(
                    "MKCOL",
                    url,
                    auth=HTTPBasicAuth(
                        env.WEBDAV_LOGIN,
                        env.WEBDAV_PASSWORD,
                    ),
                )
            except Exception as e:
                logger.error(e)
                return False

            if response.status_code == 405:  # Already exists
                continue

            if response.status_code == 201:  # Created
                if log:
                    logger.info(
                        "{}.mkdir {}".format(
                            self.__class__.__name__,
                            url.split(env.WEBDAV_HOSTNAME, 1)[1],
                        )
                    )
                continue

            logger.error(f"failed to create: {response.status_code} - {response.text}")
            return False

        return True

    def download(
        self,
        object_name: str,
        filename: str = "",
        log: bool = True,
        policy: DownloadPolicy = DownloadPolicy.NONE,
    ) -> bool:
        if filename:
            local_path = objects.path_of(
                object_name=object_name,
                filename=filename,
                create=True,
            )

            if not path.create(file.path(local_path)):
                return False

            url = f"{env.WEBDAV_HOSTNAME}/{object_name}/{filename}"

            try:
                response = requests.get(
                    url,
                    auth=HTTPBasicAuth(
                        env.WEBDAV_LOGIN,
                        env.WEBDAV_PASSWORD,
                    ),
                )
            except Exception as e:
                logger.error(e)
                return False

            if response.status_code == 404:  # object not found
                return True

            if response.status_code == 200:
                try:
                    with open(local_path, "wb") as file_:
                        file_.write(response.content)
                except Exception as e:
                    logger.error(e)
                    return False

                return super().download(
                    object_name=object_name,
                    filename=filename,
                    log=log,
                    policy=policy,
                )

            logger.error(f"failed to download: {response.status_code}")
            return False

        success, list_of_files = self.ls(
            object_name=object_name,
            where="cloud",
        )
        if not success:
            return False

        for filename_ in tqdm(list_of_files):
            if not self.download(
                object_name=object_name,
                filename=filename_,
                log=log,
                policy=policy,
            ):
                return False

        return True

    def list_raw(
        self,
        suffix: str,
        recursive: bool,
    ) -> Tuple[bool, List[str]]:
        # https://chatgpt.com/c/6824f8d3-d9c0-8005-a7fa-d646f812f4b7
        headers = {
            "Depth": "infinity" if recursive else "1",
            "Content-Type": "application/xml",
        }

        # Minimal PROPFIND XML body
        data = """<?xml version="1.0"?>
        <d:propfind xmlns:d="DAV:">
        <d:prop><d:displayname/></d:prop>
        </d:propfind>"""

        try:
            response = requests.request(
                method="PROPFIND",
                url=f"{env.WEBDAV_HOSTNAME}/{suffix}",
                data=data,
                headers=headers,
                auth=HTTPBasicAuth(
                    env.WEBDAV_LOGIN,
                    env.WEBDAV_PASSWORD,
                ),
            )
        except Exception as e:
            logger.error(e)
            return False, []

        if response.status_code == 404:  # object not found
            return True, []

        if response.status_code in (207, 207):
            tree = ET.fromstring(response.content)
            ns = {"d": "DAV:"}
            list_of_files = []
            for resp in tree.findall("d:response", ns):
                href = resp.find("d:href", ns).text
                list_of_files.append(href)

            return True, list_of_files

        logger.error(f"failed to list: {response.status_code} - {response.text}")
        return False, []

    def ls(
        self,
        object_name: str,
        where: str = "local",
    ) -> Tuple[bool, List[str]]:
        if where == "cloud":
            success, list_of_files = self.list_raw(
                suffix=f"{object_name}/",
                recursive=True,
            )

            return success, sorted(
                [
                    filename
                    for filename in [
                        filename.split(f"{env.WEBDAV_LOGIN}/{object_name}/", 1)[1]
                        for filename in list_of_files
                        if not filename.endswith("/")
                    ]
                    if filename
                ]
            )

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

        if filename:
            if not self.mkdir(
                path="{}/{}".format(
                    object_name,
                    file.path(filename),
                ),
                log=log,
            ):
                return False

            url = f"{env.WEBDAV_HOSTNAME}/{object_name}/{filename}"

            local_path = objects.path_of(
                object_name=object_name,
                filename=filename,
            )

            try:
                with open(local_path, "rb") as file_data:
                    response = requests.put(
                        url,
                        data=file_data,
                        auth=HTTPBasicAuth(
                            env.WEBDAV_LOGIN,
                            env.WEBDAV_PASSWORD,
                        ),
                    )
            except Exception as e:
                logger.error(e)
                return False

            if response.status_code in [200, 201, 204]:
                return super().upload(
                    object_name=object_name,
                    filename=filename,
                    public=public,
                    zip=zip,
                    log=log,
                )

            logger.error(f"failed to upload: {response.status_code} - {response.text}")
            return False

        object_path = "{}/".format(objects.object_path(object_name=object_name))
        for filename_ in tqdm(
            sorted(
                glob.glob(
                    objects.path_of(
                        object_name=object_name,
                        filename="**",
                    ),
                    recursive=True,
                )
            )
        ):
            if not file.exists(filename_):
                continue

            if not self.upload(
                object_name=object_name,
                filename=filename_.split(object_path, 1)[1],
                public=public,
                log=log,
            ):
                return False

        return True
