import os
import numpy as np
from time import time
import sys
import h5py
from numba import prange, njit
from scipy.signal import find_peaks

# domestic
from . import mask as msk
from . import numba_plugins as nb
from .misc import import_module_from_path
from .model import model
from ..config import data_type

def import_data( sample_dir, pattern, mod:model,  baselines='simple',
                qmask_path=None, detmask_path=None, geo_path='input/geometry.py',
                use_ion=True, crazypixelfilter='simple' ):
    """Looks for data in path/data_integrated/ and prepares them for textom reconstructions

    Parameters
    ----------
    sample_dir : str
        textom base directory
    pattern : str
        substring required to be in the files in path/data_integrated/
    mod : model
        model object, needs to have projectors and diffractlets
    baselines : str or False, optional
        'simple' to draw a straight line under each peak, (does not work if there is peak-overlap!)
        'polynomial' to fit the whole q-range minus the peaks with a 5th order polynomial (can
            handle peak-overlap, but data needs to be rather smooth where there is no peaks), 
        'False' for no baselines (if your background is low), by default 'simple'
    qmask_path : str, optional
        path to a file containing the peak-regions in q, if None will be created
        from user input, by default None
    detmask_path : str, optional
        path to a file containing the detector mask, if None will be created
        from user input, by default None
    geo_path : str, optional
        path to the desired geometry module, by default 'input/geometry.py'
    flip_fov : bool, optional
        can be set to True if the fov metadata is switched by accident, by default False
    use_ion : bool, optional
        choose if normalisation by ionization chamber should be used (if present in
        data), by default True
    """
    geo = import_module_from_path('geometry', geo_path)
    # get the images that show the sample
    scanmask = mod.Beams[:,:,0].astype(bool)                           ###########

    print('Starting data import')
    print('\tLoading integrated data from files')
    t0=time()
    bl_coeff, airscat, ion = [], [], []
    filelist = get_data_list(sample_dir, pattern)

    for g, file in enumerate( filelist ):
        # Read data from integrated file
        with h5py.File(os.path.join(sample_dir, 'data_integrated', file),'r') as hf:
            q_in = np.squeeze(hf['radial_units'][()] ).astype(data_type)
            chi_in = np.squeeze( hf['azimuthal_units'][()]*np.pi/180 ).astype(data_type)
            fov = ( hf['fov'][()] ).astype(np.int32)
            d = ( np.array(hf['cake_integ'][()]) ).astype(data_type)
            if 'ion' in hf and use_ion:
                try:
                    ion_g = winsorize(hf['ion'][()], 1)
                except:
                    ion_g = hf['ion'][()]
                ion.append(ion_g)
            else:
                use_ion=False

        # ### Bring data into the textom coordinate system
        # # get positive direction of chi
        # if np.sum(np.cross(geo.detector_direction_origin, geo.detector_direction_positive_90)).round(3) >0.:
        #     chi_in = 2*np.pi - np.flip(chi_in) # flip direction of chi
        #     d = np.flip(d, axis=1)
        # # get axis in lab coordinates
        # from_z_dot = np.dot(
        #     geo.detector_direction_origin/np.linalg.norm(geo.detector_direction_origin),
        #     geo.transverse_vertical/np.linalg.norm(geo.transverse_vertical))
        # shiftby = np.arccos(from_z_dot)
        # if np.sum(np.cross(geo.transverse_vertical, geo.detector_direction_origin)).round(3) >0.:
        #     shiftby += np.pi
        # # shift and rebin in chi if necessary
        # chi_in += shiftby # this chi corresponds to model coordinates
        # # find startpoint and rotate data if necessary
        # i_chi_0 = np.where(chi_in > 0, chi_in, np.inf).argmin() # finds smallest non-negative
        # if i_chi_0 != 0:
        #     d = np.concatenate(
        #         (d[:,i_chi_0:,:], d[:,:i_chi_0,:]),
        #         axis=1)
        # '''
        # i guess we should leave the data as they are
        # and instead calculate directly detector carthesian coordinates
        # make "check_geometry"
        #     1. integrate a dataset
        #         mask might be enough, better provide a test dataset
        #     2. plot rawdata and integrated in textom geometry
        #         calculate qx, qy, qz in carthesian
        # '''    

        # adjust data binning
        n_chi = chi_in.size
        if n_chi > mod.detShape[1]:
            n_chi = mod.detShape[1]
            d = rebin_stack_2d_dim0(d, n_chi)
        elif n_chi < mod.detShape[1]:
            print('Data is too sparse for the model, simulate with less bins.')
            return 0


        if geo.flip_fov:
            fov = np.flip( fov )
            
        if use_ion:
            # print('\tRescale by beam intensity')
            d = _rescale( d, ion[g] )

        ## Reshaping in function of scanning mode ###
        # Base code written for column scan
        d = d.reshape( *fov, d.shape[1], d.shape[2] )
        
        if 'line' in geo.scan_mode:
            fov = np.flip( fov )
            # d = np.fliplr(np.flipud( np.transpose( d, axes=(1,0,2,3)) ) )
            d = np.transpose( d, axes=(1,0,2,3)) 

        # reorder data so that they are all treated the same in the model
        if 'snake' in geo.scan_mode:
            # Flip every second row
            for ii in range(d.shape[0]):
                if ii % 2 != 0:
                    d[ii] = d[ii][::-1]
        ##############################################

        # dat.append( d )
        i0=d.shape[-1]//4
        half_fov = fov[1]//2
        edge_sample = np.array([ 
            d[0,0,i0:].mean(),d[0,-1,:,i0:].mean(), 
            d[0,-half_fov,:,i0:].mean(),  d[-1,0,:,i0:].mean(), 
            d[-1,-half_fov,:,i0:].mean(),d[-1,-1,:,i0:].mean()]) 
        airscat.append( np.min( edge_sample[edge_sample > 0.] ))
        if not ion or not use_ion:
            # print('\tRescale by air scattering')
            d /= airscat[g]

        # print('\tPadding data.')
        # t0=time()
        if hasattr( mod, 'fov_single' ):
            fov_max = mod.fov_single
        else:
            fov_max = mod.fov
        # pad the data as in mumottize
        proj =  np.zeros( (*fov_max, n_chi, *q_in.shape), data_type)
        si, sj = d.shape[:2]
        i0 = (fov_max[0] - si)//2
        j0 = (fov_max[1] - sj)//2
        proj[i0:i0+si, j0:j0+sj] = d
        proj = proj.reshape(fov_max[0]*fov_max[1], n_chi, *q_in.shape)
        # print(f'\t\ttook {time()-t0:.2f} s')

        if g==0:
            # prepare data for choosing q-regions
            powder_2D = proj[scanmask[0]].mean(axis=0)
            powder_1D = powder_2D.mean(axis=0)

            # load peak regions from file or create them by user input
            peak_reg, q_mask, q_mask_k, q_mask_hp, prom, q_peaks, t_inter_1 = mask_peak_regions( 
                sample_dir, mod, q_in, powder_1D, qmask_path) 

            #### Make the Detector mask ####
            powder_2D_masked = np.array([powder_2D[:,qm].sum(axis=1) for qm in q_mask_k])
            mask_detector, t_inter_2 = make_detector_mask( 
                sample_dir, detmask_path, powder_2D_masked, peak_reg, q_in, chi_in )
        
        scanmask_g = scanmask[g].copy()
        if crazypixelfilter == 'search':
            # print('\tRemoving outliers')
            # t0=time()
            # projections_1=projections.copy()
            # for k in range(proj.shape[0]):
            proj = _remove_crazypixels(proj, scanmask_g)
                # sys.stdout.write('\r\t\t %d / %d' % (k+1,proj.shape[0]))
                # sys.stdout.flush()
            # print(f'\t\ttook {time()-t0:.2f} s')
            ###### might be much faster with this:
            # proj[ np.nanpercentile(proj, 99) ] = np.nan # or some value, np.median(proj)
            ######
        else:
            proj = _remove_crazypixels_zscore(proj)

        if baselines=='polynomial':
            # print('\tDrawing baselines')
            # t0=time()
            bl_coeff_tmp1, scanmask_g = _draw_baselines_polynom( 
                proj, scanmask_g, q_in, q_mask, q_mask_hp, prom, 5 )
            bl_coeff_tmp2 = bl_coeff_tmp1[scanmask_g]
            # # get rid of outliers
            t_mask_0 = np.where(scanmask_g)
            blc_weight = (bl_coeff_tmp2**2).sum(axis=1) 
            bl_mask = blc_weight < 200*np.median(blc_weight)
            t_mask = t_mask_0[0][bl_mask]
            scanmask_g = np.zeros_like(scanmask_g)
            scanmask_g[t_mask] = True
            scanmask[g] = scanmask_g
            bl_coeff_tmp1 = bl_coeff_tmp1[scanmask_g]    
            # print(f'\t\ttook {time()-t0:.2f} s')
        elif baselines=='simple':
            bl_coeff_tmp1, scanmask_g = _draw_baselines_simple(
                proj, scanmask_g, q_mask_k, q_mask_hp, prom )
            scanmask[g] = scanmask_g
        else:
            print('\tNo baseline subtraction')
            bl_coeff_tmp1 = np.zeros( [] )
            baselines = False # this is so that later 'if baselines' check gives False

        # # plot data and baseline
        # plt.plot(nb.nb_mean_ax0( proj[t] ))
        # plt.plot(nb.nb_polyval(bl_coeff_tmp1[t], q_in))

        bl_coeff.append(bl_coeff_tmp1)
        t_mask = np.array( np.where(scanmask_g) ).T      

        # print('\tSubstracting background, regrouping data')
        # t0=time()
        q_mask_k_ext = np.array([nb.nb_tile_1d(qmk, n_chi) for qmk in q_mask_k]
                                ).astype(data_type)
        if baselines=='polynomial':
            data_fit = _regroup_q_polynombl( 
                proj, t_mask, mask_detector, 
                bl_coeff_tmp1, q_in, n_chi, q_mask_k_ext )
        elif baselines=='simple':
            data_fit = _regroup_q_simplebl( 
                proj, t_mask, mask_detector, 
                bl_coeff_tmp1, q_in, n_chi, q_mask_k_ext )
        else:
            data_fit = _regroup_q_nobaseline( 
                proj, t_mask, mask_detector, 
                n_chi, q_mask_k_ext )
        # print(f'\t\ttook {time()-t0:.2f} s')

        # dplot=np.zeros_like(scanmask_g).astype(data_type)
        # dplot[scanmask_g] = data_fit.mean(axis=1)
        # plt.figure()
        # plt.imshow(dplot.reshape(fov_max))

        out_path = os.path.join( sample_dir, 'analysis', 'data_textom.h5')
        if g == 0:
            print('\tSaving data to file: %s' % out_path)
            with h5py.File( out_path, 'w') as hf:
                hf.create_dataset( 'data',
                        shape=(0, data_fit.shape[1]),
                        maxshape=(None, data_fit.shape[1]),
                        chunks=(1, data_fit.shape[1]),
                        dtype=data_type,
                    )
                hf.create_dataset( 'peak_reg', data=peak_reg )
                hf.create_dataset( 'q', data = q_peaks)
                hf.create_dataset( 'detShape', data = [q_mask_k.shape[0], n_chi] )
                hf.create_dataset( 'mask_detector', data = mask_detector)
                hf.create_dataset( 'baselines', data = baselines )
            t1=time()

        # add data to h5 file
        with h5py.File( out_path, 'r+') as hf:
            dset = hf['data']
            current_rows = dset.shape[0]
            new_rows = current_rows + data_fit.shape[0]
            dset.resize( new_rows, axis=0)
            dset[current_rows:new_rows, :] = data_fit

        try:
            t_it = (time()-t1)/(g)
        except:
            t_it=0
        Nrot = len(filelist)
        sys.stdout.write(f'\r\t\tProjection {(g+1):d} / {Nrot:d}, t/proj: {t_it:.1f} s, t left: {((Nrot-g-1)*t_it/60):.1f} min' )
        sys.stdout.flush()

    gt_mask = np.array( np.where(scanmask) ).T
    # add metadata to h5 file
    with h5py.File( out_path, 'r+') as hf:
        hf.create_dataset( 'scanmask', data=scanmask )
        hf.create_dataset( 'gt_mask', data=gt_mask )
        if baselines:
            hf.create_dataset( 'bl_coeff', data=np.concatenate(bl_coeff) )
        hf.create_dataset( 'airscat', data = airscat )
        if ion:
            ion_av = np.array( [np.mean(i) for i in ion] ) # cannon write ion directly because shape
            hf.create_dataset( 'ion', data = ion_av )

    print(f'\n\t\ttook {(time()-t0)/60:.1f} min')

