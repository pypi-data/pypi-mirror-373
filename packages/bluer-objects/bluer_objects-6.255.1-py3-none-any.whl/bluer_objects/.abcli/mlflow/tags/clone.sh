#! /usr/bin/env bash

function bluer_objects_mlflow_tags_clone() {
    local source_object=$(bluer_ai_clarify_object $1 ..)

    local destination_object=$(bluer_ai_clarify_object $2 .)

    bluer_ai_log "mlflow: tags: clone: $source_object -> $destination_object ..."

    python3 -m bluer_objects.mlflow \
        clone_tags \
        --destination_object $destination_object \
        --source_object $source_object \
        "${@:3}"
}
