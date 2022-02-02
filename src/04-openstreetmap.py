#%%
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
#%%
# If data is not downloaded yet, request from ISTAT
if not os.path.exists('../data/Limiti01012021_g'):
    # download the data
    import requests, zipfile, io
    zip_file_url = 'https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/Limiti01012021_g.zip'
    # request the file
    r = requests.get(zip_file_url, verify=False)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    # unzip the file
    z.extractall("../data/")

#%%
trentino = gpd.read_file("../data/Trentino/schools/schools.geojson",
                         geometry="geometry")

# %%
# Try to give a look at the data
trentino.explore(marker_type="marker",
                 marker_kwds={"radius": "5",
                              "color": "cornflowerblue",
                              'icon': folium.map.Icon(prefix='fa',
                                                      icon='graduation-cap')})

# %% [markdown]
# ## Retrieve schools via OpenStreetMap

# %%

# %%
trent
o_download_pbf_url = "https://osmit-estratti.wmcloud.org/dati/poly/province/pbf/022_Trento_poly.osm.pbf"
# download the data
# request the file
r = requests.get(trento_download_pbf_url, allow_redirects=True)
# save the file
open('../data/trento.pbf', 'wb').write(r.content)

# %%

#%%
# Initialize the OSM object
osm = pyrosm.OSM("../data/trento.pbf")
osm.to_graph()

# %%
# TRANSPORT - SECURITY OF DRIVING, BICYCLING AND WALKING
drive_net = osm.get_network(network_type="driving")
walk_net = osm.get_network(network_type="walking")
cycle_net = osm.get_network(network_type="cycling")

#%%
custom_filter = {'amenity': True}
pois = osm.get_pois(custom_filter)
#%%
set(pois['amenity'])
#%%
# Plot
ax = pois.plot(column='amenity', markersize=3, figsize=(12,12), legend=True, 
               legend_kwds=dict(loc='upper left', ncol=5, bbox_to_anchor=(1, 1)))
plt.show()
# %%
pois.explore(marker_type="marker",
             marker_kwds={"radius": "5",
                          "color": "cornflowerblue",
                          'icon': folium.map.Icon(prefix='fa',
                                                  icon='graduation-cap')})


# %%
osm_schools = gpd.GeoDataFrame(
    pois,
    crs='EPSG:4326',
    geometry=gpd.points_from_xy(pois.lon,
                                pois.lat))

# %%

# %%


def min_dist(point, gpd2):
    gpd2['Dist'] = gpd2.apply(lambda row: point.distance(row.geometry), axis=1)
    closest_index = gpd2.iloc[gpd2['Dist'].argmin()][['geometry', 'name']]
    return closest_index


# %%
trentino[['osm_geom', 'osm_name']] = [min_dist(trentino.iloc[x, -1], osm_schools[~osm_schools['lon'].isnull()])
                                      for x in range(len(trentino))]

# %%
trentino.drop(['id', 'mun_id', 'province', 'email',
              'pec', 'website'], axis=1, inplace=True)

#%%
