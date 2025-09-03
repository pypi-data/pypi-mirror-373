import os
import numpy as np
from time import time
import sys
import importlib as imp # for reading input files
import h5py, hdf5plugin
from numba import prange, njit
from mumott.data_handling import DataContainer
from mumott.pipelines import optical_flow_alignment as amo
from mumott.pipelines import phase_matching_alignment as amp
from mumott.pipelines import run_mitra, run_sirt
from mumott.pipelines.utilities import image_processing as imp
from scipy.ndimage import rotate, shift
from scipy.optimize import curve_fit
import multiprocessing as mp

import matplotlib.pyplot as plt

# domestic
from .misc import import_module_from_path
from .data import sort_data_list_by_angles
from . import plotting as myplt
from . import exceptions as exc
from .misc import cp_add_dt, timestring, find_indices_in_range
from ..config import data_type, n_threads, use_gpu

import logging
logging.getLogger("mumott").setLevel(logging.ERROR)  # Suppress some warnings from mumott

#################################################### for data import ####################################################
def mumottize( path, 
              sub_data='data_integrated', pattern='diff', 
              align_by_transmission=False,
              q_index_range=(0,5), q_range=False,
              geo_path='input/geometry.py',
              flip_fov = False, rec_1d=False, check_ori=False,
              ):
    
    geo = import_module_from_path('geometry', geo_path)

    if os.path.basename(os.path.dirname(path)) == 'data_integrated' :
        path = os.path.join(path,'..')

    dat, kappa, omega, airscat, dy = [], [], [], [], []
    filelist = sorted( os.listdir( os.path.join(path,sub_data)) )
    filelist = [s for s in filelist if pattern in s]#[:2]
    try:
        filelist = sort_data_list_by_angles( os.path.join(path,sub_data),
                                        filelist, 'tilt_angle', 'rot_angle' )
    except:
        print('\t\tDid not find angles in files, just sorted data alphabetically')

    if 'controt' in geo.scan_mode:
        for k, file in enumerate( filelist ):
            # convert q-range to indices
            if np.any(q_range):
                with h5py.File(os.path.join(path, sub_data, file),'r') as hf:
                    q_in = hf['radial_units'][()]
                    q_index_range = find_indices_in_range(q_in,q_range)
            # continuous rotation mode
            with h5py.File(os.path.join(path, sub_data, file),'r') as hf:
                omega.append( hf['rot'][()] )
                kappa.append( np.zeros_like(omega) )
                dy.append(np.mean(hf['dty']))
                d = hf['cake_integ'][()]
            if d.ndim==3:
                dat.append( 
                    d[:,q_index_range[0]:q_index_range[1]].sum(axis=2).mean(axis=1) )
            elif d.ndim==2:
                dat.append( 
                    d[:,q_index_range[0]:q_index_range[1]].sum(axis=1) )
            sys.stdout.write(f'\r\t\t Projection {k+1:d} / {len(filelist):d}')
            sys.stdout.flush()
        print('')
    else:

        # check if geometry is correct
        q_in = import_scan_data(path, sub_data, filelist[0],
            geo.scan_mode, q_range, q_index_range, 
            align_by_transmission=align_by_transmission, flip_fov=geo.flip_fov,rec_1d=rec_1d,
            check=True)
        # actual import
        print('\tLoading data')
        t1 = time()
        with mp.Pool(processes=n_threads) as pool:
            # Map file reading to workers
            parallel_res = pool.starmap(import_scan_data, 
                [(path, sub_data, filename, geo.scan_mode, q_range, q_index_range, align_by_transmission, geo.flip_fov,rec_1d
                  ) for filename in filelist])
        dat = [p[0] for p in parallel_res]
        kappa = np.array([p[1] for p in parallel_res], data_type)
        omega = np.array([p[2] for p in parallel_res], data_type)
        airscat = np.array([p[3] for p in parallel_res], data_type)     
        print(f'\t\ttook {(time()-t1)/60} min')

    if 'controt' in geo.scan_mode:
        # sort indices according to horizontal scan
        scan_idx = np.argsort(dy)
        dat = np.array(dat)[scan_idx].T
        # .T[:,scan_idx]
        max_shape = (dat.shape[1], 1)
        # projections = np.zeros((dat.shape[0],*max_shape, 1), data_type)
        projections = dat.reshape((*dat.shape, 1, 1))

    else:
        print('\tPadding Data')
        max_shape = (0,0)
        for d in dat:
            max_shape=(
                max(max_shape[0], d.shape[0]),
                max(max_shape[1], d.shape[1]))

        # fill projections with air scattering
        projections = np.array(
            [ np.random.normal(a,np.sqrt(a)/2,(*max_shape, dat[0].shape[2])) for a in airscat], 
            data_type)
        # put data padded with the airscattering
        for k in range(len(dat)):
            # med_dat = np.median(dat[k])
            # dat[k][dat[k] > 10000*med_dat] = med_dat # filter crazy pixels
            si, sj = dat[k].shape[:2]
            i0 = (max_shape[0] - si)//2
            j0 = (max_shape[1] - sj)//2
            projections[k, i0:i0+si, j0:j0+sj] = dat[k]

    print('\tRemoving outliers')
    projections = _remove_crazypixels( projections )

    if rec_1d: 
        # make a h5 file containing all the projections for all q-values
        mm_datafile = os.path.join(path,f'analysis/rec_1d/data_rec1d.h5')
        with h5py.File(mm_datafile,'w') as hf:
            hf.create_dataset( 'radial_units', data= np.array(q_in) )
            hf.create_dataset( 'projections', 
                              (projections.shape[3], *projections.shape[:3]),
                              chunks = (1, *projections.shape[:3]),
                              shuffle="True", compression="lzf",
                              data=np.transpose(projections, (3,0,1,2) )
                            )

    else:
        # make a mumott h5 file for alignment
        # pretending that the projections are the inverse of an absorbtion measurement
        diod = projections.mean(axis=3)
        diod = 1-diod/diod.max()
        diod[diod > 1] = 1

        os.makedirs( os.path.join(path,'analysis/'), exist_ok=True )
        mm_datafile = os.path.join(path,f'analysis/data_mumott.h5')

        print(f'\tSaving mumott data file to {mm_datafile}')
        # t0=time()
        with h5py.File(mm_datafile,'w') as hf:
            hf.create_dataset( 'detector_angles', data= np.array([0]) ) 
            hf.create_dataset( 'detector_direction_origin', data=np.array(
                geo.detector_direction_origin, data_type) )
            hf.create_dataset( 'detector_direction_positive_90', data=np.array(
                geo.detector_direction_positive_90, data_type) )
            hf.create_dataset( 'inner_axis', data=np.array(
                geo.inner_axis, data_type) )
            hf.create_dataset( 'outer_axis', data=np.array(
                geo.outer_axis, data_type) )
            hf.create_dataset( 'j_direction_0', data=np.array(
                geo.transverse_horizontal, data_type) )
            hf.create_dataset( 'k_direction_0', data=np.array(
                geo.transverse_vertical, data_type) )
            hf.create_dataset( 'p_direction_0', data=np.array(
                geo.beam_direction, data_type) )
            hf.create_dataset( 'volume_shape', data=np.array((max_shape[0],max_shape[0],max_shape[1]), np.int32) )
            hf.create_dataset( 'fov_flipped', data=flip_fov)

            gp = hf.create_group('projections')
            for k, proj in enumerate(projections):
                gpk = gp.create_group(str(k))
                gpk.create_dataset('data', data=proj)#.reshape( proj.shape ))
                gpk.create_dataset('diode', data=diod[k])
                gpk.create_dataset('inner_angle', data=omega[k]*np.pi/180)
                gpk.create_dataset('outer_angle', data=kappa[k]*np.pi/180)
                gpk.create_dataset('j_offset', data=0.)
                gpk.create_dataset('k_offset', data=0.)
        # print(f'\t\ttook {time()-t0:.1f} s')
    return mm_datafile

