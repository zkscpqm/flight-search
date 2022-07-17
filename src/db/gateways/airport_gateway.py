from pathlib import Path

from src.db.gateways.base_gateway import BaseGateway
from src.db.pg_connect import FlightSearchPostgresDB
from src.flight_search.airport import Airport
from util.logging.logger import Logger
from util.types import nullable


class AirportGateway(BaseGateway):

    def __init__(self, pg: FlightSearchPostgresDB, init_script: Path = None,
                 debug_mode: bool = False, logger: Logger = None):
        BaseGateway.__init__(self, pg=pg, init_script=init_script, debug_mode=debug_mode, logger=logger)

    def import_data(self, airports: list[Airport]) -> int:
        added = 0
        for airport in airports:
            added += self.add_airport(airport)
        return added

    def add_airport(self, airport: Airport, **kwargs) -> int:
        self.logger.info(f"Inserting airport {airport.uid} ({airport.full_name})")
        columns, values = airport.get_field_value_pairs()
        return self.add_airport_raw(columns, values, **kwargs)

    def add_airport_raw(self, columns: list[str], values: list[str], **kwargs) -> int:
        query = self._build_insert_query(
            table=self.airports_table,
            columns=columns,
            values=[tuple(values)],
            avoid_conflict=True
        )
        resp = self.execute(query, **kwargs)
        if resp.failed:
            err_msg = f"Failed to add airport to database. Most recent exception: {resp.exc}"
            if resp.rollback_exc:
                err_msg += f", rollback exception: {resp.rollback_exc}"
            self.logger.error(err_msg)
            return 0
        return resp.row_count

    def get_airport(self, uid: str, fields: list[str] = None, **kwargs) -> nullable(Airport):
        self.logger.info(f"Trying to get airport by UID {uid}...")
        selection = '*' if not fields else ', '.join(fields)
        query = f"SELECT {selection} FROM {self.airports_table} WHERE uid = {self.format_value(uid)}"
        resp = self.execute(query, fetch=True, **kwargs)
        if resp.failed:
            err_msg = f"Failed to get airport with UID {uid}. Most recent exception: {resp.exc}"
            if resp.rollback_exc:
                err_msg += f", rollback exception: {resp.rollback_exc}"
            self.logger.error(err_msg)
            return
        if resp.row_count == 0:
            return
        if resp.row_count > 1:
            self.logger.warning(f"Found >1 row for UID {uid}! Returning first result")

        return Airport.from_db_row(resp.pg_resp[0], fields)
