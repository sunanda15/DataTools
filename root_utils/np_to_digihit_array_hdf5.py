import numpy as np
import os
import sys
import subprocess
from datetime import datetime
import argparse
import h5py
import root_utils.pos_utils as pu

def get_args():
    parser = argparse.ArgumentParser(description='convert and merge .npz files\
      to hdf5')
    parser.add_argument('input_files', type=str, nargs='+')
    parser.add_argument('-o', '--output_file', type=str)
    parser.add_argument('-H', '--half-height', type=float, default=300)
    parser.add_argument('-R', '--radius', type=float, default=400)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    config = get_args()
    print("ouput file:", config.output_file)
    f = h5py.File(config.output_file, 'w')
    
    script_path = os.path.dirname(os.path.abspath(__file__))
    git_status = subprocess.check_output(['git', '-C', script_path, 'status', 
                                '--porcelain', '--untracked-files=no']).decode()
    if git_status:
        raise Exception("Directory of this script ({}) is not a clean git \
          directory:\n{}Need a clean git directory for storing script version \
          in output file.".format(script_path, git_status))
    git_describe = subprocess.check_output(['git', '-C', script_path,'describe', 
                               '--always', '--long', '--tags']).decode().strip()
    print("git describe for path to this script ({}):".format(script_path), 
        git_describe)
    f.attrs['git-describe'] = git_describe
    f.attrs['command'] = str(sys.argv)
    f.attrs['timestamp'] = str(datetime.now())

    total_rows = 0  # count total events
    total_hits = 0  # total hits in 1 event
    min_hits = 1
    good_rows = 0  # count 'good' events - with at least 1 hit
    good_hits = 0  # total num of hits in 'good' events
    print("counting events and hits, in files")
    file_event_triggers_20 = {}  # dict storing first triggers of good events
    file_event_triggers_3 = {}
    for input_file in config.input_files:
        print(input_file, flush=True)
        if not os.path.isfile(input_file):
            raise ValueError(input_file+" does not exist")
        npz_file = np.load(input_file)
        # split between 20" and 3"
        trigger_times_20 = npz_file['trigger_time_20']
        trigger_types_20 = npz_file['trigger_type_20']

        trigger_times_3 = npz_file['trigger_time_3']
        trigger_types_3 = npz_file['trigger_type_3']

        hit_triggers_20 = npz_file['digi_hit_trigger_20']
        hit_triggers_3 = npz_file['digi_hit_trigger_3']

        event_triggers_20 = np.full(hit_triggers_20.shape[0], np.nan)
        event_triggers_3 = np.full(hit_triggers_3.shape[0], np.nan)

        total_rows += hit_triggers_20.shape[0]  # count total events, no need to adapt to 3"

        # since we have two trigger systems, can't simply count the hits for
        # one to tell if it's a good event. Hence the introduction of a flag,
        # when either PMT type record more than 1 hit, it's a good event
        good_event_flag = False

        # looping through events in a file, since shape[0] of the 20" and 3"
        # np arrays are both nevents, loop together
        # times/types/hit_trigs are all arrays, 1 per PMT type per event

        # can't put 20" and 3" together like this because the number of triggers
        # are different for 20" and 3". FIXME!!
        for i, (times_20, types_20, hit_trigs_20, times_3, types_3, hit_trigs_3)\
            in enumerate(zip(trigger_times_20, trigger_types_20, hit_triggers_20,
            trigger_times_3, trigger_types_3, hit_triggers_3)):

            good_triggers_20 = np.where(types_20==0)[0]
            good_triggers_3 = np.where(types_3==0)[0]
            if len(good_triggers_20)==0 and len(good_triggers_3) == 0:
                continue
            first_trigger_20 = good_triggers_20[np.argmin(times_20[good_triggers_20])]
            first_trigger_3 = good_triggers_3[np.argmin(times_3[good_triggers_3])]
            nhits_20 = np.count_nonzero(hit_trigs_20==first_trigger_20)
            nhits_3 = np.count_nonzero(hit_trigs_3==first_trigger_3)
            # total hits per event include both hits from 20" and 3"
            total_hits += nhits_20
            total_hits += nhits_3

            # good event is when the combined hits from 20" and 3" are more than 1
            if nhits_20 + nhits_3 >= min_hits:
                # the content of event_triggers_20 and _3 are exactly the same??? FIXME!!
                event_triggers_20[i] = first_trigger_20
                event_triggers_3[i] = first_trigger_3
                # good hits per event also include both hits from 20" and 3"
                good_hits += nhits_20
                good_hits += nhits_3
                good_rows += 1
        file_event_triggers_20[input_file] = event_triggers_20
        file_event_triggers_3[input_file] = event_triggers_3
    
    print(len(config.input_files), "files with", total_rows, "events with ", 
        total_hits, "hits")
    print(good_rows, "events with at least", min_hits, "hits for a total of", 
        good_hits, "hits")

    dset_labels=f.create_dataset("labels",
                                 shape=(good_rows,),
                                 dtype=np.int32)
    dset_PATHS=f.create_dataset("root_files",
                                shape=(good_rows,),
                                dtype=h5py.special_dtype(vlen=str))
    dset_IDX=f.create_dataset("event_ids",
                              shape=(good_rows,),
                              dtype=np.int32)
    # good_hits has length 20" hits + 3" hits, store hit info together?
    dset_hit_time=f.create_dataset("hit_time",
                                 shape=(good_hits, ),  
                                 dtype=np.float32)    
    dset_hit_charge=f.create_dataset("hit_charge",
                                 shape=(good_hits, ),
                                 dtype=np.float32)
    dset_hit_pmt=f.create_dataset("hit_pmt",
                                  shape=(good_hits, ),
                                  dtype=np.int32)

    # what does this variable even do... FIXME!!
    dset_event_hit_index=f.create_dataset("event_hits_index",
                                          shape=(good_rows,),
                                          dtype=np.int64) # int32 is too small to fit large indices
    dset_energies=f.create_dataset("energies",
                                   shape=(good_rows, 1),
                                   dtype=np.float32)
    dset_positions=f.create_dataset("positions",
                                    shape=(good_rows, 1, 3),
                                    dtype=np.float32)
    dset_angles=f.create_dataset("angles",
                                 shape=(good_rows, 2),
                                 dtype=np.float32)
    dset_veto = f.create_dataset("veto",
                                 shape=(good_rows,),
                                 dtype=np.bool_)
    dset_veto2 = f.create_dataset("veto2",
                                  shape=(good_rows,),
                                  dtype=np.bool_)

    offset = 0
    offset_next = 0
    hit_offset = 0
    hit_offset_next = 0
    label_map = {22: 0, 11: 1, 13: 2}  # 22 - gamma; 11 - electron; 13 - muon
    for input_file in config.input_files:
        print(input_file, flush=True)
        npz_file = np.load(input_file, allow_pickle=True)

        # need to add relevant stuff for 3"
        good_events_20 = ~np.isnan(file_event_triggers_20[input_file])
        good_events_3 = ~np.isnan(file_event_triggers_3[input_file])
        event_triggers_20 = file_event_triggers_20[input_file][good_events_20]
        event_triggers_3 = file_event_triggers_3[input_file][good_events_3]

        # the following particle & track info should be shared between 20" and 3"
        # theoretically only need to extract from one type of PMT (20" here)
        # unless I messed up 'good_events_20' value allocation
        event_ids = npz_file['event_id'][good_events_20]
        root_files = npz_file['root_file'][good_events_20]
        pids = npz_file['pid'][good_events_20]
        positions = npz_file['position'][good_events_20]
        directions = npz_file['direction'][good_events_20]
        energies = npz_file['energy'][good_events_20]
        track_pid = npz_file['track_pid'][good_events_20]
        track_energy = npz_file['track_energy'][good_events_20]
        track_stop_position = npz_file['track_stop_position'][good_events_20]
        track_start_position = npz_file['track_start_position'][good_events_20]

        hit_times_20 = npz_file['digi_hit_time_20'][good_events_20]
        hit_charges_20 = npz_file['digi_hit_charge_20'][good_events_20]
        hit_pmts_20 = npz_file['digi_hit_pmt_20'][good_events_20]
        hit_triggers_20 = npz_file['digi_hit_trigger_20'][good_events_20]

        hit_times_3 = npz_file['digi_hit_time_3'][good_events_3]
        hit_charges_3 = npz_file['digi_hit_charge_3'][good_events_3]
        hit_pmts_3 = npz_file['digi_hit_pmt_3'][good_events_3]
        hit_triggers_3 = npz_file['digi_hit_trigger_3'][good_events_3]

        offset_next += event_ids.shape[0]  # prepare for the next file

        dset_IDX[offset:offset_next] = event_ids
        dset_PATHS[offset:offset_next] = root_files
        dset_energies[offset:offset_next,:] = energies.reshape(-1,1)
        dset_positions[offset:offset_next,:,:] = positions.reshape(-1,1,3)

        labels = np.full(pids.shape[0], -1)
        for l, v in label_map.items():
            labels[pids==l] = v
        dset_labels[offset:offset_next] = labels

        polars = np.arccos(directions[:,1])
        azimuths = np.arctan2(directions[:,2], directions[:,0])
        dset_angles[offset:offset_next,:] = np.hstack((polars.reshape(-1,1),azimuths.reshape(-1,1)))

        # the following is for calculating the veto & veto2
        for i, (pids, energies, starts, stops) in enumerate(zip(track_pid, 
            track_energy,track_start_position, track_stop_position)):

            muons_above_threshold = (np.abs(pids) == 13) & (energies > 166)  # what is this energy value?
            electrons_above_threshold = (np.abs(pids) == 11) & (energies > 2)
            gammas_above_threshold = (np.abs(pids) == 22) & (energies > 2)
            above_threshold = muons_above_threshold | electrons_above_threshold\
                | gammas_above_threshold
            outside_tank = (np.linalg.norm(stops[:,(0,2)], axis=1) > config.radius)\
                | (np.abs(stops[:, 1]) > config.half_height)
            dset_veto[offset+i] = np.any(above_threshold & outside_tank)
            end_energy_estimate = energies - np.linalg.norm(stops - starts, 
                axis=1) * 2
            muons_above_threshold = (np.abs(pids) == 13) & (end_energy_estimate > 166)
            electrons_above_threshold = (np.abs(pids) == 11) & (end_energy_estimate > 2)
            gammas_above_threshold = (np.abs(pids) == 22) & (end_energy_estimate > 2)
            above_threshold = muons_above_threshold | electrons_above_threshold\
                | gammas_above_threshold
            dset_veto2[offset+i] = np.any(above_threshold & outside_tank)

        for i, (trigs_20, times_20, charges_20, pmts_20) in enumerate(zip(
            hit_triggers_20, hit_times_20, hit_charges_20, hit_pmts_20)):
            
            # start of the loop: hit_offset at the end of 3" data from last event
            dset_event_hit_index[offset+i] = hit_offset
            hit_indices_20 = np.where(trigs_20==event_triggers_20[i])[0]
            
            # the length of 20" hit info = "baseline" + new info length
            hit_offset_next = hit_offset + len(hit_indices_20)

            dset_hit_time[hit_offset:hit_offset_next] = times_20[hit_indices_20]
            dset_hit_charge[hit_offset:hit_offset_next] = charges_20[hit_indices_20]
            dset_hit_pmt[hit_offset:hit_offset_next] = pmts_20[hit_indices_20]

            hit_offset = hit_offset_next  # at the end of 20" data

            for j, (trigs_3, times_3, charges_3, pmts_3) in enumerate(zip(
                hit_triggers_3, hit_times_3, hit_charges_3, hit_pmts_3)):

                hit_indices_3 = np.where(trigs_3==event_triggers_3[i])[0]

                # the length of 3" hit info = "baseline" + new info length
                hit_offset_next = hit_offset + len(hit_indices_3)

                dset_hit_time[hit_offset:hit_offset_next] = times_3[hit_indices_3]
                dset_hit_charge[hit_offset:hit_offset_next] = charges_3[hit_indices_3]
                dset_hit_pmt[hit_offset:hit_offset_next] = pmts_3[hit_indices_3]



            hit_offset = hit_offset_next

        offset = offset_next
    f.close()
    print("saved", hit_offset, "hits in", offset, "good events (each with at least", min_hits, "hits)")
