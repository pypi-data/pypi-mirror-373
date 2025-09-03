# pygridsio

## Introduction

This is a python submodule containing IO and plotting functionality for reading and writing .asc, .zmap .nc and .tif grids.

## Installation

pygridsio is available via the pypi package registry:

`pip install pygridsio`

## Usage

`from pygridsio import *`

The standard grid class used throughout this project is a Xarray DataArray (see: https://xarray.dev/) with 2 dimensions: x and y.

To read a grid file to this class use:

`grid = read_grid(filename)`

You can write a grid to .asc, .zmap, .nc or .tif using the following method:

`write_grid(grid,filename)`

The code will discern which filetype to write out to by the file extension in filename. Note: .asc and .zmap are ascii based files and take up a lot of space. .nc and .tif are binary file types.

There is some plotting functionality implemented in pygridsio, this can be accessed using the `pygridsio.grid_plotting` module:
- The method `pygridsio.grid_plotting.plot_grid` allows you to plot a custom Grid class, or xr.DataArray with multiple options. See the description of the method for more detail.
- The method `pygridsio.grid_plotting.plot_grid_comparison` Creates a plot comparing two grids values against each other. See the description of the method for more detail.
- The method `pygridsio.grid_plotting.make_interactive_plot` Creates a interactive .html plot using plotly, this saves to a .html file