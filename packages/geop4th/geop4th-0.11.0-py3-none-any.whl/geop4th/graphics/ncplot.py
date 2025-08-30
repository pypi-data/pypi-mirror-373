# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 13:16:05 2022

@author: Alexandre Kenshilik Coche
@contact: alexandre.co@hotmail.fr
"""

#%% Imports:
import pandas as pd
import numpy as np
import xarray as xr
xr.set_options(keep_attrs = True)
import matplotlib.pyplot as plt
import numbers
from geop4th.graphics import cmapgenerator as cmg

# import matplotlib.pyplot as plt, mpld3
# import plotly.express as px
import plotly.graph_objects as go
# import plotly.graph_objects as go
# import plotly.offline as offline
# from plotly.subplots import make_subplots


#%% precip_like_discharge
def precip_like_discharge(*, input_file):
    """
    % EXEMPLE :
    import cwatplot as cwp
    cwp.precip_like_discharge(input_file = input_file) 
    
    % ARGUMENTS
    > input_file = fichier des précipitations
    > freq = 'daily' | 'monthly'
    """  
    
    
# ========== TEMP INPUTS ======================================================
#     # Monthly
#     input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\001_prelim_cotech\2022-03-19_base\Precipitation_monthavg.nc"
# 
#     # Daily
#     input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\data\input_1km_LeMeu\meteo\pr.nc"
#     input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\002_test_coeff\2022-03-25_test3\Precipitation_daily.nc"
# =============================================================================

    try:
        with xr.open_dataset(input_file) as dataset:
            dataset.load() # to unlock the resource
    except ValueError: # unable to decode time units 'Months since 1901-01-01'
                       # with "calendar 'proleptic_gregorian'"
        with xr.open_dataset(input_file, decode_times = False) as dataset:
            dataset.load()
        # Reconstruire le temps :
        start_date = pd.Series(pd.date_range(
            '1901-01', periods = int(dataset.time[0]) + 1, freq = '1D')).iloc[-1]
        date_index = pd.date_range(start = start_date, 
                                     periods = len(dataset.time), freq = '1D') 
        # Remplacer 'D' par 'MS' si les données sont en mensuel
        dataset['time'] = date_index  
    
    
    #% Calculer le bilan d'eau :
    # --------------------------
# =============================================================================
#     # Clipper les données avec le mask du BV    
# =============================================================================
    dataset = dataset.mean(dim = ('x', 'y'))

# ==== Pour calculer la surface, clipper aussi avec le mask ===================
#     with xr.open_dataset(r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\data\input_1km_LeMeu\landsurface/topo/cellarea.nc") as surface:
#         surface.load() # to unlock the resource
#     surface = surface.sum(dim = ('x', 'y'))
#     surface = float(surface.cellarea)
# =============================================================================
    surface = 534000000 # [m2] (le BV topographique du Meu fait 471 851 238 m2)
    mm2m = 1e-3 # from mm
    d2sec = 86400 # 1 day
    # Remplacer n_sec par 86400*30 si les données sont en mensuel
    dataset = dataset * surface / d2sec
    
    # # precip = dataset.to_pandas()
    # precip = pd.DataFrame()
    # precip['time'] = dataset['time'].data
    # precip['val'] = dataset['pr'].data
    precip = dataset
    
    return precip
    

    #% Plot :
    # -------
    # dataset.pr.plot(x = 'time', ax = ax1, color = 'blue', label = 'precip') 
    precip.plot(x = 'time', y = 'val', ax = ax1, color = 'blue', label = 'precip')


#%% tss_to_dataframe
def tss_to_dataframe(*, input_file, skip_rows, start_date):
    """
    Example
    -------
    # Base
    base = cwp.tss_to_dataframe(input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\001_prelim_cotech\2022-03-19_base\discharge_daily.tss",
                         skip_rows = 4,
                         start_date = '1991-08-01')
    # Virginie
    virg = cwp.tss_to_dataframe(input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\data\%ARCHIVE fichiers Virginie\simulations\sim0\discharge_daily.tss",
                         skip_rows = 0,
                         start_date = '1991-01-01')
    # Nouvelle base
    base = cwp.tss_to_dataframe(input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\003_artif\2022-03-25_base\discharge_daily.tss",
                         skip_rows = 4,
                         start_date = '2000-01-01')
    # Données
    data = cwp.tss_to_dataframe(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\10- Stations et debits\Debits\HydroDataPy\Stations_Bretagne\meu_montfort.csv",
                         skip_rows = 0,
                         start_date = '1969-01-01')
    # Precip
    precip = cwp.tss_to_dataframe(input_file = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\results\raw_results\003_artif\2022-03-25_base\Precipitation_daily.tss",
                         skip_rows = 4,
                         start_date = '2000-01-01')
    precip.val = precip.val*534000000/86400
    precip['rolling_mean'] = precip['val'].rolling(10).mean()
    
    Parameters
    ----------
    * : TYPE
        DESCRIPTION.
    input_file : TYPE
        DESCRIPTION.
    skip_rows : TYPE
        DESCRIPTION.
    start_date : TYPE
        DESCRIPTION.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    """
    
    #%% Implémentations futures :
    # ---------------------------
    # Récupérer la start_date à partir du fichier de settings indiqué au début
    # du fichier *.tss., et regarder ensuite le SpinUp
    
    
    #%% Récupération des inputs :
    # ---------------------------
    if start_date == 'std':
        print('> Pas encore implémenté...')
        # récupérer la start_date du fichier de settings
    else:
        start_date = pd.to_datetime(start_date)
    print('> start_date = ' + str(start_date))
    
    
    #%% Création des dataframes :
    # ---------------------------
    df = pd.read_csv(input_file, sep = r"\s+", header = 0, names = ['id', 'val'], skiprows = skip_rows)
    date_indexes = pd.date_range(start = start_date, 
                                 periods = df.shape[0], freq = '1D')
    df['time'] = date_indexes
    return df
        
    

#%% plot_time_series
def plot_time_series(*, figweb = None, data, labels, title = 'title', linecolors = None, 
                     fillcolors = None, cumul = False, date_ini_cumul = None, reference = None,
                     ref_norm = None, mean_norm = False, mean_center = False,
                     legendgroup = None, legendgrouptitle_text = None, stack = False,
                     col = None, row = None, lwidths = None, lstyles = None, 
                     yaxis = "y1", fill = None, mode = "lines", markers = None,
                     showlegend = True, visible = True, bar_widths = None):
    
    """
    Description
    -----------
    This function provides a wrapper to facilitate the use of plotly.graph_objects 
    class.
    It facilitates the input of several arguments:
        - data can be passed in any format
        - colors can be passed in any format (np.arrays, lists of strings...) \
