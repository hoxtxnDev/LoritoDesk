"""Chroma-key utility to remove #00ff00 green screen from sprite frames."""

from typing import Final

from PIL import Image
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

TOLERANCE: Final[int] = 40


def remove_green(pil_image: Image.Image, tolerance: int = TOLERANCE) -> QPixmap:
    """Convert a PIL image with green-screen background to a transparent QPixmap.

    Every pixel whose RGB values are within *tolerance* of (0, 255, 0) is
    made fully transparent (alpha = 0).  All other pixels remain opaque.
    """
    rgba = pil_image.convert("RGBA")
    pixels = rgba.load()
    w, h = rgba.size

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r < tolerance and g > 255 - tolerance and b < tolerance:
                pixels[x, y] = (r, g, b, 0)

    qimage = QImage(
        rgba.tobytes(), w, h, 4 * w, QImage.Format.Format_RGBA8888
    )
    return QPixmap.fromImage(qimage)
