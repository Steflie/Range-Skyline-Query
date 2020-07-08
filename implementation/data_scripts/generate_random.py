#!/usr/bin/python

# generate_random.py ----------------------------------------------------------------------------------------
#
# Description:
#     The script creates a file with randomly produced numbers which represent values of points.
#     Every line represents a point.
#
# Usage: 
#     python generate_random.py <points_volume> <num_of_dimensions>
#
# Result:
#     A txt file with the name random_<points_volume>_<num_of_dimensions>
# --------------------------------------------------------------------------------------------------

import sys
import random
import csv


# Initialize environment variables
repository = "/home/linuxas/Thesis/points_and_queries/points"

# Take script arguments
volume = int(sys.argv[1])
num_dims = int(sys.argv[2])

# File's name
filename = "random_{}_{}".format(volume, num_dims)

# Biggest random number that can be generated
#if volume == 1000:
#    biggest = 100
#elif volume == 10000 or volume == 100000:
#    biggest = 1000
#elif volume == 1000000 or volume == 10000000:
biggest = 10000

# Every appended list represents a dimension
# and will store volume random numbers
values = []
for index in range(num_dims):
    values.append([])

# Generate the random points
for index in range(volume):
    for sub_list in values:
        sub_list.append(random.randint(1, biggest))

# Write to the file
file = open(repository+'/'+filename, 'w')

writer = csv.writer(file, delimiter=' ')
writer.writerows(zip(*values))

file.close()
