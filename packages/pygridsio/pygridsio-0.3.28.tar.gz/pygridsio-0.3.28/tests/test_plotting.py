import shutil
from os import path
from pathlib import Path
from unittest import TestCase
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import copy

import numpy as np
import pandas as pd

from pygridsio import *
from pygridsio.IO.main_IO_functions import read_grid_to_custom_grid
from pygridsio.grid_functions.grid_plotting import make_interactive_plot_with_map, plot_netherlands_shapefile


class GridTest(TestCase):
    test_files_path = Path(path.dirname(__file__), "resources")
    test_files_out_path = Path(path.dirname(__file__), "resources", "test_output")

    def setUp(self):
        outpath = Path(self.test_files_out_path)
        outpath.mkdir(exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_files_out_path)

    def test_grid_plot_custom_grid(self):
        # Arrange
        grid_file_name = Path(self.test_files_path, "SLDNA_top.zmap")
        grid = read_grid_to_custom_grid(grid_file_name)

        # Act
        with self.assertRaises(TypeError):
            plot_grid(grid, outfile=Path(self.test_files_out_path, "temp.png"), zoom=True)

    def test_grid_plot(self):
        # Arrange
        grid = read_grid(self.test_files_path / "SLDNA_top.zmap")
        fig, ax = plt.subplots(figsize=(10, 10))

        # Act
        plot_grid(grid, axes=ax, outfile=Path(self.test_files_out_path, "temp2.png"), zoom=True)

    def test_grid_plot_no_colorbar(self):
        # Arrange
        grid = read_grid(self.test_files_path / "SLDNA_top.zmap")
        fig, ax = plt.subplots(figsize=(10, 10))

        # Act
        plot_grid(grid, axes=ax, outfile=Path(self.test_files_out_path, "temp3.png"), zoom=True, add_colorbar=False)

    def test_grid_plot_custom_norm(self):
        # Arrange
        grid = read_grid(self.test_files_path / "SLDNA_top.zmap")
        fig, ax = plt.subplots(figsize=(10, 10))

        # Act
        plot_grid(grid, axes=ax, outfile=Path(self.test_files_out_path, "temp3.png"), norm=None, zoom=True)

    def test_plot_grid_comparison(self):
        grid1 = read_grid(self.test_files_path / "SLDNA_top.zmap")
        grid2 = copy.deepcopy(grid1)
        grid2.data *= 0.75
        plot_grid_comparison(grid1, grid2, outfile=Path(self.test_files_out_path, "gridcomparison.png"))

        # Assert
        self.assertTrue(True)

    def test_plot_grid_comparison_with_different_resolutions(self):
        grid1 = read_grid(self.test_files_path / "SLDNA_top.zmap")
        grid2 = copy.deepcopy(grid1)
        grid2.data *= 0.75
        grid1 = resample_xarray_grid(grid1, new_cellsize=1000)

        plot_grid_comparison(grid1, grid2, outfile=Path(self.test_files_out_path, "gridcomparison.png"))

        # Assert
        self.assertTrue(True)

    def test_plot_grid_comparison_with_filenames(self):
        grid1filename = Path(self.test_files_path, "SLDNA_top.zmap")
        grid2filename = str(Path(self.test_files_path, "SLDNA_top.zmap"))
        plot_grid_comparison(grid1filename, grid2filename, outfile=Path(self.test_files_out_path, "gridcomparison.png"))

        # Assert
        self.assertTrue(True)

    def test_plot_grid_comparison_with_all_nan_grid(self):
        grid1 = read_grid(self.test_files_path / "SLDNA_top.zmap")
        grid2 = read_grid(self.test_files_path / "SLDNA_top.zmap")
        grid2.data[:] = np.nan
        plot_grid_comparison(grid1, grid2, outfile=Path(self.test_files_out_path, "gridcomparison.png"))

        # Assert
        self.assertTrue(True)

    def test_plot_shapefile(self):
        fig, ax = plt.subplots(figsize=(10, 10))

        plot_netherlands_shapefile(ax)

        # Assert
        self.assertTrue(True)

    def test_plot_grid_comparison_single_value_grids(self):
        grid1 = read_grid(self.test_files_path / "KNNSF_ntg_new.nc")
        grid2 = read_grid(self.test_files_path / "KNNSF_ntg_old.nc")
        plot_grid_comparison(grid1, grid2, outfile=Path(self.test_files_out_path, "gridcomparison_single_value.png"), add_netherlands_shapefile=True)

        # Assert
        self.assertTrue(True)

    def test_plot_grid_comparison_identical_grids(self):
        grid1 = read_grid(self.test_files_path / "KNNSF_ntg_new.nc")
        plot_grid_comparison(grid1, grid1, outfile=Path(self.test_files_out_path, "gridcomparison_identical_grids.png"), add_netherlands_shapefile=True)

        # Assert
        self.assertTrue(True)

    def test_grid_interactive_plot(self):
        # Arrange
        grid = read_grid(self.test_files_path / "SLDNA_top.zmap")
        grid = remove_padding_from_grid(grid)

        grid2 = read_grid(self.test_files_path / "SLDNA_ntg.zmap")
        grid2 = resample_xarray_grid_to_other_grid_resolution(grid2, grid)

        grid3 = copy.deepcopy(grid2)
        grid3.data[:, :] = np.nan

        well_data = pd.read_excel(self.test_files_path / "SLDNA_well_data_perm.xlsx")

        # Act
        make_interactive_plot([grid, grid2, grid3], ["top", "ntg", "dummy1234658607-"], units=["[m]", "[0-1]", "Cats"], outfile=self.test_files_out_path / "interactive_plot.html", add_netherlands_shapefile=True,
                              title=f"Aquifer: SLDNA, Scenario: BaseCase", scatter_df=well_data, scatter_z="perm_preferred")

    def test_grid_interactive_plot_mapbox(self):
        # Arrange
        grid = read_grid(self.test_files_path / "OVERVIEW__power_P50.nc")
        grid = remove_padding_from_grid(grid)
        # grid = resample_xarray_grid(grid, new_cellsize=100000)

        grid2 = copy.deepcopy(grid)
        grid2.data[:, :] = 0.5

        grid3 = copy.deepcopy(grid)
        grid3.data[:, :] = np.nan

        # Act
        make_interactive_plot_with_map([grid, grid2, grid3], ["Power", "ntg", "dummy123465860712130934905784"], self.test_files_out_path / "map.html", title="Aquifer: SLDNA")
