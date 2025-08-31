#! /usr/bin/env bash

function test_bluer_objects_gif() {
    local options=$1

    local source_object_name=test_bluer_objects_clone-$(bluer_ai_string_timestamp_short)

    bluer_objects_create_test_asset \
        $source_object_name
    [[ $? -ne 0 ]] && return 1

    bluer_objects_gif \
        ~upload,$options \
        $source_object_name \
        --frame_duration 200 \
        --output_filename test.gif \
        --scale 2 \
        --suffix .png
}
