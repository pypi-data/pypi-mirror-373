#! /usr/bin/env bash

function bluer_ai_storage_list() {
    python3 -m bluer_objects.storage \
        list_of_objects \
        --prefix "$1" \
        "${@:2}"
}
