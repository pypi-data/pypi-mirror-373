# -*- coding: utf-8 -*-
"""
Created on Thu 16 Dec 2021

@author: Alexandre Kenshilik Coche
@contact: alexandre.co@hotmail.fr

This module is a collection of tools for manipulating hydrological space-time
data, especially netCDF data. It has been originally developped to provide
preprocessing tools for CWatM (https://cwatm.iiasa.ac.at/) and HydroModPy
(https://gitlab.com/Alex-Gauvain/HydroModPy), but most functions have been
designed to be of general use.

"""

#%% Imports:
import logging
logging.basicConfig(level=logging.ERROR) # DEBUG < INFO < WARNING < ERROR < CRITICAL
logger = logging.getLogger(__name__)

import xarray as xr
xr.set_options(keep_attrs = True)
# import rioxarray as rio # Not necessary, the rio module from xarray is enough
import json
import pandas as pd
from pandas.errors import (ParserError as pd_ParserError)
import geopandas as gpd
import numpy as np
import rasterio
import rasterio.features
from affine import Affine
from shapely.geometry import (mapping, Point, Polygon, MultiPolygon)
import os
import re
import sys
from functools import partial
import gc # garbage collector
from pathlib import Path
import datetime
# import matplotlib.pyplot as plt

from pysheds.grid import Grid
from pysheds.view import Raster, ViewFinder
# ========= change since version 0.5 ==========================================
# from pysheds.pgrid import Grid as pGrid
# =============================================================================

# ========== see reproject() §Rasterize ======================================
# import geocube
# from geocube.api.core import make_geocube
# from geocube.rasterize import rasterize_points_griddata, rasterize_points_radial
# import functools
# =============================================================================

# import whitebox
# wbt = whitebox.WhiteboxTools()
# wbt.verbose = False

#%% LEGENDE: 
# ---- ° = à garder mais mettre à jour
# ---- * = à inclure dans une autre fonction ou supprimer


#%% LOADING & INITIALIZING DATASETS
###############################################################################
def load_any(data, 
             *, name = None, 
             decode_coords = 'all', 
             decode_times = True, 
             rebuild_time_val = True, 
             **kwargs):
    r"""
    This function loads any common spatio-temporal file or variable into a
    standard python variable, without the need to think about the file or variable type.
    
    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray, geopandas.GeoDataFrame, pandas.DataFrame or numpy.array)
        ``data`` will be loaded into a standard *GEOP4TH* variable:
            
        - all vector data (GeoPackage, shapefile, GeoJSON) will be loaded as a geopandas.GeoDataFrame
        - all raster data (ASCII, GeoTIFF) and netCDF will be loaded as a xarray.Dataset
        - other data will be loaded either as a pandas.DataFrame (CSV and JSON) or as a numpy.array (TIFF)
        
        If ``data`` is already a variable, no operation will be executed.
    name : str, optional, default None
        Name of the main variable for TIFF, GeoTIFF or ASCII files.
    decode_coords : bool or {"coordinates", "all"}, default "all"
        Controls which variables are set as coordinate variables:
    
        - "coordinates" or True: Set variables referred to in the
          ``'coordinates'`` attribute of the datasets or individual variables
          as coordinate variables.
        - "all": Set variables referred to in  ``'grid_mapping'``, ``'bounds'`` and
          other attributes as coordinate variables.
    
        Only existing variables can be set as coordinates. Missing variables
        will be silently ignored.
        
        Despite it is an argument for `xarray.open_dataset`, this argument is explicitely passed outside the
        following ``**kwargs`` arguments because the default value in *geop4th* is different from the default
        value in `xarray.open_dataset`.
    decode_times : bool, default True
        If True, decode times encoded in the standard NetCDF datetime format
        into datetime objects. 
        
        Despite it is an argument for `xarray.open_dataset`, this argument is explicitely passed outside the
        following ``**kwargs`` arguments because the default value in *GEOP4TH* is different from the default
        value in `xarray.open_dataset`.
    rebuild_time_val : bool, default True
        If True, infer the time coordinate as a datetime object, from available information.
    **kwargs
        Optional other arguments passed to ``xarray.open_dataset``, ``pandas.DataFrame.read_csv``,
        ``pandas.DataFrame.to_csv``, ``pandas.DataFrame.read_json`` or 
        ``pandas.DataFrame.to_json`` function calls.
        
        May contain: 
            
        - decode_cf
        - sep
        - encoding
        - force_ascii
        - ...
        
        >>> help(xarray.open_dataset)
        >>> help(pandas.read_csv)
        >>> help(pandas.to_csv)
        >>> ...

    Returns
    -------
    data_ds : geopandas.GeoDataFrame, xarray.Dataset, pandas.DataFrame or numpy.array
        Data is loaded into a GEOP4TH variable. The type of this variable is 
        accordingly to the type of data:
        
        - all vector data will be loaded as a geopandas.GeoDataFrame
        - all raster data and netCDF will be loaded as a xarray.Dataset
        - other data will be loaded either as a pandas.DataFrame (CSV and JSON) or as a numpy.array (TIFF)
        
    Examples
    --------
    >>> data_ds = geo.load_any(r'D:\data.nc')
    >>> data_ds.head()
    ...
    """
    # initialization
    kwargs['decode_coords'] = decode_coords
    kwargs['decode_times'] = decode_times
    
    # If data is already a variable, the variable will be copied
    if isinstance(data, (xr.Dataset, xr.DataArray,
                         gpd.GeoDataFrame, pd.DataFrame,
                         np.ndarray)):
        data_ds = data.copy()      
    
    # If data is a string/path, this file will be loaded into a variable
    elif isinstance(data, (str, Path)):
        print("\nLoading data...")
        
        if not os.path.isfile(data):
            print("   Err: the path provided is not a file")
            return
        
        else:
            extension_src = os.path.splitext(data)[-1]
            
            # Adapt load kwargs:
            # These arguments are only used in pandas.DataFrame.to_csv():
            if extension_src != '.csv':
                for arg in ['sep', 'encoding']: 
                    if arg in kwargs: kwargs.pop(arg)
            # These arguments are only used in pandas.DataFrame.to_json():
            if extension_src != '.json':
                for arg in ['force_ascii']:
                    if arg in kwargs: kwargs.pop(arg)
            # These arguments are only used in xarray.open_dataset():
            if extension_src != '.nc':
                for arg in ['decode_coords']: 
                    if arg in kwargs: kwargs.pop(arg)    
            # These arguments are only used in xarray.open_dataset():
            if extension_src not in ['.nc', '.tif', '.asc']:
                for arg in ['decode_times']: 
                    if arg in kwargs: kwargs.pop(arg)  

            if extension_src in ['.shp', '.json', '.gpkg']:
                try: 
                    data_ds = gpd.read_file(data, **kwargs)
                except: # DataSourceError
                    try:
                        data_ds = pd.read_json(data, **kwargs)
                    except:
                        data_ds = json.load(open(data, "r"))
                        print("   Warning: The JSON file could not be loaded as a pandas.DataFrame and was loaded as a dict")
            
            elif os.path.splitext(data)[-1] in ['.csv']:
                try:
                    data_ds = pd.read_csv(data, **kwargs)
                except pd_ParserError:
                    logger.exception("")
                    print("\nTry to pass additional arguments to `geobricks.load_any()` such as column separator `sep` (see `help(pandas.read_csv)`)\n")
                    return
            
            elif extension_src == '.nc':
                try:
                    with xr.open_dataset(data, **kwargs) as data_ds:
                        data_ds.load() # to unlock the resource
    
                except:
                    kwargs['decode_times'] = False
                    print("   _ decode_times = False")
                    try:
                        with xr.open_dataset(data, **kwargs) as data_ds:
                            data_ds.load() # to unlock the resource
                    
                    except:
                        kwargs['decode_coords'] = False
                        print("   _ decode_coords = False")
                        with xr.open_dataset(data, **kwargs) as data_ds:
                            data_ds.load() # to unlock the resource      
                    
                    if rebuild_time_val:
                        time_coords = main_time_dims(data_ds, all_coords = True, all_vars = True)
                        time_coord = time_coords[0]
                        if data_ds[time_coord].dtype == float:
                            print("   _ inferring time axis...")
                            print(f"      . inferred time coordinate is {time_coord}")
                            units, reference_date = data_ds[time_coord].attrs['units'].split('since')
                            units = units.replace(' ', '').casefold()
                            reference_date = reference_date.replace(' ', '').casefold()
                            if units in ['month', 'months', 'M']: 
                                freq = 'M'
                            elif units in ['day', 'days', 'D']:
                                freq = 'D'
                            start_date = pd.date_range(start = reference_date, 
                                                       periods = int(data_ds[time_coord][0].values)+1, 
                                                       freq = freq)[-1]
                            try:
                                data_ds[time_coord] = pd.date_range(start = start_date, 
                                                                    periods = data_ds.sizes[time_coord], 
                                                                    freq = freq)
                            except: # SPECIAL CASE to handle truncated output files (from failed CWatM simulations)
                                print('      . info: truncated time on data')
                                data_ds = data_ds.where(data_ds[time_coord]<1e5, drop = True)
                                data_ds[time_coord] = pd.date_range(start = start_date, 
                                                                    periods = data_ds.sizes[time_coord], 
                                                                    freq = freq)   
                            print(f"      . initial time = {pd.to_datetime(data_ds[time_coord])[0].strftime('%Y-%m-%d')} | final time = {pd.to_datetime(data_ds[time_coord])[-1].strftime('%Y-%m-%d')} | units = {units}")
                            
    
            elif extension_src in ['.tif', '.asc']:
                with xr.open_dataset(data, **kwargs) as data_ds:
                    data_ds.load() # to unlock the resource   
                
                if 'band' in data_ds.dims:
                    if data_ds.sizes['band'] == 1:
                        data_ds = data_ds.squeeze('band')
                        data_ds = data_ds.drop('band')
                if name is not None:
                    data_ds = data_ds.rename(band_data = name)
        
    else:
        print("Err: `data` input does not exist")
        return
    
    # Return
    return data_ds


###############################################################################
def main_vars(data):
    """
    Infer the main data variables in a dataset, or ask the user (in the case of vector datasets).

    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray, geopandas.GeoDataFrame or pandas.DataFrame)
        Data whose main variable names will be retrieved.

    Returns
    -------
    list of str
        List of the inferred main data variables.

    """
    
    data_ds = load_any(data)
    
    if isinstance(data_ds, xr.Dataset): # raster
        var = list(set(list(data_ds.data_vars)) - set(['x', 'y', 'X','Y', 'i', 'j',
                                                       'lat', 'lon', 
                                                       'spatial_ref', 
                                                       'LambertParisII',
                                                       'bnds', 'time_bnds',
                                                       'valid_time', 't', 'time',
                                                       'date',
                                                       'forecast_reference_time',
                                                       'forecast_period']))
# =============================================================================
#         if len(var) == 1:
#             var = var[0]
# =============================================================================
    
    elif isinstance(data_ds, xr.DataArray):
        var = data_ds.name
        
        if (var is None) | (var == ''):
            var = input("Name of the main variable: ")
    
    elif isinstance(data_ds, (gpd.GeoDataFrame, pd.DataFrame)): # vector
# =============================================================================
#         var = data_ds.loc[:, data_ds.columns != 'geometry']
# =============================================================================
        print("Name or id of the main data variable: ")
        i = 1
        for c in data_ds.columns:
            print(f"   {i}. {c}")
            i += 1
        col = input("")
        if col in data_ds.columns: var = col # selection by name
        else: var = data_ds.columns[int(col)-1] # selection by id
    
    elif isinstance(data_ds, pd.Series):
        var = data_ds.name
        
        if (var is None) | (var == ''):
            var = input("Name of the main variable: ")
    
    # in case var is a single variable, it is still encapsulated into a list,
    # for coherence
    if not isinstance(var, list):
        var = [var]
        
    return var


###############################################################################
def main_space_dims(data):
    """
    Infer the spatial dimension names in a dataset.

    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray, geopandas.GeoDataFrame or pandas.DataFrame)
        Data whose spatial dimensions will be detected.

    Returns
    -------
    x_var : str or list of str
        Name of the X-axis dimension.
    y_var : str or list of str
        Name of the Y-axis dimension.

    """
    
    data_ds = load_any(data)
    
    if isinstance(data_ds, (xr.Dataset, xr.DataArray)):
        x_var = list(set(list(data_ds.dims)).intersection(set(['x', 'X', 'lon', 'longitude'])))
        y_var = list(set(list(data_ds.dims)).intersection(set(['y', 'Y', 'lat', 'latitude'])))
    
    elif isinstance(data_ds, (gpd.GeoDataFrame, pd.DataFrame)):
        x_var = list(set(list(data_ds.columns)).intersection(set(['x', 'X', 'lon', 'longitude'])))
        y_var = list(set(list(data_ds.columns)).intersection(set(['y', 'Y', 'lat', 'latitude'])))
    
    if len(x_var) == 1:
        x_var = x_var[0]
    elif len(x_var) > 1:
        print("Warning: several x variables have been detected")
    else:
        print("Warning: no x variable has been detected")
    if len(y_var) == 1:
        y_var = y_var[0]
    elif len(y_var) > 1:
        print("Warning: several y variables have been detected")
    else:
        print("Warning: no y variable has been detected")
    
    return x_var, y_var


###############################################################################
def main_time_dims(data_ds, 
                   all_coords = False, 
                   all_vars = False):
    """
    Infer the time dimension and the other main time variables from a dataset.

    Parameters
    ----------
    data_ds : xarray.Dataset or geopandas.GeoDataFrame
        Data whose time variable(s) will be retrieved.
    all_coords : bool, default False
        Only used if ``data_ds`` is a xarray variable.
        If False, only dimensions are considered as potential time coordinates.
        If True, even coordinates not associated to any dimension will be 
        considered as well as potential time coordinates (along ``dims``).
    all_vars : bool, default False
        Only used if ``data_ds`` is a xarray variable.
        If True, data variables (``data_vars``) will be considered as well 
        as potential time coordinates (along ``dims``).

    Returns
    -------
    var : list of str
        List of potential time coordinate names, the first one being the most relevant.

    """
    
    time_coord_avatars = ['time', 't', 'valid_time',
                          'forecast_period', 'date',
                          'time0',
                          # 'time_bnds',
                          # 'forecast_reference_time',
                          ]
    if isinstance(data_ds, (xr.Dataset, xr.DataArray)):
        var = list(set(list(data_ds.dims)).intersection(set(time_coord_avatars)))
        if all_coords: # in this case, even non-dim coordinates will be considered as potential time coordinates
            var = list(set(var).union(set(list(data_ds.coords)).intersection(set(time_coord_avatars))))
        if all_vars: # in this case, even data variables will be considered as potential time coordinates
            if isinstance(data_ds, xr.Dataset):
                var = list(set(var).union(set(list(data_ds.data_vars)).intersection(set(time_coord_avatars))))
            elif isinstance(data_ds, xr.DataArray):
                print("Note: `all_vars` argument is unnecessary with xarray.DataArrays")

    elif isinstance(data_ds, (pd.DataFrame, gpd.GeoDataFrame)):
        var = list(set(list(data_ds.columns)).intersection(set(time_coord_avatars)))
    
# =============================================================================
#     if len(var) == 1:
#         var = var[0]
# =============================================================================
    if len(var) > 1:
        # If there are several time coordinate candidates, the best option will
        # be put in first position. The best option is determined via a series
        # of rules:
            
        candidates = []
        
        if isinstance(data_ds, (xr.Dataset, xr.DataArray)):
            # Only 1D datetime variables will be considered
            for v in var:
                if np.issubdtype(data_ds[v], np.datetime64):
                    if len(data_ds[v].dims) == 1:
                        candidates.append(v)
            
            # The first remaining candidate with the largest number of values will
            # be selected
            coords_length = {data_ds[v].size:v for v in candidates}
            first_var = coords_length[max(coords_length.keys())]
            
        elif isinstance(data_ds, (pd.DataFrame, gpd.GeoDataFrame)):
            # Only datetime variables will be considered
            for v in var:
                if np.issubdtype(data_ds[v], np.datetime64):
                    candidates.append(v)
            
            # The first remaining candidate will be selected
            first_var = candidates[0]
        
        var.pop(var.index(first_var))
        var.insert(0, first_var)
    
    return var


###############################################################################
def get_filelist(data, 
                 *, extension = None,
                 tag = ''):
    """
    This function extract from a folder (or a file) a list of relevant files.

    Parameters
    ----------
    data: path (str or pathlib.Path) or list of paths (str or pathlib.Path)
        Folder, filepath or iterable of filepaths
    extension: str, optional
        Only the files with this extension will be retrieved.
    tag: str, optional
        Only the files containing this tag in their names will be retrieved.

    Returns
    -------
    data_folder : str
        Root of the files.
    filelist : list of str
        List of selected file names.

    """
    
    # if extension[0] == '.': extension = extension[1:]
    if isinstance(extension, str):
        if extension[0] != '.': extension = '.' + extension
    
    # ---- Data is a single element
    
    # if data is a single string/path
    if isinstance(data,  (str, Path)): 
        # if this string points to a folder
        if os.path.isdir(data): 
            data_folder = data   
            if extension is not None:
                filelist = [f for f in os.listdir(data_folder)
                                 if ( (os.path.isfile(os.path.join(data_folder, f))) \
                                     & (os.path.splitext(os.path.join(data_folder, f))[-1] == extension) \
                                         & (len(re.compile(f".*({tag}).*").findall(f)) > 0) )]
            else:
                filelist = [f for f in os.listdir(data_folder)
                                 if ( (os.path.isfile(os.path.join(data_folder, f))) \
                                     & (len(re.compile(f".*({tag}).*").findall(f)) > 0) )]
            
        # if this string points to a file
        else: 
            data_folder = os.path.split(data)[0]    # root of the file 
            filelist = [data]
    
    # ---- Data is an iterable
    elif isinstance(data, (list, tuple)):
        # [Safeguard] It is assumed that data contains an iterable of files
        if not os.path.isfile(data[0]):
            print("Err: Argument should be a folder, a filepath or a list of filepath")
            return
        
        data_folder = os.path.split(data[0])[0] # root of the first element of the list
        filelist = list(data)
        
        
    return data_folder, filelist 


###############################################################################
#%%% ° pick_dates_fields
def pick_dates_fields(*, input_file, output_format = 'NetCDF', **kwargs):
    """
    % DESCRIPTION:
    This function extracts the specified dates or fields from NetCDF files that
    contain multiple dates or fields, and exports it as a single file.
    
    
    % EXAMPLE:
    import geoconvert as gc
    gc.pick_dates_fields(input_file = r"D:/path/test.nc", 
                  dates = ['2020-10-15', '2021-10-15'])

    % OPTIONAL ARGUMENTS:
    > output_format = 'NetCDF' (default) | 'GeoTIFF'
    > kwargs:
        > dates = ['2021-10-15', '2021-10-19']
        > fields = ['T2M', 'PRECIP', ...]
    """    
    
    with xr.open_dataset(input_file) as _dataset:
        _dataset.load() # to unlock the resource
    
    #% Get arguments (and build output_name):
    # ---------------------------------------
    _basename = os.path.splitext(input_file)[0]
    
    # Get fields:
    if 'fields' in kwargs:
        fields = kwargs['fields']
        if isinstance(fields, str): fields = [fields]
        else: fields = list(fields) # in case fields are string or tuple
    else:
        fields = list(_dataset.data_vars) # if not input_arg, fields = all
    
    # Get dates:
    if 'dates' in kwargs:
        dates = kwargs['dates']
        if isinstance(dates, str): 
            output_file = '_'.join([_basename, dates, '_'.join(fields)])
            dates = [dates]
        else: 
            dates = list(dates) # in case dates are tuple
            output_file = '_'.join([_basename, dates[0], 'to', 
                                    dates[-1], '_'.join(fields)])

    else:
        dates = ['alldates'] # if not input_arg, dates = all  
        output_file = '_'.join([_basename, '_'.join(fields)])
        
    
    #% Standardize terms:
    # -------------------
    if 't' in list(_dataset.dims):
        print('Renaming time coordinate')
        _dataset = _dataset.rename(t = 'time')    

    if 'lon' in list(_dataset.dims) or 'lat' in list(_dataset.dims):
        print('Renaming lat/lon coordinates')
        _dataset = _dataset.rename(lat = 'latitude', lon = 'longitude')
        # Change the order of coordinates to match QGIS standards:
        _dataset = _dataset.transpose('time', 'latitude', 'longitude')
        # Insert georeferencing metadata to match QGIS standards:
        _dataset.rio.write_crs("epsg:4326", inplace = True)
        # Insert metadata to match Panoply standards: 
        _dataset.longitude.attrs = {'units': 'degrees_east',
                                    'long_name': 'longitude'}
        _dataset.latitude.attrs = {'units': 'degrees_north',
                                    'long_name': 'latitude'}
    
    if 'X' in list(_dataset.dims) or 'Y' in list(_dataset.dims):
        print('Renaming X/Y coordinates')
        _dataset = _dataset.rename(X = 'x', Y = 'y')
        # Change the order of coordinates to match QGIS standards:
        _dataset = _dataset.transpose('time', 'y', 'x')
        # Insert metadata to match Panoply standards: 
        _dataset.x.attrs = {'standard_name': 'projection_x_coordinate',
                            'long_name': 'x coordinate of projection',
                            'units': 'Meter'}
        _dataset.y.attrs = {'standard_name': 'projection_y_coordinate',
                            'long_name': 'y coordinate of projection',
                            'units': 'Meter'}

        
# =============================================================================
#     # Rename coordinates (ancienne version):
#     try:
#         _dataset.longitude
#     except AttributeError:
#         _dataset = _dataset.rename({'lon':'longitude'})
#     try:
#         _dataset.latitude
#     except AttributeError:
#         _dataset = _dataset.rename({'lat':'latitude'})    
#     try:
#         _dataset.time
#     except AttributeError:
#         _dataset = _dataset.rename({'t':'time'}) 
# =============================================================================
    
    #% Extraction and export:
    # -----------------------
    # Extraction of fields:
    _datasubset = _dataset[fields]
    # Extraction of dates:
    if dates != 'alldates':
        _datasubset = _datasubset.sel(time = dates)

    if output_format == 'NetCDF':
        _datasubset.attrs = {'Conventions': 'CF-1.6'} # I am not sure...
        
        # Export:
        _datasubset.to_netcdf(output_file + '.nc')
    
    elif output_format == 'GeoTIFF':
        _datasubset.rio.to_raster(output_file + '.tiff')
        
       
#%% EXPORT
###############################################################################
def export(data, 
           output_filepath, 
           **kwargs):
    r"""
    Export any geospatial dataset (file or GEOP4TH variable) to a file. Note that
    if the export implies a rasterization or a vectorization, it will not be handled
    by this function. It is necessary instead to use the :func:`rasterize` function
    (or its related super-function :func:`transform`). Vectorization is not yet
    implemented in GEOP4TH.

    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray, geopandas.GeoDataFrame, pandas.DataFrame or numpy.array)
        Dataset that will be exported to ``output_filepath``.
        
        Note that ``data`` will be loaded into a standard *GEOP4TH* variable:
            
        - all vector data (GeoPackage, shapefile, GeoJSON) will be loaded as a geopandas.GeoDataFrame
        - all raster data (ASCII, GeoTIFF) and netCDF will be loaded as a xarray.Dataset
        - other data will be loaded either as a pandas.DataFrame (CSV and JSON) or as a numpy.array (TIFF)
    output_filepath : str or pathlib.Path
        Full filepath (must contains location folder, name and extension) of 
        the file to be exported. For instance: r"D:\results\exportedData.tif"
    **kwargs :
        Additional arguments that can be passed to geopandas.GeoDataFrame.to_file(),
        xarray.Dataset.to_netcdf(), xarray.Dataset.rio.to_raster(),
        pandas.DataFrame.to_csv() or pandas.DataFrame.to_json(), depending of 
        the specified file extension.

    Returns
    -------
    None. The data is exported to the specified file.

    """
    
    extension_dst = os.path.splitext(output_filepath)[-1]
    
    data_ds = load_any(data, decode_times = True, decode_coords = 'all')
    
    # Safeguards
    # These arguments are only used in pandas.DataFrame.to_csv():
    if extension_dst != '.csv':
        for arg in ['sep', 'encoding']: 
            if arg in kwargs: kwargs.pop(arg)
    # These arguments are only used in pandas.DataFrame.to_json():
    if (extension_dst != '.json') & isinstance(data_ds, pd.DataFrame):
        for arg in ['force_ascii']:
            if arg in kwargs: kwargs.pop(arg)
    
    if isinstance(data_ds, xr.DataArray):
        if 'name' in kwargs:
            name = kwargs['name']
        else:
            name = main_vars(data_ds)[0]
        data_ds = data_ds.to_dataset(name = name)
            
    
    print("\nExporting...")
    
    if isinstance(data_ds, gpd.GeoDataFrame):
        if extension_dst in ['.shp', '.json', '.geojson', '.gpkg']:
            data_ds.to_file(output_filepath, **kwargs)
            print(f"   _ Success: The data has been exported to the file '{output_filepath}'")

        elif extension_dst in ['.nc', '.tif']:
            print("Err: To convert vector to raster, use geobricks.rasterize() instead")
            return
        
        elif extension_dst in ['.csv']:
            data_ds.drop(columns = 'geometry').to_csv(output_filepath, **kwargs)
            print(f"   _ Success: The data has been exported to the file '{output_filepath}'")
        
        else:
            print("Err: Extension is not supported")
            return
    
    elif isinstance(data_ds, xr.Dataset):
        # Avoid dtypes incompatibilities
        var_list = main_vars(data_ds)
        for var in var_list:
            if data_ds[var].dtype == int:
                if any(pd.isna(val) for val in data_ds[var].encoding.values()) | any(pd.isna(val) for val in data_ds[var].attrs.values()):
                    data_ds[var] = data_ds[var].astype(float)
                    print(f"Info: convert '{var}' from `int` to `float` to avoid issues with NaN")
        
        if extension_dst == '.nc':
            data_ds.to_netcdf(output_filepath, **kwargs)
        
        elif extension_dst in ['.tif', '.asc']:
            data_ds.rio.to_raster(output_filepath, **kwargs) # recalc_transform = False
            
        else:
            print("Err: Extension is not supported")
            return
        
        print(f"   _ Success: The data has been exported to the file '{output_filepath}'")
    
    elif isinstance(data_ds, pd.DataFrame): # Note: it is important to test this
    # condition after gpd.GeoDataFrame because GeoDataFrames are also DataFrames
        if extension_dst in ['.json']:
            data_ds.to_json(output_filepath, **kwargs)
        
        elif extension_dst in ['.csv']:
            data_ds.to_csv(output_filepath, **kwargs)
        
        print(f"   _ Success: The data has been exported to the file '{output_filepath}'")
        
        
