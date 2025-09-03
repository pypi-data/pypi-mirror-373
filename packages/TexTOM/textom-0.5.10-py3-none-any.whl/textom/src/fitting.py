import os
import numpy as np
from time import time
import h5py

# domestic
from .misc import sparsemult, integrate_c
from ..config import data_type
from .model import model
from .exceptions import dimension_error

from numba import njit, prange
import warnings
from numba.core.errors import NumbaDeprecationWarning, NumbaPerformanceWarning
warnings.simplefilter('ignore', category=NumbaPerformanceWarning)

class fitting:
    """ A class to that contains loss function and gradients for fitting
    texture tomography data

    Takes input from a model and a data class object or a previously saved 'fit' pickle
    """
    def __init__(self, path, mod:model, rec1d=False ):
        """

        Parameters
        ----------
        dat : data class object or str
            if string it needs to be a 'fit'-pickle name
        mod : model class object
            only required if no pickle is loaded
        
        Attributes created
        ------------

        """
        print('Initialize Fit')
        datafile = 'data_1drec.h5' if rec1d else 'data_textom.h5'
        # import stuff from data and mod objects
        t0=time()
        with h5py.File( os.path.join(path,'analysis',datafile), 'r') as hf:
            self.data = hf['data'][()].astype(data_type)
            self.scanmask = hf['scanmask'][()]
            self.gt_mask = hf['gt_mask'][()]
            if not rec1d:
                self.peak_reg = hf['peak_reg'][()]
                self.q = hf['q']
            # self.mask_detector = hf['mask_detector'][()]
        print('\tLoaded Data')

        self.mask_detector = np.genfromtxt(os.path.join(path,'analysis','fit_detmask.txt'),bool)
        
        # ######### do check if the test for changing detector angle direction
        # nD = self.data.shape[0]
        # dat_int = np.zeros( (nD,self.mask_detector.size), data_type )
        # # for k in range(self.data.shape[0]):
        # dat_int[:,self.mask_detector] = self.data
        # dat_int2 = dat_int.reshape((nD, *self.detShape))
        # self.mask_detector = np.flip(self.mask_detector)
        # dat_int3 = np.flip(dat_int2,axis=2).reshape(dat_int.shape)[:,self.mask_detector]
        # self.data = dat_int3        
        # #########

        self.kap_zero = np.where(mod.Kappa == 0)[0]
        ## initial guess for c0 from tomogram
        tomogram = mod.tomogram.flatten()/mod.tomogram.max() # normalize so c0 will be around 1
        tomogram[tomogram<0] = 0

        self.classic = mod.classic
        if mod.classic:
            self.C = np.zeros((tomogram.size,1), data_type)
            self.C[mod.mask_voxels, 0] = tomogram[mod.mask_voxels] # initial guess for c0
        else:
            self.C = np.zeros((tomogram.size,mod.difflets.shape[1]),data_type)
        self.ns=[0]
        self.title, self.Beams, self.iBeams = mod.title, mod.Beams, mod.iBeams

        if not rec1d:
            ## renormalize the model
            g,t,_ = np.unravel_index(np.argmax(mod.Beams),mod.Beams.shape)
            iend = np.searchsorted( mod.iBeams[g, t, :],2**32-1 ) # for sparsearray
            T = sparsemult( 
                mod.Beams[g, t, :iend], 
                mod.iBeams[g, t, :iend], tomogram )
            # the simulated intensity will be multiplied by this to have C~O(1)
            gt_dat = np.argmin( np.linalg.norm(self.gt_mask - np.array([g,t]), axis=1) )
            self.sim_fac = self.data[gt_dat].max()/mod.difflets[0].max() / T
            if mod.classic:
                # self.difflet0_1D = mod.difflets[0].reshape(mod.detShape)[:,0] # not used
                self.set_orders(mod, 0, info=False)
            else:
                self.difflets_rot_masked = mod.difflets.reshape(
                    mod.difflets.shape[0],mod.difflets.shape[1],
                    mod.difflets.shape[2]*mod.difflets.shape[3]
                    )[:,:,self.mask_detector]

            # self.q = mod.Qq_det.reshape(mod.detShape)[:,0] # 1D q-vector
            self.q = np.array([qr.mean() for qr in self.peak_reg])
            try:
                self.chi = mod.Chi_det.reshape(mod.detShape)[0]
            except:
                self.chi = mod.chi

        self.choose_projections(info=False)

    def prepare_fit_c0( self, peak=None ):
        """ Calculates 0-dimensional data for fast estimation of the zero order 
        
        Parameters
        ----------
        peak : int or None
            index of the peak you want to use for 0-order fitting (should be as
            isotropic as possible), if None uses the whole dataset, default None
        """
        if peak:
            peak_start_idx = self.mask_detector[:peak*self.detShape[1]].sum()
            peak_end_idx = self.mask_detector[:(peak+1)*self.detShape[1]].sum()
            self.total_im = self.data[:,peak_start_idx:peak_end_idx].sum(axis=1) # total peak intensity for each image
            self.data_0D = self.total_im / self.difflets_rot_masked[0,0,peak_start_idx:peak_end_idx].sum() 
        else:
            self.total_im = self.data.sum(axis=1) # total intensity for each image
            # self.total_proj = self.total_im.sum(axis=1) # total intensity for each projection
            self.data_0D = self.total_im / self.difflets_rot_masked[0,0].sum() 

    def adjust_data_scaling( self ):
        """Reestimates the data based on the assumption that normalization constants
        contain noise. To be used after fitting the 0th order
        """
        print('\tAdjusting data scaling')
        self.prepare_fit_c0()
        # scal = self.insert_fov( self.projections_c0( self.C ) 
        #             ).sum(axis=1) / self.insert_fov( self.data_av ).sum(axis=1)
        # self.data_scal = np.tile(scal,(self.Beams.shape[1],1)).T[self.scanmask]
        # self.data = np.array( [s*d for s,d in zip(self.data_scal,self.data)])
        self.data_scal = self.projections_c0( self.C ) / self.data_0D
        self.data *= self.data_scal[:,np.newaxis]
        self.prepare_fit_c0()

    def projections_c0( self, C ):
        """ Wrapper for a numba-compiled function projecting the 0-order 
        coefficients and give a single value per pixel

        Parameters
        ----------
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index

        Return values
        ------------
        loss : float
        """
        proj_c0 = _projections_c0( C,
            self.gt_mask,
            self.Beams, self.iBeams, 
            )
        return proj_c0

    def set_orders( self, mod:model, n_max, info=True, exclude_ghosts=True ):
        """ Changes the HSH order

        Calculates diffractlets and updates the fit object
        using functions in the model class

        Parameters
        ----------
        mod : model class object
        n_max : int
            highest HSH order for fitting
        """
        mod.set_orders( n_max, info=info, exclude_ghosts=exclude_ghosts )
        c_tmp = self.C
        self.update_mod(mod)
        if self.C.shape[1] >= c_tmp.shape[1]:
            self.C[:,:c_tmp.shape[1]] = c_tmp
        else:
            self.C = c_tmp[:,:self.C.shape[1]]
        
    def update_mod(self, mod:model):
        """ Imports stuff from the model class

        Parameters
        ----------
        mod : model class object
        """
        self.Sn = mod.Sn
        self.ns = mod.ns
        # update diffractlets:
        difflets_full = mod.difflets.reshape((mod.difflets.shape[0],*mod.detShape))
        # regroup diffractlets into peaks, rotate and mask them
        difflets = np.empty( (mod.difflets.shape[0], self.mask_detector.sum()), data_type )
        self.detShape = (self.peak_reg.shape[0], mod.detShape[1])
        q_det = mod.Qq_det.reshape(mod.detShape)[:,0]
        for l, dlet in enumerate(difflets_full):
            dlet_tmp = np.empty( self.detShape, data_type)
            for k, reg in enumerate(self.peak_reg):
                mask_reg = ((q_det >= reg[0]) & (q_det <= reg[1]))
                dlet_tmp[k] = dlet[mask_reg].sum(axis=0)
            try:
                difflets[l] = dlet_tmp.flatten()[self.mask_detector]
            except:
                raise dimension_error('Check if No of peak regions x No of azimuthal bins agree with the detector mask size')
        self.difflets_rot_masked = (_rotate_difflets_stack(mod.Rs, difflets) * self.sim_fac).astype(data_type)

        self.C = np.zeros((mod.x_p.shape[0], mod.difflets.shape[0]), data_type)
        # print('\tupdated fit object')

    def choose_projections(self, mode='full', info=True):
        """ Decides which sample rotations to use for fitting

        Parameters
        ----------
        mode : str
        """
        # Choose projections:
        Ng0 = self.Beams.shape[0] # total number of rotations
        if mode=='notilt': # only kappa = 0
            self.chosen_proj = self.kap_zero
        elif mode=='half': # every second
            self.chosen_proj = range(0,Ng0,2)
        elif mode=='third': # every third
            self.chosen_proj = range(0,Ng0,3)
        elif mode=='asnotilt': # equidistant, as many as at kappa = 0
            n = self.kap_zero.size
            self.chosen_proj = np.arange(0,Ng0,int(Ng0/n))[:n]
        else: # all of them
            self.chosen_proj = range(Ng0)
        tmp_scanmask = self.scanmask.copy()
        mask = np.full_like(tmp_scanmask, False)
        mask[self.chosen_proj,:]=True
        tmp_scanmask[~mask] = False
        self.gt_mask = np.transpose(np.where(tmp_scanmask))
        if info:
            print('Choose projections: %s' % mode)

    def loss( self, C ):
        """ Wrapper for a numba-compiled function calculating the loss function

        Parameters
        ----------
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index

        Return values
        ------------
        loss : float
        """
        loss = _loss( C,
            self.data, self.gt_mask,
            self.Beams, self.iBeams, 
            self.difflets_rot_masked,
            )
        return loss

    def loss_c0( self, C ):
        """ Wrapper for a numba-compiled function calculating the loss function
        using only the zero-order coefficients compared to the averaged images

        Parameters
        ----------
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index

        Return values
        ------------
        loss : float
        """
        loss = _loss_c0( C,
            self.data_0D, self.gt_mask,
            self.Beams, self.iBeams, 
            )
        return loss
    
    def grad_full( self, C ):
        """ Wrapper for a numba-compiled function calculating the gradient
        of the loss function for all sHSH coefficients

        Parameters
        ----------
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index

        Return values
        ------------
        grad : 2D ndarray, float
            gradient for all the sHSH coefficients
            dim: 0: voxel index, 1: sHSH index
        """
        grad = _grad_full( C,
            self.data, self.gt_mask,
            self.Beams, self.iBeams, 
            self.difflets_rot_masked,
            )
        return grad

    def grad_highest( self, C ):
        """ Wrapper for a numba-compiled function calculating the gradient
        of the loss function for the highest order sHSH coefficients 

        Parameters
        ----------
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index

        Return values
        ------------
        grad : 2D ndarray, float
            gradient for all the sHSH coefficients
            dim: 0: voxel index, 1: sHSH index
        """            
        grad = _grad_highest( C,self.Sn[-1],   
            self.data, self.gt_mask,
            self.Beams, self.iBeams, 
            self.difflets_rot_masked,
            )
        return grad
    
    def grad_allbut0( self, C ):
        """ Wrapper for a numba-compiled function calculating the gradient
        of the loss function for all but 0-order sHSH coefficients 

        Parameters
        ----------
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index

        Return values
        ------------
        grad : 2D ndarray, float
            gradient for all the sHSH coefficients
            dim: 0: voxel index, 1: sHSH index
        """            
        grad = _grad_allbutC0( C,self.Sn[1:],   
            self.data, self.gt_mask,
            self.Beams, self.iBeams, 
            self.difflets_rot_masked,
            )
        return grad
    
    def grad_c0( self, C ):
        """ Wrapper for a numba-compiled function calculating the gradient
        of the loss function for the zero order sHSH coefficients from 
        the average image value

        Parameters
        ----------
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index

        Return values
        ------------
        grad : 2D ndarray, float
            gradient for all the sHSH coefficients
            dim: 0: voxel index, 1: sHSH index
        """
        grad = _grad_c0( C,        
            self.data_0D, self.gt_mask,
            self.Beams, self.iBeams, 
            )
        return grad

    def lipschitz( self ):
        """ Wrapper for a numba-compiled function calculating the Lipschitz 
        constant for the zero order sHSH coefficients

        Return values
        ------------
        Lipschitz : 1D ndarray, float
        """
        Lipschitz = _lipschitz_c0( self.C,
            self.gt_mask,
            self.Beams, self.iBeams,
            )
        return Lipschitz   

    def projection( self, g, C, info=True ):
        """ Wrapper for a numba-compiled function calculating a series
        of diffraction pattern corresponding to one sample orientation

        Parameters
        ----------
        g : int
            rotation index
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index

        Return values
        ------------
        images : 2D ndarray, float
            dim 0: translation, 1: detector points
        """
        if info:
            print('\tCalculating projection %d' % g )
        images = _projection(
            C, g, self.scanmask,
            self.Beams, self.iBeams, 
            self.difflets_rot_masked,
        )
        return images

    def image( self, C, g, t ):
        """Simulates a single diffraction image for rotation g and 
        translation t

        Parameters
        ----------
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index
        g : int
            rotation index
        t : int
            translation index
        Return values
        ------------
        image : 1D ndarray, float
        """
        iend = np.searchsorted(self.iBeams[g,t,:],2**32-1) # for sparsearray
        # get projected coefficients for the corresponding beam rotation/translation
        c_proj = integrate_c( self.Beams[g,t,:iend], self.iBeams[g,t,:iend], C )
        # calculate the image
        image = c_proj @ self.difflets_rot_masked[g] 
        return image

    def MDL( self, loss ):
        """ Calculates the Medium description length for order selection
        
        M. Hansen and B. Yu, ?Model selection and the principle of minimum 
        description length, Journal of the American Statistical Association,
        vol. 96, no. 454, pp. 746-774, 2001.

        Parameters
        ----------
        loss : float

        Return values
        ------------
        MDL : float
        """
        # Calculate the number of datapoints
        # lowmask = np.array(
        #     [beam[0]<2**23-1 for beam_g in self.iBeams for beam in beam_g])
        # im_mask = np.logical_and( lowmask, self.scanmask.flatten() )            
        #     [beam[0]<2**23-1 for beam_g in self.iBeams[self.chosen_proj] for beam in beam_g])
        # im_mask = np.logical_and( lowmask, self.scanmask[self.chosen_proj].flatten() )
        N_images = np.sum( self.scanmask )
        N_data = N_images * self.mask_detector.sum()
        # the number of parameters
        n_par = self.C[self.C[:,0]>0].size
        # calculate the medium description length
        MDL = N_data/2 * np.log(loss) + n_par/2 * np.log(N_data)
        return MDL

    def insert_fov( self, data ):
        d_out = np.zeros_like( self.scanmask, data_type )
        d_out[self.scanmask] = data
        return d_out
    
    def check_orientations( self, g ):

        proj = np.zeros( (self.Beams.shape[1], self.mask_detector.size), data_type )
        proj[:,self.mask_detector] = self.projection( g, self.C, info=False )
        dat = np.zeros_like(proj)
        d_mskd = self.data[ np.where(self.gt_mask[:,0]==g)[0] ]
        for nt, t in enumerate(self.gt_mask[self.gt_mask[:,0]==g][:,1]):
            dat[t,self.mask_detector] = d_mskd[nt]

        ori_dat = np.empty( (self.q.size, self.Beams.shape[1]), data_type )
        ori_fit = ori_dat.copy()
        for i_peak, q in enumerate(self.q):
            chi_hlf = self.chi[:int(self.chi.size/2)]
            ori_dat[i_peak] = _get_mean_ori( dat, self.scanmask[g], i_peak, chi_hlf, self.detShape )
            ori_fit[i_peak] = _get_mean_ori( proj, self.scanmask[g], i_peak, chi_hlf, self.detShape )

        ori_dat[ori_dat==0]=np.nan
        ori_fit[ori_fit==0]=np.nan
        return ori_dat, ori_fit

    def projection_residuals( self, g ):
        proj = self.projection( g, self.C, info=False )
        dat = self.data[ np.where(self.gt_mask[:,0]==g)[0] ]
        res = np.zeros( proj.shape[0], data_type )
        res[self.scanmask[g]] = (( proj[self.scanmask[g]] - dat )**2 ).sum(axis=1)
        return res

