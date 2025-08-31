#! /usr/bin/env bash

function bluer_ai_storage_clear() {
    local options=$1
    local do_cloud=$(bluer_ai_option_int "$options" cloud 0)
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 1)

    if [[ "$do_cloud" == 1 ]]; then
        python3 -m bluer_objects.storage \
            clear \
            --do_dryrun $do_dryrun \
            "${@:2}"
        return
    fi

    if [[ "$abcli_is_rpi" == true ]]; then
        bluer_ai_eval dryrun=$do_dryrun \
            rm -rfv $ABCLI_OBJECT_ROOT
        return
    fi

    local recent_filename=$ABCLI_OBJECT_ROOT/QGIS-recent.yaml
    if [[ ! -f "$recent_filename" ]]; then
        bluer_ai_log_warning "run \"QGIS.list_recent_projects\" first."
        return 1
    fi

    local recent_projects=$(python3 -c "from bluer_objects import file; print('+'.join(file.load_yaml('$recent_filename')[1]))")
    bluer_ai_log_list "$recent_projects" \
        --delim + \
        --after "object(s) to keep."

    pushd $ABCLI_OBJECT_ROOT >/dev/null
    local folder
    local object_name
    for folder in ./*; do
        object_name=$(basename "$folder")

        if [[ "+$recent_projects+" == *"+$object_name+"* ]]; then
            bluer_ai_log "will keep $object_name ..."
        else
            bluer_ai_log_warning "will delete $object_name ..."

            [[ "$do_dryrun" == 0 ]] &&
                rm -rfv $object_name
        fi
    done
    popd >/dev/null

    [[ "$do_dryrun" == 0 ]] &&
        rm -v $recent_filename

    return 0
}
