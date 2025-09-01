#! /usr/bin/env bash

# internal function to bluer_ai_seed.
# seed is NOT local
function bluer_ai_seed_swallow_raspbian() {
    local ssp="--break-system-packages"

    bluer_ai_seed add_repo repo=bluer-ugv
    seed="${seed}pip3 install $ssp -e .$delim_section"

    bluer_ai_seed add_repo repo=bluer-algo
    seed="${seed}pip3 install $ssp -e .$delim_section"
}
