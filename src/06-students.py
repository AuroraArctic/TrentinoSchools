# %%
# Libraries
from geojson import FeatureCollection
import os
from turtle import left
import geojson
import numpy as np
import requests
import geopandas as gpd
import folium
import pandas as pd

# %%
# 1. ADJUSTING ISTAT POPULATION DATA
# ISTAT Trentino Population, filtering total data
# about the Region and the province
df = pd.read_csv(
    "../data/population/ISTAT_Trentino_population.csv", dtype="str")
df = df[(df['ITTER107'] != "ITD20") & (df['ITTER107'] != "ITD2") &
        (df['ETA1'] != "TOTAL") & (df['Stato civile'] == "totale")]

# %%
# Removing unnecessary columns
df.drop(['Flag Codes', 'Flags',
         'Seleziona periodo', "TIPO_DATO15", 'STATCIV2', 'Stato civile',
         "Tipo di indicatore demografico", 'TIME', 'SEXISTAT1', 'ETA1'], axis=1, inplace=True)

# %%
# Renaming columns
df.rename(columns={
    'ITTER107': 'Id',
    'Territorio': 'Comune',
    'Età': 'Anni',
    'Value': 'Popolazione'
}, inplace=True)

# Converting years and population to int
df['Anni'] = [int(x.split(" ")[0]) for x in df['Anni']]
df['Popolazione'] = df['Popolazione'].astype("int32")

# Converting Municipality to Title
df['Comune'] = [x.title() for x in df['Comune']]
# %%
# Saving the dataframe as csv
df.to_csv("../data/population/trentino_pop_per_age.csv", index=False)

# Pick total population per each municipality
df = df.groupby(['Id', 'Comune', 'Sesso'], as_index=False).sum()[
    ['Id', 'Comune', 'Sesso', 'Popolazione']]
# Saving dataframe as csv
df.to_csv("../data/population/trentino_total_pop.csv", index=False)

# %%
# 2. READING SCHOOLS DATA
# Reading school files
schools = gpd.read_file(
    "../data/Trentino/schools/schools.geojson", geometry="geometry")

# Adjusting some municipalities names to match with ISTAT geojson
schools.replace("Baselga Di Pine'", 'Baselga Di Pinè', inplace=True)
schools.replace('Campitello Di Fassa - Ciampedel',
                "Campitello Di Fassa", inplace=True)
schools.replace('Canazei - Cianacei', "Canazei", inplace=True)
schools.replace("Fiave'", "Fiavè", inplace=True)
schools.replace('Fierozzo - Vlarötz', "Fierozzo", inplace=True)
schools.replace("Male'", "Malé", inplace=True)
schools.replace('Moena - Moena', "Moena", inplace=True)
schools.replace("Rovere' Della Luna", "Roverè Della Luna", inplace=True)
schools.replace('San Giovanni Di Fassa - Sen Jan',
                "San Giovanni Di Fassa", inplace=True)
schools.replace('Contá', "Contà", inplace=True)
schools.replace("Luserna - Lusérn", "Luserna", inplace=True)
schools.replace("Panchia'", "Panchià", inplace=True)
schools.replace("Ruffre' - Mendola", "Ruffrè-Mendola", inplace=True)
schools.replace("Soraga - Soraga", "Soraga Di Fassa", inplace=True)

# Save file with changes
schools.to_file("../data/Trentino/schools/schools.geojson")

# Drop useless columns for this task
schools.drop(['index', 'Id Istituto', 'Telefono', 'Fax', 'Email istituto',
             'Email segreteria', 'Sito web'], axis=1, inplace=True)

# %%
# TASK: GET NUMBER OF STUDENTS FOR EACH SCHOOL
# First option: Scraping from Aprilascuola Project
students = schools[['Nome', 'lat', 'lon', 'Tipo Istituto',
                    'Gestione', 'Comune', 'geometry', 'Id']]

