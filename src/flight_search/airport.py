import dataclasses
from collections import namedtuple
from typing import Any
import math

from util.logging.logger import Logger, get_default_logger
from util.math import calculate_distance_km
from util.types import nullable


@dataclasses.dataclass
class Airport:

    full_name: nullable(str) = None
    iso_country: nullable(str) = None
    iso_region: nullable(str) = None
    municipality: nullable(str) = None
    latitude: nullable(float) = None
    longitude: nullable(float) = None
    size: nullable(str) = None
    iata_code: nullable(str) = None
    local_code: nullable(str) = None

    logger: Logger = get_default_logger()

    @property
    def coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude

    @classmethod
    def from_namedtuple(cls, nt: namedtuple) -> 'Airport':
        return Airport(
            full_name=nt.name,
            iso_country=nt.iso_country,
            iso_region=nt.iso_region,
            municipality=nt.municipality,
            latitude=nt.latitude,
            longitude=nt.longitude,
            size=nt.type,
            iata_code=nt.iata_code,
            local_code=nt.local_code
        )

    @classmethod
    def from_db_row(cls, row: tuple, fields: list[str] = None) -> 'Airport':
        fields = fields or ['uid', 'full_name', 'country', 'region', 'municipality',
                            'latitude', 'longitude', 'ap_type', 'iata_code', 'local_code']
        rv = Airport()
        if (row_len := len(row)) != (num_fields := len(fields)):
            cls.logger.error(f"Mismatched {row_len=} and {num_fields=}..\nFields:{fields}\nRow: {row}")
            return rv
        for property_name, property_value in zip(fields, row):
            if property_name != 'uid' and hasattr(rv, property_name):
                setattr(rv, property_name, property_value)

        return rv

    def get_field_value_pairs(self, fields: list[str] = None) -> tuple[list[str], list[Any]]:
        keys = []
        values = []
        fields = fields or ['uid', 'full_name', 'iso_country', 'iso_region', 'municipality',
                            'latitude', 'longitude', 'size', 'iata_code', 'local_code']
        for attr in fields:
            if hasattr(self, attr):
                keys.append(attr)
                values.append(getattr(self, attr))
            else:
                self.logger.warning(f"Failed to get Airport attribute {attr} while building pairs")
        return keys, values

    def distance_to(self, other: 'Airport') -> float:
        return calculate_distance_km(self.coordinates, other.coordinates)

    def __hash__(self) -> int:
        return hash(self.coordinates)

    @property
    def uid(self) -> nullable(str):
        if not self.iata_code:
            return None
        if not self.local_code:
            return self.iata_code
        return f"{self.iata_code}_{self.local_code}"
