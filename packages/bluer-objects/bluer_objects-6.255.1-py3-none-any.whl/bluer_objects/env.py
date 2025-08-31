from typing import Union
import os

from bluer_options.env import load_config, load_env, get_env

load_env(__name__)
load_config(__name__)

HOME = get_env("HOME")

abcli_object_path = get_env("abcli_object_path")

ABCLI_PATH_STORAGE = get_env(
    "ABCLI_PATH_STORAGE",
    os.path.join(HOME, "storage"),
)

abcli_object_name = get_env("abcli_object_name")


ABCLI_OBJECT_ROOT = get_env(
    "ABCLI_OBJECT_ROOT",
    os.path.join(ABCLI_PATH_STORAGE, "abcli"),
)

abcli_path_git = get_env(
    "abcli_path_git",
    os.path.join(HOME, "git"),
)

ABCLI_PATH_STATIC = get_env("ABCLI_PATH_STATIC")

# https://www.randomtextgenerator.com/
DUMMY_TEXT = "This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text. This is some dummy text."

ABCLI_MLFLOW_EXPERIMENT_PREFIX = get_env("ABCLI_MLFLOW_EXPERIMENT_PREFIX")

S3_STORAGE_BUCKET = get_env("S3_STORAGE_BUCKET")
S3_PUBLIC_STORAGE_BUCKET = get_env("S3_PUBLIC_STORAGE_BUCKET")

S3_STORAGE_ENDPOINT_URL = get_env("S3_STORAGE_ENDPOINT_URL")
S3_STORAGE_AWS_ACCESS_KEY_ID = get_env("S3_STORAGE_AWS_ACCESS_KEY_ID")
S3_STORAGE_AWS_SECRET_ACCESS_KEY = get_env("S3_STORAGE_AWS_SECRET_ACCESS_KEY")

BLUER_OBJECTS_STORAGE_INTERFACE = get_env("BLUER_OBJECTS_STORAGE_INTERFACE")

MLFLOW_DEPLOYMENT = get_env("MLFLOW_DEPLOYMENT", "local")
if MLFLOW_DEPLOYMENT == "local":
    MLFLOW_TRACKING_URI = os.path.join(
        os.environ.get("HOME"),
        "mlflow",
    )
else:
    MLFLOW_TRACKING_URI = MLFLOW_DEPLOYMENT
os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI
MLFLOW_LOG_ARTIFACTS = "arvan" not in MLFLOW_DEPLOYMENT

MLFLOW_LOCK_WAIT_FOR_CLEARANCE = get_env("MLFLOW_LOCK_WAIT_FOR_CLEARANCE", 3)
MLFLOW_LOCK_WAIT_FOR_EXCLUSIVITY = get_env("MLFLOW_LOCK_WAIT_FOR_EXCLUSIVITY", 1)

WEBDAV_HOSTNAME = get_env("WEBDAV_HOSTNAME")
WEBDAV_LOGIN = get_env("WEBDAV_LOGIN")
WEBDAV_PASSWORD = get_env("WEBDAV_PASSWORD")
