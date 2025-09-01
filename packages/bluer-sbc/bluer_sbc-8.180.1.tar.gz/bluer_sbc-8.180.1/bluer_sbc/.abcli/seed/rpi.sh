#! /usr/bin/env bash

# internal function to bluer_ai_seed.
# seed is NOT local
function bluer_ai_seed_rpi() {
    bluer_ai_seed add_kaggle

    bluer_ai_seed add_ssh_key sudo

    seed="${seed}sudo apt-get --yes --force-yes install git$delim_section"

    bluer_ai_seed add_repo

    bluer_ai_seed add_bluer_ai_env

    seed="${seed}sudo apt install -y python3-pip$delim"
    seed="${seed}pip3 install --upgrade pip --no-input$delim"
    seed="${seed}pip3 install -e .$delim_section"

    bluer_ai_seed add_repo repo=bluer-objects
    seed="${seed}pip3 install -e .$delim_section"
    seed="${seed}$(bluer_ai_seed add_file $abcli_path_git/bluer-objects/.env \$HOME/git/bluer-objects/.env)$delim_section"

    bluer_ai_seed add_repo repo=bluer-sbc
    seed="${seed}pip3 install -e .$delim_section"

    seed="${seed}cd; cd git; cd bluer-ai$delim"
    seed="${seed}source ./bluer_ai/.abcli/bluer_ai.sh$delim_section"

    seed="${seed}source ~/.bashrc$delim_section"
}
