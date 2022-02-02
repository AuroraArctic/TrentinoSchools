#%%
import codecs
import pandas as pd
import geopandas as gpd

#%%
studenti = pd.read_csv("../data/StudentiStatali.csv")
studenti.drop("ANNOSCOLASTICO",axis=1, inplace=True)
#%%
scuole = pd.read_csv("../data/ScuoleStataliTrentino_2021_22.csv")
#%%

pd.merge(studenti.loc[studenti['CODICESCUOLA'].str.contains('TN', na=False)], scuole, left_on="CODICESCUOLA", right_on='Codice MIUR')

#%%
codes = set(scuole['Codice MIUR'])
codes.remove(None)

#%%

studenti[studenti['CODICESCUOLA'].isin(codes)]
