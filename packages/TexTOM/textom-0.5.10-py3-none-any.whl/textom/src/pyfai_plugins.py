import os, glob
import fabio
import h5py
import pyFAI
from time import time, sleep
import numpy as np
from subprocess import Popen
import shutil
import re
import sys

from . import handle as hdl
from . import misc as msc
from . import exceptions as exc
from ..config import data_type
from ..input import integration_parameters

def setup_integration( sample_dir:str, confirm=True ):
    """Opens the integration_parameters.py file and saves it to sample_dir after modifying
    If such a file already exists, makes a backup and opens this one.

    Parameters
    ----------
    sample_dir : str
        textom base directory

    Returns
    -------
    dict
        parameters for pyfai integration for textom
    """
    # read and edit integration_parameters.py
    intpar_path_sample = os.path.join(sample_dir,'integration_parameters.py')
    if confirm:
        # check if there is already an integration file
        if not os.path.isfile( intpar_path_sample ):
            intpar_path_module = hdl.get_file_path('textom',os.path.join('input','integration_parameters.py'))
            hdl.open_with_editor(intpar_path_module) # take the one from the textom module
            shutil.copyfile(intpar_path_module, intpar_path_sample ) # copy to the sample directory
        else:
            msc.cp_add_dt(intpar_path_sample, sample_dir, now=False) # save the old version with modification date
            hdl.open_with_editor(intpar_path_sample) # edit and use the same file
    
    par = msc.import_module_from_path('integration_parameters', intpar_path_sample)
    print(f'\tSaved integration parameters to {sample_dir}') 

    generate_caked_detector_mask(sample_dir, par)
    return par

def generate_caked_detector_mask(sample_dir:str, par:integration_parameters):
    """Integrates the provided raw detector mask so that it can be used in textom

    Parameters
    ----------
    sample_dir : str
        textom base directory
    par : integration_parameters
        contains what is given in the integration_parameters.py module
    """
    os.makedirs(os.path.join( sample_dir, 'analysis'), exist_ok=True)
    path_mask = os.path.join( sample_dir, 'analysis', 'mask_detector_cake.h5' )
    if not os.path.isfile(path_mask):
        # get mask and save its azimutal integration for further analysis
        mask = fabio.open(par.mask_path).data
        ai = pyFAI.load(par.poni_path)
        mask_cake = ai.integrate2d(
            np.ones_like(mask), 
            par.npt_rad, 
            par.npt_azi, 
            radial_range = par.rad_range, 
            azimuth_range = par.azi_range, 
            unit=par.rad_unit,
            method = par.int_method, 
            correctSolidAngle = par.solidangle_correction, 
            mask = mask, 
            safe = False,
        )
        with h5py.File(path_mask, 'w') as hf:
            hf.create_dataset('mask_cake', data = mask_cake.intensity)

