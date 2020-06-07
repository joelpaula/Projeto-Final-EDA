import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from haversine import haversine, Unit
from collections import namedtuple
from Graph import Graph, Edge #, Vertex
from TrainGraph import Station, Connection, peak_type, TrainGraph



df_stations = pd.read_csv("LondonTube/london.stations.txt")
df_stations.head()

df_connections = pd.read_csv("LondonTube/london.connections.txt")
df_connections.head()


# gr = Graph()

# train_stations = {} 
# for ts in df_stations.itertuples():
#     s = Station(id=ts.id,
#                 name=ts.name,
#                 latitude=ts.latitude,
#                 longitude=ts.longitude)
#     gr.insert_vertex(s)
#     train_stations[s.id] = s

# connections = {}
# for cn in df_connections.itertuples():
#     key1 = (cn.station1, cn.station2)
#     key2 = (cn.station2, cn.station1)
#     if key1 not in connections.keys() and key2 not in connections.keys():
#         c = Edge(train_stations[cn.station1], train_stations[cn.station2])
#         connections[key1] = c

# for edge in connections.values():
#     gr.insert_edge(edge)

# print("Stations: ", gr.vertex_count())
# print("Connections: ", gr.edge_count())

# plt.rcParams['figure.dpi'] = 150

# from math import cos, radians
# from statistics import mean

# def plot_edges(lst, color="xkcd:royal blue", marker="o", markersize=1, linewidthwidth=0.5, showgraph=False):
#     for e in lst:
#         xs = [e.origin.longitude, e.destination.longitude]
#         ys = [e.origin.latitude, e.destination.latitude]
#         plt.plot(xs, ys, c=color, marker=marker, markersize=markersize, linewidth=linewidthwidth)

#     if showgraph:
#         # Mercator projection aspect ratio approximation at this central latitude 
#         mercator_aspect_ratio = 1/cos(radians(mean(ys)))
#         plt.axes().set_aspect(mercator_aspect_ratio)

#         plt.axis('off')
#         plt.show()

# plot_edges(gr.edges(), showgraph=True)

# m_L = np.zeros([gr.vertex_count(), gr.vertex_count()], int)
# vertices = list(gr.vertices())

# for i in range(m_L.shape[0]):
#     for j in range(m_L.shape[1]):
#         if i == j:
#             m_L[i, j] = gr.degree(vertices[i])
#         elif gr.get_edge(vertices[i], vertices[j]):
#             m_L[i, j] = -1

# # Get EigenVector
# eigenvalues, v = np.linalg.eig(m_L)
# eigen_index = np.argsort(eigenvalues)[1]
# ev2nd = v[:, eigen_index]

# g1 = Graph()
# g2 = Graph()

# for i in range(ev2nd.size):
#     if ev2nd[i] < 0:
#         g1.insert_vertex(vertices[i])
#     else:
#         g2.insert_vertex(vertices[i])

# g1_count = g1.vertex_count()
# g2_count = g2.vertex_count()

# print("G1: ", g1_count, "stations")
# print("G2: ", g2_count, "stations")

# # Edges with one vertex/station in g1 and another one in g2
# e_to_cut = []
# for edge in gr.edges():
#     if all(ver in g1.vertices() for ver in edge.endpoints()):
#         g1.insert_edge(edge)
#     elif all(ver in g2.vertices() for ver in edge.endpoints()):
#         g2.insert_edge(edge)
#     else:
#         e_to_cut.append(edge)

# print("Number of connections in G1:", g1.edge_count())
# print("Number of connections in G2:", g2.edge_count())
# print("Number of cuts:", len(e_to_cut))
# print("Minimum Cut Ratio:", len(e_to_cut) / (g1_count * g2_count))

# plot_edges(g1.edges(), color="xkcd:azure")
# plot_edges(g2.edges(), color="xkcd:aquamarine")
# plot_edges(e_to_cut, color="xkcd:coral", marker="+", markersize=0.9, showgraph=True)

# for edge in e_to_cut:
#     print(edge)



# PARTE II

df_interstations = pd.read_csv("LondonTube/interstation.csv", names=["line", "from_id", "to_id", "distance", "off_peak", "am_peak", "inter_peak"], skiprows=1)
print("Distâncias e tempos entre estações:", len(df_interstations.index))
df_lines = pd.read_csv("LondonTube/london.lines.txt")
print("Linhas:", len(df_lines.index))

TrainLine = namedtuple("TrainLine", "id, name, color, stripe_color")
london_lines = {}
for l in df_lines.itertuples():
    london_lines[l.line] = TrainLine(l.line, l.name, l.colour, l.stripe)
print(london_lines)


