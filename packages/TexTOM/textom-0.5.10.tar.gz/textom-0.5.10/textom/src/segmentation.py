import numpy as np
import sys
from time import time
from numba import njit, prange
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from scipy import ndimage

from . import symmetries as sym
from . import rotation as rot

@njit#(parallel=True)
def find_clusters_numba(q, gen, threshold):
    """
    Find clusters in a 3D array where neighboring elements deviate by less than a given threshold.
    
    Parameters:
    - g: 4D numpy array with axis-angle orientations in the 4th dimesion.
    - ppgrp: str, proper point group.
    - threshold: Maximum deviation allowed between neighbors to consider them in the same cluster.
    
    Returns:
    - clusters: 3D array of the same shape as input with integer labels for each cluster.
    - num_clusters: The number of clusters found.
    """
    shape = q.shape[:3]
    # q = rot.QfromOTP( g.reshape((np.prod(shape), 3))  )
    # q = q.reshape( (*shape, 4) )

    # print('\tLooking for clusters')
    clusters = np.zeros(shape, np.int32)
    # visited = np.zeros(shape, np.bool_)
    visited = isnan_numba(q[:,:,:,0])
    vis_init = visited.sum()
    cluster_label = 0
    
    # Define neighbors for 3D connectivity (6-connected neighbors)
    neighbors = np.array([
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1)
    ])

    # Preallocate stack with a maximum possible size (equal to the array size)
    max_stack_size = visited.size - vis_init
    stack = np.empty((max_stack_size, 3), dtype=np.int32)

    def grow_cluster(x, y, z, label):
        """Grow a cluster starting from (x, y, z) using the threshold and label."""
        stack_size = 0
        stack[stack_size] = np.array([x, y, z], dtype=np.int32)
        stack_size += 1
        clusters[x, y, z] = label
        visited[x, y, z] = True

        while stack_size > 0:
            cx, cy, cz = stack[stack_size - 1]
            stack_size -= 1
            # Check all 6 neighbors
            for dx, dy, dz in neighbors:
                nx, ny, nz = cx + dx, cy + dy, cz + dz
                # Check bounds
                if 0 <= nx < shape[0] and 0 <= ny < shape[1] and 0 <= nz < shape[2]:
                    if not visited[nx, ny, nz]:
                        # calculate misorientation
                        mori = rot.misorientation_single(
                            q[nx, ny, nz], q[cx, cy, cz],gen) 
                        if mori <= threshold:
                            # Mark as visited and add to cluster
                            visited[nx, ny, nz] = True
                            clusters[nx, ny, nz] = label
                            stack[stack_size] = np.array([nx, ny, nz], dtype=np.int32)
                            stack_size += 1

    # Iterate over each point in the 3D array in parallel
    for x in range(shape[0]):
        for y in range(shape[1]):
            for z in range(shape[2]):
                if not visited[x, y, z]:
                    # Start a new cluster with a unique label
                    cluster_label += 1
                    grow_cluster(x, y, z, cluster_label)

    return clusters, cluster_label

def plot_clusters_3d(clusters, min_size=100):
    """
    Plot clusters in 3D with each cluster in a different color.
    
    Parameters:
    - clusters: 3D numpy array with integer labels for each cluster.
    """
    # Get the unique cluster labels, excluding 0 (assuming 0 is the background or unlabeled)
    cluster_labels = np.unique(clusters)
    cluster_labels = cluster_labels[cluster_labels != 0]

    cluster_sizes = np.array([(clusters==n+1).sum() for n in cluster_labels])
    cluster_labels = cluster_labels[cluster_sizes > min_size]
    
    # Set up the colormap (use a colormap with enough unique colors for each cluster)
    cmap = cm.get_cmap("tab20", len(cluster_labels))  # e.g., "tab20" for categorical colors

    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot each cluster with a unique color
    for i, label in enumerate(cluster_labels):
        # Extract the x, y, z coordinates of points in the current cluster
        x, y, z = np.where(clusters == label)
        
        # Plot the cluster in 3D with a unique color from the colormap
        ax.scatter(x, y, z, color=cmap(i), label=f"Cluster {label}", s=5)
    
    # Add labels and a legend
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.legend()
    plt.show()

