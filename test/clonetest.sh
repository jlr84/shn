#!/bin/bash
# CLONE VM: This is a script to clone a VM for the SHNet project

# SETTINGS:
# Note: Currently set to take the names for cloning as the 
# first/second command line argument. Comment out the next 
# two lines and remove "#" from the third/fourth lines to 
# specify names here instead of via command line.
CURRENTVM=$1
CLONEDVM=$2
#CURRENTVM="ubud2"
#CLONEDVM="vud2"


# Set current time to zero
SECONDS=0
now=$(date +"%T")

echo "Starting Test"

# Print current time
echo "Time1: $now"
echo "Duration: $SECONDS"
echo "Cloning from $CURRENTVM to $CLONEDVM"

# Step 1: Create new LVS Partition (named 'vud2')
echo "Creating new LVS partition..."
sudo lvcreate -y -L 10G -n $CLONEDVM /dev/xen1

# Verify Created with:
echo "VERIFY LVS PARTITION $CLONEDVM CREATED:"
sudo lvs


# Step 2: Shutdown lvs if in use
echo "Shutdown Current LVS, $CURRENTVM"
sudo xl shutdown $CURRENTVM


# Step 3: Copy OLD Disk (vud1) to NEW Disk (vud2)
echo "Copying Disks... this may take a few minutes"
sudo dd if=/dev/xen1/$CURRENTVM of=/dev/xen1/$CLONEDVM bs=32768


# Step 4: Create config file to use new lvs disk
# a) Copy old config to new config
echo "Updating config file"
sudo cp /etc/xen/$CURRENTVM.cfg /etc/xen/$CLONEDVM.cfg

# b) Swap old name (vud1) for new name (vud2)
grep -rl "$CURRENTVM" /etc/xen/$CLONEDVM.cfg | xargs sudo sed -i "s/$CURRENTVM/$CLONEDVM/g"


# Step 5: Start Old lvs back up. (New remains as clone.) 
#echo "Re-starting old (original/cloned) VM now."
#sudo xl create /etc/xen/$CURRENTVM.cfg
echo "Test completed. Results:"
now2=$(date +"%T")
duration=$SECONDS

echo "Time2: $now2"
echo "Duration: $duration"
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
              
