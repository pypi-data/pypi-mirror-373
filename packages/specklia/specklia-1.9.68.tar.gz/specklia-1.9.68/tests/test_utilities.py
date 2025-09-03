"""Unit tests for specklia.utilities.py."""

import os
from datetime import datetime

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio

from specklia.utilities import save_gdf_as_tiff


def test_save_gdf_as_tiff(test_inputs_dir: str, tmp_path: os.PathLike) -> None:
    # start by loading an example tiff
    example_tiff_path = os.path.join(test_inputs_dir, "iceland_example.tif")

    with rasterio.open(example_tiff_path) as rst:
        data_before = rst.read(1)
        transform_before = rst.transform
        bounds_before = rst.bounds  # min_x, min_y, max_x, max_y
        resolution_before = rst.transform.a
        crs_before = rst.crs

    # convert to a GeoDataFrame (matching what is available from Specklia)
    y, x = np.meshgrid(
        np.arange(bounds_before[1] + resolution_before / 2.0, bounds_before[3], resolution_before),
        np.arange(bounds_before[0] + resolution_before / 2.0, bounds_before[2], resolution_before),
    )
    x_idx, y_idx = np.floor(~transform_before * np.array(*zip([x], [y], strict=False))).astype(int)
    h = data_before[y_idx, x_idx]
    is_valid_point = (~np.isnan(h)).ravel()

    raw_df = pd.DataFrame(
        {
            "t": datetime(2020, 7, 1),
            "x": x.ravel()[is_valid_point],
            "y": y.ravel()[is_valid_point],
            "h": h.ravel()[is_valid_point],
        }
    )

    # Note that as per Specklia's output, the GeoDataFrame Geometry column is always 4326,
    # but additional columns are provided with the original data projection.
    gdf = gpd.GeoDataFrame(raw_df, geometry=gpd.points_from_xy(raw_df.x, raw_df.y), crs=crs_before).to_crs("EPSG:4326")

    # now save it back to disk using the function under test.
    # This shows the metadata we need from Specklia to complete raster integration.
    output_tiff_path = os.path.join(tmp_path, "output.tiff")
    save_gdf_as_tiff(
        gdf=gdf,
        data_col="h",
        xy_proj4=crs_before.to_proj4(),
        bounds={
            "min_x": bounds_before[0],
            "min_y": bounds_before[1],
            "max_x": bounds_before[2],
            "max_y": bounds_before[3],
        },
        output_path=output_tiff_path,
    )

    # reload it and check it matches the original GeoTIFF
    with rasterio.open(output_tiff_path) as rst:
        data_after = rst.read(1)
        transform_after = rst.transform
        bounds_after = rst.bounds  # min_x, min_y, max_x, max_y
        resolution_after = rst.transform.a
        crs_after = rst.crs

    assert transform_before == transform_after
    assert bounds_before == bounds_after
    assert resolution_before == resolution_after
    assert crs_before == crs_after
    np.testing.assert_array_equal(data_before, data_after)
