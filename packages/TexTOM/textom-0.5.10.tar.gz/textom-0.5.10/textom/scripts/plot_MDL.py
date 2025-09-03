import numpy as np
import h5py
import os
import matplotlib.pyplot as plt
from pathlib import Path

def list_newest_files(folder, num_files=5):
    """
    Lists the newest files in a folder based on modification time.

    Parameters:
    folder (str): Path to the folder.
    num_files (int): Number of newest files to list (default: 5).

    Returns:
    list: A list of the newest filenames, sorted by modification time (newest first).
    """
    folder_path = Path(folder)

    # Ensure the folder exists
    if not folder_path.is_dir():
        raise ValueError(f"The specified folder does not exist: {folder}")

    # Get all files in the folder with their modification times
    files = [
        (file, file.stat().st_mtime) for file in folder_path.iterdir() if file.is_file()
    ]

    # Sort files by modification time (newest first)
    files_sorted = sorted(files, key=lambda x: x[1], reverse=True)

    # Extract the filenames of the newest files
    newest_files = [file[0].name for file in files_sorted[:num_files]]

    return newest_files

path = '/dataSATA/data_synchrotron/esrf_id13_2024_05_ch7039_enthesisII/20240501/PROCESSED_DATA/INTEG/cement_pmma/analysis/fits/'
MDL, nmax = [],[]
for file in list_newest_files(path, 5):
    with h5py.File(os.path.join(path,file), 'r') as hf:
        MDL.append(hf['MDL'][()])

    i0 = file.find('nmax')
    i1 = file.find('_', i0)
    nmax.append( int( file[i0+4 : i1] ) )

plt.plot(nmax, MDL)
plt.xlabel('HSH order')
plt.ylabel('MDL')
plt.show()