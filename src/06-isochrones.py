# %%
# Libraries
from shapely import geometry
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
from numpy import size
import osmnx as ox
import folium
from descartes import PolygonPatch
from pyparsing import alphas
from shapely.geometry import Point, LineString, Polygon
# %%
# Reading school files
schools = gpd.read_file(
    "../data/Trentino/schools/schools.geojson", geometry="geometry")
# %%
# LET'S TRY WITH THE FIRST SCHOOL AND THEN GENERALIZE
# Configure the place, network type, trip times, and travel speed
place = schools.loc[0, 'geometry']
network_type = 'walk'
# dist = [1000, 2000]
# TODO: Setup max distance to look at when computing the graph, since there's differences
# between walking and bycicling
trip_times = [5, 10, 15, 20, 25]  # in minutes
colors = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']
travel_speed = 4.5  # walking speed in km/hour
# %%

# Get entire walking network
G = ox.graph_from_point((place.y, place.x), network_type=network_type)
# Plot the walking network adding the school (starting point)
m = ox.plot_graph_folium(G, weight=2, color="cornflowerblue",
                         kwargs={'opacity': 0.5}, tiles="openstreetmap")
m.add_child(folium.Marker((place.y, place.x)))

# %%
# GET THE CENTROID OF THE NETWORK (THE CLOSEST TO THE STARTING POINT)
# Convert the graph to geodataframe
gdf_nodes = ox.graph_to_gdfs(G, edges=False)
center_node = ox.nearest_nodes(G, place.x, place.y)
gdf_nodes.loc[center_node]
G = ox.project_graph(G, to_crs="EPSG:4326")

# %%
# add an edge attribute for time in minutes required to traverse each edge
meters_per_minute = travel_speed * 1000 / 60  # km per hour to m per minute
for u, v, k, data in G.edges(data=True, keys=True):
    data['time'] = data['length'] / meters_per_minute
# %%
# Returns route map with colour depending on the reach time


def get_folium_route_time_distance_map(G, place, trip_times, colors):

    # color the nodes according to isochrone then plot the street network
    map = folium.Map(location=(place.y, place.x),
                     tiles='cartodb positron')
    for trip_time, color in zip(sorted(trip_times, reverse=True), colors):
        subgraph = nx.ego_graph(
            G, center_node, radius=trip_time, distance='time')
        ox.plot_graph_folium(subgraph, graph_map=map,
                             color=color)
    map.fit_bounds(map.get_bounds())
    return map


get_folium_route_time_distance_map(G, place, trip_times, colors)

# %%
# make the isochrone polygons
isochrone_polys = []
for trip_time in sorted(trip_times, reverse=True):
    subgraph = nx.ego_graph(G, center_node, radius=trip_time, distance='time')
    node_points = [Point((data['x'], data['y']))
                   for node, data in subgraph.nodes(data=True)]
    bounding_poly = gpd.GeoSeries(node_points).unary_union.convex_hull
    isochrone_polys.append(bounding_poly)

# plot the network then add isochrones as colored descartes polygon patches
fig, ax = ox.plot_graph(G, show=False, close=False, edge_color='#999999', edge_alpha=0.2,
                        node_size=0, bgcolor='k')
for polygon, fc in zip(isochrone_polys, iso_colors):
    patch = PolygonPatch(polygon, fc=fc, ec='none', alpha=0.6, zorder=-1)
    ax.add_patch(patch)
plt.show()

# %%
map = folium.Map(location=(place.y, place.x),
                     tiles='cartodb positron')

subgraph = nx.ego_graph(G, center_node, radius=trip_times[1], distance='time')

node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
nodes_gdf = gpd.GeoDataFrame({'id': subgraph.nodes()}, geometry=node_points)
nodes_gdf = nodes_gdf.set_index('id')
edge_lines = []
for n_fr, n_to in subgraph.edges():
    f = nodes_gdf.loc[n_fr].geometry # source node
    t = nodes_gdf.loc[n_to].geometry # dest node
    edge_lookup = G.get_edge_data(n_fr, n_to)[0].get(
        'geometry',  LineString([f, t]))
    edge_lines.append(edge_lookup)

n = nodes_gdf.buffer(50).geometry
e = gpd.GeoSeries(edge_lines).buffer(25).geometry
all_gs = list(n) + list(e)
new_iso = gpd.GeoSeries(all_gs).unary_union
folium.Polygon(new_iso.exterior.coords.xy).add_to(map)


# %%


def make_iso_polys(G, edge_buff=25, node_buff=50, infill=False):
    isochrone_polys = []
    for trip_time in sorted(trip_times, reverse=True):
        subgraph = nx.ego_graph(
            G, center_node, radius=trip_time, distance='time')

        node_points = [Point((data['x'], data['y']))
                       for node, data in subgraph.nodes(data=True)]
        nodes_gdf = gpd.GeoDataFrame(
            {'id': subgraph.nodes()}, geometry=node_points)
        nodes_gdf = nodes_gdf.set_index('id')

        edge_lines = []
        for n_fr, n_to in subgraph.edges():
            f = nodes_gdf.loc[n_fr].geometry
            t = nodes_gdf.loc[n_to].geometry
            edge_lookup = G.get_edge_data(n_fr, n_to)[0].get(
                'geometry',  LineString([f, t]))
            edge_lines.append(edge_lookup)

        n = nodes_gdf.buffer(node_buff).geometry
        e = gpd.GeoSeries(edge_lines).buffer(edge_buff).geometry
        all_gs = list(n) + list(e)
        new_iso = gpd.GeoSeries(all_gs).unary_union

        # # try to fill in surrounded areas so shapes will appear solid and blocks without white space inside them
        # if infill:
        #     new_iso = Polygon(new_iso.exterior)
        isochrone_polys.append(new_iso)
    return isochrone_polys


isochrone_polys = make_iso_polys(G, edge_buff=25, node_buff=0, infill=True)


fig, ax = ox.plot_graph(G, show=False, close=False, edge_color='#999999', edge_alpha=0.2,
                        node_size=0, bgcolor='k')
for polygon, fc in zip(isochrone_polys, colors):
    patch = PolygonPatch(polygon, fc=fc, ec='none', alpha=0.6, zorder=-1)
    ax.add_patch(patch)
plt.show()
# %%
