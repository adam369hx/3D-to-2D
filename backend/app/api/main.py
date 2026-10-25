"""
FastAPI Server Endpoints for Orthogonal Views Generator.
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.vision.analyzer import VisionAnalyzer
from app.geometry.builder import (
    create_box, create_cylinder, create_plate_with_hole, create_stepped_block
)
from app.geometry.models import Geometry3D
from app.export.svg_exporter import ISO2DSVGExporter, TitleBlockData


app = FastAPI(
    title="Générateur de Vues Orthogonales ISO API",
    description="Backend API pour l'analyse d'image, reconstruction 3D et génération SVG ISO 5456-2",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GeometryUpdateRequest(BaseModel):
    primitive_type: str  # "box", "cylinder", "plate_with_hole", "stepped_block"
    width: float
    height: float
    depth: float
    hole_diameter: Optional[float] = 30.0
    title: Optional[str] = "PIÈCE MÉCANIQUE"
    scale: Optional[float] = 1.0
    projection_method: Optional[str] = "FIRST_ANGLE"  # "FIRST_ANGLE" or "THIRD_ANGLE"
    orientation: Optional[str] = "landscape"  # "landscape" or "portrait"
    dimensions: Optional[List[Dict[str, Any]]] = None


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Orthogonal Projection Engine API"}


@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyzes uploaded image and returns estimated 3D geometric parameters.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier transmis n'est pas une image valide.")

    contents = await file.read()
    try:
        analysis = VisionAnalyzer.analyze_image_bytes(contents)
        return {"success": True, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-svg")
def generate_svg(req: GeometryUpdateRequest):
    """
    Generates A4 SVG vector drawing based on 3D geometry parameters and ISO options.
    """
    if req.primitive_type == "cylinder":
        geom = create_cylinder(diameter=req.width, height=req.height)
    elif req.primitive_type == "plate_with_hole":
        geom = create_plate_with_hole(
            width=req.width, height=req.height, depth=req.depth, hole_diameter=req.hole_diameter or 30.0
        )
    elif req.primitive_type == "stepped_block":
        geom = create_stepped_block(width=req.width, height=req.height, depth=req.depth)
    else:
        geom = create_box(width=req.width, height=req.height, depth=req.depth)

    geom.name = req.title or "PIÈCE MÉCANIQUE"

    title_data = TitleBlockData(
        title=geom.name,
        scale=f"1:{int(1/req.scale)}" if req.scale < 1 else f"{int(req.scale)}:1",
        projection_method=req.projection_method or "FIRST_ANGLE"
    )

    svg_content = ISO2DSVGExporter.generate_svg(
        geometry=geom,
        title_data=title_data,
        orientation=req.orientation or "landscape",
        scale=req.scale or 1.0,
        projection_method=req.projection_method or "FIRST_ANGLE",
        user_dimensions=req.dimensions
    )

    return Response(content=svg_content, media_type="image/svg+xml")
