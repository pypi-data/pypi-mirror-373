import numpy as np
import glob
import importlib as imp
import h5py
import os
from time import time 
import sys
import shutil
import os
import subprocess

''' Library for handling input and output'''

def copy_folder_contents(source_folder, destination_folder):
    ''' copies everything from source to destination '''
    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Iterate over all files and subdirectories in the source folder
    for item in os.listdir(source_folder):
        source_item = os.path.join(source_folder, item)
        destination_item = os.path.join(destination_folder, item)

        # Check if the item is a file
        if os.path.isfile(source_item):
            # Skip if the file already exists in the destination folder
            if not os.path.exists(destination_item):
                shutil.copy2(source_item, destination_item)
                print(f"\tCopied: {item}")
            else:
                print(f"\tSkipped (File already exists): {item}")

        # Check if the item is a subdirectory
        elif os.path.isdir(source_item):
            # Recursively copy the subdirectory
            copy_folder_contents(source_item, destination_item)

""" 
Handle internal files
"""
def save_projections(images, rotation, path):
    dirpath = path.split('/')[0:-1]
    dir = '/'.join(dirpath)
    if os.path.isdir(dir) == False:
        os.mkdir(dir)
        print('Created path')
    h5id = h5py.File(path,'w')
    for g in range(images.shape[0]):
        dset = h5id.create_dataset( "proj"+str(g).zfill(3), images[g,:,:].shape, 'f')
        dset[:,:] = images[g,:,:]
        dset.attrs['rotation'] = rotation[g]
    print('saved projections to file: ' + path)

def load_projections(path, shape):
    images = np.empty(shape)
    rot = []
    with h5py.File(path,'r') as hf:
        sets = list(hf.keys())
        for g in range(shape[0]):
            for t in range(shape[1]):
                images[g,t,:] = hf[sets[g]][t]
            rot.append( hf[sets[g]].attrs['rotation'] )
    print('loaded data from file: ' + path)
    return images, rot

def save_coefficients( C, mod, path = 'output/sample.txt' ):
    ## writes into output/sample.txt
    # one line per voxel:
    # index, coordinates, overall scaling A, isotropic part U, sHSH coefficients cs
    px = 1 # spatial precision
    pc = 6 # coefficient precision

    os.makedirs('output', exist_ok=True) 
    fid  = open( path, 'w') 
    fid.write('i\t x\t y\t z\t c\n')
    for ivox in range( mod.x_p.shape[0] ):
        fid.write('{:.0f}\t{:.{px}f}\t{:.{px}f}\t{:.{px}f}'.format(
            ivox, *mod.x_p[ivox], px=px, pc=pc))
        for c in C[ivox]:
            fid.write('\t{:.{pc}f}'.format(
                c, pc=pc)) 
        fid.write('\n')
    fid.close()
    print('saved parameters to file: ' + path)

def load_coefficients( path ):
    t0 = time()
    data = np.genfromtxt(path, skip_header=1)
    C = data[:,4:]
    print('loaded parameters from file (%.2f s): %s' % (time()-t0, path)) 
    return C

"""
Functions handling X-ray data
"""

def load_data( path, n ):
    with h5py.File(path,'r') as hf:
        q = hf['radial_units'][0]
        phi = hf['azimuthal_units'][0]
        data = hf['cake_integ'][n]
    return q, phi, data

