#!/bin/bash
# SNAPSHOT VM: This is a script to save a snapshot
# of a selected VM 

# SETTINGS:
# Note: Currently set to take the names for snapshot as the 
# first/second command line argument. Comment out the next 
# two lines and remove "#" from the third/fourth lines to 
# specify names here instead of via command line.
CURRENTVM=$1
SNAPNAME=$2
#CURRENTVM="vud1"
#SNAPNAME="vud1_snap_1"


# Step 1: Creating snapshot
echo "Creating snapshot $SNAPNAME based on VM $CURRENTVM..."
sudo lvcreate -y -L 1GB -s -n $SNAPNAME /dev/xen1/$CURRENTVM

# Verify Created with:
echo "VERIFY SNAPSHOT $SNAPNAME WAS CREATED:"
sudo lvs

# End of script
echo "END OF SNAPSHOT SCRIPT"
