import numpy as np
import os
import sys
import shutil
import importlib
from numba import njit
import inspect
from datetime import datetime
import sys
import time
import re
import glob

from .handle import get_file_path
from ..version import __version__
from ..config import fun_mode

crystal_ascii = r"""
    ____     ____  
   /\   \   /\   \ 
  /__\___\ /__\___\
  \  / TexTOM /   /
   \/___/   \/___/ 
"""

def fancy_title():
    # # Clear the terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    if fun_mode:
        intro = add_phrase_to_crystal()
    else:
        intro = crystal_ascii

    # Display the title gradually as an animation
    for char in intro:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.0011)  # Adjust the speed of the animation
    time.sleep(0.03)
    # Add a final message
    print("\n\nWelcome to TexTOM!")
    print("====================================")
    print("A program for texture simulations.")
    print("\u00A9 Moritz Frewein, Moritz Stammer, Marc Allain, Tilman Gr\u00FCnewald.")
    print(f"Version {__version__}")
    print("====================================")
    time.sleep(0.05)

def add_phrase_to_crystal():
    line = read_phrase()
    words = line.split(' ')
    line1 = ' '.join(words[:len(words)//2])
    line2 = ' '.join(words[len(words)//2:])
    cr = crystal_ascii.split('\n')
    cr[2] = cr[2] + '    | ' + '-'*max(len(line1),len(line2))
    cr[3] = cr[3] + '    | ' + line1
    cr[4] = cr[4] + '    | ' + line2
    cr[5] = cr[5] + '    | ' + '-'*max(len(line1),len(line2))
    return '\n'.join(cr)

def read_phrase():
    phrases_path = get_file_path('textom',
            os.path.join('ressources','wise_phrases.txt') )
    with open(phrases_path) as fid:
        lines = fid.readlines()
    return lines[np.random.randint(len(lines))][:-1]

# Numba-compatible functions
@njit()
def sparsemult(sparsearray, indices, vector):
    """ Vector product using one custom sparse-array

    Parameters
    ----------
    sparsearray : ndarray, float
        list of the non-zero entries
    indices : ndarray, int
        indices of the non-zero entries
    vector : ndarray, float
        conventional vector
    
    returns: 
    ------------
    sum : float
    """
    sum = 0
    for i,S in zip(indices, sparsearray):
        sum += vector[i] * S
    return sum

@njit()
def integrate_c(sparsearray, indices, C ):
    """ Sparse-multiplication for several entries at once 

    Parameters
    ----------
    sparsearray : ndarray, float
        list of the non-zero entries
    indices : ndarray, int
        indices of the non-zero entries
    C : 2D ndarray, float
        conventional array
        dim 0: to be summed over, 1: whatever
    
    returns: 
    ------------
    c_int : ndarray float
        vector product for every entry in dim 1 of C
    """
    c_int = np.zeros( C.shape[1], C.dtype)
    for i in range(indices.shape[0]):
        idx = indices[i]
        c_int += C[idx] * sparsearray[i] # get weighted average hsh-coefficients
    return c_int

@njit()
def meshgrid(x, y):
    """Numpy-like meshgrid function that is compatible with numba

    Parameters
    ----------
    x,y : ndarray, float

    returns: 
    ------------
    xx,yy : 2D ndarray, float
    """
    xx = np.empty(shape=(y.size, x.size), dtype=x.dtype)
    yy = np.empty(shape=(y.size, x.size), dtype=y.dtype)
    for j in range(y.size):
        for k in range(x.size):
            xx[j,k] = x[k]  # change to x[k] if indexing xy
            yy[j,k] = y[j]  # change to y[j] if indexing xy
    return xx, yy

@njit()
def erf(x):
    ''' gives a numeric approximation of the error-function '''
    # save the sign of x
    sign = np.sign(x)
    x = np.abs(x)

    # constants
    a1 =  0.254829592
    a2 = -0.284496736
    a3 =  1.421413741
    a4 = -1.453152027
    a5 =  1.061405429
    p  =  0.3275911

    # A&S formula 7.1.26
    t = 1.0/(1.0 + p*x)
    y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*np.exp(-x*x)
    return sign*y # erf(-x) = -erf(x)

def idx_nearest(array,value):
    ''' finds the index of the entry closest to value in a sorted array
    '''
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (
        idx == len(array) or np.abs(value - array[idx-1]) < np.abs(value - array[idx])):
        return idx-1
    else:
        return idx

def cp_addno(source_file, destination_folder):
    """ copies a file to destination. if a file with the same
    name exits, adds a number to the name"""
    # Check if the source file exists
    if not os.path.isfile(source_file):
        print("Source file does not exist.")
        return

    # Get the filename and extension
    filename, extension = os.path.splitext(os.path.basename(source_file))

    # Prepare the destination path
    destination_file = os.path.join(destination_folder, os.path.basename(source_file))

    # If the file exists at the destination, add a number to the filename
    if os.path.exists(destination_file):
        index = 1
        while True:
            new_filename = f"{filename}_{index}{extension}"
            new_destination_file = os.path.join(destination_folder, new_filename)
            if not os.path.exists(new_destination_file):
                destination_file = new_destination_file
                break
            index += 1

    # Copy the file to the destination
    shutil.copyfile(source_file, destination_file)
    print(f"File copied to: {destination_file}")

def cp_add_dt(source_file, destination_folder, now=True):
    """ copies a file to destination and attaches a timestamp in the title"""
    # Check if the source file exists
    if not os.path.isfile(source_file):
        print("Source file does not exist.")
        return

    os.makedirs( destination_folder, exist_ok=True )

    # Get the filename and extension
    filename, extension = os.path.splitext(os.path.basename(source_file))
    # choose between current time and file modification time
    dt = timestring() if now else timestring(source_file) 
    # Prepare the destination path
    destination_file = os.path.join(destination_folder, 
                            f'{filename}_{dt}{extension}')

    # Copy the file to the destination
    shutil.copyfile(source_file, destination_file)
    print(f"File copied to: {destination_file}")

def import_module_from_path(module_name, file_path):
    # Create a module spec from the file path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    
    # Create a new module based on the spec
    module = importlib.util.module_from_spec(spec)
    
    # Add the module to the system modules
    sys.modules[module_name] = module
    
    # Execute the module in its own namespace
    spec.loader.exec_module(module)
    
    return module

def print_library_functions_and_docstrings(module, filter='', sort_alphabetical=False):
    """
    Prints all functions of a library and the first line of their docstrings.

    Parameters:
    module (module): The library module to inspect.
    filter (str): Optional filter to only show functions containing this substring.
    sort_alphabetical (bool): If True, functions are printed in alphabetical order.
                              If False, functions are printed in the order they appear in the library.
    """  
    print('Available methods:')
    # Retrieve all functions in the module, including imported ones
    functions = [
        (name, obj) for name, obj in ((name, getattr(module, name)) for name in dir(module))
        if inspect.isfunction(obj) and name[0] != '_' and filter in name
        and inspect.getmodule(obj) == module
    ]
    # functions = [
    #     (name, obj) for name, obj in inspect.getmembers(module)
    #     if inspect.isfunction(obj) and name[0] != '_' and filter in name
    # ]
    # # Determine the order of functions based on source code if sort_alphabetical is False
    # if not sort_alphabetical:
    #     try:
    #         source = inspect.getsource(module)
    #         function_order = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', source)
    #         function_order = [name for name in function_order if filter in name]
    #         functions_dict = dict(functions)
    #         functions = [(name, functions_dict[name]) for name in function_order if name in functions_dict]
    #     except (OSError, TypeError):
    #         print("Could not retrieve source code. Showing in alphabetical order.")
    
    # Sort functions alphabetically if sort_alphabetical is True
    if sort_alphabetical:
        functions = sorted(functions, key=lambda x: x[0])

    # Print function names and their first docstring line
    for name, obj in functions:
        docstring = inspect.getdoc(obj)
        first_line = docstring.split('\n')[0] if docstring else 'No docstring available'
        print(f"\t{name} : {first_line}")

def list_library_functions(module):
    """
    Lists all functions of a library.

    Parameters:
    module (module): The library module to inspect.

    Returns:
    List[str]: A list of function names in the module.
    
    Example:
    functions = list_library_functions(numpy)
    print(functions)
    """
   
    # Initialize an empty list to store function names
    function_names = []
    
    # Iterate through the members of the module
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            # Append the function name to the list
            function_names.append(name)
    
    return function_names

def print_function_docstring(module, function_name):
    """
    Prints the docstring of a specified function in a module.

    Parameters:
    module (module): The library module to inspect.
    function_name (str): The name of the function whose docstring is to be printed.
    
    Example:
    print_function_docstring(math, 'sqrt')
    """
   
    # Get the function object from the module
    function = getattr(module, function_name, None)
    
    if function and inspect.isfunction(function):
        # Get the docstring of the function
        docstring = inspect.getdoc(function)
        if docstring:
            print(f"Function {function_name}:\n{docstring}")
        else:
            print(f"No docstring available for {function_name}.")
    else:
        print(f"{function_name} is not a valid function in the given module.")

def timestring( file_path=None ):
    """Makes a timestamp string for convenient for saving data

    If given a filepath, takes the modification datetime, else the current moment
    
    Parameters
    ----------
    file_path : str
    
    Returns
    -------
    str
        timestamp e.g. '2024_11_22_15h37'
    """
    if file_path:
        dt = datetime.fromtimestamp( os.path.getmtime(file_path) )
    else:
        dt = datetime.now()
    return str(dt).replace(' ','_').replace('-','_').replace(':','h')[:-10]

def lastfile( path, filter='*' ):
    """Searches for the youngest file in the path an returns the name

    Parameters
    ----------
    path : str
        directory containing the files
    filter : str
        searches for all file corresponding to pattern, by default '*'

    Returns
    -------
    str
        name of the youngest file
    """
    search_pattern = os.path.join( path, filter )
    h5_files = glob.glob(search_pattern)
    if any(h5_files):
        h5path = max(h5_files, key=os.path.getmtime)
        return h5path
    else:
        print('No files found')

def crop_to_non_nan_region(array):
    """
    Crop a 2D array to the smallest rectangular region that contains no NaN values.
    
    Parameters:
    - array: 2D numpy array with potential NaN values.
    
    Returns:
    - Cropped 2D numpy array containing only the region with no NaNs.
    """
    # Find the indices of non-NaN values
    non_nan_rows = np.any(~np.isnan(array), axis=1)
    non_nan_cols = np.any(~np.isnan(array), axis=0)
    
    # Get the bounding box for rows and columns
    row_start, row_end = np.where(non_nan_rows)[0][[0, -1]]
    col_start, col_end = np.where(non_nan_cols)[0][[0, -1]]
    
    # Crop the array to the non-NaN region
    cropped_array = array[row_start:row_end+1, col_start:col_end+1]
    
    return cropped_array, [row_start, row_end, col_start, col_end]

def smallest_subvolume(field):
    """
    Finds the smallest subvolume containing all nonzero vectors in a 3D field or vector field.

    Parameters:
    field (np.ndarray): A 3D or 4D array of shape (nx, ny, nz, 3), where the last dimension
                        represents the vector components (x, y, z).

    Returns:
    tuple: (sliced_field, slices), where:
        - sliced_field is the smallest subvolume containing all nonzero vectors.
        - slices is a tuple of slice objects for the original array.
    """
    # Check for nonzero vectors
    if field.ndim == 4:
        nonzero_mask = np.any(field != 0, axis=-1)  # True for nonzero vectors
    elif field.ndim == 3:
        nonzero_mask = ~np.isnan(field) & (field != 0)

    # Find the bounds along each axis
    nonzero_indices = np.where(nonzero_mask)
    x_min, x_max = np.min(nonzero_indices[0]), np.max(nonzero_indices[0])
    y_min, y_max = np.min(nonzero_indices[1]), np.max(nonzero_indices[1])
    z_min, z_max = np.min(nonzero_indices[2]), np.max(nonzero_indices[2])

    # Define slices for the subvolume
    slices = (slice(x_min, x_max + 1), slice(y_min, y_max + 1), slice(z_min, z_max + 1))

    # Extract the subvolume
    subvolume = field[slices]

    return subvolume, [x_min,x_max,y_min, y_max,z_min, z_max]

def find_indices_in_range(array, value_range):
    """
    Finds the index range of entries in a 1D array within a specified range.

    Parameters:
    array (np.ndarray): A 1D array with steadily increasing values.
    value_range (tuple): A tuple (lower, upper) specifying the range of values.

    Returns:
    tuple: (lower_index, upper_index), where:
        - lower_index is the index of the first value >= lower.
        - upper_index is the index of the first value >= upper.
    """
    lower, upper = value_range

    # Use searchsorted to find insertion indices
    lower_index = np.searchsorted(array, lower, side='left')
    upper_index = np.searchsorted(array, upper, side='right')# - 1

    # Ensure indices are within bounds
    if lower_index >= len(array) or array[lower_index] < lower:
        lower_index = -1  # No valid lower index
    if upper_index < 0 or array[upper_index-1] > upper:
        upper_index = -1  # No valid upper index

    return lower_index, upper_index

def list_files_by_modification_time(directory, reverse=False, extension=None):
    """
    List all files in a directory ordered by modification time, optionally filtered by file extension.

    Parameters:
    directory (str): Path to the directory.
    reverse (bool): If True, list files from newest to oldest. Default is False (oldest to newest).
    extension (str): Optional file extension to filter by (e.g., '.txt'). Default is None (no filtering).

    Returns:
    list: A list of filenames in the directory, ordered by modification time and filtered by extension if provided.
    """
    # Get all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    # Filter by extension if provided
    if extension:
        files = [f for f in files if f.lower().endswith(extension.lower())]
    
    # Sort files by modification time
    files_sorted = sorted(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=reverse)
    
    return files_sorted

def insert_sparse_tomogram( dimensions, mask, values ):
    """ Makes a 3D tomogram out of sparse data
    """
    try:
        tomogram = np.empty( (dimensions.prod(),values.shape[1]), np.float64 )
        tomogram[:] = np.nan
        tomogram[mask] = values
        tomogram = tomogram.reshape((*dimensions, values.shape[1]))
    except:
        tomogram = np.empty( dimensions.prod(), np.float64 )
        tomogram[:] = np.nan
        tomogram[mask] = values
        tomogram = tomogram.reshape(dimensions)
    return tomogram

def is_running_in_jupyter():
    """
    Checks if the code is running inside a Jupyter notebook.
    Returns:
        bool: True if running in Jupyter, False otherwise.
    """
    try:
        from IPython import get_ipython
        if 'ipykernel' in sys.modules and isinstance(get_ipython(), type(None)) == False:
            return True
    except ImportError:
        pass
    return False