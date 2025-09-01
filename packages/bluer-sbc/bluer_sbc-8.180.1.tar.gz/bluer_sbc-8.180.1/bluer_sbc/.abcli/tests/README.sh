#! /usr/bin/env bash

function test_bluer_sbc_README() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_sbc build_README
}
