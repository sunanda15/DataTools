#!/bin/bash
#SBATCH --job-name=test_data_proc
#SBATCH --account=rpp-blairt2k
#SBATCH --time=02:30:00
#SBATCH --mem-per-cpu=8000
#SBATCH --output=%x-%a.out
#SBATCH --error=%x-%a.err
#SBATCH --cpus-per-task=1

# script written for testing the data conversion process for hybrid hk
DATA_PATH=/project/rpp-blairt2k/machine_learning/data/HKHybrid/WCSim/mu-/E0to1000MeV/unif-pos-R3240-y3287cm/4pi-dir

source ~/sourceme.sh

echo "About to run python"
# this command is not working for some reason, Nick said I need to flush the
# output but I've yet to figure out how to do that
python /home/jgao/work/DataTools/root_utils/event_dump.py $DATA_PATH/HKHybrid_mu-_E0to1000MeV_unif-pos-R3240-y3287cm_4pi-dir_3000evts_707.root -d /home/jgao/work/DataTools/root_utils/output_folder
echo "Python should be up and running"