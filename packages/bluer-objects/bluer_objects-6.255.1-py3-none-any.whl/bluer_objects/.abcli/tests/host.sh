#! /usr/bin/env bash

function test_bluer_objects_host() {
    bluer_ai_assert \
        $(bluer_objects_host get name) \
        - non-empty
}
