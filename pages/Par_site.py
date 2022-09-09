# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 16:55:32 2022

@author: hp
"""
import pandas as pd
#import numpy as np
import math
#from math import *
import mpu
#from pygc import great_circle
from sqlalchemy.engine import create_engine
import streamlit as st
from geopy.geocoders import Nominatim
#from pyxlsb import open_workbook as open_xlsb
from io import BytesIO
import folium
from streamlit_folium import folium_static
import os
from folium import plugins
#df=pd.read_excel("Nouveaux_sites.xlsx")
from sqlalchemy.engine import create_engine
import pandas as pd

# import data from DB oracle

DIALECT = 'oracle'
SQL_DRIVER = 'cx_oracle'
USERNAME = 'xe' #enter your username
PASSWORD = 'xe' #enter your password
HOST = 'DESKTOP-9RJJSL5' #enter the oracle db host url
PORT = 1521 # enter the oracle port number
SERVICE = 'XE' # enter the oracle db service name
ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE
engine = create_engine(ENGINE_PATH_WIN_AUTH)

#sql = """ SELECT * FROM test WHERE cell_name="""+condition+
#sql= sql.replace('"', "'") 

df = pd.read_sql_query("SELECT * FROM NOUVEAUX_SITES", engine)
#df=pd.read_sql_query("SELECT * from TEST where trafic_lte>40",engine)
latitude_site=0
longitude_site=0
with st.sidebar:
    Site_name=st.text_input("donner le nom de site : ") 
for i in range(len(df)):
    if df.loc[i,"sitename"]==Site_name:
        latitude_site=df.loc[i,"latitude_sector"]
        longitude_site=df.loc[i,"longitude_sector"]
    break
###

def plus_proche_network2(lat, long):
    liste = []
    liste2 = []
    #list_azi=[]
    with st.sidebar:
        d= st.number_input(label="donner le rayon de la zone  :")
    #cell= " "
    latitude_site = lat
    longitude_site = long
    for i in range(len(df)): #df: dataframe des sites
        latitude = df.loc[i, "latitude_sector"] #la valeur de la cellule (lat) a comme ligne i et colonne lat_sec
        longitude = df.loc[i, "longitude_sector"]
        dist = mpu.haversine_distance((latitude_site, longitude_site), (latitude, longitude)) #distance entre client et site on se basant sur leurs lat et lon
        if dist <= d:
            cell = df.loc[i, "sitename"] #nom du site
            latf = latitude #lat du secteur(BTS) detecté 
            longf = longitude #lon du secteur(BTS) detecté
            azim = df.loc[i, "azimuth"] #azi du secteur(BTS) detecté
            sector = df.loc[i, "sector"] #nom du secteur(BTS)detecté
            liste.append([cell, latf, longf,dist, azim, sector])
            
    return liste 
 
# application du fonction plus_proche_network2 sur  du client 
def Execution(latit,longit):
    df_result= pd.DataFrame(columns=['cell','latitude_site','longitude_site','distance','azim','Sector'])
    latitude_site=latit
    longitude_site=longit
    listt = plus_proche_network2(latitude_site,longitude_site)
    df_result = df_result.append(pd.DataFrame(listt, columns=['cell','latitude_site','longitude_site','distance','azim','Sector']),ignore_index=True)
    df_result=df_result.drop(['latitude_site','longitude_site'], axis=1)
    return df_result
Resultat=Execution(latitude_site,longitude_site)



def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data













with st.sidebar:
    df_xlsx = to_excel(Resultat)
    st.download_button(label='📥 Download Current Result ',
                                data=df_xlsx ,
                                file_name= 'les_sites_proches.xlsx')
    if st.button('go to power BI '):
     os.popen(r"C:\Users\hp\Desktop\PYTHONFILES\testone.pbix")