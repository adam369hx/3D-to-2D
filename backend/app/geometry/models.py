"""
3D Geometry Data Models and Primitives for Orthogonal Projection Engine.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import numpy as np


@dataclass
class Point3D:
    x: float
    y: float
    z: float

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=float)

    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'Point3D':
        return cls(x=float(arr[0]), y=float(arr[1]), z=float(arr[2]))


@dataclass
class Vector3D:
    x: float
    y: float
    z: float

    def length(self) -> float:
        return float(np.sqrt(self.x**2 + self.y**2 + self.z**2))

    def normalize(self) -> 'Vector3D':
        l = self.length()
        if l == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / l, self.y / l, self.z / l)


@dataclass
class Circle3D:
    center: Point3D
    normal: Vector3D  # Orientation normal of circle plane
    radius: float
    is_hole: bool = False


@dataclass
class Hole3D:
    center: Point3D
    axis: Vector3D  # Drilling direction (e.g., (0,0,-1) for Z-axis)
    radius: float
    depth: float  # -1 for through-hole


@dataclass
class Segment3D:
    p1: Point3D
    p2: Point3D
    kind: str = "edge"  # "edge", "axis", "silhouette"
    feature_id: Optional[str] = None


@dataclass
class Face3D:
    vertices: List[Point3D]
    normal: Vector3D
    is_outer: bool = True


@dataclass
class Geometry3D:
    """
    3D Parametric CAD Geometry representation.
    """
    name: str = "Objet 3D"
    primitive_type: str = "box"  # "box", "cylinder", "plate_with_hole", "stepped_block", "custom"
    width: float = 100.0   # X dimension (mm)
    height: float = 80.0   # Y dimension (mm)
    depth: float = 60.0    # Z dimension (mm)
    
    # Primitives & Features
    holes: List[Hole3D] = field(default_factory=list)
    circles: List[Circle3D] = field(default_factory=list)
    faces: List[Face3D] = field(default_factory=list)
    custom_edges: List[Segment3D] = field(default_factory=list)
    center_axes: List[Segment3D] = field(default_factory=list)

    # Metadata
    confidence: float = 1.0  # 1.0 for known/calibrated geometry, <1.0 for image estimation
    warnings: List[str] = field(default_factory=list)
    calibration_reference: Optional[str] = None  # e.g., "width=100mm"

    def get_bounding_box(self) -> Tuple[Point3D, Point3D]:
        """Returns (min_pt, max_pt) for 3D model bounding box."""
        min_pt = Point3D(-self.width / 2.0, -self.height / 2.0, -self.depth / 2.0)
        max_pt = Point3D(self.width / 2.0, self.height / 2.0, self.depth / 2.0)
        return min_pt, max_pt
