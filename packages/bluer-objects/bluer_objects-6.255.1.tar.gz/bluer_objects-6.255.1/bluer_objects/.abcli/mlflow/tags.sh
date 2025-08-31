#! /usr/bin/env bash

function bluer_objects_mlflow_tags() {
    local task=$1

    local function_name=bluer_objects_mlflow_tags_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    bluer_ai_log_error "@mlflow: tags: $task: command not found."
    return 1
}

bluer_ai_source_caller_suffix_path /tags
