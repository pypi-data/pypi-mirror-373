import numpy as np

def interpolate_line(start, end, orientation, resolution=10):
    dist = np.linalg.norm(np.subtract(end, start))
    npts = int(round(dist / resolution, 0))
    pts = np.linspace(start, end, npts)

    return pts if orientation else pts[::-1]
