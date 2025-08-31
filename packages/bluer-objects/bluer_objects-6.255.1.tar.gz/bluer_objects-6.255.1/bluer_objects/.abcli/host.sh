#! /usr/bin/env bash

function bluer_objects_host() {
    local task=$1
    local options=$2

    if [ $task == "get" ]; then
        python3 -m bluer_options.host \
            get \
            --keyword "$2" \
            "${@:3}"
        return
    fi

    if [ $task == "reboot" ]; then
        bluer_ai_eval ,$options \
            sudo reboot
        return
    fi

    if [ $task == "shutdown" ]; then
        bluer_ai_eval ,$options \
            sudo shutdown -h now
        return
    fi

    bluer_ai_log_error "@host: $task: command not found."
    return 1
}
