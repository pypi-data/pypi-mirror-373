# satfarm

[![PyPI version](https://badge.fury.io/py/satfarm.svg)](https://badge.fury.io/py/satfarm)
[![Python versions](https://img.shields.io/pypi/pyversions/satfarm.svg)](https://pypi.org/project/satfarm/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for satellite image processing with a fluent interface, built on top of rasterio and xarray.

## 🌟 Features

- **Raster data I/O**: Support for GeoTIFF, PNG, and other common formats
- **Coordinate reference system**: Transformation and resampling capabilities  
- **Band operations**: Spectral index calculations and band manipulations
- **Image rendering**: Visualization with customizable color maps
- **Geometric operations**: Clipping, shrinking, and spatial transformations
- **Fluent interface**: Chain operations together for readable, maintainable code

## 📦 Installation

```bash
pip install satfarm
```

### Development Installation

```bash
git clone https://github.com/yourusername/satfarm.git
cd satfarm
pip install -e ".[dev]"
```

## 🚀 Quick Start

```python
from satfarm import SatImage
import numpy as np

# Basic usage
processor = SatImage()

# Load and process satellite imagery
result = (processor
    .read_tif("path/to/satellite_image.tif")
    .change_pixel_dtype("float32")
    .change_nodata(new_nodata=np.nan, old_nodata=0)
    .reproject("EPSG:4326")
    .shrink(distance=30)
    .set_band_alias(["red", "green", "blue", "nir"])
    .to_tif("processed_image.tif")
)

print(result)
```

## 📖 Examples

### Spectral Index Calculation

```python
from satfarm import SatImage

# Load image and set band aliases
simage = (SatImage()
    .read_tif("multispectral_image.tif")
    .set_band_alias(["blue", "green", "red", "nir"])
)

# Calculate vegetation indices
equations = {
    "NDVI": "(B[4] - B[3]) / (B[4] + B[3])",
    "NDRE": "(B[4] - B[2]) / (B[4] + B[2])",
    "SAVI": "1.5 * (B[4] - B[3]) / (B[4] + B[3] + 0.5)"
}

# Process multiple indices
index_images = list(simage.calculate_index(equations))

for idx_img in index_images:
    print(f"Index: {idx_img.get_band_alias()}")
    stats = idx_img.calculate_band_stats()
    print(f"Statistics: {stats}")
```

### Image Rendering and Visualization

```python
# Render index with custom colormap
rendered = (index_images[0]  # NDVI
    .render_index(vmin=0, vmax=1, cmap="viridis")
    .rescale(0.5)  # Reduce resolution by 50%
    .to_png("ndvi_visualization.png")
)
```

### Image Merging and Analysis

```python
# Merge multiple index images
merged = SatImage().merge(index_images)

# Get image boundary
boundary = merged.get_boundary()

# Calculate comprehensive statistics
stats = merged.calculate_band_stats()
```

## 🏗️ API Reference

### Core Class

#### `SatImage`

The main class providing a fluent interface for satellite image processing.

**Key Methods:**

- **I/O Operations**
  - `read_tif(path)`: Load GeoTIFF files
  - `to_tif(path)`: Save as GeoTIFF
  - `to_png(path)`: Save as PNG

- **Data Manipulation**
  - `change_pixel_dtype(dtype)`: Convert pixel data type
  - `change_nodata(new_nodata, old_nodata)`: Update nodata values
  - `reproject(crs)`: Reproject to different coordinate system
  - `rescale(factor)`: Resize image by scaling factor
  - `shrink(distance)`: Reduce image extent by specified distance

- **Band Operations**
  - `set_band_alias(aliases)`: Assign names to bands
  - `extract_band(bands)`: Select specific bands
  - `apply_scale_factor(factors)`: Apply scaling factors to bands
  - `calculate_index(equations)`: Compute spectral indices

- **Analysis**
  - `calculate_band_stats()`: Compute statistical metrics
  - `get_boundary()`: Extract image boundary geometry

- **Visualization**
  - `render_index(vmin, vmax, cmap)`: Render with color mapping

- **Utilities**
  - `copy()`: Create deep copy
  - `merge(images)`: Combine multiple images
  - `is_empty()`: Check if image data exists

## 🔧 Dependencies

- **numpy** (>=1.21.0): Numerical computing
- **rioxarray** (>=0.13.0): Rasterio integration with xarray
- **geopandas** (>=0.12.0): Geospatial data handling
- **Pillow** (>=9.0.0): Image processing
- **matplotlib** (>=3.5.0): Plotting and visualization
- **typeguard** (>=4.0.0): Runtime type checking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of the excellent [rasterio](https://rasterio.readthedocs.io/) and [xarray](https://xarray.pydata.org/) libraries
- Inspired by modern geospatial processing workflows
- Thanks to the open source geospatial community

## 📞 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/satfarm/issues) on GitHub.