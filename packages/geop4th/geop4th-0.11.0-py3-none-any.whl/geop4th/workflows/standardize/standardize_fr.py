# -*- coding: utf-8 -*-
"""
Created on Thu 16 Dec 2021

@author: Alexandre Kenshilik Coche
@contact: alexandre.co@hotmail.fr

This module is a collection of tools for manipulating hydrological space-time
data, especially netcdf data. It has been originally developped to provide
preprocessing tools for CWatM (https://cwatm.iiasa.ac.at/) and HydroModPy
(https://gitlab.com/Alex-Gauvain/HydroModPy), but most functions have been
designed to be of general use.

"""

#%% Imports:
import xarray as xr
xr.set_options(keep_attrs = True)
import rioxarray as rio #Not necessary, the rio module from xarray is enough
import pandas as pd
import geopandas as gpd
import numpy as np
import rasterio
import rasterio.features
from affine import Affine
from shapely.geometry import Point
# from shapely.geometry import Polygon
# from shapely.geometry import mapping
import os
import re
import sys
import gc # garbage collector
from pathlib import Path
# import matplotlib.pyplot as plt
import fiona
import datetime

from geop4th import geobricks as geo

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

        
#%% GEOREFERENCING
###############################################################################
# Georef (ex-decorate_NetCDF_for_QGIS)
def georef(data, *, data_type = 'other', include_crs = True, export_opt = False, crs = None, **time_kwargs):   
    r"""
    Description
    -----------
    Il est fréquent que les données de source externe présentent des défauts
    de formattage (SCR non inclus, coordonnées non standard, incompatibilité
    avec QGIS...).
    Cette fonction permet de générer un raster ou shapefile standardisé, 
    en particulier du point de vue de ses métadonnées, facilitant ainsi les
    opérations de géotraitement mais aussi la visualisation sous QGIS.
    
    Exemple
    -------
    import geoconvert as gc
    gc.georef(data = r"D:\CWatM\raw_results\test1\modflow_watertable_monthavg.nc", 
              data_type = 'CWatM')
    
    Parametres
    ----------
    data : str or xr.Dataset (or xr.DataArray)
        Chemin d'accès au fichier à modifier
        (le fichier original ne sera pas altéré, un nouveau fichier '(...)_QGIS.nc'
         sera créé.)
    data_type : str
        Type de données :
            'modflow' | 'DRIAS-Climat 2020' | 'DRIAS-Eau 2021' \ 'SIM 2021' |
            'DRIAS-Climat 2022' \ 'Climat 2022' | 'DRIAS-Eau 2024' \ 'SIM 2024' |
            'CWatM' | 'autre' \ 'other'
            (case insensitive)
    include_crs : bool, optional
        DESCRIPTION. The default is True.
    export_opt : bool, optional
        DESCRIPTION. The default is True.
        Le NetCDF crée est directement enregistré dans le même dossier que 
        le fichier d'origine, en rajoutant 'georef' à son nom.
    crs : int, optional
        Destination CRS, only necessary when data_type == 'other' The default is None.
    **time_kwargs : 
        Arguments for ``use_standard_time`` function:
            - var : time variable name (str), optional, default None
            - infer_from : {'dims', 'coords', 'all'}, optional, default 'dims' 

    Returns
    -------
    xarray.Dataset or geopandas.GeoDataFrame. 
    
    """
    
# =============================================================================
#     if include_crs is False:
#         if crs is not None:
#             include_crs = True
# =============================================================================
    
    # ---- NetCDF de ModFlow
    # --------------------
    if data_type.casefold() == 'modflow': 
        # Load
        data_ds = geo.load_any(data, decode_coords = 'all', decode_times = False)
        
        print("\nFormatting data...")
        # Add standard attributes for coordinates (mandatory for QGIS to correctly read data)
        data_ds.x.attrs = {'standard_name': 'projection_x_coordinate',
                            'long_name': 'x coordinate of projection',
                            'units': 'Meter'}
        data_ds.y.attrs = {'standard_name': 'projection_y_coordinate',
                            'long_name': 'y coordinate of projection',
                            'units': 'Meter'}
        print("   _ Standard attributes added for coordinates x and y")
        
        # Add CRS
        data_epsg = 2154 # Lambert 93
        crs_suffix = ''
        if include_crs:
            data_ds.rio.write_crs(data_epsg, inplace = True)
            print(f'   _ Coordinates Reference System (epsg:{data_epsg}) included.')
        else:
            print(f'   _ Coordinates Reference System not included. {data_epsg} has to be manually specified in QGIS')
            crs_suffix = 'nocrs'
        
    # ========== USELESS ==========================================================
    #     data_ds = data_ds.transpose('time', 'y', 'x')
    # =============================================================================


    # ---- NetCDF de CWatM
    # Inclusion du SCR
    # ------------------
    elif data_type.casefold() == 'cwatm'.casefold():
        # Load
        data_ds = geo.load_any(data, decode_coords = 'all', decode_times = False)
        
        print("\nFormatting data...")
        # Add CRS
        data_epsg = 2154 # Lambert 93
        crs_suffix = ''
        if include_crs:
            data_ds.rio.write_crs(data_epsg, inplace = True)
            print(f'   _ Coordinates Reference System (epsg:{data_epsg}) included.')
        else:
            print(f'   _ Coordinates Reference System not included. {data_epsg} has to be manually specified in QGIS')
            crs_suffix = 'nocrs'
    
    
    # ---- NetCDF de la DRIAS-Climat 2020 et de la DRIAS-Eau 2021
    # Données SAFRAN (tas, prtot, rayonnement, vent... ) "DRIAS-2020"
    # ainsi que : 
    # Données SURFEX (evapc, drainc, runoffc, swe, swi...) "EXPLORE2-SIM2 2021"
    # ------------------------------------------------------------
    if data_type.replace(" ", "").casefold() in ['drias2020', 'drias-climat2020',
                                'sim2021', 'drias-eau2021']:         
        # Load
        data_ds = geo.load_any(decode_coords = 'all')
        
        print("\nFormating data...")
        # Create X and Y coordinates if necessary, from i and j
        list_var_lowcase = [v.casefold() for v in list(data_ds.coords) + list(data_ds.data_vars)]
        if 'x' not in list_var_lowcase:
            data_ds = data_ds.assign_coords(
                X = ('i', 52000 + data_ds.i.values*8000))
            print("   _ X values created from i")
        if 'y' not in list_var_lowcase:
            data_ds = data_ds.assign_coords(
                Y = ('j', 1609000 + data_ds.j.values*8000))
            print("   _ Y values created from j")
        # Replace X and Y as coordinates, and rename them
        data_ds = data_ds.swap_dims(i = 'X', j = 'Y')
        print("   _ Coordinates i and j replaced with X and Y")
        data_ds = data_ds.rename(X = 'x', Y = 'y')
        print("   _ Coordinates renamed as lowcase x and y [optional]")
        # Get main variable
        var = geo.main_var(data_ds)
        print(f"   _ Main variables are: {', '.join(var)}")
        # Ensure that lat, lon, i and j will be further loaded by xarray as coords
        data_ds[var].attrs['coordinates'] = 'x y i j lat lon'
        print("   _ x, y, i, j, lat, lon ensured to be read as coordinates")

# ============== USELESS ======================================================
#         # Reorder data, to ensure QGIS Mesh detects the correct data set   
#         data_ds = data_ds[[var, 'x', 'y', 'time']]
#         print("   _ Data reordered [safety]")
# =============================================================================
# ============== USELESS ======================================================
#         # To avoid conflicts with missing values
#         data_ds[var].encoding.pop('missing_value')
#         data_ds['lat'].encoding.pop('missing_value')
#         # data_ds['lat'].encoding['_FillValue'] = np.nan
#         data_ds['lon'].encoding.pop('missing_value')
#         # data_ds['lon'].encoding['_FillValue'] = np.nan
# =============================================================================
        
        # Add standard attributes for coordinates (mandatory for QGIS to correctly read data)
        data_ds.x.attrs = {'standard_name': 'projection_x_coordinate',
                            'long_name': 'x coordinate of projection',
                            'units': 'Meter'}
        data_ds.y.attrs = {'standard_name': 'projection_y_coordinate',
                            'long_name': 'y coordinate of projection',
                            'units': 'Meter'}
        print("   _ Standard attributes added for coordinates x and y")
        
        # Add CRS
        data_epsg = 27572 # Lambert zone II
        crs_suffix = ''
        if include_crs:
            data_ds.rio.write_crs(data_epsg, inplace = True)
            print(f'   _ Coordinates Reference System (epsg:{data_epsg}) included. (NB: This might alter Panoply georeferenced vizualisation)')
        else:
            print(f'   _ Coordinates Reference System not included. {data_epsg} has to be manually specified in QGIS')
            crs_suffix = 'nocrs'
         # Incompatibilité QGIS - Panoply :
         # Pour une raison inconnue, l'inclusion du CRS 27572 ("Lambert 
         # Zone II" / "NTF (Paris)" pose problème pour le géo-référencement
         # dans Panoply (c'est comme si Panoply prenait {lat = 0 ; lon = 0} 
         # comme origine de la projection). Sans 'spatial_ref' incluse dans le
         # netCDF, Panoply géo-référence correctement les données, probablement
         # en utilisant directement les variables 'lat' et 'lon'.
      
        
    # ---- NetCDF de la DRIAS-Climat 2022 
    # Données SAFRAN (tas, prtot, rayonnement, vent... ) "EXPLORE2-Climat 2022" 
    # -------------------------------------------------------------------------
    elif data_type.replace(" ", "").casefold() in ['drias2022', 'climat2022', 'drias-climat2022']:
        # Load
        data_ds = geo.load_any(data, decode_cf = False)

        print("\nFormating data...")
        # Correcting the spatial_ref
# =============================================================================
#         data_ds['LambertParisII'] = xr.DataArray(
#             data = np.array(-2147220352.0),
#             coords = {'LambertParisII': -2147220352.0},
#             attrs = {'grid_mapping_name': 'lambert_conformal_conic_1SP',
#                      'latitude_of_origin': 52.0,
#                      'central_meridian': 0.0,
#                      'false_easting': 600000.0,
#                      'false_northing': 2200000.0,
#                      'epsg': 27572,
#                      'references': 'http://www.umr-cnrm.fr/spip.php?article125&lang=en'}) 
#         crs_suffix = 'georef'
# =============================================================================
        data_epsg = 27572 # Lambert zone II
        if include_crs:
            # data_ds = data_ds.drop('LambertParisII')
            # data_ds.rio.write_crs(f'epsg:{data_epsg}', inplace = True)
            data_ds = geo.standard_grid_mapping(data_ds, data_epsg)
            print(f'   _ Coordinates Reference System (epsg:{data_epsg}) included. (NB: This might alter Panoply georeferenced vizualisation)')
            crs_suffix = ''
        else:
            print(f'   _ Coordinates Reference System not included. {data_epsg} has to be manually specified in QGIS')
            crs_suffix = 'nocrs'
        # Get main variable
        var = geo.main_var(data_ds)
        print(f"   _ Main variable are: {', '.join(var)}")
        # Ensure that lat, and lon will be further loaded by xarray as coords
        data_ds[var].encoding['coordinates'] = 'x y lat lon'
        if 'coordinates' in data_ds[var].attrs:
            data_ds[var].attrs.pop('coordinates')
        data_ds.lat.encoding['grid_mapping'] = data_ds[var].encoding['grid_mapping']
        data_ds.lon.encoding['grid_mapping'] = data_ds[var].encoding['grid_mapping']
        print("   _ x, y, lat, lon ensured to be read as coordinates [safety]")
        # Remove grid_mapping in attributes (it is already in encoding)
        if 'grid_mapping' in data_ds[var].attrs:
            data_ds[var].attrs.pop('grid_mapping')
    
    
    # ---- NetCDF de la DRIAS-Eau 2024 
    # Données SURFEX (evapc, drainc, runoffc, swe, swi...) "EXPLORE2-SIM2 2024" 
    # -------------------------------------------------------------------------
    elif data_type.replace(" ", "").replace("-", "").casefold() in [
            'sim2024', 'driaseau2024']: 
        # Load
        data_ds = geo.load_any(data, decode_cf = False)

        print("\nFormating data...")
        # Correcting the spatial_ref
# =============================================================================
#         data_ds['LambertParisII'] = xr.DataArray(
#             data = np.array(-2147220352.0),
#             coords = {'LambertParisII': -2147220352.0},
#             attrs = {'grid_mapping_name': 'lambert_conformal_conic_1SP',
#                      'latitude_of_origin': 52.0,
#                      'central_meridian': 0.0,
#                      'false_easting': 600000.0,
#                      'false_northing': 2200000.0,
#                      'epsg': 27572,
#                      'references': 'http://www.umr-cnrm.fr/spip.php?article125&lang=en'}) 
#         crs_suffix = ''
# =============================================================================
        data_epsg = 27572 # Lambert zone II
        if include_crs:
            # if ('LambertParisII' in data_ds.coords) | ('LambertParisII' in data_ds.data_vars):
            #     data_ds = data_ds.drop('LambertParisII')
            # data_ds.rio.write_crs(data_epsg, inplace = True)
            data_ds = geo.standard_grid_mapping(data_ds, data_epsg)
            print(f'   _ Coordinates Reference System (epsg:{data_epsg}) included. (NB: This might alter Panoply georeferenced vizualisation)')
            crs_suffix = ''
        else:
            print(f'   _ Coordinates Reference System not included. {data_epsg} has to be manually specified in QGIS')
            crs_suffix = 'nocrs'
        
        # Create X and Y coordinates if necessary, from i and j
        list_var_lowcase = [v.casefold() for v in list(data_ds.coords) + list(data_ds.data_vars)]
        data_ds = data_ds.assign_coords(
            X = ('x', 52000 + data_ds.x.values*8000))
        print("   _ X values corrected from erroneous x")
        data_ds = data_ds.assign_coords(
            Y = ('y', 1609000 + data_ds.y.values*8000))
        print("   _ Y values corrected from erroneous y")
        # Replace X and Y as coordinates, and rename them
        data_ds = data_ds.swap_dims(x = 'X', y = 'Y')
        print("   _ Coordinates x and y replaced with X and Y")
        data_ds = data_ds.drop(['x', 'y'])
        print("   _ Previous coordinates x and y removed")
        data_ds = data_ds.rename(X = 'x', Y = 'y')
        print("   _ Coordinates renamed as lowcase x and y [optional]")
        # Get main variable
        var = geo.main_var(data_ds)
        print(f"   _ Main variable are: {', '.join(var)}")
        
        # Ensure that lat, and lon will be further loaded by xarray as coords
        data_ds[var].encoding['coordinates'] = 'x y lat lon'
        if 'coordinates' in data_ds[var].attrs:
            data_ds[var].attrs.pop('coordinates')
        # Reporting grid_mapping to coords/vars that should not be displayed in QGIS:
        for c in ['lat', 'lon']: 
            if (c in data_ds.coords) | (c in data_ds.data_vars):
                data_ds[c].encoding['grid_mapping'] = data_ds[var].encoding['grid_mapping']
        print("   _ x, y, lat, lon ensured to be read as coordinates [safety]")
       # ======== USELESS ============================================================
       #         for c in ['lat', 'lon', 'time_bnds']:
       #             if c in data_ds.data_vars:
       #                 data_ds = data_ds.set_coords([c])
       # =============================================================================
        
       # Remove grid_mapping in attributes (it is already in encoding)
        if 'grid_mapping' in data_ds[var].attrs:
            data_ds[var].attrs.pop('grid_mapping')
        
