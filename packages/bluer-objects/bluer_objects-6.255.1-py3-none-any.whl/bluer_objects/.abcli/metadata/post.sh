#! /usr/bin/env bash

function bluer_objects_metadata_post() {
    local key=$1

    local value=$2

    local options=$3
    local source_type=$(bluer_ai_option_choice "$options" object,path,filename object)

    local source=$4
    [[ "$source_type" == object ]] &&
        source=$(bluer_ai_clarify_object $4 .)

    python3 -m bluer_objects.metadata post \
        --filename $(bluer_ai_option "$options" filename metadata.yaml) \
        --key "$key" \
        --value "$value" \
        --source "$source" \
        --source_type $source_type \
        "${@:5}"
}
