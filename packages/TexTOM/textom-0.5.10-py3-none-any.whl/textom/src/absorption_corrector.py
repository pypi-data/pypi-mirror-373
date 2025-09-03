import os, sys
import numpy as np
from time import time
import matplotlib.pyplot as plt
import h5py
from numba import njit, prange

# import textom.src.rotation as rot
# from textom.input import geometry as geo
# from textom.config import data_type

from . import rotation as rot
# from ..input import geometry as geo
from .model import model
from .data import mask_peak_regions, make_detector_mask
from .misc import import_module_from_path
from . import mask as msk
from ..config import data_type # azimuthal binning on the detector

def absorption_correction( sample_dir, mod:model, absorption_tomogram=False, absorption_constant_voxel=False ):

    qmask_path = os.path.join(sample_dir,'analysis','peak_regions.txt')
    detmask_path = os.path.join(sample_dir,'analysis','fit_detmask.txt')
    geo = import_module_from_path('geometry', os.path.join(sample_dir,'analysis','geometry.py'))

    scanmask = mod.Beams[:,:,0].astype(bool)     
    if not (absorption_constant_voxel or absorption_tomogram):
        print('Provide either absorption tomogram or absorption constant')
        return 0
    elif absorption_constant_voxel:
        absorption_tomogram = np.zeros_like(mod.tomogram).flatten()
        absorption_tomogram[mod.mask_voxels] = absorption_constant_voxel
        absorption_tomogram = absorption_tomogram.reshape(mod.nVox)

    # load peak regions from file or create them by user input
    filelist = sorted( os.listdir( os.path.join(sample_dir,'data_integrated')) )
    filelist = [s for s in filelist if '.h5' in s]#[:2]
    with h5py.File(os.path.join(sample_dir, 'data_integrated', filelist[0]),'r') as hf:
        q_in = np.squeeze(hf['radial_units'][()] ).astype(data_type)
        chi_in = np.squeeze( hf['azimuthal_units'][()]*np.pi/180 ).astype(data_type)
        d = ( np.array(hf['cake_integ'][()]) ).astype(data_type)
        # get pseudo powder diffraction pattern
    powder_2D = d[scanmask[0]].sum(axis=0)
    powder_1D = powder_2D.mean(axis=0)

    # load peak regions from file or create them by user input
    peak_reg, _, q_mask_k, _, _, q_peaks, t_inter_1 = mask_peak_regions( 
        sample_dir, mod, q_in, powder_1D, qmask_path) 

    # # load the detector mask from file or create it by user input
    # powder_2D_masked = np.array([powder_2D[:,qm].sum(axis=1) for qm in q_mask_k])
    # mask_detector, t_inter_2 = make_detector_mask( 
    #     sample_dir, detmask_path, powder_2D_masked, peak_reg, q_in, chi_in )
    ## might only calculate the not masked ones but for now lets leave it like this

    # calculate scattering angles
    q_peaks = np.mean(peak_reg, axis=1)
    lam = 1.239842 / mod.E_keV # wavelength in nm
    two_theta = 2 * np.arcsin( q_peaks*lam / (4*np.pi) )

    azimuthal_angles = mod.Chi_det[:mod.detShape[1]]

    print('\tCalculating absorption patterns')
    t1 = time()
    # g,t = 0, 13740
    # g,t = 171, 19641
    ng, nt, _ = mod.iBeams.shape
    absorption_patterns = np.zeros( (ng, nt, azimuthal_angles.size, two_theta.size), data_type )
    for g in range(ng):
        # rotate direction vectors
        beam_direction_g = geo.beam_direction @ rot.OTP_to_matrix(mod.Gs[g,0],mod.Gs[g,1],mod.Gs[g,2])
        detector_direction_origin_g = geo.detector_direction_origin @ rot.OTP_to_matrix(mod.Gs[g,0],mod.Gs[g,1],mod.Gs[g,2])
        detector_direction_positive_90_g = geo.detector_direction_positive_90 @ rot.OTP_to_matrix(mod.Gs[g,0],mod.Gs[g,1],mod.Gs[g,2])
 
        absorption_patterns[g] = absorption_patterns_projection(
            absorption_tomogram, mod.x_p, mod.iBeams[g],
            np.array(beam_direction_g), np.array(detector_direction_origin_g), np.array(detector_direction_positive_90_g),
            azimuthal_angles, two_theta
        )

        t_it = (time()-t1)/(g+1)
        sys.stdout.write(f'\r\t\tProjection {(g+1):d} / {ng:d}, t/proj: {t_it:.1f} s, t left: {((ng-g-1)*t_it/60):.1f} min' )
        sys.stdout.flush()
    
    path_out = os.path.join(sample_dir,'analysis','absorption_patterns.h5')
    print(f'\tSaving dat to {path_out}')
    with h5py.File(path_out, 'w') as hf:
        hf.create_dataset('absorption_patterns', 
                          data=absorption_patterns, 
                          compression="lzf")

    
