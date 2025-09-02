import numpy as np
from scipy.spatial import Delaunay
import json

from interpolation import *

# ---- Triangulation ----
def triangulate_points_3d(points, tol=1e-6):
    # Remove duplicate points (within tolerance)
    unique_points = []
    for p in points:
        if not any(np.linalg.norm(p - up) < tol for up in unique_points):
            unique_points.append(p)
    points = np.array(unique_points)

    # If fewer than 3 points remain, cannot triangulate
    if points.shape[0] < 3:
        return np.array([])

    # Fit plane
    centroid = points.mean(axis=0)
    _, _, vh = np.linalg.svd(points - centroid)
    basis_x, basis_y = vh[0], vh[1]

    # Project to 2D
    points_2d = np.column_stack([
        np.dot(points - centroid, basis_x),
        np.dot(points - centroid, basis_y)
    ])

    # Check for degenerate polygons (collinear)
    if np.linalg.matrix_rank(points_2d) < 2:
        return np.array([])

    # Triangulate
    try:
        tri = Delaunay(points_2d)
    except Exception as e:
        print("Triangulation failed:", e)
        return np.array([])

    return tri.simplices

# ---- BRep processing ----
def process_brep_shape(brep_data):
    all_vertices = []
    all_faces = []

    for part in brep_data["parts"]:
        for face in part:
            loops = face["bounds"]
            for loop in loops:
                loop_points = []
                for edge in loop["bound"]["edges"]:
                    edge_data = edge["edge"]
                    orientation = edge["orientation"] == ".T."
                    curve = edge_data["curve"]
                    start = edge_data["start"]
                    end = edge_data["end"]

                    if curve["type"] == "LINE":
                        pts = interpolate_line(start, end, orientation, resolution=5)
                    elif curve["type"] == "B_SPLINE_CURVE_WITH_KNOTS":
                        pts = interpolate_bspline_with_knots(edge_data, orientation, num_points=10)
                    elif curve["type"] == "CIRCLE":
                        center = face["surface"]["position"]["location"]
                        radius = float(curve["radius"])
                        pts = interpolate_circle(curve, start, end, orientation, num_points=10)
                    else:
                        raise NotImplementedError(f"Curve type {curve['type']} not implemented")
                    
                    # Append, avoiding duplicate start points
                    if loop_points and np.allclose(loop_points[-1], pts[0]):
                        loop_points.extend(pts[1:])
                    else:
                        loop_points.extend(pts)

                loop_points = np.array(loop_points)
                start_index = len(all_vertices)
                all_vertices.extend(loop_points)
                faces = triangulate_points_3d(loop_points) + start_index
                all_faces.extend(faces)

    return all_vertices, all_faces
def load_json_brep(path):
    with open(path, 'r') as f:
        return json.load(f)
    
# ---- Example run ----
if __name__ == "__main__":
    brep_name = 'ADVANCED_BREP_SHAPE_REPRESENTATION_6011'
    brep_data = load_json_brep(f'../out/{brep_name}.json')
    vertices, faces = process_brep_shape(brep_data)

    print(vertices, faces)

    obj_filename = f'../out/{brep_name}.obj'
    
    # ---- Write OBJ ----
    with open(obj_filename, "w") as f:
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

    print(f"OBJ written to {obj_filename} with {len(vertices)} vertices and {len(faces)} faces.")
