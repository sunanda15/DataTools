#!/bin/bash

# Author: Joanna Gao    3 Nov 2021
# This script is for checking if the number of WCSim root output files generted
# matches expectation. It will also output the file numbers that are missing.
# To use this script, do 
#     ./check_root_file_generation.sh path/to/root/files/*

alist=()

# Obtain all the numbers of root files in an array. (unordered)
for var in "$@"; do
  for file in `echo $var`; do
    number=$( echo "$file" | grep -oE '[0-9]+\.' )
    number=$( echo "$number" | grep -oE '[0-9]+' )
    alist+=("$number")
  done
done
echo "loop done"
#echo ${alist[@]}

# Sort the array in order
sorted=( $( printf "%s\n" "${alist[@]}" | sort -n ) )
echo "Finished sorting"
# echo ${sorted[@]}

echo "There are" ${#sorted[@]} "files in the path provided."

# Find out the missing numbers
missing_number=0
offset=0
for i in "${!sorted[@]}"; do
  if [[ $((${sorted[$i]} - $offset)) -ne $i ]]; then
    echo "!! The missing file number is(are)" $(($i+$offset))
    ((offset+=1))
    missing_number=1
  fi
done

if [[ $missing_number -eq 0 ]]; then
  echo "There are no missing files, HURRAY!"
fi
