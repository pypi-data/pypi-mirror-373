#%% Imports
import geoconvert as gc
import os
import time

#%% Process ERA5-Land files
def process_era5(root_folder = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany"):
    start_time = time.time()
    
    print("-----------------------------------")
    print("PREPROCESSING OF ERA5-LAND RAW DATA")
    print("-----------------------------------")
    #%% Initialization
    print("\n\n INITIALIZATION...")
    print(" ~~~~~~~~~~~~~~~~~")
    print(f'   Root folder: {root_folder}')
    
    date = ['1989-1999', '2000-2010', '2011-2021']
    print(f'   Dates: {date}')
    
    varname = ['Potential evaporation pos', # [m]/h
               'Relative humidity', # [%]
               'Surface pressure', # [Pa]
               'Surface solar radiation downwards W', # [W/m²]
               'Surface thermal radiation downwards W', # [W/m²]
               'Temperature', # [K]
               'Temperature',
               'Temperature',
               'Total precipitation', # [m]/h
               'Wind speed', # [m/s]
               ]
    
    mode = ['sum',
            'mean',
            'mean',
            'mean',
            'mean',
            'mean',
            'min',
            'max',
            'sum',
            'mean',
            ]


    #%% Update of variables
    print("\n\n UPDATING VARIABLES...")
    print(" ~~~~~~~~~~~~~~~~~~~~~")
    d=0
    for date_ in date:
        d+=1
    
    #-------------------------------------
    ### CREATE THE NECESSARY NEW VARIABLES
    #-------------------------------------
        #%%% Potential evaporations
        # gc.compute_Erefs_from_ERA5L(r"1989-1999 Potential evaporation.nc")
        print("\n    1- Switch potential evaporation from negative to positive")
        print("    __________________________________________________________")
        print(f"                                           date {d}/{len(date)}: {date_}")
        gc.compute_Erefs_from_ERA5L(
            os.path.join(root_folder, " ".join([date_, "Potential evaporation.nc"]))
            )
        #%%% Wind speed
        print("\n    2- Compute wind speed from Northing and Easting components")
        print("    ___________________________________________________________")
        print(f"                                            date {d}/{len(date)}: {date_}")
        gc.compute_wind_speed(
            os.path.join(root_folder, " ".join([date_, "U-component of wind.nc"]))
            )
    
        #%%% Relative humidity
        print("\n    3- Compute relative humidity from dewpoint, temperature and pressure")
        print("    _____________________________________________________________________")
        print(f"                                                      date {d}/{len(date)}: {date_}")
        gc.compute_relative_humidity(
            dewpoint_input_file = os.path.join(
                root_folder, " ".join([date_, "Dewpoint temperature.nc"])), 
            temperature_input_file = os.path.join(
                root_folder, " ".join([date_, "Temperature.nc"])),
            pressure_input_file = os.path.join(
                root_folder, " ".join([date_, "Surface pressure.nc"])),
            method = "Sonntag"
            )
    
    #----------------------------
    ### CONVERT UNITS WHEN NEEDED
    #----------------------------
        #%%% Radiations
        print("\n    4- Convert radiation units from J/m²/h to W/m²")
        print("    _______________________________________________")
        print(f"                              date {d}/{len(date)}: {date_}")
        gc.convert_downwards_radiation(os.path.join(
            root_folder, " ".join([date_, "Surface solar radiation downwards.nc"]))
            )
        gc.convert_downwards_radiation(os.path.join(
            root_folder, " ".join([date_, "Surface thermal radiation downwards.nc"]))
            )
    
    
    
        
    
    #%% Half-process checkup
    print("\n    > Half-process checkup <")
    print("    _________________________\n")
    print("\n".join(["\nAt this stage the folder should contain 8 (16) files per year:",
                     "    (Dewpoint temperature [K])",
                     "    (Potential evaporation crop)",
                     "  * Potential evaporation pos [m]",
                     "    (Potential evaporation water)",
                     "    (Potential evaporation)",
                     "  * Relative humidity [%]",
                     "  * Surface pressure [Pa]", 
                     "  * Surface solar radiation downwards W [W/m²]", 
                     "    (Surface solar radiation downwards [J/m²])",
                     "  * Surface thermal radiation downwards W [W/m²]",
                     "    (Surface thermal radiation downwards [J/m²])",
                     "  * Temperature [K]",
                     "  * Total precipitation [m]", 
                     "    (U-component of wind [m/s])",
                     "    (V-component of wind [m/s])",
                     "  * Wind speed [m/s]",
                     "",
                     "   (...) are original files not further needed"]))
        
    
    #%% Convert hourly into daily
    print("\n    5- Generate daily data from hourly data (in \data folder)")
    print("    __________________________________________________________")
    print("                                                     all dates\n")
    path_list = [os.path.join(
        root_folder, date_ + " " + varname[i] + ".nc") for date_ in date for i in range(0, len(varname))]
    
    mode_list = mode*len(date)
    
    # for date_ in date:
    #     for i in range(0, len(varname)):
    #         gc.hourly_to_daily(input_file = os.path.join(
    #             root_folder, date_ + " " + varname[i] + ".nc"), mode = mode[i])
    gc.hourly_to_daily(input_file = path_list, mode = mode_list)
    
    
    #%% Prepare final data files for CWatM
    print("\n    6- Generate ready-to-use data files for CWatM input (in \cwatm folder)")
    print("    _______________________________________________________________________")
    print("                                                                  all dates\n")
    for i in range(0, len(varname)):
        gc.prepare_CWatM_input(input_file = os.path.join(
            root_folder, "daily_temp", " ".join([date[0], varname[i], f"daily_{mode[i]}.nc"])),
            file_type = 'ERA5', reso_m = 6000, EPSG_out = 3035)
# =============================================================================
#     gc.prepare_CWatM_input(input_file = os.path.join(
#         root_folder, " ".join([date[0], "Potential evaporation water daily_mean.nc.nc"])),
#         file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     gc.prepare_CWatM_input(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\daily\1989-1999 Potential evaporation water daily_mean.nc", file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     gc.prepare_CWatM_input(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\daily\1989-1999 Relative humidity daily_mean.nc", file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     gc.prepare_CWatM_input(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\daily\1989-1999 Surface pressure daily_mean.nc", file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     gc.prepare_CWatM_input(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\daily\1989-1999 Surface solar radiation downwards W daily_mean.nc", file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     gc.prepare_CWatM_input(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\daily\1989-1999 Surface thermal radiation downwards W daily_mean.nc", file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     gc.prepare_CWatM_input(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\daily\1989-1999 Temperature daily_max.nc", file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     gc.prepare_CWatM_input(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\daily\1989-1999 Temperature daily_min.nc", file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     gc.prepare_CWatM_input(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\daily\1989-1999 Temperature daily_mean.nc", file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     gc.prepare_CWatM_input(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\daily\1989-1999 Total precipitation daily_mean.nc", file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     gc.prepare_CWatM_input(input_file = r"D:\2- Postdoc\2- Travaux\1- Veille\4- Donnees\8- Meteo\ERA5\Brittany\daily\1989-1999 Wind speed daily_mean.nc", file_type = 'ERA5', reso_m = 6000, CRS = 3035)
#     
# =============================================================================
    
    print("\n\n ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f" Elapsed time: {time.time() - start_time} s")    


#%% Correct ERA5-Land data
def correct_era5(input_folder = r"D:\2- Postdoc\2- Travaux\3_CWatM_EBR\data\input_1km_LeMeu\meteo\ERA5Land"):
    start_time = time.time()
    
    print("--------------------------------")
    print("CORRECTION OF ERA5-LAND RAW DATA")
    print("--------------------------------")
    #%% Initialization
    print("\n\n INITIALIZATION...")
    print(" ~~~~~~~~~~~~~~~~~")
    print(f'   Input folder: {input_folder}')
    
    date = ['1989-1999', '2000-2010', '2011-2021']
    print(f'   Dates: {date}')
    
    #%% Correct value
    print("\n\n CORRECTING VALUES...")
    print(" ~~~~~~~~~~~~~~~~~~~~")
    #%%% Precipitations
    print("\n    1- Multiplying precipitations by 0.087")
    print("    _______________________________________\n")
    gc.correct_era5(input_file = os.path.join(
        input_folder, r"1989-2021 Total precipitation res=6000m epsg3035.nc"),
        correct_factor = 0.087,
        to_dailysum = False)
    
    #%%% Downwards radiations
    print("\n    2- Multiplying solar radiations (W) by 0.0715")
    print("    ______________________________________________\n")
    gc.correct_era5(input_file = os.path.join(
        input_folder, r"1989-2021 SSRD Watt res=6000m epsg3035.nc"),
        correct_factor = 0.0715,
        to_dailysum = False,
        progressive = True)
    
    print("\n    3- Multiplying thermal radiations (W) by 0.0715")
    print("    ________________________________________________\n")
    gc.correct_era5(input_file = os.path.join(
        input_folder, r"1989-2021 STRD Watt res=6000m epsg3035.nc"),
        correct_factor = 0.0715,
        to_dailysum = False,
        progressive = True)
    
    #%%% Potential evapotranspiration
    print("\n    4- Multiplying potential evaporation by 0.04")
    print("    _____________________________________________\n")
    gc.correct_era5(input_file = os.path.join(
        input_folder, r"1989-2021 Potential evaporation pos res=6000m epsg3035.nc"),
        correct_factor = 0.04,
        to_dailysum = False)
    
    print("\n\n ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f" Elapsed time: {time.time() - start_time} s")   
    