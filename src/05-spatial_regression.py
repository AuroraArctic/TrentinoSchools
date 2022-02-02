# %%

# Get municipalities data of Trento
from itertools import groupby
import matplotlib as plt
import folium
import pandas as pd
import geopandas as gpd
import requests

#%%
# ISTAT Administrative units data 
url = 'https://github.com/napo/geospatial_course_unitn/blob/master/data/istat/istat_administrative_units_generalized_2021.gpkg?raw=true'
trentino = gpd.read_file(url, layer="municipalities")

# Selecting the province of Trento
trentino = trentino[trentino['COD_PROV'] == 22]

# %%
# Take a look at the territory selected
trentino.plot()
# %%
# Changing crs
trentino = trentino.to_crs(4326)
#%%
# Now replot to see how coordinates have changed
trentino.plot()
# %%
# Importing schools position and name
schools = gpd.read_file("../data/Trentino/schools/schools.geojson")
schools = schools[['Scuola','Tipo Istituto','Tipo Gestione','Comune','address','geometry']]
# %%
munic = {}
for i in range(len(trentino)):
    if trentino.iloc[i, 7] in munic.keys():
        munic[trentino.iloc[i, 7]].append(
            [row for row in schools[schools['geometry'].within(trentino.iloc[i, -1])].iterrows()])
    else:
        munic[trentino.iloc[i, 7]] = [
            row for row in schools[schools['geometry'].within(trentino.iloc[i, -1])].iterrows()]

# %%
n_schools = []
for m in trentino['COMUNE']:
    if m not in munic.keys():
        n_schools.append(0)
    else:
        n_schools.append(len(munic[m]))

# %%
trentino['n_schools'] = n_schools

# %%
# ADDING POPULATION DATA
# Population
population = pd.read_csv("../data/population/ItalianPopulation2021.csv")
population = population[['ITTER107', 'Territorio',
                         'Sesso', 'Value']].iloc[3:, :].reset_index(drop=True)

municipalities = pd.read_csv("../data/Municipalities.csv",
                             delimiter=";", encoding="ANSI", dtype={'ID': 'object'})

pop_tot = population.groupby(
    ['ITTER107', 'Territorio', 'Sesso'], as_index=False).sum()
pop_tot.rename(columns={'Value': 'population'}, inplace=True)

# %%
pop_tot = pop_tot[pop_tot['Sesso'] != "totale"]

#%%
pop_tot = pop_tot.pivot(index = ['ITTER107','Territorio'],
              columns='Sesso',
              values='population').reset_index()
# %%
trentino = pd.merge(trentino, pop_tot,
                    left_on='PRO_COM_T',
                    right_on='ITTER107')
# %%
trentino[['geometry', 'n_schools', 
          'COMUNE', 'population']].to_file("../data/trentino.geojson",
                                         driver='GeoJSON',
                                         encoding = "UTF-8")

#%%
trentino = trentino[['COMUNE','geometry','n_schools','ITTER107','femmine','maschi']]
trentino['population'] = trentino['femmine']+ trentino['maschi']
# %%

geo_dataset = "../data/trentino.geojson"
#%%
bins = list(trentino["n_schools"].quantile([0, 0.75,
                                            0.90, 0.95, 0.98, 0.99, 0.995, 1]))
m = folium.Map(location=[46.1, 11.2], 
               zoom_start=9, 
               tiles = 'cartodbpositron')

import geojson
geo_data = geojson.load(open(geo_dataset,encoding="utf-8"))

c = folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=trentino,
    columns=["COMUNE", "n_schools"],
    key_on="feature.properties.COMUNE",
    fill_color="YlOrRd",
    fill_opacity=0.5,
    line_opacity=0.2,
    legend_name="Number of schools",
    bins=bins,
    reset=True,
)
folium.GeoJsonTooltip(fields = ['COMUNE','n_schools','population']).add_to(c.geojson)
c.add_to(m)

folium.LayerControl().add_to(m)

m.save("../viz/schools_density.html")
