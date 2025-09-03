import os
import h5py
import numpy as np 
import hdf5plugin

path = '/dataSATA/data_synchrotron/esrf_id13_2024_05_ch7039_enthesisII/20240501/PROCESSED_DATA/INTEG/cement_pmma/'
# '/dataSATA/data_synchrotron/esrf_id13_2023_09_ihmi1513_biomorphs/ihmi1531/id13/20230914/PROCESSED_DATA/integ/coral_s3/'
# '/dataSATA/data_synchrotron/esrf_id13_2023_09_ihmi1513_biomorphs/ihmi1531/id13/20230914/PROCESSED_DATA/integ/helix_s7'
#'/dataSATA/data_synchrotron/esrf_id13_2024_05_ch7039_enthesisII/20240501/PROCESSED_DATA/INTEG/helix_nuc1/'
#'/dataSATA/data_synchrotron/esrf_id13_2023_09_ihmi1513_biomorphs/ihmi1531/id13/20230914/PROCESSED_DATA/integ/sx_worm/'
# '/dataSATA/data_synchrotron/esrf_id13_2024_2_enthesis/20240215/PROCESSED_DATA/biomorph_blobb/'
#'/dataSATA/data_synchrotron/esrf_id13_2024_2_enthesis/20240215/PROCESSED_DATA/biomorph_leaf/'
file_in = 'analysis/rec_1d/reconstruction_1Dmm_coral_s3_2024_12_03_17h53.h5'
file_out = file_in[:-3]+'_compressed.h5'
model = 'analysis/tomo.h5'

with h5py.File(os.path.join(path,model), 'r') as hf:
    mask = hf['mask_voxels'][()]
    nvox = hf['nVox'][()]
mask_voxels = np.zeros(np.prod(nvox), bool)
mask_voxels[mask] = True 
mask_voxels = mask_voxels.reshape(nvox)

with h5py.File(os.path.join(path,file_in), 'r') as hf_in:
    with h5py.File(os.path.join(path,file_out), 'w') as hf_out:
        hf_out.create_dataset('data', data = hf_in['tomogram'][()], compression=hdf5plugin.LZ4())
        hf_out.create_dataset('mask_voxels', data=mask_voxels, compression=hdf5plugin.LZ4())
        hf_out.create_dataset('radial_units', data=hf_in['radial_units'][()], compression=hdf5plugin.LZ4())