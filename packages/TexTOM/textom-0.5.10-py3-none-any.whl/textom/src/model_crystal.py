import numpy as np
import os, re
import matplotlib.pyplot as plt
from numba import njit, prange
import orix.quaternion.symmetry as osym 
from orix.quaternion import Rotation, Orientation, OrientationRegion
from time import time

from . import handle as hdl
from . import rotation as rot
from . import symmetries as sym
from . import hsh
from . import gridbased as grd
from . import numba_plugins as nb
from ..config import data_type

def parse_cif(file_path):
    """
    Parse a CIF file and calculate the positions of all atoms in the unit cell.
    
    Parameters:
        file_path (str): Path to the CIF file.

    Returns:
        dict: Contains lattice vectors, 
        atomic positions in fractional and Cartesian coordinates, and symmetry operations.
    """
    atom_labels = []
    atom_fractions = []
    space_group = None
    lattice_vectors = []
    symmetry_operations = []
    positions_cartesian = []

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Parse the CIF file line by line
        for i, line in enumerate(lines):
            # Extract space group
            if line.startswith('_space_group_IT_number'):
                space_group = int( line.split()[-1].strip("'\"") )
            
            # Extract lattice vectors
            if line.startswith('_cell_length_a'):
                a = float(line.split()[-1])
            elif line.startswith('_cell_length_b'):
                b = float(line.split()[-1])
            elif line.startswith('_cell_length_c'):
                c = float(line.split()[-1])
            elif line.startswith('_cell_angle_alpha'):
                alpha = float(line.split()[-1])
            elif line.startswith('_cell_angle_beta'):
                beta = float(line.split()[-1])
            elif line.startswith('_cell_angle_gamma'):
                gamma = float(line.split()[-1])

            # Find atomic data section
            if line.strip().startswith('loop_'):
                # Look for atomic position headers in the following lines
                headers = []
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('_'):
                    headers.append(lines[j].strip())
                    j += 1

                # Check if this block contains atomic positions
                if ('_atom_site_fract_x' in headers and
                        '_atom_site_fract_y' in headers and
                        '_atom_site_fract_z' in headers):
                    # Start reading data rows
                    while j < len(lines) and not lines[j].strip().startswith('loop_') and lines[j].strip():
                        split_line = lines[j].split()
                        atom_labels.append(split_line[headers.index('_atom_site_type_symbol')])  # Assume first column is atom type
                        atom_fractions.append([float(split_line[headers.index('_atom_site_fract_x')]),
                                            float(split_line[headers.index('_atom_site_fract_y')]),
                                            float(split_line[headers.index('_atom_site_fract_z')])])
                        j += 1

        # Convert lattice parameters to lattice vectors
        alpha, beta, gamma = np.radians([alpha, beta, gamma])
        lattice_vectors = [
            [a, 0, 0],
            [b * np.cos(gamma), b * np.sin(gamma), 0],
            [
                c * np.cos(beta),
                c * (np.cos(alpha) - np.cos(beta) * np.cos(gamma)) / np.sin(gamma),
                c * np.sqrt(1 - np.cos(beta) ** 2 - (np.cos(alpha) - np.cos(beta) * np.cos(gamma)) ** 2 / np.sin(gamma) ** 2),
            ],
        ]
        lattice_vectors = np.array(lattice_vectors)

        # Extract symmetry operations
        symmetry_mode = False
        for line in lines:
            if '_space_group_symop_operation_xyz' in line:
                symmetry_mode = True
            elif symmetry_mode and line.strip() == '':
                symmetry_mode = False
            elif symmetry_mode:
                op = line.strip().strip("'")
                symmetry_operations.append(op)

        # Apply symmetry operations to fractional coordinates
        atom_fractions = np.array(atom_fractions)
        full_fractions, atom_list = [], []
        for op in symmetry_operations:
            for (frac, at) in zip(atom_fractions, atom_labels):
                full_fractions.append(apply_symmetry_operation(op, frac))
                atom_list.append(at)
        full_fractions = np.array(full_fractions)
        full_fractions = np.mod(full_fractions, 1)  # Ensure all coordinates are within [0, 1)
        full_fractions, indices = np.unique(np.squeeze(full_fractions), axis=0, return_index=True)

        # Convert fractional to Cartesian coordinates
        positions_cartesian = np.array(
            [np.dot(frac, lattice_vectors) for frac in full_fractions]
        )
        # for frac in full_fractions:
        #     cart = np.dot(frac, lattice_vectors)
        #     positions_cartesian.append(cart)

        return {
            "atom_types": atom_labels,
            "coordinates": np.array(atom_fractions),
            "lattice_vectors": lattice_vectors,
            "space_group": space_group or "Unknown",
            'symmetry_operations': symmetry_operations,
            'atom_list': np.array(atom_list)[indices],
            'fractional_positions': full_fractions,
            'cartesian_positions': positions_cartesian,
        }

    except Exception as e:
        print(f"Error parsing CIF file: {e}")
        return None

