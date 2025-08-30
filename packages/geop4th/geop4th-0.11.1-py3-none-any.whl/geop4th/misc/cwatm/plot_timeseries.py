# -*- coding: utf-8 -*-
"""
Created on Sun May  4 05:34:00 2025
Based on D:\HyMoPy\results\processed\time_res.py

@author: Alexandre Kenshilik Coche

Tools to visualize CWatM simulation results.
This script is not a function nor a class. For now it is designed to be run 
inside Spyder, section by section.
"""

#%% IMPORTS
from geop4th import (
    geobricks as geo)
from geop4th.graphics import (
    ncplot as nc,
    cmapgenerator as cmg)
import numpy as np
import os
import datetime
import pandas as pd
from pathlib import Path
import yaml
from geop4th.misc.cwatm import readsettings as rs
from plotly.subplots import make_subplots


#%% Utilitary function to extract the correct language from texts
def translate(text, lang):
    if isinstance(text, dict):
        if lang in text:
            return text[lang]
        else:
            print(f"Warning: {lang} language is not included: {text[text.keys()[0]]} is returned")
            return text[text.keys()[0]]
    
    elif isinstance(text, list):
        print(f"Warning: text is not a dict: {text[0]} is returned")
        return text[0]
    
    else:
        print(f"Warning: text does not contain several language versions: {text} is returned")
        return text


#%% LOAD DATA & PARAMETERS [ USER CHOICES]

