#! /usr/bin/env bash

function test_bluer_objects_web_is_accessible() {
    local output=$(bluer_objects_web_is_accessible void)
    [[ "$output" -ne 0 ]] &&
        return 1

    local url="https://iribnews.ir"
    [[ "$abcli_is_github_workflow" == true ]] &&
        url="https://cnn.com"

    output=$(bluer_objects_web_is_accessible $url)
    [[ "$output" -ne 1 ]] &&
        return 1

    return 0
}