def mori_3d( g, ppgrp ):
    """Calculates misorientations between neighboring voxels

    Parameters
    ----------
    g : ndarray
        orientations in axis-angle (3-angle) parametrization
    ppgrp : str
        proper point group

    Returns
    -------
    ndarray
        misorientation arrays
    """
    q = rot.QfromOTP( # make quaternions
        g.reshape((np.prod(g.shape[:3]), 3)) # flatten
        ).reshape((*g.shape[:3], 4)) # shape back
    
    gen = sym.generators(ppgrp)
    Qgen = rot.QfromOTP(gen)
    pgroup = rot.generate_group(Qgen)

    nx,ny,nz,_ = q.shape
    mori_x = rot.misorientation_angle_stack(
        q[:-1,:,:].reshape((nx-1)*ny*nz,4), 
        q[1:,:,:].reshape((nx-1)*ny*nz,4), 
        pgroup,#gen
    ).reshape((nx-1),ny,nz)
    mori_y = rot.misorientation_angle_stack(
        q[:,:-1,:].reshape(nx*(ny-1)*nz,4), 
        q[:,1:,:].reshape(nx*(ny-1)*nz,4), 
        pgroup,#gen
    ).reshape(nx,(ny-1),nz)
    mori_z = rot.misorientation_angle_stack(
        q[:,:,:-1].reshape(nx*ny*(nz-1),4), 
        q[:,:,1:].reshape(nx*ny*(nz-1),4), 
        pgroup,#gen
    ).reshape(nx,ny,(nz-1))

    mori_max = np.max(np.array((
        np.append(np.pi*np.ones((1,ny,nz)), mori_x, axis=0),
        np.append(mori_x,np.pi*np.ones((1,ny,nz)), axis=0),
        np.append(np.pi*np.ones((nx,1,nz)), mori_y, axis=1),
        np.append(mori_y, np.pi*np.ones((nx,1,nz)), axis=1),
        np.append(np.pi*np.ones((nx,ny,1)), mori_z, axis=2),
        np.append(mori_z, np.pi*np.ones((nx,ny,1)), axis=2),
    )), axis=0)

    return mori_x, mori_y, mori_z, mori_max

def label_zones( array_3d, tresh, min_size=None, max_zones=32 ):

    array_3d[np.isnan(array_3d)] = np.pi

    # Label the connected components (zones) below a treshold
    # labeled_zones, num_zones = label(binary_dilation(array_3d < tresh))
    labeled_zones, num_zones = ndimage.label(array_3d < tresh)

    # Calculate the size of each zone
    zone_sizes = np.bincount(labeled_zones.ravel())
    
    # Find zones that meet the minimum size requirement
    valid_zones = [(label, size) for label, size in enumerate(zone_sizes) if size >= min_size and label != 0]
    
    # Sort the valid zones by size in descending order and keep only the largest `max_zones`
    largest_zones = sorted(valid_zones, key=lambda x: x[1], reverse=True)[:max_zones]
    largest_zone_labels = [label for label, size in largest_zones]
    zone_sizes = np.array([size for label, size in largest_zones])

    # Create a new array for relabeling
    zones = np.zeros_like(labeled_zones)
    for new_label, old_label in enumerate(largest_zone_labels, start=1):
        zones[labeled_zones == old_label] = new_label  # Relabel sequentially

    return zones, zone_sizes


    # zone_sizes = []
    # for n in range(1, num_zones+1):
    #     size = (labeled_zones==n).sum()
    #     if size >= min_zone_size:
    #         labeled_zones[labeled_zones==n] = 0
    #         zone_sizes.append(size)
    # zidx = np.argsort(zone_sizes)
    # for k in range(zone_sizes.size - max_zone_no):
    #     labeled_zones[labeled_zones==np.where(zidx==k)[0]] = 0

    # return labeled_zones, np.array(zone_sizes)

@njit
def isnan_numba(array):
    # Create a boolean mask where True indicates NaN values
    mask = np.zeros(array.shape, dtype=np.bool_)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            for k in range(array.shape[2]):
                # Check if the value is NaN by comparing the value to itself
                if array[i, j, k] != array[i, j, k]:
                    mask[i, j, k] = True
    return mask

