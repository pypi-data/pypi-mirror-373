#! /usr/bin/env bash

function bluer_objects_web_is_accessible() {
    local url=$1
    if [[ -z "$url" ]]; then
        bluer_ai_log_error "url not found."
        return 1
    fi

    python3 -m bluer_objects.web \
        is_accessible \
        --url $url
}