# Scraping data about students and classes based on the provincial ID
# Removing those schools with no ID
students = students[~students['Id'].isna()]

# %%
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
students[['Studenti', 'Classi']] = [
    get_students_and_classes(x) for x in students['Id']]

# Saving these information
students.to_pickle("../data/Trentino/schools/students.pkl")

# %%
# Now instead of scraping data from aprilascuola, use the official numbers provided
# by the province of Trento (more reliable according to the department of Education and Culture of Trentino)

# Reading aprilascuola data file with students and classes in December 2021
df = pd.read_csv("../data/population/students_per_school.csv",
                 sep=";", dtype=object)

# Renaming columns
df.rename(columns={
    'Istituzione Scolastica': 'Istituto',
    'Ordine Scolastico': 'Tipo Istituto',
    'Scuola/Indirizzo': 'Nome',
    'Scuola/Indirizzo - Codice PAT': 'Id',
    'Numero Iscritti': 'Studenti',
    'Numero Classi': 'Classi'
}, inplace=True)

# Applying some transformations
df['Studenti'] = df['Studenti'].astype("int32")
df['Classi'] = df['Classi'].astype("int32")
df[['Istituto', 'Tipo Istituto', 'Nome']] = df[['Istituto',
                                                'Tipo Istituto', 'Nome']].applymap(lambda s: s.title())

# Erasing duplicated lines
df.drop_duplicates(inplace=True)

# %%
# Merging schools data with students data
students = pd.merge(schools, df, on=["Id", 'Nome', 'Istituto'])
students.drop(['Tipo Istituto_x'], axis=1, inplace=True)
students.rename(columns={'Tipo Istituto_y': 'Tipo Istituto'}, inplace=True)
# %%
# Group by Municipality to get the total number of students and classes
stud_agg = students.groupby(['Comune'], as_index=False).sum()[
    ['Comune', 'Studenti', 'Classi']]
stud_agg
stud_schools = students.groupby(['Comune']).size().to_frame('Schools')
stud_agg = stud_agg.set_index('Comune')
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
# 3. CREATING A GEOJSON WITH ALL MUNICIPALITIES AND INFORMATION ABOUT STUDENTS, SCHOOLS AND POPULATION
trentino = gpd.read_file(
    "../data/Limiti01012021_g/Com01012021_g", encoding="utf-8")
trentino = trentino[trentino['COD_PROV'] == 22]
trentino = trentino.to_crs(4326)
trentino = trentino[['COMUNE', 'PRO_COM_T', 'geometry']].reset_index(drop=True)
trentino.rename(columns={
    'COMUNE': 'Comune',
    'PRO_COM_T': 'Id'
}, inplace=True)
trentino['Comune'] = [x.title() for x in trentino['Comune']]

trentino.set_index("Comune", inplace=True)
trentino['Scuole totali'] = schools.groupby(
    ['Comune']).size().to_frame("Scuole Totali")
trentino['Scuole studenti'] = students.groupby(
    ['Comune']).size().to_frame("Scuole_studenti")
trentino[['Studenti', 'Classi']] = stud_agg
trentino['Media stud per classe'] = round(
    trentino['Studenti']/trentino['Classi'], 2)
trentino['Media stud per scuola'] = round(
    trentino['Studenti']/trentino['Scuole studenti'], 2)

# Loading data about Trentino Population per age
pop_age = pd.read_csv(
    "../data/population/trentino_pop_per_age.csv", dtype="str")
pop_age.replace("San Giovanni Di Fassa-Sèn Jan",
                "San Giovanni Di Fassa", inplace=True)

pop_age['Anni'] = pop_age['Anni'].astype("int32")
pop_age['Popolazione'] = pop_age['Popolazione'].astype("int32")

# Grouping by municipality and keeping only data of people below 22 years
pop_age_tot = pop_age[(pop_age['Sesso'] == "totale") & (
    pop_age['Anni'] <= 20)].groupby(['Comune']).sum()
