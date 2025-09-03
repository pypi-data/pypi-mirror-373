import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange

import textom.src.rotation as rot
from textom.input import geometry as geo
# from textom.config import data_type

# from . import rotation as rot
# from ..input import geometry as geo
# from ..config import data_type # azimuthal binning on the detector


def absorption_correction( tomogram, mask, scattering_angles, azimuthal_angles, Gs, 
                        #   iBeams, 
                          x_p,
                          ):
    """_summary_

    Parameters
    ----------
    tomogram : _type_
        absorption tomogram
    mask :
        mask or threshold for not calculating everything
    scattering_angles : _type_
        relevant angles 2theta / q-values on the detector (peaks)
    chi :
        detector angles (binned)
    Gs : _type_
        sample rotations ? might do this afterwards.

    Returns
    -------
    _type_
        _description_
    """
    g,t = 0,0
    # for each projection (g):
    beam_direction = geo.beam_direction @ rot.OTP_to_matrix(Gs[g,0],Gs[g,1],Gs[g,2])
    detector_direction_origin = geo.detector_direction_origin @ rot.OTP_to_matrix(Gs[g,0],Gs[g,1],Gs[g,2])
    detector_direction_positive_90 = geo.detector_direction_positive_90 @ rot.OTP_to_matrix(Gs[g,0],Gs[g,1],Gs[g,2])
    # for each g and t:
    entry_point = np.array([0,3,3]) #x_p[iBeams[g,t]] # tip of the cone
    entry_point = np.array([-0.1,10,20]) #x_p[iBeams[g,t]] # tip of the cone
    
    dchi = azimuthal_angles[1]-azimuthal_angles[0] # azimuthal binning on the detector

    absorption_pattern = np.empty((scattering_angles.size,azimuthal_angles.size), np.float64)
    for q, twotheta in enumerate(scattering_angles): # cone angle ~ 2theta
        for c, chi in enumerate(azimuthal_angles):
            chi_min, chi_max = chi - dchi/2, chi + dchi/2 # range for the cone wedge

            absorption_pattern[q,c] = integrate_wedge(
                tomogram, entry_point, beam_direction, twotheta, chi_min, chi_max, 
                detector_direction_origin, detector_direction_positive_90
            )

    return absorption_pattern

@njit
def smooth_step(x, edge0, edge1):
    """Smooth transition function between 0 and 1."""
    t = numba_clip((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * (3 - 2 * t)

@njit
def numba_clip(x, min_val, max_val):
    """Numba-compatible equivalent of np.clip."""
    if x < min_val:
        return min_val
    elif x > max_val:
        return max_val
    return x

@njit
def is_inside_wedge(x, y, z, 
                    entry_point, beam_direction, two_theta, 
                    chi_min, chi_max,
                    detector_direction_origin, detector_direction_positive_90):
    """
    Check if a point (x, y, z) is inside the wedge of a the cone defined by the
    entry point of the beam into the sample, the scattering angle 2theta and 
    the respective azimuthal bin (chi_min,chi_max) on the detector.
    """
    # Adaptive eps: Increase near horizontal/vertical to reduce artifacts
    eps = 1e-1  # Small tolerance for smoothing
    # eps = eps * (1 + abs(np.cos(alpha)))

    # Shift coordinates to cone's tip
    x_shift, y_shift, z_shift = x - entry_point[0], y - entry_point[1], z - entry_point[2]
    
    # Project point onto the cone's axis
    dot_product = x_shift * beam_direction[0] + y_shift * beam_direction[1] + z_shift * beam_direction[2]
    
    # Compute radial distance from the axis
    projected = np.array([dot_product * beam_direction[i] for i in range(3)])
    radial_vector = np.array([x_shift, y_shift, z_shift]) - projected
    r = np.linalg.norm(radial_vector)
    h = np.linalg.norm(projected)

    # # Compute smooth transition for cone boundary
    # cone_weight = smooth_step(r / h, np.tan(two_theta) - eps, np.tan(two_theta) + eps)
    cone_weight = 1 - smooth_step(r / h, np.tan(two_theta) - eps, np.tan(two_theta) + eps)

    # # Check if point is within cone's angle
    # if h <= 0 or r / h > np.tan(two_theta):
    #     return False
    
    # Compute azimuthal angle relative to detector_direction_origin, detector_direction_positive_90
    radial_unit = radial_vector / (np.linalg.norm(radial_vector) + 1e-10)
    chi = np.arctan2(np.dot(radial_unit, detector_direction_positive_90), np.dot(radial_unit, detector_direction_origin))
    if chi < 0:
        chi += 2 * np.pi
    
    # return chi_min <= chi <= chi_max

    # Compute smooth transition for theta boundary
    chi_weight = smooth_step(chi, chi_min - eps, chi_min + eps) * (1 - smooth_step(chi, chi_max - eps, chi_max + eps))
    
    return cone_weight * chi_weight
    # return chi_weight

@njit
def compute_wedge_correction(origin_vec, pos_dir_vec, chi_min, chi_max):
    """
    Compute a correction factor based on the angle between the wedge plane and grid planes.
    """
    chi_av = 0.5 * (chi_min + chi_max)
    n_wedge = np.cos(chi_av) * origin_vec + np.sin(chi_av) * pos_dir_vec
    norm = np.sqrt(n_wedge[0]**2 + n_wedge[1]**2 + n_wedge[2]**2)
    n_wedge /= norm if norm > 0 else 1.0  # Avoid division by zero
    
    # Define normal vectors of the grid planes
    grid_normals = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    
    # Compute the correction factor based on the closest grid plane normal
    max_cos = 0.0
    for i in range(3):
        dot = abs(n_wedge[0] * grid_normals[i, 0] + n_wedge[1] * grid_normals[i, 1] + n_wedge[2] * grid_normals[i, 2])
        if dot > max_cos:
            max_cos = dot

    return max_cos  # Higher alignment → larger correction

@njit
def integrate_wedge(grid, cone_tip, cone_axis, opening_angle, chi_min, chi_max, origin_vec, pos_dir_vec):
    """
    Perform numerical integration over a wedge of a cone inside a 3D grid.
    """
    integral = 0.0
    grid_correction = compute_wedge_correction(origin_vec, pos_dir_vec, chi_min, chi_max)

    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            for z in range(grid.shape[2]):
                weight = is_inside_wedge(x, y, z, cone_tip, cone_axis, 
                                   opening_angle, chi_min, chi_max, 
                                   origin_vec, pos_dir_vec)
                integral += grid[x, y, z] * weight * grid_correction
    
    return integral

# tomogram = np.ones((20,20,40), np.float64)
# nchi = 30
# Chi = np.linspace(0,2*np.pi, num=nchi, endpoint=False) + 2*np.pi/nchi/2
# Q = np.linspace(np.pi/6,2*np.pi/6,num=10, endpoint=False)
# Gs = np.array([[0,0,0]])
# # Gs = np.array([[np.pi/4,np.pi/2,np.pi/2]])
# # Gs = np.array([[0.7,0.2,0.3]])

# absorption_pattern = absorption_correction(tomogram,0,
#                                 Q,Chi,Gs,0)
# print(absorption_pattern)
# CHi, QQ = np.meshgrid( Chi, Q )
# X1 = -QQ*np.sin(CHi)
# X2 = QQ*np.cos(CHi)
# plt.pcolormesh( X1, X2, absorption_pattern, cmap='plasma' )
# plt.axis('equal')
# plt.grid(False)
# plt.show()