#!/bin/sh
# Get SMI Number
clear
shouldloop=true;
while $shouldloop; do
    echo -n "Please enter the SMI Number: "
    read SMINumber
    clear
    echo -n "Is $SMINumber the correct SMI Number (y/n)?: "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        shouldloop=false;
    fi
done

# Get PLC IP Address
clear
shouldloop=true;
while $shouldloop; do
    echo -n "Please enter the PLC IP Address: "
    read PLCIP
    clear
    echo -n "Is $PLCIP the correct IP Address (y/n)?: "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        shouldloop=false;
    fi
done

# Get Application Key
clear
shouldloop=true;
while $shouldloop; do
    echo -n "Please enter application key: "
    read applicationKey
    clear
    echo -n "Is $applicationKey the correct application key (y/n)?: "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        shouldloop=false;
    fi
done

# Select Production or Development Server
clear
shouldloop=true;
serverDownload="https://sanimatic-dev.cloud.thingworx.com/Thingworx/FileRepositories/Downloads/linuxmicroserver.zip?appKey=9f09c4f6-14f6-44b7-b90d-73a7e2f0e6ef"
server="sanimatic-dev.cloud.thingworx.com"
while $shouldloop; do
    echo -n "Is this for the production server (y/n)?: "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        server="sanimatic-prod1.cloud.thingworx.com"
        serverDownload="https://sanimatic-dev.cloud.thingworx.com/Thingworx/FileRepositories/Downloads/linuxmicroserver.zip?appKey=9f09c4f6-14f6-44b7-b90d-73a7e2f0e6ef"
        shouldloop=false;
    else
        shouldloop=false;
    fi
done


# Change SSH settings
clear
echo "Modifying SSH settings..."
sudo echo "TCPKeepAlive no" >> /etc/ssh/sshd_config
sudo echo "ClientAliveInterval 30" >> /etc/ssh/sshd_config
sudo echo "ClientAliveCountMax 60" >> /etc/ssh/sshd_config
echo "Restarting ssh daemon..."
sudo systemctl restart ssh

# Update the system
clear
echo "Updating the system..."
sudo apt update && sudo apt upgrade -y

# Install Prerequisite Programs
clear
echo "Installing Prerequisite programs..."
sudo apt install -y git curl wget zip unzip python3 python3-pip

# Clone SaniTrend Cloud github repository
clear
echo "Downloading SaniTrend Cloud Repository..."
git clone https://github.com/msienkow/SaniTrendCloud_Lite.git
cd SaniTrendCloud_Lite

# Install python 3 requirements
clear
echo "Installing python3 required libraries..."
sudo pip3 install -r requirements.txt

# SaniTrend Config File
echo "Creating SaniTrend Cloud configuration file..."
echo "{" >> SaniTrendConfig.json
echo "    \"Config\": {" >> SaniTrendConfig.json
echo "        \"PLCIPAddress\": \"$PLCIP\"," >> SaniTrendConfig.json
echo "        \"PLCScanRate\": \"1000\"," >> SaniTrendConfig.json
echo "        \"SMINumber\": \"$SMINumber\"" >> SaniTrendConfig.json
echo "    }," >> SaniTrendConfig.json
echo "    \"Tags\": [" >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Analog_In_1\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"NUMBER\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Analog_In_2\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"NUMBER\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Analog_In_3\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"NUMBER\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Analog_In_4\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"NUMBER\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Analog_In_5\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"NUMBER\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Analog_In_6\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"NUMBER\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Analog_In_7\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"NUMBER\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Analog_In_8\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"NUMBER\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_1\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_2\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_3\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_4\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_5\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_6\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_7\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_8\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_9\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_10\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_11\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Digital_In_12\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"SaniTrend_Watchdog\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"PLC_Watchdog\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Reboot\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"BOOLEAN\"" >> SaniTrendConfig.json
echo "        }," >> SaniTrendConfig.json
echo "        {" >> SaniTrendConfig.json
echo "            \"tag\": \"Recipe\"," >> SaniTrendConfig.json
echo "            \"twxtype\": \"STRING\"" >> SaniTrendConfig.json
echo "        }" >> SaniTrendConfig.json
echo "    ]" >> SaniTrendConfig.json
echo "}" >> SaniTrendConfig.json

# Enable any user to reboot computer
echo "Applying settings to allow any user to reboot the system..."
chmod +x sudoers.sh
sudo ./sudoers.sh

# Dowload/Configure Thingworx Edge Microserver
echo "Downloading Thingworx Edge Microserver..."
wget -O microserver.zip $serverDownload
unzip microserver.zip
rm microserver.zip

# Install Thingworx Edge Microserver
echo "Installing Thingworx Edge Microserver..."
cd microserver
chmod +x wsems
echo "Encrypting Application Key..."
key=`./wsems -encrypt $applicationKey | sed -n '3{p;q}'`
sed -i s"|ServerURL|$server|g" etc/config.json
sed -i s"|ApplicationKey|$key|g" etc/config.json
sed -i s"|ThingName|$SMINumber|g" etc/config.json
chmod +x install_services/install
./install_services/install

# Setup Thinworx Edge Microserver for automatic Systemd Service
echo "Installing SaniTrend Cloud Systemd service..."
sudo cp sanitrend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sanitrend.service
sudo systemctl start sanitrend.service

# End of Script
