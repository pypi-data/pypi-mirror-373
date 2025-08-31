#! /usr/bin/env bash

function bluer_objects_metadata_get() {
    local options=$1
    local source_type=$(bluer_ai_option_choice "$options" object,path,filename object)

    local source=$2
    [[ "$source_type" == object ]] &&
        source=$(bluer_ai_clarify_object $2 .)

    local key=$(bluer_ai_option "$options" key)
    local default=$(bluer_ai_option "$options" default)

    python3 -m bluer_objects.metadata get \
        --default "$default" \
        --delim $(bluer_ai_option "$options" delim ,) \
        --dict_keys $(bluer_ai_option_int "$options" dict.keys 0) \
        --dict_values $(bluer_ai_option_int "$options" dict.values 0) \
        --filename $(bluer_ai_option "$options" filename metadata.yaml) \
        --key "$key" \
        --source "$source" \
        --source_type $source_type \
        "${@:3}"
}