#%% GEOREFERENCING
###############################################################################
# Georef (ex-decorate_NetCDF_for_QGIS)
def georef(data, 
           *, crs = None,
           to_file = False, 
           var_list = None,
           **time_kwargs):   
    r"""
    Description
    -----------
    Standardize the metadata required for georeferencing the data:
    
    - standardize spatial dimension names (and attributes for netCDF/rasters)
    - standardize the time dimension name and format (and attributes for netCDF/rasters)
    - standardize the nodata encoding (for netCDF/rasters): under the key '_FillValue' 
      in the encodings of the relevant data
    - standardize (and include if absent) the CRS: 'grid_mapping' key in the encoding 
      of the relevant data, and 'spatial_ref' dimensionless coordinate containing CRS info
    - 
    
    This function corrects the minor format defaults, according to Climate and
    Forecast Convention (https://cfconventions.org/conventions.html), thus facilitating
    further processing and visualization operations. For most data, these 
    corrections are enough to solve the issues encountered in visualization softwares
    (such as QGIS). If some data require deeper corrections, this should be
    done with ``standardize`` scripts (in *geop4th/workflows/standardize* folder).
    
    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray, geopandas.GeoDataFrame, pandas.DataFrame or numpy.array)
        Data to georeference.
        
        Note that if ``data`` is not a variable, it will be loaded into a standard *GEOP4TH* variable:
            
        - all vector data (GeoPackage, shapefile, GeoJSON) will be loaded as a geopandas.GeoDataFrame
        - all raster data (ASCII, GeoTIFF) and netCDF will be loaded as a xarray.Dataset
        - other data will be loaded either as a pandas.DataFrame (CSV and JSON) or as a numpy.array (TIFF)
    crs : int or str or rasterio.crs.CRS, optional
        Coordinate reference system of the source (``data``), that will be embedded in the ``data``.   
        When passed as an *integer*, ``src_crs`` refers to the EPSG code. 
        When passed as a *string*, ``src_crs`` can be OGC WKT string or Proj.4 string.
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to the same location as ``data``, while appending '_georef' to its name.
        If ``to_file`` is a path, the resulting dataset will be exported to this specified filepath.
    var_list : (list of) str, optional
        Main variables, in case data variables are too excentric to be automatically inferred.
    **time_kwargs : 
        Arguments for ``standardize_time_coord`` function:
            - var : time variable name (str), optional, default None
            - infer_from : {'dims', 'coords', 'all'}, optional, default 'dims' 

    Returns
    -------
    xarray.Dataset or geopandas.GeoDataFrame with a standard georeferencement.
    If ``to_file`` argument is used, the resulting dataset can also be exported to a file. 
    
    Example
    -------
    >>> geo.georef(r"<path/to/my/file>", to_file = True)   
    """


    # ---- Load & initialize
    data_ds = load_any(data, decode_times = True, decode_coords = 'all')
    
    if var_list is None:
        var_list = main_vars(data_ds)
    elif isinstance(var_list, str):
        var_list = [var_list]
    else:
        var_list = list(var_list)
    
    x_var, y_var = main_space_dims(data_ds)
# ====== old standard time handling ===========================================
#         time_coord = main_time_dims(data_ds)
# =============================================================================
    
    print("\nGeoreferencing data...")

    # ---- Standardize spatial coords, time coords, grid mapping and _FillValue
# =============================================================================
#         if 'X' in data_ds.coords:
#             data_ds = data_ds.rename({'X': 'x'})
#         if 'Y' in data_ds.coords:
#             data_ds = data_ds.rename({'Y': 'y'})
#         if 'latitude' in data_ds.coords:
#             data_ds = data_ds.rename({'latitude': 'lat'})
#         if 'longitude' in data_ds.coords:
#             data_ds = data_ds.rename({'longitude': 'lon'})
# =============================================================================
    if x_var == 'X':
        data_ds = data_ds.rename({'X': 'x'})
    if y_var == 'Y':
        data_ds = data_ds.rename({'Y': 'y'})
    if y_var == 'latitude':
        data_ds = data_ds.rename({'latitude': 'lat'})
    if x_var == 'longitude':
        data_ds = data_ds.rename({'longitude': 'lon'})
    
# ====== old standard time handling ===========================================
#         if len(time_coord) == 1:
#             data_ds = data_ds.rename({time_coord: 'time'})
# =============================================================================
    data_ds = standardize_time_coord(data_ds, **time_kwargs)
    
    data_ds = standardize_grid_mapping(data_ds, var_list = var_list)
    
    data_ds, _ = standardize_fill_value(data_ds, var_list = var_list)
    
    data_ds.attrs['Conventions'] = 'CF-1.12 (under test)'
    
# ======== Useless now? =======================================================
#     data_ds = data_ds.transpose('time', y_var, x_var)
# =============================================================================
    
    ### Operations specific to the data type:
    # --------------------------------------- 
    if isinstance(data_ds, gpd.GeoDataFrame):
        # ---- Add CRS to gpd.GeoDataFrames
        if crs is not None:
            data_ds.set_crs(crs = crs, 
                            inplace = True, 
                            allow_override = True)
            # data_ds = standardize_grid_mapping(data_ds, crs)
            print(f'   _ Coordinates Reference System (epsg:{data_ds.crs.to_epsg()}) included.')
        else:
            if data_ds.crs is None:
                print("   _ Warning: Data contains no CRS. Consider passing the `crs` argument")
    
    elif isinstance(data_ds, xr.Dataset):        
        # ---- Add CRS to xr.Datasets
        if crs is not None:
            data_ds.rio.write_crs(crs, inplace = True)
            print(f'   _ Coordinates Reference System (epsg:{data_ds.rio.crs.to_epsg()}) included.')
        else:
            if data_ds.rio.crs is None:
                print("   _ Warning: Data contains no CRS. Consider passing the `crs` argument")
        
        # ---- Add spatial dims attributes to xr.Datasets
        if ('x' in list(data_ds.coords)) & ('y' in list(data_ds.coords)):
            data_ds.x.attrs = {'standard_name': 'projection_x_coordinate',
                                'long_name': 'x coordinate of projection',
                                'units': 'm'}
            data_ds.y.attrs = {'standard_name': 'projection_y_coordinate',
                                'long_name': 'y coordinate of projection',
                                'units': 'm'}
            print("   _ Standard attributes added for coordinates x and y")
        
        elif ('lon' in list(data_ds.coords)) & ('lat' in list(data_ds.coords)):
            data_ds.lon.attrs = {'standard_name': 'longitude',
                                 'long_name': 'longitude',
                                 'units': 'degree_east'}
            data_ds.lat.attrs = {'standard_name': 'latitude',
                                 'long_name': 'latitude',
                                 'units': 'degree_north'}
            print("   _ Standard attributes added for coordinates lat and lon")


    # ---- Remove statistics
    for var in var_list:
        for optional_attrs in ['AREA_OR_POINT', 'STATISTICS_MAXIMUM',
                               'STATISTICS_MEAN', 'STATISTICS_MINIMUM',
                               'STATISTICS_STDDEV', 'STATISTICS_VALID_PERCENT']:
            if optional_attrs in data_ds[var].attrs:
                data_ds[var].attrs.pop(optional_attrs)   
        
    # ---- Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            export_filepath = '_'.join([os.path.splitext(data)[0], "_georef"]) + os.path.splitext(data)[-1]
            export(data_ds, export_filepath)
        else:
# =============================================================================
#             print("   _ As data input is not a file, the result is exported to a standard directory")
#             output_file = os.path.join(os.getcwd(), f"{'_'.join(['data', 'georef', crs_suffix])}.nc")
# =============================================================================
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        export(data_ds, to_file)
    
        
    # ---- Return variable
    return data_ds


    # =========================================================================
    #%    Mémos / Corrections bugs
    # =========================================================================
    # Si jamais il y a un problème de variable qui se retrouve en 'data_var'
    # au lieu d'etre en 'coords' : 
    #     data_ds = data_ds.set_coords('i')
    
    # S'il y a un problème d'incompatibilité 'missing_value' / '_FillValue' :
    #     data_ds['lon'] = data_ds.lon.fillna(np.nan)
    #     data_ds['lat'] = data_ds.lat.fillna(np.nan)
    
    # Si jamais une variable non essentielle pose problème à l'export : 
    #     data_ds = data_ds.drop('lon')
    #     data_ds = data_ds.drop('lat')
    
    # Pour trouver les positions des valeurs nan :
    #     np.argwhere(np.isnan(data_ds.lon.values))
    
    # Pour reconvertir la date
    #     units, reference_date = ds.time.attrs['units'].split('since')
    #     ds['time'] = pd.date_range(start = reference_date, 
    #                                periods = ds.sizes['time'], freq = 'MS')
    # =========================================================================


    # Créer les coordonnées 'x' et 'y'...
# =============================================================================
#         # ... à partir des lon.lat :
#         # LAISSÉ TOMBÉ, PARCE QUE LEURS VALEURS DE LATITUDE SONT FAUSSES [!]
#         coords_xy = rasterio.warp.transform(rasterio.crs.CRS.from_epsg(4326), 
#                                             rasterio.crs.CRS.from_epsg(27572), 
#                                             np.array(data_ds.lon).reshape((data_ds.lon.size), order = 'C'),
#                                             np.array(data_ds.lat).reshape((data_ds.lat.size), order = 'C'))
#         
#         # data_ds['x'] = np.round(coords_xy[0][0:data_ds.lon.shape[1]], -1) 
#         
#         # Arrondi à la dizaine à cause de l'approx. initiale sur les lat/lon :                                               
#         x = np.round(coords_xy[0], -1).reshape(data_ds.lon.shape[0], 
#                                                data_ds.lon.shape[1], 
#                                                order = 'C')
#         # donne un motif qui se répète autant de fois qu'il y a de latitudes
#         y = np.round(coords_xy[1], -1).reshape(data_ds.lon.shape[1], 
#                                                data_ds.lon.shape[0], 
#                                                order = 'F')
#         # donne un motif qui se répète autant de fois qu'il y a de longitudes
#         
#         # data_ds['x'] = x[0,:] 
#         # data_ds['y'] = y[0,:]
#         data_ds = data_ds.assign_coords(x = ('i', x[0,:]))
#         data_ds = data_ds.assign_coords(y = ('j', y[0,:]))
# =============================================================================


###############################################################################
def standardize_time_coord(data, 
                           *, var = None, 
                           infer_from = 'dims',
                           to_file = False):
    """
    Use a standard time variable as the temporal coordinate.
    Standardize its names into 'time'. If not the main time coordinate, swap 
    it with the main time coordinate.

    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray, geopandas.GeoDataFrame or pandas.DataFrame)
        Data whose temporal coordinate should be renamed.
    var : str, optional
        Variable to rename into 'time'. If not specified, the variable that will
        be renamed into 'time' will be inferred from the detected time coordinate(s).
    infer_from : {'dims', 'coords', 'all'}, default 'dims'
        Only used for xarray variables.
        To specify if the time coordinate should be infered from dimensions,
        coordinates or all variables (coordinates and data variables).
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_std_time'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.

    Returns
    -------
    geopandas.GeoDataFrame, xarray.Dataset or pandas.DataFrame
        Data with the modified name for the temporal coordinate.
        The variable type will be accordingly to the variable type of input ``data``.
    
    If ``to_file`` argument is used, the resulting dataset can also be exported to a file. 
    """
# =============================================================================
#     # Rename 'valid_time' into 'time' (if necessary)
#     for time_avatar in ['valid_time', 'date']:
#         if isinstance(data_ds, (xr.Dataset, xr.DataArray)):
#             if ((time_avatar in data_ds.coords) | (time_avatar in data_ds.data_vars)) \
#                 & ('time' not in data_ds.coords) & ('time' not in data_ds.data_vars):
#                 data_ds = data_ds.rename({time_avatar: 'time'})
#                 
#         elif isinstance(data_ds, (pd.DataFrame, gpd.GeoDataFrame)):
#             if (time_avatar in data_ds.columns) & ('time' not in data_ds.columns):
#                 data_ds = data_ds.rename(columns = {time_avatar: 'time'})
#     
#     
# =============================================================================
    
    print("Standardizing time dimension...")
    
    data_ds = load_any(data)
    
    if isinstance(data_ds, xr.Dataset):
        if ('time' in data_ds.data_vars) | ('time' in data_ds.coords):
            data_ds = data_ds.rename(time = 'time0')
            print("   _ A variable 'time' was already present and was renammed to 'time0'")

    elif isinstance(data_ds, (pd.DataFrame, gpd.GeoDataFrame)): # Note: gpd.GeoDataFrame are also pd.DataFrames
        if 'time' in data_ds.columns:
            data_ds = data_ds.rename(columns = {'time': 'time0'})
            print("   _ A variable 'time' was already present and was renammed to 'time0'")
    elif isinstance(data_ds, xr.DataArray):
        if 'time' in data_ds.coords:
            data_ds = data_ds.rename(time = 'time0')
            print("   _ A variable 'time' was already present and was renammed to 'time0'")

    if infer_from == 'dims':
        time_dims = main_time_dims(data_ds)
        time_coords = main_time_dims(data_ds)
    elif infer_from == 'coords':
        time_dims = main_time_dims(data_ds)
        time_coords = main_time_dims(data_ds, all_coords = True)
    elif infer_from == 'all':
        time_dims = main_time_dims(data_ds)
        time_coords = main_time_dims(data_ds, all_coords = True, all_vars = True)
        
    if isinstance(time_dims, str): time_dims = [time_dims]
    if isinstance(time_coords, str): time_coords = [time_coords]
    
    
    if var is not None:
        # Rename the var specified by user into 'time'
        new_tvar = var
    else:
        # Rename the time coord into 'time'
        if time_coords != []:
            new_tvar = time_coords[0]
        else: # safeguard
            print("   _ Warning: No time dimension has been identified. Consider using `infer_from = 'coords'` or `infer_from = 'all'` arguments.")
            return data_ds
        
    if isinstance(data_ds, (xr.Dataset, xr.DataArray)):
        data_ds = data_ds.rename({new_tvar: 'time'})
        print(f"   _ The variable '{new_tvar}' has been renamed into 'time'")
        
        # In the case of xarray variables, if the user-specified var is
        # not a dim, the function will try to swap it with the time dim
        if new_tvar not in time_dims:
            for d in time_dims:
                # Swap dims with the first dimension that has the same 
                # length as 'time'
                if data_ds['time'].size == data_ds.sizes[d]:
                    data_ds = data_ds.swap_dims({d: 'time'})
                    print(f"   _ The new variable 'time' (prev. '{new_tvar}') has been swaped with the dimension '{d}'")
                    break
                
                else:
                    print(r"   _ Warning: The new variable 'time' (prev. '{new_tvar}') is not a dimension, and no current dimension has been found to match. Consider trying `infer_from = 'coords'` or `infer_from = 'all'` arguments")
            
    elif isinstance(data_ds, (pd.DataFrame, gpd.GeoDataFrame)):
        data_ds = data_ds.rename(columns = {new_tvar: 'time'})
        print(f"   _ The variable '{new_tvar}' has been renamed into 'time'")

            
# =============================================================================
#     if not infer:
#         if isinstance(time_coord, str):
#             if isinstance(data_ds, (xr.Dataset, xr.DataArray)):
#                 data_ds = data_ds.rename({time_coord: 'time'})
#             elif isinstance(data_ds, (pd.DataFrame, gpd.GeoDataFrame)):
#                 data_ds = data_ds.rename(columns = {time_coord: 'time'})
#         elif isinstance(time_coord, list):
#             print("Warning: Time could not be standardized because there are several time coordinate candidates. Consider passing the argument 'infer = True' in ghc.standardize_time_coord()")
#     
#     else:
#         if isinstance(time_coord, list):
#             time_coord = time_coord[0]
#         if isinstance(data_ds, (xr.Dataset, xr.DataArray)):
#             time_coord_avatars = ['t', 'time', 'valid_time',
#                                   'forecast_period', 'date',
#                                   ]
#             time_vars = list(set(list(data_ds.data_vars)).intersection(set(time_coord_avatars)))
#             
#         elif isinstance(data_ds, (pd.DataFrame, gpd.GeoDataFrame)):
#             data_ds = data_ds.rename(columns = {time_coord: 'time'})
#     
#     # Swap the coordinate (if necessary)
#     if time_coord != []:
#         if time_coord != 'time':
#             data_ds = data_ds.swap_dims({time_coord: 'time'})
# =============================================================================
    
    # Make sure the time variable is a datetime
    if not np.issubdtype(data_ds.time, (np.datetime64)):
        try: data_ds['time'] = pd.to_datetime(data_ds['time'])
        except: print(f"   _ Warning: New 'time' variable (prev. '{new_tvar}') could not be converted into datetime dtype. Consider using `infer_from = 'coords'` or `infer_from = 'all'` arguments.")
        
    # Standardize attrs
    if isinstance(data_ds, (xr.Dataset, xr.DataArray)):
        data_ds['time'].attrs['standard_name'] = 'time'
# ======== Necessary or not? How to define the reference datetime? ============
#         data_ds['time'].attrs['units'] = 'days since 1970-01-01'
#         data_ds['time'].attrs['calendar'] = 'gregorian'
# =============================================================================
        
    # Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            export_filepath = os.path.splitext(data)[0] + "_std_time" + os.path.splitext(data)[-1]
            export(data_ds, export_filepath)
        else:
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        export(data_ds, to_file)

    return data_ds


###############################################################################
def standardize_grid_mapping(data, 
                             crs = None,
                             to_file = False,
                             var_list = None):
    """
    Some visualization softwares (such as GIS) need a standard structure 
    for `grid_mapping` information in netCDF datasets:
        
    - `grid_mapping` info should be in `encodings` and not in `attrs`
    - `grid_mapping` info should be stored in a coordinate names 'spatial_ref'
    - ...
    
    This function standardizes `grid_mapping` information, so that it is 
    compatible with such softwares as QGIS.

    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray)
        Dataset (netCDF or xarray variable) whose nodata information will be standardized.
        
        Note that ``data`` will be loaded into a xarray.Dataset or xarray.DataArray.
    crs : int or str or rasterio.crs.CRS, optional
        Coordinate reference system of the source (``data``).    
        When passed as an *integer*, ``src_crs`` refers to the EPSG code. 
        When passed as a *string*, ``src_crs`` can be OGC WKT string or Proj.4 string.
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_std_grid_map'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.
    var_list : (list of) str, optional
        List of main variables can be specified by user, to avoid any prompt.

    Returns
    -------
    data_ds : xarray.Dataset
        Standard *GEOP4TH* variable (xarray.Dataset) with corrected nodata information.
    
    If ``to_file`` argument is used, the resulting dataset can also be exported to a file. 
    """
    
    # ---- Load
    data_ds = load_any(data)
    if not isinstance(data_ds, (xr.Dataset, xr.DataArray)):
        print("Warning: the `standardize_grid_mapping` function is only intended for netCDF datasets")
        return data_ds
    
    # Get main variable
    if var_list is None:
        var_list = main_vars(data_ds)
    elif isinstance(var_list, str):
        var_list = [var_list]
    else:
        var_list = list(var_list)
    
    for var in var_list[::-1]:
        # ---- Get the potential names of grid_mapping variable and clean all 
        # grid_mapping information
        
        # Remove all the metadata about grid_mapping, and save grid_mapping names
        names = set()
        if 'grid_mapping' in data_ds.attrs:
            names.add(data_ds.attrs['grid_mapping'])
            data_ds.attrs.pop('grid_mapping')
        if "grid_mapping" in data_ds.encoding:
            names.add(data_ds.encoding['grid_mapping'])
            data_ds.encoding.pop('grid_mapping')
        if 'grid_mapping' in data_ds[var].attrs:
            names.add(data_ds[var].attrs['grid_mapping'])
            data_ds[var].attrs.pop('grid_mapping')
        if "grid_mapping" in data_ds[var].encoding:
            names.add(data_ds[var].encoding['grid_mapping'])
            data_ds[var].encoding.pop('grid_mapping')

    # Drop all variable or coord corresponding to the previously founded 
    # grid_mapping names
    temp = None
    for n in list(names):
        if n in data_ds.data_vars:
            temp = data_ds[n]
            data_ds = data_ds.drop(n)
        if n in data_ds.coords:
            temp = data_ds[n]
            data_ds = data_ds.reset_coords(n, drop = True)
        
    if crs is None:
        # Use the last grid_mapping value as the standard spatial_ref
        dummy_crs = 2154
        data_ds.rio.write_crs(dummy_crs, inplace = True) # creates the spatial_ref structure and mapping
        data_ds['spatial_ref'] = temp
    else:
        data_ds.rio.write_crs(crs, inplace = True)
    
    # ---- Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            export_filepath = os.path.splitext(data)[0] + "_std_grid_map" + os.path.splitext(data)[-1]
            export(data_ds, export_filepath)
        else:
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        export(data_ds, to_file)

    return data_ds


