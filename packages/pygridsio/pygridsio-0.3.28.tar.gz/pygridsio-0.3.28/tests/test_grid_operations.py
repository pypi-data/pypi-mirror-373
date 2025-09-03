from os import path
from pathlib import Path
from unittest import TestCase

import numpy as np

from pygridsio import *
import shutil

from pygridsio.IO.main_IO_functions import read_grid_to_custom_grid
from pygridsio.grid_functions.grid_operations import assert_grids_are_equal, remove_padding_from_custom_grid


class GridTest(TestCase):
    test_files_path = Path(path.dirname(__file__), "resources")
    test_files_out_path = Path(path.dirname(__file__), "resources", "test_output")

    def setUp(self):
        outpath = Path(self.test_files_out_path)
        outpath.mkdir(exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_files_out_path)

    def test_grid_remove_padding(self):
        # Arrange
        grid_file_name = Path(self.test_files_path, "SLDNA_top.zmap")
        grid = read_grid_to_custom_grid(grid_file_name)
        grid_no_padding = remove_padding_from_custom_grid(grid)

        non_nan_original = np.count_nonzero(~np.isnan(grid.z))
        ncells_original = np.size(grid.z)

        non_nan_new = np.count_nonzero(~np.isnan(grid_no_padding.z))
        ncells_new = np.size(grid_no_padding.z)

        # Assert
        self.assertEqual(non_nan_original, non_nan_new)
        self.assertTrue(ncells_new < ncells_original)

    def test_xarray_remove_padding(self):
        # Arrange
        grid_file_name = Path(self.test_files_path, "SLDNA_top.zmap")
        grid = read_grid(grid_file_name)
        grid_no_padding = remove_padding_from_grid(grid)

        non_nan_original = np.count_nonzero(~np.isnan(grid.data))
        ncells_original = np.size(grid.data)

        non_nan_new = np.count_nonzero(~np.isnan(grid_no_padding.data))
        ncells_new = np.size(grid_no_padding.data)

        # Assert
        self.assertEqual(non_nan_original, non_nan_new)
        self.assertTrue(ncells_new < ncells_original)

    def test_xarray_grid_resample_to_RDnew(self):
        # Arrange
        grid_file_name = Path(self.test_files_path, "SLDNA_top.zmap")
        grid = read_grid(grid_file_name)

        # Act
        resampled_grid = resample_xarray_grid(grid, 1000, set_to_RDNew=True, interp_method="nearest")

        # Assert
        self.assertEqual(len(resampled_grid.x), 293)
        self.assertEqual(len(resampled_grid.y), 335)

    def test_xarray_grid_resample_to_RDnew_multiple_times(self):
        # Arrange
        grid_file_name = Path(self.test_files_path, "SLDNA_top.zmap")
        grid = read_grid(grid_file_name)

        # Act
        resampled_grid1 = resample_xarray_grid(grid, 999, set_to_RDNew=True, interp_method="linear")
        resampled_grid2 = resample_xarray_grid(resampled_grid1, 999, set_to_RDNew=True, interp_method="linear")

        plot_grid(grid, outfile=self.test_files_out_path / "original_grid.png")
        plot_grid(resampled_grid1, outfile=self.test_files_out_path / "resampled1.png")
        plot_grid(resampled_grid2, outfile=self.test_files_out_path / "resampled2.png")

        # Assert
        self.assertTrue(assert_grids_are_equal(resampled_grid1, resampled_grid2))


    def test_xarray_grid_resample_to_other_grid_resolution(self):
        # Arrange
        grid1 = read_grid(self.test_files_path / "SLDNA_top.zmap")
        grid2 = read_grid(self.test_files_path / "ROSL_ROSLU__temperature.nc")

        # Act
        grid1 = resample_xarray_grid_to_other_grid_resolution(grid_to_resample=grid1,grid_to_use=grid2)

        # Assert
        self.assertTrue(np.array_equal(grid1.x.data, grid2.x.data))
        self.assertTrue(np.array_equal(grid1.y.data, grid2.y.data))

    def test_grid_similarity(self):
        # Arrange
        grid1 = read_grid(self.test_files_path / "KNNSF_ntg_new.nc")
        grid2 = read_grid(self.test_files_path / "KNNSF_ntg_old.nc")
        grid2_resampled = resample_xarray_grid_to_other_grid_resolution(grid_to_resample=grid2,grid_to_use=grid1)

        # Act
        difference = calculate_grid_misfit(grid1, grid2_resampled)

    def test_grid_similarity_all_zeros(self):
        # Arrange
        grid1 = read_grid(self.test_files_path / "KNNSF_ntg_new.nc")
        grid2 = read_grid(self.test_files_path / "KNNSF_ntg_old.nc")
        grid2_resampled = resample_xarray_grid_to_other_grid_resolution(grid_to_resample=grid2,grid_to_use=grid1)
        grid1.data[:] = 0

        # Act
        difference = calculate_grid_misfit(grid1, grid2_resampled)

