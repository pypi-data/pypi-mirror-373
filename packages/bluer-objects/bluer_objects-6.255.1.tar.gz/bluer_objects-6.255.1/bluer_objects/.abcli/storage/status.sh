#! /usr/bin/env bash

function bluer_ai_storage_status() {
    local options=$1
    local count=$(bluer_ai_option_int "$options" count 10)
    local depth=$(bluer_ai_option_int "$options" depth 2)
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)

    bluer_ai_eval dryrun=$do_dryrun,path=$ABCLI_PATH_STORAGE \
        "du -hc -d $depth | sort -h -r | head -n $count"
}
