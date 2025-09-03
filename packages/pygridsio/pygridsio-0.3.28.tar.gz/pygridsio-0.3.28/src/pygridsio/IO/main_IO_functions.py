from pathlib import Path
import xarray as xr

from pygridsio.IO.AscZmapIO import Grid
from pygridsio.IO.grid_to_xarray import custom_grid_to_xarray, isValidDataArrayGrid, xarray_to_custom_grid
from pygridsio.IO.netcdfIO import read_netcdf_to_custom_grid, write_to_netcdf_raster, read_netcdf_to_dataarray
from pygridsio.IO.geotiffIO import read_geotiff_to_grid, write_grid_to_geotiff
from pygridsio.grid_functions.grid_operations import assert_grid_geometry_is_equal, resample_xarray_grid_to_other_grid_resolution


def read_grid_to_custom_grid(filename: str | Path, grid_format: str = None) -> Grid:
    """providing the filename of a grid (in either .asc, .zmap, .nc) read in the grid and return a grid object
    Parameters
    ----------
    filename

    Returns
    -------
        A custom Grid object
    """
    if Path(filename).suffix == '.nc':
        return read_netcdf_to_custom_grid(filename)
    return Grid(str(filename), grid_format=grid_format)


def read_grid(filename: str | Path, grid_format: str = None) -> xr.DataArray:
    """providing the filename of a grid (in either .asc, .zmap, .nc) read in the grid and
    return an xarray object with dimensions: x, y

    Parameters
    ----------
    grid_format
    filename

    Returns
    -------
        A xr.DataArray object
    """
    if Path(filename).suffix == '.nc':
        return read_netcdf_to_dataarray(filename)
    if Path(filename).suffix == '.tif':
        return read_geotiff_to_grid(filename)
    return custom_grid_to_xarray(read_grid_to_custom_grid(filename, grid_format))


def write_grid(grid: xr.DataArray, filename: Path, RDnew=True, epsg=None):
    """Write grid to .asc, .zmap, .nc or .tif"""
    if not isValidDataArrayGrid(grid):
        raise TypeError("Provided grid type is not a valid xr.DataArray with 2 dimensions: x and y")
    if type(filename) is not Path:
        filename = Path(filename)
    if filename.suffix in [".asc", ".zmap"]:
        if epsg is not None:
            raise ValueError("epsg projection code was provided to write_grid, while the desired output filetype is .asc or .zmap; which cannot accept arbitrary epsg codes.")
        xarray_to_custom_grid(grid).write(str(filename))
    if filename.suffix == ".nc":
        if epsg is not None:
            raise ValueError("epsg projection code was provided to write_grid, while the desired output filetype is .nc; which at the moment cannot accept arbitrary epsg codes.")
        write_to_netcdf_raster(grid, filename, RDnew_projection=RDnew)
    if filename.suffix == ".tif":
        if RDnew: epsg = 28992
        write_grid_to_geotiff(grid, filename, epsg=epsg)


def combine_grids_in_dataset(grids: list[xr.DataArray], labels: list | None = None, grid_template: xr.DataArray = None):
    """
    Provided a list of grids combine them into a xr.DataSet, with each grid being its own variable. Ensure these grids all have the same geometry.
    Parameters
    ----------
    grids
    labels
    grid_template

    Returns
    -------

    """
    if labels is None:
        labels = ["grid" + str(i) for i in range(len(grids))]

    if len(grids) != len(labels):
        raise ValueError("The length of the list of grids and the list of labels must be the same")

    dataset_data = {}
    for i in range(len(grids)):
        grid_temp = grids[i]

        if grid_template is not None:
            grid_temp = resample_xarray_grid_to_other_grid_resolution(grid_to_resample=grid_temp, grid_to_use=grid_template)

        if i > 0:
            if not assert_grid_geometry_is_equal(grids[0], grid_temp):
                raise ValueError("Grids must have the same geometry to be combined into a single dataset")
        dataset_data[labels[i]] = grid_temp

    return xr.Dataset(dataset_data)
