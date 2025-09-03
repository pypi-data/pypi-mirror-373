#! /usr/bin/env python3
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

import os
from datetime import datetime

import pandas as pd
import numpy as np
import xarray as xr

from .lecsem import (
    modgridmarthe,
    _read_marthe_grid,
    _transform_xcoords,
    _transform_ycoords,
    _set_layers,
    _get_id_grid,
    _get_col_and_lig,
    _decode_title,
    _parse_dims_from_xr_attrs,
    _extract_zvar_from_ds,
    scan_var,
)


from .utils import (
    read_dates_from_pastp,
    assign_coords,
    stack_coords,
    dropna,
    fillna
)

from typing import Union


# http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
# pas vraiment, pour respecter la convention, le nom de variable le plus proche est : water_table_depth / mais on parle de charge pas prof
# proposition à faire dans https://github.com/cf-convention/discuss/issues
# water_table_altitude or level?
VARS_ATTRS = {
    'permeab': {
        'varname': 'PERMEAB',
        'units': 'm/s',
        'missing_value': 0.,
        'standard_name': '',
        'long_name': 'aquifer_hydraulic_conductivity'
    },
    'charge' : {
        'varname': 'CHARGE',
        'units': 'm',
        'missing_value': 9999.,
        'standard_name': 'water_table_level',
        'long_name':
        'groundwater head'
    },
    'saturat': {
        'varname': 'SATURAT',
        'units': '%'   ,
        'missing_value': 9999.,
        'standard_name': 'water_table_saturation',
        'long_name': 'groundwater_saturation'
    },
    'debit'  : {
        'varname': 'DEBIT',
        'units': 'm3/s',
        'missing_value': 0.,
        'standard_name': '',
        'long_name': 'flow'
    },
    'debit_rivi'    : {
        'varname': 'DEBIT_RIVI',
        'units': 'm3/s',
        'missing_value': 9999.,
        'standard_name': 'water_volume_transport_in_river_channel',
        'long_name': 'river_discharge_flow'
    },
    'qech_riv_napp' : {
        'varname': 'QECH_RIV_NAPP',
        'units': 'm3/s',
        'missing_value': 9999.,
        'standard_name': '',
        'long_name': 'surface_groundwater_exchange_flow'
    },
}



def _parse_attrs(
    title=None,
    dims=None,
    xyfactor=1.,
    dates=None,
    is_nested=False,
    dxlus=None,
    dylus=None,
    xcols=None,
    yligs=None
):
    """ Parse attributes for xarray.Dataset
    nb: attrs must be string, int, float
    """
    prologue = {
        'conventions'         :'CF-1.10', # check https://cfconventions.org/
        'title'               : title if title is not None else '',
        'marthe_grid_version' : 9.0,
        'original_dimensions' : 'x,y,z [grids]: ' + '; '.join(
            [ ' '.join(map(str, x)) for x in dims]
        ),
    }

    grid_attrs = {
        'lon_resolution': ', '.join(map(str, np.unique(dxlus))),
        'lat_resolution': ', '.join(map(str, np.unique(dylus))),
        'scale_factor'  : xyfactor,
        'nested_grid'   : str(is_nested),
        'extend'        : "xymin : {} {}; xymax: {} {}".format(
            np.min(xcols), np.min(yligs), np.max(xcols), np.max(yligs)
        ),
    }
    dates_attrs = {}
    if isinstance(dates, pd.DatetimeIndex):
        dates_attrs = {
            'period'    : '{}-{}'.format(
                pd.to_datetime(dates.min()).year, pd.to_datetime(dates.max()).year
            ), # force pd.date_time, case of pastp => numpydatetime64 / # np.datetime_as_string(i, unit='M')
            'frequency' : '{} day(s)'.format(str(dates.to_series().diff().mean().days)),
        }
    
    epilogue = {
        'creation_date' : 'Created on {}'.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ UTC')),
        'institution'   : 'BRGM, French Geological Survey, Orléans, France',  # TODO: make it optional
        'comment'       : 'Hydrogeological model created with MARTHE code '\
                          '(Thiery, D. 2020. Guidelines for MARTHE v7.8 computer code'\
                          'for hydro-systems modelling. report BRGM/RP-69660-FR).'
    }

    return {**prologue, **grid_attrs, **dates_attrs, **epilogue}



