#! /usr/bin/env bash

function bluer_ai_install_adafruit_rgb_matrix() {
    pushd $abcli_path_git >/dev/null
    git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
    cd Raspberry-Pi-Installer-Scripts
    sudo bash ./rgb-matrix.sh
    popd >/dev/null

    sudo setcap 'cap_sys_nice=eip' /usr/bin/python3.7
}

if [ "$BLUER_SBC_HARDWARE_KIND" == "adafruit_rgb_matrix" ]; then
    bluer_ai_install_module adafruit_rgb_matrix 106
fi
