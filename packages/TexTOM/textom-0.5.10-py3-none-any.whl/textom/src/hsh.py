import numpy as np
from scipy import special as sp
from numba import njit
import math
import os, sys

from . import handle as hdl

"""
This file contains functions to calculate and rotate hyperspherical harmonics
"""

def Z( omega,theta,phi, n,l,m ):
    """Compute the hyperspherical harmonic function Z^n_{l,m}

    This function is used to construct orientation distribution functions
    for axis-angle rotations. theta and phi are the polar and azimutal
    angles, respectively, defining the rotation axis. omega is the rotation
    angle.
    The function uses the scipy package to compute factorials, Gegenbauer
    polynomials and Associated Legendre functions.

    Source: Mason, J.K., and C.A. Schuh. Acta Materialia 56, no. 20 
        (December 2008): 6141–55. https://doi.org/10.1016/j.actamat.2008.08.031.

    Parameters
    ----------
    omega : ndarray, float
        rotation angle, usually ∈[0,pi)
    theta : ndarray, float
        polar angle of the rotation axis, usually ∈[0,pi)
    phi : ndarray, float
        azimutal angle of the rotation axis, usually ∈[0,2pi)
    n, l, m : int/float
        Indices of the hyperspherical harmonic function
        Usually integer or half-integer, with the conditions:
            n >= 0
            l <= n
            -l <= m <= l

    Return values
    ------------
    Z : ndarray, complex
        returns values on the complex plane with |Z| <= 1
    """
    
    #Check indices
    if n < 0:
        print('n smaller than zero, check that!, n= ',n)
    elif l < 0:
        print('l smaller than zero, check that!, l= ',l)
    elif l > n:
        print(' l larger than n, check that!, l= ',l,' n= ',n)
    elif m < l*-1:
        print ('m smaller than -l, check that!, m = ',m,' -l ',l*-1)
    elif m > l:
        print ('m larger than l, check that!, m= ',m,' l= ',l)

    Z = (-1j)**l * 2**(l+0.5) * sp.factorial(l) / (2*np.pi) * \
        np.sqrt( (2*l+1) * sp.factorial(l-m) * (n+1) * sp.factorial(n-l) / \
        ( sp.factorial(l+m) * sp.factorial(n+l+1) ) ) * \
        (np.sin(omega/2))**l * sp.eval_gegenbauer(n-l,l+1,np.cos(omega/2)) * \
        sp.lpmv(m,l,np.cos(theta)) * np.exp(1j*m*phi)
    
    return Z

### Test to check if Z and Z_numba_array are the same
# from textom.src import hsh
# import numpy as np
# n_points = 100
# test_omega = np.pi * np.random.rand(n_points)
# test_theta = np.pi * np.random.rand(n_points)
# test_phi = 2*np.pi * np.random.rand(n_points)
# old_Z = hsh.Z(test_omega,test_theta,test_phi, 4,3,2)
# new_Z = hsh.Z_numba_array(test_omega,test_theta,test_phi, 4,3,2)
# print(f'maximum deviation: {np.max(np.abs(old_Z - new_Z))}') # was about 1e-15
###

