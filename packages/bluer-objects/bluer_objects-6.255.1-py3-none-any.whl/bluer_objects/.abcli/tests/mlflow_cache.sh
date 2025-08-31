#! /usr/bin/env bash

function test_bluer_objects_mlflow_cache() {
    local keyword="test-keyword-$(bluer_ai_string_timestamp_short)"
    local value="test-value-$(bluer_ai_string_timestamp_short)"

    bluer_objects_mlflow cache write \
        $keyword $value
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        $(bluer_objects_mlflow cache read $keyword) \
        $value
}
