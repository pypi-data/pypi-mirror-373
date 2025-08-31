#! /usr/bin/env bash

bluer_ai_source_caller_suffix_path /tests

bluer_ai_env_dot_load \
    caller,plugin=bluer_objects,suffix=/../..

if [[ "$MLFLOW_DEPLOYMENT" == "local" ]]; then
    export MLFLOW_TRACKING_URI=$HOME/mlflow
else
    export MLFLOW_TRACKING_URI=$MLFLOW_DEPLOYMENT
fi

bluer_ai_env_dot_load \
    caller,filename=config.env,suffix=/..
