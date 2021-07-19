#!/bin/bash
#SBATCH --account=rpp-blairt2k
#SBATCH --time=2:0:0
#SBATCH --mem-per-cpu=16G
#SBATCH --output=%x-%a.out
#SBATCH --error=%x-%a.err
#SBATCH --cpus-per-task=1

# sets up environment and runs merge_h5.py, see that file for info
# on arguments, that all get passed through from this script

# need to write another script for the batch mode, if you're just running this
# script it counts as running in the login node

ulimit -c 0

source /home/jgao/sourceme.sh

virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index h5py

cd /home/jgao/work/DataTools/root_utils/

# need to pass in output path + output name with option "-o", and the name of
# the h5 files
echo "python merge_h5.py -o $1 `echo ${@:2}`"
python merge_h5.py -o "$1" `echo ${@:2}`

