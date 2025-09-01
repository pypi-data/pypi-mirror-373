#! /usr/bin/env bash

function bluer_ai_install_lepton() {
    sudo apt-get update --allow-releaseinfo-change

    cd ~
    sudo apt-get --yes --force-yes install bison flex aptitude qt4-qmake libqt4-dev
    sudo aptitude --yes --force-yes install libssl-dev

    # To clone linux for raspberry pi
    git clone --depth=1 https://github.com/raspberrypi/linux

    # To setup kernel
    cd ~/linux
    KERNEL=kernel7
    make bcm2709_defconfig
    sudo sed -i '$akernel=kernel7.img' /boot/config.txt

    # To build and install kernel modules
    make -j4 zImage modules dtbs
    sudo make modules_install
    sudo cp arch/arm/boot/dts/*.dtb /boot/
    sudo cp arch/arm/boot/dts/overlays/*.dtb* /boot/overlays/
    sudo cp arch/arm/boot/dts/overlays/README /boot/overlays/
    sudo cp arch/arm/boot/zImage /boot/$KERNEL.img

    sudo apt --yes --force-yes install python-opencv
    sudo pip install pylepton
}

if [ "$BLUER_SBC_SESSION_IMAGER" == "lepton" ]; then
    bluer_ai_install_module lepton 102
fi
