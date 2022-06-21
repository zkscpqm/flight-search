import dataclasses
import math
from functools import lru_cache
from typing import Iterator

import pandas as pd

from src.skylib.airport import Airport
from util.types import const


class Bounds:
    min_lat: const(float) = -90.
    max_lat: const(float) = 90.
    min_lon: const(float) = -180.
    max_lon: const(float) = 180.

    @classmethod
    def in_bounds(cls, lat: float, lon: float) -> bool:
        return cls.min_lat <= lat <= cls.max_lat and cls.min_lon <= lon <= cls.max_lon

    @classmethod
    def min_lat_i(cls) -> int:
        return int(cls.min_lat * 10 * 2)

    @classmethod
    def max_lat_i(cls) -> int:
        return int(cls.max_lat * 10 * 2)

    @classmethod
    def min_lon_i(cls) -> int:
        return int(cls.min_lon * 10 * 2)

    @classmethod
    def max_lon_i(cls) -> int:
        return int(cls.max_lon * 10 * 2)


@dataclasses.dataclass
class Field:
    lat: const(float)
    lon: const(float)
    airports: dict[str, Airport] = dataclasses.field(default_factory=lambda: {})

    def contains(self, name: str = None) -> bool:
        return name in self.airports

    def get(self, name: str) -> Airport:
        return self.airports.get(name)

    def put(self, airport: Airport):
        self.airports[airport.name] = airport

    def __len__(self) -> int:
        return len(self.airports)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"Field(airports={len(self)}, coords=({self.lat}, {self.lon}))"


class Map:

    KM_PER_SQUARE: const(float) = 12.5

    def __init__(self, data: pd.DataFrame = None):
        self._map: list[list[Field]] = []
        max_lat_i, max_lon_i = self.convert_ll_to_indexes(Bounds.max_lat, Bounds.max_lon)
        for lat_i in range(max_lat_i + 1):
            row = []
            for lon_i in range(max_lon_i + 1):
                lat, lon = self.convert_indexes_to_ll(lat_i, lon_i)
                row.append(Field(lat=lat, lon=lon))
            self._map.append(row)
        if data:
            self.populate(data)

    @staticmethod
    def _get_min_lat_bound(lat: int, offset: int) -> int:
        min_bound = lat - offset
        if min_bound < 0:
            min_bound = Bounds.max_lat_i() + min_bound

        return min_bound

    @staticmethod
    def _get_min_lon_bound(lon: int, offset: int) -> int:
        min_bound = lon - offset
        if min_bound < 0:
            min_bound = Bounds.max_lon_i() + min_bound

        return min_bound

    def subgrid(self, min_lat_i: int, min_lon_i: int, offset: int) -> Iterator[Field]:
        lat_i = min_lat_i
        lon_i = min_lon_i
        for _ in range(offset * 2):
            for _ in range(offset * 2):
                yield self.get_field(lat_i, lon_i)
                lon_i = self.next_lon_i(lon_i)
            lon_i = min_lon_i
            lat_i = self.next_lat_i(lat_i)

    @staticmethod
    def next_lat_i(lat_i: int) -> int:
        if lat_i >= Bounds.max_lat_i():
            return 0
        return lat_i + 1

    @staticmethod
    def next_lon_i(lon_i: int) -> int:
        if lon_i >= Bounds.max_lon_i():
            return 0
        return lon_i + 1

    @lru_cache
    def find_nearby(self, ap: Airport, max_radius_km: float = 100.) -> list[tuple[Airport, float]]:
        # TODO: See why some searches work in one direction but not in reverse
        max_jumps = math.ceil(max_radius_km / self.KM_PER_SQUARE)
        rv: list[tuple[Airport, float]] = []

        def __insert(ap_: Airport):
            dist = ap.distance_to(ap_)
            for idx, (stored_ap, stored_dist) in enumerate(rv):
                if dist < stored_dist and (dist <= max_radius_km):
                    rv.insert(idx, (ap_, dist))
                    return
            if dist <= max_radius_km:
                rv.append((ap_, dist))

        lat_i, lon_i = self.convert_ll_to_indexes(ap.latitude, ap.longitude)
        min_lat_i = self._get_min_lat_bound(lat_i, offset=max_jumps)
        min_lon_i = self._get_min_lon_bound(lon_i, offset=max_jumps)
        for field in self.subgrid(min_lat_i=min_lat_i, min_lon_i=min_lon_i, offset=max_jumps):
            for found_ap in field.airports.values():
                __insert(found_ap)
        return rv

    def get_field(self, lat_i: int, lon_i: int) -> Field:
        return self._map[lat_i][lon_i]

    @classmethod
    def convert_ll_to_indexes(cls, lat: float, lon: float) -> tuple[int, int]:
        rv_lat = int(round(-lat if lat < 0 else lat + Bounds.max_lat, 1) * 10)
        rv_lon = int(round(-lon if lon < 0 else lon + Bounds.max_lon, 1) * 10)
        return rv_lat, rv_lon

    @classmethod
    def convert_indexes_to_ll(cls, lat: int, lon: int) -> tuple[float, float]:
        lat /= 10
        lon /= 10
        rv_lat = -lat if lat < Bounds.max_lat else lat - Bounds.max_lat
        rv_lon = -lon if lon < Bounds.max_lon else lon - Bounds.max_lon
        return round(rv_lat, 1), round(rv_lon, 1)

    def _insert(self, lat_i: int, lon_i: int, ap: Airport):
        self._map[lat_i][lon_i].put(ap)

    def insert(self, airport: Airport):
        if Bounds.in_bounds(airport.latitude, airport.longitude):
            lat_i, lon_i = self.convert_ll_to_indexes(airport.latitude, airport.longitude)
            self._insert(lat_i, lon_i, airport)

    def populate(self, data: pd.DataFrame, closed: bool = False, small: bool = False, medium: bool = True):
        filter_ = set()
        if not closed:
            filter_.add('closed')
        if not small:
            filter_.add('small_airport')
        if not medium:
            filter_.add('medium_airport')
        for ap in data.itertuples(index=False):
            airport = Airport.from_namedtuple(ap)
            if airport.ap_type not in filter_:
                self.insert(airport)