@njit(parallel=True)
def absorption_patterns_projection(
    absorption_tomogram, coordinates, iBeams_g,
    beam_direction_g, detector_direction_origin_g, detector_direction_positive_90_g,
    azimuthal_angles, two_theta, 
    ):

    nt = iBeams_g.shape[0]
    absorption_patterns_g = np.zeros( (nt, azimuthal_angles.size, two_theta.size), data_type )
    for t in prange(nt):
        iBeam = iBeams_g[t][iBeams_g[t] < 2**32-1]
        if iBeam.size:
            p_beam = coordinates[iBeam]
            entry_point = np.argmin( np.sum(p_beam * _tile_1d_nb(beam_direction_g,p_beam.shape[0]), axis=1) ) 
                # np.sum(p_beam * np.tile(beam_direction_g,(p_beam.shape[0],1)), axis=1) ) 
                # p_beam @ beam_direction_g )
                # argmin might be off by a pixel or so, could refine it by taking the
                # highest value around this point

            # entry_point = np.array([0,0,0] # tip of the cone
            # entry_point = np.array([-0.1,20,5]) # tip of the cone
            
            absorption_pattern = np.empty((azimuthal_angles.size,two_theta.size), data_type)
            for q, twotheta in enumerate(two_theta): # cone angle ~ 2theta
                for c, chi in enumerate(azimuthal_angles):
                    absorption_pattern[c, q] = integrate_paths(
                        absorption_tomogram,
                        entry_point, beam_direction_g, twotheta, chi, 
                        detector_direction_origin_g, detector_direction_positive_90_g
                    )
                    # absorption_pattern[q,c] = integrate_middle_path(
                    #     tomogram, entry_point, np.array(beam_direction), twotheta, chi, 
                    #     np.array(detector_direction_origin), np.array(detector_direction_positive_90)
                    # )
            absorption_patterns_g[t] = absorption_pattern
    return absorption_patterns_g

@njit
def cone_wedge_to_cartesian(h, r, theta, tip, axis, origin_vec, pos_dir_vec):
    """
    Convert cone wedge coordinates (h, r, theta) to Cartesian coordinates.
    """
    # Compute position in local frame
    point = tip + h * axis + r * (np.cos(theta) * origin_vec + np.sin(theta) * pos_dir_vec)
    return point

@njit
def sample_paths( h, tip, axis, opening_angle, chi, origin_vec, pos_dir_vec, dV ):
    dr = dV**(1/3)
    zz = np.arange(0,h,dr) # start value for each path
    pp = np.arange(0,h/np.cos(opening_angle),dr) # path variable
    paths = np.zeros( (zz.size, pp.size, 3 ), np.int32 )
    for z in range(zz.size):
        z_p = pp * np.cos(opening_angle) + zz[z]
        r_p = pp * np.sin(opening_angle)
        for p in range(pp.size):
            xyz = cone_wedge_to_cartesian(z_p[p], r_p[p], chi, tip, axis, origin_vec, pos_dir_vec)
            paths[z,p] = np.round(xyz)
        # paths.append(np.array([
        #     cone_wedge_to_cartesian(z, r, t, tip, axis, origin_vec, pos_dir_vec) for z,r,t in
        #     zip(z_p, r_p, chi*np.ones_like(z_p))]))
    return paths

