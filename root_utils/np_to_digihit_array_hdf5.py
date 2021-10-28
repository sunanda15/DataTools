# Modified from Nick Prouse's h5 data processing code. Added code to extract 3"
# PMT info (stored separatly from 20")

import numpy as np
import os
import sys
import subprocess
from datetime import datetime
import argparse
import h5py

def get_args():
    parser = argparse.ArgumentParser(description='convert and merge .npz files to hdf5')
    parser.add_argument('input_files', type=str, nargs='+')
    parser.add_argument('-o', '--output_file', type=str)
    parser.add_argument('-H', '--half-height', type=float, default=7100)
    parser.add_argument('-R', '--radius', type=float, default=3400)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    config = get_args()
    print("ouput file:", config.output_file)
    f = h5py.File(config.output_file, 'w')

    script_path = os.path.dirname(os.path.abspath(__file__))
    git_status = subprocess.check_output(['git', '-C', script_path, 
                                          'status','--porcelain', 
                                          '--untracked-files=no']).decode()
    if git_status:
        raise Exception("Directory of this script ({}) is not a clean git" +
                        "directory:\n{}Need a clean git directory for storing" +
                        "script version in output file."
                        .format(script_path, git_status))
    git_describe = subprocess.check_output(['git', '-C', script_path, 
                                            'describe', '--always', '--long', 
                                            '--tags']).decode().strip()
    print("git describe for path to this script ({}):"
          .format(script_path), git_describe)
    f.attrs['git-describe'] = git_describe
    f.attrs['command'] = str(sys.argv)
    f.attrs['timestamp'] = str(datetime.now())

    total_rows = 0  # the number of events that have non zero hits
    total_hits = 0
    min_hits = 1
    good_rows_20 = 0
    good_hits_20 = 0
    good_rows_3 = 0  # is this what I need? FIXME!!
    good_hits_3 = 0
    print("counting events and hits, in files")
    file_event_triggers_20 = {}
    file_event_triggers_3 = {}
    for input_file in config.input_files:
        print(input_file, flush=True)
        if not os.path.isfile(input_file):
            raise ValueError(input_file+" does not exist")
        npz_file = np.load(input_file)

        # 20" PMT related
        trigger_times_20 = npz_file['trigger_time_20']
        trigger_types_20 = npz_file['trigger_type_20']
        hit_triggers_20 = npz_file['digi_hit_trigger_20']
        total_rows += hit_triggers_20.shape[0]  # not limited to 20"
        event_triggers_20 = np.full(hit_triggers_20.shape[0], np.nan)
        for i, (times, types, hit_trigs) in enumerate(zip(trigger_times_20, 
            trigger_types_20, hit_triggers_20)):

            good_triggers = np.where(types == 0)[0]
            if len(good_triggers) == 0:
                continue
            first_trigger = good_triggers[np.argmin(times[good_triggers])]
            nhits = np.count_nonzero(hit_trigs == first_trigger)
            total_hits += nhits
            if nhits >= min_hits:
                event_triggers_20[i] = first_trigger
                good_hits_20 += nhits
                good_rows_20 += 1
        file_event_triggers_20[input_file] = event_triggers_20

        # 3" PMT related
        trigger_times_3 = npz_file['trigger_time_3']
        trigger_types_3 = npz_file['trigger_type_3']
        hit_triggers_3 = npz_file['digi_hit_trigger_3']
        event_triggers_3 = np.full(hit_triggers_3.shape[0], np.nan)
        for i, (times, types, hit_trigs) in enumerate(zip(trigger_times_3, 
            trigger_types_3, hit_triggers_3)):

            good_triggers = np.where(types == 0)[0]
            if len(good_triggers) == 0:
                continue
            first_trigger = good_triggers[np.argmin(times[good_triggers])]
            nhits = np.count_nonzero(hit_trigs == first_trigger)
            total_hits += nhits
            if nhits >= min_hits:
                event_triggers_3[i] = first_trigger
                good_hits_3 += nhits
                good_rows_3 += 1
        file_event_triggers_3[input_file] = event_triggers_3

    print(len(config.input_files), "files with", total_rows, "events with ", 
        total_hits, "hits")
    print(good_rows_20, "events (20in PMT) with at least", min_hits, 
        "hits for a total of", good_hits_20, "hits")
    print(good_rows_3, "events (3in PMT) with at least", min_hits, 
        "hits for a total of", good_hits_3, "hits")

    dset_labels = f.create_dataset("labels",
                                   shape=(total_rows,),
                                   dtype=np.int32)
    dset_PATHS = f.create_dataset("root_files",
                                  shape=(total_rows,),
                                  dtype=h5py.special_dtype(vlen=str))
    dset_IDX = f.create_dataset("event_ids",
                                shape=(total_rows,),
                                dtype=np.int32)
    dset_hit_time_20 = f.create_dataset("hit_time_20",
                                     shape=(good_hits_20, ),
                                     dtype=np.float32)
    dset_hit_charge_20 = f.create_dataset("hit_charge_20",
                                       shape=(good_hits_20, ),
                                       dtype=np.float32)
    dset_hit_pmt_20 = f.create_dataset("hit_pmt_20",
                                    shape=(good_hits_20, ),
                                    dtype=np.int32)
    dset_event_hit_index_20 = f.create_dataset("event_hits_index_20",
                                            shape=(total_rows,),
                                            dtype=np.int64)  # int32 is too 
                                                             # small to fit 
                                                             # large indices
    dset_hit_time_3 = f.create_dataset("hit_time_3",
                                     shape=(good_hits_3, ),
                                     dtype=np.float32)
    dset_hit_charge_3 = f.create_dataset("hit_charge_3",
                                       shape=(good_hits_3, ),
                                       dtype=np.float32)
    dset_hit_pmt_3 = f.create_dataset("hit_pmt_3",
                                    shape=(good_hits_3, ),
                                    dtype=np.int32)
    dset_event_hit_index_3 = f.create_dataset("event_hits_index_3",
                                            shape=(total_rows,),
                                            dtype=np.int64)
    dset_energies = f.create_dataset("energies",
                                     shape=(total_rows, 1),
                                     dtype=np.float32)
    dset_positions = f.create_dataset("positions",
                                      shape=(total_rows, 1, 3),
                                      dtype=np.float32)
    dset_angles = f.create_dataset("angles",
                                   shape=(total_rows, 2),
                                   dtype=np.float32)
    dset_veto = f.create_dataset("veto",
                                 shape=(total_rows,),
                                 dtype=np.bool_)
    dset_veto2 = f.create_dataset("veto2",
                                  shape=(total_rows,),
                                  dtype=np.bool_)

    offset = 0
    offset_next = 0
    hit_offset_20 = 0
    hit_offset_next_20 = 0
    hit_offset_3 = 0
    hit_offset_next_3 = 0
    label_map = {22: 0, 11: 1, 13: 2}
    for input_file in config.input_files:
        print(input_file, flush=True)
        npz_file = np.load(input_file, allow_pickle=True)
        good_events_20 = ~np.isnan(file_event_triggers_20[input_file])
        good_events_3 = ~np.isnan(file_event_triggers_3[input_file])
        event_triggers_20 = file_event_triggers_20[input_file]
        event_triggers_3 = file_event_triggers_3[input_file]
        event_ids = npz_file['event_id']
        root_files = npz_file['root_file']
        pids = npz_file['pid']
        positions = npz_file['position']
        directions = npz_file['direction']
        energies = npz_file['energy']
        # 20"
        hit_times_20 = npz_file['digi_hit_time_20']
        hit_charges_20 = npz_file['digi_hit_charge_20']
        hit_pmts_20 = npz_file['digi_hit_pmt_20']
        hit_triggers_20 = npz_file['digi_hit_trigger_20']
        # 3"
        hit_times_3 = npz_file['digi_hit_time_3']
        hit_charges_3 = npz_file['digi_hit_charge_3']
        hit_pmts_3 = npz_file['digi_hit_pmt_3']
        hit_triggers_3 = npz_file['digi_hit_trigger_3']
        track_pid = npz_file['track_pid']
        track_energy = npz_file['track_energy']
        track_stop_position = npz_file['track_stop_position']
        track_start_position = npz_file['track_start_position']

        offset_next += event_ids.shape[0]

        dset_IDX[offset:offset_next] = event_ids
        dset_PATHS[offset:offset_next] = root_files
        dset_energies[offset:offset_next, :] = energies.reshape(-1, 1)
        dset_positions[offset:offset_next, :, :] = positions.reshape(-1, 1, 3)

        labels = np.full(pids.shape[0], -1)
        for k, v in label_map.items():
            labels[pids == k] = v
        dset_labels[offset:offset_next] = labels

        polars = np.arccos(directions[:, 1])
        azimuths = np.arctan2(directions[:, 2], directions[:, 0])
        dset_angles[offset:offset_next, :] = np.hstack((polars.reshape(-1, 1), 
                                                      azimuths.reshape(-1, 1)))

        for i, (pids, energies, starts, stops) in enumerate(zip(track_pid, 
            track_energy, track_start_position, track_stop_position)):

            muons_above_threshold = (np.abs(pids) == 13) & (energies > 166)
            electrons_above_threshold = (np.abs(pids) == 11) & (energies > 2)
            gammas_above_threshold = (np.abs(pids) == 22) & (energies > 2)
            above_threshold = muons_above_threshold | electrons_above_threshold\
                | gammas_above_threshold
            outside_tank = (np.linalg.norm(stops[:, (0, 2)], axis=2) > config.radius)\
                | (np.abs(stops[:, 1]) > config.half_height)
            dset_veto[offset+i] = np.any(above_threshold & outside_tank)
            end_energy_estimate = energies - np.linalg.norm(stops - starts,
                axis = 2) * 2
            muons_above_threshold = (np.abs(pids) == 13) &\
                (end_energy_estimate > 166)
            electrons_above_threshold = (np.abs(pids) == 11) &\
                (end_energy_estimate > 2)
            gammas_above_threshold = (np.abs(pids) == 22) &\
                (end_energy_estimate > 2)
            above_threshold = muons_above_threshold | electrons_above_threshold\
                | gammas_above_threshold
            dset_veto2[offset+i] = np.any(above_threshold & outside_tank)

        for i, (trigs, times, charges, pmts) in enumerate(zip(hit_triggers_20, 
            hit_times_20, hit_charges_20, hit_pmts_20)):

            dset_event_hit_index_20[offset+i] = hit_offset_20
            hit_indices = np.where(trigs == event_triggers_20[i])[0]
            hit_offset_next_20 += len(hit_indices)
            dset_hit_time_20[hit_offset_20:hit_offset_next_20] = times[hit_indices]
            dset_hit_charge_20[hit_offset_20:hit_offset_next_20] = charges[hit_indices]
            dset_hit_pmt_20[hit_offset_20:hit_offset_next_20] = pmts[hit_indices]
            hit_offset_20 = hit_offset_next_20

        for i, (trigs, times, charges, pmts) in enumerate(zip(hit_triggers_3, 
            hit_times_3, hit_charges_3, hit_pmts_3)):
            
            dset_event_hit_index_3[offset+i] = hit_offset_3
            hit_indices = np.where(trigs == event_triggers_3[i])[0]
            hit_offset_next_3 += len(hit_indices)
            dset_hit_time_3[hit_offset_3:hit_offset_next_3] = times[hit_indices]
            dset_hit_charge_3[hit_offset_3:hit_offset_next_3] = charges[hit_indices]
            dset_hit_pmt_3[hit_offset_3:hit_offset_next_3] = pmts[hit_indices]
            hit_offset_3 = hit_offset_next_3

        offset = offset_next
    f.close()
    print("saved", hit_offset_20, "hits in 20in", offset, " events (each \
        with at least", min_hits, "hits)")  # offset is a file
    print("saved", hit_offset_3, "hits in 3in", offset, " events (each \
        with at least", min_hits, "hits)")