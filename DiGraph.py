from Graph import Vertex, Edge

class DiGraph:
    def __init__(self, directed=False):
        self.__directed = directed
        self.__vertices_out = {}
        if directed:
            self.__vertices_in = {}
        else:
            self.__vertices_in = self.__vertices_out

    def insert_vertex(self, v):
        self.__vertices_out[v] = {}
        if self.__directed:
            self.__vertices_in[v] = {}

    def vertices(self):
        return self.__vertices_out.keys()

    def vertex_count(self):
        return len(self.__vertices_out)

    def insert_edge(self, e):
        self.__vertices_out[e.origin][e.destination] = e
        self.__vertices_in[e.destination][e.origin] = e

    def edges(self):
        return {
            edge
            for children in self.__vertices_out.values()
            for edge in children.values()
        }

    def edge_count(self):
        return len(self.edges())

    def get_edge(self, origin, destination):
        res = None
        if origin in self.__vertices_out:
            if destination in self.__vertices_out[origin]:
                res = self.__vertices_out[origin][destination]
        return res

    def get_incident_edges(self, v, outgoing=True):
        return self.__vertices_out[v].values() if outgoing else self.__vertices_in[v].values()

    def degree(self, v):
        # print(self.__vertices[v].keys())
        return len(self.__vertices_out[v].keys())

    def remove_vertex(self, v):
        # remove edges from this vertex
        for o in self.__vertices_out[v]:
            del self.__vertices_out[o][v]
        for o in self.__vertices_in[v]:
            del self.__vertices_in[o][v]
        del self.__vertices_out[v]
        del self.__vertices_in[v]

    def remove_edge(self, e):
        del self.__vertices_out[e.origin][e.destination]
        del self.__vertices_in[e.destination][e.origin]
