import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from haversine import haversine, Unit
from collections import namedtuple
from Graph import Graph, Edge #, Vertex
from TrainGraph import Station, Connection, peak_type
from DiGraph import DiGraph
from UpdatableBinaryHeap import UpdatableBinaryHeap


df_stations = pd.read_csv("LondonTube/london.stations.txt")
df_stations.head()

df_connections = pd.read_csv("LondonTube/london.connections.txt")
df_connections.head()


gr = Graph()

train_stations = {}  # TODO Use BST
for ts in df_stations.itertuples():
    s = Station(id=ts.id,
                name=ts.name,
                latitude=ts.latitude,
                longitude=ts.longitude)
    gr.insert_vertex(s)
    train_stations[s.id] = s

connections = {}
for cn in df_connections.itertuples():
    key1 = (cn.station1, cn.station2)
    key2 = (cn.station2, cn.station1)
    if key1 not in connections.keys() and key2 not in connections.keys():
        c = Edge(train_stations[cn.station1], train_stations[cn.station2])
        connections[key1] = c

for e in connections.values():
    gr.insert_edge(e)

print("Stations: ", gr.vertex_count())
print("Connections: ", gr.edge_count())

plt.rcParams['figure.dpi'] = 150

def plot_edges(lst, color="xkcd:royal blue", marker="o", markersize=1, linewidthwidth=0.5, showgraph=False):
    for e in lst:
        xs = [e.origin.longitude, e.destination.longitude]
        ys = [e.origin.latitude, e.destination.latitude]
        plt.plot(xs, ys, c=color, marker=marker, markersize=markersize, linewidth=linewidthwidth)

    if showgraph:
        plt.axis('off')
        plt.show()

plot_edges(gr.edges(), showgraph=True)

m_L = np.zeros([gr.vertex_count(), gr.vertex_count()], int)
vertices = list(gr.vertices())

for i in range(m_L.shape[0]):
    for j in range(m_L.shape[1]):
        if i == j:
            m_L[i, j] = gr.degree(vertices[i])
        elif gr.get_edge(vertices[i], vertices[j]):
            m_L[i, j] = -1

# Get EigenVector
eigenvalues, v = np.linalg.eig(m_L)
eigen_index = np.argsort(eigenvalues)[1]
ev2nd = v[:, eigen_index]

g1 = Graph()
g2 = Graph()

for i in range(ev2nd.size):
    if ev2nd[i] < 0:
        g1.insert_vertex(vertices[i])
    else:
        g2.insert_vertex(vertices[i])

g1_count = g1.vertex_count()
g2_count = g2.vertex_count()

print("G1: ", g1_count, "stations")
print("G2: ", g2_count, "stations")

# Edges with one vertex/station in g1 and another one in g2
e_to_cut = []
for e in gr.edges():
    if all(ver in g1.vertices() for ver in e.endpoints()):
        g1.insert_edge(e)
    elif all(ver in g2.vertices() for ver in e.endpoints()):
        g2.insert_edge(e)
    else:
        e_to_cut.append(e)

print("Number of connections in G1:", g1.edge_count())
print("Number of connections in G2:", g2.edge_count())
print("Number of cuts:", len(e_to_cut))
print("Minimum Cut Ratio:", len(e_to_cut) / (g1_count * g2_count))

plot_edges(g1.edges(), color="xkcd:azure")
plot_edges(g2.edges(), color="xkcd:aquamarine")
plot_edges(e_to_cut, color="xkcd:coral", marker="+", markersize=0.9, showgraph=True)

for e in e_to_cut:
    print(e)



# PARTE II

df_interstations = pd.read_csv("LondonTube/interstation v2.csv", names=["line", "from_id", "to_id", "distance", "off_peak", "am_peak", "inter_peak"])
print("Distâncias e tempos entre estações:", len(df_interstations.index))
df_lines = pd.read_csv("LondonTube/london.lines.txt")
print("Linhas:", len(df_lines.index))

TrainLine = namedtuple("TrainLine", "id, name, color, stripe_color")
london_lines = {}
for l in df_lines.itertuples():
    london_lines[l.line] = TrainLine(l.line, l.name, l.colour, l.stripe)
print(london_lines)


# De seguida lemos as ligações entre as estações, por linha, colocando-as num dicionário, de forma a facilitar a sua utilização quando formos adicionar as ligações entre estações.
interstations = {} # {(from_station, to_station): {line: ConnectionWeights}}
ConnectionWeights = namedtuple("ConnectionWeights", "line, from_station, to_station, distance_km, off_peak_mins, am_peak_mins, inter_peak_mins")
for line in df_interstations.itertuples():
    key = (line.from_id, line.to_id)
    if key not in interstations.keys():
        interstations[(line.from_id, line.to_id)] = {}
    interstations[(line.from_id, line.to_id)][line.line] = ConnectionWeights(line.line, line.from_id, line.to_id, line.distance, line.off_peak, line.am_peak, line.inter_peak)

print("Tempos e distâncias de ligação lidos:", sum(len(it.keys()) for it in interstations.values()))


# Criar o grafo pesado e dirigido:
weighted_gr = DiGraph()

