import copy
import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import Configuration
from secrets import SecretManager
from src.currency.exchange import ExchangeRateMap
from src.db.gateways.distance_pairs_gateway import AirportDistancePairsGateway
from src.db.pg_connect import FlightSearchPostgresDB, DBConnectConfig
from src.flight_search.airport import Airport
from src.flight_search.session import AmadeusSession
from src.flight_search_manager import FlightSearchManager
from src.geo.world_map import WorldMap
from util.logging.logger import get_logger, set_default_logger
from util.logging.log_level import LogLevelEnum
from util.logging.logging_handlers import FileHandler


def main():

    config = Configuration(Path("config.json"))
    secrets = SecretManager(
        amadeus_cred_file=Path("secrets/amadeus_creds.secret"),
        db_cred_file=Path("secrets/db_password.secret"),
        exchange_rates_cred_file=Path("secrets/exchange_rates_apikey.secret")
    )

    logger = get_logger(
        date_fmt=config.logging_date_fmt,
        time_fmt=config.logging_time_fmt,
        dt_fmt=config.logging_dt_fmt,
        level=LogLevelEnum.by_name(config.logging_level),
        extra_handlers=[
            FileHandler(date_fmt=config.logging_date_fmt, out=Path('./logs').absolute(), err_out=Path('./logs'))
        ]
    )
    set_default_logger(logger)
    gw = AirportDistancePairsGateway(
        pg=FlightSearchPostgresDB(
            config=DBConnectConfig(
                db_pass=secrets.db_password
            ),
            logger=logger
        ),
        init_script=Path(config.db_distance_pairs_init_script).absolute(),
        debug_mode=bool(config.debug_mode),
        logger=logger
    )

    airports_dataset = pd.read_csv(filepath_or_buffer=Path(config.world_map_airports_file), sep=';', header=0)
    logger.debug(f"Original dataset length: {len(airports_dataset)}")
    airports_dataset = airports_dataset[airports_dataset['iata_code'].notna() | airports_dataset['iata_code']]
    logger.debug(f"Post-drop airports dataset length: {len(airports_dataset)}")

    start = datetime.now()
    # gw.pair_exists("JOE", "UTK")

    # distance_import_dataset = [(series.iata_code, series.latitude, series.longitude)
    #                            for _, series in airports_dataset.iterrows() if series.iata_code not in {'0', 0}]
    distance_import_dataset = []
    seen = set()
    for _, series in airports_dataset.iterrows():
        if series.iata_code in {'0', 0}:
            continue
        if config.db_distance_pairs_import_skip_small_airports and series.type == 'small_airport':
            continue
        if series.iata_code in seen:
            print(f"SEEN! {series.iata_code}")  # TODO: Implement uid field to work around duplicate IATA Codes
            continue
        distance_import_dataset.append((series.iata_code, series.latitude, series.longitude))
        seen.add(series.iata_code)

    print(len(seen))
    print(len(distance_import_dataset))
    time.sleep(10)
    gw.import_data(dataset=distance_import_dataset, batch_size=config.db_distance_pairs_import_batch_size, validate=True)

    logger.info(f"populating took {(datetime.now() - start).seconds} seconds")
    # k1_, k2_ = _sort_keys("SOF", "BOJ")
    # logger.info(f"Sofia -> Burgas: {distance_map[k1_][k2_]}")
    # all_iatas = airports_dataset['iata_code'].tolist()
    # fst = True
    # for ap_tup in airports_dataset.itertuples(index=None):
    #     ap = Airport.from_namedtuple(ap_tup)
    #     res = db.get_pairs_by_ap(ap.iata_code)
    #
    #     if fst:
    #         logger.debug(str(type(res)))
    #         logger.debug(str(type(res[0])))
    #         fst = False
    #
    #     try:
    #         logger.debug(str(len(res)))
    #     except:
    #         logger.error('nope')
    #     exit(1)
    #     all_pairs_for_ap = [row[0] for row in res]
    #     set_pairs_for_ap = set(all_pairs_for_ap)
    #     if (la := len(all_pairs_for_ap)) != (ls := len(set_pairs_for_ap)):
    #         logger.warning(f"Inconsistent pair lengths for {ap.iata_code}: {la=} {ls=}")
    #
    #     if ls != len(all_iatas):
    #         logger.warning(f"Expected {len(all_iatas)} pairs for {ap.iata_code}, found only {ls}")
    #         all_iatas_cp = set(copy.deepcopy(all_iatas))
    #         for found_iata in set_pairs_for_ap:
    #             if found_iata in all_iatas_cp:
    #                 all_iatas_cp.remove(found_iata)
    #             else:
    #                 logger.debug(f"failed to find {found_iata}")
    #         logger.debug(f"Missing {len(all_iatas_cp)}:\n{all_iatas_cp}")
    #
    #


    # mgr = FlightSearchManager(
    #     world_map=WorldMap(
    #         data=airports_dataset,
    #         logger=logger
    #     ),
    #     fx_api=ExchangeRateMap(
    #         fx_exchange_api_key=secrets.exchangerates_api_key,
    #         cache_location=Path(config.fx_exchange_cache_location),
    #         logger=logger
    #     ),
    #     flight_search=AmadeusSession(
    #         api_key=secrets.amadeus_api_key,
    #         api_secret=secrets.amadeus_api_secret,
    #         logger=logger
    #     ),
    #     logger=logger
    # )

    # sess =
    # data = pd.read_csv(filepath_or_buffer=Path("data/airports_dataset.csv"), sep=';', header=0)
    #
    # map_ = Map(data)
    # ap = map_.lookup('Sofia Airport')
    # bs = map_.lookup('Burgas Airport')
    # # print(ap.distance_to(bs))
    # if ap:
    #     nearby = map_.find_nearby(ap, max_radius_km=400)
    #     if len(nearby) > 0:
    #         print(f"[{ap.name}] nearby ({len(nearby)}): {', '.join((f'{ap_.name} ({dist})' for ap_, dist in nearby))}")


if __name__ == "__main__":
    main()