def get_data_list(sample_dir, pattern):
    filelist = sorted( os.listdir( os.path.join(sample_dir,'data_integrated')) )
    filelist = [s for s in filelist if pattern in s]#[:2]
    try:
        filelist = sort_data_list_by_angles( os.path.join(sample_dir,'data_integrated'),
                                        filelist, 'tilt_angle', 'rot_angle' )
    except:
        print('\t\tDid not find angles in files, just sorted data alphabetically')
    return filelist

def mask_peak_regions( sample_dir, mod:model, q_data, powder_1D, qmask_path, show=False):
    t_inter = time() # this is to subtract the time it takes for user input for remaining time estimation
    # set up boolean mask for filtering data
    q = mod.Qq_det.reshape(mod.detShape)[:,0]
    q_mask = np.ones_like(q_data, dtype=bool)
    q_mask &= (q_data > q[0]) # cut away SAXS signal
    if os.path.isfile(qmask_path):
        # if peak regions are defined in file, take them
        peak_reg = np.genfromtxt(qmask_path)
        peak_reg = peak_reg.reshape( (peak_reg.size//2, 2)  )
        print('\tLoaded peak regions')
        if show:
            powder = mod.difflets[0].reshape(mod.detShape)[:,0]
            powder = powder / powder[-10:].mean() * powder_1D[-10:].mean()
            import matplotlib.pyplot as plt
            plt.figure()
            plt.plot(q_data[q_mask], powder_1D[q_mask])
            plt.plot(q, powder)
            plt.xlabel('q / nm^-1')
            plt.ylabel('I')
    else:
        # select peak regions from data and simulated powder pattern
        print('\tChoose regions containing diffraction peaks')
        happy = 'n'
        while happy != 'y':
            powder = mod.difflets[0].reshape(mod.detShape)[:,0]
            powder = powder / powder[-10:].mean() * powder_1D[-10:].mean()

            peak_reg = msk.select_regions( q_data[q_mask], powder_1D[q_mask], q, powder, 
                    max_regions=None,
                    title='Select individual Bragg peaks by holding LMB, remove by RMB' )
            happy = input('\thappy? (y/n) ')
        peak_reg = peak_reg.get_regions()

        with open( os.path.join(sample_dir,'analysis','peak_regions.txt'),'w') as fid:
            for reg in peak_reg:
                fid.write(f'{reg[0]}\t{reg[1]}\n')

    q_peaks = np.mean(peak_reg, axis=1)

    # find out prominence of the highest peak for filtering data
    I_mx = 0.                   
    q_mask_k = []
    for k, (start, end) in enumerate( peak_reg ):
        q_mask_k.append( ((q_data >= start) & (q_data <= end)) )
        q_mask &= ~q_mask_k[k]
        dat_peak = powder_1D[q_mask_k[k]]
        if dat_peak.max() > I_mx:
            q_mask_hp = q_mask_k[k]
            _, info = find_peaks(dat_peak, prominence=0.)
            try:
                prom = info['prominences'].max()
            except:
                prom=0.
            I_mx = dat_peak.max()
    q_mask_k = np.array(q_mask_k)#.astype(data_type)  

    t_inter = time()-t_inter
    return peak_reg, q_mask, q_mask_k, q_mask_hp, prom, q_peaks, t_inter

def make_detector_mask( sample_dir, detmask_path, powder_2D_masked, peak_reg, q_in, chi_in ):
    t_inter = time()
    if os.path.isfile(detmask_path):
        mask_detector = np.genfromtxt(detmask_path, bool)
        print('\tLoaded detector mask')
    else:
        # create the detector mask
        # check if there is a mask from pyfai
        cakemask_path = os.path.join(sample_dir, 'analysis', 'mask_detector_cake.h5')
        if os.path.isfile(cakemask_path):
            with h5py.File(cakemask_path,'r') as hf:
                mc = hf['mask_cake'][()]
            QQ,_ = np.meshgrid( q_in, chi_in )
            qm = [np.logical_and(QQ >= start, QQ <= end) for start,end in peak_reg]
            mask_detector = np.array([
                [np.logical_and.reduce(mc[k, qm[l][k]]) for k in range(chi_in.size)] 
                    for l in range(len(peak_reg))])
        else:
            mask_detector = np.ones_like(powder_2D_masked).astype(bool)

        print('\tCreate mask by removing (left mouse button) or restoring pixels (right mouse button)')
        # start = np.argmax(q_mask) # this could be useful if taking a full mask, then partially regroup ? have to do it with diffractlets too maybe
        # end = len(q_mask) - 1 - np.argmax(q_mask[::-1]) # then make these values None and when regrouping do np.mean * number of points to make up for Nones
        mask_detector = msk.mask_detector( powder_2D_masked, mask_detector )
        with open( os.path.join(sample_dir, 'analysis', 'fit_detmask.txt'),'w') as fid:
            for pxl in mask_detector:
                fid.write(f'{pxl}\n')
    t_inter = time() - t_inter
    return mask_detector, t_inter

def sort_data_list_by_angles( data_dir_path, filelist, h5_outer_rotaxis_path, h5_inner_rotaxis_path ):

    inner_angle = []
    outer_angle = []
    for file in filelist:
        with h5py.File(os.path.join(data_dir_path,file), 'r') as hf:
            inner_angle.append( hf[h5_inner_rotaxis_path][()] )
            outer_angle.append( hf[h5_outer_rotaxis_path][()] )
    # first sort by outer angles:
    order = np.lexsort([inner_angle, outer_angle])

    return [filelist[k] for k in order]

def winsorize(data, percent = 1):
    """Very simple filter, setting the upper and lower percentile to the next smaller/larger value
    """
    lower = np.percentile(data, percent)
    upper = np.percentile(data, 100-percent)
    data[data < lower] = lower
    data[data > upper] = upper
    return data

################## numba compiled functions
@njit(parallel=True)
def _regroup_chi( d, n_old, n_new ):
    # Create an array to hold the rebinned result
    d_rebinned = np.empty((d.shape[0], n_new, d.shape[2]))

    # Create the old and new column indices
    old_indices = np.arange(n_old)
    new_indices = np.linspace(0, n_old - 1, n_new)

    for t in prange( d.shape[0] ):
        # Interpolate each row
        for ii in range( d.shape[2] ):
            d_rebinned[t, :, ii] = np.interp(new_indices, old_indices, d[t, :, ii])
    return d_rebinned

@njit(parallel=True)
def _draw_baselines_all(projections, scanmask, q, qmask, q_mask_hp, prom, porder=5 ):
    # draw baselines for chosen data
    bl_coeff = np.zeros( (projections.shape[0],projections.shape[1],porder+1), data_type )
    for g in range(projections.shape[0]):
        for t in prange(projections.shape[1]):
            if scanmask[g,t]:
                # regroup data azimutally
                data_1D = nb.nb_mean_ax0( projections[g,t] )

                if _any_peak( data_1D[q_mask_hp], 0.05*prom ):
                    # draw a baseline
                    c = nb.nb_polyfit( q[qmask], data_1D[qmask], porder )
                    b = nb.nb_polyval( c, q[qmask] )
                    bl_coeff[g,t] = c * (data_1D[qmask]/b).min()
                else:
                    # exclude this image
                    scanmask[g,t]=False
    return bl_coeff, scanmask, projections

@njit(parallel=True)
def _draw_baselines_polynom(proj, scanmask, q, qmask, q_mask_hp, prom, porder=5 ):
    """Draws a polynomial baseline through the azimuthally averaged data

    Parameters
    ----------
    proj : ndarray
        projection data
    scanmask : ndarray
        decides which data will be further used for fitting, baselines
        will only be drawn on thse
    q : ndarray
        q-values of the data
    qmask : ndarray
        defines the ranges of the peaks to be treated
    q_mask_hp : ndarray
        defines the range of the highest peak
    prom : float
        prominence of the highest peak in the first projection
    porder : int, optional
        polynomial order for the baseline, by default 5

    Returns
    -------
    ndarray
        polynomial coefficients of the baselines
    ndarray
        updated scanmask
    """
    # draw baselines for chosen data
    bl_coeff = np.zeros( (proj.shape[0],porder+1), data_type )
    for t in prange(proj.shape[0]):
        if scanmask[t]:
            # regroup data azimutally
            data_1D = nb.nb_mean_ax0( proj[t] )

            if _any_peak( data_1D[q_mask_hp], 0.05*prom ):
                # draw a baseline
                c = nb.nb_polyfit( q[qmask], data_1D[qmask], porder )
                b = nb.nb_polyval( c, q[qmask] )
                bl_coeff[t] = c * (data_1D[qmask]/b).min()
            else:
                # exclude this image
                scanmask[t]=False
    return bl_coeff, scanmask

@njit(parallel=True)
def _draw_baselines_simple(proj, scanmask, q_mask_k, q_mask_hp, prom ):
    """Draws a polynomial baseline through the azimuthally averaged data

    Parameters
    ----------
    proj : ndarray
        projection data
    scanmask : ndarray
        decides which data will be further used for fitting, baselines
        will only be drawn on these
    q : ndarray
        q-values of the data
    qmask : ndarray
        defines the ranges of the peaks to be treated
    q_mask_hp : ndarray
        defines the range of the highest peak
    prom : float
        prominence of the highest peak in the first projection

    Returns
    -------
    ndarray
        polynomial coefficients of the baselines
    ndarray
        updated scanmask
    """
    # draw baselines for chosen data
    bl_coeff = np.zeros( (proj.shape[0],2*q_mask_k.shape[0]), data_type )
    for t in prange(proj.shape[0]):
        if scanmask[t]:
            # regroup data azimutally
            data_1D = nb.nb_mean_ax0( proj[t] )

            if _any_peak( data_1D[q_mask_hp], 0.05*prom ):
                # for each peak
                for p in range(q_mask_k.shape[0]):
                    # get the value at the beginning and the end of the peak
                    idxs = np.where(q_mask_k[p])[0]
                    bl_coeff[t,2*p] = data_1D[idxs[0]-1:idxs[0]+1].mean()
                    bl_coeff[t,2*p+1] = data_1D[idxs[-1]:idxs[-1]+2].mean()
            else:
                # exclude this image
                scanmask[t]=False
    return bl_coeff, scanmask

@njit
def _any_peak( curve, prominence_threshold ):
    # numba-optimized function to check if there is a peak
    # with the given prominence in the data
    i_peak = np.argmax( curve )
    left_min = np.min(curve[:i_peak]) if i_peak > 0 else 0
    right_min = np.min(curve[i_peak + 1:]) if i_peak < curve.size-1 else 0
    prominence = curve[i_peak] - max(left_min, right_min)
    if prominence >= prominence_threshold:
        return True
    return False

@njit(parallel=True)
def _regroup_q_polynombl( proj, t_mask, mask_detector, bl_coeff, q_in, n_chi, q_mask_k_ext ):
    nD = t_mask.shape[0] # effective number of images
    data_fit = np.empty( (nD, mask_detector.sum()), data_type )
    n_peaks = q_mask_k_ext.shape[0]
    for k in prange(nD):
        t = t_mask[k,0]
        # get image and subtract baseline
        d_k = proj[t] 
        bl = nb.nb_polyval( bl_coeff[t], q_in)
        d_k_sub = d_k - nb.nb_tile_1d(bl, n_chi)

        # regroup data into peaks
        d_k_regr = np.empty( (n_peaks, n_chi), data_type )
        for p in range(n_peaks):
            d_k_regr[p] = (d_k_sub*q_mask_k_ext[p]).sum(axis=1)
        d_k_regr_fl = d_k_regr.flatten()[mask_detector]

        data_fit[k] = d_k_regr_fl
    return data_fit

@njit(parallel=True)
def _regroup_q_simplebl( proj, t_mask, mask_detector, bl_coeff, q_in, n_chi, q_mask_k_ext ):
    nD = t_mask.shape[0] # effective number of images
    data_fit = np.empty( (nD, mask_detector.sum()), data_type )
    n_peaks = q_mask_k_ext.shape[0]
    # get the q-range for each peak
    q_range_p = np.empty(n_peaks, data_type)
    for p in range(n_peaks):
        qp_ind = np.where(q_mask_k_ext[p,0])[0]
        q_range_p[p] = q_in[qp_ind[-1]+1] - q_in[qp_ind[0]]

    for k in prange(nD):
        t = t_mask[k,0]
        # get image and subtract baseline
        d_k = proj[t] 

        # regroup data into peaks
        d_k_regr = np.empty( (n_peaks, n_chi), data_type )
        for p in range(n_peaks):
            #calculate integrated baseline:
            bl_int = (bl_coeff[t,2*p] + bl_coeff[t,2*p+1])/2 * q_mask_k_ext[p,0].sum()
            # subtract from peak-integral
            d_k_regr[p] = (d_k*q_mask_k_ext[p]).sum(axis=1) - bl_int
        d_k_regr_fl = d_k_regr.flatten()[mask_detector]

        data_fit[k] = d_k_regr_fl
    return data_fit

@njit(parallel=True)
def _regroup_q_nobaseline( proj, t_mask, mask_detector, n_chi, q_mask_k_ext ):
    nD = t_mask.shape[0] # effective number of images
    data_fit = np.empty( (nD, mask_detector.sum()), data_type )
    n_peaks = q_mask_k_ext.shape[0]
    for k in prange(nD):
        # get image and subtract baseline
        d_k = proj[t_mask[k,0]] 

        # regroup data into peaks
        d_k_regr = np.empty( (n_peaks, n_chi), data_type )
        for p in range(n_peaks):
            d_k_regr[p] = (d_k*q_mask_k_ext[p]).sum(axis=1)
        d_k_regr_fl = d_k_regr.flatten()[mask_detector]

        data_fit[k] = d_k_regr_fl
    return data_fit

@njit(parallel=True)
def _rescale( data, norm ):
    for k in prange( data.shape[0] ):
        if norm[k] == 0:
            data[k] = 0
        else:
            data[k] /= norm[k]
    return data

@njit(parallel=True)
def _rescale_perimage( data, norm ):
    for k in prange( data.shape[0] ):
        for l in range( data.shape[1] ):
            data[k,l] /= norm[k,l]
    return data

@njit(parallel=True)
def _remove_crazypixels( projection, scanmask ):
    dat_new = projection.copy()
    for k in prange(projection.shape[0]):
        if scanmask[k]:
            for l in range(1,projection.shape[2]-1):
                # base = np.median(projection[k,:,l])
                for m in range(-1,projection.shape[1]-1):
                    sample = np.array([
                        projection[k,m-1,l-1],projection[k,m-1,l],projection[k,m-1,l+1],
                        projection[k,m,l-1],projection[k,m,l+1],                        
                        projection[k,m,l-2],projection[k,m,l+2],
                        projection[k,m+1,l-1],projection[k,m+1,l],projection[k,m+1,l+1]
                    ])
                    base = np.median(sample)
                    if projection[k,m,l] > 10*np.abs(base):
                        dat_new[k,m,l] = base
    return dat_new

# @njit
def _remove_crazypixels_zscore( data, threshold=3 ):
    #
    z = (data - data.mean()) / data.std()
    data[z > threshold] = np.median(data)
    return data


@njit(parallel=True)
def rebin_stack_2d_dim0(stack, new_cols):
    """
    Rebin a stack of 2D arrays to a new shape using a weighted average of the corresponding regions.
    
    Parameters:
    - stack: 3D array with the arrays of original shape in dimensions 1/2.
    - new_cols: int of the new number of cols.
    
    Returns:
    - stack_rebinned: 3D array with the rebinned arrays in dimensions 1/2.
    """
    n_images = stack.shape[0]
    stack_reshaped = np.empty( (n_images, new_cols, stack.shape[2]) )
    for k in prange( n_images ):
        stack_reshaped[k] = rebin_2d_dim0( stack[k], new_cols )
    return stack_reshaped

@njit
def rebin_2d_dim0(array, n_dim0):
    """
    Rebin a 2D array to a new shape using a weighted average of the corresponding regions.
    
    Parameters:
    - array: Input 2D array (original shape).
    - n_dim0: int of the new size in dim 0cols.
    
    Returns:
    - rebinned_array: Rebinned 2D array with weighted averages.
    """
    n_dim0_orig, n_dim1_orig = array.shape # original shape
    # new_rows, new_cols = new_shape
    
    # Calculate the scaling factors (step size in each dimension)
    bin_size = n_dim0_orig / n_dim0

    # Create an empty rebinned array
    rebinned_array = np.zeros((n_dim0, n_dim1_orig))

    for i in range(n_dim0):
        # Determine the range of pixels in the original array that contribute to the new bin
        bin_start = i * bin_size
        bin_end = (i + 1) * bin_size

        # Find the indices of the original array that overlap with the new bin
        indices_to_bin = np.arange(int(np.floor(bin_start)), int(np.ceil(bin_end)))

        for j in range(n_dim1_orig):
            # Accumulate weighted sum over these indices
            weight_sum = 0
            value_sum = 0
            for c in indices_to_bin:
                # Compute the overlap (weight) for each pixel
                weight = min(bin_end, c + 1) - max(bin_start, c)

                # Add the contribution to the weighted sum
                value_sum += array[c, j] * weight
                weight_sum += weight

            # Assign the weighted average to the rebinned array
            rebinned_array[i, j] = value_sum / weight_sum

    return rebinned_array

@njit(parallel=True)
def rebin_stack_2d(stack, new_shape):
    """
    Rebin a stack of 2D arrays to a new shape using a weighted average of the corresponding regions.
    
    Parameters:
    - stack: 3D array with the arrays of original shape in dimensions 1/2.
    - new_shape: Tuple of the new shape (new_rows, new_cols).
    
    Returns:
    - stack_rebinned: 3D array with the rebinned arrays in dimensions 1/2.
    """
    n_images = stack.shape[0]
    stack_reshaped = np.empty( (n_images, new_shape[0], new_shape[1]) )
    for k in prange( n_images ):
        stack_reshaped[k] = rebin_2d_weighted( stack[k], new_shape )
    return stack_reshaped

@njit
def rebin_2d_weighted(array, new_shape):
    """
    Rebin a 2D array to a new shape using a weighted average of the corresponding regions.
    
    Parameters:
    - array: Input 2D array (original shape).
    - new_shape: Tuple of the new shape (new_rows, new_cols).
    
    Returns:
    - rebinned_array: Rebinned 2D array with weighted averages.
    """
    original_shape = array.shape
    orig_rows, orig_cols = original_shape
    new_rows, new_cols = new_shape
    
    # Calculate the scaling factors (step size in each dimension)
    row_scale = orig_rows / new_rows
    col_scale = orig_cols / new_cols

    # Create an empty rebinned array
    rebinned_array = np.zeros((new_rows, new_cols))

    for i in range(new_rows):
        for j in range(new_cols):
            # Determine the range of pixels in the original array that contribute to the new bin
            row_start = i * row_scale
            row_end = (i + 1) * row_scale
            col_start = j * col_scale
            col_end = (j + 1) * col_scale

            # Find the indices of the original array that overlap with the new bin
            row_indices = np.arange(int(np.floor(row_start)), int(np.ceil(row_end)))
            col_indices = np.arange(int(np.floor(col_start)), int(np.ceil(col_end)))

            # Accumulate weighted sum over these indices
            weight_sum = 0
            value_sum = 0
            for r in row_indices:
                for c in col_indices:
                    # Compute the overlap (weight) for each pixel
                    row_overlap = min(row_end, r + 1) - max(row_start, r)
                    col_overlap = min(col_end, c + 1) - max(col_start, c)
                    weight = row_overlap * col_overlap

                    # Add the contribution to the weighted sum
                    value_sum += array[r, c] * weight
                    weight_sum += weight

            # Assign the weighted average to the rebinned array
            rebinned_array[i, j] = value_sum / weight_sum

    return rebinned_array

def import_data_1d( path, pattern, mod:model,
                geo_path='input/geometry.py',
                flip_fov=False, use_ion=True ):

    geo = import_module_from_path('geometry', geo_path)
    # get the images that show the sample
    scanmask = mod.Beams[:,:,0].astype(bool)                           ###########

    print('Starting data import')
    print('\tLoading integrated data from files')
    t0=time()
    airscat, ion = [], []
    filelist = sorted( os.listdir( os.path.join(path,'data_integrated_1d')) )
    filelist = [s for s in filelist if pattern in s]#[:2]
    t1=time()
    for g, file in enumerate( filelist ):
        # Read data from integrated file
        with h5py.File(os.path.join(path, 'data_integrated_1d', file),'r') as hf:
            q_in = ( hf['radial_units'][0] ).astype(data_type)
            fov = ( hf['fov'][()] ).astype(np.int32)
            d = np.array(hf['cake_integ'])[()]
            if 'ion' in hf:
                ion.append(hf['ion'][()])

        if flip_fov:
            fov = np.flip( fov )
            
        if ion and use_ion:
            # print('\tRescale by beam intensity')
            d = _rescale( d, ion[g] )

        ## Reshaping in function of scanning mode ###
        # Base code written for column scan
        d = d.reshape( *fov, d.shape[1] )
        
        if 'line' in geo.scan_mode:
            fov = np.flip( fov )
            d = np.transpose( d, axes=(1,0,2)) 

        # reorder data so that they are all treated the same in the model
        if 'snake' in geo.scan_mode:
            # Flip every second row
            for ii in range(d.shape[0]):
                if ii % 2 != 0:
                    d[ii] = d[ii][::-1]
        ##############################################

        i0=d.shape[-1]//4
        # get airscattering:
        edge_sample = np.array([ 
            d[0,0,i0:].mean(), 
            d[0,-1,:,i0:].mean(), 
            d[0,-fov[1]//2,:,i0:].mean(),  
            d[fov[0]//2,0,i0:].mean(), 
            d[fov[0]//2,-1,:,i0:].mean(), 
            d[-1,0,:,i0:].mean(), 
            d[-1,-fov[1]//2,:,i0:].mean(),
            d[-1,-1,:,i0:].mean()
            ]) 
        airscat.append( np.min( edge_sample[edge_sample > 0.] ))
        if not ion or not use_ion:
            # print('\tRescale by air scattering')
            d /= airscat[g]

        max_shape = mod.fov
        # pad the data as in mumottize
        # fill projections with air scattering
        proj =  np.random.normal(airscat[g],np.sqrt(airscat[g])/2,(*max_shape, d.shape[2]))
        si, sj = d.shape[:2]
        i0 = (max_shape[0] - si)//2
        j0 = (max_shape[1] - sj)//2
        proj[i0:i0+si, j0:j0+sj] = d
        proj = proj.reshape(max_shape[0]*max_shape[1], *q_in.shape)

        scanmask_g = scanmask[g].copy()
        proj = _remove_crazypixels_1d(proj, scanmask_g)

        out_path = os.path.join( path, 'analysis', 'data_1drec.h5')
        if g == 0:
            print('\tSaving data to file: %s' % out_path)
            with h5py.File( out_path, 'w') as hf:
                hf.create_dataset( 'data',
                        shape=(0, proj.shape[1]),
                        maxshape=(None, proj.shape[1]),
                        chunks=(1, proj.shape[1]),
                        dtype='float64'
                    )
                hf.create_dataset( 'radial_units', data = q_in )

        # add data to h5 file
        with h5py.File( out_path, 'r+') as hf:
            dset = hf['data']
            current_rows = dset.shape[0]
            new_rows = current_rows + proj.shape[0]
            dset.resize( new_rows, axis=0)
            dset[current_rows:new_rows, :] = proj


        t_it = (time()-t1)/(g+1)
        Nrot = len(filelist)
        sys.stdout.write(f'\r\t\tProjection {(g+1):d} / {Nrot:d}, t/proj: {t_it:.1f} s, t left: {((Nrot-g-1)*t_it/60):.1f} min' )
        sys.stdout.flush()

    ion_av = np.array( [i.mean() for i in ion] ) # cannon write ion directly because shape
    gt_mask = np.array( np.where(scanmask) ).T
    # add metadata to h5 file
    with h5py.File( out_path, 'r+') as hf:
        hf.create_dataset( 'scanmask', data=scanmask )
        hf.create_dataset( 'gt_mask', data=gt_mask )
        hf.create_dataset( 'airscat', data = airscat )
        hf.create_dataset( 'ion', data = ion_av )
        hf.create_dataset( 'q', data=q_in)

    print(f'\t\ttook {time()-t0:.2f} s')

@njit(parallel=True)
def _remove_crazypixels_1d( projection, scanmask ):
    dat_new = projection.copy()
    for k in prange(projection.shape[0]):
        if scanmask[k]:
            for m in range(-1,projection.shape[1]-1):
                sample = np.array([
                    projection[k,m-2],projection[k,m-1],projection[k,m+1],projection[k,m+2]
                ])
                base = np.median(sample)
                if projection[k,m] > 10*np.abs(base):
                    dat_new[k,m] = base
    return dat_new