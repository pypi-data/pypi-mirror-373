import numpy as np
from numba import njit, prange

@njit(parallel=True)
def order_parameters_parallel( vectors, odf_par, basis_functions, V_fz ):

    Order_parameters = np.empty( odf_par.shape[0], vectors.dtype )
    Directors = np.empty( (odf_par.shape[0],3), vectors.dtype )

    for k in prange( odf_par.shape[0] ):
        weights = clipped_odf( V_fz, basis_functions, odf_par[k])
        Order_parameters[k], Directors[k] = weighted_order_parameter(vectors,weights)

    return Order_parameters, Directors

@njit()
def clipped_odf( V_fz, basis_functions, coefficients ):
    """ Computes a orientation distribution function from a set of sHSH coefficients

    """
    # renormalize to c0 = 1    
    c1plus = coefficients[1:]/coefficients[0]

    ## produces an ODF from HSH-coefficients
    odf = 1/V_fz + c1plus @ basis_functions

    odf[odf<0] = 0 # clip negative values
    odf = odf / odf.sum() # renormalize

    return odf

@njit
def weighted_order_parameter(vectors, weights):
    Q = np.zeros((3, 3))
    for i in range(len(vectors)):
        n = vectors[i]
        norm = np.sqrt(np.dot(n, n))
        n /= norm
        w = weights[i]
        for j in range(3):
            for k in range(3):
                Q[j, k] += w * (1.5 * n[j] * n[k] - 0.5 * (j == k))

    eigvals, eigvecs = jacobi_eigenvalue_3x3(Q)
    max_idx = np.argmax(eigvals)
    S = eigvals[max_idx]
    director = eigvecs[:, max_idx]
    return S, director

@njit
def outer_product(a, b):
    result = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            result[i, j] = a[i] * b[j]
    return result

@njit
def normalize(v):
    norm = np.sqrt(np.sum(v**2))
    return v / norm

@njit
def jacobi_eigenvalue_3x3(A, max_iterations=100, eps=1e-10):
    V = np.eye(3)
    for iteration in range(max_iterations):
        # Find the largest off-diagonal element
        a01 = abs(A[0, 1])
        a02 = abs(A[0, 2])
        a12 = abs(A[1, 2])

        if a01 >= a02 and a01 >= a12:
            p, q = 0, 1
        elif a02 >= a12:
            p, q = 0, 2
        else:
            p, q = 1, 2

        if abs(A[p, q]) < eps:
            break

        theta = 0.5 * (A[q, q] - A[p, p]) / A[p, q]
        t = np.sign(theta) / (abs(theta) + np.sqrt(1 + theta**2))
        c = 1 / np.sqrt(1 + t**2)
        s = t * c

        # Rotation
        for i in range(3):
            if i != p and i != q:
                aip = A[i, p]
                aiq = A[i, q]
                A[i, p] = A[p, i] = c * aip - s * aiq
                A[i, q] = A[q, i] = c * aiq + s * aip

        app = A[p, p]
        aqq = A[q, q]
        apq = A[p, q]

        A[p, p] = c**2 * app - 2 * s * c * apq + s**2 * aqq
        A[q, q] = s**2 * app + 2 * s * c * apq + c**2 * aqq
        A[p, q] = A[q, p] = 0.0

        for i in range(3):
            vip = V[i, p]
            viq = V[i, q]
            V[i, p] = c * vip - s * viq
            V[i, q] = c * viq + s * vip

    # Eigenvalues are the diagonal of A
    eigenvalues = np.array([A[0, 0], A[1, 1], A[2, 2]])
    return eigenvalues, V