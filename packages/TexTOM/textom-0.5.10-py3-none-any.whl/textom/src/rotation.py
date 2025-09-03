import numpy as np
from numba import njit, prange
from orix.sampling import get_sample_fundamental
import orix.quaternion.symmetry as osym 
from orix.quaternion import Orientation, Rotation
from scipy.spatial import ConvexHull

from . import symmetries as sym
from . import numba_plugins as nb
from ..config import data_type

def define_angles( dchi=2*np.pi/120, sampling='cubochoric', symmetry='222', ):
    """Defines the grid of angles for crystallite rotation

    Parameters
    ----------
    dchi : _type_, optional
        _description_, by default 2*np.pi/120
    sampling : str, optional
        _description_, by default 'cubochoric'
    symmetry : str, optional
        _description_, by default '222'

    Returns
    -------
    Gc : 2D ndarray, float
        register of axis-angle rotations
        dim: 0: rotation index, 1: [omega, theta, phi]
    dV : 1D ndarray, float
        volume element for integrating over the odf
        dim: 0: rotation index
    V_fz : float
        volume of the fundamental zone
    """
    try:
        if sampling=='cubochoric':
            pg = getattr( osym, sym.get_SFnotation( symmetry ) )
            rot_orix = get_sample_fundamental(
                    dchi*180/np.pi, 
                    point_group= pg,
                    method=sampling
            )
            
            Gc = OTPfromQ(rot_orix.data)

            # cubochoric is equal volume mapped
            # Sing and De Graef, 2016
            dV = 1/dchi**3 * np.ones( 
                Gc.shape[0], data_type)
    except:
        sampling = 'simple'
    
    if sampling == 'simple':
        ## set up angles used to rotate the single crystal patterns
        ome = np.linspace( 
            dchi/2, np.pi-dchi/2, int(np.pi/dchi), endpoint=True)
        tta = np.linspace( 
            dchi/2, np.pi-dchi/2, int(np.pi/dchi), endpoint=True)
        phi = np.linspace( 0, 2*np.pi, int(2*np.pi/dchi), endpoint=False)
        TTA, PHI, OME = np.meshgrid(tta, phi, ome)
        Ome, Tta, Phi = OME.flatten(), TTA.flatten(), PHI.flatten()
        Gc = np.column_stack((Ome,Tta,Phi))

        ## apply the crystal symmetry conditions on Tta, Phi, Ome, so in the following 
        # only these are calculated by only choosing rotations in the fundamental zone 
        # of the proper point group
        fz = sym.zone(symmetry,Gc)
        Tta, Phi, Ome = Tta[fz], Phi[fz], Ome[fz] # these are the angles that effectively will be used
        Gc = Gc[fz] # cut away the redundand ones from the rotation array

        # volume element for integrating over the odf
        # see Mason/Patala, arXiv (2019), appendix C
        # omitted factor 1/2 here, since we use omega only from 0 to pi
        dV = np.sin(Ome/2)**2 * np.sin(Tta) * dchi**3 

    # import matplotlib.pyplot as plt
    # fig = plt.figure(figsize=(15, 10))
    # scatter_kwargs = dict(
    #     projection="rodrigues",
    #     figure=fig,
    #     wireframe_kwargs=dict(color="k", linewidth=1, alpha=0.1),
    #     s=5,
    # )
    # ori_plain = Orientation(Rotation([rot.QfromOTP( Gc)]), symmetry=pg).get_random_sample(10000)
    # ori_orix = Orientation(rot_orix, symmetry=pg).get_random_sample(10000)
    # ori_orix.scatter(position=231, c="C0", **scatter_kwargs)
    # ori_plain.scatter(position=232, c="C1", **scatter_kwargs)
    # # ori_quat2.scatter(position=233, c="C2", **scatter_kwargs)

    # ori_orix.scatter(position=234, c="C0", **scatter_kwargs)
    # ori_plain.scatter(position=235, c="C1", **scatter_kwargs)
    # # ori_quat2.scatter(position=236, c="C2", **scatter_kwargs)

    # titles = ["cubochoric", "plain"]#, "quaternion"]
    # for i, title in zip([0, 1], titles):
    #     fig.axes[i].view_init(elev=90, azim=0)
    #     fig.axes[i].set_title(titles[i])
    # for i in [2, 3]:
    #     fig.axes[i].view_init(elev=0, azim=0)

    # volume of the fundamental zone [rad^3]
    V_fz = dV.sum()
    return Gc, dV, V_fz

