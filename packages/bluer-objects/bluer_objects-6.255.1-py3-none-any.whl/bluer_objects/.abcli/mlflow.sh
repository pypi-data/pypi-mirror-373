#! /usr/bin/env bash

function bluer_objects_mlflow() {
    local task=$1

    local function_name=bluer_objects_mlflow_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    if [[ ",get_id,get_run_id,rm," == *",$task,"* ]]; then
        local object_name=$(bluer_ai_clarify_object $2 .)

        python3 -m bluer_objects.mlflow \
            $task \
            --object_name $object_name \
            "${@:3}"

        return
    fi

    bluer_ai_log_error "@mlflow: $task: command not found."
    return 1
}

bluer_ai_source_caller_suffix_path /mlflow