###############################################################################
def standardize_fill_value(data, *, 
                           var_list = None, 
                           attrs = None, 
                           encod = None,
                           to_file = False):
    """
    Standardize the way the nodata value (fill value) is encoded in a netCDF dataset.
    In netCDF, several ways of embedding nodata information can be used ('_Fillvalue'
    or 'missing_value', in attributes or in encodings). Sometimes multiple
    embeddings are stored in the same dataset. When several nodata information 
    are present in the same dataset, this function
    infers the most relevant one and removes the others. In the end, the relevant nodata
    information will be stored as a '_FillValue' encoding only.

    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray)
        Dataset (netCDF or xarray variable) whose nodata information will be standardized.
        
        Note that ``data`` will be loaded into a xarray.Dataset or xarray.DataArray.
    var_list : (list of) str, optional
        Used to specify if only one data variable has to be standardized. Otherwise, 
        the nodata information will be standardized for all data variables.
    attrs : dict, optional
        If the nodata information is present in an `attrs` dict dissociated from
        the dataset, it can be passed here.
    encod : dict, optional
        If the nodata information is present in an `encoding` dict dissociated from
        the dataset, it can be passed here.
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_std_fill_val'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.

    Returns
    -------
    data_ds : xarray.Dataset
        Standard *GEOP4TH* variable (xarray.Dataset) with corrected nodata information.
    nodata : numeric
        No-data value.
    
    If ``to_file`` argument is used, the resulting dataset can also be exported to a file. 
    """
    
    data_ds = load_any(data)
    if not isinstance(data_ds, (xr.Dataset, xr.DataArray)):
        print("Warning: the `standardize_fill_value` function is only intended for netCDF datasets")
        return data_ds, None
    
    # Initializations
    if var_list is None:
        var_list = main_vars(data_ds)
    elif isinstance(var_list, str):
        var_list = [var_list]
    elif isinstance(var_list, list):
        var_list = var_list
    
    if isinstance(data_ds, xr.Dataset):
        for var in var_list:
            if attrs is None:
                attrs = data_ds[var].attrs
            if encod is None:
                encod = data_ds[var].encoding
            
            # Clean all fill_value info
            if '_FillValue' in data_ds[var].attrs:
                data_ds[var].attrs.pop('_FillValue')
            if 'missing_value' in data_ds[var].attrs:
                data_ds[var].attrs.pop('missing_value')
                
            # Set the fill_value, according to a hierarchical rule
            if '_FillValue' in encod:
                nodata = encod['_FillValue']
                data_ds[var].encoding['_FillValue'] = nodata
            elif '_FillValue' in attrs:
                nodata = attrs['_FillValue']
                data_ds[var].encoding['_FillValue'] = nodata
            elif 'missing_value' in encod:
                nodata = encod['missing_value']
                data_ds[var].encoding['_FillValue'] = nodata
            elif 'missing_value' in attrs:
                nodata = attrs['missing_value']
                data_ds[var].encoding['_FillValue'] = nodata
            else:
                nodata = np.nan
                data_ds[var].encoding['_FillValue'] = nodata
        
    elif isinstance(data_ds, xr.DataArray):
        if attrs is None:
            attrs = data_ds.attrs
        if encod is None:
            encod = data_ds.encoding
        
        # Clean all fill_value info
        if '_FillValue' in data_ds.attrs:
            data_ds.attrs.pop('_FillValue')
        if 'missing_value' in data_ds.attrs:
            data_ds.attrs.pop('missing_value')
        if 'missing_value' in data_ds.attrs:
            data_ds.attrs.pop('missing_value')
            
        # Set the fill_value, according to a hierarchical rule
        if '_FillValue' in encod:
            nodata = encod['_FillValue']
            data_ds.encoding['_FillValue'] = nodata
        elif '_FillValue' in attrs:
            nodata = attrs['_FillValue']
            data_ds.encoding['_FillValue'] = nodata
        elif 'missing_value' in encod:
            nodata = encod['missing_value']
            data_ds.encoding['_FillValue'] = nodata
        elif 'missing_value' in attrs:
            nodata = attrs['missing_value']
            data_ds.encoding['_FillValue'] = nodata
        else:
            nodata = np.nan
            data_ds.encoding['_FillValue'] = nodata
    
    # Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            export_filepath = os.path.splitext(data)[0] + "_std_fill_val" + os.path.splitext(data)[-1]
            export(data_ds, export_filepath)
        else:
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        export(data_ds, to_file)
        
    return data_ds, nodata


#%% FILE MANAGEMENT
###############################################################################
def merge_data(data, 
               *, extension = None, 
               tag = '', 
               flatten = False,
               update_val = False,
               **kwargs):
    """
    This function merge all files inside a folder.

    Parameters
    ----------
    data : (list of) str or pathlib.Path, or variable (xarray.Dataset, xarray.DataArray, geopandas.GeoDataFrame or pandas.DataFrame)
        Iterable of data to merge, or a path to a folder containing data to merge.
        In that case, the arguments ``extension`` and ``tag`` can be passed.
    extension: str, optional
        Only the files with this extension will be retrieved (when ``data`` is a folder path).
    tag: str, optional
        Only the files containing this tag in their names will be retrieved (when ``data`` is a folder path).
    flatten : bool, default False
        If True, data will be flattent over the time axis.
    update_val : bool, default False
        When data values are different, update values (the last dataset has the 
        highest priority)
    **kwargs
        Optional other arguments passed to :func:`geo.load_any` 
        (arguments for ``xarray.open_dataset``, ``pandas.DataFrame.read_csv``,
        ``pandas.DataFrame.to_csv``, ``pandas.DataFrame.read_json`` or 
        ``pandas.DataFrame.to_json`` function calls).
        
        May contain: 
            
        - decode_cf
        - sep
        - encoding
        - force_ascii
        - ...
        
        >>> help(xarray.open_dataset)
        >>> help(pandas.read_csv)
        >>> help(pandas.to_csv)
        >>> ...

    Returns
    -------
    geopandas.GeoDataFrame, xarray.Dataset, pandas.DataFrame or numpy.array
        Merged data is stored in a variable whose type is accordingly to the type of data:
        
        - all vector data will be loaded as a geopandas.GeoDataFrame
        - all raster data and netCDF will be loaded as a xarray.Dataset
        - other data will be loaded either as a pandas.DataFrame (CSV and JSON) or as a numpy.array (TIFF)
    """
    
    # ---- Load file list
    # If data is a list of files:
    if isinstance(data, (list, tuple)):
        # If the list contains paths
        if all([isinstance(data[i], (str, Path)) 
                for i in range(0, len(data))]): 
            data_folder = os.path.split(data[0])[0]
            filelist = data 
            #filelist = [os.path.split(d)[-1] for d in data]
            extension = os.path.splitext(filelist[0])[-1]
        # If the list contains xarray or geopandas variables
        elif all([isinstance(data[i], (xr.Dataset, xr.DataArray, 
                                       gpd.GeoDataFrame, pd.DataFrame)) 
                  for i in range(0, len(data))]):
            data_folder = None
            filelist = data
        else:
            print("Err: Mixed data types")
            return
    # If data is a folder:
    elif isinstance(data, (str, Path)):
        if os.path.isdir(data):
            data_folder, filename_list = get_filelist(data, extension = extension, tag = tag)
            filelist = [os.path.join(data_folder, f) for f in filename_list]
        # If data is a single file:
        elif os.path.isfile(data):
            filelist = [data]
    # If data is a xarray or a geopandas variable
    elif isinstance(data, (xr.Dataset, xr.DataArray, gpd.GeoDataFrame, pd.DataFrame)):
        data_folder = None
        filelist = [data]
        
    # if extension[0] == '.': extension = extension[1:]
    if isinstance(extension, str):
        if extension[0] != '.': extension = '.' + extension

    if len(filelist) > 1:
        print("Merging files...")
        
        if (extension in ['.nc', '.tif', '.asc']) | all([isinstance(data[i], (xr.Dataset, xr.DataArray)) 
                                                     for i in range(0, len(data))]): 
            c = 1
            ds_list = []
            # ---- Append all xr.Datasets into a list
            for f in filelist:
                ds_list.append(load_any(f, **kwargs))
                if isinstance(f, (str, Path)):
                    f_text = os.path.split(f)[-1]
                else:
                    f_text = type(f)
                print(f"      . {f_text}  ({c}/{len(filelist)})")
                c += 1
                
            # ---- Backup of attributes and encodings
            var_list = main_vars(ds_list[0])
    # ========== useless ==========================================================
    #         attrs = ds_list[0][var].attrs.copy()
    # =============================================================================
            encod = {}
            for var in var_list:
                encod[var] = ds_list[0][var].encoding.copy()
        
            # ---- Merge
            if not update_val:
                merged_ds = xr.merge(ds_list) # Note: works only when doublons are identical
            else:
                x, y = main_space_dims(ds_list[0])
                union_x = set(ds_list[0][x].values)
                union_y = set(ds_list[0][y].values)
                for ds in ds_list[1:]:
                    x, y = main_space_dims(ds)
                    union_x = union_x.union(set(ds[x].values))
                    union_y = union_y.union(set(ds[y].values))
                union_x = sorted(union_x)
                union_y = sorted(union_y)[::-1]
                for i in range(0, len(ds_list)):
                    x, y = main_space_dims(ds_list[i])
                    ds_list[i] = ds_list[i].reindex({x: union_x, y: union_y})
                merged_ds = ds_list[0]
                for ds in ds_list[1:]:
                    # First, merged_ds is expanded with ds (merged_ds has priority over ds here)
                    merged_ds = merged_ds.merge(ds, compat = 'override') 
                    # Second, non-null values of ds overwrites merge_ds
                    merged_ds.loc[{dim: ds[dim].values for dim in merged_ds.dims}] = merged_ds.loc[{dim: ds[dim].values for dim in merged_ds.dims}].where(ds.isnull(), ds)
# =============================================================================
#                     merged_ds_aligned, _ = xr.align(merged_ds, ds)
#                     merged_ds_aligned = merged_ds_aligned.where(ds.isnull(), ds)
# =============================================================================
    # ========== wrong ============================================================
    #         merged_ds = xr.concat(ds_list, dim = 'time')
    # =============================================================================
            # Order y-axis from max to min (because order is altered with merge)
            _, y_var = main_space_dims(merged_ds)
            merged_ds = merged_ds.sortby(y_var, ascending = False)
    # ========== useless ==========================================================
    #         merged_ds = merged_ds.sortby('time') # In case the files are not loaded in time order   
    # =============================================================================
            
            # ---- Transferring encodings (_FillValue, compression...)
            for var in var_list:
                merged_ds[var].encoding = encod[var]
            return merged_ds
        
        elif (extension in ['.shp', '.json', '.geojson']) | all([isinstance(data[i], gpd.GeoDataFrame) 
                                                             for i in range(0, len(data))]):
            ### Option 1: data is flattened over the time axis
            if flatten:
                # This variable will store the names of the concatenated columns
                global varying_columns
                varying_columns = []
                
                def agg_func(arg):
                    global varying_columns
    
                    if len(set(arg.values)) == 1:
                        return arg.values[0]
                    else:
                        varying_columns.append(arg.name)
                        return ', '.join(str(v) for v in arg.values)
    # =========== list of texts are not correctly reloaded in python... ===========
    #                     return list(arg.values)
    # =============================================================================
                
                c = 1
# =============================================================================
#                 gdf_list = []
#                 # ---- Append all gpd.GeoDataFrame into a list
#                 for f in filelist:
#                     gdf_list.append(load_any(f))
#                     print(f"      . {f}  ({c}/{len(filelist)})")
#                     c += 1
#                 
#                 merged_gdf = pd.concat(gdf_list)
# =============================================================================
                f = filelist[0]
                merged_gdf = load_any(f)
                if isinstance(f, (str, Path)):
                    f_text = f
                else:
                    f_text = type(f)
                print(f"      . {f_text}  ({c}/{len(filelist)})")
                for f in filelist[1:]:
                    merged_gdf = merged_gdf.merge(load_any(f), 
                                                  how = 'outer',
                                                  # on = merged_df.columns, 
                                                  )
                    if isinstance(f, (str, Path)):
                        f_text = f
                    else:
                        f_text = type(f)
                    print(f"      . {f_text}  ({c}/{len(filelist)})")
                    c += 1
                
    # ========== previous method ==================================================
                # x_var, y_var = main_space_dims(gdf_list[0])
                # merged_gdf = merged_gdf.dissolve(by=[x_var, y_var], aggfunc=agg_func)
                # # Convert the new index (code_ouvrage) into a column as at the origin
                # merged_gdf.reset_index(inplace = True, drop = False)
    # =============================================================================
                merged_gdf['geometry2'] = merged_gdf['geometry'].astype(str)
                merged_gdf = merged_gdf.dissolve(by='geometry2', aggfunc=agg_func)
                # Convert the new index (code_ouvrage) into a column as at the origin
                merged_gdf.reset_index(inplace = True, drop = True)
                
                varying_columns = list(set(varying_columns))
                
                # Correct the dtypes of the concatenated columns, because fiona does
                # not handle list dtypes
                merged_gdf[varying_columns] = merged_gdf[varying_columns].astype(str)
                
                return merged_gdf
            
            else: # No flattening
                c = 1
# ========= previous method with concat =======================================
#                 gdf_list = []
#                 # ---- Append all gpd.GeoDataFrame into a list
#                 for f in filelist:
#                     gdf_list.append(load_any(f))
#                     gdf_list[c]['annee'] = pd.to_datetime(gdf_list[c]['annee'], format = '%Y')
#                     print(f"      . {f}  ({c}/{len(filelist)})")
#                     c += 1
#                 
#                 merged_gdf = pd.concat(gdf_list)
# =============================================================================
                f = filelist[0]
                merged_gdf = load_any(f, **kwargs)
                if isinstance(f, (str, Path)):
                    f_text = f
                else:
                    f_text = type(f)
                print(f"      . {f_text}  ({c}/{len(filelist)})")
                for f in filelist[1:]:
                    merged_gdf = merged_gdf.merge(load_any(f, **kwargs), 
                                                  how = 'outer',
                                                  # on = merged_df.columns, 
                                                  )
                    if isinstance(f, (str, Path)):
                        f_text = f
                    else:
                        f_text = type(f)
                    print(f"      . {f_text}  ({c}/{len(filelist)})")
                    c += 1
                
                return merged_gdf      
    
        elif (extension in ['.csv']) | all([isinstance(data[i], pd.DataFrame) 
                                          for i in range(0, len(data))]):
            c = 1
            f = filelist[0]
            merged_df = load_any(f, **kwargs)
            if isinstance(f, (str, Path)):
                f_text = f
            else:
                f_text = type(f)
            print(f"      . {f_text}  ({c}/{len(filelist)})")
            for f in filelist[1:]:
                merged_df = merged_df.merge(load_any(f, **kwargs), 
                                            how = 'outer',
                                            # on = merged_df.columns, 
                                            )
                if isinstance(f, (str, Path)):
                    f_text = f
                else:
                    f_text = type(f)
                print(f"      . {f_text}  ({c}/{len(filelist)})")
                c += 1
            
            return merged_df  
            
    
    elif len(filelist) == 1:
        print("Warning: Only one file was found.")
        return load_any(filelist[0], **kwargs)
    
    elif len(filelist) == 0:
        print("Err: No file was found")
        return



