#! /usr/bin/env bash

function bluer_sbc() {
    local task=$1

    bluer_ai_generic_task \
        plugin=bluer_sbc,task=$task \
        "${@:2}"
}

bluer_ai_log $(bluer_sbc version --show_icon 1)
