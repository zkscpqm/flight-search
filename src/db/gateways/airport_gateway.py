from pathlib import Path

from src.db.gateways.base_gateway import BaseGateway
from src.db.pg_connect import FlightSearchPostgresDB
from src.flight_search.airport import Airport
from util.logging.logger import Logger


class AirportGateway(BaseGateway):

    def __init__(self, pg: FlightSearchPostgresDB, init_script: Path = None,
                 debug_mode: bool = False, logger: Logger = None):
        BaseGateway.__init__(self, pg=pg, init_script=init_script, debug_mode=debug_mode, logger=logger)

    def add_airport(self, airport: Airport, upsert: bool = False) -> bool:
        uid = airport.iata_code if not airport.local_code else f"{airport.iata_code}_{airport.local_code}"

    def get_airport(self, uid: str, fields: list[str] = None, **kwargs) -> Airport:
        self.logger.info(f"Trying to get airport by UID {uid}...")
        selection = '*' if not fields else ', '.join(fields)
        query = f"SELECT {selection} FROM {self.airports_table} WHERE uid = {self.format_value(uid)}"
        resp = self.execute(query, **kwargs)

