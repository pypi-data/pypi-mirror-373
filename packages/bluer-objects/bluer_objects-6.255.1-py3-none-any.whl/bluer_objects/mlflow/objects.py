from typing import Tuple
import mlflow
from mlflow.tracking import MlflowClient

from blueness import module
from bluer_options.logger import crash_report

from bluer_objects import NAME
from bluer_objects.env import ABCLI_MLFLOW_EXPERIMENT_PREFIX
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def get_id(
    object_name: str,
    create: bool = False,
) -> Tuple[bool, str]:
    experiment_name = to_experiment_name(object_name)

    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            if create:
                MlflowClient().create_experiment(name=experiment_name)
                experiment = mlflow.get_experiment_by_name(experiment_name)
            else:
                return True, ""

        return True, dict(experiment)["experiment_id"]
    except:
        crash_report(f"{NAME}.get_id({object_name})")

        return False, ""


def rm(
    object_name: str,
    is_id: bool = False,
) -> bool:
    if is_id:
        experiment_id = object_name
    else:
        success, experiment_id = get_id(object_name)
        if not success:
            return success

    try:
        client = MlflowClient()

        # get list of run_ids

        # delete all runs

        client.delete_experiment(experiment_id)
    except:
        crash_report("mlflow.rm({})".format(object_name))
        return False

    logger.info(
        "🚮 {}".format(
            "#{}".format(experiment_id)
            if is_id
            else "{} (#{})".format(object_name, experiment_id)
        )
    )

    return True


def to_experiment_name(object_name: str) -> str:
    return f"{ABCLI_MLFLOW_EXPERIMENT_PREFIX}{object_name}"


def to_object_name(experiment_name: str) -> str:
    return experiment_name.split(ABCLI_MLFLOW_EXPERIMENT_PREFIX)[-1]
