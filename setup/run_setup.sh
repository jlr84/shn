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

# End of Script
echo "End of setup script."
echo "RECOMMEND Changing mysql root password."
echo "Current Password: 'rootpass'
