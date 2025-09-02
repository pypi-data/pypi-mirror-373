import numpy as np
from scipy.interpolate import BSpline

def interpolate_bspline_with_knots(edge_data, orientation, num_points=20):
    """
    Sample evenly spaced points along a B-spline curve from BREP edge data.
    
    Parameters:
        edge_data (dict): BREP edge structure containing 'curve' info
        num_points (int): Number of points to sample along the curve
        
    Returns:
        list: List of [x, y, z] coordinates
    """
    curve = edge_data["curve"]
    degree = int(curve["deg"])
    ctrl_pts = np.array(curve["ctrl"], dtype=float)  # shape (n_ctrl, 3)

    # Expand knots according to multiplicities
    knots = []
    for k, mult in zip(curve["knots"], curve["knot_mult"]):
        knots.extend([k] * mult)
    knots = np.array(knots, dtype=float)

    # Create one BSpline for each coordinate axis
    splines = [BSpline(knots, ctrl_pts[:, dim], degree) for dim in range(3)]

    # Determine valid parameter range
    t_min, t_max = knots[degree], knots[-degree - 1]

    # Sample evenly in parameter space
    t_values = np.linspace(t_min, t_max, num_points)
    points = np.array([[spl(t) for spl in splines] for t in t_values])

    return points if not orientation else points[::-1]