def update_filelist( sample_dir:str, par:integration_parameters, ignore=[] ):
    """Reads all raw data names, filters them as indicated and checks if files are already there

    Parameters
    ----------
    sample_dir : str
        textom base directory
    par : integration_parameters
        contains what is given in the integration_parameters.py module
    ignore : list of str
        list of names of datasets to be skipped

    Returns
    -------
    fid_in : h5py file object
        this is the overview h5 file
    filtered dataset : list
        list of strings containing all datasets to be integrated
    """
    # compile the pattern for name matching
    fid_in = h5py.File( par.path_in, 'r' )
    repattern = '^' + par.h5_proj_pattern.replace('*', '(.*?)') + '$'
    repattern = re.compile(repattern)

    # get all datasets that correspond to the pattern
    filtered_datasets = []
    # scan_no = [] # feature to label the projections directly (?)
    n_integrated, n_missing = 0,0
    for entry in fid_in.keys():
        # Check if the name matches the pattern
        match = repattern.match(entry)
        if match:
            # print(entry)
            # Check if the dataset's data is actually present on the disk
            try:
                h5path_data = f'{entry}/{par.h5_data_path}'
                dataset = fid_in[h5path_data]
                # Attempt to access the dataset's shape (raises Error if the data is missing)
                _ = dataset.shape
            except:
                # print(f"Data for {entry} is missing on the disk.")
                continue  # Skip this entry if data is missing
        
            if entry in ignore:
                continue

            # Check if the dataset has already been integrated
            todo = False
            if par.mode%2:
                out_path = os.path.join(sample_dir,'data_integrated_1d', entry.split('.')[0]+'_integrate_1d.h5')
                todo = np.logical_or( todo, not os.path.isfile(out_path) )
                n_missing += todo
                n_integrated += not todo
            if par.mode>1:
                out_path = os.path.join(sample_dir,'data_integrated', entry.split('.')[0]+'_integrate_2d.h5')
                todo = np.logical_or( todo, not os.path.isfile(out_path) )
                n_missing += todo
                n_integrated += not todo
            if todo:
                # add the dataset to the integration list
                filtered_datasets.append(entry)
                # try:
                #     scan_no.append(int(match.group(1)))
                # except:
                #     pass
                    # print(f"Failed to extract scan number from entry: {entry}")
    print(f'\tRetrieved filelist, {n_integrated}/{n_missing+n_integrated} done')
    return fid_in, filtered_datasets

def start_integration_parallel( sample_dir:str, confirm=True, ignore=[] ):
    """Starts integration on several CPUs, calls integration_launcher.py

    Parameters
    ----------
    sample_dir : str
        textom base directory
    """
    par = setup_integration(sample_dir, confirm=confirm)
    print('Starting parallel pyFAI integration')
    t0 = time()
    # start parallel integration in separate processes
    int_path = hdl.get_file_path('textom',os.path.join('src','integration_launcher.py'))
    pids = []
    for k in range(par.n_tasks):
        command = [
            'taskset', '-c', '%d-%d' % (k*par.cores_per_task, (k+1)*par.cores_per_task),
            'python', int_path, 
            '-k', '%d' % (k),
            '-d', '%s' % (sample_dir),
        ]
        p = Popen(command)
        pids.append(p)
    for p in pids: # wait for all to be finished
        p.wait()
    for p in pids: # cleanup (not really necessary)
        p.kill()
    print('Integrations finished, total time: %d s' % (time()-t0))

def start_integration_online( sample_dir:str, wait=5., confirm=True, ignore=[], parallel=False ):
    """Starts integration on one GPU or CPU, updates the file list after each
    integration and continues until there is no raw data left 

    Parameters
    ----------
    sample_dir : str
        textom base directory
    wait : float
        waits this amount of seconds after integrating the last file
        before checking for new ones
    """
    par = setup_integration(sample_dir, confirm=confirm)
    print('Starting online pyFAI integration')
    t0 = time()
    if not parallel:
        flat=None
        if isinstance( par.flatfield_correction, str ):
            flat = fabio.open(par.flatfield_correction).data

        mask = fabio.open(par.mask_path).data
        try:
            ai = pyFAI.load(par.poni_path)
        except IndexError:
            raise exc.PyFAIrelated('Check if file paths in integration_parameters.py and your .poni file are correct!')

    fid_in, filtered_datasets = update_filelist( sample_dir, par, ignore=ignore )
    while len(filtered_datasets) > 0:
        try:
            if parallel:
                int_path = hdl.get_file_path('textom',os.path.join('src','integration_launcher.py'))                
                #for gpu just launch parallel processes that will be sent to the gpu
                print(f'\tIntegrating {filtered_datasets[:par.n_tasks]}')
                pids = []
                for k in range(par.n_tasks):
                    command = [
                        'python', int_path, 
                        '-k', f'{k}',
                        '-d', sample_dir,
                    ]
                    p = Popen(command)
                    pids.append(p)
                for p in pids: # wait for all to be finished
                    p.wait()
                for p in pids: # cleanup (not really necessary)
                    p.kill()
            else:
                print(f'\tIntegrating {filtered_datasets[0]}')
                flexible_integrator(sample_dir, fid_in, filtered_datasets[0], par, ai, flat, mask)
        except:
            print(f'\t\tIntegration failed, ignoring dataset {filtered_datasets[0]}')
            ignore.append(filtered_datasets[0])
        fid_in.close()
        if len(filtered_datasets) == 1:
            print('\twaiting...')
            sleep(wait)
        fid_in, filtered_datasets = update_filelist( sample_dir, par, ignore=ignore )
    print('Integrations finished, total time: %d s' % (time()-t0))

