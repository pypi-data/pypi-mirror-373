import boto3
import os
from botocore.exceptions import ClientError
import glob
from typing import Tuple, List
from xml.etree import ElementTree as ET
from tqdm import tqdm
from functools import reduce

from bluer_objects.storage.base import StorageInterface
from bluer_objects.env import ABCLI_OBJECT_ROOT
from bluer_objects import env, file, path
from bluer_objects import objects
from bluer_objects.storage.policies import DownloadPolicy
from bluer_objects.logger import logger


# https://docs.arvancloud.ir/fa/developer-tools/sdk/object-storage/
class S3Interface(StorageInterface):
    name = "s3"

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

        try:
            s3 = boto3.client(
                "s3",
                endpoint_url=env.S3_STORAGE_ENDPOINT_URL,
                aws_access_key_id=env.S3_STORAGE_AWS_ACCESS_KEY_ID,
                aws_secret_access_key=env.S3_STORAGE_AWS_SECRET_ACCESS_KEY,
            )

            paginator = s3.get_paginator("list_objects_v2")
            pages = paginator.paginate(
                Bucket=env.S3_STORAGE_BUCKET,
                Prefix="test",
            )
        except Exception as e:
            logger.error(e)
            return False

        list_of_objects = sorted(
            list(
                set(
                    reduce(
                        lambda x, y: x + y,
                        [
                            [
                                obj["Key"].split("/", 1)[0]
                                for obj in page.get("Contents", [])
                            ]
                            for page in pages
                        ],
                        [],
                    )
                )
            )
        )

        logger.info(f"{len(list_of_objects)} object(s) to delete.")

        for object_name in tqdm(list_of_objects):
            if not self.delete(
                object_name=object_name,
                do_dryrun=do_dryrun,
            ):
                return False

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
            s3 = boto3.resource(
                "s3",
                endpoint_url=env.S3_STORAGE_ENDPOINT_URL,
                aws_access_key_id=env.S3_STORAGE_AWS_ACCESS_KEY_ID,
                aws_secret_access_key=env.S3_STORAGE_AWS_SECRET_ACCESS_KEY,
            )
            bucket = s3.Bucket(env.S3_STORAGE_BUCKET)

            objects_to_delete = bucket.objects.filter(Prefix=f"{object_name}/")
            delete_requests = [{"Key": obj.key} for obj in objects_to_delete]

            if not delete_requests:
                logger.warning(f"no files found under {object_name}.")
                return True

            bucket.delete_objects(Delete={"Objects": delete_requests})
        except Exception as e:
            logger.error(e)
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

            if policy == DownloadPolicy.DOESNT_EXIST and file.exists(local_path):
                if log:
                    logger.info(f"✅ {filename}")
                return True

            if not path.create(file.path(local_path)):
                return False

            try:
                s3_resource = boto3.resource(
                    "s3",
                    endpoint_url=env.S3_STORAGE_ENDPOINT_URL,
                    aws_access_key_id=env.S3_STORAGE_AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=env.S3_STORAGE_AWS_SECRET_ACCESS_KEY,
                )
            except Exception as e:
                logger.error(e)
                return False

            try:
                bucket = s3_resource.Bucket(env.S3_STORAGE_BUCKET)

                bucket.download_file(
                    f"{object_name}/{filename}",
                    local_path,
                )
            except ClientError as e:
                if int(e.response["Error"]["Code"]) == 404:  # Not found
                    return True
                logger.error(e)
                return False

            return super().download(
                object_name=object_name,
                filename=filename,
                log=log,
                policy=policy,
            )

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

    def ls(
        self,
        object_name: str,
        where: str = "local",
    ) -> Tuple[bool, List[str]]:
        if where == "cloud":
            try:
                s3 = boto3.client(
                    "s3",
                    endpoint_url=env.S3_STORAGE_ENDPOINT_URL,
                    aws_access_key_id=env.S3_STORAGE_AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=env.S3_STORAGE_AWS_SECRET_ACCESS_KEY,
                )

                prefix = f"{object_name}/"

                paginator = s3.get_paginator("list_objects_v2")
                pages = paginator.paginate(
                    Bucket=env.S3_STORAGE_BUCKET,
                    Prefix=prefix,
                )
            except Exception as e:
                logger.error(e)
                return False, []

            return True, sorted(
                reduce(
                    lambda x, y: x + y,
                    [
                        [
                            obj["Key"].split(prefix, 1)[1]
                            for obj in page.get("Contents", [])
                        ]
                        for page in pages
                    ],
                    [],
                )
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
        if filename or zip:
            local_path = (
                os.path.join(
                    ABCLI_OBJECT_ROOT,
                    f"{object_name}.tar.gz",
                )
                if zip
                else objects.path_of(
                    object_name=object_name,
                    filename=filename,
                )
            )

            bucket_name = (
                env.S3_PUBLIC_STORAGE_BUCKET if public else env.S3_STORAGE_BUCKET
            )

            try:
                s3_resource = boto3.resource(
                    "s3",
                    endpoint_url=env.S3_STORAGE_ENDPOINT_URL,
                    aws_access_key_id=env.S3_STORAGE_AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=env.S3_STORAGE_AWS_SECRET_ACCESS_KEY,
                )

                bucket = s3_resource.Bucket(bucket_name)

                with open(local_path, "rb") as fp:
                    bucket.put_object(
                        ACL="public-read" if public else "private",
                        Body=fp,
                        Key=(
                            f"{object_name}.tar.gz"
                            if zip
                            else f"{object_name}/{filename}"
                        ),
                    )
            except ClientError as e:
                logger.error(e)
                return False

            if public:
                logger.info(
                    "🔗 https://{}.{}/{}".format(
                        bucket_name,
                        env.S3_STORAGE_ENDPOINT_URL.split("https://", 1)[1],
                        f"{object_name}.tar.gz" if zip else f"{object_name}/{filename}",
                    )
                )

            return super().upload(
                object_name=object_name,
                filename=filename,
                public=public,
                zip=zip,
                log=log,
            )

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
