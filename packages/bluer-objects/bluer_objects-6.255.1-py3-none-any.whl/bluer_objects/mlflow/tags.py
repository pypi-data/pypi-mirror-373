from typing import Tuple, Dict, List, Union
from mlflow.tracking import MlflowClient
from mlflow.entities import ViewType

from blueness import module
from bluer_options.options import Options
from bluer_options.logger import crash_report

from bluer_objects import NAME
from bluer_objects.mlflow.objects import to_experiment_name, to_object_name
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def create_filter_string(tags: str) -> str:
    tags_options = Options(tags)

    # https://www.mlflow.org/docs/latest/search-experiments.html
    return " and ".join(
        [f'tags."{keyword}" = "{value}"' for keyword, value in tags_options.items()]
    )


def get_tags(
    object_name: str,
    exclude_system_tags: bool = True,
) -> Tuple[bool, Dict[str, str]]:
    experiment_name = to_experiment_name(object_name)

    try:
        client = MlflowClient()
        experiment = client.get_experiment_by_name(experiment_name)

        if experiment is None:
            return True, {}

        tags = {
            keyword: value
            for keyword, value in experiment.tags.items()
            if not keyword.startswith("mlflow.") or not exclude_system_tags
        }

        return True, tags
    except:
        crash_report(f"{NAME}.get_tags({object_name})")
        return False, {}


# https://www.mlflow.org/docs/latest/search-experiments.html
def search(filter_string: str) -> List[str]:
    client = MlflowClient()

    return [
        to_object_name(experiment.name)
        for experiment in client.search_experiments(
            filter_string=filter_string,
            view_type=ViewType.ALL,
        )
    ]


def set_tags(
    object_name: str,
    tags: Union[str, Dict[str, str]],
    log: bool = True,
    icon="#️⃣ ",
) -> bool:
    experiment_name = to_experiment_name(object_name)

    try:
        tags = Options(tags)

        client = MlflowClient()

        experiment = client.get_experiment_by_name(experiment_name)
        if experiment is None:
            client.create_experiment(name=experiment_name)
            experiment = client.get_experiment_by_name(experiment_name)

        for key, value in tags.items():
            client.set_experiment_tag(experiment.experiment_id, key, value)
            if log:
                logger.info("{} {}.{}={}".format(icon, object_name, key, value))

    except:
        crash_report(f"{NAME}.set_tags({object_name})")
        return False

    return True
