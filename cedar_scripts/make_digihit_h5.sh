#!/bin/bash
#SBATCH --account=rpp-blairt2k
#SBATCH --time=0:01:0
#SBATCH --mem-per-cpu=1M
#SBATCH --output=%x-%a.out
#SBATCH --error=%x-%a.err
#SBATCH --cpus-per-task=1

# sets up environment and runs np_to_hit_array_hdf5.py, see that file for info
# on arguments, that all get passed through from this script

# need to write another script for the batch mode, if you're just running this
# script it counts as running in the login node

ulimit -c 0

#source /project/rpp-blairt2k/machine_learning/production_software/DataTools/\
# cedar_scripts/sourceme.sh
source ~/sourceme.sh

virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index h5py

#cd /project/rpp-blairt2k/machine_learning/production_software/DataTools/\
# root_utils/
cd /home/jgao/work/DataTools/root_utils/

# initially save to SLURM_TMPDIR for speed
#args=("$@")
#for i in "${!args[@]}"; do
#  if [[ ${args[$i]} == "-o" ]]; then
#    outfile="${args[$i+1]}"
#    tmpfile="${SLURM_TMPDIR}/$(basename $outfile)"
#    args[$i+1]="$tmpfile"
#    break
#  fi
#done

# need to pass in output path + output name with option "-o", and the name of
# the npz files
echo "python np_to_digihit_array_hdf5.py -o $1 ${@:2}"
# python np_to_digihit_array_hdf5.py -o "$1" "${@:2}"

#echo "cp $tmpfile $outfile"
#cp "$tmpfile" "$outfile"
