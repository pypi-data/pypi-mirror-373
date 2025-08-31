#! /usr/bin/env bash

function test_bluer_objects_clone() {
    local options=$1

    local source_object_name=test_bluer_objects_clone-$(bluer_ai_string_timestamp_short)

    bluer_objects_create_test_asset \
        $source_object_name
    [[ $? -ne 0 ]] && return 1

    local object_name=test_bluer_objects_clone-$(bluer_ai_string_timestamp_short)

    bluer_objects_clone \
        ~relate,~tags,~upload,$options \
        $source_object_name \
        $object_name
}
