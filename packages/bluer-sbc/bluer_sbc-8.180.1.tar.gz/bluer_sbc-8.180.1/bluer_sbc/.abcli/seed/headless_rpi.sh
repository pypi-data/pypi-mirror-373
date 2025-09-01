#! /usr/bin/env bash

# internal function to bluer_ai_seed.
# seed is NOT local
function bluer_ai_seed_headless_rpi() {
    bluer_ai_seed add_kaggle

    bluer_ai_seed add_ssh_key sudo

    # https://serverfault.com/a/1093530
    # https://packages.ubuntu.com/bionic/all/ca-certificates/download
    local certificate_name="ca-certificates_20230311ubuntu0.18.04.1_all"
    seed="${seed}wget --no-check-certificate http://security.ubuntu.com/ubuntu/pool/main/c/ca-certificates/$certificate_name.deb$delim"
    seed="${seed}sudo dpkg -i $certificate_name.deb$delim_section"
    seed="${seed}sudo apt-get update --allow-releaseinfo-change$delim"
    seed="${seed}sudo apt-get install -y ca-certificates libgnutls30$delim"
    seed="${seed}sudo apt install -y python3-venv$delim"
    seed="${seed}sudo apt install -y cmake build-essential$delim"
    seed="${seed}sudo apt install -y libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjpeg-dev libtiff-dev libwebp-dev$delim"
    seed="${seed}sudo apt-get install libopenblas-base$delim"

    seed="${seed}sudo apt-get --yes --force-yes install git$delim_section"

    bluer_ai_seed add_repo

    seed="${seed}mkdir -pv ~/storage/temp/ignore$delim"
    seed="${seed}touch ~/storage/temp/ignore/headless$delim_section"

    bluer_ai_seed add_bluer_ai_env

    seed="${seed}sudo apt install -y python3-pip$delim"
    seed="${seed}pip3 install --upgrade pip --no-input$delim"
    seed="${seed}pip3 install \"pandas<2.1\"$delim"
    seed="${seed}pip3 install pillow$delim"
    seed="${seed}pip3 install -e . --constraint ./bluer_ai/assets/no-pyarrow.txt$delim_section"

    bluer_ai_seed add_repo repo=bluer-objects
    seed="${seed}pip3 install -e .$delim_section"
    seed="${seed}$(bluer_ai_seed add_file $abcli_path_git/bluer-objects/.env \$HOME/git/bluer-objects/.env)$delim_section"

    bluer_ai_seed add_repo repo=bluer-sbc
    seed="${seed}pip3 install -e .$delim_section"

    seed="${seed}pip3 install opencv-python-headless$delim_section"
    seed="${seed}sudo apt install -y libopenjp2-7 libavcodec58 libavformat58 libswscale5 libblas3 libatlas3-base$delim_section"

    seed="${seed}cd; cd git; cd bluer-ai$delim"
    seed="${seed}source ./bluer_ai/.abcli/bluer_ai.sh$delim_section"

    seed="${seed}source ~/.bashrc$delim_section"
}
