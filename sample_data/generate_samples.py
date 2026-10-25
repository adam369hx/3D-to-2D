"""
Generates sample test images for validation.
"""

import cv2
import numpy as np


def generate_sample_images():
    # 1. Cube / Box Image
    img_cube = np.full((400, 400, 3), 245, dtype=np.uint8)
    cv2.rectangle(img_cube, (100, 100), (300, 300), (40, 40, 40), -1)
    cv2.rectangle(img_cube, (100, 100), (300, 300), (0, 0, 0), 3)
    cv2.imwrite("sample_data/images/cube_sample.png", img_cube)

    # 2. Cylinder Image
    img_cyl = np.full((400, 400, 3), 245, dtype=np.uint8)
    cv2.ellipse(img_cyl, (200, 100), (80, 30), 0, 0, 360, (50, 50, 50), -1)
    cv2.rectangle(img_cyl, (120, 100), (280, 300), (50, 50, 50), -1)
    cv2.ellipse(img_cyl, (200, 300), (80, 30), 0, 0, 360, (40, 40, 40), -1)
    cv2.imwrite("sample_data/images/cylinder_sample.png", img_cyl)

    # 3. Plate with Hole Image
    img_hole = np.full((400, 500, 3), 245, dtype=np.uint8)
    cv2.rectangle(img_hole, (80, 100), (420, 300), (60, 60, 60), -1)
    cv2.circle(img_hole, (250, 200), (50), (245, 245, 245), -1)
    cv2.circle(img_hole, (250, 200), (50), (0, 0, 0), 3)
    cv2.imwrite("sample_data/images/plate_with_hole_sample.png", img_hole)


if __name__ == "__main__":
    generate_sample_images()
    print("Sample test images created in sample_data/images/")
