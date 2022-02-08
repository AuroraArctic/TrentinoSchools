#%%
import ipywidgets as widgets
import geopandas as gpd
# %%
# Reading school files
schools = gpd.read_file("../data/Trentino/schools/schools.geojson", geometry="geometry")
#%%

def print_me(x):
    print(x)
    
select = widgets.Combobox(
    value=schools['Nome'][0],
    placeholder='Scegli una scuola',
    options=list(schools['Nome']),
    description='Scuola:',
    ensure_option=True,
    disabled=False,
    command= lambda x: print_me(x)
)
#%%
select