# ============== USELESS ======================================================
#         # Reorder data, to ensure QGIS Mesh detects the correct data set   
#         data_ds = data_ds[[var, 'x', 'y', 'time']]
#         print("   _ Data reordered [safety]")
# =============================================================================
# ============== USELESS ======================================================
#         # To avoid conflicts with missing values
#         data_ds[var].encoding.pop('missing_value')
#         data_ds['lat'].encoding.pop('missing_value')
#         # data_ds['lat'].encoding['_FillValue'] = np.nan
#         data_ds['lon'].encoding.pop('missing_value')
#         # data_ds['lon'].encoding['_FillValue'] = np.nan
# =============================================================================
        
        # Add standard attributes for coordinates (mandatory for QGIS to correctly read data)
        data_ds.x.attrs = {'standard_name': 'projection_x_coordinate',
                            'long_name': 'x coordinate of projection',
                            'units': 'metre'}
        data_ds.y.attrs = {'standard_name': 'projection_y_coordinate',
                            'long_name': 'y coordinate of projection',
                            'units': 'metre'}
        print("   _ Standard attributes added for coordintes x and y")


    # ---- Autres fichiers ou variables
    # Inclusion du SCR
    # ------------------
# =============================================================================
#     elif data_type.casefold() in ['autre', 'other']:
# =============================================================================
    else:
        # Load
        data_ds = geo.load_any(data, decode_times = True, decode_coords = 'all')
        
        x_var, y_var = geo.main_space_dims(data_ds)
# ====== old standard time handling ===========================================
#         time_coord = main_time_dims(data_ds)
# =============================================================================
        
        # Standardize spatial coords
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
        
        # Standardize time coord
# ====== old standard time handling ===========================================
#         if len(time_coord) == 1:
#             data_ds = data_ds.rename({time_coord: 'time'})
# =============================================================================
        data_ds = geo.use_standard_time(data_ds, **time_kwargs)
        
        if isinstance(data_ds, gpd.GeoDataFrame):
            print("\nFormatting data...")
            # Add CRS
            crs_suffix = ''
            if include_crs:
                if crs is not None:
                    data_epsg = crs
                    data_ds.set_crs(crs = crs, 
                                    inplace = True, 
                                    allow_override = True)
                    # data_ds = standard_grid_mapping(data_ds, crs)
                    print(f'   _ Coordinates Reference System (epsg:{crs.to_epsg()}) included.')
                else:
                    print("   _ Warning: No `crs` argument was passed")
            else:
                print('   _ Coordinates Reference System not included.')
                crs_suffix = 'nocrs'
        
        elif isinstance(data_ds, xr.Dataset):        
            print("\nFormatting data...")
            # Add CRS
            crs_suffix = ''
            if include_crs:
                if crs is not None:
                    data_ds.rio.write_crs(crs, inplace = True)
                    print(f'   _ Coordinates Reference System (epsg:{crs.to_epsg()}) included.')
                else:
                    print("   _ Warning: No crs argument was passed")
            else:
                print('   _ Coordinates Reference System not included.')
                crs_suffix = 'nocrs'
            
            # Add standard attributes for coordinates (mandatory for QGIS to correctly read data)
            if ('x' in list(data_ds.coords)) & ('y' in list(data_ds.coords)):
                data_ds.x.attrs = {'standard_name': 'projection_x_coordinate',
                                    'long_name': 'x coordinate of projection',
                                    'units': 'metre'}
                data_ds.y.attrs = {'standard_name': 'projection_y_coordinate',
                                    'long_name': 'y coordinate of projection',
                                    'units': 'metre'}
                print("   _ Standard attributes added for coordinates x and y")
            elif ('lon' in list(data_ds.coords)) & ('lat' in list(data_ds.coords)):
                data_ds.lon.attrs = {'standard_name': 'longitude',
                                     'long_name': 'longitude',
                                     'units': 'degrees_east'}
                data_ds.lat.attrs = {'standard_name': 'latitude',
                                     'long_name': 'latitude',
                                     'units': 'degrees_north'}
                print("   _ Standard attributes added for coordinates lat and lon")


    # ---- General changes
    var_list = geo.main_var(data_ds)
    for var in var_list:
        for optional_attrs in ['AREA_OR_POINT', 'STATISTICS_MAXIMUM',
                               'STATISTICS_MEAN', 'STATISTICS_MINIMUM',
                               'STATISTICS_STDDEV', 'STATISTICS_VALID_PERCENT']:
            if optional_attrs in data_ds[var].attrs:
                data_ds[var].attrs.pop(optional_attrs)
    
    # ---- Export
    # ---------
    if export_opt == True:
        print('\nExporting...')
        # Output filepath
        if isinstance(data, (str, Path)):
            (folder_name, _basename) = os.path.split(data)
            (file_name, file_extension) = os.path.splitext(_basename)
            output_file = os.path.join(folder_name, f"{'_'.join([file_name, 'georef', crs_suffix])}{file_extension}")
        else:
            print("   _ As data input is not a file, the result is exported to a standard directory")
            output_file = os.path.join(os.getcwd(), f"{'_'.join(['data', 'georef', crs_suffix])}.nc")
        
        # Export
        geo.export(data_ds, output_file)
        
        
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


#%% FILE MANAGEMENT
###############################################################################

# Shorten names
def shortname(data, data_type, ext = 'nc'):
    """
    ext : str
        
    """
    
    if ext is not None:
        ext = ext.replace('.', '')
    
    if os.path.isfile(data):
        root_folder = os.path.split(data)[0]
    else:
        root_folder = data
        
    if os.path.isdir(data):
        content_list = [os.path.join(data, f)
                     for f in os.listdir(data)]
    else:
        content_list = [data]
    
    # ---- DRIAS-Eau 2024 Indicateurs (netcdf)
    # Indicateurs SAFRAN (SWIAV, SSWI-3...) "EXPLORE2-SIM2 2024" 
    if data_type.casefold().replace(' ', '').replace('-', '') in [
            'indicateursim2024', 'indicateurssim2024','indicateurdriaseau2024',
            'indicateursdriaseau2024']:
        
        folder_pattern = re.compile('Indicateurs_(.*Annuel|.*Saisonnier)_(.*)_MF_ADAMONT_(.*)_SIM2')
        
        for elem in content_list:
            # Raccourcir le nom
            if os.path.isdir(elem):
                res = folder_pattern.findall(elem)
                if len(res) > 0:
                    outpath = '_'.join(res[0])
                    os.rename(elem, os.path.join(root_folder, outpath))
                    
    # ---- Remove custom added date-time
    elif data_type.casefold().replace(' ', '').replace('-', '') in [
            'removedate']:
        # This option enables to remove the '2024-11-06_12h53'-like suffixes
        # that I have added to file names (in order to trace the date of creation,
        # but it is unnecessary and causes file names to be too long for Windows).
        
        datetime_pattern = re.compile('(.*)_\d{4,4}-\d{2,2}-\d{2,2}_\d{2,2}h\d{2,2}.'+f'{ext}')
        
        for elem in content_list:
            if len(datetime_pattern.findall(elem)) > 0:
                os.rename(os.path.join(root_folder, elem), 
                          os.path.join(root_folder, datetime_pattern.findall(elem)[0] + f'.{ext}'))
            elif os.path.isdir(os.path.join(root_folder, elem)):
                shortname(os.path.join(root_folder, elem), data_type = data_type, ext = ext)
        

###############################################################################
def remove_double(data_folder, data_type):
    """
    The data downloaded from DRIAS website contains *some* data sets 
    available for different periods (it is the same data, but one version
    goes from 1950 to 2005, and another from 1970 to 2005). For some models,
    there are no duplicate of that sort.
    These duplicates are unnecessary. This script moves these duplicates to a
    subfolder named "doublons".
    
    Example
    -------
    folder_list = [r"Eau-SWIAV_Saisonnier_EXPLORE2-2024_historical", 
                   r"Eau-SWIAV_Saisonnier_EXPLORE2-2024_rcp45", 
                   r"Eau-SWIAV_Saisonnier_EXPLORE2-2024_rcp85"]
    root_folder = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\DRIAS\DRIAS-Eau\EXPLORE2-SIM2 2024\Pays Basque\Indicateurs"
    
    for folder in folder_list:
        base_folder = os.path.join(root_folder, folder)
        subfolder_list = [os.path.join(base_folder, f)
                     for f in os.listdir(base_folder) 
                     if os.path.isdir(os.path.join(base_folder, f))]
        for subfolder in subfolder_list:
            gc.remove_double(subfolder, data_type = "indicateurs drias eau 2024")
    """
    
    # ---- DRIAS-Eau 2024 Indicateurs (netcdf)
    # Indicateurs SAFRAN (SWIAV, SSWI-3...) "EXPLORE2-SIM2 2024" 
    if data_type.casefold().replace(' ', '').replace('-', '') in [
            'indicateursim2024', 'indicateurssim2024','indicateurdriaseau2024',
            'indicateursdriaseau2024']:
                
        content_list = [os.path.join(data_folder, f)
                     for f in os.listdir(data_folder) 
                     if (os.path.isfile(os.path.join(data_folder, f)) \
                         & (os.path.splitext(os.path.join(data_folder, f))[-1] == '.nc'))]
        
        model_pattern = re.compile("(.*)_(\d{4,4})-(\d{4,4})_(historical|rcp45|rcp85)_(.*)_(SIM2.*)")
        model_dict = {}
        
        # List all models
        for elem in content_list:
            filename = os.path.split(elem)[-1]
            var, date, datef, scenario, model, creation_date = model_pattern.findall(filename)[0]
            date = int(date)
            if model in model_dict:
                model_dict[model].append(date)
            else:
                model_dict[model] = [date]
        
        # Move duplicates
        if not os.path.exists(os.path.join(data_folder, "doublons")):
            os.makedirs(os.path.join(data_folder, "doublons"))
        
        for model in model_dict:
            if len(model_dict[model]) > 1:
                filename = '_'.join([var, f"{max(model_dict[model])}-{datef}", scenario, model, creation_date])
                os.rename(
                    os.path.join(data_folder, filename),
                    os.path.join(data_folder, 'doublons', filename)
                    )


###############################################################################
def name_xml_attributes(*, output_file, fields):  
    band_str_open = '\t<PAMRasterBand band="{}">\t\t<Description>{}'
    band_str_close = '</Description>\t</PAMRasterBand>\n</PAMDataset>'
    base_str = ''.join(['<PAMDataset>\n',
                       '\t<Metadata>\n',
                       '\t\t<MDI key="CRS">epsg:27572</MDI>\n',
                       '\t</Metadata>\n',
                       len(fields) * (band_str_open + band_str_close)])
    
    band_ids = [str(item) for item in list(range(1, len(fields)+1))]
    # Create a string list of indices: '1', '2', '3' ...
    addstr = [item for pair in zip(band_ids, fields) for item in pair]
    # Create a list alternating indices and names: '1', 'CLDC', '2', 'T2M' ...
    
    file_object = open(output_file + '.aux.xml', 'w')
    file_object.write(base_str.format(*addstr))
    file_object.close()


#%% PORTAL STANDARDIZATION
def standardize_data(data, data_name, **kwargs):
    
    # ---- Données topographiques
    #%%% IGN BD ALTI 25m (DEM)
    if data_name.casefold().replace(' ', '') in ["alti", "bdalti", "ignalti"]:
        return bdalti(data)
    
    # ---- Données climatiques
    #%%% SIM2 (csv to netcdf)
    # Données SAFRAN-ISBA (T, PRELIQ, ETP, EVAPC, SWI, RUNC... ) de réanalyse historique "SIM2" 
    elif data_name.replace(" ", "").casefold() in ['sim2']:
        return sim2(data)
    
    #%%% DRIAS-Climat 2022 (netcdf)
    # Données SAFRAN (tas, prtot, rayonnement, vent... ) "EXPLORE2-Climat 2022" 
    elif data_name.replace(" ", "").casefold() in ['drias2022', 'climat2022', 'drias-climat2022']:
        return explore2climat(data)
    
    #%%% DRIAS-Eau 2024 (netcdf)
    # Données SURFEX (evapc, drainc, runoffc, swe, swi...) "EXPLORE2-SIM2 2024" 
    elif data_name.replace(" ", "").casefold() in ['sim2024', 'drias-eau2024',
                                                   'driaseau2024']:
        return explore2eau(data)
    
    #%%% * DRIAS
    elif data_name.casefold() in ["drias"]:
        return drias(data)
    
    #%%% C3S seasonal forecast
    # https://cds.climate.copernicus.eu/datasets/seasonal-original-single-levels?tab=overview
    elif data_name.casefold() in ["c3s"]:
        return c3s(data)
    
    #%%% ERA5
    elif data_name.casefold().replace('-', '') in ["era5", "era5land", "era"]:
        return era5(data)
    
    # ---- Données d'usage de l'eau
    #%%% Water withdrawals BNPE
    elif data_name.casefold() in ['bnpe']:
        return bnpe(data, **kwargs)
    
    # ---- Données de débit
    #%%% Hydrométrie eaufrance
    elif data_name.casefold() in ['hydrometrie', 'hydrométrie', 'hydrometry',
                                  'débit', 'debit', 'discharge']:
        return hydrometry(data, **kwargs)
    
    # ---- Données d'occupation des sols
    #%%% ° Crop coefficients, version "better"
    elif data_name.casefold() in ['crop', 'crop coeff', 'crop coefficient']:
        return cropcoeff(data)
    
    #%%% ° CES OSO
    elif data_name.casefold() in ['ces oso', 'oso', 'ces']:
        return cesoso(data)
    
    #%%% ° CORINE Land Cover
    elif data_name.casefold() in ["corine", "cld", "corine land cover"]:
        return corine(data)
    
    #%%% ° Observatoire botanique de Brest (2018-2019)
    elif data_name.casefold() in ["observatoire", "obb"]:
        return obb(data)
    
    # ---- Données de sol
    #%%% ° Soil depth UCS Bretagne
    elif data_name.casefold().replace(' ', '').replace('-', '').replace('_', '') in ["ucsbretagne", "ucsbzh", "ucsppbzh"]:
        return ucsbretagne(data)