pop_age_tot.rename(columns={'Popolazione': 'Pop under 20'}, inplace=True)

pop_age_tot['Pop_mat'] = pop_age[(pop_age['Sesso'] == "totale") & (
    pop_age['Anni'] <= 6) & (pop_age['Anni'] >= 2)].groupby(['Comune'],).sum()['Popolazione']
pop_age_tot['Pop_ele'] = pop_age[(pop_age['Sesso'] == "totale") & (
    pop_age['Anni'] >= 6) & (pop_age['Anni'] <= 11)].groupby(['Comune'],).sum()['Popolazione']
pop_age_tot['Pop_med'] = pop_age[(pop_age['Sesso'] == "totale") & (
    pop_age['Anni'] >= 11) & (pop_age['Anni'] <= 14)].groupby(['Comune'],).sum()['Popolazione']
pop_age_tot['Pop_sup'] = pop_age[(pop_age['Sesso'] == "totale") & (
    pop_age['Anni'] >= 14) & (pop_age['Anni'] <= 20)].groupby(['Comune'],).sum()['Popolazione']
pop_age_tot['Popolazione'] = pop_age[pop_age['Sesso'] ==
                                     "totale"].groupby(['Comune']).sum()['Popolazione']
pop_age_tot.drop(['Anni'], axis=1, inplace=True)

trentino[['Pop under 20', 'Pop_mat', 'Pop_ele',
          'Pop_med', 'Pop_sup', 'Popolazione']] = pop_age_tot
trentino['Pop_stud/Pop_tot'] = round(trentino['Pop under 20'] /
                                     trentino['Popolazione'], 2)
trentino['Stud/Pop_stud'] = round(trentino['Studenti'] /
                                  trentino['Pop under 20'], 2)

trentino = trentino.fillna(np.nan)
trentino.to_file("../data/aggregated_data_per_municipality.geojson")

# %%
# Geodata with information to make popup in the map
geo_data = geojson.load(
    open("../data/aggregated_data_per_municipality.geojson", encoding="utf-8"))

# Creating an aggregated dataframe to use in further analysis
tn = gpd.GeoDataFrame.from_features(FeatureCollection(geo_data))
tn = tn.set_crs("EPSG:4326")
# %%
# MAP
m = folium.Map(location=[46.1, 11.2],
               zoom_start=9,
               tiles=None,
               overlay=False)

fg1 = folium.FeatureGroup(name='Studenti', overlay=False).add_to(m)
fg2 = folium.FeatureGroup(name='Popolazione', overlay=False).add_to(m)
fg3 = folium.FeatureGroup(name='Scuole', overlay=False).add_to(m)
fg4 = folium.FeatureGroup(name='Studenti/Popolazione', overlay=False).add_to(m)
fg5 = folium.FeatureGroup(
    name='Studenti/Popolazione under 20', overlay=False).add_to(m)
fg6 = folium.FeatureGroup(
    name='Media studenti per scuola', overlay=False).add_to(m)

# STUDENTS LAYER
bins = list(tn["Studenti"].quantile([0, 0.3, 0.7, 0.95, 0.99, 0.995, 1]))
# Add the first choropleth map layer to fg1
students = folium.Choropleth(
    geo_data=geo_data,
    data=tn,
    columns=['Comune', 'Studenti'],
    key_on='feature.properties.Comune',
    bins=bins,  # use the custom scale we created for legend
    fill_color='YlOrRd',
    nan_fill_color="White",  # Use white color if there is no data available for the county
    fill_opacity=0.7,
    line_opacity=0.2,
    highlight=True,
    overlay=True)

students.geojson.add_to(fg1)

folium.GeoJsonTooltip(fields=['Comune', 'Studenti', 'Classi',
                              'Scuole totali', 'Media stud per classe',
                              'Media stud per scuola'],
                      aliases=['Comune', 'Studenti', 'Classi',
                               'N. Scuole', 'Media studenti per classe',
                               'Media studenti per scuola']).add_to(students.geojson)

