import abc
import time
from pathlib import Path

from src.db.mixins import FormattingMixin
from src.db.pg_connect import FlightSearchPostgresDB, DBConnectConfig, PgResponse
from util.logging.logger import Logger, get_default_logger
from util.types import const


class BaseGateway(abc.ABC, FormattingMixin):

    logger: Logger = get_default_logger()

    airports_table: const(str) = 'airports'
    distances_table: const(str) = 'airport_distance_mapping'

    def __init__(self, pg: FlightSearchPostgresDB, debug_mode: bool = False,
                 init_script: Path = None, logger: Logger = None):
        self.pg: FlightSearchPostgresDB = pg
        self._debug_mode: bool = debug_mode
        self._closed: bool = False
        if init_script:
            self._initialize_table(script_path=init_script)
        if logger:
            self.logger: Logger = logger
            self.__class__.logger = logger

    def _initialize_table(self, script_path: Path):
        with open(script_path) as h:
            script = h.read()
        resp = self.execute(script)
        if resp.failed:
            err_msg = f"Failed to initialize table! Got exception: {resp.exc}"
            if resp.rollback_exc:
                err_msg += f", rollback exception: {resp.rollback_exc}"
            self.logger.error(err_msg)
            exit(1)

    @classmethod
    def _build_insert_query(cls, table: str, columns: list[str], values: list[tuple], conflict: str = 'pairid') -> str:
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES\n"
        for row in values:
            query += f"({','.join((cls.format_value(x) for x in row))}),\n"
        return query[:-2] + (';' if not conflict else f'ON CONFLICT ({conflict}) DO NOTHING;')

    def reconnect(self, new_config: DBConnectConfig = None):
        self.pg.reconnect(new_config=new_config)

    def close(self):
        self.pg.close()
        self._closed = True

    def execute(self, query: str, fetch: bool = False,
                max_attempts: int = 1, sleep_duration_s: float = 1., suppress_query_out: bool = False) -> PgResponse:
        total_time_ms = 0
        qry_log = f' query:\n{query}' if self._debug_mode and not suppress_query_out else ''
        for attempt_number in range(1, max_attempts + 1):
            self.logger.debug(f"Attempt ({attempt_number}/{max_attempts}){qry_log}")
            resp = self.pg.execute(q=query, fetch=fetch)
            total_time_ms += resp.exec_time_ms
            if resp.failed:
                self.logger.error(f"Query execution failed due to exception {resp.exc}!{qry_log}")
                if attempt_number != max_attempts:
                    time.sleep(sleep_duration_s)
                    continue
            self.logger.info(f"Total execution time for query: {resp.exec_time_ms:.1f}ms")
            return resp
