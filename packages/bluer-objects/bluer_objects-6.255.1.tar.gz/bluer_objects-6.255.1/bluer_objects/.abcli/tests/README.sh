#! /usr/bin/env bash

function test_bluer_objects_README() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_objects build_README
}
