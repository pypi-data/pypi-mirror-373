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
from datetime import datetime
import pandas as pd
import numpy as np

from typing import Union


def _datetime64_to_float(zdates, origin='1970-01-01T00:00:00'):
    # Memo: here, origin should be defined from pastp (time since timestep 0)
    idate = (zdates - np.datetime64(origin)) / np.timedelta64(1, 's')
    idate = np.where(idate < 0., 0., idate) # fake dates from load_marthe_grid will be set to 0, meaning timestep -9999. (eg used in parameters grids)
    return idate


def _is_sorted(a):
    return np.all(a[:-1] <= a[1:])


def _get_scale(da):
    """ Get unique values of dx, dy marthegrid.Dataset """
    dx = np.sort(np.unique(da['dx'].values))[::-1]
    dy = np.sort(np.unique(da['dx'].values))[::-1]
    return list(dx[~np.isnan(dx)]), list(dy[~np.isnan(dy)])


def _find_nearest(array, value):
    # https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def _nearest_node(node, nodes):
    """ Get nearest value in an array of tuple, i.e closest euclidiant distance of XY in an array of XYs"""
    # https://codereview.stackexchange.com/questions/28207/finding-the-closest-point-to-a-list-of-points
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node)**2, axis=1)
    return np.argmin(dist_2)


def read_dates_from_pastp(fpastp, encoding='ISO-8859-1'):
    """Read simulation timesteps from a .pastp file
    """
    # reading file as raw df - not str ; faster with pandas func
    pastp = pd.read_csv(
        fpastp,
        header=None,
        encoding=encoding
    ).squeeze('columns')

    # First, get steady state time
    idx_0  = pastp.loc[pastp.str.contains(r' \*\*\* D.*but de la simulation.*', regex=True)].index.values[0]
    date_0 = re.findall(r'[0-9]+', pastp.iloc[idx_0] )
    
    # convert as DF
    timesteps = pd.DataFrame([{
        'timestep': 0, 
        'date': datetime(int(date_0[2]), int(date_0[1]), int(date_0[0]) ) 
    }])

    # Then, get all ending times for transient state
    idx  = pastp.loc[pastp.str.contains(r'^ \*\*\* Le pas.*\d+: se termine.*', regex=True)]
    # extract dates from strings
    dates= pd.DataFrame(
        idx.str.findall(r'[0-9]+').to_list(),
        columns=['timestep', 'day', 'month', 'year'],
        #dtype={'timestep':int, 'day':int, 'month':int, 'year':int}
    )
    
    # assign dtype
    dates['timestep'] = pd.to_numeric(dates['timestep'])

    # convert data as datetime object
    dates['date'] = pd.to_datetime(dates[['day', 'month', 'year']])
    dates = dates.drop(['month','year', 'day'], axis=1)
    
    return pd.concat([timesteps, dates], axis=0)


def dropna(ds, varname: str, nanval: Union[list, float]):
    """ Drop values corrresponding to NaN (marthe convention, eg. code 9999.) 
    for 1D (or 2D (time, zone)) array
    zone must me a coordinate dimension.
    
    Returns
    -------
    dataset where variable != nanval
    """
    if isinstance(nanval, (float, int, str)):
        nanval = [nanval]
    elif isinstance(nanval, tuple):
        nanval = list(nanval)  # convert to list to be mutated
    nanval += [1.e+20]
    mask = ds[varname.lower()].where(~ds[varname.lower()].isin(nanval)).dropna(dim='zone') # drop nanval
    ds_no_nan = ds.sel(zone=mask['zone'])
    return ds_no_nan


def subset(ds, varname: str, value: Union[list, float]):
    """ Subset dataset based on variable name and value.
    --> inverse of :py:func:`dropna`
    
    Returns
    -------
    dataset where variable = value
    """
    if isinstance(value, (float, int, str)):
        value = [value]
    mask = ds[varname.lower()].where(ds[varname.lower()].isin(value)).dropna(dim='zone')
    ds_filter = ds.sel(zone=mask['zone'])
    return ds_filter


def replace(ds, varname: str, value: float, replace: float):
    """ Replace a value in xr.Dataset for a variable
    """
    ds[varname].data = np.where(ds[varname].data == value, replace, ds[varname].data)
    return ds


def fillna(ds, varname, value):
    """ Replace real nan (np.nan) value in dataset[varname], edge case of :py:func:`replace()`
    """
    ds[varname].data = np.where(np.isnan(ds[varname].data), value, ds[varname].data)
    return ds


def assign_coords(da_in, add_lay=True, coords=['x', 'y', 'z'], keep_zone=False, zone_label='zone'):
    """ assign coords to transform a 1D or 2D (time, zone) array to 3D or 4D
    """
    if len(coords) == 3:
        z_coords = da_in.get(coords[2], None) # assert z is here, or bypass
    else:
        z_coords = None
    
    if add_lay is False:
        # in some case, even if z is included it should not be treated as coord (ex. plot outcrop)
        z_coords = None
    
    da = da_in.assign_coords(
        #x=(zone_label, np.around(da_in[coords[0]].data, 1) ),
        x=(zone_label, da_in[coords[0]].data ),
        y=(zone_label, da_in[coords[1]].data ),
    )
    dims = ['y', 'x']
    
    if z_coords is not None:
        da = da.assign_coords(z=(zone_label, da_in[coords[2]].data))
        dims.insert(0, 'z')
    
    da = da.set_index(zone=dims)
    if not keep_zone:
        da = da.drop_duplicates(zone_label).unstack(zone_label)  # drop duplicates is a security for nested grids, if dropnan was not performed
    return da.sortby(dims)


def stack_coords(ds, coords=['z', 'y', 'x'], dropna=False):
    """ Transform a 3 or 4D aray into 1 or 2D array 
    inverse of  :py:func:`assign_coords`
    """
    # create zone index
    coords = [d for d in coords if d in ds.coords.keys()] # make sure to drop coords that are not present
    dims = np.prod( [len(ds[d]) for d in coords] ) # create new zone dim
    zone = np.arange(dims)
    
    # stack coords
    ds2 = ds.copy().stack(zone=coords) # multiindex zone grouping coords key
    
    # keep only zone as dim
    ds3 = ds2.drop_vars(['zone'] + coords).assign_coords(zone=('zone', zone))
    
    # get back xy[z] as var
    for c in coords:
        ds3[c] = ('zone', ds2[c].data)
    
    if dropna:
        ds3 = ds3.dropna(dim='zone')
    return ds3
