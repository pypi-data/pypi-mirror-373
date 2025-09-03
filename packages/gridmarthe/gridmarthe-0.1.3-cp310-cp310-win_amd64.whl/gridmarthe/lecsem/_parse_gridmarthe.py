#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
#
#    This file is part of gridmarthe.
#
#    gridmarthe is a python library to manage grid files for 
#    MARTHE hydrogeological computer code from French Geological Survey (BRGM).
#    Copyright (C) 2024  BRGM
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import re
import numpy as np

from .lecsem import modgridmarthe
from ..utils import _datetime64_to_float


def scan_var(xfile):
    """ List all variables stored in a Marthe grid file """
    var = modgridmarthe.scan_typevar(xfile)  # get a list of unique type_var that are in xfile
    var = np.char.strip(np.char.decode(var, 'ISO-8859-1'))  # decode byte array provided by f2py
    var = var[var != '']  # get rid of empty element provided by fortran code
    return var


def _read_marthe_grid(xfile, varname='CHARGE', shallow_only=False):
    """ Read a Marthe grid file
    using fortran wrapper, for a specific variable
    
    Parameters
    ----------
    xfile: str
        Filename to read
    varname : str
        string of variable in xfile to get values.
        Default is CHARGE (groundwater head)
    
    Returns
    -------
    zvar  : np.array
        variable read from marthe grid file as numpy ndarray (one vector)
    zdates: np.array
        array of dates (from start))
    isteps: np.array
        array of indexes of timesteps
    zxcol : np.array
        array of x coordinates
    zylig : np.array
        array of y coordinates
    zdxlu : np.array
        array of dx (equals np.diff(x))
    zdylu : np.array
        array of dy (equals np.diff(y))
    ztitle: np.array
        title of marthe grid file read
    dims  : np.array
        list of dimensions of grid [maingrid[x, y, z], nestedgrid1[...], ...]
    """
    nu_zoomx = modgridmarthe.scan_nu_zoomx(xfile) # scan nb of nested grids (gig)
    dims, nbsteps = modgridmarthe.scan_dim(xfile, varname, nu_zoomx)
    nbtot = np.prod(dims, axis=1).sum() # product deprecated => prod // DeprecationWarning: `product` is deprecated as of NumPy 1.25.0, and will be removed in NumPy 2.0. Please use `prod` instead.
    if nbtot == 0:
        raise ValueError(f'Varname ({varname}) not found in xfile. No data to parse.')
    
    if shallow_only:
        res = list(modgridmarthe.read_grid_shallow( xfile, varname, nbsteps, dims[0][-1] ,nbtot, nu_zoomx ))
    else:
        res = list(modgridmarthe.read_grid( xfile, varname, nbsteps, nbtot, nu_zoomx))
    
    res.append(dims)
    return res


def _transform_xcoords(zxcol, zylig, zdxlu, nlayer=1, factor=1):
    xcols, dxlus = [], []
    for igig in range(zxcol.shape[0]):
        nb = np.extract(zylig[igig] != 1e+20, zylig[igig]).shape[0]
        xcols2 = np.tile(zxcol[igig], nb)
        xcols2 = np.extract(xcols2 != 1e+20, xcols2)
        dxlus2 = np.tile(zdxlu[igig], nb)
        dxlus2 = np.extract(dxlus2 != 1e+20, dxlus2)
        if nlayer > 1:
            # need to paste coords for multilayer to match dims of zvar
            xcols2 = np.tile(xcols2, nlayer)
            dxlus2 = np.tile(dxlus2, nlayer)
        xcols.append(xcols2)
        dxlus.append(dxlus2)
    xcols = np.hstack(xcols)*factor
    dxlus = np.hstack(dxlus)*factor
    return xcols, dxlus


