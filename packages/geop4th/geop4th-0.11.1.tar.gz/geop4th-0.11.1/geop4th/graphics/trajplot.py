# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 01:46:55 2024

@author: Alexandre Coche Kenshilik
@contact: alexandre.co@hotmail.fr

"""
#%% IMPORTS
from geop4th import (
    geobricks as geo,
)

from geop4th.graphics import (
    ncplot as ncp, 
    cmapgenerator as cmg, 
    monitor_memory as mm,
)
import numpy as np
import os
import datetime
import pandas as pd
import re
from matplotlib import cm

try:
    import tracemalloc
except:
    0

#%% CLASS
class Figure:
    """
    Main data available as Figure attributes
    ------------------------------------------
        
    +-----------------------------+--------------------------------------------------------------------+
    | Main variables              | Description                                                        |
    +=============================+====================================================================+ 
    | ``self.model_names_list``   | | List of **model names**.                                         |
    |                             | | For example in EXPLORE2 it corresponds to the identifier of the  | 
    |                             | | climatic experiment: 'Model1', 'Model2', 'Model3'..., 'Model17'. |
    +-----------------------------+--------------------------------------------------------------------+   
    | ``self.original_data``      | | List of the **pandas.Dataframes** retrieved from the NetCDF data,|
    |                             | | for each model (climatic experiments). NetCDF data are converted |
    |                             | | into time series by considering the spatial average over the     |
    |                             | | ``coords`` argument (mask).                                      |
    +-----------------------------+--------------------------------------------------------------------+  
    | ``self.relative_ref``       | | Equivalent to ``self.original_data``, but contains the time      |
    |                             | | series used as **reference** (historic) to compute relative      | 
    |                             | | values (if user-chosen).                                         |
    +-----------------------------+--------------------------------------------------------------------+  
    | ``self.rea_data``           | | Equivalent to ``self.original_data``, but contains the           |
    |                             | | **reanalysis** time series, which are added to the plots in      |
    |                             | | order to provide a historic reference.                           |
    +-----------------------------+--------------------------------------------------------------------+   
    | ``self.all_res``            | | List of pd.Dataframes **for each period** (according to          |
    |                             | | ``period_years`` argument), containing timeseries **averaged**   |
    |                             | | **over a year** (365 days) for each model (climatic experiments) |
    |                             | | (one column per model). The year starts on the month defined by  |
    |                             | | ``annuality`` argument.                                          |
    +-----------------------------+--------------------------------------------------------------------+  
    | ``self.graph_res``          | | Results **formated for the plots**.                              |
    |                             | | Either in the form of a list of pd.Dataframes, one for each      |
    |                             | | period, each pd.Dataframe containing the aggregated result       |  
    |                             | | (*min*, *mean*, *sum*...) from ``self.all_res`` [in case of      |
    |                             | | ``plot_type = 'temporality'``].                                  |
    |                             | | Or in the form of a single pd.Dataframe containing the           |
    |                             | | aggregated values for each day [in case of ``plot_type`` is      |
    |                             | | a metric].                                                       |                                                                                            
    +-----------------------------+--------------------------------------------------------------------+       
        
    ---------------------------------------------------------------------------

    """
                                  
    
    # Verbose prints memory tracking
    verbose:bool=False
    
# =============================================================================
#     # Access the number of Figure instances, also for memory tracking
#     n_fig:int=0
# =============================================================================
    
    # Static list of plot_type arguments considered as metrics
    metric_list = ['annual', 'date']
    
    metric_labels = {'annual': ['annual {}', '{} annuelle'], 
                     'date': ['date of {}', 'date de {}'], 
                     }
    
    agg_labels = {'mean': ['mean', 'moyenne'],
                  'sum': ['sum', 'somme'],
                  'max': ['maximum', 'maximum'],
                  'min': ['minimum', 'minimum'],
                  'range': ['range', 'amplitude'],
                  'increase': ['increase', 'augmentation'],
                  'decrease': ['decrease', 'diminution'],
                  }
    
    @classmethod
    def update_verbose(cls, verbose:bool):
        cls.verbose = verbose
        
# =============================================================================
#     @classmethod
#     def get_n_fig(cls):
#         return cls.n_fig 
# =============================================================================
    
    def __init__(self,
                 var:str, 
                 root_folder,
                 scenario:str='RCP 8.5', 
                 epsg_data=None, 
                 coords='all', 
                 epsg_coords=None, 
                 rolling_days:int=1, 
                 period_years:int=10,
                 annuality='calendar',
                 plot_type:str=None,
                 repres:(None | str)='area',
                 cumul:bool=False, 
                 relative:bool=False,
                 language:str='fr',
                 color='scale',
                 plotsize='wide',
                 name:str='',
                 credit:(None | str)='auto',
                 showlegend:bool=True,
                 shadow:(None | str)=None,
                 verbose:bool=False,
                 ):
        
        """
        Examples
        --------
        ::
        
            from watertrajectories_pytools.src.graphics import trajplot as tjp
            
            mask = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\16- Territoire Annecy\masque_zone_etude.shp"
            
            F = tjp.Figure(
                var = 'T',
                root_folder = r"E:\Inputs\Climat",
                scenario = 'rcp8.5',
                coords = mask,
                rolling_days = 30,
                period_years = 10,
                annuality = 3,
                name = 'Annecy',
                )
            
            for m in mask_dict:
                for scenario in ['SIM2', 'rcp8.5']:
                    figweb, _, _ = tjp.temporality(
                        var = 'PRETOT', scenario = scenario, root_folder = r"E:\Inputs\Climat",
                        coords = mask_dict[m], name = m,
                        period_years = 10, rolling_days = 30, cumul = False, 
                        plot_type = 'temporality', annuality = 3, relative = False, 
                        language = 'fr', plotsize = 'wide', verbose = True)
                    figweb, _, _ = tjp.temporality(
                        var = 'DRAIN', scenario = scenario, root_folder = r"E:\Inputs\Climat",
                        coords = mask_dict[m], name = m,
                        period_years = 10, rolling_days = 30, cumul = False, 
                        plot_type = 'temporality', annuality = 10, relative = False, 
                        language = 'fr', plotsize = 'wide', verbose = True)
                    figweb, _, _ = tjp.temporality(
                        var = 'SWI', scenario = scenario, root_folder = r"E:\Inputs\Climat",
                        coords = mask_dict[m], name = m,
                        period_years = 10, rolling_days = 30, cumul = False, 
                        plot_type = 'temporality', annuality = 3, relative = False, 
                        language = 'fr', plotsize = 'wide', verbose = True)
                    figweb, _, _ = tjp.temporality(
                        var = 'T', scenario = scenario, root_folder = r"E:\Inputs\Climat",
                        coords = mask_dict[m], name = m,
                        period_years = 10, rolling_days = 30, cumul = False, 
                        plot_type = 'temporality', annuality = 10, relative = False, 
                        language = 'fr', plotsize = 'wide', verbose = True)
        
        
        Parameters
        ----------
        var : str
            'PRETOT' | 'PRENEI' | 'ETP' | 'EVAPC' | 'RUNOFFC' | 'DRAINC' | 'T' | 'SWI' | ...
        scenario : str
            'SIM2' | 'historical' | 'RCP 4.5' | 'RCP 8.5'
        root_folder : str, path
            Path to the folder containing climatic data.
               r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo" (on my PC)
               r"E:\Inputs\Climat" (on the external harddrive)
        epsg_data : TYPE, optional
            DESCRIPTION. The default is None.
        coords : TYPE, optional
            DESCRIPTION. The default is 'all'.
        epsg_coords : TYPE, optional
            DESCRIPTION. The default is None.
        language : TYPE, optional
            DESCRIPTION. The default is 'fr'.
        plotsize : TYPE, optional
            DESCRIPTION. The default is 'wide'.
        rolling_days : TYPE, optional
            DESCRIPTION. The default is 1.
        period_years : TYPE, optional
            DESCRIPTION. The default is 10.
        cumul : TYPE, optional
            DESCRIPTION. The default is False.
        plot_type : TYPE
            DESCRIPTION.
        repres : {None, "area" or "bar"}, optional, default None
            Only used when plot_type is a metric.
            Defines the type of graphical representation of the metric plot.
                - ``"area"``: curves representing rolling averages
                - ``"bar"``: rectangles representing period averages
        name : int
            Suffix to add in the filename. Especially usefull to indicate the
            name of the site.
        credit : str, optional, default 'auto'
            To display the acknowledgement for data and conception.
            If ``'auto'``, the standard info about data source and conception author \
