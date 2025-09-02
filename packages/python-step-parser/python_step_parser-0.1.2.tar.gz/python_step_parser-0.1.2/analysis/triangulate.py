import json
import numpy as np
import trimesh
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import trimesh.exchange
import trimesh.exchange.obj
import math

from scipy.interpolate import BSpline
from scipy.spatial import Delaunay

resolution = 10

def load_json_brep(path):
    with open(path, 'r') as f:
        return json.load(f)

def normalize(v):
    return v / np.linalg.norm(v)

def sample_brep_circle(edge_curve_circle, surface, orientation, num_points=20):
    start, end = [np.array(edge_curve_circle["start"]), np.array(edge_curve_circle["end"])]
    radius = edge_curve_circle["curve"]["radius"]
    
    # --- Determine center, axis, and reference direction ---
    if surface and surface['type'].upper() == 'CYLINDRICAL':
        # Surface gives cylinder center at some reference point
        cyl_pos = surface['position']
        center = np.array(cyl_pos['location'], dtype=float)
        axis = np.array(cyl_pos['axis'], dtype=float)
        axis /= np.linalg.norm(axis)

        # Reference direction = direction vector in cylinder's base plane
        ref_dir = np.array(cyl_pos['direction'], dtype=float)
        ref_dir /= np.linalg.norm(ref_dir)

        # Second basis vector in plane
        y_axis = np.cross(axis, ref_dir)

        # Project start/end onto base plane to get angles
        start_vec = start - center
        end_vec = end - center
        start_angle = math.atan2(np.dot(start_vec, y_axis), np.dot(start_vec, ref_dir))
        end_angle = math.atan2(np.dot(end_vec, y_axis), np.dot(end_vec, ref_dir))

        # Handle wrap-around for arc
        if np.allclose(start, end, atol=1e-8):
            angles = np.linspace(0, 2 * math.pi, num_points, endpoint=False)
        else:
            if end_angle < start_angle:
                end_angle += 2 * math.pi
            angles = np.linspace(start_angle, end_angle, num_points)

        # Height offset along cylinder axis (from start point)
        z_offset = np.dot(start_vec, axis)

        # Build points
        points = np.array([
            center + radius * math.cos(a) * ref_dir +
            radius * math.sin(a) * y_axis +
            z_offset * axis
            for a in angles
        ])
        return points
    
    else:
        print('surface type', surface['type'])
        # Base axis system
        base_center = np.array(surface["position"]["location"], dtype=float)

        # Get local axes from surface
        axis_z = normalize(np.array(surface["position"]["axis"], dtype=float))      # Cylinder axis
        axis_x = normalize(np.array(surface["position"]["direction"], dtype=float)) # Reference X direction
        axis_y = normalize(np.cross(axis_z, axis_x))                                # Perpendicular Y

        # Shift the center along axis to match this bound
        axis_offset = np.dot(start - base_center, axis_z)
        circle_center = base_center + axis_z * axis_offset
        
        # Decide if this is a full circle
        full_circle = np.allclose(start, end, atol=1e-8)
        if full_circle:
            angles = np.linspace(0, 2 * math.pi, num_points, endpoint=False)
        else:
            start_angle = math.atan2(np.dot(start - circle_center, axis_y),
                                    np.dot(start - circle_center, axis_x))
            end_angle = math.atan2(np.dot(end - circle_center, axis_y),
                                np.dot(end - circle_center, axis_x))
            if end_angle < start_angle:
                end_angle += 2 * math.pi
            angles = np.linspace(start_angle, end_angle, num_points)

        # Build points in 3D
        points = np.array([
            circle_center + radius * math.cos(a) * axis_x + radius * math.sin(a) * axis_y
            for a in angles
        ])

    return points if orientation else points[::-1]

def sample_brep_bspline_with_knots(edge_data, orientation, num_points=20):
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

    return points if orientation else points[::-1]

def extract_curve_points_line(curve, orientation):
    points = np.array([curve["start"], curve["end"]])
    return points if orientation else points[::-1]

