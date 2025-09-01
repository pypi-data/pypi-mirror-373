#! /usr/bin/env bash

function bluer_ai_install_scroll_phat_hd() {
    pushd $abcli_path_home/git >/dev/null
    git clone https://github.com/pimoroni/scroll-phat-hd
    popd >/dev/null

    # https://github.com/pimoroni/scroll-phat-hd
    sudo apt-get install python3-scrollphathd
}

if [ "$BLUER_SBC_HARDWARE_KIND" == "scroll_phat_hd" ]; then
    bluer_ai_install_module scroll_phat_hd 102
fi
