#! /usr/bin/env bash

function bluer_sbc_scroll_phat_hd() {
    local task=$1

    if [ "$task" == "validate" ]; then
        pushd $abcli_path_git/scroll-phat-hd/examples >/dev/null
        python3 plasma.py
        popd >/dev/null
        return
    fi

    bluer_ai_log_error "@sbc: scroll_phat_hd: $task: command not found."
}