# root_path = Path(os.path.dirname(os.path.realpath(__file__)))
root_path = Path(r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\processed_results\PaysBasque\plots\7th visu")

with open(os.path.join(root_path, 'settings.yaml'), 'r') as file_object:
    settings = yaml.load(file_object, Loader = yaml.SafeLoader)

# ---- Language
### User-defined language:
lang = settings['language'] # 'en' | 'fr'

# ---- Graphical plot size
plotsize = settings['plotsize'] # 'paper' | 'wide' | (width, height)

# ---- yscale
yscale = settings['yscale'] # 'linear' | 'log'
if 'ytype' in settings:
    ytype = settings['ytype'] # 'extensive' | 'intensive'
    area_ds = geo.load_any(settings['area'])
    area_column = settings['area_column']
else:
    ytype = 'extensive'

# ---- Input data to load
res_path = Path(settings['res_path'])

run_dict = settings['run_dict']
# The keys of this dict corresponds to the folder names
n_curves = len(run_dict)

# =============================================================================
# run_df = pd.DataFrame.from_dict(run_dict, orient = 'index', columns = ['name'])
# run_df.set_index('id', inplace = True)
# =============================================================================

# ---- Coordinates
# (Coordinates where results will be extracted)
### User-defined coordinates


coords_data = settings['coords_data']

gauge_ds = None
if coords_data == 'auto':
    gauge_filepath = settings['gauge_vector']
    gauge_ds = geo.load_any(gauge_filepath)
    gauge_column = settings['gauge_column']
    gauge_values_column = settings['gauge_values_column']
    
else:
    epsg_coords = settings['epsg_coords']
    coords_df = pd.DataFrame(coords_data, columns = ['coords', 'site', 'add_title'])

# Alternatively, coords can also be a filepath to a mask. In that case, the
# mean value over this mask will be retrieved.

# ---- Variable
var_selection = settings['var_selection']

# ---- Timestep
timestep = settings['timestep'] # 'daily' | 'monthavg' | 'monthend'

# ---- Figure title
fig_title = settings['fig_title']

# ---- Optional parameters
if 'rolling' in settings:
    rolling = settings['rolling']
    name_rolling = f'_roll{rolling}'
else:
    rolling = None
    name_rolling = ''

# ---- Optional graphical parameters
if 'lstyle' in settings:
    lstyle = settings['lstyle']
else:
    lstyle = None
    
if 'color_groups' in settings:
    color_groups = settings['color_groups']
    group_sum = sum(color_groups)
    if group_sum < n_curves:
        color_groups.append(n_curves - group_sum)
else:
    color_groups = [n_curves]



#%% INITIALIZATION
# ---- Graphical plot size
# Two formats are defined here: wide and paper
if plotsize == 'wide':
    plotsize = (1500, 150) # (width, height)
elif plotsize == 'paper':
    plotsize = (1000, 100)

# ---- Timestep
if timestep == 'daily':
    add_var = ''
    add_ts_title = dict(en = "daily", fr = "journalièr(es)")
elif timestep == 'monthavg':
    add_var = '_monthavg'
    add_ts_title = dict(en = "daily (monthly average)", 
                        fr = "journalièr(es) (moyennes mensuelles)")
elif timestep == 'monthend':
    add_var = '_monthend'
    add_ts_title = dict(en = "daily (month end value)", 
                        fr = "journalièr(es) (valeur de fin de mois)")

xaxis_label = dict(en = 'Time [d]', fr = 'Temps [j]')

# ---- Metric
# =============================================================================
# var_info = [['sum_gwRecharge', ["Recharge", "Recharge"], 1000], # from [m/d] to [mm/d]
#             ['sum_capRiseFromGW', ["Capillary rise", "Remontées capillaires"], 1000],
#             ['totalET', ["Total evapotranspiration", "Evapotranspiration totale"], 1000],
#             ['sum_actTransTotal', ["", ""], 1000],
#             ['sum_w1', ["topsoil water content", "Humidité du sol de surface"], 1000],
#             ['discharge', ["Discharge", "Débit"], 1],
#             ['riverbedExchangeM', ["Watertable-river exchanges", "Echanges rivière-nappe"], 1000],
#             ['baseflow', ["Baseflow", "Débit de base"], 1000],
#             ['Rain', ['Rain', 'Pluie'], 1000],
#             ['Snow', ['Snow', 'Neige'], 1000],
#             ['sum_directRunoff', ['Direct runoff', 'Ruissellement direct'], 1000],
#             ['sum_interflow', ['Interflow', 'Interflow'], 1000],
#             # [...],
#             ]
# 
# var_df = pd.DataFrame(var_info, columns = ['var', 'var_title', 'unit_conv'])
# var_df.set_index('var', inplace = True)
# =============================================================================

var_dict = {
    'sum_gwRecharge': [dict(en = "Recharge", fr = "Recharge"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_capRiseFromGW': [dict(en = "Capillary rise", fr = "Remontées capillaires"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_gwRecharge_net': [dict(en = "Net recharge", fr = "Recharge nette"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'totalET': [dict(en = "Total ETR", fr = "ETR totale"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_actTransTotal': [dict(en = "Total transpiration", fr = "Transpiration totale"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_actBareSoilEvap': [dict(en = "Bare soil evaporation", fr = "Evap. sol nu"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_openWaterEvap': [dict(en = "Open water evaporation", fr = "Evap. surfaces en eau"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_interceptEvap': [dict(en = "Intercepted precipitations evaporation", fr = "Evap. précip. interceptées"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'snowEvap': [dict(en = "Snow evaporation", fr = "Evap. neige"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'addtoevapotrans': [dict(en = "Evaporation from water pumped", fr = "Evap. prélèvements d'eau"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_w1': [dict(en = "Surface soil humidity", fr = "Humidité du sol de surface"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_w2': [dict(en = "Rhizosphere humidity", fr = "Humidité du sol (rhizosphère)"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_w3': [dict(en = "Bulk soil humidity", fr = "Humidité du sol profond"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_soil': [dict(en = "Total soil humidity", fr = "Humidité du sol total"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'grassland_effsat2': [dict(en = "Effective soil saturation (rhizosphere)", fr = "Saturation efficace du sol (rhizosphère)"), 100],
    'baseflow': [dict(en = "Baseflow", fr = "Débit de base"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'baseflow_no_drain_up': [dict(en = "Baseflow (exclud. drainage)", fr = "Débit de base (hors drainage)"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'riverbedExchangeM': [dict(en = "River-to-watertable flow", fr = "Fuites sous rivière"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'Precipitation': [dict(en = "Precipitations", fr = "Précipitations"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'Rain': [dict(en = "Rain", fr = "Pluie"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'Snow': [dict(en = "Snow", fr = "Neige"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_runoff': [dict(en = "Runoff and interflow", fr = "Ruissellement superficiel et hypodermique"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'sum_directRunoff':  [dict(en = "Runoff", fr = "Ruissellement"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'discharge': [dict(en = "Discharge", fr = "Débits"), 1, dict(en = 'm<sup>3</sup>/s', fr = 'm<sup>3</sup>/s')],
    'discharge_local': [dict(en = "Discharge (local)", fr = "Débits (local)"), 100, ['%', '%']],
    'discharge_distant': [dict(en = "Discharge (upstream)", fr = "Débits (amont)"), 1, dict(en = 'm<sup>3</sup>/s', fr = 'm<sup>3</sup>/s')],
    'sum_interflow': [dict(en = "Interflow", fr = "Ecoulement hypodermique"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'drainage_downward': [dict(en = "Drainage downwards", fr = "Drainage descendant"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    'drainage_upward': [dict(en = "Drainage upwards", fr = "Drainage ascendant"), 1000, dict(en = 'mm/d', fr = 'mm/j')],
    }

var_df = pd.DataFrame.from_dict(var_dict, 
                                orient = 'index',
                                columns = ['var_title', 'unit_conv', 'unit'])

# var_list contains all information for the variables defined by the user
var_list = var_df.loc[var_selection]


# ---- Check parameters difference between specified runs
print("\nAnalysis of parameter changes...")
param_list = []

for run in run_dict:
    # Read settings file
    (config, option, binding, outputDir) = rs.parse_configuration(res_path / Path(run) / Path(f"settings_{run}.ini")) 
    param_list.append({**option, **binding})

param_df = pd.DataFrame(param_list, index = run_dict.keys())

n_elements = param_df.nunique()
n_elements = n_elements[n_elements > 1]

for p in n_elements.index:
    print(f"   . {p}: {' | '.join(param_df[p].astype(str))}")
    
# ---- Coords if auto
if coords_data == 'auto':
    # Get run CRS (from mask CRS)
    for run in param_df.index:
        mask_path = Path((res_path / Path(run) / Path(f"settings_{run}.ini")).parent, param_df.loc[run, 'MaskMap']).resolve()
        mask_ds = geo.load_any(mask_path)
        mask_crs = mask_ds.rio.crs.to_epsg()
        param_df.loc[run, 'crs'] = mask_crs
        
    if len(param_df.crs.unique()) > 1:
        print("\nErr: Multiple CRS accross runs is not supported yet.")
    else:
        epsg_coords = mask_crs
        # Reproject gauge vector file
        gauge_ds = geo.reproject(gauge_ds, dst_crs = epsg_coords)
        coords_data = []
        for gauge in gauge_ds[gauge_column].unique():
            coords_data.append(
                [gauge_ds[gauge_ds[gauge_column] == gauge].iloc[0].geometry,
                 gauge, 
                 # gauge,
                 gauge[0:4] + ' ' + gauge[4:8] + ' ' + gauge[8:], # version adapted to hydro.eaufrance discharge data
                 ])
        
        coords_df = pd.DataFrame(coords_data, columns = ['coords', 'site', 'add_title'])
        
    
# ====== Example ==============================================================
# coords_data = [
#                [(-0.77442,     43.48537),     "Q542102001", "Q542102001"],
#                [(-1.390460897, 43.356674095), "Q931251001", "Q931251001"],
#                ]
# =============================================================================

# Adapt the size of the figure according to the number of plots
plotsize = (plotsize[0], plotsize[1]*0.22 + plotsize[1]*0.78*coords_df.shape[0])

# ---- x limits (dates)
startdate = pd.to_datetime(param_df['StepStart'], dayfirst = True).min()
if not all(param_df.loc[idx, 'StepEnd'].isnumeric() for idx in param_df.index):
    enddate = pd.to_datetime(param_df['StepEnd'], dayfirst = True).max()
else:
    enddate = startdate + pd.to_timedelta(param_df['StepEnd'].astype(int).max(), unit = 'D')
xlim = (startdate, enddate)

# ---- Colorscale 
### [USER CHOICE]
# =============================================================================
# color_map = np.vstack([cmg.discrete('wong', alpha = 1,
#                                    black = False, alternate = False)[0:4],
#                       cmg.discrete('wong', alpha = 1,
#                                    black = False, alternate = False)[0:4],
#                       cmg.discrete('wong', alpha = 1,
#                                    black = False, alternate = False)[0:4],
# # =============================================================================
# #                       cmg.discrete('wong', alpha = 1, 
# #                                         black = False, alternate = False),
# #                       cmg.discrete('wong', alpha = 1, 
# #                                         black = False, alternate = False)
# # =============================================================================
#                       ])
# =============================================================================

### [AUTOMATIC] Optimal definition of colormap based on the number of runs
color_map = np.empty((n_curves, 4))
i = 0
for c_group in color_groups:
    if c_group <= 6:
        cmap = cmg.discrete(sequence_name = 'ibm', alpha = 0.8, black = False,
                                 alternate = False, color_format = 'float')
        if c_group == 2:
            cmap = cmap[[2, 4]]
        elif c_group == 3:
            cmap = cmap[[0, 2, 4]]
        elif c_group == 4:
            cmap = cmap[[0, 2, 4]]
            add_color = cmg.discrete(sequence_name = 'wong', alpha = 0.8, black = False,
                                     alternate = False, color_format = 'float')[0, :]
            cmap = np.vstack([cmap, add_color])
        else:
            cmap = cmap[0:c_group, :]
    elif (c_group > 6) & (c_group <= 9):
        cmap = cmg.discrete(sequence_name = 'wong', alpha = 0.8, black = False,
                            alternate = False, color_format = 'float')
        cmap = cmap[::-1] 
    else:
        cmap = cmg.discrete(sequence_name = 'trio', alpha = 0.8, black = False,
                            alternate = False, color_format = 'float')
    
    color_map[i : i + c_group, :] = cmap[0 : c_group, :]
    
    i += c_group

#%% LOAD RESULTS
figweb_dict = dict()
ylim_dict = dict()
results_dict = dict()

# ---- For each variable...
for var in var_list.index:
    print(f"\nLoading {var}...")
    
    results_dict[var] = dict()
    
    # y limits are common for all subplots
    ymin = 0
    ymax = 0
    
    # ---- For each coords...
    # One subplot = one coords
    for i_coords in coords_df.index: # i_coords = count of coords
        
        print(f"\n   _ location {i_coords+ 1 }/{coords_df.shape[0]}")

        i_run = 0 # i_run = count of runs
        results_dict[var][coords_df.loc[i_coords].site] = dict() # for each coords, results will be appended to results[var]
        
        if ytype == 'intensive':
            area_val = area_ds[area_ds[area_column] == coords_df.loc[i_coords].site].geometry.area.item()
            var_df.loc[var, 'unit'] = dict(en = 'mm/d', fr = 'mm/j')[lang]
        
        # ---- For each run...
        for run in run_dict:
            print(f"\n      . run {run} : ")
            
            # Load results
            results = geo.timeseries(
                data = res_path / Path(run) / Path(var + '_' + timestep + '.nc'),
                coords = coords_df.loc[i_coords].coords, 
                coords_crs = epsg_coords,
                data_crs = epsg_coords
                )  

            # Convert results pd.DataFrame into pd.Series by keeping only the first column
            results = results.iloc[:,0]
            
            # Apply unit conversion
            results = results * var_list.loc[var, 'unit_conv']
            
            # Apply quantity conversion (extensive -> intensive) if specified
            if ytype == 'intensive':
                results = results / area_val *1000 *60*60*24
            
            # Apply rolling average
            if rolling is not None:
                results = results.rolling(rolling, center = True).mean()
            
            # Determine y limits
            ymin = min(ymin, results.min())
            ymax = max(ymax, results.max()) 
            print(f"\n---\nymax = {ymax}\n---\n")
            if yscale == 'log':
                ymin = np.log10(ymin/10)
                ymax = np.log10(ymax)
                
            # Store results
            results_dict[var][coords_df.loc[i_coords].site][run] = results

            i_run += 1
    
    ylim_dict[var] = (ymin, ymax)
    
    

#%% PLOT RESULTS
for var in var_list.index:
    # ---- Plot
    print(f"\nPlotting {var}...")
    # Reminder: one subplot = one coords
    
    cols = 2 # subplots are dispatched on 2 columns
    rows = int(np.ceil(coords_df.shape[0]/cols)) # number of rows of subplots
    
    figweb = make_subplots(rows = rows, cols = cols, 
                           # row_heights = [0.6, 0.4],
                           shared_xaxes = True,
                           shared_yaxes = True,
                           vertical_spacing = 0.04,
                           horizontal_spacing = 0.04,
                           subplot_titles = [
                               "<span style='color:#7f7f7f;'>" + translate(coords_df.loc[c].add_title, lang) + "</span>" 
                                             for c in coords_df.index],
                           # x_title = ['Time [d]', 'Temps [j]'][lang], # general x axis title
                           )
    
    for i_coords in coords_df.index: # i_coords = count of coords
    
        # Plot results
        if gauge_ds is not None:
            # Reference
            try:
                ref = gauge_ds.loc[gauge_ds[gauge_column] == coords_df.loc[i_coords].site, ['time', gauge_values_column]]
                # Apply unit conversion
                ref = ref.set_index('time') * var_list.loc[var, 'unit_conv']
                # Apply quantity conversion (extensive -> intensive) if specified
                if ytype == 'intensive':
                    area_val = area_ds[area_ds[area_column] == coords_df.loc[i_coords].site].geometry.area.item()
                    ref = ref / area_val *1000 *60*60*24
                # Apply rolling average
                if rolling is not None:
                    ref = ref.rolling(rolling, center = True).mean()
            except:
                print("Warning: `gauge_vector` does not contain values needed for reference")
                ref = None
            
            # Legend is displayed only for the first subplot (= first coords)
            showlegend = True
            if i_coords > 0:
                showlegend = False
            
            [_, _, figweb] = nc.plot_time_series(data = ref,
                                                 labels = translate(dict(en = 'data', fr = 'données'), lang),
                                                 linecolors = [0, 0, 0],
                                                 lstyles = '-',
                                                 lwidths = 0.5,
                                                 figweb = figweb,
                                                 row = np.floor((i_coords)//2) + 1, 
                                                 col = (i_coords)%2 + 1,
                                                 legendgroup = -1,
                                                 showlegend = showlegend,
                                                 # legendgrouptitle_text = 'test',
                                                 )
    
        i_run = 0 # i_run = count of runs
        for run in run_dict:
            
            # Legend is displayed only for the first subplot (= first coords)
            showlegend = True
            if i_coords > 0:
                showlegend = False

            [_, _, figweb] = nc.plot_time_series(data = results_dict[var][coords_df.loc[i_coords].site][run],
                                                 labels = translate(run_dict[run], lang),
                                                 linecolors = color_map[i_run],
                                                 lstyles = lstyle[i_run],
                                                 lwidths = 1,
                                                 figweb = figweb,
                                                 row = np.floor((i_coords)//2) + 1, 
                                                 col = (i_coords)%2 + 1,
                                                 legendgroup = i_run,
                                                 showlegend = showlegend,
                                                 # legendgrouptitle_text = 'test',
                                                 )

# =============================================================================
#         [_, _, figweb] = nc.plot_time_series(data = results,
#                                              labels = run_dict.keys(),
#                                              linecolors = color_map,
#                                              # lstyle = ['dotted', '-', '-', '-'],
#                                              lwidths = 1,
#                                              figweb = figweb,
#                                              row = np.floor((i-1)//2) + 1, 
#                                              col = (i-1)%2 + 1,
#                                              legendgroup = 1,
#                                              # legendgrouptitle_text = 'test',
#                                              )
# =============================================================================
            
            i_run += 1
            
            figweb_dict[var] = figweb
    


    # ---- Layout
    figweb_dict[var].update_layout(#font_family = 'Open Sans',
                         title = {'font': {'size': 20},
                                  'text': translate(fig_title, lang) + f": {var}",
                                  'xanchor': 'center',
                                  'x': 0.45,
                                  },
                         legend = {'title': {'text': 'Légende'},
                                   'xanchor': 'right',
                                   'y': 1.1,
                                   'xref': 'container',
                                   'yanchor': 'top',
                                   'bgcolor': 'rgba(255, 255, 255, 0.2)',
                                   },
                         plot_bgcolor = "white",
                         # legend = {'groupclick': 'togglegroup'},
                         width = plotsize[0], # paper[0], # wide[0],
                         height = plotsize[1], # paper[1], # wide[1],
                         )
    
    # Suptitle
    if rolling is not None:
        figweb.add_annotation(xanchor = 'center',
                              yanchor = 'top',
                              y = 1.05,
                              xref = 'paper',
                              yref = 'paper',
                              showarrow = False,
                              font = {'size': 16},
                              text = translate({'en': f"{rolling} rolling average",
                                                'fr': f"moyenne glissante {rolling}"}, lang),
                              )
    
    # Display only axis names when necesseray
    # x-axis name is displayed only on the last row of subplots
    for ix in [coords_df.shape[0]-1, coords_df.shape[0]]:
        if ix in [0, 1]: ix == ''
        figweb_dict[var].update_layout(
            {f'xaxis{ix}': {'title': {'font': {'size': 16},
                                      'text': translate(xaxis_label, lang)},
                            'range': xlim,
                            'showticklabels': True,
                            },
             })
    
    # y-axis name is displayed only on the first column of subplots
    for iy in range(1, coords_df.shape[0]+1, 2):
        if iy == 1: iy == ''
        figweb_dict[var].update_layout(
            {f'yaxis{iy}': {'title': {'font': {'size': 16},
                                      'text': f"{translate(var_df.loc[var].var_title, lang)} ({translate(var_df.loc[var].unit, lang)})"},
                            # 'text': field_title + ' [m3/s]'},
                            },
             })
    
    # Besides shared x-axis and y-axis, axis are linked
    figweb_dict[var].update_xaxes(matches = 'x',
                                  showline = True, linewidth = 1, 
                                  linecolor = '#7f7f7f', mirror = True)
    figweb_dict[var].update_yaxes(matches = 'y',
                                  showline = True, linewidth = 1, 
                                  linecolor = '#7f7f7f', mirror = True,
                                  type = yscale,
                                  range = ylim_dict[var])

    # ---- Figure export
    figweb_dict[var].write_html(root_path / Path('_'.join([
        var,
        timestep,
        yscale + name_rolling,
        datetime.datetime.now().strftime("%Hh%M"),
        lang,
        ]) + '.html'
        )
        )
            
        
        
    

