"""
Image attribute access and metadata operations.

This module provides methods for accessing various properties and attributes
of satellite images, including band information, spatial properties,
boundaries, and area of interest calculations.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from satfarm.SatImage import SatImage

import numpy as np
import rasterio as rio
import xarray as xr
from shapely.geometry import Polygon, MultiPolygon, shape
from typeguard import typechecked
from datetime import datetime
from typing import Self

class AttributesMixin:
    """
    Mixin class providing image attribute access methods.
    
    This mixin provides methods to query and access various properties
    of satellite images including band information, spatial boundaries,
    data validity masks, and underlying image data structures.
    """

    @typechecked
    def set_alias(self, alias: str) -> Self:
        """
        Sets the alias attribute of the image.

        Parameters
        ----------
        alias : str
            The alias to set for the image.

        Returns
        -------
        SatImage
            The modified SatImage object.
        """
        self.alias = alias
        return self
    
    @typechecked
    def set_time(self, time: datetime | None) -> Self:
        """
        Sets the time attribute of the image.

        Parameters
        ----------
        time : datetime
            The time to set for the image.

        Returns
        -------
        SatImage
            The modified SatImage object.
        """
        self.time = time
        return self

    @typechecked
    def is_empty(self: SatImage) -> bool:
        """
        Checks if the SatImage object contains an image.

        Returns
        -------
        bool
            True if the image is None, False otherwise.
        
        Examples
        --------
        >>> simage = SatImage()
        >>> simage.is_empty()
        True
        """
        return self.image is None
    
    @typechecked
    def get_band_alias(self: SatImage) -> list[str]:
        """
        Gets the band aliases (names) of the image.

        Returns
        -------
        list of str
            A list containing the alias for each band.

        Examples
        --------
        >>> simage.set_band_alias(['red', 'green', 'blue'])
        >>> simage.get_band_alias()
        ['red', 'green', 'blue']
        """
        if self.image is None:
            raise ValueError("Image is empty")
        return [f"{ba}" for ba in self.image.band.values]
    
    @typechecked
    def get_image(self: SatImage) -> xr.DataArray:
        """
        Returns the underlying xarray.DataArray of the image.

        Returns
        -------
        xarray.DataArray
            The image data.
            
        Raises
        ------
        ValueError
            If the image is empty.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        return self.image

    @typechecked
    def get_aoi(self: SatImage) -> np.ndarray:
        """
        Gets the Area of Interest (AOI) as a boolean mask.

        The AOI is determined by pixels that are not `nodata` values.

        Returns
        -------
        numpy.ndarray
            A boolean array where True represents valid data pixels.
            
        Raises
        ------
        ValueError
            If the image is empty.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        if self.image.rio.nodata is None:
            aoi = np.full_like(self.image.data[0, :, :], True, dtype=bool)
        elif np.isnan(self.image.rio.nodata):
            aoi = ~np.isnan(self.image.data[0, :, :])
        else:
            aoi = self.image.data[0, :, :] != self.image.rio.nodata
        return aoi
    
    @typechecked
    def get_boundary(self: SatImage) -> Polygon | MultiPolygon:
        """
        Gets the boundary geometry of the image's valid data area.
        
        This method extracts the boundary of non-nodata pixels in the image
        and returns it as a geometric shape. The boundary represents the
        actual data extent, which may be smaller than the full raster extent
        if nodata values are present.
        
        Returns
        -------
        Polygon or MultiPolygon
            The boundary geometry of the valid data area in the image's CRS
            
        Raises
        ------
        ValueError
            If the image is empty
        """
        # input check
        if self.image is None:
            raise ValueError("Image is empty")
        # overhead
        aoi = self.get_aoi()
        data = aoi.astype("uint8")
        transform = self.image.rio.transform()
        # extract polygon
        polygons = []
        for geom, val in rio.features.shapes(data, mask=aoi, transform=transform):
            if not np.isnan(val):
                polygons.append(shape(geom))
        # return
        return MultiPolygon(polygons)
