#! /usr/bin/env bash

function test_bluer_objects_storage_public_upload() {
    local options=$1

    local object_name=test_bluer_objects_storage_public_upload-$(bluer_ai_string_timestamp_short)
    local object_path=$ABCLI_OBJECT_ROOT/$object_name
    mkdir -pv $object_path

    bluer_objects_create_test_asset \
        $object_name \
        --depth 1
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_objects_upload \
        public \
        $object_name
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_objects_upload \
        public,zip \
        $object_name
}
