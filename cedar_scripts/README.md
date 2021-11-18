This folder contains all the scripts that run a variety of jobs on cedar. There are a few important ones for the HK hybrid data processing:

1. make_hybrid_npz.sh and run_npz_jobs.sh
   to run, simply do: ./run_npz_jobs.sh
   These two files combined do the job of submitting batch jobs for processing 
   each WCSim output root file into a npz file. Currently one batch job 
   processes one root files, but you can change this by amending file name 
   variable "f" in run_npz_jobs.sh.

2. make_digihit_h5.sh and run_h5_digi_jobs.sh
   to run, simply do ./run_h5_digi_jobs.sh
   These two files combined do the job of submitting batch jobs for processing 
   multiple npz files into one h5 file. The current setup can only do the 
   tripple digit file numbers, to process single and double digit files, consult
   other bash scripts.

3. merge_h5_script.sh and run_merge_jobs.sh
   to run, simply do ./run_merge_jobs.sh
   These two files combined do the job of submitting batch jobs for processing
   multiple h5 files into one h5 file. The merge_h5.py script called by 
   merge_h5_script.sh is modified from Nick's code specifically for HK hybrid 
   geometry.
