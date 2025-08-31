#! /usr/bin/env bash

export ABCLI_MLFLOW_STAGES="Staging|Production|Archived"

function bluer_objects_mlflow_transition() {
    local options=$1
    local model_name=$(bluer_ai_option "$options" model)
    local stage_name=$(bluer_ai_option_choice "$options" $(echo $ABCLI_MLFLOW_STAGES | tr \| ,) Staging)
    local version=$(bluer_ai_option "$options" version)

    local description="$2"

    python3 -m bluer_objects.mlflow \
        transition \
        --model_name "$model_name" \
        --version "$version" \
        --stage_name "$stage_name" \
        --description "$description" \
        "${@:3}"
}
