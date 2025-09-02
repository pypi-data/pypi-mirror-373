"""
Image rendering and visualization operations.

This module provides methods for converting single-band images (typically
spectral indices) into colored RGBA visualizations using matplotlib colormaps.
The rendering operations are designed for creating publication-ready
visualizations of satellite imagery analysis results.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from satfarm.SatImage import SatImage

import numpy as np
import matplotlib.colors as mcolors
from matplotlib import colormaps
from typeguard import typechecked


class RenderingMixin:
    """
    Mixin class providing image rendering and visualization methods.
    
    This mixin provides functionality to convert single-band images into
    colored RGBA visualizations using matplotlib colormaps. This is particularly
    useful for visualizing spectral indices and other analysis results.
    """

    @typechecked
    def render_index(self: SatImage, vmin: float, vmax: float, 
                     cmap: str | mcolors.Colormap) -> SatImage:
        """
        Renders a single-band image as a colored RGBA image.

        This is typically used for visualizing spectral indices. The input image
        must have only one band.

        Parameters
        ----------
        vmin : float
            The minimum value for the color scale normalization.
        vmax : float
            The maximum value for the color scale normalization.
        cmap : str or matplotlib.colors.Colormap
            The colormap to use for rendering.

        Returns
        -------
        SatImage
            A new 4-band (RGBA) SatImage object of type 'uint8'.

        Raises
        ------
        ValueError
            If the input image does not have exactly one band, or if `vmin` > `vmax`.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        # check input
        if len(self.image.band.values) != 1:
            raise ValueError(f"image should have only one band")
        if vmin > vmax:
            raise ValueError(f"vmin should be less than vmax")
        if isinstance(cmap, str):
            cmap = colormaps.get_cmap(cmap)
        # preprocess data
        aoi = self.get_aoi()
        # normalize raw data
        arr = self.image.isel(band=0).data
        arr = (arr - vmin) / (vmax - vmin)
        arr = np.clip(arr, 0, 1)
        carr = (255 * cmap(arr)).astype(np.uint8)
        carr = carr.transpose(2, 0, 1)
        carr[3, ~aoi] = 0
        # generate rgba image
        rgba = self.generate_backbone(nbands=4, pixel_dtype="uint8", fill_value=0, nodata=0)
        rgba.image.data = carr
        rgba.add_log({
            "action": "render_index", 
            "params": {
                "vmin": vmin, 
                "vmax": vmax, 
                "cmap": cmap.name if isinstance(cmap, mcolors.Colormap) else cmap
            }
        })
        rgba.set_band_alias(["R", "G", "B", "A"])
        # return
        return rgba
