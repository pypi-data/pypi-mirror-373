import numpy as np
import xarray as xr
from typeguard import typechecked
from datetime import datetime
from pprint import pprint
from typing import Self

from satfarm.processor._advanced_ops import AdvancedOpsMixin
from satfarm.processor._attributes import AttributesMixin
from satfarm.processor._basic_ops import BasicOpsMixin
from satfarm.processor._export import ExportMixin
from satfarm.processor._io import IOMixin
from satfarm.processor._rendering import RenderingMixin


class SatImage(
    IOMixin,
    AttributesMixin,
    BasicOpsMixin,
    AdvancedOpsMixin,
    RenderingMixin,
    ExportMixin,
):
    """
    A class for processing satellite imagery using rasterio and xarray.

    This class provides a fluent interface for chaining image processing operations.
    It handles various tasks such as reading/writing raster data, reprojection,
    resampling, band calculations, and rendering.

    Attributes
    ----------
    image : xarray.DataArray or None
        The raster data stored as an xarray DataArray with dimensions ('band', 'y', 'x').
    log : list of dict
        A log of operations performed on the image.
    """

    ################################################################################
    # init
    ################################################################################
    @typechecked
    def __init__(self):
        """Initializes an empty SatImage object.

        Examples
        --------
        >>> simage = SatImage()
        >>> simage.is_empty()
        True
        """
        self.image = None
        self.time = None
        self.alias = ""
        self.log = [{"action": "initialize"}]
    
    def __str__(self):
        if self.image is None:
            return "SatImage(Empty)"
        time_str = "0000-00-00 00:00:00" if self.time is None else self.time.strftime('%Y-%m-%d %H:%M:%S')
        info = [
            f"time={time_str}",
            f"alias={self.alias}",
            f"shape={self.image.shape[1:]}", 
            f"dtype={self.image.dtype}",
            f"nodata={self.image.rio.nodata}", 
            f"crs={self.image.rio.crs}",
            f"bands={self.image.band.values}", 
        ]
        return f"SatImage({', '.join(info)})"
    
    def __repr__(self):
        return self.__str__()
    
    @typechecked
    def check_image_format(self, raise_error: bool = False) -> bool:
        """
        Checks if the image format is valid.

        The validation checks for three conditions:
        1. The image is an instance of `xarray.DataArray`.
        2. The dimensions are in the order ('band', 'y', 'x').
        3. A Coordinate Reference System (CRS) is defined.

        Parameters
        ----------
        raise_error : bool, default False
            If True, raises a ValueError if the image format is not valid.

        Returns
        -------
        bool
            True if the image format is valid, False otherwise.

        Raises
        ------
        ValueError
            If `raise_error` is True and the image format is invalid.
        """
        check_info = {}
        check_info["is_xarray"] = ( isinstance(self.image, xr.DataArray) )
        check_info["dimension_order"] = ( self.image.dims == ("band", "y", "x") )
        check_info["crs_defined"] = ( self.image.rio.crs is not None )
        if all(check_info.values()):
            return True
        if raise_error:
            raise ValueError(f"Image format is not valid: {check_info}")
        return False
    

