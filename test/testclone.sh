#!/bin/bash

CURRENTVM=$1
CLONENAME=$2
CLONENUM=$3

# Set current time to zero
SECONDS=0
now=$(date +"%T")

echo "Starting Test"

# Print current time
echo "Time1: $now"
echo "Duration: $SECONDS"
echo "Cloning from $CURRENTVM to $CLONENAME$CLONENUM"
../scripts/clone2.sh $CLONENAME$CLONENUM

now2=$(date +"%T")
duration=$SECONDS

echo "Time2: $now2"
echo "Duration: $duration"
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
