#!/bin/bash

# random.sh ----------------------------------------------------------------------------------------
#
# Description:
#     The script creates a file with randomly produced numbers which represent values of points.
#     Every line represents a point.
#
# Usage: 
#     ./random.sh <points_volume> <num_of_dimensions>
#
# Result:
#     A txt file with the name random_<points_volume>_<num_of_dimensions>
#
# --------------------------------------------------------------------------------------------------

# Initialize environment variables
dir_to_store=$(echo '../../points_and_queries/points')

# Get parameters
volume=$(echo "$1")
dims=$(echo "$2")

# Construnct file's name
filename="random_${volume}_${dims}"

for i in $(eval echo "{1..$volume}");do 
    for j in $(eval echo "{1..$dims}");do
        # The range of the random nums is mod 2*volume
        R1=$(shuf -i 0-300000 -n 1)
        R2=$(($R1%$((2*${volume}))))
        echo $R2  >> random_numbers
    done  
done

# Transform every ${dims} rows to columns
awk -v var=${dims} 'ORS=NR%var?" ":"\n"' random_numbers  > ${dir_to_store}/${filename}

# Remove the temporary file
rm ./random_numbers