def get_reciprocal_space_coordinates(Qq_det, Chi_det, E_keV, geo):
    """Calculates the coordinates of the detector points based on
    polar coordinates q_det, chi_det and X-ray energy E_kev

    Returns
    -------
    ndarray
        3D reciprocal space coordinates and number of detector points
    """

    h = 4.135667696e-18 # keV*s
    c = 299792458 # m/s
    wavelength = h*c*1e9 / E_keV # nm

    Two_theta = 2 * np.arcsin(Qq_det * wavelength / (4*np.pi))
    QX,QY,QZ = np.empty_like(Two_theta), np.empty_like(Two_theta), np.empty_like(Two_theta)
    for k in range(QY.shape[0]):
        QX[k], QY[k], QZ[k] = reciprocal_lattice_point(Two_theta[k], Chi_det[k], wavelength,
            u_beam=geo.beam_direction,
            u0=geo.detector_direction_origin,
            u90=geo.detector_direction_positive_90,
        )

    # import matplotlib.pyplot as plt
    # fig = plt.figure(figsize=(8, 6))
    # ax = fig.add_subplot(121, projection='3d')
    # ax.scatter(QX, QY, QZ)
    # ax.set_xlabel('x')
    # ax.set_ylabel('y')
    # ax.set_zlabel('z')
    return np.column_stack([QX, QY, QZ])

# @njit
def reciprocal_lattice_point(two_theta_rad, chi_rad, wavelength_nm, 
                             u_beam=(1,0,0), u0=(0,0,1), u90=(0,1,0)):
    """
    Calculate (qx, qy, qz) from angles and wavelength, defining the geometry by vectors.

    Parameters:
    - two_theta_rad: scattering angle (2?) in rad
    - chi_rad: azimuthal angle in rad
    - wavelength_nm: wavelength of incident beam in nm
    Optional:
    - u_beam: beam direction vector
    - u0: direction vector pointing towards the origin of chi
    - u90: direction vector pointing towards chi of +90 degree

    Returns:
    - (qx, qy, qz): reciprocal space coordinates (nm^-1)
    """
    # axes
    u_beam = np.array(u_beam, data_type)
    u0 = np.array(u0, data_type)
    u90 = np.array(u90, data_type)

    # Magnitude of wavevector
    k = 2 * np.pi / wavelength_nm

    # Incoming wavevector:
    k_in = k * u_beam

    # Outgoing wavevector (direction from spherical coordinates)
    k_out = k * (
        np.cos(two_theta_rad) * u_beam + 
        np.sin(two_theta_rad) * ( np.cos(chi_rad) * u0 + np.sin(chi_rad) * u90 )
        )

    q = k_out - k_in
    return q

def apply_symmetry_operation(operation, position):
    """
    Apply a symmetry operation to a fractional position.

    Parameters:
        operation (str): The symmetry operation in CIF format (e.g., "x,y,z").
        position (list or np.ndarray): Fractional coordinates [x, y, z].

    Returns:
        np.ndarray: New fractional coordinates after applying the operation.
    """
    # Ensure the symmetry operation format is consistent and parse it
    operation = operation.strip().replace(' ', '')  # Remove spaces for easier parsing
    operation = operation.replace('x', '{x}').replace('y', '{y}').replace('z', '{z}')

    # Check for simple transformations (e.g., -x or x+1/2)
    operation = re.sub(r'([+-]?\d*\.\d+|\d+)', r'float("\1")', operation)  # Convert numbers to float type

    x, y, z = position
    local_dict = {'x': x, 'y': y, 'z': z}

    # Safely evaluate the operation
    try:
        new_pos = [eval(operation.format(x=x, y=y, z=z))]
        return np.array(new_pos)
    except Exception as e:
        print(f"Error applying symmetry operation: {operation}")
        raise e

"""
array([[1.3268    , 3.70216157, 4.84805619],
       [3.9804    , 5.19063843, 1.57644381],
       [3.9804    , 8.14856157, 4.78869381],
       [1.3268    , 0.74423843, 1.63580619],
       [1.3268    , 6.72562464, 5.90861265],
       [3.9804    , 2.16717536, 0.51588735],
       [3.9804    , 2.27922464, 3.72813735],
       [1.3268    , 6.61357536, 2.69636265],
       [1.3268    , 8.0124128 , 5.85593175],
       [3.9804    , 0.8803872 , 0.56856825],
       [3.9804    , 3.5660128 , 3.78081825],
       [1.3268    , 5.3267872 , 2.64368175],
       [2.43918912, 6.08356448, 5.9066853 ],
       [2.86801088, 2.80923552, 0.5178147 ],
       [2.86801088, 1.63716448, 3.7300647 ],
       [2.43918912, 7.25563552, 2.6944353 ],
       [5.09278912, 2.80923552, 0.5178147 ],
       [0.21441088, 6.08356448, 5.9066853 ],
       [0.21441088, 7.25563552, 2.6944353 ],
       [5.09278912, 1.63716448, 3.7300647 ]])
       """

