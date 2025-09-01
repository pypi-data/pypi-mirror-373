#! /usr/bin/env bash

function test_bluer_sbc_version() {
    local options=$1

    bluer_ai_eval ,$options \
        "bluer_sbc version ${@:2}"
}
