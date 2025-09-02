import numpy as np
import trimesh
import matplotlib.pyplot as plt

def triangulate_2d_polygon(points_2d):
    """
    Triangulate a 2D polygon with mapbox_earcut.
    points_2d: list of (x, y) tuples
    returns: list of triangle index triples
    """
    points_2d = np.asarray(points_2d, dtype=np.float32)
    flat_coords = points_2d.flatten()
    holes = np.array([], dtype=np.uint32)
    triangles = earcut.triangulate_float32(flat_coords, holes)
    return [(triangles[i], triangles[i+1], triangles[i+2]) for i in range(0, len(triangles), 3)]

def plot_polygon(points, tris):
    plt.figure()
    for t in tris:
        tri = [points[i] for i in t] + [points[t[0]]]
        xs, ys = zip(*tri)
        plt.plot(xs, ys, 'k-')
    plt.scatter(*zip(*points), c='red')
    plt.gca().set_aspect('equal')
    plt.title("Triangulated Polygon")
    plt.show()

# Define a square polygon
square = [
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0)
]

tris = triangulate_2d_polygon(square)
print("Triangle indices:", tris)
plot_polygon(square, tris)