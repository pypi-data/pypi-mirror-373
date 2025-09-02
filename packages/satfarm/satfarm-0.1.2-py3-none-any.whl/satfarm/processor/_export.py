"""
Data export and copying operations.

This module provides methods for exporting satellite images to various formats
including GeoTIFF and PNG, creating copies of images, and extracting specific
bands. It supports both file-based and in-memory (BytesIO) export operations.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from satfarm.SatImage import SatImage

import numpy as np
import rasterio as rio
from io import BytesIO
from pathlib import Path
from PIL import Image
from typing import Self
from typeguard import typechecked


class ExportMixin:
    """
    Mixin class providing data export and copying methods.
    
    This mixin includes functionality for exporting images to various formats,
    creating deep copies of image objects, extracting specific bands, and
    converting images to different output formats including GeoTIFF and PNG.
    """

    @typechecked
    def copy(self: SatImage) -> Self:
        """
        Creates a deep copy of the SatImage object.

        Returns
        -------
        SatImage
            A new SatImage instance with a copy of the image data.
        """
        from satfarm.SatImage import SatImage
        if self.image is None:
            raise ValueError("Image is empty")
        new_simage = (
            SatImage()
            .read_tif(self.image.copy())
            .set_log(self.log.copy())
            .set_alias(self.alias)
            .set_time(self.time)
            .add_log({"action": "copy"})
        )
        return new_simage
    
    @typechecked
    def extract_band(self: SatImage, bands: list[str]) -> Self:
        """
        Extracts a subset of bands from the image.

        Parameters
        ----------
        bands : list of str
            A list of band aliases to extract.

        Returns
        -------
        SatImage
            A new SatImage object containing only the specified bands.
        
        Examples
        --------
        >>> simage.get_band_alias()
        ['B1', 'B2', 'B3', 'B4']
        >>> new_simage = simage.extract_band(['B4', 'B3', 'B2'])
        >>> new_simage.get_band_alias()
        ['B4', 'B3', 'B2']
        """
        from satfarm.SatImage import SatImage
        if self.image is None:
            raise ValueError("Image is empty")
        sel = self.image.sel(band=bands)
        new_simage = (
            SatImage()
            .read_tif(sel)
            .set_log(self.log.copy())
            .set_alias(self.alias)
            .set_time(self.time)
            .add_log({"action": "extract_band", "params": {"bands": bands}})
        )
        return new_simage
    
    @typechecked
    def to_png_bytesio(self: SatImage) -> BytesIO:
        """
        Converts a 4-band (RGBA) image to a PNG byte stream.

        The input image must have 4 bands (R, G, B, A) and a 'uint8' data type.

        Returns
        -------
        io.BytesIO
            A byte stream containing the PNG image data.

        Raises
        ------
        ValueError
            If the image does not have 4 bands or is not of 'uint8' type.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        # check input
        if self.image.data.shape[0] != 4:
            raise ValueError(f"Image should have 4 bands for RGBA mode")
        if self.image.data.dtype != np.uint8:
            raise ValueError(f"Image should have uint8 dtype for PNG mode")
        # convert to rgba array
        rgba_array = np.transpose(self.image.data, (1, 2, 0))
        image = Image.fromarray(rgba_array, mode='RGBA')
        # save to bytesio
        bio = BytesIO()
        image.save(bio, format='PNG')
        bio.seek(0)
        # return
        return bio

    @typechecked
    def to_png(self: SatImage, path: str | Path) -> Self:
        """
        Saves the image as a PNG file.

        Parameters
        ----------
        path : str or Path
            The path to save the PNG file.

        Returns
        -------
        Self
            The modified SatImage object.
        """
        bio = self.to_png_bytesio()
        with open(path, "wb") as f:
            f.write(bio.getvalue())
        return self
    
    @typechecked
    def to_tif_bytesio(self: SatImage, format: str = "GTiff", compress: str = "lzw", predictor: int = 1) -> BytesIO:
        """
        Converts the image to a GeoTIFF byte stream.

        This method uses rasterio to write the image data, including CRS and
        transform information, into an in-memory file.

        Parameters
        ----------
        format : str, default 'GTiff'
            The rasterio driver to use for writing.
        compress : str, default 'lzw'
            The compression method.
        predictor : int, default 1
            The predictor for compression (if applicable).

        Returns
        -------
        io.BytesIO
            A byte stream containing the GeoTIFF image data.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        # set save parameters
        open_params = dict(
            driver=format, 
            height=self.image.rio.height, 
            width=self.image.rio.width, 
            count=self.image.data.shape[0], 
            dtype=self.image.dtype, 
            nodata=self.image.rio.nodata,
            crs=self.image.rio.crs,
            compress=compress,
            predictor=predictor, 
            transform=self.image.rio.transform()
        )
        # save
        band_alias = self.image.band.values
        with rio.io.MemoryFile() as memfile:
            with memfile.open(**open_params) as dst:
                for bi, ba in enumerate(band_alias):
                    dst.set_band_description(bi + 1, ba)
                dst.write(self.image.data)
            bio = BytesIO(memfile.read())
            bio.seek(0)
        return bio

    @typechecked
    def to_tif(self: SatImage, path: str | Path) -> Self:
        """
        Saves the image as a GeoTIFF file.

        Parameters
        ----------
        path : str or Path
            The path to save the GeoTIFF file.

        Returns
        -------
        Self
            The modified SatImage object.
        """
        bio = self.to_tif_bytesio()
        with open(path, "wb") as f:
            f.write(bio.getvalue())
        return self
