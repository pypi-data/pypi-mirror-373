"""
Basic image operations for satellite image processing.

This module provides fundamental image manipulation operations such as
data type conversion, nodata handling, clipping, reprojection, rescaling,
and band management.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from satfarm.SatImage import SatImage

import geopandas as gpd
import numpy as np
from rasterio.enums import Resampling
from shapely.geometry import Polygon, MultiPolygon
from typing import Self
from typeguard import typechecked


class BasicOpsMixin:
    """
    Mixin class providing basic image operation methods.
    
    This mixin provides fundamental operations for satellite image processing
    including data type conversion, coordinate system transformation, geometric
    operations, and band management. All methods return the modified object
    to enable method chaining.
    """

    @typechecked
    def set_log(self: SatImage, logs: list[dict]):
        """
        Sets the processing log.

        Parameters
        ----------
        logs : list of dict
            A list of dictionaries representing the processing history.

        Returns
        -------
        SatImage
            The modified SatImage object.
        """
        self.log = logs
        return self
    
    @typechecked
    def add_log(self: SatImage, log: dict) -> Self:
        """
        Adds a new entry to the processing log.

        Parameters
        ----------
        log : dict
            A dictionary containing information about the operation to log.

        Returns
        -------
        Self
            The modified SatImage object.
        """
        self.log.append(log)
        return self

    @typechecked
    def change_pixel_dtype(self: SatImage, dtype: str) -> Self:
        """
        Changes the pixel data type of the image.

        Parameters
        ----------
        dtype : str
            The target data type (e.g., 'float32', 'uint16').

        Returns
        -------
        SatImage
            The modified SatImage object.

        Examples
        --------
        >>> simage.change_pixel_dtype('float32')
        """
        if self.image is None:
            raise ValueError("Image is empty")
        self.image = self.image.astype(dtype)
        self.add_log({
            "action": "change_pixel_dtype", 
            "params": {"dtype": dtype}
        })
        return self
    
    @typechecked
    def change_nodata(self: SatImage, new_nodata: float, old_nodata: float | list[float] | None = None) -> Self:
        """
        Changes the nodata value of the image.

        This method updates the image data by replacing old nodata values with a
        new one and sets the new nodata value in the image's metadata.

        Parameters
        ----------
        new_nodata : float
            The new nodata value.
        old_nodata : float or list of float, optional
            The old nodata value(s) to be replaced. If None, the current
            nodata value from the image's metadata is used.

        Returns
        -------
        SatImage
            The modified SatImage object.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        # get aoi
        aoi = np.full_like(self.image.data[0, :, :], True, dtype=bool)
        if not isinstance(old_nodata, list):
            old_nodata = [old_nodata]
        for val in old_nodata:
            if val is None:
                val = self.image.rio.nodata
            if np.isnan(val):
                aoi = np.logical_and(aoi, ~np.isnan(self.image.data[0, :, :]))
            else:
                aoi = np.logical_and(aoi, self.image.data[0, :, :] != val)
        # change nodata
        self.image.data[:, ~aoi] = new_nodata
        self.image.rio.write_nodata(new_nodata, inplace=True)
        self.add_log({
            "action": "change_nodata", 
            "params": {"new_nodata": new_nodata, "old_nodata": old_nodata}
        })
        return self
    
    @typechecked
    def clip(self: SatImage, boundary: Polygon | MultiPolygon) -> Self:
        """
        Clips the image to a given geometric boundary.
        
        This method crops the image to the extent of the provided geometry,
        retaining only pixels that intersect with the boundary.
        
        Parameters
        ----------
        boundary : Polygon or MultiPolygon
            The geometric boundary to clip the image to
            
        Returns
        -------
        SatImage
            The clipped SatImage object
            
        Raises
        ------
        ValueError
            If the image is empty
        """
        # input check
        if self.image is None:
            raise ValueError("Image is empty")
        # clip
        params = dict(
            geometries=[boundary],
            all_touched=False, 
            drop=True, 
            invert=False, 
            from_disk=False
        )
        self.image = self.image.rio.clip(**params)
        self.add_log({
            "action": "clip", 
            "params": {"boundary": boundary}
        })
        return self
    
    @typechecked
    def shrink(self: SatImage, distance: float) -> Self:
        """
        Shrinks the image boundary by a specified distance.
        
        This method reduces the image extent by buffering the current boundary
        inward by the specified distance. The operation is performed in an
        appropriate UTM coordinate system for accurate distance calculations.
        
        Parameters
        ----------
        distance : float
            The distance in meters to shrink the boundary inward
            
        Returns
        -------
        SatImage
            The shrunk SatImage object
            
        Raises
        ------
        ValueError
            If the image is empty or distance is not positive
        """
        # input check
        if self.image is None:
            raise ValueError("Image is empty")
        if distance <= 0:
            raise ValueError("distance should be positive")
        # get boundary
        boundary = self.get_boundary()
        # find utm zone
        centroid = boundary.centroid
        zone_number = int((np.floor((centroid.x + 180) / 6) % 60) + 1)
        if centroid.y >= 0:
            utm_epsg_code = f"EPSG:{32600 + zone_number}"
        else:
            utm_epsg_code = f"EPSG:{32700 + zone_number}"
        # shrink boundary
        shrinked_boundary = (
            gpd.GeoSeries([boundary], crs='EPSG:4326')
            .to_crs(utm_epsg_code)
            .buffer(-distance)
            .to_crs("EPSG:4326")
            .iloc[0]
        )
        # clip
        self.clip(shrinked_boundary)
        self.add_log({
            "action": "shrink", 
            "params": {"distance": distance}
        })
        return self

    @typechecked
    def reproject(self: SatImage, crs: str) -> Self:
        """
        Reprojects the image to a new CRS.

        Parameters
        ----------
        crs : float
            The new CRS to reproject the image to.

        Returns
        -------
        SatImage
            The reprojected SatImage object.
        """
        # input check
        if self.image is None:
            raise ValueError("Image is empty")
        if crs[:4] != "EPSG":
            raise ValueError("crs should be a string starting with 'EPSG:'")
        # reproject
        self.image = self.image.rio.reproject(crs)
        self.add_log({
            "action": "reproject", 
            "params": {"crs": crs}
        })
        return self

    @typechecked
    def rescale(self: SatImage, rescale: float, resampling: str = "bilinear") -> Self:
        """
        Rescales the image by a given factor.

        This method changes the image's resolution by adjusting its width and
        height according to the rescale factor.

        Parameters
        ----------
        rescale : float
            The factor to rescale the image. A value > 1 downsamples,
            and a value < 1 upsamples. The factor is multiplied to the pixel size.
        resampling : str, default 'bilinear'
            The resampling method to use. See `rasterio.enums.Resampling`
            for available options (e.g., 'nearest', 'cubic').

        Returns
        -------
        SatImage
            The rescaled SatImage object.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        # input check
        if rescale == 1:
            return self
        if resampling not in Resampling.__members__:
            raise ValueError(f"resampling should be one of {list(Resampling.__members__.keys())}")
        # resize pixel size
        new_width = int(np.ceil(self.image.rio.width / rescale))
        new_height = int(np.ceil(self.image.rio.height / rescale))
        new_shape = (new_height, new_width)
        rmethod = getattr(Resampling, resampling)
        self.image = self.image.rio.reproject(self.image.rio.crs, shape=new_shape, resampling=rmethod)
        self.add_log({
            "action": "rescale", 
            "params": {"rescale": rescale, "resampling": resampling}
        })
        return self
    
    @typechecked
    def reset_band_alias(self: SatImage) -> Self:
        """
        Resets band aliases to default numbered format (e.g., 'B1', 'B2', ...).

        Returns
        -------
        SatImage
            The modified SatImage object.
        
        Examples
        --------
        >>> simage.set_band_alias(['red', 'nir'])
        >>> simage.reset_band_alias()
        >>> simage.get_band_alias()
        ['B1', 'B2']
        """
        if self.image is None:
            raise ValueError("Image is empty")
        nbands = self.image.sizes.get("band")
        original_bands = [f"B{bi+1}" for bi in range(nbands)]
        self.image = self.image.assign_coords(band=original_bands)
        self.add_log({
            "action": "reset_band_alias"
        })
        return self
    
    @typechecked
    def set_band_alias(self: SatImage, alias: list[str]) -> Self:
        """
        Sets the aliases (names) for the image bands.

        Parameters
        ----------
        alias : list of str
            A list of names for the bands. The length of the list must match
            the number of bands in the image.

        Returns
        -------
        SatImage
            The modified SatImage object.

        Raises
        ------
        ValueError
            If the length of the alias list does not match the number of bands.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        # check input
        nbands = self.image.sizes.get("band")
        if len(alias) != nbands:
            raise ValueError(f"alias list must have {nbands} elements")
        # change band name
        self.image = self.image.assign_coords(band=alias)
        self.add_log({
            "action": "set_band_alias", 
            "params": {"alias": alias}
        })
        return self
    
