import dataclasses
from time import time

import psycopg2

from util.types import nullable, const


@dataclasses.dataclass
class DBConnectConfig:
    db_host: str = 'localhost'
    db_port: int = 5432
    db_user: str = 'postgres'
    db_pass: str = None


class FlightSearchPostgresDB:

    db_name: const(str) = 'flight-search'
    distances_table: const(str) = 'airport_distance_mapping'

    def __init__(self, config: DBConnectConfig):
        self._conf: DBConnectConfig = config

        self._initialized: bool = False
        self._db_conn: nullable(psycopg2.connection) = None

        self._connect()

    def reconnect(self, new_config: DBConnectConfig = None):
        if new_config:
            self._conf = new_config
        self._connect()

    def _connect(self):
        c = psycopg2.connect(
            database=self.db_name,
            user=self._conf.db_user,
            password=self._conf.db_pass,
            host=self._conf.db_host,
            port=self._conf.db_port,
        )
        self._db_conn = c
        self._initialized = True

    def close(self):
        if self._initialized:
            self._db_conn.close()
            self._initialized = False

    @classmethod
    def _build_insert_query(cls, table: str, columns: list[str], values: list[tuple]) -> str:
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES\n"
        query += ',\n'.join((f"({', '.join(values.pop(0))})" for _ in range(len(values))))
        return query + ';'

    def bulk_insert_distances(self, data: list[tuple]):

        start = time()
        query = self._build_insert_query(
            table=self.distances_table,
            columns=['ap1', 'ap2', 'distance_km'],
            values=data,
        )
        query_build_t = time()
        self._perform(query)
        insert_t = time()
        print(f"""Timestats: 
query build: {query_build_t - start}s
insert: {insert_t - query_build_t}s
total: {insert_t - start}s"""
              )

    def _perform(self, q: str):
        with self._db_conn.cursor() as cur:
            cur.execute(q)
        self._db_conn.commit()
