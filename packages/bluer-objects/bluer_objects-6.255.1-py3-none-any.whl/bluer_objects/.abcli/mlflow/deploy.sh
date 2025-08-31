#! /usr/bin/env bash

function bluer_objects_mlflow_deploy() {
    local options=$1
    local do_set=$(bluer_ai_option_int "$options" set 0)

    if [[ "$do_set" == 1 ]]; then
        local url=$2
        if [[ -z "$url" ]]; then
            bluer_ai_log_error "url not found."
            return 1
        fi

        pushd $abcli_path_git/bluer-objects >/dev/null
        dotenv set \
            MLFLOW_DEPLOYMENT \
            $url
        popd >/dev/null

        bluer_objects init
        return
    fi

    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local port=$(bluer_ai_option "$options" port 5001)

    [[ "$MLFLOW_DEPLOYMENT" != "local" ]] &&
        bluer_ai_log_warning "MLFLOW_DEPLOYMENT is not local".

    bluer_ai_badge "🤖"

    bluer_ai_eval dryrun=$do_dryrun \
        mlflow ui \
        --backend-store-uri $MLFLOW_TRACKING_URI \
        --default-artifact-root file://$MLFLOW_TRACKING_URI \
        --host 0.0.0.0 \
        --port $port

    bluer_ai_badge "💻"
}
