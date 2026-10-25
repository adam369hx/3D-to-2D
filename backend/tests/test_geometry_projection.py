"""
Unit tests for Geometry Models, Builder, and Orthogonal Projection Engine.
"""

import pytest
import numpy as np
from app.geometry.models import Point3D, Vector3D, Geometry3D
from app.geometry.builder import (
    create_box, create_cylinder, create_plate_with_hole, create_stepped_block
)
from app.projection.engine import ProjectionEngine


def test_box_creation():
    box = create_box(width=100, height=80, depth=60)
    assert box.width == 100
    assert box.height == 80
    assert box.depth == 60
    assert len(box.faces) == 6
    assert len(box.center_axes) == 3


def test_cylinder_creation():
    cyl = create_cylinder(diameter=50, height=100)
    assert cyl.width == 50
    assert cyl.height == 100
    assert cyl.depth == 50
    assert len(cyl.circles) == 2
    assert len(cyl.custom_edges) == 4


def test_plate_with_hole_creation():
    plate = create_plate_with_hole(width=120, height=80, depth=40, hole_diameter=30)
    assert len(plate.holes) == 1
    assert plate.holes[0].radius == 15.0
    assert len(plate.circles) == 2


def test_projection_all_six_views():
    box = create_box(width=100, height=80, depth=60)
    views = ProjectionEngine.generate_all_views(box)

    expected_views = ["FACE", "ARRIÈRE", "GAUCHE", "DROITE", "DESSUS", "DESSOUS"]
    assert set(views.keys()) == set(expected_views)

    for name, view in views.items():
        assert view.name == name
        assert len(view.segments) > 0
        assert view.width > 0
        assert view.height > 0


def test_view_proportions_and_alignment():
    # Box 100 x 80 x 60
    box = create_box(width=100, height=80, depth=60)
    views = ProjectionEngine.generate_all_views(box)

    # Face view width = 100, height = 80
    assert abs(views["FACE"].width - 100.0) < 1e-2
    assert abs(views["FACE"].height - 80.0) < 1e-2

    # Left / Right view width = 60, height = 80
    assert abs(views["GAUCHE"].width - 60.0) < 1e-2
    assert abs(views["GAUCHE"].height - 80.0) < 1e-2

    # Top / Bottom view width = 100, height = 60
    assert abs(views["DESSUS"].width - 100.0) < 1e-2
    assert abs(views["DESSUS"].height - 60.0) < 1e-2


def test_hidden_lines_in_hole_projection():
    plate = create_plate_with_hole(width=120, height=80, depth=40, hole_diameter=30)
    views = ProjectionEngine.generate_all_views(plate)

    # Top view should contain hidden lines representing the hole through the depth
    dessus_view = views["DESSUS"]
    hidden_segs = [s for s in dessus_view.segments if s.style == "hidden"]
    assert len(hidden_segs) >= 2
