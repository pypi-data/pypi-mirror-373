import numpy as np
from numba import njit

from . import rotation as rot
from ..config import data_type

@njit
def fisher_SO3(Q, q_mean, kappa, Q_group): 
    """
    von Mises-Fisher distribution on fundamental zone (fz)

    Parameters
    --------
    Q : 2d ndarray, float
        array of unit quaternions representing orientations
    q_mean: 1d ndarray, float 
        mean orientation as quaternion
    kappa: float
        concentration parameter for von Mises-Fisher distribution (~1/sigma^2) ! this value seems not correct
    Q_group: 2d ndarray, float
        array of unit quaternions with all symmetry operations of the point group
    
    Returns:
    ------------
    odf: 1d ndarray, float
        non-normalized probabilty density for each quaternion
    """
    # We put multiple (mises-fisher) bell functions on the unit quaternion sphere
    # One on every symmetry equivalent q_mu
    # Evaluate the sum of these on orientations Q
    q_mean_equivalents = symmetry_equivalent_quaternions(q_mean,Q_group)
    # q_mu_equivalents = np.atleast_2d(q_mu) # this is to show what happens if you use only q_mu

    # calculate odf as a sum of distributions from equivalents
    odf = np.zeros((q_mean_equivalents.shape[0],Q.shape[0]), dtype=data_type)
    for i in range(q_mean_equivalents.shape[0]):
        mux = np.abs( q_mean_equivalents[i] @ Q.T )
        odf[i]= np.exp(kappa * (mux - 1))
    odf = np.sum(odf, axis=0)# / np.exp(kappa)
    return odf

@njit(parallel=True)
def get_rotated_diffractlets(Qc, Qs, Q_grid, Q_group, kappa, I_single_crystal, detShape ):
    difflets_rot = np.empty( (Qs.shape[0], Q_grid.shape[0], *detShape), data_type )
    # s,gr=0,0
    for s in prange(Qs.shape[0]):
        for gr in range(Q_grid.shape[0]):
            q_mean = rot.quaternion_multiply( Qs[s], Q_grid[gr] )
            odf = fisher_SO3( Qc, q_mean, kappa, Q_group )
            # sparse calculate the projections (only points in odf that are high)
            diff_pattern = np.zeros(detShape, data_type)
            idcs_odf = np.nonzero( odf > 0.01 * odf.max() )[0] # cut small values of the odf
            for h in idcs_odf:
                diff_pattern += I_single_crystal[h] * odf[h]
            difflets_rot[s,gr] = diff_pattern
    return difflets_rot

@njit
def get_odf_fisher( coefficients, Qc, Q_grid, Q_group, kappa, cutoff=1e-2 ):
    odf = np.zeros_like(Qc[:,0])
    for c in range(coefficients.size):
        if coefficients[c] > coefficients.max()*cutoff:
            odf += fisher_SO3( Qc, Q_grid[c], kappa, Q_group)
    return odf

@njit(parallel=True)
def get_odf_max_orientations( C_voxels, Qc, Q_grid, Q_group, kappa ):
    Q_max = np.empty( (C_voxels.shape[0], 4), data_type )
    for v in prange(C_voxels.shape[0]):
        odf = get_odf_fisher( C_voxels[v], Qc, Q_grid, Q_group, kappa )
        Q_max[v] = Qc[np.argmax(odf)]
    return Q_max

@njit
def gaussian_SO3(Q, q_mean, std, Q_group): 
    """
    von Mises-Fisher distribution on fundamental zone (fz)

    Parameters
    --------
    Q : 2d ndarray, float
        array of unit quaternions representing orientations
    q_mean: 1d ndarray, float 
        mean orientation as quaternion
    std: float
        standard deviation in radians
    Q_group: 2d ndarray, float
        array of unit quaternions with all symmetry operations of the point group
    
    Returns:
    ------------
    odf: 1d ndarray, float
        non-normalized probabilty density for each quaternion
    """
    
    dQ = rot.misorientation_angle_stack(Q, nb_full(Q.shape,q_mean), Q_group)
    odf = np.exp( - dQ**2/(2*std**2) )

    return odf

@njit
def gaussian_3d( Q, q_mu, std, gen, dV=1 ):
    """
    Gauss bell on FZ
    Parameters
    --------
    Q : 2d ndarray, float
        array of unit quaternions representing orientations
    mu: 1d ndarray, float 
        mean orientation as quaternion
    std: float
        standard deviation - sigma
    gen: 2d ndarray, float
        OTP of the two generators for the point group symmetries
        dim0: generators, dim1: OTP
    
    Returns:
    ------------
    odf: 1d ndarray, float
        non-normalized probabilty (mass) for each of the orientations g
    """
    # for omega_mu = 0, then dg is omega
    dg = rot.ang_distance(Q, nb_full(Q.shape,q_mu), gen)
    odf = np.exp( - dg**2/(2*std**2) )
    return odf #/( odf @ dV ) Does not return a valid pmf at the moment

@njit
def symmetry_equivalent_quaternions(q, Q_group, prec=7):
    Q_eq = np.empty_like(Q_group)
    for k in range(Q_group.shape[0]):
        Q_eq[k] = np.round( rot.quaternion_multiply( Q_group[k], q ), prec)

    Q_eq[Q_eq[:,0]<0] *= -1 # bring all to positive real part
    return nb_unique_axis0(Q_eq)

from .misc import integrate_c
from numba import prange
# @njit(parallel=True)
def projection( g, Qc, Isc, gen, Q_mu, c_sample, kappa, Qs, Beams, iBeams, detShape, dV ):
    diff_patterns_g = np.empty((Beams.shape[1],detShape[0],detShape[1]), data_type)
    for t in prange(Beams.shape[1]):
        # project the coefficients
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        c_proj = integrate_c( Beams[g,t,:iend], iBeams[g,t,:iend], c_sample )
        # get the resulting odf from rotated mu
        odf_proj = np.zeros( Qc.shape[0], data_type )
        idcs_basis = np.nonzero(c_proj > 0.01 * c_proj.max())[0]
        for c in idcs_basis:
            q_mu = rot.quaternion_multiply(  Q_mu[c], Qs[g] )
            odf_proj += c_proj[c] * fisher_SO3(Qc, q_mu, kappa, gen, dV )
        # sparse calculate the projections (only points in odf that are high)
        diff_pattern = np.zeros(Isc.shape[1], data_type)
        idcs_odf = np.nonzero(odf_proj> 0.01 * odf_proj.max())[0]
        for h in idcs_odf:
            diff_pattern += Isc[h] * odf_proj[h]
        diff_patterns_g[t] = diff_pattern.reshape((detShape[0],detShape[1]))
    return diff_patterns_g

@njit
def nb_full(shape, fill_array):
    out = np.empty((shape[0], fill_array.shape[0]), dtype=fill_array.dtype)
    for i in range(shape[0]):
        for j in range(fill_array.shape[0]):
            out[i, j] = fill_array[j]
    return out

@njit
def nb_unique_axis0(arr):
    n, m = arr.shape
    output = np.empty((n, m), dtype=arr.dtype)
    count = 0

    for i in range(n):
        duplicate = False
        for j in range(count):
            is_same = True
            for k in range(m):
                if arr[i, k] != output[j, k]:
                    is_same = False
                    break
            if is_same:
                duplicate = True
                break
        if not duplicate:
            for k in range(m):
                output[count, k] = arr[i, k]
            count += 1

    return output[:count]