def load_mat_proj( path ):
    ''' Loads a file from SASTT alignment
    
    Parameters
    ----------
    path : str

    Return values
    ------------
    kappa, omega: 1D ndarray, float
        tilt and rotation angle
    shiftx, shiftz : 1D ndarray, float
        shifts of projections for alignment
    air_scat : 1D ndarray, float
        intensity correction from air scattering
    tomogram : 1D ndarray, float
        resulting tomogram from SASTT
    '''
    f = h5py.File(path,'r')
    n_proj = f['projection/dx'][()].shape[0]
    kappa = np.array([ f[f.get('projection/rot_x')[k][0]][0][0] for k in range(n_proj) ])
    omega = np.array([ f[f.get('projection/rot_y')[k][0]][0][0] for k in range(n_proj) ])
    shiftx = np.array([ f[f.get('projection/dx')[k][0]][0][0] for k in range(n_proj) ])
    shiftz = np.array([ f[f.get('projection/dy')[k][0]][0][0] for k in range(n_proj) ])
    # filename = np.array([ f[f.get('projection/todo_list')[k][0]][0][0] for k in range(n_proj) ])
    # pad = np.array([ f[f.get('projection/pad')[k][0]][0][0] for k in range(n_proj) ])
    air_scat = np.array([ f[f.get('projection/air_scattering')[k][0]][0][0] for k in range(n_proj) ])
    tomogram = np.array(f.get('tomogram'))
    return kappa, omega, shiftx, shiftz, air_scat, tomogram

def load_shifts_mumott( path ):
    ''' Loads a file from Mumott alignment
    
    Parameters
    ----------
    path : str

    Return values
    ------------
    kappa, omega: 1D ndarray, float
        tilt and rotation angle
    shiftx, shiftz : 1D ndarray, float
        shifts of projections for alignment
    air_scat : 1D ndarray, float
        intensity correction from air scattering
    tomogram : 1D ndarray, float
        resulting tomogram from SASTT
    '''
    with h5py.File(path,'r') as hf:
        kappa = hf['kappa'][()]
        omega = hf['omega'][()]
        shifty = hf['shifts'][()][:,0]
        shiftz = hf['shifts'][()][:,1]
        # air_scat = np.array([ f[f.get('projection/air_scattering')[k][0]][0][0] for k in range(n_proj) ])
        tomogram = hf['tomogram'][()]
        sinogram = hf['sinogram'][()]
    return kappa, omega, shifty, shiftz, tomogram, sinogram

def get_filelist( dat ):
    kappa, omega, _, _, _, _ = load_mat_proj(dat.shifts)
    kapstr = [('%d'%k).replace('-','m') for k in kappa]
    omestr = [('%08.2f'%o).replace('.','p') for o in omega]
    nameref = ['_%s_%s_'%(k,o) for k,o in zip(kapstr,omestr)]

    filenames = np.array( next(os.walk(dat.datapath), (None, None, []))[2] ) # [] if no file

    filelist = []
    missing = []
    duplicates = []
    for nam in nameref:
        match = [str(s) for s in filenames if nam in s]
        # match = next((str(s) for s in filenames if nam in s), None) # this is faster but only gives the first find!
        if (len(match) == 0):
            missing.append(nam)
        elif (len(match) >1 ):
            duplicates.append(match)
        else:
            filelist.append(match)

    print('\t Loaded filelist and compared with input')
    print('\t\t missing: %d' % len(missing) )
    [print(miss) for miss in missing]
    print('\t\t duplicates: %d' % len(duplicates) )
    [print(dupl) for dupl in duplicates]

    # this moves duplicates to a different folder
    # path_dupl = os.path.normpath(path)+'_duplicatesele/'
    # os.makedirs( path_dupl, exist_ok=True)
    # for dupl in duplicates:
    #     os.rename(path+dupl[1], path_dupl+dupl[1])

    return filelist

def get_list_opt( path ):

    lst = []
    with open(path, 'r') as fid:
        lines = fid.readlines()    

    for line in lines:
        file = line.strip()
        i0 = file.find('nmax')
        i1 = file.find('_', i0)
        nmax = int( file[i0+4 : i1] )
        lst.append([file, nmax])
    return(lst)

