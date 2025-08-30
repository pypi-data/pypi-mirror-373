# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 16:58:10 2024

@author: Alexandre Kenshilik Coche
@contact: alexandre.co@hotmail.fr

PAGAIE_interface est une interface regroupant les fonctions de geohydroconvert
pertinentes pour géotraiter les données géographiques dans le cadre de la 
méthodologie Eau et Territoire (https://eau-et-territoire.org ).
A la difference de geohydroconvert, trajectoire_toolbox propose une sélection 
des fonctions les plus utiles de geohydroconvert, au sein d'une interface
traduite en Français.
"""

#%% IMPORTATIONS
import os
import re
from functools import wraps
from pathlib import Path
import datetime
import xarray as xr
import pandas as pd
import numpy as np
xr.set_options(keep_attrs = True)
from geop4th import geobricks as geo
from geop4th.workflows.standardize import standardize_fr as stzfr

#%% A DEPLACER !!!
# =============================================================================
# @formating
# def era5(data, *, 
#          mask=None, 
#          bounds=None, 
#          resolution=None, 
#          x0=None, 
#          y0=None,
#          base_template=None, 
#          **rio_kwargs,
#          ):     
#     # ERA5
#     if data_type.casefold().replace(' ', '').replace('-', '') in [
#             "era5", "era5land", "era"]:
#         data_folder, filelist = liste_fichiers(data, extension = '.nc')
# 
#         # outpath = outpath[:-3] # to remove '.nc'
#         outpath = os.path.splitext(filelist[0])[0]
#         outpath = os.path.join(data_folder, outpath)
#         # Corriger les données
#         ds = convertir_cwatm([os.path.join(data_folder, f) for f in filelist], data_type = "ERA5")
#         # Géoréférencer les données
#         ds = georeferencer(data = ds, data_type = "other", crs = 4326)
#         # Compression avec pertes (packing)
#         ds_comp = compresser(ds)
#         exporter(ds_comp, outpath + '_pack' + '.nc')
#         # Reprojections et exports
#         # rio_kwargs['dst_crs'] = 2154
#         for res in resolution:
#             if res is None:
#                 res_suffix = ''
#                 if 'resolution' in rio_kwargs:
#                     rio_kwargs.pop('resolution')
#             else:
#                 res_suffix = f'_{res}m'
#                 rio_kwargs['resolution'] = res
#             n_mask = 0
#             for m in mask:
#                 n_mask += 1
#                 ds_rprj = reprojeter(data = ds, mask = m, bounds = bounds,
#                                      x0 = x0, y0 = y0, base_template = base_template,
#                                      **rio_kwargs)
#                 exporter(ds_rprj, outpath + res_suffix + f'_mask{n_mask}' + '.nc')
#                 # exporter(ds_rprj, outpath + f'_{rundate}' + res_suffix + '.nc') # Pas de rundate car noms des fichiers trop longs...
#         
#         del ds_rprj
#         del ds
#         del ds_comp
# =============================================================================

#%% DECORATOR
def formating(func):
    @wraps(func)
    def wrapper(data, **kwargs):
        
        if 'resolution' not in kwargs:
            kwargs['resolution'] = None
        if 'mask' not in kwargs:
            kwargs['mask'] = None
        
        kwargs['rundate'] = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%M")
        
        if isinstance(kwargs['resolution'], int) or (kwargs['resolution'] is None):
            kwargs['resolution'] = [kwargs['resolution']] # it can therefore be a list of tuples or a list of lists
            
        if not isinstance(kwargs['mask'], list):
            kwargs['mask'] = [kwargs['mask']]
        
        func(data, **kwargs)
        
    return wrapper
    

#%% FILE MANAGEMENT
def infer_outpath(path):
    
    # Safeguard
    try:
        path = Path(path)
    except TypeError as err:
        print(f"TypeError: `path` should be a valid path\n{err}\n")
        raise
        
    if path.is_file():
        stz_pattern = re.compile(".*stz.*")
        if (len(stz_pattern.findall(path.stem)) == 0) & (len(stz_pattern.findall(path.parent.stem)) == 0):
            print("Warning: make sure that the file defined by `path` has been standardized with geop4th standardize functions")
        outpath = path
        
    elif path.is_dir():
        _, filelist = geo.get_filelist(path, tag = 'stz')
        if len(filelist) == 0:
            print(f"Warning: `data` was passed as a folder, but no standardized files have been identified in this folder. Please consider using geop4th standardize functions beforehand. `outpath` is inferred from the first file: {filelist[0]}")
            _, filelist_all = geo.get_filelist(path)
            outpath = path / filelist_all[0]
        elif len(filelist) > 1:
            print(f"Warning: Several files were detected as standardized in the `data` folder. The outpath is inferred from the first file: {filelist[0]}")
            outpath = path / filelist[0]
        else:
            outpath = path / filelist[0]
    
    return outpath
            
            
        
#%% PORTAL FOR FORMATING
def format_data(data, 
                data_name, *, 
                mask=None, 
                bounds=None, 
                resolution=None, 
                x0=None, 
                y0=None,
                base_template=None, 
                **rio_kwargs,
                ):
    
    # ---- Données topographiques
    #%%% BD ALTI 25m
    if data_name.casefold().replace(' ', '') in ['bdalti', 'alti', 'ignalti']:
        return bdalti(data)
    
    # ---- Données climatiques
    #%%% DRIAS-Climat 2022 (netcdf)
    # Données SAFRAN (tas, prtot, rayonnement, vent... ) "EXPLORE2-Climat 2022" 
    elif data_name.casefold().replace(' ', '').replace('-', '') in [
            'drias2022', 'climat2022', 'driasclimat2022']:
        return explore2climat(data)
    
    #%%% DRIAS-Eau 2024 (netcdf)
    # Indicateurs SAFRAN (SWIAV, SSWI-3...) "EXPLORE2-SIM2 2024" 
    elif data_name.casefold().replace(' ', '').replace('-', '') in [
            'sim2024', 'indicateursim2024', 'indicateurssim2024',
            'driaseau2024', 'indicateurdriaseau2024',
            'indicateursdriaseau2024']:
        return explore2eau(data)
    
    #%%% SIM2 (csv to netCDF)
    # Réanalyse historique climatique Safran-Isba(-Modcou) "SIM2" 
    elif data_name.casefold().replace(' ', '').replace('-', '') in [
            'sim2', 'sim', 'safranisba', 'safranisbamodcou',
            ]:
        return sim2(data)
    
    # ---- Données d'usage de l'eau
    #%%% BNPE
    elif data_name.casefold().replace(' ', '').replace('-', '') in [
            "bnpe"]:
        return bnpe(data)
    
    # ---- Données d'occupation des sols
    #%%% OCS SCOT Pays Basque
    elif data_name.casefold().replace(' ', '').replace('-', '') in [
            "ocs", "ocspbs", "ocspaysbasque"]:
        return ocspaysbasque(data)
    
    
#%% FUNCTIONS FOR FORMATING
#%%% Topographic data

@formating
def dem(data, *, 
        mask=None, 
        bounds=None, 
        resolution=None, 
        x0=None, 
        y0=None,
        base_template=None, 
        outpath = None,
        **rio_kwargs,
        ):
    r"""
    Format standardized DEM data for CWatM:
    
    - reproject and clip them into passed ``resolution``, ``mask``, ``dst_crs``, ``x0``, ``y0`` ...
    - generate matching maps of flow directions (DISABLED AT THE MOMENT)
    - generate matching maps of standard deviations of elevation

    Parameters
    ----------
    data : path (str or pathlib.Path), or variable (numpy.ndarray, xarray.Dataset or xarray.DataArray)
        MNT Dataset retrieved from IGN "ALTI" database
        https://geoservices.ign.fr/bdalti
    mask : (list of) str, pathlib.Path, shapely.geometry, xarray.DataArray or geopandas.GeoDataFrame, optional
        Filepath of mask used to clip the data. 
    bounds : iterable or None, optional, default None
        Boundaries of the target domain as a tuple (x_min, y_min, x_max, y_max).
    resolution : (list of) int, optional
        List of resolutions to use for data formating.
    x0: number, optional, default None
        Origin of the X-axis, used to align the reprojection grid. 
    y0: number, optional, default None
        Origin of the Y-axis, used to align the reprojection grid. 
    base_template : str, pathlib.Path, xarray.DataArray or geopandas.GeoDataFrame, optional
        Filepath, used as a template for spatial profile. Supported file formats
        are *.tif*, *.nc* and vector formats supported by geopandas (*.shp*, *.json*, ...).
    outpath : str, optional
        Outpath stem when ``data`` is passed as a GEOP4TH variable instead of a filepath.
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
    None. Generate the formated files, with filepaths derived from ``data`` or from
    ``outpath``.
    
    Examples
    ---------
    >>> cwatm.dem(
        r"E:\Inputs\DEM\IGN\BDALTIV2_folder\BDALTIV2_stz.tif", 
        resolution = [500, 1000], 
        x0 = 0, 
        y0 = 0, 
        dst_crs = 27572, 
        mask = r"E:\Inputs\masks\MyMask.shp"
        )
    Exporting...
       _ Success: The data has been exported to the file 'E:\Inputs\DEM\IGN\BDALTIV2\BDALTIV2_stz_CWATM_1000m_mask1.tif'
    Exporting...
       _ Success: The data has been exported to the file 'E:\Inputs\DEM\IGN\BDALTIV2\ElevationStD_BDALTIV2_stz_CWATM_1000m_mask1.tif'
    Exporting...
       _ Success: The data has been exported to the file 'E:\Inputs\DEM\IGN\BDALTIV2\BDALTIV2_stz_CWATM_500m_mask1.tif'
    Exporting...
       _ Success: The data has been exported to the file 'E:\Inputs\DEM\IGN\BDALTIV2\ElevationStD_BDALTIV2_stz_CWATM_500m_mask1.tif'
    """
    
    # ---- Load
    # Initialize the output filepath(s)
    if isinstance(data, xr.Dataset):
        if outpath is None:
            print("Error: if `data` is a xarray.Dataset, the argument `outpath` needs to be passed")
            return
        else:
            outpath_stem = Path(outpath)
    
    elif isinstance(data, (str, Path)):
        outpath_stem = infer_outpath(data)
        data = outpath_stem
    
    outpath = outpath_stem.with_suffix('.tif').with_stem(outpath_stem.stem + '_CWATM')
    
    # Load    
    data_ds = geo.load_any(data)
    
    # Impose reprojection resampling to be the minimum value
    rio_kwargs['resampling'] = 9, # 9: minimum
    
    # ---- Replace 0 (sea level) with nodata
    main_var = geo.main_vars(data_ds)[0]
    encod = data_ds[main_var].encoding # store encodings (_FillValue, compression...)
    data_ds[main_var] = data_ds[main_var].where(data_ds[main_var] != 0)
    data_ds[main_var].encoding = encod # transfer encodings
    
    # ---- Reproject
    for res in resolution:
        if res is None:
            res_suffix = ''
            if 'resolution' in rio_kwargs:
                rio_kwargs.pop('resolution')
        else:
            res_suffix = f'_{res}m'
            rio_kwargs['resolution'] = res
        n_mask = 0
        for m in mask:
            n_mask += 1
            ds_rprj = geo.reproject(data_ds, mask = m, bounds = bounds,
                                    x0 = x0, y0 = y0, base_template = base_template,
                                    **rio_kwargs) #  x0 = 12.5, y0 = 12.5
            geo.export(ds_rprj, 
                       outpath.with_stem(outpath.stem + res_suffix + f'_mask{n_mask}')
                       )
            
            # ---- Flow directions
# ============= issue with pysheds ============================================
#             ldd = geo.compute_ldd(ds_rprj, dirmap = '1-9', engine = 'pysheds')
#             geo.export(ldd, 
#                        outpath.with_stem('LDD_' + outpath.stem + res_suffix + f'_mask{n_mask}')
#                        )
# =============================================================================
            
            # ---- Standard deviation on each cell              
            if res is not None:
                # impose a resampling according to the standard deviation
                if 'resampling' in rio_kwargs:
                    rio_kwargs.pop('resampling')
                    
                elevstd = geo.reproject(data_ds, mask = m, bounds = bounds,
                                        x0 = x0, y0 = y0, base_template = base_template,
                                        resampling = 'std', # standard deviation
                                        **rio_kwargs)
                geo.export(elevstd, outpath.with_stem('ElevationStD_' + outpath.stem + res_suffix + f'_mask{n_mask}'))
            else:
                print("Err: Standard Deviation can only be computed if there is a downscaling. A resolution argument should be passed")
 
#%%% Données climatiques
@formating
def explore2climat(data, *, 
                   mask=None, 
                   bounds=None, 
                   resolution=None, 
                   x0=None, 
                   y0=None,
                   base_template=None, 
                   **rio_kwargs,
                   ):
    
    # DRIAS-Climat 2022 (netcdf)
    # Données SAFRAN (tas, prtot, rayonnement, vent... ) "EXPLORE2-Climat 2022" 
        
    data_folder, filelist = geo.get_filelist(data, extension = '.nc')
    
    for file_name in filelist:
        data = os.path.join(data_folder, file_name)
        # Raccourcir le nom
        motif1 = re.compile('(.*Adjust_France)')
        motif2 = re.compile('(historical|rcp25|rcp45|rcp85)')
        motif3 = re.compile('(\d{4,4}-\d{4,4}.*)')
        str1 = motif1.split(file_name)[1][:-7]
        str2 = motif2.split(file_name)[1]
        str3 = motif3.split(file_name)[1]
        outpath = '_'.join([str1, str2, str3])
        # outpath = outpath[:-3] # to remove '.nc'
        outpath = os.path.splitext(outpath)[0]
        outpath = os.path.join(data_folder, outpath)
        # Corriger les données
        ds = stzfr.explore2climat(data)
        # Géoréférencer les données
        ds = geo.georef(data = ds, data_type = 'drias2022')
        # Compression avec pertes (packing)
        ds_comp = geo.pack(ds)
        geo.export(ds_comp, outpath + '_pack' + '.nc')
        # Reprojections et exports
        # rio_kwargs['dst_crs'] = 2154
        for res in resolution:
            if res is None:
                res_suffix = ''
                if 'resolution' in rio_kwargs:
                    rio_kwargs.pop('resolution')
            else:
                res_suffix = f'_{res}m'
                rio_kwargs['resolution'] = res
            n_mask = 0
            for m in mask:
                n_mask += 1
                ds_rprj = geo.reproject(ds, mask = m, bounds = bounds,
                                        x0 = x0, y0 = y0, base_template = base_template,
                                        **rio_kwargs)
                geo.export(ds_rprj, outpath + res_suffix + f'_mask{n_mask}' + '.nc')
                # exporter(ds_rprj, outpath + f'_{rundate}' + res_suffix + '.nc') # Pas de rundate car noms des fichiers trop longs...
                
        del ds_rprj
        del ds
        del ds_comp


@formating
def explore2eau(data, *, 
                mask=None, 
                bounds=None, 
                resolution=None, 
                x0=None, 
                y0=None,
                base_template=None, 
                **rio_kwargs,
                ):               
    # DRIAS-Eau 2024 (netcdf)
    # Indicateurs SAFRAN (SWIAV, SSWI-3...) "EXPLORE2-SIM2 2024" 
            
    data_folder, filelist = geo.get_filelist(data, extension = '.nc')

    for file_name in filelist:
        data = os.path.join(data_folder, file_name)
        # Raccourcir le nom
        motif1 = re.compile('(.*_France)')
        motif2 = re.compile('(historical|rcp25|rcp45|rcp85)')
        motif3 = re.compile('(\d{4,4}-\d{4,4}.*)')
        str1 = motif1.split(file_name)[1][:-7]
        str2 = motif2.split(file_name)[1]
        str3 = motif3.split(file_name)[1]
        outpath = '_'.join([str1, str2, str3])
        # outpath = outpath[:-3] # to remove '.nc'
        outpath = os.path.splitext(outpath)[0]
        outpath = os.path.join(data_folder, outpath)
        # Corriger les données
        ds = stzfr.explore2eau(data)
        # Géoréférencer les données
        ds = geo.georef(data = ds, data_type = "DRIAS-Eau 2024")
        # Compression avec pertes (packing)
        ds_comp = geo.pack(ds)
        geo.export(ds_comp, outpath + '_pack' + '.nc')
        # Reprojections et exports
        # rio_kwargs['dst_crs'] = 2154
        for res in resolution:
            if res is None:
                res_suffix = ''
                if 'resolution' in rio_kwargs:
                    rio_kwargs.pop('resolution')
            else:
                res_suffix = f'_{res}m'
                rio_kwargs['resolution'] = res
            n_mask = 0
            for m in mask:
                n_mask += 1
                ds_rprj = geo.reproject(data = ds, mask = m, bounds = bounds,
                                        x0 = x0, y0 = y0, base_template = base_template,
                                        **rio_kwargs)
                geo.export(ds_rprj, outpath + res_suffix + f'_mask{n_mask}' + '.nc')
                # exporter(ds_rprj, outpath + f'_{rundate}' + res_suffix + '.nc') # Pas de rundate car noms des fichiers trop longs...
        
        del ds_rprj
        del ds
        del ds_comp
            

@formating
def meteo(data, *, 
          mask=None, 
          bounds=None, 
          resolution=None, 
          x0=None, 
          y0=None,
          base_template=None, 
          **rio_kwargs,
          ): 
    
    # SIM2 (csv to netCDF)
    # Réanalyse historique climatique Safran-Isba(-Modcou) "SIM2" 
        
    # Load data
# =============================================================================
#         sim2_pattern = re.compile("_SIM2_(.*)")
# =============================================================================
    
    if isinstance(data, list):
        data_ds = geo.merge_data(data)
        if os.path.isdir(data[0]): 
            outpath = data
# =============================================================================
#                 suffix = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%M")
# =============================================================================
        elif os.path.isfile(data[0]):
            outpath = os.path.split(data)[0]
# =============================================================================
#                 suffix = sim2_pattern.findall(os.path.splitext(os.path.split(data)[-1])[0])[0]
# =============================================================================
    elif isinstance(data, (str, Path)):
        if os.path.isfile(data):
            data_ds = geo.load_any(data, sep = ';')
            outpath = os.path.split(data)[0]
# =============================================================================
#                 suffix = sim2_pattern.findall(os.path.splitext(os.path.split(data)[-1])[0])[0]
# =============================================================================
        elif os.path.isdir(data):
            # Recherche en 1er les fichiers .csv
            outpath, filelist = geo.get_filelist(data, extension = '.csv')
            if len(filelist) > 0:
                data_ds = geo.merge_data(os.path.join(outpath, filelist))
            # Si aucun, recherche en 2e les fichiers .nc (1 fichier par variable)
            else:
                data_ds = xr.Dataset()
                for var in ['PRENEI_Q', 'PRELIQ_Q', 'PRETOT_Q', 'T_Q', 'TINF_H_Q', 
                            'TSUP_H_Q', 'ETP_Q', 'Q_Q', 'FF_Q', 'DLI_Q', 'SSI_Q', 'HU_Q']:
                    outpath, filelist = geo.get_filelist(data, extension = '.nc', tag = var)
                    if (filelist) > 0:
                        ds_temp = geo.merge(os.path.join(outpath, filelist))
                        data_ds[var] = ds_temp[var]
                
    else:
        data_ds = geo.load_any(data)

    if isinstance(data_ds, pd.DataFrame):
        # data_ds = geo.convert_to_cwatm(data_ds, data_type = "SIM2")
        data_ds = stzfr.sim2(data_ds)

    # Géoréférencer les données
    data_ds = geo.georef(data_ds)
    
    # Préparation outpath
    time_var = geo.main_time_dims(data_ds)[0]
    print('---')
    print(data_ds[time_var].min())
    start_year = pd.to_datetime(data_ds[time_var].min().values).strftime("%Y-%m")
    end_year = pd.to_datetime(data_ds[time_var].max().values).strftime("%Y-%m")
    
    var_list = geo.main_vars(data_ds)
    
    for var in var_list:
        var_ds = data_ds[[var]].copy()
        
        # Reprojections et exports
        # rio_kwargs['dst_crs'] = 2154
        for res in resolution:
            if res is None:
                res_suffix = ''
                if 'resolution' in rio_kwargs:
                    rio_kwargs.pop('resolution')
            else:
                res_suffix = f'_{res}m'
                rio_kwargs['resolution'] = res
            n_mask = 0
            for m in mask:
                n_mask += 1
                ds_rprj = geo.reproject(data = var_ds, mask = m, bounds = bounds,
                                        x0 = x0, y0 = y0, base_template = base_template,
                                        **rio_kwargs)
                geo.export(ds_rprj, os.path.join(
                    outpath, '_'.join([var, start_year, end_year]) + res_suffix + f'_mask{n_mask}.nc')
                    )


#%%% Données d'occupation du sol
@formating
def ocspaysbasque(data, *, 
                  mask=None, 
                  bounds=None, 
                  resolution=None, 
                  x0=None, 
                  y0=None,
                  base_template=None, 
                  **rio_kwargs,
                  ):         
    # OCS SCOT Pays Basque
    data_folder, filelist = geo.get_filelist(data, extension = '.nc')

    # outpath = outpath[:-3] # to remove '.nc'
    outpath = os.path.splitext(filelist[0])[0]
    outpath = os.path.join(data_folder, outpath)
    # Corriger les données
    ds = stzfr.ocspaysbasque([os.path.join(data_folder, f) for f in filelist])
    # Géoréférencer les données
    ds = geo.georef(data = ds, data_type = "other", crs = 4326)
    # Compression avec pertes (packing)
    ds_comp = geo.pack(ds)
    geo.export(ds_comp, outpath + '_pack' + '.nc')
    # Reprojections et exports
    # rio_kwargs['dst_crs'] = 2154
    for res in resolution:
        if res is None:
            res_suffix = ''
            if 'resolution' in rio_kwargs:
                rio_kwargs.pop('resolution')
        else:
            res_suffix = f'_{res}m'
            rio_kwargs['resolution'] = res
        n_mask = 0
        for m in mask:
            n_mask += 1
            ds_rprj = geo.reproject(data = ds, mask = m, bounds = bounds,
                                    x0 = x0, y0 = y0, base_template = base_template,
                                    **rio_kwargs)
            geo.export(ds_rprj, outpath + res_suffix + f'_mask{n_mask}' + '.nc')
            # exporter(ds_rprj, outpath + f'_{rundate}' + res_suffix + '.nc') # Pas de rundate car noms des fichiers trop longs...
    
    del ds_rprj
    del ds
    del ds_comp

#%%% Données d'usages de l'eau
@formating
def bnpe(data, *, 
         mask=None, 
         bounds=None, 
         resolution=None, 
         x0=None, 
         y0=None,
         base_template=None, 
         **rio_kwargs,
         ): 
    
    # BNPE
    # ---- Creer les fichiers qui combinent les info sur les chroniques et les infos sur les ouvrages
    gdf = stzfr.bnpe(data = data)
    
    # ---- Initialisations
    concat_folder = Path(data).with_name("concat")
    
    year_start = int(gdf.time.dt.year.min())
    year_end = int(gdf.time.dt.year.max())
    
    time_dim = geo.main_time_dims(gdf)[0]
    
    n_mask = 0
    for m in mask:
        n_mask += 1
        
        # ---- Manage folders
        if not (concat_folder / Path(f"mask{n_mask}")).exists():
            os.makedirs(concat_folder / Path(f"mask{n_mask}"))
    
        # ---- Cut json files on masks
        print(f"\nCut shapefile over mask {n_mask}/{len(mask)}:")
        reprj_gdf = geo.reproject(gdf, 
                                  # main_vars = 1, # useless
                                  mask = m)
        
        geo.export(reprj_gdf, 
                   concat_folder / Path(f"mask{n_mask}") / f"{year_start}-{year_end}_clipped.json",
                   encoding='utf-8')
        
        # ---- Fichier récapitulatif .csv
        # Reorder columns (optional)
        col_names_base = ['code_ouvrage', 'nom_commune', 'volume', 'code_usage', 'libelle_usage', 'prelevement_ecrasant'] + [time_dim]
        
        if ('libelle_type_milieu' in gdf.columns) & ('code_type_milieu' in gdf.columns):
            col_names = col_names_base + ['code_type_milieu', 'libelle_type_milieu']
        elif ('libelle_type_milieu' in gdf.columns) & ('code_type_milieu' not in gdf.columns):
            col_names = col_names_base + ['libelle_type_milieu']
        elif ('libelle_type_milieu' not in gdf.columns) & ('code_type_milieu' in gdf.columns):
            col_names = col_names_base + ['code_type_milieu']
# =============================================================================
#         df = pd.DataFrame(reprj_gdf[col_names])
# =============================================================================
        
        col_names = [time_dim] + col_names
        remaining_col = list(set(gdf.columns) - set(col_names))
# =============================================================================
#         df = df[[time_dim] + col_names
# =============================================================================
        df = pd.DataFrame(reprj_gdf[col_names + remaining_col])
        
        # Remove useless rows
        df = df[df.volume > 0]
        
        # Sort by nom_commune
        df.sort_values(by = 'nom_commune', inplace = True)
        
        # Export du fichier récapitulatif csv
        df.to_csv(concat_folder / "recap.csv", sep = ';', encoding = 'utf-8')
    
    
        # ---- Rastérisation
        for res in resolution:
            if res is None:
                res_suffix = ''
                res_folder = ''
                if 'resolution' in rio_kwargs:
                    rio_kwargs.pop('resolution')
            else:
                res_suffix = f'_{res}m'
                res_folder = f"{res}m"
                rio_kwargs['resolution'] = res

            # Folders
            if not (concat_folder / "netcdf" / res_folder / f"mask{n_mask}").exists():
                os.makedirs(concat_folder / "netcdf" / res_folder / f"mask{n_mask}")
            
            # Reprojection
            ds_rprj = geo.reproject(data = gdf, mask = m, bounds = bounds,
                                    x0 = x0, y0 = y0, 
                                    base_template = base_template,
                                    rasterize = True, main_vars = None,
                                    **rio_kwargs)
            
            if 'dst_crs' in rio_kwargs:
                ds_rprj = geo.georef(data = ds_rprj, 
                                     include_crs = True, 
                                     crs = rio_kwargs['dst_crs'])
            else:
                ds_rprj = geo.georef(data = ds_rprj)
            
            # Export de chaque fichier annuel reprojeté
            geo.export(ds_rprj,
                       concat_folder / "netcdf" / res_folder / f"mask{n_mask}" / f"{year_start}-{year_end}_clipped.nc",
                       )


#%% STANDARDIZE OUTPUTS
def output(data, 
           *, data_type = 'CWatM'):
    # data_type peut être aussi = 'MODFLOW'
    0
    

#%% AUTRES FONCTIONS
def zones_basses(mnt_raster):
    # Génère un raster indiquant les pixels sous le niveau de la mer, à partir
    # d'un raster de modèle numérique de terrain
    
    with xr.open_dataset(mnt_raster, 
                         decode_times = False, 
                         decode_coords = 'all') as mnt_ds:
        mnt_ds.load()


def dummy_fractionLandcover(base, first_year = 2020, last_year = 2020):
    frac0 = geo.dummy_input(base, 0)
    frac1 = geo.dummy_input(base, 1)
    
    mvar = geo.main_var(frac0)[0]
    
    data_ds = frac0.copy()
    data_ds = data_ds.rename({mvar: 'fracforest'})
    data_ds['fracgrassland'] = frac1[mvar]
    data_ds['fracirrNonPaddy'] = frac0[mvar]
    data_ds['fracirrPaddy'] = frac0[mvar]
    data_ds['fracsealed'] = frac0[mvar]
    data_ds['fracwater'] = frac0[mvar]
    
    data_ds = data_ds.expand_dims(dim = {'time': pd.date_range(start = f"{first_year}-01-01", periods = last_year - first_year + 1, freq = 'YE') }, axis = 0)
    
    data_ds = geo.georef(data_ds, crs = data_ds.rio.crs)
    data_ds, _ = geo.standard_fill_value(data_ds)
    
    for var in geo.main_var(data_ds):
        data_ds[var].attrs['long_name'] = var

    return data_ds



def dummy_dzRel(base, out_path):
    array = geo.dummy_input(base, 1)
    mvar = geo.main_var(array)[0]
    
    data_ds = xr.Dataset()
    for n in [0, 1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        var = f'dzRel{n:04}'
        data_ds[var] = array[mvar]
        data_ds[var].attrs['long_name'] = var
    
    data_ds = geo.georef(data_ds, crs = data_ds.rio.crs)
    data_ds, _ = geo.standard_fill_value(data_ds)
    
    geo.export(data_ds, Path(out_path)/"dzRel_dummy.nc")
    return data_ds


def dummy_lakeres(base, out_path):
    # array = geo.dummy_input(base, 1)
    # mvar = geo.main_var(array)[0]
    
    print("Warning: The input `base` should necessary be the mask")
    
    data_ds = geo.dummy_input(base, 0)
    mvar = geo.main_var(data_ds)[0]
    xvar, yvar = geo.main_space_dims(data_ds)
    
    stack_da = data_ds[mvar].stack(xy = [xvar, yvar])
    
    # Determine the coordinates of the first not-NaN cell
    x, y = stack_da[stack_da.notnull()].xy[0].item()
    
    data_ds[mvar].loc[{xvar: x, yvar: y}] = 1
    
    data_ds = geo.georef(data_ds, crs = data_ds.rio.crs)
    data_ds, _ = geo.standard_fill_value(data_ds)
    
    geo.export(data_ds, Path(out_path)/"lakeres_dummy.nc")
    return data_ds


def dummy_routing(base, out_path):
    ds_dict = {}
    ds_dict['chanMan'] = geo.dummy_input(base, 0.3)
    ds_dict['chanGrad'] = geo.dummy_input(base, 0.02)
    ds_dict['chanGradMin'] = geo.dummy_input(base, 0.0001)
    ds_dict['chanLength'] = geo.dummy_input(base, 1400)
    ds_dict['chanWidth'] = geo.dummy_input(base, 17)
    ds_dict['chanDepth'] = geo.dummy_input(base, 1)
    
    for var in ds_dict:
        ds_dict[var] = geo.georef(ds_dict[var], crs = ds_dict[var].rio.crs)
        ds_dict[var], _ = geo.standard_fill_value(ds_dict[var])
        
        geo.export(ds_dict[var], Path(out_path)/f"{var}_dummy.nc")
        
    return ds_dict