def extract_oriented_edge_points(edge_data, surface, orientation):
    curve_type = edge_data["curve"]["type"]
    
    if curve_type == "CIRCLE":
        return sample_brep_circle(edge_data, surface, orientation, 20)
    
    if curve_type == "B_SPLINE_CURVE_WITH_KNOTS":
        return sample_brep_bspline_with_knots(edge_data, orientation, 20)
    
    if curve_type != "LINE":
        print(f'unknown curve type {curve_type}. rendering as line')
    
    return extract_curve_points_line(edge_data, orientation)

def extract_face_bound(face_bound, surface):
    loop = face_bound["bound"]["edges"]
    face_orientation = face_bound["orientation"] == '.T.'
    points = None
    for edge in loop:
        edge_points = extract_oriented_edge_points(
            edge["edge"],
            surface,
            str(edge["orientation"]).upper() == '.T.'
        )
        # print('edge points', edge_points, edge["edge"]["curve"]["type"])
        if points is None:
            points = edge_points
        else:
            points = np.concatenate([points, edge_points])
    if face_orientation:
        points = points[::-1]
    return points.tolist()

def extract_cylindrical_surface(bounds, surface, radial_segments=36, height_segments=1):
    """
    Sample a cylindrical surface mesh between two circular edge loops.

    Parameters
    ----------
    edge_loops : list of dict
        Each dict is an ORIENTED_EDGE for a circular loop. Expected exactly 2.
    surface : dict
        The CYLINDRICAL surface definition from the BRep.
    radial_segments : int
        Number of segments around the cylinder.
    height_segments : int
        Number of segments along the cylinder axis.
    
    Returns
    -------
    vertices : np.ndarray
        (N, 3) array of vertex positions.
    faces : np.ndarray
        (M, 3) array of triangle indices.
    """

    if surface["type"].upper() != "CYLINDRICAL":
        raise ValueError("Surface type must be CYLINDRICAL")

    # Extract surface axis and reference direction
    cyl_pos = surface['position']
    center_base = np.array(cyl_pos['location'], dtype=float)
    axis = np.array(cyl_pos['axis'], dtype=float)
    axis /= np.linalg.norm(axis)

    ref_dir = np.array(cyl_pos['direction'], dtype=float)
    ref_dir /= np.linalg.norm(ref_dir)
    y_axis = np.cross(axis, ref_dir)

    radius = float(surface['radius'])

    print('bounds', bounds)

    # Get heights from edge loops (distance along axis from base center)
    heights = []
    for loop in bounds:
        edge_curve = loop['edge']
        start = np.array(edge_curve['start'], dtype=float)
        vec_from_center = start - center_base
        h = np.dot(vec_from_center, axis)
        heights.append(h)
    heights = sorted(heights)

    # Generate vertices
    vertices = []
    for i in range(height_segments + 1):
        z = heights[0] + (heights[1] - heights[0]) * (i / height_segments)
        for j in range(radial_segments):
            theta = 2 * math.pi * j / radial_segments
            point = center_base + z * axis \
                    + radius * math.cos(theta) * ref_dir \
                    + radius * math.sin(theta) * y_axis
            vertices.append(point)
    vertices = np.array(vertices)

    # Generate faces (quad strip triangulated)
    faces = []
    for i in range(height_segments):
        for j in range(radial_segments):
            next_j = (j + 1) % radial_segments
            p0 = i * radial_segments + j
            p1 = i * radial_segments + next_j
            p2 = (i + 1) * radial_segments + j
            p3 = (i + 1) * radial_segments + next_j
            faces.append([p0, p2, p1])
            faces.append([p1, p2, p3])
    faces = np.array(faces, dtype=int)

    return vertices.tolist(), faces.tolist()

