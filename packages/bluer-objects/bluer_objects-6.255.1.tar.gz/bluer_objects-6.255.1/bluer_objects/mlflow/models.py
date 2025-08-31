from typing import Tuple, List
from mlflow.tracking import MlflowClient

from blueness import module
from bluer_options.logger import crash_report

from bluer_objects import NAME
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def list_registered_models() -> Tuple[
    bool,
    List[str],
]:
    try:
        client = MlflowClient()
        return True, [dict(rm)["name"] for rm in client.search_registered_models()]

    except:
        crash_report(f"{NAME}.list_registered_models()")
        return False, []


def transition(
    model_name: str,
    version: str,
    stage_name: str,
    description: str,
) -> bool:
    logger.info(
        '{}.transition: {}(#{}) ->  {} - "{}")'.format(
            NAME,
            model_name,
            version,
            stage_name,
            description,
        )
    )

    try:
        client = MlflowClient()
        client.transition_model_version_stage(
            name=model_name, version=version, stage=stage_name
        )

        if description:
            client.update_model_version(
                name=model_name, version=version, description=description
            )

    except:
        crash_report(f"{NAME}.transition({model_name})")
        return False

    return True
