from pathlib import Path


from src.db.gateways.base_gateway import BaseGateway
from src.db.pg_connect import FlightSearchPostgresDB
from util.logging.logger import Logger
from util.math import calculate_distance_km
from util.types import nullable


class AirportDistancePairsGateway(BaseGateway):

    def __init__(self, pg: FlightSearchPostgresDB, init_script: Path = None,
                 debug_mode: bool = False, logger: Logger = None):
        BaseGateway.__init__(self, pg=pg, init_script=init_script, debug_mode=debug_mode, logger=logger)

    @staticmethod
    def order_iata_key_pairs(ap1_iata: str, ap2_iata: str) -> tuple[str, str]:
        if ap1_iata < ap2_iata:
            return ap1_iata, ap2_iata
        return ap2_iata, ap1_iata

    def import_data(self, dataset: list[tuple[str, float, float]],
                    batch_size: int = 1000, validate: bool = True) -> int:
        self.logger.info(f"Starting data import for {len(dataset)} airports...")
        insertions = 0
        seen: set[str] = set()
        batch: list[tuple[str, str, str, float]] = []

        def flush(insertions_: int) -> int:
            ins = self.bulk_insert_distances(data=batch[:])
            insertions_ += ins
            self.logger.debug(f"Successfully imported {ins} pairs (total: {insertions})")
            return insertions_

        num_expected_pairs = len(dataset)

        for ap1_iata, ap1_lat, ap1_lon in dataset:
            existing_pairs = self.get_pairs_by_ap(ap1_iata)
            if (num_existing_pairs := len(existing_pairs)) == num_expected_pairs:
                self.logger.info(f"Skipping import for {ap1_iata}, all mappings exist")
                continue
            self.logger.debug(f"Found {num_existing_pairs}/{num_expected_pairs} existing pairs for airport {ap1_iata}")
            for code, _, _ in dataset:
                if code not in existing_pairs:
                    self.logger.debug(f"NOT FOUND!! {code}")
            for ap2_iata, ap2_lat, ap2_lon in dataset:
                left_key, right_key = self.order_iata_key_pairs(ap1_iata, ap2_iata)
                if (pair_id := f"'{left_key}_{right_key}'") not in seen:
                    if self.pair_exists(left_key, right_key):
                        seen.add(pair_id)
                        continue
                    batch.append(
                        (pair_id, f"'{left_key}'", f"'{right_key}'",
                         calculate_distance_km((ap1_lat, ap1_lon), (ap2_lat, ap2_lon))
                         ))
                    seen.add(pair_id)

                    if len(batch) >= batch_size:
                        insertions = flush(insertions)
                        batch = []
        insertions = flush(insertions)
        self.logger.info(f"Initial import finished. Made {insertions} insertions.")
        if validate:
            insertions += self._validate_import(dataset)
        return insertions

    def _validate_import(self, dataset: list[tuple[str, float, float]]) -> int:
        self.logger.info("Performing import validation...")
        num_expected_pairs = len(dataset)
        new_insertions = 0
        for ap1_iata, ap1_lat, ap1_lon in dataset:
            self.logger.debug(f"Validating pairs for airport {ap1_iata}")
            pairs = self.get_pairs_by_ap(ap1_iata)
            if (pair_count := len(pairs)) != num_expected_pairs:
                self.logger.warning(f"Found {pair_count} pairs for airport {ap1_lat} (expected {num_expected_pairs})")
                for ap2_iata, ap2_lat, ap2_lon in dataset:
                    key_l, key_r = self.order_iata_key_pairs(ap1_iata, ap2_iata)
                    if self.get_distance(key_l, key_r) is None:
                        self.logger.warning(f"Found missing pair {ap1_iata} -> {ap2_iata}! Inserting...")
                        rc = self.insert_distance(key_l, key_r, calculate_distance_km(
                            (ap1_lat, ap1_lon), (ap2_lat, ap2_lon)
                        ))
                        if rc != 1:
                            self.logger.error(f"Expected rowcount 1 for single insert, got {rc}")
                        new_insertions += rc
                        pair_count += rc
                        if pair_count == num_expected_pairs:
                            break
        self.logger.info(f"Validation run inserted {new_insertions} new rows")
        return new_insertions

    def insert_distance(self, ap1_iata: str, ap2_iata: str, distance: float) -> int:
        self.logger.debug(f"Inserting distance {ap1_iata} -> {ap2_iata} (~{distance:.2f}km)")
        query = self._build_insert_query(
            table=self.distances_table,
            columns=['pairid', 'ap1', 'ap2', 'distance_km'],
            values=[(f"'{ap1_iata}_{ap2_iata}'", f"'{ap1_iata}'", f"'{ap2_iata}'", f"'{distance}'")]
        )
        resp = self.execute(query, max_attempts=3)
        if resp.failed:
            err_msg = f"Failed to insert distance pair into db. Most recent exception: {resp.exc}"
            if resp.rollback_exc:
                err_msg += f", rollback exception: {resp.rollback_exc}"
            self.logger.error(err_msg)
            return 0
        return resp.row_count

    def bulk_insert_distances(self, data: list[tuple]) -> int:
        self.logger.debug(f"Starting distance bulk insert: {len(data)} values")
        data_len = len(data)
        query = self._build_insert_query(
            table=self.distances_table,
            columns=['pairid', 'ap1', 'ap2', 'distance_km'],
            values=data,
        )
        resp = self.execute(query, max_attempts=3, suppress_query_out=True)
        if resp.failed:
            err_msg = f"Failed to bulk insert {data_len} distance pairs into db. Most recent exception: {resp.exc}"
            if resp.rollback_exc:
                err_msg += f", rollback exception: {resp.rollback_exc}"
            self.logger.error(err_msg)
            return 0

        if resp.row_count != data_len:
            self.logger.warning(f"Inserted {resp.row_count} distance pairs when passed data had length {data_len}")

        return resp.row_count

    def get_distance(self, ap1_iata: str, ap2_iata: str) -> nullable(float):
        ap1_, ap2_ = self.order_iata_key_pairs(ap1_iata, ap2_iata)
        query = f"SELECT distance_km FROM {self.distances_table}  WHERE ap1 = '{ap1_}' AND ap2 = '{ap2_}'"
        resp = self.execute(query, fetch=True)
        if resp.failed:
            err_msg = f"Failed to get distance pair ({ap1_iata} -> {ap2_iata}) Most recent exception: {resp.exc}"
            if resp.rollback_exc:
                err_msg += f", rollback exception: {resp.rollback_exc}"
            self.logger.error(err_msg)
            return

        if resp.row_count == 0:
            self.logger.error(f"Could not find distance pair {ap1_iata} -> {ap2_iata}")
            return

        if resp.row_count > 1:
            self.logger.warning(f"Multiple ({resp.row_count}) entries found for distance pair {ap1_iata} -> {ap2_iata}")

        return resp.pg_resp[0][0]

    def pair_exists(self, ap1_iata: str, ap2_iata: str) -> bool:
        ap1_, ap2_ = self.order_iata_key_pairs(ap1_iata, ap2_iata)
        query = f"SELECT COUNT(*) FROM {self.distances_table} WHERE ap1 = '{ap1_}' AND ap2 = '{ap2_}' "
        resp = self.execute(query, fetch=True)
        if resp.failed:
            err_msg = f"Failed to get distance pair ({ap1_iata} -> {ap2_iata}) Most recent exception: {resp.exc}"
            if resp.rollback_exc:
                err_msg += f", rollback exception: {resp.rollback_exc}"
            self.logger.error(err_msg)
            return False
        if (resp_len := len(resp.pg_resp)) > 1:
            self.logger.warning(f"Received more than 1 result for pair search ({resp_len})")
        return resp.pg_resp[0][0] > 0

    def get_pairs_by_ap(self, ap_iata: str) -> dict[str, float]:
        query = f"SELECT ap1 pair, distance_km from {self.distances_table} where ap2 = '{ap_iata}' " \
                f"union " \
                f"select ap2 pair, distance_km from {self.distances_table} where ap1 = '{ap_iata}';"

        resp = self.execute(query, fetch=True)
        if resp.failed:
            err_msg = f"Failed to get pairs for airport {ap_iata}. Most recent exception: {resp.exc}"
            if resp.rollback_exc:
                err_msg += f", rollback exception: {resp.rollback_exc}"
            self.logger.error(err_msg)
            return {}

        rv: dict[str, float] = {}
        self.logger.debug(f"Found {resp.row_count} pairs for airport {ap_iata}")
        for row in resp.pg_resp:
            if (pair_name := row[0]) in rv:
                self.logger.warning(f"Duplicate pair {ap_iata} -> {pair_name} found!")
            rv[pair_name] = float(row[1])
        return rv



