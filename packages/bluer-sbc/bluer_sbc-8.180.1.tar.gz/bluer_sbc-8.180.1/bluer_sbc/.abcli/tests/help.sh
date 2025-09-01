#! /usr/bin/env bash

function test_bluer_sbc_help() {
    local options=$1

    local module
    for module in \
        "@rpi" \
        "@rpi fake_display" \
        \
        "@sbc" \
        \
        "@sbc adafruit_rgb_matrix" \
        "@sbc adafruit_rgb_matrix validate" \
        \
        "@sbc camera" \
        "@sbc camera capture" \
        "@sbc camera capture image" \
        "@sbc camera capture video" \
        "@sbc camera preview" \
        \
        "@sbc hat" \
        "@sbc hat input" \
        "@sbc hat output" \
        "@sbc hat validate" \
        \
        "@sbc lepton" \
        "@sbc lepton capture" \
        "@sbc lepton preview" \
        \
        "@sbc pypi" \
        "@sbc pypi browse" \
        "@sbc pypi build" \
        "@sbc pypi install" \
        \
        "@sbc pytest" \
        \
        "@sbc scroll_phat_hd" \
        "@sbc scroll_phat_hd validate" \
        \
        "@sbc sparkfun_top_phat" \
        "@sbc sparkfun_top_phat validate" \
        \
        "@sbc test" \
        "@sbc test list" \
        \
        "@sbc unicorn_16x16" \
        "@sbc unicorn_16x16 validate" \
        \
        "grove info" \
        "grove validate" \
        "grove validate oled_128x64" \
        \
        "bluer_sbc"; do
        bluer_ai_eval ,$options \
            bluer_ai_help $module
        [[ $? -ne 0 ]] && return 1

        bluer_ai_hr
    done

    return 0
}
