#! /usr/bin/env bash

function bluer_objects_mlflow_tags_set() {
    local object_name=$(bluer_ai_clarify_object $1 .)

    local tags=$2

    python3 -m bluer_objects.mlflow \
        set_tags \
        --object_name $object_name \
        --tags "$tags" \
        "${@:3}"
}
