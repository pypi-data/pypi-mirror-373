import copy
import numpy as np
import xarray as xr
from pygridsio.IO.AscZmapIO import Grid

from pygridsio.IO.grid_to_xarray import isValidDataArrayGrid


def assert_grid_geometry_is_equal(grid1: xr.DataArray, grid2: xr.DataArray):
    if not np.array_equal(grid1.x, grid2.x, equal_nan=True):
        return False
    if not np.array_equal(grid1.y, grid2.y, equal_nan=True):
        return False
    return True


def assert_grids_are_equal(grid1: xr.DataArray, grid2: xr.DataArray):
    if not np.array_equal(grid1.x, grid2.x, equal_nan=True):
        return False
    if not np.array_equal(grid1.y, grid2.y, equal_nan=True):
        return False
    if not np.array_equal(grid1.data, grid2.data, equal_nan=True):
        return False
    return True


def remove_padding_from_grid(grids: Grid | xr.DataArray | xr.Dataset) -> Grid | xr.DataArray | xr.Dataset:
    if isinstance(grids, Grid):
        return remove_padding_from_custom_grid(grids)
    elif isinstance(grids, xr.DataArray):
        return remove_padding_from_xarray(grids)
    elif isinstance(grids, xr.Dataset):
        print("Not yet implemented for xr.Datasets")
    else:
        raise TypeError(f"Type of grid not recognised, accepted grids are: Grid, xr.DataArray")


def remove_padding_from_custom_grid(grid: Grid) -> Grid:
    first_col, last_col, first_row, last_row = return_first_and_last_non_nan_rows_and_columns(grid.z)

    newNx = last_col - first_col + 1
    newNy = last_row - first_row + 1
    newGridx = grid.gridx[first_col:last_col + 1]
    newGridy = grid.gridy[first_row:last_row + 1]
    newValues = grid.z[first_row:last_row + 1, first_col:last_col + 1]

    # create a new grid object:
    new_grid = copy.deepcopy(grid)
    new_grid.gridx = newGridx
    new_grid.gridy = newGridy
    new_grid.nx = newNx
    new_grid.ny = newNy
    new_grid.z = newValues

    return new_grid


def remove_padding_from_xarray(grid: xr.DataArray) -> xr.DataArray:
    if not isValidDataArrayGrid(grid):
        raise TypeError("This method only accepts a xarray DataArray with dimensions x and y")

    first_col, last_col, first_row, last_row = return_first_and_last_non_nan_rows_and_columns(grid.data)
    newGridx = grid.x.data[first_col:last_col + 1]
    newGridy = grid.y.data[first_row:last_row + 1]
    newValues = grid.data[first_row:last_row + 1, first_col:last_col + 1]
    return xr.DataArray(newValues, coords=[("y", newGridy), ("x", newGridx)], dims=["y", "x"])


def resample_xarray_grid(grid: xr.DataArray, new_cellsize: float, set_to_RDNew=False, interp_method="linear") -> xr.DataArray:
    if not isValidDataArrayGrid(grid):
        raise TypeError("This method only accepts a xarray DataArray with dimensions x and y.")

    # Create new coordinate arrays
    if set_to_RDNew:
        x_min = 0.0
        y_min = 300000
        x_max = 293000
        y_max = 635000
    else:
        x_min, x_max = grid.x.min(), grid.x.max()
        y_min, y_max = grid.y.min(), grid.y.max()

    new_x = np.arange(x_min, x_max, new_cellsize)
    new_y = np.arange(y_min, y_max, new_cellsize)

    if np.array_equal(new_x, grid.x.data) and np.array_equal(new_y, grid.y.data):
        return grid # grid is already at desired resolution. No resampling is performed

    # Interpolating the data to the new grid
    grid_interp = grid.interp(x=new_x, y=new_y, method=interp_method)
    return grid_interp


def resample_xarray_grid_to_other_grid_resolution(grid_to_resample: xr.DataArray = None, grid_to_use: xr.DataArray = None, interp_method="linear") -> xr.DataArray:
    if not isValidDataArrayGrid(grid_to_resample):
        raise TypeError("This method only accepts a xarray DataArray with dimensions x and y")
    if not isValidDataArrayGrid(grid_to_use):
        raise TypeError("This method only accepts a xarray DataArray with dimensions x and y")
    return grid_to_resample.interp(x=grid_to_use.x, y=grid_to_use.y, method=interp_method)


def calculate_grid_misfit(grid1: xr.DataArray, grid2: xr.DataArray):
    """
    This returns a value describing how different two grids are on their non-nan values.
    It is equal to:

    sqrt((grid1 - grid2)^2 ) / sqrt(grid1^2)
    Where grid1 and grid2 in the above equation is equal to the element wise comparison of their grid values.

    This means:
    - a value of 0 means the grids are identical
    - a value of 0.1 means that grid1 and grid2 differ by 10% of the magnitude of grid1
    - a value of 1.0 means that grid1 and grid2 differ by 100% of the magnitude of grid1
    - a value of 2.0 means that grid1 and grid2 differ by 200% of the magnitude of grid1
    Parameters
    ----------
    grid1
    grid2

    Returns
    -------

    """

    if not isValidDataArrayGrid(grid1):
        raise TypeError("This method only accepts a xarray DataArray with dimensions x and y")
    if not isValidDataArrayGrid(grid2):
        raise TypeError("This method only accepts a xarray DataArray with dimensions x and y")
    if not np.array_equal(grid1.x.data, grid2.x.data) or not np.array_equal(grid1.y.data, grid2.y.data):
        raise ValueError("grid1 and grid2 must have the same resolution before measuring similarity")

    grid1_data = grid1.data
    grid1_data.flatten()
    grid1_data = grid1_data[~np.isnan(grid1_data)]

    diff = grid1.data - grid2.data
    diff1d = diff.flatten()
    diff1d = diff1d[~np.isnan(diff1d)]

    grid1_norm = np.linalg.norm(grid1_data)
    if grid1_norm == 0:
        return np.inf
    else:
        return np.linalg.norm(diff1d) / grid1_norm


def return_first_and_last_non_nan_rows_and_columns(grid_values: np.array):
    nx = grid_values.shape[1]
    ny = grid_values.shape[0]

    first_col = 0
    for i in range(nx):
        if np.any(~np.isnan(grid_values[:, i])):
            first_col = i
            break

    last_col = nx - 1
    for i in range(nx - 1, 0, -1):
        if np.any(~np.isnan(grid_values[:, i])):
            last_col = i
            break

    first_row = 0
    for j in range(ny):
        if np.any(~np.isnan(grid_values[j, :])):
            first_row = j
            break

    last_row = ny - 1
    for j in range(ny - 1, 0, -1):
        if np.any(~np.isnan(grid_values[j, :])):
            last_row = j
            break

    return first_col, last_col, first_row, last_row