#%% STANDARDIZE FUNCTIONS
# =============================================================================
# def convert_to_cwatm(data, data_type, reso_m = None, EPSG_out=None, 
#                         EPSG_in = None, coords_extent = 'Bretagne'):
# # =============================================================================
# #     previously prepare_CWatM_input(*, data, data_type, reso_m = None, 
# #                                    EPSG_out, EPSG_in = None, 
# #                                    coords_extent = 'Bretagne'):
# # =============================================================================
# 
#     
# # ====== Ancienne version du script ===========================================
# #     (input_folder, _file_name) = os.path.split(data)
# #     (file_name, file_extension) = os.path.splitext(_file_name)
# # =============================================================================
# =============================================================================

def era5(data):

    # ---- Merge files
    # Usually ERA5-Land files are too big to be downloaded for the full period.
    # Here the first step is to merge the available ERA5.nc files.
    merged_ds = geo.merge_data(data)
    
    var_list = geo.main_var(data)
    
    # ---- Convert hourly to daily
    print("   _ Converting hourly to daily...")
    modelist = { # to differentiate extensive from intensive quantities
        'ro': 'sum',
        'sro': 'sum',
        'ssro': 'sum',
        'evavt': 'sum',
        'evatc': 'sum',
        'pev': 'sum',
        'tp': 'sum',
        'fal': 'mean',
        'rh': 'mean',
        'ssrd': 'mean',
        'strd': 'mean',
        'sp': 'mean',
        't2m': 'mean',
        'd2m': 'mean',
        'u10': 'mean',
        'v10': 'mean',
        'wind_speed': 'mean'}
    
    daily_ds = xr.Dataset()
    
    for var in var_list:
        daily_ds[var] = geo.hourly_to_daily(merged_ds, mode = modelist[var])
        
        # ---- Convert units when needed
        if var in ['ssrd', 'strd']:
            print("   _ Converting radiation units from J/m²/h to W/m²")
            daily_ds[var] = convert_downwards_radiation(daily_ds[var])
        
        elif var == 'pev':
            print("   _ Converting negative potential evapotranspiration to positive")
            # Backup of attributes and encodings
            attrs = daily_ds[var].attrs.copy()
            encod = daily_ds[var].encoding.copy()
            
            daily_ds[var] = daily_ds[var]*-1
            
            # Transferring attributes and encodings
            daily_ds[var].encoding = encod
            daily_ds[var].attrs = attrs
            
            # Case of packing
            if ('scale_factor' in daily_ds[var].encoding) | ('add_offset' in daily_ds[var].encoding):
                # Packing (lossy compression) induces a loss of precision of 
                # apprx. 1/1000 of unit, for a quantity with an interval of 150 
                # units. The packing is initially used in some original ERA5-Land data.
                print("      . Correcting packing encodings...")
                daily_ds[var].encoding['add_offset'] = daily_ds[var].encoding['add_offset']*-1

    
    return daily_ds
        

    
def bdalti(data,
           *, to_file = False):
    """
    Standardize the DEM data from IGN's ALTI Database (https://geoservices.ign.fr/bdalti):
    
    - merge tiles
    - georeference (embed CRS = 2154, standardize `_FillValue`, `grid_mapping` and `time`)
    - replace nodata values (-99999.0) with np.nan
    

    Parameters
    ----------
    data : (list of) str or pathlib.Path, or variable (xarray.Dataset or xarray.DataArray)
        ``data`` is usually the folder containing all the raw BDALTI tiles downloaded from
        IGN website. It can also be a list of filepaths or xarray variables. 
        It can also be a single filepath or xarray variable.
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to the same location as ``data``, with the name 'BDALTIV2_stz.tif'.
        If ``to_file`` is a path, the resulting dataset will be exported to this specified filepath.

    Returns
    -------
    data_ds : xarray.Dataset
        Standardized DEM.
    If ``to_file`` argument is used, the standardized DEM is exported to a file. 
    If ``to_file = True``, the standardized DEM is exported to the GeoTIFF file
    'BDALTIV2_stz.tif'.
    
    Examples
    ---------
    >>> stzfr.bdalti(
        r"E:\Inputs\DEM\IGN\BDALTIV2_2-0_25M_ASC_LAMB93-IGN69", 
        to_file = True
        )
    Exporting...
       _ Success: The data has been exported to the file 'E:\Inputs\DEM\IGN\BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_PAYS_BASQUE\BDALTIV2_stz.tif'
    <xarray.Dataset> Size: 252MB
    Dimensions:      (x: 7000, y: 9000)
    Coordinates:
      * x            (x) float64 56kB 3e+05 3e+05 3e+05 ... 4.75e+05 4.75e+05
      * y            (y) float64 72kB 6.4e+06 6.4e+06 ... 6.175e+06 6.175e+06
        spatial_ref  int64 8B 0
    Data variables:
        elev         (y, x) float32 252MB nan nan nan nan nan ... nan nan nan nan
    

    """
    
    # ---- Merge tiles (if relevant)
    data_ds = geo.merge_data(data, extension = '.asc')
    
    # ---- Rename the main variable (ASCII files do not have a variable name)
    # (in case file is exported into a netCDF)
    if isinstance(data_ds, xr.Dataset):
        main_var = geo.main_vars(data_ds)[0]
        data_ds = data_ds.rename({main_var: 'elev'})
    elif isinstance(data_ds, xr.DataArray):
        data_ds = data_ds.rename('elev')
        data_ds = data_ds.to_dataset() # convert into xarray.Dataset
    else:
        print(f"Error: BD ALTI data is not supposed to be a {type(data_ds)}")
        return
    
    # ---- Georeference
    data_ds = geo.georef(data_ds, crs = 2154)
    
    # ---- Replace nodata values (-99999.0) with NaN
# =============================================================================
#     encod = data_ds['elev'].encoding # store encodings (_FillValue, compression...)
#     data_ds['elev'] = data_ds['elev'].where(data_ds['elev'] != -99999) # replace nodata
#     data_ds['elev'].encoding = encod # transfer encodings
# =============================================================================
    data_ds['elev'].encoding['_FillValue'] = np.nan
    
    # ---- Export
    if to_file == True:
        if isinstance(data, (str, Path)):
            print('\nExporting...')
            # Determine the filename
            if os.path.isdir(data): 
# =============================================================================
#                 data_folder, filelist = geo.get_filelist(data, extension = '.asc')
#                 stem = os.path.join(data_folder, filelist[0])
# =============================================================================
                stem = os.path.join(data, 'BDALTIV2.tif')
            elif os.path.isfile(data):
                stem = data
            
            # Export
            export_filepath = os.path.splitext(stem)[0] + "_stz" + ".tif"
            geo.export(data_ds, export_filepath)
            
        else:
            print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
        
    elif isinstance(to_file, (str, Path)):
        print('\nExporting...')
        geo.export(data_ds, to_file)

    # ---- Returns results as a GEOP4TH variable (xr.Dataset)
    return data_ds


def sim2(data,
         *, to_file = False,
         merge_csv = True):
    r"""
    Standardizes MeteoFrance "SIM2" datasets downloaded as .csv files from data.gouv website
    (https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-quotidienne)
    into standard netCDF files by:
    
    - merge all available .csv files
    - add a total_precipitation variable
    - convert .csv files into xarray.Datasets variables, which can then be 
      exported to netCDF files
    - standardize the x and y values
    - embedd the CRS (epsg:27572)
    - standardize netCDF names and attributes (coordinates, grid_mapping)
    - standardize units

    Parameters
    ----------
    data : (list of) str or pathlib.Path, or variable (pandas.Dataframe)
        ``data`` is usually the folder containing all the raw SIM2 tiles downloaded from
        the data.gouv website [https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-quotidienne]. 
        It can also be a list of filepaths or pandas variables. 
        It can also be a single filepath or pandas variable.
    to_file : bool or path (str or pathlib.Path), default False
        If True and if ``data`` is a path (str or pathlib.Path), the resulting
        dataset will be exported to the same location as ``data``, with the name 'SIM2_stz.tif'.
        If ``to_file`` is a path, the resulting dataset will be exported to this specified filepath.
    merge_csv : bool, default True
        Option to avoid memory issues (processing is much slower)

    Returns
    -------
    data_ds : xarray.Dataset
        Standardized meteorological data.
    If ``to_file`` argument is used, the standardized DEM is exported to a file. 
    If ``to_file = True``, the standardized DEM is exported to the GeoTIFF file
    'SIM2_stz.tif'.
    
    Examples
    --------
    >>> stzfr.sim2(
        r"E:\Inputs\Climate\SIM2\csv", 
        to_file = True
        )
    Exporting...
       _ Success: The data has been exported to the file 'E:\Inputs\Climate\SIM2\csv\SIM2_stz.nc'
    <xarray.Dataset> Size: 2GB
    Dimensions:        (time: 518, y: 134, x: 143)
    Coordinates:
      * time           (time) datetime64[ns] 4kB 1958-08-01 ... 2025-08-20
      * y              (y) int64 1kB 1617000 1625000 1633000 ... 2673000 2681000
      * x              (x) int64 1kB 60000 68000 76000 ... 1180000 1188000 1196000
        spatial_ref    int64 8B 0
    Data variables: (12/26)
        PRENEI_Q       (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
        PRELIQ_Q       (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
        T_Q            (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
        FF_Q           (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
        Q_Q            (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
        DLI_Q          (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
                ...
        ECOULEMENT_Q   (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
        WG_RACINE_Q    (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
        WGI_RACINE_Q   (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
        TINF_H_Q       (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
        TSUP_H_Q       (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
        PRETOT_Q       (time, y, x) float64 79MB nan nan nan nan ... nan nan nan nan
    """
    
# =============================================================================
#     # Needed columns
#     usecols = ['LAMBX', 'LAMBY', 'DATE']
# =============================================================================

    # Units and long names (from liste_parametres.odt https://www.data.gouv.fr/fr/datasets/r/d1ffaf5e-7d15-4fb5-a34c-f76aaf417b46)
    units_by_var = {
                 'PRENEI_Q': ['mm', 'Précipitations solides (cumul quotidien 06-06 UTC)'], 
                 'PRELIQ_Q': ['mm', 'Précipitations liquides (cumul quotidien 06-06 UTC)'], 
                 'T_Q': ['°C','Température (moyenne quotidienne)'], 
                 'FF_Q': ['m/s', 'Vitesse du vent (moyenne quotidienne)'], 
                 'Q_Q': ['g/kg','Humidité spécifique (moyenne quotidienne)'], 
                 'DLI_Q': ['J/cm2', 'Rayonnement atmosphérique (cumul quotidien)'],
                 'SSI_Q': ['J/cm2', 'Rayonnement visible (cumul quotidien)'], 
                 'HU_Q': ['%', 'Humidité relative (moyenne quotidienne)'], 
                 'EVAP_Q': ['mm', 'Evapotranspiration réelle (cumul quotidien 06-06 UTC)'], 
                 'ETP_Q': ['mm', 'Evapotranspiration potentielle (formule de Penman-Monteith)'], 
                 'PE_Q': ['mm', 'Pluies efficaces (cumul quotidien)'], 
                 'SWI_Q': ['%', "Indice d'humidité des sols (moyenne quotidienne 06-06 UTC)"],
                 'DRAINC_Q': ['mm', 'Drainage (cumul quotidien 06-06 UTC)'], 
                 'RUNC_Q': ['mm', 'Ruissellement (cumul quotidien 06-06 UTC)'], 
                 'RESR_NEIGE_Q': ['mm', 'Equivalent en eau du manteau neigeux (moyenne quotidienne 06-06 UTC)'], 
                 'RESR_NEIGE6_Q': ['mm', 'Equivalent en eau du manteau neigeux à 06 UTC'], 
                 'HTEURNEIGE_Q': ['m', 'Epaisseur du manteau neigeux (moyenne quotidienne 06-06 UTC)'], 
                 'HTEURNEIGE6_Q': ['m', 'Epaisseur du manteau à 06 UTC'], 
                 'HTEURNEIGEX_Q': ['m', 'Epaisseur du manteau neigeux maximum au cours de la journée'], 
                 'SNOW_FRAC_Q': ['%', 'Fraction de maille recouverte par la neige (moyenne quotidienne 06-06 UTC)'], 
                 'ECOULEMENT_Q': ['mm', 'Ecoulement à la base du manteau neigeux'], 
                 'WG_RACINE_Q': ['mm','Contenu en eau liquide dans la couche racinaire à 06 UTC'], 
                 'WGI_RACINE_Q': ['mm', 'Contenu en eau gelée dans la couche de racinaire à 06 UTC'], 
                 'TINF_H_Q': ['°C', 'Température minimale des 24 températures horaires'], 
                 'TSUP_H_Q': ['°C', 'Température maximale des 24 températures horaires'],
                 'PRETOT_Q': ['mm', 'Précipitations totales (cumul quotidien 06-06 UTC)'], 
                 }
    # NB: Cumulated values (day 1) are summed from 06:00 UTC (day 1) to 06:00 UTC (day 2)
    # Therefore, days correspond to Central Standard Time days.

    # ---- Merge tiles (if relevant)
    if isinstance(data, (str, Path)):
        _, filelist = geo.get_filelist(data, extension = '.csv')
        _, latest = geo.get_filelist(data, extension = '.csv', tag = 'latest')
        n_files = len(filelist) - len(latest)
        print(f"Merging SIM2 files requires a significant amount of RAM: {n_files*7 + 7}Go is advised")
        print("Otherwise, pass the argument `merge_csv = False` (slower but less memory errors)")
    
    if merge_csv:
        df = geo.merge_data(data, 
                            extension = '.csv',
                            sep = ';',
                            header=0, 
                            decimal='.',
                            parse_dates=['DATE'],
                            # date_format='%Y%m%d', # Not available before pandas 2.0.0
                            )
        
        datalist = [df]
    
    else:
        print("In this `merge_csv = False` mode, only the standardized data corresponding to the last input data will be returned")
        # Loading list  
        data_folder, filelist = geo.get_filelist(data, extension = '.csv')   
        datalist = [os.path.join(data_folder, f) for f in filelist]
    
    # ---- (re)Loading
    for d in datalist:
        df = geo.load_any(d, sep=';', 
                          header=0, decimal='.',
                          parse_dates=['DATE'],
                          # date_format='%Y%m%d', # Not available before pandas 2.0.0
                          )
    
        # ---- Formatting    
        df.rename(columns = {'LAMBX': 'x', 'LAMBY': 'y', 'DATE': 'time'}, inplace = True)
        df[['x', 'y']] = df[['x', 'y']]*100 # convert hm to m
        df.set_index(['time', 'y', 'x'], inplace = True)
        
        # Add a column total precipitations when possible
        if ('PRENEI_Q' in df.columns) & ('PRELIQ_Q' in df.columns):
            df['PRETOT_Q'] = df['PRENEI_Q'] + df['PRELIQ_Q']
            print("   New column added: PRETOT_Q = PRENEI_Q + PRELIQ_Q")
        
        # ---- Convert to xarray.Dataset and keep formatting
        data_ds = df.to_xarray()
        # Continuous axis
        data_ds = data_ds.reindex(x = range(data_ds.x.min().values, data_ds.x.max().values + 8000, 8000))
        data_ds = data_ds.reindex(y = range(data_ds.y.min().values, data_ds.y.max().values + 8000, 8000))
        # Include CRS and standardize attributes
        data_ds = geo.georef(data_ds, crs = 27572)
    
        # ---- Transferring metadata and standardizing units 
        print("Treating units and metadata...")
    
        for var in list(data_ds.data_vars): # batch_var: 
            # Include metadata
            data_ds[var].attrs = {
                # 'standard_name': var, # it is not standard according to CF Convention 
                # (https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html)
                'long_name': units_by_var[var][1],
                'units': units_by_var[var][0]}   
            
            # Standarize units
            if units_by_var[var][0] == 'mm': # mm -> m
                data_ds[var] = geo.convert_unit(data_ds[var], '/1000')
    # =============================================================================
    #         elif units_by_var[var][0] == '°C':
    #             data_ds[var] = convert_unit(data_ds[var], '+273.15')
    # =============================================================================
            elif units_by_var[var][0] == 'J/cm2': # J/cm² (daily sum) ->  W/m² 
                data_ds[var] = geo.convert_unit(data_ds[var], '/8.64')
                # *10**4 to convert cm² to m² ; and /86400 to convert J/d to W
        
            # ---- Export
            if to_file == True:
                if isinstance(data, (str, Path)):
                    print('\nExporting...')
                    # Determine the filename
                    if os.path.isdir(data): 
                        stem = os.path.join(data, f'{var}_SIM2.nc')
                    elif os.path.isfile(data):
                        stem = os.path.join(
                            os.path.split(data)[0], 
                            f'{var}_' + os.path.split(data)[-1])
                    
                    # Export
                    export_filepath = os.path.splitext(stem)[0] + "_stz" + ".nc"
                    geo.export(data_ds[[var]], export_filepath)
                    
                else:
                    print("Warning; `data` should be a path (str or pathlib.Path) for using `to_file=True`.")
                
            elif isinstance(to_file, (str, Path)):
                print('\nExporting...')
                geo.export(data_ds, 
                           os.path.join(
                               os.path.split(to_file)[0],
                               f'{var}_' + os.path.split(to_file)[-1])
                           )

    # ---- Returns results as a GEOP4TH variable (xr.Dataset)
    return data_ds
        
        