def make_list_proj( basedir, listname, exclude):
    """
    Example input
    basedir = '/dataSATA/data_synchrotron/esrf_id13_2023_09_ihmi1513_biomorphs/ihmi1531/id13/20230914/RAW_DATA/helix_s7/'
    listname = 'data/list_helix_s7.txt'
    exclude = ['_a_','_b_','_c_',]
    """

    dirs = [x[0].split('/')[-1] for x in os.walk(basedir)]
    dirs_data, kappa, omega = [], [], []
    omega = []
    for dir in dirs:
        ex = [k in dir for k in exclude]
        if any(ex):
            continue
        if dir[-4:]=='diff':
            angles_str = dir.split('_')[-3:-1]
            kap = float(angles_str[0].replace('m','-'))
            ome = float(angles_str[1].replace('p','.'))


            kappa.append(kap)
            omega.append(ome)
            dirs_data.append(dir)
    kappa, omega = np.array(kappa), np.array(omega)

    fid  = open( listname, 'w') 
    fid.write(basedir)
    fid.write('\n kap\t ome\t file\t duplicate')

    for kap in np.unique(kappa)[::-1]:
        ord_kap = np.where(kappa==kap)[0].tolist()
        ome_sub = omega[ ord_kap ]
        ord_ome = np.argsort( ome_sub ).tolist()
        files_sub = [dirs_data[i] for i in ord_kap]
        files_ord = [files_sub[i] for i in ord_ome]
        ome_ord = ome_sub[ord_ome]
        bool_dup = ome_ord[:-1]-ome_ord[1:]
        # bool_dup = np.logical_not( np.concatenate([bool_dup,[0,]]), np.concatenate([[0,],bool_dup]) )
        dup = [ '' if i else '*' for i in bool_dup ]
        dup.insert(0,'')

        for k in range(ome_ord.shape[0]):
            fid.write('\n %u \t %5.2f \t %s \t %s' %( kap, ome_ord[k], files_ord[k], dup[k] ))
        
    fid.close()

def load_list_proj( path ):

    kappa, omega, filenames = [], [], []

    with open(path, 'r') as f:
        content = f.readlines()

        path = content[0].strip()
        for line in content[2:]:
            values = line.strip().split()
            kappa.append(float(values[0]))
            omega.append(float(values[1]))
            filenames.append(values[2])
    
    return kappa, omega, filenames, path
            
def save_dict_to_h5(dict_data, h5_path):
    """
    Save all variables in a Python dictionary to an HDF5 file using h5py.

    Parameters:
    dict_data (dict): Dictionary containing the data to be saved. The values can be 
                      NumPy arrays, nested dictionaries, or other types (which will 
                      be converted to strings).
    h5_path (str): Name of the HDF5 file to save the data to.
    """
    def recursively_save_dict_contents_to_group(h5file, path, dict_data):
        """
        Recursively saves the contents of a dictionary to an HDF5 group.

        Parameters:
        h5file (h5py.File): The HDF5 file object.
        path (str): The current path within the HDF5 file.
        dict_data (dict): The dictionary to save.
        """
        for key, item in dict_data.items():
            if isinstance(item, list):
                item = np.array(item)
            if isinstance(item, (np.ndarray, np.generic)):
                # Save NumPy arrays directly
                h5file[path + key] = item
            elif isinstance(item, (int, float, str, bool)):
                # Save single numbers and strings directly
                h5file[path + key] = item
            elif isinstance(item, dict):
                # Recursively save nested dictionaries
                recursively_save_dict_contents_to_group(h5file, path + key + '/', item)
            else:
                # Convert other types to string before saving
                h5file[path + key] = str(item)

    os.makedirs( os.path.dirname(h5_path), exist_ok=True )

    # Open the HDF5 file in write mode
    with h5py.File(h5_path, 'w') as h5file:
        # Start the recursive saving process from the root path
        recursively_save_dict_contents_to_group(h5file, '/', dict_data)

# def create_h5_file(file_path, data_dict):
#     """
#     Create an HDF5 file from a dictionary of data.