def load_marthe_grid(
    filename: str,
    varname: Union[str, None] = None,
    fpastp: Union[str, None] = None,
    dates=None,
    nanval: Union[int, float, None] = None,
    drop_nan: bool = False,
    xyfactor: Union[int, float] = 1.,
    shallow_only=False,
    keepligcol: bool = False,
    add_id_grid: bool = False,
    title: Union[str, None] = None,
    var_attrs: dict = {},
    model_attrs: dict = {
        'resolution_units': 'm',
        'projection'      : 'epsg:27572',
        'domain'          : 'FR-France',
    },
    engine: str = 'xarray',
    verbose: bool=False,
):
    """ Read Marthe Grid File as xarray.Dataset 
    
    The gridfile is read as a sequence: the variable for all layer
    for main grid, then all layer for nested grids, is stored in
    a 1D vector for every timestep. A single spatial identifier
    ``zone`` is used to map spatial coordinates.

    Before plot operations, user can assign coordinates (set x,y
    as dimension coordinates and drop zone) to get 2-D arrays (or
    3D arrays if multilayer) for every timesteps.

    Parameters
    ----------
        filename: str
            A path to marthegrid file (.permh, .out, etc.)
        
        varname : str, Optionnal
            variable to access in martgrid file, e.g ``CHARGE`` for groundwater head. See marthegrid file content.
            if None  is passed (default), function will scan all varnames in filename and keep first only
            if 'all' is passed,  function will scan all varnames in filename and keep all. 
            All datavars are added to dataset, using recursive call to func
            if wrong variable name is passed, empty data will be returned.
        
        fpastp: str, Optionnal
            A pastp file to read for dates
        
        dates: sequence, Optionnal
            Can be a pd.date_range, pd.Series, pd.DatetimeIndex, np.array or list of datetime/np.datetime objects.
            If no dates (or no fpastp) is provided, a fake sequence of dates from 1850 to 1900 will
            be used for xarray object
        
        nanval: float, Optionnal
            A code value for nan values. Default is 9999.
        
        drop_nan: bool, Optionnal
            Drop nan values (corresponding to nanval) in xarray object to return.
            Default is False (keep nan values).
        
        xyfactor: int or float, Optionnal
            factor to transform X and Y values. e.g.: 1000 to convert km XY to meters.
            Default is 1.
        
        shallow_only: bool, Optionnal
            Boolean to read only the first layer. Default is False.
        
        keepligcol: bool, Optionnal
            Add columns (col) and rows (lig) index (from 1 to n), Default is False.
        
        add_id_grid: bool, Optionnal
            Add grid id (from 0 to n), useful for nested grids.
            0 is main grid, Default is False
        
        title: str , Optionnal
            Title for grid attributes. Default is None (not used)
        
        var_attrs: dict, Optionnal
            Dictionnary of attributes to add to variable DataArray.
        
        model_attrs: dict, Optionnal
            Dictionnary of attributes to add to Dataset.
            by default, gis attrs are added and can be modified
            
            >>> {
            ...    'resolution_units': 'm',
            ...    'projection'      : 'epsg:27572',
            ...    'domain'          : 'FR-France'
            ... }
        
        engine: str, Optionnal
            Engine to use for returned object. Default is 'xarray', which return xarray.Dataset object.
            Another option is 'numpy', which return a list of numpy arrays :
            [zvar, zdates, isteps, zxcol, zylig, zdxlu, zdylu, ztitle, dims]

        verbose: bool, Optionnal
            Print some information about execution in stdout.
            Default is False.
    
    Returns
    -------
        ds: xr.Dataset
            A xarray.Dataset object containing values and attributes read from Marthe grid file.
    """
    
    # Fortran error cause sys exit. To avoid this, we add a test on file first
    if not os.path.exists(filename):
        raise FileNotFoundError("File : `{}` does not exist. Please check syntax/path.".format(filename))
    
    if varname is None:
        if verbose:
            print("Warning, no varname passed to function `_read_marthe_grid`. Taking the first varname in filename")
        varname = scan_var(filename)
        if verbose:
            print('Variables founded: ', varname)
        if len(varname) >= 1:
            varname = varname[0]
        else:
            # if no varname read from scan, it can be a bug (some version of marthe did not write field name in metadata)
            raise ValueError('No variable founded in file, please consider check file or clean it (cleanmgrid util or winmarthe)')

    elif varname.lower() == 'all':
        varname  = scan_var(filename)
        # -- recursive call
        arrays = []
        for var in varname:
            arrays.append( load_marthe_grid(
                filename, var, fpastp, dates, nanval, drop_nan, xyfactor, shallow_only,
                keepligcol, add_id_grid, title, var_attrs, model_attrs, engine, verbose
            ) )
        return xr.merge(arrays)
        
    elif varname.islower():
        varname = varname.upper() # in marthegridfiles, varnames are always uppercase; if user pass lowercase, this avoid error/empty array
    
    # --- read var, xycoords, timesteps, etc. from file
    (
        zvar, zdates, isteps, zxcol,
        zylig, zdxlu, zdylu, ztitle, dims
    ) = _read_marthe_grid(filename, varname, shallow_only=shallow_only)

    if engine == 'numpy':
        return [zvar, zdates, isteps, zxcol, zylig, zdxlu, zdylu, ztitle, dims]
    
    # --- transform data and parse into xarray.Dataset
    if shallow_only:
        print('NOT YET AVAILABLE')
        # TODO shape (time, gig, values) -> (time, values)
    
    if title is None:
        title = _decode_title(ztitle)
    
    # bool to check if nested grid
    if len(dims) > 1:
        is_nested = True
    else:
        is_nested = False
    
    # memo: dims = [maingrid[x, y, z], gig1[x, y, z], ...]
    xcols, dxlus = _transform_xcoords(zxcol, zylig, zdxlu, nlayer=dims[0][-1], factor=xyfactor)
    yligs, dylus = _transform_ycoords(zxcol, zylig, zdylu, nlayer=dims[0][-1], factor=xyfactor)
    
    if varname == '': varname = 'variable'  # security if force mode
    vattrs = VARS_ATTRS.get(varname.lower(), {})
    vattrs.update(var_attrs)
    dic_data = {
        varname.lower() : (["time", "zone"], zvar, vattrs), #dict(**vattrs, **var_attrs)
        'x'  : ("zone", xcols, {'units': 'm', 'axis': 'X',  'coverage_content_type' : "coordinate"}), #'standard_name': 'longitude',
        'y'  : ("zone", yligs, {'units': 'm', 'axis': 'Y',  'coverage_content_type' : "coordinate"}), #'standard_name': 'latitude' ,
        'dx' : ("zone", dxlus),
        'dy' : ("zone", dylus)
    }
    
    # dic_coords = {
    #
    # }
    
    if keepligcol:
        if is_nested:
            add_id_grid = True # force to add id_grid if nested grid
        cols, ligs   = _get_col_and_lig(dims)
        dic_data['col'] = ("zone", cols)
        dic_data['lig'] = ("zone", ligs)
    
    if add_id_grid:
        dic_data['id_grid'] = ("zone", _get_id_grid(dims))
    
    # if pseudo2D => add z dimension
    # TODO assert valid if real3D
    if dims[0][-1] > 1:
        zlus = _set_layers(dims)
        zattrs = {'units': '-', 'axis': 'Z', 'positive': 'down', 'standard_name': 'depth', 'long_name': 'aquifer_layer'} # not if full 3D ! TODO better
        dic_data['z'] = ("zone", zlus, zattrs) # add lay
        
    if fpastp is not None:
        # add dates from a pastp file, case of non-uniform timesteps or edition not set every timestep
        timesteps = read_dates_from_pastp(fpastp)
        dates = timesteps.loc[timesteps['timestep'].isin(isteps), 'date'].values
        dates = pd.DatetimeIndex(dates) # only for frequency
    elif dates is None:
        if verbose:
            print('Warning: No dates or fpastp provided, using default (fake) dates to constructed xarray object.')
        dates = pd.date_range('1850', '1900', len(isteps))
        # dates = np.arange(1, len(isteps)+1) # TODO use integers for time is no dates provided ?

    # --- Create xarray.Dataset object
    ds = xr.Dataset(
        data_vars=dic_data,
        coords={
            'time': dates,
            'zone': np.arange(1, zvar.shape[1] + 1, dtype=np.int32),
        },
        attrs={
            **_parse_attrs(title, dims, xyfactor, dates, is_nested, dxlus, dylus, xcols, yligs),
            **model_attrs
        }
    )
    
    # add non-dimensionnal coordinates
    # 'xc': (['zone'], xcols), # TODO coordinates directly as coords depending on dims ?
    # 'yc': (['zone'], yligs),
    # 'domain_size': dims, # add non dimension coordinate for info
    # 'domain_origin': [(x0, y0) for igig in grids], # add non dimension coordinate for info
    # ds = ds.assign_coords(  # or toto.set_coords(['time', 'zone', 'x', 'y', 'z', 'dx', 'dy'])
        # dic_coords
    # )
    
    if drop_nan:
        if nanval is None:
            nanval = vattrs.get('missing_value', 9999.)  # if no  user defined nanval, try to get corresponding val in dict then 9999. if not present
        
        if not isinstance(nanval, (list, tuple)):
            nanval = [nanval]
        elif isinstance(nanval, tuple):
            nanval = list(nanval)
        
        if (varname.lower() == 'permeab' or filename.endswith("permh")) and is_nested:
            if -9999. not in nanval:
                nanval += [-9999.]
        
        ds = dropna(ds, varname, nanval)
        ds['zone_all'] = ('zone', ds['zone'].data)  # keep old zone as variable for write method // memo: remove tuple to keep as dim
        ds['zone'] = np.arange(1, np.size(ds['zone'].data) + 1, dtype=np.int32)  # rearange zone
        
    # FIXME better, prevent bug at write : https://github.com/pydata/xarray/issues/7722 // https://stackoverflow.com/questions/65019301/variable-has-conflicting-fillvalue-and-missing-value-cannot-encode-data-when
    # del ds[varname.lower()].encoding['missing_value']
    return ds


