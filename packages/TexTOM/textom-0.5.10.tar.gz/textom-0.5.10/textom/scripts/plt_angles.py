import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

def plot_unit_sphere_with_points(angles, angles2):
    """
    Plots a 3D unit sphere and points on its surface given by a list of azimuthal and polar angles.

    Parameters:
    angles (list of tuples): List of (azimuthal, polar) angle tuples in radians.
    """
    # Create a figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Create a unit sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='b', alpha=0.1)

    # # Create a band up to 45 deg tilt
    # u = np.linspace(0, 2 * np.pi, 100)
    # v = np.linspace(np.pi/4, np.pi/2, 100)
    # x = np.outer(np.cos(u), np.sin(v))
    # y = np.outer(np.sin(u), np.sin(v))
    # z = np.outer(np.ones(np.size(u)), np.cos(v))
    # ax.plot_surface(x, y, z, color='b', alpha=0.2)

    # Add latitude and longitude lines (grid)
    for theta in np.linspace(0, 2 * np.pi, 24):  # Longitude lines
        x = np.cos(theta) * np.sin(v)
        y = np.sin(theta) * np.sin(v)
        z = np.cos(v)
        ax.plot(x, y, z, color='k', linewidth=0.2)

    for phi in np.linspace(0, np.pi, 12):  # Latitude lines
        x = np.cos(u) * np.sin(phi)
        y = np.sin(u) * np.sin(phi)
        z = np.ones_like(u) * np.cos(phi)
        ax.plot(x, y, z, color='k', linewidth=0.2)

    # Plot points on the sphere
    for az, pol in angles:
        x_point = np.cos(az) * np.sin(pol)
        y_point = np.sin(az) * np.sin(pol)
        z_point = np.cos(pol)
        ax.scatter(x_point, y_point, z_point, color='r')

    # Plot points on the sphere
    for az, pol in angles2:
        x_point = np.cos(az) * np.sin(pol)
        y_point = np.sin(az) * np.sin(pol)
        z_point = np.cos(pol)
        ax.scatter(x_point, y_point, z_point, color='k')

    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Set the aspect ratio to be equal
    ax.set_box_aspect([1, 1, 1])  # Aspect ratio is 1:1:1 (equal)

    # Make grid and axes invisible
    ax.grid(False)
    # ax.set_axis_off()
    ax.set_xticks([])
    ax.set_xticks([], minor=True)
    ax.set_yticks([])
    ax.set_yticks([], minor=True)    
    ax.set_zticks([])
    ax.set_zticks([], minor=True)

    # d = 1.4
    # # Plot custom axes through the origin
    # ax.plot([-d, d], [0, 0], [0, 0], color='k', linewidth=1)
    # ax.plot([0, 0], [-d, d], [0, 0], color='k', linewidth=1)
    # ax.plot([0, 0], [0, 0], [-d, d], color='k', linewidth=1)

    # # Add labels to the axes
    # ax.text(d, 0, 0, 'X', color='k', fontsize='large')
    # ax.text(0, d, 0, 'Y', color='k', fontsize='large')
    # ax.text(0, 0, d, 'Z', color='k', fontsize='large')

    # Set the view to see the xz-plane
    ax.view_init(elev=0, azim=90)

    plt.show()

import src.handle as hdl
kappa, omega, shifty, shiftz, _, _ = hdl.load_mat_proj('data/SASTT_helix_s7_20230921_aligned_FBP.mat')

for k in range(kappa.shape[0]):
    if omega[k] > 180:
        kappa[k] *= -1
        omega[k] += 180

angles = np.column_stack((omega, 90-kappa))*np.pi/180

n=41
Ng0 = kappa.size
c=np.arange(0,Ng0,int(Ng0/n))[:n]
angles2 = angles[c]

plot_unit_sphere_with_points(angles, angles2)