def qchi(q,chi):
    """ Makes arrays with q and chi values for each detector point

    Parameters
    ----------
    q : 1D ndarray
        momentum exchange
    chi : 1D ndarray
        azimuthal angle on detector

    returns: 
    ------------
    Q, Chi : 1D ndarray, float
        flattened meshgrids of q and chi, representing all detector points
    detshape : tuple, int
        number of q and phi values
    """
    CHi,QQ = np.meshgrid(chi,q)
    detshape = CHi.shape
    Chi, Q = CHi.flatten(), QQ.flatten()
    return Q, Chi, detshape

"""
Some functions helping to convert between different rotation conventions,
to perform rotations and to handle quaternions
"""

def XAfromOTP(ome,tta,phi):
    """ Creates an axis-angle vector from 3 angles omega, theta, phi

    Parameters
    ----------
    omega : ndarray, float
        rotation angle, usually ∈[0,pi)
    theta : ndarray, float
        polar angle of the rotation axis, usually ∈[0,pi)
    phi : ndarray, float
        azimutal angle of the rotation axis, usually ∈[0,2pi)

    Return values
    ------------
    XA : 2D ndarray, float
        array of axis-angle vectors with 3 entries
    """
    XA = np.column_stack([
            ome * np.sin(tta) * np.cos(phi),
            ome * np.sin(tta) * np.sin(phi),
            ome * np.cos(tta)
        ])
    return XA

def OTPfromXA(V):
    """ Extracts the 3 angles omega, theta, phi from an axis-angle vector

    Parameters
    ----------
    XA : 2D ndarray, float
        array of axis-angle vectors with 3 entries

    Return values
    ------------
    omega : ndarray, float
        rotation angle, usually ∈[0,pi)
    theta : ndarray, float
        polar angle of the rotation axis, usually ∈[0,pi)
    phi : ndarray, float
        azimutal angle of the rotation axis, usually ∈[0,2pi)
    """
    ome = np.sqrt((V**2).sum(axis=1))
    tta = np.arccos(np.divide(V[:,2],ome, where=(ome!=0)))
    phi = np.sign(V[:,1]) * np.arccos(
        np.divide(V[:,0],np.sqrt(V[:,0]**2+V[:,1]**2), where=[a[0]!=0 or a[1]!=0 for a in V]) )
    return ome, tta, phi

def RodfromOTP(ome,tta,phi):
    """ Creates a Rodrigues vector from 3 angles omega, theta, phi

    Parameters
    ----------
    omega : ndarray, float
        rotation angle, usually ∈[0,pi)
    theta : ndarray, float
        polar angle of the rotation axis, usually ∈[0,pi)
    phi : ndarray, float
        azimutal angle of the rotation axis, usually ∈[0,2pi)

    Return values
    ------------
    Rod : 2D ndarray, float
        array of Rodrigues vectors with 3 entries
    """
    Rod = np.column_stack([
            np.tan(ome/2) * np.sin(tta) * np.cos(phi),
            np.tan(ome/2) * np.sin(tta) * np.sin(phi),
            np.tan(ome/2) * np.cos(tta)
        ])
    return Rod