#%% REPROJECTIONS, CLIP, CONVERSIONS
###############################################################################
def transform(data, *, 
              src_crs = None, 
              base_template = None, 
              bounds = None,  
              bounds_crs = None,
              x0 = None, 
              y0 = None, 
              mask = None, 
              to_file = False,
              export_extension = None, 
              rasterize = False, 
              main_var_list = None,
              rasterize_mode = ['sum', 'dominant', 'and'], 
              **rio_kwargs):
    r"""
    Reproject, clip, rasterize or convert space-time data.
    :func:`transform`, :func:`reproject` and :func:`convert` are three aliases of the same function.

    Parameters
    ----------
    data : str, pathlib.Path, xarray.Dataset, xarray.DataArray, geopandas.GeoDataFrame or pandas.DataFrame
        Data to transform. Supported file formats are *.tif*, *.asc*, *.nc*, vector 
        formats supported by geopandas (*.shp*, *.json*, ...), and *.csv*.
    src_crs : int or str or rasterio.crs.CRS, optional
        Coordinate reference system of the source (``data``).    
        When passed as an *integer*, ``src_crs`` refers to the EPSG code. 
        When passed as a *string*, ``src_crs`` can be OGC WKT string or Proj.4 string.
    base_template : str, pathlib.Path, xarray.DataArray or geopandas.GeoDataFrame, optional
        Filepath, used as a template for spatial profile. Supported file formats
        are *.tif*, *.nc* and vector formats supported by geopandas (*.shp*, *.json*, ...).
    bounds : iterable or None, optional, default None
        Boundaries of the target domain as a tuple (x_min, y_min, x_max, y_max).
        The values are expected to be given according to ``bounds_crs`` if it is not None. 
        If ``bounds_crs`` is None, ``bounds`` are expected to be given according to the destination
        CRS ``dst_crs`` if it is not None. It ``dst_crs`` is also None, ``bounds`` are then
        expected to be given according to the source CRS (``src_crs`` of ``data``'s CRS).
    bounds_crs : int or str or rasterio.crs.CRS, optional
        Coordinate reference system of the bounds (if ``bounds`` is not None).    
        When passed as an *integer*, ``src_crs`` refers to the EPSG code. 
        When passed as a *string*, ``src_crs`` can be OGC WKT string or Proj.4 string.
    x0: number, optional, default None
        Origin of the X-axis, used to align the reprojection grid. 
    y0: number, optional, default None
        Origin of the Y-axis, used to align the reprojection grid. 
    mask : str, pathlib.Path, shapely.geometry, xarray.DataArray or geopandas.GeoDataFrame, optional
        Filepath of mask used to clip the data.  
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_geop4th'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.
    export_extension : str, optional
        Extension to which the data will be converted and exported. Only used
        when the specified ``data`` is a filepath. It ``data`` is a variable
        and not a file, it will not be exported.
        
        If ``rasterize=True`` and ``export_extension`` is not specified, it will
        be set to '.tif' by default.
    rasterize : bool, default False
        Option to rasterize data (if ``data`` is a vector data).
    main_var_list : iterable, default None
        Data variables to rasterize. Only used if ``rasterize`` is ``True``.
        If ``None``, all variables in ``data`` are rasterized.
    rasterize_mode : str or list of str, or dict, default ['sum', 'dominant', 'and']
        Defines the mode to rasterize data:
            
        - for numeric variables: ``'mean'`` or ``'sum'`` (default)
        - for categorical variables: ``'percent'`` or ``'dominant'`` (default)
            
          - ``'dominant'`` rises the most frequent level for each cell
          - ``'percent'`` creates a new variable per level, which stores 
          the percentage (from 0 to 100) of occurence of this level compared
          to all levels, for each cell.
                
        - for boolean variables: ``'or'`` or ``'and'`` (default)
        The modes can be specified for each variable by passing ``rasterize_mode``
        as a dict: ``{'<var1>': 'mean', '<var2>': 'percent', ...}``. This argument
        specification makes it possible to force a numeric variable to be rasterized
        as a categorical variable. Unspecified variables will be rasterized with the default mode.
        
    
    **rio_kwargs : keyword args, optional
        Argument passed to the ``xarray.Dataset.rio.reproject()`` function call.
        
        **Note**: These arguments are prioritary over ``base_template`` attributes.
        
        May contain: 
            
        - ``dst_crs`` : str
        - ``resolution`` : float or tuple
        - ``shape`` : tuple (int, int)
        - ``transform`` : Affine
        - ``nodata`` : float or None
        - ``resampling`` : 
                
          - see ``help(rasterio.enums.Resampling)``
          - most common are: ``5`` (average), ``13`` (sum), ``0`` (nearest), 
            ``9`` (min), ``8`` (max), ``1`` (bilinear), ``2`` (cubic)...
          - the functionality ``'std'`` (standard deviation) is also available
            
        - see ``help(xarray.Dataset.rio.reproject)``

    Returns
    -------
    Transformed data : xarray.Dataset or geopandas.GeoDataFrame.
        The type of the resulting variable is accordingly to the type of input data and to
        the conversion operations (such as rasterize):
        
        - all vector data will be output as a geopandas.GeoDataFrame
        - all raster data and netCDF will be output as a xarray.Dataset

    If ``data`` is a file, the resulting dataset will be exported to a file as well
    (with the suffix '_geop4th'), except if the parameter ``to_file=False`` is passed.
    """
    
    #%%%% Load data, base and mask
    # ===========================
    # Export management
    raster_extensions = ['.nc', '.tif', '.asc'] # supported raster extensions
    vector_extensions = ['.shp', '.json', '.gpkg', '.csv'] # supported vector extensions
    
    if export_extension is not None:
        if to_file == False: to_file = True
    
    to_export = False
    if to_file == True:
        if isinstance(data, (str, Path)):
            if export_extension is None:
                if rasterize:
                    export_extension = '.tif'
                else:
                    export_extension = os.path.splitext(data)[-1]
            if export_extension is not None:
                export_filepath = os.path.splitext(data)[0] + "_geop4th" + export_extension
                to_export = True
                src_extension = os.path.splitext(data)[-1]
                if src_extension in vector_extensions:
                    if export_extension in vector_extensions:
                        print(f"The transformed data will be exported to {export_filepath}")
                    elif export_extension in raster_extensions:
                        if not rasterize:
                            print(f"The data will be rasterized before exported to {export_filepath}")
                            rasterize = True
                        else:
                            print(f"The transformed data will be exported to {export_filepath}")
                    else:
                        print("Warning: `export_extension` is not recognized. The data will not be exported to a file.")
                elif src_extension in raster_extensions:
                    if export_extension in raster_extensions:
                        print(f"The transformed data will be exported to {export_filepath}")
                    elif export_extension in vector_extensions:
                        print("Warning: `export_extension` implies data to be vectorized, but vectorization is not yet implemented. The data will not be exported to a file.")
                    else:
                        print("Warning: `export_extension` is not recognized. The data will not be exported to a file.")
        else:
            if export_extension is not None:
                print("Warning: the parameter `export_extension` is only used when `data` refers to a file. When `data` is a variable, it will not be exported to a file.")
            else:
                print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`")
    
    elif isinstance(to_file, (str, Path)):
        to_export = True
        export_filepath = to_file
        # Safeguard
        if export_extension is not None:
            if os.path.splitext(to_file)[-1] != export_extension:
                print("Warning: `export_extension` will be discarded as it does not match `to_file`")
    
    else:
        if export_extension is not None:
            print("Warning: the parameter `export_extension` is not compatible with `to_file=False`")
        
    # Initializations
    data_ds = load_any(data, decode_times = True, decode_coords = 'all')
    
    # base
    base_ds = None
    if base_template is not None:
        base_ds = load_any(base_template, decode_times = True, decode_coords = 'all')
    
    # source CRS
    if src_crs is not None:
        if isinstance(data_ds, xr.Dataset): # raster
            data_ds.rio.write_crs(src_crs, inplace = True)
        elif isinstance(data_ds, gpd.GeoDataFrame): # vector
            data_ds.set_crs(crs = src_crs, inplace = True, allow_override = True)
    
    else:
        if isinstance(data_ds, xr.Dataset): # raster
            src_crs = data_ds.rio.crs
        elif isinstance(data_ds, gpd.GeoDataFrame): # vector
            src_crs = data_ds.crs
        elif isinstance(data_ds, pd.DataFrame): # csv
            print("Error: The `src_crs` argument is required for using this function with CSV or pandas.DataFrames")
            return

    # mask
    if mask is not None:
        if not isinstance(mask, (Point, Polygon, MultiPolygon)):
            mask_ds = load_any(mask, decode_times = True, decode_coords = 'all')
        else:
            # the geometry is converted into a gpd.GeoDataFrame
# =============================================================================
#             if src_crs is not None:
#                 geom_crs = src_crs
#             else:
#                 geom_crs = data_ds.rio.crs
# =============================================================================
            mask_ds = gpd.GeoDataFrame([0], geometry = [mask], crs = src_crs)
    
    # Identify spatial coord names
# =============================================================================
#     for yname in ['latitude', 'lat', 'y', 'Y']:
#         if yname in data_ds.coords:
#             yvar = yname
#     for xname in ['longitude', 'lon', 'x', 'X']:
#         if xname in data_ds.coords:
#             xvar = xname
# =============================================================================
    if not isinstance(data_ds, gpd.GeoDataFrame):
        xvar, yvar = main_space_dims(data_ds)
    
    # Initialize x0 and y0 if None
    if isinstance(data_ds, (xr.Dataset, xr.DataArray)): # raster
        x_res, y_res = data_ds.rio.resolution()
        if x0 is None:
            x0 = data_ds[xvar][0].item() + x_res/2
        if y0 is None:
            y0 = data_ds[yvar][0].item() + y_res/2
    elif isinstance(data_ds, gpd.GeoDataFrame): # vector
        if x0 is None:
            x0 = data_ds.total_bounds[0] # xmin
        if y0 is None:
            y0 = data_ds.total_bounds[1] # ymin
    elif isinstance(data_ds, pd.DataFrame): # csv
        if x0 is None:
            x0 = data_ds[xvar].min() # xmin
        if y0 is None:
            y0 = data_ds[yvar].max() # ymin
    
    #%%%% Compute parameters
    # =====================
    print("\nComputing parameters...")
    
    # ---- Safeguards against redundant arguments
    # -------------------------------------------
    if ('transform' in rio_kwargs) & ('shape' in rio_kwargs) & (bounds is not None):
        print("   _ Err: bounds cannot be passed alongside with both transform and shape")
        return
    
    if 'resolution' in rio_kwargs:
        if ('shape' in rio_kwargs) | ('transform' in rio_kwargs):
        # safeguard to avoid RioXarrayError
            print("   _ Err: resolution cannot be used with shape or transform.")
            return
        
    if (bounds is not None) & (mask is not None):
        print("   _ Err: bounds and mask cannot be passed together")
        return
    
    
    # ---- Backup of rio_kwargs
    # -------------------------
    rio_kwargs0 = rio_kwargs.copy()
    
    # Info message
    if ('transform' in rio_kwargs) & (bounds is not None):
        if (bounds[0] != rio_kwargs['transform'][2]) | (bounds[3] != rio_kwargs['transform'][5]):
            print("   _ ...")
    
    
    # ---- No base_template
    # ---------------------
    if base_ds is None:
        ### Retrieve <dst_crs> (required parameter)
        if 'dst_crs' not in rio_kwargs:
# =============================================================================
#             if isinstance(data_ds, (xr.Dataset, xr.DataArray)): # raster
#                 rio_kwargs['dst_crs'] = data_ds.rio.crs
#             elif isinstance(data_ds, gpd.GeoDataFrame): # vector
#                 rio_kwargs['dst_crs'] = data_ds.crs
#             elif isinstance(data_ds, pd.DataFrame): # csv
#                 rio_kwargs['dst_crs'] = src_crs
# =============================================================================
            rio_kwargs['dst_crs'] = src_crs 
            # Reminder: src_crs is not None. If src_crs were passed as a None input, 
            # it has been previously extracted from data_ds

            
    # ---- Base_template
    # ------------------
    # if there is a base, it will be used after being updated with passed parameters
    else:
        base_kwargs = {}
        
        ### 1. Retrieve all the available info from base:
        if isinstance(base_ds, (xr.Dataset, xr.DataArray)):
            # A- Retrieve <dst_crs> (required parameter)
            if 'dst_crs' not in rio_kwargs:
                try:
                    rio_kwargs['dst_crs'] = base_ds.rio.crs
                except:
# =============================================================================
#                     if isinstance(data_ds, (xr.Dataset, xr.DataArray)): # raster
#                         rio_kwargs['dst_crs'] = data_ds.rio.crs
#                     elif isinstance(data_ds, gpd.GeoDataFrame): # vector
#                         rio_kwargs['dst_crs'] = data_ds.crs
#                     elif isinstance(data_ds, pd.DataFrame): # csv
#                         rio_kwargs['dst_crs'] = src_crs
# =============================================================================
                    rio_kwargs['dst_crs'] = src_crs
                    # Reminder: src_crs is not None. If src_crs were passed as a None input, 
                    # it has been previously extracted from data_ds
            
            # B- Retrieve <shape> and <transform>
            base_kwargs['shape'] = base_ds.rio.shape
            base_kwargs['transform'] = base_ds.rio.transform()
            # Note that <resolution> is ignored from base_ds
                
        elif isinstance(base_ds, gpd.GeoDataFrame):
            # A- Retrieve <dst_crs> (required parameter)
            if 'dst_crs' not in rio_kwargs:
                try:
                    rio_kwargs['dst_crs'] = base_ds.crs
                except:
# =============================================================================
#                     if isinstance(data_ds, (xr.Dataset, xr.DataArray)): # raster
#                         rio_kwargs['dst_crs'] = data_ds.rio.crs
#                     elif isinstance(data_ds, gpd.GeoDataFrame): # vector
#                         rio_kwargs['dst_crs'] = data_ds.crs
#                     elif isinstance(data_ds, pd.DataFrame): # csv
#                         rio_kwargs['dst_crs'] = src_crs
# =============================================================================
                    rio_kwargs['dst_crs'] = src_crs
                    # Reminder: src_crs is not None. If src_crs were passed as a None input, 
                    # it has been previously extracted from data_ds
            
            # B- Retrieve <shape> and <transform>
            if 'resolution' in rio_kwargs:
                # The bounds of gpd base are used with the user-defined resolution
                # in order to compute 'transform' and 'shape' parameters:
                x_res, y_res = format_xy_resolution(
                    resolution = rio_kwargs['resolution'])
                shape, x_min, y_max = get_shape(
                    x_res, y_res, base_ds.total_bounds, x0, y0)
                base_kwargs['transform'] = Affine(x_res, 0.0, x_min,
                                                  0.0, y_res, y_max)
                base_kwargs['shape'] = shape
            else:
                print("   _ Err: resolution needs to be passed when using a vector base")
                return
            
        ### 2. Update <base_kwargs> with <rio_kwargs>
        for k in rio_kwargs:
            base_kwargs[k] = rio_kwargs[k]
        # Replace rio_kwargs with the updated base_kwargs
        rio_kwargs = base_kwargs
    
    
    # ---- Mask
    # ---------
    # <mask> has priority over bounds or rio_kwargs
    if mask is not None:
        # Reproject the mask
        if isinstance(mask_ds, gpd.GeoDataFrame):
            mask_ds.to_crs(crs = rio_kwargs['dst_crs'], inplace = True)
            bounds_mask = mask_ds.total_bounds
        elif isinstance(mask_ds, (xr.Dataset, xr.DataArray)):
            mask_ds = mask_ds.rio.reproject(dst_crs = rio_kwargs['dst_crs'])
            # On a xr.Dataset mask, only `1` or other positive values are taken into account (`0` and `nan` are excluded from the mask)
            mask_ds = mask_ds.where(mask_ds > 0, drop = True)
            # As rasterio.reproject() inverts the y axis direction, the ymax and ymin needs to be swapped
            bounds_mask = (mask_ds.rio.bounds()[0], mask_ds.rio.bounds()[3],
                           mask_ds.rio.bounds()[2], mask_ds.rio.bounds()[1])
    else:
        bounds_mask = None
    
    
    # ---- Bounds
    # -----------
    # <bounds> has priority over rio_kwargs
    if (bounds is not None) | (bounds_mask is not None):
        if bounds_mask is not None:
            bounds = bounds_mask
        else:
            if bounds is not None:
                print("   _ Note that bounds should be in the format (x_min, y_min, x_max, y_max) and in `bounds_crs` (if `bounds_crs` is None, `dst_crs` is considered instead if it exists, otherwise `src_crs` or `data`'s CRS is used')")
                if bounds_crs is not None:
                    # reprojection of bounds
                    bounds_box = Polygon([
                        (bounds[0], bounds[1]),
                        (bounds[2], bounds[1]), 
                        (bounds[2], bounds[3]), 
                        (bounds[0], bounds[3]),
                        (bounds[0], bounds[1]),
                        ])
                    bounds_gdf = gpd.GeoDataFrame([0], crs = bounds_crs, geometry = [bounds_box])
                    bounds = bounds_gdf.to_crs(rio_kwargs['dst_crs']).total_bounds                    
            
        ### Apply <bounds> values to rio arguments
        if ('shape' in rio_kwargs0):
            # resolution will be defined from shape and bounds
            x_res, y_res = format_xy_resolution(bounds = bounds, 
                                                shape = rio_kwargs['shape'])
            rio_kwargs['transform'] = Affine(x_res, 0.0, bounds[0],
                                              0.0, y_res, bounds[3])
            
        elif ('resolution' in rio_kwargs0):
            # shape will be defined from resolution and bounds
            x_res, y_res = format_xy_resolution(
                resolution = rio_kwargs['resolution'])
            shape, x_min, y_max = get_shape(
                x_res, y_res, bounds, x0, y0)
            rio_kwargs['transform'] = Affine(x_res, 0.0, x_min,
                                              0.0, y_res, y_max)
            rio_kwargs['shape'] = shape
            
        # elif ('transform' in rio_kwargs0):
        else:
            if isinstance(data_ds, (xr.Dataset, xr.DataArray)):
                # shape will be defined from transform and bounds
                if not 'transform' in rio_kwargs:
                    rio_kwargs['transform'] = data_ds.rio.transform()
                x_res, y_res = format_xy_resolution(
                    resolution = (rio_kwargs['transform'][0],
                                  rio_kwargs['transform'][4]))
                shape, x_min, y_max = get_shape(
                    x_res, y_res, bounds, x0, y0)
                rio_kwargs['transform'] = Affine(x_res, 0.0, x_min,
                                                  0.0, y_res, y_max)
                rio_kwargs['shape'] = shape
        
    
    # ---- Resolution
    # ---------------
    if ('resolution' in rio_kwargs) and ('transform' in rio_kwargs):
        x_res, y_res = format_xy_resolution(
            resolution = rio_kwargs['resolution'])
        transform = list(rio_kwargs['transform'])
        transform[0] = x_res
        transform[4] = y_res
        rio_kwargs['transform'] = Affine(*transform[0:6])
        rio_kwargs.pop('resolution')   
        
    
    # ---- Resampling
    # ---------------
    if 'resampling' not in rio_kwargs:
        # by default, resampling is 5 (average) instead of 0 (nearest)
        rio_kwargs['resampling'] = rasterio.enums.Resampling(5)
    else:
        if isinstance(rio_kwargs['resampling'], int):
            rio_kwargs['resampling'] = rasterio.enums.Resampling(rio_kwargs['resampling'])
        elif len(rio_kwargs['resampling']) == 1:
            if isinstance(rio_kwargs['resampling'][0], int):
                rio_kwargs['resampling'] = rasterio.enums.Resampling(rio_kwargs['resampling'][0])


    #%%%% Reproject
    # ===========
    print("\nReprojecting...")
    
    if isinstance(data_ds, (xr.Dataset, xr.DataArray)): # raster
        # ---- Reproject raster
        # Backup of attributes and encodings
        if isinstance(data_ds, xr.Dataset):
            attrs_dict = {var: data_ds[var].attrs.copy() for var in data_ds.data_vars}
            encod_dict = {var: data_ds[var].encoding.copy() for var in data_ds.data_vars}
        elif isinstance(data_ds, xr.DataArray):
            attrs_dict = data_ds.attrs.copy()
            encod_dict = data_ds.encoding.copy()
        
        # Handle timedelta, as they are not currently supported (https://github.com/corteva/rioxarray/discussions/459)
        if isinstance(data_ds, xr.Dataset):
            NaT_dict = {}
            for var in data_ds.data_vars:
                NaT_dict[var] = False
    # ========== previous handmade method =========================================
    #             # Get one non-nan value
    #             sample_non_nan_val = data_ds[var].median(skipna = True)
    #             # If this value is a timedelta:
    #             if isinstance(sample_non_nan_val, (pd.Timedelta, np.timedelta64)):
    # =============================================================================
                if np.issubdtype(data_ds[var], np.timedelta64):
                    NaT_dict[var] = True
                    
                    data_ds[var] = data_ds[var].dt.days
                    data_ds[var].encoding = encod_dict[var]
        elif isinstance(data_ds, xr.DataArray):
            NaT_dict = False
            if np.issubdtype(data_ds, np.timedelta64):
                NaT_dict = True
                
                data_ds = data_ds.dt.days
                data_ds.encoding = encod_dict
        
        if ('x' in list(data_ds.coords)) & ('y' in list(data_ds.coords)) & \
            (('lat' in list(data_ds.coords)) | ('lon' in list(data_ds.coords))):
            # if lat and lon are among coordinates, they should be temporarily moved
            # to variables to be reprojected
            data_ds = data_ds.reset_coords(['lat', 'lon'])
        
        if rio_kwargs['resampling'] == 'std': # special case for standard deviation
                                              # because std is not part of rasterio
                                              # resampling methods.
            rio_kwargs.pop('resampling')
            
            data_reprj_mean = data_ds.rio.reproject(
                resampling = rasterio.enums.Resampling(5), # average
                **rio_kwargs)
            
            square_ds = data_ds**2
            
            sumsquare = square_ds.rio.reproject(
                resampling = rasterio.enums.Resampling(13), # sum,
                **rio_kwargs)
            
            n_upscale = abs(np.prod(data_reprj_mean.rio.resolution())/np.prod(data_ds.rio.resolution()))
            if n_upscale > 1:
                data_reprj = np.sqrt(abs(1/n_upscale*sumsquare - data_reprj_mean**2))
            else:
                print("Err: Standard Deviation can only be computed if there is a downscaling. A resolution argument should be passed")
        
        else: # normal case
            data_reprj = data_ds.rio.reproject(**rio_kwargs) # rioxarray

        
        if ('x' in list(data_ds.coords)) & ('y' in list(data_ds.coords)) & \
            (('lat' in list(data_ds.coords)) | ('lon' in list(data_ds.coords))):
            # if lat and lon are among coordinates, they should be temporarily moved
            # to variables to be reprojected
            data_reprj = data_reprj.set_coords(['lat', 'lon'])
        
# ======= NOT FINISHED ========================================================
#         # Handle timedelta
#         if NaT:
#             val = pd.to_timedelta(data_reprj[var].values.flatten(), unit='D').copy()
#             data_reprj[var] = val.to_numpy().reshape(data_reprj[var].shape)
#             # It is still required to precise the dimensions...
# =============================================================================
        
        # Correct _FillValues for all data_variables
        if isinstance(data_ds, xr.Dataset):
            for var in attrs_dict:
                data_reprj, _ = standardize_fill_value(
                    data_reprj, var_list = var, 
                    encod = encod_dict[var], attrs = attrs_dict[var])
                if NaT_dict[var]:
                    data_reprj[var] = pd.to_timedelta(data_reprj[var], units = 'D')
        elif isinstance(data_ds, xr.DataArray):
            data_reprj, _ = standardize_fill_value(
                data_reprj, 
                encod = encod_dict, attrs = attrs_dict)
            if NaT_dict:
                data_reprj = pd.to_timedelta(data_reprj, units = 'D')
        
        # ---- Clip raster (to refine the clip to the exact shape of the mask,
        # not just bounds)
        if mask is not None:
            if isinstance(mask_ds, gpd.GeoDataFrame):
                data_reprj = data_reprj.rio.clip(mask_ds.geometry.apply(mapping),
                                     mask_ds.crs,
                                     all_touched = True)
            elif isinstance(mask_ds, (xr.Dataset, xr.DataArray)):
                data_reprj = data_reprj.where(mask_ds)
        
        ds_reprj = data_reprj
    
    elif isinstance(data_ds, gpd.GeoDataFrame): # vector
        # ---- Reproject vector
        data_reprj = data_ds.to_crs(crs = rio_kwargs['dst_crs'], inplace = False)
        
        # ---- Clip vector
        if mask is not None:
            if isinstance(mask_ds, gpd.GeoDataFrame):
                data_reprj = data_reprj.clip(mask = mask_ds)
            elif isinstance(mask_ds, (xr.Dataset, xr.DataArray)):
                data_reprj = data_reprj.clip(mask = bounds) # faster...
                # ...but the most rigorous way would be to vectorize the
                # raster and to intersect it with data_reprj
                
        ds_reprj = data_reprj # if rasterize is True, ds_reprj will be re-instantiated
        
        if rasterize: 
        # (note that `ds_reprj` above will not be considered under `rasterize=True` condition and will be reinstantiated instead)
        # ---- Rasterize vector
            # Safeguard (maybe useless)
            if 'transform' not in rio_kwargs:
                if 'resolution' in rio_kwargs:
                    x_res, y_res = format_xy_resolution(
                        resolution = rio_kwargs['resolution'])
                    shape, x_min, y_max = get_shape(
                        x_res, y_res, data_reprj.total_bounds, x0, y0)
                    
                    transform_ = Affine(x_res, 0.0, x_min,
                                        0.0, y_res, y_max)
                    
                    rio_kwargs['transform'] = transform_
                    rio_kwargs.pop('resolution')
                    
                else:
                    print("Err: A resolution is needed to rasterize vector data")
                    return
            # height = int((data_ds.total_bounds[3] - data_ds.total_bounds[1]) / rio_kwargs['resolution'])
            # width = int((data_ds.total_bounds[2] - data_ds.total_bounds[0]) / rio_kwargs['resolution'])

            # transform_ = Affine(rio_kwargs['resolution'], 0.0, data_ds.total_bounds[0], 
            #                     0.0, -rio_kwargs['resolution'], data_ds.total_bounds[3])
        
            
# =============================================================================
#             global measure_main_vars
#             measure_main_var = main_vars(data_reprj)                
# =============================================================================
# =============================================================================
#             for var in data_reprj.loc[:, data_reprj.columns != 'geometry']:
# =============================================================================
            if main_var_list is None:
                # var_list = data_ds[:, data_ds.columns != 'geometry'].columns
                var_list = data_ds.drop('geometry', axis = 1).columns
            else:
                var_list = main_var_list
            
            if 'geometry' in var_list: var_list = list(set(var_list) - set('geometry'))
            
            
# =============================================================================
#             geo_grid = make_geocube(
#                 vector_data = data_reprj,
#                 measurements = [var],
#                 # measurements = data_reprj.columns[:-1], # chaque colonne deviendra un xr.DataArray
#                 # out_shape = shape,
#                 # transform = rio_kwargs['transform'],
#                 resolution = (rio_kwargs['transform'][0], rio_kwargs['transform'][4]),
#                 rasterize_function = functools.partial(rasterize_image, merge_alg = merge_alg),
#                 )
# =============================================================================
# Between rasterio and geocube, rasterio has been chosen, for several reasons:
#   - rasterio installation raises less conflicts
#   - advantages of geocube are almost as complexe to use as to implement them with rasterio:
#      - the 'categorical_enums' functionality is affected by merge_alg
#      - no way to output the most common level
            
            ds_reprj = xr.Dataset()
            x_coords = np.arange(x_min, x_min + shape[1]*x_res, x_res).astype(np.float32)
            y_coords = np.arange(y_max, y_max + shape[0]*y_res, y_res).astype(np.float32)
            coords = [y_coords, x_coords]
            dims = ['y', 'x']
            
            numeric_col = data_reprj.select_dtypes(include = 'number').columns
            timedelta_col = data_reprj.select_dtypes(include = ['timedelta']).columns
            bool_col = data_reprj.select_dtypes(include = bool).columns
            categorical_col = data_reprj.select_dtypes(include = [object, 'category'], 
                                                     exclude = ['number', 'datetime', 'datetimetz', 'timedelta', bool]).columns
            
            # Format <rasterize_mode>:
            # ------------------------
            # Correct categorical_col if unusual categorical variables are indicated in rasterize_mode 
            if isinstance(rasterize_mode, dict):
                for var in rasterize_mode:
                    # if user has specified a 'categorical' mode for a variable
                    if rasterize_mode[var] in ['dominant', 'percent']:
                        # data_reprj[var].astype('category')
                        # and if this variable has not already been identified as categorical (for example if it is numeric)
                        if not var in categorical_col:
                            # then it is appended to categorical variables list
                            categorical_col.append(var)
            
            # Safeguard
            if isinstance(rasterize_mode, str):
                rasterize_mode = [rasterize_mode]
            
            if isinstance(rasterize_mode, list):
                rm_dict = {}
                for rm in rasterize_mode: 
                    if rm in ['sum', 'mean']:
                        rm_dict_add = {num_var: rm for num_var in (set(numeric_col).union(set(timedelta_col))).intersection(set(var_list))}
                    elif rm in ['dominant', 'percent']:
                        rm_dict_add = {num_var: rm for num_var in set(categorical_col).intersection(set(var_list))}
                    elif rm in ['and', 'or']:
                        rm_dict_add = {num_var: rm for num_var in set(bool_col).intersection(set(var_list))}
                    
                    rm_dict = {**rm_dict, **rm_dict_add} # merge dictionnaries
                
                rasterize_mode = rm_dict
            
            for var in var_list:
                if var not in rasterize_mode:
                    if var in set(numeric_col).union(set(timedelta_col)):
                        rasterize_mode[var] = 'sum'
                    elif var in categorical_col:
                        rasterize_mode[var] = 'dominant'
                    elif var in bool_col:
                        rasterize_mode[var] = 'and'
            
# ======== already in % Load data =============================================
#             xvar, yvar = main_space_dims(data_reprj)
# =============================================================================
            if not isinstance(xvar, list):
                xvar = [xvar]
            if not isinstance(yvar, list):
                yvar = [yvar]
            # Numeric space variables are not summed
            for x in xvar:
                if x in rasterize_mode:
                    rasterize_mode[x] = "mean"
            for y in yvar:
                if y in rasterize_mode:
                    rasterize_mode[y] = "mean"            

            # Time axis management
# ======== previous version ===================================================
#             datetime_col = data_reprj.select_dtypes(include = ['datetime', 'datetimetz']).columns
# =============================================================================
            datetime_col = main_time_dims(data_reprj)
            if len(datetime_col) == 1:
                print(f"A time axis has been detected in column '{datetime_col[0]}'")
                t_coords = data_reprj[datetime_col[0]].unique()
                coords = [t_coords] + coords
                dims = ['time'] + dims
                
                for num_var in (set(numeric_col).union(set(timedelta_col))).intersection(set(var_list)):
                    data_3D = []
                    for t in t_coords:
                        data_reprj_temp = data_reprj[data_reprj[datetime_col[0]] == t]   
                    
                        rasterized_data = rasterio.features.rasterize(
                            [(val['geometry'], val[num_var]) for _, val in data_reprj_temp.iterrows()],
                            out_shape = shape,
                            transform = rio_kwargs['transform'],
                            fill = 0, # np.nan
                            merge_alg = rasterio.enums.MergeAlg.add,
                            all_touched = False,
                            # dtype = rasterio.float64, # rasterio.float32,
                            )
                        
                        # Normalize if mode == 'mean' instead of 'sum'
                        if rasterize_mode[num_var] == "mean":
                            rasterized_weight = rasterio.features.rasterize(
                                [(val['geometry'], 1) for _, val in data_reprj_temp.iterrows()],
                                out_shape = shape,
                                transform = rio_kwargs['transform'],
                                fill = 0, # np.nan
                                merge_alg = rasterio.enums.MergeAlg.add,
                                all_touched = False,
                                # dtype = rasterio.float64, # rasterio.float32,
                                )

                            # Normalize
                            rasterized_data = rasterized_data / rasterized_weight
                            
                            # Replace inf with np.nan
                            np.nan_to_num(rasterized_data, posinf = np.nan)
                        
                        data_3D.append(rasterized_data)
                        
                    # Fill the dataset
                    ds_reprj[num_var] = xr.DataArray(np.array(data_3D),
                                                     coords = coords,
                                                     dims = dims)
                    
                        # Replace 0 with np.nan
# =============================================================================
#                         ds_reprj = ds_reprj.where(ds_reprj != 0)
# =============================================================================

                # Categorical variables: level by level
                for cat_var in set(categorical_col).intersection(set(var_list)):
                    # Case 'dominant' (more frequent):
                    if rasterize_mode[cat_var] == "dominant":
                        data_3D = []
                        for t in t_coords:
                            data_reprj_temp = data_reprj[data_reprj[datetime_col[0]] == t]   
                        
                            levels = data_reprj[cat_var].unique()
                            # String/categorical data are not handled well by GIS softwares...
                            id_levels = {i:levels[i] for i in range(0, len(levels))}
                            for i in id_levels:
                                data_reprj_lvl = data_reprj_temp[data_reprj_temp[cat_var] == levels[i]] 
                                rasterized_levels = rasterio.features.rasterize(
                                    [(val['geometry'], 1) for _, val in data_reprj_lvl.iterrows()],
                                    out_shape = shape,
                                    transform = rio_kwargs['transform'],
                                    fill = 0, # np.nan
                                    merge_alg = rasterio.enums.MergeAlg.add,
                                    all_touched = False,
                                    # dtype = rasterio.float32,
                                    )
                                
                                if i == 0: # 1er passage
                                    rasterized_data = rasterized_levels.copy().astype(int)
                                    rasterized_data[:] = -1
                                    rasterized_data[rasterized_levels > 0] = i
                                    rasterized_levels_prev = rasterized_levels.copy()
                                else:
                                    rasterized_data[rasterized_levels > rasterized_levels_prev] = i
                                    rasterized_levels_prev = np.maximum(rasterized_levels,
                                                                        rasterized_levels_prev)
                                    
                            data_3D.append(rasterized_data)
                        
                        ds_reprj[cat_var] = xr.DataArray(np.array(data_3D),
                                                         coords = coords,
                                                         dims = dims)
                        
                        # Inform
                        nodata_level = {-1: 'nodata'}
                        id_levels = {**nodata_level, **id_levels}
                        ds_reprj[f"{cat_var}_levels"] = ', '.join([f"{k}: {id_levels[k]}" for k in id_levels]) # str(id_levels)
                        ds_reprj[cat_var].attrs['levels'] = ', '.join([f"{k}: {id_levels[k]}" for k in id_levels])
# =============================================================================
#                         print(f"Info: Variable `{cat_var}` is categorized as follow:")
#                         print('\n'.join([f"  . {k}: {id_levels[k]}" for k in id_levels]))
# =============================================================================
                        
                    # Case 'percent' (compute frequency among other levels):
                    elif rasterize_mode[cat_var] == "percent":
                        levels = data_reprj[cat_var].unique()
                        for l in levels:
                            data_reprj_lvl = data_reprj[data_reprj[cat_var] == l]
                            
                            data_3D = []
                            for t in t_coords:
                                data_reprj_temp = data_reprj_lvl[data_reprj_lvl[datetime_col[0]] == t]   
                                
                                rasterized_levels = rasterio.features.rasterize(
                                    [(val['geometry'], 1) for _, val in data_reprj_temp.iterrows()],
                                    out_shape = shape,
                                    transform = rio_kwargs['transform'],
                                    fill = 0, # np.nan
                                    merge_alg = rasterio.enums.MergeAlg.add,
                                    all_touched = False,
                                    # dtype = rasterio.float32,
                                    )
                                
                                data_3D.append(rasterized_levels)
                            
                            ds_reprj[f"{cat_var}_{l}"] = xr.DataArray(np.array(data_3D),
                                                                      coords = coords,
                                                                      dims = dims)
                            
                        # Normalize
                        all_level_sum = ds_reprj[f"{cat_var}_{levels[0]}"]
                        for i in range(1, len(levels)):
                            all_level_sum = all_level_sum + ds_reprj[f"{cat_var}_{levels[i]}"]
                        # all_level_sum = ds_reprj[[f"{cat_var}:{l}" for l in levels]].sum()
                        for l in levels:
                            ds_reprj[f"{cat_var}_{l}"] = ds_reprj[f"{cat_var}_{l}"] / all_level_sum * 100
                    
                ds_reprj = ds_reprj.sortby(datetime_col[0]) # reorder time-axis values

                
            else:
                if len(datetime_col) > 1:
                    print(f"Too many datetime columns: {datetime_col}. No time axis is inferred")
            
                for num_var in (set(numeric_col).union(set(timedelta_col))).intersection(set(var_list)):
                    rasterized_data = rasterio.features.rasterize(
                        [(val['geometry'], val[num_var]) for _, val in data_reprj.iterrows()],
                        out_shape = shape,
                        transform = rio_kwargs['transform'],
                        fill = 0, # np.nan
                        merge_alg = rasterio.enums.MergeAlg.add,
                        all_touched = False,
                        # dtype = rasterio.float64, # rasterio.float32,
                        )
                    
                    # Normalize if mode == 'mean' instead of 'sum'
                    if rasterize_mode[num_var] == "mean":
                        rasterized_weight = rasterio.features.rasterize(
                            [(val['geometry'], 1) for _, val in data_reprj.iterrows()],
                            out_shape = shape,
                            transform = rio_kwargs['transform'],
                            fill = 0, # np.nan
                            merge_alg = rasterio.enums.MergeAlg.add,
                            all_touched = False,
                            # dtype = rasterio.float64, # rasterio.float32,
                            )
                        
                        # Normalize
                        rasterized_data = rasterized_data / rasterized_weight
                        
                        # Replace inf with np.nan
                        np.nan_to_num(rasterized_data, posinf = np.nan)
                    
                    # Fill the dataset
                    ds_reprj[num_var] = xr.DataArray(rasterized_data,
                                                     coords = coords,
                                                     dims = dims)

                # Replace 0 with np.nan
# =============================================================================
#                 ds_reprj = ds_reprj.where(ds_reprj != 0)
# =============================================================================
                    
                # Categorical variables: level by level
                for cat_var in set(categorical_col).intersection(set(var_list)):
                    # Case 'dominant' (more frequent):
                    if rasterize_mode[cat_var] == "dominant":
                        levels = data_reprj[cat_var].unique()
                        # String/categorical data are not handled well by GIS softwares...
                        id_levels = {i:levels[i] for i in range(0, len(levels))}
                        for i in id_levels:
                            data_reprj_lvl = data_reprj[data_reprj[cat_var] == levels[i]] 
                            rasterized_levels = rasterio.features.rasterize(
                                [(val['geometry'], 1) for _, val in data_reprj_lvl.iterrows()],
                                out_shape = shape,
                                transform = rio_kwargs['transform'],
                                fill = 0, # np.nan
                                merge_alg = rasterio.enums.MergeAlg.add,
                                all_touched = False,
                                # dtype = rasterio.float32,
                                )
                            
                            if i == 0: # 1er passage
                                rasterized_data = rasterized_levels.copy().astype(int)
                                rasterized_data[:] = -1
                                rasterized_data[rasterized_levels > 0] = i
                                rasterized_levels_prev = rasterized_levels.copy()
                            else:
                                rasterized_data[rasterized_levels > rasterized_levels_prev] = i
                                rasterized_levels_prev = np.maximum(rasterized_levels,
                                                                    rasterized_levels_prev)
                        
                        ds_reprj[cat_var] = xr.DataArray(rasterized_data,
                                                         coords = coords,
                                                         dims = dims)
                        
                        # Inform
                        nodata_level = {-1: 'nodata'}
                        id_levels = {**nodata_level, **id_levels}
                        ds_reprj[f"{cat_var}_levels"] = ', '.join([f"{k}: {id_levels[k]}" for k in id_levels]) # str(id_levels)
                        ds_reprj[cat_var].attrs['levels'] = ', '.join([f"{k}: {id_levels[k]}" for k in id_levels])
# =============================================================================
#                         print(f"Info: Variable {cat_var} is categorized as follow:")
#                         print('\n'.join([f"  . {k}: {id_levels[k]}" for k in id_levels]))
# =============================================================================
                        
                        
                    # Case 'percent' (compute frequency among other levels):
                    elif rasterize_mode[cat_var] == "percent":
                        levels = data_reprj[cat_var].unique()
                        for l in levels:
                            data_reprj_lvl = data_reprj[data_reprj[cat_var] == l] 
                            rasterized_levels = rasterio.features.rasterize(
                                [(val['geometry'], 1) for _, val in data_reprj_lvl.iterrows()],
                                out_shape = shape,
                                transform = rio_kwargs['transform'],
                                fill = 0, # np.nan
                                merge_alg = rasterio.enums.MergeAlg.add,
                                all_touched = False,
                                # dtype = rasterio.float32,
                                )
                        
                            ds_reprj[f"{cat_var}_{l}"] = xr.DataArray(rasterized_levels,
                                                                      coords = coords,
                                                                      dims = dims)
                        
                        # Normalize
                        all_level_sum = ds_reprj[f"{cat_var}_{levels[0]}"]
                        for i in range(1, len(levels)):
                            all_level_sum = all_level_sum + ds_reprj[f"{cat_var}_{levels[i]}"]
                        # all_level_sum = ds_reprj[[f"{cat_var}:{l}" for l in levels]].sum()
                        for l in levels:
                            ds_reprj[f"{cat_var}_{l}"] = ds_reprj[f"{cat_var}_{l}"] / all_level_sum * 100
                        
            
                
# =============================================================================
#                 # convert levels to values
#                 ds_reprj['levels'] = levels
#                 ds_reprj[cat_var] = ds_reprj['levels'][ds_reprj[cat_var].astype(int)].drop('levels')
# =============================================================================
            
# =============================================================================
#                 # Replace 0 with np.nan
#                 ds_reprj = ds_reprj.where(ds_reprj != 0)
# =============================================================================
            

    elif isinstance(data_ds, pd.DataFrame): # csv
        print("The reprojection or rasterization of CSV data and pandas.DataFrames is not supported yet. These types of data can only be clipped to the specified `bounds` or `mask`. In that last case, only the rectangular extent of the `mask` (box bounds) is considered rather than the precise `mask` shape")

        # ---- Clip csv
        ds_reprj = data_ds[(data_ds[xvar] >= bounds[0]) & (data_ds[xvar] <= bounds[2]) & \
                           (data_ds[yvar] >= bounds[1]) & (data_ds[yvar] <= bounds[3])]
        # reminder: bounds has already been either retrieved from `bounds` argument, 
        # or computed from `mask` argument, and it has already been reprojected if necessary
   
    
    
    else:
        print("Warning: The reprojection of the data type is not supported")
        ds_reprj = data_reprj
    
    # ds_reprj.rio.write_crs(rio_kwargs['dst_crs'], inplace = True)
    if isinstance(ds_reprj, (xr.Dataset, xr.DataArray)):
        ds_reprj = georef(data = ds_reprj, 
                          crs = rio_kwargs['dst_crs'])
            
    # --- Export
    if to_export:
        print('\nExporting...')
        export(ds_reprj, export_filepath)
    
    return ds_reprj  


###############################################################################
#%%% Other aliases (reproject, convert)

reproject = transform
convert = transform

###############################################################################
#%%% Clip (partial alias)
clip = partial(transform, 
               base_template = None,
               x0 = None,
               y0 = None,
               rasterize = False,
               main_var_list = None,
               rasterize_mode = ['sum', 'dominant', 'and'],
               # dst_crs = None,
               )

clip.__name__ = 'clip(data, *, src_crs=None, bounds=None, mask=None, to_file=False, export_extension=None)'
clip.__doc__ = r"""
    Clip space-time data.
    :func:`clip` is a **partial alias** of the :func:`transform() <geobricks.transform>` function.

    Parameters
    ----------
    data : str, pathlib.Path, xarray.Dataset, xarray.DataArray or geopandas.GeoDataFrame
        Data to transform. Supported file formats are *.tif*, *.asc*, *.nc* and vector 
        formats supported by geopandas (*.shp*, *.json*, ...).
    src_crs : int or str or rasterio.crs.CRS, optional, default None
        Coordinate reference system of the source (``data``).    
        When passed as an *integer*, ``src_crs`` refers to the EPSG code. 
        When passed as a *string*, ``src_crs`` can be OGC WKT string or Proj.4 string.
    bounds : iterable or None, optional, default None
        Boundaries of the target domain as a tuple (x_min, y_min, x_max, y_max).
    mask : str, pathlib.Path, shapely.geometry, xarray.DataArray or geopandas.GeoDataFrame, optional, default None
        Filepath of mask used to clip the data. 
    to_file : bool, default True
        If True and if ``data`` is a file, the resulting dataset will be exported to a 
        file with the same name and the suffix '_geop4th'.
    export_extension : str, optional
        Extension to which the data will be converted and exported. Only used
        when the specified ``data`` is a filepath. It ``data`` is a variable
        and not a file, it will not be exported.

    Returns
    -------
    Clipped data : xarray.Dataset or geopandas.GeoDataFrame.
        The type of the resulting variable is accordingly to the type of input data and to
        the conversion operations (such as rasterize):
        
        - all vector data will be output as a geopandas.GeoDataFrame
        - all raster data and netCDF will be output as a xarray.Dataset

    """


###############################################################################
#%%% Rasterize (partial alias)
rasterize = partial(transform, 
                    rasterize = True)

rasterize.__name__ = "rasterize(data, *, src_crs=None, base_template=None, bounds=None, x0=None, y0=None, mask=None, to_file=False, export_extension='.tif'', main_var_list=None, rasterize_mode=['sum', 'dominant', 'and'], **rio_kwargs)"
rasterize.__doc__ = r"""
    Rasterize vector space-time data.
    :func:`rasterize` is a **partial alias** of the :func:`transform() <geobricks.transform>` function.

    Parameters
    ----------
    data : str, pathlib.Path, xarray.Dataset, xarray.DataArray or geopandas.GeoDataFrame
        Data to transform. Supported file formats are *.tif*, *.asc*, *.nc* and vector 
        formats supported by geopandas (*.shp*, *.json*, ...).
    src_crs : int or str or rasterio.crs.CRS, optional, default None
        Coordinate reference system of the source (``data``).    
        When passed as an *integer*, ``src_crs`` refers to the EPSG code. 
        When passed as a *string*, ``src_crs`` can be OGC WKT string or Proj.4 string.
    base_template : str, pathlib.Path, xarray.DataArray or geopandas.GeoDataFrame, optional, default None
        Filepath, used as a template for spatial profile. Supported file formats
        are *.tif*, *.nc* and vector formats supported by geopandas (*.shp*, *.json*, ...).
    bounds : iterable or None, optional, default None
        Boundaries of the target domain as a tuple (x_min, y_min, x_max, y_max).
    x0: number, optional, default None
        Origin of the X-axis, used to align the reprojection grid. 
    y0: number, optional, default None
        Origin of the Y-axis, used to align the reprojection grid. 
    mask : str, pathlib.Path, shapely.geometry, xarray.DataArray or geopandas.GeoDataFrame, optional, default None
        Filepath of mask used to clip the data. 
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_geop4th'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.
    export_extension : str, default '.tif'
        Extension to which the data will be converted and exported. Only used
        when the specified ``data`` is a filepath. It ``data`` is a variable
        and not a file, it will not be exported.
    main_var_list : iterable, default None
        Data variables to rasterize. Only used if ``rasterize`` is ``True``.
        If ``None``, all variables in ``data`` are rasterized.
    rasterize_mode : str or list of str, or dict, default ['sum', 'dominant', 'and']
        Defines the mode to rasterize data:
            
            - for numeric variables: ``'mean'`` or ``'sum'`` (default)
            - for categorical variables: ``'percent'`` or ``'dominant'`` (default)
            
                - ``'dominant'`` rises the most frequent level for each cell
                - ``'percent'`` creates a new variable per level, which stores 
                the percentage (from 0 to 100) of occurence of this level compared
                to all levels, for each cell.
                
            - for boolean variables: ``'or'`` or ``'and'`` (default)
        The modes can be specified for each variable by passing ``rasterize_mode``
        as a dict: ``{'<var1>': 'mean', '<var2>': 'percent', ...}``. This argument
        specification makes it possible to force a numeric variable to be rasterized
        as a categorical variable. Unspecified variables will be rasterized with the default mode.
        
    
    **rio_kwargs : keyword args, optional, defaults are None
        Argument passed to the ``xarray.Dataset.rio.reproject()`` function call.
        
        **Note**: These arguments are prioritary over ``base_template`` attributes.
        
        May contain: 
            
        - ``dst_crs`` : str
        - ``resolution`` : float or tuple
        - ``shape`` : tuple (int, int)
        - ``transform`` : Affine
        - ``nodata`` : float or None
        - ``resampling`` : 
                
           - see ``help(rasterio.enums.Resampling)``
           - most common are: ``5`` (average), ``13`` (sum), ``0`` (nearest), 
             ``9`` (min), ``8`` (max), ``1`` (bilinear), ``2`` (cubic)...
           - the functionality ``'std'`` (standard deviation) is also available
            
        - see ``help(xarray.Dataset.rio.reproject)``

    Returns
    -------
    Transformed data : xarray.Dataset or geopandas.GeoDataFrame.
        The type of the resulting variable is accordingly to the type of input data and to
        the conversion operations (such as rasterize):
        
        - all vector data will be output as a geopandas.GeoDataFrame
        - all raster data and netCDF will be output as a xarray.Dataset

    """


###############################################################################
#%%% Align on the closest value
def nearest(x = None, y = None, x0 = 700012.5, y0 = 6600037.5, res = 75): 
    """
    
    
    Exemple
    -------
    import geoconvert as gc
    gc.nearest(x = 210054)
    gc.nearest(y = 6761020)
    
    Parameters
    ----------
    x : float, optional
        Valeur de la coordonnée x (ou longitude). The default is None.
    y : float, optional
        Valeur de la coordonnée y (ou latitude). The default is None.

    Returns
    -------
    Par défault, cette fonction retourne la plus proche valeur (de x ou de y) 
    alignée sur la grille des cartes topo IGN de la BD ALTI.
    Il est possible de changer les valeurs de x0, y0 et res pour aligner sur
    d'autres grilles.
    """
    
    # ---- Paramètres d'alignement : 
    # ---------------------------
# =============================================================================
#     # Documentation Lambert-93
#     print('\n--- Alignement d'après doc Lambert-93 ---\n')
#     x0 = 700000 # origine X
#     y0 = 6600000 # origine Y
#     res = 75 # résolution
# =============================================================================
    
    # Coordonnées des cartes IGN BD ALTI v2
    if (x0 == 700012.5 or y0 == 6600037.5) and res == 75:
        print('\n--- Alignement sur grille IGN BD ALTI v2 (defaut) ---')   
    
    closest = []

    if x is not None and y is None:
        # print('x le plus proche = ')
        if (x0-x)%res <= res/2:
            closest = x0 - (x0-x)//res*res
        elif (x0-x)%res > res/2:
            closest = x0 - ((x0-x)//res + 1)*res
    
    elif y is not None and x is None:
        # print('y le plus proche = ')
        if (y0-y)%res <= res/2:
            closest = y0 - (y0-y)//res*res
        elif (y0-y)%res > res/2:
            closest = y0 - ((y0-y)//res + 1)*res
    
    else:
        print('Err: only one of x or y parameter should be passed')
        return
        
    return closest


###############################################################################
#%%% Format x_res and y_res
def format_xy_resolution(*, resolution=None, bounds=None, shape=None):
    """
    Format x_res and y_res from a resolution value/tuple/list, or from 
    bounds and shape.

    Parameters
    ----------
    resolution : number | iterable, optional
       xy_res or (x_res, y_res). The default is None.
    bounds : iterable, optional
        (x_min, y_min, x_max, y_max). The default is None.
    shape : iterable, optional
        (height, width). The default is None.

    Returns
    -------
    x_res and y_res

    """
    if (resolution is not None) & ((bounds is not None) | (shape is not None)):
        print("Err: resolution cannot be specified alongside with bounds or shape")
        return
    
    if resolution is not None:
        if isinstance(resolution, (tuple, list)):
            x_res = abs(resolution[0])
            y_res = -abs(resolution[1])
        else:
            x_res = abs(resolution)
            y_res = -abs(resolution)
            
    if ((bounds is not None) & (shape is None)) | ((bounds is None) & (shape is not None)):
        print("Err: both bounds and shape need to be specified")
    
    if (bounds is not None) & (shape is not None):
        (height, width) = shape
        (x_min, y_min, x_max, y_max) = bounds
        x_res = (x_max - x_min) / width
        y_res = -(y_max - y_min) / height
        
    return x_res, y_res


###############################################################################
#%%% Get shape
def get_shape(x_res, y_res, bounds, x0=0, y0=0):
    # bounds should be xmin, ymin, xmax, ymax
    # aligne sur le 0, arrondit, et tutti quanti
    (x_min, y_min, x_max, y_max) = bounds
    
    x_min2 = nearest(x = x_min, res = x_res, x0 = x0)
    if x_min2 > x_min:
        x_min2 = x_min2 - x_res
        
    y_min2 = nearest(y = y_min, res = y_res, y0 = y0)
    if y_min2 > y_min:
        y_min2 = y_min2 - abs(y_res)
        
    x_max2 = nearest(x = x_max, res = x_res, x0 = x0)
    if x_max2 < x_max:
        x_max2 = x_max2 + x_res
        
    y_max2 = nearest(y = y_max, res = y_res, y0 = y0)
    if y_max2 < y_max:
        y_max2 = y_max2 + abs(y_res)
    
    
    width = (x_max2 - x_min2)/x_res
    height = -(y_max2 - y_min2)/y_res
    if (int(width) == width) & (int(height) == height):
        shape = (int(height), int(width))
    else:
        print(f"Warning: shape values are not integers: ({width}, {height})")
        rel_err = (abs((np.rint(width) - width)/np.rint(width)),
                   abs((np.rint(height) - height)/np.rint(height)))
        print(f".                               errors: ({rel_err[0]*100} %, {rel_err[1]*100} %)")
        # Safeguard
        if (rel_err[0] > 1e-8) | (rel_err[1] > 1e-8):
            print("Error")
            shape = None
        else:
            shape = (int(np.rint(height)), int(np.rint(width)))
    
    return shape, x_min2, y_max2

           
#%% COMPRESS & UNCOMPRESS netCDF
###############################################################################
def unzip(data,
          to_file = False):
    """
    Uncompress gzipped netCDF. Only applies to gzip compression (non-lossy compression).
    Even if gzip compression is not destructive, in some GIS softwares 
    uncompressed netCDF are quicker to manipulate than gzipped netCDF.

    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray)
        Dataset (netCDF or xarray variable) that will be unzipped.
        
        Note that ``data`` will be loaded into a xarray.Dataset or xarray.DataArray.
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_unzip'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.

    Returns
    -------
    data_ds : xarray.Dataset
        Standard *GEOP4TH* variable (xarray.Dataset) with gzip compression removed.
    
    If ``to_file`` argument is used, the resulting dataset can also be exported to a file. 
    """
    # Load
    data_ds = load_any(data, decode_times = True, decode_coords = 'all')
    if not isinstance(data_ds, (xr.Dataset, xr.DataArray)):
        print("Error: the `unzip` function is only intended for netCDF datasets")
        return
    
    # Get main variable
    var_list = main_vars(data_ds)
    
    for var in var_list:
        # Deactivate zlib
        data_ds[var].encoding['zlib'] = False
    
    # Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            export_filepath = os.path.splitext(data)[0] + "_unzip" + os.path.splitext(data)[-1]
            export(data_ds, export_filepath)
        else:
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        export(data_ds, to_file)
    
    # Return
    return data_ds
    

###############################################################################
def gzip(data, 
         complevel = 3, 
         shuffle = False,
         to_file = False):
    r"""
    Apply a non-lossy compression (gzip) to a netCDF dataset.
    
    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray)
        Dataset (netCDF or xarray variable) that will be gzipped (non-lossy).
        
        Note that ``data`` will be loaded into a xarray.Dataset or xarray.DataArray.
    complevel : {1, 2, 3, 4, 5, 6, 7, 8, 9}, default 3
        Compression level, (1 being fastest, but lowest compression ratio, 
        9 being slowest but best compression ratio).
    shuffle : bool, default False
        HD5 shuffle filter, which de-interlaces a block of data before zgip 
        compression by reordering the bytes
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_gzip'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.

    Returns
    -------
    data_ds : xarray.Dataset
        Standard *GEOP4TH* variable (xarray.Dataset) with gzip compression added.
    
    If ``to_file`` argument is used, the resulting dataset can also be exported to a file. 
    
    Examples
    --------
    geo.gzip(myDataset, complevel = 4, shuffle = True)
    geo.gzip(r"D:\folder\data1.nc", complevel = 5)
    """
    # Load
    data_ds = load_any(data, decode_times = True, decode_coords = 'all')
    if not isinstance(data_ds, (xr.Dataset, xr.DataArray)):
        print("Error: the `gzip` function is only intended for netCDF datasets")
        return
    
    # Get main variable
    var_list = main_vars(data_ds)
    
    for var in var_list:
        # Activate zlib
        data_ds[var].encoding['zlib'] = True
        data_ds[var].encoding['complevel'] = complevel
        data_ds[var].encoding['shuffle'] = shuffle
        data_ds[var].encoding['contiguous'] = False
    
    # Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            export_filepath = os.path.splitext(data)[0] + "_gzip" + os.path.splitext(data)[-1]
            export(data_ds, export_filepath)
        else:
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        export(data_ds, to_file)
    
    # Return
    return data_ds
    
    
###############################################################################
def pack(data, 
         nbits = 16,
         to_file = False):
    """
    Applies a lossy compression to a netCDF dataset, by packing the values to
    a data type with smaller number of bits. Under the hood, this function
    automatically defines the corresponding ``add_offset`` and ``scale_factor``.

    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (xarray.Dataset, xarray.DataArray)
        Dataset (netCDF or xarray variable) that will be gzipped (non-lossy).
        
        Note that ``data`` will be loaded into a xarray.Dataset or xarray.DataArray.
    nbits : {8, 16}, default 16
        Number of bits for the data type of the output values.
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_pack'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.

    Returns
    -------
    data_ds : xarray.Dataset
        Standard *GEOP4TH* variable (xarray.Dataset) with lossy compression.
    
    If ``to_file`` argument is used, the resulting dataset can also be exported to a file. 

    """
    if (nbits != 16) & (nbits != 8):
        print("Err: nbits should be 8 or 16")
        return

    # Load
    data_ds = load_any(data, decode_times = True, decode_coords = 'all')
    if not isinstance(data_ds, (xr.Dataset, xr.DataArray)):
        print("Error: the `pack` function is only intended for netCDF datasets")
        return
    
    # Get main variable
    var_list = main_vars(data_ds)

    for var in var_list:
        # Compress
        bound_min = data_ds[var].min().item()
        bound_max = data_ds[var].max().item()
        # Add an increased max bound, that will be used for _FillValue
        bound_max = bound_max + (bound_max - bound_min + 1)/(2**nbits)
        scale_factor, add_offset = compute_scale_and_offset(
            bound_min, bound_max, nbits)
        data_ds[var].encoding['scale_factor'] = scale_factor
    
        data_ds[var].encoding['dtype'] = f'uint{nbits}'
        data_ds[var].encoding['_FillValue'] = (2**nbits)-1
        data_ds[var].encoding['add_offset'] = add_offset
        print("   Compression (lossy)")
        # Prevent _FillValue issues
        if ('missing_value' in data_ds[var].encoding) & ('_FillValue' in data_ds[var].encoding):
            data_ds[var].encoding.pop('missing_value')
    
    # Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            export_filepath = os.path.splitext(data)[0] + "_pack" + os.path.splitext(data)[-1]
            export(data_ds, export_filepath)
        else:
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        export(data_ds, to_file)
    
    # Return
    return data_ds



#%%% Packing netcdf (previously packnetcdf.py)
"""
Created on Wed Aug 24 16:48:29 2022

@author: script based on James Hiebert's work (2015):
    http://james.hiebert.name/blog/work/2015/04/18/NetCDF-Scale-Factors.html

RAPPEL des dtypes :
    uint8 (unsigned int.)       0 to 255
    uint16 (unsigned int.)      0 to 65535
    uint32 (unsigned int.)      0 to 4294967295
    uint64 (unsigned int.)      0 to 18446744073709551615
    
    int8    (Bytes)             -128 to 127
    int16   (short integer)     -32768 to 32767
    int32   (integer)           -2147483648 to 2147483647
    int64   (integer)           -9223372036854775808 to 9223372036854775807 
    
    float16 (half precision float)      10 bits mantissa, 5 bits exponent (~ 4 cs ?)
    float32 (single precision float)    23 bits mantissa, 8 bits exponent (~ 8 cs ?)
    float64 (double precision float)    52 bits mantissa, 11 bits exponent (~ 16 cs ?)
"""

###############################################################################
def compute_scale_and_offset(min, max, n):
    """
    Computes scale and offset necessary to pack a float32 (or float64?) set 
    of values into a int16 or int8 set of values.
    
    Parameters
    ----------
    min : float
        Minimum value from the data
    max : float
        Maximum value from the data
    n : int
        Number of bits into which you wish to pack (8 or 16)

    Returns
    -------
    scale_factor : float
        Parameter for netCDF's encoding
    add_offset : float
        Parameter for netCDF's encoding
    """
    
    # stretch/compress data to the available packed range    
    add_offset = min
    scale_factor = (max - min) / ((2 ** n) - 1)
    
    return (scale_factor, add_offset)


###############################################################################
def pack_value(unpacked_value, scale_factor, add_offset):
    """
    Compute the packed value from the original value, a scale factor and an 
    offset.

    Parameters
    ----------
    unpacked_value : numeric
        Original value.
    scale_factor : numeric
        Scale factor, multiplied to the original value.
    add_offset : numeric
        Offset added to the original value.

    Returns
    -------
    numeric
        Packed value.

    """
    
    # print(f'math.floor: {math.floor((unpacked_value - add_offset) / scale_factor)}')
    return int((unpacked_value - add_offset) / scale_factor)


###############################################################################
def unpack_value(packed_value, scale_factor, add_offset):
    """
    Retrieve the original value from a packed value, a scale factor and an
    offset.

    Parameters
    ----------
    packed_value : numeric
        Value to unpack.
    scale_factor : numeric
        Scale factor that was multiplied to the original value to retrieve.
    add_offset : numeric
        Offset that was added to the original value to retrieve.

    Returns
    -------
    numeric
        Original unpacked value.

    """
    return packed_value * scale_factor + add_offset        
   

#%% OPERATIONS ON UNITS
###############################################################################
def hourly_to_daily(data, 
                    *, mode = 'sum',
                    to_file = False):
    """
    Converts a hourly dataset to daily values. Implemented only for netCDF so far.

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    mode : {'mean', 'max', 'min', 'sum'}, default 'sum'
        DESCRIPTION.
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_daily'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.

    Returns
    -------
    datarsmpl : TYPE
        DESCRIPTION.
    
    If ``to_file`` argument is used, the resulting dataset can also be exported to a file. 

    """
   
    # ---- Process data
    #% Load data:
    data_ds = load_any(data, decode_coords = 'all', decode_times = True)
    
    var_list = main_vars(data_ds)
        
    mode_dict = {}
    if isinstance(mode, str):
        for var in var_list:
            mode_dict[var] = mode
            
    elif isinstance(mode, dict):
        mode_dict = mode
        if len(var_list) > len(mode_dict):
            diff = set(var_list).difference(mode_dict)
            print(f"   _ Warning: {len(diff)} variables were not specified in 'mode': {', '.join(diff)}. They will be assigned the mode 'sum'.")
            for d in diff:
                mode_dict[d] = 'sum'
    
    time_coord = main_time_dims(data_ds)
    
    datarsmpl = xr.Dataset()
    
    #% Resample:
    print("   _ Resampling time...")
    for var in var_list:
        if mode_dict[var] == 'mean':
            datarsmpl[var] = data_ds[var].resample({time_coord: '1D'}).mean(dim = time_coord,
                                                                            keep_attrs = True)
        elif mode_dict[var] == 'max':
            datarsmpl[var] = data_ds[var].resample({time_coord: '1D'}).max(dim = time_coord,
                                                                           keep_attrs = True)
        elif mode_dict[var] == 'min':
            datarsmpl[var] = data_ds[var].resample({time_coord: '1D'}).min(dim = time_coord,
                                                                           keep_attrs = True)
        elif mode_dict[var] == 'sum':
            datarsmpl[var] = data_ds[var].resample({time_coord: '1D'}).sum(dim = time_coord,
                                                                           skipna = False,
                                                                           keep_attrs = True)
        
        # ---- Preparing export   
        # Transfer encodings   
        datarsmpl[var].encoding = data_ds[var].encoding
            
        # Case of packing
        if ('scale_factor' in datarsmpl[var].encoding) | ('add_offset' in datarsmpl[var].encoding):
            # Packing (lossy compression) induces a loss of precision of 
            # apprx. 1/1000 of unit, for a quantity with an interval of 150 
            # units. The packing is initially used in some original ERA5-Land data.
            if mode == 'sum':
                print("   Correcting packing encodings...")
                datarsmpl[var].encoding['scale_factor'] = datarsmpl[var].encoding['scale_factor']*24
                datarsmpl[var].encoding['add_offset'] = datarsmpl[var].encoding['add_offset']*24

    # Transfert coord encoding
    for c in list(datarsmpl.coords):
        datarsmpl[c].encoding = data_ds[c].encoding
        datarsmpl[c].attrs = data_ds[c].attrs
    datarsmpl[time_coord].encoding['units'] = datarsmpl[time_coord].encoding['units'].replace('hours', 'days')
    
    # ---- Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            export_filepath = os.path.splitext(data)[0] + "_daily" + os.path.splitext(data)[-1]
            export(datarsmpl, export_filepath)
        else:
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        export(datarsmpl, to_file)
    
    return datarsmpl


###############################################################################
def to_instant(data, 
               derivative = False,
               to_file = False):
    """
    

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    derivative : TYPE, optional
        DESCRIPTION. The default is False.
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_instant'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.

    Returns
    -------
    inst_ds : TYPE
        DESCRIPTION.
        
    If ``to_file`` argument is used, the resulting dataset can also be exported to a file. 

    """
    
    data_ds = load_any(data, decode_coords = 'all', decode_times = True)
    time_coord = main_time_dims(data_ds)
    if isinstance(time_coord, list):
        time_coord = time_coord[0]
    
    if derivative:
        inst_ds = data_ds.diff(dim = time_coord)/data_ds[time_coord].diff(dim = time_coord)
    else:
        inst_ds = data_ds.diff(dim = time_coord)
    
    # Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            export_filepath = os.path.splitext(data)[0] + "_instant" + os.path.splitext(data)[-1]
            export(inst_ds, export_filepath)
        else:
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        export(inst_ds, to_file)
    
    return inst_ds
    

###############################################################################
def convert_unit(data, 
                 operation, 
                 *, var = None,
                 to_file = False):
    """
    

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    operation : TYPE
        DESCRIPTION.
    * : TYPE
        DESCRIPTION.
    var : TYPE, optional
        DESCRIPTION. The default is None.
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to a file with the same pathname and the 
        suffix '_units'. If ``to_file`` is a path, the resulting dataset 
        will be exported to this specified filepath.

    Returns
    -------
    data_ds : TYPE
        DESCRIPTION.
        
    If ``to_file`` argument is used, the resulting dataset can also be exported to a file. 

    """
    
    metric_prefixes = ['p', None, None, 'n', None, None, 'µ', None, None, 
                       'm', 'c', 'd', '', 'da', 'h', 'k', None, None, 'M', 
                       None, None, 'G']
    
    # ---- Load data and operands
    data_ds = load_any(data)
    
    if not isinstance(operation, str):
        print("Err: 'operation' should be a str.")
        return
    else:
        operation = operation.replace(' ', '').replace('x', '*').replace('×', '*').replace('÷', '/')
        operand = operation[0]
        factor = float(operation[1:])
    
    
    if isinstance(data_ds, (pd.DataFrame, gpd.GeoDataFrame)):
        if var is None:
            mvar = main_vars(data_ds)
        else:
            mvar = var
        
        # ---- Operation        
        if operand == '*':
            data_ds[mvar] = data_ds[mvar] * factor
        elif operand == '/':
            data_ds[mvar] = data_ds[mvar] / factor
        elif operand == '+':
            data_ds[mvar] = data_ds[mvar] + factor
        elif operand == '-':
            data_ds[mvar] = data_ds[mvar] - factor
        
        return data_ds  
        
    
    elif isinstance(data_ds, xr.Dataset):
        mvar = main_vars(data_ds)
        if len(mvar) == 1:
            data_da = data_ds[mvar[0]]
        else: # mvar is a list
            if var is not None:
                data_da = data_ds[var]
            else:
                print("Err: convert_unit can only be used on xarray.DataArrays or xarray.Datasets with one variable. Consider passing the argument 'var'.")
                return
    elif isinstance(data_ds, xr.DataArray):
        data_da = data_ds
  
    # ---- Preparing export
    attrs = data_da.attrs
    encod = data_da.encoding
    
    # ---- Operation        
    # exec(f"data_da = data_da {operation}") # vulnerability issues
    if operand == '*':
        data_da = data_da * factor
    elif operand == '/':
        data_da = data_da / factor
    elif operand == '+':
        data_da = data_da + factor
    elif operand == '-':
        data_da = data_da - factor
    
    # ---- Transfert metadata
    data_da.encoding = encod
    data_da.attrs = attrs # normally unnecessary
    for unit_id in ['unit', 'units']:
        if unit_id in data_da.attrs:
            if operand in ['*', '/']:                
                significand, exponent = f"{factor:e}".split('e')
                significand = float(significand)
                exponent = int(exponent)
                # if factor_generic%10 == 0:
                if significand == 1:
                    current_prefix = data_da.attrs[unit_id][0]
                    current_idx = metric_prefixes.index(current_prefix)
                    # new_idx = current_idx + int(np.log10(factor_generic))
                    if operand == "*":
                        new_idx = current_idx - exponent
                        new_unit = data_da.attrs[unit_id] + f" {operand}{significand}e{exponent}" # By default
                    elif operand == "/":
                        new_idx = current_idx + exponent
                        new_unit = data_da.attrs[unit_id] + f" *{significand}e{-exponent}" # By default
                        
                    if (new_idx >= 0) & (new_idx <= len(metric_prefixes)):
                        if metric_prefixes[new_idx] is not None:
                            new_unit = metric_prefixes[new_idx] + data_da.attrs[unit_id][1:]
                    
                    data_da.attrs[unit_id] = new_unit
                
                else:
                    new_unit = data_da.attrs[unit_id] + f" {operand}{significand}e{exponent}" # By default
                    data_da.attrs[unit_id] = new_unit
                

    # Case of packing
    if ('scale_factor' in data_da.encoding) | ('add_offset' in data_da.encoding):
        # Packing (lossy compression) induces a loss of precision of 
        # apprx. 1/1000 of unit, for a quantity with an interval of 150 
        # units. The packing is initially used in some original ERA5-Land data.
        if operand == '+':
            data_da.encoding['add_offset'] = data_da.encoding['add_offset'] + factor
        elif operand == '-':
            data_da.encoding['add_offset'] = data_da.encoding['add_offset'] - factor
        elif operand == '*':
            data_da.encoding['add_offset'] = data_da.encoding['add_offset'] * factor
            data_da.encoding['scale_factor'] = data_da.encoding['scale_factor'] * factor
        elif operand == '/':
            data_da.encoding['add_offset'] = data_da.encoding['add_offset'] / factor
            data_da.encoding['scale_factor'] = data_da.encoding['scale_factor'] / factor
    
    if isinstance(data_ds, xr.Dataset):
        if len(mvar) == 1:
            data_ds[mvar[0]] = data_da
        else: # mvar is a list
            if var is not None:
                data_ds[var] = data_da
            else:
                print("Err: convert_unit can only be used on xarray.DataArrays or xarray.Datasets with one variable. Consider passing the argument 'var'.")
                return
    elif isinstance(data_ds, xr.DataArray):
        data_ds = data_da
    
    # Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            export_filepath = os.path.splitext(data)[0] + "_units" + os.path.splitext(data)[-1]
            export(data_ds, export_filepath)
        else:
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        export(data_ds, to_file)
    
    return data_ds    



###############################################################################
#%%% * hourly_to_daily (OLD)
def hourly_to_daily_old(*, data, mode = 'mean', **kwargs):
    # Cette version précédente (mise à jour) gère des dossiers
    
    """
    Example
    -------
    import geoconvert as gc
    # full example:
    gc.hourly_to_daily(input_file = r"D:/2011-2021_hourly Temperature.nc",
                       mode = 'max',
                       output_path = r"D:/2011-2021_daily Temperature Max.nc",
                       fields = ['t2m', 'tp'])
    
    # input_file can also be a folder:
    gc.hourly_to_daily(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\test", 
                       mode = 'mean')
    
    Parameters
    ----------
    input_file : str, or list of str
        Can be a path to a file (or a list of paths), or a path to a folder, 
        in which cas all the files in this folder will be processed.
    mode : str, or list of str, optional
        = 'mean' (default) | 'max' | 'min' | 'sum'
    **kwargs 
    --------
    fields : str or list of str, optional
        e.g: ['t2m', 'tp', 'u10', 'v10', ...]
        (if not specified, all fields are considered)
    output_path : str, optional
        e.g: [r"D:/2011-2021_daily Temperature Max.nc"]
        (if not specified, output_name is made up according to arguments)
        
    Returns
    -------
    None. Processed files are created in the output destination folder.

    """

    # ---- Get input file path(s)
    data_folder, filelist = get_filelist(data, extension = '.nc')
        
    #% Safeguard for output_names:
    if len(filelist) > 1 and 'output_path' in kwargs:
        print('Warning: Due to multiple output, names of the output files are imposed.') 
    
    
    # ---- Format modes
    if isinstance(mode, str): mode = [mode]
    else: mode = list(mode)
    
    if len(mode) != len(filelist):
        if (len(mode) == 1) & (len(filelist)>1):
            mode = mode*len(filelist)
        else:
            print("Error: lengths of input file and mode lists do not match")
            return
            
        
    # ---- Process data
    for i, f in enumerate(filelist):  
        print(f"\n\nProcessing file {i+1}/{len(filelist)}: {f}...")
        print("-------------------")
        #% Load data:
        data_ds = load_any(os.path.join(data_folder, f), 
                           decode_coords = 'all', decode_times = True)

        #% Get fields:
        if 'fields' in kwargs:
            fields = kwargs['fields']
            if isinstance(fields, str): fields = [fields]
            else: fields = list(fields) # in case fields are string or tuple
        else:
            fields = list(data_ds.data_vars) # if not input_arg, fields = all
        
        #% Extract subset according to fields
        fields_intersect = list(set(fields) & set(data_ds.data_vars))
        data_subset = data_ds[fields_intersect]
        print("   _ Extracted fields are {}".format(fields_intersect))
        if fields_intersect != fields:
            print('Warning: ' + ', '.join(set(fields) ^ set(fields_intersect)) 
                  + ' absent from ' + data)
        
        #% Resample:
        print("   _ Resampling time...")
        if mode[i] == 'mean':
            datarsmpl = data_subset.resample(time = '1D').mean(dim = 'time',
                                                                keep_attrs = True)
        elif mode[i] == 'max':
            datarsmpl = data_subset.resample(time = '1D').max(dim = 'time',
                                                               keep_attrs = True)
        elif mode[i] == 'min':
            datarsmpl = data_subset.resample(time = '1D').min(dim = 'time',
                                                               keep_attrs = True)
        elif mode[i] == 'sum':
            datarsmpl = data_subset.resample(time = '1D').sum(dim = 'time',
                                                               skipna = False,
                                                               keep_attrs = True)
        
        #% Build output name(s):
        if len(filelist) > 1 or not 'output_path' in kwargs:         
            basename = os.path.splitext(f)[0]
            output_name = os.path.join(
                data_folder, 'daily',
                basename + ' daily_' + mode[i] + '.nc')
            ## Regex solution, instead of splitext:
            # _motif = re.compile('.+[^\w]')
            # _basename = _motif.search(data).group()[0:-1]
            
            if not os.path.isdir(os.path.join(data_folder, 'daily')):
                os.mkdir(os.path.join(data_folder, 'daily'))
            
        else:
            output_name = kwargs['output_path']
        
        
        # ---- Preparing export   
        # Transfer encodings
        for c in list(datarsmpl.coords):
            datarsmpl[c].encoding = data_ds[c].encoding
        
        for f in fields_intersect:
            datarsmpl[f].encoding = data_ds[f].encoding
            
            # Case of packing
            if ('scale_factor' in datarsmpl[f].encoding) | ('add_offset' in datarsmpl[f].encoding):
                # Packing (lossy compression) induces a loss of precision of 
                # apprx. 1/1000 of unit, for a quantity with an interval of 150 
                # units. The packing is initially used in some original ERA5-Land data.
                if mode[i] == 'sum':
                    print("   Correcting packing encodings...")
                    datarsmpl[f].encoding['scale_factor'] = datarsmpl[f].encoding['scale_factor']*24
                    datarsmpl[f].encoding['add_offset'] = datarsmpl[f].encoding['add_offset']*24
            
        #% Export
        export(datarsmpl, output_name)


def dummy_input(base, value):
    """
    Creates a dummy space-time map with the same properties as the base, but with
    a dummy value.

    Parameters
    ----------
    base : TYPE
        DESCRIPTION.
    value : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    data_ds = load_any(base)
    var_list = main_vars(data_ds)
    
    for var in var_list:
        data_ds[var] = data_ds[var]*0 + value
        
    return data_ds


#%% EXTRACTIONS
###############################################################################
def timeseries(data, 
               *, coords = 'all', 
               coords_crs = None, 
               data_crs = None, 
               mode = 'mean', 
               start_date = None,
               end_date = None,
               var_list = None, 
               cumul = False):
    """
    This function extracts the temporal data in one location given by 
    coordinate.

    Parameters
    ----------
    data : path (str, pathlib.Path) or variable (xarray.Dataset or xarray.DataArray)
        timeseries is only intended to handle raster data (ASCII and GeoTIFF) and netCDF.
        ``data`` will be loaded as a xarray.Dataset.
    coords : 'all', str or path, geopandas.GeoDataFrame, shapely.geometry or tuple of (float, float), default 'all'
        The keyword, coordinates or mask that will be used to extract the timeseries.
        If 'all', all the pixels in data are considered. Mask can be raster
        or vector data. If a tuple of coordinates is passed, coordinates should
        be ordered as (x, y) or (lon, lat).
    coords_crs : any CRS accepted by ``pyproj.CRS.from_user_input``, optional
        CRS of ``coords``, in case it is not already embedded in it.
        
        Accepted CRS can be for example:
            
        - EPSG integer codes (such as 4326)
        - authority strings (such as “epsg:4326”)
        - CRS WKT strings
        - pyproj.CRS
        - ...
        
    data_crs : any CRS accepted by ``pyproj.CRS.from_user_input``, optional
        CRS of ``data``, in case it is not already embedded in it.
        
        Accepted CRS can be for example:
            
        - EPSG integer codes (such as 4326)
        - authority strings (such as “epsg:4326”)
        - CRS WKT strings
        - pyproj.CRS
        - ...
        
    mode : {'mean', 'sum', 'max', 'min'}, default 'mean'
        How selected data will be aggregated.
    start_date : str or datetime, optional
        Start of the selected time period to extract.
    end_date : str or datetime, optional
        End of the selected time period to extract.
    var_list : (list of) str, optional
        Fields (variables) to extract.
    cumul : bool, default False
        If True, values will be retrieved as cumulated sums.

    Returns
    -------
    pandas.DataFrame
        Frame containing the timeseries.

    """
    
    # ---- Load
    # Handle data
    data_ds = load_any(data, decode_times = True, decode_coords = 'all')
    if not isinstance(data_ds, (xr.Dataset, xr.DataArray, gpd.GeoDataFrame)):
        # raise Exception('timeseries function is intended to handle geospatial raster or netCDF data')
        print('Error: timeseries function is intended to handle geospatial vector, raster or netCDF data')
        return
    
    #% Get and process other arguments   
    if var_list is None:
        var_list = main_vars(data_ds)
    elif isinstance(var_list, str):
        var_list = [var_list]
    else:
        var_list = list(var_list)
# =============================================================================
#         fields = list(data_ds.data_vars) # if not input_arg, fields = all
# =============================================================================
    print('Variables = {}'.format(str(var_list)))    

    if data_crs is not None:
        data_ds = georef(data_ds, crs = data_crs, var_list = var_list)
    else:
        data_ds = georef(data_ds, var_list = var_list)
        
    time_dim = main_time_dims(data_ds)[0]  
    space_dims = main_space_dims(data_ds)
    
    if isinstance(data_ds, gpd.GeoDataFrame):
        data_ds = data_ds.set_index(time_dim)
    
    # Handle coords
    if isinstance(coords, list): coords = tuple(coords) # in case coords are a list instead of a tuple
    
    if isinstance(coords, (str, Path)):
        if coords != 'all':
            coords = load_any(coords)
    
    if isinstance(coords, gpd.GeoDataFrame):
        if coords_crs is not None:
            coords = georef(coords, crs = coords_crs)
        else:
            coords = georef(coords)

    if start_date is not None:
        start_date = pd.to_datetime(start_date)
        # safeguard
        if not isinstance(start_date, (datetime.datetime, pd.Timestamp)):
            print("Error: `start_date` is not recognized as a valid date")
            return
    else:
        if isinstance(data_ds, xr.Dataset):
            start_date = data_ds[time_dim][0].values
        elif isinstance(data_ds, gpd.GeoDataFrame):
            start_date = data_ds.index[0]
    
    if end_date is not None:
        end_date = pd.to_datetime(end_date)
        # safeguard
        if not isinstance(end_date, (datetime.datetime, pd.Timestamp)):
            print("Error: `end_date` is not recognized as a valid date")
            return
    else:
        if isinstance(data_ds, xr.Dataset):
            end_date = data_ds[time_dim][-1].values
        elif isinstance(data_ds, gpd.GeoDataFrame):
            end_date = data_ds.index[-1]
        
        
# =============================================================================
#     #% Convert temperature:
#     for _field in fields:
#         if 'units' in data_ds[_field].attrs:
#             if data_ds[_field].units == 'K':
#                 data_ds[_field] = data_ds[_field]-273.15
#                 # _datasubset[_field].units = '°C'
# =============================================================================

    # ---- Extraction
    if isinstance(coords, str):
        if coords == 'all':
            print("All cells are considered")
            sel_ds = data_ds.copy()
    
    # Reprojections when needed
    elif isinstance(coords, gpd.GeoDataFrame):
        nrows = coords.shape[0]
        if nrows > 1:
            if isinstance(coords.geometry[0], Point):
                # Safeguard for Frames containing more than one Point:
                print("Error: `coords` contains several Points, instead of a single one")
                return
            elif isinstance(coords.geometry[0], Polygon, MultiPolygon):
                print("Warning: `coords` contains several Polygons. The union of all will be considered")
                # Note that there is no need for safeguard here, as masking with reproject() will handle several Polygons
            
        # Handling CRS:
        ## . Set a CRS to `coords` if needed
        if coords.crs is None:
            if coords_crs is None:
                print("Warning: No CRS is associated with `coords`. It is assumed that coords crs is the same as `data`'s. Note that CRS can be passed with `coords_crs` arguments")
                coords.set_crs(epsg = data_ds.rio.crs, inplace = True, allow_override = True)
            else:
                coords.set_crs(epsg = coords_crs, inplace = True, allow_override = True)
        ## . Reproject (even when not necessary)
        if isinstance(data_ds, xr.Dataset):
            dst_crs = data_ds.rio.crs
        elif isinstance(data_ds, gpd.GeoDataFrame):
            dst_crs = data_ds.crs
        coords = reproject(coords, dst_crs = dst_crs) # more GEOP4TH-style
        # coords.to_crs(epsg = data_ds.rio.crs, inplace = True) # faster
        
        # Case of Point: convert into a tuple
        if isinstance(coords.geometry[0], Point):
            coords = tuple(coords.geometry[0].x, coords.geometry[0].y)
    
    elif isinstance(coords, (tuple, Point, Polygon, MultiPolygon)):
        if coords_crs is None:
            # if data_ds.rio.crs.is_valid: # deprecated in rasterio 2.0.0
            if data_ds.rio.crs.is_epsg_code:   
                print("Warning: No `coords_crs` has been specified. It is assumed that coords crs is the same as `data`'s")
                coords_crs = data_ds.rio.crs
            else:
                print("Warning: No valid CRS is defined for `data` nor `coords`. Note that CRS can be passed with `data_crs` and `coords_crs` arguments")
                
        else:
            if isinstance(coords, tuple):
                coords = Point(coords)
                
            # Newest method (convert to Frame)
            coords = gpd.GeoDataFrame([0], geometry = [coords], crs = coords_crs)
            coords = reproject(coords, dst_crs = data_ds.rio.crs)
            coords = coords.geometry[0]
            
            # Previous conversion method (rasterio.warp.transform)
# =============================================================================
#             coords = rasterio.warp.transform(rasterio.crs.CRS.from_epsg(coords_crs), 
#                                                   rasterio.crs.CRS.from_epsg(data_crs), 
#                                                   [coords[0]], [coords[1]])
#             coords = (coords[0][0], coords[1][0])
#             # (to convert a tuple of arrays into a tuple of float)
# =============================================================================
            
        # Case of Point: convert (back) into a tuple
        if isinstance(coords, Point):
            coords = (coords.x, coords.y)
            
        
    # Extract      
    if isinstance(coords, (Polygon, MultiPolygon, gpd.GeoDataFrame, xr.Dataset)):
        sel_ds = reproject(data_ds, mask = coords)
    
    elif isinstance(coords, tuple): # Note that Points have been converted into tuples beforehand
        if len(set(space_dims).intersection({'lat', 'lon', 'latitude', 'longitude'})) > 0:
            print("Caution: When using a tuple as `coords` with a geographic coordinate system, the order should be (longitude, latitude)")
        
        if isinstance(data_ds, xr.Dataset):
            sel_ds = data_ds.sel({space_dims[0]: [coords[0]], 
                                 space_dims[1]: [coords[1]]},
                                 method = 'nearest')
        elif isinstance(data_ds, gpd.GeoDataFrame):
            print("Error: Not implemented yet!")
            

    # ---- Post-processing operations
    if isinstance(data_ds, xr.Dataset):
        # Select specified fields
        sel_ds = sel_ds[var_list]
        
        # Aggregation
        if mode == 'mean':
            # results = data_ds.mean(dim = list(data_ds.dims)[-2:], 
            #                         skipna = True, keep_attrs = True)
            results = sel_ds.mean(dim = space_dims, 
                                  skipna = True, keep_attrs = True)
        elif mode == 'sum':
            results = sel_ds.sum(dim = space_dims, 
                                 skipna = True, keep_attrs = True)
        elif mode == 'max':
            results = sel_ds.max(dim = space_dims, 
                                 skipna = True, keep_attrs = True)
        elif mode == 'min':
            results = sel_ds.min(dim = space_dims, 
                                 skipna = True, keep_attrs = True)
        
        # Time period selection
        results = results.sel({time_dim: slice(start_date, end_date)})
        
        # Cumulative sum option
        if cumul:
            print('\ncumul == True')
            timespan = results['time'
                ].diff(
                    dim = 'time', label = 'lower')/np.timedelta64(1, 'D')
            
            _var = main_vars(results)
            results[_var][dict(time = slice(0, timespan.size))
                           ] = (results[_var][dict(time = slice(0, timespan.size))
                                               ] * timespan.values).cumsum(axis = 0)
    
            # Last value:
            results[_var][-1] = np.nan
    
    elif isinstance(data_ds, gpd.GeoDataFrame):
        # Select specified fields
        sel_ds = sel_ds[var_list]
        
        # Aggregation
        if mode == 'mean':
            # results = data_ds.mean(dim = list(data_ds.dims)[-2:], 
            #                         skipna = True, keep_attrs = True)
            results = sel_ds.groupby(by = time_dim).mean()
        elif mode == 'sum':
            results = sel_ds.groupby(by = time_dim).sum()
        elif mode == 'max':
            results = sel_ds.groupby(by = time_dim).max()
        elif mode == 'min':
            results = sel_ds.groupby(by = time_dim).min()
        
        # Time period selection
        results = results.loc[slice(start_date, end_date)]
        
        # Cumulative sum option
        if cumul:
            print('\ncumul == True')
            if isinstance(results, xr.Dataset):
                timespan = results[time_dim
                    ].diff(
                        dim = time_dim, label = 'lower')/np.timedelta64(1, 'D')
            
                results.loc[slice(0, timespan.size)
                               ] = (results.loc[slice(0, timespan.size)
                                                   ] * timespan.values).cumsum(axis = 0)
        
                # Last value:
                results.iloc[-1] = np.nan
            
            elif isinstance(results, pd.DataFrame):
                timespan = results.index.diff()/np.timedelta64(1, 'D')
                                        
                results = results.mul(timespan, axis = 'index')
                                                           
                # Last value:
                results.iloc[-1] = np.nan
                
    
    # Memory cleaning
    del data_ds 
    del sel_ds
    gc.collect()
    
    # ---- Export          
# =============================================================================
#     # Drop spatial_ref
#     if 'spatial_ref' in results.coords or 'spatial_ref' in results.data_vars:
#         results = results.drop('spatial_ref')
# =============================================================================
    # Drop non-data_vars fields
    if isinstance(results, xr.Dataset):
        to_discard = list(set(list(results.data_vars)).union(set(list(results.coords))) - set(var_list) - set([time_dim]))
        results = results.drop(to_discard)
        # Convert to pandas.DataFrame
        results = results.to_dataframe()
    elif isinstance(results, pd.DataFrame):
        to_discard = list(set(results.columns) - set(var_list) - set(time_dim))
        results = results.drop(columns = to_discard)

    return results


###############################################################################
#%%% * xr.DataSet to DataFrame
def xr_to_pd(xr_data):
    """
    Format xr objects (such as those from gc.time_series) into pandas.DataFrames
    formatted as in gc.tss_to_dataframe.

    Parameters
    ----------
    xr_data : xarray.DataSet or xarray.DataArary
        Initial data to convert into pandas.DataFrame
        NB: xr_data needs to have only one dimension.

    Returns
    -------
    Pandas.DataFrame

    """
    print("\n_Infos...")
    
    if type(xr_data) == xr.core.dataset.Dataset:
        var_list = main_vars(xr_data)
        print(f"    Data is a xr.Dataset, with {', '.join(var_list)} as the main variables")
        xr_data = xr_data[var_list]
    elif type(xr_data) == xr.core.dataarray.DataArray:
        print("    Data is a xr.Dataarray")
    
    res = xr_data.to_dataframe(name = 'val')
    res = res[['val']]
    res['time'] = pd.to_datetime(res.index)
    if not res.time.dt.tz:
        print("    The timezone is not defined")
        # res['time'] = res.time.dt.tz_localize('UTC')
    res.index = range(0, res.shape[0])
# =============================================================================
#     res['id'] = res.index
# =============================================================================
    
    print('') # newline
    return res
    

###############################################################################
#%%% ° tss_to_dataframe
def tss_to_dataframe(*, input_file, skip_rows, start_date, cumul = False):
    """
    Example
    -------
    base = gc.tss_to_dataframe(input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\001_prelim_cotech\2022-03-19_base\discharge_daily.tss",
                         skip_rows = 4,
                         start_date = '1991-08-01')
    
    precip = gc.tss_to_dataframe(input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\003_artif\2022-03-25_base\Precipitation_daily.tss",
                         skip_rows = 4,
                         start_date = '2000-01-01')
    precip.val = precip.val*534000000/86400
    # (le BV topographique du Meu fait 471 851 238 m2)
    precip['rolling_mean'] = precip['val'].rolling(10).mean()
    
    Parameters
    ----------
    input_file : str
        Chemin d'accès au fichier d'entrée
    skip_rows : int
        Nombre de lignes à enlever en tête de fichier. /!\ ce nombre n'est '
    start_date : str ou datetime
        Date de la 1re valeur du fichier
        /!\ Si str, il faut qu'elle soit au format "%Y-%m-%d"

    Returns
    -------
    df : pandas.DataFrame

    
    Implémentations futures
    -----------------------
    Récupérer la start_date à partir du fichier de settings indiqué au début
    du fichier *.tss., et regarder ensuite le SpinUp
    """
    
    #%% Récupération des inputs :
    # ---------------------------
    if start_date == 'std':
        print('> Pas encore implémenté...')
        # récupérer la start_date du fichier de settings
    else:
        start_date = pd.to_datetime(start_date)
    # print('> start_date = ' + str(start_date))
    
    
    #%% Création des dataframes :
    # ---------------------------
    # df = pd.read_csv(input_file, sep = r"\s+", header = 0, names = ['id', 'val'], skiprows = skip_rows)
    if skip_rows == 0: # Cas des fichiers de débits *.css, sans lignes d'info,
                       # avec seulement un header
        _fields = ['']
        n_col = 1
        
    else: # Cas des outputs *.tss avec plusieurs lignes d'info, la 2e ligne 
          # indiquant le nombre de colonnes. Dans ce cas, skip_rows doit être
          # égal à 2.
        with open(input_file) as temp_file:
            # temp_file.readline()
            # n_col = int(temp_file.readline()[0])
            content = temp_file.readlines()
            n_col = int(content[skip_rows-1][0])
        _fields = [str(n) for n in range(1, n_col)]
        _fields[0] = ''
        
    df = pd.read_csv(input_file, 
                     sep = r"\s+", 
                     header = 0, 
                     skiprows = skip_rows -1 + n_col, 
                     names = ['id'] +  ['val' + ending for ending in _fields],
                     )
    
    # Si la colonne id contient déjà des dates (au format texte ou datetime) :
    if type(df.id[0]) in [str, 
                          pd.core.indexes.datetimes.DatetimeIndex,
                          pd._libs.tslibs.timestamps.Timestamp]:
        df['time'] = pd.to_datetime(df.id)
    # Sinon (= si la colonne id contient des indices), il faut reconstruire les dates :
    else:
        date_indexes = pd.date_range(start = start_date, 
                                     periods = df.shape[0], freq = '1D')
        df['time'] = date_indexes
    
    if cumul:
        print('\ncumul == True')
        # Values are expected to be expressed in [.../d]
        # Cumsum is applied on all columns with values ('val', 'val2', 'val3', ...)
        
        timespan = df.loc[
            :, df.columns == 'time'
            ].diff().shift(-1, fill_value = 0)/np.timedelta64(1, 'D')
        
        # timespan = df.loc[
        #     :, df.columns == 'time'
        #     ].diff()/np.timedelta64(1, 'D')
        
        df.iloc[
            :].loc[:, (df.columns != 'id') * (df.columns != 'time')
            ] = (df.iloc[
                :].loc[:, (df.columns != 'id') * (df.columns != 'time')
                ] * timespan.values).cumsum(axis = 0)
        
        # Last value
        # df.iloc[-1].loc[:, (df.columns != 'id') * (df.columns != 'time')] = np.nan
        
                # np.diff(df.time)/np.timedelta64(1, 'D')
    return df


#%% MNT & WATERSHEDS OPERATIONS
###############################################################################
def extract_watershed(*, ldd, 
                      outlet, 
                      dirmap = '1-9',
                      engine:str = 'pysheds', 
                      src_crs = None,
                      drop = False):
    """
    

    Parameters
    ----------
    ldd : TYPE
        DESCRIPTION.
    outlets : TYPE
        DESCRIPTION.
    engine : TYPE
        DESCRIPTION.
    drop : bool, default False
        If True, only coordinate labels where the mask is are kept
        (coordinate labels outside from the mask are dropped from the result).

    Returns
    -------
    None.

    """
    
    # ---- Specify directional mapping
    if isinstance(dirmap, str):
        dirmap = dirmap.casefold().replace(' ', '').replace('-', '')
        if dirmap in ['19', '[19]', 'keypad', 'pcraster']:
            dirmap = (8, 9, 6, 3, 2, 1, 4, 7)       # pcraster system
        elif dirmap in ['d8', 'esri']:
            dirmap = (64, 128, 1, 2, 4, 8, 16, 32)  # ESRI system
        elif dirmap in ['d8wbt', 'wbt', 'whiteboxtools']:
            dirmap = (128, 1, 2, 4, 8, 16, 32, 64)  # WhiteBox Tools system
    
    # ---- Loading
    ds = load_any(ldd, decode_coords = 'all') # mask_and_scale = False
    if src_crs is not None:
        ds.rio.write_crs(src_crs, inplace = True)
    else:
        if ds.rio.crs is None:
            print("Err: The Coordinate Reference System is required. It should be embedded in the input DEM or passed with the 'src_crs' argument")
            return
    ds, nodata = standardize_fill_value(ds)

    var = main_vars(ds)[0]
    print(f"Drain direction variable is inferred to be {var}")
    x_var, y_var = main_space_dims(ds)
    encod = ds[var].encoding
    
    # Replacing nan with appropriate nodata value  
    std_nodata = min(dirmap) - 4
    if np.isnan(nodata):
        print(f"Warning: The nodata value {nodata} is not a number and is then corrected to {std_nodata} (int32)")
        nodata = std_nodata
    else:
        if (not np.int32(nodata) == nodata):
            print(f"Warning: The nodata value {nodata} dtype is wrong and is then corrected to {std_nodata} (int32)")
            nodata = std_nodata
        else:
            if nodata in dirmap:
                print(f"Warning: The nodata value {nodata} is part of dirmap and is then corrected to {std_nodata} (int32)")
                nodata = std_nodata
            else:
                nodata = np.int32(nodata)
    ds[var] = ds[var].fillna(nodata)
    
    viewfinder = ViewFinder(affine = ds.rio.transform(), 
                            shape = ds.rio.shape, 
                            crs = ds.rio.crs, 
                            nodata = np.int32(nodata))
    
    ldd = Raster(ds[var].astype(np.int32).data, viewfinder=viewfinder)
    grid = Grid.from_raster(ldd)
    
    # ---- With pysheds
    if engine.casefold() in ["pyshed", "pysheds"]:
        print('Pysheds engine...')
        
        # Compute accumulation
        acc = grid.accumulation(ldd, dirmap = dirmap, nodata_out = np.int32(-1))
        # Snap pour point to high accumulation cell (drained area > 1km²)
# ======== not working as desired (snaps to nearest corner) ===================
#         x_snap, y_snap = grid.snap_to_mask(
#             # acc > (1000 ** 2) / abs(ds.rio.resolution()[0] * ds.rio.resolution()[1]), 
#             acc > 15,
#             (outlet[0], outlet[1]), 
#             nodata_out = np.bool(False),
#             snap = "center",
#             )
#         
#         # Center snapped coords
#         x_snap += math.copysign(abs(ds.rio.resolution()[0]/2), outlet[0]-x_snap)
#         y_snap += math.copysign(abs(ds.rio.resolution()[1]/2), outlet[1]-y_snap)
#         
#         print(f"   . snap: {outlet[0]} -> {x_snap}  |  {outlet[1]} -> {y_snap}}}")
# =============================================================================
        
        col, row = grid.nearest_cell(outlet[0], outlet[1], snap = 'center')
        # if acc[row, col] < (1000 ** 2) / abs(ds.rio.resolution()[0] * ds.rio.resolution()[1]):
        if acc[row, col] < 15:
            print("   _ Warning: outlet seems to be out from mainstream")
        
            x_snap, y_snap = grid.snap_to_mask(
                # acc > (1000 ** 2) / abs(ds.rio.resolution()[0] * ds.rio.resolution()[1]), 
                acc > 15,
                (outlet[0], outlet[1]), 
                # nodata_out = np.bool(False),
                # snap = "center",
                # xytype='coordinate',
                )
            x_snap += ds.rio.resolution()[0]/2
            y_snap += ds.rio.resolution()[-1]/2
            
            print(f"      . consider trying: {x_snap}, {y_snap}")

        shed = grid.catchment(x = outlet[0], y = outlet[1], 
                              fdir = ldd, xytype='coordinate', 
                              nodata_out = np.bool(False),
                              dirmap = dirmap,
                              snap = 'center')
        
        # Output
        ds[var] = ([y_var, x_var], np.array(shed))
        ds = ds.rename({var: 'mask'})
        ds['mask'] = ds['mask'].astype(np.int8)
        ds['mask'].encoding = encod
        ds['mask'].encoding['dtype'] = np.int8
        ds['mask'].encoding['rasterio_dtype'] = np.int8
        ds['mask'].encoding['_FillValue'] = 0

        ds = georef(data = ds)
        
        if drop:
            ds = ds.where(ds.mask > 0, drop = True)
        
        
    # ---- Avec WhiteToolBox
# ======== discontinued =======================================================
#     elif engine.casefold() in ["wtb", "whitetoolbox"]:
#         print('WhiteToolBox engine...')
#     
#     wbt.watershed(
#         d8_path,
#         outlets_file,
#         os.path.join(os.path.split(d8_path)[0], "mask_bassin_xxx_wbt.tif"),
#         esri_pntr = True,
#         )
# =============================================================================
    
    return ds
    
    
###############################################################################
def compute_ldd(dem_path, 
                dirmap = '1-9',
                engine:str = 'pysheds',
                src_crs = None):
    """
    Convert a Digital Elevation Model (DEM) into a Local Drain Direction map (LDD).

    Parameters
    ----------
    dem_path : str, pathlib.Path, xarray.Dataset or xarray.DataArray
        Digital Elevation Model data. Supported file formats are *.tif*, *.asc* and *.nc*. 
        
    dirmap : tuple or str, optional, default '1-9'
        Direction codes convention.
        
        - ``'1-9'`` (or ``'keypad'``, or ``'pcraster'``): from 1 to 9, upward, 
          from bottom-left corner, no-flow is 5 [pcraster convention]
        - ``'D8'`` (or ``'ESRI'``): from 1 to 128 (base-2), clockwise, from 
          middle-right position, no-flow is 0 [esri convention]
        - ``'D8-WBT'`` (or ``'WhiteBoxTools'``): from 1 to 128 (base-2), 
          clockwise, from top-right corner, no-flow is 0 [WhiteBoxTools convention]
          
    engine : {'pysheds', 'whiteboxtools'}, optional, default 'pyshed'
        ``'whiteboxtools'`` has been deactivated to avoid the need to install whiteboxtools.

    Returns
    -------
    LDD raster, xarray.Dataset.

    """
    
    
    # ---- With pysheds
    if engine.casefold() in ["pyshed", "pysheds"]:
        """
        Adapted from Luca Guillaumot's work
        """
        
        print('Pysheds engine...')

        # Load the pysheds elements (grid & data)
# ===== obsolete: load from file ==============================================
        # ext = os.path.splitext(dem_path)[-1]
        # if ext == '.tif':
        #     grid = Grid.from_raster(dem_path, data_name = 'dem')
        #     dem = grid.read_raster(dem_path)
        # elif ext == '.asc':
        #     grid = Grid.from_ascii(dem_path)
        #     dem = grid.read_ascii(dem_path)
# ============================================================================= 
        ds = load_any(dem_path, decode_coords = 'all')
        if src_crs is not None:
            ds.rio.write_crs(src_crs, inplace = True)
        else:
            if ds.rio.crs is None:
                print("Err: The Coordinate Reference System is required. It should be embedded in the input DEM or passed with the 'src_crs' argument")
                return
        ds, nodata = standardize_fill_value(ds)
        var = main_vars(ds)[0]
        print(f"Elevation variable is inferred to be {var}")
        x_var, y_var = main_space_dims(ds)
        encod = ds[var].encoding
        # NaN data are problematic when filling
        # nan_mask = ds[var].isnull().data
        nan_mask = xr.where(~ds[var].isnull(), True, False).data
        ds[var] = ds[var].fillna(-9999)
        ds[var].encoding = encod
        
        viewfinder = ViewFinder(affine = ds.rio.transform(), 
                                shape = ds.rio.shape, 
                                crs = ds.rio.crs, 
                                nodata = nodata)
        dem = Raster(ds[var].data, viewfinder=viewfinder)
        grid = Grid.from_raster(dem)
        
        # Fill depressions in DEM
# =============================================================================
#         print('   . dem no data is ', grid.nodata)
# =============================================================================
        flooded_dem = grid.fill_depressions(dem)
        # Resolve flats in DEM
        inflated_dem = grid.resolve_flats(flooded_dem)
        # Specify directional mapping
        if isinstance(dirmap, str):
            dirmap = dirmap.casefold().replace(' ', '').replace('-', '')
            if dirmap in ['19', '[19]', 'keypad', 'pcraster']:
                dirmap = (8, 9, 6, 3, 2, 1, 4, 7)
            elif dirmap in ['d8', 'esri']:
                dirmap = (64, 128, 1, 2, 4, 8, 16, 32)  # ESRI system
            elif dirmap in ['d8wbt', 'wbt', 'whiteboxtools']:
                dirmap = (128, 1, 2, 4, 8, 16, 32, 64)  # WhiteBox Tools system

        # Compute flow directions
        direc = grid.flowdir(inflated_dem, dirmap=dirmap, 
                             nodata_out = np.int32(-3))
        # Replace flats (-1) with value 5 (no flow)
        direc = xr.where(direc == -1, 5, direc)
        # Replace pits (-2) with value 5 (no flow)
        direc = xr.where(direc == -2, 5, direc)
        
        # Output
        ds[var] = ([y_var, x_var], np.array(direc))
        ds[var] = ds[var].where(nan_mask)
        ds = ds.rename({var: 'LDD'})
# =============================================================================
#         ds['LDD'] = ds['LDD'].astype(float) # astype(int)
# =============================================================================
# =============================================================================
#         ds['LDD'] = ds['LDD'].astype(np.int32)
# =============================================================================
        ds['LDD'].encoding = encod
        ds['LDD'].encoding['dtype'] = np.int32
        ds['LDD'].encoding['rasterio_dtype'] = np.int32
        ds['LDD'].encoding['_FillValue'] = -3
# ========= issue with dtypes when exporting ==================================
#         if 'scale_factor' in ds['LDD'].encoding:
#             ds['LDD'].encoding['scale_factor'] = np.int32(ds['LDD'].encoding['scale_factor'])
#         if 'add_offset' in ds['LDD'].encoding:
#             ds['LDD'].encoding['add_offset'] = np.int32(ds['LDD'].encoding['add_offset'])
#         if '_FillValue' in ds['LDD'].encoding:
#             ds['LDD'].encoding['_FillValue'] = np.int32(-1)
# =============================================================================
        ds = georef(data = ds)
        
    
    # ---- With WhiteToolBox (discontinued)
# =============================================================================
#     elif engine.casefold() in ["wtb", "whitetoolbox"]:
#         print('WhiteToolBox engine...')
#         dist_ = 10
#         
#         # Breach depressions
#         wbt.breach_depressions_least_cost(
#             dem_path,
#             os.path.splitext(dem_path)[0] + f"_breached{dist_}[wtb].tif",
#             dist_)
#         print('    Fichier intermédiaire créé')
#         
# # =============================================================================
# #         # Fill depression (alternative)
# #         wbt.fill_depressions(
# #             dem_path,
# #             os.path.splitext(dem_path)[0] + "_filled[wtb].tif",
# #             10)
# # =============================================================================
#         
#         # Creation du D8
#         suffix = "breached{}[wtb]".format(dist_)
#         wbt.d8_pointer(
#             os.path.splitext(dem_path)[0] + "_" + suffix + ".tif",
#             os.path.join(os.path.split(dem_path)[0], "D8_xxx_" + suffix + "_wtb.tif"), 
#             esri_pntr = True)
#         print('    LDD "D8 ESRI" créé')
# =============================================================================

    return ds    
    

######## DOES NOT WORK ########################################################
# =============================================================================
# for a better solution: https://gis.stackexchange.com/questions/413349/calculating-area-of-lat-lon-polygons-without-transformation-using-geopandas
# =============================================================================
def cell_area(data, src_crs = None, engine = 'pysheds'):
    
    # ---- With pysheds
    if engine.casefold() in ["pyshed", "pysheds"]:
        print('Pysheds engine...')

        # Load the pysheds grid 
        ds = load_any(data, decode_coords = 'all')
        if src_crs is not None:
            ds.rio.write_crs(src_crs, inplace = True)
        else:
            if ds.rio.crs is None:
                print("Err: The Coordinate Reference System is required. It should be embedded in the input DEM or passed with the 'src_crs' argument")
                return
        ds, nodata = standardize_fill_value(ds)
        var = main_vars(ds)[0]
        x_var, y_var = main_space_dims(ds)
        encod = ds[var].encoding
# =============================================================================
#         # NaN data are problematic when filling
#         # nan_mask = ds[var].isnull().data
#         nan_mask = xr.where(~ds[var].isnull(), True, False).data
#         ds[var] = ds[var].fillna(-9999)
# =============================================================================
        ds[var].encoding = encod
        
# ===== useless because pGrid only takes files as inputs ======================
#         viewfinder = ViewFinder(affine = ds.rio.transform(), 
#                                 shape = ds.rio.shape, 
#                                 crs = ds.rio.crs, 
#                                 nodata = nodata)
#         raster = Raster(ds[var].data, viewfinder=viewfinder)
# =============================================================================
        
        export(ds, r"temp_raster.tif")        
        grid = pGrid.from_raster(r"temp_raster.tif", data_name = 'area')
        grid.cell_area()
        os.remove(r"temp_raster.tif")
        print(r"   _ The temporary file 'temp_raster.tif' has been removed")
        
        # Output
        ds[var] = ([y_var, x_var], np.array(grid.area))
        ds = ds.rename({var: 'area'})
        ds['area'].encoding = encod
        
        print("\nWarning: This function does not work as expected yet: area are only computed from the resolution")
        return ds
    

###############################################################################
#%%% ° Convert LDD code
"""
To switch between different direction mappings
"""
def switch_direction_map(input_file, input_mapping, output_mapping):
    
    #%%% Inputs
    mapping_dict = {'input': input_mapping, 'output': output_mapping}
    
    for m in mapping_dict:
        if mapping_dict[m].casefold().replace("_", "").replace(" ", "") in ["ldd","localdraindirections"]:
            mapping_dict[m] = "LDD"
        elif mapping_dict[m].casefold().replace("_", "").replace(" ", "") in ["d8", "esri", "d8esri", "esrid8", "d8standard", "standardd8"]:
            mapping_dict[m] = "D8 ESRI"
        elif mapping_dict[m].casefold().replace("_", "").replace(" ", "") in ["wtb", "whitetoolbox", "d8whitetoolbox", "d8wtb", "wtbd8"]:
            mapping_dict[m] = "WTB"
        elif mapping_dict[m].casefold().replace("_", "").replace(" ", "") in ["agnps"]:
            mapping_dict[m] = "AGNPS" 
        else:
            return "Error: mapping unknown"
        
        print(f"{m} direction: {mapping_dict[m]}")
    

    #%%% Conversion    
    # Chargement des données
    data_in = rasterio.open(input_file, 'r')
    data_profile = data_in.profile
    val = data_in.read()
    data_in.close()
    
    # Conversion
    
    # rows: 0:'LDD', 1:'D8', 2:'WTB'
    col = ['LDD', 'D8 ESRI', 'WTB', 'AGNPS']
    keys_ = np.array(
        [[8, 64,  128,  1,],#N
         [9, 128, 1,    2,],  #NE
         [6, 1,   2,    3,],  #E
         [3, 2,   4,    4,],  #SE
         [2, 4,   8,    5,],  #S
         [1, 8,   16,   6,], #SO
         [4, 16,  32,   7,], #O
         [7, 32,  64,   8,], #NO
         [5, 0,   0,    None,]]) #-
    
    for d in range(0, 9):
        val[val == keys_[d, 
                         col.index(mapping_dict['input'])
                         ]
            ] = -keys_[d, 
                      col.index(mapping_dict['output'])]
        
    val = -val # On passe par une valeur négative pour éviter les redondances
    # du type : 3 --> 2, 2 --> 4
    
    #%%% Export
    output_file = os.path.splitext(input_file)[0] + "_{}.tif".format(mapping_dict['output'])
    
    with rasterio.open(output_file, 'w', **data_profile) as output_f:
        output_f.write(val)
        print("\nFile created")
        

###############################################################################
#%%% ° Alter modflow_river_percentage
def river_pct(input_file, value):
    """
    Creates artificial modflow_river_percentage inputs (in *.nc) to use for
    drainage.

    Parameters
    ----------
    input_file : str
        Original modflow_river_percentage.tif file to duplicate/modify
    value : float
        Value to impose on cells (from [0 to 1], not in percentage!)
        This value is added to original values as a fraction of the remaining
        "non-river" fraction:
            For example, value = 0.3 (30%):
                - cells with 0 are filled with 0.3
                - cells with 1 remain the same
                - cells with 0.8 take the value 0.86, because 30% of what should
                have been capillary rise become baseflow (0.8 + 0.3*(1-0.8))
                - cells with 0.5 take the value 0.65 (0.5 + 0.3*(1-0.5))

    Returns
    -------
    None.

    """
    #%% Loading
    # ---------
    if os.path.splitext(input_file)[-1] == '.tif':
        with xr.open_dataset(input_file, # .tif 
                             decode_times = True, 
                             ) as ds:
            ds.load()
    elif os.path.splitext(input_file)[-1] == '.nc':
        with xr.open_dataset(input_file, 
                             decode_times = True, 
                             decode_coords = 'all',
                             ) as ds:
            ds.load()   
    
    #%% Computing
    # -----------
    # ds['band_data'] = ds['band_data']*0 + value
    ds_ones = ds.copy(deep = True)
    ds_ones['band_data'] = ds_ones['band_data']*0 + 1
    
    #% modflow_river_percentage_{value}.nc:
    ds1 = ds.copy(deep = True)
    ds1['band_data'] = ds1['band_data'] + (ds_ones['band_data'] - ds1['band_data'])*value
    
    #% drainage_river_percentage_{value}.nc :
    ds2 = ds1 - ds
    
    #%% Formatting
    # ------------
    ds1.rio.write_crs(2154, inplace = True)
    ds1.x.attrs = {'standard_name': 'projection_x_coordinate',
                                'long_name': 'x coordinate of projection',
                                'units': 'Meter'}
    ds1.y.attrs = {'standard_name': 'projection_y_coordinate',
                                'long_name': 'y coordinate of projection',
                                'units': 'Meter'}
    # To avoid conflict when exporting to netcdf:
    ds1.x.encoding['_FillValue'] = None
    ds1.y.encoding['_FillValue'] = None
    
    ds2.rio.write_crs(2154, inplace = True)
    ds2.x.attrs = {'standard_name': 'projection_x_coordinate',
                                'long_name': 'x coordinate of projection',
                                'units': 'Meter'}
    ds2.y.attrs = {'standard_name': 'projection_y_coordinate',
                                'long_name': 'y coordinate of projection',
                                'units': 'Meter'}
    # To avoid conflict when exporting to netcdf:
    ds2.x.encoding['_FillValue'] = None
    ds2.y.encoding['_FillValue'] = None
    
    #%% Exporting
    # -----------
    (folder, file) = os.path.split(input_file)
    (file, extension) = os.path.splitext(file)
    
    output_file1 = os.path.join(folder, "_".join([file, str(value)]) + '.nc')
    ds1.to_netcdf(output_file1)
    
    output_file2 = os.path.join(folder, "_".join(['drainage_river_percentage', str(value)]) + '.nc')
    ds2.to_netcdf(output_file2)


#%% QUANTITIES OPERATIONS
###############################################################################
# Calcule ETref et EWref à partir de la "pan evaporation" de ERA5-Land
def compute_Erefs_from_Epan(input_file):
    print("\nDeriving standard grass evapotranspiration and standard water evapotranspiration from pan evaporation...")
    Epan = load_any(input_file, decode_coords = 'all', decode_times = True)
    
    var = main_vars(Epan)
    
    print("   _ Computing ETref (ET0) from Epan...")
    ETref = Epan.copy()
    ETref[var] = ETref[var]*0.675
    
    print("   _ Computing EWref from Epan...")
    EWref = Epan.copy()
    EWref[var] = EWref[var]*0.75
    
    print("   _ Transferring encodings...")
    ETref[var].encoding = Epan[var].encoding
    EWref[var].encoding = Epan[var].encoding
    # Case of packing
    if ('scale_factor' in Epan[var].encoding) | ('add_offset' in Epan[var].encoding):
        # Packing (lossy compression) induces a loss of precision of 
        # apprx. 1/1000 of unit, for a quantity with an interval of 150 
        # units. The packing is initially used in some original ERA5-Land data
        ETref[var].encoding['scale_factor'] = ETref[var].encoding['scale_factor']*0.675
        ETref[var].encoding['add_offset'] = ETref[var].encoding['add_offset']*0.675
        EWref[var].encoding['scale_factor'] = EWref[var].encoding['scale_factor']*0.75
        EWref[var].encoding['add_offset'] = EWref[var].encoding['add_offset']*0.75
    
    return ETref, EWref


###############################################################################
def compute_wind_speed(u_wind_data, v_wind_data):
    """
    U-component of wind is parallel to the x-axis
    V-component of wind is parallel to the y-axis
    """
    
# =============================================================================
#     print("\nIdentifying files...")
#     U_motif = re.compile('U-component')
#     U_match = U_motif.findall(input_file)
#     V_motif = re.compile('V-component')
#     V_match = V_motif.findall(input_file)
#     
#     if len(U_match) > 0:
#         U_input_file = '%s' % input_file # to copy the string
#         V_input_file = '%s' % input_file
#         V_input_file = V_input_file[:U_motif.search(input_file).span()[0]] + 'V' + V_input_file[U_motif.search(input_file).span()[0]+1:]
#     elif len(V_match) > 0:
#         V_input_file = '%s' % input_file # to copy the string
#         U_input_file = '%s' % input_file
#         U_input_file = U_input_file[:V_motif.search(input_file).span()[0]] + 'U' + U_input_file[V_motif.search(input_file).span()[0]+1:]
# =============================================================================
    
    print("\nComputing wind speed from U- and V-components...")

    U_ds = load_any(u_wind_data, decode_coords = 'all', decode_times = True)
    V_ds = load_any(v_wind_data, decode_coords = 'all', decode_times = True)
    
    wind_speed_ds = U_ds.copy()
    wind_speed_ds = wind_speed_ds.rename(u10 = 'wind_speed')
    wind_speed_ds['wind_speed'] = np.sqrt(U_ds.u10*U_ds.u10 + V_ds.v10*V_ds.v10)
        # nan remain nan
    
    print("   _ Transferring encodings...")
    wind_speed_ds['wind_speed'].encoding = V_ds.v10.encoding
    wind_speed_ds['wind_speed'].attrs['long_name'] = '10 metre wind speed'
    # Case of packing
    if ('scale_factor' in V_ds.v10.encoding) | ('add_offset' in V_ds.v10.encoding):
        # Packing (lossy compression) induces a loss of precision of 
        # apprx. 1/1000 of unit, for a quantity with an interval of 150 
        # units. The packing is initially used in some original ERA5-Land data
    
        # Theoretical max wind speed: 
        max_speed = 56 # m/s = 201.6 km/h
        (scale_factor, add_offset) = compute_scale_and_offset(-max_speed, max_speed, 16)
            # Out: (0.0017090104524299992, 0.0008545052262149966)
        wind_speed_ds['wind_speed'].encoding['scale_factor'] = scale_factor
        wind_speed_ds['wind_speed'].encoding['add_offset'] = add_offset
        # wind_speed_ds['wind_speed'].encoding['FillValue_'] = -32767
            # To remain the same as originally
            # Corresponds to -55.99829098954757 m/s
    
    return wind_speed_ds
    

###############################################################################
def compute_relative_humidity(*, dewpoint_input_file, 
                              temperature_input_file,
                              pressure_input_file,
                              method = "Penman-Monteith"):
    
    """
    cf formula on https://en.wikipedia.org/wiki/Dew_point
    
    gc.compute_relative_humidity(
        dewpoint_input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\2011-2021 Dewpoint temperature.nc", 
        temperature_input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\2011-2021 Temperature.nc",
        pressure_input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\2011-2021 Surface pressure.nc",
        method = "Sonntag")
    
    """
    
    
    # ---- Loading data
    # --------------
    print("\nLoading data...")
    # Checking that the time period matches:
    years_motif = re.compile('\d{4,4}-\d{4,4}')
    years_dewpoint = years_motif.search(dewpoint_input_file).group()
    years_pressure = years_motif.search(pressure_input_file).group()
    years_temperature = years_motif.search(temperature_input_file).group()
    if (years_dewpoint == years_pressure) and (years_dewpoint == years_temperature):
        print("   Years are matching: {}".format(years_dewpoint))
    else:
        print("   /!\ Years are not matching: {}\n{}\n{}".format(years_dewpoint, years_pressure, years_temperature))
        # return 0
    
    with xr.open_dataset(dewpoint_input_file, decode_coords = 'all') as Dp:
        Dp.load() # to unlock the resource
    with xr.open_dataset(temperature_input_file, decode_coords = 'all') as T:
        T.load() # to unlock the resource
    with xr.open_dataset(pressure_input_file, decode_coords = 'all') as Pa:
        Pa.load() # to unlock the resource
    
    # ---- Sonntag formula
    # -----------------
    if method.casefold() in ['sonntag', 'sonntag1990']:
        print("\nComputing the relative humidity, using the Sonntag 1990 formula...")
        # NB : air pressure Pa is not used in this formula
        
        # Constants:
        alpha_ = 6.112 # [hPa]
        beta_ = 17.62 # [-]
        lambda_ = 243.12 # [°C]
        
        # Temperature in degrees Celsius:
        Tc = T.copy()
        Tc['t2m'] = T['t2m'] - 273.15
        Dpc = Dp.copy()
        Dpc['d2m'] = Dp['d2m'] - 273.15
        
        # Saturation vapour pressure [hPa]:
        Esat = Tc.copy()
        Esat = Esat.rename(t2m = 'vpsat')
        Esat['vpsat'] = alpha_ * np.exp((beta_ * Tc['t2m']) / (lambda_ + Tc['t2m']))
        
        # Vapour pressure [hPa]:
        E = Dp.copy()
        E = E.rename(d2m = 'vp')
        E['vp'] = alpha_ * np.exp((Dpc['d2m'] * beta_) / (lambda_ + Dpc['d2m']))
        
        # Relative humidity [%]:
        RHS = Dp.copy()
        RHS = RHS.rename(d2m = 'rh')
        RHS['rh'] = E['vp']/Esat['vpsat']*100
    
    elif method.casefold() in ['penman', 'monteith', 'penman-monteith']:
        print("\nComputing the relative humidity, using the Penman Monteith formula...")
        # NB : air pressure Pa is not used in this formula
        # Used in evaporationPot.py
        # http://www.fao.org/docrep/X0490E/x0490e07.htm   equation 11/12
        
        # Constants:
        alpha_ = 0.6108 # [kPa]
        beta_ = 17.27 # [-]
        lambda_ = 237.3 # [°C]
        
        # Temperature in degrees Celsius:
        Tc = T.copy()
        Tc['t2m'] = T['t2m'] - 273.15
        Dpc = Dp.copy()
        Dpc['d2m'] = Dp['d2m'] - 273.15
        
        # Saturation vapour pressure [kPa]:
        Esat = Tc.copy()
        Esat = Esat.rename(t2m = 'vpsat')
        Esat['vpsat'] = alpha_ * np.exp((beta_ * Tc['t2m']) / (lambda_ + Tc['t2m']))
        
        # Vapour pressure [kPa]:
        E = Dp.copy()
        E = E.rename(d2m = 'vp')
        E['vp'] = alpha_ * np.exp((beta_ * Dpc['d2m']) / (lambda_ + Dpc['d2m']))
        
        # Relative humidity [%]:
        # https://www.fao.org/3/X0490E/x0490e07.htm Eq. (10)
        RHS = Dp.copy()
        RHS = RHS.rename(d2m = 'rh')
        RHS['rh'] = E['vp']/Esat['vpsat']*100
        
    #% Attributes
    print("\nTransferring encodings...")
    RHS['rh'].attrs['units'] = '%'
    RHS['rh'].attrs['long_name'] = 'Relative humidity (from 2m dewpoint temperature)'
    RHS['rh'].encoding = Dp['d2m'].encoding
    # Case of packing
    if ('scale_factor' in Dp['d2m'].encoding) | ('add_offset' in Dp['d2m'].encoding):
        # Packing (lossy compression) induces a loss of precision of 
        # apprx. 1/1000 of unit, for a quantity with an interval of 150 
        # units. The packing is initially used in some original ERA5-Land data.
        
        # RHS['rh'].encoding['scale_factor'] = 0.0016784924086366065
        # RHS['rh'].encoding['add_offset'] = 55.00083924620432
        # RHS['rh'].encoding['_FillValue'] = 32767
        # RHS['rh'].encoding['missing_value'] = 32767
        (scale_factor, add_offset) = compute_scale_and_offset(-1, 100, 16)
            # Out: (0.0015411612115663385, 49.50077058060578)
        RHS['rh'].encoding['scale_factor'] = scale_factor
        RHS['rh'].encoding['add_offset'] = add_offset
        # RHS['rh'].encoding['_FillValue'] = -32767 
            # To match with original value
            # Corresponds to -0.9984588387884301 %
    
    
    return RHS


###############################################################################
# Convertit les données de radiation (J/m2/h) en W/m2
def convert_downwards_radiation(input_file, is_dailysum = False):   
    print("\nConverting radiation units...")
    rad = load_any(input_file, decode_coords = 'all', decode_times = True)
    
    var = main_vars(rad)
    print("   _ Field is: {}".format(var))
    
    print("   _ Computing...")
    rad_W = rad.copy()
    if not is_dailysum:
        conv_factor = 3600 # because 3600s in 1h
    else:
        conv_factor = 86400 # because 86400s in 1d
    rad_W[var] = rad_W[var]/conv_factor 
    
    print("   _ Transferring encodings...")
    rad_W[var].attrs['units'] = 'W m**-2'
    rad_W[var].encoding = rad[var].encoding
    
    # Case of packing
    if ('scale_factor' in rad_W[var].encoding) | ('add_offset' in rad_W[var].encoding):
        # Packing (lossy compression) induces a loss of precision of 
        # apprx. 1/1000 of unit, for a quantity with an interval of 150 
        # units. The packing is initially used in some original ERA5-Land data.
        rad_W[var].encoding['scale_factor'] = rad_W[var].encoding['scale_factor']/conv_factor
        rad_W[var].encoding['add_offset'] = rad_W[var].encoding['add_offset']/conv_factor
        # NB: 
        # rad_W[var].encoding['FillValue_'] = -32767
            # To remain the same as originally
            # Corresponds to -472.11... m/s
            # NB: For few specific times, data are unavailable. Such data are coded 
            # with the value -1, packed into -32766
    
    return rad_W
    


#%% * OBSOLETE ? Shift rasters (GeoTIFF or NetCDF)
###############################################################################
# Pas totalement fini. Code issu de 'datatransform.py'
def transform_tif(*, input_file, x_shift = 0, y_shift = 0, x_size = 1, y_size = 1):
    """
    EXAMPLE:
        import datatransform as dt
        dt.transform_tif(input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\data\input_1km_LeMeu\areamaps\mask_cwatm_LeMeu_1km.tif",
                     x_shift = 200,
                     y_shift = 300)
    """
    
    # Ouvrir le fichier : 
    data = rasterio.open(input_file, 'r')
    # Récupérer le profil :
    _prof_base = data.profile
    trans_base = _prof_base['transform']
    # Juste pour visualiser :
    print('\nLe profil affine initial est :')
    print(trans_base)
    # Modifier le profile :  
    trans_modf = Affine(trans_base[0]*x_size, trans_base[1], trans_base[2] + x_shift,
                        trans_base[3], trans_base[4]*y_size, trans_base[5] + y_shift)
    print('\nLe profil modifié est :')
    print(trans_modf)
    _prof_modf = _prof_base
    _prof_modf.update(transform = trans_modf)
    
    # Exporter :
    _basename = os.path.splitext(input_file)[0]
    
    add_name = ''
    if x_shift != 0 or y_shift !=0:
        add_name = '_'.join([add_name, 'shift'])
        if x_shift != 0:
            add_name = '_'.join([add_name, 'x' + str(x_shift)])
        if y_shift != 0:
            add_name = '_'.join([add_name, 'y' + str(y_shift)])
    if x_size != 1 or y_size !=1:
        add_name = '_'.join([add_name, 'size'])
        if x_size != 1:
            add_name = '_'.join([add_name, 'x' + str(x_size)])
        if y_size != 1:
            add_name = '_'.join([add_name, 'y' + str(y_size)])
    output_file = '_'.join([_basename, add_name]) + '.tif'
    with rasterio.open(output_file, 'w', **_prof_modf) as out_f:
        out_f.write_band(1, data.read()[0])
    
    data.close()
    
def transform_nc(*, input_file, x_shift = 0, y_shift = 0, x_size = 1, y_size = 1):
    """
    EXAMPLE:
        import datatransform as dt
        dt.transform_nc(input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\data\input_1km_LeMeu\landsurface\topo\demmin.nc",
                     x_shift = 200,
                     y_shift = 400)       
    """
    
    with xr.open_dataset(input_file) as data:
        data.load() # to unlock the resource
        
    # Modifier :
    data['x'] = data.x + x_shift
    data['y'] = data.y + y_shift
    
    # Exporter :
    _basename = os.path.splitext(input_file)[0]
    
    add_name = ''
    if x_shift != 0 or y_shift !=0:
        add_name = '_'.join([add_name, 'shift'])
        if x_shift != 0:
            add_name = '_'.join([add_name, 'x' + str(x_shift)])
        if y_shift != 0:
            add_name = '_'.join([add_name, 'y' + str(y_shift)])
    if x_size != 1 or y_size !=1:
        add_name = '_'.join([add_name, 'size'])
        if x_size != 1:
            add_name = '_'.join([add_name, 'x' + str(x_size)])
        if y_size != 1:
            add_name = '_'.join([add_name, 'y' + str(y_size)])
    output_file = '_'.join([_basename, add_name]) + '.nc'
    
    data.to_netcdf(output_file)
    

#%% * tools for computing coordinates
###############################################################################
def convert_coord(pointXin, pointYin, inputEPSG = 2154, outputEPSG = 4326):	
    """
    Il y a un soucis dans cette fonction. X et Y se retrouvent inversées.
    Il vaut mieux passer par les fonctions rasterio (voir plus haut) :
        
    coords_conv = rasterio.warp.transform(rasterio.crs.CRS.from_epsg(inputEPSG), 
                                          rasterio.crs.CRS.from_epsg(outputEPSG), 
                                          [pointXin], [pointYin])
    pointXout = coords_conv[0][0]
    pointYout = coords_conv[1][0]
    """
    #% Inputs (standards)
    # =============================================================================
    # # Projected coordinates in Lambert-93 
    # pointXin = 350556.92318   #Easthing
    # pointYin = 6791719.72296  #Northing
    # (Rennes coordinates)
    # =============================================================================
    
    # =============================================================================
    # # Geographical coordinates in WGS84 (2D) 
    # pointXin = 48.13222  #Latitude (Northing)
    # pointYin = -1.7      #Longitude (Easting)
    # (Rennes coordinates)
    # =============================================================================
    
    # =============================================================================
    # # Spatial Reference Systems
    # inputEPSG = 2154   #Lambert-93
    # outputEPSG = 4326  #WGS84 (2D)
    # =============================================================================
    
    # # Conversion into EPSG system
    # For easy use, inputEPSG and outputEPSG can be defined with identifiers strings
    switchEPSG = {
        'L93': 2154,   #Lambert-93
        'L-93': 2154,  #Lambert-93
        'WGS84': 4326, #WGS84 (2D)
        'GPS': 4326,   #WGS84 (2D)
        'LAEA': 3035,  #LAEA Europe 
        }
    
    if isinstance(inputEPSG, str):
        inputEPSG = switchEPSG.get(inputEPSG, False)
        # If the string is not a valid identifier:
        if not inputEPSG:
            print('Unknown input coordinates system')
            return
            
    if isinstance(outputEPSG, str):
        outputEPSG = switchEPSG.get(outputEPSG, False)
        # If the string is not a valid identifier:
        if not outputEPSG:
            print('Unknown output coordinates system')
            return

    
    #% Outputs
# =============================================================================
#     # Méthode osr
#     # create a geometry from coordinates
#     point = ogr.Geometry(ogr.wkbPoint)
#     point.AddPoint(pointXin, pointYin)
#     
#     # create coordinate transformation
#     inSpatialRef = osr.SpatialReference()
#     inSpatialRef.ImportFromEPSG(inputEPSG)
#     
#     outSpatialRef = osr.SpatialReference()
#     outSpatialRef.ImportFromEPSG(outputEPSG)
#     
#     coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
#     
#     # transform point
#     point.Transform(coordTransform)
#     pointXout = point.GetX()
#     pointYout = point.GetY()
# =============================================================================
    
    # Méthode rasterio      
    coords_conv = rasterio.warp.transform(rasterio.crs.CRS.from_epsg(inputEPSG), 
                                          rasterio.crs.CRS.from_epsg(outputEPSG), 
                                          [pointXin], [pointYin])
    pointXout = coords_conv[0][0]
    pointYout = coords_conv[1][0]
    
    # Return point coordinates in output format
    return(pointXout, pointYout)


#%% date tools for QGIS
"""
Pour faire facilement la conversion "numéro de bande - date" dans QGIS lorsqu'on
ouvre les fichers NetCDF comme rasters.

/!\ Dans QGIS, le numéro de 'band' est différent du 'time'
(parfois 'band' = 'time' + 1, parfois il y a une grande différence)
C'est le 'time' qui compte.
"""
###############################################################################
def date_to_index(_start_date, _date, _freq):
    time_index = len(pd.date_range(start = _start_date, end = _date, freq = _freq))-1
    print('La date {} correspond au temps {}'.format(_date, str(time_index)))
    return time_index


###############################################################################
def index_to_date(_start_date, _time_index, _freq):
    date_index = pd.date_range(start = _start_date, periods = _time_index+1, freq = _freq)[-1]
    print('Le temps {} correspond à la date {}'.format(_time_index, str(date_index)))
    return date_index


#%% main
if __name__ == "__main__":
    # Format the inputs (assumed to be strings) into floats
    sys.argv[1] = float(sys.argv[1])
    sys.argv[2] = float(sys.argv[2])
    # Print some remarks
    print('Arguments:')
    print(sys.argv[1:])
    # Execute the ConvertCoord function
    (a,b) = convert_coord(*sys.argv[1:])
    print(a,b)