def reset_geometry(ds, path_to_permh: str, variable='permeab', fillna=False):
    """ Reset a Marthe grid geometry based on permh dataset

    This function is useful/used, to reconstruct the geometry of the dataset
    (if NaN were dropped for example), before writting marthe grid, where the full
    domain is needed (including non active cells).
    
    Note
    ----
    
    Join is performed with xy[z] (if xy are present in coords) or zone
    to get zone back in full domain (if dropped, or nan were dropped, etc.).

    If nan were dropped during :py:func:`gridmarthe.load_grid_marthe()`, 'zone_all'
    was added and will be used (this variable store the zone index before the reindexing
    during :py:func:`gridmarthe.dropna`).
    
    Parameters
    ----------
    ds: xr.Dataset
    
    path_to_permh: str
        path to the .permh file containing domain
        
    variable: str
        variable (ds key) containing data
    
    fillna: bool (Optionnal)
        to fillna WITH permh nan value.
        permh nan value are used because it can contain different nan values (0 and -9999 for nested grids)
        for simplier nan fills, this can be performed outside of this function.
    
    Returns
    -------
        xr.Dataset containing original variables and geometry read from permh file
    """
    da = ds.copy()
    # All values (nan, nested grid margins) should be included in permh dataset.
    permh = load_marthe_grid(path_to_permh, drop_nan=False, add_id_grid=True, keepligcol=True, verbose=False)
    
    
    if 'x' in da.coords.keys():
        da = stack_coords(da, dropna=True)
        coords = [x for x in da.coords.keys() if x in ['x', 'y', 'z']] # if xy assert only existing coords in xyz
    elif 'zone_all' in da.keys():
        da['zone'] = da['zone_all'].data  # restore zone_all (zone before reorder after dropnan) for merge
        da = da.drop('zone_all')
        coords = ['zone']
    else:
        coords = ['zone']

    # to pandas for simplier join/merge operations
    da = da.to_dataframe().reset_index()
    
    # get real zone back
    grid = permh.to_dataframe().reset_index()
    grid['inactive'] = grid['permeab']
    grid = grid.drop('permeab', axis=1)
    # todo groupby time, loop on time and join grid every timestep... if needed to write with time ?
    # mostly used for parameters...
    tmp = grid.merge(
        da.loc[:, coords+[variable]],
        on=coords,
        suffixes=['', '_y'],
        how='left',
    )
    tmp = tmp.drop(tmp.filter(regex='_y$', axis=1),axis=1) # drop overlapping cols, if there is some.
    if fillna:
        # tmp = tmp.fillna(nanval) # no because, different codes for nested or not.
        tmp[variable] = np.where(np.isnan(tmp[variable]), grid['inactive'], tmp[variable])
    tmp = tmp.drop('inactive', axis=1)
    tmp = tmp.set_index(['time', 'zone']).to_xarray()
    tmp.attrs = ds.attrs # get back attrs
    return tmp