def get_weights(from_ts, to_ts, line, use_oposite_direction=False, calculate_weights=False):
    """Get the weights (time and distance) for a line from station `from_ts` to 
    station `to_ts`
        : use_oposite_direction (bool): When interstation weights are not found 
    from_ts` to `to_ts`, then we try to get from `to_ts`to `from_ts`.
        : calculate_weights (bool): When interstation weights are not found from 
    `from_ts` to `to_ts` (and from `to_ts`to `from_ts`, depending on 
    use_oposite_direction), calculate the direct distance and assume a time based 
    on 30km/h speed.
    """
    weights = None
    key = (from_ts, to_ts)
    if key in interstations.keys():
        if line in interstations[key].keys():
            weights = interstations[key][line]
        else:
            weights = next(iter(interstations[key].values()))
    elif use_oposite_direction and (to_ts, from_ts) in interstations.keys():
        key = (to_ts, from_ts)
        if line in interstations[key].keys():
            weights = interstations[key][line]
        else:
            weights = next(iter(interstations[key].values()))
    elif calculate_weights:
        distance_kms = haversine(train_stations[from_ts].geo_ref(), train_stations[to_ts].geo_ref())
        # assume 30km/h speed
        time_mins = distance_kms * 2 # distance x 60mins / 30km
        weights = ConnectionWeights(line, from_ts, to_ts, distance_kms, time_mins, time_mins, time_mins)
    return weights

# read train stations    
train_stations = {}  # TODO Use BST
for ts in df_stations.itertuples():
    s = Station(id=ts.id,
                name=ts.name,
                latitude=ts.latitude,
                longitude=ts.longitude)
    weighted_gr.insert_vertex(s)
    train_stations[s.id] = s

# now read all the connections and create the edges for these connections
for cn in df_connections.itertuples():
    weights = get_weights(cn.station1, cn.station2, cn.line)
    c = weighted_gr.get_edge(train_stations[cn.station1], train_stations[cn.station2])
    if c:
        # connection already exists - add the line
        c.add_line(cn.line)
    elif weights:
        c = Connection(train_stations[cn.station1], train_stations[cn.station2], weights.distance_km,
            weights.off_peak_mins, weights.am_peak_mins, weights.inter_peak_mins, cn.line)
        weighted_gr.insert_edge(c)
    else:
        c = Connection(train_stations[cn.station1], train_stations[cn.station2], 0, 0, 0, 0, cn.line)
        weighted_gr.insert_edge(c)

# calculate missing weights (distance + times)
for cn in weighted_gr.edges():
    if cn.distance_km == 0:
        weights = get_weights(cn.origin.id, cn.destination.id, 0, True, True)
        cn.distance_km = weights.distance_km
        cn.set_time(weights.am_peak_mins, peak_type.AM_PEAK)
        cn.set_time(weights.inter_peak_mins, peak_type.INTER_PEAK)
        cn.set_time(weights.off_peak_mins, peak_type.OFF_PEAK)

print("Stations: ", weighted_gr.vertex_count())
print("Connections: ", weighted_gr.edge_count())


# Próximo passo: pesquisar distancia entre Amersham (id 6) e Wimbledon (id 299).
def shortest_path(gr, origin, destination, peak):
    cloud = {}
    priority_queue = UpdatableBinaryHeap()
    # distances = {}
    priority_queue.add(0, origin)

    while not priority_queue.is_empty():
        d, v = priority_queue.first()
        cloud[v] = d
        if v is destination:
            break
        for e in gr.get_incident_edges(v):
            u = e.opposite(v)
            if u not in cloud:
                weight = e.get_time(peak)
                print(u, weight)
                if priority_queue.get_key(u) is None or priority_queue.get_key(u) > d + weight:
                    priority_queue.update_or_add(d + weight, u)

    return cloud

# Próximo passo: pesquisar distancia entre Amersham (id 6) e Wimbledon (id 299).
# Baker street = 11; Green Park = 107
from_station = 11
to_station = 107
cl = shortest_path(weighted_gr, train_stations[from_station], train_stations[to_station], peak_type.AM_PEAK)
#cl = shortest_path(weighted_gr, train_stations[6], train_stations[299], peak_type.AM_PEAK)
# Próximo passo: pesquisar distancia entre Amersham (id 6) e South Harrow (id 235).
# cl = shortest_path(weighted_gr, train_stations[6], train_stations[235], peak_type.AM_PEAK)
print("From ", train_stations[from_station], "to", train_stations[to_station], "AM Peak time:", cl[train_stations[to_station]] )
#print(cl)

# # Bibliografia
# Demmel, J. (2009). CS267 lecture 13 – Graph Partitioning. Obtido em 25 de Maio de 2020, de U.C. Berkeley CS267/EngC233: https://people.eecs.berkeley.edu/~demmel/cs267_Spr09/Lectures/lecture13_partition_jwd09.ppt
# 
# Gonina, K., Ray, S., & Su, B.-Y. (2020). _Graph Partitioning_. Obtido em 25 de Maio de 2020, de Berkeley Our Pattern Language: https://patterns.eecs.berkeley.edu/?page_id=571
# 
# Kabelíková, P. (2006). _Graph Partitioning Using Spectral Methods_. (Tese). VSB - Technical University of Ostrava, República Checa. Obtido em 25 de Maio de 2020: https://pdfs.semanticscholar.org/ab34/1258fbab7b2e9a719c6bbeb96fc204356a82.pdf
# 
# Wikipédia. (2019). _Partição de grafos_. Obtido de Wikipédia: https://pt.wikipedia.org/wiki/Parti%C3%A7%C3%A3o_de_grafos
