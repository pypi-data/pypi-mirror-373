#! /usr/bin/env bash

function bluer_sbc_grove() {
    local task=$1

    if [ "$task" == "info" ]; then
        # https://learn.adafruit.com/scanning-i2c-addresses/raspberry-pi
        i2cdetect -y 1
        return
    fi

    if [ "$task" == "validate" ]; then
        local what=$(bluer_ai_clarify_input $2 button)

        local args=""
        local filepath="grove.py/grove"
        if [ "$what" == "adc" ]; then
            local filename="adc"
        elif [ "$what" == "button" ]; then
            filename="grove_button"
            args="24"
        elif [ "$what" == "oled_128x64" ]; then
            filepath="Seeed_Python_SSD1315/examples"
            filename="image"
        else
            bluer_ai_log_error "@sbc: grove: $task: $what: hardware not found."
            return
        fi

        filename=$(bluer_ai_clarify_input $3 $filename)

        local grove_path=$abcli_path_git/$filepath

        bluer_ai_log "validating grove $what: $grove_path/$filename.py $args"
        pushd $grove_path >/dev/null
        python3 $filename.py $args
        popd >/dev/null

        return
    fi

    bluer_ai_log_error "@sbc: grove: $task: command not found."
}