@njit#(parallel=True)
def QfromOTP( OTP ):
    """ Creates Quaternions from 3 angles omega, theta, phi

    Parameters
    ----------
    OTP : 2D ndarray, float
        stack of angles for axis-angle rotations
        dim 0: rotation index, 1: [omega, theta, phi]

    Return values
    ------------
    Q : 2D ndarray, float
        stack of quaternions with 4 entries
        dim 0: rotation index, 1: [q0, q1, q2, q3]
    """
    Q = np.empty( (OTP.shape[0],4), data_type )
    for g in prange(OTP.shape[0]):
        ome, tta, phi = OTP[g,0], OTP[g,1], OTP[g,2]
        Q[g] = np.array([
                np.cos(ome/2),
                np.sin(ome/2) * np.sin(tta) * np.cos(phi),
                np.sin(ome/2) * np.sin(tta) * np.sin(phi),
                np.sin(ome/2) * np.cos(tta)
            ])
    Q[Q[:,0] < 0] *= -1
    return Q

@njit#(parallel=True)
def OTPfromQ( Q ):
    """ Extracts the 3 angles omega, theta, phi from a quaterion

    Parameters
    ----------
    Q : 2D ndarray, float
        stack of quaternions with 4 entries
        dim 0: rotation index, 1: [q0, q1, q2, q3]

    Return values
    ------------
    OTP : 2D ndarray, float
        stack of angles for axis-angle rotations
        dim 0: rotation index, 1: [omega, theta, phi]
    """
    OTP = np.empty( (Q.shape[0],3), data_type )
    for g in prange(Q.shape[0]):
        r = np.sqrt( (Q[g,1:]**2).sum() )
        OTP[g] = np.array([
            2 * np.arctan2( r, Q[g,0] ),
            np.arctan2( np.sqrt( Q[g,1]**2 + Q[g,2]**2 ), Q[g,3] ),
            np.arctan2( Q[g,2], Q[g,1] ),
        ])
    OTP[ OTP[:,2]<0, 2 ] += 2*np.pi
    return OTP
        
@njit
def OTP_to_matrix( ome, tta, phi ):
    """ Creates rotation matrices from 3 angles omega, theta, phi

    Parameters
    ----------
    omega : ndarray, float
        rotation angle, usually ∈[0,pi)
    theta : ndarray, float
        polar angle of the rotation axis, usually ∈[0,pi)
    phi : ndarray, float
        azimutal angle of the rotation axis, usually ∈[0,2pi)

    Return values
    ------------
    R : ndarray, float
    """
    x = np.sin(tta) * np.cos(phi)
    y = np.sin(tta) * np.sin(phi)
    z =  np.cos(tta)
    so = np.sin(ome)
    co = np.cos(ome)
    R = np.array([
        [ co + x**2*(1-co), x*y*(1-co) - z*so, x*z*(1-co) + y*so ],
        [ y*x*(1-co) + z*so, co + y**2 *(1-co), y*z*(1-co) - x*so ],
        [ z*x*(1-co) - y*so, z*y*(1-co) + x*so, co + z**2 *(1-co) ]
    ])
    return R.astype(data_type)

@njit
def stack_mrot( vs, OTP ):
    """ Rotates a stack of vectors by a list of rotations

    Parameters
    ----------
    vs : 2D ndarray, float
        stack of vectors
        dim 0: vector index, 1: [x,y,z]
    OTP : 2D ndarray, float
        stack of angles for axis-angle rotations
        dim 0: rotation index, 1: [omega, theta, phi]

    Return values
    ------------
    R : ndarray, float
    """
    Nrot = OTP.shape[0]
    vs_rot = np.empty( ( Nrot, vs.shape[0], 3 ), data_type)
    for g in prange( Nrot ):
        R = OTP_to_matrix( OTP[g,0], OTP[g,1], OTP[g,2] ).T
        vs_rot[g] = vs @ R
    return vs_rot