def get_reciprocal_points( lattice_vectors, hkl_list):
    """
    Calculate reciprocal lattice points for the given crystal up to the given miller indices.
    """
    # Direct lattice vectors 
    a1 = lattice_vectors[0]
    a2 = lattice_vectors[1]
    a3 = lattice_vectors[2]
    
    # Reciprocal lattice vectors
    V = np.dot(a1, np.cross(a2, a3))  # Unit cell volume
    b1 = 2 * np.pi * np.cross(a2, a3) / V
    b2 = 2 * np.pi * np.cross(a3, a1) / V
    b3 = 2 * np.pi * np.cross(a1, a2) / V
    
    # Generate reciprocal lattice points
    reciprocal_points = []
    for hkl in hkl_list:
        G = hkl[0] * b1 + hkl[1] * b2 + hkl[2] * b3
        reciprocal_points.append(G)
    
    return np.array(reciprocal_points)

def group_equivalent_reflections(hkl_max, lattice_vectors, point_group_quaternions):
    """Group reflections into families using symmetry operations."""
    families = {}
    
    # Generate reciprocal lattice points
    h_vals = np.arange(-hkl_max, hkl_max + 1)
    k_vals = np.arange(-hkl_max, hkl_max + 1)
    l_vals = np.arange(-hkl_max, hkl_max + 1)
    indices = []
    for h in h_vals:
        for k in k_vals:
            for l in l_vals:
                indices.append([h,k,l])

    # Reciprocal lattice vectors
    V = np.dot(lattice_vectors[0], np.cross(lattice_vectors[1], lattice_vectors[2]))  # Unit cell volume
    reciprocal_lattice_vectors = np.column_stack([
         2 * np.pi * np.cross(lattice_vectors[1], lattice_vectors[2]) / V,
        2 * np.pi * np.cross(lattice_vectors[2], lattice_vectors[0]) / V,
        2 * np.pi * np.cross(lattice_vectors[0], lattice_vectors[1]) / V
        ])

    for hkl in indices:
        # skip (0,0,0)
        if tuple(hkl) == (0,0,0):
            continue
        equivalents = equivalents_of_hkl(hkl, reciprocal_lattice_vectors, point_group_quaternions)

        # pick representative        
        pos_eq = np.all(np.greater_equal(equivalents,0),axis=1)
        if np.any(pos_eq):
            rep = tuple(max(np.array(equivalents)[pos_eq].tolist()))
        else:
            rep = max(equivalents)

        if rep not in families:
            families[rep] = set()
            families[rep].update(equivalents)
    
    representatives = []
    equivalents = []
    for rep, eqs in families.items():
        representatives.append(rep)
        equivalents.append(eqs)
    
    return representatives, equivalents


def equivalents_of_hkl(hkl, B, rotations, include_inversion=True,
                       tol=1e-4, friedel_equivalence=False):
    """
    Determine multiplicity of Miller index hkl under provided point-group rotations.
    Inputs:
      - hkl: tuple/list (h,k,l) integers
      - B: 3x3 reciprocal basis matrix [b1 b2 b3] (columns)
      - rotations: iterable of quaternions (proper rotations)
      - include_inversion: whether to also include inversion (-I)
      - tol: acceptance tolerance in reciprocal-space (same units as B)
      - friedel_equivalence: if True, treat hkl and -h-k-l as identical (Friedel)
    Returns:
      - unique_hkls: list of unique integer (h,k,l) generated
      - count: multiplicity (len of unique_hkls)
    """
    hkl = np.asarray(hkl, dtype=int)
    G = B @ hkl.reshape(3,1) 
    Binv = np.linalg.inv(B)
    found = []

    def accept_Gprime(Gp):
        # Convert back to h' (real)
        h_real = Binv @ Gp
        h_rounded = np.rint(h_real).astype(int).flatten()
        # compute residual in reciprocal space
        resid = np.linalg.norm(B @ h_rounded - Gp)
        if resid <= tol:
            return tuple(h_rounded)
        else:
            return None

    for q in rotations:
        Gp = rot.quaternion_rotate_vector( q, G.flatten() )
        h_ = accept_Gprime(Gp)
        if h_ is not None:
            found.append(h_)
        if include_inversion:
            Gp_inv = -Gp
            h2 = accept_Gprime(Gp_inv)
            if h2 is not None:
                found.append(h2)

    # canonicalize/fold Friedel pairs if requested
    unique_set = set()
    for h in found:
        if friedel_equivalence:
            h_neg = tuple((-np.array(h)).tolist())
            rep = max(h, h_neg)
        else:
            rep = h
        unique_set.add(rep)

    unique_hkls = sorted(unique_set)
    return unique_hkls

# def plot_powder_pattern(reciprocal_points, energy_keV, num_bins=100):
#     """Compute and plot the powder diffraction pattern (Intensity vs 2θ)."""
#     wavelength = 12.398 / energy_keV  # Convert energy to wavelength (Å)
#     G_magnitudes = np.linalg.norm(reciprocal_points, axis=1)  # Compute |G|
    
#     # Convert |G| to 2θ using Bragg's Law: 2θ = 2 * arcsin(λG / 4π)
#     theta_2 = 2 * np.arcsin(wavelength * G_magnitudes / (4 * np.pi)) * (180 / np.pi)  # Convert to degrees
    
#     # Create histogram (powder diffraction pattern)
#     hist, bin_edges = np.histogram(theta_2, bins=num_bins, density=True)
#     bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
#     # Plot powder pattern
#     plt.figure(figsize=(8, 5))
#     plt.plot(bin_centers, hist, '-k', lw=1.5)
#     plt.xlabel('2θ (degrees)')
#     plt.ylabel('Intensity (arb. units)')
#     plt.title('Simulated Powder Diffraction Pattern')
#     plt.grid(True)
#     plt.show()

