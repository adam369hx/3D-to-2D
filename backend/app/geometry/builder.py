"""
Parametric 3D Model Builders for Technical Geometries.
Generates exact 3D models (cuboid, cylinder, plate with hole, stepped block)
with faces, edges, circles, holes, and symmetry center axes.
"""

import numpy as np
from typing import List
from app.geometry.models import (
    Point3D, Vector3D, Circle3D, Hole3D, Segment3D, Face3D, Geometry3D
)


def create_box(width: float = 100.0, height: float = 80.0, depth: float = 60.0, confidence: float = 1.0) -> Geometry3D:
    """
    Creates a 3D Box / Parallelepiped centered at origin (0,0,0).
    Width (X), Height (Y), Depth (Z).
    """
    w2, h2, d2 = width / 2.0, height / 2.0, depth / 2.0

    # 8 Vertices
    v = [
        Point3D(-w2, -h2, -d2),  # 0
        Point3D( w2, -h2, -d2),  # 1
        Point3D( w2,  h2, -d2),  # 2
        Point3D(-w2,  h2, -d2),  # 3
        Point3D(-w2, -h2,  d2),  # 4
        Point3D( w2, -h2,  d2),  # 5
        Point3D( w2,  h2,  d2),  # 6
        Point3D(-w2,  h2,  d2)   # 7
    ]

    # 6 Faces (Normal vectors pointing outwards)
    faces = [
        # Front (Z = +d2)
        Face3D([v[4], v[5], v[6], v[7]], Vector3D(0, 0, 1)),
        # Back (Z = -d2)
        Face3D([v[1], v[0], v[3], v[2]], Vector3D(0, 0, -1)),
        # Left (X = -w2)
        Face3D([v[0], v[4], v[7], v[3]], Vector3D(-1, 0, 0)),
        # Right (X = +w2)
        Face3D([v[5], v[1], v[2], v[6]], Vector3D(1, 0, 0)),
        # Top (Y = +h2)
        Face3D([v[7], v[6], v[2], v[3]], Vector3D(0, 1, 0)),
        # Bottom (Y = -h2)
        Face3D([v[0], v[1], v[5], v[4]], Vector3D(0, -1, 0)),
    ]

    # Center Axes (Symmetry)
    axes = [
        Segment3D(Point3D(-w2 * 1.2, 0, 0), Point3D(w2 * 1.2, 0, 0), kind="axis"),
        Segment3D(Point3D(0, -h2 * 1.2, 0), Point3D(0, h2 * 1.2, 0), kind="axis"),
        Segment3D(Point3D(0, 0, -d2 * 1.2), Point3D(0, 0, d2 * 1.2), kind="axis"),
    ]

    return Geometry3D(
        name="Pavé Droit / Cube",
        primitive_type="box",
        width=width,
        height=height,
        depth=depth,
        faces=faces,
        center_axes=axes,
        confidence=confidence
    )


def create_cylinder(diameter: float = 60.0, height: float = 100.0, confidence: float = 1.0) -> Geometry3D:
    """
    Creates a 3D Cylinder with axis along Y.
    Width (X) = Depth (Z) = diameter, Height (Y) = height.
    """
    radius = diameter / 2.0
    h2 = height / 2.0

    # Top and Bottom Circles
    top_circle = Circle3D(Point3D(0, h2, 0), Vector3D(0, 1, 0), radius)
    bot_circle = Circle3D(Point3D(0, -h2, 0), Vector3D(0, -1, 0), radius)

    # Top & Bottom faces
    # Approximated by circular polygon or represented parametrically
    n_seg = 32
    angles = np.linspace(0, 2 * np.pi, n_seg, endpoint=False)
    
    top_verts = [Point3D(radius * np.cos(a), h2, radius * np.sin(a)) for a in angles]
    bot_verts = [Point3D(radius * np.cos(a), -h2, radius * np.sin(a)) for a in angles[::-1]]

    faces = [
        Face3D(top_verts, Vector3D(0, 1, 0)),
        Face3D(bot_verts, Vector3D(0, -1, 0))
    ]

    # Side silhouette edges (X max and X min, Z max and Z min)
    custom_edges = [
        Segment3D(Point3D(-radius, -h2, 0), Point3D(-radius, h2, 0), kind="silhouette"),
        Segment3D(Point3D(radius, -h2, 0), Point3D(radius, h2, 0), kind="silhouette"),
        Segment3D(Point3D(0, -h2, -radius), Point3D(0, h2, -radius), kind="silhouette"),
        Segment3D(Point3D(0, -h2, radius), Point3D(0, h2, radius), kind="silhouette"),
    ]

    # Axis of symmetry
    axes = [
        Segment3D(Point3D(0, -h2 * 1.2, 0), Point3D(0, h2 * 1.2, 0), kind="axis"),
        Segment3D(Point3D(-radius * 1.2, h2, 0), Point3D(radius * 1.2, h2, 0), kind="axis"),
        Segment3D(Point3D(0, h2, -radius * 1.2), Point3D(0, h2, radius * 1.2), kind="axis"),
        Segment3D(Point3D(-radius * 1.2, -h2, 0), Point3D(radius * 1.2, -h2, 0), kind="axis"),
        Segment3D(Point3D(0, -h2, -radius * 1.2), Point3D(0, -h2, radius * 1.2), kind="axis"),
    ]

    return Geometry3D(
        name="Cylindre",
        primitive_type="cylinder",
        width=diameter,
        height=height,
        depth=diameter,
        circles=[top_circle, bot_circle],
        faces=faces,
        custom_edges=custom_edges,
        center_axes=axes,
        confidence=confidence
    )


