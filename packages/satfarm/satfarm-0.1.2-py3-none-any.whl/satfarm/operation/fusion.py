"""
Utilities for fusing or interpolating `SatImage` instances over time.

This module currently provides functionality to generate time-interpolated
images by leveraging per-band summary statistics across a sequence of
'SatImage' objects. The interpolation estimates a target image's band values
by adjusting a reference image using the interpolated mean values per band.
"""

import rioxarray as rxr
import pandas as pd
import numpy as np
from satfarm import SatImage
from datetime import datetime

def interp_image(simages: list[SatImage], 
               time: datetime | list[datetime]
               ) -> list[SatImage]:
    """
    Interpolate `SatImage` objects to one or more target timestamps.

    The method performs a simple time interpolation based on per-band mean
    statistics. It computes the mean for each band across the input images,
    linearly interpolates those means to the requested timestamps, and then
    adjusts a reference image (the most recent input image) so its band values
    reflect the interpolated means while preserving the spatial patterns.

    Parameters
    ----------
    simages : list of SatImage
        Input images with valid `time`, identical band aliases, and identical
        pixel data types. Images are internally sorted by `time`.
    time : datetime or list of datetime
        Target timestamp(s) to interpolate to. If a single `datetime` is
        provided, it is promoted to a list.

    Returns
    -------
    list of SatImage
        New images corresponding to the requested timestamps. Each image is a
        copy of the most recent input image, with its per-band values adjusted
        to match the interpolated per-band means.

    Raises
    ------
    ValueError
        If band aliases differ across inputs, if dtypes differ, or if any input
        image is missing its `time` attribute.

    Notes
    -----
    - Interpolation is performed using `numpy.interp` on per-band mean values.
    - Spatial structure is preserved by applying a uniform offset within the
      area of interest (non-nodata pixels) for each band.
    - The last image (latest `time`) is used as the spatial reference.
    """
    # sort by time
    simages = sorted(simages, key=lambda simage: simage.time)
    # input check
    band_alias_list = [simage.image.band.values.tolist() for simage in simages]
    dtype_list = [simage.image.dtype for simage in simages]
    stime_list = [simage.time for simage in simages]
    if len(set([str(ba) for ba in band_alias_list])) != 1:
        raise ValueError("All images must have the same band alias")
    if len(set(dtype_list)) != 1:
        raise ValueError("All images must have the same data type")
    if None in stime_list:
        raise ValueError("All images must have time property")
    # normalize input types
    if isinstance(time, datetime):
        time = [time]
    band_alias_list = band_alias_list[0]
    pixel_dtype = dtype_list[0]
    # calculate per-image, per-band mean statistics for interpolation
    rows = []
    for simage in simages:
        row = dict()
        row["time"] = simage.time
        row["timestamp"] = simage.time.timestamp()
        stats = simage.calculate_band_stats()
        for band_alias in band_alias_list:
            rvalue = stats[band_alias]["mean"]
            row[band_alias] = rvalue
        rows.append(row)
    ref_df = pd.DataFrame(rows)
    # interpolate per-band means to the requested timestamps
    rows = []
    for t in time:
        row = dict()
        row["time"] = t
        row["timestamp"] = t.timestamp()
        for band_alias in band_alias_list:
            pred_rvalue = np.interp(x=row["timestamp"], xp=ref_df["timestamp"], fp=ref_df[band_alias])
            row[band_alias] = pred_rvalue
        rows.append(row)
    dst_df = pd.DataFrame(rows)
    # create new images by adjusting the latest image to match interpolated means
    base_image = simages[-1] # use most recent image as spatial reference
    base_row = ref_df.iloc[-1]
    intp_images = []
    for _, dst_row in dst_df.iterrows():
        intp_image = base_image.copy()
        intp_image.time = dst_row["time"]
        for band_alias in band_alias_list:
            value_arr = intp_image.image.sel(band=band_alias).data
            # update only valid pixels within the area of interest (non-nodata)
            aoi = (value_arr != intp_image.image.rio.nodata)
            value_arr[aoi] = (
                value_arr[aoi]
                + dst_row[band_alias] 
                - base_row[band_alias]
            )
            value_arr = value_arr.astype(pixel_dtype)
            intp_image.image.sel(band=band_alias).data = value_arr
        
        intp_images.append(intp_image)
    # return
    return intp_images
