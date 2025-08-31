#! /usr/bin/env bash

function test_bluer_objects_storage_upload_download() {
    local options=$1

    local object_name=test_bluer_objects_storage_upload_download-$(bluer_ai_string_timestamp_short)
    local object_path=$ABCLI_OBJECT_ROOT/$object_name
    mkdir -pv $object_path

    bluer_objects_create_test_asset \
        $object_name \
        --depth 1
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_objects_ls local $object_name
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    # upload
    bluer_objects_upload \
        filename=this.yaml \
        $object_name
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_objects_upload \
        filename=subfolder/this.yaml \
        $object_name
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_objects_upload \
        - \
        $object_name
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_objects_ls cloud $object_name
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    # clean-up
    rm -rfv $object_path
    bluer_ai_hr

    # download
    bluer_objects_download \
        filename=this.yaml \
        $object_name
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_objects_download \
        filename=subfolder/this.yaml \
        $object_name
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_objects_download \
        - \
        $object_name
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_objects_download \
        policy=doesnt_exist \
        $object_name
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    bluer_objects_upload \
        zip \
        $object_name
}
