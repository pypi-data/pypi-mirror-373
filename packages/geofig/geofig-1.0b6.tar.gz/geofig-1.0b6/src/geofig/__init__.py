"""Library to procedurally generate geometric figures as SVG images."""

from .figure import CSS, Figure, Padding, ts
from .geometry import Arc, Scalar, Transformer, closest_entity, closest_point, ellipse_angle


__all__ = (
    "Arc",
    "CSS",
    "Figure",
    "Padding",
    "Scalar",
    "Transformer",
    "closest_entity",
    "closest_point",
    "ellipse_angle",
    "ts",
)
