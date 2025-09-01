#! /usr/bin/env bash

function bluer_sbc_hat() {
    local task=$1

    if [[ "|input|validate|" == *"|$task|"* ]]; then
        python3 -m bluer_sbc.hardware.hat \
            $task \
            "${@:2}"
        return
    fi

    if [ "$task" == "output" ]; then
        python3 -m bluer_sbc.hardware.hat \
            output \
            --outputs "$2" \
            "${@:3}"
        return
    fi

    python3 -m bluer_sbc.hardware.hat "$@"
}
