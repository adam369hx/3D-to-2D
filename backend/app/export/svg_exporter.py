"""
ISO Technical Drawing Standards and SVG Layout Engine.
Supports NF EN ISO 5456-2 (Projections), NF EN ISO 128 (Line styles),
NF EN ISO 7200 (Title block), and NF EN ISO 5457 (A4 Formats).
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from app.geometry.models import Geometry3D
from app.projection.engine import ProjectionEngine, View2D, Segment2D, Circle2D


@dataclass
class TitleBlockData:
    title: str = "PIÈCE MÉCANIQUE"
    drawing_number: str = "ISO-2025-001"
    scale: str = "1:1"
    projection_method: str = "FIRST_ANGLE"  # "FIRST_ANGLE" (European) or "THIRD_ANGLE" (American)
    author: str = "Ingénieur Dessinateur"
    date: str = "2025-02-23"
    format: str = "A4"
    company: str = "GÉNÉRATEUR DESSIN TECHNIQUE"


class ISO2DSVGExporter:
    """
    Generates exact physical ISO-compliant vector SVG documents on A4 sheets.
    """

    # Physical Dimensions in mm
    A4_PORTRAIT = (210.0, 297.0)
    A4_LANDSCAPE = (297.0, 210.0)

    # Line Styles conforming to ISO 128
    LINE_STYLES = {
        "visible": {
            "stroke": "#000000",
            "stroke-width": "0.5",     # Trait continu fort (0.5 mm)
            "stroke-linecap": "round",
            "stroke-linejoin": "round"
        },
        "hidden": {
            "stroke": "#1E293B",
            "stroke-width": "0.25",    # Trait interrompu fin (0.25 mm)
            "stroke-dasharray": "3,2",
            "stroke-linecap": "round"
        },
        "axis": {
            "stroke": "#CC0000",
            "stroke-width": "0.18",    # Trait mixte fin (0.18 mm / axe de symétrie)
            "stroke-dasharray": "10,2,2,2",
            "stroke-linecap": "round"
        },
        "border": {
            "stroke": "#000000",
            "stroke-width": "0.7"      # Cadre du dessin
        },
        "titleblock": {
            "stroke": "#000000",
            "stroke-width": "0.35"
        },
        "dimension": {
            "stroke": "#0066CC",
            "stroke-width": "0.25"
        }
    }

    @classmethod
    def get_projection_positions(
        cls,
        projection_method: str,
        orientation: str,
        views: Dict[str, View2D],
        scale: float,
        margin: float = 20.0
    ) -> Dict[str, Tuple[float, float]]:
        """
        Calculates sheet positions (cx, cy) for all 6 views on A4 sheet
        conforming to First Angle (European) or Third Angle (American) projection.
        """
        sheet_w, sheet_h = cls.A4_LANDSCAPE if orientation == "landscape" else cls.A4_PORTRAIT
        
        # Center of drawing area (leaving space for title block at bottom right)
        drawing_cx = sheet_w / 2.0
        drawing_cy = (sheet_h - 40.0) / 2.0

        # Spacing distances between view centers based on scaled model dimensions
        face_w = views["FACE"].width * scale
        face_h = views["FACE"].height * scale
        depth_sz = views["GAUCHE"].width * scale

        gap_x = max(25.0, face_w / 2.0 + depth_sz / 2.0 + 15.0)
        gap_y = max(25.0, face_h / 2.0 + depth_sz / 2.0 + 15.0)

        positions = {}

        if projection_method == "FIRST_ANGLE":
            # European Projection Standard (NF EN ISO 5456-2):
            # FACE at center
            # DESSUS (Top view) placed BELOW Face view
            # DESSOUS (Bottom view) placed ABOVE Face view
            # GAUCHE (Left view) placed to the RIGHT of Face view
            # DROITE (Right view) placed to the LEFT of Face view
            # ARRIÈRE (Rear view) placed far RIGHT
            positions["FACE"] = (drawing_cx, drawing_cy)
            positions["DESSUS"] = (drawing_cx, drawing_cy + gap_y)
            positions["DESSOUS"] = (drawing_cx, drawing_cy - gap_y)
            positions["GAUCHE"] = (drawing_cx + gap_x, drawing_cy)
            positions["DROITE"] = (drawing_cx - gap_x, drawing_cy)
            positions["ARRIÈRE"] = (drawing_cx + gap_x * 2.0, drawing_cy)

        else:
            # Third Angle Projection (American):
            # FACE at center
            # DESSUS placed ABOVE Face view
            # DESSOUS placed BELOW Face view
            # GAUCHE placed LEFT of Face view
            # DROITE placed RIGHT of Face view
            # ARRIÈRE placed far LEFT
            positions["FACE"] = (drawing_cx, drawing_cy)
            positions["DESSUS"] = (drawing_cx, drawing_cy - gap_y)
            positions["DESSOUS"] = (drawing_cx, drawing_cy + gap_y)
            positions["GAUCHE"] = (drawing_cx - gap_x, drawing_cy)
            positions["DROITE"] = (drawing_cx + gap_x, drawing_cy)
            positions["ARRIÈRE"] = (drawing_cx - gap_x * 2.0, drawing_cy)

        return positions

    @classmethod
    def create_title_block_symbol(cls, parent_group: ET.Element, x: float, y: float, method: str):
        """
        Draws the standardized ISO Projection Symbol (Cone frustum).
        """
        sym_g = ET.SubElement(parent_group, "g", {"id": "symbole-projection"})
        
        # Cone dimensions
        d1, d2, length = 6.0, 12.0, 14.0
        cx = x + 18.0
        cy = y + 10.0

        # Center axes
        ET.SubElement(sym_g, "line", {
            "x1": str(cx - 15), "y1": str(cy), "x2": str(cx + 20), "y2": str(cy),
            **cls.LINE_STYLES["axis"]
        })

        if method == "FIRST_ANGLE":
            # Cone on left, Circle views on right
            # Cone trapezoid
            x_left = cx - 10
            x_right = x_left + length
            pts = f"{x_left},{cy - d1/2} {x_right},{cy - d2/2} {x_right},{cy + d2/2} {x_left},{cy + d1/2}"
            ET.SubElement(sym_g, "polygon", {
                "points": pts, "fill": "none", **cls.LINE_STYLES["visible"]
            })
            # Circles on right
            c_x = x_right + 12
            ET.SubElement(sym_g, "circle", {
                "cx": str(c_x), "cy": str(cy), "r": str(d1/2), "fill": "none", **cls.LINE_STYLES["visible"]
            })
            ET.SubElement(sym_g, "circle", {
                "cx": str(c_x), "cy": str(cy), "r": str(d2/2), "fill": "none", **cls.LINE_STYLES["visible"]
            })
        else:
            # Third Angle: Circles on left, Cone on right
            c_x = cx - 8
            ET.SubElement(sym_g, "circle", {
                "cx": str(c_x), "cy": str(cy), "r": str(d1/2), "fill": "none", **cls.LINE_STYLES["visible"]
            })
            ET.SubElement(sym_g, "circle", {
                "cx": str(c_x), "cy": str(cy), "r": str(d2/2), "fill": "none", **cls.LINE_STYLES["visible"]
            })
            x_left = c_x + 12
            x_right = x_left + length
            pts = f"{x_left},{cy - d1/2} {x_right},{cy - d2/2} {x_right},{cy + d2/2} {x_left},{cy + d1/2}"
            ET.SubElement(sym_g, "polygon", {
                "points": pts, "fill": "none", **cls.LINE_STYLES["visible"]
            })

    @classmethod
    def generate_svg(
        cls,
        geometry: Geometry3D,
        title_data: Optional[TitleBlockData] = None,
        orientation: str = "landscape",
        scale: float = 1.0,
        projection_method: str = "FIRST_ANGLE",
        user_dimensions: Optional[List[Dict]] = None
    ) -> str:
        """
        Generates full ISO A4 SVG string.
        """
        if title_data is None:
            title_data = TitleBlockData(title=geometry.name, scale=f"1:{int(1/scale)}" if scale < 1 else f"{int(scale)}:1")

        sheet_w, sheet_h = cls.A4_LANDSCAPE if orientation == "landscape" else cls.A4_PORTRAIT

        # Root SVG Element
        svg = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": f"{sheet_w}mm",
            "height": f"{sheet_h}mm",
            "viewBox": f"0 0 {sheet_w} {sheet_h}",
            "version": "1.1"
        })

        # White Background
        ET.SubElement(svg, "rect", {
            "x": "0", "y": "0", "width": str(sheet_w), "height": str(sheet_h),
            "fill": "#FFFFFF"
        })

        # A4 Border Frame (Margin 10mm from edges)
        margin = 10.0
        ET.SubElement(svg, "rect", {
            "x": str(margin), "y": str(margin),
            "width": str(sheet_w - 2 * margin), "height": str(sheet_h - 2 * margin),
            "fill": "none", **cls.LINE_STYLES["border"]
        })

        # Generate 6 2D Views
        views = ProjectionEngine.generate_all_views(geometry)
        positions = cls.get_projection_positions(projection_method, orientation, views, scale, margin)

        # SVG Groups for structured CAD layers
        g_visible = ET.SubElement(svg, "g", {"id": "contours-visibles"})
        g_hidden = ET.SubElement(svg, "g", {"id": "arretes-cachees"})
        g_axes = ET.SubElement(svg, "g", {"id": "axes-symetrie"})
        g_texts = ET.SubElement(svg, "g", {"id": "textes-et-titres"})
        g_cotations = ET.SubElement(svg, "g", {"id": "cotations"})

        # Render each view
        for v_name, view in views.items():
            cx, cy = positions[v_name]

            # View Designation Label
            t_elem = ET.SubElement(g_texts, "text", {
                "x": str(cx), "y": str(cy + (view.height * scale) / 2.0 + 8.0),
                "text-anchor": "middle", "font-family": "sans-serif",
                "font-size": "3.5", "font-weight": "bold", "fill": "#000000"
            })
            t_elem.text = view.title_fr.upper()

            # Render Segments
            for seg in view.segments:
                # SVG Y axis is inverted relative to standard Cartesian Y
                sx1 = cx + seg.x1 * scale
                sy1 = cy - seg.y1 * scale
                sx2 = cx + seg.x2 * scale
                sy2 = cy - seg.y2 * scale

                line_kwargs = {
                    "x1": str(sx1), "y1": str(sy1),
                    "x2": str(sx2), "y2": str(sy2)
                }

                if seg.style == "visible":
                    ET.SubElement(g_visible, "line", {**line_kwargs, **cls.LINE_STYLES["visible"]})
                elif seg.style == "hidden":
                    ET.SubElement(g_hidden, "line", {**line_kwargs, **cls.LINE_STYLES["hidden"]})
                elif seg.style == "axis":
                    ET.SubElement(g_axes, "line", {**line_kwargs, **cls.LINE_STYLES["axis"]})

            # Render Circles
            for circ in view.circles:
                scx = cx + circ.cx * scale
                scy = cy - circ.cy * scale
                sr = circ.r * scale

                c_kwargs = {"cx": str(scx), "cy": str(scy), "r": str(sr), "fill": "none"}

                if circ.style == "visible":
                    ET.SubElement(g_visible, "circle", {**c_kwargs, **cls.LINE_STYLES["visible"]})
                elif circ.style == "hidden":
                    ET.SubElement(g_hidden, "circle", {**c_kwargs, **cls.LINE_STYLES["hidden"]})

        # Render User Dimensions (Cotations)
        if user_dimensions:
            for dim in user_dimensions:
                # E.g. Dimension annotation line & text
                v_target = dim.get("view", "FACE")
                if v_target in positions:
                    cx, cy = positions[v_target]
                    dx1 = cx + dim.get("x1", 0) * scale
                    dy1 = cy - dim.get("y1", 0) * scale
                    dx2 = cx + dim.get("x2", 0) * scale
                    dy2 = cy - dim.get("y2", 0) * scale
                    val_str = f"{dim.get('value', 0):.1f} mm"

                    # Dimension line
                    ET.SubElement(g_cotations, "line", {
                        "x1": str(dx1), "y1": str(dy1), "x2": str(dx2), "y2": str(dy2),
                        **cls.LINE_STYLES["dimension"]
                    })
                    # Dimension text
                    dtext = ET.SubElement(g_cotations, "text", {
                        "x": str((dx1 + dx2) / 2.0), "y": str((dy1 + dy2) / 2.0 - 2.0),
                        "text-anchor": "middle", "font-family": "sans-serif", "font-size": "3.0", "fill": "#0066CC"
                    })
                    dtext.text = val_str

        # Cartouche (Title Block) conforming to NF EN ISO 7200
        # Dimensions: 180mm x 35mm located at bottom right corner inside frame
        cb_w, cb_h = 180.0, 35.0
        cb_x = sheet_w - margin - cb_w
        cb_y = sheet_h - margin - cb_h

        g_cartouche = ET.SubElement(svg, "g", {"id": "cartouche-iso-7200"})

        # Cartouche outer border
        ET.SubElement(g_cartouche, "rect", {
            "x": str(cb_x), "y": str(cb_y), "width": str(cb_w), "height": str(cb_h),
            "fill": "#FFFFFF", **cls.LINE_STYLES["titleblock"]
        })

        # Horizontal partition line
        ET.SubElement(g_cartouche, "line", {
            "x1": str(cb_x), "y1": str(cb_y + 15), "x2": str(cb_x + cb_w), "y2": str(cb_y + 15),
            **cls.LINE_STYLES["titleblock"]
        })

        # Vertical partition line
        ET.SubElement(g_cartouche, "line", {
            "x1": str(cb_x + 100), "y1": str(cb_y), "x2": str(cb_x + 100), "y2": str(cb_y + cb_h),
            **cls.LINE_STYLES["titleblock"]
        })

        # Text labels in Cartouche
        def add_cart_text(x_offset, y_offset, label, value, size="2.5", bold=False):
            t1 = ET.SubElement(g_cartouche, "text", {
                "x": str(cb_x + x_offset), "y": str(cb_y + y_offset),
                "font-family": "sans-serif", "font-size": "2.0", "fill": "#666666"
            })
            t1.text = label
            t2 = ET.SubElement(g_cartouche, "text", {
                "x": str(cb_x + x_offset), "y": str(cb_y + y_offset + 4.0),
                "font-family": "sans-serif", "font-size": size,
                "font-weight": "bold" if bold else "normal", "fill": "#000000"
            })
            t2.text = str(value)

        add_cart_text(4, 4, "TITRE / PIÈCE:", title_data.title, size="3.5", bold=True)
        add_cart_text(4, 19, "ORGANISATION:", title_data.company)
        add_cart_text(104, 4, "ÉCHELLE:", title_data.scale, bold=True)
        add_cart_text(140, 4, "FORMAT:", title_data.format)
        add_cart_text(104, 19, "DATE:", title_data.date)
        add_cart_text(140, 19, "DESSIN N°:", title_data.drawing_number)

        # Projection Symbol
        cls.create_title_block_symbol(g_cartouche, cb_x + 50, cb_y + 15, projection_method)

        # Return formatted XML SVG
        return ET.tostring(svg, encoding="unicode")