@njit
def Z_numba(omega, theta, phi, n, l, m):
    """
    Numba-friendly version of your Z().
    All inputs are scalars. n,l,m are integers with n>=l>=0 and |m|<=l.
    Returns complex128.
    """
    # sanity (no Python exceptions in njit; keep cheap guards)
    if l < 0 or n < 0 or l > n or abs(m) > l:
        return np.nan + 0j

    # pieces
    half_omega = 0.5 * omega
    s = np.sin(half_omega)
    c_half = np.cos(half_omega)
    ct = np.cos(theta)

    # (-1j)**l
    p_neg_i = pow_neg_i(l)

    # real prefactor before special functions
    # 2**(l+0.5) * fac(l) / (2*pi)
    ln_fac_l = ln_factorial(l)
    ln_pref_real = (l + 0.5) * np.log(2.0) + ln_fac_l - np.log(2.0 * np.pi)
    pref_real = np.exp(ln_pref_real)

    # sqrt( (2l+1) * fac(l-m) * (n+1) * fac(n-l) / ( fac(l+m) * fac(n+l+1) ) )
    ln_num = np.log(2.0 * l + 1.0) \
             + ln_factorial(l - abs(m)) \
             + np.log(n + 1.0) \
             + ln_factorial(n - l)
    ln_den = ln_factorial(l + abs(m)) + ln_factorial(n + l + 1)
    ln_ratio = 0.5 * (ln_num - ln_den)
    sqrt_ratio = np.exp(ln_ratio)

    # (sin(omega/2))**l
    sin_pow = s ** l if l > 0 else 1.0

    # Gegenbauer: C_{n-l}^{(l+1)}(cos(omega/2))
    C = gegenbauer_C(n - l, l + 1.0, c_half)

    # Associated Legendre: P_l^m(cos(theta))
    P = associated_legendre_P(l, m, ct)

    # exp(i m phi)
    e_imphi = np.cos(m * phi) + 1j * np.sin(m * phi)

    # assemble
    out = p_neg_i * (pref_real * sqrt_ratio) * sin_pow * C * P * e_imphi
    return out

# ---------- helpers (nopython-safe) ----------

@njit
def pow_neg_i(l):
    # (-1j)**l cycles every 4
    r = l % 4
    if r == 0:
        return 1.0 + 0.0j
    elif r == 1:
        return 0.0 - 1.0j
    elif r == 2:
        return -1.0 + 0.0j
    else:
        return 0.0 + 1.0j

@njit
def ln_factorial(n):
    # ln(n!) via lgamma
    return math.lgamma(n + 1.0)

@njit
def gegenbauer_C(n, alpha, x):
    # C_n^{(alpha)}(x), n>=0, alpha>0
    if n == 0:
        return 1.0
    if n == 1:
        return 2.0 * alpha * x
    Cnm2 = 1.0
    Cnm1 = 2.0 * alpha * x
    for k in range(1, n):
        # k goes 1..n-1 to produce C_{k+1}
        kp1 = k + 1.0
        num = 2.0 * (k + alpha) * x * Cnm1 - (k + 2.0 * alpha - 1.0) * Cnm2
        Cn = num / kp1
        Cnm2 = Cnm1
        Cnm1 = Cn
    return Cnm1

@njit
def associated_legendre_P(l, m, x):
    """
    Unnormalized associated Legendre P_l^m(x) with Condon-Shortley phase.
    l>=0, |m|<=l, x in [-1,1]
    """
    if m < 0:
        # P_l^{-m} = (-1)^m (l-m)!/(l+m)! P_l^{m}
        mp = -m
        Plmp = associated_legendre_P(l, mp, x)
        sign = -m
        ln_ratio = ln_factorial(l - mp) - ln_factorial(l + mp)
        return ((-1.0)**mp) * np.exp(ln_ratio) * Plmp

    # m >= 0 from here
    # P_m^m(x) = (-1)^m (2m-1)!! (1-x^2)^{m/2}
    # use logs: (2m-1)!! = 2^m * Gamma(m+1/2) / sqrt(pi)
    if m == 0:
        Pmm = 1.0
    else:
        ln_double_fact = m * np.log(2.0) + math.lgamma(m + 0.5) - 0.5 * np.log(np.pi)
        ln_base = 0.5 * m * np.log(max(0.0, 1.0 - x * x))
        Pmm = ((-1.0)**m) * np.exp(ln_double_fact + ln_base)

    if l == m:
        return Pmm

    # P_{m+1}^m(x) = x (2m+1) P_m^m(x)
    Pm1m = x * (2.0 * m + 1.0) * Pmm
    if l == m + 1:
        return Pm1m

    # upward recurrence for l >= m+2
    Plm2 = Pmm
    Plm1 = Pm1m
    for ell in range(m + 2, l + 1):
        num = (2.0 * ell - 1.0) * x * Plm1 - (ell + m - 1.0) * Plm2
        Pl = num / (ell - m)
        Plm2 = Plm1
        Plm1 = Pl
    return Plm1

