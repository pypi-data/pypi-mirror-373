#! /usr/bin/env bash

function bluer_objects_metadata() {
    local task=${1:-help}

    local function_name="bluer_objects_metadata_$task"
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    bluer_ai_log_error "@metadata: $task: command not found."
    return 1
}

bluer_ai_source_caller_suffix_path /metadata
