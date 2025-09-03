# Type stubs for zignal package
# This file helps LSPs understand the module structure

from __future__ import annotations

# Re-export all types from _zignal
from ._zignal import (
    Rgb as Rgb,
    Rgba as Rgba,
    Hsl as Hsl,
    Hsv as Hsv,
    Lab as Lab,
    Lch as Lch,
    Lms as Lms,
    Oklab as Oklab,
    Oklch as Oklch,
    Xyb as Xyb,
    Xyz as Xyz,
    Ycbcr as Ycbcr,
    Rectangle as Rectangle,
    BitmapFont as BitmapFont,
    Image as Image,
    Matrix as Matrix,
    Canvas as Canvas,
    Interpolation as Interpolation,
    Blending as Blending,
    DrawMode as DrawMode,
    MotionBlur as MotionBlur,
    OptimizationPolicy as OptimizationPolicy,
    Assignment as Assignment,
    FeatureDistributionMatching as FeatureDistributionMatching,
    PCA as PCA,
    ConvexHull as ConvexHull,
    SimilarityTransform as SimilarityTransform,
    AffineTransform as AffineTransform,
    ProjectiveTransform as ProjectiveTransform,
    solve_assignment_problem as solve_assignment_problem,
    # Type aliases
    Point as Point,
    Size as Size,
    RgbTuple as RgbTuple,
    RgbaTuple as RgbaTuple,
    Color as Color,
)

__version__: str
__all__: list[str]