def write_marthe_grid(ds, fileout='grid.out', varname='charge', file_permh: str = None, title=None, dims=None, debug=False):
    """ Write Dataset as MartheGrid v9 file
    
    ds should contain x, y, dx, dy, attrs[['title', 'original_dimensions']]
    in case of error, please use :py:func:`gridmarthe.reset_geometry` first.
    When providing a path to ``file_permh`` argument, :py:func:`gridmarthe.reset_geometry` is called automatically.
    
    A good pratice is to provide the permh file when writing dataset to marthegrid format.
    
    >>> gm.write_marthe_grid(ds, 'toto.out', file_permh='./mymodel/model.permh')
    
    WARNING: This function was developped to write parameters grids to marthe format.
    Not to recreate simulation results (hydraulic head at several timesteps for example) as gridmarthe format.
    This means that this function should not be used for dataset with several timesteps.
    Example, to create a new initial hydraulic head file based on simulation, select the timestep in dataset before
    writing.
    
    >>> ds = ds_head.isel(time=16) # or do an aggregation (eg mean over a period)
    >>> gm.write_marthe_grid(ds, 'mymodel.charg')
    
    Parameters
    ----------
    ds: xr.Dataset
        dataset containing data, coordinates (x,y[,z]), dx,dy and dimensions (in attrs).
    
    fileout: str
        filename to write
    
    varname: str (Optionnal)
        variable name (key) containing values.
    
    file_permh: str (Optionnal)
        path to the permh file corresponding to current Marthe model.
        Needed to recreate full dimension if NaN dropped before.
        
    title: str (Optionnal)
        title written in marthe grid file
    
    dims: list of array
        list containing array of dimension for every grid (ie len(dims) > 1 if nested grid)
        format is `[[x_main_grid, y_main_grid, z_main_grid], [x_nested_1, ...], ...]`
        eg. `[[354,252,2], [182,156,2]]`
        if only main grid : `[[x,y,z]]`
        if None (default, dims will be parsed from ds.attrs['original_dimensions'] which is added
        when read with :py:func:`gridmarthe.load_marthe_grid`. If not present (lost in some computation for example),
        please use py:func:`gridmarthe.reset_geometry` or provide list of dims manually.
    
    debug: bool, Optionnal (default is False).
    
    Returns
    -------
    status: int.
        0 if everything's ok. 1 otherwise.
    
    """
    
    ds2 = ds.copy()
    
    if dims is None:
        dims = _parse_dims_from_xr_attrs(ds2.attrs.get('original_dimensions'))
    
    if dims is None:
        raise ValueError("""Original dimensions cannot be None.\
Attributes was not founded in dataset so pleave provide a list with original domain dimensions
""")
    
    # --- Check if expected dimensions match variable dimensions
    # if not, recreate full grid with domain grid (permh file)
    if np.prod(np.array(dims), axis=1).sum() != np.size(ds2[varname].data):
        # if dimension differs, file_permh is required
        error = "Expected size and variable array size differ. Please provide a permh file to recreate original grid."
        assert file_permh is not None, error
        
        _fill_na = True if varname == 'permeab' else False # if permeab, fill_na with permh file (0 and/or -9999.)
        
        # reset geometry with full domain (stored in permh file)
        ds2 = reset_geometry(ds2, path_to_permh=file_permh, variable=varname, fillna=_fill_na)
        if not _fill_na:
            # if not permh variable, fill nan with constant values, based on variable
            NANs = VARS_ATTRS.get(varname, {}).get('missing_value', 9999.)
            ds2  = fillna(ds2, varname, NANs)
    
    # extract variables from dataset
    (
        zvar, zdates,
        zxcol, zylig, zdxlu, zdylu,
        ztitle, izdates
    ) = _extract_zvar_from_ds(ds2, varname)
    
    if title is None and ztitle == '':
        title = 'Marthe Grid ' # dummy arg to set type as string
    
    # call fortran module to write marthe grid
    status = modgridmarthe.write_grid(
        zvar=zvar,
        xcol=zxcol,
        ylig=zylig,
        dxlu=zdxlu,
        dylu=zdylu,
        typ_don=varname.upper(),
        titsem=title, #TODO debug use of ztitle
        n_dims=dims,
        nval=len(zvar[0]),
        ngrid=len(dims),
        nsteps=len(zdates),
        dates=izdates,
        debug=debug,
        xfile=fileout
    )

    if status != 0:
        print("\033[1;31m\nEDISEM Status={}\033[0m\n".format(status))
        print("An error occurred while writting Marthe Grid with EDSEMI subroutines.")
        print("Please check array consistency (9999. or 0. for nan values\
        [ie, do not drop nan val before write or use `gm.reset_geometry()`]) or coordinates order [zyx]")
    
    return status 

