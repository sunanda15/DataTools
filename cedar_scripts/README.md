This folder contains all the scripts that run a variety of jobs on cedar. There are a few important ones for the HK hybrid data processing:

1. make_hybrid_npz.sh and run_npz_jobs.sh
   to run, simply do: ./run_npz_jobs.sh
   These two files combined do the job of submitting batch jobs for processing each WCSim output root file into a npz file. Currently one batch job processes one root files, but you can change this by amending file name variable "f" in run_npz_jobs.sh.

2. make_digihit_h5.sh and run_h5_digi_jobs.sh
   to run, simply do ./run_h5_digi_jobs.sh
   These two files 
