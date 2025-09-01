#! /usr/bin/env bash

function bluer_ai_install_sparkfun_top_phat() {
    # https://learn.sparkfun.com/tutorials/sparkfun-top-phat-hookup-guide/button-controller
    sudo pip3 install sparkfun-qwiic

    # https://learn.sparkfun.com/tutorials/sparkfun-top-phat-hookup-guide/ws2812b-leds
    sudo pip3 install adafruit-circuitpython-neopixel

    # https://github.com/rpi-ws281x/rpi-ws281x-python
    # https://github.com/jgarff/rpi_ws281x
    # https://stackoverflow.com/a/53045690/17619982
    sudo pip3 install rpi_ws281x

    pushd $abcli_path_home/git >/dev/null
    git clone https://github.com/sparkfun/Top_pHAT_Button_Py
    popd >/dev/null

    # https://learn.sparkfun.com/tutorials/sparkfun-top-phat-hookup-guide/24-tft-display-linux-54-update
    pushd $abcli_path_home >/dev/null
    curl -L https://cdn.sparkfun.com/assets/learn_tutorials/1/1/7/0/sfe-topphat-overlay.dts \
        --output ./sfe-topphat-overlay.dts
    dtc -@ -I dts -O dtb -o rpi-display.dtbo sfe-topphat-overlay.dts
    sudo cp rpi-display.dtbo /boot/overlays
    popd >/dev/null
}

if [ "$BLUER_SBC_HARDWARE_KIND" == "sparkfun-top-phat" ]; then
    bluer_ai_install_module sparkfun_top_phat 104

    # https://learn.sparkfun.com/tutorials/sparkfun-top-phat-hookup-guide/24-tft-display-archived
    con2fbmap 1 1
fi
