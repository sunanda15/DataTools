#!/bin/bash
#SBATCH --account=rpp-blairt2k
#SBATCH --time=3:00:00
#SBATCH --mem-per-cpu=16G
#SBATCH --output=%x-%a.out
#SBATCH --error=%x-%a.err
#SBATCH --cpus-per-task=1

# Reconverts the files given in the argument

# exit when any command fails
set -e

ulimit -c 0

source /home/jgao/sourceme.sh
long_data_dir=${data_dir}/HKHybrid/WCSim

for var in "$@"; do
  for file in `echo $var`; do
    echo "The current file is $file"
    npzdir="$(dirname "$file")"
    echo "The directory containing file is extracted, which is $npzdir"
    npzdir="${npzdir//$long_data_dir/}"
    echo "After deletion, the dir path is $npzdir"
    npzdir="${data_dir}/${name}/numpy/${npzdir}"
    echo "The npz dir is $npzdir"
    mkdir -p "$npzdir"
    echo "[`date`] converting ${file} to numpy file in ${npzdir}"
    # python "$DATATOOLS/root_utils/event_dump.py" "${file}" -d "${npzdir}"
  done
done

endtime="`date`"
echo "[${endtime}] Completed"
