import os, glob, sys, shutil
os.environ["MKL_NUM_THREADS"] = "1" 
os.environ["NUMEXPR_NUM_THREADS"] = "1" 
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
import h5py, hdf5plugin
import matplotlib.pyplot as plt
from importlib import reload # this is to reload
import imageio.v3 as iio
from time import time
from typing import Union, Optional
from numba import njit, prange
import orix.quaternion.symmetry as osym 


# domestic
from . import handle as hdl
from . import hsh
from . import rotation as rot
from . import symmetries as sym
from . import mask as msk
from . import orix_plugins as orx
from .model import model
from .misc import meshgrid, integrate_c, erf, cp_addno, import_module_from_path
from . import model_crystal as cry
from ..config import data_type
from .gridbased import fisher_SO3, gaussian_SO3

# sample_dir = '/Users/moritz/Documents/papers/benchmark/gen_sample/'

def setup_generated_sample(sample_dir):
    os.makedirs(os.path.join(sample_dir,'analysis'), exist_ok=True)
    os.makedirs(os.path.join(sample_dir,'data_integrated'), exist_ok=True)

    gen_path = os.path.join(sample_dir,'analysis','generation.py')
    gen = import_module_from_path('generation', gen_path)

    # save alignment file for projectors
    tomogram=gen.sample_mask.astype(data_type)
    with h5py.File(os.path.join(sample_dir,'analysis','alignment_result.h5'),'w') as hf:
        hf.create_dataset('kappa', data=gen.kappa)
        hf.create_dataset('omega', data=gen.omega)
        hf.create_dataset('shifts', data=np.zeros((gen.kappa.size,2)))
        hf.create_dataset('tomogram', data=tomogram)
        hf.create_dataset('sinogram', data=[])    

    with open(os.path.join(sample_dir,'analysis','voxelmask.txt'), 'w') as fid:
        for iv in np.where(gen.sample_mask.flatten())[0]:
            fid.write(f'{iv}\n')      
    
    return gen

def setup_grid(resolution, symmetry):
    
    pg = getattr( osym, sym.get_SFnotation( symmetry ) )
    q_odf = rot.get_sample_fundamental(
                resolution,
                point_group= pg,
                method='cubochoric'
        ).data.astype(data_type)
    n_basis_functions = q_odf.shape[0]
    # kappa = 5* 1/(resolution*np.pi/180)**2
   
    # show sampling
    orx.plot_points_in_fz(q_odf,symmetry,title='Centers of the basis functions')
    return n_basis_functions, q_odf

def save_projections(sample_dir, mod:model):
    # gen_path = os.path.join(sample_dir,'analysis','generation.py')
    # gen = import_module_from_path('generation', gen_path)

    # n_basis_functions, q_odf = setup_grid(gen.grid_resolution, mod.symmetry)
    # generators = sym.generators(mod.symmetry)

    # # set up sample coefficients
    # sample_bf_coefficients = np.zeros((np.prod(mod.nVox), n_basis_functions), data_type)
    # flatmask = np.where(mod.mask_voxels.flatten())[0]
    # for v in flatmask:
    #     i_dir = np.random.randint(n_basis_functions)
    #     sample_bf_coefficients[v,i_dir] = 1
    
    # Qs = rot.QfromOTP( mod.Gs )
    # Qc = rot.QfromOTP( mod.Gc )

    # for g in range(mod.Beams.shape[0]):
    #     diff_patterns_g = projection( 
    #         Qc, mod.Isc, Qs, mod.Beams, mod.iBeams, mod.detShape, mod.dV,
    #         sample_bf_coefficients, q_odf, gen.grid_resolution, generators )
    
    # set up sample coefficients
    n_basis_functions = mod.difflets.shape[1]
    sample_bf_coefficients = np.zeros((np.prod(mod.nVox), n_basis_functions), data_type)
    flatmask = np.where(mod.mask_voxels.flatten())[0]
    for v in flatmask:
        i_dir = np.random.randint(n_basis_functions)
        sample_bf_coefficients[v,i_dir] = 1

    for g in range(mod.Beams.shape[0]):
        diff_patterns_g = mod.projection( g, sample_bf_coefficients )
        with h5py.File(os.path.join(sample_dir,'data_integrated',f'gen_sample_proj{g:03d}.h5'), 'w') as hf:
            hf.create_dataset('cake_integ', data=diff_patterns_g)        
            hf.create_dataset('fov', data=mod.fov)
            hf.create_dataset('radial_units', data=mod.Qq_det.reshape(mod.detShape)[0])
            hf.create_dataset('azimuthal_units', data=mod.Chi_det.reshape(mod.detShape)[:,0])
    with h5py.File(os.path.join(sample_dir,'data_integrated','sample_coefficients.h5'), 'w') as hf:
        hf.create_dataset('coefficients', data=sample_bf_coefficients)