def create_plate_with_hole(
    width: float = 120.0,
    height: float = 80.0,
    depth: float = 40.0,
    hole_diameter: float = 30.0,
    confidence: float = 1.0
) -> Geometry3D:
    """
    Creates a plate with a central through-hole along the Z axis (Front-to-Back).
    """
    box_geom = create_box(width, height, depth, confidence=confidence)
    box_geom.name = "Pièce avec Trou Debouchant"
    box_geom.primitive_type = "plate_with_hole"

    hole_radius = hole_diameter / 2.0
    d2 = depth / 2.0

    hole = Hole3D(
        center=Point3D(0, 0, 0),
        axis=Vector3D(0, 0, 1),
        radius=hole_radius,
        depth=depth
    )
    box_geom.holes = [hole]

    # Front and Back Circles for the hole
    circle_front = Circle3D(Point3D(0, 0, d2), Vector3D(0, 0, 1), hole_radius, is_hole=True)
    circle_back = Circle3D(Point3D(0, 0, -d2), Vector3D(0, 0, -1), hole_radius, is_hole=True)
    box_geom.circles = [circle_front, circle_back]

    # Center axis for hole
    hole_axes = [
        Segment3D(Point3D(0, 0, -d2 * 1.2), Point3D(0, 0, d2 * 1.2), kind="axis"),
        Segment3D(Point3D(-hole_radius * 1.3, 0, d2), Point3D(hole_radius * 1.3, 0, d2), kind="axis"),
        Segment3D(Point3D(0, -hole_radius * 1.3, d2), Point3D(0, hole_radius * 1.3, d2), kind="axis"),
        Segment3D(Point3D(-hole_radius * 1.3, 0, -d2), Point3D(hole_radius * 1.3, 0, -d2), kind="axis"),
        Segment3D(Point3D(0, -hole_radius * 1.3, -d2), Point3D(0, hole_radius * 1.3, -d2), kind="axis"),
    ]
    box_geom.center_axes.extend(hole_axes)

    return box_geom


def create_stepped_block(
    width: float = 100.0,
    height: float = 80.0,
    depth: float = 60.0,
    step_w: float = 40.0,
    step_h: float = 30.0,
    confidence: float = 1.0
) -> Geometry3D:
    """
    Creates an L-shaped / Stepped Block.
    Step removed from top-right corner.
    """
    w2, h2, d2 = width / 2.0, height / 2.0, depth / 2.0
    
    # 2D Profile in XY plane
    # Points counter-clockwise
    # (x, y):
    # 0: (-w2, -h2)
    # 1: (w2, -h2)
    # 2: (w2, h2 - step_h)
    # 3: (w2 - step_w, h2 - step_h)
    # 4: (w2 - step_w, h2)
    # 5: (-w2, h2)
    
    p2d = [
        (-w2, -h2),
        (w2, -h2),
        (w2, h2 - step_h),
        (w2 - step_w, h2 - step_h),
        (w2 - step_w, h2),
        (-w2, h2)
    ]

    front_verts = [Point3D(x, y, d2) for x, y in p2d]
    back_verts = [Point3D(x, y, -d2) for x, y in p2d[::-1]]

    faces = [
        Face3D(front_verts, Vector3D(0, 0, 1)),
        Face3D(back_verts, Vector3D(0, 0, -1)),
    ]

    # Side faces along the profile edges
    n_pts = len(p2d)
    for i in range(n_pts):
        pt1 = p2d[i]
        pt2 = p2d[(i + 1) % n_pts]
        
        v1 = Point3D(pt1[0], pt1[1], -d2)
        v2 = Point3D(pt2[0], pt2[1], -d2)
        v3 = Point3D(pt2[0], pt2[1], d2)
        v4 = Point3D(pt1[0], pt1[1], d2)

        # Compute normal
        edge_vec = np.array([pt2[0] - pt1[0], pt2[1] - pt1[1], 0])
        norm_vec = np.cross(edge_vec, np.array([0, 0, -1]))
        norm = Vector3D.from_array(norm_vec / np.linalg.norm(norm_vec))

        faces.append(Face3D([v1, v2, v3, v4], norm))

    axes = [
        Segment3D(Point3D(-w2 * 1.2, 0, 0), Point3D(w2 * 1.2, 0, 0), kind="axis"),
        Segment3D(Point3D(0, -h2 * 1.2, 0), Point3D(0, h2 * 1.2, 0), kind="axis"),
        Segment3D(Point3D(0, 0, -d2 * 1.2), Point3D(0, 0, d2 * 1.2), kind="axis"),
    ]

    return Geometry3D(
        name="Pièce Étagée / Profil en L",
        primitive_type="stepped_block",
        width=width,
        height=height,
        depth=depth,
        faces=faces,
        center_axes=axes,
        confidence=confidence
    )
