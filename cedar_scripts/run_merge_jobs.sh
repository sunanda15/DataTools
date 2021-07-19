#!/bin/bash
# Script for submitting batch job for merging h5 files

# exit when any command fails
set -e

# initial environment setup
export DATATOOLS=/project/rpp-blairt2k/jgao/DataTools
cd $DATATOOLS/cedar_scripts

# project name, input data directory and output file name for this run
name=HKHybrid
data_dir=/scratch/jgao/data/h5
output_dir=/scratch/jgao/data
mkdir -p $output_dir

log_dir="/scratch/jgao/log/h5"
mkdir -p $log_dir
cd $log_dir

# 0-999 npz files for mu-, 0-999 npz files for e-
# 0-9 in 1 file, 10-99 in 1 file, 100-199 ... 900-999
f="${data_dir}/*.hdf5"
sbatch --time=2:0:0 --job-name=mergeh5_all \
"${DATATOOLS}/cedar_scripts/merge_h5_script.sh" \
"${output_dir}/all.hdf5" "$f"

