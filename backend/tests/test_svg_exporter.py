"""
Unit tests for ISO SVG Exporter and Layout Validation.
"""

import pytest
import xml.etree.ElementTree as ET
from app.geometry.builder import create_box, create_plate_with_hole
from app.export.svg_exporter import ISO2DSVGExporter, TitleBlockData


def test_svg_export_valid_xml():
    box = create_box(100, 80, 60)
    svg_str = ISO2DSVGExporter.generate_svg(box, scale=1.0, orientation="landscape")

    # Assert valid XML
    root = ET.fromstring(svg_str)
    assert root.tag == "{http://www.w3.org/2000/svg}svg" or root.tag == "svg"
    assert root.attrib["width"] == "297.0mm"
    assert root.attrib["height"] == "210.0mm"


def test_svg_export_contains_required_iso_layers():
    box = create_box(100, 80, 60)
    svg_str = ISO2DSVGExporter.generate_svg(box)
    root = ET.fromstring(svg_str)

    group_ids = [elem.attrib.get("id") for elem in root.findall(".//{http://www.w3.org/2000/svg}g")]
    if not group_ids:
        group_ids = [elem.attrib.get("id") for elem in root.findall(".//g")]

    assert "contours-visibles" in group_ids
    assert "arretes-cachees" in group_ids
    assert "axes-symetrie" in group_ids
    assert "cartouche-iso-7200" in group_ids


def test_svg_export_portrait_orientation():
    box = create_box(100, 80, 60)
    svg_str = ISO2DSVGExporter.generate_svg(box, orientation="portrait")
    root = ET.fromstring(svg_str)

    assert root.attrib["width"] == "210.0mm"
    assert root.attrib["height"] == "297.0mm"


def test_svg_export_third_angle_projection():
    plate = create_plate_with_hole(120, 80, 40, hole_diameter=30)
    svg_str = ISO2DSVGExporter.generate_svg(
        plate, projection_method="THIRD_ANGLE", scale=0.5
    )
    root = ET.fromstring(svg_str)
    assert root is not None
