import dataclasses
from collections import namedtuple

from geopy import distance

from util.types import nullable


@dataclasses.dataclass
class Airport:
    name: str
    country: str
    region: str
    municipality: str
    latitude: float
    longitude: float
    ap_type: str
    iata_code: nullable(str) = None
    local_code: nullable(str) = None

    @property
    def coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude

    @classmethod
    def from_namedtuple(cls, nt: namedtuple) -> 'Airport':
        return Airport(
            name=nt.name,
            country=nt.iso_country,
            region=nt.iso_region,
            municipality=nt.municipality,
            latitude=nt.latitude,
            longitude=nt.longitude,
            ap_type=nt.type,
            iata_code=nt.iata_code,
            local_code=nt.local_code
        )

    def distance_to(self, other: 'Airport') -> float:
        return distance.geodesic(self.coordinates, other.coordinates, ellipsoid='WGS-84').km

    def __hash__(self) -> int:
        return hash(self.coordinates)