will be displayed. To remove all mention of credits, pass ``credit=''``.
        color : 'scale', 'discrete', <colormap> (str) or list of colors, optional, default 'scale'
            Colors for the plots (for now, only for *temporality* plots)
        relative : bool
            Whether the values should be computed as absolute or relatively to
            the reference period.
        showlegend : bool, optional, default True
            Whether to display the legend or not.
        shadow : {None, 'last', 'first', 'firstlast', 'lastfirst', 'all'}, optional, default = None
            Whether to display dialy values in grey shadows, and for which period. 
        annuality : int or str
            Type of year : 
                'calendar' | 'meteorological' | 'meteo' | 'hydrological' | 'hydro'
                1 | 9 | 10 
        verbose: bool
            Whether or not to display memory diagnotics.
        """
        
# =============================================================================
#         Figure.n_fig = Figure.n_fig+1
# =============================================================================
        
        # ---- Folders
        self.root_folder = root_folder
        
        # ---- Results
        self.model_names_list = None
        self.original_data = None
        self.relative_ref = None
        self.rea_data = None
        self.all_res = None
        self.all_daily = None
        self.graph_res = None
        self.graph_daily = None
        self.year_labels = None
        
        self.xaxis_add_label = ['', '']
        self.yaxis_add_label = ['', '']
        self.agg_rule = None
        self.is_metric = False
        
        # ---- Coords
        self.epsg_data = epsg_data
        self.coords = coords
        self.epsg_coords = epsg_coords
            
        # ---- Adjustments of names and folders
        self.scenario = scenario.casefold().replace('.', '').replace(' ', '')
        if self.scenario == 'sim2': 
            self.scenario = self.scenario.upper()
        
        if var.casefold().replace(' ', '').replace('-', '').replace('adjust', '') in [
                'evspsblpot', 'etp', 'pet']:
            self.var = 'ETP'
        elif var.casefold().replace(' ', '').replace('-', '').replace('adjust', '') in [
                'prsn', 'prenei', 'neige', 'snow']:
            self.var = 'PRENEI'
        elif var.casefold().replace(' ', '').replace('-', '').replace('adjust', '') in [
                'prtot', 'precip', 'pretot']:
            self.var = 'PRETOT'
        elif var.casefold().replace(' ', '').replace('-', '').replace('adjust', '') in [
                'tas', 't', 'temp']:
            self.var = 'T'
        elif var.casefold().replace(' ', '').replace('-', '').replace('adjust', '') in [
                'swi']:
            self.var = 'SWI'
        elif var.casefold().replace(' ', '').replace('-', '').replace('adjust', '') in [
                'swe', 'resr_neige', 'neige']:
            self.var = 'SWE'
        elif var.casefold().replace(' ', '').replace('-', '').replace('adjust', '') in [
                'drainc', 'drain', 'rec']:
            self.var = 'DRAINC'
        elif var.casefold().replace(' ', '').replace('-', '').replace('adjust', '') in [
                'runoff', 'runoffc', 'runc', 'run']:
            self.var = 'RUNOFFC'
        elif var.casefold().replace(' ', '').replace('-', '').replace('adjust', '') in [
                'etr', 'aet', 'evap', 'evapc']:
            self.var = 'EVAPC'
        
        # Projections
        self.info_by_var = { # var : [UNIT, UNIT_COEFF, DESCRIPTION, VARNAME IN FILENAME, DATA FOLDER, DATA SOURCE]
                     'PRENEI': ['mm', 1000, ['Snow', 'Neige'], 'prsn', 'DRIAS-Climat\EXPLORE2-Climat2022', 'drias-climat.fr'], 
                     # 'PRELIQ': ['mm', 1000, ['Liquid precipitations', 'Précipitations liquides', 'drias-climat.fr']], 
                     'PRETOT': ['mm', 1000, ['Total precipitations', 'Précipitations totales'], 'prtot', 'DRIAS-Climat\EXPLORE2-Climat2022', 'drias-climat.fr'],
                     'T': ['°C', -273.15, ['Temperature', 'Température'], 'tas', 'DRIAS-Climat\EXPLORE2-Climat2022', 'drias-climat.fr'], 
                     'EVAPC': ['mm', 1000, ['Actual evapotranspiration', 'Evapotranspiration réelle'], 'EVAPC', f'DRIAS-Eau\EXPLORE2-SIM2 2024\{self.var}', 'drias-eau.fr'], 
                     'ETP': ['mm', 1000, ['Potential evapotranspiration (Penman-Monteith)', 'Evapotranspiration potentielle (Penman-Monteith)'], 'evspsblpot', 'DRIAS-Climat\EXPLORE2-Climat2022', 'drias-climat.fr'], 
                     'SWI': ['-', 1, ['Soil Wetness Index', "Indice d'humidité des sols"], 'SWI', f'DRIAS-Eau\EXPLORE2-SIM2 2024\{self.var}', 'drias-eau.fr'],
                     'SWE': ['mm', 1, ['Snow Water Equivalent', "Equivalent en eau du manteau neigeux"], 'SWE', f'DRIAS-Eau\EXPLORE2-SIM2 2024\{self.var}', 'drias-eau.fr'],
                     'DRAINC': ['mm', 1000, ['Drainage (recharge)', 'Drainage (recharge)'], 'DRAINC', f'DRIAS-Eau\EXPLORE2-SIM2 2024\{self.var}', 'drias-eau.fr'], 
                     'RUNOFFC': ['mm', 1000, ['Surface runoff', 'Ruissellement'], 'RUNOFFC', f'DRIAS-Eau\EXPLORE2-SIM2 2024\{self.var}', 'drias-eau.fr'], 
                     }
        
        # Reanalyses historiques
        self.info_by_var_sim2 = { # var : [UNIT, UNIT_COEFF, DESCRIPTION, VARNAME IN FILENAME, DATA SOURCE]
                     'PRENEI': ['mm', 1, ['Snow', 'Neige'], 'PRENEI_Q', 'meteo.data.gouv.fr'], 
                     'PRELIQ': ['mm', 1, ['Liquid precipitations', 'Précipitations liquides'], 'PRELIQ_Q', 'meteo.data.gouv.fr'], 
                     'PRETOT': ['mm', 1, ['Total precipitations', 'Précipitations totales'], 'PRETOT_Q', 'meteo.data.gouv.fr'],
                     'T': ['°C', 0, ['Temperature', 'Température'], 'T_Q', 'meteo.data.gouv.fr'], 
                     'EVAPC': ['mm', 1, ['Actual evapotranspiration', 'Evapotranspiration réelle'], 'EVAP_Q', 'meteo.data.gouv.fr'], 
                     'ETP': ['mm', 1, ['Potential evapotranspiration (Penman-Monteith)', 'Evapotranspiration potentielle (Penman-Monteith)'], 'ETP_Q', 'meteo.data.gouv.fr'], 
                     'SWI': ['-', 1, ["Soil Wetness Index", "Indice d'humidité des sols"], 'SWI_Q', 'meteo.data.gouv.fr'],
                     'SWE': ['mm', 1, ["Snow Water Equivalent", "Equivalent en eau du manteau neigeux"], 'RESR_NEIGE_Q', 'meteo.data.gouv.fr'],
                     'DRAINC': ['mm', 1, ['Drainage (recharge)', 'Drainage (recharge)'], 'DRAINC_Q', 'meteo.data.gouv.fr'], 
                     'RUNOFFC': ['mm', 1, ['Surface runoff', 'Ruissellement'], 'RUNC_Q', 'meteo.data.gouv.fr'], 
                     }
        
        if self.scenario == 'SIM2': # réanalyses historiques
            self.data_folder = r"SIM2\compressed"
            self.n_model = 1
            self.varname = self.info_by_var_sim2[self.var][3]
            self.unit_coeff = self.info_by_var_sim2[self.var][1]
            
        else: # projections
            self.data_folder = os.path.join('DRIAS', self.info_by_var[self.var][4], 'lossy_compressed')
            self.n_model = 17
            self.varname = self.info_by_var[self.var][3]
            self.unit_coeff = self.info_by_var[self.var][1] # DRIAS data on my PC are stored in [m]. But we want to plot them in [mm]
        
        # ---- Relative
        self.relative = relative
        self.rel_title = ['', '']
        if self.relative:
            self.rel_suf = '_rel'
        else:
            self.rel_suf = ''
            
        # ---- Representation mode suffix (only for metrics)
        self.repres_suf = ''
            
        # ---- Initialize user inputs
        self.shadow = None
        self.plot_type = None # other arguments are either optional for all
                              # Figure methods, or they have a default value. 
        
        self.update(
            rolling_days=rolling_days, 
            period_years=period_years,
            annuality=annuality,
            plot_type=plot_type,
            repres=repres,
            cumul=cumul,
            plotsize=plotsize,
            color=color,
            language=language,
            name=name,
            credit=credit,
            showlegend=showlegend,
            shadow=shadow,
            )

        # ---- Verbose
        if verbose is not None:
            self.update_verbose(verbose)
        
        # ---- Loading
        self.load()
        
        
    def load(self):
        r"""
        Results
        -------
        This method also update the instance attributes all_res and graph_res,
        which respectively store the whole results and the final results used 
        for the plot.
        
        Warning
        -------
        This method can lead to memory size issues. It seems to appear when the 
        garbage collector is not doing its job fast enough in the xarray variable
        data from C:\ProgramData\Miniconda3\envs\cwatenv\Lib\site-packages\xarray\coding\variables.py.
        
        To solve this, you might just need to open this folder on Windows.
        
        Examples (pipeline)
        --------
        import os
        mask_folder = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\15- Territoire Pays Basque"
        mask_dict = dict()
        mask_dict['cotier'] = os.path.join(mask_folder, r"Sage-cotier-basque.shp")
        mask_dict['CAPB'] = os.path.join(mask_folder, r"zone_etude_fusion.shp")
        mask_dict['Nive-Nivelle'] = os.path.join(mask_folder, r"Nive-Nivelle.shp")
        for var in ['PRETOT', 'DRAIN', 'SWI', 'T']:
            for scenario in ['SIM2', 'rcp8.5']:
                for m in mask_dict:
                    F = tjp.Figure(
                        var = var,
                        root_folder = r"E:\Inputs\Climat",
                        scenario = scenario,
                        coords = mask_dict[m],
                        name = m,
                        rolling_days = 30,
                        period_years = 10,
                        )
                    F.plot(plot_type = 'annual_sum')
                    F.plot(plot_type = 'annual_sum', period_years = 30)
                    F.plot(plot_type = 'annual_sum', period_years = 1)
                    F.plot(plot_type = 'annual_scatter', agg_rule = 'sum')
                    F.plot(plot_type = '15/11', period_years = 10)
                    F.plot(plot_type = '15/05', period_years = 10)
                    if var == 'DRAIN':
                        F.plot(plot_type = '> 1.5')
    
        """
        
        # For memory tracking (initialization)
        if self.verbose:
            tracemalloc.start()
        
        # Folder
        folder = os.path.join(self.root_folder, self.data_folder) # monPC    
        
        print("\n_ Loading...")
    
        # ---- Load reference (if required)
        if self.scenario != 'SIM2':
            # SIM2 reference (historical reanalysis)
            rea_folder = os.path.join(self.root_folder, r"SIM2\compressed")
            print("   . SIM2 reference (historical reanalysis)")
            rea_pattern = re.compile(f"^{self.info_by_var_sim2[self.var][3]}.*_SIM2_.*")
            
            filelist_rea = [
                os.path.join(rea_folder, f) for f in os.listdir(rea_folder)
                if (os.path.isfile(os.path.join(rea_folder, f)) \
                    & (os.path.splitext(os.path.join(rea_folder, f))[-1] == '.nc') \
                        & (len(rea_pattern.findall(f)) > 0))]
            
            if len(filelist_rea) > 1:
                print(f"Err: too many detected files: {filelist_rea}")
                return
            else:
                filepath_rea = filelist_rea[0]
                
                self.rea_data = geo.time_series(
                    input_file = filepath_rea,
                    coords = self.coords, epsg_coords = self.epsg_coords, 
                    epsg_data = self.epsg_data,
                    )
                
                if self.verbose:
                    # memory monitoring
                    snapshot = tracemalloc.take_snapshot()
                    mm.display_top(snapshot)
        
        # ---- Load main dataset
        model_pattern = re.compile(f"^{self.varname}.*_{self.scenario}_.*")
        self.model_names_list = []
        self.original_data = []
        self.relative_ref = []
        
        for i_model in range(1, self.n_model + 1): # range(1, 18):
            model_name = f'Model{i_model}'
            print(f"   . {model_name}")
            if self.scenario == 'SIM2': # reanalyses historiques
                full_folder = folder
            else: # projections
                full_folder = os.path.join(folder, model_name)
            
            filelist = [
                os.path.join(full_folder, f) for f in os.listdir(full_folder)
                if (os.path.isfile(os.path.join(full_folder, f)) \
                    & (os.path.splitext(os.path.join(full_folder, f))[-1] == '.nc') \
                        & (len(model_pattern.findall(f)) > 0))]
            
            if len(filelist) > 1:
                print(f"Err: too many detected files: {filelist}")
                return
            elif len(filelist) == 0:
                print(f"Scenario {self.scenario} is absent for {model_name}")
            else:
                filepath = filelist[0]
                
                self.model_names_list.append(model_name)
                    
                df = geo.time_series(
                    input_file = filepath,
                    coords = self.coords, epsg_coords = self.epsg_coords, 
                    epsg_data = self.epsg_data,
                    )
                if self.var == 'T':
                    df = df + self.unit_coeff
                else:
                    df = df * self.unit_coeff

                self.original_data.append(df)


                if self.verbose:
                    # memory monitoring
                    snapshot = tracemalloc.take_snapshot()
                    mm.display_top(snapshot)
                
                # ---- Load relative values (if required)
                if self.relative:
                    relative_pattern = re.compile(f"^{self.varname}.*_historical_.*")
                    
                    filelist_rel = [
                        os.path.join(full_folder, f) for f in os.listdir(full_folder)
                        if (os.path.isfile(os.path.join(full_folder, f)) \
                            & (os.path.splitext(os.path.join(full_folder, f))[-1] == '.nc') \
                                & (len(relative_pattern.findall(f)) > 0))]
                    
                    if len(filelist_rel) > 1:
                        print(f"Err: too many detected reference files: {filelist_rel}")
                        return
                    elif len(filelist_rel) == 0:
                        print(f"The historical reference is absent for {model_name}")
                    else:
                        filepath_rel = filelist_rel[0]
                
                        ref_df = geo.time_series(
                            input_file = filepath_rel,
                            coords = self.coords, epsg_coords = self.epsg_coords, 
                            epsg_data = self.epsg_data,
                            )
                        if self.var == 'T':
                            ref_df = ref_df + self.unit_coeff
                        else:
                            ref_df = ref_df * self.unit_coeff
                        
                        self.relative_ref.append(ref_df)
                        
        
    def plot(self, 
             *,
             rolling_days=None, 
             period_years=None,
             annuality=None,
             plot_type=None,
             
             plotsize=None,
             name=None,
             credit=None,
             color=None,
             language=None,
             showlegend=None,
             shadow=None,
             repres=None,
             cumul=None,
             ):
        """
        Examples
        --------
        F = tjp.Figure(
            var = 'DRAINC',
            root_folder = r"E:\Inputs\Climat",
            scenario = 'rcp8.5',
            coords = r"C:\file.shp",
            rolling_days = 30,
            annuality = 10,
            name = 'myCatchment',
            )
        F.plot(plot_type = '> 1.5', period_years = 10)
        F.plot(plot_type = 'annual_sum')
        F.plot(plot_type = 'annual_sum', period_years = 30)
        F.plot(plot_type = 'annual_scatter', period_years = 1)
        F.plot(plot_type = '15/11', period_years = 10)
        

        Parameters
        ----------
        plot_type : str
            'temporality' | 'annual_sum'

        Returns
        -------
        None.

        """
        # ---- Initializations
        # Updates
        # -+-+-+-
        self.update(
            rolling_days=rolling_days, 
            period_years=period_years,
            annuality=annuality,
            cumul=cumul, 
            plot_type=plot_type,
            repres=repres,
            language=language,
            showlegend=showlegend,
            shadow=shadow,
            plotsize=plotsize,
            name=name,
            credit=credit,
            color=color)
        
        # Other initializations
        # -+-+-+-+-+-+-+-+-+-+-
        # Safeguard
        if self.plot_type is None: 
            print("Err: A plot_type argument is required.")
            return

        # Retrieve plot_mode (metric to plot) and agg_rule (aggregation rule, 
        # such as sum, mean, min...) from plot_type (user input)
        self.plot_mode, self.agg_rule, self.is_logical, self.is_date, \
        self.is_month, self.months = self.get_plot_mode(self.plot_type)

        # If plot_mode is in any of the previous case, it means it is a metric 
        # (and not a keyword like 'temporality' or 'scatter')
        if (self.plot_mode in self.metric_list) | self.is_logical | self.is_date | self.is_month:
            self.is_metric = True
        else:
            self.is_metric = False
        
        # The plot mode is to show scatter plot of annual values
        if self.plot_mode == 'scatter':
            if self.agg_rule is None:
                print("Err: A agg_rule argument is required when plot_type is 'annual_scatter'.")
                return
            print(f"aggregation rule = {self.agg_rule}")

        # Time-0 dataframe, used as a reference for dates
        # -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        self.df0 = self.original_data[0].copy()
        # Remove incomplete years
        # if (df.index[0].month > self.annuality) | (not df.index[0].is_month_start):
        if self.df0.index[0] > datetime.datetime(year=self.df0.index[0].year, month=self.annuality, day=1):
            self.df0 = self.df0[slice(f'{self.df0.index[0].year + 1}-{self.annuality}-01', self.df0.index[-1])]
        else:
            self.df0 = self.df0[slice(f'{self.df0.index[0].year}-{self.annuality}-01', self.df0.index[-1])]
        # if (df.index[-1].month < (
        #         datetime.datetime(year=1900, month=self.annuality, day=1) \
        #             - pd.DateOffset(months=1)
        #             ).month) | (df.index[-1].day < 31):
        # if (df.index[-1].month < self.annuality) | (not df.index[-1].is_month_end):
        if self.df0.index[-1] < datetime.datetime(year=self.df0.index[-1].year, month=self.annuality, day=1) - pd.DateOffset(days=1):
            self.df0 = self.df0[slice(self.df0.index[0], f'{self.df0.index[-1].year - 1}-{self.annuality}-01')][0:-1]
        else:
            self.df0 = self.df0[slice(self.df0.index[0], f'{self.df0.index[-1].year}-{self.annuality}-01')][0:-1]
        
        # Define keystones dates
        self.initialdate = self.df0.index[0]
        self.finaldate = self.df0.index[-1]
        if isinstance(self.period_years, int):
            self.startdate = self.initialdate
            self.enddate = self.startdate + pd.DateOffset(years = self.period_years, days = -1)
        elif isinstance(self.period_years, list):
            period_count = 0
            self.startdate = datetime.datetime(year = self.period_years[0][0],
                                               month = self.annuality,
                                               day = 1)
            self.enddate = datetime.datetime(year = self.period_years[0][1],
                                             month = self.annuality,
                                             day = 1) + pd.DateOffset(days = -1)
        
        # Initialize empty lists that will store results
        # -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        self.year_labels = [] # will store the strings "startyear-endyear"
        self.all_res = [] # will store the final results: range over all models for each period
        self.all_daily = []
        self.all_rea_daily = []
        self.graph_res = [] # previous results formated for the graph 
        self.graph_daily = []
        self.graph_rea = []
        self.graph_rea_daily = []
        self.mean_relative_ref = []
        
        self.plot_mode, self.agg_rule, self.is_logical, self.is_date, \
        self.is_month, self.months = self.get_plot_mode(self.plot_type)
        
        print("\n_ Time processing...")
        
        # ---- Data treatment: Relative results (if required)
        if self.relative:
            for i in range(0, len(self.original_data)):
                ref_df = self.relative_ref[i].copy()
                
                # Remove incomplete years
# =============================================================================
#                 if (ref_df.index[0].month > self.annuality) | (not ref_df.index[0].is_month_start):
#                     ref_df = ref_df[slice(f'{ref_df.index[0].year + 1}-{self.annuality}-01', ref_df.index[-1])]
#                 else:
#                     ref_df = ref_df[slice(f'{ref_df.index[0].year}-{self.annuality}-01', ref_df.index[-1])]
#                 if (ref_df.index[-1].month < self.annuality) | (not ref_df.index[-1].is_month_end):
#                     ref_df = ref_df[slice(ref_df.index[0], f'{ref_df.index[-1].year - 1}-{self.annuality}-01')][0:-1]
#                 else:
#                     ref_df = ref_df[slice(ref_df.index[0], f'{ref_df.index[-1].year}-{self.annuality}-01')][0:-1]
# =============================================================================
                
                # Extract the reference period
                ref_startdate = datetime.datetime(year=1971, month=self.annuality, day=1)
                ref_enddate = ref_startdate + (self.enddate - self.startdate) + pd.DateOffset(days = -1)
                ref_df = ref_df[slice(ref_startdate, ref_enddate)]
                
                # Remove 29th February (to avoid unrecognized dates when standardizing yearly timeseries)
                ref_df = ref_df.iloc[(ref_df.index.month != 2) | (ref_df.index.day != 29)]
                
                # Rolling window
                ref_df = ref_df.rolling(f"{self.rolling_days}D", center = True).mean()
                
                # Mean
                mean_ref_df = ref_df
                
                # Compute an average annual time series
                mean_ref_df = mean_ref_df.groupby([mean_ref_df.index.month, mean_ref_df.index.day]).agg(self.agg_rule)
                # mean_ref_df.index += pd.DateOffset(years = 1800 - mean_ref_df.index[0].year)
                # [pd.to_datetime(f"1800-{m}-{d}", format = "%Y-%m-%d") for (m, d) in mean_ref_df.index]
                mean_ref_df.index = [pd.to_datetime(f"1800-{m}-{d}", format = "%Y-%m-%d") 
                                 if m > ref_enddate.month else pd.to_datetime(f"1801-{m}-{d}", format = "%Y-%m-%d")
                                 for (m, d) in mean_ref_df.index
                                 ]
                # 1800 is used as an arbitrary year
                mean_ref_df.sort_index(inplace = True)
                
                mean_ref_df.attrs = {'period': (self.startdate, self.enddate),
                                     'model': self.model_names_list[i]}
                
                # Save & store
                self.mean_relative_ref.append(mean_ref_df)
                
                self.rel_title = [f" relative to {ref_startdate.strftime('%Y-%m')} ➞ {ref_enddate.strftime('%Y-%m')}",
                             f" relativement à {ref_startdate.strftime('%Y-%m')} ➞ {ref_enddate.strftime('%Y-%m')}"]
        
        # ---- Data treatment: reference data (if required)
        if self.scenario != 'SIM2':
            # SIM2 reference (historical reanalysis)

            # Remove incomplete years
            # if (self.rea_data.index[0].month > annuality) | (not self.rea_data.index[0].is_month_start):
            if self.rea_data.index[0] > datetime.datetime(year=self.rea_data.index[0].year, month=self.annuality, day=1):
                rea_df = self.rea_data[slice(f'{self.rea_data.index[0].year + 1}-{self.annuality}-01', self.rea_data.index[-1])]
            else:
                rea_df = self.rea_data[slice(f'{self.rea_data.index[0].year}-{self.annuality}-01', self.rea_data.index[-1])]
            # if (df.index[-1].month < (
            #         datetime.datetime(year=1900, month=self.annuality, day=1) \
            #             - pd.DateOffset(months=1)
            #             ).month) | (df.index[-1].day < 31):
            # if (self.rea_data.index[-1].month < self.annuality) | (not self.rea_data.index[-1].is_month_end):
            if self.rea_data.index[-1] < datetime.datetime(year=self.rea_data.index[-1].year, month=self.annuality, day=1) - pd.DateOffset(days=1):
                rea_df = self.rea_data[slice(self.rea_data.index[0], f'{self.rea_data.index[-1].year - 1}-{self.annuality}-01')][0:-1]
            else:
                rea_df = self.rea_data[slice(self.rea_data.index[0], f'{self.rea_data.index[-1].year}-{self.annuality}-01')][0:-1]
            
            # Remove 29th February (to avoid unrecognized dates when standardizing yearly timeseries)
            rea_df = rea_df.iloc[(rea_df.index.month != 2) | (rea_df.index.day != 29)]
            
            # Rolling window
            daily_rea_df = rea_df.copy(deep=True)
            rea_df = rea_df.rolling(f"{self.rolling_days}D", center = True).mean()
            
            rea_startdate = []
            rea_enddate = []
            rea_startdate.append(datetime.datetime(year=1971, month=self.annuality, day=1))
            rea_enddate.append(rea_startdate[0] + (self.enddate - self.startdate) + pd.DateOffset(days = -1))
            rea_enddate.append(rea_df.index[-1])
            rea_startdate.append(rea_enddate[-1] - (self.enddate - self.startdate) + pd.DateOffset(days = -1))
            self.rea_labels = []
            
            for k in range(0, len(rea_startdate)):
                rea_daily = [] # all daily results for one single period
                
                # Select the desired period
                mean_rea_df = rea_df[slice(rea_startdate[k], rea_enddate[k])].copy()
                daily_mean_rea_df = daily_rea_df[slice(rea_startdate[k], rea_enddate[k])].copy()
                
                # Compute an average annual time series
                mean_rea_df = mean_rea_df.groupby([mean_rea_df.index.month, mean_rea_df.index.day]).agg(self.agg_rule)
                min_rea_df = daily_mean_rea_df.groupby([daily_mean_rea_df.index.month, daily_mean_rea_df.index.day]).min()
                max_rea_df = daily_mean_rea_df.groupby([daily_mean_rea_df.index.month, daily_mean_rea_df.index.day]).max()
                
                mean_rea_df.index = [pd.to_datetime(f"1800-{m}-{d}", format = "%Y-%m-%d") 
                                 if m > rea_enddate[k].month else pd.to_datetime(f"1801-{m}-{d}", format = "%Y-%m-%d")
                                 for (m, d) in mean_rea_df.index
                                 ]
                min_rea_df.index = [pd.to_datetime(f"1800-{m}-{d}", format = "%Y-%m-%d") 
                                 if m > self.enddate.month else pd.to_datetime(f"1801-{m}-{d}", format = "%Y-%m-%d")
                                 for (m, d) in min_rea_df.index
                                 ]
                max_rea_df.index = [pd.to_datetime(f"1800-{m}-{d}", format = "%Y-%m-%d") 
                                 if m > self.enddate.month else pd.to_datetime(f"1801-{m}-{d}", format = "%Y-%m-%d")
                                 for (m, d) in max_rea_df.index
                                 ]

                # 1800 is used as an arbitrary year
                mean_rea_df.sort_index(inplace = True)
                min_rea_df.sort_index(inplace = True)
                max_rea_df.sort_index(inplace = True)
                
                mean_rea_df.attrs = {'period': (rea_startdate[k], rea_enddate[k])}
                min_rea_df.attrs = {'period': (rea_startdate[k], rea_enddate[k])}
                max_rea_df.attrs = {'period': (rea_startdate[k], rea_enddate[k])}
                
                # Save & store
                self.graph_rea.append(mean_rea_df)
                rea_daily.append(min_rea_df)
                rea_daily.append(max_rea_df)
                
                # self.rea_labels.append(f'{rea_startdate[k].strftime("%Y-%m")} ➞ {rea_enddate[k].strftime("%Y-%m")}')
                self.rea_labels.append(f"{rea_startdate[k].strftime('%m')}/<b>{rea_startdate[k].year}</b> ➞ {rea_enddate[k].strftime('%m')}/<b>{rea_enddate[k].year}</b>")
            
                # Convert rea_daily into list of df with 'min' and 'max' columns
                merge_rea_daily = pd.concat(rea_daily, axis = 1)
                merge_rea_daily = merge_rea_daily.set_axis(
                    [f"{rea_startdate[k].year}_{rea_enddate[k].year}_min", f"{rea_startdate[k].year}_{rea_enddate[k].year}_max"], 
                    axis = 1)
                
                self.all_rea_daily.append(merge_rea_daily)
                
                # Only for 'temporality' plot_type            
                min_rea_daily = merge_rea_daily.min(axis = 1)
                min_rea_daily = min_rea_daily.to_frame('min')
                max_rea_daily = merge_rea_daily.max(axis = 1)
                max_rea_daily = max_rea_daily.to_frame('max')
                min_rea_daily = min_rea_daily.merge(max_rea_daily, 
                                        left_index = True,
                                        right_index = True)
                self.graph_rea_daily.append(min_rea_daily)
        
        # ---- Data treatment
        print("\n_ Formatting...")
        while self.enddate <= self.finaldate:
            print(f"   . {self.startdate.strftime('%Y-%m')} : {self.enddate.strftime('%Y-%m')}")
            single_period_res = [] # all-model results for one single period
            single_period_daily = [] # all-model results for one single period
            for i in range(0, len(self.original_data)):
                df = self.original_data[i].copy()
                # Remove incomplete years
# =============================================================================
#                 # if (df.index[0].month > self.annuality) | (not df.index[0].is_month_start):
#                 if df.index[0] > datetime.datetime(year=df.index[0].year, month=self.annuality, day=1):
#                     df = df[slice(f'{df.index[0].year + 1}-{self.annuality}-01', df.index[-1])]
#                 else:
#                     df = df[slice(f'{df.index[0].year}-{self.annuality}-01', df.index[-1])]
#                 # if (df.index[-1].month < (
#                 #         datetime.datetime(year=1900, month=self.annuality, day=1) \
#                 #             - pd.DateOffset(months=1)
#                 #             ).month) | (df.index[-1].day < 31):
#                 # if (df.index[-1].month < self.annuality) | (not df.index[-1].is_month_end):
#                 if df.index[-1] < datetime.datetime(year=df.index[-1].year, month=self.annuality, day=1) - pd.DateOffset(days=1):
#                     df = df[slice(df.index[0], f'{df.index[-1].year - 1}-{self.annuality}-01')][0:-1]
#                 else:
#                     df = df[slice(df.index[0], f'{df.index[-1].year}-{self.annuality}-01')][0:-1]
# =============================================================================
                df = df[slice(self.initialdate, self.finaldate)]
                
                # Remove 29th February (to avoid unrecognized dates when standardizing yearly timeseries)
                df = df.iloc[(df.index.month != 2) | (df.index.day != 29)]
                
                # Rolling window
                df_daily = df.copy(deep=True)
                df = df.rolling(f"{self.rolling_days}D", center = True).mean()
                # df_daily = df.copy(deep=True)
                
                # Select the desired period
                df = df[slice(self.startdate, self.enddate)].copy()
                df_daily = df_daily[slice(self.startdate, self.enddate)].copy()
                
                # Compute an average annual time series
                mean_df = df.groupby([df.index.month, df.index.day]).agg(self.agg_rule)
                min_df = df_daily.groupby([df_daily.index.month, df_daily.index.day]).min()
                max_df = df_daily.groupby([df_daily.index.month, df_daily.index.day]).max()
                
                mean_df.index = [pd.to_datetime(f"1800-{m}-{d}", format = "%Y-%m-%d") 
                                 if m > self.enddate.month else pd.to_datetime(f"1801-{m}-{d}", format = "%Y-%m-%d")
                                 for (m, d) in mean_df.index
                                 ]
                min_df.index = [pd.to_datetime(f"1800-{m}-{d}", format = "%Y-%m-%d") 
                                 if m > self.enddate.month else pd.to_datetime(f"1801-{m}-{d}", format = "%Y-%m-%d")
                                 for (m, d) in min_df.index
                                 ]
                max_df.index = [pd.to_datetime(f"1800-{m}-{d}", format = "%Y-%m-%d") 
                                 if m > self.enddate.month else pd.to_datetime(f"1801-{m}-{d}", format = "%Y-%m-%d")
                                 for (m, d) in max_df.index
                                 ]
                # 1800 is used as an arbitrary year
                mean_df.sort_index(inplace = True)
                min_df.sort_index(inplace = True)
                max_df.sort_index(inplace = True)
                
                mean_df.attrs = {'period': (self.startdate, self.enddate),
                                 'model': self.model_names_list[i]}
                min_df.attrs = {'period': (self.startdate, self.enddate),
                                 'model': self.model_names_list[i]}
                max_df.attrs = {'period': (self.startdate, self.enddate),
                                 'model': self.model_names_list[i]}
                
                if self.relative:
                    mean_df = mean_df - self.mean_relative_ref[i]
                    min_df = min_df - self.mean_relative_ref[i]
                    max_df = max_df - self.mean_relative_ref[i]
                
                # Save & store
                single_period_res.append(mean_df)
                single_period_daily.append(min_df)
                single_period_daily.append(max_df)
            
            # Define the filled area
# ======= old version =========================================================
#             merge_res = single_period_res[0].copy()
#             return single_period_res
#             for r in range(1, len(single_period_res)):
#                 merge_res = merge_res.merge(single_period_res[r], 
#                                             left_index = True, 
#                                             right_index = True,
#                                             how = 'outer')
# =============================================================================
            merge_res = pd.concat(single_period_res, axis = 1)
            merge_res = merge_res.set_axis([f"{self.varname}_{model}" 
                                            for model in self.model_names_list], axis = 1)
            
            merge_daily = pd.concat(single_period_daily, axis = 1)
            list_min = [f"{self.varname}_{model}_min" for model in self.model_names_list]
            list_max = [f"{self.varname}_{model}_max" for model in self.model_names_list]
            list_daily = [None] * len(self.model_names_list) * 2
            list_daily[::2] = list_min
            list_daily[1::2] = list_max
            merge_daily = merge_daily.set_axis(list_daily, axis = 1)
            
            self.all_res.append(merge_res)
            self.all_daily.append(merge_daily)
            
            if self.plot_mode == 'temporality':
                min_res = merge_res.min(axis = 1)
                min_res = min_res.to_frame('min')
                max_res = merge_res.max(axis = 1)
                max_res = max_res.to_frame('max')
                min_res = min_res.merge(max_res, 
                                        left_index = True,
                                        right_index = True)
                # min_res = min_res.set_axis(['min', 'max'])
                self.graph_res.append(min_res)
                
                min_daily = merge_daily.min(axis = 1)
                min_daily = min_daily.to_frame('min')
                max_daily = merge_daily.max(axis = 1)
                max_daily = max_daily.to_frame('max')
                min_daily = min_daily.merge(max_daily, 
                                        left_index = True,
                                        right_index = True)
                self.graph_daily.append(min_daily)
                
                # self.year_labels.append(f"{self.startdate.strftime('%Y-%m')} ➞ {self.enddate.strftime('%Y-%m')}")
                self.year_labels.append(f"{self.startdate.strftime('%m')}/<b>{self.startdate.year}</b> ➞ {self.enddate.strftime('%m')}/<b>{self.enddate.year}</b>")
                
            elif self.plot_mode == 'scatter':
                if self.agg_rule == 'mean':
                    agg_res = merge_res.mean(axis = 0)
                elif self.agg_rule == 'sum':
                    agg_res = merge_res.sum(axis = 0)
                # agg_res = agg_res.to_frame(f'{startyear}-{endyear}').T
                # agg_res = agg_res.to_frame(f"{self.startdate.strftime('%Y-%m')} ➞ {self.enddate.strftime('%Y-%m')}").T
                agg_res = agg_res.to_frame(self.startdate.year).T
                agg_res.index.name = 'time'
                # sum_res.set_index(f'{startyear}-{endyear}')
                if len(self.graph_res) == 0:
                    self.graph_res = agg_res.copy()
                else:
                    self.graph_res = pd.concat([self.graph_res, agg_res], axis = 0)
                    
            elif self.is_metric:
                metric_res = self.metric(merge_res, self.startdate, self.plot_type)
                
                # Range
                min_res = metric_res.min(axis = 1)
                min_res = min_res.to_frame('min')
                max_res = metric_res.max(axis = 1)
                max_res = max_res.to_frame('max')
                min_res = min_res.merge(max_res, 
                                        left_index = True,
                                        right_index = True)
                self.graph_res.append(min_res)
            
            if self.enddate <= self.finaldate:
                if isinstance(self.period_years, list):
                    period_count += 1
                    if period_count < len(self.period_years):
                        self.startdate = datetime.datetime(
                            year = self.period_years[period_count][0],
                            month = self.annuality,
                            day = 1)
                        self.enddate = datetime.datetime(
                            year = self.period_years[period_count][1],
                            month = self.annuality,
                            day = 1) + pd.DateOffset(days = -1)
                    else:
                        # to quit the while loop
                        self.enddate = self.finaldate + pd.DateOffset(years = 1)
                
                elif isinstance(self.period_years, int):
                    if self.is_metric:
                        self.startdate += pd.DateOffset(years = 1)
                        self.enddate += pd.DateOffset(years = 1)
                    else:
                        self.startdate += pd.DateOffset(years = self.period_years)
                        self.enddate += pd.DateOffset(years = self.period_years)
                
        # Additional treatment for metrics
        if self.is_metric:  
            # Redefinition of graph_res
            self.graph_res = pd.concat(self.graph_res)
            
            # Additional treatment for relative representation
            if self.relative:
                self.graph_res['to_min'] = 0
                self.graph_res['to_max'] = 0
                self.graph_res.loc[(self.graph_res['min'] > 0), 'to_max'] = self.graph_res.loc[(self.graph_res['min'] > 0).index, 'min']
                self.graph_res.loc[(self.graph_res['min'] > 0), 'max'] = self.graph_res.loc[(self.graph_res['min'] > 0).index, 'max'] - self.graph_res.loc[(self.graph_res['min'] > 0).index, 'min']
                self.graph_res.loc[(self.graph_res['min'] > 0), 'min'] = 0
                self.graph_res.loc[(self.graph_res['max'] < 0), 'to_min'] = self.graph_res.loc[(self.graph_res['min'] > 0).index, 'max']
                self.graph_res.loc[(self.graph_res['max'] < 0), 'min'] = self.graph_res.loc[(self.graph_res['max'] > 0).index, 'min'] - self.graph_res.loc[(self.graph_res['max'] > 0).index, 'max']
                self.graph_res.loc[(self.graph_res['max'] < 0), 'max'] = 0
            
            # Xaxis title
# =============================================================================
#             years_before = self.period_years //2
#             years_after = self.period_years //2 + self.period_years %2
#             self.xaxis_add_label = [f"<br><i>({self.startdate.strftime('%m')}/<b>YYYY-{years_before}</b> ➞ {(self.startdate + pd.DateOffset(years = years_after, days = - 1)).strftime('%m')}/<b>YYYY+{years_after}</b></i>)", 
#                                     f"<br><i>({self.startdate.strftime('%m')}/<b>AAAA-{years_before}</b> ➞ {(self.startdate + pd.DateOffset(years = years_after, days = - 1)).strftime('%m')}/<b>AAAA+{years_after}</b></i>)"]
#             self.graph_res.index = self.graph_res.index + pd.DateOffset(years = years_before)
# =============================================================================
            self.xaxis_add_label = ['', '']
            
            if isinstance(self.period_years, list):
                self.period_lengths = [
                    datetime.datetime(
                        year = self.period_years[period_count][1], 
                        month = self.annuality, 
                        day = 1,
                        ) - datetime.datetime(
                            year = self.period_years[period_count][0], 
                            month = self.annuality, 
                            day = 1,
                            ) for period_count in range(0, len(self.period_years))]
                self.graph_res.index = pd.to_datetime(
                    [datetime.datetime(
                        year = self.period_years[period_count][0], 
                        month = self.annuality, 
                        day = 1,
                        ) + self.period_lengths[period_count]/2 for period_count in range(0, len(self.period_years))]
                    )
                            
            elif isinstance(self.period_years, int):
                self.graph_res.index = self.graph_res.index + pd.DateOffset(
                    years = self.period_years //2,
                    months = self.period_years %2 /2*12)
                
                # self.period_lengths defined later, if self.repres == "bar"
            
            if isinstance(self.period_years, int):
                self.layer_labels = [f"<b>Centered roll. mean ({self.period_years} y)</b>",
                                      f"<b>Moy. glissante centrée ({self.period_years} ans)</b>"]
            elif isinstance(self.period_years, list):
                self.layer_labels = [f"<b>Centered roll. mean ({len(self.period_years)} periods)</b>",
                                      f"<b>Moy. glissante centrée ({len(self.period_years)} périodes)</b>"]
            
            
        # ---- layout/export
        self.layout() # self.apply_layout()
    
        
    def layout(self,
               *, plotsize=None,
               name=None,
               credit=None,
               color=None,
               language=None,
               showlegend=None,
               shadow=None,
               repres=None,
               cumul=None):
        
        # ---- Update
        self.update(
            plotsize=plotsize,
            name=name,
            credit=credit,
            color=color,
            language=language,
            showlegend=showlegend,
            shadow=shadow,
            repres=repres,
            cumul=cumul,)
        
        
        # ---- Plotting
        print("\n_ Plotting...")
        # mode 1: temporality
        if self.plot_mode == 'temporality':
            # Axis titles
            self.xaxis_add_label = ['', '']
            self.yaxis_add_label = ['', '']
            
            # Colormap
    # =============================================================================
    #         color_map1 = cmg.discrete('trio', alpha = 1, black = False,
    #                          color_format = 'rgba_str', alternate = True)
    #         color_map2 = cmg.discrete('wong', alpha = 1, black = False,
    #                           color_format = 'rgba_str', alternate = False)
    #         color_map3 = cmg.discrete('ibm', alpha = 1, black = False,
    #                           color_format = 'rgba_str', alternate = False)
    #         
    #         color_map = np.vstack([
    #                                # np.array([0, 0, 0, 1]), 
    #                                color_map2,
    #                                color_map2,
    #                               ])
    # =============================================================================
            
            # Colors
            if self.color == 'scale':
                if not self.relative:
                    color_map = cm.viridis(np.linspace(0, 1, len(self.all_res)))
                else:
                    color_map = cm.plasma(np.linspace(0, 1, len(self.all_res)))
                    
            elif self.color == 'discrete':
                if len(self.graph_res) <= 6:
                    color_map = cmg.discrete(sequence_name = 'ibm', alpha = 1, black = False,
                                             alternate = False, color_format = 'float')
                    color_map = color_map[::-1]
                    if len(self.graph_res) == 2:
                        color_map = color_map[[2, 4]]
                    elif len(self.graph_res) == 3:
                        color_map = color_map[[0, 2, 4]]
                    elif len(self.graph_res) == 4:
                        color_map = color_map[[0, 2, 4]]
                        add_color = cmg.discrete(sequence_name = 'wong', alpha = 1, black = False,
                                                 alternate = False, color_format = 'float')
                        color_map = np.vstack([color_map, add_color]) 
                elif (len(self.graph_res) > 6) & (len(self.graph_res) <= 9):
                    color_map = cmg.discrete(sequence_name = 'wong', alpha = 1, black = False,
                                             alternate = False, color_format = 'float')
                    color_map = color_map[::-1] 
                else:
                    color_map = cmg.discrete(sequence_name = 'trio', alpha = 1, black = False,
                                             alternate = False, color_format = 'float')
                    
            elif isinstance(self.color, str):
                color_map = exec(f"cm.{self.color}(np.linspace(0, 1, len(self.all_res)))")
            
            else:
                color_map = self.color

            
            color_map_fill = color_map.copy()
            
            if not self.cumul:
                color_map_fill[:, -1] = 0.5
            else:
                color_map_fill[:, -1] = 0.2
            
            
            # Line properties
            lwidth = [1.5]*len(self.all_res)
            lstyle = ['-']*len(color_map)
            lstyle2 = lstyle.copy()
            if self.cumul:
                lstyle2 = ['dotted']*len(color_map)
            
            # Figure
            self.figweb = None  
            
            # Grey shades for climatic variability
            if self.shadow is not None:
                # First chrological curve
                if self.shadow in ['all', 'first', 'firstlast', 'lastfirst']:
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_rea_daily[0]['min'],
                                                               fill = self.cumul_filloption,
                                                               labels = 'min',
                                                               linecolors = [0.0, 0.0, 0.0, 1],
                                                               lwidths = 0.2,
                                                               lstyles = '-',
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               legendgroup = 2000,
                                                               showlegend = False,
                                                               )
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_rea_daily[0]['max'],
                                                               fill = 'tonexty',
                                                               labels = ['daily range for', 'gamme journalière pour '][self.lang] + self.rea_labels[0],
                                                               linecolors = [0.0, 0.0, 0.0, 1],
                                                               fillcolors = [0.0, 0.0, 0.0, 0.08/len(self.graph_rea_daily)],
                                                               lwidths = 0.2,
                                                               lstyles = '-',
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               legendgroup = 2000,
                                                               showlegend = True,
                                                               )
                
                # Next curves
                if self.shadow == 'all':
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_rea_daily[1]['min'],
                                                               fill = self.cumul_filloption,
                                                               labels = 'min',
                                                               linecolors = [0.0, 0.0, 0.0, 1],
                                                               lwidths = 0.2,
                                                               lstyles = 'dotted',
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               legendgroup = 3000,
                                                               showlegend = False,
                                                               )
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_rea_daily[1]['max'],
                                                               fill = 'tonexty',
                                                               labels = ['daily range for', 'gamme journalière pour '][self.lang] + self.rea_labels[1],
                                                               linecolors = [0.0, 0.0, 0.0, 1],
                                                               fillcolors = [0.0, 0.0, 0.0, 0.08/len(self.graph_rea_daily)],
                                                               lwidths = 0.2,
                                                               lstyles = 'dotted',
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               legendgroup = 3000,
                                                               showlegend = True,
                                                               )
                    
                    for i in range(0, len(self.graph_daily)-1):
                        [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                                   data = self.graph_daily[i]['min'],
                                                                   fill = self.cumul_filloption,
                                                                   labels = 'min',
                                                                   linecolors = color_map[i],
                                                                   lwidths = 0.2,
                                                                   lstyles = lstyle[i],
                                                                   cumul = self.cumul,
                                                                   date_ini_cumul = self.date_ini_cumul,
                                                                   legendgroup = 4000 + i,
                                                                   showlegend = False,
                                                                   )
                        [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                                   data = self.graph_daily[i]['max'],
                                                                   fill = 'tonexty',
                                                                   labels = ['daily range for', 'gamme journalière pour '][self.lang] +  self.year_labels[i],
                                                                   linecolors = color_map[i],
                                                                   fillcolors = [0.0, 0.0, 0.0, 0.08/len(self.graph_daily)],
                                                                   lwidths = 0.2,
                                                                   lstyles = lstyle2[i],
                                                                   cumul = self.cumul,
                                                                   date_ini_cumul = self.date_ini_cumul,
                                                                   legendgroup = 4000 + i,
                                                                   showlegend = True,
                                                                   )
                
                # Last chronological curve
                if self.shadow in ['all', 'last', 'firstlast', 'lastfirst']:
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_daily[-1]['min'],
                                                               fill = self.cumul_filloption,
                                                               labels = 'min',
                                                               linecolors = color_map[[-1]],
                                                               lwidths = 0.2,
                                                               lstyles = lstyle[-1],
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = False,
                                                               )
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_daily[-1]['max'],
                                                               fill = 'tonexty',
                                                               labels = ['daily range for', 'gamme journalière pour '][self.lang] + self.year_labels[-1],
                                                               linecolors = color_map[[-1]],
                                                               fillcolors = [0.0, 0.0, 0.0, 0.08/len(self.graph_daily)],
                                                               lwidths = 0.2,
                                                               lstyles = lstyle2[-1],
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = True,
                                                               )
            # =========== zorder property does not work ===================================
            #                     self.figweb.update_traces(zorder = 10, selector = {'line':{'width': 1.5}})
            #                     self.figweb.update_traces(zorder = 0, selector = {'line':{'width': 0.2}})
            # =============================================================================
            
            # SIM2 reference (historical reanalysis)
            if self.scenario != 'SIM2':
                [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                           data = self.graph_rea[::-1],
                                                           labels = self.rea_labels[::-1],
                                                           linecolors = np.array([[0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0]]),
                                                           lwidths = [1.5]*len(self.graph_rea),
                                                           lstyles = ['-', 'dotted'][::-1],
                                                           legendgroup = 1000,
                                                           # legendgrouptitle_text = ['Historical reanalysis', 'Reanalyse historique'][self.lang],
                                                           cumul = self.cumul,
                                                           date_ini_cumul = self.date_ini_cumul,)
            
            # Main curves
            for p in range(0, len(self.graph_res)):
                if self.graph_res[p]['min'].equals(self.graph_res[p]['max']):
                    # Lines will be visible and there will be no shade
                    color_map_line = color_map.copy()
                    fill_opt = None
                else:
                    # Lines will be set transparent, and shade will be visible
                    color_map_line = color_map.copy()
                    color_map_line[:, -1] = 0
                    fill_opt = 'tonexty'
                    
                [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                           data = self.graph_res[p]['min'],
                                                           fill = self.cumul_filloption,
                                                           labels = 'min',
                                                           linecolors = color_map_line[[p]],
                                                           lwidths = lwidth[p],
                                                           lstyles = lstyle[p],
                                                           legendgroup = p,
                                                           # legendgrouptitle_text = self.year_labels[p],
                                                           cumul = self.cumul,
                                                           date_ini_cumul = self.date_ini_cumul,
                                                           showlegend = False)
                [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                           data = self.graph_res[p]['max'],
                                                           fill = fill_opt,
                                                           labels = self.year_labels[p],
                                                           linecolors = color_map_line[[p]],
                                                           fillcolors = color_map_fill[[p]],
                                                           lwidths = lwidth[p],
                                                           lstyles = lstyle2[p],
                                                           legendgroup = p,
                                                           # legendgrouptitle_text = self.year_labels[p],
                                                           cumul = self.cumul,
                                                           date_ini_cumul = self.date_ini_cumul,
                                                           showlegend = True)
                    

                    
            # Axes
            self.xtickformat = '%b' # '%d/%m'
            
        # mode 2: annual_sum
        elif self.plot_mode == 'scatter':
            # Axis titles
            self.xaxis_add_label = [f"<br><i>({self.startdate.strftime('%m')}/<b>YYYY</b> ➞ {self.enddate.strftime('%m')}/<b>YYYY+{self.enddate.year - self.startdate.year}</b></i>)", 
                                    f"<br><i>({self.startdate.strftime('%m')}/<b>AAAA</b> ➞ {self.enddate.strftime('%m')}/<b>AAAA+{self.enddate.year - self.startdate.year}</b></i>)"]
            
            self.yaxis_add_label = ['', '']
            
            # Colormap
            color_map1 = cmg.discrete('trio', alpha = 1, black = False,
                             color_format = 'rgba_str', alternate = False)
            color_map2 = cmg.discrete('wong', alpha = 1, black = False,
                              color_format = 'rgba_str', alternate = False)
            color_map3 = cmg.discrete('ibm', alpha = 1, black = False,
                              color_format = 'rgba_str', alternate = False)
            
            color_map = np.vstack([
                                   # np.array([0, 0, 0, 1]), 
                                   color_map2,
                                   color_map2,
                                  ])
            
            # color_map = cm.viridis(np.linspace(0, 1, len(self.all_res)))
            
            # Line properties
            lwidth = [1.5]*self.graph_res.shape[1]
            lstyle = ['-']*len(color_map1) + ['dotted']*len(color_map1)
            
            # Figure
            self.figweb = None
            [self.fig1, self.ax1, self.figweb] = ncp.plot_time_series(
                                                       figweb = self.figweb,
                                                       data = [self.graph_res[[f"{self.varname}_{model}"]] 
                                                                     for model in self.model_names_list],
                                                       labels = self.model_names_list,
                                                       linecolors = color_map,
                                                       lwidths = lwidth,
                                                       lstyles = lstyle,
                                                       # legendgroup = p,
                                                       # legendgrouptitle_text = self.year_labels[p],
                                                       mode = 'markers',
                                                       markers = dict(
                                                           size = 12),
                                                       )
            
            # Axes
            self.xtickformat = '%Y'
        
        # mode 3: metrics
        elif self.is_metric:
            # Yaxis title
            if self.is_logical:
                self.yaxis_add_label = [f"<br><i>(number of days such as {self.var} {self.plot_mode})</i>",     # en
                                        f"<br><i>(nombre de jours tels que {self.var} {self.plot_mode})</i>"]   # fr
            elif self.is_date:
                self.yaxis_add_label = [f"<br><i>(value at the date of {self.plot_mode})</i>",      # en
                                        f"<br><i>(valeur à la date du {self.plot_mode})</i>"]       # fr
            
            elif self.is_month:
                month_name_start = datetime.datetime(year = 1800, month = self.months[0], day = 1).strftime('%B')
                month_name_end = datetime.datetime(year = 1800, month = self.months[-1], day = 1).strftime('%B')
# ============= Future developpment (lang) ====================================
#                 To improve the month name language, it is advised to install
#                 the babel package, then use: 
#                 babel.dates.format_date(datetime.datetime(year = 1800, month = self.months[0], day = 1), "MMMM", locale = language)
# =============================================================================
                
                if month_name_start == month_name_end:
                    month_name = month_name_start
                else:
                    month_name = month_name_start + ' → ' + month_name_end
                month_label = [month_name + ' {}',      # en
                               '{} sur ' + month_name]  # fr

                self.yaxis_add_label = ["<br><i>(" + month_label[0].format(self.agg_labels[self.agg_rule][0]) + ")</i>",    # en
                                        "<br><i>(" + month_label[1].format(self.agg_labels[self.agg_rule][1]) + ")</i>"]    # fr
            
            else:
                # self.yaxis_add_label = [f"<br><i>({m_label}</i>)" for m_label in self.metric_labels[self.plot_mode]]
                self.yaxis_add_label = ["<br><i>(" + self.metric_labels[self.plot_mode][0].format(self.agg_labels[self.agg_rule][0]) + ")</i>",    # en
                                        "<br><i>(" + self.metric_labels[self.plot_mode][1].format(self.agg_labels[self.agg_rule][1]) + ")</i>"]    # fr
            
            # Colormap
            color_map = cmg.discrete('wong', alpha = 1, black = False,
                              color_format = 'rgba_str', alternate = False)
            color_map2 = cmg.discrete('wong', alpha = 0.5, black = False,
                              color_format = 'rgba_str', alternate = False)
            color_map_rel = cmg.discrete('ibm', alpha = 1, black = False,
                                      color_format = 'rgba_str', alternate = False)
            
            # Line properties
            lwidth = 1.5
            lstyle = '-'
            
            # Figure
            self.figweb = None 
            
            if self.repres == "area":
                if not self.relative:
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_res['min'],
                                                               fill = self.cumul_filloption,
                                                               labels = 'min',
                                                               linecolors = color_map[7],
                                                               lwidths = lwidth,
                                                               lstyles = lstyle,
                                                               legendgroup = 1,
                                                               # legendgrouptitle_text = self.year_labels[p],
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = False)
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_res['max'],
                                                               fill = 'tonexty',
                                                               labels = self.layer_labels[self.lang],
                                                               linecolors = color_map[7],
                                                               # fillcolor = color_map2[3],
                                                               lwidths = lwidth,
                                                               lstyles = lstyle,
                                                               legendgroup = 1,
                                                               # legendgrouptitle_text = self.year_labels[p],
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = True)
                elif self.relative:
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_res['to_min'],
                                                               fill = 'tozeroy',
                                                               labels = None, #['to_min'],
                                                               fillcolors = 'rgba(255, 255, 255, 0)',
                                                               linecolors = 'rgba(255, 255, 255, 0)',
                                                               lwidths = lwidth,
                                                               lstyles = lstyle,
                                                               legendgroup = 1,
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = False,
                                                               visible = True)
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_res['min'],
                                                               fill = 'tonexty',
                                                               labels = self.layer_labels[self.lang] + ' (neg)', # ['min'],
                                                               # markers = {'color': color_map_rel[4]},
                                                               linecolors = color_map[3],
                                                               lwidths = lwidth,
                                                               lstyles = lstyle,
                                                               legendgroup = 1,
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = True,)
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_res['to_max'],
                                                               fill = 'tozeroy',
                                                               labels = None, # [self.layer_labels[self.lang]],
                                                               # markers = {'color': 'rgba(255, 255, 255)'},
                                                               linecolors = 'rgba(255, 255, 255, 0)', 
                                                               fillcolors = 'rgba(255, 255, 255, 0)',
                                                               lwidths = lwidth,
                                                               lstyles = lstyle,
                                                               legendgroup = 2,
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = False,
                                                               visible = True)
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               data = self.graph_res['max'],
                                                               fill = 'tonexty',
                                                               labels = self.layer_labels[self.lang] + ' (pos)',
                                                               # markers = {'color': color_map_rel[0]},
                                                               linecolors = color_map[-1],
                                                               # fillcolors = color_map2[[3]],
                                                               lwidths = lwidth,
                                                               lstyles = lstyle,
                                                               legendgroup = 2,
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = True)
                    
            
            elif self.repres == "bar":
                # Treatment for periods
                if isinstance(self.period_years, int):
                    date_list = []
                    block_centered_date = self.graph_res.index[0]
                    while block_centered_date <= self.finaldate:
                        date_list.append(block_centered_date)
                        block_centered_date += pd.DateOffset(years = self.period_years)
                    date_list = pd.to_datetime(date_list).intersection(self.graph_res.index)
                    graph_res = self.graph_res.loc[date_list, :]
                    self.period_lengths = [self.enddate - self.startdate]*graph_res.shape[0] # nrows
                else:
                    graph_res = self.graph_res.copy()
                
                period_lengths = [p.total_seconds()*1000 for p in self.period_lengths]

# ============ already defined ================================================
#                 elif isinstance(self.period_years, list):
#                     self.period_lengths
# =============================================================================
                
                if not self.relative:
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               mode = "bar",
                                                               data = graph_res['min'],
                                                               bar_widths = period_lengths,
                                                               fill = self.cumul_filloption,
                                                               labels = 'min',
                                                               fillcolors = "rgba(255, 255, 255, 0)",
                                                               linecolors = "rgba(255, 255, 255, 0)",
                                                               lwidths = lwidth,
                                                               # lstyle = lstyle,
                                                               legendgroup = 1,
                                                               # legendgrouptitle_text = self.year_labels[p],
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = False,
                                                               visible = True,)
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               mode = "bar",
                                                               bar_widths = period_lengths,
                                                               data = graph_res['max'] - graph_res['min'],
                                                               # fill = 'tonexty',
                                                               labels = [self.layer_labels[self.lang]],
                                                               linecolors = color_map[7],
                                                               fillcolors = color_map2[7],
                                                               lwidths = lwidth,
                                                               # lstyles = lstyle,
                                                               legendgroup = 1,
                                                               # legendgrouptitle_text = self.year_labels[p],
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = True)
                
                elif self.relative:
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               mode = 'bar',
                                                               data = graph_res['to_min'],
                                                               bar_widths = period_lengths,
                                                               labels = None, #['to_min'],
                                                               # markers = {'color': 'rgba(255, 255, 255)'},
                                                               linecolors = 'rgba(255, 255, 255, 0)',
                                                               fillcolors = 'rgba(255, 255, 255, 0)',
                                                               lwidths = lwidth,
                                                               lstyles = lstyle,
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = False,
                                                               visible = True)
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               mode = 'bar',
                                                               data = graph_res['min'],
                                                               bar_widths = period_lengths,
                                                               labels = self.layer_labels[self.lang] + ' (neg)', # ['min'],
                                                               # markers = {'color': color_map_rel[3]},
                                                               fillcolors = color_map2[3],
                                                               linecolors = color_map[3],
                                                               lwidths = lwidth,
                                                               lstyles = lstyle,
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = True)
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               mode = 'bar',
                                                               data = graph_res['to_max'],
                                                               bar_widths = period_lengths,
                                                               labels = None, # [self.layer_labels[self.lang]],
                                                               # markers = {'color': 'rgba(255, 255, 255)'},
                                                               # linecolors = color_map_rel[3], 
                                                               linecolors = 'rgba(255, 255, 255, 0)',
                                                               fillcolors = 'rgba(255, 255, 255, 0)',
                                                               lwidths = lwidth,
                                                               lstyles = lstyle,
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = False,
                                                               visible = True)
                    [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
                                                               mode = 'bar',
                                                               data = graph_res['max'],
                                                               bar_widths = period_lengths,
                                                               labels = self.layer_labels[self.lang] + ' (pos)',
                                                               # markers = {'color': color_map_rel[0]},
                                                               # linecolors = color_map_rel[0],
                                                               fillcolors = color_map2[-1],
                                                               linecolors = color_map[-1],
                                                               lwidths = lwidth,
                                                               lstyles = lstyle,
                                                               cumul = self.cumul,
                                                               date_ini_cumul = self.date_ini_cumul,
                                                               showlegend = True)
                
                # Adjust legend on bars
                self.figweb.update_traces(
                    hoverinfo = None,
                    hovertext = [f"{(graph_res.index[i] - pd.DateOffset(seconds = period_lengths[i]/2/1000)).strftime('%Y-%m')} → {(graph_res.index[i] + pd.DateOffset(seconds = period_lengths[i]/2/1000)).strftime('%Y-%m')}" for i in range(0, len(period_lengths))],
                    hovertemplate = "%{hovertext}<br><b>%{y}</b>",
                    )

                
# ============ Note in case of SIM2 ===========================================
#             [fig1, ax1, self.figweb] = ncp.plot_time_series(figweb = self.figweb,
#                                                        data = [self.graph_res['max']],
#                                                        # fill = 'tonexty',
#                                                        labels = [self.layer_labels[self.lang]],
#                                                        linecolors = color_map2[[3]],
#                                                        # fillcolors = color_map2[[3]],
#                                                        lwidths = [lwidth],
#                                                        lstyles = [lstyle],
#                                                        mode = 'markers',
#                                                        markers = {"size": 28},
#                                                        legendgroup = 1,
#                                                        # legendgrouptitle_text = self.year_labels[p],
#                                                        cumul = self.cumul,
#                                                        date_ini_cumul = self.date_ini_cumul,
#                                                        showlegend = True)
# =============================================================================
                
            # Axes
            self.xtickformat = '%Y'
        
        # ---- Scales
        # X
    # =============================================================================
    #     dates_lim = [results[0].time.iloc[0],
    #                  results[0].time.iloc[-1] + pd.Timedelta(days = 3653)]
    # =============================================================================
        # None 
        # ['2004-01-04', '2024-01-05']
           
        # Y
    # =============================================================================
    #     ylim = [results[0].val.mean(), results[0].val.mean()]
    # =============================================================================
        if self.plot_mode == 'date':
            self.ytickformat = '%d/%m'
        else:
            self.ytickformat = None
    
        if self.scenario == 'SIM2':
            ylabel = f'{self.info_by_var_sim2[self.var][2][self.lang]} [{self.info_by_var_sim2[self.var][0]}]' 
        else:
            ylabel = f'{self.info_by_var[self.var][2][self.lang]} [{self.info_by_var[self.var][0]}]'    
        
        # Adjust language of legends
        if self.plot_mode == 'temporality':
            if self.scenario != 'SIM2':
                self.figweb.update_traces(legendgrouptitle_text = ['Historical reanalysis', 'Reanalyse historique'][self.lang],
                                          selector = ({'legendgroup': 1000}))
        elif self.is_metric:
            self.figweb.update_traces(name = self.layer_labels[self.lang], 
                                      selector = ({'fill': 'tonexty'}))
    
    
        # ---- Title
        title = f"Scenario {self.scenario.upper()}" + self.rel_title[self.lang]
        
        # ---- Figure update
        self.figweb.update_layout(#font_family = 'Open Sans',
                           title = {'font': {'size': self.title_fontsize},
                                    'text': title,
                                    'xanchor': 'center',
                                    'x': 0.5,
                                    },
                           # annotations = {'xanchor': 'middle',
                           #                'yanchor': 'top',
                           #                'size': 20,
                           #                'text': add_title + "\nK = 5e-6 m/s   Poro = 0.1%   e = 25 m"},
                           xaxis = {'title': {'font': {'size': self.axes_fontsize},
                                              'text': ['Time [d]', 'Temps [j]'][self.lang] + self.xaxis_add_label[self.lang]},
                                    # 'range': dates_lim,
                                    'tickformat': self.xtickformat,
                                    
                                    },
                           yaxis = {'title': {'font': {'size': self.axes_fontsize},
                                               'text': ylabel + self.yaxis_add_label[self.lang]},
                                              # 'text': field_title + ' [m3/s]'},
                                    'type': 'linear',
                                    # 'range': ylim,#_ylim_figweb,
                                    'tickformat': self.ytickformat,
                                    },
                           legend = {'title': {'text': ['<b>Legend</b>', '<b>Légende</b>'][self.lang]},
                                     'xanchor': 'right',
                                     'y': 1,
                                     'yanchor': 'top',
                                     'bgcolor': 'rgba(255, 255, 255, 0.2)',
                                     'tracegroupgap': 0,
                                     # 'orientation': legend_orientation,
                                     },
                           font = {'size': self.txt_fontsize},
                           plot_bgcolor = "white",
                           showlegend = self.showlegend,
                           # legend = {'groupclick': 'togglegroup'},
                           width = self.plotdims[0], # paper[0], # wide[0],
                           height = self.plotdims[1], # paper[1], # wide[1],
                           )
        
        # ---- Horizontal 0 line (when self.relative = True)
        if self.relative:
            self.figweb.add_hline(y = 0,
                             line_color = 'rgba(255, 255, 255, 1)', line_width = 5,
                             )
        
        # ---- Relative bar chart
        if self.is_metric & (self.repres == "bar"): # & self.relative
            self.figweb.update_layout(barmode = 'relative') # center around 0
        
        
        # ---- Credits
        if self.credit == 'auto':
            if self.scenario == 'SIM2':
                data_src = self.info_by_var_sim2[self.var][4]
            else:
                data_src = self.info_by_var[self.var][5]
            credit_text = [f"data: {data_src} | design: Alexandre Coche",
                           f"données : {data_src} | conception : Alexandre Coche"][self.lang]
        elif isinstance(self.credit, str):
            credit_text = self.credit
        self.figweb.add_annotation(xanchor = 'right',
                                   xref = 'paper',
                                   x = 1,
                                   yref = 'paper',
                                   y = -0.2,
                                   yanchor = 'bottom',
                                   font = {'size': 8,
                                           'color': 'rgba(0, 0, 0, 0.5)'},
                                   text = f"<i>{credit_text}</i>",
                                   showarrow = False
                                   )
        
        
        # ---- Figure export
        output_name =  '_'.join([self.var + self.rel_suf, self.name, self.scenario.upper(), 
                                 self.plot_type.replace('>', 'sup').replace('<', 'inf').replace('==', 'eq').replace('/', '-') + self.repres_suf,
                                 self.period_str, 
                                 f'{self.rolling_days}d' \
                                     + [f'_ms{self.annuality}', ''][self.is_metric],
                                 self.language, self.plotsize + self.cumul_suf,
                                 # datetime.datetime.now().strftime("%Y-%m-%d_%Hh%M"),
                                 datetime.datetime.now().strftime("%Y-%m-%d"),
                                 ])
        
        self.figweb.write_html(os.path.join(self.root_folder,
                                       'tempo',
                                       output_name + '.html'
                                       )
                          )
        
        self.figweb.write_image(os.path.join(self.root_folder,
                                        'tempo',
                                       output_name + '.png'
                                       )
                          )
            


    def update(self, *, 
               var=None, 
               root_folder=None,
               scenario=None, 
               epsg_data=None, 
               coords=None, 
               epsg_coords=None, 
               relative=None,
               
               rolling_days=None, 
               period_years=None,
               annuality=None,
               plot_type=None,
               repres=None,
               cumul=None, 
               
               language=None,
               plotsize=None,
               color=None,
               name=None,
               credit=None,
               showlegend=None,
               shadow=None,
               
               verbose=None,
               ):
        # All default values are None so that the unspecified values are not
        # updated.
        
        # ---- Plot parameters
        # Annuality
        if annuality is not None:
            if annuality == 'calendar':
                self.annuality = 1
            elif annuality in ['meteo', 'meteorological']:
                self.annuality = 9
            elif annuality in ['hydro', 'hydrological']:
                self.annuality = 10
            else:
                self.annuality = annuality
        
        if rolling_days is not None:
            self.rolling_days = rolling_days
            
        if period_years is not None:
            self.period_years = period_years
            if isinstance(self.period_years, tuple):
                self.period_years = [self.period_years]
            
            if isinstance(self.period_years, int):
                self.period_str = f'{self.period_years}y'
            elif isinstance(self.period_years, list):
                self.period_str = f'{len(self.period_years)}periods'
        
        # Cumul
        if cumul is not None:
            self.cumul = cumul
            if self.cumul:
                self.date_ini_cumul = '1900-01-01'
                self.cumul_suf = '_cumul'
                self.cumul_filloption = 'tozeroy'
            else:
                self.cumul_suf = ''
                self.date_ini_cumul = None
                self.cumul_filloption = None
        
        # Plot type
        if plot_type is not None: self.plot_type = plot_type
        
        # Representation mode
        if repres is not None: 
            if (repres == 'area') & (isinstance(self.period_years, list)):
                print("\nWarning: The representation mode cannot be a curve ('area') when period_years is a list of periods and not an integer.")
                repres = "bar"
            self.repres = repres
            if self.is_metric:
                self.repres_suf = f"_{self.repres}"
            else:
                self.repres_suf = ''
        
        # ---- Layout parameters
        # Language
        if language is not None:
            language_dict = {"en": 0,
                             "fr": 1,}
            self.language = language
            self.lang = language_dict[self.language]
        
        # Graphical plot size
        # Two formats are defined here: wide and paper
        if plotsize == 'wide':
            self.plotsize = plotsize
            self.plotdims = (1500, 700) # (width, height)
            self.title_fontsize = 26
            self.axes_fontsize = 18
            self.txt_fontsize = 15.5
            
        elif plotsize == 'paper' :
            self.plotsize = plotsize
            self.plotdims = (1000, 550)
            self.title_fontsize =  20
            self.axes_fontsize =  16
            self.txt_fontsize = 12
        
        # Output name
        if name is not None: self.name = name
        
        # Acknowledgement
        if credit is None:
            if not hasattr(self, 'credit'):
                self.credit = ''
        else: 
            self.credit = credit
        
        # Color
        if color is not None: self.color = color
        
        # Show legend
        if showlegend is not None: self.showlegend = showlegend
        
        # Show daily shadows
        if shadow is not None: self.shadow = shadow
        
        # ---- Load parameters
        # For these attributes, we need more than an update, we need a reload
        if var is not None:
            self.var = var
        if root_folder is not None:
            self.root_folder = root_folder
        if scenario is not None:
            self.scenario = scenario
        if epsg_data is not None:
            self.epsg_data = epsg_data
        if coords is not None:
            self.coords = coords
        if epsg_coords is not None:
            self.epsg_coords = epsg_coords
        if relative is not None:
            self.relative = relative
            
        if not all(v is None for v in [var, root_folder, scenario,
                                       epsg_data, coords, epsg_coords, relative]):
            self = Figure(
                var=self.var, 
                root_folder=self.root_folder,
                scenario=self.scenario, 
                epsg_data=self.epsg_data, 
                coords=self.coords, 
                epsg_coords=self.epsg_coords,
                plot_type=self.plot_type,
                rolling_days=self.rolling_days, 
                period_years=self.period_years,
                annuality=self.annuality,
                cumul=self.cumul, 
                relative=self.relative,
                language=self.language,
                plotsize=self.plotsize,
                name=self.name,
                verbose=self.verbose,
                )
            
            
    @classmethod
    def get_plot_mode(cls, plot_type):
        # This method is used in plot() and in metric()
        
        # Initialize cases
        is_logical = False
        is_date = False
        is_month = False
        months = None
        
        plot_mode = plot_type.split('_')[0]
        if len(plot_type.split('_')) > 1:
            agg_rule = plot_type.split('_')[1]
        else:
            agg_rule = None
            
        if plot_mode == "temporality":
            if agg_rule is None:
                agg_rule = 'mean'
                print("Warnin: agg_rule (aggregation rule such as '_min', '_mean', '_sum'...) has been imposed to 'mean'.")
        
        logical_expr = re.compile(".*(<|>|=).*")
        # date_expr = re.compile('(\d{2,2})/(\d{2,2})')
        calendar_expr = "JFMAMJJASONDJFMAMJJASOND"
        month_expr = re.compile("m[0-9]{1,2}")
        
        # The plot mode is a characteristic date
        if plot_mode == 'date':
            if agg_rule is None:
                print("Err: agg_rule (aggregation rule such as '_min', '_mean', '_sum'...) should be passed in plot_type argument.")
                return
            else:
                agg_rule = 'idx' + agg_rule
        
        # The plot mode is a condition
        if len(logical_expr.findall(plot_mode)) > 0:
            is_logical = True
            agg_rule = None # Set to None, as the number of days is the only aggregation rule possible
            
        # The plot mpode is a date (single day)
        elif len(re.compile('.*(/).*').findall(plot_mode)) > 0:
        # elif len(date_expr.findall(plot_mode)) > 0:
            is_date = True
            agg_rule = None # Set to None, as the value is the only aggregation rule possible
            
        # The plot mode is one or several months
        elif plot_mode in calendar_expr:
            is_month = True
            months = re.compile(plot_mode).search(calendar_expr).span()
            if agg_rule is None:
                print("Err: agg_rule (aggregation rule such as '_min', '_mean', '_sum'...) should be passed in plot_type argument.")
                return
            # Adjust values
            months = [m+1 for m in range(months[0], months[1])]
            for i in range(0, len(months)):
                if months[i] > 12:
                    months[i] -= 12
        elif len(month_expr.findall(plot_mode)) > 0:
            m_int = int(plot_mode[1:])
            if (m_int > 0) & (m_int <= 12):
                is_month = True
                months = [m_int]
                if agg_rule is None:
                    print("Err: agg_rule (aggregation rule such as '_min', '_mean', '_sum'...) should be passed in plot_type argument.")
                    return            
    
        return plot_mode, agg_rule, is_logical, is_date, is_month, months
        
            
    @classmethod
    def metric(cls, merge_res, startdate, plot_type):
    # This function can be used without creating a Figure instance.
    # To use it: 
    #   F = Figure   # (without parentheses!)
    #   F.metric(...)
        
        # Decipher plot_type
        plot_mode, agg_rule, is_logical, is_date, is_month, months = cls.get_plot_mode(plot_type)
        
        if is_month:
            cond_chain = '|'.join([f"(merge_res.index.month == {m})" for m in months])
            res = merge_res.loc[eval(cond_chain)]
        else: # plot_mode = 'annual', date, logical...
            res = merge_res.copy()
        
        if plot_type == 'date':
            metric_res = res.agg(agg_rule, axis = 0).to_frame(startdate).T
            for c in metric_res.columns:
                if metric_res[c].dt.dayofyear.item() >= startdate.dayofyear:
                    metric_res[c] = metric_res[c].dt.dayofyear
                else:
                    metric_res[c] = metric_res[c].dt.dayofyear + 365
        
        elif is_date:
            date_expr = re.compile('(\d{2,2})/(\d{2,2})')
            
            day, month = date_expr.findall(plot_type)[0]
            
            metric_res = res[(res.index.month == int(month)) \
                                   & (res.index.day == int(day))]
            metric_res.index = [startdate]
        
        elif is_logical:
            logical_expr = re.compile(".*(<|>|<=|>=|==)(.*)")
            cond = logical_expr.findall(plot_type)[0]
            metric_res = (eval(f"res {cond[0]} {cond[1]}")).sum().to_frame(startdate).T
        
        else:
            if agg_rule == 'range':
                metric_res = (res.max(axis = 0) - res.min(axis = 0)).to_frame(startdate).T
            elif agg_rule == 'decrease':
                print("Warning: Not implemented yet")
            elif agg_rule == 'increase':
                print("Warning: Not implemented yet")
            else:
                metric_res = res.agg(agg_rule, axis = 0).to_frame(startdate).T
        
        return metric_res
            
        
    
    @staticmethod
    def timeseries(*,
            data_type, var, scenario, season, domain = 'Pays-Basque',
            epsg_data = None, coords = 'all', epsg_coords = None, 
            language = 'fr', plotsize = 'wide', rolling_window = 1,
            plot_type = '2series',
                   ):
        """
        Examples
        --------
        import climatic_plot as tjp
        
        tjp.timeseries(data_type = "Indicateurs DRIAS-Eau 2024 SWIAV", 
                        scenario = 'historical', season = 'JJA',
                        domain = 'Pays Basque', 
                        rolling_window = 10,
                        plot_type = '2series')    
        
        # ---- Original and rolled series for SWIAV
        for season in ['JJA', 'SON', 'DJF', 'MAM']:
            for scenario in ['historical', 'rcp45', 'rcp85']:
                for domain in ['Pays Basque', 'Annecy']:
                    tjp.timeseries(data_type = "Indicateurs DRIAS-Eau 2024", 
                                    var = 'SWIAV',
                                    scenario = scenario, season = season,
                                    domain = domain, 
                                    rolling_window = 10,
                                    plot_type = '2series')
                    
        # ---- Same for SSWI
        for season in ['JJA', 'SON', 'DJF', 'MAM']:
            for scenario in ['rcp45', 'rcp85']:
                for domain in ['Pays Basque', 'Annecy']:
                    tjp.timeseries(data_type = "Indicateurs DRIAS-Eau 2024", 
                                    var = 'SSWI',
                                    scenario = scenario, season = season,
                                    domain = domain, 
                                    rolling_window = 10,
                                    plot_type = '2series')
        
        # ---- All different colors with SIM2
        tjp.timeseries(data_type = "Indicateurs DRIAS-Eau 2024", 
                        var = 'SWIAV',
                        scenario = 'historical', season = 'JJA',
                        domain = 'Pays Basque', 
                        rolling_window = 10,
                        plot_type = 'all with sim2')
        
        # ---- Narratifs
        for season in ['JJA', 'SON', 'DJF', 'MAM']:
            for domain in ['Pays Basque', 'Annecy']:
                tjp.timeseries(data_type = "Indicateurs DRIAS-Eau 2024",
                                var = 'SWIAV',
                                scenario = 'rcp85', season = season,
                                domain = domain, 
                                rolling_window = 10,
                                plot_type = 'narratifs')
    
        Parameters
        ----------
        * : TYPE
            DESCRIPTION.
        root_folder : TYPE
            DESCRIPTION.
        scenario : str
            'historical' | 'rcp45' | 'rcp85'
        season : str
            'DJF' | 'MAM' | 'JJA' | 'SON' | 'NDJFMA' | 'MAMJJASO' | 'JJASO' | 'SONDJFM'
        data_type : TYPE
            DESCRIPTION.
        epsg_data : TYPE, optional
            DESCRIPTION. The default is None.
        coords : TYPE, optional
            DESCRIPTION. The default is 'all'.
        epsg_coords : TYPE, optional
            DESCRIPTION. The default is None.
        language : TYPE, optional
            DESCRIPTION. The default is 'fr'.
        plotsize : TYPE, optional
            DESCRIPTION. The default is 'wide'.
        rolling_window : TYPE, optional
            DESCRIPTION. The default is 10.
        plot_type : TYPE, optional
            DESCRIPTION. The default is '2series'.
         : TYPE
            DESCRIPTION.
    
        Returns
        -------
        None.
    
        """
        #%% GENERAL SETTINGS
        # ---- Language
        language_dict = {"en": 0,
                         "fr": 1,}
        lang = language_dict[language]
        
        # ---- Graphical plot size
        # Two formats are defined here: wide and paper
        if plotsize == 'wide':
            plotsize = (1500, 700) # (width, height)
        elif plotsize == 'paper' :
            plotsize = (1000, 550)
        
        #%% DRIAS-Eau Indicateurs
        if (data_type.casefold().replace(' ', '').replace('-', '') in [
                'indicateursexplore22024',
                'indicateursdriaseau2024']) & (plot_type != 'narratifs'):
        
            # ---- Folder
            root_folder = rf"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\DRIAS\DRIAS-Eau\EXPLORE2-SIM2 2024\{domain}\Indicateurs\Eau-{var}_Saisonnier_EXPLORE2-2024_{scenario}"
            
            # ---- Season      
            season_list = [d for d in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, d))]
            if season not in season_list:
                print(r"Erreur : Les données ne contiennent pas la saison {season}.")
            
            folder = os.path.join(root_folder, season)
            
            # ---- Units
            unit = '-'
            ylabel = [f'{var} [{unit}]', f'{var} [{unit}]']
            
            # ---- Loading
            filelist = [
                os.path.join(folder, f) for f in os.listdir(folder)
                if (os.path.isfile(os.path.join(folder, f)) \
                    & (os.path.splitext(os.path.join(folder, f))[-1] == '.nc'))]
                
            labels = []
            results = []
            
            for f in filelist:
                model_pattern = re.compile(f"{scenario}_(.*)_SIM2")
                filename = os.path.split(f)[-1]
                model = model_pattern.findall(filename)[0]
                labels.append(model)
                
                timeseries = geo.time_series(
                    input_file = f,
                    coords = coords, epsg_coords = epsg_coords, 
                    epsg_data = epsg_data,
                    )
                
                results.append(timeseries)
            
            # =============================================================================
            # # Rolling window
            # for res in results:
            #     # Rolling window
            #     res.set_index('time', inplace = True)
            #     res = res.rolling('365.25D', center = True).mean()
            # =============================================================================
            
            
            #%%% Graphics
            #%%%% All different colors
            if plot_type == 'all':
                suffix = 'all'
                # Colormap
                color_map1 = cmg.discrete('trio', alpha = 1, black = False,
                                 color_format = 'rgba_str', alternate = True)
                color_map2 = cmg.discrete('wong', alpha = 1, black = False,
                                 color_format = 'rgba_str', alternate = False)
                color_map3 = cmg.discrete('ibm', alpha = 1, black = False,
                                 color_format = 'rgba_str', alternate = False)
                
                color_map = np.vstack([
                                       # np.array([0, 0, 0, 1]), 
                                       color_map1,
                                       color_map1,
                                      ])
                # Line properties
                lwidth = [1.5]*len(results)
                lstyle = ['-']*len(color_map1) + ['dotted']*len(color_map1)
                
                # Rolling window
                for i in range(0, len(results)):
                    results[i] = results[i].rolling(time = rolling_window, center = True).mean()
                
                # Figure
                [fig1, ax1, figweb] = ncp.plot_time_series(data = results,
                                                           labels = labels,
                                                           color_map = color_map,
                                                           lwidth = lwidth,
                                                           lstyle = lstyle,
                                                           )
            
            #%%%% All different colors with SIM2
            elif plot_type.casefold().replace(' ', '').replace('-', '') == 'allwithsim2':
                suffix = 'withSIM2'
                # Colormap
                color_map1 = cmg.discrete('trio', alpha = 1, black = False,
                                 color_format = 'rgba_str', alternate = True)
                color_map2 = cmg.discrete('wong', alpha = 1, black = False,
                                 color_format = 'rgba_str', alternate = False)
                color_map3 = cmg.discrete('ibm', alpha = 1, black = False,
                                 color_format = 'rgba_str', alternate = False)
                
                color_map = np.vstack([
                                       # np.array([0, 0, 0, 1]), 
                                       color_map1,
                                       color_map1,
                                      ])
                # Line properties
                lwidth = [1.5]*len(results)
                lstyle = ['-']*len(color_map1) + ['dotted']*len(color_map1)
                
                # Rolling window
                for i in range(0, len(results)):
                    results[i] = results[i].rolling(time = rolling_window, center = True).mean()
                
                # Figure
                [fig1, ax1, figweb] = ncp.plot_time_series(data = results,
                                                           labels = labels,
                                                           color_map = color_map,
                                                           lwidth = lwidth,
                                                           lstyle = lstyle,
                                                           )
                
                # Add SIM2
                if domain == 'Pays Basque':
                    territoire_folder = r'15- Territoire Pays Basque'
                elif domain == 'Annecy':
                    territoire_folder = r'16- Territoire Annecy'
                    
                sim2_ts = geo.time_series(
                    input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\Surfex\SIM2\compressed\SWI_Q_SIM2_1958_202410_comp.nc",
                    coords = os.path.join(r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees",
                                          territoire_folder,
                                          r"masque_zone_etude.shp"))
                
                # Seasonalization
                first_year = sim2_ts.time[0].dt.year.item()
                last_year = sim2_ts.time[-1].dt.year.item()
                sim2_ts = sim2_ts.sel(
                    time = slice(f"{first_year}-12-01", f"{last_year-1}-11-30")
                )
    
                if season == 'DJF':
                    reduced_sim2 = sim2_ts.where((sim2_ts.time.dt.month <= 2) | (sim2_ts.time.dt.month >= 12), drop = True).copy()
                elif season== 'MAM':
                    reduced_sim2 = sim2_ts.where((sim2_ts.time.dt.month >= 3) & (sim2_ts.time.dt.month <= 5), drop = True).copy()
                elif season == 'JJA':
                    reduced_sim2 = sim2_ts.where((sim2_ts.time.dt.month >= 6) & (sim2_ts.time.dt.month <= 8), drop = True).copy()
                elif season == 'SON':
                    reduced_sim2 = sim2_ts.where((sim2_ts.time.dt.month >= 9) & (sim2_ts.time.dt.month <= 11), drop = True).copy()
                
                group = reduced_sim2.time.dt.year \
                + np.floor((reduced_sim2.time.dt.month)/12) - 1
                group = group.astype(int)
                reduced_sim2 = reduced_sim2.groupby(group).mean()
                reduced_sim2 = reduced_sim2.rename({'group': 'time'})
                
                # Rolling window for SIM2
                reduced_sim2 = reduced_sim2.rolling(time = rolling_window, center = True).mean()
                
                labels = ['SIM2']
                color_map = np.array([[0.0, 0.0, 0.0, 1.0]])
                [fig1, ax1, figweb] = ncp.plot_time_series(figweb = figweb,
                                                           data = [reduced_sim2],
                                                           labels = labels,
                                                           color_map = color_map,
                                                           lwidth = lwidth,
                                                           lstyle = lstyle,
                                                           )
            
            #%%%% Original and rolled series
            elif plot_type.replace(' ', '').replace('-', '') == '2series':
                suffix = '2series'
                # color_map1 = cmg.discrete('trio', alpha = 0.2, black = False,
                #                  color_format = 'rgba_str', alternate = False)
                color_map2 = cmg.discrete('wong', alpha = 0.3, black = False,
                                  color_format = 'rgba_str', alternate = False)
                color_map22 = cmg.discrete('wong', alpha = 0.5, black = False,
                                  color_format = 'rgba_str', alternate = False)
                # color_map3 = cmg.discrete('ibm', alpha = 0.2, black = False,
                #                   color_format = 'rgba_str', alternate = False)
                
                # Line properties
                lwidth = [1.5]*len(results)
                lstyle = ['-']*len(results)
                
                # Rolling window
                results_roll = results.copy()
                for i in range(0, len(results_roll)):
                    results_roll[i] = results_roll[i].rolling(time = rolling_window, center = True).mean()
                
                # Figure
                [fig1, ax1, figweb] = ncp.plot_time_series(data = results,
                                                           labels = labels,
                                                           color_map = np.repeat(color_map2[[8]],
                                                                                 len(results),
                                                                                 axis = 0),
                                                           lwidth = lwidth,
                                                           lstyle = lstyle,
                                                           legendgroup = 1,
                                                           legendgrouptitle_text = ['originals', 'originaux'][lang],
                                                           )
                
                [fig1, ax1, figweb] = ncp.plot_time_series(figweb = figweb,
                                                           data = results_roll,
                                                           labels = labels,
                                                           color_map = np.repeat(color_map22[[7]],
                                                                                 len(results_roll),
                                                                                 axis = 0),
                                                           lwidth = lwidth,
                                                           lstyle = lstyle,
                                                           legendgroup = 2,
                                                           legendgrouptitle_text = [
                                                               f'rolling mean: {rolling_window} years',
                                                               f'moy glissante : {rolling_window} ans'][lang],
                                                           )
                
                
            #%%%% Original and rolled series with SIM2
            elif plot_type.casefold().replace(' ', '').replace('-', '') == '2serieswithsim2':
                suffix = '2seriesSIM2'
                # color_map1 = cmg.discrete('trio', alpha = 0.2, black = False,
                #                  color_format = 'rgba_str', alternate = False)
                color_map2 = cmg.discrete('wong', alpha = 0.3, black = False,
                                  color_format = 'rgba_str', alternate = False)
                color_map22 = cmg.discrete('wong', alpha = 0.5, black = False,
                                  color_format = 'rgba_str', alternate = False)
                # color_map3 = cmg.discrete('ibm', alpha = 0.2, black = False,
                #                   color_format = 'rgba_str', alternate = False)
                
                # Line properties
                lwidth = [1.5]*len(results)
                lstyle = ['-']*len(results)
                
                # Rolling window
                results_roll = results.copy()
                for i in range(0, len(results_roll)):
                    results_roll[i] = results_roll[i].rolling(time = rolling_window, center = True).mean()
                
                # Figure
                [fig1, ax1, figweb] = ncp.plot_time_series(data = results,
                                                           labels = labels,
                                                           color_map = np.repeat(color_map2[[8]],
                                                                                 len(results),
                                                                                 axis = 0),
                                                           lwidth = lwidth,
                                                           lstyle = lstyle,
                                                           legendgroup = 1,
                                                           legendgrouptitle_text = ['originals', 'originaux'][lang],
                                                           )
                
                [fig1, ax1, figweb] = ncp.plot_time_series(figweb = figweb,
                                                           data = results_roll,
                                                           labels = labels,
                                                           color_map = np.repeat(color_map22[[7]],
                                                                                 len(results_roll),
                                                                                 axis = 0),
                                                           lwidth = lwidth,
                                                           lstyle = lstyle,
                                                           legendgroup = 2,
                                                           legendgrouptitle_text = [
                                                               f'rolling mean: {rolling_window} years',
                                                               f'moy glissante : {rolling_window} ans'][lang],
                                                           )
                
                # Add SIM2
                if domain == 'Pays Basque':
                    territoire_folder = r'15- Territoire Pays Basque'
                elif domain == 'Annecy':
                    territoire_folder = r'16- Territoire Annecy'
                    
                sim2_ts = geo.time_series(
                    input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\Surfex\SIM2\compressed\SWI_Q_SIM2_1958_202410_comp.nc",
                    coords = os.path.join(r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees",
                                          territoire_folder,
                                          r"masque_zone_etude.shp"))
                
                # Seasonalization
                first_year = sim2_ts.time[0].dt.year.item()
                last_year = sim2_ts.time[-1].dt.year.item()
                sim2_ts = sim2_ts.sel(
                    time = slice(f"{first_year}-12-01", f"{last_year-1}-11-30")
                )
    
                if season == 'DJF':
                    reduced_sim2 = sim2_ts.where((sim2_ts.time.dt.month <= 2) | (sim2_ts.time.dt.month >= 12), drop = True).copy()
                elif season== 'MAM':
                    reduced_sim2 = sim2_ts.where((sim2_ts.time.dt.month >= 3) & (sim2_ts.time.dt.month <= 5), drop = True).copy()
                elif season == 'JJA':
                    reduced_sim2 = sim2_ts.where((sim2_ts.time.dt.month >= 6) & (sim2_ts.time.dt.month <= 8), drop = True).copy()
                elif season == 'SON':
                    reduced_sim2 = sim2_ts.where((sim2_ts.time.dt.month >= 9) & (sim2_ts.time.dt.month <= 11), drop = True).copy()
                
                group = reduced_sim2.time.dt.year \
                + np.floor((reduced_sim2.time.dt.month)/12) - 1
                group = group.astype(int)
                reduced_sim2 = reduced_sim2.groupby(group).mean()
                reduced_sim2 = reduced_sim2.rename({'group': 'time'})
    
                labels = ['SIM2']
                color_map = np.array([[0.0, 0.0, 0.0, 0.3]])
                [fig1, ax1, figweb] = ncp.plot_time_series(figweb = figweb,
                                                           data = [reduced_sim2],
                                                           labels = labels,
                                                           color_map = color_map,
                                                           lwidth = lwidth,
                                                           lstyle = lstyle,
                                                           legendgroup = 1,
                                                           )
                # Rolling window for SIM2
                rolled_sim2 = reduced_sim2.rolling(time = rolling_window, center = True).mean()
                labels = ['SIM2']
                color_map = np.array([[0.0, 0.0, 0.0, 1]])
                [fig1, ax1, figweb] = ncp.plot_time_series(figweb = figweb,
                                                           data = [rolled_sim2],
                                                           labels = labels,
                                                           color_map = color_map,
                                                           lwidth = lwidth,
                                                           lstyle = lstyle,
                                                           legendgroup = 2,
                                                           )
            
        
        #%% DRIAS-Eau Indicateurs 4 narratifs
        elif (data_type.casefold().replace(' ', '').replace('-', '') in [
                'indicateursexplore22024',
                'indicateursdriaseau2024']) & (plot_type == 'narratifs'):
        
            # ---- Folder
            root_folder = rf"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\DRIAS\DRIAS-Eau\EXPLORE2-SIM2 2024\{domain}\Indicateurs\Eau-{var}_Saisonnier_EXPLORE2-2024_{scenario}"
            
            # ---- Season
            season_list = [d for d in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, d))]
            if season not in season_list:
                print(r"Erreur : Les données ne contiennent pas la saison {season}.")
            
            folder = os.path.join(root_folder, season)
            
            # ---- Units
            unit = '-'
            ylabel = [f'{var} [{unit}]', f'{var} [{unit}]']
            
            # ---- Loading
            filelist = [
                os.path.join(folder, f) for f in os.listdir(folder)
                if (os.path.isfile(os.path.join(folder, f)) \
                    & (os.path.splitext(os.path.join(folder, f))[-1] == '.nc'))]
                
            labels = []
            results = []
            
            
            for narratif in ['EC-EARTH_HadREM3-GA7-05', # narratif orange
                             'CNRM-CM5_ALADIN63',       # narratif jaune
                             'HadGEM2-ES_CCLM4-8-17',   # narratif violet
                             'HadGEM2-ES_ALADIN63',     # narratif vert
                             ]:
                
                for f in filelist:
                    model_pattern = re.compile(f"{scenario}_(.*)_SIM2")
                    filename = os.path.split(f)[-1]
                    model = model_pattern.findall(filename)[0]
                
                    if model == narratif:
                        labels.append(model)
                        timeseries = geo.time_series(
                            input_file = f,
                            coords = coords, epsg_coords = epsg_coords, 
                            epsg_data = epsg_data,
                            )
    
                        results.append(timeseries)
    
            labels = ['<b>narratif orange</b> : fort réchauffement<br>et fort assèchement (notamment en été)',
                      '<b>narratif jaune</b> : changements futurs<br>relativement peu marqués',
                      '<b>narratif violet</b> : fort réchauffement et forts<br> contrastes saisonniers en précipitations',
                      '<b>narratif vert</b> : réchauffement marqué<br>et augmentation des précipitations']
            
            #%%% Graphic
            suffix = 'narratifs'
            # Colormap
            color_map1 = cmg.discrete('wong', alpha = 0.15, black = False,
                             color_format = 'rgba_str', alternate = False)
            color_map11 = cmg.discrete('wong', alpha = 1, black = False,
                             color_format = 'rgba_str', alternate = False)
            color_map2 = cmg.discrete('trio', alpha = 1, black = False,
                              color_format = 'rgba_str', alternate = False)
            color_map3 = cmg.discrete('ibm', alpha = 1, black = False,
                              color_format = 'rgba_str', alternate = False)
            
            color_map1 = np.vstack([
                                   color_map1,
                                  ])[[4, 0, 1, 5]]
            color_map11 = np.vstack([
                                   color_map11,
                                  ])[[4, 0, 1, 5]]
            
            # Line properties
            lwidth = [1.5]*len(results)
            lstyle = ['-']*len(results)
            
            # Rolling window
            results_roll = results.copy()
            for i in range(0, len(results_roll)):
                results_roll[i] = results_roll[i].rolling(time = rolling_window, center = True).mean()
            
            
            # Figure
            [fig1, ax1, figweb] = ncp.plot_time_series(data = results,
                                                       labels = labels,
                                                       color_map = color_map1,
                                                       lwidth = lwidth,
                                                       lstyle = lstyle,
                                                       legendgroup = 1,
                                                       legendgrouptitle_text = ['originals', 'originaux'][lang],
                                                       )
            
            [fig1, ax1, figweb] = ncp.plot_time_series(figweb = figweb,
                                                       data = results_roll,
                                                       labels = labels,
                                                       color_map = color_map11,
                                                       lwidth = lwidth,
                                                       lstyle = lstyle,
                                                       legendgroup = 2,
                                                       legendgrouptitle_text = [
                                                           f'rolling mean: {rolling_window} years',
                                                           f'moy glissante : {rolling_window} ans'][lang],
                                                       )
            
            # Y
            ylim = [results[0].val.mean() - 0.3, results[0].val.mean() + 0.3]
        
        
        #%% Non conforme
        else: 
            print(f'Data_type non reconnu : {data_type}')
            return
        
        #%% MISE EN FORME ET EXPORT  
        # ---- Scales
        # X
        dates_lim = [results[0].time.iloc[0],
                     results[0].time.iloc[-1] + pd.Timedelta(days = 3653)]
        # None 
        # ['2004-01-04', '2024-01-05']
           
        # Y
        if var == 'SWIAV':
            buff = 0.3
        elif var == 'SSWI':
            buff = 3
        elif var == 'SWI04D':
            buff = 40
        else:
            buff = 1
        ylim = [results[0].val.mean() - buff, results[0].val.mean() + buff]
        
        # ---- Title
        title = f"{os.path.split(root_folder)[-1]} : <b>{season}</b>"
        
        # ---- Figure update
        figweb.update_layout(#font_family = 'Open Sans',
                           title = {'font': {'size': 20},
                                    'text': title,
                                    'xanchor': 'center',
                                    'x': 0.5,
                                    },
                           # annotations = {'xanchor': 'middle',
                           #                'yanchor': 'top',
                           #                'size': 20,
                           #                'text': add_title + "\nK = 5e-6 m/s   Poro = 0.1%   e = 25 m"},
                           xaxis = {'title': {'font': {'size': 16},
                                              'text': ['Time [d]', 'Temps [j]'][lang]},
                                    'range': dates_lim,
                                    
                                    },
                           yaxis = {'title': {'font': {'size': 16},
                                               'text': ylabel[lang]},
                                              # 'text': field_title + ' [m3/s]'},
                                    'type': 'linear',
                                    'range': ylim,#_ylim_figweb,
                                    },
                           legend = {'title': {'text': 'Légende'},
                                     'xanchor': 'right',
                                     'y': 1.1,
                                     'yanchor': 'top',
                                     'bgcolor': 'rgba(255, 255, 255, 0.2)',
                                     },
                           plot_bgcolor = "white",
                           # legend = {'groupclick': 'togglegroup'},
                           width = plotsize[0], # paper[0], # wide[0],
                           height = plotsize[1], # paper[1], # wide[1],
                           )
        
        # ---- Figure export
        figweb.write_html(os.path.join(root_folder,
                                       '_'.join([title, 
                                                 season, 
                                                 f'rolling{rolling_window}',
                                                 suffix,
                                                 datetime.datetime.now().strftime("%Y-%m-%d_%Hh%M"),
                                                 ]) + '.html'
                                       )
                          )
        
        figweb.write_image(os.path.join(root_folder,
                                       '_'.join([title, 
                                                 season, 
                                                 f'rolling{rolling_window}',
                                                 suffix,
                                                 datetime.datetime.now().strftime("%Y-%m-%d_%Hh%M"),
                                                 ]) + '.png'
                                       )
                          )



