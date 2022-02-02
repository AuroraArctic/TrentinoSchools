# %%
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
# %%
# Data import
df = pd.read_csv("../data/trentino/scuole.csv")
df['CAP'] = df['CAP'].astype('string')
# Create a complete address with street name and number, cap, municipality and province
tn_addresses = list(df['Scuola']+", "+df['Indirizzo'].str.title() + ", " +
                    df['CAP']+", " + df['Comune'].str.title() + ", Trento")

# %%
# Geocoding with OpenStreetMap first
geo_tn = gpd.tools.geocode(tn_addresses,
                           provider="nominatim",
                           user_agent="schools")

#%%
# %%
# Save results obtained in geojson not to lose them
first = df.merge(geo_tn[~geo_tn['address'].isnull()],
                 left_index=True, right_index=True)
schools = gpd.GeoDataFrame(first)

# schools.to_crs(4326).to_file("../data/trentino/schools.geojson",index=True)

# %%
# Missing addresses indexes
missing_indexes = list(geo_tn.index)
for x in list(first.index):
    missing_indexes.remove(x)

# %%
# Geocode with Arcgis the remaining addresses
# Create a complete address with street name and number, cap, municipality and province
tn_addresses = list(df.loc[missing_indexes, 'Indirizzo'].str.title() + ", " +
                    df.loc[missing_indexes, 'CAP']+", " +
                    df.loc[missing_indexes, 'Comune'].str.title() + ", Trento")

# %%
# Geocoding with Arcgis without school names
geo_tn = gpd.tools.geocode(tn_addresses,
                           provider="arcgis")

# %%
geo_tn.index = missing_indexes

# %%
second = df.merge(geo_tn[(~geo_tn['address'].isnull()) &
                         (~geo_tn['address'].str.startswith("38"))],
                  left_index=True, right_index=True)
schools = gpd.GeoDataFrame(pd.concat([schools, second]))

# %%
missing_indexes = list(df.index)
for x in list(schools.index):
    missing_indexes.remove(x)

# %%
tn_addresses = list(df.loc[missing_indexes, 'Indirizzo'].str.title() + ", " +
                    df.loc[missing_indexes, 'Comune'].str.title() + ", Trento")

# %%
# Geocoding with OpenStreetMap without school names
geo_tn = gpd.tools.geocode(tn_addresses,
                           provider="nominatim",
                           user_agent="schools")

# %%
geo_tn.index = missing_indexes

# %%
third = df.merge(geo_tn, left_index=True, right_index=True)
schools = gpd.GeoDataFrame(pd.concat([schools, third]))
# %%
# Search for None objects
schools.loc[schools['geometry'].is_empty,
            'geometry'] = Point(10.83887,46.02616)
schools.loc[schools['address'].isnull(), 'address'] = "Scuola dell'Infanzia di S. Croce Bleggio, 7, \
    Frazione Santa Croce di Bleggio Inferiore, 7, Villa, Comano Terme, Comunità delle Giudicarie, \
    Provincia di Trento, Trentino-Alto Adige, 38071, Italia"
# %%
schools.sort_index(inplace=True)
#%%
# Saving coordinates in GeoJSON
schools.to_crs(4326).to_file("../data/trentino/schools.geojson",index=True)
# %%

#%% 
# Saving schools as shapefile
schools = gpd.read_file("../data/trentino/schools.geojson")
schools.to_file("schools.shp",driver='ESRI Shapefile')