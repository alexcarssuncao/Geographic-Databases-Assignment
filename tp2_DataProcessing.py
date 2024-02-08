# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 08:42:50 2023

PROCESS THE INMET TABLES AND PRINTS A USABLE DATAFRAME

@author: Alexandre de Carvalho Assunção
"""

import os
import pandas as pd
from pathlib import Path


DEBUGGING = False
DATA = []

for YEAR in ['2018','2019','2020','2021','2022']:

    YEAR_FOLDER = Path(__file__).with_name(YEAR)
    
    files = os.listdir(YEAR_FOLDER)
    
    os.chdir(YEAR_FOLDER)
    
    ########################################################
    ##               PROCESSING THE TABLES                ##
    ########################################################
    
    for table in files:
        
        #
        # a) Read the header of the table, containing the station, lat, and lon
        #
        temp_df = []
        with open(table,'r',encoding = 'latin1') as df:
            for _ in range(6):
                line = df.readline()
                line = line.strip().split(":;")
                temp_df.append(line)
        temp_df = list(map(list, zip(*temp_df)))
        
        #
        # - Select relevant variables and give them more palatable names:
        #
        df_head = pd.DataFrame(temp_df,columns=['REGIÃO', 'UF', 'ESTAÇÃO', 'CODIGO (WMO)', 'LATITUDE', 'LONGITUDE'])
        df_head = df_head[['ESTAÇÃO','LATITUDE','LONGITUDE']]
        df_head.rename(columns={'ESTAÇÃO':'est','LATITUDE':'lat','LONGITUDE':'lon'},inplace=True)
        
        #
        # b) Read the metereologic data for that station
        #
        df_tail = pd.read_csv(table,encoding ='latin1',skiprows = 8,sep = ';')
        
        #
        # - Select relevant variables and give them more palatable names:
        #
        if YEAR == '2018':
            df_tail = df_tail[['DATA (YYYY-MM-DD)','HORA (UTC)','TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']]
            df_tail.rename(columns={'DATA (YYYY-MM-DD)': 'date','HORA (UTC)':'time','TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)':'Temperature'}, inplace=True)
        else:
            df_tail = df_tail[['Data','Hora UTC','TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']]
            df_tail.rename(columns={'Data': 'date','Hora UTC':'time','TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)':'Temperature'}, inplace=True)
            df_tail['time'] = df_tail['time'][:-4]
            
        #
        # - Turn date and time strings into datetime objects.
        # - Same for Temperature, Lat, and Lon strings into floats for manipulation.
        #
        df_tail['date'] = pd.to_datetime(df_tail['date'])
        
        if YEAR == '2018':
            df_tail['time'] = pd.to_datetime(df_tail['time'],format = '%H:%M')
        else:
            df_tail['time'] = pd.to_datetime(df_tail['time'],format = '%H%M %Z')
            
        df_tail['Temperature'] = df_tail['Temperature'].str.replace(',', '.').astype(float)
        #df_head['lat'] = df_head['lat'].str.replace(',','.').astype(float)
        #df_head['lon'] = df_head['lon'].str.replace(',','.').astype(float)
        
        '''
        START PROCESSING DATA AND GATHERING STATISTICS
        '''
        #
        # 1- Check for outliers and deals with them
        #
        z_scores = (df_tail['Temperature'] - df_tail['Temperature'].mean()) / df_tail['Temperature'].std()
        outliers = (z_scores > 3) | (z_scores < -3)
        
        
        if DEBUGGING == True:
            print("Outliers:")
            print(df_tail[outliers])
            print('\n')
        
        #
        # 2- Calculate the mean and standart deviation on the data sans outliers
        #
        mean_temp = df_tail[~outliers]['Temperature'].mean()
        std_temp = df_tail[~outliers]['Temperature'].std()
        
        if DEBUGGING == True:
            print(df_head['est'][1])
            print(mean_temp)
            print(std_temp)
            print('\n')
        
        #
        # 3- Discard the tables where everyone is an outlier:
        #
        if abs(mean_temp) < 50 and abs(std_temp) < 50: 
            DATA.append([int(YEAR),df_head['est'][1],float(df_head['lat'][1].replace(',','.')),float(df_head['lon'][1].replace(',','.')),mean_temp,std_temp])
    
    os.chdir('..')
    
    
if DEBUGGING == True:
    print(DATA)
    
Out = pd.DataFrame(DATA,columns = ['Year','Station','Latitude','Longitude','Mean_Temp','Std_Temp'])
csv_data = Out.to_csv(Path(__file__).with_name('temp_data.csv'),index=False)