def get_q_index_range(path, sub_data, file,q_range):
    # convert q-range to indices
    if np.any(q_range):
        with h5py.File(os.path.join(path, sub_data, file),'r') as hf:
            q_in = hf['radial_units'][()].flatten()
            q_index_range = find_indices_in_range(q_in,q_range)
    return q_index_range

def import_scan_data(
        path, sub_data, file,
        scan_mode,
        q_range, q_index_range,
        align_by_transmission=False,
        flip_fov=False,rec_1d=False,
        check=False
    ):

    if np.any(q_range):
        q_index_range = get_q_index_range(path, sub_data, file, q_range)

    with h5py.File(os.path.join(path, sub_data, file),'r') as hf:
        q_in=( hf['radial_units'][0,slice(*q_index_range)] 
                ).astype(data_type).flatten()
        fov = ( hf['fov'][()] ).astype(np.int32)
        try:
            kappa = ( hf['tilt_angle'][()] )
            omega = ( hf['rot_angle'][()] )

        except: # for backwards compatibilty
            # find out angles from name:
            splnm = file.split('_')
            i_diff = next(i for i, s in enumerate(splnm) if 'diff' in s) # find where is 'diff'
            kappa = float( splnm[i_diff-2].replace('m','-') ) 
            omega = float( splnm[i_diff-1].replace('p','.') ) 
        # d = hf['cake_integ'][:,:,q_index_range[0]:q_index_range[1]].sum(axis=2)
        # d = d.reshape(*fov,d.shape[1])
        if align_by_transmission:
            d = np.atleast_2d(hf['data_transmission'][()].astype(data_type)).T
        else:
            d = hf['cake_integ']
            if d.ndim==2: # for reading 1D data
                d = d[:,q_index_range[0]:q_index_range[1]].astype(data_type)
            elif d.ndim==3:
                d = d[:,:,q_index_range[0]:q_index_range[1]].astype(data_type).mean(axis=1)

    if flip_fov:
        fov = np.flip(fov)

    if rec_1d: # for q-resolved data
        d = d.reshape(*fov,d.shape[1])
    else:
        d = d.sum(axis=1)
        d = d.reshape(*fov,1)

    if 'line' in scan_mode:
        fov = np.flip( fov )
        # d = np.fliplr(np.flipud( np.transpose( d, axes=(1,0,2)) ) )
        d = np.transpose( d, axes=(1,0,2))
        # d = np.rot90(d, 2)

    # reorder data so that they are all treated the same in the model
    if 'snake' in scan_mode:
        # Flip every second row
        for ii in range(d.shape[0]):
            if ii % 2 != 0:
                d[ii] = d[ii][::-1]

    # get airscattering:
    airscat = min( d[0,0].mean(), d[0,-1].mean(), d[-1,0].mean(), d[-1,-1].mean() )

    if check:
        print('\tCheck if data is displayed correctly, then close the figure.')
        plt.figure()
        plt.imshow(d.mean(-1).T)
        plt.xlabel('here should be the bottom of the sample')
        plt.show(block=True)
        happy = input('\t\thappy? (y/n) ')
        if 'n' in happy:
            sys.tracebacklimit = 0
            raise exc.FOV('Data import not correct, check scanmode and consider enabling flip_fov = True')
        else:
            return q_in
    else:
        return d, kappa, omega, airscat