@njit(parallel=True)
def _loss( C, data, gt_mask, Beams, iBeams, difflets_rot ): 
    """ Calculates the loss function as the sum of squared residuals

    Parameters
    ----------
    C : 2D ndarray, float
        set of sHSH coefficients for each voxel
        dim: 0: voxel index, 1: sHSH index
    data : 3D ndarray, float
        dim: 0: rotation, 1: translation, 2: detector points
    scanmask : 2D ndarray, bool
        dim: 0: rotation, 1: translation
    Beams : 3D ndarray, float
        sparse-array containing beam intensity for all configurations
        dim: 0: rotation, 1: translation, 2: voxel (sparse)
    iBeams : 3D ndarray, int
        array of indices for the sparse Beams array
        dim: 0: rotation, 1: translation, 2: voxel index
    difflets_rot : 3D ndarray, float
        diffractlets for all sample rotations
        dim: 0: sample rotation, 1: sHSH indices, 2: detector points

    returns: 
    ------------
    loss : float
    """
    loss = 0.0
    for k in prange(gt_mask.shape[0]):
        g,t = gt_mask[k,0], gt_mask[k,1]
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        # get projected coefficients for the corresponding beam rotation/translation
        c_proj = integrate_c( Beams[g,t,:iend], iBeams[g,t,:iend], C )
        # calculate the image
        I_sim = c_proj @ difflets_rot[g] 
        # calculate the squared sum of residuals
        residuals = data[k] - I_sim 
        loss += (residuals**2).sum()# / (data[k]**2).sum()
    return loss

