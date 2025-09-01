#! /usr/bin/env bash

function bluer_ai_install_grove() {
    pushd $abcli_path_git >/dev/null

    # https://wiki.seeedstudio.com/Grove_Base_Kit_for_Raspberry_Pi/
    curl -L https://github.com/Seeed-Studio/grove.py/raw/master/install.sh \
        --output grove_install.sh
    sudo bash ./grove_install.sh

    git clone https://github.com/kamangir/grove.py
    cd grove.py
    sudo pip3 install -e .

    # https://wiki.seeedstudio.com/Grove-OLED-Yellow%26Blue-Display-0.96-%28SSD1315%29_V1.0/
    sudo apt-get install -y python-smbus
    sudo apt-get install -y i2c-tools
    sudo pip3 install Adafruit-BBIO
    sudo pip3 install Adafruit-SSD1306

    cd ..
    git clone https://github.com/IcingTomato/Seeed_Python_SSD1315.git

    popd >/dev/null
}

if [ "$BLUER_SBC_HARDWARE_KIND" == "grove" ]; then
    bluer_ai_install_module grove 106
fi