@njit(parallel=True)
def ang_distance( q1, q2, gen ):
    """ Calculates the closest distance between 2 quaternions
    respecting a crystal symmetry represented by symmetry generators

    Q. Huynh, Metrics for 3d rotations: Comparison and analysis, 
    Journal of Mathematical Imaging and Vision, vol. 35, pp. 155-164, 2009.

    Parameters
    ----------
    q1, q2 : 2D ndarray, float
        stacks of quaternions
    gen : 2D ndarray, float
        2 symmetry generators in OTP representation
        [[ome1,tta1,phi1], [ome2,tta2,phi2]]

    Return values
    ------------
    DQ : ndarray, float
    """
    DQ = np.empty(q1.shape[0], data_type )
    # make quaternions from generators
    Q_gen = QfromOTP( gen )
    n1 = int(2*np.pi / gen[0,0]) # n1-fold symmetry from 1st generator
    n2 = int(2*np.pi / gen[1,0]) # n2-fold symmetry from 2nd generator
    for k in prange(q1.shape[0]):
        dq = np.pi
        qc = q2[k]
        for _ in range(n1):
            qc = quaternion_multiply( qc, Q_gen[0] ) # rotate point by 1st generator
            for _ in range(n2):
                qc = quaternion_multiply( qc, Q_gen[1] ) # rotate point by 2st generator
                # add to the odf according to the real quaternion distance
                r = 2*(qc*q1[k]).sum()**2 - 1
                if np.abs(r) > 1:
                    r /= np.abs(r) # this is for rounding errors
                dq = min(dq, np.arccos( r ))
        DQ[k] = dq
    return DQ

@njit(parallel=True)
def misorientation( q1, q2, gen ):
    """ Calculates the closest distance between 2 quaternions
    respecting a crystal symmetry represented by symmetry generators

    Q. Huynh, Metrics for 3d rotations: Comparison and analysis, 
    Journal of Mathematical Imaging and Vision, vol. 35, pp. 155-164, 2009.

    Parameters
    ----------
    q1, q2 : 2D ndarray, float
        stacks of quaternions
    gen : 2D ndarray, float
        2 symmetry generators in OTP representation
        [[ome1,tta1,phi1], [ome2,tta2,phi2]]

    Return values
    ------------
    DQ : ndarray, float
    """
    DQ = np.empty(q1.shape[0], data_type )
    # make quaternions from generators
    Q_gen = QfromOTP( gen )
    if gen[0,0] > 0:
        n1 = int(2*np.pi / gen[0,0]) # n1-fold symmetry from 1st generator
    else:
        n1=1
    if gen[1,0] > 0:
        n2 = int(2*np.pi / gen[1,0]) # n2-fold symmetry from 2nd generator
    else:
        n2=1
    for k in prange(q1.shape[0]):
        dq = np.pi
        qa = q1[k]
        qb = q2[k]
        for _ in range(n1):
            qa = quaternion_multiply( Q_gen[0], qa ) # rotate point by 1st generator
            for _ in range(n2):
                qa = quaternion_multiply( Q_gen[1], qa ) # rotate point by 2st generator
                for _ in range(n1):
                    qb = quaternion_multiply( qb, Q_gen[0] ) # rotate point by 1st generator
                    for _ in range(n2):
                        qb = quaternion_multiply( qb, Q_gen[1] ) # rotate point by 2st generator
                        # add to the odf according to the real quaternion distance
                        r = 2*(qa*qb).sum()**2 - 1
                        if np.abs(r) > 1:
                            r /= np.abs(r) # this is for rounding errors
                        dq = min(dq, np.arccos( r ))
        DQ[k] = dq
    return DQ

