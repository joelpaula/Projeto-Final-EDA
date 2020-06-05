from enum import Enum
from Graph import Vertex, Edge

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

    def get_time(self, peak):
        return self.__times[peak]

    def set_time(self, value, peak):
        self.__times[peak] = value

    def __str__(self):
        return f"{self.name if self.name else ''}: ({self.endpoints()[0].name} -- {self.endpoints()[1].name}) distance: {self.distance_km}km"

    def __repr__(self):
        return str(self)

