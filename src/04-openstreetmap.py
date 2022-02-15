# %%
# Libraries to import
import pandas as pd
import pygeos
import pyrosm
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
import requests
import os

# %%
osm_tn_url = "https://osmit-estratti.wmcloud.org/dati/poly/province/pbf/022_Trento_poly.osm.pbf"
# %%
# If data is not downloaded yet, request from ISTAT
if not os.path.exists('../data/Limiti01012021_g'):
    # download the data
    import requests
    import zipfile
    import io
    zip_file_url = 'https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/Limiti01012021_g.zip'
    # request the file
    r = requests.get(zip_file_url, verify=False)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    # unzip the file
    z.extractall("../data/")

# %%
trentino = gpd.read_file("../data/Trentino/schools/schools.geojson",
                         geometry="geometry")

# %%
trento_download_pbf_url = "https://osmit-estratti.wmcloud.org/dati/poly/province/pbf/022_Trento_poly.osm.pbf"
# download the data
# request the file
r = requests.get(trento_download_pbf_url, allow_redirects=True)
# save the file
open('../data/trento.pbf', 'wb').write(r.content)

# %%

# %%
# Initialize the OSM object
osm = pyrosm.OSM("../data/trento.pbf")

# %%
# TRANSPORT - DRIVING, BICYCLING AND WALKING
drive_net = osm.get_network(network_type="driving")
walk_net = osm.get_network(network_type="walking")
cycle_net = osm.get_network(network_type="cycling")

# %%
# Get natural elements
nature = osm.get_natural()
nature.explore()
ax = nature.plot(column='natural', markersize=3, figsize=(12, 12), legend=True,
                 legend_kwds=dict(loc='upper left', ncol=5, bbox_to_anchor=(1, 1)))
plt.show()
# %%
custom_filter = {'amenity': True, 
                 'shop' : True,
                 'tourism': True,
                 'leisure': True}
pois = osm.get_pois(custom_filter)

# %%
pois = pois[['lat', 'lon', 'name', 'amenity','shop','tourism',
             'leisure', 'opening_hours','phone', 'website',
             'internet_access', 'geometry']]

pois['category'] = pois['amenity'].fillna(pois['shop']).fillna(pois['tourism']).fillna(pois['leisure'])
pois.drop(['amenity','shop','tourism', 'leisure'], axis=1, inplace=True)
# %%
def categorize(type):
    if type in ['bus_station']:
        return "Bus"
    elif type in ['bar', 'cafe', 'restaurant', 'restaurant;bar', 
                  'restaurant;cafe', 'fast_food','food_court',
                  'ice_cream', 'supermarket',]:
        return "Food"
    elif type in ['childcare', 'clinic', 'dentist', 'doctors', 'hospital', 'pharmacy']:
        return "Healthcare"
    elif type in ['training','gym','ski_school','sailing_school']:
        return "Sport"
    elif type in ['theatre','museum','arts_centre','cinema','library', 'zoo', 'planetarium']:
        return "Culture"
    elif type in ["typography",'tipography','drinking_water','stationery', 'copyshop','printing']:
        return "Utilities"
    elif type in ['outdoor']

set(pois['category'])
pois['type'] = [categorize(x) for x in pois['category']]
# %%
if not os.path.exists("../data/amenity_classification.csv"):
    pd.DataFrame(set(pois['amenity'])).to_csv(
        "../data/amenity_classification.csv", index=False)
else:
    classification = pd.read_csv("../data/amenity_classification.csv")
# Manual insertion of the classification with -1, 0 and 1
pois = pd.merge(pois[['amenity', 'geometry']],
                classification, how="inner", on='amenity')
pois['classification'] = pd.Categorical(pois['classification'], ordered=True)
pois = gpd.GeoDataFrame(pois)
# %%
# Plot
ax = pois.plot(column='classification', markersize=3, figsize=(12, 12), legend=True,
               legend_kwds=dict(loc='upper left', ncol=5, bbox_to_anchor=(1, 1)))
plt.show()
# %%
# TASKS
# 1. Get all points around 500 meters from every school
# 2. Color schools in blue, good points in green, bad in red, neutral in yellow

# %%
schools = gpd.read_file("../data/Trentino/schools/schools.geojson")
