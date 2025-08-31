#! /usr/bin/env bash

function bluer_objects_file() {
    python3 -m bluer_objects.file \
        "$1" \
        --filename "$2" \
        "${@:3}"
}