#################################################### for actual alignment ####################################################
def align( path_in, 
        mode = 'optical_flow',
        rec_iteration=5, stop_max_iteration=20, 
        pm_upsampling=10, excluded_projections=[],
        offsets_start = None, center_rec=True,
        redo=False, use_gpu=True,
        align_horizontal=True, align_vertical=True,
        crop_image=False,
        output = True, ):

    dc = DataContainer( path_in )

    if np.any(offsets_start):
        # take given offsets as start values
        dc.geometry.j_offsets = np.array(offsets_start[0], dtype=data_type)
        dc.geometry.k_offsets = np.array(offsets_start[1], dtype=data_type)
    if redo:
        # remove all prior alignment from geometry
        dc.geometry.j_offsets = np.zeros(len(dc.geometry), dtype=data_type)
        dc.geometry.k_offsets = np.zeros(len(dc.geometry), dtype=data_type)

    alignment_param = dict(
            use_gpu = use_gpu,
            # optimal_shift=np.zeros((np.size(dc.diode, 0), 2)),
            rec_iteration=rec_iteration,
            stop_max_iteration=stop_max_iteration,
            align_horizontal=align_horizontal, align_vertical=align_vertical,
            center_reconstruction=center_rec,
            # high_pass_filter=0.01,    
            # smooth_data = True,
            # sigma_smooth = 3,
            optimizer_kwargs=dict(nestorov_weight=0.6)
        )

    if mode == 'optical_flow':
        shifts, sinogram, tomogram = amo.run_optical_flow_alignment( dc, **alignment_param )
        shifts += np.column_stack( (dc.geometry.j_offsets,dc.geometry.k_offsets) )

    elif mode == 'phase_matching':
        if np.any(crop_image):
            projection_cropping = (slice(*crop_image[0]), slice(*crop_image[1]))
        else:
            projection_cropping = (slice(None,None,None),slice(None,None,None))
        result = amp.run_phase_matching_alignment(dc, 
                ignored_subset=None, 
                projection_cropping=projection_cropping,
                # projection_cropping=(slice(None, None, None), slice(None, None, None)), 
                # reconstruction_pipeline=<function run_mitra>, 
                # reconstruction_pipeline_kwargs=None, 
                use_gpu=True, use_absorbances=True, 
                maxiter=stop_max_iteration, upsampling=pm_upsampling, 
                shift_tolerance=None, 
                shift_cutoff=None, relative_sample_size=1.0, 
                relaxation_weight=0.0, center_of_mass_shift_weight=0.0, 
                align_j=True, align_k=True
                )
        shifts = np.column_stack( (dc.geometry.j_offsets,dc.geometry.k_offsets) )
        sinogram = np.moveaxis(result['projections'][:,:,:,0], 0, -1)
        tomogram = result['reconstruction']

    if output:
        path_out = os.path.join( os.path.dirname(path_in), 'alignment_result.h5' )
        with h5py.File( path_out, 'w') as hf:
            hf.create_dataset('shifts', data=shifts)
            hf.create_dataset('sinogram', data=sinogram)
            hf.create_dataset('tomogram', data=tomogram )
            hf.create_dataset('omega', data=dc.geometry.inner_angles )
            hf.create_dataset('kappa', data=dc.geometry.outer_angles )
            hf.create_dataset('alignment_mode', data=mode)
            if np.any(crop_image):
                hf.create_dataset('cropping', data=crop_image)
            
        print(f'Saved alignment result to {path_out}')
    
    return shifts


