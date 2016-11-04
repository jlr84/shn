#!/bin/bash
# CLONE VM: This is a script to restore to a clone when 
# given a clone name and the current vm to stop
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


# Step 2: Change clone lvs name match new vud name
echo "Changing Clone name from $CLONENAME to $NEWNAME"
sudo lvrename /dev/xen1/$CLONENAME /dev/xen1/$NEWNAME

# Verify name change
echo "VERIFY Name Changed to $NEWNAME:"
sudo lvs


# Step 3: Rename config file to match new name
# a) Change name of file
echo "Updating config file name"
sudo mv /etc/xen/$CLONENAME.cfg /etc/xen/$NEWNAME.cfg

# b) Swap clone name for new name 
grep -rl "$CLONENAME" /etc/xen/$NEWNAME.cfg | xargs sudo sed -i "s/$CLONENAME/$NEWNAME/g"


# Step 4: Start NEW VUD/VM 
echo "Starting restored VM now, named $NEWNAME."
sudo xl create /etc/xen/$NEWNAME.cfg
