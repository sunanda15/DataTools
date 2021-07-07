#!/bin/bash
# Example script to set up and submit batch jobs

# exit when any command fails
set -e

# initial environment setup
export DATATOOLS=/project/rpp-blairt2k/jgao/DataTools
cd $DATATOOLS/cedar_scripts

# project name, input data directory and output file name for this run
name=HKHybrid
data_dir=/scratch/jgao/data
output_dir=/scratch/jgao/data/h5
mkdir -p $output_dir

log_dir="/scratch/jgao/log/h5"
mkdir -p $log_dir
cd $log_dir

# 0-999 npz files for mu-, 0-999 npz files for e-
# Try 2 files of 1 e- 1 mu- at a time, concatinating file names together
for i in {0..0}; do
  for j in e- mu-; do
    f="${data_dir}/${name}/${j}/*/*/*/*_${i}.npz "
    sbatch --time=2:0:0 --job-name=npz2h5 \
      "${DATATOOLS}/cedar_scripts/make_digihit_h5.sh" \
      "${output_dir}/${j}_${i}.hdf5" "$f"
  done
done

# Try 20 files of 10 e- 10 mu- at a time