def _transform_ycoords(zxcol, zylig, zdylu, nlayer=1, factor=1):
    yligs, dylus = [], []
    for igig in range(zylig.shape[0]):
        yligs2, dylus2 = [], []
        for i in range(len(zxcol[igig][zxcol[igig] != 1e+20])):
            tmp1 = zylig[igig][zylig[igig] != 1e+20]
            tmp2 = zdylu[igig][zdylu[igig] != 1e+20]
            if nlayer > 1:
                # need to paste coords for multilayer to match dims of zvar
                tmp1 = np.tile(tmp1, nlayer)
                tmp2 = np.tile(tmp2, nlayer)
            yligs2.append(tmp1)
            dylus2.append(tmp2)
        yligs2 = np.vstack(yligs2).transpose().flatten()
        dylus2 = np.vstack(dylus2).transpose().flatten()
        yligs.append(yligs2)
        dylus.append(dylus2)
    yligs = np.hstack(yligs)*factor
    dylus = np.hstack(dylus)*factor
    return yligs, dylus


def _set_layers(dims):
    # add layer to match dim of zvar
    zlay = []
    for igig in range(len(dims)):
        for z in range(dims[igig][-1]):
            zlay.append(np.tile(z+1, dims[igig][0] * dims[igig][1]))
    zlay = np.hstack(zlay)
    return zlay.astype(np.int32)


def _decode_title(title, encoding='ISO-8859-1'):
    title = title.decode(encoding)
    title = re.search(r'(\D+)\s+Pas\s+\d+;', title)
    if title is not None:
        return title.group(1).strip()
    else:
        return None


def _get_col_and_lig(dims):
    """ Add col/lig indexes (i,j) """
    # cols are xcoords index (x are sorted asc)
    # ligs are ycoords index (y are sorted dsc)
    # dims = [maingrid[x, y, z], gig[x, y, z], ...]
    # cols and lig indexes are a range from 1 to len(x), for each grid. Same index col/lig, for every layer (z dim).
    cols, ligs = [], []
    for grid in dims:
        zcols = np.arange(1, grid[0]+1)
        zligs = np.arange(1, grid[1]+1) # lig 0 is max y ; max lig is min y.
        # add res tiled on y and z dims, for xcols
        cols = np.append(cols, np.tile(zcols, grid[-1] * grid[1]))
        # for ylig, it's a bit different, we need to map ylig on shape of xcol for each ylig, then tile on z dim
        # e.g. we need:
        # [xcol] 1, 2, 3, 4, 5
        # [ylig]   [ value ]
        # 1,     1  1  1  1  1
        # 2,     2  2  2  2  2
        # 3,     ...
        # but flattened, so: repeat ylig value on xcol size, then tile on z_dim size
        ligs = np.append( ligs, np.tile( np.repeat(zligs, zcols.shape[0]), grid[-1] ) )
    return cols.astype(np.int32), ligs.astype(np.int32)


def _get_id_grid(dims):
    # add id grid : 0 = main grid, >0 = nested grid(s)
    id_grids = []
    for igig in range(len(dims)):
        id_grids.append(np.tile(igig, np.prod(dims[igig])))
    id_grids = np.hstack(id_grids)
    return id_grids


def _parse_dims_from_xr_attrs(str_dims):
    if str_dims is None:
        return None
    else:
        return [list(map(int, x.split(' '))) for x in str_dims.strip('x, y, z [grids]: ').split('; ')]


# def sort_data(ds):
    # TODO:
    # s'assurer de l'ordre si ds a été retravaillé :
        # order by z, y, x, dx
    # extraire les x, y, dx, dy selon dims = pas de doublons
    # print('not yet available')


def _extract_zvar_from_ds(ds, varname):
    
    zvar    = ds[varname].data
    zdates  = ds.time.data
    zxcol   = ds.x.data
    zylig   = ds.y.data
    zdxlu   = ds.dx.data
    zdylu   = ds.dy.data
    ztitle  = ds.attrs.get('title')
    izdates = _datetime64_to_float(zdates)

    return (
        zvar, zdates,
        zxcol, zylig, zdxlu, zdylu,
        ztitle, izdates
    )


if __name__ == '__main__':
    
    # print(_lecsem.__doc__)
    print(modgridmarthe.__doc__)
    

