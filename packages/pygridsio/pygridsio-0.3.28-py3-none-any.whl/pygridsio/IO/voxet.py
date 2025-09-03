"""
GOCAD (http://www.gocad.org) utilities
"""
from __future__ import annotations

import os
import numpy as np
from pygridsio.IO.gocad import header

#        NOTE: This file should not be removed or modified without first consulting Jan Diederik van Wees (Jan_Diederik.vanWees@tno.nl)
#        This class is used by PyGridsio to read in and write out .asc and .zmap files; Jan Diederik also uses it as the backbone grid class for other projects such as ga4a.
#        This statement is valid from 04/06/2025 until agreed otherwise.


def write_property_to_gocad_voxet(propertyfilename, propertyvalues):
    """
    NOTE: This class should not be removed or modified without first consulting Jan Diederik van Wees (Jan_Diederik.vanWees@tno.nl)
        This class is used by PyGridsio to read in and write out .vo files; Jan Diederik also uses it as the backbone grid class for other projects such as ga4a.
        This statement is valid from 04/06/2025 until agreed otherwise.

    This function writes a numpy array into the right format for a gocad
    voxet property file. This assumet there is a property already added to the .vo file,
    and is just updating the file.
    propertyfile - string giving the path to the file to write
    propertyvalues - numpy array nz,ny,nx ordering and in float format

     call like : # copy files from structural lab to the blank results folder
    write_property_to_gocad_voxet('Hecho\\Results_/ResultVoxetResultBox_Strati@@',array)
    """
    propertyvalues = propertyvalues.astype('>f4') #big endian
#     array = propertyvalues.newbyteorder()
    propertyvalues.tofile(propertyfilename)

