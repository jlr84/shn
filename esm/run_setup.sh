#!/bin/bash
# This is an initial setup sript for my SHN project (See: https://github.com/jlr84/shn )
# This is a shorter setup script for use with the ESM on a separate system (without 
# the monitor/controller/agent)
# The main difference is that this is not as dependant on Python 3.5, so that is not 
# checked, and MySQL is not required, to MySQL setup steps are removed. 
# 
#!!!!
# ADDITIONALLY, the controller/monitor ip addresses have to be manually set!!!
#!!!!
MONITOR_IP=172.31.31.112
CONTROLLER_IP=172.31.31.112

echo "--SHN-- Starting Setup Script."

# Update packages
echo "--SHN-- Updating host's packages with 'apt-get update'."
sudo apt-get update

# Install pip | debconf
echo "--SHN-- Installing pip (for python3) & debconf-utils."
sudo apt-get -y install python3-pip debconf-utils

# Install project requirements using pip (based on 'requirements.txt')
# Note: Assumption that 'requipments.txt' is in parent directory
echo "--SHN-- Installing project requirements using pip."
sudo -H pip3 install -r ../requirements.txt


# This section adds default controller/monitor/agent values to /etc/hosts file
# NOTE: This assigns the local hosts' local ip address to all three; 
# !CHANGE! the ip address values below (by replacing '$ipadd' with the correct
# ip address of each or change manually (in /etc/hosts) after setup is complete.
echo "--SHN-- Adding default values for controller, monitor, and agent1 to '/etc/hosts' file."
echo "--SHN-- NOTE: Original hosts file saved as '/etc/hosts.shnbackup'."

# Get current local ip address and store in variable 'IPADD'
IPADD="$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1 -d'/')"
echo "--SHN-- Your current local ip address is '$IPADD'; using this as default for controller, monitor, and agent1 (unless already adjusted manually in this script file)."

# Backup ORIGINAL hosts file
sudo cp /etc/hosts /etc/hosts.shnbackup

# Add default values to shntemp file (along with copy of current /etc/hosts)
sudo echo "$IPADD   agent1.shn.local       agent1" | cat - /etc/hosts > shntemp && sudo mv shntemp shntemp2
sudo echo "$MONITOR_IP   monitor.shn.local      monitor" | cat - shntemp2 > shntemp && sudo mv shntemp shntemp2
sudo echo "$CONTROLLER_IP   controller.shn.local   controller" | cat - shntemp2 > shntemp && sudo rm shntemp2

# Change permissions / owndership of temp file to match /etc/hosts file
echo "--SHN-- New/updated [temporary] hosts file created; adjusting ownership/permission to match original hosts flie."
sudo chown --reference=/etc/hosts shntemp
sudo chmod --reference=/etc/hosts shntemp

# Move temp file to replace /etc/hosts file
echo "--SHN-- Saving new/updated hosts file to '/etc/hosts'."
sudo mv shntemp /etc/hosts

## End of Script
echo "--SHN-- Initial setup complete."
