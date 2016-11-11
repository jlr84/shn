#!/bin/bash
# CLONE VM: This is a script to restore to a clone when 
# given a clone name, the current name, and a name to save 
# the old VM hard drive to.
# NOTE: vm stopped is NOT deleted (simply shutdown, to 
# retain for forensics analysis [future work])

# SETTINGS:
# Note: Currently set to take the name of the current vm, the 
# name of the clone to restore to, and the new vm name as the
# first/second/third command line arguments. Comment out the 
# next three lines and remove "#" from the fourth-sixth lines
# to specify names here instead of via command line. 
CURRENTVM=$1
CLONENAME=$2
NEWNAME=$3
#CURRENTVM="vud2"
#CLONENAME="vud2_clone_1"
#NEWNAME="vud3"

# Step 1: STOP current VUD/VM
echo "Stopping Current VUD/VM, $CURRENTVM..."
sudo xl shutdown $CURRENTVM


# Step 2: Rename CURRENT(OLD) lvs to new name
echo "Changing CURRENT(OLD) lvs from $CURRENTVM to $NEWNAME"
sudo lvrename /dev/xen1/$CURRENTVM /dev/xen1/$NEWNAME


# Step 3: Rename CLONE lvs to CURRENT(NEW) name
echo "Changing CLONE lvs to CURRENT(NEW) name: from $CLONENAME to $CURRENTVM"
sudo lvrename /dev/xen1/$CLONENAME /dev/xen1/$CURRENTVM

# Verify name change
echo "VERIFY Names Changed:"
sudo lvs


# Step 4: Remove config file for clone (no longer needed)
echo "Removing Clone config file no longer needed"
sudo rm /etc/xen/$CLONENAME.cfg


# Step 5: Start Newly restored VUD/VM 
#echo "Starting restored VM now, named $CURRENTVM."
#sudo xl create /etc/xen/$CURRENTVM.cfg
