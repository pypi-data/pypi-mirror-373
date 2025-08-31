#! /usr/bin/env bash

function bluer_objects_mlflow_tags_search() {
    local options=$1
    local is_explicit=$(bluer_ai_option_int "$options" explicit 0)

    python3 -m bluer_objects.mlflow \
        search \
        --explicit_query $is_explicit \
        --tags "$options" \
        "${@:2}"
}