def explore2climat(data):
    # (netCDF)
    # Load
    data_ds = geo.load_any(data)
    
    # Get main variable
    var_list = geo.main_var(data_ds)
    print(f"   _ Main variable are: {', '.join(var_list)}")
    
    # Backup of attributes and encodings
    attrs_dict = {}
    encod_dict = {}
    for var in var_list:
        attrs_dict[var] = data_ds[var].attrs.copy()
        encod_dict[var] = data_ds[var].encoding.copy()
    
    # If it contains time_bnds (periods time)
    if ('time_bnds' in data_ds.coords) | ('time_bnds' in data_ds.data_vars):
        # The closing bounds is used for time coordinates
        time_attrs = data_ds['time'].attrs.copy()
        data_ds['time'] = data_ds.time_bnds.loc[{'bnds': 1}]
        data_ds['time'].attrs = time_attrs
        # time_bnds and bnds are removed
        data_ds = data_ds.drop_dims('bnds')
        print("   _ 'time_bnds' and 'bnds' removed")
    
    # Convert units
    for var in var_list:
        if var in ['evspsblpotAdjust', 'prsnAdjust', 'prtotAdjust']:
            data_ds[var] = data_ds[var]/1000*(60*60*24) # conversion from mm.s-1 to m.d-1
            data_ds[var].attrs = attrs_dict[var]
            data_ds[var].attrs['units'] = 'm.d-1'
            data_ds[var].encoding = encod_dict[var]
            print('   _ Units converted from mm/s to m/d')
    
# =============================================================================
#         # Remove compression (too long to load in QGIS otherwise)
#         data_ds[var].encoding['zlib'] = False
# =============================================================================
    
    return data_ds
        
    
def explore2eau(data):
    # Load
    xr_kwargs = {}
# =============================================================================
#         # Particular case for SSWI (grid_mapping is bugged)
#         sswi_pattern = re.compile('.*(SSWI).*')
#         if len(sswi_pattern.findall(data)) > 0:
#             xr_kwargs['drop_variables'] = 'LambertParisII'
# =============================================================================
    xr_kwargs['drop_variables'] = 'LambertParisII'
    
    data_ds = geo.load_any(data, **xr_kwargs)
    
    # Get main variable
    var_list = geo.main_var(data_ds)
    print(f"   _ Main variables are: {', '.join(var_list)}")
    
    # Backup of attributes and encodings
    attrs_dict = {}
    encod_dict = {}
    for var in var_list:
        attrs_dict[var] = data_ds[var].attrs.copy()
        encod_dict[var] = data_ds[var].encoding.copy()
    
    # If it contains time_bnds (periods time)
    if ('time_bnds' in data_ds.coords) | ('time_bnds' in data_ds.data_vars):
        # The closing bounds is used for time coordinates
        attributes = data_ds['time'].attrs.copy()
        data_ds['time'] = data_ds.time_bnds.loc[{'bnds': 1}]
        data_ds['time'].attrs = attributes
        # time_bnds and bnds are removed
        data_ds = data_ds.drop_dims('bnds')
        print("   _ 'time_bnds' and 'bnds' removed")
    
    # Convert units
    for var in var_list:
        if var in ['DRAINC', 'EVAPC', 'RUNOFFC']:
            data_ds[var] = data_ds[var]/1000 # conversion from mm.d-1 to m.d-1
            data_ds[var].attrs = attrs_dict[var]
            data_ds[var].attrs['units'] = 'm.d-1'
            data_ds[var].encoding = encod_dict[var]
            print('   _ Units converted from mm/d to m/d')
    
# =============================================================================
#         # Particular case for SSWI (_FillValue is wrong)
#         if ('missing_values' in data_ds[var].encoding) \
#             & ('_FillValue' in data_ds[var].encoding):
#             print(data_ds[var].encoding['missing_value'])
#             print(data_ds[var].encoding['_FillValue'])
# =============================================================================
# =============================================================================
#             data_ds[var].encoding['_FillValue'] = 999999
#             data_ds[var].encoding.pop('missing_value')
# =============================================================================
# ======= NOT ACCURATE ENOUGH =================================================
#         # Also, if SSWI and seasonal, dates should be shifted 45 days back
#         sswi_season_pattern = re.compile('.*(SSWI_seas).*')
#         if len(sswi_season_pattern.findall(data)) > 0:
#             encodings = data_ds['time'].encoding.copy()
#             data_ds['time'] = data_ds['time'] - pd.Timedelta(days = 45)
#             data_ds['time'].encoding = encodings
# =============================================================================
    
# =============================================================================
#         # Remove compression (too long to load in QGIS otherwise)
#         data_ds[var].encoding['zlib'] = False
# =============================================================================
    
    return data_ds
    

def c3s(data):
    data_ds = geo.load_any(data, 
                       # decode_times = True, 
                       # decode_coords = 'all'
                       )

    # Get main variable
    var = geo.main_var(data_ds)
    print(f"   _ Main variables are: {', '.join(var)}")
    # Backup of attributes and encodings
    attrs = dict()
    encod = dict()
    for v in var:
        attrs[v] = data_ds[v].attrs.copy()
        encod[v] = data_ds[v].encoding.copy()
    
    # Format time coordinate
    if ('forecast_reference_time' in data_ds.coords) | ('forecast_reference_time' in data_ds.data_vars):
        data_ds = data_ds.squeeze('forecast_reference_time').drop('forecast_reference_time')
    if ('forecast_period' in data_ds.coords) | ('forecast_period' in data_ds.data_vars):
        data_ds = data_ds.drop('forecast_period')
    
# =========== implemented in load_any =========================================
#         data_ds = use_standard_time(data_ds)
# =============================================================================
    
    return data_ds
        
    
def bnpe(data, extension = '.json'):
    data_folder, filelist = geo.get_filelist(data, extension = extension)
    folder_root = os.path.split(data_folder)[0]
    
    # Complete withdrawals timeseries by merging each file with water origin
    # =========
    # Retrieve infos ouvrages
    folder_ouvrage, filelist_ouvrage = geo.get_filelist(os.path.join(data, "ouvrages"), extension = extension)
    ouvrage_list = [geo.load_any(os.path.join(folder_ouvrage, f), sep = ';') for f in filelist_ouvrage]
    ouvrages = pd.concat(ouvrage_list, axis = 0, ignore_index = True).drop_duplicates()
    ouvrages.reset_index(drop = True, inplace = True)
    
# =============================================================================
#     if not os.path.exists(os.path.join(folder_root, "allinfo")):
#         os.makedirs(os.path.join(folder_root, "allinfo"))
# =============================================================================
    
    allinfo_gdf_list = []
    
    # Chroniques de prélèvement
    for f in filelist:
        temp_gdf = geo.load_any(os.path.join(data_folder, f), sep = ";")
        
        # Case where the files are in JSON format instead of GeoJSON:
        if isinstance(temp_gdf, dict):
            temp_gdf = pd.DataFrame.from_dict(temp_gdf['data'])
            geometry = [Point(xy) for xy in zip(temp_gdf.longitude, 
                                                temp_gdf.latitude)]
            temp_gdf = gpd.GeoDataFrame(
                temp_gdf,
                crs = 4326,
                geometry = geometry)
            
        # Combine ouvrage info and withdrawal timeseries
        temp_gdf = pd.merge(temp_gdf, ouvrages[['code_ouvrage', 
                                                'code_type_milieu', 
                                                'libelle_type_milieu']], 
                            on = 'code_ouvrage', how = 'left')
        
        # Complete allinfo_gdf_list
        allinfo_gdf_list.append(temp_gdf)
        
# =============================================================================
#         # For each year, export a json file including water origin information
#         geo.export(temp_gdf, 
#                os.path.join(folder_root, "allinfo", f),
#                encoding='utf-8')
# =============================================================================
    
    # Merge all files into a single vector one
    # =========
    merged_gdf = geo.merge_data(data = allinfo_gdf_list)
# ========= flat gdf considered useless =======================================
#     flat_merged_gdf = geo.merge_data(data = allinfo_gdf_list, flatten = True)
# =============================================================================
    
    merged_gdf['time'] = merged_gdf.annee.astype(str) + '-12-31'
    merged_gdf['time'] = pd.to_datetime(merged_gdf['time'], format = "%Y-%m-%d")
    
    # Export
    # =========
# =============================================================================
#     if not os.path.exists(os.path.join(folder_root, "concat")):
#         os.makedirs(os.path.join(folder_root, "concat"))
# =============================================================================
        
# ====== function returns a variable instead of exporting =====================
#     year_pattern = re.compile("\d{4,4}")
#     year_start = int(year_pattern.findall(os.path.splitext(filelist[0])[0])[0])
#     year_end = int(year_pattern.findall(os.path.splitext(filelist[-1])[0])[0])
#     geo.export(merged_gdf, 
#                # os.path.join(folder_root, "concat", f"{year_start}-{year_end}.shp"),
#                os.path.join(folder_root, "concat", f"{year_start}-{year_end}.json"),
#                encoding='utf-8')
# =============================================================================
    
# ========= flat gdf considered useless =======================================
#     geo.export(flat_merged_gdf, 
#                # os.path.join(folder_root, "concat", f"{year_start}-{year_end}.shp"),
#                os.path.join(folder_root, "concat", f"{year_start}-{year_end}_flat.json"),
#                encoding='utf-8')
# =============================================================================
# ========= flat gdf considered useless =======================================
#     return {f"{year_start}-{year_end}.json": merged_gdf,
#             f"{year_start}-{year_end}_flat.json": flat_merged_gdf}
# =============================================================================
    
    return merged_gdf


def hydrometry(data, extension = '.json'):
    data_folder, filelist = geo.get_filelist(data, extension = extension)
    folder_root = os.path.split(data_folder)[0]
    
    # Complete withdrawals timeseries by merging each file with water origin
    # =========
    # Retrieve infos on stations
    folder_stations, filelist_stations = geo.get_filelist(os.path.join(data, "stations"), extension = extension)
    stations_list = [gpd.read_file(os.path.join(folder_stations, f)) for f in filelist_stations]
    stations = pd.concat(stations_list, axis = 0, ignore_index = True).drop_duplicates()
    stations.reset_index(drop = True, inplace = True)
    
    allinfo_gdf_list = []
    
    # Chroniques de prélèvement
    for f in filelist:
        temp_gdf = geo.load_any(os.path.join(data_folder, f))
        
        # Case where the files are in JSON format instead of GeoJSON:
        if isinstance(temp_gdf, dict):
            temp_gdf = pd.DataFrame.from_dict(temp_gdf['data'])
            geometry = [Point(xy) for xy in zip(temp_gdf.longitude, 
                                                temp_gdf.latitude)]
            temp_gdf = gpd.GeoDataFrame(
                temp_gdf,
                crs = 4326,
                geometry = geometry)
            
        # Combine station info and discharge timeseries
        temp_gdf = pd.merge(temp_gdf, stations[['code_site',
                                                'code_station',
                                                'code_cours_eau', 
                                                'libelle_cours_eau', 
                                                'uri_cours_eau',
                                                'commentaire_influence_locale_station',
                                                'date_ouverture_station',
                                                ]], 
                            on = 'code_station', how = 'left')
        
        # Complete allinfo_gdf_list
        allinfo_gdf_list.append(temp_gdf)
    
    # Merge all files into a single vector one
    # =========
    merged_gdf = geo.merge_data(data = allinfo_gdf_list)
    
    merged_gdf['time'] = pd.to_datetime(merged_gdf['date_obs_elab'], format = "%Y-%m-%d")
    
    # Correct units
    # ========
    # convert l/s into m3/s, or mm into m
    merged_gdf = geo.convert_unit(merged_gdf, '/1000', var = 'resultat_obs_elab')
    
    return merged_gdf
        
    
    