# @njit       
def structure_factor( reciprocal_points, atomic_form_factors, atom_positions, bool_pos_el ):
    '''
    reciprocal_points: 2D ndarray, float
        dim 0: reciprocal lattice points, 1: [qx,qy,qz]
    atomic_form_factors : 2D ndarray, float
        atomic form factors for different elements
        dim0: elements, dim1: q
    unit_cell_pos: 2D ndarray, float
        real space atomic positions
    bool_pos_el : 2D ndarray, string
        mask for uc_pos to find elements
        dim0: element dim1: mask for positions in uc

    Return values
    -------------
    SU_complex: 1D ndarray, complex128
        structure factor of the unit cell, function of Q
        dim0: complex structure factor
    '''
    SU_complex=np.zeros_like(reciprocal_points[:,0], np.complex128)
    nEl=bool_pos_el.shape[0]
    
    for i in range(nEl): #for all elements 
        f=atomic_form_factors[i] #get atomic form factor (for all Qs)
        sComplex=np.zeros_like(SU_complex)
        for r in atom_positions[bool_pos_el[i,:]]: #all atom positions of that element
            qr = np.dot(reciprocal_points,r)
            sComplex += np.exp(qr*1j)
        SU_complex += f*sComplex
    return np.real(SU_complex*SU_complex.conjugate())

def structure_factor_from_cif(cif_path, cutoff_structure_factor=1e-4, max_hkl=4, q_max=60, powder=False):

    crystal_data = parse_cif(cif_path)
    lattice_vectors = crystal_data['lattice_vectors']/10 # assumes angstroem and converts to nm

    #### Calculate reciprocal lattice points
    symmetry = sym.get_proper_point_group(crystal_data['space_group'])
    gen = sym.generators(symmetry)
    Q_gen = rot.QfromOTP(gen)
    Q_group = rot.generate_group(Q_gen) # point group rotational symmetries
    hkl_list_full, hkl_equivalents_full = group_equivalent_reflections(max_hkl, lattice_vectors, Q_group)

    reciprocal_points_full = get_reciprocal_points( lattice_vectors, hkl_list_full )
    q_abs_full = np.linalg.norm(reciprocal_points_full, axis=1)
    # cut at max q
    hkl_list = np.array(hkl_list_full)[q_abs_full < q_max]
    hkl_equivalents = np.array(hkl_equivalents_full)[q_abs_full < q_max]
    reciprocal_points = reciprocal_points_full[q_abs_full < q_max]
    q_abs = q_abs_full[q_abs_full < q_max] 

    #### Calculate atomic form factors
    #
    chem = crystal_data['atom_list'] # chemical symbols of all atoms in the unit cell
    #
    elements = np.unique(chem)
    Nel = elements.size
    #bool mask for the unit cell
    atom_types_bool = np.empty( (Nel, chem.shape[0]), bool )
    for k in range(Nel):
        # determinate the positions of element k 
        atom_types_bool[k,:] = chem == elements[k]
    #
    ff_path = hdl.get_file_path('textom',
        os.path.join('ressources','atomic_formfactors.txt'))
    ffcoeff = np.genfromtxt( ff_path, dtype="|U8", skip_header=2 )
    ffcoeff_used = np.array([ ffcoeff[ np.where( el == ffcoeff )[0][0], 1: ] for el in elements]).astype(data_type)
    a = ffcoeff_used[:,0:-1:2]
    b = ffcoeff_used[:,1:-1:2]
    c = ffcoeff_used[:,-1]
    FF_element = np.empty( (Nel, q_abs.size), np.float64 ) # atomic form factors for all used elements
    for k in range(Nel):
        A, Qf = np.meshgrid( a[k], q_abs ) # using angstroems^-1 here for simplicity
        B, _ = np.meshgrid( b[k], q_abs )
        C = c[k]
        #Calculate form factor http://lampx.tugraz.at/~hadley/ss1/crystaldiffraction/atomicformfactors/formfactors.php
        F = ( A * np.exp( -B * (Qf/(4*np.pi))**2  ) ).sum(axis=1) + C
        # _, FF = np.meshgrid( self.Chi_det.reshape(self.detShape)[0], F )
        FF_element[k,:] = F
    #
    # # plot to verify form factors:
    # idcs = np.argsort(q_abs)
    # plt.plot(q_abs[idcs],FF_element[0,idcs])
    # #

    #### Calculate structure factor from unit cell
    atom_positions = crystal_data['cartesian_positions']/10 # coordinates of all atoms in the unit cell converted to nm
    structure_factors = structure_factor( reciprocal_points, FF_element, atom_positions, atom_types_bool)
    # # plot to verify structure factors:
    # idcs = np.argsort(q_abs)
    # plt.plot(q_abs[idcs],structure_factors[idcs], 'x')
    # #

    # exclude non-diffracting peaks from here (cut-off - corresponds to extinction conditions)
    mask_diffracting_peaks = structure_factors > cutoff_structure_factor*structure_factors.max()
    mask_diffracting_peaks[0] = False # exclude [0 0 0]
    q_used = q_abs[mask_diffracting_peaks]
    hkl_used = hkl_list[mask_diffracting_peaks]
    structure_factors_used = structure_factors[mask_diffracting_peaks]
    hkl_equivalents_used = hkl_equivalents[mask_diffracting_peaks]
    multiplicities_used = np.array([len(eq) for eq in hkl_equivalents_used])
    reciprocal_points_used = reciprocal_points[mask_diffracting_peaks]

    order = np.argsort(q_used)
    q_used = q_used[order]
    hkl_used = hkl_used[order]
    structure_factors_used = structure_factors_used[order]
    multiplicities_used = multiplicities_used[order]
    hkl_equivalents_used = hkl_equivalents_used[order] # not returned atm
    reciprocal_points_used = reciprocal_points_used[order]

    reciprocal_points_used_full = np.concatenate([
        get_reciprocal_points(lattice_vectors, np.array(list(hkl_eq))) for hkl_eq in hkl_equivalents_used]
    )

    if powder:
        return q_used, hkl_used, structure_factors_used, multiplicities_used
    else:
        return q_used, reciprocal_points_used_full, structure_factors_used, multiplicities_used, hkl_used, symmetry
    # schreit nach einem structure_dict oder object

