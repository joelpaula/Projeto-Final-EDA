class Vertex:
    def __init__(self, name=None):
        self.__name = name

    @property
    def name(self):
        return self.__name

    def __str__(self):
        return f"{self.__name}"

    def __repr__(self):
        return str(self)


class Edge:
    def __init__(self, origin, destination, name=None):
        self.__name = name
        self.__vertices = (origin, destination)

    @property
    def name(self):
        return self.__name

    @property
    def origin(self):
        return self.__vertices[0]

    @property
    def destination(self):
        return self.__vertices[1]

    def endpoints(self):
        return self.__vertices

    def opposite(self, v):
        return next(i for i in self.__vertices if i is not v)

    def __str__(self):
        return f"{self.__name if self.__name else ''}: ({self.__vertices[0].name} -- {self.__vertices[1].name})"

    def __repr__(self):
        return str(self)


class Graph:
    def __init__(self):
        self.__vertices = {}

    def insert_vertex(self, v):
        self.__vertices[v] = {}

    def vertices(self):
        return self.__vertices.keys()

    def vertex_count(self):
        return len(self.__vertices)

    def insert_edge(self, e):
        self.__vertices[e.origin][e.destination] = e
        self.__vertices[e.destination][e.origin] = e

    def edges(self):
        return {
            edge
            for children in self.__vertices.values()
            for edge in children.values()
        }

    def edge_count(self):
        return len(self.edges())

    def get_edge(self, u, v):
        res = None
        if u in self.__vertices:
            if v in self.__vertices[u]:
                res = self.__vertices[u][v]
        return res

    def degree(self, v):
        # print(self.__vertices[v].keys())
        return len(self.__vertices[v].keys())

    def remove_vertex(self, v):
        # remove connections to this vertex
        for o in self.__vertices[v]:
            del self.__vertices[o][v]
        del self.__vertices[v]

    def remove_edge(self, e):
        del self.__vertices[e.origin][e.destination]
        del self.__vertices[e.destination][e.origin]