#%%% * DRIAS
def drias(data):
    print(f'\nProcessed file = {data}')
    
    with xr.open_dataset(data, decode_coords = 'all') as data_ds:
        data_ds.load() # to unlock the resource
    
    #% Formating
    # -----------
    print('\nPre-formating...')
    # Drop useless variables
    data_ds = data_ds.drop(['i', 'j', 'lat', 'lon'])
    print('   _ Additional coords (i, j, lat, lon) dropped')
    # Add CRS
    if not EPSG_in: # EPSG = None, by default
        if 'spatial_ref' not in list(data_ds.coords) + list(data_ds.data_vars):
            EPSG_in = 27572
            data_ds.rio.write_crs(f"epsg:{EPSG_in}", inplace = True)
            print(f"   _ The Coordinates Reference System is not indicated in the original file. By default, epsg:{EPSG_in} is used")
        else:
            EPSG_in = data_ds.rio.crs.to_epsg()
    
# =============================================================================
#         data_ds = data_ds.rename(prtotAdjust = 'pr')
#         print(f"   _ Precipitation variable name modified: prtotAdjust -> pr")
# =============================================================================
    # Get main variable
    var = geo.main_var(data_ds)
    print(f"   _ Main variable is: {var}")
    
    data_ds[var] = data_ds[var]/1000*(60*60*24) # conversion from from mm.s-1 to m.d-1
    data_ds[var].attrs['units'] = 'm.d-1'
    print('   _ Units converted from mm/s to m/d')
    
    #% Reproject in defined CRS
    # -------------------------
    print('\nReprojecting...')
    print('   _ From epsg:{} to epsg:{}'.format(str(EPSG_in), str(EPSG_out)))
    
    # Resolution
    coord1 = list(data_ds.coords)[1]
    coord2 = list(data_ds.coords)[2]
    if reso_m is None:
        print('   _ Input resolution is taken as output resolution based on {}'.format(coord1))
        reso = float(data_ds[coord1][1] - data_ds[coord1][0])
        if data_ds[coord1].units[0:6].casefold() == 'degree':
            reso_m = round(reso*111200)
        elif data_ds[coord1].units[0:1].casefold() == 'm':
            reso_m = reso
    print('   _ Resolution: {} km'.format(reso_m/1000))
    
# =============================================================================
#         data_coords_conv = rasterio.warp.transform(rasterio.crs.CRS.from_epsg(EPSG_in), 
#                                                    rasterio.crs.CRS.from_epsg(EPSG_out), 
#                                                    [data_ds.x.values.min()], [data_ds.y.values.max()])
#         if reso_m == 75:
#             x_min = ac.nearest(x = data_coords_conv[0][0] - reso_input)
#             y_max = ac.nearest(x = data_coords_conv[1][0] + reso_input)
#         else:
#             x_min = (data_coords_conv[0][0] - reso_input) // reso_m * reso_m - reso_m/2
#             y_max = (data_coords_conv[1][0] + reso_input) // reso_m * reso_m + reso_m/2    
# =============================================================================
    
    
    if coords_extent == 'from_input':
        reprj_ds = data_ds.rio.reproject(
            dst_crs = 'epsg:'+str(EPSG_out), 
            resampling = rasterio.enums.Resampling(5),
            )
        print('   _ Data reprojected based on the extent and resolution of input data')
        print('     (user-defined resolution is not taken into account)')
    
    else: # In all other cases, x_min, x_max, y_max and y_min will be determined before .rio.reproject()
        if type(coords_extent) == str & coords_extent.casefold() in ["bretagne", "brittany"]:
            # Emprise sur la Bretagne
            if EPSG_out == 3035:   #LAEA
                x_min = 3164000
                x_max = 3572000
                y_max = 2980000
                y_min = 2720000
            elif EPSG_out == 2154: #Lambert-93
                x_min = 70000
                x_max = 460000
                y_max = 6909000
                y_min = 6651000
            elif EPSG_out == 4326: #WGS84
                x_min = -5.625
                x_max = -0.150
                y_max = 49.240
                y_min = 46.660
            print('   _ Extent based on Brittany')
        
        elif type(coords_extent) == list:
            [x_min, x_max, y_min, y_max] = coords_extent
            print('   _ User-defined extent')
        
        # Alignement des coordonnées selon la résolution (valeurs rondes)
        x_min = nearest(x = x_min, res = reso_m, x0 = 0)
        x_max = nearest(x = x_max, res = reso_m, x0 = 0)
        y_max = nearest(y = y_max, res = reso_m, y0 = 0)
        y_min = nearest(y = y_min, res = reso_m, y0 = 0)
        print("   _ Bounds:")
        print("               {}".format(y_max))
        print("      {}           {}".format(x_min, x_max))
        print("               {}".format(y_min))
        
        transform_ = Affine(reso_m, 0.0, x_min,  
                            0.0, -reso_m, y_max)
        
# =============================================================================
#         width_ = int(data_ds.x.shape[0] * reso_input / reso_m //1 +1)
#         height_ = int(data_ds.y.shape[0] * reso_input / reso_m //1 +1)
# =============================================================================
        
        dst_height = (y_max - y_min)//reso_m
        dst_width = (x_max - x_min)//reso_m
        
        reprj_ds = data_ds.rio.reproject(
            dst_crs = 'epsg:'+str(EPSG_out), 
            shape = (dst_height, dst_width),
            transform = transform_, 
            resampling = rasterio.enums.Resampling(5),
            # nodata = np.nan,
            )


# =============================================================================
#         # Adding attributes:
#         ds_reprj.rio.write_crs("epsg:"+str(EPSG_out), inplace = True)
#         ds_reprj.x.attrs = {'standard_name': 'projection_x_coordinate',
#                                     'long_name': 'x coordinate of projection',
#                                     'units': 'Meter'}
#         ds_reprj.y.attrs = {'standard_name': 'projection_y_coordinate',
#                                     'long_name': 'y coordinate of projection',
#                                     'units': 'Meter'}
#         ds_reprj.soildepth.attrs = {'grid_mapping': "spatial_ref"}
# =============================================================================
    
# =============================================================================
#         #% Convert values units :
#         # from [kg m-2s-1] to [mm d-1] 
#         ds_reprj[var] = ds_reprj[var] *60*60*24
#         ds_reprj.pr.attrs['units'] = 'mm.d-1'
#         # -> plutôt appliquer un facteur de conversion dans les settings de CWatM
# =============================================================================

    #% Export :
    print("\nPreparing export, formating encodings and attributes...")
    print('   _ Output file type: {}'.format(file_extension))
    
    reprj_ds[coord1].encoding = data_ds[coord1].encoding
    reprj_ds[coord2].encoding = data_ds[coord2].encoding
    print("   _ Coords attributes transferred")
    
    if 'original_shape' in reprj_ds[var].encoding.keys():
        reprj_ds[var].encoding.pop('original_shape')
        reprj_ds[coord1].encoding.pop('original_shape')
        reprj_ds[coord2].encoding.pop('original_shape')
        print("   _ 'original_shape' has been removed")
    
    
    # If it is the PrecipitationMaps, it is necessary to erase the x and y
    # '_FillValue' encoding, because precipitation inputs are taken as 
    # format model by CWatM
    if var == 'tp': 
        reprj_ds.x.encoding['_FillValue'] = None
        reprj_ds.y.encoding['_FillValue'] = None
        print("   _ Fill Value removed from x and y")
    
    # reprj_ds.x.encoding['_FillValue'] = None
    # reprj_ds.y.encoding['_FillValue'] = None
    # reprj_ds[var].encoding['_FillValue'] = np.nan
    
    # Compression (not lossy)
    reprj_ds[var].encoding['zlib'] = True
    reprj_ds[var].encoding['complevel'] = 4
    reprj_ds[var].encoding['contiguous'] = False
    reprj_ds[var].encoding['shuffle'] = True
    print('   _ Compression x4 without loss (zlib)')
    
    output_file = os.path.join(input_folder,
                               ' '.join([file_name, 
                                         'res='+str(reso_m)+'m', 
                                         'CRS='+str(EPSG_out),
                                         ]) + file_extension)
    
    reprj_ds.to_netcdf(output_file)      
    """
    La compression (2x plus petit) fait planter QGIS lorsqu'il essaye
    de lire le fichier comme un maillage.
    Il est nécessaire d'effacer la _FillValue des coordonnées x et y.
    """
    
    print('\n -> Successfully exported to:\n' + output_file)
    
    return reprj_ds


#%%% ° CORINE Land Cover
def corine(data):
    (folder_name, file_name) = os.path.split(data)
    (file_name, extension) = os.path.splitext(file_name)
    
    data_years = [1990, 2000, 2006, 2012, 2018]
    y = data_years[4]
    
    land_convert = [
        [23, 24, 25, 26, 27, 28, 29], # 1. forests
        [12, 15, 16, 17, 18, 19, 20, 21, 22], # 2. grasslands and non-irrigated crops
        [14], # 3. rice fields
        [13, ], # 4. irrigated crops
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], # 5. sealed lands
        [40, 41, 42, 43], # 6. water surfaces
        # [7, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39], # x. sol nu
        ]
    
# =============================================================================
#         with xr.open_dataset(data) as data_ds:
#             data_ds.load() # to unlock the resource
# =============================================================================
    
    #%%%% Découpe du fichier (mondial) sur la Bretagne 
    # -----------------------------------------------
    with rasterio.open(data, 'r') as data:
        # data_profile = data.profile
        # data_crs = data.crs # epsg:3035
        # data_val = data.read()[0] # np.ndarray
        #     # 46000 lignes
        #     # 65000 colonnes
        # data_dtype = data.dtypes[0] # int8
        
        # Définition du périmètre de découpe
# =============================================================================
#             shapes = Polygon([
#                 (3188000, 2960000),
#                 (3188000 + 364000, 2960000),
#                 (3188000 + 364000, 2960000 - 231000),
#                 (3188000, 2960000 - 231000),
#                 (3188000, 2960000)])
# =============================================================================
# =============================================================================
#             shapes = rasterio.warp.transform_geom(
#                 {'init': 'epsg:3035'},
#                 data.crs,
#                 {'type': 'Polygon',
#                  'coordinates': [[
#                      (3188000, 2960000),
#                      (3188000 + 364000, 2960000),
#                      (3188000 + 364000, 2960000 - 231000),
#                      (3188000, 2960000 - 231000),
#                      (3188000, 2960000)]]}
#                 )
# =============================================================================
        with fiona.open(r"D:\2- Postdoc\2- Travaux\2- Suivi\2- CWatM\2022-01-12) Synthèse inputs\Mask_Bretagne_3035_1km.shp", "r") as shapefile:
            shapes = [feature["geometry"] for feature in shapefile]
        
        # Découpe
        out_raster, out_transform = rasterio.mask.mask(data, 
                                                      shapes, 
                                                      crop = True)
        
        crp_data = out_raster[0]
        
        # Mise à jour des attributs
        # data_profile = data.meta
        data_profile = data.profile
        data_profile.update({
            # "driver": "Gtiff",
        	"height": crp_data.shape[0],
        	"width": crp_data.shape[1],
        	# "nodata": -128,
        	"transform": out_transform})
        
        # Export (fichier facultatif)
        output_file = os.path.join(folder_name, file_name + '_Brittany.tif')
        with rasterio.open(output_file, 'w', **data_profile) as output_f:
            output_f.write_band(1, crp_data)
        print('\nCropped file has been successfully exported')
        
    
    #%%%% Extraction des types d'occupation du sol
    # -------------------------------------------
    data_profile['dtype'] = 'float32' # pour limiter la taille sur disque
    
    for i in range(0,6):
        # Création d'une carte de mêmes dimensions, avec la valeur 1 sur
        # les pixels correspondant au landcover voulu, et 0 sur les autres
        print('\nClass ' + str(i+1) + ":")
        count = np.zeros(crp_data.shape, dtype = data_profile['dtype'])
        count = count.astype('float32') # pour limiter la taille sur disque
        
        for code in land_convert[i]:
            # count[crp_data == code] += 1 # Normalement ça ne dépasse jamais 1
            count[crp_data == code] = 1
        
        # Export en résolution initiale (fichiers facultatifs)
        output_file = os.path.join(folder_name, file_name + '_class' + str(i+1) + '.tif')
        with rasterio.open(output_file, 'w', **data_profile) as output_f:
            output_f.write_band(1, count)
        print('   - Successfully exported into initial-resolution *.tif')

      

        # Reprojection and conversion of counts into percentages
        # dst_trsfm = Affine(1000, 0, 900000,
        #                    0, -1000, 5500000)
        # dst_trsfm = Affine(1000, 0, 3188000,
        #                    0, -1000, 2960000)
        dst_trsfm = Affine(1000, 0, 3165000,
                           0, -1000, 2954000)
        
        # data_reprj = np.zeros((4600, 6500), dtype = np.float32)
        # data_reprj = np.zeros((231, 364), dtype = np.float32)
        data_reprj = np.zeros((258, 407), dtype = np.float32)
        
        dst_data_profile = data_profile.copy()
        dst_data_profile.update({
        	"height": data_reprj.shape[0],
        	"width": data_reprj.shape[1],
        	"transform": dst_trsfm,
            "nodata": np.nan})
        
        rasterio.warp.reproject(count, 
                                destination = data_reprj, 
                                src_transform = data_profile['transform'],
                                src_crs = data_profile['crs'],
                                src_nodata = data_profile['nodata'],
                                dst_transform = dst_data_profile['transform'],
                                dst_crs = dst_data_profile['crs'],
                                dst_nodata = dst_data_profile['nodata'],
                                resampling = rasterio.enums.Resampling(5),
                                )
        
        # Export en résolution finale (fichiers intermédiaires nécessaires)
        output_file = os.path.join(folder_name, 
                                   '_'.join([file_name, '_class' + str(i+1), '1000m.tif'])
                                   )
        with rasterio.open(output_file, 'w', **dst_data_profile) as output_f:
            output_f.write_band(1, data_reprj)
        print('   - Successfully exported into coarse-resolution *.tif')
        
        
    #%%%% Conversion des derniers fichiers créés (*.tif) en *.nc
    # ---------------------------------------------------------
    var_names = [
        'fracforest',
        'fracgrassland',
        'fracirrNonPaddy',
        'fracirrPaddy',
        'fracsealed',
        'fracwater',
        ]
    
    # Initialization:
    i = 0
    with xr.open_dataset(os.path.join(folder_name, '_'.join([file_name, '_class' + str(i+1), '1000m.tif']))) as data_ds:
        data_ds.load()
    # data_ds = data_ds.squeeze('band').drop('band')
    data_ds = data_ds.rename(band = 'time')
    # data_ds = data_ds.reindex(time = [datetime.datetime(2018, 1, 31)])
    data_ds = data_ds.assign_coords({'time': ('time', [datetime.datetime(y, 1, 31)])})
    data_ds = data_ds.rename(band_data = var_names[i])
 
    for i in range(1,6):
        with xr.open_dataset(os.path.join(folder_name, '_'.join([file_name, '_class' + str(i+1), '1000m.tif']))) as data_tmp:
            data_tmp.load()
        # data_tmp = data_tmp.squeeze('band').drop('band')
        data_tmp = data_tmp.rename(band = 'time')
        # data_tmp = data_tmp.reindex(time = [datetime.datetime(2018, 1, 31)])
        data_tmp = data_tmp.assign_coords({'time': ('time', [datetime.datetime(y, 1, 31)])})
        data_tmp = data_tmp.rename(band_data = var_names[i])
        data_ds[var_names[i]] = data_tmp[var_names[i]]
    
    # Rectification de la normalisation des pourcentages