def plot_powder_pattern(cif_path, cutoff_structure_factor=1e-4, max_hkl=4, q_max=60):
    
    q, hkl, S, M = structure_factor_from_cif(cif_path, cutoff_structure_factor, max_hkl, q_max=q_max, powder=True)
    powder_intensities = S * M
    # plt.plot( q_used, powder_intensities, 'x' )
    print('hkl\tq\tInt\t\tRelative I\tMultiplicity')
    plt.figure()
    for (xi, yi, l, m) in zip(q, powder_intensities, hkl, M):
        plt.plot([xi,xi],[0,yi],'r')
        plt.text(xi, yi, l, va='bottom', ha='center')
        print(f'{l}\t{xi:5.3}\t{yi:8.1f}\t{100*yi/powder_intensities.max():.1f}\t{m}')
    plt.ylim(bottom=0)
    plt.show()

# @njit
# def quaternion_to_match_vectors(u, v):
#     """
#     Returns the quaternion (w, x, y, z) that rotates unit vector u into v.
#     u and v must be 3D unit vectors.
#     """
#     u = np.asarray(u, dtype=np.float64)
#     v = np.asarray(v, dtype=np.float64)
#     u /= np.linalg.norm(u)
#     v /= np.linalg.norm(v)

#     dot = np.dot(u, v)

#     if np.isclose(dot, 1.0):
#         # Vectors are the same
#         return np.array([1.0, 0.0, 0.0, 0.0])
#     elif np.isclose(dot, -1.0):
#         # Vectors are opposite
#         # Find an orthogonal vector
#         orthogonal = np.array([1.0, 0.0, 0.0])
#         if np.isclose(abs(u[0]), 1.0):
#             orthogonal = np.array([0.0, 1.0, 0.0])
#         axis = np.cross(u, orthogonal)
#         axis /= np.linalg.norm(axis)
#         return np.array([0.0, *axis])  # 180° rotation: w=0
#     else:
#         axis = np.cross(u, v)
#         axis /= np.linalg.norm(axis)
#         angle = np.arccos(nb.nb_clip(dot, -1.0, 1.0))
#         w = np.cos(angle / 2.0)
#         xyz = axis * np.sin(angle / 2.0)
#         return np.concatenate(([w], xyz))

@njit
def quaternion_to_match_vectors(u, v):
    u = nb.nb_vectornorm(u.astype(np.float64))
    v = nb.nb_vectornorm(v.astype(np.float64))

    d = nb.nb_dot(u, v)

    # Same direction
    if abs(d - 1.0) < 1e-12:
        return np.array([1.0, 0.0, 0.0, 0.0])

    # Opposite direction
    elif abs(d + 1.0) < 1e-12:
        # Find an orthogonal axis
        if abs(u[0]) < 0.9:
            ortho = np.array([1.0, 0.0, 0.0])
        else:
            ortho = np.array([0.0, 1.0, 0.0])
        axis = nb.nb_cross(u, ortho)
        axis = nb.nb_vectornorm(axis)
        return np.array([0.0, axis[0], axis[1], axis[2]])

    # General case
    else:
        axis = nb.nb_cross(u, v)
        axis = nb.nb_vectornorm(axis)
        # Clip dot to [-1,1] manually to avoid NaNs
        dd = d
        if dd > 1.0: dd = 1.0
        elif dd < -1.0: dd = -1.0
        angle = np.arccos(dd)
        w = np.cos(angle/2.0)
        s = np.sin(angle/2.0)
        return np.array([w, axis[0]*s, axis[1]*s, axis[2]*s])