@njit()
def misorientation_single( qa, qb, gen ):
    """ Calculates the closest distance between 2 quaternions
    respecting a crystal symmetry represented by symmetry generators

    Q. Huynh, Metrics for 3d rotations: Comparison and analysis, 
    Journal of Mathematical Imaging and Vision, vol. 35, pp. 155-164, 2009.

    Parameters
    ----------
    q1, q2 : 1D ndarray, float
        quaternions to compare
    gen : 2D ndarray, float
        2 symmetry generators in OTP representation
        [[ome1,tta1,phi1], [ome2,tta2,phi2]]

    Return values
    ------------
    DQ : ndarray, float
    """
    # make quaternions from generators
    Q_gen = QfromOTP( gen )
    n1 = int(2*np.pi / gen[0,0]) # n1-fold symmetry from 1st generator
    n2 = int(2*np.pi / gen[1,0]) # n2-fold symmetry from 2nd generator
    dq = np.pi
    for _ in range(n1):
        qa = quaternion_multiply( Q_gen[0], qa ) # rotate point by 1st generator
        for _ in range(n2):
            qa = quaternion_multiply( Q_gen[1], qa ) # rotate point by 2st generator
            for _ in range(n1):
                qb = quaternion_multiply( qb, Q_gen[0] ) # rotate point by 1st generator
                for _ in range(n2):
                    qb = quaternion_multiply( qb, Q_gen[1] ) # rotate point by 2st generator
                    # add to the odf according to the real quaternion distance
                    r = 2*(qa*qb).sum()**2 - 1
                    if np.abs(r) > 1:
                        r /= np.abs(r) # this is for rounding errors
                    dq = min(dq, np.arccos( r ))
    return dq

@njit
def quaternion_multiply(q1, q2):
    """ Multiplies 2 quaternions according to their rules

    Parameters
    ----------
    q1, q2 : ndarray, float
        quaternions [q0, q1, q2, q3]

    Return values
    ------------
    multiplied quaternion [q0, q1, q2, q3]
    """
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return np.array([w, x, y, z], data_type)

@njit()
def quaternion_rotate_vector(q, v):
    """Rotate vector v by quaternion q."""
    q_conj = np.array([q[0], -q[1], -q[2], -q[3]])
    v_quat = np.array([0.0, *v])
    rotated = quaternion_multiply(
        quaternion_multiply(q, v_quat),
        q_conj
    )
    return rotated[1:]  # return x, y, z

def mean_orientation(Qc, odf):
    """Quaternion Averaging via Eigen Decomposition (Markley et al. 2007)
    Works only in full SO(3), not respecting symmetries.

    Parameters
    ----------
    Qc : 2d ndarray (N,4)
        array of quaternions 
    odf : 1d ndarray (N)
        weight for each quaternion

    Returns
    -------
    ndarray (4)
        average quaternion
    """
    # Handle sign ambiguity
    for i in range(1, Qc.shape[0]):
        if np.dot(Qc[0], Qc[i]) < 0:
            Qc[i] = -Qc[i]

    # Build the symmetric accumulator matrix
    A = np.zeros((4,4),data_type)
    for k, o in enumerate(odf):
        A += o * np.outer(Qc[k],Qc[k])
    A /= odf.sum()
    # Compute the eigenvector corresponding to the largest eigenvalue
    eigvals, eigvecs = np.linalg.eigh(A)
    avg_quaternion = eigvecs[:, np.argmax(eigvals)]

    return -avg_quaternion

def samplerotations_eq3D( d_rot, tilts ):
    """ Calculates rotation and tilt angles equally spaced over a sphere

    Parameters
    ----------
    d_rot : float
        distance between rotations at zero tilt in degree
    tilts : list of int
        list of tilt angles in degree

    returns: 
    ------------
    Omega, Kappa : ndarray, float
        rotation and tilt angles in degree
    """
    omega, kappa = np.array([]),np.array([])
    d_ome = d_rot
    for k, kap in enumerate( np.array(tilts) ):
        if kap == 0.0:
            ome_max = 180
        else:
            ome_max = 360
        n_ome = np.round(ome_max/d_ome * np.cos(kap*np.pi/180)).astype(int)
        if np.mod(k,2) != 0:
            ome_min = ome_max/n_ome/2
        else:
            ome_min = 0
        omega = np.concatenate(
            [omega, np.linspace(ome_min,ome_max,n_ome, endpoint=False)],
            axis=0 )
        kappa = np.concatenate([kappa, kap*np.ones(n_ome)], axis=0)

    return np.array(omega).flatten(), np.array(kappa).flatten()

