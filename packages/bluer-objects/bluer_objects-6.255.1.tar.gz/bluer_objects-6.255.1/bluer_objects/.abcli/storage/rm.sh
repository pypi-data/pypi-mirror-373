#! /usr/bin/env bash

function bluer_ai_storage_rm() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 1)

    local object_name=$(bluer_ai_clarify_object $2 void)

    bluer_ai_eval dryrun=$do_dryrun \
        rm -rfv $ABCLI_OBJECT_ROOT/$object_name
}
