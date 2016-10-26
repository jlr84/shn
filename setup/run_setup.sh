#!/bin/bash

# Update packages
sudo apt-get update

# Install pip | debconf
sudo apt-get -y install python-pip debconf-utils

# Install project requirements using pip (based on 'requirements.txt')
# Note: Assumption that 'requipments.txt' is in parent directory
sudo pip install -r ../requirements.txt

# Install Mariadb (replacement for mysql)
sudo debconf-set-selections <<< 'mariadb-server mysql-server/root_password password rootpass'
sudo debconf-set-selections <<< 'mariadb-server mysql-server/root_password_again password rootpass'
sudo apt-get -y install mariadb-server

# Execute mysql initial setup
cat dbsetup.sql | mysql -uroot -prootpass


# This section adds default controller/monitor/agent values to /etc/hosts file
# NOTE: This assigns the local hosts' local ip address to all three; 
# !CHANGE! the ip address values below (by replacing '$ipadd' with the correct
# ip address of each or change manually (in /etc/hosts) after setup is complete.

# Get current local ip address and store in variable 'ipadd'
ipadd="$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1 -d'/')"

# Backup ORIGINAL hosts file
sudo cp /etc/hosts /etc/hosts.shnbackup

# Add default values to shntemp file (along with copy of current /etc/hosts)
sudo echo "$ipadd   agent1.shn.local       agent1" | cat - /etc/hosts > shntemp && sudo mv shntemp shntemp2
sudo echo "$ipadd   monitor.shn.local      monitor" | cat - shntemp2 > shntemp && sudo mv shntemp shntemp2
sudo echo "$ipadd   controller.shn.local   controller" | cat - shntemp2 > shntemp && sudo rm shntemp2

# Change permissions / owndership of temp file to match /etc/hosts file
sudo chown --reference=/etc/hosts shntemp
sudo chmod --reference=/etc/hosts shntemp

# Move temp file to replace /etc/hosts file
sudo mv shntemp /etc/hosts

## End of Script
echo "End of setup script."
echo "RECOMMEND Changing mysql root password."
echo "(Current Password: 'rootpass')"
