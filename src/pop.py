# %%
import pandas as pd

# ISTAT Trentino Population, filtering total data
# about the Region and the province
df = pd.read_csv("../data/population/ISTAT_Trentino_population.csv", dtype="str")
df = df[(df['ITTER107'] != "ITD20") & (df['ITTER107'] != "ITD2") & (df['ETA1'] != "TOTAL") & (df['Stato civile'] == "totale")]

# %%
# Removing unnecessary columns
df.drop(['Flag Codes', 'Flags',
              'Seleziona periodo', "TIPO_DATO15", 'STATCIV2','Stato civile',
              "Tipo di indicatore demografico", 'TIME', 'SEXISTAT1', 'ETA1'], axis=1, inplace=True)

# %%
# Renaming columns
df.rename(columns = {
    'ITTER107': 'Id',
    'Territorio': 'Comune',
    'Età':'Anni',
    'Value':'Popolazione'
}, inplace=True)

# Converting years and population to int
df['Anni'] = [int(x.split(" ")[0]) for x in df['Anni']]
df['Popolazione'] = df['Popolazione'].astype("int32")

# Converting Municipality to Title
df['Comune'] = [x.title() for x in df['Comune']]
#%%
# Saving the dataframe as csv
df.to_csv("../data/population/trentino_pop_per_age.csv", index=False)

# Pick total population per each municipality
df = df.groupby(['Id','Comune','Sesso'], as_index = False).sum()[['Id','Comune','Sesso', 'Popolazione']]
# Saving dataframe as csv
df.to_csv("../data/population/trentino_total_pop.csv", index=False)

