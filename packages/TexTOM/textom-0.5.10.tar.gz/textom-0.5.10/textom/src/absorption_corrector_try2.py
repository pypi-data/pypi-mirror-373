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
    entry_point = np.array([-0.1,20,5]) #x_p[iBeams[g,t]] # tip of the cone
    
    dchi = azimuthal_angles[1]-azimuthal_angles[0] # azimuthal binning on the detector

    absorption_pattern = np.empty((scattering_angles.size,azimuthal_angles.size), np.float64)
    for q, twotheta in enumerate(scattering_angles): # cone angle ~ 2theta
        for c, chi in enumerate(azimuthal_angles):
            chi_min, chi_max = chi - dchi/2, chi + dchi/2 # range for the cone wedge

            absorption_pattern[q,c] = integrate_eV_conewedge(
                tomogram, entry_point, np.array(beam_direction), twotheta, chi_min, chi_max, 
                np.array(detector_direction_origin), np.array(detector_direction_positive_90)
            )

    return absorption_pattern

@njit
def cone_wedge_to_cartesian(h, r, theta, tip, axis, origin_vec, pos_dir_vec):
    """
    Convert cone wedge coordinates (h, r, theta) to Cartesian coordinates.
    """
    # Compute position in local frame
    point = tip + h * axis + r * (np.cos(theta) * origin_vec + np.sin(theta) * pos_dir_vec)
    return point

# @njit
def integrate_eV_conewedge(grid, cone_tip, cone_axis, opening_angle, chi_min, chi_max, origin_vec, pos_dir_vec,
                   dV=2):
    """
    Perform an integration over a cone wedge by sampling points equal-volume
    """
    integral = 0.
    h = np.sqrt(grid.shape[0]**2+grid.shape[2]**2)# max length of the cone
    points = sample_cone_wedge( h, cone_tip, cone_axis, opening_angle, chi_min, chi_max, origin_vec, pos_dir_vec, dV )
    points = np.round(points).astype(np.int64)
    points_u, cts = np.unique(points,axis=0,return_counts=True)

    for p,c in zip(points_u,cts):
        if np.all( p >= np.zeros_like(p) ) and np.all( p < np.array(grid.shape) ):
            integral += c* grid[p[0],p[1],p[2]]
            
    return integral

@njit
def integrate_mc_conewedge(grid, cone_tip, cone_axis, opening_angle, chi_min, chi_max, origin_vec, pos_dir_vec,
                   N_mc=1e4):
    """
    Perform MC integration over a cone divided into wedges
    """
    integral = 0.

    for _ in range(N_mc):
        # Generate random equal-volume points within the cone
        # https://stackoverflow.com/questions/41749411/uniform-sampling-by-volume-within-a-cone
        a = np.sqrt(grid.shape[0]**2+grid.shape[2]**2)# a is the max length of the cone
        b = a*np.tan(opening_angle) # b is the max radius of the cone
        h = a * np.random.rand()**(1/3) # sampling of the height
        r = (b / a) * h * np.sqrt(np.random.rand()) # sampling of the radius
        t = chi_min + (chi_max-chi_min) * np.random.rand() # sampling of the angle

        p = cone_wedge_to_cartesian(h,r,t,
                        cone_tip, cone_axis, origin_vec, pos_dir_vec)
        
        p = np.round(p).astype(np.int64)
        if np.all( p >= np.zeros_like(p) ) and np.all( p < np.array(grid.shape) ):
            integral += grid[p[0],p[1],p[2]]
            
    return integral

def generate_equal_volume_points(tip, axis, opening_angle, chi_min, chi_max, origin_vec, pos_dir_vec, dV):
    """
    Generate points inside the wedge of a cone that occupy approximately equal volumes.
    """
    points = []
    
    # Compute total volume of the wedge
    h_max = 1  # Assume unit height for normalization, scale later
    V_total = (1/3) * np.pi * (np.tan(opening_angle) ** 2) * h_max**3 * (chi_max - chi_min) / (2 * np.pi)
    
    # Determine number of points needed
    num_points = int(V_total / dV)
    
    # Distribute points in (h, r, theta)
    h_vals = np.linspace(0, h_max, int(num_points ** (1/3)))
    for h in h_vals:
        r_max = h * np.tan(opening_angle)
        r_vals = np.linspace(0, r_max, int(num_points ** (1/3)))
        for r in r_vals:
            theta_vals = np.linspace(chi_min, chi_max, int(num_points ** (1/3)))
            for theta in theta_vals:
                points.append(cone_wedge_to_cartesian(h, r, theta, tip, axis, origin_vec, pos_dir_vec))
    
    return np.array(points)

def sample_cone_wedge( h, tip, axis, opening_angle, chi_min, chi_max, origin_vec, pos_dir_vec, dV ):
    dr = dV**(1/3)
    points = []
    zz = np.arange(0,h,dr)
    R = h*np.tan(opening_angle)
    dt = np.arctan(dr/R)
    tt = np.arange(chi_min,chi_max,dt)
    for z in zz:
        rr = np.arange(0, z/h*R )
        for r in rr:
            for t in tt:
                points.append(cone_wedge_to_cartesian(z, r, t, tip, axis, origin_vec, pos_dir_vec))
    print(len(points))
    return np.array(points)

# def equal_volume_cone_wedge_sampling( h, r, chi_min, chi_max, dV ):

#     z_sample = np.linspace(0, h**3, num=n_z)**(1/3)

#     return points

# tomogram = np.ones((40,40,10), np.float64)
# nchi = 30
# Chi = np.linspace(0,2*np.pi, num=nchi, endpoint=False) + 2*np.pi/nchi/2
# Q = np.linspace(10, 35, num=10, endpoint=False) # nm^-1
# lam = 0.0826565
# two_theta = 2 * np.arcsin( Q*lam / (4*np.pi) )
# Gs = np.array([[0,0,0]])
# # Gs = np.array([[np.pi/4,np.pi/2,np.pi/2]])
# # Gs = np.array([[0.7,0.2,0.3]])

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

# points = sample_cone_wedge(30, np.array([0,0,0]), np.array([1,0,0]), np.pi/6, 
#                                       0, np.pi/6, np.array([0,0,1]), np.array([0,-1,0]), 2)
# print(points.shape)
# fig = plt.figure()#figsize=(10, 10))
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter(points[:,0],points[:,1],points[:,2])

# plt.show()