@njit
def get_probability(q_peak, q_detector, odf_basis_function, odf_args, sampling=300):
    ''' 
    Paramters:
    --------
    q_peak: 1d ndarray, float 
        peak location in reciprocal space (in base orientation)
    q_detector: 1d ndarray, float
        desired peak location after rotation
    orientation_distribution: function
        probability function
    odf_args : tuple
        input for the function

    Returns:
    -------------
    proba: float
        probability that peak gets turned into q, given the ODF(mu,sig/kap)

    returns the probabilty that peak appears at q (given some parameters for the underlying distribution),
    by summing the probability of all rotations that rotate the crystal accordingly
    '''

    if np.abs(np.linalg.norm(q_detector)-np.linalg.norm(q_peak)) > 1e-3: # 1e-10 is maybe a bit strict
        print("Can't rotate peak into desired q - check input")
        return
    
    # Find a rotation that rotates the bragg peak on the detector pixel
    R_align = quaternion_to_match_vectors( q_peak, q_detector )

    # Define quaternion orientations that will produce the same bragg peaks
    axis = q_detector/np.linalg.norm(q_detector) # i,j,k parts of Rot2
    ome = np.linspace(-np.pi, np.pi , sampling)
    w = np.cos(ome/2)
    ijk = np.zeros((sampling, 3)) 
    for i in range(3):
        ijk[:,i] = np.sin(ome/2) * axis[i]
    R_sampling = np.hstack((np.atleast_2d(w).T , ijk))

    R_sampling[R_sampling[:,0]<0] = -R_sampling[R_sampling[:,0]<0]

    Rotations = np.zeros_like(R_sampling)
    for i in range(sampling):
        Rotations[i] = rot.quaternion_multiply( R_sampling[i], R_align)

    # orot = Rotation(Rotations)
    # oori = Orientation(orot, symmetry=point_group)
    # orot_fz = oori < OrientationRegion(point_group)

    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(Rotations[:,1],Rotations[:,2],Rotations[:,3])
    # ax.set_xlim((-1,1))
    # ax.set_ylim((-1,1))
    # ax.set_zlim((-1,1))

    # evaluate the basis function at these orientations
    Probabilities = odf_basis_function( Rotations, *odf_args )

    probability_integrated = np.sum(Probabilities) * 2*np.pi/sampling
    return probability_integrated


@njit
def diffractlet( detector_coordinates, reciprocal_points, structure_factors, multiplicities,
                odf_basis_function, odf_args ):

    n_peaks = structure_factors.size
    odf = np.zeros( detector_coordinates.shape[:2], np.complex128 ) # need complex for HSH
    for i_peak in range(n_peaks):
        for i_chi, q_detector in enumerate(detector_coordinates[i_peak]): 
            # for q in Q_group:
            #     point = rot.quaternion_rotate_vector(q, reciprocal_points[i_peak].copy())
            #     odf[i_peak, i_chi] += get_probability( 
            #         point, q_detector.copy(), 
            #         odf_basis_function, odf_args, sampling=100)
            #     # # friedel partner 
            #     # odf[i_peak, i_chi] += get_probability( 
            #     #     -point, q_detector.copy(), 
            #     #     odf_basis_function, odf_args, sampling=100)
            for k in range(multiplicities[i_peak]):
                idx = multiplicities[:i_peak].sum() + k
                odf[i_peak, i_chi] += get_probability( 
                    reciprocal_points[idx].copy(), q_detector.copy(), 
                    odf_basis_function, odf_args, sampling=100)
        # # ### test good sampling
        # samplings = np.logspace(np.log(50),np.log(10000),num=50,base=np.exp(1)).astype(int)
        # probabilities = []
        # for s in samplings:
        #     probabilities.append(get_probability( # angular coordinate missing
        #         reciprocal_points[i_peak].copy(), q_detector.copy(), 
        #         odf_basis_function, odf_args, sampling=s ))
        # plt.semilogx( samplings, np.array(probabilities)/probabilities[-1] )
        # # 100 - 1% off
        # # 200 - 0.5% off
        # # 900 - 0.1% off
        
        # print(f'\n\tFinished peak Nr.{i_peak+1}/{n_peaks}')

    difflet = odf * structure_factors[:,np.newaxis]
    return difflet

@njit
def hsh_wrapper(orientations_q, n, l, m):
    """
    Vectorized version: orientations in OTP notation
    Returns a 1D complex128 array of results.
    """
    OTP = rot.OTPfromQ(orientations_q)
    N = orientations_q.shape[0]
    out = np.empty(N, dtype=np.complex128)
    for i in range(N):
        out[i] = hsh.Z_numba(OTP[i,0], OTP[i,1], OTP[i,2], n, l, m)
    return out

