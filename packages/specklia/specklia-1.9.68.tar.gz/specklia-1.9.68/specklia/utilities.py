"""File contains client-side utilities provided to make it easier to use Specklia."""

import os
from datetime import datetime
from typing import Dict, List, TypedDict

import geopandas as gpd
import numpy as np
import rasterio
import rasterio.transform
from shapely.geometry import shape


def save_gdf_as_tiff(
    gdf: gpd.GeoDataFrame,
    data_col: str,
    bounds: Dict[str, float],
    output_path: str,
    xy_proj4: str | None = None,
    data_type: str = "float32",
) -> None:
    """
    Save a GeoDataFrame as a GeoTIFF file.

    This function is provided so that raster data returned from Specklia in the form of GeoDataFrames
    can be easily converted back to GeoTIFF for integration with other tools.

    Note that this function intentionally *does not* check whether the supplied GeoDataFrame will result
    in a full raster after transformation. Instead, a grid is defined based on the bounds arguments
    and the sorted unique values in gdf, and the data_col values directly assigned to it.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        The GeoDataFrame to save to a GeoTIFF file.
    data_col : str
        The name of the column within the GeoDataFrame to save out as a Tiff file.
    bounds : Dict[str, float]
        A dictionary containing the keys "min_x", "min_y", "max_x" and "max_y" indicating the bounds of the saved tiff.
        These are provided separately because the data in gdf may not extend to the desired edges of the tiff file.
    output_path : str
        The output path of the GeoTIFF file.
    xy_proj4 : str | None
        If not None, the Proj4 code of the 'x' and 'y' columns in the GeoDataFrame. These columns will then be used
        to generate the raster instead of the GeoDataFrame's geometry.
        If None, the GeoDataFrame's geometry is used to generate the raster instead.
    data_type : str
        The data type to save data_col as, by default 'float32'
    """
    # we start by working out the desired axes of the output raster
    if xy_proj4 is not None:
        # use the 'x' and 'y' columns in the GeoDataFrame
        x_col = gdf["x"]
        y_col = gdf["y"]
        crs = xy_proj4
    else:
        # we use the geometry within the GeoDataFrame.
        x_col = gdf.geometry.x
        y_col = gdf.geometry.y
        crs = gdf.geometry.crs

    # TODO: The below lines will only work if there's at least one pair of adjacent pixels in X
    # and at least one pair of adjacent pixels in Y. We'll reload Specklia's raster data at a later
    # date to explicitly store the x and y resolutions to mitigate this, but it's a low priority problem.
    dx = np.min(np.diff(np.sort(x_col.unique())))
    dy = np.min(np.diff(np.sort(y_col.unique())))

    # generate all of the points we want to end up with in the output raster
    # we need to offset both these axes by one in order to use np.searchsorted() in a manner that matches
    # how the EOLIS Gridded products were loaded into Specklia.
    desired_x_axis = np.arange(bounds["min_x"], bounds["max_x"], dx) + dx
    desired_y_axis = np.arange(bounds["min_y"], bounds["max_y"], dy) + dy

    # create the output raster, but fill it with NaN
    gridded_data = np.full((len(desired_y_axis), len(desired_x_axis)), np.nan)

    # set the valid points within it
    gridded_data[np.searchsorted(desired_y_axis, y_col), np.searchsorted(desired_x_axis, x_col)] = gdf[data_col]

    # finally, save the raster to file.
    # There's a lot of wierdness here w.r.t axes orientation that we have to replicate
    # in order to maintain compatibility with the Timeseries Service.
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=gridded_data.shape[0],
        width=gridded_data.shape[1],
        count=1,
        dtype=data_type,
        crs=crs,
        transform=rasterio.transform.from_origin(bounds["min_x"], bounds["max_y"], dx, dy),
        compress="lzw",
        nodata=np.nan,
    ) as rst:
        rst.write_band(1, np.flipud(gridded_data))


def deserialise_sources(sources: List[Dict]) -> List[Dict]:
    """
    Reverse some serialisation of sources returned from /query.

    Reverses some serialisation of the sources dictionary returned from the /query endpoint for end-user convenience.
    Convert the WKB coverage polygon into a Shapely geometry object, and the min and max times into datetimes.

    Parameters
    ----------
    sources: List[Dict]
        A list of sources returned from Specklia

    Returns
    -------
    List[Dict]
        Sources after the coverage polygon, min_time and max_time have been deserialised.
    """
    for source in sources:
        source["geospatial_coverage"] = shape(source["geospatial_coverage"])
        source["min_time"] = datetime.fromisoformat(source["min_time"])
        source["max_time"] = datetime.fromisoformat(source["max_time"])

    return sources


class NewPoints(TypedDict):
    """List of data points to ingest."""

    gdf: gpd.GeoDataFrame
    source: dict