@njit(parallel=True)
def _loss_c0( C, data_av, gt_mask, Beams, iBeams ): 
    """ Calculates the loss function as the sum of squared residuals
    using only the zero-order coefficients compared to the averaged images

    Parameters
    ----------
    C : 2D ndarray, float
        set of sHSH coefficients for each voxel
        dim: 0: voxel index, 1: sHSH index
    data_av : 2D ndarray, float
        dim: 0: rotation, 1: translation
    scanmask : 2D ndarray, bool
        dim: 0: rotation, 1: translation
    Beams : 3D ndarray, float
        sparse-array containing beam intensity for all configurations
        dim: 0: rotation, 1: translation, 2: voxel (sparse)
    iBeams : 3D ndarray, int
        array of indices for the sparse Beams array
        dim: 0: rotation, 1: translation, 2: voxel index

    returns: 
    ------------
    loss : float
    """
    loss = 0.0
    for k in prange(gt_mask.shape[0]):
        g,t = gt_mask[k,0], gt_mask[k,1]
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        # get projected coefficients for the corresponding beam rotation/translation
        c0_proj = sparsemult( Beams[g,t,:iend], iBeams[g,t,:iend], C[:,0] )
        loss += (data_av[k] - c0_proj)**2# / (data_av[k])**2 
    return loss