# =============================================================================
#         # data_ds.fillna(0)
#         sum_norm = data_ds[var_names[0]]+data_ds[var_names[1]]+data_ds[var_names[2]]+data_ds[var_names[3]]+data_ds[var_names[4]]+data_ds[var_names[5]]
#         for i in range(0,6):
#             data_ds[var_names[i]] = data_ds[var_names[i]]/sum_norm
# =============================================================================
    
    data_ds.rio.write_crs('epsg:3035', inplace = True)
    data_ds.x.attrs = {'standard_name': 'projection_x_coordinate',
                        'long_name': 'x coordinate of projection',
                        'units': 'Meter'}
    data_ds.y.attrs = {'standard_name': 'projection_y_coordinate',
                        'long_name': 'y coordinate of projection',
                        'units': 'Meter'}
    output_file = os.path.join(folder_name, 'fractionLandcover_Bretagne_CORINE_{}.nc'.format(str(y)))
    
    # NB : Il est nécessaire de faire disparaître les valeurs nan
# =============================================================================
#         data_ds['fracforest'].encoding['_FillValue'] = 0 # ou None ??
#         data_ds['fracgrassland'].encoding['_FillValue'] = 0 # ou None ??
#         data_ds['fracirrNonPaddy'].encoding['_FillValue'] = 0 # ou None ??
#         data_ds['fracirrPaddy'].encoding['_FillValue'] = 0 # ou None ??
#         data_ds['fracsealed'].encoding['_FillValue'] = 0 # ou None ??
#         data_ds['fracwater'].encoding['_FillValue'] = 0 # ou None ??
# =============================================================================
    
    data_ds.to_netcdf(output_file)

            
#%%% ° Observatoire botanique de Brest (2018-2019)
def obb(data):
    land_convert = [
        [0, 0, 0], # 1. forests
        [0, 0, 0], # 2. grasslands and non-irrigated crops
        [0, 0, 0], # 3. rice fields
        [0, 0, 0], # 4. irrigated crops
        [0, 0, 0], # 5. sealed lands
        [0, 0, 0], # 6. water surfaces
        # [7, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39], # x. sol nu
        ]
    return 'Pas encore implémenté'


#%%% ° CES OSO
def cesoso(data):
    return "Pas encore implémenté"
    
#%%% ° Soil depth from UCS Bretagne
def ucsbretagne(data):
    data_df = gpd.read_file(data) # data_df = soil depth
    data_epsg = data_df.crs.to_epsg()
    
    #% Calcul des profondeurs locales moyennes pondérées
    print('\nComputing local weighted depth averages...')
    soil_depth_limit = 140 # valeur semi-arbitraire
    class_depth_convert = {'0':0,
                           '1':soil_depth_limit - (soil_depth_limit-100)/2,
                           '2':90,
                           '3':70,
                           '4':50,
                           '5':30,
                           '6':10,
                           }
    data_df['EPAIS_1_NUM'] = [class_depth_convert[val] for val in data_df['EPAIS_DOM'].values] 
    data_df['EPAIS_2_NUM'] = [class_depth_convert[val] for val in data_df['EPAIS_2'].values] 
    data_df['EPAIS_1_2'] = (data_df['EPAIS_1_NUM'] * data_df['P_EPAISDOM'] + data_df['EPAIS_2_NUM'] * data_df['P_EPAIS2']) / (data_df['P_EPAISDOM'] + data_df['P_EPAIS2'])
    data_df['EPAIS_1_2'] = data_df['EPAIS_1_2']/100 # Convertir cm vers m
    
    #% Reprojection dans le CRS voulu
    print('\nReprojecting...')
    print('   from epsg:{} to epsg:{}'.format(str(data_epsg), str(EPSG_out)))
    data_df.to_crs('epsg:'+str(EPSG_out), inplace = True)
    
    #% Rasterisation
    print('\nRasterizing...')
    x_min = 74000
    y_max = 6901000
    bounds_conv = rasterio.warp.transform(rasterio.crs.CRS.from_epsg(2154), 
                                          rasterio.crs.CRS.from_epsg(EPSG_out), 
                                          [74000], [6901000]) # Limites (larges) de la Bretagne en L93
    x_min = bounds_conv[0][0] // reso_m * reso_m
    y_max = bounds_conv[1][0] // reso_m * reso_m
    
    # Décalage d'un demi pixel
    if reso_m == 75:
        x_min = nearest(x = x_min) - 75/2
        y_max = nearest(x = y_max) + 75/2
    else:
        x_min = x_min - reso_m/2
        y_max = y_max + reso_m/2
    
    transform_ = Affine(reso_m, 0.0, x_min,  
                        0.0, -reso_m, y_max)
    
# =============================================================================
#         transform_ = Affine(reso_m, 0.0, x_min,  
#                             0.0, reso_m, 670500)
# =============================================================================
    
    width_ = 377000 // reso_m + 1
    height_ = 227000 // reso_m + 1
    
    raster_data = rasterio.features.rasterize(
        [(val['geometry'], val['EPAIS_1_2']) for i, val in data_df.iterrows()],
        out_shape = (height_, width_),
        transform = transform_,
        fill = np.NaN,
        all_touched = True)
    
    #% Convertir en DataSet
    print('\nConverting into xarray.Dataset...')
    # Converting to xarray dataarray:
    dataarray_ = xr.DataArray(raster_data, 
                              coords = [np.arange(y_max,
                                                  y_max - reso_m * height_,
                                                  -reso_m).astype(np.float32),
                                        np.arange(x_min, 
                                                  x_min + reso_m * width_, 
                                                  reso_m).astype(np.float32)], 
                              dims = ['y', 'x'])
    # NB : La fonction 'range()' est évitée car elle renvoie des entiers
    # QGIS n'arrive pas à détecter le CRS lorsque les axes sont des entiers
    
# =============================================================================
#         dataarray_ = xr.DataArray(raster_data.transpose(), 
#                                   coords = [range(x_min, 
#                                                   x_min + reso_m * width_, 
#                                                   reso_m),
#                                             range(y_max,
#                                                   y_max - reso_m * height_,
#                                                   -reso_m)], 
#                                   dims = ['x', 'y'])
# =============================================================================
    
    # Converting to xarray dataset:
    dataset_ = dataarray_.to_dataset(name = 'soildepth')
    
    # Adding attributes:
    dataset_.rio.write_crs("epsg:"+str(EPSG_out), inplace = True)
    dataset_.x.attrs = {'standard_name': 'projection_x_coordinate',
                                'long_name': 'x coordinate of projection',
                                'units': 'Meter'}
    dataset_.y.attrs = {'standard_name': 'projection_y_coordinate',
                                'long_name': 'y coordinate of projection',
                                'units': 'Meter'}
    dataset_.soildepth.attrs = {'grid_mapping': "spatial_ref"} # A supprimer ???
    # dataset_.assign_coords(spatial_ref = dataset_.spatial_ref)
    # dataset_.rio.write_crs("epsg:"+str(EPSG_out), inplace = True)
    

    #% Export :
    print('\nCompressing and saving...')
    
    full_file_name = ' '.join([file_name, 
                                 'res='+str(reso_m)+'m', 
                                 'CRS='+str(EPSG_out),
                                 'lim='+str(soil_depth_limit),
                                 ])
    output_file = os.path.join(input_folder, 
                               full_file_name + '.nc')
    print('   --> result exported to:\n   --> ' + output_file)
    
    var = main_var(dataset_)
    # dataset_[var].encoding['_FillValue'] = None # ou np.nan ?
    # ERREUR : dataset_.to_netcdf(output_file, encoding = {var: {'zlib': True, 'dtype': 'float32', 'scale_factor': 0.00000001, '_FillValue': np.nan},})
    dataset_.to_netcdf(output_file)
    
    #% Fichiers pour CWatM
    topsoil_ds = dataset_.where(dataset_['soildepth']<0.30, 0.30)
    topsoil_ds = topsoil_ds.where(~np.isnan(dataset_), np.nan)
    # topsoil_ds = topsoil_ds.where(~np.isnan(dataset_), 0)
    subsoil_ds = dataset_ - topsoil_ds
    output_top = os.path.join(input_folder, 
                              'soildepth1_' + full_file_name + '.nc')
    output_sub = os.path.join(input_folder, 
                              'soildepth2_' + full_file_name + '.nc')
    
    # topsoil_ds.to_netcdf(output_top, encoding = {var: {'zlib': True, 'dtype': 'float32', 'scale_factor': 0.00000001, '_FillValue': np.nan},})
    topsoil_ds.to_netcdf(output_top)
    # subsoil_ds.to_netcdf(output_sub, encoding = {var: {'zlib': True, 'dtype': 'float32', 'scale_factor': 0.00000001, '_FillValue': np.nan},})
    subsoil_ds.to_netcdf(output_sub)
    """
    La compression (27x plus petit) fait planter CWatM lorsqu'il utilise
    l'option use_soildepth_as_GWtop
    """

    
    return dataset_
    
#%%% ° Crop coefficients, version "better"
def cropcoeff(data):
    #%%%% Initialization:
    landcover_motif = re.compile('cropCoefficient[a-zA-Z]*')
    pos = landcover_motif.search(file_name).span()
    landcover = file_name[15:pos[1]]
    name = os.path.splitext(file_name)[0][0:pos[1]]
    print(f'\nProcessed landcover = {landcover}')
    print("___________________")
    
    
    with xr.open_dataset(
            data,
            decode_coords = 'all',
            ) as data:
        data.load()
    
    #%%%% Reprojection:
    print('\nReprojecting...')
    
    if not EPSG_in: # EPSG = None, by default
        if 'spatial_ref' not in list(data.coords) + list(data.data_vars):
            print("   Le SCR n'est pas renseigné dans les données initiales. Par défaut, le WGS84 est utilisé")
            EPSG_in = 4326
        else:
            EPSG_in = data.rio.crs.to_epsg()
    print("   From epsg:{} to espg:{}".format(EPSG_in, EPSG_out))
    data.rio.write_crs("epsg:{}".format(EPSG_in), inplace = True)
    
    # Emprise sur la Bretagne
    if EPSG_out == 3035:   #LAEA
        x_min = 3164000
        x_max = 3572000
        y_max = 2980000
        y_min = 2720000
    elif EPSG_out == 2154: #Lambert-93
        x_min = 70000
        x_max = 460000
        y_max = 6909000
        y_min = 6651000
# =============================================================================
#         # To properly implement management of lat/lon, reso_m should be upgraded
#         # with a system including reso_deg (future developments)
#         elif EPSG_out == 4326: #WGS84 (in this case, reso_m should be in ° instead of m)
#             x_min = -5.625
#             x_max = -0.150
#             y_max = 49.240
#             y_min = 46.660
# =============================================================================

    # Alignement des coordonnées selon la résolution (valeurs rondes)
    x_min = nearest(x = x_min, res = reso_m, x0 = 0)
    x_max = nearest(x = x_max, res = reso_m, x0 = 0)
    y_max = nearest(y = y_max, res = reso_m, y0 = 0)
    y_min = nearest(y = y_min, res = reso_m, y0 = 0)
    print("   Final bounds:")
    print("               {}".format(y_max))
    print("      {}           {}".format(x_min, x_max))
    print("               {}".format(y_min))

    # Reproject
    if reso_m is None:
        coord1 = list(data.coords)[1]
        print('NB : La resolution est déterminée à partir des {}\n'.format(coord1))
        reso = float(data[coord1][1] - data[coord1][0])
        if data[coord1].units[0:6].casefold() == 'degree':
            reso_m = round(reso*111200)
        elif data[coord1].units[0:1].casefold() == 'm':
            reso_m = reso
    print('   Resolution: {} km'.format(str(reso_m/1000)))
    
    dst_height = (y_max - y_min)//reso_m
    dst_width = (x_max - x_min)//reso_m
    
    data_reprj = data.rio.reproject(
        dst_crs = 'epsg:'+str(EPSG_out), 
        # resolution = (1000, 1000),
        shape = (dst_height, dst_width),
        transform = Affine(reso_m, 0.0, x_min,
                           0.0, -reso_m, y_max), 
        resampling = rasterio.enums.Resampling(5),
        nodata = np.nan)
    
    
    #%%%% Preparing export:
    print("\nPreparing export...")
# =============================================================================
#         # Change the order of coordinates to match QGIS standards:
#             # Normally, not necessary
#         data_reprj = data_reprj.transpose('time', 'y', 'x')
#         print("      order of coordinates = 'time', 'y', 'x'")
# =============================================================================
    # Formatting to match standards (encodings and attributes)
    print("   Formating encodings and attributes")
# =============================================================================
#         for c in ['time', 'latitude', 'longitude']:
#             data_reprj[c].attrs = data[c].attrs
#             data_reprj[c].encoding = data[c].encoding
#         for f in _fields_intersect:
#             data_reprj[f].attrs = data[f].attrs
#             data_reprj[f].encoding = data[f].encoding
# =============================================================================
    # Insert georeferencing metadata to match QGIS standards:
    # data_reprj.rio.write_crs("epsg:4326", inplace = True)
    # print("      CRS set to epsg:4326")
            
    data_reprj.x.encoding = data.lon.encoding
    data_reprj.y.encoding = data.lat.encoding
    data_reprj.x.encoding.pop('original_shape')
    data_reprj.y.encoding.pop('original_shape')
    
    var = geo.main_var(data)
    
    # If it is the PrecipitationMaps, it is necessary to erase the x and y
    # '_FillValue' encoding, because precipitation inputs are taken as 
    # format model by CWatM
    if var == 'tp': 
    # if name == 'Total precipitation daily_mean':
        data_reprj.x.encoding['_FillValue'] = None
        data_reprj.y.encoding['_FillValue'] = None
    
    # Compression (not lossy)
    data_reprj[var].encoding = data[var].encoding
    data_reprj[var].encoding.pop('chunksizes')
    data_reprj[var].encoding.pop('original_shape')
