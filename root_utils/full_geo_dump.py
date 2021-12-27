from root_utils.root_file_utils import *
import argparse
import numpy as np

ROOT.gROOT.SetBatch(True)

# number of 3" PMTs in the mPMT
mPMT_unit = 19

def get_args():
    parser = argparse.ArgumentParser(description='dump geometry data from WCSim\
        into numpy .npz file')
    parser.add_argument('input_file', type=str)
    parser.add_argument('output_file', type=str, default=None, nargs='?')
    parser.add_argument('hybrid_store_method', type=int, default=0, nargs='?', 
        help='Choose the geo storage method you want for HybridHK:\n \
        0 - info of two types of PMTs stored separately\n \
        1 - both PMT info stored together with an additional array indicating \
        PMT type')
    args = parser.parse_args()
    return args


def geodump(input_file, output_file, hybrid_store_method):
    '''
    There are two options for storing HybridHK PMT geometry:
    0 - info of two types of PMTs stored separately
    1 - both PMT info stored together with an additional array indicating PMT 
    type (default)
    '''

    print("input file:", input_file)
    print("output file:", output_file)
    if hybrid_store_method == 0:  # method 0
        print("HybridHK geo of two types of PMTs stored separately.")
    else:  # method 1
        print("HybridHK geo of two types of PMTs stored together.")

    file = WCSimFile(input_file)

    geo = file.geo

    num_pmts_20 = geo.GetWCNumPMT(0)
    num_pmts_3  = geo.GetWCNumPMT(1)

    tube_no_20 = np.zeros(num_pmts_20, dtype=int)
    position_20 = np.zeros((num_pmts_20, 3))
    orientation_20 = np.zeros((num_pmts_20, 3))

    tube_no_3 = np.zeros(num_pmts_3, dtype=int)
    mPMT_no = np.zeros(num_pmts_3, dtype=int)
    position_3 = np.zeros((num_pmts_3, 3))
    orientation_3 = np.zeros((num_pmts_3, 3))

    for i in range(num_pmts_20):
        pmt = geo.GetPMT(i, 0)
        tube_no_20[i] = pmt.GetTubeNo()
        for j in range(3):
            position_20[i][j] = pmt.GetPosition(j)
            orientation_20[i][j] = pmt.GetOrientation(j)

    for i in range(num_pmts_3):
        pmt = geo.GetPMT(i, 1)
        tube_no_3[i] = pmt.GetmPMT_PMTNo()
        mPMT_no[i] = pmt.GetmPMTNo()
        for j in range(3):
            position_3[i][j] = pmt.GetPosition(j)
            orientation_3[i][j] = pmt.GetOrientation(j)

    # method 0
    if hybrid_store_method == 0:
        np.savez_compressed(output_file, tube_no_20=tube_no_20, 
          position_20=position_20, orientation_20=orientation_20, 
          tube_no_3=tube_no_3, mPMT_no=mPMT_no, position_3=position_3,
          orientation_3=orientation_3)

    # method 1
    else:
        tube_no = np.concatenate((tube_no_20,tube_no_3), axix=0)
        position = np.concatenate((position_20, position_3), axis=0)
        orientation = np.concatenate((orientation_20,orientation_3),axis=0)
        type_change_index =  num_pmts_20 # 0 for 20", 1 for 3"

        np.savez_compressed(output_file, tube_no=tube_no, position=position, 
            orientation=orientation, type_change_index=type_change_index)

if __name__ == '__main__':
    ROOT.gSystem.Load(os.environ['WCSIMDIR'] + "/libWCSimRoot.so")
    config = get_args()

    if os.path.splitext(config.input_file)[1].lower() != '.root':
        print("File " + config.input_file + " is not a .root file")
        exit(1)
    input_file = os.path.abspath(config.input_file)

    if config.output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.geo.npz'
        print("Output file not set, using", output_file)
    else:
        output_file = os.path.abspath(config.output_file)

    if config.hybrid_store_method is None:
        hybrid_store_method = 0
        print("Storing method not set, using default method (0) - \
               store all info separately")
    else:
        hybrid_store_method = config.hybrid_store_method

    geodump(input_file, output_file, hybrid_store_method)