@njit(parallel=True)
def _projections_c0( C, gt_mask, Beams, iBeams ): 
    """ Calculates the loss function as the sum of squared residuals
    using only the zero-order coefficients compared to the averaged images

    Parameters
    ----------
    C : 2D ndarray, float
        set of sHSH coefficients for each voxel
        dim: 0: voxel index, 1: sHSH index
    scanmask : 2D ndarray, bool
        dim: 0: rotation, 1: translation
    Beams : 3D ndarray, float
        sparse-array containing beam intensity for all configurations
        dim: 0: rotation, 1: translation, 2: voxel (sparse)
    iBeams : 3D ndarray, int
        array of indices for the sparse Beams array
        dim: 0: rotation, 1: translation, 2: voxel index

    returns: 
    ------------
    loss : float
    """
    c0_proj = np.empty(gt_mask.shape[0], data_type)
    for k in prange(gt_mask.shape[0]):
        g,t = gt_mask[k,0], gt_mask[k,1]
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        # get projected coefficients for the corresponding beam rotation/translation
        c0_proj[k] = sparsemult( Beams[g,t,:iend], iBeams[g,t,:iend], C[:,0] )
    return c0_proj

@njit(parallel=True)
def _grad_full( C, data, gt_mask, Beams, iBeams, difflets_rot ): 
    """ Calculates the gradient for all coefficients

    Parameters
    ----------
    C : 2D ndarray, float
        set of sHSH coefficients for each voxel
        dim: 0: voxel index, 1: sHSH index
    data : 3D ndarray, float
        dim: 0: rotation, 1: translation, 2: detector points
    scanmask : 2D ndarray, bool
        dim: 0: rotation, 1: translation
    Beams : 3D ndarray, float
        sparse-array containing beam intensity for all configurations
        dim: 0: rotation, 1: translation, 2: voxel (sparse)
    iBeams : 3D ndarray, int
        array of indices for the sparse Beams array
        dim: 0: rotation, 1: translation, 2: voxel index
    difflets_rot : 3D ndarray, float
        diffractlets for all sample rotations
        dim: 0: sample rotation, 1: sHSH indices, 2: detector points

    Return values
    ------------
    grad : 2D ndarray, float
        gradient for all the sHSH coefficients
        dim: 0: voxel index, 1: sHSH index
    """
    grad = np.zeros_like( C )
    for k in prange(gt_mask.shape[0]):
        g,t = gt_mask[k,0], gt_mask[k,1]
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        # get projected coefficients for the corresponding beam rotation/translation
        c_proj = integrate_c( Beams[g,t,:iend], iBeams[g,t,:iend], C )
        # calculate the image
        I_sim = c_proj @ difflets_rot[g] 
        # get the gradient on the coefficients from this projection
        residuals = data[k] - I_sim 
        grad_proj =  - 2 * difflets_rot[g] @ residuals
        # put the beam-intensity weighted value into each voxel
        for isp in range(iend): # sparse index
            iv = iBeams[g,t,isp] # voxel index
            grad[iv] += Beams[g,t,isp] * grad_proj
    return grad

