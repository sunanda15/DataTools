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
# 0-9 in 1 file, 10-99 in 1 file, 100-199 ... 900-999.
# Turns out the merge_h5.py file needs modifying, I'm too lazy, processing
# all npz files together for now
# for i in {1..9}; do
#   for j in e- mu-; do
#     f="${data_dir}/${name}/${j}/*/*/*/*_${i}[0-9][0-9].npz "
#     sbatch --time=2:0:0 --job-name=npz2h5_${j}_${i} \
#       "${DATATOOLS}/cedar_scripts/make_digihit_h5.sh" \
#       "${output_dir}/${j}_${i}.hdf5" "$f"
#   done
# done

f="${data_dir}/${name}/mu-/*/*/*/*_5[0-9][0-9].npz"
sbatch --time=4:0:0 --job-name=npz2h5_mu-_5 \
  "${DATATOOLS}/cedar_scripts/make_digihit_h5.sh" \
  "${output_dir}/mu-_5.hdf5" "$f"

f1="${data_dir}/${name}/e-/*/*/*/*_9[0-9][0-9].npz"
sbatch --time=4:0:0 --job-name=npz2h5_e-_9 \
  "${DATATOOLS}/cedar_scripts/make_digihit_h5.sh" \
  "${output_dir}/e-_9.hdf5" "$f1"
