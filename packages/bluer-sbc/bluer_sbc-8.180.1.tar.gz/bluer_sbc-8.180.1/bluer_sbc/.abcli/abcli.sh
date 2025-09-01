#! /usr/bin/env bash

bluer_ai_source_caller_suffix_path /tests

bluer_ai_env_dot_load \
    caller,filename=config.env,suffix=/..

bluer_ai_env_dot_load \
    caller,plugin=bluer_sbc,suffix=/../..

[[ "$abcli_is_github_workflow" == true ]] &&
    export BLUER_SBC_SESSION_IMAGER_ENABLED=0