def regroup( h5path, regroup_max = 16, 
            horizontal=True, vertical=True 
            ):
    print('\tDownsample data')
    path_dir = os.path.dirname(h5path)

    att_cp = [ 'detector_direction_origin', 'detector_direction_positive_90', 
              'inner_axis', 'outer_axis', 'j_direction_0', 'k_direction_0', 'p_direction_0',]

    for k in range( 1, int(np.log2(regroup_max))+1 ):
        print(f'\t\t{2**k:d} times')
        new_h5path = os.path.join(path_dir,f'data_mumott_gr{2**k:d}.h5')

        with h5py.File(h5path, 'r') as src, h5py.File(new_h5path, 'w') as dst:
            # copy parameters from the other h5 file
            def copy_items(name, obj):
                if name in att_cp:
                    src.copy(name, dst)
            src.visititems(copy_items)
            
            # regroup data in every projection by taking means of 2x2 blocks
            proj = src['projections']
            projNo = []
            def collect_projNo(name, obj):
                if isinstance(obj, h5py.Group):
                    projNo.append(name)
            proj.visititems(collect_projNo)
            projNo = sorted(projNo, key=lambda x: int(x))
            gp = dst.create_group('projections')
            for k, pN in enumerate(projNo):
                diode_new = _average_neighbors(src[f'projections/{pN}/diode'][()],
                                              horizontal,vertical)
                data_new = (1-diode_new).reshape((*diode_new.shape,1))
                gpk = gp.create_group(str(k))
                gpk.create_dataset('data', data=data_new)
                gpk.create_dataset('diode', data=diode_new)
                gpk.create_dataset('inner_angle', data=src[f'projections/{pN}/inner_angle'])
                gpk.create_dataset('outer_angle', data=src[f'projections/{pN}/outer_angle'])
                gpk.create_dataset('j_offset', data=0.)
                gpk.create_dataset('k_offset', data=0.)

            dst.create_dataset('detector_angles', data=np.array([0.]), dtype=data_type)
            dst.create_dataset('volume_shape', dtype=np.int32,
                               data=[diode_new.shape[0],diode_new.shape[0],diode_new.shape[1]])
        h5path = new_h5path # create the next one from the last