def extract_face(face, vert_offset):
    surface = face["surface"]
    if surface["type"] == "CYLINDRICAL":
        top_bound = face["bounds"][0]["bound"]["edges"][0]
        bottom_bound = face["bounds"][1]["bound"]["edges"][0]
        return extract_cylindrical_surface([top_bound, bottom_bound], surface)
    else:
        face_points = []
        for bound in face["bounds"]:
            if bound["type"] == "FACE_BOUND":
                face_points += extract_face_bound(bound, surface)
            else:
                print(f'Could not find handler for bound with type {bound["type"]}')

        face_points = remove_consecutive_duplicates(face_points)
        tri_simplices = triangulate_points_3d(face_points, vert_offset)
        return face_points, tri_simplices

def plot_3d_polygon_flat(points_2d, flatten='z'):
    x, y, z = zip(*points_2d)
    if flatten.lower() == 'x':
        plt.plot(z + (z[0],), y + (y[0],), '-o')
    elif flatten.lower() == 'y':
        plt.plot(x + (x[0],), z + (z[0],), '-o')
    else:
        plt.plot(x + (x[0],), y + (y[0],), '-o')
    plt.axis('equal')
    plt.title("Projected 2D Polygon")
    plt.show()

def remove_consecutive_duplicates(points):
    cleaned = []
    for p in points:
        if not cleaned or not np.allclose(p, cleaned[-1]):
            cleaned.append(p)
    # Optionally remove last if it matches the first (closed loop)
    if len(cleaned) > 1 and np.allclose(cleaned[0], cleaned[-1]):
        cleaned.pop()
    return cleaned

def triangulate_points_3d(points, offset=0):
    """
    Triangulate a set of 3D points lying on a plane.
    
    Args:
        points (np.ndarray): Nx3 array of 3D coordinates.
    
    Returns:
        vertices (np.ndarray): Nx3 array of vertices.
        faces (np.ndarray): Mx3 array of triangle vertex indices.
    """
    points = np.array(points)
    if points.shape[1] != 3:
        raise ValueError("Input points must be Nx3 array of 3D coordinates")
    
    # Step 1: Fit a plane to points
    centroid = points.mean(axis=0)
    uu, dd, vv = np.linalg.svd(points - centroid)
    normal = vv[2, :]
    
    # Step 2: Build orthonormal basis for projection
    basis_x = vv[0, :]
    basis_y = vv[1, :]
    
    # Step 3: Project points to 2D
    points_2d = np.column_stack([
        np.dot(points - centroid, basis_x),
        np.dot(points - centroid, basis_y)
    ])
    
    # Step 4: Triangulate in 2D
    tri = Delaunay(points_2d)
    
    # Step 5: Return original vertices and triangle indices
    return (tri.simplices + offset).tolist()

def points_to_obj(points, simplices, filename):
    with open(filename, 'w') as f:
        # Vertices
        for v in points:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        # Faces (OBJ uses 1-based indexing)
        for face in simplices:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

# Load and process the JSON
brep_data = load_json_brep("../out/ADVANCED_BREP_SHAPE_REPRESENTATION_6011.json")

all_vertices = []
all_faces = []
vert_offset = 0

for face_set in brep_data["parts"]:
    print('faces in sets', len(face_set))
    for face in face_set:
        face_points, face_tris = extract_face(face, vert_offset)
        print(f'adding {len(face_tris)} new triangles')
        print(face_tris)

        all_vertices += face_points
        all_faces += face_tris
        vert_offset += len(face_points)

        # break



print('rendering', len(all_faces), 'triangle points')
print('points', all_vertices)
points_to_obj(all_vertices, all_faces, '../out/ADVANCED_BREP_SHAPE_REPRESENTATION_6011_alt.obj')


# Optionally: create a full mesh for visualization or export
# vertices = np.vstack(all_triangles)
# faces = np.arange(len(vertices)).reshape(-1, 3)
# mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

# Preview or save
# mesh.show()
# mesh.export('output.stl')

# print('volume', mesh.volume)

# face_obj = trimesh.exchange.obj.export_obj(mesh)
# with open(f'../out/ADVANCED_BREP_SHAPE_REPRESENTATION_6011.obj', 'w') as f:
#     f.writelines(face_obj)
