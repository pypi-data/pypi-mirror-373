from bluer_ai.help.generic import help_functions as generic_help_functions

from bluer_objects import ALIAS
from bluer_objects.help.clone import help_clone
from bluer_objects.help.create_test_asset import help_create_test_asset
from bluer_objects.help.download import help_download
from bluer_objects.help.gif import help_gif
from bluer_objects.help.host import help_functions as help_host
from bluer_objects.help.ls import help_ls
from bluer_objects.help.metadata import help_functions as help_metadata
from bluer_objects.help.mlflow import help_functions as help_mlflow
from bluer_objects.help.upload import help_upload
from bluer_objects.help.web import help_functions as help_web

help_functions = generic_help_functions(plugin_name=ALIAS)

help_functions.update(
    {
        "clone": help_clone,
        "create_test_asset": help_create_test_asset,
        "download": help_download,
        "gif": help_gif,
        "host": help_host,
        "ls": help_ls,
        "metadata": help_metadata,
        "mlflow": help_mlflow,
        "upload": help_upload,
        "web": help_web,
    }
)
