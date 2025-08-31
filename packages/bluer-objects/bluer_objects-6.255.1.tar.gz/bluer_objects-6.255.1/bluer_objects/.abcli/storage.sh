#! /usr/bin/env bash

function bluer_ai_storage() {
    local task=$1

    local function_name=bluer_ai_storage_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 -m bluer_objects.storage "$@"
}

bluer_ai_source_caller_suffix_path /storage
