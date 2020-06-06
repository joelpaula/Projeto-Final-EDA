from enum import Enum
from Graph import Vertex, Edge
from DiGraph import DiGraph
from UpdatableBinaryHeap import UpdatableBinaryHeap

class Station(Vertex):
    def __init__(self, id, name, latitude, longitude):
        super().__init__(name=name)
        self.__id = id
        self.__latitude = latitude
        self.__longitude = longitude

    @property
    def id(self):
        return self.__id

    @property
    def latitude(self):
        return self.__latitude

    @property
    def longitude(self):
        return self.__longitude
    
    def geo_ref(self):
        return (self.__latitude, self.__longitude)

    def __str__(self):
        return f"[{self.id}] {self.name} ({self.latitude}, {self.longitude})"

    def __repr__(self):
        return str(self)

class peak_type(Enum):
    OFF_PEAK = 1
    AM_PEAK = 2
    INTER_PEAK = 3

class Connection(Edge):
    def __init__(self, origin, destination, distance_km, off_peak_mins, am_peak_mins, inter_peak_mins, line, name=None):
        super().__init__(origin=origin, destination=destination, name=name)
        self.distance_km = distance_km
        self.__times = {peak_type.OFF_PEAK: off_peak_mins, 
                        peak_type.AM_PEAK: am_peak_mins, 
                        peak_type.INTER_PEAK: inter_peak_mins}
        self.__lines = {line}

    @property
    def lines(self):
        return self.__lines

    def add_line(self, line):
        self.__lines.add(line)

    def get_time(self, peak, lines):
        line_change_time = 0
        if not any(line for line in lines if line in self.__lines):
            line_change_time = 10
        return self.__times[peak] + line_change_time

    def set_time(self, value, peak):
        self.__times[peak] = value

    def __str__(self):
        return f"{self.name if self.name else ''}: ({self.endpoints()[0].name} -- {self.endpoints()[1].name}) distance: {self.distance_km}km"

    def __repr__(self):
        return str(self)

class TrainGraph(DiGraph):
    def __init__(self):
        super().__init__(directed=False)

    def shortest_path(self, origin, destination, peak):
        """"
        Calculates shortest path from origin station to destination station.
        Returns a tuple (time, path), where:
         `time` is the path's time in minutes;
         `path` is a list with Stations, ordered from origin to destination.
        """
        cloud = {}
        paths = {}
        priority_queue = UpdatableBinaryHeap()

        priority_queue.add(0, (origin, None))

        while not priority_queue.is_empty():
            d, (v, incoming_edge) = priority_queue.first()
            if v not in paths.keys():
                paths[v] = None
            cloud[v] = d
            if v is destination:
                break
            for edge in self.get_incident_edges(v):
                u = edge.opposite(v)
                sc_pair = (u, edge)
                if u not in cloud:
                    if incoming_edge:
                        lines = incoming_edge.lines
                    else:
                        lines = edge.lines
                    weight = edge.get_time(peak, lines)
                    if priority_queue.get_key(sc_pair) is None or priority_queue.get_key(sc_pair) > d + weight:
                        paths[u]= v
                        priority_queue.update_or_add(d + weight, sc_pair)

        return cloud[v], TrainGraph.__get_path(paths, destination)

    @staticmethod
    def __get_path(path_dict, origin):
        if path_dict[origin] is None:
            return [origin]
        else:
            return TrainGraph.__get_path(path_dict, path_dict[origin]) + [origin]
