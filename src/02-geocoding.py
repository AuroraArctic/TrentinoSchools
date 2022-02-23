# %%
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
# %%
# Data import
df = pd.read_pickle("../data/trentino/scuole.pkl")
df['CAP'] = df['CAP'].astype('string')
# %%
df = gpd.GeoDataFrame(df,
                      crs='EPSG:4326',
                      geometry=gpd.points_from_xy(df.lon, df.lat))
# %%
# Inspecting those schools with no coordinates
geocode_df = df[df['lat'].isna()]
# %%
# Create a complete address with street name and number, cap, municipality and province
tn_addresses = list(geocode_df['Nome']+", "+geocode_df['Indirizzo'].str.title() + ", " +
                    geocode_df['CAP']+", " + geocode_df['Comune'].str.title() + ", Trento")

# %%
# Geocoding with OpenStreetMap first, specifying the school to gather the exact position
geo_tn = gpd.tools.geocode(tn_addresses,
                           provider="nominatim",
                           user_agent="schools")

# %%
first = geocode_df.merge(geo_tn[~geo_tn['address'].isnull()],
                         left_index=True, right_index=True, suffixes=('x', ''))
first.drop(['geometryx'], axis=1, inplace=True)

df.loc[first.index, 'geometry'] = first['geometry']
df.loc[first.index, 'lat'] = [i.y for i in first['geometry']]
df.loc[first.index, 'lon'] = [i.x for i in first['geometry']]

# %%
# Geocode with Arcgis the remaining addresses
geocode_df = df[df['lat'].isna()]
# Create a complete address with street name and number, cap, municipality and province
tn_addresses = list(geocode_df['Indirizzo'].str.title() + ", " +
                    geocode_df['CAP']+", " + geocode_df['Comune'].str.title() + ", Trento")

# %%
# Geocoding with Arcgis without school names
geo_tn = gpd.tools.geocode(tn_addresses,
                           provider="arcgis")

#%%
geo_tn.index = geocode_df.index
second = geocode_df.merge(geo_tn[(~geo_tn['address'].isnull()) &
                                 (~geo_tn['address'].str.startswith("38"))],
                          left_index=True, right_index=True, suffixes=('x', ''))
second.drop(['geometryx'], axis=1, inplace=True)
#%%
df.loc[second.index, 'geometry'] = second['geometry']
df.loc[second.index, 'lat'] = [i.y for i in second['geometry']]
df.loc[second.index, 'lon'] = [i.x for i in second['geometry']]

# %%
geocode_df = df[df['lat'].isna()]
# %%
tn_addresses = list(geocode_df['Indirizzo'].str.title() + ", " +
                    geocode_df['Comune'].str.title() + ", Trento")

# %%
# Geocoding with OpenStreetMap without school names
geo_tn = gpd.tools.geocode(tn_addresses,
                           provider="nominatim",
                           user_agent="schools")
#%%
geo_tn.index = geocode_df.index
third = geocode_df.merge(geo_tn[~geo_tn['address'].isnull()],
                          left_index=True, right_index=True, suffixes=('x', ''))
third.drop(['geometryx'], axis=1, inplace=True)
#%%
df.loc[third.index, 'geometry'] = third['geometry']
df.loc[third.index, 'lat'] = [i.y for i in third['geometry']]
df.loc[third.index, 'lon'] = [i.x for i in third['geometry']]
# %%
# Search for None objects remaining
geocode_df = df[df['lat'].isna()]

# %%
# Manually inserting coordinates
geocode_df[['lat','lon']] = [[46.43982, 11.69179],
                             [45.91263, 10.61412],
                             [46.0354, 10.87076],
                             [46.22257, 10.82716],
                             [45.81072, 11.01411],
                             [46.02616, 10.83888],
                             [46.42304, 11.68182]]
geocode_df['geometry'] = geometry = [Point(xy) for xy in zip(geocode_df['lon'], geocode_df['lat'])]
# %%
df.loc[geocode_df.index, 'geometry'] = geocode_df['geometry']
df.loc[geocode_df.index, 'lat'] = [i.y for i in geocode_df['geometry']]
df.loc[geocode_df.index, 'lon'] = [i.x for i in geocode_df['geometry']]
# %%
# Check if there are None points
df.explore()
# %%

# Saving coordinates in GeoJSON
df.to_crs(4326).to_file("../data/trentino/schools/schools.geojson", index=False)

# Saving schools as shapefile
df = gpd.read_file("../data/trentino/schools/schools.geojson")
df.to_file("../data/Trentino/schools", driver='ESRI Shapefile')
