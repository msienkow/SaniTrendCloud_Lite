#!/bin/sh
# Get SMI Number
shouldloop=true;
while $shouldloop; do
    echo -n "Please enter the SMI Number: "
    read SMINumber
    echo -n "is $SMINumber the correct SMI Number (y/n)?: "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        shouldloop=false;
    fi
done

# Get PLC IP Address
shouldloop=true;
while $shouldloop; do
    echo -n "Please enter the PLC IP Address: "
    read PLCIP
    echo -n "is $PLCIP the correct IP Address (y/n)?: "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        shouldloop=false;
    fi
done

# Get Application Key
shouldloop=true;
while $shouldloop; do
    echo -n "Please enter application key: "
    read applicationKey
    echo -n "is $applicationKey the correct IP Address (y/n)?: "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        shouldloop=false;
    fi
done

# Select Production or Development Server
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
echo "Modifying SSH settings..."
sudo echo "TCPKeepAlive no" >> /etc/ssh/sshd_config
sudo echo "ClientAliveInterval 30" >> /etc/ssh/sshd_config
sudo echo "ClientAliveCountMax 60" >> /etc/ssh/sshd_config
sudo systemctl restart ssh

# Update the system
echo "Updating the system..."
sudo apt get update && sudo apt upgrade -y

# Install Prerequisite Programs
echo "Installing Prerequisite programs..."
sudo apt install -y git curl wget

# Install python 3 requirements
sudo pip3 install -r requirements.txt

# Clone SaniTrend Cloud github repository
echo "Downloading SaniTrend Cloud Repository..."
git clone https://github.com/msienkow/SaniTrendCloud_Lite.git
cd SaniTrendCloud_Lite
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
echo "Applying settings to allow any user to reboot the system"
chmod +x sudoers.sh
sudo ./sudoers.sh

# Dowload/Configure Thingworx Edge Microserver
wget -O microserver.zip $serverDownload
unzip microserver.zip
rm microserver.zip
chmod +x microserver/wsems
cd microserver
echo "Encrypting Application Key..."
key=`./wsems -encrypt $applicationKey | sed -n '3{p;q}'`

# Setup Thinworx Edge Microserver for automatic Systemd Service
sudo cp sanitrend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sanitrend.service
sudo systemctl start sanitrend.service