# -------------------------------------------------------------
@njit
def Rs_n_stack( Gs, n, Xsn ):
    ''' calculates sHSH rotation matrices for all rotation Gs and order n
    '''
    Rs_stack = np.zeros( (Gs.shape[0], Xsn.shape[0], Xsn.shape[0]), np.float64 )
    for g in range(Gs.shape[0]):
        Rs_stack[g] = Rs_n( Gs[g], n, Xsn )
    
    return Rs_stack

@njit
def Rs_n( g, n, Xsn ):
    ''' calculates a single sHSH rotation matrix for a rotation g and order n
    '''
    rot_HSH = R( n, g, np.array([0.,0.,0.]) ) # this is the HSH rotation matrix
    rot_sHSH = np.real( np.conj( Xsn ) @ rot_HSH @ Xsn.T ) # here it's converted to sHSH
    return rot_sHSH


@njit
def R( n, gl, gr=np.array([0.,0.,0.]) ):
    """Function that computes a HSH rotation matrix for a given order n

    Source: Mason, J. K., Acta Crystallographica Section A Foundations of 
        Crystallography 65, no. 4 (July 1, 2009): 259–66. 
        https://doi.org/10.1107/S0108767309009921.
        equation (10)

    Parameters
    ----------
    n : int/float
        order of the HSH
    gl, gr : 2D ndarray, float
        axis-angle rotations given by angles: [omega, theta, phi]
        dimensions: 0: rotation, 1: ome,tta,phis
        
    Return values
    ------------
    R : 2D ndarray, complex
        matrix to convert a vector of HSH coefficients to a different
        vector that results in the same ODF but rotated
    """
    Ul = U( n/2, gl[0],gl[1],gl[2])
    Ur_inv = U( n/2, gr[0], gr[1], gr[2], True)
    UrUl = np.kron( Ur_inv, Ul ).astype(np.complex128)
    CG = CGn( n ).astype(np.complex128)
    R = ( CG @ UrUl @ np.conj(CG.T) )
    return R

@njit
def U(j,ome,tta,phi,invert=False):
    # U converts a rotation angle and spherical angles of the rotation
    # axis into the equivalent irrep of SO(3).
    # 
    # Inputs:
    #   j  - specifies dimension of the irrep.
    #   ome  - rotation angle in the interval [0, 2 \pi].
    #   tta - polar angle of rotation axis in the interval [0, \pi].
    #   phi - aximuthal angle of rotation axis in the interval [0, 2 \pi].
    #
    # Outputs:
    #   U  - (2 j + 1)-dimensional representation of SO(3), using the conventions
    #        established in Eq. 6 on page 81 of D. A. Varshalovich et al, Quantum
    #        Theory of Angular Momentum, 1988. Rows and columns ordered in
    #        increasing values of m' and m.
    #
    # Copyright 2019 Jeremy Mason
    #
    # Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
    # http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
    # http://opensource.org/licenses/MIT>, at your option. This file may not be
    # copied, modified, or distributed except according to those terms.

    if invert:
        ome = - ome

    tmp = np.tan(ome / 2) * np.cos(tta)
    tmp = (1 - 1j * tmp) / np.sqrt(1 + tmp**2)
    r_base = 1j * np.exp(-1j * phi) * tmp
    c_base = -1j * np.exp(1j * phi) * tmp
    
    # Require w to be in [-\pi, \pi]
    w = np.mod(ome + np.pi, 2 * np.pi) - np.pi
    xi = 2. * np.arcsin(np.sin(w / 2.) * np.sin(tta))
    U = wigner_d(j, xi).astype(np.complex128)
    
    m = np.arange(-j,j+1)
    n = int( 2 * j + 1 )
    for a in range(n):
        U[a, :] = U[a, :] * r_base**m[a]
        U[:, a] = U[:, a] * c_base**m[a]
    return U