def start_test_integration( sample_dir:str, dset_no=0 ):
    par = setup_integration(sample_dir, confirm=True)
    par.mode = 3 # for integrating both 1D and 2D
    flat=None
    if isinstance( par.flatfield_correction, str ):
        flat = fabio.open(par.flatfield_correction).data
    mask = fabio.open(par.mask_path).data
    ai = pyFAI.load(par.poni_path)
    fid_in, filtered_datasets = update_filelist( sample_dir, par, ignore=[] )
    print(f'\tIntegrating {filtered_datasets[dset_no]}')
    flexible_integrator(sample_dir, fid_in, filtered_datasets[dset_no], par, ai, flat, mask,
                        frame_average=True)
    # add "_test" to filenames
    list_of_int_files = glob.glob(os.path.join(sample_dir,'data_integrated','*.h5'))
    latest_file = max(list_of_int_files, key=os.path.getctime)
    new_name = os.path.splitext(latest_file)[0]+'_test.h5'
    os.rename(latest_file, new_name)
        # add "_test" to filenames
    test_filenames = []
    for subdir in ['data_integrated','data_integrated_1d']:
        list_of_int_files = glob.glob(os.path.join(sample_dir,subdir,'*.h5'))
        latest_file = max(list_of_int_files, key=os.path.getctime)
        new_name = os.path.splitext(latest_file)[0]+'_test.h5'
        os.rename(latest_file, new_name)
        test_filenames.append(new_name)
    return test_filenames