# Criar o grafo pesado e dirigido:
subway_wgr = TrainGraph()

# read train stations    
train_stations = {} 
for ts in df_stations.itertuples():
    s = Station(id=ts.id,
                name=ts.name,
                latitude=ts.latitude,
                longitude=ts.longitude)
    subway_wgr.insert_vertex(s)
    train_stations[s.id] = s

# now read all the inter stations from file and add them as connections to the intermediate dictionary 
connections = {}
for cn in df_interstations.itertuples():
    key = (cn.from_id, cn.to_id)
    if key not in connections.keys():
        c = Connection(train_stations[cn.from_id], train_stations[cn.to_id], 
            cn.distance, cn.off_peak, cn.am_peak, cn.inter_peak, cn.line)
        connections[key] = c
    else:
        connections[key].add_line(cn.line) 

# now read all the connections from file and add them to the intermediate dictionary
for cn in df_connections.itertuples():
    key = (cn.station1, cn.station2)
    if key in connections.keys():
        c = connections[key]
        if cn.line not in c.lines:
            # connection already exists - add the line
            c.add_line(cn.line)
    else:
        c = Connection(train_stations[cn.station1], train_stations[cn.station2], 0, 
            cn.time, cn.time, cn.time, cn.line)
        connections[key]= c

# Now check for any missing opposite direction edges
for cn in connections.values():
    # correct non existing distance/time
    if cn.distance_km == 0:
        distance_kms = haversine(cn.origin.geo_ref(), cn.destination.geo_ref())
        cn.distance_km = distance_kms
        if cn.get_time(peak_type.OFF_PEAK, cn.lines) == 0:
            time_mins = round(distance_kms * 2, 4) # distance x 60mins / 30km
            cn.set_time(peak_type.OFF_PEAK, time_mins)
            cn.set_time(peak_type.AM_PEAK, time_mins)
            cn.set_time(peak_type.INTER_PEAK, time_mins)
    # check opposite exists or create otherwise
    key_opposite = (cn.destination.id, cn.origin.id)
    if not key_opposite in connections.keys():
        line = list(cn.lines)[0]
        c = Connection(cn.destination, cn.origin, cn.distance_km, 
            cn.get_time(peak_type.OFF_PEAK, cn.lines), cn.get_time(peak_type.AM_PEAK, cn.lines), 
            cn.get_time(peak_type.INTER_PEAK, cn.lines), line)
        for line in cn.lines:
            c.add_line(line)
        subway_wgr.insert_edge(c)

# Insert edges into graph
for edge in connections.values():
    subway_wgr.insert_edge(edge)

print("Stations: ", subway_wgr.vertex_count())
print("Connections: ", subway_wgr.edge_count())

# Próximo passo: pesquisar distancia entre Amersham (id 6) e Wimbledon (id 299).

# Próximo passo: pesquisar distancia entre Amersham (id 6) e Wimbledon (id 299).
# Baker street = 11; Green Park = 107
# Amersham = 6; South Harrow = 235
# Uxbridge = 271; South Harrow = 235
# Baker street = 11; Notting Hill Gate = 186
from_station = 6
to_station = 299
travel_time, travel_path = subway_wgr.shortest_path(train_stations[from_station], train_stations[to_station], peak_type.AM_PEAK)
#cl = shortest_path(weighted_gr, train_stations[6], train_stations[299], peak_type.AM_PEAK)
# cl = shortest_path(weighted_gr, train_stations[6], train_stations[235], peak_type.AM_PEAK)
print("From ", train_stations[from_station], "to", train_stations[to_station], "AM Peak time:", travel_time, "Path:", travel_path )
#print(cl)

# # Bibliografia
# Demmel, J. (2009). CS267 lecture 13 – Graph Partitioning. Obtido em 25 de Maio de 2020, de U.C. Berkeley CS267/EngC233: https://people.eecs.berkeley.edu/~demmel/cs267_Spr09/Lectures/lecture13_partition_jwd09.ppt
# 
# Gonina, K., Ray, S., & Su, B.-Y. (2020). _Graph Partitioning_. Obtido em 25 de Maio de 2020, de Berkeley Our Pattern Language: https://patterns.eecs.berkeley.edu/?page_id=571
# 
# Kabelíková, P. (2006). _Graph Partitioning Using Spectral Methods_. (Tese). VSB - Technical University of Ostrava, República Checa. Obtido em 25 de Maio de 2020: https://pdfs.semanticscholar.org/ab34/1258fbab7b2e9a719c6bbeb96fc204356a82.pdf
# 
# Wikipédia. (2019). _Partição de grafos_. Obtido de Wikipédia: https://pt.wikipedia.org/wiki/Parti%C3%A7%C3%A3o_de_grafos
