import matplotlib.pyplot as plt
import numpy as np
import os

import textom.src.handle as hdl
from textom.src.misc import import_module_from_path

def geometry_plot( geo ):

    # Create a figure and axis with 3D projection
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Define the coordinates for the 3D plot with offset
    X = np.array([-100, 100])  # x coordinates for the red line
    Y = np.array([0, 0])    # y coordinates for the red line
    Z = np.array([0, 0])    # z coordinates for the red line

    # Plot the red line in x-direction
    ax.plot(X, Y, Z, color='red')

    # Move the small coordinate system by -25 in y and z
    offset = -25
    ax.quiver(0, offset, offset, 50, 0, 0, color='b', label='X axis')  # X axis
    ax.quiver(0, offset, offset, 0, 50, 0, color='g', label='Y axis')  # Y axis
    ax.quiver(0, offset, offset, 0, 0, 50, color='purple', label='Z axis')  # Z axis

    # Generate random data with Gaussian distribution around a circle of radius 30 in y-z plane
    np.random.seed(0)  # for reproducibility
    n=100
    theta = np.random.uniform(0, 2*np.pi, n)
    r0 = np.random.normal(0, 5, n)  
    r1 = np.random.normal(15, 5, n) 
    r2 = np.random.normal(30, 2, n)  
    ax.scatter([100] * n, r0 * np.cos(theta), r0 * np.sin(theta), c='b', marker='.')
    ax.scatter([100] * n, r1 * np.cos(theta), r1 * np.sin(theta), c='b', marker='.')
    ax.scatter([100] * n, r2 * np.cos(theta), r2 * np.sin(theta), c='b', marker='.')

    # Add a small cube at the origin using a surface plot
    ax.scatter(0, 0, 0, c='y', marker='D', s=100, label='sample')

    # Add a curved arrow for rotation in the xy plane next to the sample
    arrow_radius = 15
    theta_curve = np.linspace(0, np.pi, 100)
    x_curve = arrow_radius * np.cos(theta_curve)
    y_curve = arrow_radius * np.sin(theta_curve)
    z_curve = np.zeros_like(x_curve)
    ax.plot(x_curve, y_curve, z_curve, color='g', linewidth=2)
    ax.quiver(arrow_radius,0,0,0,-5,0, color='g', linewidth=2, 
            length=1, arrow_length_ratio=2, label='inner rot axis')

    # Add a curved arrow for rotation in the xy plane next to the sample
    arrow_radius = 20
    theta_curve = np.linspace(0, np.pi, 100)
    x_curve = arrow_radius * np.cos(theta_curve)
    z_curve = arrow_radius * np.sin(theta_curve)
    y_curve = np.zeros_like(x_curve)
    ax.plot(x_curve, y_curve, z_curve, color='g', linewidth=2)
    ax.quiver(arrow_radius,0,0,0,0,-5, color='g', linewidth=2, 
            length=1, arrow_length_ratio=2, label='outer rot axis')

    # Set plot labels and limits
    ax.set_xlim([-100, 150])
    ax.set_ylim([-50, 50])
    ax.set_zlim([-50, 50])

    # Add a legend
    ax.legend()

    # Turn off the grid
    ax.grid(False)

    # Hide axes
    ax.set_axis_off()

    ax.set_aspect("equal")

    plt.show()

geo_path = hdl.get_file_path('textom',os.path.join('input','geometry.py'))
geo = import_module_from_path('geometry', geo_path)
