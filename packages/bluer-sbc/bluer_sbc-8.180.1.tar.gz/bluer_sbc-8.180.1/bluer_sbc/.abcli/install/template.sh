#! /usr/bin/env bash

function bluer_ai_install_bluer_sbc_template() {
    bluer_ai_log "wip"
}

if [ "$BLUER_SBC_HARDWARE_KIND" == "bluer_sbc_template" ]; then
    bluer_ai_install_module bluer_sbc_template 101
fi
