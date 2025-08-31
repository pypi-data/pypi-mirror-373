#! /usr/bin/env bash

function bluer_objects_mlflow_run() {
    local object_name=$(bluer_ai_clarify_object $1 .)

    python3 -m bluer_objects.mlflow \
        start_end_run \
        --object_name $object_name \
        --start_end "$2" \
        "${@:3}"
}
