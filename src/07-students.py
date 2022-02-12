# %%
# Libraries
import geojson
import numpy as np
import requests
import geopandas as gpd
import folium
import pandas as pd

# %%
# Reading school files
schools = gpd.read_file(
    "../data/Trentino/schools/schools.geojson", geometry="geometry")

# Adjusting some municipalities names to match with ISTAT geojson
schools.replace("Baselga Di Pine'", 'Baselga Di Pinè', inplace=True)
schools.replace('Campitello Di Fassa - Ciampedel', "Campitello Di Fassa", inplace=True)
schools.replace('Canazei - Cianacei', "Canazei", inplace=True)
schools.replace( "Fiave'", "Fiavè", inplace=True)
schools.replace('Fierozzo - Vlarötz', "Fierozzo", inplace=True)
schools.replace("Male'", "Malé", inplace=True)
schools.replace('Moena - Moena', "Moena", inplace=True)
schools.replace("Rovere' Della Luna", "Roverè Della Luna", inplace=True)
schools.replace('San Giovanni Di Fassa - Sen Jan', "San Giovanni Di Fassa", inplace=True)
schools.replace('Contá', "Contà", inplace=True)

# Save file with changes
schools.to_file("../data/Trentino/schools/schools.geojson")

# Drop useless columns for this task
schools.drop(['index', 'Id Istituto', 'Telefono', 'Fax', 'Email istituto',
             'Email segreteria', 'Sito web'], axis=1, inplace=True)

# %%
students = schools[['Nome', 'lat', 'lon', 'Tipo Istituto',
                    'Gestione', 'Comune', 'geometry', 'Id']]
# Scraping data about students and classes
students = students[~students['Id'].isna()]

#%%
# Function to gather the number of students and classes for the current scolastic year
def get_students_and_classes(id):
    if id == None:
        return [np.nan, np.nan]
    else:
        # 1. Get the resource at the url specified
        url = "https://www.istruzione.provincia.tn.it/services/sei/api/v1/institutes/students/{}"
        r = requests.get(url.format(id)).json()
        # 2. Sum students and classes for the current year
        alunni = 0
        classi = 0
        for ordine in r['alunniXClassiAnnoScolasticoCorrente']:
            alunni += ordine['numeroAlunni']
            classi += ordine['numeroClassi']
        return [alunni, classi]

# Inserting students and classes for each school with a provincial code
students[['Studenti', 'Classi']] = [get_students_and_classes(x) for x in students['Id']]

# Saving these information
students.to_pickle("../data/Trentino/schools/students.pkl")

#%% 
# Now instead of scraping data from aprilascuola, use the official numbers provided
# by the province of Trento (more reliable according to the director of Education)

# %%
# Reading aprilascuola data file with students and classes in December 2021
df = pd.read_csv("../data/population/students_per_school.csv", sep=";", dtype=object)
df.rename(columns={
    'Istituzione Scolastica': 'Istituto',
    'Ordine Scolastico': 'Tipo Istituto',
    'Scuola/Indirizzo': 'Nome',
    'Scuola/Indirizzo - Codice PAT': 'Id',
    'Numero Iscritti': 'Studenti',
    'Numero Classi': 'Classi'
}, inplace=True)
df['Studenti'] = df['Studenti'].astype("int32")
df['Classi'] = df['Classi'].astype("int32")
df[['Istituto', 'Tipo Istituto', 'Nome']] = df[['Istituto',
                                                'Tipo Istituto', 'Nome']].applymap(lambda s: s.title())

# Erasing duplicated lines
df.drop_duplicates(inplace=True)

#%%
students = pd.merge(schools, df, on=["Id",'Nome','Istituto'])
students.drop(['Tipo Istituto_x'],axis=1, inplace=True)
students.rename(columns = {'Tipo Istituto_y': 'Tipo Istituto'}, inplace=True)
#%%
stud_agg = students.groupby(['Comune'], as_index=False).sum()[
    ['Comune', 'Studenti', 'Classi']]
stud_agg
stud_schools = students.groupby(['Comune']).size().to_frame('Schools')
# %%
stud_agg = stud_agg.set_index('Comune')
# Geodata with information to make popup in the map
import numpy as np
geo_data = geojson.load(open("../data/trentino.geojson", encoding="utf-8"))
len(geo_data['features'])
for s in geo_data['features']:
    # Total number of schools
    s['properties']['N. Scuole'] = s['properties']['n_schools'] 
    comune = s['properties']['Comune']
    if comune not in list(stud_agg.index):
        s['properties']['Studenti'] = np.nan
        s['properties']['Classi'] = np.nan
        # Schools of which we detain students data
        s['properties']['n_schools'] = 0
        s['properties']['density'] = np.nan
        s['properties']['Media studenti per classe'] = np.nan
        s['properties']['Media studenti per scuola'] = np.nan
    else:
        s['properties']['Studenti'] = int(stud_agg.loc[comune,'Studenti'])
        s['properties']['Classi'] = int(stud_agg.loc[comune,'Classi'])
        # Schools of which we detain students data
        s['properties']['n_schools'] = int(stud_schools.loc[comune,'Schools'])
        s['properties']['density'] = round(int(s['properties']['Studenti'])/int(s['properties']['population']),2)
        s['properties']['Media studenti per classe'] = round(s['properties']['Studenti']/s['properties']['Classi'],2)
        s['properties']['Media studenti per scuola'] = round(s['properties']['Studenti']/s['properties']['n_schools'],2)
