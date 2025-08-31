from typing import Tuple, List
import mlflow
import random
from mlflow.tracking import MlflowClient
from mlflow.entities import ViewType

from blueness import module
from bluer_options import string
from bluer_options.logger import crash_report

from bluer_objects import NAME
from bluer_objects.mlflow.objects import get_id
from bluer_objects.mlflow.tags import get_tags
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def end_run(
    object_name: str,
) -> bool:
    try:
        mlflow.end_run()
        logger.info("⏹️  {}".format(object_name))
    except:
        crash_report(f"{NAME}.end_run({object_name})")
        return False

    return True


def get_run_id(
    object_name: str,
    count: int = -1,
    offset: int = 0,
    create: bool = False,
    is_id: bool = False,
) -> Tuple[bool, List[str]]:
    if is_id:
        experiment_id = object_name
    else:
        success, experiment_id = get_id(object_name, create=create)
        if not success:
            return False, []

    try:
        client = MlflowClient()

        list_of_runs = client.search_runs(
            experiment_ids=[experiment_id],
            run_view_type=ViewType.ACTIVE_ONLY,
            max_results=count + offset,
        )

        return True, [run._info.run_id for run in list_of_runs][offset:]

    except:
        crash_report(f"{NAME}.get_run_id({object_name})")
        return False, []


def start_run(
    object_name: str,
) -> bool:
    success, experiment_id = get_id(object_name, create=True)
    if not success:
        return False

    max_count = 25000
    success, list_of_runs = get_run_id(
        experiment_id,
        count=max_count,
        is_id=True,
    )
    if not success:
        return False

    run_counter = len(list_of_runs) + 1
    if run_counter > max_count:
        logger.warning(f"{object_name}: more than {max_count} runs!")
        run_counter = max_count + random.randint(1, max_count)

    run_name = f"{object_name}-{run_counter:05d}"

    success, tags = get_tags(object_name)
    if not success:
        return False

    try:
        mlflow.start_run(
            experiment_id=experiment_id,
            tags=tags,
            run_name=run_name,
        )
        logger.info(f"⏺️  {object_name} | {run_counter:05d}")
    except:
        crash_report(f"{NAME}.start_run({object_name})")
        return False

    return True
