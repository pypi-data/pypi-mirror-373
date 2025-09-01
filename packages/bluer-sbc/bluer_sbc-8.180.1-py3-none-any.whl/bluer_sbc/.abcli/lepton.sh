#! /usr/bin/env bash

function bluer_sbc_lepton() {
    local task=$1

    if [[ "|capture|preview|" == *"|$task|"* ]]; then
        python3 -m bluer_sbc.imager.lepton \
            $task \
            --output_path $abcli_object_path \
            "${@:2}"
        return
    fi

    python3 -m bluer_sbc.imager.lepton "$@"
}
