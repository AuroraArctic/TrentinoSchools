# %%
import folium
import pandas as pd
import geopandas as gpd
from folium.plugins import MarkerCluster
import branca
# %%
schools = gpd.read_file("../data/trentino/schools.geojson")
schools[['Istituto Principale', 'Scuola', 'Comune']] = schools[[
    'Istituto Principale', 'Scuola', 'Comune']].applymap(lambda x: x.title())
# %%


def generate_popup(row, columns):
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
        """.format(row['Scuola'])
        
    # Iterate over columns
    for c in ['Istituto Principale', 'Tipo Istituto', 'Tipo Gestione',
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


# CLUSTERING MAP
map = folium.Map(location=[46.0904, 11.14], zoom_start=10, tiles=None)

# Adding layers
folium.TileLayer('openstreetmap', name="OpenStreetMap").add_to(map)
folium.TileLayer("Stamen Watercolor", name="Watercolor").add_to(map)
folium.TileLayer("Cartodb dark_matter", name="Dark").add_to(map)
folium.TileLayer("cartodbpositron", name="Light").add_to(map)


# Adding cluster of points
fg = folium.FeatureGroup(name='Schools', show=True)
cluster = MarkerCluster().add_to(fg)
map.add_child(fg)

# Tile Layer control
folium.LayerControl().add_to(map)

# Adding points to clusters
for p in schools.iterrows():
    text = generate_popup(p[1], schools.columns)
    iframe = branca.element.IFrame(html=text, width=400, height=280)
    popup = folium.Popup(folium.Html(text, script=True), max_width=400)
    folium.Marker([p[1]['geometry'].y, p[1]['geometry'].x],
                  icon=folium.map.Icon(prefix='fa',
                                       icon='graduation-cap'),
                  popup=popup,
                  tooltip=p[1]['Scuola']).add_to(cluster)
map
#map.save('../viz/schools_cluster.html')

# %%
