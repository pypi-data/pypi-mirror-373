#! /usr/bin/env bash

function bluer_objects_ls() {
    local options=$1
    local where=$(bluer_ai_option_choice "$options" cloud,local)

    if [[ -z "$where" ]]; then
        ls -1 "$@"
    else
        local object_name=$(bluer_ai_clarify_object $2 .)

        python3 -m bluer_objects.storage \
            ls \
            --object_name $object_name \
            --where $where \
            "${@:3}"
    fi
}