@njit
def wigner_d(j,tta):
    # wigner_d constructs a Wigner little d matrix given a total angular 
    # momenum and an angle. This corresponds to the irrep of SO(3) for a rotation
    # about the y axis. Follows the approach of X. M. Feng et al in 
    # 10.1103/PhysRevE.92.043307.
    # 
    # Inputs:
    #   j     - specifies dimension of the matrix.
    #   tta   - rotation angle in the interval [0, 2 \pi].
    #
    # Outputs:
    #   d     - Wigner little d matrix, with the rows and columns ordered in
    #           increasing values of m' and m. 
    #
    # Copyright 2019 Jeremy Mason
    #
    # Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
    # http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
    # http://opensource.org/licenses/MIT>, at your option. This file may not be
    # copied, modified, or distributed except according to those terms.

    m = np.arange(-j,j+1)#np.arange(-j,j+1,1,np.int64)
    n = int(2*j+1)

    X = np.sqrt((j + m) * (j - m + 1)) / (2 * 1j)
    # Jy is a tridiagonal Hermitian matrix
    Jy = np.zeros((n, n),np.complex128)#np.zeros([n, n],dtype=complex)
    for a in range(1,n):
        b = n - a - 1
        Jy[a - 1, a] = -X[a]
        Jy[b + 1, b] =  X[a]

    # # Requires that eigenvectors be ordered with increasing eigenvalues
    w,v = np.linalg.eig(Jy)
    w_ord = np.argsort(np.real(w))
    V_temp = v[:,w_ord]
    ## I however need to change to complex here for V and W
    V = V_temp.astype(np.complex128)
    W = np.copy(V)
    for a in range(n):
        W[:, a] = W[:, a] * np.exp(-1j * m[a] * tta)

    d = W @ np.conj(V.T)
    return np.real(d)

@njit
def CGn(n):
    """ Calculates all Clebsch-Gordan coefficients for an order n
    and assigns them into a matrix for further handling
    """
    l = n/2
    CG = np.zeros( ((n + 1)**2, (n + 1)**2), np.float64)
    for a in np.arange( 0, n+1, 1, np.int64 ):
        for b in np.arange( -a, a+1, 1, np.int64 ):
            row = np.array( (a + 1)**2 - a + b -1 , np.int64 )
            C, m1, m2 = CleGor( l, l, a, b )
            for c in np.arange( 0, len(C), 1, np.int64 ):
                col = int( (m1[c] + l) * (2 * l + 1) + (m2[c] + l) )
                CG[row, col] = C[c,0]
    return CG

@njit
def CleGor(j1, j2, J, M):
    # CleGor returns the Clebsch-Gordan coefficients for the specified
    # total angular momenta and coupled z angular momentum component. This form
    # is particularly convenient from a computational standpoint. Follows the
    # approach of W. Straub in viXra:1403.0263.
    # 
    # Inputs:
    #   j1 - first uncoupled total angular momentum.
    #   j2 - second uncoupled total angular momentum.
    #   j  - coupled total angular momentum.
    #   m  - coupled z angular momentum component.
    #
    # Outputs:
    #   C  - all of the nonzero Clebsch-Gordan coefficients for the specified
    #        inputs. Ordered in increasing values of m1.
    #   m1 - first uncoupled z angular momentum components.
    #   m2 - second uncoupled z angular momentum components.
    #
    # Copyright 2019 Jeremy Mason
    #
    # Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
    # http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
    # http://opensource.org/licenses/MIT>, at your option. This file may not be
    # copied, modified, or distributed except according to those terms.    
    
    if (J < abs(j1 - j2) or J > j1 + j2 or abs(M) > J):
        # Nothing to do
        # But to the silly list for numba with a type
        ## THis is not working yet, just here to see if jitting helps
        print('asdf')
        # l = List.empty_list(int64)
        # return l, l, l
    else:
        m11 = (M - j1 - j2 + abs(j1 - j2 + M)) / 2
        m1n = (M + j1 + j2 - abs(j1 - j2 - M)) / 2
        
        m1 = np.arange(m11,m1n+1,1,np.float64)
        m2 = M - m1
        
        j_const = j1 * (j1 + 1) + j2 * (j2 + 1) - J * (J + 1)
        
        n = int(m1n - m11 + 1)
        # A is a tridiagonal symmetric matrix
        ## Switched from list to tuple here to enable numba typing
        A = np.zeros( (n, n), np.float64 )
        for a in range(n):
            A[a,a] = j_const + 2 * m1[a] * m2[a]
        for a in range(n-1):
            tmp = np.sqrt(j1 * (j1 + 1) - m1[a] * m1[a+1]) * np.sqrt(j2 * (j2 + 1) - m2[a] * m2[a+1])
            A[a, a + 1] = tmp
            A[a + 1, a] = tmp
        
        # A determines C up to sign and normalization
        ## Here, we have the problem that the la.null_space isn't numba supported, can we switch to 
        ##numpy.linalg.svd?
        # C = la.null_space(A)
        C = nullspace(A)
        C = np.sign(C[n-1]) * C / np.sqrt( np.conj(C.T) @ C )
        return C, m1, m2

