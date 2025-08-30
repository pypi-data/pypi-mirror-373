# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 16:25:29 2022

@author: Alexandre Coche Kenshilikov

Previously cwatres.py (changed on 20-07-2022)
Previously advancedresults.py (changed on 07-12-2022)
compare_maps() copied from comparison_maps.py
"""

#%% Imports :
# ~~~~~~~~~~~
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import xarray as xr
xr.set_options(keep_attrs = True)
import rioxarray as rio #Not necessary, the rio module from xarray is enough
import rasterio
import rasterio.features
from affine import Affine
# from shapely.geometry import Point
import os
import sys
import re
# import matplotlib as mpl
import matplotlib.pyplot as plt
import readsettings as rs
from cwatm.management_modules.output import *

#%% WATERTABLE DEPTH
def watertable_depth(result_folder, timestep = 'daily', 
                     landcover = ['grassland', 'forest']):
    """
    DESCRIPTION :
    Calcule la profondeur de la nappe à partir de son altitude et de la
    topographie, en retranchant l'épaisseur du sol
    
    EXEMPLE :
    import visualization_advanced as va
    va.watertable_depth(r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\005_calib_groundwater\08")
    
    # Obsolète
    va.watertable_depth(topo = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\data\input_1km_LeMeu\ModFlow_inputs\75m\elevation_modflow.tif", 
                        watertable = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\005_calib_groundwater\01_base_Ronan\modflow_watertable_monthavg.nc", 
                        soil1 = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\data\input_1km_LeMeu\soil\soildepth1_1km.nc", 
                        soil2 = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\data\input_1km_LeMeu\soil\soildepth2_1km.nc", 
                        output = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\005_calib_groundwater\01_base_Ronan\modflow_watertable_depth_monthavg_QGIS.nc")
    
    To run for a whole screening
    ----------------------------
    for c in range(27, 31):
        for r in range(0, 616):
            print('\n-------')
            print(f'CAT = {c}    RUN = {r}')
            if not os.path.isfile(rf"D:\acoche\3_CWatM_EBR\results\raw_results\c{c:03n}\r{r:04n}\modflow_watertable_depth_daily.nc"):
                try:
                    va.watertable_depth(rf"D:\acoche\3_CWatM_EBR\results\raw_results\c{c:03n}\r{r:04n}", timestep = 'daily')
                except:
                    print('/!\ Failed')
            else:
                print('Already done')
    """
    
    
# =============================================================================
#     # TEMP INPUTS #
#     data_folder = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\data\input_1km_LeMeu"
#     topo = os.path.join(data_folder, r"ModFlow_inputs\75m\elevation_modflow.tif")
#     result_folder = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\003_artif\2022-03-25_all_city"
#     watertable = os.path.join(result_folder, r"modflow_watertable_monthavg.nc")
#     soil1 = os.path.join(data_folder, r"soil\soildepth1_1km.nc")
#     soil2 = os.path.join(data_folder, r"soil\soildepth2_1km.nc")
#     output = os.path.join(result_folder, r"modflow_watertable_depth_monthavg_QGIS.nc")
#     mdfw_soil_thickness = os.path.join(result_folder, r"modflowtotalSoilThickness_totalend.nc")
# =============================================================================
    

    #%%% Chargement des données :
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    landcover_list = landcover
    if timestep == 'daily':
        decode_times_arg = True
    elif timestep == 'monthavg':
        decode_times_arg = False
    
    # Paramètres généraux
    # -------------------
    setting_file = [f for f in os.listdir(result_folder) if f.endswith('.ini')]
    if len(setting_file) == 1:
        setting_file = setting_file[0]
        (config, option, binding, outputDir) = rs.parse_configuration(
            os.path.join(result_folder, setting_file))
    else:
        print('\nNot able to find the setting file in the output_folder.')
        

    if result_folder[3:9] == 'acoche': # server Buffon
        cwatm_path = r"D:\acoche"
    elif result_folder[3:8] == 'Users': # server Risce
        # not implemented yet
        print('Server Risce: paths not standard')
        return
    else: # personal PC
        cwatm_path = r"D:\2- Postdoc\2- Travaux"
    main_folder_name = '3_CWatM_EBR'
    motif = re.compile(main_folder_name + '.*')
    print("\nRacine des fichiers d'input = {}".format(
        os.path.join(cwatm_path, main_folder_name)))
    
    # Création des chemins
    # --------------------
    mdfw_topo = os.path.join(cwatm_path, motif.search(binding['topo_modflow']).group())
    mdfw_river_percentage = os.path.join(cwatm_path, motif.search(binding['chanRatio']).group())
    mdfw_soil_thickness = os.path.join(result_folder, r"modflowtotalSoilThickness_totalend.nc")
    watertable = os.path.join(result_folder, f"modflow_watertable_{timestep}.nc")
    river_depth = os.path.join(cwatm_path, motif.search(binding['chanDepth']).group())
    output_file = os.path.join(result_folder, f"modflow_watertable_depth_{timestep}.nc")
    
    # For different landcovers
    # ------------------------
    path_rootDepth1 = dict()
    path_rootDepth2 = dict()
    path_rootDepth3 = dict()
    path_gravit_effsat1 = dict()
    path_gravit_effsat2 = dict()
    path_gravit_effsat3 = dict()
    path_fracVeg = dict()
    path_list = [path_rootDepth1, path_rootDepth2, path_rootDepth3,
                 path_gravit_effsat1, path_gravit_effsat2, path_gravit_effsat3, 
                 path_fracVeg,]
    for landcover in landcover_list:
        path_rootDepth1[landcover] = os.path.join(result_folder,
                                                  f"{landcover}_rootDepth1_totalend.nc")
        path_rootDepth2[landcover] = os.path.join(result_folder,
                                                  f"{landcover}_rootDepth2_totalend.nc")
        path_rootDepth3[landcover] = os.path.join(result_folder,
                                                  f"{landcover}_rootDepth3_totalend.nc")
        path_gravit_effsat1[landcover] = os.path.join(result_folder,
                                               f"{landcover}_gravit_effsat1_{timestep}.nc")
        path_gravit_effsat2[landcover] = os.path.join(result_folder,
                                               f"{landcover}_gravit_effsat2_{timestep}.nc")
        path_gravit_effsat3[landcover] = os.path.join(result_folder,
                                               f"{landcover}_gravit_effsat3_{timestep}.nc")
        path_fracVeg[landcover] = os.path.join(result_folder,
                                               f"frac{landcover.capitalize()}_totalend.nc")
    
    # Chargement MNT modflow
    # ----------------------
    with xr.open_dataset(mdfw_topo, 
                         decode_times = decode_times_arg) as topo_ds:
        topo_ds.load() # to unlock the resource
    topo_ds = topo_ds.where(topo_ds['band_data'] != -99999)  
        # car il y a visiblement dans le fichier initial de topo une redondance
        # des valeurs non affichées : nan et -99999, les dernières n'étant pas '_FillValue' ?
    topo_ds = topo_ds.sel(band = 1)
    topo_ds = topo_ds.drop_vars('band')
    
    # Chargement output watertable (réso modflow)
    # -------------------------------------------
    # NB : C'est une élévation absolue (= par rapprot niveau de la mer)
    with xr.open_dataset(watertable, 
                         decode_times = decode_times_arg, 
                         decode_coords = 'all') as watertable_ds:
        watertable_ds.load()
    
    main_var = list(watertable_ds.data_vars)[0] # par ex 'modflow_watertable_monthavg'
        
    # Alignment problem with Luca's modflow outputs
    if (watertable_ds['x'].values[0] != topo_ds.x.values[0]) | (watertable_ds['y'].values[0] != topo_ds.y.values[0]):
        print(f"\nL'emprise de l'output watertable est décalée de {(watertable_ds['x'].values[0]-topo_ds.x.values[0])/(watertable_ds['y'].values[1]-watertable_ds['y'].values[0])}x et {(watertable_ds['y'].values[0]-topo_ds.y.values[0])/(watertable_ds['y'].values[1]-watertable_ds['y'].values[0])}y")
        print("Réalignement effectué")
        watertable_ds['x'] = topo_ds.x
        watertable_ds['y'] = topo_ds.y
    

    # Chargement données sol (réso modflow)
    # -------------------------------------
    # with xr.open_dataset(soil1) as soil1_ds:
    #     soil1_ds.load()
    # with xr.open_dataset(soil2) as soil2_ds:
    #     soil2_ds.load()
    with xr.open_dataset(mdfw_soil_thickness,
                         decode_coords = 'all',
                         decode_times = decode_times_arg) as mdfw_soil_thickness_ds:
        mdfw_soil_thickness_ds.load()

        if (mdfw_soil_thickness_ds['x'].values[0] != topo_ds.x.values[0]) | (mdfw_soil_thickness_ds['y'].values[0] != topo_ds.y.values[0]):
            print(f"\nL'emprise de l'output mdfw_soil_thickness est décalée de {(mdfw_soil_thickness_ds['x'].values[0]-topo_ds.x.values[0])/(mdfw_soil_thickness_ds['y'].values[1]-mdfw_soil_thickness_ds['y'].values[0])}x et {(mdfw_soil_thickness_ds['y'].values[0]-topo_ds.y.values[0])/(mdfw_soil_thickness_ds['y'].values[1]-mdfw_soil_thickness_ds['y'].values[0])}y")
            print("Réalignement effectué")
            mdfw_soil_thickness_ds['x'] = topo_ds.x
            mdfw_soil_thickness_ds['y'] = topo_ds.y
    
    # Chargement couches de sol (réso modflow), pour différents landcovers
    # --------------------------------------------------
    rootDepth1_ds = xr.Dataset()
    rootDepth2_ds = xr.Dataset()
    rootDepth3_ds = xr.Dataset()
    gravit_effsat1_ds = xr.Dataset()
    gravit_effsat2_ds = xr.Dataset()
    gravit_effsat3_ds = xr.Dataset()
    fracVeg_ds = xr.Dataset()
    ds_list = [rootDepth1_ds, rootDepth2_ds, rootDepth3_ds,
               gravit_effsat1_ds, gravit_effsat2_ds, gravit_effsat3_ds, 
               fracVeg_ds,]
    for i in range(0, 7):
        for landcover in landcover_list:
            with xr.open_dataset(path_list[i][landcover],
                                 decode_coords = 'all',
                                 decode_times = decode_times_arg) as temp:
                ds_list[i][landcover] = temp[list(temp.data_vars)[0]]
        # Correction of attributes
        ds_list[i].attrs['standard_name'] = '_'.join(os.path.split(path_list[i]['grassland'])[-1].split('_')[-2:])[:-3]
        ds_list[i].attrs['long_name'] = ''

    # Chargement pourcentages de rivières (réso modflow)
    # --------------------------------------------------
    # Il est nécessaire d'appliquer une correction pour les rivières :
    with xr.open_dataset(mdfw_river_percentage,
                         decode_times = decode_times_arg) as mdfw_river_percentage_ds:
        mdfw_river_percentage_ds.load()
    mdfw_river_percentage_ds = mdfw_river_percentage_ds.drop('band')
    mdfw_river_percentage_ds = mdfw_river_percentage_ds.squeeze('band')
    
    
    # Récupération SCR cwatm
    # ----------------------
    maskmap = os.path.join(cwatm_path, motif.search(binding['MaskMap']).group())
    if os.path.splitext(maskmap)[-1] == ".nc":
        decode_coords_arg = 'all'
    else:
        decode_coords_arg = None

    with xr.open_dataset(maskmap, decode_coords = decode_coords_arg) as mask_ds:
        mask_ds.load()
    if 'spatial_ref' in list(mask_ds.coords) + list(mask_ds.data_vars):
        cwatm_epsg = mask_ds.rio.crs.to_epsg()
        print("\nCRS of CWatM is epsg:{}".format(cwatm_epsg))
    else:
        cwatm_epsg = 3035
        print("\nCRS of CWatM inputs is assumed to be epsg:{}".format(cwatm_epsg))
    
    mdfw_maskmap = os.path.join(cwatm_path, motif.search(binding['modflow_basin']).group())
    if os.path.splitext(mdfw_maskmap)[-1] == ".nc":
        decode_coords_arg = 'all'
    else:
        decode_coords_arg = None
        
    with xr.open_dataset(mdfw_maskmap, decode_coords = decode_coords_arg) as mdfw_mask_ds:
        mdfw_mask_ds.load()
    if 'spatial_ref' in list(mdfw_mask_ds.coords) + list(mdfw_mask_ds.data_vars):
        mdfw_epsg = mdfw_mask_ds.rio.crs.to_epsg()
        print("CRS of Modflow is epsg:{}".format(mdfw_epsg))
    else:
        mdfw_epsg = 2154
        print("CRS of Modflow inputs is assumed to be epsg:{}".format(mdfw_epsg))
    
    
# =============================================================================
#     # Chargement de la profondeur des rivières (réso CWatM)
#     # -----------------------------------------------------
#     """
#     La profondeur des rivières n'est finalement pas prise en compte par Modflow
#     """
#     with xr.open_dataset(river_depth) as river_depth_ds:
#         river_depth_ds.load()
#         river_depth_ds.rio.write_crs("epsg:{}".format(cwatm_epsg), inplace = True)
#     
#     # Reprojection :
#     river_depth_reprj = river_depth_ds.rio.reproject(
#         'epsg:{}'.format(mdfw_epsg), 
#         # resolution = (1000, 1000),
#         shape = (500, 650),
#         transform = Affine(75, 0.0, mdfw_river_percentage_ds.x.min().values-(75*10.5),
#                            0.0, -75, mdfw_river_percentage_ds.y.max().values+(75*10.5)), 
#         resampling = rasterio.enums.Resampling(5),
#         nodata = np.nan)
#     
#     
#     # Seules les cellules considérées comme rivières par modflow sont conservées :
#     mdfw_river_depth_ds = mdfw_river_percentage_ds.copy()
#     mdfw_river_depth_ds['band_data'] = mdfw_river_depth_ds.band_data * river_depth_reprj.chanbnkf
# =============================================================================
    
    
    #%%% Calcul basique de la profondeur de nappe
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# =============================================================================
# # Correction du sol
# Dans les settings, dans le § [GROUNDWATER_MODFLOW], on trouve :
# # Defining the upper limit of the groundwater layer
# use_soildepth_as_GWtop = False
# correct_soildepth_underlakes = False
# depth_underlakes = 1
# 
# Je pense que c'est de cette correction que Luca parle
# 
# On peut visualiser cette correction dans l'output modflowtotalSoilThickness_totalend.nc
# =============================================================================

    
    watertable_depth_ds = watertable_ds.copy()
    use_soildepth_as_GWtop = binding['use_soildepth_as_GWtop']
    
    #% 1| Profondeur de la nappe relativement à la topo :
    # --------------------------------------------------
    if use_soildepth_as_GWtop:
        """
        Cette formule donne la profondeur de la nappe par rapport à la topo,
        en considérant que la nappe ne peut pas empiéter sur le sol (la prof.
        de la nappe est au minimum égale à l'épaisseur du sol).
        La profondeur est donnée en valeurs positives.
        """
        watertable_depth_ds[main_var] = topo_ds['band_data'] \
            - watertable_ds[main_var]
        
    else:
        watertable_depth_ds[main_var] = topo_ds['band_data'] \
            - watertable_ds[main_var] \
                - mdfw_soil_thickness_ds['modflowtotalSoilThickness_totalend']
        
# =============================================================================
#     #% 2| Profondeur de la nappe relativement à la base du sol :
#     # ----------------------------------------------------------
#     """
#     Ou dit autrement : prof. de la nappe + du sol par rapport à la topo
#     """
#     if use_soildepth_as_GWtop:
#         watertable_depth_ds[main_var] = watertable_ds[
#             main_var] + mdfw_soil_thickness_ds[
#                 'modflowtotalSoilThickness_totalend'] - topo_ds['band_data']
#                     
#     else:
#         watertable_depth_ds[main_var] = watertable_ds[
#             main_var] - topo_ds['band_data']
# =============================================================================
        
# =============================================================================
#     # Il est possible de prendre en compte la profondeur des rivières
#     # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     # Mais la prof. des rivières n'est pas prise en compte par Modflow, 
#     # seulement par CWatM pour le ROUTING
#     
#     #% Premier type de correction des rivières :
#     # ------------------------------------------
#     watertable_depth_ds['modflow_watertable_monthavg'] = watertable_depth_ds[
#         'modflow_watertable_monthavg'] + mdfw_river_depth_ds[
#             'band_data'] - topo_ds['band_data']    
#       
#     #% Deuxième type de correction des rivières :
#     # -------------------------------------------
#     watertable_depth_ds['modflow_watertable_monthavg'] = xr.where(
#         mdfw_river_percentage_ds.band_data == 1,
#         0,
#         watertable_depth_ds['modflow_watertable_monthavg'],
#         keep_attrs = False)
#     # Marche pas, je ne sais pas pourquoi...
# =============================================================================
    
# =============================================================================
#     #% Pour appliquer une profondeur nulle aux pixels avec des rivières
#     watertable_depth_ds[
#         main_var] = watertable_depth_ds.modflow_watertable_monthavg.where(
#         mdfw_river_percentage_ds.band_data == 0,
#         0)
# =============================================================================
    
# =============================================================================
#     # Enlever les pixels initiaux NaN ?
#     watertable_depth_ds[
#         main_var] = watertable_depth_ds.modflow_watertable_monthavg.where(
#         ~np.isnan(watertable_ds.modflow_watertable_monthavg.isel(time = 0)),
#         np.nan)
# =============================================================================
    
    #%%% Addition of water in the bottom layer of soil (subsoil)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    watersheet3_ds = xr.Dataset()    # Dataset containing the equivalent water level [m] in 3rd soil layer (subsoil) to add to watertable
    watersheet3_reprj = xr.Dataset() # Previous dataset, reprojected
    fracVeg_reprj = xr.Dataset()     # Dataset containing landcover fractions, reprojected
    
    # Convert the effective saturation into equivalent watersheet
    for landcover in landcover_list:
        watersheet3_ds[landcover] = rootDepth3_ds[landcover] * gravit_effsat3_ds[landcover]
    
    # Reproject:
    reso_x = float(watertable_depth_ds.x[1] - watertable_depth_ds.x[0])
    reso_y = float(watertable_depth_ds.y[1] - watertable_depth_ds.y[0])
    transform_ = Affine(reso_x, 
                        0.0, 
                        float(watertable_depth_ds.x.min() - reso_x/2),  
                        0.0, 
                        reso_y, # reso_y is negative here
                        float(watertable_depth_ds.y.max() - reso_y/2))
    
    height_ = int(watertable_depth_ds.y.shape[0])
    width_ = int(watertable_depth_ds.x.shape[0])
    
    watersheet3_ds.rio.write_crs(cwatm_epsg, inplace = True)
    watersheet3_ds = watersheet3_ds.transpose('time', 'y', 'x')
    
    watersheet3_reprj = watersheet3_ds.rio.reproject(dst_crs = mdfw_epsg,
                                                     transform = transform_,
                                                     resampling = rasterio.enums.Resampling(5),
                                                     shape = (height_, width_),
                                                     # nodata = np.nan
                                                     )
    
    # Keep values only where watertable reaches the soil bottom (replace values with 0 everywhere else)
    for landcover in landcover_list:
        watersheet3_reprj[landcover] = xr.where(
            watertable_depth_ds[main_var] >= -mdfw_soil_thickness_ds['modflowtotalSoilThickness_totalend'],
            watersheet3_reprj[landcover],
            0)

        
    # Reproject landcover fractions
    fracVeg_ds.rio.write_crs(cwatm_epsg, inplace = True)
    fracVeg_reprj = fracVeg_ds.rio.reproject(dst_crs = mdfw_epsg,
                                             transform = transform_,
                                             resampling = rasterio.enums.Resampling(5),
                                             shape = (height_, width_),
                                             # nodata = np.nan
                                             )
        
    # Weighted average according to landcovers   
     # Initialization
    watersheet3_reprj['weighted'] = 0
    fracVeg_reprj['sum'] = 0
     # Loop
    for landcover in landcover_list:
        watersheet3_reprj['weighted'] = watersheet3_reprj['weighted'] + watersheet3_reprj[landcover] * fracVeg_reprj[landcover]
        fracVeg_reprj['sum'] = fracVeg_reprj['sum'] + fracVeg_reprj[landcover]
    watersheet3_reprj['normed_average'] = watersheet3_reprj['weighted'] / fracVeg_reprj['sum']
    
    # Add to watertable_depth_ds
    watertable_depth_ds[main_var] = watertable_depth_ds[main_var] + watersheet3_reprj['normed_average']


    #%%% Addition of water in the middle layer of soil (topsoil)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    watersheet2_ds = xr.Dataset()    # Dataset containing the equivalent water level [m] in 2nd soil layer (bulk soil) to add to watertable
    watersheet2_reprj = xr.Dataset() # Previous dataset, reprojected
    # fracVeg_reprj_dict[ already created
    
    # Convert the effective saturation into equivalent watersheet
    for landcover in landcover_list:
        watersheet2_ds[landcover] = rootDepth2_ds[landcover] * gravit_effsat2_ds[landcover]
    
    # Reproject:   
    watersheet2_ds.rio.write_crs(cwatm_epsg, inplace = True)
    watersheet2_ds = watersheet2_ds.transpose('time', 'y', 'x')
    
    watersheet2_reprj = watersheet2_ds.rio.reproject(dst_crs = mdfw_epsg,
                                                     transform = transform_,
                                                     resampling = rasterio.enums.Resampling(5),
                                                     shape = (height_, width_),
                                                     # nodata = np.nan
                                                     )
    
    

# =============================================================================
#         middle_layer_limit = -0.3
# =============================================================================
    rootDepth12_ds = rootDepth1_ds + rootDepth2_ds
    # Reproject
    rootDepth12_ds.rio.write_crs(cwatm_epsg, inplace = True)
    rootDepth12_ds = rootDepth12_ds.transpose('y', 'x')
    rootDepth12_ds = rootDepth12_ds.rio.reproject(dst_crs = mdfw_epsg,
                                                  transform = transform_,
                                                  resampling = rasterio.enums.Resampling(5),
                                                  shape = (height_, width_),
                                                  # nodata = np.nan
                                                  )
    
    # Keep values only where below soil layer is saturated (replace values with 0 everywhere else)
    for landcover in landcover_list:
        watersheet2_reprj[landcover] = xr.where(
            watertable_depth_ds[main_var] >= -rootDepth12_ds[landcover],
            watersheet2_reprj[landcover],
            0,
            keep_attrs = False)

# =============================================================================
#     for landcover in landcover_list:
#         watersheet2_reprj[landcover] = xr.where(
#             watertable_depth_ds[main_var] >= -rootDepth12_ds[landcover],
#             watersheet2_reprj[landcover],
#             0,
#             keep_attrs = False)
# =============================================================================
    

    # Weighted average according to landcovers   
     # Initialization
    watersheet2_reprj['weighted'] = 0
    fracVeg_reprj['sum'] = 0
     # Loop
    for landcover in landcover_list:
        watersheet2_reprj['weighted'] = watersheet2_reprj['weighted'] + watersheet2_reprj[landcover] * fracVeg_reprj[landcover]
        fracVeg_reprj['sum'] = fracVeg_reprj['sum'] + fracVeg_reprj[landcover]
    watersheet2_reprj['normed_average'] = watersheet2_reprj['weighted'] / fracVeg_reprj['sum']
    
    # Add to watertable_depth_ds
    watertable_depth_ds[main_var] = watertable_depth_ds[main_var] + watersheet2_reprj['normed_average']

        
        # NB: modflow total soil thickness is 0.75% thicker than input
                                
    # watertable_depth_ds.where(
    #     watertable_depth_ds[
    #         main_var] >= -mdfw_soil_thickness_ds[
    #             'modflowtotalSoilThickness_totalend'],
    #     watertable_depth_ds[
    #         main_var] - np.mean(watersheet3_dict['grassland'].loc[dict(x = watertable_depth_ds.x, y = watertable_depth_ds.y)], 
    #                             # watersheet3_dict['forest'].loc[dict(x = watertable_depth_ds.x, y = watertable_depth_ds.y)]
    #                             ),
    #     drop = False
    #     )                                
            

    #%%% Formatage et export
    # ~~~~~~~~~~~~~~~~~~~~~~
    if timestep == 'daily':
        timestep_suffix = ''
    else:
        timestep_suffix = timestep
    wt_depth_var = 'modflow_watertable_depth' + timestep_suffix
    watertable_depth_ds = watertable_depth_ds.rename({main_var: wt_depth_var})
    watertable_depth_ds.x.attrs = {'standard_name': 'projection_x_coordinate',
                                   'long_name': 'x coordinate of projection',
                                   'units': 'Meter'}
    watertable_depth_ds.y.attrs = {'standard_name': 'projection_y_coordinate',
                                   'long_name': 'y coordinate of projection',
                                   'units': 'Meter'}
    watertable_depth_ds[wt_depth_var].attrs = {'long_name': 'watertable depth',
                                               'units': 'Meter'}

    # Transfert des encoding (pour conserver la taille sur disque)
    watertable_depth_ds[wt_depth_var].encoding = watertable_ds[main_var].encoding

    watertable_depth_ds.rio.write_crs(mdfw_epsg, inplace = True)    
    
    watertable_depth_ds.to_netcdf(output_file)
    
    
    #%%% Wetlands
    # ~~~~~~~~~~~
    
    # wetland_ds = watertable_depth_ds[main_var].where(
    #     watertable_depth_ds[main_var] > -0.3,
    #     drop = False)*0+1
    
    wetland_limit = -0.30
    print(f"\nWetlands are defined by lands saturated at {-wetland_limit*100} cm below surface")
    
    wetland_da = xr.where(
        watertable_depth_ds[wt_depth_var] > wetland_limit,
        watertable_depth_ds[wt_depth_var]*0+1,
        watertable_depth_ds[wt_depth_var]*0
        )
    
    wetland_ds = wetland_da.to_dataset()
    wetland_ds = wetland_ds.rename({wt_depth_var: 'wetland' + timestep_suffix})
    
    output_file_wl = os.path.join(result_folder, f"wetland_{timestep}.nc") 
    wetland_ds.x.attrs = {'standard_name': 'projection_x_coordinate',
                        'long_name': 'x coordinate of projection',
                        'units': 'Meter'}
    wetland_ds.y.attrs = {'standard_name': 'projection_y_coordinate',
                        'long_name': 'y coordinate of projection',
                        'units': 'Meter'}
    wetland_ds['wetland' + timestep_suffix].encoding = watertable_ds[main_var].encoding
    wetland_ds.rio.write_crs(mdfw_epsg, inplace = True)
    wetland_ds.to_netcdf(output_file_wl)
    
    # Average occurence
    mean_wetland_ds = wetland_ds.mean(dim = 'time')
    mean_wetland_ds = mean_wetland_ds.rename({'wetland' + timestep_suffix: 'wetland_totalavg'})
    
    output_file_mwl = os.path.join(result_folder, "wetland_totalavg.nc")
    mean_wetland_ds.x.attrs = {'standard_name': 'projection_x_coordinate',
                               'long_name': 'x coordinate of projection',
                               'units': 'Meter'}
    mean_wetland_ds.y.attrs = {'standard_name': 'projection_y_coordinate',
                               'long_name': 'y coordinate of projection',
                               'units': 'Meter'}
    mean_wetland_ds['wetland_totalavg'].attrs = {'long_name': 'proportion of wetlands',
                                                 }
    mean_wetland_ds['wetland_totalavg'].encoding = watertable_ds[main_var].encoding
    mean_wetland_ds.rio.write_crs(mdfw_epsg, inplace = True) 
    mean_wetland_ds.to_netcdf(output_file_mwl)
    
    
#%% WILTING POINT AND WATER STRESS
def dry(result_folder, landcover = 'grassland'):
    #%%% Chargement des données :
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Paramètres généraux
    # -------------------
    setting_file = [f for f in os.listdir(result_folder) if f.endswith('.ini')]
    if len(setting_file) == 1:
        setting_file = setting_file[0]
        (config, option, binding, outputDir) = rs.parse_configuration(
            os.path.join(result_folder, setting_file))
    else:
        print('\nNot able to find the setting file in the output_folder.')
        
    cwatm_path = r"D:\2- Postdoc\2- Travaux"
    main_folder_name = '3_CWatM_EBR'
    motif = re.compile(main_folder_name + '.*')
    print("\nRacine des fichiers d'input = {}".format(
        os.path.join(cwatm_path, main_folder_name)))
    
    # Création des chemins
    # --------------------
    grassland_w2 = os.path.join(result_folder, f"{landcover}_w2_daily.nc")
    grassland_wwp2 = os.path.join(result_folder, f"{landcover}_wwp2_totalend.nc")
    
# =============================================================================
#     grassland_rws = os.path.join(result_folder, r"grassland_rws_daily.nc")
# =============================================================================

    
    # Chargements
    # -----------
    with xr.open_dataset(grassland_w2, 
                         decode_times = True, 
                         decode_coords = 'all') as grassland_w2_ds:
        grassland_w2_ds.load()
    with xr.open_dataset(grassland_wwp2, 
                         # decode_times = True, 
                         decode_coords = 'all') as grassland_wwp2_ds:
        grassland_wwp2_ds.load()
        
# =============================================================================
#     with xr.open_dataset(grassland_rws, 
#                          decode_times = True, 
#                          decode_coords = 'all') as grassland_rws_ds:
#         grassland_rws_ds.load()
# =============================================================================
    
    
    #%%% Calculs
    # ~~~~~~~~~~
    wilted_ds = xr.where(
        grassland_w2_ds[f'{landcover}_w2'] < grassland_wwp2_ds[f'{landcover}_wwp2_totalend'],
        grassland_w2_ds[f'{landcover}_w2']*0+1,
        grassland_w2_ds[f'{landcover}_w2']*0
        )
    
    output_file_wilted = os.path.join(result_folder, "wilted_daily.nc")
    wilted_ds.rio.write_crs(3035, inplace = True)
    wilted_ds.to_netcdf(output_file_wilted)
    
    # Average occurence
    mean_wilted_ds = wilted_ds.mean(dim = 'time')
    
    output_file_mwilted = os.path.join(result_folder, "wilted_avg.nc")
    mean_wilted_ds.rio.write_crs(3035, inplace = True) 
    mean_wilted_ds.to_netcdf(output_file_mwilted)
    
# =============================================================================
#     # Water stress reduction factor
#     mean_grassland_rws_ds = grassland_rws_ds.mean(dim = 'time')
#     
#     output_file_mrws = os.path.join(result_folder, "grassland_rws_avg.nc")
#     mean_grassland_rws_ds.rio.write_crs(3035, inplace = True) 
#     mean_grassland_rws_ds.to_netcdf(output_file_mrws)
# =============================================================================
    
        
    
    #%%% Problèmes et notes
    # ~~~~~~~~~~~~~~~~~~~~~
    """
    • il faut corriger la profondeur des rivières [...]
    
    • la nappe se retrouve souvent au-dessus de 0 m (2-20 cm)
        → ça peut être une charge hydraulique 
    
    • parfois la nappe au-dessus du sol de 15 m ...
        → c'est dans les carrières (c'est négligeable)
                
    • L'activation de use_soildepth_as_GWtop ne change rien aux débits, recharges...
    """
    

#%% CREATE GRAVIT_EFFSAT_timestep.nc files (gravitationnal effective saturation)
def gravit_effsat(folder_path):
    """
    

    Parameters
    ----------
    folder_path : str
        Path to the folder containing outputs (or root path when
                                               recursive exploration will be
                                               implemented)

    Returns
    -------
    grassland_gravit_effsat_daily.nc etc. files are created in the same directory.

    """
    

    file_list = os.listdir(folder_path)
    
    #%%% Loading mandatory files
    # field capacity
    wfc1_ds = xr.Dataset()
    wfc2_ds = xr.Dataset()
    wfc3_ds = xr.Dataset()
    wfc_list = [wfc1_ds, wfc2_ds, wfc3_ds]
    # saturation water content
    ws1_ds = xr.Dataset()
    ws2_ds = xr.Dataset()
    ws3_ds = xr.Dataset()
    ws_list = [ws1_ds, ws2_ds, ws3_ds]
    for layer in range(0, 3):
        for landcover in ['forest', 'grassland']:
            # field capacity
            name = f'{landcover}_wfc{layer+1}_totalend.nc'
            if name in file_list:
                with xr.open_dataset(os.path.join(folder_path, name),
                                     decode_coords = 'all',
                                     decode_times = False) as temp:
                    wfc_list[layer][landcover] = temp[list(temp.data_vars)[0]]
            # saturation water content
            name = f'{landcover}_ws{layer+1}_totalend.nc'
            if name in file_list:
                with xr.open_dataset(os.path.join(folder_path, name),
                                     decode_coords = 'all',
                                     decode_times = False) as temp:
                    ws_list[layer][landcover] = temp[list(temp.data_vars)[0]]

    
    #%%% Exploring files
    for file_ in file_list:
        if os.path.splitext(file_)[-1] == '.nc': # if the element is a NetCDF file
            name = os.path.splitext(file_)[0]
            pattern_gravit = re.compile('.*gravit.*')
            pattern_sum = re.compile('.*sum.*')
            res_gravit = pattern_gravit.findall(name)
            res_sum = pattern_sum.findall(name)
            if (len(res_gravit) == 0) & (len(res_sum) == 0): # if filename contains neither 'sum' either 'gravit'
                pattern_effsat = re.compile('effsat\d*')
                int_el = pattern_effsat.findall(name)
                if len(int_el) > 0:
                    layer = int(int_el[0][-1]) - 1
                    ext_el = pattern_effsat.split(name)
                    new_name = 'gravit_' + int_el[0]
                    new_name = new_name.join(ext_el)
                    landcover = name.split('_')[0]
                    print(f"- File '{name}' as basis for '{new_name}'")
                    
                    #%%% Computation
                    soilwater_name = f'w{layer+1}'.join(ext_el)
                    with xr.open_dataset(os.path.join(folder_path, soilwater_name + '.nc'),
                                         decode_coords = 'all',
                                         decode_times = False) as data:
                        data.load() # to unlock the ressource
                    data = data.rename({list(data.data_vars)[0]: landcover}) # to have a consistent name for operations
                    data[landcover] = (data[landcover] - wfc_list[layer][landcover]) / (ws_list[layer][landcover] - wfc_list[layer][landcover])
                    # data = data.where(data[landcover] > 0, 0)
                    data = xr.where(data[landcover] < 0, 0, data)
                    
                    # Formatting
                    data = data.rename({landcover: new_name})
                    with xr.open_dataset(os.path.join(folder_path, name + '.nc'),
                                         decode_coords = 'all',
                                         decode_times = False) as effsat:
                        data[new_name].attrs = effsat[list(effsat.data_vars)[0]].attrs
                        data[new_name].encoding = effsat[list(effsat.data_vars)[0]].attrs
                    data.rio.write_crs(3035, inplace = True)
                    
                    # Exporting
                    data.to_netcdf(os.path.join(folder_path, new_name + '.nc'))
        
        
        elif os.path.isdir(os.path.join(folder_path, file_)):
            print('') # saut de ligne
            print(rf'Exploring {file_}\...') 
            gravit_effsat(os.path.join(folder_path, file_))
                
    

#%% ANIM QGIS
def date_counter(*, output_folder, start_date, fqce = 'M', **kwargs):
    """
    % DESCRIPTION :
    Exporte une série d'images *.png servant de compteur de dates pour
    l'animation qgis.
    
    % EXEMPLES :
    > import advancedresults as ar
    > ar.date_counter(output_folder = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\processed_results\003\animation", 
                      start_date = '2000-01-01', fqce = 'M', period = 180)
    
    % ARGUMENTS :
    > start_date = date de départ
    > fqce = fréquence des pas de temps : 'D' | 'M' (défaut) | 'MS' (début du mois)
    > kwargs:
        > end_date = date de fin
            Si rien n'est spécifié, il faut qu'il y ait une 'period' de 
            spécifiée.
        > period = nombre de pas de temps.
            Si rien n'est spécifié, il faut qu'il y ait une 'end_date'
    """
    
    
    #% Get fields:
    # ------------
    if 'end_date' in kwargs:
        end_date = kwargs['end_date']
    else:
        end_date = None
    
    if 'period' in kwargs:
        period = kwargs['period']
    else:
        period = None
    
    
    #% Préparation de l'index :
    # -------------------------
    date_index = pd.date_range(start = start_date, 
                               end = end_date,  
                               periods = period, 
                               freq = fqce).strftime("%Y-%m-%d")
    
    
    #% Création et export des images :
    # --------------------------------
    for i, _date in enumerate(date_index):
        fig1, ax1 = plt.subplots(1, figsize = (3.5, 0.625)) 
        # inches à 96dpi = 336x60
        fig1.suptitle(_date, fontsize = 40)
        ax1.axis('off')
        filename = 'date_' + str(f'{i:04d}')
        fig1.savefig(os.path.join(output_folder, filename + '.png'), transparent = True)
        plt.close(fig1)
        
    return date_index    
    

#%% COMPARE NETCDF MAPS
def compare_maps(folder_ref, folder_comp, filename, mode):
    """
    Example
    -------
    va.compare_maps(folder_ref = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\017_new_data_landcover_meteo\01",
                      folder_comp = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\017_new_data_landcover_meteo\07",
                      filename = "sum_gwRecharge_monthavg.nc",
                      mode = "ratio")

    Parameters
    ----------
    folder_ref : str
        Name of the folder first to compare (reference).
    folder_comp : str
        Name of the folder to compare to the first folder.
    filename : str
        Name of the file to process.
    mode : str
        ratio | diff | relative difference.

    Returns
    -------
    Create a *.nc file in the folder "D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\processed_results"

    """
    
    #%% Load data
    # -----------
    print('\nLoading data...')
    # If the extension has not been included, include it:
    if os.path.splitext(filename)[-1] == '':
        print(' NB: Extension has not been indicated. Netcdf files will be considered.')
        filename = filename + '.nc'
        
    # Check if files exist. Otherwise show the closest name
    if not os.path.isfile(os.path.join(folder_ref, filename)) or not os.path.isfile(os.path.join(folder_comp, filename)):
        print(' WARNING: Issues with filename...')
        space_ref = [f for f in os.listdir(folder_ref) 
                     if os.path.isfile(os.path.join(folder_ref, f)) 
                     and os.path.splitext(f)[-1] == '.nc']
        space_comp = [f for f in os.listdir(folder_comp) 
                     if os.path.isfile(os.path.join(folder_comp, f)) 
                     and os.path.splitext(f)[-1] == '.nc']
        
        if not os.path.isfile(os.path.join(folder_ref, filename)):
            print('    File not found in first folder')
            closest_match = difflib.get_close_matches(filename, space_ref)
            if not closest_match: 
                common_match = ["- no match -"]
            else:  
                i = 0
                f = closest_match[i]
                while f not in space_comp and i < len(closest_match)-1:
                    i+=1
                    f = closest_match[i]
                common_match = f
            
        if not os.path.isfile(os.path.join(folder_comp, filename)):
            print('    File not found in second folder')
            closest_match = difflib.get_close_matches(filename, space_comp)
            if not closest_match: 
                common_match = ["- no match -"]
            else:  
                i = 0
                f = closest_match[i]
                while f not in space_ref and i < len(closest_match)-1:
                    i+=1
                    f = closest_match[i]
                common_match = f
            
        print('    Closest file to this name is "{}"'.format(common_match))
        filename = common_match
        print('    IMPORTANT: This file will be processed here')
    
    
    # Load datasets
    with xr.open_dataset(os.path.join(folder_ref, filename), 
                         decode_coords = 'all', 
                         decode_times = False) as data_ref:
        data_ref.load() # to unlock the resource
    
    with xr.open_dataset(os.path.join(folder_comp, filename), 
                         decode_coords = 'all', 
                         decode_times = False) as data_comp:
        data_comp.load() # to unlock the resource
    
    
    
    
    #%% Compute
    # ---------
    print('\nComputing...')
    if mode.casefold() == "ratio":
        mode_prefix = 'RATIO'
        res = data_comp/data_ref
        
    elif mode.casefold() in ['difference', 'diff']:
        mode_prefix = 'DIFF'
        res = data_comp-data_ref
        
    elif mode.casefold() in ['relative difference', 'rel diff', 'reldiff', 'diffrel']:
        mode_prefix = 'RELDIFF'
        res = (data_comp-data_ref)/data_ref
        
    
    #%% Export
    # --------
    print('\nExporting...')
    motif = re.compile('\d{3,3}.*\d{2,2}')
    extr_str_ref = motif.search(folder_ref).group()
    id_ref = extr_str_ref[0:3] + 'r' + os.path.split(folder_ref)[-1]
    extr_str_comp = motif.search(folder_comp).group()
    id_comp = extr_str_comp[0:3] + 'r' + os.path.split(folder_comp)[-1]
    output_name = os.path.join(r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\processed_results",
                               '_'.join([os.path.splitext(filename)[0], mode_prefix, id_comp, 'vs', id_ref]) + '.nc'
                               )
    
    res.to_netcdf(output_name)
    
    print(' Result file successfully created: \n {}'.format(output_name))
    
    return res
    

#%% GET FOLDERS : Internal function to get the current folder
def get_folders():
    script_folder = os.path.dirname(os.path.realpath(__file__))
    
    # Defining the root, result and settings folders (should be user-adjusted)
    root_folder = os.path.dirname(os.path.dirname(script_folder))
    result_folder = os.path.join(root_folder, 'results', 'raw_results')
    settings_design_folder = os.path.join(root_folder, 
                                          'data',
                                          'input_1km_LeMeu',
                                          'settings_and_experiment_designs',
                                          )
    
    return [script_folder, root_folder, result_folder, settings_design_folder]

    