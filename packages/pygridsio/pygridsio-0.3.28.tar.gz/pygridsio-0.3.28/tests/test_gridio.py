from os import path
from pathlib import Path
from unittest import TestCase

import numpy as np
import xarray as xr
import shutil

from pygridsio import read_grid, write_grid, combine_grids_in_dataset, resample_xarray_grid
from pygridsio.IO.geotiffIO import write_grid_to_geotiff, read_geotiff_to_grid
from pygridsio.IO.main_IO_functions import read_grid_to_custom_grid
from pygridsio.IO.netcdfIO import write_dataset_to_netcdf_raster, write_to_netcdf_raster


class GridTest(TestCase):
    test_files_path = Path(path.dirname(__file__), "resources")
    test_files_out_path = test_files_path / "test_output"

    def setUp(self):
        self.test_files_out_path.mkdir(exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_files_out_path)

    def test_grid_read_troublesome_zmap_to_custom_grid(self):
        """
        A weird one; I got a .zmap grid which has some combiination of ystart, yend and ny which causes the gridy array to have a length that is not equal to ny;
        This is to do with a rounding error of the function np.arange() which is used to instantiate gridy and gridx, ensure this doesn't happen.
        """

        # Arrange
        grid = read_grid_to_custom_grid(self.test_files_path / "troublesome.zmap")

        # Assert
        self.assertTrue(len(grid.gridy) == 33)


    def test_grid_read_to_custom_grid(self):
        # Arrange
        grid_file_name = Path(self.test_files_path, "SLDNA_top.zmap")
        grid = read_grid_to_custom_grid(grid_file_name)

        # Assert
        self.assertTrue(True)

    def test_grid_read_fname_without_suffix(self):
        # Arrange
        grid_file_name = Path(self.test_files_path, "SLDNA_ntg")
        grid = read_grid_to_custom_grid(grid_file_name, grid_format="ZMAP")

        # Assert
        self.assertTrue(True)

    def test_grid_read_to_xarray(self):
        # Arrange
        grid_file_name = Path(self.test_files_path, "SLDNA_top.zmap")
        grid = read_grid(grid_file_name)

        # Assert
        self.assertTrue(True)

    def test_combine_grids_in_dataset(self):
        # Arrange
        grid1 = read_grid(self.test_files_path / "SLDNA_top.zmap")
        grid2 = read_grid(self.test_files_path / "SLDNA_ntg.zmap")

        grids_dataset = combine_grids_in_dataset([grid1, grid2], labels=["top", "ntg"], grid_template=grid1)

        # Assert
        self.assertTrue(True)

    def test_combine_grids_in_dataset_different_resolutions(self):
        # Arrange
        grid1 = read_grid(self.test_files_path / "SLDNA_top.zmap")
        grid2 = read_grid(self.test_files_path / "SLDNA_ntg.zmap")
        grid2_resampled = resample_xarray_grid(grid2, new_cellsize=1000, set_to_RDNew=True)

        with self.assertRaises(ValueError):
            grids_dataset = combine_grids_in_dataset([grid1, grid2_resampled], labels=["top", "ntg"])

    def test_write(self):
        grid_file_name = Path(self.test_files_path, "SLDNA_top.zmap")
        grid = read_grid(grid_file_name)
        write_grid(grid, Path(self.test_files_out_path, "test.nc"))
        write_grid(grid, Path(self.test_files_out_path, "test.zmap"))
        write_grid(grid, Path(self.test_files_out_path, "test.asc"))
        write_grid(grid, Path(self.test_files_out_path, "test.tif"))

    def test_write_dataset(self):
        # Arrange
        grid1 = read_grid(self.test_files_path / "SLDNA_top.zmap")
        grid2 = read_grid(self.test_files_path / "SLDNA_ntg.zmap")
        grids_dataset = combine_grids_in_dataset([grid1, grid2], labels=["top", "ntg"], grid_template=grid1)
        write_dataset_to_netcdf_raster(grids_dataset, Path(self.test_files_out_path, "test_dataset.nc"))

    def test_write_to_netcdf_raster(self):
        # Arrange
        grid1 = read_grid(self.test_files_path / "SLDNA_top.zmap")
        grid2 = read_grid(self.test_files_path / "SLDNA_ntg.zmap")
        grid3 = read_grid_to_custom_grid(self.test_files_path / "SLDNA_top.zmap")
        grids_dataset = combine_grids_in_dataset([grid1, grid2], labels=["top", "ntg"], grid_template=grid1)

        # Act
        write_to_netcdf_raster(grid1, Path(self.test_files_out_path, "dataarray_write.nc"))
        write_to_netcdf_raster(grids_dataset, Path(self.test_files_out_path, "dataset_write.nc"))
        write_to_netcdf_raster(grid3, Path(self.test_files_out_path, "grid_write.nc"))

        # Assert
        grids_from_netcdf = xr.load_dataset(Path(self.test_files_out_path, "dataarray_write.nc"))
        grids_from_netcdf = xr.load_dataset(Path(self.test_files_out_path, "dataset_write.nc"))
        grids_from_netcdf = xr.load_dataset(Path(self.test_files_out_path, "grid_write.nc"))

    def test_read_netcdf_to_custom_grid(self):
        # Arrange
        grid_original = read_grid_to_custom_grid(self.test_files_path / "SLDNA_top.zmap")
        write_to_netcdf_raster(grid_original, self.test_files_out_path / "SLDNA_top.nc")

        # Act
        grid_written = read_grid_to_custom_grid(self.test_files_out_path / "SLDNA_top.nc")

        # Assert
        self.assertTrue(np.array_equal(grid_original.z, grid_written.z, equal_nan=True))


    def test_geotiff_IO(self):
        # Arrange
        grid_original = read_grid(self.test_files_path / "ROSLL__ntg.nc")

        # Act
        write_grid_to_geotiff(grid_original, self.test_files_out_path / "ROSLL__ntg.tif", epsg="RDnew")
        grid_read = read_geotiff_to_grid(self.test_files_out_path / "ROSLL__ntg.tif")

        # Assert
        xr.testing.assert_allclose(grid_read, grid_original)

    def test_geotiff_IO_read_write_grid(self):

        grid_original = read_grid(self.test_files_path / "ROSLL__ntg.nc")
        write_grid(grid_original, self.test_files_path / "ROSLL__ntg.tif")
        grid_from_geotiff = read_grid(self.test_files_path / "ROSLL__ntg.tif")

        # Assert
        xr.testing.assert_allclose(grid_original, grid_from_geotiff)