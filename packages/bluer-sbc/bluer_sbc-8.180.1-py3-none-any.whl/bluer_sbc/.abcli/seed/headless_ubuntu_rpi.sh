#! /usr/bin/env bash

# internal function to bluer_ai_seed.
# seed is NOT local
function bluer_ai_seed_headless_ubuntu_rpi() {
    local target=$1

    seed="$seed$(bluer_ai_seed add_file $abcli_path_git/bluer-sbc/bluer_sbc/ROS/sudoers.d /etc/sudoers.d/ROS)$delim"
    seed="${seed}sudo chown root:root /etc/sudoers.d/ROS$delim"
    seed="${seed}sudo chmod 440 /etc/sudoers.d/ROS$delim_section"

    seed="${seed}sudo systemctl disable unattended-upgrades$delim"
    seed="${seed}sudo apt remove unattended-upgrades$delim"
    seed="${seed}sudo apt update$delim"
    seed="${seed}sudo apt upgrade$delim"
    seed="${seed}sudo apt install -y wireless-tools$delim"
    seed="${seed}sudo apt install -y gcc python3-dev$delim"
    seed="${seed}sudo apt install -y gcc-aarch64-linux-gnu$delim"
    seed="${seed}sudo apt install -y v4l-utils$delim"
    seed="${seed}sudo apt install -y ffmpeg$delim"
    seed="${seed}sudo apt install -y python3-venv$delim_section"

    seed="${seed}sudo mkdir -p /etc/systemd/system/getty@tty1.service.d$delim"
    seed="$seed$(bluer_ai_seed add_file $abcli_path_git/bluer-sbc/bluer_sbc/ROS/override.conf /etc/systemd/system/getty@tty1.service.d/override.conf)$delim"
    seed="${seed}sudo systemctl daemon-reexec$delim"
    seed="${seed}sudo systemctl restart getty@tty1$delim_section"

    bluer_ai_seed add_ssh_key

    bluer_ai_seed add_repo

    seed="${seed}mkdir -pv ~/storage/temp/ignore/$delim"
    seed="${seed}touch ~/storage/temp/ignore/headless$delim_section"

    bluer_ai_seed add_bluer_ai_env

    seed="${seed}pip install --upgrade pip --no-input$delim"
    seed="${seed}pip3 install -e .$delim"
    seed="${seed}pip3 install evdev$delim"
    seed="${seed}pip3 install opencv-python-headless$delim_section"

    bluer_ai_seed add_repo repo=bluer-objects
    seed="${seed}pip3 install -e .$delim_section"
    seed="${seed}$(bluer_ai_seed add_file $abcli_path_git/bluer-objects/.env \$HOME/git/bluer-objects/.env)$delim_section"

    bluer_ai_seed add_repo repo=bluer-sbc
    seed="${seed}pip3 install -e .$delim_section"
    seed="${seed}$(bluer_ai_seed add_file $abcli_path_git/bluer-sbc/.env \$HOME/git/bluer-sbc/.env)$delim_section"

    bluer_ai_seed add_repo repo=bluer-ugv
    seed="${seed}pip3 install -e .$delim_section"

    bluer_ai_seed add_repo repo=bluer-algo
    seed="${seed}pip3 install -e .$delim_section"

    seed="${seed}pip3 install RPi.GPIO$delim_section"

    seed="${seed}source \$HOME/git/bluer-ai/bluer_ai/.abcli/bluer_ai.sh$delim_section"
}
