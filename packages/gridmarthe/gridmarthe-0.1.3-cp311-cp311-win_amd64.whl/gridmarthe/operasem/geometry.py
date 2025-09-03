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

""" Module to manage geometry attributes of Marthe grids/domain
"""

import numpy as np
import xarray as xr

from .gis import to_geodataframe
from ..utils import _nearest_node, subset


def _get_mask_array(ds, varname: str='permeab', nanval: list=[-9999., 0.]):
    """ Get mask array of active domain, from permh file (hydraulic conductivity)
    """
    return ds.where(~ds[varname].isin(nanval), drop=True)


def get_active_mask(ds, varname: str='permeab', nanval: list=[-9999., 0.], as_array=False, shp_file=None):
    """ Filter dataset on non-nan values, and dissolve results to get a mask shape 
    input ds should be the permh dataset (read from permh file, ie Horizontal hydraulic conductivity)
    
    Parameters
    ----------
    
    ds : xr.Dataset
    
    varname: str, optional
        default is 'permeab'
    
    nanval: float or list, optional.
        default are 'permeab' nan values : 0,-9999.
    
    as_array: bool, optional.
        default is False. Option to get result as a xr.Dataset and not geodataframe.
        
    shp_file: str, optional.
        if set (and not `as_array`), used to stored result in a file.
    
    Returns
    -------
    either a xr.Dataset filter to mask array or a
    gpd.GeoDataFrame with active domain.
    """
    mask = _get_mask_array(ds, varname, nanval)
    mask = ds.sel(zone=mask['zone'])
    if not as_array:
        gdf  = to_geodataframe(mask)
        gdf  = gdf.dissolve()
        if shp_file is not None:
            gdf.to_file(shp_file)
        return gdf
    return mask


def _get_true_topo(topo, key='h_topogr'):
    # in Marthe, topography is stored in the first layer,
    # for the whole domain, avoiding duplicates data.
    # Here, this function tile topography to all layers
    # to allow vectorized operations.
    ds = topo.copy()
    if 'z' not in list(topo.dims) + list(topo.keys()):
        zdim = 1
    else:
        zdim = len(np.unique(topo.z.data))
    true_topo = subset(topo, 'z', 1)[key].data  # true topo is only 1st layer
    true_topo = np.tile(true_topo, zdim)  # set topo for all layers
    ds[key] = (('time', 'zone'), true_topo)
    return ds


def _get_upper_alt(topo, hsubs):
    """ Compute upper altitude of cells by layer
    Topo should contains the same values in all layers, see :py_func:`_get_true_topo`

    TODO: make valid version with time (if topo change with times)

    Parameters
    ----------

    Returns
    -------
    dataset with only (time,zone), (h_topogr, h_substr, h_upper)
    """
    ds = xr.combine_by_coords([topo, hsubs], combine_attrs='override')
    
    df = ds.isel(time=0).to_dataframe().reset_index()  # time is constant! TODO change this/ check if working
    df = df.sort_values(by=['x', 'y', 'z']).copy()  # assure data are sort in this way
    # set nans for topo and hsubs
    # this is constant in Marthe / should not be changed by user
    for x in ['h_substrat', 'h_topogr']:
        df[x] = df[x].replace(9999., np.nan)  # avoid doing this on full df, zone might be impacted
    
    # Compute z top of layers
    df['h_topogr'] = df.groupby(['x', 'y'])['h_topogr'].transform('first')  # topo is always first of group
    df['tmp']      = df.groupby(['x', 'y'])['h_substrat'].ffill()  # ffill z down for each group
    df['h_upper']  = df.groupby(['x', 'y'])['tmp'].shift(1)  # then shift to initiate z top
    # For the first layer (or if h_upper is NaN but h_substrat is valid), then h_topogr is z upper (first layer)
    mask = (df['h_upper'].isna()) & (df['h_substrat'].notna())
    df.loc[mask, 'h_upper'] = df.loc[mask, 'h_topogr']

    # debug
    # df.to_csv('toto.csv')

    # # switch back to xarray backend
    ds = df.set_index(['time','zone'])[['h_topogr', 'h_substrat', 'h_upper']].to_xarray()
    return ds


def _get_thickness(h_upper, hsubs):
    """ Compute layer thickness from upper altitudes
    and substratums.

    See, :py_func:`_get_upper_alt`
    """
    return h_upper - hsubs


def _get_depth(topo, h_upper):
    return topo - h_upper


