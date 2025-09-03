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


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'gridmarthe.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

import xarray as xr
from typing import Union

from .__version__ import __version__
from .gridmarthe import *
from .operasem import *
from .plot import plot_nested_grid, plot_outcrop


@xr.register_dataset_accessor('mart')
class MartheGrid(object):
    """ A Marthe grid attributes/methods accessor for xarray.Dataset objects
    
    Example
    --------
    >>> ds = gm.load_marthe_grid(**kwargs)
    >>> ds.mart.dropna('permeab', 0.)
    
    """
    def __init__(self, xr_obj: Union[xr.Dataset, None] = None):
        self.obj = xr_obj
    
    def assign_coords(self, add_lay=True):
        return assign_coords(self.obj, add_lay)
    
    def stack_coords(self, coords=['z', 'y', 'x']):
        return stack_coords(self.obj, coords)
    
    def to_geodataframe(self, epsg='EPSG:27572', fmt='long'):
        # from .mgrid_utils import to_geodataframe
        return to_geodataframe(self.obj, epsg, fmt)
    
    def to_recarray(self):
        """ return a np.recarray from pymarthe compatibility """
        # TODO, add pymarthe requested informations (i, j, etc.) => grid should be read with `add_grid_id`, and `keep_col` options.
        df = self.obj.to_dataframe()
        return df.to_records()
    
    def to_raster(self, x_dim='x', y_dim='y', time=None, epsg=27572, filename_tpl='raster'):
        """ Write raster file for a specific timestep (or all) from dataset 
        Warning, only functionnal for regular grids
        """
        if time is None:
            time = self.obj.times  # if not defined, get all available times
        if isinstance(time, str):  # make sure to get a iterable for slicing
            time = [time]
        
        for t in time:
            to_raster(self.obj.sel(time=slice(t)), x_dim, y_dim, epsg, "{}_{}.tiff".format(filename_tpl, t))
        
        return None
    
    def subset_coords(self, dims=['x', 'y'], gdf=None, xmin=None, ymin=None, xmax=None, ymax=None):
        return subset_with_coords(self.obj, dims, gdf, xmin, ymin, xmax, ymax)
    
    def dropna(self, varname='charge', nanval=9999.):
        ds = self.obj.copy()
        masque = ds[varname].where(ds[varname] != nanval).dropna(dim='zone') # drop nanval
        return ds.sel(zone=masque['zone'])
