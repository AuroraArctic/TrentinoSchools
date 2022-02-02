# %%
# Setup
import pandas as pd
import numpy as np

# %%
# Import dataset
df = pd.read_csv("../data/trentino/vivoscuola_dataset.csv", sep = ";")

# %%
# Remove Istituti Comprensivi
df = df[~df['Scuola'].isnull()]

# %%
# Infer school type by the complete name
type = []
for i in range(len(df)):
    s = df.iloc[i, 1].lower()
    t = ""
    if ("asilo" in s) or ("scuola materna" in s):
        t = "Scuola Materna"
    elif "scuola dell'infanzia" in s:
        t = "Scuola dell'infanzia"
    elif ("scuola primaria" in s) or ("primaria" in s):
        t = "Scuola Primaria"
    elif ("scuola secondaria di primo " in s) or ("secondaria i" in s):
        t = "Scuola Secondaria di Primo Grado"
    elif ("scuola secondaria di secondo " in s) or ("liceo" in s) or ("istituto tecnico" in s) or ("istituto professionale" in s):
        t = "Scuola Secondaria di Secondo Grado"
    elif ("formazione professionale" in s) or ("formazione professionale" in df.iloc[i,0].lower()):
        t = "Formazione professionale"
    elif "educazione per adulti" in s:
        t = "Formazione per adulti" 
    else:
        t = np.nan
    type.append(t)
df['Tipo Istituto'] = type

# %%
# Map Public and Private school into short version
type = []
for x in df['Tipo Gestione']:
    if "Paritaria" in x:
        type.append("Paritaria")
    else:
        type.append("Statale")
        
df['Tipo Gestione'] = type

# %%
# Select the columns
df = df[['Istituto Principale', 'Scuola', 'Tipo Istituto', 
         'Tipo Gestione', 'Indirizzo','Comune', 'Telefono', 
         'Fax', 'Email istituto', 'Email segreteria', 'Sito web', 'Codice MIUR']]

# %%
# Separate CAP and Address
df['CAP'] = [x[-5:] for x in df['Indirizzo']]
df['Indirizzo'] = [x[:-6] for x in df['Indirizzo']]

#%%
df.reset_index(drop=True, inplace=True)
df.to_csv("../data/trentino/scuole.csv", index=False)
#%%