#     Parameters:
#     file_path (str): Path to the HDF5 file to be created.
#     data_dict (dict): Dictionary containing data to be stored in the HDF5 file. The keys are dataset names, and the values are the dataset values.

#     Returns:
#     None
#     """
#     with h5py.File(file_path, 'w') as h5file:
#         for key, value in data_dict.items():
#             # Handle nested dictionaries
#             if isinstance(value, dict):
#                 group = h5file.create_group(key)
#                 for sub_key, sub_value in value.items():
#                     group.create_dataset(sub_key, data=sub_value)
#             else:
#                 h5file.create_dataset(key, data=value)

def load_h5_to_dict( h5_path ):
    """
    Read all contents of an HDF5 file into a Python dictionary.

    Parameters:
    h5_path (str): Path to the HDF5 file.

    Returns:
    dict: Dictionary containing all contents of the HDF5 file.
    """
    def recursive_read(group):
        result = {}
        for key, item in group.items():
            if isinstance(item, h5py.Dataset):
                result[key] = item[()]
            elif isinstance(item, h5py.Group):
                result[key] = recursive_read(item)
        return result

    with h5py.File(h5_path, 'r') as h5file:
        return recursive_read(h5file)

def copy_h5_except(source_file, dest_file, exclude_datasets):
    """
    Copies data from source HDF5 file to a new HDF5 file, excluding specified datasets.
    
    Parameters:
    source_file (str): Path to the source HDF5 file.
    dest_file (str): Path to the destination HDF5 file.
    exclude_datasets (list): List of dataset names to exclude from copying.
    """
    with h5py.File(source_file, 'r') as src, h5py.File(dest_file, 'w') as dst:
        def copy_items(name, obj):
            if name not in exclude_datasets:
                src.copy(name, dst)

        src.visititems(copy_items)

    
def write_xdmf_reader(reader_filename, paraview_filenames, shape, attributes, attr_type):
    '''
    - reader_filename: Name of the xdmf file to be written
    - paraview_filename: Name of the h5 file to be read by paraview
    - volume: Dictionary containing the data shape ordereed as X, Y, Z
    - attributes: List of attributes to pass to paraview (e.g., mean, doo, orientation, std)
    - attr_type: List of attribute types (e.g., Scalar, Vector)
    -------------------------------------------------------------------------------
    Author: Adrian Rodriguez-Palomo
    Last update: 2023-11-16
    Modified by Moritz frewein 2024-12-05
    -------------------------------------------------------------------------------
    '''

    if isinstance(paraview_filenames, str): # if it's just a name
        paraview_filenames = [paraview_filenames for _ in range(len(attributes))]
    elif len(paraview_filenames) == 1: # if it's a list with 1 entry
        paraview_filenames = [paraview_filenames[0] for _ in range(len(attributes))]
    
    if reader_filename[-5:] != '.xdmf':
        reader_filename = reader_filename + '.xdmf'

    # Definine volume shape
    Nx,Ny,Nz = shape[0], shape[1], shape[2]

    if len(attributes) != len(attr_type):
        raise ValueError('The number of attributes and attribute types must be the same')

    # Create the xdmf file
    f = open(reader_filename, 'w')
    
    # Header for xml file
    f.write('''<?xml version="1.0" ?>
    <!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>
    <Xdmf Version="2.0">
        <Domain>
            <Grid Name="Structured Grid" GridType="Uniform">
                <Topology TopologyType="3DCoRectMesh" NumberOfElements="%d %d %d"/>
            
                <Geometry GeometryType="Origin_DxDyDz">
                    <DataItem Name="Origin" Dimensions="3" NumberType="Float" Precision="4" Format="XML">
                        0 0 0
                    </DataItem>
            
                    <DataItem Name="Spacing" Dimensions="3" NumberType="Float" Precision="4" Format="XML">
                        1 1 1
                    </DataItem>
                </Geometry>'''%(Nx, Ny, Nz))
    
    # Write attributes
    for ii in range(len(attributes)):
        if paraview_filenames[ii][-3:] != '.h5':
            paraview_filenames[ii] = paraview_filenames[ii] + '.h5'

        if attr_type[ii] == 'Scalar':
            f.write('''\n
                <Attribute Name="%s" AttributeType="%s" Center="Node">
                    <DataItem Dimensions="%d %d %d" NumberType="Float" Precision="8" Format="HDF">
                        %s:/%s
                    </DataItem>
                </Attribute>'''%(attributes[ii], attr_type[ii], Nx, Ny, Nz, 
                                 os.path.basename(paraview_filenames[ii]), attributes[ii]))

        elif attr_type[ii] == 'Vector':
            f.write('''\n
                <Attribute Name="%s" AttributeType="%s" Center="Node">
                    <DataItem Dimensions="%d %d %d 3" NumberType="Float" Precision="8" Format="HDF">
                        %s:/%s
                    </DataItem>
                </Attribute>'''%(attributes[ii], attr_type[ii], Nx, Ny, Nz, 
                                 os.path.basename(paraview_filenames[ii]), attributes[ii]))
    
    # Write end of file
    f.write('''\n
            </Grid>
        </Domain>
    </Xdmf>''')
    
    # Close file
    f.close()
    print(f'Paraview linker file {reader_filename} written successfully')
