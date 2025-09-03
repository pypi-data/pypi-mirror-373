#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
#
#    This file is part of gridmarthe.
#
#    gridmarthe is a python library to manage grid files for 
#    MARTHE hydrogeological computer code from French Geological Survey (BRGM).
#    Copyright (C) 2024-2025  BRGM
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
""" GIS utility for marthe grids
"""


import numpy as np

from shapely.geometry import Polygon
from pyproj import Transformer
import geopandas as gpd
import xarray as xr

from ..utils import assign_coords


def _mk_cell_polygon(xleft, ylower, xright, yupper):
    return Polygon(
        (
            (xleft , ylower),
            (xright, ylower),
            (xright, yupper),
            (xleft , yupper),
            (xleft , ylower)
        )
    )


_polygonize = np.vectorize(_mk_cell_polygon)


def _build_polyg(ds):
    """ build a (rectangular) polygon shape from marthegrid dataset """
    
    x0 = ds.x.values - (ds.dx.values / 2.)
    y0 = ds.y.values - (ds.dy.values / 2.)
    x1 = ds.x.values + (ds.dx.values / 2.)
    y1 = ds.y.values + (ds.dy.values / 2.)
    
    return _polygonize(x0, y0, x1, y1)


def to_geodataframe(ds, epsg='EPSG:27572', fmt='long'):
    """ Convert marthegrid.Dataset to a geodataframe

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset to convert.
    epsg : str, optional
        The EPSG code for the coordinate reference system, by default 'EPSG:27572'.
    fmt : str, optional
        The format of the output GeoDataFrame, either 'long' or 'wide', by default 'long'.
    
    Returns
    -------
    geopandas.GeoDataFrame
        The converted GeoDataFrame.
    """
    
    polygons = _build_polyg(ds) # .isel(time=0) # x,y does not vary in time
    df = ds.to_dataframe() #.to_pandas() # only for 1 dim
    
    if 'time' in ds.dims.keys():
        polygons = np.tile(polygons.flatten(), len(np.unique(df.index.get_level_values('time')))) # ad geom for every timestep
    
    gdf = gpd.GeoDataFrame(
        df,
        geometry=polygons,
        crs=epsg
    )
    
    if fmt == "wide" and 'time' in ds.dims.keys():
        # here no wide fmt if no time, so no if 'time' in ds.dims.keys():
        gdf = gdf.unstack('time')
        gdf.columns = [
            '{}_{}'.format(x, y.strftime('%Y%m%d'))\
            if x not in ['x', 'y', 'dx', 'dy', 'z', 'geometry'] else x\
            for x, y in gdf.columns
        ]
        gdf = gdf.loc[:,~gdf.columns.duplicated()].copy()  # drop duplicated cols
        gdf = gdf.set_geometry('geometry')  # need to make again geom after drop dupl
    
    return gdf


def _check_rioxarray():
    try:
        import rioxarray
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            'rioxarray is not Found in python env.' + \
            'Please install it or reinstall gridmarthe with optionnal dependancies: pip install gridmarthe[opt]'
        )
    return


def clip_dataset(ds, gdf, crs=27572, engine='gdf'):
    """ Clip a xarray Dataset with a gpd.GeoDataFrame

    Needs rioxarray. If not installed, raise ModuleNotFoundError
    please install it or reinstall gridmarthe with optionnal dependancies: pip install gridmarthe[opt]

    See: https://corteva.github.io/rioxarray/html/examples/clip_geom.html
    Todo: shapely version

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset to clip.
    gdf : geopandas.GeoDataFrame
        The GeoDataFrame containing the geometry to clip with.
    crs : int, optional
        The coordinate reference system to use for the clipping, by default 27572.
    engine : str, optional
        The engine to use for clipping, by default 'gdf'.
    
    Returns
    -------
    xarray.DataArray or xarray.Dataset
        The clipped dataset.
    """
    _check_rioxarray()
    shp = gdf.to_crs(crs)
    da  = assign_coords(ds.rio.write_crs("EPSG:{}".format(crs)))
    clipped_da = da.rio.clip(shp.geometry.values, shp.crs, drop=True)
    return clipped_da


