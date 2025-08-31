#! /usr/bin/env bash

function bluer_objects() {
    local task=$1

    bluer_ai_generic_task \
        plugin=bluer_objects,task=$task \
        "${@:2}"
}

bluer_ai_log $(bluer_objects version --show_icon 1)
