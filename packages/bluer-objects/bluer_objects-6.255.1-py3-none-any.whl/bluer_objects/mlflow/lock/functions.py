import time

from blueness import module
from bluer_options import string

from bluer_objects import NAME, env
from bluer_objects.mlflow.tags import get_tags, set_tags
from bluer_objects.logger import logger


NAME = module.name(__file__, NAME)


def lock(
    object_name: str,
    lock_name: str = "lock",
    timeout: int = -1,
    verbose: bool = True,
) -> bool:
    logger.info(
        "{}.lock: {}.{}{}".format(
            NAME,
            object_name,
            lock_name,
            "" if timeout == -1 else " @ {}".format(string.pretty_duration(timeout)),
        )
    )

    start_time = time.time()
    while True:
        if timeout > 0 and time.time() - start_time > timeout:
            if verbose:
                logger.warning(
                    "{}.lock: {}.{} timeout.".format(
                        NAME,
                        object_name,
                        lock_name,
                    )
                )
            return False

        success, list_of_tags = get_tags(object_name=object_name)
        if not success:
            return False

        lock_value = list_of_tags.get(lock_name, "")
        if lock_value:
            if verbose:
                logger.warning(
                    "{}.lock: {}.{} is locked by {}.".format(
                        NAME,
                        object_name,
                        lock_name,
                        lock_value,
                    )
                )
            time.sleep(env.MLFLOW_LOCK_WAIT_FOR_CLEARANCE)
            continue

        lock_value = string.random()
        if not set_tags(
            object_name=object_name,
            tags={lock_name: lock_value},
            log=verbose,
            icon="🔒",
        ):
            return False

        time.sleep(env.MLFLOW_LOCK_WAIT_FOR_EXCLUSIVITY)

        success, list_of_tags = get_tags(object_name=object_name)
        if not success:
            return False

        lock_value_read = list_of_tags.get(lock_name, "")
        if lock_value_read != lock_value:
            if verbose:
                logger.warning(
                    "{}.lock: {}.{} is relocked by {} != {}.".format(
                        NAME,
                        object_name,
                        lock_name,
                        lock_value_read,
                        lock_value,
                    )
                )
            time.sleep(env.MLFLOW_LOCK_WAIT_FOR_CLEARANCE)
            continue

        break

    logger.info(
        "{}.lock: {}.{} is locked by {}.".format(
            NAME,
            object_name,
            lock_name,
            lock_value,
        )
    )
    return True


def unlock(
    object_name: str,
    lock_name: str = "lock",
    verbose: bool = True,
) -> bool:
    logger.info(
        "{}.unlock: {}.{}".format(
            NAME,
            object_name,
            lock_name,
        )
    )

    return set_tags(
        object_name=object_name,
        tags={lock_name: ""},
        log=verbose,
        icon="🔒",
    )