@njit(parallel=True)
def diffractlets_parallel_hsh( order, symmetrization_matrix, 
                                detector_coordinates, sample_rotations,
                                reciprocal_points, multiplicities, structure_factors):
    
    n_difflets, n_hsh = symmetrization_matrix.shape

    lm = np.empty((n_hsh, 2), dtype=np.int64)
    idx = 0
    for l in range(order+1):
        for m in range(-l, l+1):
            lm[idx, 0] = l
            lm[idx, 1] = m
            idx += 1

    n_rotations = sample_rotations.shape[0]
    Gs = rot.OTPfromQ(sample_rotations)

    difflets_hsh = np.empty( (n_hsh, n_difflets, *detector_coordinates.shape[:2]), np.complex128 )
    for k in prange( n_hsh ):
        # calculate complex HSH diffractlet
        hsh_difflet = diffractlet( 
                detector_coordinates.astype(np.float64), 
                reciprocal_points.astype(np.float64), structure_factors.astype(np.float64), multiplicities,
                hsh_wrapper, (order,lm[k,0],lm[k,1]) )
        # symmetrize
        for i_shsh in range(n_difflets):
                difflets_hsh[k, i_shsh] = symmetrization_matrix[i_shsh, k] * hsh_difflet
    difflets = np.real( difflets_hsh.sum(axis=0) )

    difflets_rot = np.empty( (n_rotations, n_difflets, detector_coordinates.shape[0], detector_coordinates.shape[1]), 
                data_type )
    rotations_sHSH = hsh.Rs_n_stack( np.column_stack( (-Gs[:,0], Gs[:,1], Gs[:,2]) ).astype(np.float64),
                                    order, symmetrization_matrix )
    for g, Rs_g in enumerate(rotations_sHSH):
        # difflets_rot[g] = (Rs_g @ difflets.reshape((difflets.shape[0], difflets.shape[1]*difflets.shape[2]))).reshape(difflets.shape)
        difflets_rot[g] = rotate_difflets( Rs_g, difflets)

    return difflets_rot, difflets_hsh

@njit
def rotate_difflets(Rs_g, difflets):
    n, _ = Rs_g.shape
    _, m, l = difflets.shape
    C = np.zeros((n, m, l), Rs_g.dtype)
    for i in range(n):
        for j in range(m):
            s = np.zeros(l, Rs_g.dtype)
            for k in range(n):
                s += Rs_g[i, k] * difflets[k, j]
            C[i, j] = s
    return C

@njit(parallel=True)
def diffractlets_parallel_grid( resolution, Q_grid, Q_group, 
                                detector_coordinates, sample_rotations,
                                reciprocal_points, multiplicities, structure_factors ):
    
    n_rotations = sample_rotations.shape[0]
    n_difflets = Q_grid.shape[0]
    difflets = np.empty( (n_rotations, n_difflets, *detector_coordinates.shape[:2]), np.complex128 )
    for g in prange(n_rotations):
        reciprocal_points_rot = np.empty_like(reciprocal_points)
        for p in range(reciprocal_points.shape[0]):
            reciprocal_points_rot[p] = rot.quaternion_rotate_vector(sample_rotations[g], reciprocal_points[p])

        for k in range( n_difflets ):
            difflets[g,k] = diffractlet( 
                    detector_coordinates.astype(np.float64), 
                    reciprocal_points_rot.astype(np.float64), structure_factors.astype(np.float64), multiplicities,
                    # grd.fisher_SO3, 
                    # (Q_grid[k].astype(np.float64), 10/(resolution*np.pi/180)**2, Q_group.astype(np.float64))                
                    grd.gaussian_SO3, 
                    (Q_grid[k].astype(np.float64), resolution*np.pi/180 / 2, Q_group.astype(np.float64))
                    )

    return np.real(difflets).astype(data_type)

def get_diffractlets( cr, chi_det, geo, sample_rotations, max_order=4, resolution=25, cutoff_structure_factor=1e-4, mode='hsh' ):
    """Maybe change resolution to Q_grid, then I can define it outside.

    Parameters
    ----------
    cr : _type_
        _description_
    chi_det : _type_
        _description_
    geo : _type_
        _description_
    sample_rotations : _type_
        _description_
    orders : list or int, optional
        HSH orders, by default 4
    resolution : int, optional
        _description_, by default 25
    cutoff_structure_factor : float, optional
        _description_, by default 1e-4
    mode : str, optional
        _description_, by default 'hsh'

    Returns
    -------
    _type_
        _description_
    """
    # Qq_det, Chi_det, detShape = rot.qchi(q_det, chi_det)
    # get_reciprocal_space_coordinates()

    q_hkl, reciprocal_points_full, structure_factors, multiplicities, hkl, symmetry = structure_factor_from_cif( 
        cr.cifPath, q_max=cr.q_range[1], cutoff_structure_factor=cutoff_structure_factor )
    Qq_det, Chi_det, detShape = rot.qchi(q_hkl, chi_det)
    detector_coordinates = get_reciprocal_space_coordinates( Qq_det, Chi_det, cr.E_keV, geo )
    detector_coordinates = detector_coordinates.reshape((*detShape,3))
    pg = getattr( osym, sym.get_SFnotation( symmetry ) )

    print('\tRetrieved reciprocal space coordinates, calculating diffractlets')
    t0 = time()
    if mode=='hsh':
        ns = hsh.get_orders(symmetry, max_order, info=False)
        difflets_n = []
        for order in ns:
            if order==0:
                difflets = np.array(np.full( (sample_rotations.shape[0],1,*detShape), 
                                np.atleast_2d( structure_factors*multiplicities).T ), data_type)
            else:
                symmetrization_matrix, slices_order = hsh.symmetrization_matrix( np.atleast_1d(ns), symmetry )
                difflets,_ = diffractlets_parallel_hsh( order, symmetrization_matrix[str(order)],
                            detector_coordinates, sample_rotations,
                            reciprocal_points_full, multiplicities, structure_factors)
                # n_difflets = symmetrization_matrix[str(order)].shape[0]
                # difflets = np.zeros( (n_difflets, *detector_coordinates.shape[:2]), np.complex128 )
                # k = 0
                # for l in range(order):
                #     for m in range(-l,l+1):
                #         # calculate complex HSH diffractlet
                #         hsh_difflet = diffractlet( detector_coordinates, reciprocal_points, structure_factors, 
                #                     hsh.Z, (order,l,m) )
                #         # symmetrize
                #         for i_shsh in range(n_difflets):
                #                 difflets[i_shsh] += symmetrization_matrix[str(order)][i_shsh, k] * hsh_difflet
                #         k+=1
                #         # print(f'\tfinished n={order}, l={l}, m={m}')
            difflets_n.append(difflets)
            print(f'\t\tfinished order {order}')
        
        difflets_full = np.concatenate(difflets_n, axis=1)

    elif mode=='grid':
        
        Q_grid = rot.get_sample_fundamental(
                        resolution,
                        point_group= pg,
                        method='cubochoric'
                ).data.astype(data_type)
        
        # Q_grid = rot.QfromOTP(np.array([[0,0,0], [np.pi/2,np.pi/2,np.pi/2]]))
        # resolution = 10

        generators = sym.generators(symmetry)
        q_gen = rot.QfromOTP(generators)
        Q_group = rot.generate_group(q_gen)
        difflets_full = diffractlets_parallel_grid( resolution, Q_grid,#[36:38], 
                    Q_group, detector_coordinates, sample_rotations,
                    reciprocal_points_full, multiplicities, structure_factors, )
        # print(Q_grid)

    else:
        print('mode not recognized, choose hsh or grid')
        return 0
    
    print(f'\t\ttook {(time()-t0)/60:.2f} min')
    return Qq_det.reshape(detShape), Chi_det.reshape(detShape), hkl, difflets_full, symmetry


