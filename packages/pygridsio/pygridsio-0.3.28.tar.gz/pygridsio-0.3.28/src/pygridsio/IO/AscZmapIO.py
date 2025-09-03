#! /usr/bin/env python
from __future__ import annotations

import contextlib
import copy
import datetime
import io
import os

import numpy as np
import pandas as pd
import pykrige.kriging_tools as kt

from pygridsio.IO.voxet import Voxet


EMPTY_COORD_SYS = '<null>'

#        NOTE: This file should not be removed or modified without first consulting Jan Diederik van Wees (Jan_Diederik.vanWees@tno.nl)
#        This class is used by PyGridsio to read in and write out .asc and .zmap files; Jan Diederik also uses it as the backbone grid class for other projects such as ga4a.
#        This statement is valid from 04/06/2025 until agreed otherwise.


class Grid:
    """
        NOTE: This class should not be removed or modified without first consulting Jan Diederik van Wees (Jan_Diederik.vanWees@tno.nl)
        This class is used by PyGridsio to read in and write out .asc and .zmap files; Jan Diederik also uses it as the backbone grid class for other projects such as ga4a.
        This statement is valid from 04/06/2025 until agreed otherwise.

      This is a class for holding a Grid object.

      Attributes:
          _fname (str): the filepath of the Grid excluding extension (this is controlled by the gridIO attribute
          _grid_io (GridIO): the IO object controlling read and write, these are initialized in the init, and can created
                  a call to GridIOFactory().getGridIO(format)
          gridx (numpy float array) : x coordinates of grid mesh  ranging from in range (0,nx-1)
          gridy  (numpy float array): y coordinates of grid mesh  ranging from in range (0,ny-1)
          z (numpy float array): z values, two dmensional array of dimension (nx,ny)
          nodata_val (float):  no data value (can also be nan)
          orx (float): origin x coordinate
          ory (float): origin y coordinate
          cellsize (float): cell size
          dx (float): same as cell size
          dy (float): same as cell size

      Methods:
           read()  :  reads a grid from (fname + gridIO extension)
           write() : writes the grid to (fname + gridIO extension)
           setnodata(val: float):  sets the nodata value to val
           addZvalues

      the following operators are suported for the pygridsio, which operate on the z values and assume that the operands
      have equal grid sizes
       +, -, * and /

      """

    def __init__(self, filename: str = None, grid_format: str = None, readhelpers = None, read=True):
        """
            construct Grid instance from fname and format

        :param filename:  the filepath of the Grid excluding extension (this is controlled by the format)
        :param grid_format: format string, choose between ArcGridIOARC.FORMAT or CsvGridIO.FORMAT
        :param readhelpers: dictonary for assisting in reading
         if format is CSV, keys ZCSV and PROP are expected: the x,y,z of grid centers are read from  X,Y,Z named columns, and makes
         a match where zcsv==Z, which is isolated as Grid, same holds  for the property column to be mapped as Grid.
         if format is VOXET keys INDEX (0..N) and index direction IDIR (0,1,2) and PROP are expected
        """
        self.z: np.ndarray | None = None
        self.gridx: np.ndarray | None = None
        self.gridy: np.ndarray | None = None
        self.orx: float | None = None
        self.ory: float | None = None
        self.dx: float | None = None
        self.dy: float | None = None
        self._grid_io = None
        self.cellsize: float | None = None
        self.nodata_val = None
        self.coord_sys: str | None = None

        self._fname: str = filename
        self._readhelpers = readhelpers


        if grid_format is None and filename is not None:
            if filename.endswith(ArcGridIO.SUFFIX):
                self._grid_io = GridIOFactory().get_grid_io(ArcGridIO.FORMAT)
            elif filename.endswith(ZmapGridIO.SUFFIX):
                self._grid_io = GridIOFactory().get_grid_io(ZmapGridIO.FORMAT)
            elif filename.endswith(CsvGridIO.SUFFIX):
                self._grid_io = GridIOFactory().get_grid_io(CsvGridIO.FORMAT, readhelpers= self._readhelpers)
            else:
                raise IOError("Unknown grid file extension for file: " + filename)
        elif filename is not None:
            self._grid_io = GridIOFactory().get_grid_io(grid_format)
        if read:
            self.read()

    @classmethod
    def from_number(cls, number: float):
        """
         create a grid with 4 cells/nodes which are covering -inf,inf

        :param number: value of the grid cells
        :return: grid
        """
        g = cls('default.asc', read=False)
        g.z = (np.ones(4)*number).reshape(2,2)
        dxdy = 1e30
        g.gridx = np.asarray([-0.5*dxdy, 0.5*dxdy])
        g.gridy = g.gridx * 1.0
        g.orx =  g.gridx[0]
        g.ory = g.gridy[0]
        g.dx = g.gridx[1]- g.gridx[0]
        g.dy = g.gridy[1] - g.gridy[0]

        g.cellsize =g.dx
        return g

    def fillblanks(self, g2use:Grid, shift=0):
        """
         modify the grid to fill no data values where g2use is define. In that case add shift
        :param g2use:  grid to use to fill no data values
        :param shift:  added to the value of g2use
        :return:
        """
        nx = len(self.gridx)
        ny = len(self.gridy)
        for n in range(nx):
            for m in range(ny):
                if (np.isnan(self.z[m,n])):
                    if (not np.isnan(g2use.z[m,n])):
                        self.z[m,n] = g2use.z[m,n]+ shift

    def swapy(self):
        """
         swap the valyes from ymin to ymax and viceversa (i.e. mirror in the mid x-axis of the grid)
        :return: the object has been modified

        """
        zswap = self.z * 1
        nx = len(self.gridx)
        ny = len(self.gridy)
        for n in range(nx):
            for m in range(ny):
                mm = ny - m - 1
                zswap[mm, n] = self.z[m,n]
        self.z = zswap

    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self, fname: str):
        """
        Set the file name (path). The file extension (.asc/.zmap) determines the IO format
        Args:
            fname: file path
        """
        if fname.endswith(ArcGridIO.SUFFIX):
            self._grid_io = GridIOFactory().get_grid_io(ArcGridIO.FORMAT)
        elif fname.endswith(ZmapGridIO.SUFFIX):
            self._grid_io = GridIOFactory().get_grid_io(ZmapGridIO.FORMAT)
        elif fname.endswith(CsvGridIO.SUFFIX):
            self._grid_io = GridIOFactory().get_grid_io(CsvGridIO.FORMAT)
        elif fname.endswith(VoxetGridIO.SUFFIX):
            self._grid_io = GridIOFactory().get_grid_io(VoxetGridIO.FORMAT)
        self._fname = fname

    @property
    def grid_io(self):
        return self._grid_io

    @grid_io.setter
    def grid_io(self, grid_io):
        self._grid_io = GridIOFactory().get_grid_io(grid_io)

    def read(self) -> None:
        """
        Reads a grid from fname and gridIO object
        """
        gio = self.grid_io
        f = self.fname
        self.z, self.gridx, self.gridy, self.cellsize, self.nodata_val, self.coord_sys = gio.read(f, readhelpers=self._readhelpers)
        self.set_origin_dx_dy()
        self.set_nodata_value(np.nan)

    def set_origin_dx_dy(self):
        self.orx = self.gridx[0]
        self.ory = self.gridy[0]
        self.cellsize = self.gridx[1] - self.gridx[0]
        self.dx = self.cellsize
        self.dy = self.cellsize

    def getxyminmax(self):
        xmin = self.gridx[0]
        xmax = self.gridx[-1]
        ymin = self.gridy[0]
        ymax = self.gridy[-1]
        return xmin, ymin, xmax, ymax

    def write(self, fname=None, style=2):
        """
            Write file to specified file path. The file extension (.asc/.zmap) determines the IO format
        Args:
            fname: file name path
        """
        if fname is not None:
            self.fname = fname
        self.grid_io.write(self)


    def set_nodata_value(self, nodataval: float):
        if np.isnan(self.nodata_val):
            # do other way
            self.z = np.where(np.isnan(self.z), nodataval, self.z)
        else:
            # this works only if self.nodata is not nan
            self.z = np.where(self.z == self.nodata_val, nodataval, self.z)
        self.nodata_val = nodataval

    def add_values_dataframe(self, df: pd.DataFrame, xname='x', yname='y', as_name='z') -> pd.DataFrame:
        """
            add a new column to a DataFrame, corresponding to values of the Grid at X,Y coordinates corresponding
            the row values in xname,yname respectively. FOR SOME REASON THIS DOES NOT WORK WELL YET, USE THE
            BbaseHelperTNO.addZvalues instead

        :param df : dataframe to add column
        :param xname: x coordinate column name in the DataFrame
        :param yname: y coordinate column name in the DataFrame
        :param as_name: new (or existing) column name in the DataFrame for the pr
        :return: modified df (Dataframe) with additional column corresponding to Z values of grid at xname,yname  column values

        """
        z = pd.Series([], dtype=np.float64)
        for i in range(len(df)):
            xval = df[xname][i]
            yval = df[yname][i]
            z[i] = self.valueatxy(xval, yval)
        df.insert(3, as_name, z, allow_duplicates=True)
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def find_i_index(self, x):
        if x < (self.gridx[0] - self.dx / 2) or x > (self.gridx[-1] + self.dx / 2):
            return -1
        for i, xval in enumerate(self.gridx):
            if x <= self.gridx[i] + self.dx / 2:
                return i

    def find_j_index(self, y):
        if y < (self.gridy[0] - self.dy / 2) or y >( self.gridy[-1] + self.dy / 2):
            return -1
        for j, yval in enumerate(self.gridy):
            if y <= self.gridy[j] + self.dy / 2:
                return j

    def valueatxy(self, xval, yval):
        ii = self.find_i_index(xval)
        jj = self.find_j_index(yval)
        if ii == -1 or jj == -1 :
            return np.nan
        else:
            return self.z[jj, ii]

    def valueatxy_list(self, xvals, yvals):
        return [self.valueatxy(xvals[i],yvals[i]) for i in range(len(xvals))]

    def grid_z_clip(self, z_min: float = None, z_max: float = None):
        if z_min is not None and z_max is not None:
            self.z = np.clip(self.z, a_min=z_min, a_max=z_max)
        elif z_min is not None and z_max is None:
            self.z = np.clip(self.z, a_min=z_min)
        elif z_min is None and z_max is not None:
            self.z = np.clip(self.z, a_max=z_max)

    def grid_xy_clip(self, xmin: float, ymin: float, xmax: float, ymax: float):
        istart = self.find_i_index(xmin)
        if istart == -1:
            istart = 0
        iend = self.find_i_index(xmax)
        if iend == -1:
            iend = len(self.gridx)
        jstart = self.find_j_index(ymin)
        if jstart == -1:
            jstart = 0
        jend = self.find_j_index(ymax)
        if jend == -1:
            jend = len(self.gridy)
        gridx_new = self.gridx[istart:iend]
        gridy_new = self.gridy[jstart:jend]
        z_new = self.z[jstart:jend, istart:iend]
        self.gridx = gridx_new
        self.gridy = gridy_new
        self.z = z_new
        self.set_origin_dx_dy()

    def gridresample(self, lod=1, grid2use=None):
        """
        resample  gridx_new, gridy_new, alternatively cellsize is enlarged by lod*cellsize to coarsen the grid
        the result is written in the grid

        :param lod: (int) coarsen the existing grid by enlarging cellsize to lod*cellsize
        :param grid2use: (Grid)  use another grid to specify the new grid locations default=None

        """
        xmin = self.gridx[0]
        xmax = self.gridx[-1]
        ymin = self.gridy[0]
        ymax = self.gridy[-1]

        cellsize_new = self.cellsize * lod
        if grid2use is None:
            gridx_new = np.arange(xmin, xmax, cellsize_new)
            gridy_new = np.arange(ymin, ymax, cellsize_new)
        else:
            gridx_new = grid2use.gridx * 1.0
            gridy_new = grid2use.gridy * 1.0

        # orginal index
        ii = np.arange(0, len(self.gridx))
        jj = np.arange(0, len(self.gridy))
        ii_new = np.round(np.interp(gridx_new, self.gridx, ii))
        jj_new = np.round(np.interp(gridy_new, self.gridy, jj))
        ii_new = ii_new.astype(int)
        jj_new = jj_new.astype(int)

        if grid2use is None:
            for i, ival in enumerate(ii_new):
                gridx_new[i] = self.gridx[ival]
            for j, jval in enumerate(jj_new):
                gridy_new[j] = self.gridy[jval]
            gx, gy = np.meshgrid(gridx_new, gridy_new)
            z_new = gx
        else:
            z_new = grid2use.z * 1.0

        for i, ival in enumerate(ii_new):
            for j, jval in enumerate(jj_new):
                z_new[j, i] = self.z[jval, ival]

        self.z = z_new
        self.gridx = gridx_new
        self.gridy = gridy_new
        self.set_origin_dx_dy()

    def get_as_mask(self):
        """
            get as mask setting all define values to 1.0, rest to unknown
        """
        self.unmask()
        gmask = self * 0.0 + 1.0
        return gmask

    def unmask(self):
        self.z = np.ma.filled(self.z.astype(float), np.nan)

    def replace(self, subgrid):
        """
          replace the grid values where subgrid is defined (not nan) with subgrid values.
          It assumes that sizes of both pygridsio are the same

        :param subgrid: (Grid)  grid to superpose of the grid. It assumes that the
        """

        gsubmask = subgrid.get_as_mask()
        # get 1 values inside the subgrid, and 0 outside
        gsubmask.z = np.nan_to_num(gsubmask.z)
        # get 0 values inside the subgrid and 1 outside
        gsubmaskcomp = gsubmask * 1.0
        gsubmaskcomp.z = 1.0 - gsubmask.z

        # zero all values in the subgrid domain
        self.z = self.z * gsubmaskcomp.z

        # and add the subgrid
        self.z = self.z + np.nan_to_num(subgrid.z)

    def __add__(self, other):
        gresult = copy.deepcopy(self)
        if isinstance(other, Grid):
            gresult.z = self.z + other.z
        else:
            gresult.z = self.z + other
        return gresult

    def __radd__(self, other):
        return Grid.__add__(self, other)

    def __truediv__(self, other):
        gresult = copy.deepcopy(self)
        if isinstance(other, Grid):
            gresult.z = self.z / other.z
        else:
            gresult.z = self.z / other
        return gresult

    def __rtruediv__(self, other):
        return Grid.__truediv__(self, other)

    def __mul__(self, other):
        gresult = copy.deepcopy(self)
        if isinstance(other, Grid):
            gresult.z = self.z * other.z
        else:
            gresult.z = self.z * other
        return gresult

    def __rmul__(self, other):
        return Grid.__mul__(self, other)

    def __sub__(self, other):
        gresult = copy.deepcopy(self)
        if isinstance(other, Grid):
            gresult.z = self.z - other.z
        else:
            gresult.z = self.z - other
        return gresult

    def __rsub__(self, other):
        gresult = copy.deepcopy(self)
        if isinstance(other, Grid):
            gresult.z = -self.z + other.z
        else:
            gresult.z = -self.z + other
        return gresult


