#! /usr/bin/env bash

function bluer_ai_storage_exists() {
    python3 -m bluer_objects.storage \
        exists \
        --object_name "$1" \
        "${@:2}"
}