# POPOLATION LAYER
bins = list(tn["Popolazione"].quantile([0, 0.4, 0.7, 0.9, 0.97, 0.99, 1]))

pop = folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=tn,
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

folium.GeoJsonTooltip(fields=['Comune', 'Popolazione', 'Studenti', 'Scuole totali'],
                      aliases=['Comune', 'Popolazione', 'Studenti', 'N. Scuole']).add_to(pop.geojson)


# NUMBER OF SCHOOLS LAYER
bins = list(tn["Scuole totali"].quantile(
    [0, 0.6, 0.85, 0.95, 0.975, 0.993, 1]))
scu = folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=tn,
    columns=["Comune", "Scuole totali"],
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

folium.GeoJsonTooltip(fields=['Comune', 'Studenti', 'Classi',
                              'Scuole totali', 'Media stud per classe',
                              'Media stud per scuola', 'Popolazione'],
                      aliases=['Comune', 'Studenti', 'Classi',
                               'N. Scuole', 'Media studenti per classe',
                               'Media studenti per scuola', 'Popolazione']).add_to(scu.geojson)

bins = list(tn['Pop_stud/Pop_tot'].quantile([0, 0.4, 0.72, 0.95, 0.99, 1]))
den = folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=tn,
    columns=["Comune", 'Pop_stud/Pop_tot'],
    key_on="feature.properties.Comune",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Students over population",
    bins=bins,
    highlight=True,
    reset=True,
    nan_fill_color="White",
)
den.geojson.add_to(fg4)

folium.GeoJsonTooltip(fields=['Comune', 'Studenti', 'Pop_stud/Pop_tot',
                              'Scuole totali', 'Media stud per classe',
                              'Media stud per scuola', 'Popolazione'],
                      aliases=['Comune', 'Studenti', 'Studenti/Popolazione',
                               'N. Scuole', 'Media studenti per classe',
                               'Media studenti per scuola', 'Popolazione']).add_to(den.geojson)

bins = list(
    tn["Stud/Pop_stud"].quantile([0, 0.25, 0.50, 0.75, 0.90, 0.945, 1]))
den2 = folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=tn,
    columns=["Comune", "Stud/Pop_stud"],
    key_on="feature.properties.Comune",
    fill_color="RdBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Students over population",
    bins=bins,
    highlight=True,
    reset=True,
    nan_fill_color="White",
)
den2.geojson.add_to(fg5)
folium.GeoJsonTooltip(fields=['Comune', 'Studenti', 'Pop_stud/Pop_tot',
                              'Scuole totali', 'Pop under 20', 'Stud/Pop_stud'],
                      aliases=['Comune', 'Studenti', 'Studenti/Popolazione',
                               'N. Scuole', 'Popolazione (<22 anni)', 'Densità di studenti su popolazione studentesca']).add_to(den2.geojson)

# MEDIA STUDENTI PER SCUOLA
bins = list(
    tn["Media stud per scuola"].quantile([0, 0.25, 0.50, 0.75, 0.90, 0.945, 1]))
med = folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=tn,
    columns=["Comune", "Media stud per scuola"],
    key_on="feature.properties.Comune",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    bins=bins,
    highlight=True,
    reset=True,
    nan_fill_color="White",
)
med.geojson.add_to(fg6)
folium.GeoJsonTooltip(fields=['Comune', 'Studenti', 'Media stud per scuola'],
                      aliases=['Comune', 'Studenti', 'Media studenti per scuola']).add_to(med.geojson)


folium.TileLayer('cartodbpositron', overlay=True,
                 control=False, name="Light Mode").add_to(m)
folium.LayerControl(collapsed=False).add_to(m)
m
#m.save("../viz/students_population.html")
# %%

