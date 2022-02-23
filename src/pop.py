# %%
import pandas as pd

df = pd.read_csv("../data/population/pop_per_age_trentino.csv", dtype="str")
df = df[(df['ITTER107'] != "ITD20") & (df['ITTER107'] != "ITD2") & (df['ETA1'] != "TOTAL") & (df['Stato civile'] == "totale")]

# %%
df.drop(['Flag Codes', 'Flags',
              'Seleziona periodo', "TIPO_DATO15", 'STATCIV2','Stato civile',
              "Tipo di indicatore demografico", 'TIME', 'SEXISTAT1', 'ETA1'], axis=1, inplace=True)

# %%
df.rename(columns = {
    'ITTER107': 'Id',
    'Territorio': 'Comune',
    'Età':'Anni',
    'Value':'Popolazione'
}, inplace=True)

df['Anni'] = [int(x.split(" ")[0]) for x in df['Anni']]
df['Popolazione'] = df['Popolazione'].astype("int32")
df['Comune'] = [x.title() for x in df['Comune']]
#%%
df.to_csv("../data/population/trentino_pop_per_age.csv", index=False)

#%%
# Pick total population per each municipality
df = df.groupby(['Id','Comune','Sesso'], as_index = False).sum()[['Id','Comune','Sesso', 'Popolazione']]
df.to_csv("../data/population/total_trentino_pop.csv", index=False)
