#! /usr/bin/env bash

function bluer_objects_clone() {
    local options=$1
    local do_relate=$(bluer_ai_option_int "$options" relate 1)
    local do_upload=$(bluer_ai_option_int "$options" upload 0)
    local clone_tags=$(bluer_ai_option_int "$options" tags 1)
    local copy_content=$(bluer_ai_option_int "$options" content 1)
    local do_download=$(bluer_ai_option_int "$options" download 1)
    local transfer_mechanism=$(bluer_ai_option_choice "$options" cp,mv mv)

    local object_1_name=$(bluer_ai_clarify_object $2 ..)
    local object_2_name=$(bluer_ai_clarify_object $3 .)

    bluer_ai_log "$object_1_name -clone:$transfer_mechanism-> $object_2_name"

    [[ "$do_download" == 1 ]] &&
        bluer_objects_download - $object_1_name

    local object_1_path=$ABCLI_OBJECT_ROOT/$object_1_name
    local object_2_path=$ABCLI_OBJECT_ROOT/$object_2_name

    if [[ "$copy_content" == 1 ]]; then
        bluer_ai_eval - \
            rsync \
            -avv \
            $object_1_path/ \
            $object_2_path
    else
        local extension
        for extension in qgz; do
            cp -v \
                $object_1_path/*.$extension \
                $object_2_path
        done
    fi

    [[ "$clone_tags" == 1 ]] &&
        bluer_objects_mlflow_tags clone \
            $object_1_name \
            $object_2_name

    [[ "$do_relate" == 1 ]] &&
        bluer_objects_mlflow_tags set \
            $object_2_name \
            cloned.$object_1_name

    pushd $object_2_path >/dev/null
    local filename
    for filename in $object_1_name.*; do
        $transfer_mechanism -v \
            $filename \
            $object_2_path/$object_2_name.${filename##*.}
    done
    popd >/dev/null

    [[ -f "$object_1_path/metadata.yaml" ]] &&
        cp -v \
            $object_1_path/metadata.yaml \
            $object_2_path/metadata-$object_1_name.yaml

    [[ "$do_upload" == 1 ]] &&
        bluer_objects_upload - $object_2_name

    return 0
}
