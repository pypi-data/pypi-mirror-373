# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 16:58:10 2024

@author: Alexandre Kenshilik Coche
@contact: alexandre.co@hotmail.fr

download.py est un ensemble de fonctions permettant le téléchargement
automatique de données françaises nécessaires à la modélisation 
hydrologique des socio-écosystèmes.
Cet outil a notamment vocation à regrouper les données classiques nécessaires
au modèle CWatM utilisé dans le cadre de la 
méthodologie Eau et Territoire (https://eau-et-territoire.org ).
"""

#%% IMPORTATIONS
import os
import re
import requests
import datetime
from io import (BytesIO, StringIO)
import gzip
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import xarray as xr
xr.set_options(keep_attrs = True)
from geop4th import geobricks as geo
from geop4th.workflows.standardize import standardize_fr as stzfr


#%% Utilitaries to check if a request is valid
def valid_request(response, 
                  file_format = 'geojson', 
                  prev_frame = None):
    """
    Utilitary to check if a request is valid.

    Parameters
    ----------
    response : request.response
        `request` object that contains a server's response to an HTTP request.
        This ``response`` variable can be obtained with ``requests.get(<url>)``
    file_format : {'csv', 'json', 'geojson'}, default 'geojson'
        File format in which the data will be retrieved.
    prev_frame : pandas.DataFrame or geopandas.GeoDataFrame, optional
        Frame used for recurrence run (when request results are on several pages)

    Returns
    -------
    isvalid : bool
        Flag indicating if the request has succeeded.
    frame : pandas.DataFrame of geopandas.GeoDataFrame
        Frame contaning the downloaded values.
        If ``file_format`` is 'geojson', returns a geopandas.GeoDataFrame, otherwise
        return a pandas.DataFrame (non-geospatialized data).

    """
    isvalid = False
    frame = prev_frame
    
    if (response.status_code == 200): # all correct, one single page
        _, frame = valid_single_request(response, file_format)
    
    elif (response.status_code == 206): # correct but results are on several pages
        isvalid, frame = valid_single_request(response, file_format)
        
        # Safeguard preventing technical limitations of BNPE API (max request size)
        # BNPE API can not handle more than 20000 results in one request
        if 'last' in response.links:
            page_pattern = re.compile("page=(\d*)")
            n_page = page_pattern.findall(response.links['last']['url'])
            if len(n_page) > 0:
                n_results = int(n_page[0]) * frame.shape[0]
                if n_results > 20000:
                    print(f"\nErr: Up to {n_results} results were asked but BNPE API cannot retrieve more than 20000 results in one request. If you passed a `masks` argument, please provide smaller masks.")
                    return False, None
        
        if prev_frame is not None:
            frame = pd.concat([prev_frame, frame], axis = 0, ignore_index = True).drop_duplicates()
        
        if 'next' in response.links:
            response = requests.get(response.links['next']['url'])
            _, frame = valid_request(response, file_format, 
                                           prev_frame = frame)
        
    elif (response.status_code == 400):
        print("Err: Incorrect request")
    elif (response.status_code == 401):
        print("Err: Unauthorized")
    elif (response.status_code == 403):
        print("Err: Forbidden")
    elif (response.status_code == 404):
        print("Err: Not Found")
    elif (response.status_code == 500):
        print("Err: Server internal error")
    
    # if frame is not None
    if isinstance(frame, pd.DataFrame):
        isvalid = True
        
    return isvalid, frame
        

def valid_single_request(response, 
                         file_format = 'geojson'):
    """
    Utilitary to check if a request is valid.

    Parameters
    ----------
    response : request.response
        `request` object that contains a server's response to an HTTP request.
        This ``response`` variable can be obtained with ``requests.get(<url>)``
    file_format : {'csv', 'json', 'geojson'}, default 'geojson'
        File format in which the data will be retrieved.

    Returns
    -------
    isvalid : bool
        Flag indicating if the request has succeeded.
    frame : pandas.DataFrame of geopandas.GeoDataFrame
        Frame contaning the downloaded values.
        If ``file_format`` is 'geojson', returns a geopandas.GeoDataFrame, otherwise
        return a pandas.DataFrame (non-geospatialized data).

    """
    
    # ---- Determine validity of downloaded data
    isvalid = False
    if file_format == 'csv':
        if response.text != '': # not empty
            isvalid = True
    elif file_format in ['json', 'geojson']:
        if response.json()['count'] != 0: # not empty
            isvalid = True
    
    if isvalid:  
        # ---- Retrieve results as a dataframe 
        # Save data content into a DataFrame (or a GeoDataFrame)
        if file_format == 'csv':
            frame = pd.read_csv(BytesIO(response.content), sep=";")
        elif file_format == 'geojson':
            # For some datasets, the 'GeoJSON' format option is not available,
            # only classic JSON is retrieved
            # In these cases, if the user requires a GeoJSON, the JSON dict
            # needs to be converted to GeoJSON before export :
                
            if 'type' in response.json():
                if response.json()['type'] == 'FeatureCollection':
                    # Response content is truly a GeoJSON
                    json_to_geojson = False
                else:
                    json_to_geojson = True
            
            else:
                json_to_geojson = True
            
            if json_to_geojson:
                # Additional step of georefencing are necessary    
                json_df = pd.DataFrame.from_dict(response.json()['data'])
                geometry = [Point(xy) for xy in zip(json_df.longitude, 
                                                    json_df.latitude)]
                frame = gpd.GeoDataFrame(
                    json_df,
                    crs = 4326,
                    geometry = geometry)
                
            else:
                frame = gpd.read_file(response.text, driver='GeoJSON')
            
        elif file_format == 'json':
# =============== useless =====================================================
#                     data_stations = pd.DataFrame.from_dict(
#                         {i: response.json()['data'][i] for i in range(len(response.json()['data']))},
#                         orient = 'index')
# =============================================================================
            frame = pd.DataFrame.from_dict(response.json()['data'])                
        
    else:
        frame = None
    
    return isvalid, frame


#%% BNPE (Données de prélèvements)
def bnpe(*, dst_folder, 
         start_year = None, 
         end_year = None, 
         masks = None, 
         departments = None, 
         communes = None, 
         file_formats = 'geojson'):
    """
    Function to facilitate the downloading of French water withdrawal data from BNPE API.

    Parameters
    ----------
    dst_folder : str or pathlib.Path
        Destination folder in which the downloaded data will be stored.
    start_year : int, optional
        Year from which the data will be retrieved.
    end_year : int, optional
        Year until which the data will be retrieved.
    masks : list of-, or single element among str, pathlib.Path, xarray.Dataset, xarray.DataArray or geopandas.GeoDataFrame, optional
        Mask on which the data will be retrieved.
        At least one parameter among ``masks``, ``departments`` or ``communes``
        should be passed.
    departments : int or list of int, optional
        INSEE code(s) of department(s) for which data will be retrieved.
        At least one parameter among ``masks``, ``departments`` or ``communes``
        should be passed.
    communes : int or list of int, optional
        INSEE code(s) of commune(s) for which data will be retrieved.
        At least one parameter among ``masks``, ``departments`` or ``communes``
        should be passed.
    file_formats : str or list of str, {'csv', 'json', 'geojson'}, default 'geojson'
        File format in which the data will be retrieved.

    Returns
    -------
    None. Downloaded data is stored in ``dst_folder``

    """
    
    # ---- Argument retrieving    
    # Safeguard
    if (departments is None) & (communes is None) & (masks is None):
        print("Err: It is required to specify at least one area with the arguments `departments` or `communes` or `masks`")
        return
    
    if start_year is None:
        start_year = 2008
        if end_year is None:
            end_year = datetime.datetime.today().year
    if isinstance(start_year, (str, float)):
        start_year = int(start_year)
    
    if end_year is None: # and start_year is not None, see previous case
        years = [start_year]
    else:
        if isinstance(end_year, (str, float)):
            end_year = int(end_year)
        years = list(range(start_year, end_year + 1))
    
    if masks is not None:
        if isinstance(masks, tuple):
            masks = list(masks)
        elif not isinstance(masks, list):
            masks = [masks]
    
    if departments is not None:
        if isinstance(departments, (str, float)):
            departments = [int(departments)]
        elif isinstance(departments, int):
            departments = [departments]
        elif isinstance(departments, tuple):
            departments = list(departments)
    
    if communes is not None:
        if isinstance(communes, (str, float)):
            communes = [int(communes)]
        elif isinstance(communes, int):
            communes = [communes]
        elif isinstance(communes, tuple):
            communes = list(communes)
    
    if isinstance(file_formats, str):
        file_formats = [file_formats]
    for i in range(0, len(file_formats)):
        # file_formats = file_formats.replace('.', '')
        if file_formats[i][0] == '.': file_formats[i] = file_formats[i][1:]
    
    outdir = os.path.join(dst_folder, "originaux")
    if not os.path.exists(outdir): os.makedirs(outdir)
    
    outdir_ouvrages = os.path.join(dst_folder, "originaux", "ouvrages")
    if not os.path.exists(outdir_ouvrages): os.makedirs(outdir_ouvrages)
    
    # ---- Requests
    print("\nDownloading...")
    for y in years:
        y = int(y)
        print(f"\n   . {y}")
        
        if departments is not None:
            for d in departments:
                d = f"{d:02.0f}" # format '00'
                
                for f in file_formats:
                    if f == 'csv':
                        url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques.csv?annee={y}&code_departement={d}&size=5000"
                        outpath = os.path.join(outdir, f"dpmt{d}_{y}.csv")
                    elif f == 'geojson':
                        url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques?annee={y}&code_departement={d}&format=geojson&size=5000"
                        outpath = os.path.join(outdir, f"dpmt{d}_{y}.json")
                    elif f == 'json':
                        url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques?annee={y}&code_departement={d}&size=5000"
                        outpath = os.path.join(outdir, f"dpmt{d}_{y}.json")
                    
                    response = requests.get(url)
                    
                    isvalid, frame = valid_request(response, f)
                    if isvalid:
                        # Export
                        if f == 'csv':
                            geo.export(frame, outpath, sep = ';', encoding = 'utf-8', index = False)
                        else:
                            geo.export(frame, outpath)
                                
        
        if communes is not None:
            for c in communes:
                c = f"{c:<05.0f}" # format '000000'
                
                for f in file_formats:
                    if f == 'csv':
                        url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques.csv?annee={y}&code_commune_insee={c}&size=5000"
                        outpath = os.path.join(outdir, f"cmne{c}_{y}.csv")
                    elif f == 'geojson':
                        url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques?annee={y}&code_commune_insee={c}&format=geojson&size=5000"
                        outpath = os.path.join(outdir, f"cmne{c}_{y}.json")
                    elif f == 'json':
                        url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques?annee={y}&code_commune_insee={c}&size=5000"
                        outpath = os.path.join(outdir, f"cmne{c}_{y}.json")
                    
                    response = requests.get(url)
            
                    isvalid, frame = valid_request(response, f)
                    if isvalid:
                        # Export
                        if f == 'csv':
                            geo.export(frame, outpath, sep = ';', encoding = 'utf-8', index = False)
                        else:
                            geo.export(frame, outpath)
                            
        if masks is not None:
            i_mask = 0
            for m in masks:
                i_mask += 1
                mask_ds = geo.load_any(m)
                mask_ds = geo.reproject(mask_ds, dst_crs = 4326) 
                
                for f in file_formats:
                    if f == 'csv':
                        url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques.csv?annee={y}&bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&size=5000"
                        outpath = os.path.join(outdir, f"mask{i_mask}_{y}.csv")
                    elif f == 'geojson':
                        url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques?annee={y}&bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&format=geojson&size=5000"
                        outpath = os.path.join(outdir, f"mask{i_mask}_{y}.json")
                    elif f == 'json':
                        url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques?annee={y}&bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&size=5000"
                        outpath = os.path.join(outdir, f"mask{i_mask}_{y}.json")
                    
                    response = requests.get(url)
            
                    isvalid, frame = valid_request(response, f)
                    
# ======= {draft} to automatically handle too large requests ==================
#                     isvalid, frame, exceeds = valid_request(response, f)
#                     
#                     if exceeds:
#                         masks = [*masks[0:i_mask-1], split(masks[i_mask-1]), *masks[i_mask:]]
#                         bnpe(dst_folder = dst_folder, start_year = start_year, 
#                              end_year = end_year, masks = masks, 
#                                  departments = departments, communes = communes, 
#                                  file_formats = file_formats)
#                         return
# =============================================================================
                    
                    if isvalid:
                        # In the `mask` case, the data is clipped to the mask
                        if isinstance(frame, gpd.GeoDataFrame):
                            frame = geo.reproject(frame, mask = m)
                        else: # frame is only a pd.DataFrame
                            # first frame is converted to a GeoDataFrame
                            geometry = [Point(xy) for xy in zip(frame.longitude, 
                                                                frame.latitude)]
                            gdf = gpd.GeoDataFrame(
                                frame,
                                crs = 4326,
                                geometry = geometry)
                            # Then it is clipped
                            gdf = geo.reproject(gdf, mask = m)
                            # Finally it is converted back to a DataFrame
                            frame = pd.DataFrame(gdf.drop(columns = 'geometry'))

                        # Export
                        if f == 'csv':
                            geo.export(frame, outpath, sep = ';', encoding = 'utf-8', index = False)
                        else:
                            geo.export(frame, outpath)
                
    # Infos sur ouvrage
    if departments is not None:
        for d in departments:
            d = f"{d:02.0f}" # format '00'

            for f in file_formats:
                if f == 'csv':
                    url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/ouvrages.csv?code_departement={d}&size=5000"
                    outpath = os.path.join(outdir_ouvrages, f"dpmt{d}_ouvrages.csv")
                elif f == 'geojson':
                    url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/ouvrages?code_departement={d}&format=geojson&size=5000"
                    outpath = os.path.join(outdir_ouvrages, f"dpmt{d}_ouvrages.json")
                elif f == 'json':
                    url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/ouvrages?code_departement={d}&size=5000"
                    outpath = os.path.join(outdir_ouvrages, f"dpmt{d}_ouvrages.json")
                
                response = requests.get(url)
                
                isvalid, frame = valid_request(response, f)
                if isvalid:
                    # Export
                    if f == 'csv':
                        geo.export(frame, outpath, sep = ';', encoding = 'utf-8', index = False)
                    else:
                        geo.export(frame, outpath)
        
    if communes is not None:
        for c in communes:
            c = f"{c:<05.0f}" # format '000000'
            
            for f in file_formats:
                if f == 'csv':
                    url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/ouvrages.csv?code_commune_insee={c}&size=5000"
                    outpath = os.path.join(outdir_ouvrages, f"cmne{c}_ouvrages.csv")
                elif f == 'geojson':
                    url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/ouvrages?code_commune_insee={c}&format=geojson&size=5000"
                    outpath = os.path.join(outdir_ouvrages, f"cmne{c}_ouvrages.json")
                elif f == 'json':
                    url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/ouvrages?code_commune_insee={c}&size=5000"
                    outpath = os.path.join(outdir_ouvrages, f"cmne{c}_ouvrages.json")
                
                response = requests.get(url)
                
                isvalid, frame = valid_request(response, f)
                if isvalid:
                    # Export
                    if f == 'csv':
                        geo.export(frame, outpath, sep = ';', encoding = 'utf-8', index = False)
                    else:
                        geo.export(frame, outpath)
                        
    if masks is not None:
        i_mask = 0
        for m in masks:
            i_mask += 1
            mask_ds = geo.load_any(m)
            mask_ds = geo.reproject(mask_ds, dst_crs = 4326) 
            
            for f in file_formats:
                if f == 'csv':
                    url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/ouvrages.csv?bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&size=5000"
                    outpath = os.path.join(outdir_ouvrages, f"mask{i_mask}_ouvrages.csv")
                elif f == 'geojson':
                    url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/ouvrages?bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&format=geojson&size=5000"
                    outpath = os.path.join(outdir_ouvrages, f"mask{i_mask}_ouvrages.json")
                elif f == 'json':
                    url = rf"https://hubeau.eaufrance.fr/api/v1/prelevements/referentiel/ouvrages?bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&size=5000"
                    outpath = os.path.join(outdir_ouvrages, f"mask{i_mask}_ouvrages.json")
                
                response = requests.get(url)
                
                isvalid, frame = valid_request(response, f)
                
                if isvalid:
                    # In the `mask` case, the data is clipped to the mask
                    if isinstance(frame, gpd.GeoDataFrame):
                        frame = geo.reproject(frame, mask = m)
                    else: # frame is only a pd.DataFrame
                        # first frame is converted to a GeoDataFrame
                        geometry = [Point(xy) for xy in zip(frame.longitude, 
                                                            frame.latitude)]
                        gdf = gpd.GeoDataFrame(
                            frame,
                            crs = 4326,
                            geometry = geometry)
                        # Then it is clipped
                        gdf = geo.reproject(gdf, mask = m)
                        # Finally it is converted back to a DataFrame
                        frame = pd.DataFrame(gdf.drop(columns = 'geometry'))
                
                    # Export
                    if f == 'csv':
                        geo.export(frame, outpath, sep = ';', encoding = 'utf-8', index = False)
                    else:
                        geo.export(frame, outpath)
                        

#%% Hydrometry (Mesures de débits)
def hydrometry(*, dst_folder, 
               masks, 
               start_year, 
               end_year = None, 
               quantities = 'QmnJ', 
               file_formats = 'geojson'):
    """
    Function to facilitate the downloading of French hydrometry data from EauFrance API.

    Parameters
    ----------
    dst_folder : str or pathlib.Path
        Destination folder in which the downloaded data will be stored.
    masks : list of-, or single element among str, pathlib.Path, xarray.Dataset, xarray.DataArray or geopandas.GeoDataFrame, optional
        Mask on which the data will be retrieved.
    start_year : int, optional
        Year from which the data will be retrieved.
    end_year : int, optional
        Year until which the data will be retrieved.
    quantities : str or list of str, default 'QmnJ'
    
        - 'QmnJ': average daily discharge
        - 'QmM': average monthly discharge
        - 'HIXM': maximum instant height per month
        - 'HIXnJ': maximum instant height per day
        - 'QINM': minimum instant discharge per month
        - 'QINnJ': minimum instant discharge per day
        - 'QixM': maximum instant discharge per month
        - 'QIXnJ': maximum instant discharge per day
    
    file_formats : str or list of str, {'csv', 'json', 'geojson'}, default 'geojson'
        File format in which the data will be retrieved.

    Returns
    -------
    None. Downloaded data is stored in ``dst_folder``
    """

    # ---- Argument retrieving
    if isinstance(start_year, (str, float)):
        start_year = int(start_year)
    if end_year is None:
        years = [start_year]
    else:
        if isinstance(end_year, (str, float)):
            end_year = int(end_year)
        years = list(range(start_year, end_year + 1))
    
    if masks is not None:
        if isinstance(masks, tuple):
            masks = list(masks)
        elif not isinstance(masks, list):
            masks = [masks]
    
    if isinstance(file_formats, str):
        file_formats = [file_formats]
    for i in range(0, len(file_formats)):
        # file_formats = file_formats.replace('.', '')
        if file_formats[i][0] == '.': file_formats[i] = file_formats[i][1:]
    
    if isinstance(quantities, str):
        quantities = [quantities]
    
    outdir = os.path.join(dst_folder, "originaux")
    if not os.path.exists(outdir): os.makedirs(outdir)
    
    outdir_stations = os.path.join(dst_folder, "originaux", "stations")
    if not os.path.exists(outdir_stations): os.makedirs(outdir_stations)

    # ---- Requests
    print("\nDownloading...")    
                           
    i_mask = 0
    for m in masks:
        i_mask += 1
        mask_ds = geo.load_any(m)
        mask_ds = geo.reproject(mask_ds, dst_crs = 4326) 
        
        # List of stations 
        for f in file_formats:
            if f == 'csv':
                url = rf"https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations.csv?bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&size=10000"
                outpath = os.path.join(outdir_stations, f"mask{i_mask}_stations.csv")
            elif f == 'geojson':
                url = url = rf"https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations?bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&format=geojson&size=10000"
                outpath = os.path.join(outdir_stations, f"mask{i_mask}_stations.json")
            elif f == 'json':
                url = url = rf"https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations?bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&size=10000"
                outpath = os.path.join(outdir_stations, f"mask{i_mask}_stations.json")
            
            response = requests.get(url)
            
            isvalid, data_stations = valid_request(response, f)
            
            if isvalid:
                # Data is clipped to the mask
                if isinstance(data_stations, gpd.GeoDataFrame):
                    data_stations = geo.reproject(data_stations, mask = m)
                else: # frame is only a pd.DataFrame
                    # first frame is converted to a GeoDataFrame
                    data_stations.loc[:, ['longitude', 'latitude']] = data_stations['coordLatLon'].str.split(',', expand = True).rename(columns = {0: 'latitude', 1: 'longitude'}).astype(float)
                    geometry = [Point(xy) for xy in zip(data_stations.longitude, 
                                                        data_stations.latitude)]
                    gdf = gpd.GeoDataFrame(
                        data_stations,
                        crs = 4326,
                        geometry = geometry)
                    # Then it is clipped
                    gdf = geo.reproject(gdf, mask = m)
                    # Finally it is converted back to a DataFrame
                    data_stations = pd.DataFrame(gdf.drop(columns = ['geometry', 'latitude', 'longitude']))
                
                # Export
                if f == 'csv':
                    geo.export(data_stations, outpath, sep = ';', encoding = 'utf-8', index = False)
                else:
                    geo.export(data_stations, outpath)
            
        # Discharge data
        for y in years:
            y = int(y)
            print(f"   . {y}")
            
            for station_id in data_stations['code_station']:

                for f in file_formats:
                    for q in quantities:
                        if f == 'csv':                    
                            url = rf"https://hubeau.eaufrance.fr/api/v2/hydrometrie/obs_elab.csv?code_entite={station_id}&bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&date_debut_obs_elab={y}-01-01&date_fin_obs_elab={y}-12-31&grandeur_hydro_elab={q}&size=20000"
                            outpath = os.path.join(outdir, f"{q}_{station_id}_mask{i_mask}_{y}.csv")
# ============ apparently format option is not available ======================
#                         elif f == 'geojson':
#                             url = rf"https://hubeau.eaufrance.fr/api/v2/hydrometrie/obs_elab?code_entite={station_id}&bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&date_debut_obs_elab={y}-01-01&date_fin_obs_elab={y}-12-31&grandeur_hydro_elab={q}&format=geojson&size=20000"
#                             outpath = os.path.join(outdir, f"{q}_{station_id}_mask{i_mask}_{y}.json")
# =============================================================================
                        elif f in ['geojson', 'json']:
                            url = rf"https://hubeau.eaufrance.fr/api/v2/hydrometrie/obs_elab?code_entite={station_id}&bbox={mask_ds.total_bounds[0]}&bbox={mask_ds.total_bounds[1]}&bbox={mask_ds.total_bounds[2]}&bbox={mask_ds.total_bounds[3]}&date_debut_obs_elab={y}-01-01&date_fin_obs_elab={y}-12-31&grandeur_hydro_elab={q}&size=20000"
                            outpath = os.path.join(outdir, f"{q}_{station_id}_mask{i_mask}_{y}.json")
                        
                        response = requests.get(url)
                        
                        isvalid, frame = valid_request(response, f)
                        
                        if isvalid:
                            # Data is clipped to the mask
                            if isinstance(frame, gpd.GeoDataFrame):
                                frame = geo.reproject(frame, mask = m)
                            else: # frame is only a pd.DataFrame
                                # first frame is converted to a GeoDataFrame
                                geometry = [Point(xy) for xy in zip(frame.longitude, 
                                                                    frame.latitude)]
                                gdf = gpd.GeoDataFrame(
                                    frame,
                                    crs = 4326,
                                    geometry = geometry)
                                # Then it is clipped
                                gdf = geo.reproject(gdf, mask = m)
                                # Finally it is converted back to a DataFrame
                                frame = pd.DataFrame(gdf.drop(columns = 'geometry'))
                        
                            # Export
                            if f == 'csv':
                                geo.export(frame, outpath, sep = ';', encoding = 'utf-8', index = False)
                            else:
                                geo.export(frame, outpath)



#%% SIM2 (Données climatiques de réanalyse historique MétéoFrance)
def sim2(*, var_list, 
         dst_folder: str,
         first_year: int=None, 
         last_year: int=None,
         extension = '.nc', 
         mask: str=None):
    """
    Depuis le 13/12/2023 ces données sont en accès ouvert sur https://meteo.data.gouv.fr
    (onglet "Données climatologiques de référence pour le changement climatique",
    puis "Données changement climatique - SIM quotidienne" : 
    https://meteo.data.gouv.fr/datasets/6569b27598256cc583c917a7 )
    
    Parameters
    ----------
    var_list : iterable
        List of variable names.
        Works with SIM2 variable names: 'DRAINC_Q' | 'RUNC_Q' | 'EVAP_Q' | 'PRETOT_Q' | 'T_Q' ...
        The '_Q' is optional ('DRAINC', 'RUNC'... also work)
    dst_folder : str or pathlib.Path
        Path to the output folder containing the clipped SIM2 netCDF files.
        According to the files already present in this folder, only the necessary
        complementary files will be downloaded.
    first_year : int, optional
        Data will be extracted from 1st January of first_year to 31st December of last_year.
        If None, the earliest available date will be considered.
    last_year : int, optional
        End date of data to be extracted. 
        If None, the current date of the day will be used instead.
    extension : {'.nc', '.csv'}, default '.nc'
        Output file type.
    mask : str or pathlib.Path, optional
        Shapefile path to indicate how to clip
        the CSV or netCDF files that will be exported to the ``dst_folder`` folder.
        Note: The only purpose of using ``mask`` at this step is to save space on disk.

    Returns
    -------
    None. Create or update the netcdf files.
    """

    # ---- Initialization
    print("\nInitializing...")
    # Variables
# =============================================================================
#     if ('PRETOT' in var_list) | ('PRETOT_Q' in var_list):
#         var_list = var_list + ['PRENEI', 'PRELIQ']
# =============================================================================
    for i in range(0, len(var_list)):
        if var_list[i][-2:] != '_Q':
            var_list[i] = var_list[i] + '_Q'
    var_sublist = []
    
    # Folders
    if not os.path.isdir(dst_folder):
        os.makedirs(dst_folder)
    if extension[0] != '.': extension = '.' + extension
    
    # Dates
    if first_year is None:
        first_year = 1958
    first_date = pd.to_datetime(f"{first_year}-01-01", format = "%Y-%m-%d")
    
    if last_year is None:
        last_date = pd.to_datetime('today').normalize()
        last_year = last_date.year
    else:
        last_date = pd.to_datetime(f"{last_year}-12-31", format = "%Y-%m-%d")
    
# =============================================================================
#     # Mask
#     if mask is not None:
#         if not os.path.splitext(mask)[-1] == '.shp':
#             print("Err: The mask value should point to a .shp file. Otherwise, use mask=None to deactivate clipping")
#             return
# =============================================================================
    
    france_extent = (56000.0, 1613000.0, 1200000.0, 2685000.0) # whole France 
                                                               # limits for SIM2 
                                                               # data in epsg:2154 

    data_to_merge = []

    # ---- Determine which data needs to be downloaded
    # Data already available for each variable 

    local_data = pd.DataFrame(index = var_list, columns = ['file',
                                                           'start_date',
                                                           'end_date',
                                                           'extent'])
    local_data.extent = False

    sim_pattern = re.compile('(.*)_SIM2_')
    _, filelist = geo.get_filelist(dst_folder, extension = extension)
# =============================================================================
#     filelist = [os.path.join(dst_folder, f) \
#                 for f in os.listdir(dst_folder) \
#                     if os.path.isfile(os.path.join(dst_folder, f))]
# =============================================================================
    if len(filelist) > 0: # folder is not empty
        for file in filelist:
            filename = os.path.split(file)[-1]
            sim2_match = sim_pattern.findall(filename)
            var = sim2_match[0].replace("_QUOT", "")
            local_data.loc[var, 'file'] = file
            
            remove_file = False
            if extension == '.csv':
                df_temp = pd.read_csv(os.path.join(dst_folder, file), sep = ';', 
# =============================================================================
#                                       usecols = ['LAMBX', 'LAMBY', 'DATE'] + var_list,
# =============================================================================
                                      header = 0, decimal = '.',
                                      parse_dates = ['DATE'],
                                      # date_format='%Y%m%d', # Not available before pandas 2.0.0
                                      )
                
                # Variables
                if len(set(var_list).intersection(set(df_temp.columns))) < len(var_list):
                    print(f"   Local data {os.path.split(file)[-1]} does not include all desired variables")
                    remove_file = True # the file will be deleted (outside this section)
                
                # Dates
                if pd.date_range(start = df_temp.DATE.iloc[0], 
                                 end = df_temp.DATE.iloc[-1], 
                                 freq = 'D').size == df_temp.DATE.size: # all time values are contiguous
                    local_data.loc[var, 'start_date'] = pd.to_datetime(df_temp.DATE.iloc[0])
                    local_data.loc[var, 'end_date'] = pd.to_datetime(df_temp.DATE.iloc[-1])
            
            elif extension == '.nc':
                with geo.load_any(os.path.join(dst_folder, file), decode_coords = 'all', decode_times = True) as ds_temp:
                    # Dates
                    if pd.date_range(start = ds_temp.time[0].item(), 
                                     end = ds_temp.time[-1].item(), 
                                     freq = 'D').size == ds_temp.time.size: # all time values are contiguous
                        local_data.loc[var, 'start_date'] = pd.to_datetime(ds_temp.time[0].item())
                        local_data.loc[var, 'end_date'] = pd.to_datetime(ds_temp.time[-1].item())
                    # Spatial extent
                    resolution = abs(ds_temp.rio.resolution()[0])
                    ds_extent = np.array(ds_temp.rio.bounds())
                    if mask is not None:
                        mask_gdf = geo.load_any(mask)
                        mask_gdf = geo.reproject(mask_gdf, dst_crs = ds_temp.rio.crs)
                        # mask_extent = mask_gdf.buffer(resolution).total_bounds
                        if isinstance(mask_gdf, gpd.GeoDataFrame):
                            mask_extent = mask_gdf.total_bounds
                        elif isinstance(mask_gdf, xr.Dataset):
                            mask_extent = mask_gdf.rio.bounds()
                        mask_extent[0] = geo.nearest(
                            x = mask_extent[0], x0 = ds_extent[0], 
                            y0 = ds_extent[1], res = resolution)
                        if mask_extent[0] > mask_gdf.total_bounds[0]:
                            mask_extent[0] -= resolution
                        mask_extent[1] = geo.nearest(
                            y = mask_extent[1], x0 = ds_extent[0],
                            y0 = ds_extent[1], res = resolution)
                        if mask_extent[1] > mask_gdf.total_bounds[1]:
                            mask_extent[1] -= resolution
                        mask_extent[2] = geo.nearest(
                            x = mask_extent[2], x0 = ds_extent[0],
                            y0 = ds_extent[1], res = resolution)
                        if mask_extent[2] < mask_gdf.total_bounds[2]:
                            mask_extent[2] += resolution
                        mask_extent[3] = geo.nearest(
                            y = mask_extent[3], x0 = ds_extent[0],
                            y0 = ds_extent[1], res = resolution)
                        if mask_extent[3] < mask_gdf.total_bounds[3]:
                            mask_extent[3] += resolution
                            
                    else:
                        mask_extent = france_extent # whole France
                    
                    if (ds_extent[0:2] <= mask_extent[0:2]).any() | (ds_extent[2:4] >= mask_extent[2:4]).any() :
                        local_data.loc[var, 'extent'] = True
                    else:
                        print(f"   Local data {os.path.split(file)[-1]} does not cover desired spatial extent")
                        remove_file = True # the file will be deleted (outside this 'with' section)
            
            if remove_file:
                os.remove(os.path.join(dst_folder, file))
                   
        # local_data.iloc[:, 0:3][local_data.extent == True] = np.nan
        local_data.loc[local_data.index[local_data.extent == False], local_data.columns[0:3]] = np.nan
        
    
    # ---- Download
    print("\nDownloading...")
    # Download only the necessary data files from MeteoFrance API
    # Until the access to SIM2 data is implemented through the Météo-France's
    # API (https://portail-api.meteofrance.fr), the current stable urls
    # are used.
    
    stable_urls = {
        'QUOT_SIM2_1958-1959': ('https://www.data.gouv.fr/fr/datasets/r/5dfb33b3-fae5-4d0e-882d-7db74142bcae', 
                                0.16, pd.to_datetime('1958-08-01', format = "%Y-%m-%d"),
                                pd.to_datetime('1959-12-31', format = "%Y-%m-%d")),
        'QUOT_SIM2_1960-1969': ('https://www.data.gouv.fr/fr/datasets/r/eb0d6e42-cee6-4d7c-bc5b-646be4ced72e', 
                                1.1, pd.to_datetime('1960-01-01', format = "%Y-%m-%d"),
                                pd.to_datetime('1969-12-31', format = "%Y-%m-%d")),
        'QUOT_SIM2_1970-1979': ('https://www.data.gouv.fr/fr/datasets/r/33417617-c0dd-4513-804e-c3f563cb81b4', 
                                1.1, pd.to_datetime('1970-01-01', format = "%Y-%m-%d"),
                                pd.to_datetime('1979-12-31', format = "%Y-%m-%d")),
        'QUOT_SIM2_1980-1989': ('https://www.data.gouv.fr/fr/datasets/r/08ad5936-cb9e-4284-a6fc-36b29aca9607', 
                                1.1, pd.to_datetime('1980-01-01', format = "%Y-%m-%d"),
                                pd.to_datetime('1989-12-31', format = "%Y-%m-%d")),
        'QUOT_SIM2_1990-1999': ('https://www.data.gouv.fr/fr/datasets/r/ad584d65-7d2d-4ff1-bc63-4f93357ed196', 
                                1.1, pd.to_datetime('1990-01-01', format = "%Y-%m-%d"),
                                pd.to_datetime('1999-12-31', format = "%Y-%m-%d")),
        'QUOT_SIM2_2000-2009': ('https://www.data.gouv.fr/fr/datasets/r/10d2ce77-5c3b-44f8-bb46-4df27ed48595', 
                                1.1, pd.to_datetime('2000-01-01', format = "%Y-%m-%d"),
                                pd.to_datetime('2009-12-31', format = "%Y-%m-%d")),
        'QUOT_SIM2_2010-2019': ('https://www.data.gouv.fr/fr/datasets/r/da6cd598-498b-4e39-96ea-fae89a4a8a46', 
                                1.1, pd.to_datetime('2010-01-01', format = "%Y-%m-%d"),
                                pd.to_datetime('2019-12-31', format = "%Y-%m-%d")),
        'QUOT_SIM2_latest_period': ('https://www.data.gouv.fr/fr/datasets/r/92065ec0-ea6f-4f5e-8827-4344179c0a7f', 
                                    1.1, pd.to_datetime('2020-01-01', format = "%Y-%m-%d"),
                                    (pd.to_datetime('today').normalize() - pd.Timedelta(1, 'D')).replace(day = 1) - pd.Timedelta(1, 'D')),
        'QUOT_SIM2_latest_days': (#'https://www.data.gouv.fr/fr/datasets/r/ff8e9fc6-d269-45e8-a3c3-a738195ea92a',
                                  'https://www.data.gouv.fr/fr/datasets/r/adcca99a-6db0-495a-869f-40c888174a57',
                                   0.1, (pd.to_datetime('today').normalize() - pd.Timedelta(1, 'D')).replace(day = 1),
                                   pd.to_datetime('today').normalize() - pd.Timedelta(1, 'D')),
        }
    
    available_data = pd.DataFrame.from_dict(
        data = stable_urls, 
        orient = 'index', 
        columns = ['url', 'size_Go', 'start_date', 'end_date'])
    
    ### Identify which files will be needed
    # -------------------------------------
    # If there is no netcdf file already
    if local_data.file.isnull().values.any():
        # Then all the data files will be downloaded
        to_download = available_data.index[
            (available_data.end_date > first_date) \
                 & (available_data.start_date < last_date)]
    else:
        # The "core period" is the period that is covered by local data for 
        # specified variables
        min_core_date = local_data.start_date[var_list].max()
        max_core_date = local_data.end_date[var_list].min()
        
        if first_date < min_core_date:
            inf_idx = available_data.index[(available_data.start_date < min_core_date) & (available_data.end_date > first_date)]
        else:
            inf_idx = []
        
        if last_date > max_core_date:
            sup_idx = available_data.index[(available_data.end_date > max_core_date) & (available_data.start_date < last_date)]
        else:
            sup_idx = []
        
        to_download = list(set(inf_idx).union(set(sup_idx)))
    
    # Files to download to cover the times
    # (Note that if the specified spatial extent is not covered, the files have been previously deleted in __init__())
    if len(to_download) > 0:
        # print(f"The following .csv datasets will be downoladed: {', '.join([dataname + '(' + self.available_data.loc[dataname, 'size_Go'] + ')' for dataname in to_download])}")
        ram_space = available_data.loc[to_download, 'size_Go'].max()
        disk_space = available_data.loc[to_download, 'size_Go'].sum()/2.5*len(var_list) \
            - sum(os.path.getsize(os.path.join(dst_folder, f)) \
                  for f in os.listdir(dst_folder) \
                      if os.path.isfile(os.path.join(dst_folder, f)))/1073741824 
        disk_space = np.max([0, disk_space])
        print(f"The following CSV datasets will be downloaded to RAM and exported to netCDF files to cover the required period and area: {', '.join(to_download)}")
        print(f"(required RAM: < {ram_space} Go, required space: < {disk_space:.2f} Go)")
      
    ### Download the required files
    # -----------------------------
    if len(to_download) > 0:
        for dataname in to_download: 
            print(f"\nDownloading {dataname}...")
            print("   (can take several min, depending on internet speed)")
            response = requests.get(available_data.loc[dataname, 'url'])
    
            if (response.status_code == 200) & (os.path.splitext(response.url)[-1] != '.tmp'):
                # Decompress gzip content
                with gzip.open(BytesIO(response.content), 'rt') as f:
                    # Determine variables to extract in the current file
                    var_sublist = local_data.loc[var_list].index[
                        (local_data.start_date[var_list] > available_data.loc[dataname, 'start_date']) \
                            | (local_data.end_date[var_list] < available_data.loc[dataname, 'end_date'])]
                    var_sublist = var_sublist.to_list() + local_data[local_data.file.isnull()].index.to_list()  
                    # Replace 'PRETOT_Q' with 'PRELIQ_Q' and 'PRENEI_Q' if needed
                    var_list_csv = []
                    for v in var_list:
                        if v != 'PRETOT_Q':
                            var_list_csv += [v]
                        else:
                            var_list_csv += ['PRELIQ_Q', 'PRENEI_Q']
                    # Read .csv file and export desired variables
                    df = pd.read_csv(f, sep = ';', 
                                     usecols = ['LAMBX', 'LAMBY', 'DATE'] + var_list_csv,
                                     header = 0, decimal = '.',
                                     parse_dates = ['DATE'],
                                     # date_format='%Y%m%d', # Not available before pandas 2.0.0
                                     )
                    df = df[(df.DATE >= first_date) & (df.DATE <= last_date)]
                    
                    # Cumulated values (day 1) are summed from 06:00 UTC (day 1) to 06:00 UTC (day 2)
                    # Therefore, days correspond to Central Standard Time days.
# =============================================================================
#                     df['DATE'] = df['DATE'].tz_localize('Etc/GMT-6')
# =============================================================================

                    if 'PRETOT_Q' in var_list:
                        df['PRETOT_Q'] = df['PRELIQ_Q'] + df['PRENEI_Q']
                        if not 'PRELIQ_Q' in var_list:
                            df.drop(columns = 'PRELIQ_Q', inplace = True)
                        if not 'PRENEI_Q' in var_list:
                            df.drop(columns = 'PRENEI_Q', inplace = True)
                    
                    if extension == '.csv':
                        # Standardization step necessary for further clipping 
                        # (this step is realized in stzfr.sim2(df) when extension == '.nc' (see below))
                        df.rename(columns = {'LAMBX': 'x', 'LAMBY': 'y', 'DATE': 'time'}, inplace = True)
                        df[['x', 'y']] = df[['x', 'y']]*100 # convert hm to m
                        data_to_merge.append(df)
                    
                    elif extension == '.nc':
                        ds = stzfr.sim2(df)
                        data_to_merge.append(ds)

            else:
                print(f"   *****\n   Error while downloading the file {dataname}.csv\n   *****")
                
    else:
        print("No additional original dataset needs to be downloaded.")
        return
    
    
    # Export preparation
    name_pattern = re.compile("(.*)\d{4,6}-\d{4,6}")
    basename = name_pattern.findall(dataname)
    if len(basename) > 0:
        basename = basename[0]
    else:
        basename = 'QUOT_SIM2_'
    outpath = os.path.join(dst_folder, basename + f"{first_year}-{last_year}")
    
    
    if extension == '.csv':
# =============================================================================
#         if mask is not None:
#             print(f"Warning: As `extension` for output is {extension}, the `mask` will not be taken into account.")
#             print("If you want to save the results clipped over the specified mask, please pass `extension = '.nc'`")
# =============================================================================
        
        # ---- Clip data
        clipped_df = []
        
        if mask is not None:
            maskname = os.path.splitext(os.path.split(mask)[-1])[0]
            
            print(f"   _ clipping on {maskname}")
            
            i = 0
            for d in data_to_merge:
                i += 1
                print(f"      . {i}/{len(data_to_merge)}")
                
                clipped_df.append(geo.clip(d, src_crs = 27572, mask = mask))
        
        else:
            clipped_df = data_to_merge
        
        # ---- Merge pandas DataFrames
        print("Merging...")
        merged_df = geo.merge_data(clipped_df)
        
        # Revert temporary corrections on x and y dimension
        merged_df[['x', 'y']] = merged_df[['x', 'y']]/100 # convert hm to m
        merged_df.rename(columns = {'x': 'LAMBX', 'y': 'LAMBY', 'time': 'DATE'}, inplace = True)
        
        # ---- Export
        print("\nExporting...")
        print(f"   _ to {outpath}.csv")
        merged_df.to_csv(outpath + '.csv',
                         sep = ';',
                         header = True,
                         decimal = '.')
        
    elif extension == '.nc':
        # Clip and merge files in folder
        
# =============================================================================
#         if 'PRETOT' in data_to_merge[0]:
#             var_list = var_list + ['PRETOT']
# =============================================================================
        
        for var in data_to_merge[0].data_vars: 
            print(f"\nProcessing {var}...")

            # ---- Clip data
            clipped_ds = []
            
            if mask is not None:
                maskname = os.path.splitext(os.path.split(mask)[-1])[0]
                mask_ds = geo.load_any(mask)
                if isinstance(mask_ds, xr.Dataset):
                    mask_ds = mask_ds.where(mask_ds > 0, drop = True)
                    bounds = mask_ds.rio.bounds()
                    try: mask_crs = mask_ds.rio.crs
                    except: mask_crs = None
                elif isinstance(mask_ds, gpd.GeoDataFrame):
                    bounds = mask_ds.total_bounds
                    try: mask_crs = mask_ds.crs
                    except: mask_crs = None
                
                print(f"   _ clipping on {maskname}")
                
                i = 0
                for d in data_to_merge:
                    i += 1
                    print(f"      . {i}/{len(data_to_merge)}")
                    
                    clipped_ds.append(geo.clip(d[[var]], 
                                               bounds = bounds,
                                               bounds_crs = mask_crs))
            
            else:
                clipped_ds = data_to_merge
            
            # ---- Merge netCDF files
            # Add local files
            _, varfilelist = geo.get_filelist(dst_folder, 
                                              extension = ".nc", 
                                              tag = '^' + var)
            # it is necessary to add '^' before the string so that it will detect
            # only the files that start with var. To avoid confusion between
            # 'T_Q' and 'PRETOT_Q' (which also contains 'T_Q')
            for localfile in varfilelist:
                clipped_ds.append(geo.load_any(os.path.join(dst_folder, localfile)))
            
            print(f"   _ merging {len(clipped_ds)} files")
            merged_ds = geo.merge_data(clipped_ds, update_val = True)
            # update_val = True because sometimes SIM2 original datasets can overlap
            for localfile in varfilelist:
                os.remove(os.path.join(dst_folder, localfile))
            
            # ---- Export
            print("\nExporting...")
            var_outpath = os.path.join(os.path.split(outpath)[0],
                         f"{var}_" +  os.path.split(outpath)[-1]) + ".nc"
            print(f"   _ to {var_outpath}")

            geo.export(merged_ds, var_outpath)