def align_regrouped( path:str, mode='optical_flow',
                    regroup_max = 16, use_gpu=True,
                    pre_rec_it = 5, pre_max_it = 5,
                    last_rec_it = 40, last_max_it = 5,
                    align_horizontal=True, align_vertical=True,
                    crop_image = False,
                     ):
    """Aligns dataset step by step going to higher and higher sampling

    Parameters
    ----------
    path : str
        sample_dir/analysis/
    mode : str, optional
        _description_, by default 'optical_flow'
    regroup_max : int, optional
        _description_, by default 16
    use_gpu : bool, optional
        _description_, by default True
    pre_rec_it : int, optional
        _description_, by default 5
    pre_max_it : int, optional
        _description_, by default 5
    last_rec_it : int, optional
        _description_, by default 40
    last_max_it : int, optional
        _description_, by default 5
    align_horizontal : bool, optional
        _description_, by default True
    align_vertical : bool, optional
        _description_, by default True
    crop_image : bool, optional
        _description_, by default False
    """
    # check how many projections there are
    subgroup_count = 0
    def collect_subgroups(name, obj):
        nonlocal subgroup_count
        if isinstance(obj, h5py.Group) and name != 'projections':
            subgroup_count += 1
    with h5py.File(os.path.join(path,f'data_mumott_gr{regroup_max:d}.h5'), 'r') as f:
        group = f['projections']
        group.visititems(collect_subgroups)

    # load excluded projection indices
    # excl = np.genfromtxt(os.path.join(path,))
    
    offsets = np.array((np.zeros(subgroup_count,data_type),np.zeros(subgroup_count,data_type)))
    all_shifts = []

    if regroup_max > 1:
        for k in range( int(np.log2(regroup_max)), 0, -1 ):
            regroup_pxls = 2**k
            if crop_image:
                cr=(np.array(crop_image)/regroup_pxls).astype(np.int32)
                cr[np.array(crop_image)==-1]=-1
            else:
                cr = False
            print(f'Align {regroup_pxls:d}-times downsampled data')
            shifts = align( os.path.join(path,f'data_mumott_gr{regroup_pxls:d}.h5'),
                    mode=mode, crop_image=cr, #excluded_projections=excl,
                    rec_iteration=pre_rec_it, stop_max_iteration=pre_max_it, 
                    align_horizontal=align_horizontal, align_vertical=align_vertical,
                    use_gpu=use_gpu,offsets_start=offsets,
                    output=False, redo=False )
            
            offsets = (2*shifts).T
            all_shifts.append(offsets * 2**(k-1))

    print('Align full dataset')
    shifts = align( os.path.join(path,f'data_mumott.h5'),
                    mode=mode, crop_image=crop_image,
                    rec_iteration=last_rec_it,
                    stop_max_iteration=last_max_it, use_gpu=use_gpu,
                    center_rec=False,
                    offsets_start=offsets , output=True, redo=False)
    all_shifts.append(shifts.T)

    fig,ax = plt.subplots(2,1, figsize=(8,4), sharex=True)
    for k,a in enumerate(all_shifts):
        ax[0].plot(a[0],label=str(2**k))
        ax[1].plot(a[1])
    ax[0].legend(title='downsampling')
    ax[0].set_ylabel('Horizontal shift [pixels]')
    ax[1].set_ylabel('Vertical shift [pixels]')
    ax[1].set_xlabel('Projections')
    fig.tight_layout()
    plt.show()

def project_tomogram(tomogram, rotation_angle, tilt_angle, axis=(1, 2)):
    """
    Project a 3D tomogram given a rotation and tilt angle.

    Parameters:
    tomogram (ndarray): 3D numpy array representing the tomogram.
    rotation_angle (float): Rotation angle in rad.
    tilt_angle (float): Tilt angle in rad.
    axis (tuple): Axis around which to rotate the tomogram. Default is (1, 2).

    Returns:
    projection (ndarray): 2D numpy array representing the projection.
    """
    # Step 1: Rotate the tomogram
    rotated_tomogram = rotate(tomogram, rotation_angle*180/np.pi, 
                              axes=axis, reshape=False)

    # Step 2: Tilt the tomogram
    tilted_tomogram = rotate(rotated_tomogram, tilt_angle*180/np.pi, 
                             axes=(0, 2), reshape=False)

    # Step 3: Project the tomogram onto a 2D plane
    projection = np.sum(tilted_tomogram, axis=0)

    return projection

def get_projections( g, path_mumott_data, path_alignment ):
    # Load the actual data
    with h5py.File( path_mumott_data, 'r') as hf:
        proj = hf['projections'][str(g)]['diode'][()]
    proj = 1 - proj

    #### This is to double-check the projection with scipy, needs the additional inputs:
    ## tomogram, kap, ome, shift_y, shift_z 
    ## e.g. from this:     kap,ome,shift_y,shift_z,tomogram = hdl.load_shifts_mumott( path_alignment )
    # # Step 1: Rotate the tomogram
    # rotated_tomogram = rotate(tomogram, ome[g]*180/np.pi, axes=(0,1), reshape=False)

    # # Step 2: Tilt the tomogram
    # tilted_tomogram = rotate(rotated_tomogram, -kap[g]*180/np.pi, axes=(0, 2), reshape=False)

    # # Step 3: Project the tomogram onto a 2D plane
    # proj_n = np.sum(tilted_tomogram, axis=0)

    # # Shift the projection for comparison
    # proj_n = proj_n.reshape(proj_n.shape[:2])# * proj.max()/proj_n.max()
    # proj_n = shift( proj_n, shift=(-shift_y[g], -shift_z[g]), 
    #             order=1, mode='nearest')

    # Load the projection
    with h5py.File( path_alignment, 'r') as hf:
        proj_n = hf['sinogram'][:,:,g]
    
    # rescale projection
    def linear_func(x, a):
        return a * x
    popt, _ = curve_fit(linear_func, proj.flatten(), proj_n.flatten())
    proj_n /= popt[0]

    return proj, proj_n

