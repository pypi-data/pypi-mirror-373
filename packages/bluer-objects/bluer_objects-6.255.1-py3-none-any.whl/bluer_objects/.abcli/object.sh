#! /usr/bin/env bash

function bluer_ai_clarify_object() {
    local object_name=$1
    local default=${2:-$(bluer_ai_string_timestamp)}
    local type_name=${3:-object}

    local object_var=abcli_${type_name}_name
    local object_var_prev=abcli_${type_name}_name_prev
    local object_var_prev2=abcli_${type_name}_name_prev2

    [[ -z "$object_name" ]] || [[ "$object_name" == "-" ]] &&
        object_name=$default

    if [ "$object_name" == "." ]; then
        object_name=${!object_var}
    elif [ "$object_name" == ".." ]; then
        object_name=${!object_var_prev}
    elif [ "$object_name" == "..." ]; then
        object_name=${!object_var_prev2}
    fi

    mkdir -p $ABCLI_OBJECT_ROOT/$object_name

    echo $object_name
}
