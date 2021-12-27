"""
Python 3 script for processing a list of ROOT files into .npz files

To keep references to the original ROOT files, the file path is stored in the 
output. An index is saved for every event in the output npz file corresponding 
to the event index within that ROOT file (ev).

Authors: Nick Prouse

Modified by: Joanna Gao (Apr 2021)
"""

import argparse
from root_utils.root_file_utils import *
from root_utils.pos_utils import *

ROOT.gROOT.SetBatch(True)


def get_args():
    parser = argparse.ArgumentParser(description='dump WCSim data into numpy .npz file')
    parser.add_argument('input_files', type=str, nargs='+')
    parser.add_argument('-d', '--output_dir', type=str, default=None)
    args = parser.parse_args()
    return args


def dump_file(infile, outfile):

    wcsim = WCSimFile(infile)
    nevents = wcsim.nevent

    # All data arrays are initialized here

    event_id = np.empty(nevents, dtype=np.int32)
    root_file = np.empty(nevents, dtype=object)

    pid = np.empty(nevents, dtype=np.int32)
    position = np.empty((nevents, 3), dtype=np.float32)
    direction = np.empty((nevents, 3), dtype=np.float32)
    energy = np.empty(nevents,dtype=np.float32)

    digi_hit_pmt_20 = np.empty(nevents, dtype=object)
    digi_hit_charge_20 = np.empty(nevents, dtype=object)
    digi_hit_time_20 = np.empty(nevents, dtype=object)
    digi_hit_trigger_20 = np.empty(nevents, dtype=object)

    digi_hit_pmt_3 = np.empty(nevents, dtype=object)
    digi_hit_charge_3 = np.empty(nevents, dtype=object)
    digi_hit_time_3 = np.empty(nevents, dtype=object)
    digi_hit_trigger_3 = np.empty(nevents, dtype=object)

    true_hit_pmt_20 = np.empty(nevents, dtype=object)
    true_hit_time_20 = np.empty(nevents, dtype=object)
    true_hit_pos_20 = np.empty(nevents, dtype=object)
    true_hit_start_time_20 = np.empty(nevents, dtype=object)
    true_hit_start_pos_20 = np.empty(nevents, dtype=object)
    true_hit_parent_20 = np.empty(nevents, dtype=object)

    true_hit_pmt_3 = np.empty(nevents, dtype=object)
    true_hit_time_3 = np.empty(nevents, dtype=object)
    true_hit_pos_3 = np.empty(nevents, dtype=object)
    true_hit_start_time_3 = np.empty(nevents, dtype=object)
    true_hit_start_pos_3 = np.empty(nevents, dtype=object)
    true_hit_parent_3 = np.empty(nevents, dtype=object)

    track_id = np.empty(nevents, dtype=object)
    track_pid = np.empty(nevents, dtype=object)
    track_start_time = np.empty(nevents, dtype=object)
    track_energy = np.empty(nevents, dtype=object)
    track_start_position = np.empty(nevents, dtype=object)
    track_stop_position = np.empty(nevents, dtype=object)
    track_parent = np.empty(nevents, dtype=object)
    track_flag = np.empty(nevents, dtype=object)

    trigger_time_20 = np.empty(nevents, dtype=object)
    trigger_type_20 = np.empty(nevents, dtype=object)

    trigger_time_3 = np.empty(nevents, dtype=object)
    trigger_type_3 = np.empty(nevents, dtype=object)

    for ev in range(wcsim.nevent):
        wcsim.get_event(ev)
        # print("Now processing event ", ev)

        event_info = wcsim.get_event_info()
        pid[ev] = event_info["pid"]
        position[ev] = event_info["position"]
        direction[ev] = event_info["direction"]
        energy[ev] = event_info["energy"]

        true_hits_20 = wcsim.get_hit_photons_20()
        true_hit_pmt_20[ev] = true_hits_20["pmt_20"]
        true_hit_time_20[ev] = true_hits_20["end_time_20"]
        true_hit_pos_20[ev] = true_hits_20["end_position_20"]
        true_hit_start_time_20[ev] = true_hits_20["start_time_20"]
        true_hit_start_pos_20[ev] = true_hits_20["start_position_20"]
        true_hit_parent_20[ev] = true_hits_20["track_20"]

        true_hits_3 = wcsim.get_hit_photons_3()
        true_hit_pmt_3[ev] = true_hits_3["pmt_3"]
        true_hit_time_3[ev] = true_hits_3["end_time_3"]
        true_hit_pos_3[ev] = true_hits_3["end_position_3"]
        true_hit_start_time_3[ev] = true_hits_3["start_time_3"]
        true_hit_start_pos_3[ev] = true_hits_3["start_position_3"]
        true_hit_parent_3[ev] = true_hits_3["track_3"]

        digi_hits_20 = wcsim.get_digitized_hits_20()
        digi_hit_pmt_20[ev] = digi_hits_20["pmt_20"]
        digi_hit_charge_20[ev] = digi_hits_20["charge_20"]
        digi_hit_time_20[ev] = digi_hits_20["time_20"]
        digi_hit_trigger_20[ev] = digi_hits_20["trigger_20"]

        digi_hits_3 = wcsim.get_digitized_hits_3()
        digi_hit_pmt_3[ev] = digi_hits_3["pmt_3"]
        digi_hit_charge_3[ev] = digi_hits_3["charge_3"]
        digi_hit_time_3[ev] = digi_hits_3["time_3"]
        digi_hit_trigger_3[ev] = digi_hits_3["trigger_3"]

        tracks = wcsim.get_tracks()
        track_id[ev] = tracks["id"]
        track_pid[ev] = tracks["pid"]
        track_start_time[ev] = tracks["start_time"]
        track_energy[ev] = tracks["energy"]
        track_start_position[ev] = tracks["start_position"]
        track_stop_position[ev] = tracks["stop_position"]
        track_parent[ev] = tracks["parent"]
        track_flag[ev] = tracks["flag"]

        triggers_20 = wcsim.get_triggers_20()
        trigger_time_20[ev] = triggers_20["time_20"]
        trigger_type_20[ev] = triggers_20["type_20"]

        triggers_3 = wcsim.get_triggers_3()
        trigger_time_3[ev] = triggers_3["time_3"]
        trigger_type_3[ev] = triggers_3["type_3"]

        event_id[ev] = ev
        root_file[ev] = infile

    np.savez_compressed(outfile,
                        event_id=event_id,
                        root_file=root_file,
                        pid=pid,
                        position=position,
                        direction=direction,
                        energy=energy,
                        digi_hit_pmt_20=digi_hit_pmt_20,
                        digi_hit_charge_20=digi_hit_charge_20,
                        digi_hit_time_20=digi_hit_time_20,
                        digi_hit_trigger_20=digi_hit_trigger_20,
                        digi_hit_pmt_3=digi_hit_pmt_3,
                        digi_hit_charge_3=digi_hit_charge_3,
                        digi_hit_time_3=digi_hit_time_3,
                        digi_hit_trigger_3=digi_hit_trigger_3,
                        true_hit_pmt_20=true_hit_pmt_20,
                        true_hit_time_20=true_hit_time_20,
                        true_hit_pos_20=true_hit_pos_20,
                        true_hit_start_time_20=true_hit_start_time_20,
                        true_hit_start_pos_20=true_hit_start_pos_20,
                        true_hit_parent_20=true_hit_parent_20,
                        true_hit_pmt_3=true_hit_pmt_3,
                        true_hit_time_3=true_hit_time_3,
                        true_hit_pos_3=true_hit_pos_3,
                        true_hit_start_time_3=true_hit_start_time_3,
                        true_hit_start_pos_3=true_hit_start_pos_3,
                        true_hit_parent_3=true_hit_parent_3,
                        track_id=track_id,
                        track_pid=track_pid,
                        track_start_time=track_start_time,
                        track_energy=track_energy,
                        track_start_position=track_start_position,
                        track_stop_position=track_stop_position,
                        track_parent=track_parent,
                        track_flag=track_flag,
                        trigger_time_20=trigger_time_20,
                        trigger_type_20=trigger_type_20,
                        trigger_time_3=trigger_time_3,
                        trigger_type_3=trigger_type_3
                        )
    del wcsim


