#! /usr/bin/env bash

function bluer_sbc_unicorn_16x16() {
    local task=$1

    if [ "$task" == "validate" ]; then
        pushd $abcli_path_git/unicorn-hat-hd/examples >/dev/null
        python3 rainbow.py
        popd >/dev/null
        return
    fi

    bluer_ai_log_error "@sbc: unicorn_16x16: $task: command not found."
}
