from typing import List

from bluer_options.terminal import show_usage, xtra

from bluer_objects.help.mlflow.cache import help_functions as help_cache
from bluer_objects.help.mlflow.lock import help_functions as help_lock
from bluer_objects.help.mlflow.tags import help_functions as help_tags
from bluer_ai import env


def help_browse(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("experiment,models", mono=mono)

    return show_usage(
        [
            "@mlflow",
            "browse",
            f"[{options}]",
            "[.|<object-name>]",
        ],
        "browse mlflow.",
        mono=mono,
    )


def help_deploy(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun,port=<5001>", mono=mono)

    return show_usage(
        [
            "@mlflow",
            "deploy",
            f"[{options}]",
        ],
        "deploy mlflow.",
        mono=mono,
    )


def help_deploy_set(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@mlflow",
            "deploy",
            "set",
            "<url> | local",
        ],
        "set mlflow deployment.",
        mono=mono,
    )


def help_get_id(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@mlflow",
            "get_id",
            "[.|<object-name>]",
        ],
        "get mlflow id for <object-name>.",
        mono=mono,
    )


def help_get_run_id(
    tokens: List[str],
    mono: bool,
) -> str:
    args = [
        "[--count <1>]",
        "[--delim <space>]",
        "[--offset <0>]",
    ]

    return show_usage(
        [
            "@mlflow",
            "get_run_id",
            "[.|<object-name>]",
        ]
        + args,
        "get mlflow run ids for <object-name>.",
        mono=mono,
    )


def help_list_registered_models(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@mlflow",
            "list_registered_models",
        ],
        "list mlflow registered models.",
        mono=mono,
    )


def help_log_artifacts(
    tokens: List[str],
    mono: bool,
) -> str:
    args = ["[--model_name <model-name>]"]

    return show_usage(
        [
            "@mlflow",
            "log_artifacts",
            "[.|<object-name>]",
        ]
        + args,
        "<object-name> -artifacts-> mlflow.",
        mono=mono,
    )


def help_log_run(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@mlflow",
            "log_run",
            "[.|<object-name>]",
        ],
        "<object-name> -run-> mlflow.",
        mono=mono,
    )


def help_rm(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@mlflow",
            "rm",
            "[.|<object-name>]",
        ],
        "rm <object-name> from mlflow.",
        mono=mono,
    )


def help_run(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@mlflow",
            "run",
            "start | end",
            "[.|<object-name>]",
        ],
        "start | end mlflow run.",
        mono=mono,
    )


def help_test(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun", mono=mono)

    return show_usage(
        [
            "@mlflow",
            "test",
            f"[{options}]",
        ],
        "test mlflow.",
        mono=mono,
    )


def help_transition(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "model=<model-name>,stage=<stage>,version=<version>"

    return show_usage(
        [
            "@mlflow",
            "transition",
            f"[{options}]",
            "[<description>]",
        ],
        "transition <model-name>.",
        {
            "stage: {}".format(" | ".join(env.ABCLI_MLFLOW_STAGES.split("|"))): "",
        },
        mono=mono,
    )


help_functions = {
    "browse": help_browse,
    "cache": help_cache,
    "deploy": {
        "": help_deploy,
        "set": help_deploy_set,
    },
    "get_id": help_get_id,
    "get_run_id": help_get_run_id,
    "list_registered_models": help_list_registered_models,
    "lock": help_lock,
    "log_artifacts": help_log_artifacts,
    "log_run": help_log_run,
    "rm": help_rm,
    "run": help_run,
    "tags": help_tags,
    "test": help_test,
    "transition": help_transition,
}