which makes it possible to use indifferently *plotly* or *matplotlib* colormaps functions.
        - colors can be passed universally as ``linecolors`` and ``fillcolors`` argument, no matter \
what graphical function is used then by plotly (for instance go.Bar normally needs \
colors to be passed in the marker dict whereas go.Scatter needs colors to be passed \
in the line dict as well as through an fillcolor argument)
    
    It also offers additional treatments in an easy way:
        - plot cumulative values
        - normalized values

    This function is particularly appropriate to plot time series.
    
    Example
    -------
    import cwatplot as cwp
    [_, _, figweb] = cwp.plot_time_series(data = [dfA, dfV], 
                                          labels = ['Altrui', 'Vergogn'])

    
    Parameters
    ----------
    figweb: plotly figure
        Can plot on top of a previous plotly figure.
    data: array of pandas.DataFrames
        Data to plot.
    labels: array of strings
        Texts for legend.
    title: string
        Title used for the matplotlib figure (fig1, ax1). Not used for plotly
        figure (figweb).
    linecolors: np.array
        Colors are stored in [R, G, B, Alpha].
        For instance: linecolors = [[1.0, 0.5, 0.4, 1],[...]].
    cumul: bool
        Option to plot cumulated curves (True).
    date_ini_cumul: string
        The string should indicate the date in the format 'YYYY-MM-DD'.
        (for instance: date_ini_cumul = '2000-07-31')
        Only used when cumul = True.
    reference: pandas.DataFrame
        Used for displaying metrics (NSE, NSElog, VOLerr), computed against
        the reference data provided here.
    ref_norm: pandas.DataFrame (or xarray.DataSet, beta version...)
        Used for plotting values normalized against the provided reference data.
    mean_norm: bool
        Option to normalize each curve against its mean (True).
    mean_center: bool
        Option to center each curve on its mean (True).
    legendgroup: string
        To group curves under the provided group identifier.
        One group at a time.
    legendgrouptitle_text:
        Text associated with the group identifier.
    stack: bool
        Option to plot stacked curves (True).
    col: int
        Column number for subplots.
    row: int
        Row number for subplots.
    visible: {True, False, "legendonly"}, optional, default True
        Determines whether or not this trace is visible. 
        If ``"legendonly"``, the trace is not drawn, but can appear as a legend 
        item (provided that the legend itself is visible).
    mode: {"markers", "lines", "lines+markers", "bar"}, optional, default "lines"
        To select the representation mode.
    markers : list of dict

    Returns
    -------
    fig1: matplotlib figure
        OBSOLETE: recent developments (normalized curves,
        stacked curves...) have not been implemented in this figure.
    ax1: matplotlib axis
        Related to the previous figure. OBSOLETE.
    figweb: plotly figure
        This figure version includes all options.
    """ 
    
    # ---- Initialization of data
    # ============================
    # 0. if data is None
    if data is None:
        print("Error: `data` is None")
        return None, None, figweb
    
    # 1. if data is a single xarray.Dataarray, it is embedded into a list
    if isinstance(data, xr.DataArray):
        data = [data]
    # 2. if data is a single pandas.Series, it is embedded into a list
    elif isinstance(data, pd.Series):
        data = [data]
    # 3. 
    elif isinstance(data, xr.Dataset):
        # 3-A. if there is only one data_vars, it is embedded into a list
        if len(data.data_vars) == 1:
            data = [data]
        # 3-B. if there are more than one data_vars, it is split into a list of several Datasets
        else:
            data = [data.loc[var] for var in data.data_vars]
    # 4. if data is a single pandas.DataFrame, we first determine if this frame
    # contains a single data set, or several
    elif isinstance(data, pd.DataFrame):
        # 4-A. if there is only one column, it is embedded into a list
        if len(data.columns) == 1:
            data = [data]
        # 4-B. if there are more than one column, we determine whether the first column is the time index
        else:
            # 4-B-1. if there is a datetime column
            if data.select_dtypes(include=['datetime', 'datetimetz']).shape[1] > 0:
                assumed_time_col = data.select_dtypes(include=['datetime', 'datetimetz']).columns[0]
                data = [data[[assumed_time_col, c]] for c in data.columns]
            # 4-B-2. if not, the index is assumed to be the time index
            else:
                data = [data[[c]] for c in data.columns]

    n_curves = len(data)
    

    # ---- Convert to lists
    # ======================
    if labels is None:
        labels = [None]*n_curves
    else:
        if isinstance(labels, str):
            labels = [labels]
        else:
            labels = list(labels)
    if len(labels) != n_curves:
        print(f"/!\ {n_curves} data series but {len(labels)} labels")
    
    if lwidths is None:
        lwidths = [None]*n_curves
    else:
        if isinstance(lwidths, numbers.Number):
            lwidths = [lwidths]*n_curves
        elif isinstance(lwidths, tuple):
            lwidths = list(lwidths)
    
    if lstyles is None:
        lstyles = [None]*n_curves
    else:
        if isinstance(lstyles, str):
            lstyles = [lstyles]*n_curves
        elif isinstance(lstyles, tuple):
            lstyles = list(lstyles)
        
    if bar_widths is None:
        bar_widths = [None]*n_curves
    else:
        if isinstance(bar_widths, numbers.Number):
            bar_widths = [bar_widths]*n_curves
    
    # Handling colors
    if linecolors is None:
        linecolors = [None]*n_curves
    else:
        linecolors = cmg.to_rgba_str(linecolors)
        if isinstance(linecolors, (str, tuple)):
            linecolors = [linecolors]*n_curves
        elif isinstance(linecolors, list):
            if not isinstance(linecolors[0], (str, list, tuple)):
                linecolors = [linecolors]*n_curves
                
    if fillcolors is None:
        fillcolors = [None]*n_curves
    else:
        fillcolors = cmg.to_rgba_str(fillcolors)
        if isinstance(fillcolors, (str, tuple)):
            fillcolors = [fillcolors]*n_curves
        elif isinstance(fillcolors, list):
            if not isinstance(fillcolors[0], (str, list, tuple)):
                fillcolors = [fillcolors]*n_curves
    
    if markers is None:
        markers = [None]*n_curves
    else:
        if isinstance(markers, dict):
            markers = [markers]*n_curves
                    
    
    if legendgrouptitle_text is not None:
        legendgrouptitle_text = '<b>' + legendgrouptitle_text + '</b>'        
    
    
    # ---- Formating
    # =============== 
    for i in range(0, len(data)):
        data[i] = data[i].copy() # Pour ne pas réécrire sur les variables
    # data = data.copy() # Pour ne pas réécrire sur les variables
    n_curves = len(data)
    if len(labels) != n_curves:
        print('/!\ ' + str(n_curves) + ' séries de données mais ' + str(len(labels)) + ' étiquettes')
    
    # Conversion en pandas.dataframe avec 2 colonnes: 'val' et 'time':
    for i in range(0, n_curves):    
        # conversion des datasets en dataframe
        if isinstance(data[i], xr.Dataset):
            # Déterminer le field :
            _tmp_fields = list(data[i].data_vars)
            # Créer le Dataframe :
            _tmp_df = pd.DataFrame(data = data[i][_tmp_fields[0]].values, 
                                   columns = ['val'])
            # Rajouter la colonne time :
            _tmp_df['time'] = data[i]['time'].values

            # Mettre à jour :
            data[i] = _tmp_df
            
        # conversion des series en dataframe
        if isinstance(data[i], pd.Series):
            data[i] = data[i].to_frame(name = 'val')
            
        # Creation de la colonne 'time'
        if 'time' not in data[i].columns:
            if data[i].index.name == 'time':
                data[i]['time'] = data[i].index
            elif isinstance(data[i].index, pd.core.indexes.datetimes.DatetimeIndex):
                data[i]['time'] = data[i].index
                print(f"   Warning: Data {i+1}/{len(data)}: index is used as time axis")
            elif data[i].select_dtypes(include=['datetime', 'datetimetz']).shape[1] > 0:
                assumed_time_col = data[i].select_dtypes(include=['datetime', 'datetimetz']).columns[0]
                data.rename(columns = {assumed_time_col: 'time'}, inplace = True)
                print(f"   Warning: Data {i+1}/{len(data)}: column '{assumed_time_col}' is used as time axis")
                    
        # Creation de la colonne 'val'
        if 'val' not in data[i].columns:
            # not_time_col = set(data[i].columns).difference({'time'}, sort = False)
            val_col = data[i].columns.difference(data[i].select_dtypes(include=['datetime', 'datetimetz', object]).columns, sort=False)
            data[i].rename(columns = {val_col[0]: 'val'}, inplace = True)
            if val_col.size > 1:
                print(f"   Warning: Data {i}/{len(data)}: column '{val_col[0]}' is used as main values column, but there are {val_col.size - 1} other candidate columns: {', '.join(val_col[1:])}")
            
            
    # Valeurs cumulées :
    if cumul:
        for i in range(0, n_curves):
            _tmp_df = data[i].copy(deep = True)
            
            # Calcul des écarts temporels entre chaque valeur
            timespan = _tmp_df.loc[
                :, _tmp_df.columns == 'time'
                ].diff().shift(-1, fill_value = 0)/np.timedelta64(1, 'D')
            
            # Calcul de la cumulée
            # _tmp_df.iloc[:-1]['val'
            #             ] = (_tmp_df.iloc[:-1]['val'
            #                              ] * timespan.values).cumsum(axis = 0)
            _tmp_df[['val'
                ]] = (_tmp_df[['val'
                        ]] * timespan.values).cumsum(axis = 0)
            
            # # Correction de la dernière valeur
            # _tmp_df.iloc[-1]['val'] = np.nan
            
            # Alignement sur une date commune :
            cond = _tmp_df.time.dt.normalize() == date_ini_cumul
            # Si la date_ini_cumul existe dans le dataframe :
            if cond.sum() != 0:
                _tmp_df.loc[
                    :, 'val'] = _tmp_df.loc[
                        :, 'val'] - _tmp_df.loc[cond, 'val'].values
            else:
                _tmp_df.loc[
                    :, 'val'] = _tmp_df.loc[
                        :, 'val'] - _tmp_df.iloc[-1].loc['val']
            
            data[i] = _tmp_df
        
    
    # Valeurs normalisées par la moyenne :
    if mean_norm:
        for i in range(0, n_curves):
            _tmp_df = data[i].copy(deep = True)
            _tmp_df['val'] = _tmp_df['val'] / _tmp_df['val'].mean()
            data[i] = _tmp_df.copy(deep = True)
            
    # Valeurs centrées sur la moyenne :
    if mean_center:
        for i in range(0, n_curves):
            _tmp_df = data[i].copy()
            _tmp_df['val'] = _tmp_df['val'] - _tmp_df['val'].mean()
            data[i] = _tmp_df
            
    # Valeurs normalisées par rapport à une référence :
    if ref_norm is not None:
        # Conversion en pandas.dataframe : 
        if isinstance(ref_norm, xr.Dataset):
            # Déterminer le field :
            _tmp_fields = list(ref_norm.data_vars)
            # Créer le Dataframe :
            _tmp_df = pd.DataFrame(data = ref_norm[_tmp_fields[0]].values, 
                                   columns = ['val'])
            # Rajouter la colonne time :
            _tmp_df['time'] = ref_norm['time'].values
            # Mettre à jour :
            ref_norm = _tmp_df.copy(deep = True)
        
        for i in range(0, n_curves):
            _tmp_df = data[i].copy(deep = True)
            _tmp_df['val'] = _tmp_df['val'] / ref_norm['val']
            data[i] = _tmp_df
    
    # Affichage des indicateurs (NSE, NSElog, KGE ...) :
    if reference is not None:
        VOLerr = [0]*len(data)
        NSE = [0]*len(data)
        NSElog = [0]*len(data)
        reference.time.dt.tz_localize(None)
        
        # Calcul des métriques :
        for i in range(0, n_curves):
            data[i]['time'] = data[i]['time'].dt.tz_localize(None)
            temp = reference.merge(data[i], left_on = 'time', right_on = 'time')
            NSE[i] = 1 - (np.sum((temp.val_x - temp.val_y)**2) / np.sum((temp.val_x - temp.val_x.mean())**2))
            cond = (temp.val_x > 0) & (temp.val_y > 0)
            NSElog[i] = 1 - (np.sum((np.log(temp.val_x[cond]) - np.log(temp.val_y[cond]))**2) / np.sum((np.log(temp.val_x[cond]) - np.log(temp.val_x.mean()))**2))
            VOLerr[i] = np.sum(temp.val_y - temp.val_x) / np.sum(temp.val_x) # NB: not expressed in %
    
    # Courbes empilées ou non :
    if stack: # si l'option est activée
        stackgroup = np.random.rand()
    else:
        stackgroup = None
    
    # ---- Graphics
    # ==============
    #% Paramétrer graphes :
    fig1, ax1 = plt.subplots(1, figsize = (20, 12)) # Initialise la figure et les axes.
    # ax1.set_xlim(xlim)
    
    #% Couleurs :
    # ------------
# =============================================================================
#     if None in linecolors:    
#     # =============================================================================
#     #     # Echelle automatique :
#     #     _cmap = mpl.cm.get_cmap('Spectral', n_curves)
#     #     color_map = [list(_cmap(i)) for i in range(0, 12)]
#     #   # 'hsv'
#     #   # 'Spectral'
#     # =============================================================================
#         
#     # =============================================================================
#     #     # Echelle personnalisée :
#     #     color_map = custom(4,  [0.949, 0.000, 0.784, 1.000],
#     #                                 [1.000, 0.784, 0.059, 0.850], 
#     #                                 [0.110, 0.733, 1.000, 0.700],
#     #                                 )
#     # =============================================================================
#         
#         # Echelle manuelle : 
#         _cmap_catalog = [
#             [0.980, 0.691, 0.168, 0.8],  # 0. orange
#             [0.973, 0.392, 0.420, 0.9],  # 1. orange-rose
#             [0.847, 0.000, 0.035, 0.8],  # 2. rouge royal
#             [0.471, 0.000, 0.118, 0.8],  # 3. blackred
#             [1.000, 0.557, 0.827, 0.8],  # 4. rose bonbon
#             [0.949, 0.000, 0.784, 0.8],  # 5. fuschia
#             [0.655, 0.204, 0.886, 0.8],  # 6. pourpre
#             [0.404, 0.059, 0.902, 0.8],  # 7. violet fugace
#             [0.000, 0.000, 0.470, 0.8],  # 8. bleu marine - noir
#             [0.000, 0.318, 0.910, 0.8],  # 9. bleu
#             [0.000, 0.707, 0.973, 0.8],  # 10. bleu ciel
#             [0.000, 0.757, 0.757, 0.8],  # 11. bleu-vert émeraude
#             [0.625, 0.777, 0.027, 0.8],  # 12. vert
#             [0.824, 0.867, 0.141, 0.7],  # 13. vert-jaune (ou l'inverse)
#             [1.000, 0.784, 0.059, 0.8],  # 14. jaune-orangé
#             [0, 0, 0, 0.5],              # 15. noir
#             [0.37, 0.37, 0.37, 1],       # 16. gris sombrero
#             [0.70, 0.70, 0.70, 1],       # 17. gris clairero
#             ]
#         color_map = np.array(_cmap_catalog)[[6, 1, 14, 9, 11, 8, 3, 4, 12, 13, 0], :]
# =============================================================================
    
    #% Epaisseurs :
    # -------------
    if stack:
        lwidths = [0]*n_curves
    
    # Styles de lignes :
    # ------------------
    lstyle_convert = {'-':'solid', '--':'5, 2', 'dotted':'dot', None:None}
    lstyle_plotly = [lstyle_convert[style] for style in lstyles] 
    
    # Markers :
    # ---------
    if not isinstance(figweb, go.Figure):    
        figweb = go.Figure()
    for i in range(0, n_curves):         
        if mode != 'bar':
            # png :
# =============================================================================
#             data[i].plot(x = 'time', y = 'val', ax = ax1, 
#                                color = color_map[i], 
#                                label = labels[i], 
#                                lw = lwidths[i], ls = lstyles[i])
#             data[i]['label'] = labels[i]
# =============================================================================
            # html :
            if reference is not None: # Displays NSE, KGE... indications
                figweb.add_trace(go.Scatter(
                    x = data[i].time,
                    y = data[i].val,
                    name = labels[i] + # '<b>' + labels[i] + '</b>' +
                    '<br>(VOL<sub>err</sub>: ' + "{:.2f}".format(VOLerr[i]) + ' | NSE: ' + "{:.2f}".format(NSE[i]) + ' | NSE<sub>log</sub>: ' + "{:.2f})".format(NSElog[i]),
                    line = {'color': cmg.to_rgba_str(linecolors[i]),
                            'width': lwidths[i],
                            'dash': lstyle_plotly[i]},
                    legendgroup = legendgroup,
                    legendgrouptitle_text = legendgrouptitle_text,
                    stackgroup = stackgroup,
                    yaxis = yaxis,
                    fill = fill,
                    fillcolor = cmg.to_rgba_str(fillcolors[i]),
                    mode = mode,
                    marker = markers[i],
                    showlegend = showlegend,
                    ),
                    row = row,
                    col = col,
                    )
            else:
                figweb.add_trace(go.Scatter(
                    x = data[i].time,
                    y = data[i].val,
                    name = labels[i], # '<b>' + labels[i] + '</b>',
                    line = {'color': cmg.to_rgba_str(linecolors[i]),
                            'width': lwidths[i],
                            'dash': lstyle_plotly[i]},
                    legendgroup = legendgroup,
                    legendgrouptitle_text = legendgrouptitle_text,
                    stackgroup = stackgroup,
                    yaxis = yaxis,
                    fill = fill,
                    fillcolor = cmg.to_rgba_str(fillcolors[i]),
                    mode = mode,
                    marker = markers[i],
                    showlegend = showlegend,
                    visible = visible,
                    ),
                    row = row,
                    col = col,
                    )
            
        elif mode == 'bar':
            # Fill color if missing
            if markers[i] is None:
                markers[i] = dict()
                markers[i]['color'] = fillcolors[i]
                markers[i]['line'] = dict()
                markers[i]['line']['color'] = linecolors[i]
                markers[i]['line']['width'] = lwidths[i]
            else:            
                if 'color' in markers[i]:
                    if markers[i]['color'] is None:
                        markers[i]['color'] = fillcolors[i]
                else:
                    markers[i]['color'] = fillcolors[i]
                if 'line' in markers[i]:
                    if 'color' in markers[i]['line']:
                        if markers[i]['line']['color'] is None:
                            markers[i]['line']['color'] = fillcolors[i]
                    else:
                        markers[i]['line']['color'] = fillcolors[i]
                    if 'width' in markers[i]['line']:
                        if markers[i]['line']['width'] is None:
                            markers[i]['line']['width'] = lwidths[i]
                    else:
                        markers[i]['line']['width'] = lwidths[i]
                        
                else:
                    markers[i]['line'] = dict()
                    markers[i]['line']['color'] = fillcolors[i]
                    markers[i]['line']['width'] = lwidths[i]
            
            # html :
            if reference is not None: # Displays NSE, KGE... indications
                figweb.add_trace(go.Bar(
                    x = data[i].time,
                    y = data[i].val,
                    width = bar_widths,
                    marker = markers[i],
                    name = labels[i] + # '<b>' + labels[i] + '</b>' +
                    '<br>(VOL<sub>err</sub>: ' + "{:.2f}".format(VOLerr[i]) + ' | NSE: ' + "{:.2f}".format(NSE[i]) + ' | NSE<sub>log</sub>: ' + "{:.2f})".format(NSElog[i]),
                    legendgroup = legendgroup,
                    legendgrouptitle_text = legendgrouptitle_text,
                    yaxis = yaxis,
                    showlegend = showlegend,
                    visible = visible,
                    ),
                    row = row,
                    col = col,
                    )
            else:
                figweb.add_trace(go.Bar(
                    x = data[i].time,
                    y = data[i].val,
                    width = bar_widths,
                    marker = markers[i],
                    name = labels[i], # '<b>' + labels[i] + '</b>',
                    legendgroup = legendgroup,
                    legendgrouptitle_text = legendgrouptitle_text,
                    yaxis = yaxis,
                    showlegend = showlegend,
                    visible = visible,
                    ),
                    row = row,
                    col = col,
                    )
            
# =============================================================================
#             figweb.update_layout(bargap = 0)
# =============================================================================

    
    # Version express :
    # glob_df = pd.concat(data, sort = False)
    # figweb = px.line(glob_df, x = 'time', y = 'val', color = 'label', title = title)

    
    ax1.set_xlabel('Temps [j]', fontsize = 16)
    
    # ax1.set_xticklabels(ax1.get_xticks(), fontsize = 12)
    # ax1.set_yticklabels(ax1.get_yticks(), fontsize = 12)
    ax1.tick_params(axis = 'both', labelsize = 14)
    
    plt.legend(loc = "upper right", title = "Légende", frameon = False, 
               fontsize = 18)
    
    ax1.set_title(title, fontsize = 24)

    # Légendes sur les courbes (hover) :
    if reference is not None:
        figweb.update_traces(
            hoverinfo = 'all',
            # text = ['VOLerr: ' + "{:.3f}".format(VOLerr[i]) + '<br>NSE: ' + "{:.3f}".format(NSE[i]) + '<br>NSElog: ' + "{:.3f}".format(NSElog[i]) for i in range(0, len(data))],
            hovertemplate = "t: %{x}<br>" + "y: %{y}<br>",
            )

    
    return fig1, ax1, figweb

    # f.savefig(r"D:\2- Postdoc\2- Travaux\2- Suivi\2- CWatM\2022-01-27) Comparaison données météo\Chronique_Tmean_ERA5-vs-Weenat.png")
    # figweb.write_html(r"D:\2- Postdoc\2- Travaux\2- Suivi\2- CWatM\2022-01-27) Comparaison données météo\Chronique_Tmean_ERA5-vs-Weenat.html")



    # ---- Plot formats
    # ===================
    ## discharge_daily
    ax1.set_xlim(['2001-01-01', '2010-12-31'])
    fig1.set_size_inches(40, 12)
# =============================================================================
#     # Log
#     ax1.set_yscale('log')
#     ax1.set_ylim([1e-1, 5e2])
# =============================================================================
    # Linéaire
    ax1.set_yscale('linear')
    ax1.set_ylim([0, 100])
    fig1.suptitle('Débits journaliers - Bassin du Meu', fontsize = 24) # Titre
    ax1.set_title("Station de Monfort-sur-Meu - L'Abbaye", fontsize = 20) # Sous-titre
    ax1.set_ylabel('Débit [m3/s]', fontsize = 16)
    
    ## baseflow_daily
    ax1.set_ylim([0, 100])
    fig1.suptitle('Débit de base - Bassin du Meu', fontsize = 24) # Titre
    ax1.set_title("Station de Monfort-sur-Meu - L'Abbaye", fontsize = 20) # Sous-titre
    ax1.set_ylabel('Débit [m]', fontsize = 16)
    
    ## Recharge
    ax1.set_yscale('linear')
    ax1.set_ylim([0, 10])
    fig1.suptitle('Recharge journalière, en un point au centre du Bassin du Meu', fontsize = 24) # Titre
    ax1.set_title("La Guivelais - Saint-Onen-la-Chapelle", fontsize = 20) # Sous-titre
    ax1.set_ylabel('Recharge [mm/j]', fontsize = 16)
    
    
    # ---- Export
    # =============
    fig1.savefig(r"---.png")
    # fig1.savefig(r"D:\2- Postdoc\2- Travaux\2- Suivi\1- Cotech & Copil\2022-03-25) Cotech\TEST.png")


# =============================================================================
# def figure_cotech():
#     [fig1, ax1] = cwp.plot_time_series(data = [data], labels = ['Données mesurées'])
#     fig1.savefig(r"D:\2- Postdoc\2- Travaux\2- Suivi\1- Cotech & Copil\2022-03-25) Cotech\débits_lin_Data.png")
#     
#     [fig1, ax1] = cwp.plot_time_series(data = [data, model_old], labels = ['Données mesurées', 'Processus souterrains simples'])
#     fig1.savefig(r"D:\2- Postdoc\2- Travaux\2- Suivi\1- Cotech & Copil\2022-03-25) Cotech\débits_lin_Data-Prev.png")
#     
#     [fig1, ax1] = cwp.plot_time_series(data = [data, model_old, model_new], labels = ['Données mesurées', 'Processus souterrains simples', 'Processus souterrains Modflow'])
#     fig1.savefig(r"D:\2- Postdoc\2- Travaux\2- Suivi\1- Cotech & Copil\2022-03-25) Cotech\débits_lin_Data-Prev-Modflow.png")
#     
#     [fig1, ax1] = cwp.plot_time_series(data = [base, data], labels = ['Processus souterrains Modflow', 'Données mesurées'])
#     fig1.savefig(r"D:\2- Postdoc\2- Travaux\2- Suivi\1- Cotech & Copil\2022-03-25) Cotech\débits_log_Data-Modflow.png")
#     
#     [fig1, ax1] = cwp.plot_time_series(data = [precip, base, data], labels = ['Precipitations', 'Processus souterrains Modflow', 'Données mesurées'])
#     fig1.savefig(r"D:\2- Postdoc\2- Travaux\2- Suivi\1- Cotech & Copil\2022-03-25) Cotech\débits_log_Precip-Data-Modflow.png")

# =============================================================================

#%% Other tools 
# The previous functions have been moved to: cmapgenerator.py
# def custom(n_steps, *args):
# def custom_two_colors(n_steps, first_color, last_color):



