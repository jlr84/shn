#!/bin/bash

## Update packages
#sudo apt-get update
#
## Install pip and git
#sudo apt-get -y install python-pip git 

#sudo apt-get -y install debconf-utils
#export DEBIAN_FRONTEND=noninteractive
sudo debconf-set-selections <<< 'mariadb-server mysql-server/root_password password rootpass'
sudo debconf-set-selections <<< 'mariadb-server mysql-server/root_password_again password rootpass'
sudo apt-get -y install mariadb-server

#
## Clone "shn" git repository
#git clone https://github.com/jlr84/shn.git
#
## Move into "shn" directory
#cd ./shn
#
## Install project requirements using pip (based on 'requirements.txt')
#sudo pip install -r ./requirements.txt
#
# End
echo "End of Script"