class GridIO:
    """
        This is a class for IO of a Grid Object.

        Methods:
             read()  :  reads a grid from (fname + gridIO extension)
             write(g: Grid) : writes the grid to (fname + gridIO extension)
    """

    def __init__(self):
        pass

    def read(self, fname, readhelpers=None):
        raise NotImplementedError("abstract class reading should use derived class")

    def write(self, g: Grid, style=2):
        raise NotImplementedError("abstract class reading should use derived class")


class ArcGridIO(GridIO):
    """
        This is a class for IO of a Arc Grid Object.

        Methods:
             read()  :  reads a grid from (fname + ArcGridIO.SUFFIX)
             write(g: Grid) : writes the grid to (fname + ArcGridIO.SUFFIX)
    """
    FORMAT = "ARC"
    SUFFIX = ".asc"
    nodata_value = -9.99999E005

    def read(self, fname, readhelpers=None):
        if not fname.endswith(self.SUFFIX):
            fname = fname + self.SUFFIX
        z, gridx, gridy, cellsize, nodata = kt.read_asc_grid(filename=fname)
        return z, gridx, gridy, cellsize, nodata, EMPTY_COORD_SYS

    def write(self, g: Grid, style=2):
        if not g.fname.endswith(self.SUFFIX):
            g.fname = g.fname + self.SUFFIX

        with contextlib.suppress(FileNotFoundError):
            os.remove(g.fname)

        nodataorig = g.nodata_val
        g.set_nodata_value(ArcGridIO.nodata_value)

        kt.write_asc_grid(g.gridx, g.gridy, g.z, filename=g.fname, no_data= ArcGridIO.nodata_value, style=style)


        if np.ma.is_masked(g.z):
            g.z = np.array(g.z.tolist(ArcGridIO.nodata_value))

        x = np.squeeze(np.array(g.gridx))
        y = np.squeeze(np.array(g.gridy))
        z = np.squeeze(np.array(g.z))
        nrows = z.shape[0]
        ncols = z.shape[1]

        dx = abs(x[1] - x[0])
        dy = abs(y[1] - y[0])
        check_x_y_spacing(x, y, dx, dy)

        cellsize = -1
        if style == 2:
            if dx != dy:
                raise ValueError(
                    "X and Y spacing is not the same. "
                    "Cannot write *.asc file in the specified format."
                )
            cellsize = dx

        xllcenter = x[0]
        yllcenter = y[0]

        # Note that these values are flagged as -1. If there is a problem in trying
        # to write out style 2, the -1 value will appear in the output file.
        xllcorner = -1
        yllcorner = -1
        if style == 2:
            xllcorner = xllcenter - dx / 2.0
            yllcorner = yllcenter - dy / 2.0

        with io.open(g.fname, "w") as f:
            if style == 1:
                f.write("NCOLS          " + "{:<10n}".format(ncols) + "\n")
                f.write("NROWS          " + "{:<10n}".format(nrows) + "\n")
                f.write("XLLCENTER      " + "{:<10.2f}".format(xllcenter) + "\n")
                f.write("YLLCENTER      " + "{:<10.2f}".format(yllcenter) + "\n")
                f.write("DX             " + "{:<10.2f}".format(dx) + "\n")
                f.write("DY             " + "{:<10.2f}".format(dy) + "\n")
                f.write("NODATA_VALUE   " + "{:<10.2f}".format(ArcGridIO.nodata_value) + "\n")
            elif style == 2:
                f.write("NCOLS          " + "{:<10n}".format(ncols) + "\n")
                f.write("NROWS          " + "{:<10n}".format(nrows) + "\n")
                f.write("XLLCORNER      " + "{:<10.2f}".format(xllcorner) + "\n")
                f.write("YLLCORNER      " + "{:<10.2f}".format(yllcorner) + "\n")
                f.write("CELLSIZE       " + "{:<10.2f}".format(cellsize) + "\n")
                f.write("NODATA_VALUE   " + "{:<10.2f}".format(ArcGridIO.nodata_value) + "\n")
            else:
                raise ValueError("style kwarg must be either 1 or 2.")

            for m in range(z.shape[0] - 1, -1, -1):
                for n in range(z.shape[1]):
                    f.write("{:<16.2f}".format(z[m, n]))
                if m != 0:
                    f.write("\n")

        g.set_nodata_value(nodataorig)


