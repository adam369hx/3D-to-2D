"""
Exports sample SVG drawings for validation.
"""

from app.geometry.builder import (
    create_box, create_cylinder, create_plate_with_hole, create_stepped_block
)
from app.export.svg_exporter import ISO2DSVGExporter, TitleBlockData


def export_sample_svgs():
    # 1. Cube SVG
    box = create_box(width=100, height=80, depth=60)
    svg_box = ISO2DSVGExporter.generate_svg(box, TitleBlockData(title="PAVÉ DROIT 100x80x60"), scale=1.0)
    with open("sample_data/outputs/pave_droit_6_vues.svg", "w", encoding="utf-8") as f:
        f.write(svg_box)

    # 2. Cylinder SVG
    cyl = create_cylinder(diameter=60, height=100)
    svg_cyl = ISO2DSVGExporter.generate_svg(cyl, TitleBlockData(title="CYLINDRE ISO"), scale=1.0)
    with open("sample_data/outputs/cylindre_6_vues.svg", "w", encoding="utf-8") as f:
        f.write(svg_cyl)

    # 3. Plate with Hole SVG
    plate = create_plate_with_hole(width=120, height=80, depth=40, hole_diameter=30)
    dims = [{
        "view": "FACE", "x1": -60, "y1": -40, "x2": 60, "y2": -40, "value": 120.0
    }]
    svg_plate = ISO2DSVGExporter.generate_svg(plate, TitleBlockData(title="PLAQUE PERCÉE ISO"), scale=1.0, user_dimensions=dims)
    with open("sample_data/outputs/plaque_percee_6_vues.svg", "w", encoding="utf-8") as f:
        f.write(svg_plate)


if __name__ == "__main__":
    export_sample_svgs()
    print("Sample SVG outputs saved in sample_data/outputs/")
