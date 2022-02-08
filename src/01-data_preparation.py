# %%
# Setup
import json
import pandas as pd
import numpy as np

# %%
# VIVOSCUOLA DATASET
# Import dataset with professional schools
vivo = pd.read_csv("../data/vivoscuola.csv", sep=";")

# %%
# Remove Istituti Comprensivi
vivo = vivo[~vivo['Scuola'].isnull()]

# %%
# Infer school type by the complete name


def insert_school_type(df, name_index, ist_index):
    type = []
    for i in range(len(df)):
        s = df.iloc[i, name_index].lower()
        t = ""
        if ("asilo" in s) or ("scuola materna" in s) or ("scuola dell'infanzia" in s):
            t = "Scuola dell'Infanzia"
        elif ("scuola primaria" in s) or ("primaria" in s):
            t = "Scuola Primaria"
        elif ("scuola secondaria di primo " in s) or ("secondaria i" in s):
            t = "Scuola Secondaria di Primo Grado"
        elif ("scuola secondaria di secondo " in s) or ("liceo" in s) or ("istituto tecnico" in s) or ("istituto professionale" in s):
            t = "Scuola Secondaria di Secondo Grado"
        elif ("formazione professionale" in s) or ("formazione professionale" in df.iloc[i, ist_index].lower()):
            t = "Formazione professionale"
        elif "educazione per adulti" in s:
            t = "Educazione per adulti"
        else:
            t = np.nan
        type.append(t)
    df['Tipo Istituto'] = type


insert_school_type(vivo, 1, 0)
# %%
# Map Public and Private school into short version
type = []
for x in vivo['Tipo Gestione']:
    if "Paritaria" in x:
        type.append("Paritaria")
    else:
        type.append("Statale")

vivo['Tipo Gestione'] = type

# %%
# Select the columns
vivo = vivo[['Istituto Principale', 'Scuola', 'Tipo Istituto',
             'Tipo Gestione', 'Indirizzo', 'Comune', 'Telefono',
             'Fax', 'Email istituto', 'Email segreteria', 'Sito web', 'Codice MIUR']]

vivo.rename(columns={
    'Istituto Principale': 'Istituto',
    'Scuola': 'Nome',
    'Tipo Gestione': 'Gestione'
}, inplace=True)

# %%
# Separate CAP and Address
vivo['CAP'] = [x[-5:] for x in vivo['Indirizzo']]
vivo['Indirizzo'] = [x[:-6] for x in vivo['Indirizzo']]

# %%
vivo.reset_index(drop=True, inplace=True)
vivo.to_csv("../data/trentino/vivoscuole.csv", index=False)
# %%
# Open JSON as file to not misinterpret the id
import json
with open("../data/aprilascuola.json") as f:
    json = json.load(f)

codes = {}
for school in json:
    codes[school['idobj']] = school['codiceProvinciale']
# APRILASCUOLA DATASET
apri = pd.read_json(
    "https://aprilascuola.provincia.tn.it/sei//api/istituzioneScolastica/istituzioni/ricerca")

apri['codiceProvinciale'] = [codes[x] for x in apri['idobj']]
apri.drop(['idobj'], axis=1, inplace=True)

apri.rename(columns={
    'idPadre': 'Id Istituto',
    'codiceProvinciale': 'Id',
    'codiceMiur': 'Codice MIUR',
    'denominazioneUfficiale': 'Nome',
    'latitudeY': 'lat',
    'longitudeX': 'lon',
    'istituzionePadre': 'Istituto',
    'indirizzo': 'Indirizzo',
    'email': 'Email',
    'telefono': 'Telefono',
    'comune': 'Comune'
}, inplace=True)
# %%
apri['Id Istituto'] = [x['codiceProvinciale'] for x in apri['Istituto']]
apri['Istituto'] = [x['denominazioneUfficiale'] for x in apri['Istituto']]
# %%
apri[['Istituto', 'Nome', 'Comune']] = apri[['Istituto', 'Nome', 'Comune']
                                            ].applymap(lambda s: s.title() if s != None else None)
vivo[['Istituto', 'Nome', 'Comune']] = vivo[['Istituto', 'Nome', 'Comune']
                                            ].applymap(lambda s: s.title() if s != None else None)

# %%
apri = apri[(~apri['Id Istituto'].isna()) & (apri['Nome'] != "Educazione Libera Per Adulti")]


insert_school_type(apri, 3, 9)
# %%
# Remove Istituti Comprensivi
# %%
common = pd.merge(apri, vivo, how="inner", on=['Nome', 'Istituto'])
# %%
materne = vivo[vivo['Tipo Istituto'] == "Scuola dell'Infanzia"]
non_mat = vivo[vivo['Tipo Istituto'] != "Scuola dell'Infanzia"]

len(materne)
len(non_mat)


common = pd.merge(apri, non_mat, how="inner", on=['Nome', 'Istituto'])
# %%
# Check if all apri rows are inside the joined dataframe
for i in apri['Id'].index:
    if apri['Id'][i] not in list(common['Id']):
        print(i)

# %%
# Check if all vivo rows are inside the joined dataframe
indexes = []
for i in non_mat['Nome'].index:
    if non_mat['Nome'][i] not in list(common['Nome']):
        indexes.append(i)

# Clearly not... therefore, let's check these names with a right join, erasing the rows where the id is available
# %%
for x in list(missing_vivo.index):
    if missing_vivo.loc[x]['Nome'] not in apri['Nome']:
        print(x)

# %%
# TASK: Add the remaining rows in non_mat inside common

# 1. Adjust columns in common
# MIUR is equal in most of the rows, the remaining ones are None in apri and present in vivo
common[common['Codice MIUR_x'] != common['Codice MIUR_y']]

# Keep vivoscuola addresses and contact information, since they are well formatted and complete
common.rename(columns={
    'Indirizzo_y': 'Indirizzo',
    'Telefono_y': 'Telefono',
    'Comune_y': 'Comune',
    'Tipo Istituto_y': 'Tipo Istituto',
    'Codice MIUR_y': 'Codice MIUR'}, inplace=True)
# %%
common.drop(['Codice MIUR_x', 'Indirizzo_x', 'Telefono_x', 'Email',
             'Comune_x', 'Tipo Istituto_x', ], axis=1, inplace=True)
# %%
# 2. Add the remaining missing schools in Vivo
common = pd.concat([common,
          non_mat[(non_mat['Nome'].isin(missing_vivo['Nome'])) &
        (non_mat['Indirizzo'].isin(missing_vivo['Indirizzo_y'])) &
        (non_mat['Istituto'].isin(missing_vivo['Istituto']))]], axis=0, ignore_index=True)
# %%
# Adding scuole materne to the dataset, inserting None where information is missing
common=pd.concat([common, materne], axis=0, ignore_index=True)

#%%
# There are some duplicates
common[common.duplicated(subset= ['Nome','Istituto','Comune','Indirizzo'], keep=False)]
#%%
common.loc[(common['Nome'] == "Scuola Primaria Cavedine") & 
           (common['Id'].isna()), ['Codice MIUR','Telefono', 'Indirizzo', 'lat','lon']] = ['TNEE84407R', ' 0461/568892', 'Via 25 Aprile, 7', 45.99417, 10.97179]

#%% 
# Recheck
common[common.duplicated(subset= ['Nome','Istituto','Comune','Indirizzo'], keep=False)]

#%%
common.to_pickle("../data/Trentino/scuole.pkl")
