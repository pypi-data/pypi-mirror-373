from pathlib import Path

import rioxarray as rxr
import xarray as xr


def read_geotiff_to_grid(file_path):
    """
    Reads a single-band GeoTIFF file into a xarray DataArray; with two coordinates, x and y.

    Parameters:
    - file_path (str): Path to the GeoTIFF file.

    Returns:
    - xarray.DataArray: The loaded raster data.

    Raises:
    - ValueError: If the GeoTIFF contains multiple bands.
    """
    with rxr.open_rasterio(file_path) as tif:  # Ensures file is closed properly
        da = tif.load()

    # Check if multiple bands exist
    if "band" in da.dims and da.sizes["band"] > 1:
        raise ValueError(f"Error: The file '{file_path}' contains multiple bands ({da.sizes['band']}), but only single-band TIFFs are supported.")

    # Drop the "band" dimension if present
    da = da.squeeze(dim="band", drop=True) if "band" in da.dims else da

    # Drop the attrs read in from the geotiff
    da = da.drop_attrs()

    # Drop the 'spatial_ref' coordinate if it exists
    if "spatial_ref" in da.coords:
        da = da.drop_vars("spatial_ref")

    # Ensure y-axis is in ascending order (bottom to top)
    if da.y[0] > da.y[-1]:  # If y is decreasing, flip it
        da = da.reindex(y=da.y[::-1])

    return da


def write_grid_to_geotiff(da: xr.DataArray, output_path: str | Path, epsg: int | str = None):
    """
    Writes a xarray DataArray to a GeoTIFF file.

    Parameters:
    - da (xarray.DataArray): The raster data to write.
    - output_path (str): Path to save the GeoTIFF file.
    - epsg (int | str, optional): EPSG code to set the coordinate reference system before saving.
        if "RDnew" is provided as a string it will write the geotiff with the epsg code 28992 (RD new)
    """
    if epsg is not None:
        if epsg == "RDnew":
            da = da.rio.write_crs(28992, inplace=False)
        else:
            da = da.rio.write_crs(epsg, inplace=False)

    # Ensure y-axis is in descending order (top to bottom); as assumed by geotiff
    if da.y[0] < da.y[-1]:  # If y is increasing, flip it
        da = da.reindex(y=da.y[::-1])

    da.rio.to_raster(output_path)