@njit
def nullspace(A, atol=1e-13, rtol=1e-13):
    """Compute an approximate basis for the nullspace of A.

    The algorithm used by this function is based on the singular value
    decomposition of `A`.

    Source: https://scipy-cookbook.readthedocs.io/items/RankNullspace.html
        last accessed: 7 June 2023

    Parameters
    ----------
    A : ndarray
        A should be at most 2-D.  A 1-D array with length k will be treated
        as a 2-D with shape (1, k)
    atol : float
        The absolute tolerance for a zero singular value.  Singular values
        smaller than `atol` are considered to be zero.
    rtol : float
        The relative tolerance.  Singular values less than rtol*smax are
        considered to be zero, where smax is the largest singular value.

    If both `atol` and `rtol` are positive, the combined tolerance is the
    maximum of the two; that is::
        tol = max(atol, rtol * smax)
    Singular values smaller than `tol` are considered to be zero.

    Return values
    ------------
    ns : ndarray
        If `A` is an array with shape (m, k), then `ns` will be an array
        with shape (k, n), where n is the estimated dimension of the
        nullspace of `A`.  The columns of `ns` are a basis for the
        nullspace; each element in numpy.dot(A, ns) will be approximately
        zero.
    """

    A = np.atleast_2d(A)
    u, s, vh = np.linalg.svd(A)
    tol = max(atol, rtol * s[0])
    nnz = (s >= tol).sum()
    ns = vh[nnz:].conj().T
    return ns

############################################################################################
############################################################################################
### helper functions to manipulate the hsh indices
def get_idx(n,l,m,ns):
    ## input: 
    # n,l,m     desired n,l and m values, e.g. 2,2,0
    # ns        used n's in ascending order, e.g. [0,2,4]
    ## output:
    # idx       index of the coefficient in a 1D array
    
    npos = np.where(ns==n)[0][0]
    ## needed to unroll that one np.sum([2*ll+1 for ll in range(l)])
    idx_temp = 0
    for ll in range(l):
        idx_temp = idx_temp+2*ll+1
    idx = npos + idx_temp + l + m
    return int(idx)

def get_nlm(idx,ns):
    ## input: 
    # idx       index of the coefficient in a 1D array
    # ns        used n's in ascending order, e.g. [0,2,4]
    ## output:
    # n,l,m     corresponding n,l and m values, e.g. 2,2,0

    Ln = [(n+1)**2 for n in ns] # number of unique combinations [l,m] for every n
    Ll = [2*l+1 for l in range(np.max(ns)+1)] # number of m for every l
    ni = 0
    while idx > np.sum(Ln[:ni+1])-1:
        ni += 1
    l = 0
    while idx > np.sum(Ln[:ni]) + np.sum(Ll[:l+1])-1:
        l += 1
    m = idx - np.sum(Ln[:ni]) - np.sum(Ll[:l]) - l
    return ns[ni],l,int(m)