class Voxet:

    PROP = 'PROP'
    AXIS = 'AXIS'
    HEADER = 'HEADER'
    READALLPROP ='READALLPROP'
    def __init__(self, filename: str, load_prop='READALLPROP', nodata_value='nan'):
        self.z: np.ndarray | None = None
        self.gridx: np.ndarray | None = None
        self.gridy: np.ndarray | None = None
        self.orx: float | None = None
        self.ory: float | None = None
        self.orz: float | None = None
        self.dx: float | None = None
        self.dy: float | None = None
        self.dz: float | None = None

        self.coord_sys: str | None = None

        self.fullpath: str = filename
        self.fnamebase: str = os.path.splitext(os.path.basename(self.fullpath))[0]
        self.nodata_value = nodata_value
        self.readHeader()
        self.readProp(load_prop)





    def readHeader(self ):
        """
        GOCAD voxet reader
            deploying
            fname :  voxet name (full path)
            load_prop: properties to be loaded, if none all are loaded
            nodata_value:  no data value for the properties
        """
        path = self.fullpath
        no_data_value = self.nodata_value

        print (str ('reading voxet ' + path))
        lines = open( path ).readlines()
        cast = {}
        casters = {
            str: ('NAME', 'FILE', 'TYPE', 'ETYPE', 'FORMAT', 'UNIT', 'ORIGINAL_UNIT', 'STORAGE_TYPE'),
            int: ('N', 'ESIZE', 'OFFSET', 'SIGNED', 'PAINTED_FLAG_BIT_POS'),
            float: ('O', 'D', 'U', 'V', 'W', 'MIN', 'MAX', 'NO_DATA_VALUE', 'SAMPLE_STATS'),
        }
        for c in casters:
            for k in casters[c]:
                cast[k] = c
        voxet = {}
        counter = 0
        while counter < len( lines ):
            line = lines[counter].strip()
            counter += 1
            f = line.replace('"', '').split()
            if len( f ) == 0 or line.startswith( '#' ):
                continue
            elif line.startswith( 'GOCAD Voxet' ):
                id_ = f[2]
                axis, prop = {}, {}
            elif f[0] == 'HEADER':
                hdr, counter = header( lines, counter )
            elif len( f ) > 1:
                k = f[0].split( '_', 1 )
                #print (k)
                if k[0] == 'AXIS':
                    axis[k[1]] = tuple( cast[k[1]]( x ) for x in f[1:] )
                elif f[0] == 'PROPERTY':
                    prop[f[1]] = {'PROPERTY': f[2]}
                elif k[0] == 'PROP':
                    if len( f ) > 3:
                        prop[f[1]][k[1]] = tuple( cast[k[1]]( x ) for x in f[2:] )
                    else:
                        try:
                            prop[f[1]][k[1]] = cast[k[1]](f[2])
                        except BaseException as err:
                            print('casting error in voxet keyword', err)
                            raise BaseException(err)

            elif f[0] == 'END':

                voxet[id_] = {Voxet.HEADER: hdr, Voxet.AXIS: axis, Voxet.PROP: prop}
                vindex = '1'
                self.voxetdict = voxet[vindex]
                axis = self.voxetdict[Voxet.AXIS]

                self.nx = axis['N'][0]
                self.ny = axis['N'][1]
                self.nz = axis['N'][2]

                # orx,ory,orz are set through the O UVW or through minmax, decide based on
                amin = np.asarray(axis['MIN'])
                amax = np.asarray(axis['MAX'])

                ones = np.ones(3)
                if (np.dot(amax -ones, amin)<1e-3):
                    self.orx = axis['O'][0]
                    self.ory = axis['O'][1]
                    self.orz = axis['O'][2]
                    # assume
                    self.dx = axis['U'][0]
                    self.dy = axis['V'][1]
                    self.dz = axis['W'][2]
                else:
                    # use amin and amax
                    self.orx = amin[0]
                    self.ory = amin[1]
                    self.orz = amin[2]

                    self.dx = (amax[0] - amin[0]) / (self.nx-1)
                    self.dy = (amax[1] - amin[1]) / (self.ny-1)
                    self.dz = (amax[2] - amin[2]) / (self.nz-1)



    def readProp(self, load_prop:str, swapy= False):
        """"
         load the property from the property list,
         it fills the data with flattened arrays
         the data is given a global no data value  (typically nan)
        """
        prop = self.voxetdict[Voxet.PROP]
        axis = self.voxetdict[Voxet.AXIS]
        no_data_value = self.nodata_value
        path = self.fullpath
        loadall = load_prop == Voxet.READALLPROP
        for ploop in prop:
            if (loadall or prop[ploop]['PROPERTY'] == load_prop):
                pindex = ploop
                p = prop[pindex]
                if (pindex == '-1'):
                    print(str('property ' + load_prop + ' cannot be found in Voxet '))
                f = os.path.join(os.path.dirname(path), p['FILE'])
                dtype = '>f%s' % p['ESIZE']
                data = np.fromfile(f, dtype)
                if no_data_value == 'nan':
                    data[data == p['NO_DATA_VALUE']] = np.nan
                elif no_data_value is not None:
                    data[data == p['NO_DATA_VALUE']] = no_data_value
                n = axis['N']
                pdata = data.reshape(n[::-1]).T
                if swapy:
                    pdataswap = pdata * 1.0
                    for i in range(self.nx):
                        for j in range(self.ny):
                            jj = self.ny-j-1
                            for k in range(self.nz):
                                pdataswap[i,jj,k] = pdata[i,j,k]
                    pdata = pdataswap
                p['DATA'] = pdata



    def getpropIndex(self, propname:str):
        prop = self.voxetdict[Voxet.PROP]
        for ploop in prop:
            if (prop[ploop]['PROPERTY'] == propname):
                return ploop
        return -1


    def createZvals(self):
        nx = self.nx
        ny = self.ny
        nz = self.nz
        zval = np.asarray(np.zeros(nx * ny * nz)).reshape(nx,ny,nz)
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    zval[i,j,k] =  self.orz + k*self.dz
        self.setPropValues('Z', zval, np.nan)

    def getPropValues(self, propname:str, swapy=False):
        """"
          :param propname, name of the property
          :returns data_values as float array [nx,ny,nz]
        """
        prop = self.voxetdict[Voxet.PROP]
        indexprop = self.getpropIndex(propname)
        try:
            data_values = prop[indexprop]['DATA']
        except:
            try:
                self.readProp(load_prop=propname, swapy=swapy)
                data_values = prop[indexprop]['DATA']
            except BaseException as err:
                if (propname=='Z'):
                    self.createZvals()
                    data_values = self.getPropValues('Z')
                else:
                    raise BaseException(err)

        return data_values

    def setPropValues(self, propname: str, data_values, no_data_value):
        prop = self.voxetdict[Voxet.PROP]
        indexprop = self.getpropIndex(propname)
        if (indexprop >= 0):
            prop[indexprop]['DATA'] = data_values
        else:
            indexprop = str(len(prop)+1)
            p= {}
            p['PROPERTY'] = propname
            p['DATA'] = data_values
            p['NO_DATA_VALUE'] = no_data_value

            prop[indexprop]= p
        return

    def getTopBottom(self, propname:str, propval:float, gettop=True):
        """
        get a grid as the top of bottom bounds of cells

        :param propname: property name to use for the bounds
        :param propval:  property value to limit the bounds
        :param gettop:  get the top or the bottom
        :return:  grid with the vaues
        """
        try:
            data_values = self.getPropValues(propname)
        except BaseException as err:
            print ('Voxet::getTopBottom unable to get properties for ', propname, err)
            raise BaseException(err)
        try:
            data_z = self.getPropValues('Z')
        except BaseException as err:
            print ('Voxet::getTopBottom unable to get properties for ', 'Z', err)
            raise BaseException(err)
        nx = self.nx
        ny = self.ny
        nz = self.nz
        originx = self.orx
        originy = self.ory

        z = np.empty([ny, nx])
        for n in range(nx):
            for m in range(ny):
                z[m, n] = self.nodata_value
                idtop = -1
                idbase = -1
                for kindex in range(nz):
                    if abs(propval-data_values[n,m,kindex])<1e-3:
                       if (idtop < 0):
                            idtop = kindex
                       idbase = kindex
                ztb = self.nodata_value
                if (idtop>=0):
                    if (gettop):
                        ztb = data_z[n,m,idtop]
                        if (idtop>0):
                            ztb -= 0.5 * ( ztb-data_z[n,m,idtop-1])
                    else:
                        ztb = data_z[n, m, idbase]
                        if (idbase < nz-1):
                            ztb += 0.5 *( data_z[n, m, idbase + 1] - ztb)
                z[m, n] = ztb

        dx = self.dx
        dy = self.dy

        gridx = np.arange(originx, originx + nx * dx - 1e-3, dx)
        gridy = np.arange(originy, originy + ny * dy - 1e-3, dy)
        cellsize = (dx, dy)
        return z, gridx, gridy, cellsize, float(self.nodata_value)


    def getKslice(self, propname:str, kindex:int, swapy=False):
        try:
            data_values = self.getPropValues(propname)
        except BaseException as err:
            print ('Voxet::getKslice unable to get properties for ', propname, err)
            raise BaseException(err)
        nx = self.nx
        ny = self.ny
        originx = self.orx
        originy = self.ory

        z = np.empty([ny, nx])
        for n in range(nx):
            for m in range(ny):
                mm = m
                if swapy:
                    mm = ny-m-1
                z[mm, n] = data_values[n, m, kindex]
        dx = self.dx
        dy = self.dy

        gridx = np.arange(originx, originx + nx * dx - 1e-3, dx)
        gridy = np.arange(originy, originy + ny * dy - 1e-3, dy)
        cellsize = (dx, dy)
        return z, gridx, gridy, cellsize, float(self.nodata_value)

    def getXy(self, i,j):
        x = self.orx+ i*self.dx
        y = self.ory+ j*self.dy
        return np.asarray([x,y])

    def write (self, outfnamebase=None):
        """
        write gocad voxet file and properties
        :param  outfnamebase: output filename (exluding .vo), if omitted it will use the existing filename
                this name excludes the file path and will write
        """
        fnamebase = self.fnamebase
        if (outfnamebase!=None):
            fnamebase = outfnamebase
        basedir = os.path.dirname (self.fullpath)
        # Create the output .vo file.
        # This file just contains text metadata which describes the data.
        print('Writing output .vo file')
        output_filename_vo = os.path.join(basedir, fnamebase + '.vo')
        with open(output_filename_vo, 'wt') as output_file_vo:

            output_file_vo.write('GOCAD Voxet 1\n')

            output_file_vo.write('HEADER {\n')
            output_file_vo.write(' name:density2\n')
            output_file_vo.write('*painted:on\n')
            output_file_vo.write('	         *painted*variable:density\n')
            output_file_vo.write(' *regions*painted_grid:density\n')
            output_file_vo.write('last_selected_folder:Property Sections\n')
            output_file_vo.write('*psections*solid:true\n')
            output_file_vo.write('*density*psections:1 1 1 1 1 1 1 1 1 0\n')
            output_file_vo.write('*psections*grid:false\n')
            output_file_vo.write('properties_movie:off\n')
            output_file_vo.write('movie:on\n')
            output_file_vo.write('*movie_property:density\n')
            output_file_vo.write('*low_clip:0\n')
            output_file_vo.write('*colormap*low_clip_transparent:false\n')
            output_file_vo.write('*colormap*high_clip_transparent:false\n')
            output_file_vo.write('*high_clip:1500\n')
            output_file_vo.write('ascii:off\n')
            output_file_vo.write('}\n')
            output_file_vo.write('GOCAD_ORIGINAL_COORDINATE_SYSTEM\n')
            output_file_vo.write('NAME Default\n')
            output_file_vo.write('AXIS_NAME \"X\" \"Y\" \"Z\"\n')
            output_file_vo.write('AXIS_UNIT \"m\" \"m\" \"ms\"\n')
            output_file_vo.write('ZPOSITIVE Depth\n')
            output_file_vo.write('END_ORIGINAL_COORDINATE_SYSTEM\n')

            # Write out the origin.
            # This is offset so that a minimum block at x,y,z = 1,1,1 will be at 0,0,0.
            output_file_vo.write( 'AXIS_O %f %f %f\n' % (self.orx,self.ory,self.orz  ))
            # Write out the size of each dimension.
            output_file_vo.write('AXIS_U %f 0 0\n' % (self.dx ))
            output_file_vo.write('AXIS_V 0 %f 0\n' % (self.dy ))
            output_file_vo.write('AXIS_W 0 0 %f\n' % (self.dz ))
            output_file_vo.write('AXIS_MIN 0 0 0\n')
            output_file_vo.write('AXIS_MAX 1 1 1\n')
            # Write out the number of blocks.
            output_file_vo.write('AXIS_N %d %d %d\n' % (self.nx, self.ny, self.nz))
            output_file_vo.write('AXIS_NAME "axis-1" "axis-2" "axis-3"\n')
            output_file_vo.write('AXIS_UNIT " number" " number" " number"\n')
            output_file_vo.write('AXIS_TYPE even even even\n')
            # Write out the property definition.
            output_file_vo.write('\n')

            prop = self.voxetdict[Voxet.PROP]
            for ploop in prop:
                iplus1 = int(ploop)
                p = prop[ploop]
                propname = p['PROPERTY']
                propnodatavalue = p['NO_DATA_VALUE']
                output_file_vo.write('PROPERTY %d "%s"\n' % (iplus1,propname))
                output_file_vo.write('PROPERTY_CLASS %d "%s"\n' % (iplus1,propname))
                output_file_vo.write('PROPERTY_CLASS_HEADER %d "%s" {\n' % (iplus1,propname))
                output_file_vo.write(' *pclip:99\n')
                output_file_vo.write('last_selected_folder:Property\n')
                output_file_vo.write('*colormap*low_clip_transparent:true\n')
                output_file_vo.write('*colormap*high_clip_transparent:true\n')
                output_file_vo.write('*scale_function:linear\n')
                output_file_vo.write('*low_clip:200\n')
                output_file_vo.write('*high_clip:4386.596\n')
                output_file_vo.write('}\n')
                output_file_vo.write('PROP_ORIGINAL_UNIT %d  none\n' % iplus1)
                output_file_vo.write('PROP_UNIT %d  none\n' % iplus1)
                output_file_vo.write('PROP_NO_DATA_VALUE %d %f\n' % (iplus1,propnodatavalue))
                output_file_vo.write('PROP_SAMPLE_STATS %d  75000 1367.9 108839 50 1500\n' % iplus1)
                output_file_vo.write('PROP_ESIZE %d 4\n' % iplus1)
                output_file_vo.write('PROP_ETYPE %d IEEE\n' % iplus1)
                output_file_vo.write('PROP_FORMAT %d RAW\n' % iplus1)
                output_file_vo.write('PROP_OFFSET %d 0\n' % iplus1)
                propfile = str('%s_%s@@'% ( fnamebase, propname) )
                output_file_vo.write('PROP_FILE %d %s\n' % (iplus1, propfile))
                # needs to
                propertyfilename = os.path.join(basedir,propfile)
                data_values = self.getPropValues(propname)
                # make a copy and replace the no data values with the original from reading
                nx = self.nx
                ny = self.ny
                nz = self.nz
                z2 = np.empty([nz, ny, nx])
                for n in range(nx):
                    for m in range(ny):
                        for k in range(nz):
                          v = data_values[n,m, k]
                          if (np.isnan(v) or (v==self.nodata_value)):
                              v = propnodatavalue
                          z2[k,m,n] = v
                write_property_to_gocad_voxet(propertyfilename,z2)



            # Write the end of the file.
            output_file_vo.write('\n')
            output_file_vo.write('END\n')




