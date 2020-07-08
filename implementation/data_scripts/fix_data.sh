#!/bin/bash

# fix_data.sh --------------------------------------------------------------------------------------
#
# Description:
#   This script transforms the given file in order to meet the format standards of the project.
#   Every column uses one space as a delimeter and every line column are data.
#   Metadata lines and columns are being erased.
#
# Usage: 
#   ./fix_data.sh <filename>
#
# Result:
#   The same file with the right format
# --------------------------------------------------------------------------------------------------

# Initialize environment variables
dir_to_store=$(echo '../../points_and_queries/points')

# Get parameter
filename="$1"

echo "Process the file: $filename"

# Remove the first line of the file
sed -i '1d' $filename 

# Subtitute multiple spaces with one
sed -i 's/\t/     /g' $filename
sed -ie "s/  */ /g" $filename

# Discard the first column
#cut -d ' ' -f 2- $filename
sed -i -r 's/(\s+)?\S+//1' $filename

# Move the file to the data repository
mv $filename ${dir_to_store}/$filename