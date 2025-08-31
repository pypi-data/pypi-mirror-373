#! /usr/bin/env bash

function test_bluer_objects_mlflow_lock() {
    local options=$1

    local object_name="test-object-$(bluer_ai_string_timestamp_short)"
    local lock_name="lock-$(bluer_ai_string_random)"

    bluer_ai_eval ,$options \
        bluer_objects_mlflow_lock \
        lock \
        $object_name \
        --lock $lock_name \
        --timeout 10
    [[ $? -ne 0 ]] && return 1

    bluer_ai_eval ,$options \
        bluer_objects_mlflow_lock \
        lock \
        $object_name \
        --lock $lock_name \
        --timeout 10
    [[ $? -eq 0 ]] && return 1

    bluer_ai_eval ,$options \
        bluer_objects_mlflow_lock \
        unlock \
        $object_name \
        --lock $lock_name
}
