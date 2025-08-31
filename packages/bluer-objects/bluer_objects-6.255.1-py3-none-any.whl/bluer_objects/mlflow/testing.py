import mlflow

from blueness import module
from bluer_options import string
from bluer_options.logger import crash_report

from bluer_objects import NAME, VERSION
from bluer_objects.mlflow.objects import get_id
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def test() -> bool:
    object_name = string.pretty_date(
        as_filename=True,
        unique=True,
    )

    success, experiment_id = get_id(
        object_name,
        create=True,
    )
    if not success:
        return success

    try:
        mlflow.start_run(
            experiment_id=experiment_id,
            tags={"purpose": "testing"},
        )
        mlflow.end_run()

        logger.info(f"✅ {NAME}-{VERSION}-{mlflow.version.VERSION}")
    except:
        crash_report(f"{NAME}.test()")
        return False

    return True