def subset_with_coords(da, dims=['x', 'y'], gdf=None, xmin=None, ymin=None, xmax=None, ymax=None):
    """ subset DataArray or Dataset on rectangular shape, with gpd.GeoDataFrame or bounds

    Parameters
    ----------
    da : xarray.DataArray or xarray.Dataset
        The data to subset.
    dims : list of str, optional
        The dimensions to use for subsetting, by default ['x', 'y'].
    gdf : geopandas.GeoDataFrame, optional
        A GeoDataFrame containing the geometry to use for subsetting, by default None.
    xmin, ymin, xmax, ymax : float, optional
        The manual bounds to use for subsetting, by default None.
    
    Returns
    -------
    xarray.DataArray or xarray.Dataset
        The subsetted data.
    """
    if gdf is not None:
        # edit, one line with total_bounds attribute instead of bounds
        # xmin, ymin, xmax, ymax = gdf.bounds.T.values # or .T.to_numpy(), in any case return np.array // total_bounds instead of bounds
        # xmin, ymin, xmax, ymax = xmin[0], ymin[0], xmax[0], ymax[0]
        xmin, ymin, xmax, ymax = gdf.total_bounds #gdf.bounds.T.values # or .T.to_numpy(), in any case return np.array // total_bounds instead of bounds
    else:
        assert xmin is not None, "When using manual bounds, all must be set"
        assert xmax is not None, "When using manual bounds, all must be set"
        assert ymin is not None, "When using manual bounds, all must be set"
        assert ymax is not None, "When using manual bounds, all must be set"
    
    mask_lon = ( da[dims[0]] >= xmin) & ( da[dims[0]] <= xmax) #da.xc
    mask_lat = ( da[dims[1]] >= ymin) & ( da[dims[1]] <= ymax)
    
    # imin, imax = np.where(da[var[0]].values==xmin)[0], np.where(da[var[0]].values==xmax)[0]
    # jmin, jmax = np.where(da[var[1]].values==ymin)[0], np.where(da[var[1]].values==ymax)[0]

    # sub_da = da.isel(i=slice(int(imin), int(imax)+1), j=slice(int(jmax), int(jmin)+1)) # j in reverse order / +1 on imax, jmin because upper is exclude in py slicing
    
    return da.where(mask_lon & mask_lat, drop=True)


def _transf_proj_xy(ds, from_epsg="EPSG:27572", to_epsg="EPSG:2154"):
    """ Transform coordinates of a dataset using pyproj.

    **!** return more unique points than initial due to projection deformation
    """
    transformer = Transformer.from_crs(from_epsg, to_epsg, always_xy=True)
    x_source, y_source = ds.x.data, ds.y.data
    x_target, y_target = transformer.transform(x_source, y_source)
    ds = ds.copy()
    ds['x'].data, ds['y'].data = np.astype(x_target, np.float32), np.astype(y_target, np.float32)
    ds.attrs['projection'] = to_epsg
    return ds

# def _transf_proj_regrid(ds, from_epsg="EPSG:27572", to_epsg="EPSG:2154"):
    # """ Recreate a transformed grid based on dx,dy and x0,y0"
    # transformer = Transformer.from_crs(from_epsg, to_epsg, always_xy=True)
    # nx, ny = len(x), len(y)
    # x0, y0 = np.nanmin(x), np.nanmin(y)
    # x1, y1 = np.nanmax(x), np.nanmax(y)
    # dx, dy = ds['dx'].data, ds['dy'].data
    # return

def _transf_proj_meshgrid(ds, from_epsg="EPSG:27572", to_epsg="EPSG:2154"):
    """ Transform grid of a dataset using pyproj,
    using meshgrid
    """
    x, y = np.unique(ds['x'].data), np.unique(ds['y'].data)
    transformer = Transformer.from_crs(from_epsg, to_epsg, always_xy=True)
    
    xx, yy = np.meshgrid(x, y)
    xx_transformed, yy_transformed = transformer.transform(xx, yy)
    data_transformed = xr.DataArray(
        assign_coords(ds)['permeab'].data,
        dims=["y", "x"],
        coords={"y": yy_transformed[:, 0], "x": xx_transformed[0, :]}
    )
    return data_transformed


def transf_proj(ds, from_epsg="EPSG:27572", to_epsg="EPSG:2154", engine='rioxarray'):
    """  Transform grid of a dataset using pyproj

    engine: rioxarray, meshgrid, xy

    Data (ds) needs to be a 2D array with xy as coords dimensions and time sliced.
    If needed, use :py:func:`gridmarthe.assign_coords` first.

    Warning: IN DEVELOPMENT, not tested yet // USE WITH CAUTION
    """ 
    if engine == 'rioxarray':
        _check_rioxarray()
        ds_transf = ds.rio.write_crs(from_epsg).rio.reproject(to_epsg)
    elif engine == 'meshgrid':
        ds_transf = _transf_proj_meshgrid(ds, from_epsg, to_epsg)
    elif engine == 'xy':
        ds_transf = _transf_proj_xy(ds, from_epsg, to_epsg)
    return ds_transf


def to_raster(da, x_dim='x', y_dim='y', epsg=27572, fout='raster.tiff'):
    """ Write a xr.DataArray to a raster file
    
    need xarray with rioxarray installed.
    Only for regular grids.
    
    TODO: add support for irregular grids, using PostMARTHE QGIS plugin code.

    Parameters
    ----------
    da : xarray.DataArray
        The DataArray to write to a raster file (only 2D, i.e. no time dimension, select
        a variable and timestep before).
    x_dim : str, optional
        The name of the x dimension, by default 'x'.
    y_dim : str, optional
        The name of the y dimension, by default 'y'.
    epsg : int, optional
        The EPSG code for the coordinate reference system, by default 27572.
    fout : str, optional
        The output file path for the raster file, by default 'raster.tiff'.
    
    Returns
    -------
    None
        The function writes the raster file and returns None.
    """
    _check_rioxarray()
    da = da.copy().rio.write_crs('epsg:{}'.format(epsg))
    da = da.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim)
    da.rio.to_raster(fout)
    return None