# =============================================================================
#         data_reprj[var].encoding['zlib'] = True
#         data_reprj[var].encoding['complevel'] = 4
#         data_reprj[var].encoding['contiguous'] = False
#         data_reprj[var].encoding['shuffle'] = True
# =============================================================================
    # NB: The packing induces a loss of precision of apprx. 1/1000 of unit,
    # for a quantity with an interval of 150 units. The packing is
    # initially used in the original ERA5-Land data.    
    
    print("   All attributes and encodings transfered")
    

    #%%%% Export :
    print('\nSaving...')          
    output_file = os.path.join(input_folder,
                               '_'.join([file_name, 
                                        'res='+str(reso_m)+'m', 
                                        'epsg'+str(EPSG_out),
                                         ]) + '.nc')        

    data_reprj.to_netcdf(output_file)
    print("\nLe resultat a bien été exporté dans le fichier : {}".format(output_file))
    
    return data_reprj


###############################################################################
#%%% * Formate les données RHT
def process_rht(shp_file, attrs_file, fields = 'all'):
    """
    Pour rajouter les attributs dans le shapefile, de anière à pouvoir 
    l'afficher facilement dans QGIS.

    Parameters
    ----------
    shp_file : str
        Chemin vers le fichier shapefile
    attrs_file : str
        Chemin vers la table externe d'attributs
    fields : list
        Liste des noms de colonnes que l'on veut insérer dans le shapefile

    Returns
    -------
    Create a new file.
    """
    
    # Inputs
    # ------
    gdf_in = gpd.read_file(shp_file)
    
    df_attrs = pd.read_csv(attrs_file, sep = r";", header = 0, skiprows = 0)
    
    if fields == 'all': fields = list(df_attrs.columns)
    if not isinstance(fields, list): fields = [fields]
    if 'id_drain' not in fields: fields.append('id_drain')
    print('Fields :\n{}'.format(fields))

    # Fusion
    # ------
    gdf_out = gdf_in.merge(df_attrs[fields], left_on = "ID_DRAIN", right_on = "id_drain")
    
    # Export
    # ------
    out_name = os.path.splitext(shp_file)[0] + '_merged.shp'
    gdf_out.to_file(out_name)
    
    return gdf_out    


###############################################################################
#%%% * convert_from_h5_newsurfex (with recessions)
def convert_from_h5_newsurfex(*, input_file, mesh_file, scenario = 'historic', 
                    output_format = 'NetCDF', **kwargs):
    r"""
    % DESCRIPTION:
    This function converts Ronan *.h5 files from SURFEX into NetCDF files, or
    GeoTIFF images, in order to make output files readable by QGIS.
    
    % EXAMPLE:
    >> import geoconvert as gc
    >> gc.convert_from_h5_newsurfex(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\Surfex\BZH\REA.h5",
                          mesh_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\Surfex\BZH\shapefile\maille_meteo_fr_pr93.shp",
                          output_format = "NetCDF",
                          fields = ["REC", "TAS"])
    
    % ARGUMENTS:
    >    
    
    % OPTIONAL ARGUMENTS:
    > output_format = 'NetCDF' (défault) | 'GeoTIFF'
    > scenario = 'historic' | 'RCP2.6' | 'RCP4.5' | 'RCP8.5'
    > kwargs:
        > fields = variable(s) to conserve (among all attributes in input file)
                 = ['ETP', 'PPT', 'REC', 'RUN', 'TAS']
        (One file per variable will be created.)
        
        > dates = for instance : ['2019-01-01', '2019-01-02', ...]
        (If no date is specified, all dates from input file are considered)
    """
    
    #% Get fields argument:
    # ---------------------
    if 'fields' in kwargs:
        fields = kwargs['fields']
        if isinstance(fields, str): fields = [fields]
        else: fields = list(fields) # in case fields are string or tuple
    else:
        print('\n/!\ Fields need to be specified\n')
        
    
    
    for _field in fields:
        print('Processing ' + _field + '...')
        print('   Loading data...')
        #% Load data sets:
        # ----------------
        # _data contains the values, loaded as a pandas dataframe
        _data = pd.read_hdf(input_file, _field + '/' + scenario)
        _data.index.freq = 'D' # Correct the frequency of timestamp, because it
                               # is altered during importation
        _data = _data.iloc[:, 0:-1] # Get rid of the last 'MEAN' column
        _data = _data.transpose()
        
        # _dataset contains the spatial metadata, and will be used as the
        # final output structure
        _dataset = gpd.read_file(mesh_file)
        _dataset.num_id = _dataset.num_id.astype(int) # Convert 'num_id' (str) 
                                                      # into integer
        
        # Only cells present in _data are considered:
        _datasubset = _dataset[_dataset.num_id.isin(_data.index)]
        _datasubset = _datasubset.merge(_data, left_on = "num_id", 
                                        right_index = True)
        _datasubset.index = _datasubset.num_id # replace indexes by id_values
        
        #% Get dates argument: (and build output_name)
        # --------------------
        _basename = os.path.splitext(input_file)[0]
        
        if 'dates' in kwargs:
            dates = kwargs['dates']
            if isinstance(dates, str): 
                output_file = '_'.join([_basename, dates, _field])
                dates = [dates]
            else: 
                dates = list(dates) # in case dates are tuple
                output_file = '_'.join([_basename, dates[0], 'to', dates[-1], _field])
        else:
            dates = _data.columns # if not input_arg, dates = all
            output_file = '_'.join([_basename, scenario, _field])
        
        #% Exports:
        # ---------       
        profile_base = {'driver': 'NetCDF',
                        'dtype': 'float32',
                        'nodata': None,
                        'width': 37,
                        'height': 23,
                        'count': 1,
                        # 'count': len(dates),
                        'crs': rio.crs.CRS.from_epsg(27572),
                        'transform': Affine(8000, 0.0, 56000, 0.0, 8000, 2261000),
                        # values deducted from Xlamb and Ylamb
                        # can also be found from QGIS: "X (ou Y) du sommet le plus proche"
                        'tiled': False,
                        'interleave': 'band'}
        
    # =============================================================================
    #     # Getting bounds from polygons is less precise:
    #     _datasubset.geometry.total_bounds[0:1]
    #     # >> [ 107438.43514434074, 6697835.528522245 ] in epsg:2154
    #     Affine(8000, 0.0, 56092.06862427108, 0.0, 8000, 2260917.5598924947)
    #     # more precise values: 57092.06862427143, 2259917.559892499
    #     #   --> does not improve much...
    # =============================================================================
    
    # =============================================================================
    #     # Using polygon limits instead of polygon centers is less precise:
    #     rasterized_data = rasterio.features.rasterize(
    #         [(_dataval.loc['geometry'], _dataval.loc[pd.to_datetime(_date)]) for i, _dataval in _datasubset.to_crs(27572).iterrows()],
    #         out_shape = (profile_base['height'], profile_base['width']),
    #         transform = profile_base['transform'],
    #         fill = 0,
    #         all_touched = True)
    #         # dtype = rasterio.uint8
    # =============================================================================
        
        #% Add coordinates of the center of each polygon, as a POINT object:
        # ------------------------------------------------------------------
        _datasubset['centers'] = [Point(x_y) 
                                  for x_y in zip(_datasubset.loc[:, 'Xlamb'], 
                                                 _datasubset.loc[:, 'Ylamb'])]
        # NB: Coordinates are here in Lambert Zone II (epsg:27572)    
        
# =============================================================================
#    #{a}     # Previous version, creating a raster per date (very slow):
#             rasterized_data = rasterio.features.rasterize(
#             [(_dataval.loc['centers'], _dataval.loc[pd.to_datetime(_date)]) 
#               for i, _dataval in _datasubset.iterrows()],
#             out_shape = (profile_base['height'], profile_base['width']),
#             transform = profile_base['transform'],
#             fill = np.NaN,
#             all_touched = True)
#             # dtype = rasterio.uint8
# =============================================================================
        
        #% Create a raster mask:
        # ---------------------
        rasterized_mask = rasterio.features.rasterize(
            [(_dataval.loc['centers'], _dataval.loc['num_id']) 
             for i, _dataval in _datasubset.iterrows()],
            out_shape = (profile_base['height'], profile_base['width']),
            transform = profile_base['transform'],
            fill = np.NaN,
            all_touched = True)
            # dtype = rasterio.uint16
        
# =============================================================================
#         #% Apercu visuel rapide :
#         plt.imshow(rasterized_mask, origin = 'lower')
# =============================================================================
        
        #% Build a xarray based on the previous mask:
        # -------------------------------------------
        print('   Building an xarray...')
        # Initialization:
        array3D = np.full((len(dates), 
                           profile_base['height'], 
                           profile_base['width']), np.nan)
        
        # Filling:
        for (_y, _x), _id_val in np.ndenumerate(rasterized_mask):
            if not np.isnan(_id_val):
                array3D[:, _y, _x] = _datasubset.loc[_id_val].iloc[10:-1]
        
        # Converting to xarray dataarray:
        dataarray = xr.DataArray(array3D, 
                                  coords = [dates, 
                                            np.arange(2265000,
                                                      2265000 + 8000*profile_base['height'],
                                                      8000).astype(np.float32),
                                            np.arange(60000, 
                                                      60000 + 8000*profile_base['width'], 
                                                      8000).astype(np.float32)],
        # NB : La fonction 'range()' est évitée car elle renvoie des entiers
        # QGIS n'arrive pas à détecter le CRS lorsque les axes sont des entiers
                                  dims = ['time', 'y', 'x'])
        
        # Converting to xarray dataset:
        dataset = dataarray.to_dataset(name = _field)
        
        # Adding attributes:
        dataset.rio.write_crs("epsg:27572", inplace = True)
        dataset.x.attrs = {'standard_name': 'projection_x_coordinate',
                                    'long_name': 'x coordinate of projection',
                                    'units': 'Meter'}
        dataset.y.attrs = {'standard_name': 'projection_y_coordinate',
                                    'long_name': 'y coordinate of projection',
                                    'units': 'Meter'}
        
        # Export:
        # -------
        if output_format.casefold() in ['nc', 'netcdf']:
            dataset.to_netcdf(output_file + '.nc')
            (folder_name, file_name) = os.path.split(output_file + '.nc')
            print("   The dataset has been successfully exported to the file '{}' in the folder '{}'\n".format(file_name, folder_name))
            
        elif output_format.casefold() in ['tif', 'tiff', 'geotiff']:
            with rasterio.open(output_file + '.tiff', 'w', **profile_base) as out_f:
                for i, d in enumerate(dates):
                    out_f.write_band(i, dataset.sel(time = d))
            (folder_name, file_name) = os.path.split(output_file + '.nc')
            print("   The dataset has been successfully exported to the file '{}' in the folder '{}'\n".format(file_name, folder_name))

        
    return fields
    
    
# =============================================================================
#     #- - - - - - SANDBOX - - - - - 
#     #% Single day:
#     # date = _data.loc[:,_data.columns == '2019-10-15'].columns.values
#     date = _data.loc[:,_data.columns == _date].columns[0]
#     _datasingleday = _datasubset.loc[:, date]
#     
#     #% Matplot:
#     _datasubset.plot(column = date, cmap = 'RdYlBu_r', vmin = 10.5, vmax = 15)
# =============================================================================


