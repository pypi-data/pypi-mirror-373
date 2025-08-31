#! /usr/bin/env bash

function bluer_objects_create_test_asset() {
    local object_name=$(bluer_ai_clarify_object $1 .)

    python3 -m bluer_objects.testing \
        create_test_asset \
        --object_name $object_name \
        "${@:2}"
}
