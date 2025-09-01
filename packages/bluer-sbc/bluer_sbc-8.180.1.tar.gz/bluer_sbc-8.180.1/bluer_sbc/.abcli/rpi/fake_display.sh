#! /usr/bin/env bash

function bluer_sbc_rpi_fake_display() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)

    if [[ "$abcli_is_rpi" == false ]]; then
        bluer_ai_log_warning "rpi not found."
        return 0
    fi

    sudo apt-get install -y xvfb
    [[ $? -ne 0 ]] && return 1

    Xvfb :99 -screen 0 640x480x24 &
    [[ $? -ne 0 ]] && return 1

    export DISPLAY=:99
}