class ZmapGridIO(GridIO):
    """
        This is a class for IO of a Zmap Grid Object (IO Petrel).

        Methods:
             read()  :  reads a grid from (fname + ZmapGridIO.SUFFIX)
             write(g: Grid) : writes the grid to (fname + ZmapGridIO.SUFFIX)
    """
    FORMAT = "ZMAP"
    SUFFIX = ".zmap"
    fieldwidth = 15
    nodesperline = 5
    nodata_value = 1E30

    def read(self, fname, readhelpers=None):

        no_data_value, nx, ny, originx, originy, maxx, maxy, dx, dy = 0, 0, 0, 0, 0, 0, 0, 0, 0
        data_values = np.empty(1)
        coord_sys = EMPTY_COORD_SYS

        i_header_line, i_value = 0, 0
        with io.open(fname, "r") as f:
            while True:
                line = f.readline()
                if line.startswith('!'):
                    line_strings = line.split(":")
                    if line_strings[0].__contains__('COORDINATE REFERENCE SYSTEM'):
                        coord_sys = line_strings[1].replace('\n', '')
                else:
                    line_strings = line.split()
                    line_strings = [string.replace(',', '') for string in line_strings]

                if len(line_strings) == 0:
                    break

                if i_header_line == -1 and not line_strings[0].startswith('!'):
                    for i_string in range(len(line_strings)):
                        data_values[i_value] = float(line_strings[i_string])
                        i_value += 1

                if line_strings[0].startswith('@'):
                    if i_header_line == 0:
                        i_header_line += 1
                    else:
                        i_header_line = -1

                if i_header_line > 0:
                    if i_header_line == 2:
                        no_data_value = float(line_strings[1])
                    elif i_header_line == 3:
                        ny = int(line_strings[0])
                        nx = int(line_strings[1])
                        originx = float(line_strings[2])
                        maxx = float(line_strings[3])
                        originy = float(line_strings[4])
                        maxy = float(line_strings[5])
                        data_values = np.empty(ny * nx)
                    i_header_line += 1

        z = np.empty([ny, nx])
        i_value = 0
        for n in range(z.shape[1]):
            for m in range(z.shape[0] - 1, -1, -1):
                z[m, n] = data_values[i_value]
                i_value += 1

        dx = (maxx - originx) / (nx - 1)
        dy = (maxy - originy) / (ny - 1)

        gridx = np.arange(originx, originx + nx * dx, dx)
        gridy = np.arange(originy, originy + ny * dy, dy)

        # Due to rounding errors it is possible that np.arrange() results in a gridx or gridy array that is too large by 1 value; simply clip to ny,nx
        if len(gridx) > nx:
            gridx = gridx[:nx]
        if len(gridy) > ny:
            gridy = gridy[:ny]

        cellsize = (dx, dy)

        return z, gridx, gridy, cellsize, no_data_value, coord_sys

    def write(self, g: Grid):
        if not g.fname.endswith(self.SUFFIX):
            g.fname = g.fname + self.SUFFIX

        with contextlib.suppress(FileNotFoundError):
            os.remove(g.fname)

        x = np.squeeze(np.array(g.gridx))
        y = np.squeeze(np.array(g.gridy))
        z = np.squeeze(np.array(g.z))

        nx = len(x)
        ny = len(y)

        dx = abs(x[1] - x[0])
        dy = abs(y[1] - y[0])
        check_x_y_spacing(x, y, dx, dy)

        xllcenter = x[0]
        yllcenter = y[0]

        hix = xllcenter + (nx - 1) * dx
        hiy = yllcenter + (ny - 1) * dy

        now = datetime.datetime.now()

        with io.open(g.fname, "w") as f:
            f.write("!" + "\n")
            f.write("!     ZIMS FILE NAME :  " + os.path.basename(g.fname) + "\n")
            f.write("!     FORMATTED FILE CREATION DATE: " + now.strftime("%d/%m/%Y") + "\n")
            f.write("!     FORMATTED FILE CREATION TIME: " + now.strftime("%H:%M:%S") + "\n")
            f.write("!     COORDINATE REFERENCE SYSTEM: " + g.coord_sys + "\n")
            f.write("!" + "\n")
            f.write("@Grid HEADER, GRID, " + str(ZmapGridIO.nodesperline) + "\n")
            f.write(" " + str(ZmapGridIO.fieldwidth) + ", " + str(ZmapGridIO.nodata_value) + ",  , 1 , 1" + "\n")
            f.write("   " + str(ny) + ",  " + str(nx) + ",  " + str(xllcenter) + ",  " + str(hix) + ",  " + str(
                yllcenter) + ",  " + str(hiy) + "\n")
            f.write("   " + str(dx) + ",  0.0,  0.0    " + "\n")
            f.write("@" + "\n")

            for n in range(z.shape[1]):
                count = 0
                for m in range(z.shape[0] - 1, -1, -1):
                    count += 1
                    if np.isnan(z[m, n]):
                        f.write(space_back_to_front(format(ZmapGridIO.nodata_value, "13.7E") + '  '))
                    else:
                        if abs(z[m, n]) >= 1E100:
                            f.write(space_back_to_front(format(z[m, n], "13.7E") + ' '))
                        elif abs(z[m, n]) >= 1E6:
                            f.write(space_back_to_front(format(z[m, n], "13.7E") + '  '))
                        else:
                            f.write(space_back_to_front("{:<13.4f}".format(z[m, n]) + '  '))
                    if count % ZmapGridIO.nodesperline == 0 or m == 0:
                        f.write("\n")