def check_consistency( path_alignment, path_MMdata, save_to_result=False ):
    print('\tCalculating residuals')
    err = []
    with h5py.File(path_alignment,'r') as hf:
        kap = hf['kappa'][()]
    for g in range( kap.size ):
        proj,proj_n = get_projections( g, path_MMdata, path_alignment )
        err.append( np.sqrt(((proj-proj_n)**2).sum()/(proj**2).sum()) )
        sys.stdout.write('\r\t\t %d / %d' % (g+1,kap.size))
        sys.stdout.flush()

    if save_to_result:
        with h5py.File(path_alignment,'r+') as hf:
            hf.create_dataset( 'consistency', data=err )

    print('')
    plt.figure()
    plt.plot(err)
    plt.xlabel( 'Projection' )
    plt.ylabel( 'Average relative deviation' )
    plt.title( 'Consistency of measured and simulated projections' )
    plt.show()

def show_aligned_projection( g, path_alignment, path_MMdata ):
    with h5py.File(path_alignment,'r') as hf:
        kap = hf['kappa'][()]
        ome = hf['omega'][()]
    proj,proj_n = proj,proj_n = get_projections( g, path_MMdata, path_alignment )
    fig,ax = plt.subplots(1,3, figsize=(9,4))
    vmax = max( proj.max(), proj_n.max() )
    vmin = min( proj.min(), proj_n.min() )
    ax[0].imshow(proj_n, cmap='jet', vmin=vmin, vmax=vmax )
    ax[1].imshow(proj, cmap='jet', vmin=vmin, vmax=vmax)
    ax[2].imshow(np.abs(proj_n-proj), cmap='jet', vmin=vmin, vmax=vmax)
    ax[0].set_title('Projected from tomogram')
    ax[1].set_title('Measured')
    ax[2].set_title('Absolute deviation')
    fig.suptitle(f'Projection {g}: kap {kap[g]*180/np.pi:.1f}, ome: {ome[g]*180/np.pi:.1f}')
    fig.tight_layout()
    plt.show()

def check_projections( path, 
                      path_result = 'analysis/alignment_result.h5',
                      path_data = 'analysis/data_mumott.h5',
                      output = True,
                       ):

    print('\tLoading projections and shifts')
    with h5py.File(os.path.join(path,path_result),'r') as hf:
        shifts = hf['shifts'][()]

    with h5py.File(os.path.join(path,path_data), 'r') as hf:
        gr = hf['projections']
        projNo = []
        def collect_projNo(name, obj):
            if isinstance(obj, h5py.Group):
                projNo.append(name)
        gr.visititems(collect_projNo)
        projNo = sorted(projNo, key=lambda x: int(x))
        proj, ome, kap = [], [], []
        for pN in projNo:
            proj.append( gr[pN]['diode'][()] )
            ome.append( gr[pN]['inner_angle'][()])
            kap.append(gr[pN]['outer_angle'][()])

    print('\tPlotting shifted projections in browser (check popup blocker)')
    myplt.plot_shifted_projections(
        1-np.array(proj), shifts[:,1], shifts[:,0],
        names= [f'omega {180/np.pi*o:.1f}, kappa {180/np.pi*k:.1f}' for o,k in zip(ome,kap)],
        output=output,
    )

