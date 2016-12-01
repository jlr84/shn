#!/bin/bash

# Set current time to zero
SECONDS=0
now=$(date +"%T")

# Print current time
echo "Time1: $now"
echo "Duration: $SECONDS"

sleep 5

now2=$(date +"%T")
duration=$SECONDS

echo "Time1: $now"
echo "Time2: $now2"
echo "Duration: $duration"
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
