#! /usr/bin/env bash

function test_bluer_objects_help() {
    local options=$1

    # legacy, not tested:
    #  - @mysql

    local module
    for module in \
        "@cp" \
        \
        "@create_test_asset" \
        \
        "@objects" \
        \
        "@objects pypi" \
        "@objects pypi browse" \
        "@objects pypi build" \
        "@objects pypi install" \
        \
        "@objects pytest" \
        \
        "@objects test" \
        "@objects test list" \
        \
        "@cp" \
        \
        "@download" \
        \
        "@gif" \
        \
        "@ls" \
        \
        "@host" \
        "@host get" \
        "@host reboot" \
        "@host shutdown" \
        \
        "@lock" \
        "@lock lock" \
        "@lock unlock" \
        \
        "@metadata" \
        "@metadata get" \
        "@metadata post" \
        \
        "@mlflow" \
        "@mlflow browse" \
        "@mlflow cache" \
        "@mlflow deploy" \
        "@mlflow deploy set" \
        "@mlflow get_id" \
        "@mlflow get_run_id" \
        "@mlflow list_registered_models" \
        "@mlflow log_artifacts" \
        "@mlflow log_run" \
        "@mlflow rm" \
        "@mlflow run" \
        "@mlflow tags" \
        "@mlflow tags clone" \
        "@mlflow tags get" \
        "@mlflow tags search" \
        "@mlflow tags set" \
        "@mlflow test" \
        "@mlflow transition" \
        \
        "@select" \
        \
        "@storage" \
        "@storage clear" \
        "@storage download_file" \
        "@storage exists" \
        "@storage list" \
        "@storage rm" \
        "@storage status" \
        \
        "@upload" \
        \
        "@web" \
        "@web is_accessible" \
        "@web where_am_i" \
        \
        "@wait" \
        \
        "bluer_objects"; do
        bluer_ai_eval ,$options \
            bluer_ai_help $module
        [[ $? -ne 0 ]] && return 1

        bluer_ai_hr
    done

    return 0
}
