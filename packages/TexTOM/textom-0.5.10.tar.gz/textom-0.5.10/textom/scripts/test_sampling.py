import numpy as np
import matplotlib.pyplot as plt

def generate_hemisphere_points(num_points, y_max=1.0):
    """
    Generate evenly distributed points on the surface of a hemisphere.

    Parameters:
        num_points (int): Number of points to generate.
        y_max (float): Maximum y-coordinate value (between 0 and 1).

    Returns:
        np.ndarray: Array of shape (num_points, 3) containing the 3D coordinates of the points.
    """
    if not (0 < y_max <= 1.0):
        raise ValueError("y_max must be between 0 and 1.")

    points = []
    golden_angle = np.pi * (3 - np.sqrt(5))  # Golden angle in radians

    for i in range(num_points):
        y = i / (num_points - 1) * y_max  # y-coordinate ranges from 0 to y_max for a hemisphere
        radius = np.sqrt(1 - y**2)  # Radius of the circle at height y

        theta = i * golden_angle  # Angle around the circle
        x = radius * np.cos(theta)
        z = radius * np.sin(theta)

        points.append([x, y, z])

    return np.array(points)

# Example usage
num_points = 100
y_max = 0.8
hemisphere_points = generate_hemisphere_points(num_points, y_max=y_max)

# Plot the points in 3D
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(hemisphere_points[:, 0], hemisphere_points[:, 1], hemisphere_points[:, 2], c='b', marker='o')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Points on a Hemisphere with y_max = {:.2f}'.format(y_max))
plt.show()