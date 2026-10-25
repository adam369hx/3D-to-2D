"""
Unit tests for Vision Analysis Module and API Endpoints.
"""

import pytest
import numpy as np
import cv2
from fastapi.testclient import TestClient
from app.vision.analyzer import VisionAnalyzer
from app.api.main import app


client = TestClient(app)


def create_dummy_synthetic_image():
    """Generates a synthetic PNG image of a rectangle for testing."""
    img = np.full((300, 400, 3), 255, dtype=np.uint8)
    # Draw black rectangle
    cv2.rectangle(img, (50, 50), (350, 250), (0, 0, 0), -1)
    _, encoded = cv2.imencode(".png", img)
    return encoded.tobytes()


def test_vision_analyzer_synthetic_image():
    img_bytes = create_dummy_synthetic_image()
    analysis = VisionAnalyzer.analyze_image_bytes(img_bytes)

    assert "detected_primitive" in analysis
    assert "confidence" in analysis
    assert analysis["confidence"] > 0.0
    assert "warnings" in analysis


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_api_generate_svg_endpoint():
    payload = {
        "primitive_type": "plate_with_hole",
        "width": 100.0,
        "height": 80.0,
        "depth": 40.0,
        "hole_diameter": 25.0,
        "title": "TEST PIECE",
        "scale": 1.0,
        "projection_method": "FIRST_ANGLE",
        "orientation": "landscape"
    }

    res = client.post("/api/generate-svg", json=payload)
    assert res.status_code == 200
    assert "image/svg+xml" in res.headers["content-type"]
    assert "<svg" in res.text
    assert "contours-visibles" in res.text