def generate_group(generators, prec = 7):
    G = set()
    queue = [tuple(g) for g in generators]
    G.add((1.0, 0.0, 0.0, 0.0))  # Identity

    while queue:
        current = queue.pop()
        for g in G.copy():
            new = quaternion_multiply(np.array(current), np.array(g))
            if new[0] < 0:
                new *= -1
            new = new / np.linalg.norm(new)
            tup = tuple(np.round(new, decimals=prec))  # avoid FP errors
            if tup not in G:
                G.add(tup)
                queue.append(tup)
            if len(queue) > 40:
                prec -= 1
                queue = round_remove_duplicates(queue, prec)

    return np.array(list(G), data_type)

def round_remove_duplicates(array_list, decimals=3):
    rounded = [np.round(arr, decimals) for arr in array_list]
    
    seen = set()
    unique = []
    for arr in rounded:
        key = tuple(arr.flatten())
        if key not in seen:
            seen.add(key)
            unique.append(arr)
    
    return unique

@njit
def symmetry_equivalent_quaternions(q, Q_group, prec=7):
    Q_eq = np.empty_like(Q_group)
    for k in range(Q_group.shape[0]):
        Q_eq[k] = np.round( quaternion_multiply( Q_group[k], q ), prec)

    Q_eq[Q_eq[:,0]<0] *= -1 # bring all to positive real part
    return nb.nb_unique_axis0(Q_eq)

def map_to_fz(q, Q_group, q_ref=np.array([1, 0, 0, 0])):
    q = q / np.linalg.norm(q)
    best_q = q
    max_dot = -1
    for q_op in Q_group:
        q_sym = quaternion_multiply(q_op, q)
        dot = abs(np.dot(q_sym, q_ref))
        if dot > max_dot:
            max_dot = dot
            best_q = q_sym
    if best_q[0] < 0:
        best_q *= -1
    return best_q / np.linalg.norm(best_q)

@njit()
def quaternion_conjugate(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])

@njit()
def misorientation_angle(q1, q2, Q_group):
    """  Calculates the closest distance between 2 quaternions symmetry
    given by a point group
    
    newer version using the full proper point group """
    q1 = q1 / np.linalg.norm(q1)
    q2 = q2 / np.linalg.norm(q2)
    w_max = 0.
    for q_op in Q_group:
        q2_rot = quaternion_multiply(q_op, q2)
        q_rel = quaternion_multiply(quaternion_conjugate(q1), q2_rot)
        w = nb.nb_clip(abs(q_rel[0]), 0.0, 1.0)
        w_max = max(w,w_max)
    return 2 * np.arccos(w_max)  # in radians

@njit()#parallel=True)
def misorientation_angle_stack(Q1, Q2, Q_group):
    mori_stack = np.empty_like(Q1[:,0])
    for k in prange(Q1.shape[0]):
        mori_stack[k] = misorientation_angle(Q1[k],Q2[k],Q_group)
    return mori_stack

@njit()
def slerp(q0, q1, t, eps=1e-6):
    # spline linear interpolation between 2 quaternions for t in [0,1]
    d = np.dot(q0,q1)
    if d < 0:
        q1 = -q1
        d = -d
    if d > 1 - eps:
        # nearly identical -> nlerp
        q = (1-t)*q0 + t*q1
        return q / nb_quaternion_norm(q)
    Omega = np.arccos(d)
    s0 = np.sin((1-t)*Omega) / np.sin(Omega)
    s1 = np.sin(t*Omega) / np.sin(Omega)
    return s0*q0 + s1*q1

@njit()
def nlerp(q0, q1, t):
    # normalized linear interpolation (faster) between 2 quaternions for t in [0,1]
    q = (1-t)*q0 + t*q1
    return q / nb_quaternion_norm(q)

@njit
def nb_quaternion_norm(q):
    """Gives the vectornorm along the first axis
    """
    norm = np.sqrt(q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3])
    if norm == 0.0:
        return q
    return q / norm