"""
Utility functions for the satfarm package.

This module contains helper functions for logging, UUID generation, 
geometry hashing, and various constants used throughout the package.
"""

import json
from datetime import datetime
from hashlib import sha256 as hashlib_sha256
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import numpy as np
import shapely
from dotenv import load_dotenv
from shapely.geometry import MultiPolygon, Polygon, shape
from typeguard import typechecked

load_dotenv()


# constants
DEFAULT_IMAGE_CRS = "EPSG:4326"
DEFAULT_IMAGE_NAN_VALUE = np.nan
DEFAULT_IMAGE_FORMAT = "GTiff"


@typechecked
def log_pipeline(msg: str):
    """
    Print a timestamped log message with UTC time.
    
    The timestamp is displayed with millisecond precision in ISO 8601 format.
    
    Parameters
    ----------
    msg : str
        The log message to output
        
    Examples
    --------
    >>> log_pipeline("Processing started")
    [2024-01-15T10:30:45.123Z] Processing started
    """
    dt = datetime.now(tz=ZoneInfo("UTC"))
    dt = dt.replace(microsecond=(dt.microsecond // 10000) * 10000)
    dts = dt.isoformat(timespec='milliseconds')
    print(f"[{dts}] {msg}", flush=True)


@typechecked
def gen_uuid4() -> str:
    """
    Generate a UUID4 string.
    
    Returns a randomly generated UUID4 format unique identifier as a string.
    
    Returns
    -------
    str
        A UUID4 format string (e.g., "550e8400-e29b-41d4-a716-446655440000")
        
    Examples
    --------
    >>> uuid_str = gen_uuid4()
    >>> print(len(uuid_str))
    36
    >>> is_uuid4(uuid_str)
    True
    """
    return str(uuid4())


@typechecked
def is_uuid4(s: str) -> bool:
    """
    Check if the given string is a valid UUID4.
    
    This function validates that the input string conforms to the UUID4 format
    and version specification.
    
    Parameters
    ----------
    s : str
        The string to validate as a UUID4
        
    Returns
    -------
    bool
        True if the string is a valid UUID4, False otherwise
        
    Examples
    --------
    >>> is_uuid4("550e8400-e29b-41d4-a716-446655440000")
    True
    >>> is_uuid4("invalid-uuid")
    False
    >>> is_uuid4("550e8400-e29b-31d4-a716-446655440000")  # UUID version 3, not 4
    False
    """
    try:
        val = UUID(s, version=4)
    except (ValueError, AttributeError, TypeError):
        return False
    # uuid.UUID allows any valid UUID, so we must check version explicitly
    return str(val) == s and val.version == 4


def gen_geojson_hash(geojson: dict, grid_size: float = 1e-8):
    """
    Generate a unique hash string for a GeoJSON geometry.
    
    This function converts a GeoJSON geometry to a deterministic hash string
    by normalizing the geometry coordinates to a specified grid precision
    and then computing a SHA-256 hash of the normalized geometry.
    
    Parameters
    ----------
    geojson : dict
        A GeoJSON geometry dictionary (must be a Polygon or MultiPolygon)
    grid_size : float, default 1e-8
        The precision grid size for coordinate normalization
        
    Returns
    -------
    str
        A hexadecimal SHA-256 hash string of the normalized geometry
        
    Raises
    ------
    ValueError
        If the GeoJSON is invalid or contains unsupported geometry types
        
    Examples
    --------
    >>> geojson = {
    ...     "type": "Polygon",
    ...     "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
    ... }
    >>> hash_str = gen_geojson_hash(geojson)
    >>> len(hash_str)
    64
    """
    try:
        shp = shape(geojson)
    except Exception as e:
        raise ValueError(f"Invalid geojson: {e}")
    if not isinstance(shp, (Polygon, MultiPolygon)):
        raise ValueError(f"Invalid geometry type: {shp.geom_type}")
    shp = shapely.set_precision(shp, grid_size)
    geojson_str = json.dumps(shp.__geo_interface__).encode('utf-8')
    geojson_hash = hashlib_sha256(geojson_str).hexdigest()
    return geojson_hash


if __name__ == "__main__":
    geojson = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
    }

    log_pipeline("test")

    id = gen_uuid4()
    is_valid_id = is_uuid4(id)
    log_pipeline(f"id: {id}")
    log_pipeline(f"is_valid_id: {is_valid_id}")

    geojson_hash = gen_geojson_hash(geojson)
    log_pipeline(geojson_hash)

    log_pipeline(f"geojson_hash: {geojson_hash}")