def plot_diffractlet( Qq_det, Chi_det, hkl, difflet, q_bins=50, cmap='bwr', logscale=False, sym_cmap=True ):

    f = plt.figure(figsize=(12,6))
    ax1 = f.add_subplot(121)
    ax2 = f.add_subplot(122, projection='polar')

    chi = Chi_det[0] 
    q_peaks = Qq_det[:,0]

    if isinstance(q_bins,np.ndarray):
        q_plot = q_bins
    else:
        q_plot = np.linspace(q_peaks[0],q_peaks[-1],num=q_bins)
    difflet_plot = np.zeros((q_plot.size, difflet.shape[1]))
    for k in range(difflet.shape[0]):
        l = np.argmin(np.abs(q_plot-q_peaks[k]))
        difflet_plot[l,:] += difflet[k,:]
    Chi_plot, Q_plot = np.meshgrid(chi,q_plot)

    from matplotlib.colors import LogNorm, TwoSlopeNorm
    if logscale:
        difflet_log = difflet_plot - difflet_plot.min() + 1e-3
        ax1.pcolormesh(Q_plot, Chi_plot* 180/np.pi, difflet_log, cmap=cmap, norm=LogNorm())
        im=ax2.pcolormesh(Chi_plot, Q_plot, difflet_log, cmap=cmap, norm=LogNorm())
    elif sym_cmap:
        ax1.pcolormesh(Q_plot, Chi_plot* 180/np.pi, difflet_plot, cmap=cmap, norm=TwoSlopeNorm(vcenter=0))
        im=ax2.pcolormesh(Chi_plot, Q_plot, difflet_plot, cmap=cmap, norm=TwoSlopeNorm(vcenter=0))
    else:
        ax1.pcolormesh(Q_plot, Chi_plot* 180/np.pi, difflet_plot, cmap=cmap )
        im=ax2.pcolormesh(Chi_plot, Q_plot, difflet_plot, cmap=cmap )

    ax1.set_xlabel('q [nm^-1]')
    ax1.set_ylabel('chi [degree]')
    ax_top = ax1.twiny()
    ax_top.set_xlim(ax1.get_xlim())  # sync limits
    ax_top.set_xticks(q_peaks, labels=hkl)
    ax_top.tick_params(axis='x', labelrotation=45) 
    # ax1.set_xticks(q_peaks, labels=hkl )
    f.colorbar(im)
    f.tight_layout()

def plot_single_crystal_pattern(cr, cutoff_structure_factor=1e-4, axis=0):
    "very simple plot, axis (either 0,1,2) defines the beam direction with respect to the crystal structure"
    q_hkl, reciprocal_points_full, structure_factors, multiplicities, hkl, symmetry = structure_factor_from_cif( 
        cr.cifPath, q_max=cr.q_range[1], cutoff_structure_factor=cutoff_structure_factor )

    def other_axes(n:int):
        if n==0:
            return (1,2)
        elif n==1:
            return (2,0)
        elif n==2:
            return (0,1)
    det_axes = other_axes(axis)

    peaks = []
    for point in reciprocal_points_full:
        if np.abs(point[axis]) < 1e-2:
            peaks.append((point[det_axes[0]], point[det_axes[1]]))
    peaks = np.array(peaks)
    plt.scatter(peaks[:,0], peaks[:,1])
                         
    