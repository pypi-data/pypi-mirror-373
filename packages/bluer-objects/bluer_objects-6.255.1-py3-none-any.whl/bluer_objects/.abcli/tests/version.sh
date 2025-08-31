#! /usr/bin/env bash

function test_bluer_objects_version() {
    local options=$1

    bluer_ai_eval ,$options \
        "bluer_objects version ${@:2}"

    return 0
}