def backproject_all( path, path_input, range_q=None, path_data=None, only_mumottize=False, batch_size=10 ):
    """calculates a scalar tomogram for each q-value

    Parameters
    ----------
    path : str  
        textom base sample directory    
    path_input : str    
        path of the input file
    range_q : list or ndarray or None
        first and second entry will be evaluated as indices
    path_data : str, optional
        path to the data_mumott.h5 file, if None makes it, by default None
    only_mumottize : bool, optional
        only makes the data_mumott.h5 file, by default False
    batch_size : int, optional
        decides how many datasets are loaded at once (memory optimization), by default 10

    Returns
    -------
    str
        path of the result .h5 file
    """
    inp = import_module_from_path('input_1Drec', path_input )
    
    with h5py.File( os.path.join(path,'analysis/alignment_result.h5'), 'r' ) as hf:
        # kap = hf['kappa'][()]
        # ome = hf['omega'][()]
        shifts = hf['shifts'][()]

    # kap=np.delete( kap, inp.exclude_proj )
    # ome=np.delete( ome, inp.exclude_proj )
    # shifts=np.delete( shifts, inp.exclude_proj, axis=0 )
 
    if not path_data:
        path_data = mumottize(path, sub_data=inp.subdir_data, pattern=inp.pattern, 
            q_index_range=[0,None],
            geo_path=os.path.join(path,'analysis/geometry.py'),
            flip_fov=inp.flip_fov, rec_1d=True,
            )
    
    if not only_mumottize:
        # load mumott file from alignment
        dc = DataContainer(os.path.join(path,'analysis/data_mumott.h5'))

        #Load metadata
        with h5py.File(path_data, 'r') as hf:
            nq, n_proj, fov_y, fov_z = hf['projections'].shape
            q_values = hf['radial_units'][()]
        
        if range_q:
            q_values = q_values[int(range_q[0]):int(range_q[1])]
            nq = q_values.size
        else:
            range_q = [0,-1]

        # set up output file
        title = os.path.basename(os.path.dirname(path))
        out_path = os.path.join(path,'analysis/rec_1d/',
                        f'reconstruction_1Dmm_{title}_{timestring()}.h5')
        with h5py.File( out_path, 'w' ) as hf:
            hf.create_dataset( 'sample_name', data=title )
            hf.create_dataset( 'radial_units', data=q_values )
            hf.create_dataset( 'sinogram', 
                              shape=(nq, n_proj, fov_y, fov_z), dtype=data_type,
                              compression=hdf5plugin.LZ4()
                                )
            hf.create_dataset( 'tomogram', 
                              shape=(nq, fov_y, fov_y, fov_z), dtype=data_type,
                               compression=hdf5plugin.LZ4() )

        n_batches = nq//batch_size
        for l in range( n_batches ):
            print('\tLoading batch')
            with h5py.File(path_data, 'r') as hf:
                projections = hf['projections'][int(range_q[0])+l*batch_size:(l+1)*batch_size]
            sino, tomo = [], []
            # reconstruct each q-value
            print('\tStarting reconstructions')
            for k in range( batch_size ):
                projection = projections[k]
                # transform to "diode scale"
                scal = projection.max()
                d = 1 - projection/scal

                # insert the data shifted according to alignment
                diodes_ref = np.moveaxis( d, 0, -1)
                diodes_shifted = imp.imshift_fft(diodes_ref, shifts[:, 0], shifts[:, 1])
                for ii in range(dc.projections.diode.shape[0]):
                    dc.projections[ii].diode = diodes_shifted[..., ii]
                sino.append(scal*(1-np.moveaxis(diodes_shifted, -1,0)))

                # reconstruct and scale back
                tomo.append( scal * run_sirt( dc, use_absorbances=True, 
                    use_gpu=use_gpu, maxiter=inp.sirt_max_iter, tdqm=False,
                    enforce_non_negativity=True,
                    )['result']['x'][:,:,:,0] )
                
                sys.stdout.write(f'\r\t\t q-value {l*batch_size+k+1:d} / {nq:d}')
                sys.stdout.flush()
            
            # print('\n\tSaving data')
            with h5py.File( out_path, 'r+' ) as hf:
                hf['sinogram'][l*batch_size:(l+1)*batch_size] = np.array(sino)
                hf['tomogram'][l*batch_size:(l+1)*batch_size] = np.array(tomo)
        return out_path

def backproject_qranges( path, path_input, path_data=None, only_mumottize=False ):
    inp = import_module_from_path('input_1Drec', path_input )
    
    with h5py.File( os.path.join(path,'analysis/alignment_result.h5'), 'r' ) as hf:
        kap = hf['kappa'][()]
        ome = hf['omega'][()]
        shifts = hf['shifts'][()]

    kap=np.delete( kap, inp.exclude_proj )
    ome=np.delete( ome, inp.exclude_proj )
    shifts=np.delete( shifts, inp.exclude_proj, axis=0 )
 
    if not path_data:
        path_data = mumottize(path, sub_data=inp.subdir_data, pattern=inp.pattern, 
            q_index_range=[np.min(inp.roi_list), np.max(inp.roi_list)],
            geo_path=os.path.join(path,'analysis/geometry.py'),
            flip_fov=inp.flip_fov, rec_1d=True,
            )
    
    if not only_mumottize:
        # load mumott file from alignment
        dc = DataContainer(os.path.join(path,'analysis/data_mumott.h5'))

        # set up output file
        title = os.path.basename(os.path.dirname(path))
        out_path = os.path.join(path,'analysis/rec_1d/',
                        f'reconstruction_1Dmm_{title}_{timestring()}.h5')
        with h5py.File( out_path, 'w' ) as hf:
            hf.create_dataset( 'sample_name', data=title )

        # loop over the peaks and reconstruct each q-value
        fov = (dc.projections[0].data.shape[0], dc.projections[0].data.shape[1])
        for q_range, peak_name in zip(inp.roi_list, inp.peak_names):
            print(f'\tReconstructing peak {peak_name}')

            tl = time()
            with h5py.File(path_data, 'r') as hf:
                projections = hf['projections'][
                    q_range[0]-np.min(inp.roi_list):q_range[1]-np.min(inp.roi_list)]
                q_peak = hf['radial_units'][
                    q_range[0]-np.min(inp.roi_list):q_range[1]-np.min(inp.roi_list)]
            print(f'\t\tLoaded data {time()-tl} s')

            nq = projections.shape[0]
            tomograms = np.empty( (fov[0], *fov, nq), data_type)
            sinograms = np.empty( (projections.shape[1], *fov, nq), data_type)
            for k in range( nq ):
                # transform to "diode scale"
                scal = projections[k].max()
                d = 1 - projections[k]/scal

                # insert the data shifted according to alignment
                diodes_ref = np.moveaxis( d, 0, -1)
                diodes_shifted = imp.imshift_fft(diodes_ref, shifts[:, 0], shifts[:, 1])
                for ii in range(dc.projections.diode.shape[0]):
                    dc.projections[ii].diode = diodes_shifted[..., ii]
                sinograms[:,:,:,k] = scal*(1-np.moveaxis(diodes_shifted, -1,0))

                tomograms[:,:,:,k] = scal * run_sirt( dc, use_absorbances=True, 
                    use_gpu=True, maxiter=20, tdqm=False,
                    enforce_non_negativity=True,
                    )['result']['x'][:,:,:,0]
                
                sys.stdout.write(f'\r\t\t q-value {k+1:d} / {nq:d}')
                sys.stdout.flush()

            print('\n\tSaving data')
            with h5py.File( out_path, 'r+' ) as hf:
                gpk = hf.create_group( peak_name )
                gpk.create_dataset( 'radial_units', data=q_peak )
                gpk.create_dataset( 'sinogram', data = sinograms )
                gpk.create_dataset( 'tomogram', data = tomograms )