def space_back_to_front(string):
    net = string.replace(' ', '')
    return "".join(string.rsplit(net)) + net


def check_x_y_spacing(x, y, dx, dy):
    if (
            abs((x[-1] - x[0]) / (x.shape[0] - 1)) != dx
            or abs((y[-1] - y[0]) / (y.shape[0] - 1)) != dy
    ):
        raise ValueError(
            "X or Y spacing is not constant; *.zmap grid cannot be written."
        )


class CsvGridIO(GridIO):
    """
        This is a class for IO of a CSV Grid Object
        The class is not yet supported

        Methods:
             read()  :  reads a grid from (fname + CsvGridIO.SUFFIX)
             write(g: Grid) : writes the grid to (fname + CsvGridIO.SUFFIX)
    """
    FORMAT = "CSV"
    SUFFIX = ".csv"

    def read(self, fname, readhelpers=None):
        raise NotImplementedError("not implemented yet")

    def write(self, g: Grid):
        raise NotImplementedError("not implemented yet")



class VoxetGridIO(GridIO):
    """
        This is a class for IO of a Voxet Grid Object
        The class is not yet supported

        Methods:
             read()  :  reads a grid from (fname + VoxetGridIO.SUFFIX)
             write(g: Grid) : writes the grid to (fname + Arc.SUFFIX)
    """
    FORMAT = "VOXET"
    SUFFIX = ".vo"

    def read(self, fname, readhelpers=None):
        if not fname.endswith(self.SUFFIX):
            fname = fname + self.SUFFIX

        no_data_value, nx, ny, originx, originy, maxx, maxy, dx, dy = 0, 0, 0, 0, 0, 0, 0, 0, 0
        data_values = np.empty(1)
        coord_sys = EMPTY_COORD_SYS

        kindex = readhelpers['INDEX']
        prop = readhelpers['PROP']
        swapy = False
        try:
            swapy = readhelpers['SWAPY']
        except:
            pass
        try:
            v = Voxet(fname, load_prop=prop)
        except BaseException as err:
            print('reading voxet error:', err)
            raise BaseException(err)


        #v = Voxet(fname)
        if (kindex>=0):
            z, gridx, gridy, cellsize, no_data_value = v.getKslice(prop, kindex, swapy=swapy)
        else:
            propval = 0
            gettop = True
            try:
                propval = readhelpers['PROPVAL']
                gettop = readhelpers['GETTOP']
            except:
                pass
            z, gridx, gridy, cellsize, no_data_value = v.getTopBottom(prop, propval, gettop)

        return z, gridx, gridy, cellsize, no_data_value, coord_sys


    def write(self, g: Grid):
        raise NotImplementedError("not implemented yet")


