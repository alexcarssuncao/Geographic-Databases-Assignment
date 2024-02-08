# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 11:41:20 2023

USES THE PROCESSED INMET DATAFRAME TO PRODUCE A SERIES OF MAPS

@author: Alexandre de Carvalho Assunção
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

DEBUGGING = True

#############################################################################
###  Opens the processed INMET data and the IBGE map of MG's Mesoregions  ###
#############################################################################

#
# a) Load the files' paths
#
DataFrame_path = 'C:/Users/alexc/OneDrive/Documentos/BDG_TP2/temp_data.csv'
ShapeFile_path = 'C:/Users/alexc/OneDrive/Documentos/BDG_TP2/MG_Mesorregioes_2022/MG_Mesorregioes_2022.shp'
Product_Shapefile_Path = 'C:/Users/alexc/OneDrive/Documentos/BDG_TP2/Resultados_Shapefiles/'
#
# b) Opens the files
#
total_df = pd.read_csv(DataFrame_path)
MG = gpd.read_file(ShapeFile_path)


Mean_Yearly_Temp = [] # Stores yearly mean temperature for the entire state
Std_Yearly_Temp = []  # Stores temperature stdDev for the entire state

'''
    Select the Year for Analysis:
'''

for YEAR in [2018,2019,2020,2021,2022]:

    df = total_df[total_df['Year'] == YEAR]
    
    
    ######################################################################
    ###         TURN THE STATIONS DATAFRAME INTO A GEO-DATABASE        ###
    ######################################################################
    #
    # a) Select each station's latitude and longitude and turn it into a point.
    #
    geometry = gpd.points_from_xy(df['Longitude'], df['Latitude'])
    stations = gpd.GeoDataFrame(df, geometry=geometry)
    #
    # b) Reproject the points using the CRS value in the shapefile's .prj file.
    #
    stations.crs = 'EPSG:4674'
    stations = stations.to_crs(MG.crs)
    
    #######################################################################
    ###      MERGE THE STATION POINTS WITH THE MAP OF MINAS GERAIS      ###
    #######################################################################
    
    map_with_stations = gpd.sjoin(stations, MG, how='left', op='within')
    
    avg_temp_by_region = map_with_stations.groupby('CD_MESO')['Mean_Temp'].mean().reset_index()
    
    map_with_avg_temp = MG.merge(avg_temp_by_region, on='CD_MESO', how='left')
    
    #
    # a) Gathers the mean temperature and std for the entire state of MG by year
    #
    Mean_Yearly_Temp.append(avg_temp_by_region['Mean_Temp'].mean())
    Std_Yearly_Temp.append(avg_temp_by_region['Mean_Temp'].std())
    
    #
    # b) Plots the results
    #
    ax = MG.plot(color='white', edgecolor='black',figsize=(20, 12))
    ax.set_axis_off()
    map_with_avg_temp.plot(column='Mean_Temp', cmap='YlOrRd', ax=ax)
    cbar = plt.colorbar(ax.get_children()[1], ax=ax, orientation='vertical', fraction=0.03, pad=0.1)
    cbar.ax.set_title('Temperature (\u00b0C)',fontsize = 20)
    
    '''
    #
    #  PRINT STATIONS MAP --> TEMPORARY MAPS.
    #
    ax = MG.plot(color='white', edgecolor='black', figsize=(20, 12))
    ax.set_axis_off()
    merged_map.plot(column='Mean_Temp', color='black',ax=ax)
    '''
    #
    # c) Displays the results
    #
    plt.title('Average Minimum Temperature by Mesoregion in '+str(YEAR),fontsize = 26)
    plt.show()
    
    #
    # d) Saves the resulting shapefiles
    #
    os.chdir(Product_Shapefile_Path)
    map_with_avg_temp.to_file('AvgMinTemp_MG_'+str(YEAR)+'.shp', driver='ESRI Shapefile')

if DEBUGGING == True:
    print(Mean_Yearly_Temp)
    print(Std_Yearly_Temp)