def backproject( dc, method='sirt', use_abs=False,
                rec_iteration=20, use_gpu=True, tdqm=True ):
    if method=='sirt':
        tomogram = run_sirt( dc, use_absorbances=use_abs, 
            use_gpu=use_gpu, maxiter=rec_iteration, tdqm=tdqm,
        )#['result']['x']    
    else:
        tomogram = run_mitra( dc, use_absorbances=use_abs, 
            use_gpu=use_gpu, maxiter=rec_iteration, tdqm=tdqm,
        )['result']['x']

    # if output:
    #     path_out = os.path.join( os.path.dirname(path_in), 'alignment_result.h5' )
    #     with h5py.File( path_out, 'w') as hf:
    #         hf.create_dataset('shifts', data=np.zeros((dc.diode.shape[0],2),data_type))
    #         hf.create_dataset('sinogram', data=dc.data[:,:,:,0].transpose(1,2,0))
    #         hf.create_dataset('tomogram', data=tomogram )
    #         hf.create_dataset('omega', data=dc.geometry.inner_angles )
    #         hf.create_dataset('kappa', data=dc.geometry.outer_angles )
    #     print(f'Saved alignment result to {path_out}')
    return tomogram

@njit(parallel=True)
def _remove_crazypixels( data ):
    dat_new = data.copy()
    for k in range(data.shape[3]):
        for g in prange(data.shape[0]):
            for l in range(-1, data.shape[1]-1):
                for m in range(-1, data.shape[2]-1):
                    sample = np.array([
                        data[g,l-1,m-1,k],data[g,l-1,m,k],data[g,l-1,m+1,k],
                        data[g,l,m-1,k],                  data[g,l,m+1,k],
                        data[g,l+1,m-1,k],data[g,l+1,m,k],data[g,l+1,m+1,k],
                        ])
                    base = np.median(sample)
                    if data[g,l,m,k] > 10*np.abs(base):
                        dat_new[g,l,m,k] = base
    return dat_new

@njit(parallel=True)
def _average_neighbors(arr, hor=True, ver=True):
    """Numba-compiled function for regrouping data

    Parameters
    ----------
    arr : 2D-array
        data to be regrouped
    hor : bool, optional
        toggle horizontal regrouping, by default True
    ver : bool, optional
        toggle vertical regrouping, by default True

    Returns
    -------
    2D-array
        regrouped data
    """
    rows, cols = arr.shape
    f_row = 2 if ver else 1
    f_col = 2 if hor else 1
    new_rows = (rows + 1) // f_row if ver else rows
    new_cols = (cols + 1) // f_col if hor else cols
    
    # Initialize a new array to hold the averaged values
    result = np.zeros((new_rows, new_cols))

    for i in prange(new_rows):
        for j in range(new_cols):
            # Determine the slice for the 2x2 block
            row_start = f_row * i
            row_end = min(f_row * i + f_row, rows)
            col_start = f_col * j
            col_end = min(f_col * j + f_col, cols)
            
            # Extract the block and compute the average
            block = arr[row_start:row_end, col_start:col_end]
            result[i, j] = np.mean(block)
    
    return result