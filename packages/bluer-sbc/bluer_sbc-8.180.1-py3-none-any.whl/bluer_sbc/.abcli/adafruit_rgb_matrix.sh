#! /usr/bin/env bash

function bluer_sbc_adafruit_rgb_matrix() {
    local task=$1

    if [ "$task" == "validate" ]; then
        pushd $abcli_path_git/Raspberry-Pi-Installer-Scripts/rpi-rgb-led-matrix/examples-api-use >/dev/null
        sudo ./demo -D0
        popd >/dev/null
        return
    fi

    bluer_ai_log_error "@sbc: adafruit_rgb_matrix: $task: command not found."
}
