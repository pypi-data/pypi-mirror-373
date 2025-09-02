"""
satfarm: A Python package for satellite image processing

This package provides a unified interface for reading, processing, analyzing,
and visualizing satellite imagery data. Built on top of rasterio and xarray,
it enables chaining of various satellite image processing operations in a
fluent interface pattern.

Key Features:
- Raster data I/O (GeoTIFF, PNG, etc.)
- Coordinate reference system transformation and resampling
- Band operations and spectral index calculations
- Image rendering and visualization
- Image clipping and geometric transformations

Examples
--------
>>> from satfarm import SatImage
>>> processor = SatImage()
>>> processor.read_tif("path/to/image.tif")
>>> processor.set_band_alias(['red', 'green', 'blue', 'nir'])
>>> ndvi_processor = next(processor.calculate_index({"NDVI": "(B[4] - B[1]) / (B[4] + B[1])"}))
"""

__version__ = "0.1.0"

from .SatImage import SatImage
from .ops import *

__all__ = ["SatImage", "ops", "__version__"]