# @njit(parallel=True)
def projection( Qc, Isc, Qs, Beams, iBeams, detShape, dV, 
               sample_bf_coefficients, q_odf, resolution, gen ):
    diff_patterns_g = np.empty((Beams.shape[1],detShape[0],detShape[1]), data_type)
    for t in prange(Beams.shape[1]):
        # project the coefficients
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        c_proj = integrate_c( Beams[g,t,:iend], iBeams[g,t,:iend], sample_bf_coefficients )
        # get the resulting odf from rotated mu
        odf_proj = np.zeros( Qc.shape[0], data_type )
        idcs_basis = np.nonzero(c_proj > 0.01 * c_proj.max())[0]
        for c in idcs_basis:
            q_mu = rot.quaternion_multiply(  q_odf[c], Qs[g] )
            odf_proj += c_proj[c] * gaussian_3d(Qc, q_mu, resolution*np.pi/180, gen, dV )
        # sparse calculate the projections (only points in odf that are high)
        diff_pattern = np.zeros(Isc.shape[1], data_type)
        idcs_odf = np.nonzero(odf_proj> 0.01 * odf_proj.max())[0]
        for h in idcs_odf:
            diff_pattern += Isc[h] * odf_proj[h]
        diff_patterns_g[t] = diff_pattern.reshape((detShape[0],detShape[1]))
    return diff_patterns_g

def plot_basefunction_texture(resolution, mod, g_center=(0,0,0)):
    
    q_center = rot.QfromOTP(np.atleast_2d(g_center)).flatten()
    Qc = rot.QfromOTP( mod.Gc )
    generators = sym.generators(mod.symmetry)
    q_gen = rot.QfromOTP(generators)
    Q_group = rot.generate_group(q_gen)

    # show the center of the distribution
    orx.plot_points_in_fz(q_center,mod.symmetry)
    plt.title('mean')
    # plot gaussian distribution
    # odf = fisher_SO3(Qc,q_center,10/(resolution*np.pi/180)**2,Q_group)
    odf = gaussian_SO3(Qc, q_center, resolution*np.pi/180, Q_group)

    # orx.odf_cloud_general(mod.Gc,
    #     gaussian_3d(Qc,q_center,resolution*np.pi/180,generators,1),
    #     mod.symmetry,num_samples=1000)
    # plt.title('gauss')
    # plot fisher distribution
    orx.odf_cloud_general(mod.Gc,
        odf,
        mod.symmetry,
        )
    # plt.title('fisher')
    # plot a polefigure
    orx.plot_pole_figure_from_odf(mod.Gc,odf,
                    mod.symmetry, hkl=(1,0,0) )
    orx.plot_pole_figure_from_odf(mod.Gc,odf,
                    mod.symmetry, hkl=(0,1,0) )
    orx.plot_pole_figure_from_odf(mod.Gc,odf,
                    mod.symmetry, hkl=(0,0,1) )
