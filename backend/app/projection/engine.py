"""
3D to 2D Orthographic Projection Engine with Hidden Edge Determination
Conforming to ISO 5456-2 and ISO 128 conventions.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from app.geometry.models import (
    Point3D, Vector3D, Circle3D, Hole3D, Segment3D, Face3D, Geometry3D
)


@dataclass
class Segment2D:
    x1: float
    y1: float
    x2: float
    y2: float
    style: str  # "visible", "hidden", "axis"
    view_name: str  # "FACE", "ARRIÈRE", "GAUCHE", "DROITE", "DESSUS", "DESSOUS"


@dataclass
class Circle2D:
    cx: float
    cy: float
    r: float
    style: str  # "visible", "hidden", "axis"
    view_name: str


@dataclass
class Ellipse2D:
    cx: float
    cy: float
    rx: float
    ry: float
    angle: float
    style: str
    view_name: str


@dataclass
class View2D:
    name: str  # e.g. "FACE"
    title_fr: str  # e.g. "Vue de face"
    width: float   # 2D model bounding width in mm
    height: float  # 2D model bounding height in mm
    segments: List[Segment2D]
    circles: List[Circle2D]
    ellipses: List[Ellipse2D]
    camera_dir: Vector3D
    bbox_2d: Tuple[float, float, float, float]  # (min_x, min_y, max_x, max_y)


class ProjectionEngine:
    """
    Computes exact 2D projections for all 6 standard orthogonal views:
    FACE, ARRIÈRE, GAUCHE, DROITE, DESSUS, DESSOUS.
    """

    # Camera direction vectors looking TOWARDS the model
    CAMERA_DIRECTIONS = {
        "FACE": Vector3D(0, 0, -1),      # Looking down -Z
        "ARRIÈRE": Vector3D(0, 0, 1),     # Looking down +Z
        "GAUCHE": Vector3D(1, 0, 0),      # Looking down +X
        "DROITE": Vector3D(-1, 0, 0),     # Looking down -X
        "DESSUS": Vector3D(0, -1, 0),     # Looking down -Y
        "DESSOUS": Vector3D(0, 1, 0)      # Looking down +Y
    }

    VIEW_TITLES = {
        "FACE": "Vue de face",
        "ARRIÈRE": "Vue arrière",
        "GAUCHE": "Vue de gauche",
        "DROITE": "Vue de droite",
        "DESSUS": "Vue de dessus",
        "DESSOUS": "Vue de dessous"
    }

    @classmethod
    def project_point(cls, pt: Point3D, view_name: str) -> Tuple[float, float, float]:
        """
        Projects 3D point (x, y, z) into 2D (u, v) and depth d.
        Depth d is used for visibility / occlusion check.
        """
        x, y, z = pt.x, pt.y, pt.z

        if view_name == "FACE":
            # Camera at +Z looking towards -Z
            return x, y, -z
        elif view_name == "ARRIÈRE":
            # Camera at -Z looking towards +Z
            return -x, y, z
        elif view_name == "GAUCHE":
            # Camera at -X looking towards +X
            return z, y, x
        elif view_name == "DROITE":
            # Camera at +X looking towards -X
            return -z, y, -x
        elif view_name == "DESSUS":
            # Camera at +Y looking towards -Y
            return x, -z, y
        elif view_name == "DESSOUS":
            # Camera at -Y looking towards +Y
            return x, z, -y
        else:
            raise ValueError(f"Unknown view name: {view_name}")

    @classmethod
    def generate_view(cls, geometry: Geometry3D, view_name: str) -> View2D:
        """
        Generates 2D projection for a single orthogonal view.
        """
        camera_dir = cls.CAMERA_DIRECTIONS[view_name]
        segments: List[Segment2D] = []
        circles: List[Circle2D] = []
        ellipses: List[Ellipse2D] = []

        # 1. Process 3D Faces and Edges
        edge_visibility_map: Dict[Tuple[Tuple[float, float, float], Tuple[float, float, float]], str] = {}

        for face in geometry.faces:
            # Face outward normal dot camera_dir
            norm_dot = (
                face.normal.x * camera_dir.x +
                face.normal.y * camera_dir.y +
                face.normal.z * camera_dir.z
            )

            # Face is front-facing if norm_dot > 1e-4
            is_front_facing = norm_dot > 1e-4

            # Extract edges from face polygon
            n_v = len(face.vertices)
            for i in range(n_v):
                p1 = face.vertices[i]
                p2 = face.vertices[(i + 1) % n_v]

                # Canonical edge representation (order invariant)
                pt1_tuple = (round(p1.x, 3), round(p1.y, 3), round(p1.z, 3))
                pt2_tuple = (round(p2.x, 3), round(p2.y, 3), round(p2.z, 3))
                edge_key = tuple(sorted([pt1_tuple, pt2_tuple]))

                current_status = edge_visibility_map.get(edge_key, "hidden")
                if is_front_facing:
                    edge_visibility_map[edge_key] = "visible"
                elif current_status != "visible":
                    edge_visibility_map[edge_key] = "hidden"

        # Project mapped edges
        for (pt1_tuple, pt2_tuple), vis in edge_visibility_map.items():
            pt1 = Point3D(*pt1_tuple)
            pt2 = Point3D(*pt2_tuple)

            u1, v1, _ = cls.project_point(pt1, view_name)
            u2, v2, _ = cls.project_point(pt2, view_name)

            # Skip degenerate point projections
            if abs(u1 - u2) < 1e-3 and abs(v1 - v2) < 1e-3:
                continue

            segments.append(Segment2D(u1, v1, u2, v2, style=vis, view_name=view_name))

        # 2. Process Custom Edges / Silhouettes (for cylinders, curves)
        for edge in geometry.custom_edges:
            u1, v1, d1 = cls.project_point(edge.p1, view_name)
            u2, v2, d2 = cls.project_point(edge.p2, view_name)

            # Determine silhouette visibility based on cylinder direction
            vis = "visible"
            if edge.kind == "silhouette":
                if view_name in ["DESSUS", "DESSOUS"] and geometry.primitive_type == "cylinder":
                    continue  # Silhouette disappears into circle top/bottom outline

            if abs(u1 - u2) > 1e-3 or abs(v1 - v2) > 1e-3:
                segments.append(Segment2D(u1, v1, u2, v2, style=vis, view_name=view_name))

        # 3. Process Circles (Top/Bottom of cylinders, Holes)
        for circle in geometry.circles:
            u_c, v_c, _ = cls.project_point(circle.center, view_name)
            
            # Normal dot camera_dir
            c_norm_dot = (
                circle.normal.x * camera_dir.x +
                circle.normal.y * camera_dir.y +
                circle.normal.z * camera_dir.z
            )

            # Check if circle is viewed end-on (circle plane parallel to camera direction)
            if abs(c_norm_dot) > 0.9:
                # Direct view of full circle
                vis = "visible"
                circles.append(Circle2D(u_c, v_c, circle.radius, style=vis, view_name=view_name))
            elif abs(c_norm_dot) < 0.1:
                # Viewed edge-on: projects as a line segment
                if circle.is_hole:
                    vis = "hidden" if abs(c_norm_dot) < 0.1 else "visible"
                else:
                    vis = "visible"

                # Side projection line for circle diameter
                if view_name in ["FACE", "ARRIÈRE", "GAUCHE", "DROITE"]:
                    r = circle.radius
                    if abs(circle.normal.y) > 0.9:  # Cylinder aligned with Y
                        segments.append(Segment2D(u_c - r, v_c, u_c + r, v_c, style=vis, view_name=view_name))

        # 4. Process Holes
        for hole in geometry.holes:
            u_h, v_h, _ = cls.project_point(hole.center, view_name)

            # Hole direction dot camera_dir
            axis_dot = (
                hole.axis.x * camera_dir.x +
                hole.axis.y * camera_dir.y +
                hole.axis.z * camera_dir.z
            )

            if abs(axis_dot) > 0.9:
                # Hole viewed along drilling axis -> circle
                circles.append(Circle2D(u_h, v_h, hole.radius, style="visible", view_name=view_name))
            else:
                # Hole viewed side-on -> two hidden dashed parallel lines
                r = hole.radius
                depth = hole.depth if hole.depth > 0 else geometry.depth

                if view_name in ["GAUCHE", "DROITE", "DESSUS", "DESSOUS"]:
                    d2 = depth / 2.0
                    segments.append(Segment2D(u_h - d2, v_h + r, u_h + d2, v_h + r, style="hidden", view_name=view_name))
                    segments.append(Segment2D(u_h - d2, v_h - r, u_h + d2, v_h - r, style="hidden", view_name=view_name))

        # 5. Process Center / Symmetry Axes
        for axis_seg in geometry.center_axes:
            u1, v1, _ = cls.project_point(axis_seg.p1, view_name)
            u2, v2, _ = cls.project_point(axis_seg.p2, view_name)

            if abs(u1 - u2) > 1e-3 or abs(v1 - v2) > 1e-3:
                segments.append(Segment2D(u1, v1, u2, v2, style="axis", view_name=view_name))

        # Compute Bounding Box (Excluding symmetry center axes for physical model bounds)
        body_segs = [s for s in segments if s.style != "axis"]
        all_x = [s.x1 for s in body_segs] + [s.x2 for s in body_segs] + [c.cx - c.r for c in circles] + [c.cx + c.r for c in circles]
        all_y = [s.y1 for s in body_segs] + [s.y2 for s in body_segs] + [c.cy - c.r for c in circles] + [c.cy + c.r for c in circles]

        if not all_x or not all_y:
            min_x, max_x, min_y, max_y = -10.0, 10.0, -10.0, 10.0
        else:
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)

        w = max(1.0, max_x - min_x)
        h = max(1.0, max_y - min_y)

        return View2D(
            name=view_name,
            title_fr=cls.VIEW_TITLES[view_name],
            width=w,
            height=h,
            segments=segments,
            circles=circles,
            ellipses=ellipses,
            camera_dir=camera_dir,
            bbox_2d=(min_x, min_y, max_x, max_y)
        )

    @classmethod
    def generate_all_views(cls, geometry: Geometry3D) -> Dict[str, View2D]:
        """
        Generates all 6 orthogonal views from the 3D geometry model.
        """
        views = {}
        for view_name in ["FACE", "ARRIÈRE", "GAUCHE", "DROITE", "DESSUS", "DESSOUS"]:
            views[view_name] = cls.generate_view(geometry, view_name)
        return views
