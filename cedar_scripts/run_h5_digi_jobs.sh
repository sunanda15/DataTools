#!/bin/bash
# Example script to set up and submit batch jobs

# exit when any command fails
set -e

# initial environment setup
export DATATOOLS=/project/rpp-blairt2k/jgao/DataTools
cd $DATATOOLS/cedar_scripts

# project name, input data directory and output file name for this run
name=HKHybrid
data_dir=/scratch/jgao/data/
output_dir=/scratch/jgao/data/HKHybrid/h5
mkdir -p $output_dir

log_dir="/scratch/jgao/log/h5"
mkdir -p $log_dir
cd $log_dir

# 0-999 npz files for mu-, 0-999 npz files for e-
# 0-9 in 1 file, 10-99 in 1 file, 100-199 ... 900-999.
for i in {1..9}; do
  for j in mu- pi0; do
    f="${data_dir}/${name}/${j}/*/*/*/*_${i}[0-9][0-9].npz "
    sbatch --time=3:0:0 --job-name=npz2h5_${j}_${i} \
      "${DATATOOLS}/cedar_scripts/make_digihit_h5.sh" \
      "${output_dir}/${j}_${i}.hdf5" "$f"
  done
done

