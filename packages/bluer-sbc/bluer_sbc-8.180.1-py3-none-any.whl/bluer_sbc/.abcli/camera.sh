#! /usr/bin/env bash

function bluer_sbc_camera() {
    local task=$1

    if [[ "|capture|preview|" == *"|$task|"* ]]; then
        local options=$2
        local capture_video=$(bluer_ai_option_int "$options" video 0)
        [[ "$capture_video" == 1 ]] &&
            task=capture_video

        python3 -m bluer_sbc.imager.camera \
            $task \
            "${@:3}"

        return
    fi

    python3 -m bluer_sbc.imager.camera "$@"
}
