# %%
import folium
import pandas as pd
import geopandas as gpd
from folium.plugins import MarkerCluster
import branca
# %%
schools = gpd.read_file("../data/trentino/schools/schools.geojson")
schools[['Istituto', 'Nome', 'Comune']] = schools[[
    'Istituto', 'Nome', 'Comune']].applymap(lambda x: x.title())
# %%


def generate_popup(row):
    # Open the HTML popup table
    text = """
        <!DOCTYPE html>
        <html>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,400;0,500;1,300;1,400;1,700&display=swap');
            </style>
            <h4 style="font-family: 'Roboto', sans-serif;">{}</h4>
            <table style="height: 150px; width: 350px; font-family: 'Roboto', sans-serif;">
            <tbody>
        """.format(row['Nome'])

    # Iterate over columns
    for c in ['Istituto', 'Tipo Istituto', 'Gestione',
              'Indirizzo', 'Comune', 'CAP', 'Telefono', 'Fax',
              'Email istituto', 'Email segreteria', 'Sito web']:

        # If the value is Null, don't insert it in the table
        if row[c] != None:
            if c in ['Sito web']:
                # Insertion of clickable links
                text = text + """
                <tr>
                    <td><b>{}</b></td>
                    <td><a href = "https://{}" target="_blank">{}</a></td>""".format(c, row[c], row[c]) + """
                </tr>
                """
            elif c in ['Telefono', 'Fax']:
                # Insertion of clickable links
                text = text + """
                <tr>
                    <td><b>{}</b></td>
                    <td><a href = "tel:{}" target="_blank">{}</a></td>""".format(c, row[c], row[c]) + """
                </tr>
                """
            elif 'Email' in c:
                # Insertion of clickable links
                text = text + """
                <tr>
                    <td><b>{}</b></td>
                    <td><a href = "mailto:{}" target="_blank">{}</a></td>""".format(c, row[c], row[c]) + """
                </tr>
                """
            else:  # No need for links
                text = text + """
                    <tr>
                        <td><b>{}</b></td>
                        <td>{}</td>""".format(c, row[c]) + """
                    </tr>
                """

    # Close the table
    text = text + """
            </tbody>
            </table>
        </html>
        """
    return text

#%%
# Importing Trentino GeoData
url = 'https://github.com/napo/geospatial_course_unitn/blob/master/data/istat/istat_administrative_units_generalized_2021.gpkg?raw=true'
trentino = gpd.read_file(url, layer="municipalities")
trentino = trentino[trentino['COD_PROV'] == 22]
trentino = trentino.to_crs(4326)
trentino = trentino.dissolve(by="COD_PROV")
# %%
# CLUSTERING MAP
map = folium.Map(location=[46.0904, 11.14], zoom_start=9, tiles=None)

# Adding layers
folium.TileLayer("cartodbpositron", name="Light").add_to(map)
folium.TileLayer("Cartodb dark_matter", name="Dark").add_to(map)
folium.TileLayer('openstreetmap', name="OpenStreetMap").add_to(map)

# Adding Trentino Boundary
style = {'fillColor': 'rgba(255,255,255,0)', 'color': '#DD696D'}
tn = folium.FeatureGroup(name='Trentino', show=True)
folium.GeoJson(trentino.to_json(), 
               style_function=lambda x:style).add_to(tn)
map.add_child(tn)


# Adding cluster of points
fg = folium.FeatureGroup(name='Schools', show=True)
cluster = MarkerCluster(icon_create_function="""
    function (cluster) {    
        var childCount = cluster.getChildCount();  
        if (childCount < 20) {  
            c = '#FEDB71'
        } else if (childCount < 40) {  
            c = '#FEB85D' 
        } else if (childCount < 100) {  
            c = '#EE8A59';  
        } else { 
            c = '#DD696D'  
        }    
        return new L.DivIcon({ html: '<div style="background-color:'+c+'"><span>' + childCount + '</span></div>', className: 'marker-cluster', iconSize: new L.Point(40, 40) });

  }
  """).add_to(fg)
map.add_child(fg)

# Tile Layer control
folium.LayerControl().add_to(map)

# Adding points to clusters
for p in schools.iterrows():
    text = generate_popup(p[1])
    iframe = branca.element.IFrame(html=text, width=400, height=280)
    popup = folium.Popup(folium.Html(text, script=True), max_width=400)
    folium.Marker([p[1]['geometry'].y, p[1]['geometry'].x],
                  icon=folium.map.Icon(prefix='fa',
                                       icon='graduation-cap',
                                       color="lightred"),
                  popup=popup,
                  name = p[1]['Nome'],
                  tooltip=p[1]['Nome']).add_to(cluster)
    
#Add search bar
from folium.plugins import Search
servicesearch = Search(
    layer=cluster,
    search_label='name',
    search_zoom=18,
    placeholder='Search for a school',
    collapsed=True).add_to(map)

map.save('../viz/schools_cluster.html')

# %%
map