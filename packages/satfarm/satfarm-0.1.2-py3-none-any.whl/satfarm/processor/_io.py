"""
Input/output operations for satellite images.

This module provides methods for reading raster data from various sources
and merging multiple images. It supports reading from file paths, BytesIO
objects, and existing xarray DataArrays, as well as combining multiple
SatImage objects into a single merged image.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from satfarm.SatImage import SatImage

import numpy as np
import rioxarray as rxr
import xarray as xr
from io import BytesIO
from pathlib import Path
from typing import Self
from typeguard import typechecked


class IOMixin:
    """
    Mixin class providing input/output operations.
    
    This mixin handles reading raster data from various sources including
    files, in-memory objects, and existing DataArrays. It also provides
    functionality for merging multiple satellite images into a single
    multi-band image with proper spatial alignment.
    """
    
    @typechecked
    def read_tif(self: SatImage, file: str | Path | BytesIO | xr.DataArray) -> Self:
        """
        Reads a raster file into the SatImage object.

        The input can be a file path, a BytesIO object, or an existing
        xarray.DataArray.

        Parameters
        ----------
        file : str, Path, BytesIO, or xarray.DataArray
            The input raster data to read.

        Returns
        -------
        Self
            The SatImage instance with the loaded image.
            
        Raises
        ------
        ValueError
            If the input `file` has an invalid type.
        """
        # read or set image
        if isinstance(file, (str, Path)):
            self.image = rxr.open_rasterio(file)
            self.log.append({"action": "read_tif", "file": str(file)})
        elif isinstance(file, BytesIO):
            self.image = rxr.open_rasterio(file)
            self.log.append({"action": "read_tif", "file": "bytesio object"})
        elif isinstance(file, xr.DataArray):
            self.image = file
            self.log.append({"action": "read_tif", "file": "rioxarray object"})
        else:
            raise ValueError(f"Invalid path type: {type(file)}")
        # check image format
        self.check_image_format(raise_error=True)
        return self
    
    @typechecked
    def merge(self: SatImage, 
              satimages: list[SatImage], 
              backbone: xr.DataArray | None = None, 
              dtype: str = "float32", 
              nodata: float = np.nan) -> Self:
        """
        Merges multiple SatImage objects into the current object.

        Bands from all images are combined. If a `backbone` is provided, all
        images are reprojected to match its grid before merging. The operation
        modifies the current object in-place.

        Parameters
        ----------
        satimages : list of SatImage
            A list of SatImage objects to merge.
        backbone : xarray.DataArray, optional
            A template DataArray to match the projection and resolution.
        dtype : str, default 'float32'
            The data type for the merged image.
        nodata : float, default numpy.nan
            The nodata value for the merged image.

        Returns
        -------
        SatImage
            The modified SatImage object containing the merged data.

        Raises
        ------
        ValueError
            If band aliases are not unique across the images to be merged.
        """
        from satfarm.SatImage import SatImage
        # check input
        images = [si.get_image() for si in satimages if not si.is_empty()]
        if len(images) == 0:
            return SatImage()
        if len(images) == 1:
            return images[0]
        if backbone is None:
            backbone = images[0]
        # merge images
        band_alias = []
        ds = xr.Dataset()
        for image in images:
            image = image.rio.reproject_match(backbone)
            for bi, alias in enumerate(image.band.values):
                if alias in band_alias:
                    raise ValueError(f"Band alias '{alias}' not unique")
                band_alias.append(f"{alias}")
                ds[alias] = image.isel(band=bi).astype(dtype)
        # as array
        merged = ds.to_array(dim="band")
        merged.rio.write_crs(backbone.rio.crs)
        merged.rio.write_transform(backbone.rio.transform())
        merged.rio.write_nodata(nodata)
        self.image = merged
        self.set_band_alias(band_alias)
        # log
        self.log.append({
            "action": "merge", 
            "params": {
                "satimages": [si.log for si in satimages],
                "backbone": type(backbone), 
                "dtype": dtype,
                "nodata": nodata,
            }
        })
        # return
        return self
