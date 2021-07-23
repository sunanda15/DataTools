# Copied from Nick Prouse's git repo

import argparse
import h5py
import numpy as np

def get_args():
    parser = argparse.ArgumentParser(description='merge hdf5 files with common datasets by concatenating them together')
    parser.add_argument('input_files', type=str, nargs='+')
    parser.add_argument('-o', '--output_file', type=str)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    config = get_args()
    print("output file:", config.output_file)
    out_file = h5py.File(config.output_file, 'w')
    infiles = [h5py.File(f, 'r') for f in config.input_files]
    print(f"opened input file {infiles[0].filename}")
    keys = infiles[0].keys()
    attr_keys = infiles[0].attrs.keys()
    for f in infiles[1:]:
        print(f"opened and checking input file {f.filename}")
        if f.keys() != keys:
            raise KeyError(f"HDF5 file {f.filename} keys {f.keys()} do" +
                            " not match first file's keys {keys}.")
        if f.attrs.keys() != attr_keys:
            raise KeyError(f"HDF5 file {f.filename} attributes" +
                            " {f.attrs.keys()} do not match first" +
                            " file's attributes {attr_keys}.")
    for k in attr_keys:
        out_file.attrs[k] = np.hstack([f.attrs[k] for f in infiles]).tolist()
    for k in keys:
        dtype = infiles[0][k].dtype
        shape = list(infiles[0][k].shape)
        for f in infiles[1:]:
            shape[0] += f[k].shape[0]
            if shape[1:] != list(f[k].shape[1:]):
                raise ValueError(f"Array {k} in {f.filename} has shape" +
                                  " {f[k].shape} which is incompatible with" +
                                  " extending previous files shape {shape}.")
        print(f"writing {k}, shape {shape}, dtype {dtype}")
        dset = out_file.create_dataset(k, shape=shape, dtype=dtype)
        isIndex_20 = False
        isIndex_3  = False
        # the following part needs to be different for 20" and 3"
        if k == "event_hits_index_20":
            isIndex_20 = True
            offset_20 = 0
            print("  is an 20in PMT index array, so adding length of" + 
                  " hit_pmt_20 array in each file to the index values of" +
                  " the following file")
        elif k == "event_hits_index_3":
            isIndex_3 = True
            offset_3 = 0
            print("  is an 3in PMT index array, so adding length of" + 
                  " hit_pmt_3 array in each file to the index values of" +
                  " the following file")
        start = 0
        for f in infiles:
            stop = start+f[k].shape[0]
            print(f"  entries {start}:{stop} from file {f.filename}")
            if isIndex_20:
                dset[start:stop] = np.array(f[k]) + offset_20
                offset_20 += f['hit_pmt_20'].shape[0]
                print("The length of this hit_pmt_20 is: ", f['hit_pmt_20'].shape[0])
                print("offset_20: ", offset_20)
            elif isIndex_3:
                dset[start:stop] = np.array(f[k]) + offset_3
                offset_3 += f['hit_pmt_3'].shape[0]
                print("The length of this hit_pmt_3 is: ", f['hit_pmt_3'].shape[0])
                print("offset_3: ", offset_3)
            else:
                dset[start:stop] = f[k]
            start = stop
    print(f"Written output file {out_file.filename}.")
    out_file.close()