def flexible_integrator(sample_dir:str, fid_in, dataset:str, par:integration_parameters, ai, flat, mask, 
                        frame_average=False):
    """Lauches pyfai integration, used in both parallel and online mode,
    both for 1d or 2d integration. Writes data and metadata in sample_dir/data_integrated/

    Parameters
    ----------
    sample_dir : str
        textom base directory
    fid_in : h5py file object
        this is the overview h5 file
    dataset : str
        path to the dataset in the overview h5 file
    par : integration_parameters
        contains what is given in the integration_parameters.py module
    ai : AzimuthalIntegrator object
        pyfai integrator
    flat : fabio image
        flat field correction
    mask : ndarray, 2d
        raw detector mask
    """
    # get paths for the correct h5 file
    h5path_data = f'{dataset}/{par.h5_data_path}'
    metadata = read_metadata(fid_in, dataset, par)

    #     out_name = '{}_{:03d}_{:03d}_{:.0f}_{:08.2f}_diff_scan_0001_comb'.format(
    #                 par.title,
    #                 scan_no[l],scan_no[l],
    #                 fid_in[h5path_tilt][()],
    #                 fid_in[h5path_rot][()],
    #             ).replace('.','p')
    # else:
    out_name = dataset.split('.')[0]

    data_in = fid_in[h5path_data]
    if frame_average:
        # print('yay')
        # data_in = np.atleast_3d( np.mean(
            # data_in[ metadata['npts_fast_scanaxis'] * metadata['npts_fast_scanaxis'] // 2 : metadata['npts_fast_scanaxis'] * ( metadata['npts_fast_scanaxis'] // 2 + 1 )],
            # axis=0 ) )
        data_in = data_in[ metadata['npts_slow_scanaxis'] * metadata['npts_fast_scanaxis'] // 2 : metadata['npts_slow_scanaxis'] * ( metadata['npts_fast_scanaxis'] // 2 + 1 )]
        # data_in = np.atleast_2d(np.max(data_in,axis=0))
        # print('yo')
    n_frames = data_in.shape[0]

    if par.mode%2:
        os.makedirs(os.path.join(sample_dir, 'data_integrated_1d/'), exist_ok=True)
        path_out = os.path.join(
            sample_dir, 'data_integrated_1d/',
            out_name + '_integrate_1d.h5'
        )
        fid_out = h5py.File( path_out, 'w' )
        write_metadata( metadata, fid_out )

        radial_dset = fid_out.create_dataset( 'radial_units', (1,par.npt_rad_1D) )
        intensity_dset = fid_out.create_dataset(
            'cake_integ',
            ( n_frames, par.npt_rad_1D ),
            chunks = ( 1, par.npt_rad_1D ),
            shuffle="True", compression="lzf",
            dtype=data_type,
            )

        t0 = time()
        for frame in range (0,n_frames):
            # print(frame)
                
            result1D = ai.integrate1d(
                data_in[frame,:,:], 
                par.npt_rad_1D, 
                radial_range = par.rad_range, 
                unit=par.rad_unit,
                method = par.int_method, 
                correctSolidAngle = par.solidangle_correction, 
                dark = par.darkcurrent_correction,
                flat = flat,
                mask = mask, 
                polarization_factor = par.polarisation_factor, 
                safe = False,
            )

            radial_dset[0,:] = result1D.radial
            intensity_dset[frame,:]= result1D.intensity

            t_it = (time()-t0)/(frame+1)
            sys.stdout.write(f'\r\t\tIntegrated frames: {(frame+1):d} / {n_frames:d}, t/frame: {t_it:.3f}' )
            sys.stdout.flush()
        # ai.reset()
        fid_out.close()
        print(f', total time: {time()-t0:.1f} s')

    if par.mode>1:
        os.makedirs(os.path.join(sample_dir, 'data_integrated/'), exist_ok=True)
        path_out = os.path.join(
            sample_dir, 'data_integrated/',
            out_name + '_integrate_2d.h5'
        )
        fid_out = h5py.File( path_out, 'w' )
        write_metadata(metadata, fid_out)

        radial_dset = fid_out.create_dataset( 'radial_units', (1,par.npt_rad) )
        azimuthal_dset = fid_out.create_dataset( 'azimuthal_units', (1,par.npt_azi) )
        intensity_dset = fid_out.create_dataset(
                'cake_integ',
                ( n_frames, par.npt_azi, par.npt_rad ),
                chunks = ( 1, par.npt_azi, par.npt_rad ),
                shuffle="True", compression="lzf",
                dtype=data_type,
                )
        
        t0 = time()
        for frame in range (0,n_frames):
            result2D = ai.integrate2d(
                data_in[frame,:,:], 
                par.npt_rad, 
                par.npt_azi, 
                radial_range = par.rad_range, 
                azimuth_range= par.azi_range, 
                unit=par.rad_unit,
                method = par.int_method, 
                correctSolidAngle = par.solidangle_correction, 
                dark = par.darkcurrent_correction,
                flat = flat,
                mask = mask, 
                polarization_factor = par.polarisation_factor, 
                safe = False,
            )

            radial_dset[0,:] = result2D.radial
            azimuthal_dset[0,:] = result2D.azimuthal
            intensity_dset[frame,:,:]= result2D.intensity

            t_it = (time()-t0)/(frame+1)
            sys.stdout.write(f'\r\t\tIntegrated frames: {(frame+1):d} / {n_frames:d}, t/frame: {t_it:.2f}' )
            sys.stdout.flush()
        # ai.reset()
        fid_out.close()
        print(f'Total time: {time()-t0:.1f} s')

def read_metadata( fid_in, dataset, par:integration_parameters ):
    """Reads metadata from raw file as given in the integration_parameters.py file

    Parameters
    ----------
    fid_in : h5py file object
        this is the overview h5 file
    dataset : str
        path to the dataset in the overview h5 file
    par : integration_parameters
        contains what is given in the integration_parameters.py module

    Returns
    -------
    dict
        metadata and names to be written in the integrated file

    Raises
    ------
    exc.metadata_missing
        aborts if required metadata are missing
    """
    metadata = {}

    # Read required metadata
    required = [
        ('rot_angle', par.h5_rot_angle_path),
        ('tilt_angle', par.h5_tilt_angle_path),
        ('ty', par.h5_ty_path),
        ('tz', par.h5_tz_path),
        ('npts_fast_scanaxis',par.h5_nfast_path),
        ('npts_slow_scanaxis',par.h5_nslow_path),
    ]
    for dset_name, dset_path in required:
        try:
            h5path = f'{dataset}/{dset_path}'
            metadata[dset_name] = fid_in[h5path][()]
        except:
            if dset_name == 'rot_angle':
                splnm = dataset.split('_')
                i_diff = next(i for i, s in enumerate(splnm) if 'diff' in s) # find where is 'diff'
                print('\t\tReading rotation angle from name')
                metadata[dset_name] = float( splnm[i_diff-1].replace('m','-').replace('p','.') ) 
            elif dset_name == 'tilt_angle':
                splnm = dataset.split('_')
                i_diff = next(i for i, s in enumerate(splnm) if 'diff' in s) # find where is 'diff'
                metadata[dset_name]= float( splnm[i_diff-2].replace('m','-').replace('p','.') )
                print('\t\tReading rotation angle from name')
            else:
                print(f'\t\tRequired metadata in {h5path} not found, stopping' )
                raise exc.metadata_missing(f'Required metadata in {h5path} not found')

    # this differs depending on scan or controt
    if par.h5_nfast_path:
        try:
            h5path_nfast = f'{dataset}/{par.h5_nfast_path}'
            nfast = fid_in[h5path_nfast][()]
        except:
            print(f'\t\tRequired metadata in {h5path_nfast} not found, stopping' )
            raise exc.metadata_missing(f'Required metadata in {h5path_nfast} not found')
        try:
            h5path_nslow = f'{dataset}/{par.h5_nslow_path}'
            nslow = fid_in[h5path_nslow][()]
        except:
            print(f'\t\tRequired metadata in {h5path_nslow} not found, stopping' )
            raise exc.metadata_missing(f'Required metadata in {h5path_nslow} not found')
        metadata['fov'] = ( nfast, nslow )

    # read optional metadata
    optional = [
        ('ion', par.h5_ion_path),
        ('data_transmission', par.h5_data_transmission_path),
    ]
    for dset_name, dset_path in optional:
        try:
            if dset_path:
                h5path = f'{dataset}/{dset_path}'
                metadata[dset_name] = fid_in[h5path][()]
            else:
                metadata[dset_name] = None
        except:
            print(f'\t\tOptional metadata in {h5path} not found, continuing' )

    return metadata

def write_metadata( metadata, fid_out ):
    """Writes metadata to the integrated data file

    Parameters
    ----------
    metadata : dict
        metadata and names to be written in the integrated file
    fid_out : h5py file object
        this is the integrated data h5 file
    """
    for key in metadata:
        fid_out.create_dataset( key, data = metadata[key])

###############################################################################################
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.widgets import Button
from numba import njit, prange
from .misc import import_module_from_path

def check_detector_geometry( intpar_path:str, testfile:str, testfile_dataset:str, frame_no:int, geo_path:str, flip_detector_x=False, flip_detector_y=False,
                                vmin=1,vmax = 10, logscale = False ):

    par = msc.import_module_from_path('integration_parameters', intpar_path)
    mask = fabio.open(par.mask_path).data
    ai = pyFAI.load(par.poni_path)

    # integrate the test-dataset
    fid_in = h5py.File(testfile, 'r')
    # test_data = np.sum( fid_in['2.1'][par.h5_data_path],axis=0 )#[0] # check if 0 is ok (can pass it also as argument or plot several ?)
    test_data = fid_in[testfile_dataset][par.h5_data_path][frame_no] # check if 0 is ok (can pass it also as argument or plot several ?)
    result2D = ai.integrate2d(
                test_data, 
                par.npt_rad, 
                par.npt_azi, 
                radial_range = par.rad_range, 
                azimuth_range= par.azi_range, 
                unit=par.rad_unit,
                method = par.int_method, 
                correctSolidAngle = par.solidangle_correction, 
                dark = par.darkcurrent_correction,
                mask = mask, 
                polarization_factor = par.polarisation_factor, 
                safe = False,
            )
    q = result2D.radial
    chi = result2D.azimuthal * np.pi/180
    test_data_polar = result2D.intensity

    # test_data_polar[60,-1] =test_data_polar.max()
    # test_data_polar[60,-2] =test_data_polar.max()
    # test_data_polar[60,-3] =test_data_polar.max()
    # test_data_polar[90,-1] =np.nan
    # test_data_polar[90,-2] =np.nan
    # test_data_polar[90,-3] =np.nan
    geo = import_module_from_path('geometry', geo_path )
    det_Y,det_Z = get_detector_coordinates(geo, q, chi)

    fig = plt.figure(figsize=(18, 10))
    ax1 = fig.add_subplot(121)
    ax1.matshow( test_data, vmin=vmin,vmax=vmax, 
                norm=LogNorm() if logscale else None,
                )
    if geo.flip_detector_lr:
        ax1.invert_xaxis()
    if geo.flip_detector_ud:
        ax1.invert_yaxis()

    ax2 = fig.add_subplot(122)#, polar=True)
    ax2.pcolormesh( det_Y, det_Z, test_data_polar, vmax=vmax,
                   norm=LogNorm() if logscale else None,
                   )
    # ax2.set_axis_off()
    ax1.set_title('Raw data')
    ax1.set_xlabel(r'$\leftarrow y$')
    ax1.set_ylabel(r'$z \rightarrow$')
    ax2.set_xlabel(f'$q_y$ [nm$^-1$]')
    ax2.set_ylabel(f'$q_z$ [nm$^-1$]')
    ax2.invert_xaxis()
    ax2.set_title('Integrated data')
    plt.axis('equal')
    plt.show(block=True)

def get_detector_coordinates(geo, q, chi):
    # load geometry and calculate qx, qy
    # CHi, QQ = np.meshgrid( chi, q )
    QQ, CHi = np.meshgrid( q, chi )
    # Y = -QQ*np.sin(CHi)
    # Z = QQ*np.cos(CHi)
    Y,Z = np.empty_like(CHi), np.empty_like(CHi)
    for k in range(Y.shape[0]):
        for l in range(Y.shape[1]):
            Y[k,l], Z[k,l] = polar_to_cartesian(QQ[k,l], CHi[k,l], 
                u0=(geo.detector_direction_origin[1], geo.detector_direction_origin[2]),
                u90=(geo.detector_direction_positive_90[1], geo.detector_direction_positive_90[2]) # 
            )
    return Y, Z

@njit
def polar_to_cartesian(q:float, chi:float, u0=(0,1), u90=(1,0)):
    # Ensure numpy arrays
    u0 = np.array(u0)
    u90 = np.array(u90)
    
    # Compute Cartesian coordinates
    point = q * (np.cos(chi) * u0 + np.sin(chi) * u90)
    return point[0], point[1]

def flatmesh( x, y):
    XX,YY = np.meshgrid(x,y)
    return XX.flatten(), YY.flatten()