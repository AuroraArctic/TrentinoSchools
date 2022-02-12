#%%
import pandas as pd

df = pd.read_csv("../data/population/ItalianPopulation2021.csv")
#%%
df = df[df['ITTER107'].isin(trentino['ITTER107'])].drop(['Flag Codes', 'Flags',
                                                    'Seleziona periodo',"TIPO_DATO15",
                                                    "Tipo di indicatore demografico", 'TIME'], axis=1)

#%%
df.to_csv("../data/population/trentino_pop_per_age.csv", index=False)

#%%
df_new = pd.read_csv("../data/population/ItalianPopulation2021_2.csv")

df_new = df_new[['ITTER107','Territorio','Sesso','Value']]
df_new = df_new[df_new['ITTER107'].isin(trentino['ITTER107'])]

df_new.to_csv("../data/population/total_trentino_pop.csv", index=False)