#! /usr/bin/env bash

function test_bluer_objects_mlflow_logging() {
    local object_name="test-object-$(bluer_ai_string_timestamp_short)"

    bluer_objects_clone \
        upload \
        vanwatch-mlflow-validation-2024-09-23-10673 \
        "$object_name"

    bluer_objects_mlflow rm $object_name
}