@njit(parallel=True)
def _grad_highest(C, order_slice, data, gt_mask, Beams, iBeams, difflets_rot ): 
    """ Calculates the gradient for the highest order coefficients

    Parameters
    ----------
    C : 2D ndarray, float
        set of sHSH coefficients for each voxel
        dim: 0: voxel index, 1: sHSH index
    data : 3D ndarray, float
        dim: 0: rotation, 1: translation, 2: detector points
    scanmask : 2D ndarray, bool
        dim: 0: rotation, 1: translation
    Beams : 3D ndarray, float
        sparse-array containing beam intensity for all configurations
        dim: 0: rotation, 1: translation, 2: voxel (sparse)
    iBeams : 3D ndarray, int
        array of indices for the sparse Beams array
        dim: 0: rotation, 1: translation, 2: voxel index
    difflets_rot : 3D ndarray, float
        diffractlets for all sample rotations
        dim: 0: sample rotation, 1: sHSH indices, 2: detector points

    Return values
    ------------
    grad : 2D ndarray, float
        gradient for all the sHSH coefficients
        dim: 0: voxel index, 1: sHSH index
    """
    grad = np.zeros_like( C )
    for k in prange(gt_mask.shape[0]):
        g,t = gt_mask[k,0], gt_mask[k,1]
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        # get projected coefficients for the corresponding beam rotation/translation
        c_proj = integrate_c( Beams[g,t,:iend], iBeams[g,t,:iend], C )
        # calculate the image
        I_sim = c_proj @ difflets_rot[g] 
        # get the gradient on the coefficients from this projection
        residuals = data[k] - I_sim 
        grad_proj =  - 2 * difflets_rot[g, order_slice[0]:order_slice[1]] @ residuals
        # put the beam-intensity weighted value into each voxel
        for isp in range(iend): # sparse index
            iv = iBeams[g,t,isp] # voxel index
            grad[iv, order_slice[0]:order_slice[1]] += Beams[g,t,isp] * grad_proj
    return grad

