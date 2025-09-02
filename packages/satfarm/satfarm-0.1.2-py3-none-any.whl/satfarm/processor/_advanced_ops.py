"""
Advanced image processing operations for satellite imagery.

This module provides advanced operations including scale factor application,
spectral index calculations, statistical analysis, and backbone generation
for creating template images with matching spatial properties.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from satfarm.SatImage import SatImage

import numpy as np
import xarray as xr
from numpy import sqrt
from typing import Iterator, Self
from typeguard import typechecked


class AdvancedOpsMixin:
    """
    Mixin class providing advanced image processing operations.
    
    This mixin includes methods for sophisticated image analysis and processing
    such as spectral index calculations, statistical analysis, scale factor
    applications, and template image generation. These operations are typically
    used for scientific analysis of satellite imagery.
    """

    @typechecked
    def apply_scale_factor(self: SatImage, scale_factor: dict[str, float]) -> Self:
        """
        Applies a scale factor to specified image bands.

        Parameters
        ----------
        scale_factor : dict of str to float
            A dictionary where keys are band aliases (str) and values are the
            scale factors to apply.

        Returns
        -------
        SatImage
            The modified SatImage object.

        Raises
        ------
        ValueError
            If any band alias in the dictionary does not exist in the image.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        
        current_aliases = self.get_band_alias()
        for alias, sf in scale_factor.items():
            if alias not in current_aliases:
                raise ValueError(f"Band alias '{alias}' not found in image.")
            self.image.loc[dict(band=alias)] *= sf
        self.add_log({
            "action": "apply_scale_factor", 
            "params": {"scale_factor": scale_factor}
        })
        return self
    
    @typechecked
    def add_noise(self, scale: float=0.01):
        aoi = self.get_aoi()
        if self.image is None:
            raise ValueError("Image is empty")
        h, w = self.image.data[0].shape
        noise = np.random.normal(loc=0, scale=scale, size=(h, w))
        self.image.data[:, aoi] += noise[aoi]
        return self
    
    @typechecked
    def generate_backbone(self: SatImage, nbands: int=0, pixel_dtype: str="float32", fill_value: float=0, nodata: float=np.nan) -> SatImage:
        """
        Generates a new SatImage with the same spatial properties but new data.

        This creates a "backbone" or template image with the same dimensions,
        CRS, and transform as the current image, but filled with a specified value.

        Parameters
        ----------
        nbands : int, optional
            Number of bands for the new image. If 0, uses the same number of
            bands as the current image.
        pixel_dtype : str, default 'float32'
            Data type for the new image.
        fill_value : float, default 0
            Value to fill the new image data with.
        nodata : float, default numpy.nan
            Nodata value for the new image.

        Returns
        -------
        SatImage
            A new SatImage object serving as a backbone.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        # check input
        if nbands == 0:
            nbands = self.image.sizes.get("band")
        # generate backbone
        ds = xr.Dataset()
        for bi in range(nbands):
            ds[f"{bi+1}"] = xr.DataArray(
                data=np.full(shape=self.image[0].data.shape, fill_value=fill_value, dtype=pixel_dtype),
                dims=("y", "x"), 
                coords={"y": self.image.y, "x": self.image.x}
            )
        backbone = ds.rio.write_crs(self.image.rio.crs)
        backbone = backbone.to_array(dim="band")
        backbone.rio.write_nodata(nodata, inplace=True)
        # generate backbone image
        from satfarm.SatImage import SatImage
        backbone_image = (
            SatImage()
            .read_tif(backbone)
            .set_log(self.log)
            .add_log({"action": "generate_backbone", "params": {
                "nbands": nbands, 
                "pixel_dtype": pixel_dtype, 
                "fill_value": fill_value, 
                "nodata": nodata
            }})
        )
        return backbone_image
    
    @typechecked
    def calculate_index(self: SatImage, equation: dict[str, str]) -> Iterator[SatImage]:
        """
        Calculates one or more spectral indices using user-defined equations.

        This method evaluates mathematical expressions for each index and yields
        a new single-band SatImage for each result.

        Parameters
        ----------
        equation : dict of str to str
            A dictionary where keys are the names for the output indices (band aliases)
            and values are the mathematical equations as strings.
            Band numbers in equations must be 1-based and enclosed in brackets,
            e.g., `(B[4] - B[3]) / (B[4] + B[3])` for NDVI.

        Yields
        ------
        Iterator[SatImage]
            An iterator of single-band SatImage objects, one for each calculated index.
        
        Examples
        --------
        >>> equations = {
        ...     "NDVI": "(B[4] - B[3]) / (B[4] + B[3])",
        ...     "NDWI": "(B[3] - B[8]) / (B[3] + B[8])"
        ... }
        >>> # Assuming B8 is nir and B4 is red, B3 is green
        >>> simage.set_band_alias(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'])
        >>> for index_image in simage.calculate_index(equations):
        ...     print(index_image.get_band_alias())
        """
        if self.image is None:
            raise ValueError("Image is empty")
        nbands = self.image.sizes.get("band")
        B = {bi+1: self.image.data[bi, :, :] for bi in range(nbands)}
        for alias, eq in equation.items():
            simg = self.generate_backbone(nbands=1, pixel_dtype="float32", fill_value=np.nan, nodata=np.nan)
            simg.image.data[0,:,:] = eval(eq)
            simg.add_log({
                "action": "calculate_index", 
                "params": {"alias": alias, "equation": eq}
            })
            simg.set_band_alias([alias])
            yield simg
    
    @typechecked
    def calculate_band_stats(self: SatImage, digits: int = 3) -> dict[str, dict[str, float]]:
        """
        Calculates summary statistics for each band of the image.

        Statistics include count, mean, standard deviation, min, max, and
        quartiles (25%, 50%, 75%).

        Parameters
        ----------
        digits : int, default 3
            The number of decimal places to round the statistics to.

        Returns
        -------
        dict
            A nested dictionary where outer keys are band aliases and inner keys
            are statistic names.
        """
        if self.image is None:
            raise ValueError("Image is empty")
        stats = {}
        for alias in self.get_band_alias():
            aoi = self.get_aoi()
            band_arr = self.image.sel(band=alias).data
            band_pix = band_arr[aoi]
            stats[alias] = {
                "count": int(np.sum(aoi)),
                "mean": round(float(np.mean(band_pix)), digits),
                "std": round(float(np.std(band_pix)), digits),
                "min": round(float(np.min(band_pix)), digits),
                "25%": round(float(np.percentile(band_pix, 25)), digits),
                "50%": round(float(np.median(band_pix)), digits),
                "75%": round(float(np.percentile(band_pix, 75)), digits),
                "max": round(float(np.max(band_pix)), digits)
            }
        
        return stats
