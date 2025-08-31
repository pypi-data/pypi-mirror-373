#! /usr/bin/env bash

function test_bluer_objects_metadata() {
    local returned_value
    for post_func in {1..3}; do
        local object_name=$(bluer_ai_string_timestamp)
        local object_path=$ABCLI_OBJECT_ROOT/$object_name
        local filename=$object_path/metadata.yaml

        local key=$(bluer_ai_string_random)
        local value=$(bluer_ai_string_random)

        [[ "$post_func" == 1 ]] &&
            bluer_objects_metadata post \
                $key $value \
                filename \
                $filename \
                --verbose 1

        [[ "$post_func" == 2 ]] &&
            bluer_objects_metadata post \
                $key $value \
                object,filename=metadata.yaml \
                $object_name \
                --verbose 1

        [[ "$post_func" == 3 ]] &&
            bluer_objects_metadata post \
                $key $value \
                path,filename=metadata.yaml \
                $object_path \
                --verbose 1

        for get_func in {1..3}; do
            [[ "$get_func" == 1 ]] &&
                returned_value=$(bluer_objects_metadata get \
                    key=$key,filename \
                    $filename)

            [[ "$get_func" == 2 ]] &&
                returned_value=$(bluer_objects_metadata get \
                    key=$key,filename=metadata.yaml,object \
                    $object_name)

            [[ "$get_func" == 3 ]] &&
                returned_value=$(bluer_objects_metadata get \
                    key=$key,filename=metadata.yaml,path \
                    $object_path)

            bluer_ai_assert "$value" "$returned_value"
            [[ $? -ne 0 ]] && return 1
        done
    done

    return 0
}
