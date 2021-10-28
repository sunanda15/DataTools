#!/bin/bash
#SBATCH --account=rpp-blairt2k
#SBATCH --time=5-0:00:00
#SBATCH --mem=10G
#SBATCH --output=%x.%A-%a.out
#SBATCH --error=%x.%A-%a.err
#SBATCH --cpus-per-task=1
#SBATCH --array=0-399

# runs fitqun on file
# usage: runfiTQun.sh [input WCSim file] [output suffix] [parameter override file] [numper of events to skip] [number of events to fit] [log dir]
# output directory is input directory with WCSim replaced by fiTQun
# array job replaces 0 in _0. with the SLURM_ARRAY_TASK_ID

# exit when any command fails
set -e

ulimit -c 0

in_file="${1/_0./_$SLURM_ARRAY_TASK_ID.}"
out_file="${in_file/WCSim/fiTQun}"
out_file="${out_file/.root/_${4}.${2}.root}"
out_name="$(basename "$out_file")"
out_dir="$(dirname "$out_file")"
logfile="${6}/${out_name/.root/.log}"
mkdir -p "$out_dir"
mkdir -p "$6"
echo "[`date`] running fiTQun on ${in_file} output to ${out_file}"
cd $FITQUN_ROOT
./runfiTQunWC -s "$4" -n "$5" -p "$3" -r "$out_file" "${in_file}" > "${logfile}"
endtime="`date`"
echo "[${endtime}] Completed"