@njit(parallel=True)
def _grad_allbutC0(C, order_slice, data, gt_mask, Beams, iBeams, difflets_rot ): 
    """ Calculates the gradient for the highest order coefficients

    Parameters
    ----------
    C : 2D ndarray, float
        set of sHSH coefficients for each voxel
        dim: 0: voxel index, 1: sHSH index
    data : 3D ndarray, float
        dim: 0: rotation, 1: translation, 2: detector points
    scanmask : 2D ndarray, bool
        dim: 0: rotation, 1: translation
    Beams : 3D ndarray, float
        sparse-array containing beam intensity for all configurations
        dim: 0: rotation, 1: translation, 2: voxel (sparse)
    iBeams : 3D ndarray, int
        array of indices for the sparse Beams array
        dim: 0: rotation, 1: translation, 2: voxel index
    difflets_rot : 3D ndarray, float
        diffractlets for all sample rotations
        dim: 0: sample rotation, 1: sHSH indices, 2: detector points

    Return values
    ------------
    grad : 2D ndarray, float
        gradient for all the sHSH coefficients
        dim: 0: voxel index, 1: sHSH index
    """
    grad = np.zeros_like( C )
    for k in prange(gt_mask.shape[0]):
        g,t = gt_mask[k,0], gt_mask[k,1]
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        # get projected coefficients for the corresponding beam rotation/translation
        c_proj = integrate_c( Beams[g,t,:iend], iBeams[g,t,:iend], C )
        # calculate the image
        I_sim = c_proj @ difflets_rot[g] 
        # get the gradient on the coefficients from this projection
        residuals = data[k] - I_sim 
        grad_proj =  - 2 * difflets_rot[g, 1:] @ residuals
        # put the beam-intensity weighted value into each voxel
        for isp in range(iend): # sparse index
            iv = iBeams[g,t,isp] # voxel index
            grad[iv, 1:] += Beams[g,t,isp] * grad_proj
    return grad