def cSymmHSH(point_group, n):
    """Loads a matrix to transform HSHs to sHSHs

    loads sets of coefficients that make the hyperspherical 
    harmonic expansion invariant a certain crystal symmetry. 
    These can  be interpreted as defining a compact basis
    for an orientation distribution obeying the required symmetry, 
    namely, the symmetrized hyperspherical harmonics (sHSHs).

    This function loads from files created separately by Matlab
    functions in ressources/symmetrizedHSH

    Parameters
    ----------
    proper_point_group : str
        name of the crystal symmetry, taken from a provided table
    n : int
        order of the HSHs

    Return values
    ------------
    nlm : ndarray, int
        HSH indices corresponding to the coefficients
    c : 2D ndarray, complex
        matrix of HSH coefficients for all sHSHs for given n and lattice
        dimensions: 0: HSH orders, 1: sHSHs
    """
    path_csym = hdl.get_file_path('textom',
            os.path.join('ressources','symmetrizedHSH','output',
                         point_group + '_n' + str(n)))
    # filename = 'ressources/symmetrizedHSH/output/' + point_group + '_n' + str(n)
    if os.path.isfile(path_csym):
        data = np.genfromtxt(
            path_csym,
            dtype=np.complex128,
            skip_header=1,
            skip_footer=0,
        )
        
        nlm = data[:,:3].real.astype(int)
        c = data[:,3:].T
        return nlm, c
    
    else:
        print('Symmetrized HSH base file does not exist. Check for typos or generate it via matlab files')
        sys.exit(1)

def get_NsHSH(point_group, n):
    """ Returns how many sHSHs exist for the respective point group and order

    Parameters
    ----------
    point_group : str
        name of the crystal symmetry, taken from a provided table
    n : int
        order of the HSHs
    """
    if np.mod(n,2):
        return 0
    elif n==0:
        return 1
    else:
        path_overview = hdl.get_file_path('textom',
            os.path.join('ressources','symmetrizedHSH','output','overview.txt'))
        with open(path_overview, "r") as file:
                NsHSH_all = eval( file.read() )[point_group]
        return NsHSH_all[int(n/2-1)]

def symmetrization_matrix( orders, symmetry ):
    # Number sHSHs for each n
    n_sHSHs  =  np.array( [get_NsHSH(symmetry,n) for n in orders] ) 

    slices_hsh = np.array(
        [ [ n_sHSHs[:k].sum(), n_sHSHs[:k+1].sum() ] 
            for k in range(n_sHSHs.shape[0]) ]) # 'slices' of coefficients as numbers for each n

    # calculate symmetrized HSHs from linear combinations of HSHs
    Xsn = {'0': np.array([[1.]], np.complex128)}
    for n in orders[1:]:
        _, csym = cSymmHSH(symmetry, n) # get sSHSs and orders
        Xsn[str(n)] = csym # HSH to sHSH coefficient rotation matrix

    return Xsn, slices_hsh

def get_orders( symmetry, n_max = 20, info=True, exclude_ghosts=True ):
    ''' Gives the allowed orders up to n_max
    
    Parameters
    ----------
    n_max : int
        maximum HSH order used
    info : bool
        if True, the list of how many sHSHs exist at each order is printed
    
    Return values
    ------------
    n_allowed : ndarray, int
        orders where sHSHs exist for this point group
    '''
    if info:
        print('\t\tn\tNo of symmetrized HSHs for order n')
    n_allowed = [0]
    for n in range(1,n_max+1):
        Nn = get_NsHSH(symmetry,n)
        if exclude_ghosts and (not n%2) and (n%4): # condition for ghosts
            ghost = f' ({Nn} ghosts)'
            Nn = 0
        else:
            ghost = ''
        if info:
            print('\t\t%u\t %u%s' % (n, Nn, ghost) )
        if Nn > 0:
            n_allowed.append(n)
    return np.array(n_allowed)
        