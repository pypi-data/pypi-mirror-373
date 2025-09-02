import numpy as np

def interpolate_circle(curve, start, end, orientation, num_points=20):
    start, end = [np.array(start), np.array(end)]
    radius = curve["radius"]
    
    # Vector from start to end in the circle plane
    # Compute circle center assuming perfect circle geometry
    chord_mid = (start + end) / 2.0
    chord_vec = end - start
    chord_length = np.linalg.norm(chord_vec)

    if chord_length > 2 * radius:
        raise ValueError("Arc length cannot exceed diameter.")

    # Normal to the plane of the circle
    plane_normal = np.array([1.0, 0.0, 0.0])  # guessed from constant X

    # Direction perpendicular to chord within the plane
    chord_dir = chord_vec / chord_length
    perp_dir = np.cross(plane_normal, chord_dir)
    perp_dir /= np.linalg.norm(perp_dir)

    # Distance from chord midpoint to circle center
    center_offset = np.sqrt(radius**2 - (chord_length / 2.0)**2)
    center = chord_mid + perp_dir * center_offset

    # Local coordinates in plane
    start_vec = start - center
    end_vec = end - center

    # Angles
    start_angle = np.arctan2(start_vec[2], start_vec[1])
    end_angle = np.arctan2(end_vec[2], end_vec[1])

    # Handle orientation
    if orientation:
        if end_angle > start_angle:
            end_angle -= 2 * np.pi
    else:
        if start_angle > end_angle:
            start_angle -= 2 * np.pi

    # Sample angles
    angles = np.linspace(start_angle, end_angle, num_points)

    # Generate points
    points = []
    for a in angles:
        y = center[1] + radius * np.cos(a)
        z = center[2] + radius * np.sin(a)
        x = center[0]
        points.append([x, y, z])

    pts = np.array(points)
    return pts if orientation else pts[::-1]