@njit(parallel=True)
def _grad_c0( C, data_av, gt_mask, Beams, iBeams ): 
    """ Calculates the gradient for the zero order coefficients
    from the averaged images

    Parameters
    ----------
    C : 2D ndarray, float
        set of sHSH coefficients for each voxel
        dim: 0: voxel index, 1: sHSH index
    data_av : 2D ndarray, float
        dim: 0: rotation, 1: translation
    scanmask : 2D ndarray, bool
        dim: 0: rotation, 1: translation
    Beams : 3D ndarray, float
        sparse-array containing beam intensity for all configurations
        dim: 0: rotation, 1: translation, 2: voxel (sparse)
    iBeams : 3D ndarray, int
        array of indices for the sparse Beams array
        dim: 0: rotation, 1: translation, 2: voxel index

    returns: 
    ------------
    grad : 2D ndarray, float
        gradient for all the sHSH coefficients
        dim: 0: voxel index, 1: sHSH index
    """
    grad = np.zeros_like( C )
    for k in prange(gt_mask.shape[0]):
        g,t = gt_mask[k,0], gt_mask[k,1]
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        # get projected coefficients for the corresponding beam rotation/translation
        c0_proj = sparsemult( Beams[g,t,:iend], iBeams[g,t,:iend], C[:,0] )
        residual = data_av[k] - c0_proj
        # assign gradient to the affected voxels
        grad[ iBeams[g,t,:iend], 0 ] += - 2 * residual * Beams[g,t,:iend]
    return grad

@njit(parallel=True)
def _lipschitz_c0( C, gt_mask, Beams, iBeams ): 
    """ Calculates the Lipschitz constant for the zero order coefficients

    Parameters
    ----------
    C : 2D ndarray, float
        set of sHSH coefficients for each voxel
        dim: 0: voxel index, 1: sHSH index
    scanmask : 2D ndarray, bool
        dim: 0: rotation, 1: translation
    Beams : 3D ndarray, float
        sparse-array containing beam intensity for all configurations
        dim: 0: rotation, 1: translation, 2: voxel (sparse)
    iBeams : 3D ndarray, int
        array of indices for the sparse Beams array
        dim: 0: rotation, 1: translation, 2: voxel index

    returns: 
    ------------
    L : 1D ndarray, float
    """
    L = np.zeros_like( C[:,0], data_type)
    for k in prange(gt_mask.shape[0]):
        g,t = gt_mask[k,0], gt_mask[k,1]
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        # assign contribution to the affected voxels
        L[ iBeams[g,t,:iend] ] += Beams[g,t,:iend]#**2
    return L

