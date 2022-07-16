import dataclasses
from datetime import datetime
from time import time

import psycopg2

from util.logging.logger import Logger, get_default_logger
from util.types import nullable, const


@dataclasses.dataclass
class DBConnectConfig:
    db_host: str = 'localhost'
    db_port: int = 5432
    db_name: str = 'postgres'
    db_user: str = 'postgres'
    db_pass: str = None


@dataclasses.dataclass
class PgResponse:
    query: str
    exec_time_ms: float
    pg_resp: list[tuple]
    row_count: int
    exc: Exception = None
    rollback_exc: Exception = None

    @property
    def failed(self) -> bool:
        return self.exc is not None or self.rollback_exc is not None


class FlightSearchPostgresDB:

    logger: Logger = get_default_logger()

    def __init__(self, config: DBConnectConfig, logger: Logger):
        if logger:
            self.logger: Logger = logger
            self.__class__.logger = logger
        self._conf: DBConnectConfig = config

        self._initialized: bool = False
        self._db_conn: nullable(psycopg2.connection) = None

        self._connect()

    def reconnect(self, new_config: DBConnectConfig = None):
        if new_config:
            self._conf = new_config
        self._connect()

    def _connect(self):
        self.logger.info(f"Attempting to connect to DB `{self._conf.db_name}` on {self._conf.db_host}:{self._conf.db_port}")
        c = psycopg2.connect(
            database=self._conf.db_name,
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

    def execute(self, q: str, fetch: bool = False) -> PgResponse:
        start_ = datetime.now()
        exc_ = None
        rb_exc_ = None
        rc = 0
        rv = []
        with self._db_conn.cursor() as cur:
            try:
                cur.execute(q)
                if fetch:
                    rv = cur.fetchall()
                    rc = len(rv)
                else:
                    rc = cur.rowcount
                self._db_conn.commit()
            except Exception as exc:
                exc_ = exc
                try:
                    self.logger.debug(f"ROLLBACK! {q=}")
                    self._db_conn.rollback()
                except Exception as rb_exc:
                    rb_exc_ = rb_exc
                    ...
        return PgResponse(
            query=q,
            exec_time_ms=(datetime.now() - start_).microseconds / 1000,
            pg_resp=rv,
            row_count=rc,
            exc=exc_,
            rollback_exc=rb_exc_
        )