#-----------------------------------------------------------------------------------------#

from importlib.resources import files

def get_file_path(package_name, filename):
    """Gets the file path of a file inside a package."""
    try:
        # Retrieve the file path
        package = files(package_name)
        file_path = package / filename
        return str(file_path)
    except Exception as e:
        print(f"Error retrieving file path: {e}")
        return None

def open_with_editor(filepath):
    """Opens the given file with the default text editor."""
    print(f"Opening file in editor: {os.path.basename(filepath)}")
    try:
        if os.name == 'nt':  # Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # macOS or Linux
            subprocess.call(["xdg-open", filepath])
            # editor = os.getenv('EDITOR', 'vi')  # Use the EDITOR env variable or fallback to 'vi'
            # subprocess.run([editor, filepath])
        else:
            raise OSError(f"Unsupported OS: {os.name}")
        input('\tPress enter when finished editing')
    except Exception as e:
        print(f"Failed to open the file: {e}")

import platform

def open_pdf(filepath):
    """Opens the given PDF file with the default PDF viewer."""
    try:
        if platform.system() == 'Windows':  # Windows
            os.startfile(filepath)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', filepath])
        elif platform.system() == 'Linux':  # Linux
            subprocess.Popen(['xdg-open', filepath])
        else:
            raise OSError(f"Unsupported platform: {platform.system()}")
    except Exception as e:
        print(f"Failed to open the PDF file: {e}")

# import h5py
# import multiprocessing as mp
# import numpy as np

# def read_file(file_path, dataset_name):
#     """Read data from a single HDF5 file."""
#     with h5py.File(file_path, 'r') as f:
#         data = f[dataset_name][:]
#     return data

# def parallel_read_files(file_paths, dataset_name, num_workers=4):
#     """Read multiple HDF5 files in parallel while respecting file order."""
#     with mp.Pool(processes=num_workers) as pool:
#         # Map file reading to workers
#         results = pool.starmap(read_file, [(file_path, dataset_name) for file_path in file_paths])
    
#     # Concatenate results while preserving the order of file_paths
#     combined_data = np.concatenate(results, axis=0)
#     return combined_data

# # Example usage
# if __name__ == '__main__':
#     file_paths = ['file1.h5', 'file2.h5', 'file3.h5']  # List of HDF5 file paths
#     dataset_name = '/path/to/dataset'
#     num_workers = 4  # Specify the number of parallel workers
    
#     combined_data = parallel_read_files(file_paths, dataset_name, num_workers=num_workers)
#     print("Combined data shape:", combined_data.shape)