@njit
def integrate_paths(grid, cone_tip, cone_axis, opening_angle, chi, origin_vec, pos_dir_vec,
                   dV=1):
    """
    Perform an integration over a cone wedge by sampling points equal-volume
    """
    h = np.sqrt(grid.shape[0]**2+grid.shape[2]**2)# max length of the cone
    paths = sample_paths( h, cone_tip, cone_axis, opening_angle, chi, origin_vec, pos_dir_vec, dV )
    path_ints = np.zeros( paths.shape[0], data_type )
    for p in range(paths.shape[0]):
        for point in paths[p]:
            if np.all( point >= np.zeros_like(point) ) and np.all( point < np.array(grid.shape) ):
                path_ints[p] += grid[point[0],point[1],point[2]]         
    return np.mean(path_ints)

@njit
def _tile_1d_nb(a, n):
    # numba-optimized function to c
    # Create an output array of the desired shape
    out = np.empty((n, len(a)), data_type)
    
    # Fill the output array with repeated values from a
    for i in range(n):
        out[i] = a
    
    return out

# the following seems too much of an approximation
""" 
def middle_path( h, tip, axis, opening_angle, chi, origin_vec, pos_dir_vec, dV ):
    # to calculate the middle i should actually take it out of iBeams
    dr = dV**(1/3)
    p = np.arange(0,h/np.cos(opening_angle),dr) # path variable
    z_p = p * np.cos(opening_angle) + h/2 # z_middle
    r_p = p * np.sin(opening_angle)
    middle_path = np.array([
            cone_wedge_to_cartesian(z, r, t, tip, axis, origin_vec, pos_dir_vec) for z,r,t in
            zip(z_p, r_p, chi*np.ones_like(z_p))])
    return middle_path

def integrate_middle_path(grid, cone_tip, cone_axis, opening_angle, chi, origin_vec, pos_dir_vec,
                   dV=1):
    h = np.sqrt(grid.shape[0]**2+grid.shape[2]**2)# max length of the cone
    path = middle_path( h, cone_tip, cone_axis, opening_angle, chi, origin_vec, pos_dir_vec, dV )
    path_int = 0.
    points = np.round(path).astype(np.int64)
    for p in points:
        if np.all( p >= np.zeros_like(p) ) and np.all( p < np.array(grid.shape) ):
            path_int += grid[p[0],p[1],p[2]]
    return path_int
    """
# tomogram = np.ones((40,40,10), np.float64)
# nchi = 30
# Chi = np.linspace(0,2*np.pi, num=nchi, endpoint=False) + 2*np.pi/nchi/2
# Q = np.linspace(10, 35, num=10, endpoint=False) # nm^-1
# lam = 0.0826565
# two_theta = 2 * np.arcsin( Q*lam / (4*np.pi) )
# Gs = np.array([[0,0,0]])
# # Gs = np.array([[np.pi/4,np.pi/2,np.pi/2]])
# Gs = np.array([[0.7,0.2,0.3]])

# absorption_pattern = absorption_correction(tomogram,0,
#                                 two_theta,Chi,Gs,0)
# # print(absorption_pattern)
# CHi, QQ = np.meshgrid( Chi, Q )
# X1 = -QQ*np.sin(CHi)
# X2 = QQ*np.cos(CHi)
# m = plt.pcolormesh( X1, X2, absorption_pattern, cmap='plasma', vmin=0, vmax=absorption_pattern.max() )
# plt.axis('equal')
# plt.grid(False)
# plt.colorbar(m)

# # points = sample_cone_wedge(30, np.array([0,0,0]), np.array([1,0,0]), np.pi/6, 
# #                                       0, np.pi/6, np.array([0,0,1]), np.array([0,-1,0]), 2)
# # print(points.shape)
# # fig = plt.figure()#figsize=(10, 10))
# # ax = fig.add_subplot(111, projection='3d')
# # ax.scatter(points[:,0],points[:,1],points[:,2])

# plt.show()