@njit(parallel=True)
def _projection( C, g, scanmask, Beams, iBeams, difflets_rot ):
    """Simulates diffraction images from a 2D scan over the sample

    Parameters
    ----------
    C : 2D ndarray, float
        set of sHSH coefficients for each voxelN
        dim: 0: voxel index, 1: sHSH index
    g : int
        rotation index
    scanmask : 2D ndarray, bool
        dim: 0: rotation, 1: translation
    Beams : 3D ndarray, float
        sparse-array containing beam intensity for all configurations
        dim: 0: rotation, 1: translation, 2: voxel (sparse)
    iBeams : 3D ndarray, int
        array of indices for the sparse Beams array
        dim: 0: rotation, 1: translation, 2: voxel index
    difflets_rot : 3D ndarray, float
        diffractlets for all sample rotations
        dim: 0: sample rotation, 1: sHSH indices, 2: detector points
        
    Return values
    ------------
    images : 3D ndarray, float
        array of resulting scattering intensity for each point on the 
        detector, for each rotation and translation
        dimensions: 0: rotation, 1: translation, 2: detector points
    """
    images = np.zeros( (Beams.shape[1], difflets_rot.shape[2]), data_type )
    for t in prange(Beams.shape[1]): # translations
        if scanmask[g,t]:
            iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
            # get projected coefficients for the corresponding beam rotation/translation
            c_proj = integrate_c( Beams[g,t,:iend], iBeams[g,t,:iend], C ).astype(data_type)
            # calculate the image
            images[t] = c_proj @ difflets_rot[g] 
    return images

@njit()
def _rotate_difflets_stack( Rs_stack, difflets ):
    ''' calculates the symmetrized HSH rotation matrices and the corresponding
    diffraction images for all sHSHs of order n and all rotations Gs
    '''
    difflets_stack = np.zeros( (Rs_stack.shape[0], difflets.shape[0], difflets.shape[1]), data_type )
    for g, Rs_g in enumerate(Rs_stack):
        difflets_stack[g] = Rs_g @ difflets
    
    return difflets_stack

@njit(parallel=True)
def _get_mean_ori( im, scanmask, i_peak, chi, detShape ):
    ori = np.zeros( im.shape[0], data_type )
    for t in prange(im.shape[0]):
        if scanmask[t]:
            im2D = im[t].reshape( detShape )
            # get azimuthal data for one peak
            I_azi = im2D[i_peak]
            nphi_2 = int( I_azi.size/2 ) 
            # divide data to from 0 to pi and pi to 2pi
            I_azi1, I_azi2 = I_azi[nphi_2:], I_azi[:nphi_2]
            # remove mask/detector gaps
            I_azi1[I_azi1==0] = I_azi2[I_azi1==0]
            I_azi2[I_azi2==0] = I_azi1[I_azi2==0]
            # average both parts
            I_azi_folded = (I_azi1 + I_azi2)/2
            # to calculate the mean
            x_mean = ( I_azi_folded * np.cos( 2*chi ) ).sum() / I_azi_folded.sum()
            y_mean = ( I_azi_folded * np.sin( 2*chi ) ).sum() / I_azi_folded.sum()
            chi_mean = np.arctan2( y_mean, x_mean ) / 2 + np.pi/2

            ori[t] = chi_mean
    return ori

# not used
# @njit(parallel=True)
# def _get_powder_1D( data, mask_detector, detShape, iBeams, scanmask ):
#     data_1D = np.zeros((detShape[0]),data_type)
#     for g in prange(iBeams.shape[0]): # rotations
#         for t in range(iBeams.shape[1]): # translations
#             if ( scanmask[g,t] and (iBeams[g,t,0] < 2**32-1) ):
#                 data_1D += _masked_to_1D(
#                     data[g,t,mask_detector], mask_detector, detShape)
#     return data_1D

# @njit
# def _masked_to_1D( A, mask_detector, detShape ):
#     A_full = np.zeros( detShape, data_type ).flatten()
#     A_full[mask_detector] = A
#     A_1D = np.array([dq[dq>0].mean() for dq in A_full.reshape(detShape)])
#     return A_1D

@njit(parallel=True)
def beamnorm(gt_mask, Beams ): 
    Nb = np.empty( gt_mask.shape[0] )
    for k in prange(gt_mask.shape[0]):
        g,t = gt_mask[k,0], gt_mask[k,1]
        Nb[k] = Beams[g,t].sum()
    return Nb