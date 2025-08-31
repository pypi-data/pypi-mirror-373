#! /usr/bin/env bash

function bluer_objects_mlflow_lock() {
    local task=$1

    local function_name=bluer_objects_mlflow_lock_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 -m bluer_objects.mlflow.lock "$@"
}

bluer_ai_source_caller_suffix_path /lock