if __name__ == '__main__':

    config = get_args()
    if config.output_dir is not None:
        print("output directory: " + str(config.output_dir))
        if not os.path.exists(config.output_dir):
            print("                  (does not exist... creating new directory)")
            os.mkdir(config.output_dir)
        if not os.path.isdir(config.output_dir):
            raise argparse.ArgumentTypeError("Cannot access or create output \
                                             directory" + config.output_dir)
    else:
        print("output directory not provided... output files will be in same \
               locations as input files")

    file_count = len(config.input_files)
    current_file = 0

    for input_file in config.input_files:
        if os.path.splitext(input_file)[1].lower() != '.root':
            print("File " + input_file + " is not a .root file, skipping")
            continue
        input_file = os.path.abspath(input_file)

        if config.output_dir is None:
            output_file = os.path.splitext(input_file)[0] + '.npz'
        else:
            output_file = os.path.join(config.output_dir, 
                    os.path.splitext(os.path.basename(input_file))[0] + '.npz')

        print("\nNow processing " + input_file)
        print("Outputting to " + output_file)

        dump_file(input_file, output_file)

        current_file += 1
        print("Finished converting file " + output_file + " (" + str(current_file)
               + "/" + str(file_count) + ")")

    print("\n=========== ALL FILES CONVERTED ===========\n")