stud_agg = stud_agg.reset_index()

#%%
from geojson import FeatureCollection
resume_schools_municipalities = gpd.GeoDataFrame.from_features(FeatureCollection(geo_data))
resume_schools_municipalities.rename(columns = {'population':'Popolazione'}, inplace=True)

resume_schools_municipalities['Studenti'] = resume_schools_municipalities['Studenti'].astype("Int64")
resume_schools_municipalities['Classi'] = resume_schools_municipalities['Classi'].astype("Int64")
resume_schools_municipalities['density'] = resume_schools_municipalities['density'].astype("Float64")
resume_schools_municipalities['Media studenti per classe'] = resume_schools_municipalities['Media studenti per classe'].astype("Float64")
resume_schools_municipalities['Media studenti per scuola'] = resume_schools_municipalities['Media studenti per scuola'].astype("Float64")

resume_schools_municipalities.drop(resume_schools_municipalities[resume_schools_municipalities['Studenti'].isna()].index, inplace=True)
resume_schools_municipalities = resume_schools_municipalities.set_crs("EPSG:4326")

resume_schools_municipalities.to_file("../data/aggregated_data_per_municipality.geojson")
#%%
#%%
# MAP
m = folium.Map(location=[46.1, 11.2],
               zoom_start=9,
               tiles=None,
               overlay=False)

fg1 = folium.FeatureGroup(name='Studenti',overlay=False).add_to(m)
fg2 = folium.FeatureGroup(name='Popolazione',overlay=False).add_to(m)
fg3 = folium.FeatureGroup(name='Scuole',overlay=False).add_to(m)

bins = list(resume_schools_municipalities["Studenti"].quantile([0, 0.7, 0.95, 0.99, 0.995, 1]))
#Add the first choropleth map layer to fg1
students=folium.Choropleth(
            geo_data=geo_data,
            data=resume_schools_municipalities,
            columns=['Comune', 'Studenti'],  
            key_on='feature.properties.Comune', 
            bins=bins, #use the custom scale we created for legend
            fill_color='YlOrRd',
            nan_fill_color="White", #Use white color if there is no data available for the county
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Studenti Trentino',
            highlight=True,
            overlay=True)

students.geojson.add_to(fg1)

folium.GeoJsonTooltip(fields = ['Comune', 'Studenti','Classi',
                                'N. Scuole', 'Media studenti per classe',
                                'Media studenti per scuola', 'population'],
                      aliases = ['Comune', 'Studenti','Classi',
                                'N. Scuole', 'Media studenti per classe',
                                'Media studenti per scuola', 'Popolazione']).add_to(students.geojson)

bins = list(resume_schools_municipalities["Popolazione"].quantile([0, 0.7, 0.95, 0.99, 0.995, 1]))

pop = folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=resume_schools_municipalities,
    columns=["Comune", "Popolazione"],
    key_on="feature.properties.Comune",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Number of students",
    bins=bins,
    highlight=True,
    reset=True,
    nan_fill_color="White",
)
pop.geojson.add_to(fg2)

folium.GeoJsonTooltip(fields = ['Comune', 'population','Studenti','N. Scuole'],
                      aliases=['Comune', 'Popolazione','Studenti', 'N. Scuole']).add_to(pop.geojson)


# # Layer with the number of schools
bins = list(resume_schools_municipalities["N. Scuole"].quantile([0, 0.7, 0.95, 0.99, 0.995, 1]))
scu = folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=resume_schools_municipalities,
    columns=["Comune", "N. Scuole"],
    key_on="feature.properties.Comune",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Number of students",
    bins=bins,
    highlight=True,
    reset=True,
    nan_fill_color="White",
)
scu.geojson.add_to(fg3)

folium.GeoJsonTooltip(fields = ['Comune', 'Studenti','Classi',
                                'N. Scuole', 'Media studenti per classe',
                                'Media studenti per scuola', 'population'],
                      aliases = ['Comune', 'Studenti','Classi',
                                'N. Scuole', 'Media studenti per classe',
                                'Media studenti per scuola', 'Popolazione']).add_to(scu.geojson)

folium.TileLayer('cartodbdark_matter',overlay=True,name="Dark Mode").add_to(m)
folium.TileLayer('cartodbpositron',overlay=True,name="Light Mode").add_to(m)
folium.LayerControl(collapsed=False).add_to(m)
m
m.save("../viz/students_population.html")
# %%