def compute_geometry(topo, hsubs, mask=None):
    """ Compute geometry attributes of Marthe domain

    Parameters
    ----------
    topo : xr.Dataset
        Topgraphy of the domain (stored in the first layer, in Marthe Conventions).
    hsubs : xr.Dataset
        altitude of all the lower boundary in the domain
    mask : numpy.array
        list of indices (`zone`) to keep, if None (default) not used.

    Returns
    -------
    xr.Dataset
        A new dataset with layer, depth, thickness, upper/lower altitude.
    """

    # compute elements of geometry
    xtopo = _get_true_topo(topo)  # map topo values to all layers
    xhsubs = hsubs.copy()
    
    if mask is not None:
        xtopo  = xtopo.sel(zone=mask)
        xhsubs = xhsubs.sel(zone=mask)
    
    tmp   = _get_upper_alt(xtopo, xhsubs)
    thick = _get_thickness(tmp['h_upper'].data, tmp['h_substrat'].data)
    depth = _get_depth(tmp['h_topogr'].data, tmp['h_upper'].data)
    
    # put values in xr.Dataset
    # ds = xr.combine_by_coords([ds, tmp])
    ds = xtopo.copy()
    ds['z_lower']    = (('time', 'zone'), tmp['h_substrat'].data)
    ds['z_upper']    = (('time', 'zone'), tmp['h_upper'].data)
    ds['thickness']  = (('time', 'zone'), thick)
    ds['depth']      = (('time', 'zone'), depth)
    return ds


def get_surface_layer(ds, aquif_layers=None):
    """ Compute surface mask of marthe domain
    
    This function return min layer for every zone of a grimarthe dataset with z coords
    A subset on specific (aquifers) layers can be performed with `aquif_layers`.
    if set, aquif_layers must be a sequence (list, tuple, array) of layer (list of int).
    
    This should be used to get a surface mask, ie get zone to filter a dataset.
    
    Examples
    --------
    >>>    mask = get_surface_layer(ds, [6,8,9])
    >>>    ds_surf = ds.sel(zone=mask.zone.data)
        
    Parameters
    ----------
        ds: xr.Dataset
        aquif_layers: sequence (list, tuple, array) of int
            representing layers to subset ds. Only active domain must 
            be passed to function (ie drop nan first)
            
    Returns
    -------
        surface_mask: xr.Dataset
    """
    df = ds.to_dataframe()
    df = df.reset_index()
    
    if aquif_layers is not None:
        df = df[df['z'].isin(aquif_layers)]
    
    idx_z_min = df.groupby(['x', 'y', 'time']).z.idxmin() # get index of min z ("layer") for each x,y,t groups
    first_aquif_lay = df.loc[idx_z_min].reset_index().set_index('zone').drop('index', axis=1)
    # time not needed here, zone are independant from time coords
    return first_aquif_lay.to_xarray()



def search_zone(ds, i=None, j=None, x=None, y=None, z=None):
    """ search zone number in marthe grid,
    based on xy or ij (col, lig)

    This function can be used to search zone number from coordinates or indices.
    You must provide either (i,j) or (x,y).

    Note
    ----
    if ds is multilayered, you need to provide the layer you want (int)
    ds should contains dx and dy
    ds should not have assigned coords (x and y are variables, zone is the dimension coordinates (with time))

    Parameters
    ----------
    ds : xr.Dataset
        dataset with zone, x, y, dx, dy variables.
    i : int, optional
        column index to search zone.
    j : int, optional
        row index to search zone.
    x : float, optional
        x coordinate to search zone.
    y : float, optional
        y coordinate to search zone.
    z : int, optional
        layer index to search zone. If not provided, all layers are considered.
    
    Returns
    -------
    zone : xr.Dataset
        dataset with zone variable, containing the zone number(s) corresponding to the provided coordinates.
        If no zone is found, an empty dataset is returned.
    If multiple zones are found, all of them are returned.
    """
    ds_search = ds.copy()
    
    if z is not None:
        ds_search = ds_search.where(ds_search.z == z, drop=True)

    if x is not None:
        assert y is not None, 'if x is provided, y cannot be None'
        ## mask = ds.sel(x=x, y=y, method='nearest') # possible uniquement si x,y sont des coordonnées/dim
        nearest = _nearest_node(np.array([(x, y)]), np.array(list(zip(ds_search['x'].data, ds_search['y'].data))))
        nearest_zone = ds_search.isel(zone=nearest)
        
        # check if xy is in a cell == dx and dy are not greater than grid resolution
        dx = np.abs(nearest_zone.x.data - x)
        dy = np.abs(nearest_zone.y.data - y)
        mask = ds_search['zone'] == nearest_zone.zone if (dx <= nearest_zone.dx.data) & (dy <= nearest_zone.dy.data) else ds_search['zone'].isnull()

    if i is not None:
        assert j is not None, 'if i is provided, j cannot be None'
        mask = (ds_search['col'] == i) & (ds_search['lig'] == j)

    # zone = ds.where(mask, drop=True)['zone'].data
    zone = ds_search.where(mask, drop=True)
    return zone
