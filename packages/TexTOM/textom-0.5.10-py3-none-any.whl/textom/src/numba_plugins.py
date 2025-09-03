import numpy as np
from numba import njit

from ..config import data_type

@njit
def nb_vectornorm(v):
    """Gives the vectornorm along the first axis
    """
    norm = np.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if norm == 0.0:
        return v
    return v / norm

@njit
def nb_dot(u, v):
    """Gives the dot product along the first axis
    """
    return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]

@njit
def nb_cross(u, v):
    """Gives the cross product along the first axis
    """
    return np.array([
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0],
    ])

@njit
def nb_polyfit(x, y, degree):
    """
    Fit a polynomial of a specified degree to the given data using least squares approximation.
    Numba compatible version of the numpy function
    
    Parameters:
    x (array-like): The x-coordinates of the data points.
    y (array-like): The y-coordinates of the data points.
    degree (int): The degree of the polynomial to fit.

    Returns:
    array: Coefficients of the polynomial, highest power first.
    """
    n = len(x)
    m = degree + 1
    A = np.empty((n, m), data_type)
    for i in range(n):
        for j in range(m):
            A[i, j] = x[i] ** (degree - j)
    return np.linalg.lstsq(A, y )[0]

@njit
def nb_polyval(coeff, x):
    """
    Evaluate a polynomial given the coefficients at the points x.
    Uses Horner's Method.
    Numba compatible version of the numpy function

    Parameters:
    coeff (array-like): The coefficients of the polynomial.
    x (array-like): The x-coordinates of the data points.
    """
    res = np.zeros_like(x)
    for c in coeff:
        res = x * res + c
    return res

@njit
def nb_tile_1d(a, n):
    # numba-optimized function to c
    # Create an output array of the desired shape
    out = np.empty((n, len(a)), data_type)
    
    # Fill the output array with repeated values from a
    for i in range(n):
        out[i] = a
    
    return out

@njit
def nb_mean_ax0(a):
    # numba-optimized function to calculate mean values along the first dimension
    res = np.empty( a.shape[1], data_type)
    for i in range(a.shape[1]):
        res[i] = a[:,i].mean()
    return res

@njit
def nb_isnan(array):
    # Create a boolean mask where True indicates NaN values
    mask = np.zeros(array.shape, dtype=np.bool_)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            for k in range(array.shape[2]):
                # Check if the value is NaN by comparing the value to itself
                if array[i, j, k] != array[i, j, k]:
                    mask[i, j, k] = True
    return mask

@njit
def nb_clip(x, min_val, max_val):
    """Numba-compatible equivalent of np.clip."""
    if x < min_val:
        return min_val
    elif x > max_val:
        return max_val
    return x

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