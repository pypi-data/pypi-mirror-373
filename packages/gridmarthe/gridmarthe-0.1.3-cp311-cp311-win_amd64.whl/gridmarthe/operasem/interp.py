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
""" Interpolation and regridding module
"""


import numpy as np
import xarray as xr #needs netcdf4, rioxarray

from ..utils import _get_scale


def get_new_coords(ds, res=1000):
    """ Reset xy with a range from min to max, with res as step"""
    xmin, xmax = np.min(ds.x).values, np.max(ds.x).values
    ymin, ymax = np.min(ds.y).values, np.max(ds.y).values
    
    new_x = np.arange(xmin, xmax+res, res)
    new_y = np.arange(ymin, ymax+res, res)
    
    return new_x, new_y


def interp_grid(da, new_x=None, new_y=None, method='nearest', **kwargs):
    """ Interpolate on a new grid using `xarray.Dataset.interp`

    Parameters
    ----------
    da: xr.Dataset
        the input dataset to interpolate on new coordinates.
    new_x: array-like
        the new x-axis coordinate to use
    new_y: array-like
        the new y-axis coordinate to use
    method: str, Optionnal (default='nearest')
        `xr.Dataset.interp` method to use. Default is 'nearest'
    **kwargs: dict, Optionnal.
        Any keywords argument to pass to `xr.Dataset.interp`.
    
    Returns
    -------
        interpolated xr.Dataset
    """
    # https://docs.xarray.dev/en/stable/user-guide/interpolation.html
    # https://earth-env-data-science.github.io/lectures/xarray/xarray-part2.html
    if new_x is None or new_y is None:
        new_x = np.linspace(da['x'][0], da['x'][-1], int(da['x'].size / 2) ) # da.dims["lat"]
        new_y = np.linspace(da['y'][0], da['y'][-1], int(da['y'].size / 2) )
    return da.interp(x=new_x, y=new_y, method=method, **kwargs)


def rescale_grid(da, res=1000, **kwargs):
    """ Wrapper function that uses `get_new_coords()` and `interp_grid()` together
    
    See also
    --------
    `get_new_coords`
    `interp_grid`
    """
    new_x, new_y = get_new_coords(da, res)
    new_da = interp_grid(da, new_x, new_y, **kwargs) # here da with assign coords
    return new_da


def coarse_nested_grid(da, varname='charge', dx=None, dy=None):
    """ Coarse nested grid to res of main grid
    only realy valid if nested grid resolution is a multiple of maingrid resolution
    coords needs to be assign first
    """
    if dx is None or dy is None:
        dx, dy = _get_scale(da)
    dx1, dy1 = dx.pop(0), dy.pop(0)
    grid = da.where(da['dx'] == dx1, drop=True) # & da['dy'] == dy1
    for dx2, dy2 in zip(dx, dy):
        gig = da.where(da['dx'] == dx2, drop=True)
        gig = gig[varname].coarsen(x=int(dx1/dx2), y=int(dy1/dy2), boundary='trim').mean()
        grid = xr.combine_by_coords([grid, gig])
    return grid


def aggregate_to_grid(value_grid, target_grid):
    # Définir un facteur d'agrégation basé sur les résolutions
    factor_x = int(round((value_grid.x.size / target_grid.x.size)))
    factor_y = int(round((value_grid.y.size / target_grid.y.size)))

    # Vérifier que le facteur est valide
    if factor_x > 1 and factor_y > 1:
        value_grid_coarse = value_grid.coarsen(x=factor_x, y=factor_y, boundary="trim").mean()
    else:
        raise ValueError("Les tailles des grilles ne permettent pas une agrégation nette.")
    return value_grid_coarse