class GridIOFactory:
    """
        This  class is a factory for IO objects

        static Methods:
             read_grid(fname :str , format: str)  :  reads a grid from (fname) in format, this method is discouraged,
             as the Grid constructor allows the same by Grid(fname, format)

             getGridIO (format: str) : gets an instance of the apppropriate GridIO object
    """

    @staticmethod
    def read_grid(fname: str, grid_format="ARC") -> Grid:
        return Grid(fname, grid_format=grid_format)
        # gridIO = GridTNOFactory.getGridIO(format)
        # return gridIO.fromFile(fname).grid

    @staticmethod
    def get_grid_io(grid_format: str="ARC") -> GridIO:
        """Factory Method"""
        builder = {
            ArcGridIO().FORMAT: ArcGridIO,
            ZmapGridIO().FORMAT: ZmapGridIO,
            CsvGridIO().FORMAT: CsvGridIO
        }
        f = builder[grid_format]()
        return f



class GridIOFactory:
    """
        This  class is a factory for IO objects

        static Methods:
             read_grid(fname :str , format: str)  :  reads a grid from (fname) in format, this method is discouraged,
             as the Grid constructor allows the same by Grid(fname, format)

             getGridIO (format: str) : gets an instance of the apppropriate GridIO object
    """

    @staticmethod
    def read_grid(fname: str, grid_format="ARC") -> Grid:
        return Grid(fname, grid_format=grid_format)
        # gridIO = GridTNOFactory.getGridIO(format)
        # return gridIO.fromFile(fname).grid

    @staticmethod
    def get_grid_io(grid_format: str="ARC") -> GridIO:
        """Factory Method"""
        builder = {
            ArcGridIO().FORMAT: ArcGridIO,
            ZmapGridIO().FORMAT: ZmapGridIO,
            CsvGridIO().FORMAT: CsvGridIO,
            VoxetGridIO().FORMAT: VoxetGridIO
        }
        f = builder[grid_format]()
        return f
