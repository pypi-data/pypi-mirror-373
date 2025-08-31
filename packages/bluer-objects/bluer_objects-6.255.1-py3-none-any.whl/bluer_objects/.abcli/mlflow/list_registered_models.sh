#! /usr/bin/env bash

function bluer_objects_mlflow_list_registered_models() {
    local options=$1

    python3 -m bluer_objects.mlflow \
        list_registered_models \
        "${@:2}"
}
