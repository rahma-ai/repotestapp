import streamlit as st

st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
    
    )

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

st.title("SISA Application")

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
df = pd.read_sql_query("SELECT * FROM NOUVEAUX_SITES", engine)

#st.dataframe(df)
## get latitude and longitude of the client 
#st.text_area('vous pouvez coller ici longitude et latitude une seul fois ! ')
with st.sidebar:
    st.markdown("Renseignez les coordonnées GPS de client ")
    latitude_client= st.number_input(label="donner latitude  de client :")
    longitude_client= st.number_input(label="donner longitude de client :")


# Latitude & Longitude input  et l'adresse de client est l'output 
geolocator = Nominatim(user_agent="geoapiExercises")
location = geolocator.reverse(str(latitude_client)+","+str(longitude_client))
address = location.raw['address']
city=address.get('city','')
st.write("la ville de client est:",city)
# algorithme les plus proches netzorkes from the client
def plus_proche_network2(lat, long):
    liste = []
    liste2 = []
    #list_azi=[]
    with st.sidebar:
        d= st.slider("donner le rayon de couverture  :", 0, 20)
    #d = st.number_input(label="donner le rayon de couverture  :")
    cell= " "
    lat_customer = lat
    lon_customer = long
    for i in range(len(df)): #df: dataframe des sites
        latitude = df.loc[i, "latitude_sector"] #la valeur de la cellule (lat) a comme ligne i et colonne lat_sec
        longitude = df.loc[i, "longitude_sector"]
        dist = mpu.haversine_distance((lat_customer, lon_customer), (latitude, longitude)) #distance entre client et site on se basant sur leurs lat et lon
        if dist <= d:
            cell = df.loc[i,"sitename"] #nom du site
            latf = latitude #lat du secteur detecté 
            longf = longitude #lon du secteur detecté
            azim = df.loc[i,"azimuth"] #azi du secteur detecté
            sector = df.loc[i,"sector"] #nom du secteur(BTS)detecté
            liste.append([cell, latf, longf, azim, dist, sector])
    for l in liste:
        liste2.append([lat_customer, lon_customer, l[0], l[1], l[2],l[3],l[4]*1000,l[5]])
    return liste2
# application du fonction plus_proche_network2 sur longitude et latitude du client 
def Execution(latitude_client,longitude_client):
    df_result= pd.DataFrame(columns=['lat_customer','lon_customer','site','Lat','Lont','azim','distance','Sector'])
    lat_customer = latitude_client
    lon_customer = longitude_client
    listt = plus_proche_network2(lat_customer,lon_customer)
    df_result = df_result.append(pd.DataFrame(listt, columns=['lat_customer','lon_customer','site','Lat','Lont','azim','distance','Sector']),ignore_index=True)
    df_result=df_result.drop(['lat_customer','lon_customer'], axis=1)
    return df_result
# crre un fichier excel contient les site reseaux plus proches de client
Resultat_palque=Execution(latitude_client,longitude_client)


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
df_xlsx = to_excel(Resultat_palque)
with st.sidebar:
    st.download_button(label='📥 Download Current Result',
                                data=df_xlsx ,
                                file_name= 'df_test.xlsx')
                                                                                    ### visualiser les sites sur une map
#morroco=folium.Map(location=[latitude_client,longitude_client],zoom_start=10)
# get map of morrocc o from its longitudes and latitude

morroco=folium.Map(location=[latitude_client,longitude_client],zoom_start=15)# get map of morrocc o from its longitudes and latitude
for _, site in Resultat_palque.iterrows():
    folium.Marker(
        location=[site['Lat'], site['Lont']],
        popup=site['site']+"-" + site['Sector'],
        tooltip=site['site']+" - " + site['Sector'],
        icon=folium.Icon(color='orange')
 ).add_to(morroco)
folium.Marker(
    location=[33.592126,-7.614453],
    icon=folium.Icon(icon='envelope',color='red')
).add_to(morroco)
#folium_static(morroco, width=1000, height=950)



# Display azimuths sectors 
for index, site in Resultat_palque.iterrows():
    location=[site['Lat'], site['Lont']]
    length = .001
    azim1 = site['azim']-20 
    azim2= site['azim']+20 
    angle1= 450 - azim1
    angle2= 450 - azim2
    end_lat1 = location[0] + length * math.sin(math.radians(angle1))
    end_lon1 = location[1] + length * math.cos(math.radians(angle1))
    end_lat2 = location[0] + length * math.sin(math.radians(angle2))
    end_lon2 = location[1] + length * math.cos(math.radians(angle2))

    #Dsiplay sector
    ang_sec= (angle1+angle2)/2
    lat_sec= location[0] + .0008 * math.sin(math.radians(ang_sec))
    Lon_sec= location[1] + .0008  * math.cos(math.radians(ang_sec))
    name_sec= site["azim"]

    folium.Polygon([location, [end_lat1, end_lon1], [end_lat2, end_lon2]],
                    color="red",
                    weight=1,
                    fill=True,
                    fill_color="red",
                    fill_opacity=0.1).add_to(morroco)
    folium.Marker(location=[lat_sec, Lon_sec],
              popup=site["Sector"],
              icon=folium.DivIcon(html="<b>"+ str(name_sec)+"</b>"),
              ).add_to(morroco)

folium_static(morroco, width=1000, height=950)
with st.sidebar:
    if st.button('go to power BI '):
        os.popen(r"C:\Users\hp\Desktop\PYTHONFILES\testone.pbix")