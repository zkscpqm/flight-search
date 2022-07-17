from datetime import datetime
from pathlib import Path

from config import Configuration
from secrets import SecretManager
from src.db.gateways.airport_gateway import AirportGateway
from src.db.gateways.distance_pairs_gateway import AirportDistancePairsGateway
from src.db.pg_connect import FlightSearchPostgresDB, DBConnectConfig
from src.flight_search.airport import Airport
from util.logging.logger import get_logger, set_default_logger
from util.logging.log_level import LogLevelEnum
from util.logging.logging_handlers import FileHandler
from util.math import format_timedelta_string


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
    db = FlightSearchPostgresDB(config=DBConnectConfig(db_pass=secrets.db_password), logger=logger)

    ap_gw = AirportGateway(
        pg=db,
        init_script=Path(config.db_airports_init_script).absolute(),
        debug_mode=bool(config.debug_mode),
        logger=logger
    )

    dist_gw = AirportDistancePairsGateway(
        pg=db,
        init_script=Path(config.db_distance_pairs_init_script).absolute(),
        debug_mode=bool(config.debug_mode),
        logger=logger
    )
    airports = []
    seen_uids = set()
    with open(Path(config.world_map_airports_file)) as airports_file:
        next(airports_file)  # Skip header
        for airport_row in airports_file:
            airport_details = airport_row[:-1].split(";")
            if airport_details[0] not in {0, '0'}:
                ap = Airport(
                    full_name=airport_details[0],
                    iso_country=airport_details[1],
                    iso_region=airport_details[2],
                    municipality=airport_details[3],
                    latitude=float(airport_details[4]),
                    longitude=float(airport_details[5]),
                    size=airport_details[6],
                    iata_code=airport_details[7],
                    local_code=(airport_details[8] if len(airport_details) == 9 else '')
                )

            if ap.iata_code not in {None, ''}\
                    and not (config.db_skip_small_airports and ap.size == 'small_airport')\
                    and ap.uid not in seen_uids:
                airports.append(ap)
                seen_uids.add(ap.uid)

    start = datetime.now()

    added_airports = ap_gw.import_data(airports)
    ap_import_finished = datetime.now()
    logger.info(f"Populating Airports table with {added_airports} entries took {format_timedelta_string(ap_import_finished - start)}")
    n = dist_gw.import_data(
        airports=airports,
        batch_size=config.db_distance_pairs_import_batch_size,
        validate=True
    )

    logger.info(f"Calculating and populating {n} distances took {format_timedelta_string(datetime.now() - ap_import_finished)}")
    logger.info(f"Total time taken: {format_timedelta_string(datetime.now() - start)}")

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

if __name__ == "__main__":
    main()
