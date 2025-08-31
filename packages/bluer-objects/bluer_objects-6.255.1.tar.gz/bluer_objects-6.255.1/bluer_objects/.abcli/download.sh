#! /usr/bin/env bash

function bluer_objects_download() {
    local options=$1
    local filename=$(bluer_ai_option "$options" filename)
    local policy=$(bluer_ai_option "$options" policy none)

    local object_name=$(bluer_ai_clarify_object $2 .)

    python3 -m bluer_objects.storage \
        download \
        --object_name $object_name \
        --filename "$filename" \
        --policy $policy
    [[ $? -ne 0 ]] && return 1

    local open_options=$3
    local do_open=$(bluer_ai_option_int "$open_options" open 0)
    [[ "$do_open" == 0 ]] &&
        return 0

    bluer_ai_open filename=$filename,$open_options \
        $object_name
}