#%%% * convert_from_h5_oldsurfex (data from Quentin)
###############################################################################
def convert_from_h5_oldsurfex(*, output_format = 'csv', **kwargs):
    r"""
    % DESCRIPTION :
    Cette fonction formate les fichiers Surfex de Quentin en fichiers *.csv
    organisés par dates (lignes) et identifiants de mailles (colonnes).
    
    % EXEMPLES :
    >> import surfexconvert as sc  #(NB : il faut au préalable que le dossier soit ajouté dans le PYTHONPATH))
    >> sc.convert_from_h5_oldsurfex(output_format = "csv", 
                                 start_years = list(range(2005, 2011, 1)),
                                 variables = ['DRAIN', 'ETR'])
            
    >> sc.convert_from_oldsurfex(output_format = "nc", 
                                 mesh_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\Surfex\BZH\shapefile\maille_meteo_fr_pr93.shp")

    % ARGUMENTS (OPTIONNELS) :
    > output_format = 'csv' (défault) | 'NetCDF' | 'GeoTIFF'
    > kwargs:
        > input_folder = dossier contenant les fichiers à traiter.
            Si rien n'est spécifié, le dossier du script est pris en compte
        > variables = variable(s) à traiter (parmi DRAIN, ETR, PRCP et RUNOFF)
            Si ce n'est pas spécifié, toutes les variables sont considérées
        > start_years = années à traiter
            (par ex : 2012 correspond au fichier blabla_2012_2013)
            Si rien n'est spécifié, toutes les années sont considérées
        > mesh_file = chemin d'accès au fichier de correspondances entre les
        id des tuiles et leurs coordonnées
            (nécessaire uniquement pour NetCDF et GeoTIFF)
    """   
    
    # ---- RECUPERATION DES INPUTS
    #--------------------------
    if 'input_folder' in kwargs:
        input_folder = kwargs['input_folder']
    else:
        input_folder = os.path.dirname(os.path.realpath(__file__))
    
     # Si 'variables' est renseigné, il est converti en liste de strings.
     # Sinon, toutes les variables sont prises en compte (DRAIN, ETR, PRCP...).
    if 'variables' in kwargs:
        variables = kwargs['variables']
        if isinstance(variables, str): variables = [variables]
        else: variables = list(variables)
    else:
        variables = ['DRAIN', 'ETR', 'PRCP', 'RUNOFF']
    print('> variables = ' + ', '.join(variables))
    
     # Si 'start_years' est renseigné, il est converti en liste de strings.
     # Sinon, toutes les années sont considérées (1970-1971 -> 2011-2012).
    if 'start_years' in kwargs:
        start_years = kwargs['start_years']
        if isinstance(start_years, str): start_years = [start_years]
        else: 
            start_years = list(start_years)
            start_years = [str(y) for y in start_years]
    else:
        start_years = [str(y) for y in range(1970, 2012, 1)]
    print("> années de départ = " + ', '.join(start_years))
    
    if 'mesh_file' in kwargs:
        mesh_file = kwargs['mesh_file']
    
    
    #% Localisation des dossiers et fichiers de base : 
    #-------------------------------------------------
    idlist_file = os.path.join(input_folder, 
                               r"numero_mailles_bretagne_etendue.txt")
    # (= fichier des identifiants des mailles) 
    mesh_indexes = np.loadtxt(idlist_file, dtype = int)
    
    
    # ---- TRAITEMENT DES DONNEES
    for _variable in variables:
        print("Traitement de " + _variable + "...")
        dataset_allyears = pd.DataFrame(columns = mesh_indexes) #(initialisation)
        
        for _year in start_years:
            print(_year)
            input_file = os.path.join(input_folder, 
                                      "_".join([_variable, _year, 
                                                str(int(_year)+1)])) 
            # (= fichier de données)

            #% Importation :
            #---------------
            raw_data = pd.read_table(input_file, delimiter = "   ", 
                                     engine = 'python', header = None)
            
            # Redimensionnement :
            #--------------------
            if pd.to_datetime(str(int(_year) + 1)).is_leap_year: n_days = 366
            else: n_days = 365
            reshp_array = np.array(raw_data).reshape((n_days, 610), 
                                                     order = 'C')
            reshp_array = reshp_array[:, 0:-6] # Array de 365 lignes et 604 col
            
            # Ajout des étiquettes :
            #-----------------------
            _start_date = _year + '-07-31'
            date_indexes = pd.date_range(start = _start_date, 
                                         periods = n_days, freq = '1D')
            dataframe_1y = pd.DataFrame(data = reshp_array, 
                                        index = date_indexes, 
                                        columns = mesh_indexes, copy = True)
            
            dataset_allyears = dataset_allyears.append(dataframe_1y)
            
            # =================================================================
            #     #% Rajouter des moyennes ou sommes annuelles comme sur les 
            #        précédentes données Surfex :
            #     T['mean'] = T.mean(axis = 1)
            #     T['sum'] = T.sum(axis = 1)
            # =================================================================
          
            
        # ---- EXPORTATION
        output_file = os.path.join(input_folder, 
                                   "_".join([_variable, start_years[0],
                                            str(int(start_years[-1])+1)]
                                            )
                                   )
        
        #% Export en CSV :
        #-----------------
        if output_format in ['csv', 'CSV']:
            dataset_allyears.to_csv(output_file + ".csv", sep = '\t', 
                                    header = True) 
            (folder_name, file_name) = os.path.split(output_file + ".csv")
            print("> Le fichier \'{}\' a été créé dans le dossier \'{}\'.".format(
                file_name, folder_name))
            
        
        #% Export en NetCDF ou TIFF :
        #----------------------------
        elif output_format in ['NetCDF', 'nc', 'TIFF', 'tiff', 'tif', 'GeoTIFF']:            
            #% Géoréférencement des données / formatage
            print("Formatage...")
            # (NB : dataset_allyears sera écrasé plus tard)
            all_date_indexes = dataset_allyears.index
            n_dates = len(all_date_indexes)
            _data = dataset_allyears.transpose(copy = True)
            _geodataset = gpd.read_file(mesh_file)
            _geodataset.num_id = _geodataset.num_id.astype(int)
            
            _geodataset = _geodataset[_geodataset.num_id.isin(_data.index)]
            _geodataset = _geodataset.merge(_data, left_on = "num_id", 
                                            right_index = True)
            
            res_x = 8000 # résolution Surfex [m]
            res_y = 8000
            n_x = len(pd.unique(_geodataset.loc[:, 'Xlamb']))
            n_y = len(pd.unique(_geodataset.loc[:, 'Ylamb']))
            x_min = min(_geodataset.loc[:, 'Xlamb']) - res_x/2 #NB : not 56000
            y_min = min(_geodataset.loc[:, 'Ylamb']) - res_y/2
            profile_base = {'driver': 'NetCDF',
                            'dtype': 'float64',
                            'nodata': None,
                            # 'time': n_dates,
                            'height': n_y, #23
                            'width': n_x, #37
                            'count': n_dates,
                            'crs': rio.crs.CRS.from_epsg(27572),
                            'transform': Affine(res_x, 0.0, x_min,  
                                                0.0, res_y, y_min),
                            # values deducted from Xlamb and Ylamb and QGIS
                            'tiled': False,
                            'interleave': 'band'}
            
            _geodataset['centers'] = [Point(x_y) for x_y in 
                                        zip(_geodataset.loc[:, 'Xlamb'], 
                                            _geodataset.loc[:, 'Ylamb'])]
            # NB: Coordinates are here in Lambert Zone II (epsg:27572)    
            
            raster_data_allyears = np.empty(shape = (n_dates,
                                                     profile_base['height'], 
                                                     profile_base['width']))
            
            print("  Rasterisation... ({} éléments. Peut prendre plusieurs minutes)".format(len(all_date_indexes)))
            for d, _date in enumerate(all_date_indexes):
                _raster_data = rasterio.features.rasterize(
                    [(_dataval.loc['centers'], _dataval.loc[pd.to_datetime(_date)]) 
                      for i, _dataval in _geodataset.iterrows()],
                    out_shape = (profile_base['height'], profile_base['width']),
                    transform = profile_base['transform'],
                    fill = np.NaN,
                    all_touched = True)
                
                raster_data_allyears[d, :, :] = _raster_data
                #*** Est-ce que cette étape peut être faite telle quelle avec 
                # des données incluant tous les temps ?***
                
            print("  xarray...")
            dataarray_allyears = xr.DataArray(
                raster_data_allyears, 
                #raster_data_allyears.astype('float32'), 
                coords = [all_date_indexes, 
                          np.sort(pd.unique(_geodataset.loc[:, 'Ylamb'])), 
                          np.sort(pd.unique(_geodataset.loc[:, 'Xlamb']))],
                # <!> NB <!> Il est extrêmement important de trier les
                # indices dans l'ordre croissant !!! (ils sont désordonnés dans 
                # _geodataset). Sinon QGIS n'arrive pas à lire les fichiers !
                dims = ['time', 'y', 'x']) 
# =============================================================================
#                 # [AVANT : dims = ['time', 'latitude', 'longitude'])]
# =============================================================================
                # L'ordre conseillé des dimensions est t, lat, lon, mais ça n'a
                # pas d'incidence.
            
            # Conversion en Dataset :
            dataset_allyears = dataarray_allyears.to_dataset(name = _variable)
            
            print("Exportation...")
            if output_format in ['NetCDF', 'nc']:
                #% Pour NetCDF :
                # - - - - - - - -        
                # Formatage des attributs selon les conventions QGIS :
                # Insert georeferencing metadata :
                dataset_allyears.rio.write_crs("epsg:27572", inplace = True)
                dataset_allyears.x.attrs = {'standard_name': 'projection_x_coordinate',
                                            'long_name': 'x coordinate of projection',
                                            'units': 'Meter'}
                dataset_allyears.y.attrs = {'standard_name': 'projection_y_coordinate',
                                            'long_name': 'y coordinate of projection',
                                            'units': 'Meter'}
# =============================================================================
#                 # AVANT :
#                 dataset_allyears.longitude.attrs = {'units': 'degrees_east',
#                                            'long_name': 'longitude'}
#                 dataset_allyears.latitude.attrs = {'units': 'degrees_north',
#                                            'long_name': 'latitude'}
# =============================================================================
                # dataset_allyears.time.attrs = {'units': 'days since 1970-01-01',
                #                       'calendar': 'gregorian',
                #                       'long_name': 'time'}
                dataset_allyears.attrs = {'Conventions': 'CF-1.6'}
                
                dataset_allyears.to_netcdf(output_file + ".nc")
                (folder_name, file_name) = os.path.split(output_file + ".nc")
                print("> Le fichier \'{}\' a été créé dans le dossier \'{}\'.".format(
                    file_name, folder_name))
            
            else:
                #% Pour TIFF :
                # - - - - - - -
                dataset_allyears[_variable].rio.to_raster(output_file + '.tiff')
    # =============================================================================
    #             # Méthode sans rioxarray :
    #             # (Problème : les valeurs des coordonnées semblent désordonnées)
    #             with rasterio.open(output_file + ".tiff", 'w', 
    #                                **profile_base) as out_f:
    #                 for d, _date in enumerate(all_date_indexes):
    #                     # out_f.write_band(d + 1, raster_data_allyears[d, :, :])
    #                     out_f.write_band(d + 1, 
    #                                      dataset_allyears[_variable].sel(time = _date))      
    # =============================================================================
                (folder_name, file_name) = os.path.split(output_file + ".tiff")
                print("> Le fichier \'{}\' a été créé dans le dossier \'{}\'.".format(
                    file_name, folder_name))
                    
    return dataset_allyears


###############################################################################
#%%% ERA5-Land
def correct_bias(input_file, correct_factor = 1, to_dailysum = True,
                 progressive = False):
    """
    Fonction plutôt à utiliser sur les données finales formatées
    correct_factor:
        - for precipitations (hourly) : 1.8
        - for precipitations (daily sum): 0.087 
        - for radiations (daily sum): 0.0715 (and progressive = True)
        - for potential evapotranspiration pos (daily sum): 0.04
    """
    
    print("\nLoading...")
    with xr.open_dataset(input_file, decode_coords = 'all') as ds:
        ds.load() # to unlock the resource
        
    ds2 = ds.copy(deep = True)
    
    print("\nCorrecting values: multiply by {}...".format(correct_factor))
    
    if not progressive: # constant correction for any day
        var_list = main_var(ds)
        suffix = f"{correct_factor}"
        for var in var_list:
            ds2[var] = ds2[var]*correct_factor
        correct_factor_max = correct_factor
    
    elif progressive: # varying correction along the year (stronger in summer, weaker in winter)
        var_list = main_var(ds)
        suffix = f"{correct_factor}P1"
        monthly_correction = np.array([0.74130111, 0.6586179, 1.04861236, 
                                       0.98615636, 0.96493336, 1.15048825, 
                                       1.06386533, 1.16570181, 1.001253, 
                                       0.81417812, 0.71620761, 0.76901861]) * correct_factor
        # Redefinition of correct_factor as a monthly correction:
        # correct_factor = ds2.mean(dim = ['latitude', 'longitude']).groupby("time.month").mean()
        # correct_factor[var] = monthly_correction
        correct_factor_monthly = xr.DataArray(monthly_correction, dims = 'month', coords = {'month': list(range(1,13))})
        for var in var_list:
            ds2[var] = ds2[var].groupby('time.month', squeeze = False)*correct_factor_monthly
        
        ds2 = ds2.drop("month")
        correct_factor_max = float(correct_factor_monthly.max())
        
# =============================================================================
#         # Pipeline pour calculer les coefficients
#         month_length = ds.time.dt.days_in_month
#         weights = (
#             month_length.groupby("time.month") / month_length.groupby("time.month").sum())
#         # Pour vérifier que la somme des pondérations fait bien 1 pour chaque mois
#         np.testing.assert_allclose(weights.groupby("time.month").sum().values, np.ones(12))
#         ds_weighted = (ds * weights).groupby("time.month").sum(dim="time")
#         ds_weighted.mean(dim = ['longitude', 'latitude'])
#         # Référence (visuelle, d'après https://loa.univ-lille.fr/documents/LOA/formation/stages/B_Anh.pdf)
#         [20, 30, 90, 125, 145, 170, 165, 155, 100, 50, 25, 20] # kWh/m²/month
#         [2322581, 3857143, 10451613, 15000000, 16838710, 20400000,
#          19161290, 18000000, 12000000, 5806452, 3000000, 2322581] # J/m²/d
# =============================================================================
        
    
    unit_factor = 1
    if to_dailysum: # Si les données d'entrée sont des moyennes en m/h :
        print("\nCorrecting units:")
        print("   input values are in .../h")
        print("   multiply by 24 --> .../d")
        for var in var_list:
            ds2[var] = ds2[var]*24
        unit_factor = 24
        
    
    print("\nCorrecting encodings...")
    for var in var_list:
        ds2[var].encoding = ds[var].encoding
        ds2[var].encoding['scale_factor'] = ds[var].encoding['scale_factor']*correct_factor_max*unit_factor
        ds2[var].encoding['add_offset'] = ds[var].encoding['add_offset']*correct_factor_max*unit_factor

    ds2.x.encoding['_FillValue'] = None
    ds2.y.encoding['_FillValue'] = None
    
    print("\nExporting...")
    output_file = os.path.splitext(input_file)[0] + f" x{suffix}.nc"
    ds2.to_netcdf(output_file)
    


###############################################################################
# Complete CWatM climatic variables
def secondary_era5_climvar(data):
    """
    This function computes the secondary data from ERA5-Land data, such as:
        - crop and water standard ETP from pan evaporation
        - wind speed from U- and V-components
        - relative humidity from T°, P and dewpoint

    Parameters
    ----------
    data : filepath or xarray.dataset (or xarray.dataarray)
        Main dataset used to generate secondary quantities.

    Returns
    -------
    None. Generates intended files.

    """
    
    # ---- Load main dataset
    data_ds = geo.load_any(data, decode_coords = 'all', decode_times = True)
    var = geo.main_var(data_ds)
    
    # ---- Corrections
    if var == 'pev': 
        ETref, EWref = compute_Erefs_from_Epan(data_ds)
        geo.export(ETref, ' ET0crop'.join(os.path.splitext(data_ds)))
        geo.export(EWref, ' EW0'.join(os.path.splitext(data_ds)))
    
    elif var in ['u10', 'v10']:
        if var == 'u10': 
            v10 = input("Filepath to V-component of wind")
            u10 = data_ds
            
        elif var == 'v10':
            u10 = input("Filepath to U-component of wind")
            v10 = data_ds
        
        wind_speed_ds = compute_wind_speed(u10, v10)
        geo.export(wind_speed_ds, ' wind_speed'.join(os.path.splitext(data_ds)))
    
    elif var == 'rh':
        dewpoint_file = input("Filepath to dewpoint data: ")
        temperature_file = input("Filepath to 2m mean temperature data: ")
        pressure_file = input("Filepath to surface pressurce data: ")
        rhs_ds = compute_relative_humidity(
            dewpoint_input_file = dewpoint_file, 
            temperature_input_file = temperature_file,
            pressure_input_file = pressure_file,
            method = "Sonntag"
            )
        geo.export(rhs_ds, ' Relative humidity'.join(os.path.splitext(data_ds)))


#%% main
if __name__ == "__main__":
    # Format the inputs (assumed to be strings) into floats
    sys.argv[1] = float(sys.argv[1])
    sys.argv[2] = float(sys.argv[2])
